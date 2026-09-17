# Agent Relay Usage Guide

This guide covers `agent-relay` Skill v1.4.0: initialization, role handoff, Agent replacement, pause and recovery, state inspection, and task acceptance.

## Initialize a repository

```text
$agent-relay initialize this repository
$agent-relay 初始化当前仓库
```

The Skill checks the repository, asks for the project language (`en-US` or `zh-CN`), asks which Agent serves Planner, Implementer, and Reviewer, then creates project files, Profiles, and bindings. It does not create a real task, overwrite existing project instructions, or modify product code.

## Agent choices

| Choice | Stable tool ID |
|---|---|
| Codex | `codex` |
| Cursor | `cursor` |
| Claude Code | `claude-code` |
| WorkBuddy | `workbuddy` |
| ZCode | `zcode` |
| Trae | `trae` |
| DeepSeek Harness | `deepseek-harness` |
| OpenCode | `opencode` |
| Other | User-provided stable ID |

One Agent may serve multiple roles, but every participant needs a unique `participant_id`. Role and tool ID are immutable after registration.

## Create and continue a task

```text
Create a task to implement user login.
continue
$agent-relay continue
```

The task lives under `docs/agent/tasks/<TASK-ID>/` and contains `STATE.md`, `requirement.md`, `plan.md`, `execution.md`, `review.md`, `decisions.md`, and append-only `progress/` records. `STATE.md` is the single live state source.

Every Agent reads `PROJECT_STATUS.md`, `STATE.md`, `role-bindings.md`, its Profile, its role file, and the previous handoff before acting. If it is not the current participant, it reports the wait state and remains read-only.

## Planner

```text
Act as the Planner and prepare the plan for the active task.
```

Planner owns requirements, scope, constraints, risks, decisions, `plan.md`, and acceptance criteria. Planner does not modify product code.

## Implementer

```text
Act as the Implementer and execute the approved plan.
```

Before changing product code, Implementer must choose `USE` or `DO_NOT_USE` for subagents. Implementer changes code and tests, records a `delivery_id`, test evidence, and `execution.md`, then hands off to Reviewer.

For rework:

```text
Address the current Reviewer findings.
```

Rework creates fresh delivery evidence and preserves history.

## Reviewer and completion

```text
Act as the Reviewer and inspect the active task.
Verify the current task and close it when acceptance is complete.
```

Reviewer independently checks requirements, plan, actual diff, tests, and delivery version. Results may be `CHANGES_REQUESTED`, `VERIFYING`, `PLANNING`, `BLOCKED`, or `DONE`. `DONE` means acceptance only; it does not authorize merge, release, deployment, deletion, rollback, or push.

## Replace an Agent

```text
$agent-relay replace agent
$agent-relay switch agent
$agent-relay 更换 Agent
$agent-relay 替换 Agent
```

Choose the role, scope (`current-task`, `project-default`, or `both`), a same-role participant, the reason, and authorization. Repeated switching is supported, for example `Codex → Cursor → OpenCode → Codex`. Old identities and `MANAGEMENT` history remain. Replacing the current participant increments `stage_round`, clears old writer/checkpoint ownership, and replacing Implementer resets the subagent decision.

## Pause, resume, and block

```text
Pause the active task and record a checkpoint.
continue
Record that the task is blocked by an API credential problem.
```

Before resuming, check disk differences, processes, side effects, and delivery evidence. Do not blindly repeat an interrupted operation.

## State helper

```bash
python3 .agents/skills/agent-relay/scripts/workflow_state.py \
  --repo . status
```

The helper provides a short-lived local lock, revision compare-and-swap, and atomic state replacement. It protects coordination state only, not product code.

Example replacement:

```bash
python3 .agents/skills/agent-relay/scripts/workflow_state.py \
  --repo . replace-agent \
  --role implementer --from cursor-impl --to opencode-impl \
  --scope current-task --expected-revision 10 \
  --reason "Cursor quota exhausted" \
  --authorization "User approved in the current conversation"
```

Release a stale lock only after confirming that the old session stopped and obtaining explicit authorization.

## Write eligibility

Business writes require an active task, a confirmed participant identity, matching role and assignment, no foreign writer session, and verified worktree, baseline, and delivery evidence. Remain read-only when the task is inactive, the Agent is not current, another writer is active, the revision is stale, or state/history is contradictory.

## Shared tool entry points

Codex, Cursor, DeepSeek Harness, and OpenCode share:

```text
AGENTS.md
docs/agent/
.agents/skills/agent-relay/
```

DeepSeek Harness requires `dsh-agent-instructions` and project Skill loading. OpenCode discovers the root `AGENTS.md` and `.agents/skills/`. Do not create duplicate `.dsh/skills` or `.opencode/skills` trees.

## Standard flow

```text
Initialize → choose language and role Agents → Planner
          → Implementer → Reviewer → rework if needed
          → final verification → DONE
```

See the [Skill instructions](../shared/.agents/skills/agent-relay/SKILL.md), [initialization reference](../shared/.agents/skills/agent-relay/references/initialization.md), [protocol](../shared/.agents/skills/agent-relay/references/protocol.md), and [installation guide](../distribution/INSTALL.md) for details.
