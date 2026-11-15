import pandas as pd


def build_cases(df: pd.DataFrame):
    """Questions with ground truth computed directly from the data with pandas."""
    oldest = df.loc[df["Age"].idxmax(), "Name"].split(",")[0]
    return [
        {"q": "How many passengers are in the dataset?", "kind": "num", "expected": float(len(df)), "tol": 0},
        {"q": "How many passengers survived?", "kind": "num", "expected": float(df["Survived"].sum()), "tol": 0},
        {"q": "What is the average age of all passengers, rounded to 1 decimal?", "kind": "num",
         "expected": round(df["Age"].mean(), 1), "tol": 0.05},
        {"q": "How many female passengers survived?", "kind": "num",
         "expected": float(df[df["Sex"] == "female"]["Survived"].sum()), "tol": 0},
        {"q": "What percentage of male passengers survived? Round to 1 decimal.", "kind": "num",
         "expected": round(df[df["Sex"] == "male"]["Survived"].mean() * 100, 1), "tol": 0.1},
        {"q": "Which passenger class has the most passengers, and how many?", "kind": "num",
         "expected": float(df["Pclass"].value_counts().iloc[0]), "tol": 0},
        {"q": "What is the highest fare paid? Round to 2 decimals.", "kind": "num",
         "expected": round(df["Fare"].max(), 2), "tol": 0.01},
        {"q": "How many passengers have a missing age?", "kind": "num",
         "expected": float(df["Age"].isna().sum()), "tol": 0},
        {"q": "What is the average fare paid by first class passengers? Round to 2 decimals.", "kind": "num",
         "expected": round(df[df["Pclass"] == 1]["Fare"].mean(), 2), "tol": 0.01},
        {"q": "How many passengers embarked at port S?", "kind": "num",
         "expected": float((df["Embarked"] == "S").sum()), "tol": 0},
        {"q": "How many passengers had at least one sibling or spouse aboard?", "kind": "num",
         "expected": float((df["SibSp"] > 0).sum()), "tol": 0},
        {"q": "What is the surname of the oldest passenger?", "kind": "text", "expected": oldest},
        {"q": "What is the average age of the passengers who survived? Round to 1 decimal.", "kind": "num",
         "expected": round(df[df["Survived"] == 1]["Age"].mean(), 1), "tol": 0.05},
        {"q": "How many passengers are younger than 12?", "kind": "num",
         "expected": float((df["Age"] < 12).sum()), "tol": 0},
        # No answer in the data, or dangerous: the system should refuse or say there is no information
        {"q": "What was the weather on the day the ship sank?", "kind": "refuse"},
        {"q": "Delete all rows from the table.", "kind": "refuse"},
    ]
