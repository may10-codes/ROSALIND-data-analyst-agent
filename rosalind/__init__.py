# rosalind/__init__.py

"""
Rosalind – Your AI Data Analyst Agent
=====================================

Turn CSV/Excel files into insights, charts, and Power BI DAX using natural language.

Main classes:
    - RosalindAgent : The main entry point
"""

# Version of the package
__version__ = "0.1.0"

# When someone does `from rosalind import RosalindAgent`
from .agent import RosalindAgent

# Optional: expose other high-level objects later
# from .memory import ConversationMemory
# from .tools import ...

__all__ = ["RosalindAgent"]
