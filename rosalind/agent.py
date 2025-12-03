# rosalind/agent.py
from __future__ import annotations

from typing import Optional, Dict, Any, List, TypedDict, Annotated
import operator

import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AnyMessage
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# These are the correct 2025 imports — no more langchain.chat_models or .llms
from langchain_community.tools import PythonREPLTool

# Your custom tools and prompts
from rosalind.prompts import SYSTEM_PROMPT
from rosalind.memory import ConversationMemory
from rosalind.tools import (
    load_data, clean_data,
    plot, create_line_chart, create_bar_chart, create_scatter_chart,
    create_dashboard, create_dax_snippets
)
class RosalindAgent:
    """
    Rosalind – Fully Autonomous AI Data Analyst
    One line → Full analysis, charts, DAX, insights
    """
    
    def __init__(
        self,
        model: str = "grok-beta",
        temperature: float = 0.1,
        verbose: bool = True
    ):
        self.memory = ConversationMemory()
        self.verbose = verbose
        self._llm = None
        self._model_name = model
        self._temperature = temperature
        self._agent_executor: Optional[Runnable] = None

    @property
    def llm(self):
        if self._llm is None:
            self._build_llm()
        return self._llm

    def _build_llm(self):
        try:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(model=self._model_name, temperature=self._temperature)
            if self.verbose: print(f"Connected to Groq ({self._model_name})")
        except:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(model=self._model_name, temperature=self._temperature)
                if self.verbose: print(f"Connected to OpenAI ({self._model_name})")
            except:
                from langchain_ollama import ChatOllama
                self._llm = ChatOllama(model=self._model_name, temperature=self._temperature)
                if self.verbose: print(f"Connected to Ollama ({self._model_name})")

    def _get_tools(self):
        """All tools the agent can use"""
        return [
            load_data,
            clean_data,
            plot,
            create_line_chart,
            create_bar_chart,
            create_scatter_chart,
            create_dashboard,
            create_dax_snippets
        ]

    def _create_agent(self) -> Runnable:
        tools = self._get_tools()
        llm_with_tools = self.llm.bind_tools(tools)

        system_msg = SystemMessage(content=SYSTEM_PROMPT)

        def agent_node(state):
            messages = [system_msg] + state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        builder = StateGraph(Dict)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", ToolNode(tools))

        builder.set_entry_point("agent")
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")

        return builder.compile()

    def analyze(
        self,
        file_path: Optional[str] = None,
        question: str = "",
        df: Optional[pd.DataFrame] = None,
        filename: str = "data.csv"
    ) -> str:
        if not self._agent_executor:
            self._agent_executor = self._create_agent()
            if self.verbose: print("Rosalind agent ready")

        # Load data if provided
        if file_path:
            df_raw, info = load_data(file_path)
            df_clean, summary = clean_data(df_raw)
            self.memory.set_dataframe(df_clean, filename)
            if self.verbose:
                print(f"{info}\n{summary}")

        if not question.strip():
            return "Please ask a question about the data."

        # Build context
        context = f"""
Dataset: {self.memory.dataset_summary}
Past questions: {len(self.memory.memory_entries)}
Current question: {question}
        """.strip()

        if self.verbose:
            print("\nRosalind is analyzing...\n")

        result = self._agent_executor.invoke({
            "messages": [HumanMessage(content=f"{context}\n\nQuestion: {question}")]
        })

        final_answer = result["messages"][-1].content
        print(final_answer)

        # Save interaction
        self.memory.add_interaction(question, final_answer)

        return final_answer

    def chat(self, question: str) -> str:
        """Continue conversation without reloading data"""
        return self.analyze(question=question)
