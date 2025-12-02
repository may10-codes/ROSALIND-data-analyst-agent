# rosalind/tools/visualization.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
import json

# Ensure output directory exists
OUTPUT_DIR = Path("outputs/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _save_fig(fig, prefix: str = "chart") -> str:
    """Helper to save figure and return filename"""
    filename = OUTPUT_DIR / f"{prefix}_{uuid.uuid4().hex[:8]}.html"
    fig.write_html(filename, include_plotlyjs="cdn")
    print(f"Chart saved: {filename.name}")
    return str(filename.name)

def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "Trend Over Time",
    color: Optional[str] = None,
    hover_data: Optional[list] = None
) -> str:
    fig = px.line(
        df, x=x, y=y, color=color, title=title,
        hover_data=hover_data, template="simple_white"
    )
    fig.update_layout(height=600, hovermode="x unified")
    return _save_fig(fig, "line")

def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "Comparison",
    color: Optional[str] = None,
    text_auto: bool = True
) -> str:
    fig = px.bar(
        df, x=x, y=y, color=color, title=title,
        text_auto=text_auto, template="simple_white"
    )
    fig.update_layout(height=600)
    return _save_fig(fig, "bar")

def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "Correlation",
    color: Optional[str] = None,
    size: Optional[str] = None,
    trendline: Optional[str] = "ols"
) -> str:
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        trendline=trendline, trendline_color_override="red",
        title=title, template="simple_white"
    )
    fig.update_layout(height=600)
    return _save_fig(fig, "scatter")

def create_dashboard(
    df: pd.DataFrame,
    metrics: Dict[str, Dict[str, Any]],
    title: str = "Rosalind Executive Dashboard"
) -> str:
    """
    metrics = {
        "Total Revenue": {"current": 1250000, "previous": 980000},
        "Growth Rate": {"current": 27.6, "previous": 0, "suffix": "%"},
        "Top Region Sales": {"data": top_df}
    }
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=list(metrics.keys())[:4],
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "bar", "colspan": 2}, None]],
        vertical_spacing=0.15
    )

    # Top 2 indicators
    for i, (label, val) in enumerate(list(metrics.items())[:2]):
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=val["current"],
            delta={"reference": val.get("previous", 0)},
            title={"text": label},
            number={"valueformat": ",.0f", "suffix": val.get("suffix", "")}
        ), row=1, col=i+1)

    # Bar chart (3rd subplot)
    if len(metrics) >= 3:
        bar_key = list(metrics.keys())[2]
        bar_data = metrics[bar_key].get("data")
        if bar_data is not None and isinstance(bar_data, pd.DataFrame):
            fig.add_trace(go.Bar(
                x=bar_data.iloc[:, 0], y=bar_data.iloc[:, 1],
                name=bar_key
            ), row=2, col=1)

    fig.update_layout(height=800, title_text=title, showlegend=False)
    return _save_fig(fig, "dashboard")
