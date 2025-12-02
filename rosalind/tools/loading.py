# rosalind/tools/loading.py
import pandas as pd
from pathlib import Path
from typing import Tuple

def load_data(file_path: str) -> Tuple[pd.DataFrame, str]:
    """
    Load CSV or Excel file. Returns dataframe and a short description.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() in [".csv"]:
        df = pd.read_csv(path)
    elif path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        raise ValueError("Supported formats: CSV, XLSX")

    info = f"Loaded {path.name}: {df.shape[0]:,} rows × {df.shape[1]} columns"
    return df, info
