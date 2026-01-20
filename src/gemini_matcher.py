# src/gemini_matcher.py
"""
Gemini Match Approach (Method 5 Alternative)
Uses Google Gemini 2.5 Flash Lite for intelligent classification
"""

import json
import time
import os
from typing import Dict, Any
import google.generativeai as genai
import config


class GeminiMatcher:
    """LLM-based matching using Google Gemini"""
    
    def __init__(self, api_key: str = None, domain: str = "General Business"):
        """
        Initialize Gemini matcher
        
        Args:
            api_key: Google API key (uses env default if None)
            domain: Company domain for context
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API key not provided and not found in environment")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use gemini-2.0-flash-lite (faster, cheaper)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)
        self.call_count = 0
        self.total_cost = 0.0
    
    def match(self, primary_group: str) -> Dict[str, Any]:
        """
        Use Gemini to classify primary group
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Dictionary with prediction
        """
        for attempt in range(config.LLM_MAX_RETRIES):
            try:
                result = self._call_gemini(primary_group)
                self.call_count += 1
                return result
                
            except Exception as e:
                if attempt < config.LLM_MAX_RETRIES - 1:
                    wait_time = config.LLM_RETRY_DELAY * (2 ** attempt)
                    print(f"Gemini API error (attempt {attempt + 1}/{config.LLM_MAX_RETRIES}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Gemini API failed after {config.LLM_MAX_RETRIES} attempts: {e}")
                    return {
                        'predicted_fs': config.DEFAULT_PREDICTION['predicted_fs'],
                        'confidence': config.DEFAULT_PREDICTION['confidence'],
                        'reasoning': config.DEFAULT_PREDICTION['reasoning'],
                        'matched_row': None,
                        'matched_training_row': 'Gemini prediction (failed)',
                        'predicted_columns': self._get_default_columns()
                    }
    
    def _call_gemini(self, primary_group: str) -> Dict[str, Any]:
        """
        Make actual API call to Gemini
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Parsed result with all 12 columns
        """
        user_message = f"Classify this accounting line item with ALL 12 columns: {primary_group}"
        
        # Combine system prompt + user message
        full_prompt = f"{self.system_prompt}\n\n{user_message}"
        
        # Call Gemini with generation config
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,  # Deterministic
                max_output_tokens=4000,  # More than GPT's 2000
                response_mime_type="application/json"  # Force JSON output
            )
        )
        
        # Extract response
        content = response.text.strip()
        
        # Parse JSON
        try:
            result = json.loads(content)
            if result['fs'] == 'Profit & Loss':
                result['bs_main_category'] = "Equity And Liabilities"
                result['bs_classification'] = "Capital A/c"
                result['bs_sub_classification'] = "Reserve and Surplus"
                result['bs_sub_classification_2'] = "1. Capital"

            if result['fs'] == 'Balance Sheet':
                result['pl_classification'] = None
                result['pl_sub_classification'] = None
                result['pl_classification_1'] = None

            # Validate
            if 'fs' not in result:
                raise ValueError("Response missing 'fs' field")
            
            if result['fs'] not in config.VALID_FS_VALUES:
                raise ValueError(f"Invalid fs value: {result['fs']}")
            
            confidence = result.get('confidence', 0.8)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                confidence = 0.8
            
            # Clean nulls
            def clean_null(value):
                if value in ("null", "", "None", None):
                    return None
                return value
            
            # Extract all 12 columns
            predicted_columns = {
                'fs': result['fs'],
                'bs_main_category': clean_null(result.get('bs_main_category')),
                'bs_classification': clean_null(result.get('bs_classification')),
                'bs_sub_classification': clean_null(result.get('bs_sub_classification')),
                'bs_sub_classification_2': clean_null(result.get('bs_sub_classification_2')),
                'pl_classification': clean_null(result.get('pl_classification')),
                'pl_sub_classification': clean_null(result.get('pl_sub_classification')),
                'pl_classification_1': clean_null(result.get('pl_classification_1')),
                'cf_classification': clean_null(result.get('cf_classification')),
                'cf_sub_classification': clean_null(result.get('cf_sub_classification')),
                'expense_type': clean_null(result.get('expense_type'))
            }
            
            return {
                'predicted_fs': result['fs'],
                'confidence': float(confidence),
                'reasoning': result.get('reasoning', 'Gemini classification'),
                'matched_row': None,
                'matched_training_row': 'Gemini prediction',
                'predicted_columns': predicted_columns
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {content[:500]}") from e
        except KeyError as e:
            raise ValueError(f"Gemini response missing required field: {e}") from e
    
    def _get_default_columns(self):
        """Return default empty columns"""
        return {
            'fs': 'Profit & Loss',
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
    
    def update_domain(self, domain: str):
        """Update company domain and regenerate system prompt"""
        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'call_count': self.call_count,
            'total_cost': self.total_cost,
            'domain': self.domain,
            'model': 'gemini-2.0-flash-lite'
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        self.call_count = 0
        self.total_cost = 0.0