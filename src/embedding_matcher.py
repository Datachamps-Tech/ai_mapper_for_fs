"""
Embedding Match Approach (Method 4)
Uses sentence-transformers (all-MiniLM-L6-v2) for semantic embeddings
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import config


class EmbeddingMatcher:
    """Embedding-based matching using sentence-transformers"""
    
    def __init__(self, training_data: pd.DataFrame, threshold: float = None):
        """
        Initialize embedding matcher
        
        Args:
            training_data: DataFrame with training data
            threshold: Minimum similarity threshold (0-1)
        """
        self.training_data = training_data
        self.threshold = threshold if threshold is not None else config.THRESHOLDS['embeddings']
        
        # Load sentence transformer model
        self.model = SentenceTransformer(config.SENTENCE_TRANSFORMER_MODEL)
        
        # Pre-compute embeddings for all training data
        self._compute_training_embeddings()
    
    def _compute_training_embeddings(self):
        """Pre-compute embeddings for all training examples"""
        # Extract primary groups
        primary_groups = self.training_data['primary_group'].tolist()
        
        # Compute embeddings in batch (much faster)
        self.training_embeddings = self.model.encode(
            primary_groups,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Store rows for retrieval
        self.training_rows = [row.to_dict() for idx, row in self.training_data.iterrows()]
    
    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt embedding-based match using cosine similarity
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Dictionary with match result or None:
            {
                'predicted_fs': str,
                'confidence': float (0-1),
                'matched_row': Dict (full training row with all columns),
                'matched_training_row': str (primary_group name),
                'predicted_columns': Dict (all 12 predicted columns)
            }
        """
        if self.training_embeddings is None or len(self.training_embeddings) == 0:
            return None
        
        # Compute embedding for input
        input_embedding = self.model.encode(
            [primary_group],
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Compute cosine similarity with all training embeddings
        similarities = cosine_similarity(input_embedding, self.training_embeddings)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        # Check if best score meets threshold
        if best_score >= self.threshold:
            best_row = self.training_rows[best_idx]
            
            # Extract all prediction columns from the matched row
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
                'confidence': float(best_score),  # Convert numpy float to Python float
                'matched_row': best_row,
                'matched_training_row': best_row['primary_group'],
                'predicted_columns': predicted_columns
            }
        
        return None
    
    def get_top_matches(self, primary_group: str, top_n: int = 5) -> list:
        """
        Get top N matches for debugging/analysis
        
        Args:
            primary_group: Input primary group name
            top_n: Number of top matches to return
            
        Returns:
            List of dictionaries with top matches
        """
        if self.training_embeddings is None or len(self.training_embeddings) == 0:
            return []
        
        # Compute embedding for input
        input_embedding = self.model.encode(
            [primary_group],
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Compute cosine similarity with all training embeddings
        similarities = cosine_similarity(input_embedding, self.training_embeddings)[0]
        
        # Get top N indices
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        matches = []
        for idx in top_indices:
            row = self.training_rows[idx]
            matches.append({
                'primary_group': row['primary_group'],
                'fs': row['fs'],
                'score': float(similarities[idx])
            })
        
        return matches
    
    def refresh(self, training_data: pd.DataFrame):
        """
        Refresh with new training data
        
        Args:
            training_data: Updated DataFrame
        """
        self.training_data = training_data
        self._compute_training_embeddings()
    
    def save_embeddings(self) -> Dict:
        """
        Get embeddings for saving to cache
        
        Returns:
            Dictionary with embeddings data
        """
        return {
            'embeddings': self.training_embeddings,
            'rows': self.training_rows,
            'primary_groups': self.training_data['primary_group'].tolist()
        }
    
    def load_embeddings(self, embeddings_data: Dict) -> bool:
        """
        Load pre-computed embeddings from cache
        
        Args:
            embeddings_data: Dictionary with embeddings data
            
        Returns:
            True if successful
        """
        try:
            # Verify data matches current training data
            if len(embeddings_data['primary_groups']) != len(self.training_data):
                return False
            
            # Check if primary groups match
            current_groups = self.training_data['primary_group'].tolist()
            if embeddings_data['primary_groups'] != current_groups:
                return False
            
            # Load embeddings
            self.training_embeddings = embeddings_data['embeddings']
            self.training_rows = embeddings_data['rows']
            
            return True
        except Exception as e:
            print(f"Warning: Could not load cached embeddings: {e}")
            return False
