import sys

from agent import run_agent
from llm import GeminiClient
from tools import DataTools

question = " ".join(sys.argv[1:]) or "What percentage of passengers survived?"
tools = DataTools("titanic.csv", table="passengers")
result = run_agent(question, tools, GeminiClient())

for i, step in enumerate(result["steps"], start=1):
    print(f"[{i}] {step['tool']} {step['args']}")
print()
print(result["answer"])
