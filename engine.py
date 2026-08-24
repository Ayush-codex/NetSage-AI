import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "system_config.json"

PROMPT_PATH = (
    BASE_DIR
    / "prompts"
    / "diagnose_prompt.md"
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(
    BASE_DIR / ".env"
)


# ============================================================
# LOAD CONFIG
# ============================================================

def load_config():

    if not CONFIG_PATH.exists():

        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# LOAD PROMPT
# ============================================================

def load_prompt():

    if not PROMPT_PATH.exists():

        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    with open(
        PROMPT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# LOAD SETTINGS
# ============================================================

CONFIG = load_config()

SYSTEM_PROMPT = load_prompt()


# ============================================================
# API KEY
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY is not configured. "
        "Add it to Streamlit Cloud Secrets."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = CONFIG.get(
    "model",
    "gemini-3.6-flash"
)


# ============================================================
# AI DIAGNOSIS
# ============================================================

def diagnose(case, rule_result):

    try:

        prompt = f"""
{SYSTEM_PROMPT}

Troubleshooting Case:

Case ID:
{case.get("case_id")}

Symptom:
{case.get("symptom")}

Topology:
{case.get("topology_note")}

Show Command Output:
{case.get("show_outputs")}

Concept:
{case.get("concept_tag")}

OSI Layer:
{case.get("osi_layer")}

Rule Checker Result:
{json.dumps(rule_result, indent=2)}

Return only valid JSON.
"""


        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )


        raw_text = response.text.strip()


        # Remove markdown JSON fences if Gemini adds them
        if raw_text.startswith("```json"):

            raw_text = raw_text.replace(
                "```json",
                "",
                1
            ).strip()


        if raw_text.startswith("```"):

            raw_text = raw_text.replace(
                "```",
                "",
                1
            ).strip()


        if raw_text.endswith("```"):

            raw_text = raw_text[:-3].strip()


        diagnosis = json.loads(
            raw_text
        )


        return {

            "success": True,

            "case_id": case.get(
                "case_id"
            ),

            "diagnosis": diagnosis,

            "error": None

        }


    except Exception as error:

        return {

            "success": False,

            "case_id": case.get(
                "case_id"
            ),

            "diagnosis": None,

            "error": str(error)

        }
