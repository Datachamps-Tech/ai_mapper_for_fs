"""
Exact Match Approach (Method 1)
Case-insensitive, normalized exact match
"""

import pandas as pd
from typing import Optional, Dict, Any
from src.utils import normalize
import config


class ExactMatcher:
    """Exact match using normalized strings"""
    
    def __init__(self, training_data: pd.DataFrame):
        """
        Initialize exact matcher
        
        Args:
            training_data: DataFrame with training data
        """
        self.training_data = training_data
        self._create_lookup()
    
    def _create_lookup(self):
        """Create normalized lookup dictionary for O(1) access"""
        self.lookup = {}
        
        for idx, row in self.training_data.iterrows():
            normalized_key = normalize(row['primary_group'])
            # Store the full row for later retrieval
            self.lookup[normalized_key] = row.to_dict()
    
    def match(self, primary_group: str) -> Optional[Dict[str, Any]]:
        """
        Attempt exact match
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Dictionary with match result or None:
            {
                'predicted_fs': str,
                'confidence': 1.0,
                'matched_row': Dict (full training row with all columns),
                'matched_training_row': str (primary_group name),
                'predicted_columns': Dict (all 12 predicted columns)
            }
        """
        normalized_input = normalize(primary_group)
        
        if normalized_input in self.lookup:
            matched_row = self.lookup[normalized_input]
            
            # Extract all prediction columns from the matched row
            predicted_columns = {
                'fs': matched_row['fs'],
                'bs_main_category': matched_row.get('bs_main_category'),
                'bs_classification': matched_row.get('bs_classification'),
                'bs_sub_classification': matched_row.get('bs_sub_classification'),
                'bs_sub_classification_2': matched_row.get('bs_sub_classification_2'),
                'pl_classification': matched_row.get('pl_classification'),
                'pl_sub_classification': matched_row.get('pl_sub_classification'),
                'pl_classification_1': matched_row.get('pl_classification_1'),
                'cf_classification': matched_row.get('cf_classification'),
                'cf_sub_classification': matched_row.get('cf_sub_classification'),
                'expense_type': matched_row.get('expense_type')
            }
            
            return {
                'predicted_fs': matched_row['fs'],
                'confidence': 1.0,  # Exact match always has perfect confidence
                'matched_row': matched_row,
                'matched_training_row': matched_row['primary_group'],
                'predicted_columns': predicted_columns
            }
        
        return None
    
    def refresh(self, training_data: pd.DataFrame):
        """
        Refresh with new training data
        
        Args:
            training_data: Updated DataFrame
        """
        self.training_data = training_data
        self._create_lookup()
