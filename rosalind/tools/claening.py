# rosalind/tools/cleaning.py
import pandas as pd
import numpy as np
from typing import Dict, List

def detect_and_fix_issues(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Automatically detect and fix common data issues.
    Returns cleaned df + list of actions taken.
    """
    actions = []
    original_shape = df.shape

    # 1. Duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        actions.append(f"Removed {duplicates:,} duplicate rows")

    # 2. Missing values (smart fill)
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype in ['float64', 'int64']:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                actions.append(f"Filled missing numeric values in '{col}' with median ({median_val})")
            else:
                mode_val = df[col].mode()
                if not mode_val.empty:
                    fill_val = mode_val[0]
                    df[col] = df[col].fillna(fill_val)
                    actions.append(f"Filled missing values in '{col}' with mode ('{fill_val}')")

    # 3. Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )
    actions.append("Standardized column names (lowercase, snake_case)")

    # 4. Date parsing
    for col in df.columns:
        if "date" in col or "time" in col or df[col].dtype == "object":
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                if df[col].notna().any():
                    actions.append(f"Converted '{col}' to datetime")
            except:
                pass

    new_shape = df.shape
    if original_shape != new_shape:
        actions.append(f"Shape changed from {original_shape} → {new_shape}")

    return df, actions


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Public function used by the agent: clean + return summary
    """
    df_clean, actions = detect_and_fix_issues(df.copy())
    summary = "Data cleaning complete:\n• " + "\n• ".join(actions) if actions else "No issues detected"
    return df_clean, summary
