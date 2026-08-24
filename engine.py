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
PROMPT_PATH = BASE_DIR / "diagnose_prompt.md"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(BASE_DIR / ".env")


# ============================================================
# LOAD CONFIGURATION
# ============================================================

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# LOAD SYSTEM PROMPT
# ============================================================

def load_prompt():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()


# ============================================================
# LOAD PROJECT SETTINGS
# ============================================================

CONFIG = load_config()
SYSTEM_PROMPT = load_prompt()


# ============================================================
# GET GEMINI API KEY
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    try:
        import streamlit as st

        GEMINI_API_KEY = st.secrets.get(
            "GEMINI_API_KEY",
            None
        )
    except Exception:
        pass


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# GET MODEL NAME
# ============================================================

MODEL_NAME = CONFIG.get(
    "model",
    "gemini-3.6-flash"
)


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_json_response(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# ============================================================
# RUN AI DIAGNOSIS
# ============================================================

def diagnose(case, rule_result):

    try:

        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file locally or "
                "Streamlit Secrets when deployed."
            )

        if client is None:
            raise ValueError(
                "Gemini client could not be initialized."
            )


        # ----------------------------------------------------
        # CREATE CASE PROMPT
        # ----------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

============================================================
NETWORK TROUBLESHOOTING CASE
============================================================

Case ID:
{case.get("case_id", "Unknown")}

Symptom:
{case.get("symptom", "Not provided")}

Topology Note:
{case.get("topology_note", "Not provided")}

Show Command Output:
{case.get("show_outputs", "Not provided")}

Expected Fault:
{case.get("expected_fault", "Not provided")}

OSI Layer:
{case.get("osi_layer", "Not provided")}

Concept Tag:
{case.get("concept_tag", "Not provided")}

Severity:
{case.get("severity", "Not provided")}

============================================================
DETERMINISTIC RULE CHECKER RESULT
============================================================

{json.dumps(rule_result, indent=2)}

============================================================
INSTRUCTIONS
============================================================

Analyze the available evidence.

Use the symptom, show-command output, topology information,
and rule checker result.

Do not invent configuration details.

Return only valid JSON.

Required format:

{{
    "root_cause": "Most likely root cause",
    "osi_layer": "Relevant OSI layer",
    "confidence": "low, medium, or high",
    "evidence": [
        "Evidence 1",
        "Evidence 2"
    ],
    "next_command": "Recommended Cisco command",
    "fix_steps": [
        "Step 1",
        "Step 2"
    ],
    "human_review_required": true
}}
"""


        # ----------------------------------------------------
        # CALL GEMINI
        # ----------------------------------------------------

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )


        # ----------------------------------------------------
        # VALIDATE RESPONSE
        # ----------------------------------------------------

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )


        raw_text = clean_json_response(
            response.text
        )


        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        diagnosis = json.loads(
            raw_text
        )


        # ----------------------------------------------------
        # SUCCESS RESPONSE
        # ----------------------------------------------------

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
