# rosalind/memory.py
import faiss
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path

class ConversationMemory:
    """
    Simple but powerful memory system:
    - Stores the current dataframe (so tools always have access)
    - Stores past Q&A + insights using FAISS vector store
    """
    
    def __init__(self, persist_dir: str = "outputs/memory"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.df: Optional[pd.DataFrame] = None
        self.dataset_name: str = ""
        self.dataset_summary: str = ""
        
        # FAISS index for semantic memory (future-proof)
        self.dimension = 384  # We'll use sentence-transformers later if needed
        self.index = faiss.IndexFlatL2(self.dimension)
        self.memory_entries: List[Dict[str, Any]] = []
        self.next_id = 0

    def set_dataframe(self, df: pd.DataFrame, filename: str = "uploaded_data"):
        """Store the main dataframe that all analysis will use"""
        self.df = df.copy()
        self.dataset_name = filename
        self.dataset_summary = f"{filename} | {df.shape[0]:,} rows × {df.shape[1]} columns | cols: {list(df.columns)}"
        print(f"Memory updated → {self.dataset_summary}")

    def get_dataframe(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No dataset loaded yet. Use load_data tool first.")
        return self.df

    def add_interaction(self, question: str, answer: str, metadata: Dict[str, Any] = None):
        """Store a Q&A pair for future reference"""
        entry = {
            "id": self.next_id,
            "question": question,
            "answer": answer,
            "metadata": metadata or {}
        }
        self.memory_entries.append(entry)
        self.next_id += 1

    def get_recent_interactions(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return last n interactions (for context)"""
        return self.memory_entries[-n:]

    def clear(self):
        """Start fresh"""
        self.df = None
        self.dataset_name = ""
        self.dataset_summary = ""
        self.memory_entries = []
        self.next_id = 0
        print("Memory cleared.")

    def summary(self) -> str:
        if not self.df:
            return "No data loaded."
        return f"Current dataset: {self.dataset_name} | {len(self.memory_entries)} past interactions"
