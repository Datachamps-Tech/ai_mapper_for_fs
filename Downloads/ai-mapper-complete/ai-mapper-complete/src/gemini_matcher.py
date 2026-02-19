# src/gemini_matcher.py
"""
Gemini Match Approach (Method 5 Alternative)
Uses Google Gemini (flash-lite) for intelligent accounting classification
"""

import json
import time
import os
from typing import Dict, Any

import google.generativeai as genai
import config


class GeminiMatcher:
    """LLM-based matcher using Google Gemini"""

    def __init__(self, api_key: str = None, domain: str = "General Business"):
        """
        Initialize Gemini matcher

        Args:
            api_key: Google API key (env GOOGLE_API_KEY if None)
            domain: Company domain for accounting context
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided and not found in environment")

        genai.configure(api_key=self.api_key)

        # Fast + cheap model
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)

        self.call_count = 0
        self.total_cost = 0.0  # kept for interface parity

    # ------------------------------------------------------------------ #
    # PUBLIC API
    # ------------------------------------------------------------------ #

    def match(self, primary_group: str) -> Dict[str, Any]:
        """
        Classify a primary group using Gemini with retry + fallback

        Returns:
            Dict compatible with AIMapper._format_result()
        """
        for attempt in range(config.LLM_MAX_RETRIES):
            try:
                result = self._call_gemini(primary_group)
                self.call_count += 1
                return result

            except Exception as e:
                if attempt < config.LLM_MAX_RETRIES - 1:
                    wait_time = config.LLM_RETRY_DELAY * (2 ** attempt)
                    print(
                        f"Gemini API error "
                        f"(attempt {attempt + 1}/{config.LLM_MAX_RETRIES}): {e}"
                    )
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(
                        f"Gemini API failed after "
                        f"{config.LLM_MAX_RETRIES} attempts: {e}"
                    )
                    return self._fallback_result()

    # ------------------------------------------------------------------ #
    # INTERNALS
    # ------------------------------------------------------------------ #

    def _call_gemini(self, primary_group: str) -> Dict[str, Any]:
        """
        Perform the actual Gemini API call and return parsed output
        """

        user_message = (
            f"Classify this accounting line item with ALL 12 columns:\n"
            f"{primary_group}"
        )

        full_prompt = f"{self.system_prompt}\n\n{user_message}"

        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=4000,
                response_mime_type="application/json",
            ),
        )

        # Gemini SDK guarantees aggregated text here
        if not response or not response.text:
            raise ValueError("Gemini returned empty response")

        raw_text = response.text.strip()

        # ---------------- PARSE JSON ---------------- #

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            raise ValueError(f"Gemini returned invalid JSON: {raw_text[:500]}")

        # 🔴 CRITICAL FIX: Gemini may return a LIST
        if isinstance(parsed, list):
            if not parsed:
                raise ValueError("Gemini returned empty JSON list")
            parsed = parsed[0]

        if not isinstance(parsed, dict):
            raise ValueError(
                f"Gemini returned unexpected JSON type: {type(parsed)}"
            )

        # ---------------- VALIDATION ---------------- #

        fs = parsed.get("fs")
        if fs not in config.VALID_FS_VALUES:
            raise ValueError(f"Invalid or missing fs value: {fs}")

        confidence = parsed.get("confidence", 0.8)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            confidence = 0.8

        # ---------------- NORMALIZATION ---------------- #

        def clean_null(val):
            if val in ("null", "", "None", None):
                return None
            return val

        # Enforce mandatory hierarchy rules
        if fs == "Profit & Loss":
            parsed["bs_main_category"] = "Equity And Liabilities"
            parsed["bs_classification"] = "Capital A/c"
            parsed["bs_sub_classification"] = "Reserve and Surplus"
            parsed["bs_sub_classification_2"] = "1. Capital"

        if fs == "Balance Sheet":
            parsed["pl_classification"] = None
            parsed["pl_sub_classification"] = None
            parsed["pl_classification_1"] = None
            parsed["expense_type"] = None

        predicted_columns = {
            "fs": fs,
            "bs_main_category": clean_null(parsed.get("bs_main_category")),
            "bs_classification": clean_null(parsed.get("bs_classification")),
            "bs_sub_classification": clean_null(parsed.get("bs_sub_classification")),
            "bs_sub_classification_2": clean_null(parsed.get("bs_sub_classification_2")),
            "pl_classification": clean_null(parsed.get("pl_classification")),
            "pl_sub_classification": clean_null(parsed.get("pl_sub_classification")),
            "pl_classification_1": clean_null(parsed.get("pl_classification_1")),
            "cf_classification": clean_null(parsed.get("cf_classification")),
            "cf_sub_classification": clean_null(parsed.get("cf_sub_classification")),
            "expense_type": clean_null(parsed.get("expense_type")),
        }

        return {
            "predicted_fs": fs,
            "confidence": float(confidence),
            "reasoning": parsed.get("reasoning", "Gemini classification"),
            "matched_row": None,
            "matched_training_row": "Gemini prediction",
            "predicted_columns": predicted_columns,
        }

    # ------------------------------------------------------------------ #
    # FALLBACKS & UTILITIES
    # ------------------------------------------------------------------ #

    def _fallback_result(self) -> Dict[str, Any]:
        """Return deterministic fallback on total failure"""
        predicted_fs = config.DEFAULT_PREDICTION["predicted_fs"]

        predicted_columns = self._get_default_columns()
        predicted_columns["fs"] = predicted_fs  # prevent fs drift

        return {
            "predicted_fs": predicted_fs,
            "confidence": config.DEFAULT_PREDICTION["confidence"],
            "reasoning": config.DEFAULT_PREDICTION["reasoning"],
            "matched_row": None,
            "matched_training_row": "Gemini prediction (failed)",
            "predicted_columns": predicted_columns,
        }

    def _get_default_columns(self) -> Dict[str, Any]:
        return {
            "fs": None,
            "bs_main_category": None,
            "bs_classification": None,
            "bs_sub_classification": None,
            "bs_sub_classification_2": None,
            "pl_classification": None,
            "pl_sub_classification": None,
            "pl_classification_1": None,
            "cf_classification": None,
            "cf_sub_classification": None,
            "expense_type": None,
        }

    def update_domain(self, domain: str):
        """Update domain context"""
        self.domain = domain
        self.system_prompt = config.get_llm_system_prompt(domain)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "call_count": self.call_count,
            "total_cost": self.total_cost,
            "domain": self.domain,
            "model": "gemini-2.0-flash-lite",
        }

    def reset_stats(self):
        self.call_count = 0
        self.total_cost = 0.0
