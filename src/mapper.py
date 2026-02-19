"""
AI Mapper - Orchestrator
Runs sequential cascade of matching approaches with early exit
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import config
from src.data_loader import DataLoader
from src.exact_matcher import ExactMatcher
from src.fuzzy_matcher import FuzzyMatcher
from src.semantic_matcher import SemanticMatcher
from src.embedding_matcher import EmbeddingMatcher
from src.llm_matcher import LLMMatcher
from src.utils import create_result_dict
from src.gemini_matcher import GeminiMatcher
import concurrent.futures
class AIMapper:
    """Main orchestrator for accounting classification"""
    
    def __init__(self, domain: str = "General Business", api_key: str = None):
        """
        Initialize AI Mapper
        
        Args:
            domain: Company domain for LLM context
            api_key: OpenAI API key
        """
        self.domain = domain
        self.api_key = api_key
        
        # Initialize data loader
        self.data_loader = DataLoader()
        
        # Initialize matchers (will be set after loading data)
        self.exact_matcher = None
        self.fuzzy_matcher = None
        self.semantic_matcher = None
        self.embedding_matcher = None
        self.llm_matcher = None
        
        # Load training data
        self._load_training_data()
        
        # Statistics
        self.session_stats = {
            'predictions_made': 0,
            'method_distribution': {
                'exact': 0,
                'fuzzy': 0,
                'semantic': 0,
                'embeddings': 0,
                'llm': 0
            },
            'needs_review_count': 0
        }
    
# In mapper.py — replace _load_training_data()



    def _load_training_data(self):
        """Load training data and initialize matchers — heavy ones in parallel"""
        result = self.data_loader.load_training_data()
        
        if not result['success']:
            raise RuntimeError(f"Failed to load training data: {result['message']}")
        
        training_data = result['data']
        
        # These are fast — do them immediately
        self.exact_matcher = ExactMatcher(training_data)
        self.fuzzy_matcher = FuzzyMatcher(training_data)
        self.llm_matcher = GeminiMatcher(api_key=None, domain=self.domain)
        
        # spaCy + SentenceTransformer are slow — load them in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            semantic_future = executor.submit(SemanticMatcher, training_data)
            embedding_future = executor.submit(EmbeddingMatcher, training_data)
            
            self.semantic_matcher = semantic_future.result()
            self.embedding_matcher = embedding_future.result()
    
    def predict_single(self, primary_group: str, return_decision_trail: bool = False) -> Dict[str, Any]:
        """
        Predict financial statement for a single primary group
        Uses sequential cascade with early exit
        
        Args:
            primary_group: Input primary group name
            return_decision_trail: If True, include attempts from all methods
            
        Returns:
            Dictionary with prediction result
        """
        decision_trail = []
        
        # Method 1: Exact Match
        result = self.exact_matcher.match(primary_group)
        if result:
            decision_trail.append({'method': 'exact', 'result': result})
            if result['confidence'] >= config.THRESHOLDS['exact']:
                return self._format_result(primary_group, result, 'exact', decision_trail if return_decision_trail else None)
        else:
            decision_trail.append({'method': 'exact', 'result': None})
        
        # Method 2: Fuzzy Match
        result = self.fuzzy_matcher.match(primary_group)
        if result:
            decision_trail.append({'method': 'fuzzy', 'result': result})
            if result['confidence'] >= config.THRESHOLDS['fuzzy']:
                return self._format_result(primary_group, result, 'fuzzy', decision_trail if return_decision_trail else None)
        else:
            decision_trail.append({'method': 'fuzzy', 'result': None})
        
        # Method 3: Semantic Similarity
        result = self.semantic_matcher.match(primary_group)
        if result:
            decision_trail.append({'method': 'semantic', 'result': result})
            if result['confidence'] >= config.THRESHOLDS['semantic']:
                return self._format_result(primary_group, result, 'semantic', decision_trail if return_decision_trail else None)
        else:
            decision_trail.append({'method': 'semantic', 'result': None})
        
        # Method 4: Embeddings
        result = self.embedding_matcher.match(primary_group)
        if result:
            decision_trail.append({'method': 'embeddings', 'result': result})
            if result['confidence'] >= config.THRESHOLDS['embeddings']:
                return self._format_result(primary_group, result, 'embeddings', decision_trail if return_decision_trail else None)
        else:
            decision_trail.append({'method': 'embeddings', 'result': None})
        
        # Method 5: LLM (always returns a result)
        result = self.llm_matcher.match(primary_group)
        decision_trail.append({'method': 'llm', 'result': result})
        
        return self._format_result(primary_group, result, 'llm', decision_trail if return_decision_trail else None)
    
    def _format_result(
        self, 
        primary_group: str, 
        match_result: Dict[str, Any], 
        method: str,
        decision_trail: Optional[List] = None
    ) -> Dict[str, Any]:
        
        self.session_stats['predictions_made'] += 1
        self.session_stats['method_distribution'][method] += 1
        
        if match_result['confidence'] < config.THRESHOLDS['review']:
            self.session_stats['needs_review_count'] += 1
        
        # Extract matched training row name
        matched_name = match_result.get('matched_training_row', '')
        
        # If not provided, extract from matched_row dict
        if not matched_name and match_result.get('matched_row'):
            matched_name = match_result['matched_row'].get('primary_group', '')
        
        # For LLM, explicitly mark it
        if method == 'llm' and not matched_name:
            matched_name = 'LLM prediction'
        
        # Get predicted columns - either from match_result or create default
        predicted_columns = match_result.get('predicted_columns', {
            'fs': match_result['predicted_fs'],
            'bs_main_category': None,
            'bs_classification': None,
            'bs_sub_classification': None,
            'bs_sub_classification_2': None,
            'pl_classification': None,
            'pl_sub_classification': None,
            'pl_classification_1': None,
            'cf_classification': None,
            'cf_sub_classification': None,
            'expense_type': None
        })
        
        result = create_result_dict(
            primary_group=primary_group,
            predicted_fs=match_result['predicted_fs'],
            confidence=match_result['confidence'],
            method_used=method,
            matched_training_row=matched_name,
            matched_row_data=match_result.get('matched_row'),
            reasoning=match_result.get('reasoning', ''),
            predicted_columns=predicted_columns  # ← NOW PASSING ALL 12 COLUMNS
        )
        
        if decision_trail:
            result['decision_trail'] = decision_trail
        
        return result
        
    def predict_batch(
        self, 
        input_file: Path, 
        output_file: Path = None,
        resume: bool = False,
        progress_callback = None
    ) -> Dict[str, Any]:
        """
        Process batch of primary groups from Excel file
        
        Args:
            input_file: Path to input Excel file
            output_file: Path to output Excel file (auto-generated if None)
            resume: If True, resume from checkpoint
            progress_callback: Function to call with progress updates (row_num, total_rows, current_item)
            
        Returns:
            Dictionary with batch processing results
        """
        # Check for existing checkpoint
        checkpoint_data = None
        if resume and config.PROGRESS_CHECKPOINT.exists():
            try:
                with open(config.PROGRESS_CHECKPOINT, 'r') as f:
                    checkpoint_data = json.load(f)
            except:
                checkpoint_data = None
        
        # Read input file
        df = pd.read_excel(input_file)
        
        if 'primary_group' not in df.columns:
            return {
                'success': False,
                'message': 'Input file must have "primary_group" column',
                'processed_count': 0
            }
        
        # Initialize results
        if checkpoint_data and checkpoint_data.get('input_file') == str(input_file):
            results = checkpoint_data['results']
            start_idx = checkpoint_data['last_processed_idx'] + 1
            print(f"Resuming from row {start_idx + 1}...")
        else:
            results = []
            start_idx = 0
        
        total_rows = len(df)
        
        # Process each row
        for idx in range(start_idx, total_rows):
            primary_group = df.iloc[idx]['primary_group']
            
            # Skip null values
            if pd.isna(primary_group):
                continue
            
            # Make prediction
            result = self.predict_single(str(primary_group))
            results.append(result)
            
            # Progress callback
            if progress_callback:
                progress_callback(idx + 1, total_rows, primary_group)
            
            # Save checkpoint every N rows
            if (idx + 1) % config.CHECKPOINT_INTERVAL == 0:
                self._save_checkpoint(input_file, results, idx)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = config.BATCH_OUTPUT_DIR / f"predictions_{timestamp}.xlsx"
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save results
        output_df.to_excel(output_file, index=False)
        
        # Delete checkpoint on successful completion
        if config.PROGRESS_CHECKPOINT.exists():
            config.PROGRESS_CHECKPOINT.unlink()
        
        return {
            'success': True,
            'message': f'Processed {len(results)} rows successfully',
            'processed_count': len(results),
            'output_file': output_file,
            'stats': self._get_batch_stats(results)
        }
    
    def _save_checkpoint(self, input_file: Path, results: List[Dict], last_idx: int):
        """Save progress checkpoint"""
        checkpoint = {
            'input_file': str(input_file),
            'last_processed_idx': last_idx,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(config.PROGRESS_CHECKPOINT, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def _get_batch_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from batch results"""
        if not results:
            return {}
        
        method_counts = {}
        needs_review_count = 0
        total_confidence = 0
        
        for result in results:
            method = result['method_used']
            method_counts[method] = method_counts.get(method, 0) + 1
            
            if result['needs_review']:
                needs_review_count += 1
            
            total_confidence += result['confidence']
        
        return {
            'total_processed': len(results),
            'method_distribution': method_counts,
            'needs_review_count': needs_review_count,
            'needs_review_percentage': (needs_review_count / len(results)) * 100,
            'average_confidence': total_confidence / len(results),
            'llm_calls': method_counts.get('llm', 0)
        }
    
    def check_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Check if there's an incomplete batch to resume
        
        Returns:
            Dictionary with checkpoint info or None
        """
        if not config.PROGRESS_CHECKPOINT.exists():
            return None
        
        try:
            with open(config.PROGRESS_CHECKPOINT, 'r') as f:
                checkpoint = json.load(f)
            
            return {
                'exists': True,
                'input_file': checkpoint['input_file'],
                'processed_rows': checkpoint['last_processed_idx'] + 1,
                'timestamp': checkpoint['timestamp']
            }
        except:
            return None
    
    def refresh_training_data(self) -> Dict[str, Any]:
        """
        Refresh training data from Excel
        
        Returns:
            Dictionary with refresh status
        """
        result = self.data_loader.load_training_data(force_refresh=True)
        
        if result['success']:
            # Refresh all matchers
            training_data = result['data']
            self.exact_matcher.refresh(training_data)
            self.fuzzy_matcher.refresh(training_data)
            self.semantic_matcher.refresh(training_data)
            self.embedding_matcher.refresh(training_data)
        
        return result
    
    def add_to_training_data(self, primary_group: str, fs: str) -> Dict[str, Any]:
        """
        Add new entry to training data
        
        Args:
            primary_group: Primary group name
            fs: Financial statement classification
            
        Returns:
            Dictionary with status
        """
        result = self.data_loader.add_training_row(primary_group, fs)
        
        if result['success']:
            # Refresh matchers with new data
            self.refresh_training_data()
        
        return result
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training data statistics"""
        return self.data_loader.get_stats()
    
    def search_training_data(self, query: str) -> pd.DataFrame:
        """Search training data"""
        return self.data_loader.search_training_data(query)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        stats = self.session_stats.copy()
        stats['llm_stats'] = self.llm_matcher.get_stats()
        return stats
    
    def update_domain(self, domain: str):
        """Update company domain"""
        self.domain = domain
        self.llm_matcher.update_domain(domain)
