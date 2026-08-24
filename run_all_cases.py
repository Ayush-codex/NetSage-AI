import pandas as pd
from pathlib import Path

from checker import diagnose_case



BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "cases.csv"
)




cases = pd.read_csv(DATA_PATH)


print("=" * 70)
print("NETSAGE AI - DETERMINISTIC RULE CHECKER")
print("=" * 70)

print(f"Total cases: {len(cases)}")




results = []

for _, row in cases.iterrows():

    case = row.to_dict()

    result = diagnose_case(case)

    results.append(result)

    print(
        f"\n{result['case_id']} | "
        f"{result['concept_tag']}"
    )

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Rules checked: "
        f"{', '.join(result['rules_checked']) or 'None'}"
    )

    print(
        f"Errors detected: "
        f"{result['error_count']}"
    )

    for error in result["errors"]:

        print(
            f"  → {error['type']}: "
            f"{error['message']}"
        )



error_cases = sum(
    result["status"] == "ERRORS_DETECTED"
    for result in results
)

clean_cases = sum(
    result["status"] == "NO_KNOWN_ERRORS"
    for result in results
)


print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"Total cases:       {len(results)}")
print(f"Errors detected:   {error_cases}")
print(f"No known errors:   {clean_cases}")

print("=" * 70)