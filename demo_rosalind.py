# demo_rosalind.py
from rosalind.agent import RosalindAgent

print("Rosalind – Your AI Data Analyst Agent")
print("Starting live demo...\n")

agent = RosalindAgent(model="grok-beta", verbose=True)  # Change to your model

# Test 1 – Sales analysis
agent.analyze(
    file_path="data/sample_sales_2024.csv",
    question="Give me a full executive summary of 2024 performance. Why did December suck? Show me a trend chart and give me DAX for YoY growth."
)

print("\n" + "="*60 + "\n")

# Test 2 – M-Pesa analysis (same session – she remembers!)
agent.chat("Now analyze the M-Pesa data. Who are the top merchants? Where are people withdrawing most? Show a dashboard.")

agent.analyze(
    file_path="data/sample_mpesa_transactions.csv",
    question="Full analysis of M-Pesa transactions. Top merchants, locations, and patterns. Generate a dashboard and DAX for total volume."
)
