---
name: project-role-workflow
description: Use when initializing a repository for file-based Planner, Implementer, and Reviewer collaboration, or when creating, planning, implementing, reviewing, resuming, repairing, verifying, switching, or closing tasks in an initialized repository.
---

# Project Role Workflow

Keep project context in repository files so a new agent session can continue without replaying chat history.

## Commands and Language

These explicit commands are equivalent:

| 中文 | English |
|---|---|
| `$project-role-workflow 初始化当前仓库` | `$project-role-workflow initialize this repository` |
| `$project-role-workflow 继续` | `$project-role-workflow continue` |
| `$project-role-workflow 更换 Agent` / `$project-role-workflow 替换 Agent` | `$project-role-workflow replace agent` / `$project-role-workflow switch agent` |

The same Chinese or English wording may be used without the `$` prefix when the Skill is already loaded. During initialization, ask for the project language **before** asking which tools serve the three roles. Record `language: zh-CN` or `language: en-US` in `PROJECT_STATUS.md`. From then on, use that language for user-facing messages and all new requirements, plans, execution reports, reviews, progress records, decisions, and acceptance reports. Keep protocol field names and status enum values stable.

## Initialize a Repository

If the user asks to initialize this workflow, or `docs/agent/PROJECT_STATUS.md` is absent when this Skill is explicitly invoked, read [references/initialization.md](references/initialization.md) and initialize from `assets/project-template/` before using the task workflow.

Initialization may create missing collaboration files, but it must not overwrite project files, invent participant identities, create a real task, or modify product code. After installing the baseline, collect the Planner, Implementer, and Reviewer tool choices and create their registered Profiles.

Before an Implementer changes product code, read `STATE.md.subagent_policy`. If it is `UNSELECTED`, ask the user whether to use subagents (`USE` / `DO_NOT_USE`) and record the answer and authorization reference. Do not start implementation until the choice is explicit.

## Replace an Agent

Old and new agents may both start a replacement, including repeated A → B → A switches. Read [references/state-helper.md](references/state-helper.md) and [references/protocol.md](references/protocol.md), then:

1. Show the three roles and their current task/default bindings; ask which role changes.
2. Ask for scope: `current-task`, `project-default`, or `both`.
3. Select an existing same-role `active`/`standby` participant or explicitly register a new immutable identity.
4. Record the reason and authorization, show the exact proposed change, and obtain confirmation.
5. Use `scripts/workflow_state.py replace-agent` with the freshly read revision. Do not edit coordination state around the helper.
6. End the management operation. If the new participant is current, tell the user to invoke `继续` / `continue` separately.

Changing chat windows while keeping the same participant is session recovery/takeover, not participant replacement. A running foreign writer must first be proven stopped; pass `--confirm-writer-stopped` only when that evidence and explicit authorization exist. Never auto-release a lock. If Python is unavailable, use the documented manual single-writer path and state that lock/CAS protection is degraded.

## Start Here

1. Read `docs/agent/PROJECT_STATUS.md`, then the active task `STATE.md`.
2. Read and honor the recorded project language before communicating or writing.
3. Read `docs/agent/role-bindings.md`. If this tool has one active identity, restore it. If it has multiple identities, ask the user to select a participant_id; do not infer identity from the role currently needed.
4. Confirm the task is active, the identity matches current_role/current_participant, and no other writer_session is running. Otherwise remain read-only and report who or what is awaited in the project language.
5. Read the participant Profile, its role file, requirement, relevant deliverables, latest valid checkpoint, decisions, and real code version.
6. Work within the role, leave versioned evidence, and hand off using the documented order.

For state transitions, permissions, takeover, version evidence, interruption recovery, and handoff rules, read [references/protocol.md](references/protocol.md) before any write.

## Non-negotiable Boundaries

- `PROJECT_STATUS.md` chooses the only active task. A direct request to work on another task is not a task switch unless the user explicitly authorizes the switch.
- `STATE.md` chooses the current participant. Tool name alone is not identity.
- A running writer_session is not abandoned merely because it is old or silent. Take over only after confirming the old session stopped and receiving explicit takeover authorization.
- owner, revision, writer_session, rules, and this Skill are coordination records, not locks or authentication.
- Chat text does not replace project records. Do not claim DONE without evidence tied to the reviewed delivery.

## Quick Outcomes

| Observation | Action |
|---|---|
| Not the active task or participant | Read-only; report the active task and awaited participant |
| Multiple identities for this tool | Ask only which participant_id to use |
| Another writer_session is running | Inspect read-only; wait or request explicit takeover after confirming it stopped |
| Valid assignment and idle state | Register this session, then perform the role |
| Missing or contradictory state | Stop business work; use an authorized repair session |
| Handoff complete | Tell the user which participant/tool should be opened and say “继续” |

## Red Flags

- “The needed role is obvious, so I can assume that identity.”
- “The other session is probably dead, so I can replace its writer_session.”
- “The bug is small, so I can fix it while waiting for Reviewer.”
- “The progress file says what happened, so I do not need to inspect the code version.”

Each red flag means stop writing and follow the read-only or repair path in the protocol.

## Common Mistakes

| Shortcut | Correct response |
|---|---|
| STATE needs reviewer, so a new Codex session assumes its reviewer identity | If Codex has multiple identities, ask which participant_id this session represents |
| A writer is old or silent, so replace its session ID | Confirm it stopped and obtain explicit takeover authorization first |
| execution is idle, so any assigned role may start | Only current_participant may start |
| Reviewer sees a trivial fix | Record the finding and hand it to Implementer |
