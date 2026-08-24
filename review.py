from datetime import datetime


VALID_DECISIONS = {
    "Accepted",
    "Edited",
    "Rejected"
}


def create_review(
    case_id: str,
    ai_diagnosis: dict,
    decision: str,
    reviewer_notes: str = "",
    edited_diagnosis: dict | None = None
) -> dict:

    if decision not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision: {decision}"
        )

    final_diagnosis = (
        edited_diagnosis
        if decision == "Edited"
        else ai_diagnosis
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "case_id": case_id,
        "decision": decision,
        "reviewer_notes": reviewer_notes,
        "ai_root_cause": ai_diagnosis.get(
            "root_cause", ""
        ),
        "final_root_cause": final_diagnosis.get(
            "root_cause", ""
        ),
        "ai_confidence": ai_diagnosis.get(
            "confidence", 0
        ),
        "human_review_required": True
    }