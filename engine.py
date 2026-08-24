import json
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# File paths
CONFIG_PATH = BASE_DIR / "system_config.json"
PROMPT_PATH = BASE_DIR / "prompts" / "diagnose_prompt.md"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_prompt():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()


CONFIG = load_config()
SYSTEM_PROMPT = load_prompt()
