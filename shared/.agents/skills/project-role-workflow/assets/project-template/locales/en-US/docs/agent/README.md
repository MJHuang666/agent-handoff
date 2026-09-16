# Agent Collaboration Guide

This directory is the shared project context for every Agent. Read `PROJECT_STATUS.md`, the active task `STATE.md`, and `workflow.md` before working.

## Language

`PROJECT_STATUS.md.language` is the project language. Use it for communication and all new requirements, plans, execution reports, reviews, progress records, decisions, and acceptance reports. Keep file names, YAML keys, status values, participant IDs, and delivery IDs stable.

## Ownership

| File or directory | Authority |
|---|---|
| `PROJECT_STATUS.md` | Project overview and unique active task |
| `tasks/<task>/STATE.md` | Task stage, participant, session, evidence, and exceptions |
| `role-bindings.md` | Participant identity and defaults |
| `roles/` | Role responsibilities and permissions |
| `profiles/` | Participant-specific agreements |
| `workflow.md` | Flow, handoff, recovery, and state rules |
| `protocol.md` | Core role and write rules when the project Skill is unavailable |
| `tasks/` | Task templates, deliverables, and append-only history |

## Continue

In the assigned tool, say `continue`. The Agent resolves its participant, checks the active task and turn, reads the prior handoff, works only when assigned, and records evidence before handoff.

If it is not the Agent's turn, it stays read-only and reports the waiting role and participant.
