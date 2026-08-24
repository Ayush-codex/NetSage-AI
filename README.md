# NetSage AI

## AI-Assisted Network Troubleshooting with Human Review

NetSage AI is an AI-assisted troubleshooting platform for
Cisco Packet Tracer and Cisco-style networking lab scenarios.

The system analyzes network symptoms, topology information,
and Cisco show-command output to identify likely faults,
suggest verification commands, and recommend possible fixes.

Every AI diagnosis requires human review before acceptance.

---

## Features

- Cisco Packet Tracer troubleshooting cases
- Deterministic networking rule checker
- AI-assisted diagnosis using Gemini
- Evidence-based reasoning
- OSI layer identification
- Confidence scoring
- Recommended verification commands
- Suggested remediation steps
- Human Accept/Edit/Reject workflow
- Responsible AI audit logging
- Troubleshooting dashboard
- Issue and severity analysis

---

## Architecture

```text
Case Dataset
     |
     v
Streamlit Interface
     |
     v
Deterministic Rule Checker
     |
     v
Rule Evidence
     |
     v
Gemini AI Diagnosis
     |
     v
Structured JSON
     |
     v
Human Review
     |
     v
Audit Log

Technology Stack
Frontend
Streamlit
Backend
Python
Data Processing
Pandas
Networking
Cisco Packet Tracer
Cisco show-command outputs
AI
Google Gemini API
Structured JSON output
Pydantic
Storage
CSV
Diagnostic Workflow
Select a troubleshooting case.
Review the symptom and topology.
Inspect show-command output.
Run deterministic checks.
Send evidence to the AI diagnosis engine.
Receive structured diagnosis.
Review the diagnosis as a human.
Accept, edit, or reject the recommendation.
Save the review to the audit log.
Analyze results in the dashboard.
Safety

NetSage AI does not automatically apply network
configuration changes.

All AI recommendations require human review.

The system records human decisions so that incorrect
AI diagnoses can be analyzed.

Project Structure
data/
docs/
prompts/
src/
.env
.gitignore
README.md
requirements.txt
system_config.json
Running the Project

Create and activate the virtual environment.

Install dependencies:

pip install -r requirements.txt

Configure the Gemini API key in .env:

GEMINI_API_KEY=your_key

Run:

streamlit run src/app.py
Responsible AI

The project includes an audit log containing human
review decisions.

The review process supports:

Accepted
Edited
Rejected

At least five cases are documented where human review
corrected or modified an AI diagnosis




