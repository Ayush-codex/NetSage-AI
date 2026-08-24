import json
import os
import streamlit as st
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field




BASE_DIR = Path(__file__).resolve().parent.parent

PROMPT_PATH = (
    BASE_DIR
    / "prompts"
    / "diagnose_prompt.md"
)

CONFIG_PATH = (
    BASE_DIR
    / "system_config.json"
)




load_dotenv(
    BASE_DIR / ".env"
)

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

except:

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )




def load_config() -> dict:
    """Load NetSage configuration."""

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


CONFIG = load_config()

MODEL_NAME = CONFIG["ai"]["model"]

TEMPERATURE = CONFIG["ai"]["temperature"]

HUMAN_REVIEW_REQUIRED = CONFIG[
    "diagnosis"
]["human_review_required"]




def create_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Add it to the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )




class Diagnosis(BaseModel):

    root_cause: str = Field(
        description=(
            "Most likely root cause of the "
            "network problem."
        )
    )

    osi_layer: str = Field(
        description=(
            "Most relevant OSI layer, such as "
            "Layer 1, Layer 2, Layer 3, Layer 4, "
            "or Layer 7."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence in the diagnosis between "
            "0 and 1."
        )
    )

    evidence: List[str] = Field(
        description=(
            "Specific evidence from the supplied "
            "case or rule checker."
        )
    )

    next_command: str = Field(
        description=(
            "Cisco command that should be run next "
            "to verify the diagnosis."
        )
    )

    fix_steps: List[str] = Field(
        description=(
            "Recommended remediation steps. "
            "These are suggestions only."
        )
    )

    human_review_required: bool = Field(
        description=(
            "Must always be true because a human "
            "must review the proposed fix."
        )
    )




def load_prompt() -> str:

    if not PROMPT_PATH.exists():

        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


SYSTEM_PROMPT = load_prompt()




def build_case_prompt(
    case: dict,
    rule_result: dict
) -> str:

    case_id = case.get(
        "case_id",
        "UNKNOWN"
    )

    symptom = case.get(
        "symptom",
        ""
    )

    topology = case.get(
        "topology_note",
        ""
    )

    show_outputs = case.get(
        "show_outputs",
        ""
    )

    concept = case.get(
        "concept_tag",
        ""
    )

    severity = case.get(
        "severity",
        ""
    )

    rule_results = json.dumps(
        rule_result,
        indent=2,
        ensure_ascii=False
    )

    return f"""
CASE ID:
{case_id}

SYMPTOM:
{symptom}

TOPOLOGY:
{topology}

CONCEPT:
{concept}

SEVERITY:
{severity}

SHOW OUTPUT:
{show_outputs}

RULE CHECKER RESULTS:
{rule_results}

Analyze this case using only the supplied evidence.

Return the required structured JSON diagnosis.

Remember:
- Do not invent evidence.
- Do not claim a fix was executed.
- Human review is mandatory.
"""




def validate_diagnosis(
    diagnosis: Diagnosis
) -> Diagnosis:

    
    diagnosis.human_review_required = True

    
    diagnosis.confidence = max(
        0.0,
        min(
            1.0,
            diagnosis.confidence
        )
    )

    return diagnosis




def generate_diagnosis(
    case: dict,
    rule_result: dict
) -> dict:

    client = create_client()

    case_prompt = build_case_prompt(
        case,
        rule_result
    )

    full_prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + case_prompt
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
        config={
            "temperature": TEMPERATURE,
            "response_mime_type": "application/json",
            "response_schema": Diagnosis,
        }
    )

    
    if hasattr(response, "parsed") and response.parsed:

        diagnosis = response.parsed

        if not isinstance(
            diagnosis,
            Diagnosis
        ):

            diagnosis = Diagnosis.model_validate(
                diagnosis
            )

    else:

        diagnosis = Diagnosis.model_validate_json(
            response.text
        )

    diagnosis = validate_diagnosis(
        diagnosis
    )

    return diagnosis.model_dump()




def diagnose(
    case: dict,
    rule_result: dict
) -> dict:

    try:

        diagnosis = generate_diagnosis(
            case,
            rule_result
        )

        return {
            "success": True,
            "case_id": case.get("case_id"),
            "diagnosis": diagnosis,
            "error": None
        }

    except Exception as error:

        return {
            "success": False,
            "case_id": case.get("case_id"),
            "diagnosis": None,
            "error": str(error)
        }
