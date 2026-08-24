import pandas as pd
from pathlib import Path

from checker import diagnose_case
from engine import diagnose




BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "cases.csv"
)




cases = pd.read_csv(DATA_PATH)




case_row = cases[
    cases["case_id"] == "NET-001"
]

if case_row.empty:
    raise RuntimeError(
        "NET-001 was not found in cases.csv"
    )

case = case_row.iloc[0].to_dict()




print("=" * 70)

print("NETSAGE AI - AI DIAGNOSIS TEST")

print("=" * 70)

print(
    f"Case: {case['case_id']}"
)

print(
    f"Concept: {case['concept_tag']}"
)

print(
    f"Symptom: {case['symptom']}"
)



rule_result = diagnose_case(case)


print("\nRULE CHECKER RESULT:")
print("=" * 70)

print(rule_result)




if rule_result["status"] == "NO_KNOWN_ERRORS":

    print(
        "\nWARNING:"
        "\nThe deterministic checker did not detect "
        "a known error."
    )

    print(
        "AI diagnosis will still be attempted."
    )


result = diagnose(
    case,
    rule_result
)




print("\nAI RESULT:")
print("=" * 70)

print(result)




if result["success"]:

    diagnosis = result["diagnosis"]

    print("\nRoot Cause:")
    print(
        diagnosis["root_cause"]
    )

    print("\nOSI Layer:")
    print(
        diagnosis["osi_layer"]
    )

    print("\nConfidence:")
    print(
        diagnosis["confidence"]
    )

    print("\nEvidence:")

    for evidence in diagnosis["evidence"]:
        print(
            f"- {evidence}"
        )

    print("\nNext Command:")
    print(
        diagnosis["next_command"]
    )

    print("\nFix Steps:")

    for step in diagnosis["fix_steps"]:
        print(
            f"- {step}"
        )

    print("\nHuman Review Required:")
    print(
        diagnosis["human_review_required"]
    )

else:

    print("\nAI diagnosis failed:")
    print(
        result["error"]
    )