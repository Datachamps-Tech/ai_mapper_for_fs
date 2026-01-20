# db/utils.py

import math
from typing import Any


def clean_nan(value: Any):
    """
    Convert NaN / pandas NaT to None.
    Works recursively for dicts.
    """
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, dict):
        return {k: clean_nan(v) for k, v in value.items()}

    return value
