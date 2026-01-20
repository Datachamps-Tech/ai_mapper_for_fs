"""
Data loader for training data management
Handles Excel, JSON, CSV conversion and caching
"""

import pandas as pd
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import config
from src.utils import validate_training_data, normalize
from sqlalchemy import text
from db.session import engine


class DataLoader:
    """Manages loading, caching, and refreshing training data"""
    
    def __init__(self):
        self.training_data: Optional[pd.DataFrame] = None
        self.training_embeddings: Optional[Dict] = None
        self.last_loaded: Optional[datetime] = None
        
    def load_training_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        try:
            query = """
                SELECT
                    primary_group,
                    fs,
                    bs_main_category,
                    bs_classification,
                    bs_sub_classification,
                    bs_sub_classification_2,
                    pl_classification,
                    pl_sub_classification,
                    pl_classification_1,
                    cf_classification,
                    cf_sub_classification,
                    expense_type
                FROM raw.ai_mapper_train
                WHERE is_active = true
            """
            df = pd.read_sql(text(query), engine)

            validation = validate_training_data(df)
            if not validation['valid']:
                return {
                    'success': False,
                    'message': f"Training data validation failed: {validation['errors']}",
                    'data': None,
                    'source': 'db',
                    'validation': validation
                }

            self.training_data = df
            self.last_loaded = datetime.now()

            return {
                'success': True,
                'message': f'Loaded {len(df)} rows from Postgres',
                'data': df,
                'source': 'db',
                'validation': validation
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'DB load failed: {str(e)}',
                'data': None,
                'source': 'db',
                'validation': None
            }

    def _load_from_excel(self) -> Dict[str, Any]:
        """Load training data from Excel and create cache"""
        try:
            # Read Excel
            df = pd.read_excel(config.TRAINING_EXCEL)
            
            # Validate
            validation = validate_training_data(df)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'message': f"Training data validation failed: {', '.join(validation['errors'])}",
                    'data': None,
                    'source': 'excel',
                    'validation': validation
                }
            
            # Store in memory
            self.training_data = df
            self.last_loaded = datetime.now()
            
            # Create caches
            self._save_to_json(df)
            self._save_to_csv(df)
            
            return {
                'success': True,
                'message': f'Loaded {len(df)} rows from Excel',
                'data': df,
                'source': 'excel',
                'validation': validation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error reading Excel: {str(e)}',
                'data': None,
                'source': 'excel',
                'validation': None
            }
    
    def _load_from_json(self) -> Dict[str, Any]:
        """Load training data from JSON cache"""
        try:
            with open(config.TRAINING_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            
            # Validate
            validation = validate_training_data(df)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'message': f"Cached data validation failed: {', '.join(validation['errors'])}",
                    'data': None,
                    'source': 'json',
                    'validation': validation
                }
            
            # Store in memory
            self.training_data = df
            self.last_loaded = datetime.now()
            
            return {
                'success': True,
                'message': f'Loaded {len(df)} rows from cache (JSON)',
                'data': df,
                'source': 'json',
                'validation': validation
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error reading JSON cache: {str(e)}',
                'data': None,
                'source': 'json',
                'validation': None
            }
    
    def _save_to_json(self, df: pd.DataFrame) -> bool:
        """Save DataFrame to JSON cache"""
        try:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict for JSON serialization
            data = df.to_dict(orient='records')
            
            with open(config.TRAINING_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Warning: Could not save JSON cache: {e}")
            return False
    
    def _save_to_csv(self, df: pd.DataFrame) -> bool:
        """Save DataFrame to CSV (for Git tracking)"""
        try:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(config.TRAINING_CSV, index=False, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Warning: Could not save CSV: {e}")
            return False
    
    def add_training_row(self, primary_group: str, fs: str) -> Dict[str, Any]:
        """
        Add new row to training data
        
        Args:
            primary_group: Primary group name
            fs: Financial statement classification
            
        Returns:
            Dictionary with result:
            {
                'success': bool,
                'message': str,
                'total_rows': int
            }
        """
        try:
            # Validate inputs
            if not primary_group or not primary_group.strip():
                return {
                    'success': False,
                    'message': 'Primary group cannot be empty',
                    'total_rows': 0
                }
            
            if fs not in config.VALID_FS_VALUES:
                return {
                    'success': False,
                    'message': f'Invalid fs value. Must be one of: {config.VALID_FS_VALUES}',
                    'total_rows': 0
                }
            
            # Load current data
            if self.training_data is None:
                result = self.load_training_data()
                if not result['success']:
                    return {
                        'success': False,
                        'message': 'Could not load training data',
                        'total_rows': 0
                    }
            
            # Check for duplicate
            normalized_input = normalize(primary_group)
            existing = self.training_data[
                self.training_data['primary_group'].apply(normalize) == normalized_input
            ]
            
            if not existing.empty:
                return {
                    'success': False,
                    'message': f'Primary group "{primary_group}" already exists in training data',
                    'total_rows': len(self.training_data)
                }
            
            # Create new row (only fill required columns)
            new_row = {col: None for col in config.ALL_COLUMNS}
            new_row['primary_group'] = primary_group.strip()
            new_row['fs'] = fs
            
            # Append to DataFrame
            self.training_data = pd.concat(
                [self.training_data, pd.DataFrame([new_row])],
                ignore_index=True
            )
            
            
            # Update caches
            self._save_to_json(self.training_data)
            self._save_to_csv(self.training_data)
            
            return {
                'success': True,
                'message': f'Added successfully! Total rows: {len(self.training_data)}',
                'total_rows': len(self.training_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding row: {str(e)}',
                'total_rows': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get training data statistics
        
        Returns:
            Dictionary with stats
        """
        if self.training_data is None:
            return {
                'total_rows': 0,
                'bs_count': 0,
                'pl_count': 0,
                'last_loaded': None
            }
        
        return {
            'total_rows': len(self.training_data),
            'bs_count': len(self.training_data[self.training_data['fs'] == 'Balance Sheet']),
            'pl_count': len(self.training_data[self.training_data['fs'] == 'Profit & Loss']),
            'last_loaded': self.last_loaded.strftime('%Y-%m-%d %H:%M:%S') if self.last_loaded else None
        }
    
    def search_training_data(self, query: str) -> pd.DataFrame:
        """
        Search training data by keyword
        
        Args:
            query: Search query
            
        Returns:
            Filtered DataFrame
        """
        if self.training_data is None or query is None or query.strip() == "":
            return pd.DataFrame()
        
        query_lower = query.lower()
        
        # Search in primary_group column
        mask = self.training_data['primary_group'].str.lower().str.contains(query_lower, na=False)
        
        return self.training_data[mask]
    
    def export_csv(self) -> Optional[Path]:
        """
        Export training data to CSV
        
        Returns:
            Path to CSV file or None if failed
        """
        if self.training_data is None:
            return None
        
        try:
            self._save_to_csv(self.training_data)
            return config.TRAINING_CSV
        except:
            return None
    
    def load_embeddings(self) -> Optional[Dict]:
        """
        Load pre-computed embeddings from pickle file
        
        Returns:
            Dictionary with embeddings or None
        """
        if not config.TRAINING_EMBEDDINGS.exists():
            return None
        
        try:
            with open(config.TRAINING_EMBEDDINGS, 'rb') as f:
                self.training_embeddings = pickle.load(f)
            return self.training_embeddings
        except Exception as e:
            print(f"Warning: Could not load embeddings: {e}")
            return None
    
    def save_embeddings(self, embeddings: Dict) -> bool:
        """
        Save embeddings to pickle file
        
        Args:
            embeddings: Dictionary with embeddings
            
        Returns:
            True if successful
        """
        try:
            config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(config.TRAINING_EMBEDDINGS, 'wb') as f:
                pickle.dump(embeddings, f)
            self.training_embeddings = embeddings
            return True
        except Exception as e:
            print(f"Warning: Could not save embeddings: {e}")
            return False
