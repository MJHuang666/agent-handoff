# Multi-Agent Workflow

## Daily Path

1. Read `PROJECT_STATUS.md.language`; use it for communication and new documents.
2. Resolve the participant from `role-bindings.md` and its Profile.
3. Check `active_task`, task `STATE.md`, current role, participant, execution, and writer session.
4. Read the role rules, requirement, prior deliverable, valid checkpoint, decisions, and real code version.
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
