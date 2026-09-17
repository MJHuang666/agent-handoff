# Agent Relay Protocol

This repository uses file-based collaboration between Planner, Implementer, and Reviewer.

## Language

Read `PROJECT_STATUS.md.language` first. Use it for all user-facing messages and new task prose. Keep file names, YAML keys, status enums, participant IDs, delivery IDs, and review issue IDs stable.

## Write Eligibility

Business writes require the active task, confirmed participant identity, matching role and assignment, no foreign writer session, and verified workdir/version evidence. Otherwise remain read-only and report the awaited participant.

## Agent Replacement

Accept `replace agent`, `switch agent`, and the documented Chinese aliases. Either old or new Agent may start this explicit management operation. Keep the role fixed and choose `current-task`, `project-default`, or `both`; create or reuse a same-role identity. Prefer `.agents/skills/agent-relay/scripts/workflow_state.py` for its short-lived local lock, expected-revision validation, and atomic replacement.

Repeated A → B → A switching reuses immutable participant IDs and appends a MANAGEMENT record each time. A current participant change increments revision and stage_round and clears writer/checkpoint ownership; a non-current task assignment increments revision only. Implementer replacement resets the subagent decision. Never auto-release a lock or overwrite a running writer. Complete replacement before the new participant invokes `continue` separately.

## Implementer Subagent Gate

Before changing product code, `STATE.md.subagent_policy` must be `USE` or `DO_NOT_USE`. If it is `UNSELECTED`, ask the user in the project language and record the explicit choice in `subagent_decision_ref`. Use subagents only with `USE` and record delegation, results, and evidence.

## Roles

- Planner owns requirements, plans, decisions, and acceptance criteria; Planner proposes durable knowledge-index candidates but does not mark them verified or modify product code.
- Implementer owns code, tests, execution evidence, and rework; Implementer does not close review issues.
- Reviewer independently checks the real delivery and decides changes, planning return, blocking, verification, or completion; during VERIFYING, Reviewer promotes only verified reusable conclusions to `knowledge-index.md`. Reviewer does not fix product code.

## Handoff

Finish the role deliverable, append progress, update STATE as the handoff commit point, clear writer ownership, then refresh PROJECT_STATUS. Files do not wake another tool; the user opens the next tool and says `继续` or `continue`.

DONE means task acceptance only. It does not authorize merge, release, deployment, deletion, rollback, or takeover.
