# run_ai_mapper_db.py

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.session import SessionLocal
from db.staging_reader import fetch_distinct_primary_groups
from db.dimfs_writer import insert_dimfs
from src.mapper import AIMapper

MAX_WORKERS = int(os.getenv("AI_MAPPER_WORKERS", 5))

# Thread-local storage for DB sessions (one session per thread, not shared)
_thread_local = threading.local()


def get_thread_session():
    """Each thread gets its own SQLAlchemy session."""
    if not hasattr(_thread_local, "session"):
        _thread_local.session = SessionLocal()
    return _thread_local.session


def close_thread_session():
    """Close this thread's session if it exists."""
    if hasattr(_thread_local, "session"):
        _thread_local.session.close()
        del _thread_local.session


def process_single_row(row, mapper):
    """
    Worker function: classifies one staging row and writes to dim_fs.
    Each thread gets its own DB session via thread-local storage.
    mapper is shared (read-only after init) — safe across threads.
    """
    stg_id = row["id"]
    raw_id = row["raw_id"]
    tenant_id = row["tenant_id"]
    primary_group = row["primary_group"]

    item_start = time.time()

    try:
        # Classify — mapper is shared but all operations are read-only
        result = mapper.predict_single(primary_group)
        elapsed = time.time() - item_start

        # Thread-local session — no sharing, no race conditions
        session = get_thread_session()
        insert_dimfs(
            session=session,
            stg_id=stg_id,
            raw_id=raw_id,
            tenant_id=tenant_id,
            primary_group=primary_group,
            ai_result=result
        )
        session.commit()

        truncated = (primary_group[:42] + "...") if len(primary_group) > 45 else primary_group
        print(f"✅ {truncated:<45} | {elapsed:5.2f}s | {result['method_used']:^10} | {result['confidence']:4.0%}")

        return {"status": "success", "primary_group": primary_group, "result": result}

    except Exception as e:
        # Roll back only this thread's session
        try:
            get_thread_session().rollback()
        except Exception:
            pass
        print(f"❌ FAILED: {primary_group} → {e}")
        return {"status": "failed", "primary_group": primary_group, "error": str(e)}


def main():
    print("🔍 Checking for new items to classify...")
    rows = fetch_distinct_primary_groups()
    print(f"📊 Found {len(rows)} new items to classify")

    if len(rows) == 0:
        print("✅ All items already classified. Nothing to do.")
        return

    # Initialize mapper ONCE — shared across all threads (read-only after init)
    print("⚙️ Initializing AI mapper...")
    init_start = time.time()
    mapper = AIMapper()
    mapper.refresh_training_data()
    print(f"✅ Mapper initialized in {time.time() - init_start:.2f}s")
    print(f"⚡ Running with {MAX_WORKERS} parallel workers\n")

    print(f"{'Item':<45} | {'Time':>6} | {'Method':^10} | {'Conf':>5}")
    print("-" * 75)

    total_start = time.time()
    results = []

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_row = {
                executor.submit(process_single_row, row, mapper): row
                for row in rows
            }

            for future in as_completed(future_to_row):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    row = future_to_row[future]
                    print(f"❌ Unhandled exception for {row['primary_group']}: {e}")
                    results.append({"status": "failed", "primary_group": row["primary_group"], "error": str(e)})

    finally:
        # Close all thread-local sessions
        # ThreadPoolExecutor reuses threads, so explicitly clean up
        # (sessions auto-close when threads exit, but this is safer)
        pass

    total_time = time.time() - total_start
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")

    print("\n" + "=" * 75)
    print("🎉 AI MAPPING COMPLETED")
    print("=" * 75)
    print(f"⏱️  Total time:     {total_time:.2f}s  ({total_time / len(rows):.2f}s per item avg)")
    print(f"⚡ Throughput:     {len(rows) / total_time:.2f} items/sec")
    print(f"✅ Success:        {success_count}/{len(rows)}")
    print(f"❌ Failed:         {failed_count}/{len(rows)}")

    if failed_count > 0:
        print("\n⚠️  Failed items:")
        for r in results:
            if r["status"] == "failed":
                print(f"   - {r['primary_group']}: {r.get('error', 'unknown')}")

    print("=" * 75)


if __name__ == "__main__":
    main()