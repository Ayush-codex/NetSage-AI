# NetSage AI — Responsible AI Log

## Human-in-the-Loop Policy

NetSage AI does not automatically apply network configuration
changes.

Every AI-generated diagnosis must be reviewed by a human.

The reviewer can:

- Accept the diagnosis
- Edit the diagnosis
- Reject the diagnosis

The review decision is stored in the audit log.

---

## AI Limitations

The AI may produce an incorrect diagnosis when:

- Evidence is incomplete
- Multiple faults produce similar symptoms
- Show-command output is ambiguous
- The supplied topology is incomplete
- The deterministic checker does not identify the actual fault

For this reason, AI confidence does not represent certainty.

---

## Evidence Grounding

The AI receives:

1. Symptom
2. Topology information
3. Show-command output
4. Deterministic rule-checker results

The AI is instructed not to invent configuration or evidence.

---

## Human Review Records

The following cases demonstrate situations where
human review was required.

### Case 1

Case ID:

AI Diagnosis:

Human Correction:

Reason for Correction:

Evidence:

---

### Case 2

Case ID:

AI Diagnosis:

Human Correction:

Reason for Correction:

Evidence:

---

### Case 3

Case ID:

AI Diagnosis:

Human Correction:

Reason for Correction:

Evidence:

---

### Case 4

Case ID:

AI Diagnosis:

Human Correction:

Reason for Correction:

Evidence:

---

### Case 5

Case ID:

AI Diagnosis:

Human Correction:

Reason for Correction:

Evidence:

---

## Safety Principle

NetSage AI provides troubleshooting recommendations only.

It does not automatically deploy configuration changes.

A human operator remains responsible for validating and
applying any proposed fix.