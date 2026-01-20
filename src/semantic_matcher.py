"""
Semantic Match Approach (Method 3)
Uses spaCy en_core_web_md for semantic similarity
"""

import pandas as pd
from typing import Optional, Dict, Any
import spacy
from src.utils import normalize
import config


class SemanticMatcher:
    """Semantic matching using spaCy"""
    
    def __init__(self, training_data: pd.DataFrame, threshold: float = None):
        """
        Initialize semantic matcher
        
        Args:
            training_data: DataFrame with training data
            threshold: Minimum similarity threshold (0-1)
        """
        self.training_data = training_data
        self.threshold = threshold if threshold is not None else config.THRESHOLDS['semantic']
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{config.SPACY_MODEL}' not found. "
                f"Please run: python -m spacy download {config.SPACY_MODEL}"
            )
        
        # Pre-compute document vectors for all training data
        self._compute_training_vectors()
    
    def _compute_training_vectors(self):
        """Pre-compute spaCy document vectors for all training examples"""
        self.training_vectors = []
        
        for idx, row in self.training_data.iterrows():
            doc = self.nlp(row['primary_group'])
            self.training_vectors.append({
                'doc': doc,
                'row': row.to_dict()
            })
    
    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt semantic match using spaCy similarity
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Dictionary with match result or None:
            {
                'predicted_fs': str,
                'confidence': float (0-1),
                'matched_row': Dict (full training row with all columns),
                'matched_training_row': best_match,
                'predicted_columns': Dict (all 12 predicted columns)
            }
        """
        if not self.training_vectors:
            return None
        
        # Compute vector for input
        input_doc = self.nlp(primary_group)
        
        best_score = 0
        best_match = None
        best_row = None
        
        # Compare against all training vectors
        for item in self.training_vectors:
            training_doc = item['doc']
            row = item['row']
            
            # Compute similarity (0-1 range)
            similarity = input_doc.similarity(training_doc)
            
            if similarity > best_score:
                best_score = similarity
                best_match = row['primary_group']
                best_row = row
        
        # Check if best score meets threshold
        if best_score >= self.threshold:
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
                'confidence': best_score,
                'matched_row': best_row,
                'matched_training_row': best_match,
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
        if not self.training_vectors:
            return []
        
        input_doc = self.nlp(primary_group)
        matches = []
        
        for item in self.training_vectors:
            training_doc = item['doc']
            row = item['row']
            similarity = input_doc.similarity(training_doc)
            
            matches.append({
                'primary_group': row['primary_group'],
                'fs': row['fs'],
                'score': similarity
            })
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_n]
    
    def refresh(self, training_data: pd.DataFrame):
        """
        Refresh with new training data
        
        Args:
            training_data: Updated DataFrame
        """
        self.training_data = training_data
        self._compute_training_vectors()
