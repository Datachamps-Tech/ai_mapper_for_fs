"""
Embedding Match Approach (Method 4)
Uses sentence-transformers (all-MiniLM-L6-v2) for semantic embeddings
With disk caching — skips recomputation if training data hasn't changed.
"""

import pickle
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import config

# Cache lives at data/cache/ relative to project root
CACHE_DIR = Path("data/cache")


class EmbeddingMatcher:
    """Embedding-based matching using sentence-transformers"""

    def __init__(self, training_data: pd.DataFrame, threshold: float = None):
        """
        Initialize embedding matcher.
        Loads embeddings from disk cache if training data hasn't changed.
        Only recomputes when cache is missing or stale.

        Args:
            training_data: DataFrame with training data
            threshold: Minimum similarity threshold (0-1)
        """
        self.training_data = training_data
        self.threshold = threshold if threshold is not None else config.THRESHOLDS['embeddings']

        # Load sentence transformer model (always needed — used at match time too)
        self.model = SentenceTransformer(config.SENTENCE_TRANSFORMER_MODEL)

        # Try cache first, fall back to computing from scratch
        if not self._load_from_cache(training_data):
            print("⚙️  Computing embeddings (first run or training data changed)...")
            self._compute_training_embeddings()
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
        Try loading pre-computed embeddings from disk.
        Returns True if successful, False if cache is missing or stale.
        """
        cache_key = self._get_cache_key(training_data)
        cache_file = CACHE_DIR / f"embeddings_{cache_key}.pkl"

        if not cache_file.exists():
            return False

        try:
            with open(cache_file, 'rb') as f:
                cached = pickle.load(f)

            self.training_embeddings = cached['embeddings']
            self.training_rows = cached['rows']
            print(f"⚡ Embeddings loaded from cache ({len(self.training_rows)} rows)")
            return True

        except Exception as e:
            print(f"⚠️  Cache load failed, will recompute: {e}")
            return False

    def _save_to_cache(self):
        """Save computed embeddings to disk for future runs."""
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_key = self._get_cache_key(self.training_data)
            cache_file = CACHE_DIR / f"embeddings_{cache_key}.pkl"

            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'embeddings': self.training_embeddings,
                    'rows': self.training_rows
                }, f)

            print(f"💾 Embeddings cached to {cache_file.name}")

        except Exception as e:
            # Non-fatal — just means next run will recompute
            print(f"⚠️  Could not save embeddings cache: {e}")

    # ------------------------------------------------------------------ #
    # CORE LOGIC
    # ------------------------------------------------------------------ #

    def _compute_training_embeddings(self):
        """Pre-compute embeddings for all training examples"""
        primary_groups = self.training_data['primary_group'].tolist()

        self.training_embeddings = self.model.encode(
            primary_groups,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        self.training_rows = [row.to_dict() for _, row in self.training_data.iterrows()]

    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt embedding-based match using cosine similarity.

        Args:
            primary_group: Input primary group name

        Returns:
            Dictionary with match result or None
        """
        if self.training_embeddings is None or len(self.training_embeddings) == 0:
            return None

        input_embedding = self.model.encode(
            [primary_group],
            convert_to_numpy=True,
            show_progress_bar=False
        )

        similarities = cosine_similarity(input_embedding, self.training_embeddings)[0]

        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]

        if best_score >= self.threshold:
            best_row = self.training_rows[best_idx]

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
                'confidence': float(best_score),
                'matched_row': best_row,
                'matched_training_row': best_row['primary_group'],
                'predicted_columns': predicted_columns
            }

        return None

    def get_top_matches(self, primary_group: str, top_n: int = 5) -> list:
        """Get top N matches for debugging/analysis"""
        if self.training_embeddings is None or len(self.training_embeddings) == 0:
            return []

        input_embedding = self.model.encode(
            [primary_group],
            convert_to_numpy=True,
            show_progress_bar=False
        )

        similarities = cosine_similarity(input_embedding, self.training_embeddings)[0]
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
            self._compute_training_embeddings()
            self._save_to_cache()

    def save_embeddings(self) -> Dict:
        """Get embeddings for external use"""
        return {
            'embeddings': self.training_embeddings,
            'rows': self.training_rows,
            'primary_groups': self.training_data['primary_group'].tolist()
        }

    def load_embeddings(self, embeddings_data: Dict) -> bool:
        """Load pre-computed embeddings from external source"""
        try:
            if len(embeddings_data['primary_groups']) != len(self.training_data):
                return False

            current_groups = self.training_data['primary_group'].tolist()
            if embeddings_data['primary_groups'] != current_groups:
                return False

            self.training_embeddings = embeddings_data['embeddings']
            self.training_rows = embeddings_data['rows']
            return True

        except Exception as e:
            print(f"Warning: Could not load embeddings: {e}")
            return False