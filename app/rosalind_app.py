# app/rosalind_app.py
import streamlit as st
from rosalind.agent import RosalindAgent
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Rosalind – AI Data Analyst", layout="wide")
st.title("Rosalind – Your AI Data Analyst")
st.markdown("**Upload your CSV/Excel → Ask anything → Get insights, charts & DAX**")

agent = RosalindAgent(model="grok-beta", verbose=False)

uploaded_file = st.file_uploader("Upload your data", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.success(f"Loaded {uploaded_file.name} → {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    agent.memory.set_dataframe(df, uploaded_file.name)

    question = st.text_input("Ask Rosalind anything about this data:", placeholder="Why did sales drop in December?")
    
    if st.button("Analyze") and question:
        with st.spinner("Rosalind is thinking..."):
            answer = agent.chat(question)
            st.markdown(answer)
            
            # Show saved charts
            charts = [f for f in os.listdir("outputs/visualizations") if f.endswith(".html")][-3:]
            for chart in charts:
                st.markdown(f"**Chart:** {chart}")
                with open(f"outputs/visualizations/{chart}", "r") as f:
                    st.components.v1.html(f.read(), height=600)
