import sqlite3

import pandas as pd

MAX_ROWS = 50


class DataTools:
    """Read-only tools over a CSV file, to be called by an LLM later."""

    def __init__(self, csv_path, table="data"):
        df = pd.read_csv(csv_path)
        self.table = table
        self.con = sqlite3.connect(":memory:", check_same_thread=False)
        df.to_sql(table, self.con, index=False)
        self.con.execute("PRAGMA query_only = ON")

    def describe(self):
        info = self.con.execute(f"PRAGMA table_info({self.table})").fetchall()
        columns = [{"name": row[1], "type": row[2]} for row in info]
        count = self.con.execute(f"SELECT COUNT(*) FROM {self.table}").fetchone()[0]
        cur = self.con.execute(f"SELECT * FROM {self.table} LIMIT 3")
        names = [d[0] for d in cur.description]
        sample = [dict(zip(names, row)) for row in cur.fetchall()]
        return {"table": self.table, "row_count": count, "columns": columns, "sample": sample}

    def run_sql(self, query):
        q = query.strip().rstrip(";").strip()
        if ";" in q:
            return {"error": "Only a single statement is allowed."}
        if not q.lower().startswith(("select", "with")):
            return {"error": "Only SELECT queries are allowed."}
        try:
            cur = self.con.execute(q)
            columns = [d[0] for d in cur.description]
            rows = cur.fetchmany(MAX_ROWS + 1)
        except sqlite3.Error as e:
            return {"error": str(e)}
        return {
            "columns": columns,
            "rows": [list(r) for r in rows[:MAX_ROWS]],
            "truncated": len(rows) > MAX_ROWS,
        }
