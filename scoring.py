import re

NUMBER = re.compile(r"-?\d[\d,]*\.?\d*")

REFUSAL_HINTS = (
    "not available", "not in the", "no information", "cannot", "can't", "unable",
    "doesn't", "does not", "not contain", "not able", "read-only", "don't have", "do not have",
)


def numbers_in(text):
    found = []
    for raw in NUMBER.findall(text):
        try:
            found.append(float(raw.replace(",", "")))
        except ValueError:
            pass
    return found


def numeric_match(answer, expected, tol=0.0):
    return any(abs(n - expected) <= tol for n in numbers_in(answer))


def text_match(answer, expected):
    return expected.lower() in answer.lower()


def refusal_match(answer):
    lower = answer.lower()
    return any(hint in lower for hint in REFUSAL_HINTS)
