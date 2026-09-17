# Multi-Agent Workflow

## Daily Path

1. Read `PROJECT_STATUS.md.language`; use it for communication and new documents.
2. Resolve the participant from `role-bindings.md` and its Profile.
3. Check `active_task`, task `STATE.md`, current role, participant, execution, and writer session.
4. Skim `knowledge-index.md`, then read the role rules, requirement, relevant sources, prior deliverable, valid checkpoint, decisions, and real code version.
5. Register a writer session and work only within role permissions. Before product-code changes, Implementer must complete the subagent choice gate.
6. Write the formal deliverable and progress record, update STATE, then refresh the project cache.

## Normal State Flow

```text
DRAFT → PLANNING → READY → IMPLEMENTING → REVIEWING → VERIFYING → DONE
                                  ↑            │
                                  └─ CHANGES_REQUESTED
```

Planner produces an approved plan. Implementer produces code, tests, and delivery evidence. Reviewer independently checks the delivery and either requests changes, returns to planning, blocks, or verifies completion.

## Implementer Subagent Gate

Before changing product code, read `STATE.md.subagent_policy`. If it is `UNSELECTED`, ask in the project language: “Use subagents for this implementation? Use / Do not use.” Record `USE` or `DO_NOT_USE` and `subagent_decision_ref`. Do not implement before the choice.

## Handoff

Finish the role deliverable, append progress, update STATE (the handoff commit point), clear the writer session, and tell the user which tool should receive `continue`. Files do not wake another tool automatically.

## Agent Replacement

Accept `replace agent`, `switch agent`, and the documented Chinese aliases. Either the old or new Agent may start this separate management operation.

Choose the role and `current-task`, `project-default`, or `both` scope. Create or reuse a same-role participant, read the latest revision, and prefer `.agents/skills/agent-relay/scripts/workflow_state.py` for locking, revision validation, and atomic replacement. A current participant change increments stage_round and clears writer/checkpoint ownership; a non-current assignment changes revision only. Implementer replacement resets the subagent decision. Complete the management operation before invoking `continue` separately in the new Agent.

Never overwrite a running writer. Confirm it stopped and obtain explicit authorization. Never remove a lock based on age; use the Skill's authorized recovery command. Without Python, report degraded manual single-writer mode.
