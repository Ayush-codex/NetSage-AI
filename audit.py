import pandas as pd
from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent

AUDIT_PATH = (
    BASE_DIR
    / "data"
    / "audit_log.csv"
)




COLUMNS = [
    "timestamp",
    "case_id",
    "decision",
    "reviewer_notes",
    "ai_root_cause",
    "final_root_cause",
    "ai_confidence",
    "human_review_required"
]




def save_audit_record(record: dict):
    """
    Save one human-review record.

    Handles:
    - Missing audit file
    - Empty audit file
    - Existing audit records
    """

    AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    new_row = pd.DataFrame(
        [record],
        columns=COLUMNS
    )

    

    if (
        not AUDIT_PATH.exists()
        or AUDIT_PATH.stat().st_size == 0
    ):

        new_row.to_csv(
            AUDIT_PATH,
            index=False
        )

        return


    

    try:

        old_data = pd.read_csv(
            AUDIT_PATH
        )

    except pd.errors.EmptyDataError:

        old_data = pd.DataFrame(
            columns=COLUMNS
        )


    

    for column in COLUMNS:

        if column not in old_data.columns:

            old_data[column] = ""


    old_data = old_data[
        COLUMNS
    ]


    

    data = pd.concat(
        [
            old_data,
            new_row
        ],
        ignore_index=True
    )


    data.to_csv(
        AUDIT_PATH,
        index=False
    )




def load_audit_log():
    """
    Load the human-review audit log safely.
    """

    if (
        not AUDIT_PATH.exists()
        or AUDIT_PATH.stat().st_size == 0
    ):

        return pd.DataFrame(
            columns=COLUMNS
        )


    try:

        return pd.read_csv(
            AUDIT_PATH
        )

    except pd.errors.EmptyDataError:

        return pd.DataFrame(
            columns=COLUMNS
        )