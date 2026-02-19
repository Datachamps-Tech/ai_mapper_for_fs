"""
LLM Match Approach (Method 5)
Uses gpt-5-nano for intelligent classification
"""

import json
import time
from typing import Dict, Any
from openai import OpenAI
import config


class LLMMatcher:
    """LLM-based matching using OpenAI GPT-4"""
    
    def __init__(self, api_key: str = None, domain: str = "General Business"):
        """
        Initialize LLM matcher
        
        Args:
            api_key: OpenAI API key (uses config default if None)
            domain: Company domain for context
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)
        self.call_count = 0
        self.total_cost = 0.0
    
    def match(self, primary_group: str) -> Dict[str, Any]:
        """
        Use LLM to classify primary group
        
        Args:
            primary_group: Input primary group name
            
        Returns:
            Dictionary with prediction:
            {
                'predicted_fs': str,
                'confidence': float (0-1),
                'reasoning': str,
                'matched_row': None,
                'matched_training_row': 'LLM prediction'
            }
        """
        # Attempt with retry logic
        for attempt in range(config.LLM_MAX_RETRIES):
            try:
                result = self._call_llm(primary_group)
                self.call_count += 1
                return result
                
            except Exception as e:
                if attempt < config.LLM_MAX_RETRIES - 1:
                    # Exponential backoff
                    wait_time = config.LLM_RETRY_DELAY * (2 ** attempt)
                    print(f"LLM API error (attempt {attempt + 1}/{config.LLM_MAX_RETRIES}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # All retries failed - return default
                    print(f"LLM API failed after {config.LLM_MAX_RETRIES} attempts: {e}")
                    return {
                        'predicted_fs': config.DEFAULT_PREDICTION['predicted_fs'],
                        'confidence': config.DEFAULT_PREDICTION['confidence'],
                        'reasoning': config.DEFAULT_PREDICTION['reasoning'],
                        'matched_row': None,
                        'matched_training_row': 'LLM prediction (failed)'
                    }
    
    def _call_llm(self, primary_group: str) -> Dict[str, Any]:
        """
        Make actual API call to OpenAI for full 12-column prediction

        Args:
            primary_group: Input primary group name

        Returns:
            Parsed result with all 12 columns from LLM
        """
        user_message = f"Classify this accounting line item with ALL 12 columns: {primary_group}"

        # Call OpenAI API with temperature=0 for deterministic output
        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_completion_tokens=2000  # ← Increased for longer response
        )

        # Extract response
        content = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith('```'):
                lines = content.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json or (not line.strip().startswith('```')):
                        json_lines.append(line)
                content = '\n'.join(json_lines).strip()

            result = json.loads(content)

            # Validate response format
            if 'fs' not in result:
                raise ValueError("Response missing 'fs' field")

            if result['fs'] not in config.VALID_FS_VALUES:
                raise ValueError(f"Invalid fs value: {result['fs']}")

            # Ensure confidence is present and valid
            confidence = result.get('confidence', 0.8)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                confidence = 0.8

            # Helper function to convert "null" strings to actual None
            def clean_null(value):
                if value == "null" or value == "" or value == "None":
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
                'reasoning': result.get('reasoning', 'LLM classification'),
                'matched_row': None,
                'matched_training_row': 'LLM prediction',
                'predicted_columns': predicted_columns  # ← NOW INCLUDES ALL 12 COLUMNS
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {content[:500]}") from e
        except KeyError as e:
            raise ValueError(f"LLM response missing required field: {e}") from e

    def update_domain(self, domain: str):
        """
        Update company domain and regenerate system prompt
        
        Args:
            domain: New company domain
        """
        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'call_count': self.call_count,
            'total_cost': self.total_cost,
            'domain': self.domain
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        self.call_count = 0
        self.total_cost = 0.0
