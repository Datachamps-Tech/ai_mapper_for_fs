"""
Utility functions for AI Accounting Mapper
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import config


def normalize(text: str) -> str:
    """
    Normalize text for matching (lowercase + strip whitespace)
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return ""
    return text.lower().strip()


def validate_excel_file(file_path: Path, required_column: str = 'primary_group') -> Dict[str, Any]:
    """
    Validate uploaded Excel file
    
    Args:
        file_path: Path to Excel file
        required_column: Column that must exist
        
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'message': str,
            'data': pd.DataFrame or None,
            'row_count': int
        }
    """
    try:
        # Check file exists
        if not file_path.exists():
            return {
                'valid': False,
                'message': f'File not found: {file_path}',
                'data': None,
                'row_count': 0
            }
        
        # Try to read Excel
        df = pd.read_excel(file_path)
        
        # Check if empty
        if df.empty:
            return {
                'valid': False,
                'message': 'File is empty',
                'data': None,
                'row_count': 0
            }
        
        # Check for required column
        if required_column not in df.columns:
            return {
                'valid': False,
                'message': f'Missing required column: "{required_column}"',
                'data': None,
                'row_count': 0
            }
        
        # Remove rows where required column is null
        original_count = len(df)
        df = df[df[required_column].notna()]
        removed_count = original_count - len(df)
        
        if df.empty:
            return {
                'valid': False,
                'message': f'All rows have null values in "{required_column}" column',
                'data': None,
                'row_count': 0
            }
        
        message = f'Valid file with {len(df)} rows'
        if removed_count > 0:
            message += f' ({removed_count} null rows removed)'
        
        return {
            'valid': True,
            'message': message,
            'data': df,
            'row_count': len(df)
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error reading file: {str(e)}',
            'data': None,
            'row_count': 0
        }


def validate_training_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate training data structure
    
    Args:
        df: Training data DataFrame
        
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'stats': Dict
        }
    """
    errors = []
    warnings = []
    
    # Check required columns
    missing_columns = [col for col in config.REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for empty values in required columns
    if not errors:
        for col in config.REQUIRED_COLUMNS:
            null_count = df[col].isna().sum()
            if null_count > 0:
                warnings.append(f"Column '{col}' has {null_count} empty values")
    
    # Check for invalid fs values
    if 'fs' in df.columns:
        invalid_fs = df[~df['fs'].isin(config.VALID_FS_VALUES + [None])]['fs'].unique()
        if len(invalid_fs) > 0:
            warnings.append(f"Invalid fs values found: {', '.join(map(str, invalid_fs))}")
    
    # Check for duplicates
    if 'primary_group' in df.columns:
        duplicates = df[df['primary_group'].duplicated(keep=False)]
        if not duplicates.empty:
            dup_count = len(duplicates['primary_group'].unique())
            warnings.append(f"Found {dup_count} duplicate primary_group entries")
    
    # Calculate stats
    stats = {
        'total_rows': len(df),
        'bs_count': len(df[df['fs'] == 'Balance Sheet']) if 'fs' in df.columns else 0,
        'pl_count': len(df[df['fs'] == 'Profit & Loss']) if 'fs' in df.columns else 0,
    }
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'stats': stats
    }


def format_confidence(confidence: float) -> str:
    """
    Format confidence as percentage
    
    Args:
        confidence: Float between 0 and 1
        
    Returns:
        Formatted string like "85.5%"
    """
    return f"{confidence * 100:.1f}%"


def get_opposite_fs(fs: str) -> str:
    """
    Get the opposite financial statement
    
    Args:
        fs: Either "Balance Sheet" or "Profit & Loss"
        
    Returns:
        The opposite FS
    """
    return "Profit & Loss" if fs == "Balance Sheet" else "Balance Sheet"


def should_review(confidence: float, threshold: float = None) -> bool:
    """
    Determine if prediction needs review
    
    Args:
        confidence: Prediction confidence
        threshold: Review threshold (uses config default if None)
        
    Returns:
        True if confidence is below threshold
    """
    if threshold is None:
        threshold = config.THRESHOLDS['review']
    return confidence < threshold


def create_result_dict(
    primary_group: str,
    predicted_fs: str,
    confidence: float,
    method_used: str,
    matched_training_row: Optional[str] = None,
    matched_row_data: Optional[Dict] = None,
    reasoning: str = "",
    predicted_columns: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create standardized result dictionary with all 12 prediction columns
    
    Args:
        primary_group: Original input
        predicted_fs: Predicted financial statement
        confidence: Confidence score
        method_used: Method that produced the result
        matched_training_row: Name of matched training row (if applicable)
        matched_row_data: Full matched row data (if applicable)
        reasoning: LLM reasoning (if applicable)
        predicted_columns: Dictionary with all 12 predicted columns
        
    Returns:
        Standardized result dictionary
    """
    needs_review_flag = should_review(confidence)
    
    # Initialize predicted columns if not provided
    if predicted_columns is None:
        predicted_columns = {
            'fs': predicted_fs,
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
        }
    
    result = {
        'primary_group': primary_group,
        'predicted_fs': predicted_fs,
        'confidence': confidence,
        'method_used': method_used,
        'matched_training_row': matched_training_row or ("LLM prediction" if method_used == "llm" else ""),
        'needs_review': needs_review_flag,
        'low_confidence_alternative': get_opposite_fs(predicted_fs) if needs_review_flag else "",
        'reasoning': reasoning
    }
    
    # Add all 12 predicted columns
    result.update(predicted_columns)
    
    # Add full matched row data if available
    if matched_row_data:
        result['matched_row_full'] = matched_row_data
    
    return result


def get_method_color(method: str) -> str:
    """
    Get color for method badge in UI
    
    Args:
        method: Method name
        
    Returns:
        Hex color code
    """
    method_colors = {
        'exact': config.COLORS['success_green'],
        'fuzzy': config.COLORS['secondary_blue'],
        'semantic': config.COLORS['secondary_blue'],
        'embeddings': config.COLORS['secondary_blue'],
        'llm': config.COLORS['primary_blue']
    }
    return method_colors.get(method, config.COLORS['primary_blue'])


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
