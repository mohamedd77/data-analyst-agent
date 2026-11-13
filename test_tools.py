import pytest

from tools import DataTools


@pytest.fixture
def tools():
    return DataTools("titanic.csv", table="passengers")


def test_describe(tools):
    d = tools.describe()
    assert d["row_count"] == 891
    assert "Survived" in [c["name"] for c in d["columns"]]
    assert len(d["sample"]) == 3


def test_count(tools):
    r = tools.run_sql("SELECT COUNT(*) FROM passengers")
    assert r["rows"] == [[891]]


def test_group_by(tools):
    r = tools.run_sql(
        "SELECT Sex, ROUND(AVG(Survived), 2) FROM passengers GROUP BY Sex ORDER BY Sex"
    )
    assert r["rows"] == [["female", 0.74], ["male", 0.19]]


@pytest.mark.parametrize("bad", [
    "DROP TABLE passengers",
    "DELETE FROM passengers",
    "UPDATE passengers SET Survived = 1",
    "SELECT 1; DROP TABLE passengers",
])
def test_rejects_non_select(tools, bad):
    assert "error" in tools.run_sql(bad)


def test_write_hidden_inside_cte_is_blocked(tools):
    r = tools.run_sql("WITH x AS (SELECT 1) DELETE FROM passengers")
    assert "error" in r
    assert tools.run_sql("SELECT COUNT(*) FROM passengers")["rows"] == [[891]]


def test_row_limit(tools):
    r = tools.run_sql("SELECT * FROM passengers")
    assert len(r["rows"]) == 50
    assert r["truncated"] is True


def test_bad_sql_returns_error(tools):
    assert "error" in tools.run_sql("SELECT nope FROM passengers")
