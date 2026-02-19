"""
Semantic Match Approach (Method 3)
Uses spaCy en_core_web_md for semantic similarity.
With disk caching — stores raw numpy vectors (NOT spaCy Doc objects, which can't be pickled).
Match time uses cosine similarity on vectors instead of doc.similarity() — identical results.
"""

import pickle
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from src.utils import normalize
import config

# Cache lives at data/cache/ relative to project root
CACHE_DIR = Path("data/cache")


class SemanticMatcher:
    """Semantic matching using spaCy"""

    def __init__(self, training_data: pd.DataFrame, threshold: float = None):
        """
        Initialize semantic matcher.
        Loads vectors from disk cache if training data hasn't changed.
        Only recomputes when cache is missing or stale.

        NOTE: spaCy Doc objects cannot be pickled (they're bound to vocab).
        So we cache raw numpy vectors instead and use cosine similarity at match time.
        Results are identical — doc.similarity() is just cosine similarity on vectors internally.

        Args:
            training_data: DataFrame with training data
            threshold: Minimum similarity threshold (0-1)
        """
        self.training_data = training_data
        self.threshold = threshold if threshold is not None else config.THRESHOLDS['semantic']

        # Always load spaCy — needed at match time for encoding the input query
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{config.SPACY_MODEL}' not found. "
                f"Please run: python -m spacy download {config.SPACY_MODEL}"
            )

        # Try cache first, fall back to computing from scratch
        if not self._load_from_cache(training_data):
            print("⚙️  Computing spaCy vectors (first run or training data changed)...")
            self._compute_training_vectors()
            self._save_to_cache()

    # ------------------------------------------------------------------ #
    # CACHE LOGIC
    # ------------------------------------------------------------------ #

    def _get_cache_key(self, training_data: pd.DataFrame) -> str:
        """
        MD5 hash of all primary_group values.
        Cache is invalidated automatically when training data changes.
        """
        content = "".join(sorted(training_data['primary_group'].tolist())).encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def _load_from_cache(self, training_data: pd.DataFrame) -> bool:
        """
        Try loading pre-computed vectors from disk.
        Returns True if successful, False if cache is missing or stale.
        """
        cache_key = self._get_cache_key(training_data)
        cache_file = CACHE_DIR / f"semantic_{cache_key}.pkl"

        if not cache_file.exists():
            return False

        try:
            with open(cache_file, 'rb') as f:
                cached = pickle.load(f)

            # Restore numpy vectors and row metadata
            self.training_vectors_np = cached['vectors']   # numpy array shape (N, 300)
            self.training_rows = cached['rows']             # list of dicts
            print(f"⚡ Semantic vectors loaded from cache ({len(self.training_rows)} rows)")
            return True

        except Exception as e:
            print(f"⚠️  Semantic cache load failed, will recompute: {e}")
            return False

    def _save_to_cache(self):
        """Save computed vectors to disk for future runs."""
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_key = self._get_cache_key(self.training_data)
            cache_file = CACHE_DIR / f"semantic_{cache_key}.pkl"

            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'vectors': self.training_vectors_np,
                    'rows': self.training_rows
                }, f)

            print(f"💾 Semantic vectors cached to {cache_file.name}")

        except Exception as e:
            print(f"⚠️  Could not save semantic cache: {e}")

    # ------------------------------------------------------------------ #
    # CORE LOGIC
    # ------------------------------------------------------------------ #

    def _compute_training_vectors(self):
        """
        Pre-compute spaCy vectors for all training examples.
        Stores numpy arrays (not Doc objects) so they can be cached/pickled.
        """
        vectors = []
        rows = []

        for _, row in self.training_data.iterrows():
            doc = self.nlp(row['primary_group'])
            vectors.append(doc.vector)          # numpy array of shape (300,)
            rows.append(row.to_dict())

        # Stack into (N, 300) matrix for fast batch cosine similarity
        self.training_vectors_np = np.array(vectors)
        self.training_rows = rows

    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt semantic match using spaCy vectors + cosine similarity.

        Args:
            primary_group: Input primary group name

        Returns:
            Dictionary with match result or None
        """
        if not hasattr(self, 'training_vectors_np') or len(self.training_vectors_np) == 0:
            return None

        # Encode input to vector
        input_vec = self.nlp(primary_group).vector.reshape(1, -1)

        # Cosine similarity against all training vectors at once
        similarities = cosine_similarity(input_vec, self.training_vectors_np)[0]

        best_idx = np.argmax(similarities)
        best_score = float(similarities[best_idx])
        best_row = self.training_rows[best_idx]

        if best_score >= self.threshold:
            predicted_columns = {
                'fs': best_row['fs'],
                'bs_main_category': best_row.get('bs_main_category'),
                'bs_classification': best_row.get('bs_classification'),
                'bs_sub_classification': best_row.get('bs_sub_classification'),
                'bs_sub_classification_2': best_row.get('bs_sub_classification_2'),
                'pl_classification': best_row.get('pl_classification'),
                'pl_sub_classification': best_row.get('pl_sub_classification'),
                'pl_classification_1': best_row.get('pl_classification_1'),
                'cf_classification': best_row.get('cf_classification'),
                'cf_sub_classification': best_row.get('cf_sub_classification'),
                'expense_type': best_row.get('expense_type')
            }

            return {
                'predicted_fs': best_row['fs'],
                'confidence': best_score,
                'matched_row': best_row,
                'matched_training_row': best_row['primary_group'],
                'predicted_columns': predicted_columns
            }

        return None

    def get_top_matches(self, primary_group: str, top_n: int = 5) -> list:
        """Get top N matches for debugging/analysis"""
        if not hasattr(self, 'training_vectors_np') or len(self.training_vectors_np) == 0:
            return []

        input_vec = self.nlp(primary_group).vector.reshape(1, -1)
        similarities = cosine_similarity(input_vec, self.training_vectors_np)[0]
        top_indices = np.argsort(similarities)[::-1][:top_n]

        return [
            {
                'primary_group': self.training_rows[idx]['primary_group'],
                'fs': self.training_rows[idx]['fs'],
                'score': float(similarities[idx])
            }
            for idx in top_indices
        ]

    def refresh(self, training_data: pd.DataFrame):
        """
        Refresh with new training data.
        Cache key will change automatically if data changed — triggers recompute.
        """
        self.training_data = training_data
        if not self._load_from_cache(training_data):
            self._compute_training_vectors()
            self._save_to_cache()