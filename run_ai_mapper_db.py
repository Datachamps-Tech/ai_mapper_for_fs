# run_ai_mapper_db.py

from db.session import SessionLocal
from db.staging_reader import fetch_distinct_primary_groups
from db.dimfs_writer import insert_dimfs
from src.mapper import AIMapper
import time
import os


def main():
    # Get tenant_id from environment variable (set by API)
    tenant_id = os.getenv("TENANT_ID")
    
    if tenant_id:
        print(f"🔍 Running AI mapper for tenant: {tenant_id}")
    else:
        print("🔍 Running AI mapper for ALL tenants (batch mode)")
    
    # Fetch unclassified items with tenant filter
    rows = fetch_distinct_primary_groups(tenant_id=tenant_id)
    
    print(f"📊 Found {len(rows)} new items to classify")
    
    # Early exit if nothing to do
    if len(rows) == 0:
        print("✅ All items already classified. Nothing to do.")
        return
    
    # Initialize session and mapper
    print("⚙️ Initializing AI mapper...")
    session = SessionLocal()
    
    init_start = time.time()
    mapper = AIMapper()  # Uses shared API key from environment
    mapper.refresh_training_data()
    print(f"✅ Mapper initialized in {time.time() - init_start:.2f}s\n")

    try:
        total_start = time.time()
        
        print(f"{'Item':<45} | {'Time':>6} | {'Method':^10} | {'Conf':>5}")
        print("-" * 75)
        
        for idx, row in enumerate(rows, 1):
            stg_id = row["id"]
            raw_id = row["raw_id"]
            row_tenant_id = row["tenant_id"]
            primary_group = row["primary_group"]

            # Time individual prediction
            item_start = time.time()
            result = mapper.predict_single(primary_group)
            elapsed = time.time() - item_start

            # Insert to database with stg_id
            insert_dimfs(
                session=session,
                stg_id=stg_id,
                raw_id=raw_id,
                tenant_id=row_tenant_id,
                primary_group=primary_group,
                ai_result=result
            )

            # Progress line
            truncated = (primary_group[:42] + '...') if len(primary_group) > 45 else primary_group
            print(f"{truncated:<45} | {elapsed:5.2f}s | {result['method_used']:^10} | {result['confidence']:4.0%}")
            
            # Commit every 10 rows
            if idx % 10 == 0:
                session.commit()
                print(f"💾 Checkpoint: {idx}/{len(rows)} committed")

        # Final commit
        session.commit()
        
        total_time = time.time() - total_start
        
        # Display stats
        stats = mapper.get_session_stats()
        llm_stats = stats.get('llm_stats', {})
        
        print("\n" + "=" * 75)
        print("🎉 AI MAPPING COMPLETED SUCCESSFULLY")
        print("=" * 75)
        if tenant_id:
            print(f"👤 Tenant ID:        {tenant_id}")
        print(f"⏱️  Total time:        {total_time:.2f}s ({total_time/len(rows):.2f}s per item)")
        print(f"📊 Total predictions: {stats['predictions_made']}")
        print(f"🤖 LLM calls:         {llm_stats.get('call_count', 0)} ({llm_stats.get('call_count', 0)/len(rows)*100:.1f}%)")
        print(f"⚠️  Needs review:      {stats['needs_review_count']}")
        
        print("\n📈 Method Distribution:")
        for method, count in stats['method_distribution'].items():
            if count > 0:
                pct = count / stats['predictions_made'] * 100
                bar = "█" * int(pct / 2)
                print(f"  {method:12} | {bar:50} {count:3} ({pct:5.1f}%)")
        
        print("=" * 75)

    except Exception as e:
        session.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        session.close()
        print("🔒 Database connection closed")


if __name__ == "__main__":
    main()