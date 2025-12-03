# rosalind/agent.py
from __future__ import annotations

from typing import Optional, List, TypedDict, Annotated
import operator

import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# Tools — PythonREPLTool moved to community in 0.3+
from langchain_community.tools import PythonREPLTool

from rosalind.prompts import SYSTEM_PROMPT
from rosalind.memory import ConversationMemory
from rosalind.tools import (
    load_data, clean_data,
    plot, create_line_chart, create_bar_chart, create_scatter_chart,
    create_dashboard, create_dax_snippets
)


# ─────────────────────────────── State Definition ───────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    memory: Optional[ConversationMemory]


class RosalindAgent:
    def __init__(
        self,
        openai_api_key: str,
        memory: Optional[ConversationMemory] = None,
        verbose: bool = False
    ):
        self.memory = memory or ConversationMemory()
        self.verbose = verbose
        self._agent_executor = None

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=openai_api_key,
        )

        # All tools
        tools = [
            load_data, clean_data,
            plot, create_line_chart, create_bar_chart, create_scatter_chart,
            create_dashboard, create_dax_snippets,
            PythonREPLTool(),
        ]

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(tools)

        # ────────────────────────── LangGraph Workflow ──────────────────────────
        def agent_node(state: AgentState):
            messages = state["messages"]

            # Inject conversation memory
            if self.memory and len(self.memory.buffer) > 0:
                messages = self.memory.buffer + messages

            # System prompt
            system_msg = SystemMessage(content=SYSTEM_PROMPT)
            response = llm_with_tools.invoke([system_msg] + messages)
            return {"messages": [response]}

        # Build graph
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(tools))

        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")

        self._agent_executor = workflow.compile()

    def analyze(
        self,
        file_path: Optional[str] = None,
        question: str = "",
        df: Optional[pd.DataFrame] = None,
        filename: str = "data.csv"
    ) -> str:
        if not question.strip():
            return "Please ask a question about the data."

        # Load and clean data if file provided
        if file_path:
            df_raw, info = load_data(file_path)
            df_clean, summary = clean_data(df_raw)
            self.memory.set_dataframe(df_clean, filename)
            if self.verbose:
                print(f"{info}\n{summary}")

        # Build context
        context = f"""
Dataset: {self.memory.dataset_summary or "No data loaded yet"}
Past questions: {len(self.memory.memory_entries)}
Current question: {question}
        """.strip()

        if self.verbose:
            print("\nRosalind is analyzing...\n")

        # Run agent
        result = self._agent_executor.invoke({
            "messages": [HumanMessage(content=f"{context}\n\nQuestion: {question}")],
            "memory": self.memory
        })

        final_answer = result["messages"][-1].content

        if self.verbose:
            print(final_answer)

        # Save to memory
        self.memory.add_interaction(question, final_answer)

        return final_answer

    def chat(self, question: str) -> str:
        """Continue conversation without reloading data"""
        return self.analyze(question=question)
