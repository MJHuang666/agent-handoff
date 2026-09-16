---
name: project-role-workflow
description: Use when creating, planning, implementing, reviewing, resuming, repairing, verifying, switching, or closing tasks in a repository initialized with docs/agent/PROJECT_STATUS.md.
---

# Project Role Workflow

Keep project context in repository files so a new Agent session can continue without replaying chat history.

## Commands and Language

`$project-role-workflow 继续` and `$project-role-workflow continue` are equivalent. Read `docs/agent/PROJECT_STATUS.md.language` first and use that language for user-facing messages and all new task prose. Keep protocol fields and enum values stable.

## Continue

1. Read `docs/agent/PROJECT_STATUS.md` and the active task `STATE.md`.
2. Resolve the session participant from `docs/agent/role-bindings.md`; if this tool has multiple identities, ask for the participant ID.
3. Confirm the task, participant, role, assignment, and writer session. If any check fails, remain read-only and report the awaited participant in the project language.
4. Read the participant Profile, role file, requirement, prior deliverables, valid checkpoint, decisions, and real code version.
5. Work within the role, leave versioned evidence, and hand off using [references/protocol.md](references/protocol.md).

Before Implementer changes product code, `STATE.md.subagent_policy` must be `USE` or `DO_NOT_USE`. If it is `UNSELECTED`, ask the user in the project language and record `subagent_decision_ref` before implementation.

## Boundaries

- `PROJECT_STATUS.md` chooses the only active task; `STATE.md` chooses the current participant.
- Tool name alone is not identity.
- A running writer session is not abandoned based on age or silence.
- Reviewer records findings but does not fix product code.
- DONE requires evidence tied to the reviewed delivery and does not authorize merge, release, deployment, deletion, or rollback.
