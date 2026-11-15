TOOL_DECLARATIONS = [
    {
        "name": "describe_table",
        "description": "Get the table name, row count, column names and types, and 3 sample rows. Call this first if you are unsure about the schema.",
    },
    {
        "name": "run_sql",
        "description": "Run one read-only SQLite SELECT query on the table and return columns and rows (max 50 rows).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A single SQLite SELECT statement."}
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are a careful data analyst. Answer questions about the user's table by calling the tools. "
    "Use describe_table if you do not know the columns. Write SQLite SQL and call run_sql. "
    "If a tool returns an error, fix your query and try again. "
    "Base your answer only on tool results, never invent numbers, and keep the final answer short."
)


def call_tool(tools, name, args):
    if name == "describe_table":
        return tools.describe()
    if name == "run_sql":
        return tools.run_sql(args.get("query", ""))
    return {"error": f"Unknown tool: {name}"}


def run_agent(question, tools, client, max_steps=6):
    contents = [{"role": "user", "parts": [{"text": question}]}]
    steps = []

    for _ in range(max_steps):
        reply = client.generate(contents, SYSTEM_PROMPT, TOOL_DECLARATIONS)
        contents.append(reply)  # keep the model's content exactly as received

        parts = reply.get("parts", [])
        calls = [p["functionCall"] for p in parts if "functionCall" in p]
        if not calls:
            answer = "".join(p.get("text", "") for p in parts).strip()
            return {"answer": answer, "steps": steps}

        responses = []
        for call in calls:
            name, args = call["name"], call.get("args", {})
            result = call_tool(tools, name, args)
            steps.append({"tool": name, "args": args, "result": result})
            responses.append({"functionResponse": {"name": name, "response": result}})
        contents.append({"role": "user", "parts": responses})

    return {"answer": "Stopped: reached the maximum number of steps.", "steps": steps}
