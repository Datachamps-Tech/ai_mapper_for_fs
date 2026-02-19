"""
Fuzzy Match Approach (Method 2)
Uses rapidfuzz for overall string similarity
"""

import pandas as pd
from typing import Optional, Dict, Any
from rapidfuzz import fuzz
from src.utils import normalize
import config


class FuzzyMatcher:
    """Fuzzy matching using rapidfuzz"""
    
    def __init__(self, training_data: pd.DataFrame, threshold: float = None):
        """
        Initialize fuzzy matcher
        
        Args:
            training_data: DataFrame with training data
            threshold: Minimum similarity threshold (0-100)
        """
        self.training_data = training_data
        self.threshold = threshold if threshold is not None else config.THRESHOLDS['fuzzy']
        # Convert threshold from 0-1 to 0-100 for rapidfuzz
        self.threshold_percent = self.threshold * 100
    
    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt fuzzy match using overall similarity (Ratio algorithm)
        
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
        if self.training_data is None or self.training_data.empty:
            return None
        
        normalized_input = normalize(primary_group)
        best_score = 0
        best_match = None
        best_row = None
        
        # Compare against all training examples
        for idx, row in self.training_data.iterrows():
            normalized_training = normalize(row['primary_group'])
            
            # Use Ratio algorithm (overall similarity)
            score = fuzz.ratio(normalized_input, normalized_training)
            
            if score > best_score:
                best_score = score
                best_match = row['primary_group']
                best_row = row.to_dict()
        
        # Check if best score meets threshold
        if best_score >= self.threshold_percent:
            # Convert score from 0-100 to 0-1
            confidence = best_score / 100.0
            
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
                'confidence': confidence,
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
        if self.training_data is None or self.training_data.empty:
            return []
        
        normalized_input = normalize(primary_group)
        matches = []
        
        for idx, row in self.training_data.iterrows():
            normalized_training = normalize(row['primary_group'])
            score = fuzz.ratio(normalized_input, normalized_training)
            
            matches.append({
                'primary_group': row['primary_group'],
                'fs': row['fs'],
                'score': score / 100.0
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
