import copy

from agent import run_agent
from tools import DataTools


class FakeClient:
    """Plays back scripted model replies, so tests need no network or API key."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def generate(self, contents, system, tool_declarations):
        self.seen.append(copy.deepcopy(contents))
        return self.replies.pop(0)


def text(t):
    return {"role": "model", "parts": [{"text": t}]}


def call(name, **args):
    return {"role": "model", "parts": [{"functionCall": {"name": name, "args": args}}]}


def make_tools():
    return DataTools("titanic.csv", table="passengers")


def test_answers_directly_without_tools():
    result = run_agent("hi", make_tools(), FakeClient([text("Hello")]))
    assert result["answer"] == "Hello"
    assert result["steps"] == []


def test_runs_tool_then_answers():
    client = FakeClient([
        call("run_sql", query="SELECT COUNT(*) FROM passengers"),
        text("There are 891 passengers."),
    ])
    result = run_agent("How many passengers?", make_tools(), client)
    assert result["answer"] == "There are 891 passengers."
    assert result["steps"][0]["tool"] == "run_sql"
    assert result["steps"][0]["result"]["rows"] == [[891]]
    last_user_turn = client.seen[1][-1]
    assert last_user_turn["parts"][0]["functionResponse"]["name"] == "run_sql"


def test_tool_error_is_returned_to_the_model():
    client = FakeClient([call("run_sql", query="DROP TABLE passengers"), text("I cannot do that.")])
    result = run_agent("delete it", make_tools(), client)
    assert "error" in result["steps"][0]["result"]
    assert result["answer"] == "I cannot do that."


def test_unknown_tool():
    client = FakeClient([call("hack_the_planet"), text("ok")])
    result = run_agent("x", make_tools(), client)
    assert "error" in result["steps"][0]["result"]


def test_stops_after_max_steps():
    client = FakeClient([call("describe_table") for _ in range(10)])
    result = run_agent("loop forever", make_tools(), client, max_steps=3)
    assert len(result["steps"]) == 3
    assert "maximum" in result["answer"]


def test_model_reply_is_kept_exactly_as_received():
    reply = {"role": "model", "parts": [
        {"functionCall": {"name": "describe_table", "args": {}}, "thoughtSignature": "sig123"}
    ]}
    client = FakeClient([reply, text("done")])
    run_agent("x", make_tools(), client)
    assert client.seen[1][1]["parts"][0]["thoughtSignature"] == "sig123"
