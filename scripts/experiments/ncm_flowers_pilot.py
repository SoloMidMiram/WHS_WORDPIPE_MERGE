"""Validate the synthetic Flowers pilot contract using the standard library."""
import hashlib
import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ncm_flowers_synthetic.json"


def source_text(case):
    return "## " + case["title"] + "\n\n" + "\n".join(case["lines"])


def source_digest(case):
    return hashlib.sha256(source_text(case).encode("utf-8")).hexdigest()


def load_cases():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if data["scope"] != "synthetic" or data["schema"] != "whs-ncm-pilot-v1":
        raise ValueError("Only the reviewed synthetic suite is supported")
    cases = data["cases"]
    if len({case["source_reference"] for case in cases}) != len(cases):
        raise ValueError("Duplicate source reference")
    for case in cases:
        if any(not fact["literal"] or fact["literal"] not in source_text(case) for fact in case["facts"]):
            raise ValueError(f"Annotation missing from source: {case['id']}")
    return cases


if __name__ == "__main__":
    print(json.dumps({"scope": "synthetic", "sources": {
        case["source_reference"]: source_digest(case) for case in load_cases()
    }}, indent=2))
