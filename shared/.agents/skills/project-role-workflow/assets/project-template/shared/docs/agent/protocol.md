# Project Role Workflow Protocol

This repository uses file-based collaboration between Planner, Implementer, and Reviewer.

## Language

Read `PROJECT_STATUS.md.language` first. Use it for all user-facing messages and new task prose. Keep file names, YAML keys, status enums, participant IDs, delivery IDs, and review issue IDs stable.

## Write Eligibility

Business writes require the active task, confirmed participant identity, matching role and assignment, no foreign writer session, and verified workdir/version evidence. Otherwise remain read-only and report the awaited participant.

## Implementer Subagent Gate

Before changing product code, `STATE.md.subagent_policy` must be `USE` or `DO_NOT_USE`. If it is `UNSELECTED`, ask the user in the project language and record the explicit choice in `subagent_decision_ref`. Use subagents only with `USE` and record delegation, results, and evidence.

## Roles

- Planner owns requirements, plans, decisions, and acceptance criteria; Planner does not modify product code.
- Implementer owns code, tests, execution evidence, and rework; Implementer does not close review issues.
- Reviewer independently checks the real delivery and decides changes, planning return, blocking, verification, or completion; Reviewer does not fix product code.

## Handoff

Finish the role deliverable, append progress, update STATE as the handoff commit point, clear writer ownership, then refresh PROJECT_STATUS. Files do not wake another tool; the user opens the next tool and says `继续` or `continue`.

DONE means task acceptance only. It does not authorize merge, release, deployment, deletion, rollback, or takeover.
