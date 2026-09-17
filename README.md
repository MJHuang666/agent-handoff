# Agent Relay

[简体中文](README.zh-CN.md)

Make memory belong to the project, not the agent.
A lightweight framework for persistent, portable, and agent-independent project cognition across Coding Agents.

The best part is that communication between agents doesn’t need to rely on conversation context at all.

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/c613f203-32b8-4056-aa8e-1f53f6ec1200" />


Agent Relay is a lightweight multi-Agent collaboration framework. Coding Agents do not need to share conversation context; they relay durable project state through the repository. Planner, Implementer, and Reviewer preserve reusable project knowledge in files rather than relying on one chat window's memory. An optional standard-library Python helper adds a short-lived state lock, expected-revision checks, and atomic replacement.

It supplies dedicated Codex and Cursor adapters and first-class shared entry support for DeepSeek Harness and OpenCode. Claude Code, WorkBuddy, ZCode, Trae, and other tools can use the same protocol through a thin project-level instruction. Roles remain independent from tools.

## Why it exists

Agent conversations do not naturally share context. This template makes the repository the durable handoff surface:

```text
Requirement → Plan → Implementation → Review → Rework → Verification
               docs/agent/tasks/<TASK-ID>/
```

Each role writes fixed deliverables and append-only progress records. The next agent reads the project summary, compact `knowledge-index.md`, task state, and prior role output before acting. A project can therefore recover its working understanding after an Agent, chat, machine, or model changes.

## Roles

| Role | Owns | Does not do |
|---|---|---|
| Planner | Requirement, scope, plan, decisions, acceptance criteria | Change product code |
| Implementer | Code, tests, execution evidence, rework | Close review issues |
| Reviewer | Independent review, verification, completion decision | Directly fix product code |

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/be8dc516-a6e7-4c4e-9027-4321259445e7" />


## Quick start

1. Install `shared/.agents/skills/agent-relay/` as a personal Skill for your tool.
2. Open a new repository and run either command:

   ```text
   $agent-relay initialize this repository
   $agent-relay 初始化当前仓库
   ```
<img width="814" height="628" alt="9a3c8948164a8b340d70ad3fc11335e4" src="https://github.com/user-attachments/assets/0d171199-0a2a-45ef-802d-3aadf5998133" />


3. Select `English` or `中文` before assigning a tool to each role.
4. Create the first task with the Planner.
5. Open the next role's tool and say `continue` or `继续` at each handoff.

<img width="840" height="362" alt="2c7493b4c6a7366e669c5f0bcb1274c5" src="https://github.com/user-attachments/assets/d285da83-36d3-43ce-9a30-0d2ef4a8211d" />


The selected language controls later user-facing conversation and task prose. Stable file names, YAML keys, IDs, and status enums remain unchanged.

The built-in tool choices are Codex, Cursor, Claude Code, WorkBuddy, ZCode, Trae, DeepSeek Harness, OpenCode, and Other. DeepSeek Harness and OpenCode reuse root `AGENTS.md` plus `.agents/skills/agent-relay/`; the initializer does not create duplicate `.dsh` or `.opencode` Skill trees.

Before product-code work, an Implementer must ask whether to use subagents. The explicit choice is recorded in the task state; no code work starts while the choice is unselected.

## Replace an agent

Either the old or new agent can start the management flow:

```text
$agent-relay replace agent
$agent-relay switch agent
$agent-relay 更换 Agent
$agent-relay 替换 Agent
```

Choose Planner, Implementer, or Reviewer and whether the replacement affects the current task, future defaults, or both. The role stays fixed while a same-role participant changes. A → B → A switching is supported and leaves a distinct management record each time. A running writer is never taken over by age, and stale-lock release requires explicit authorization. After replacement, invoke `continue` separately in the new agent.

## Repository layout

```text
shared/                         Canonical protocol, task templates, and Skill
  .agents/skills/agent-relay/
  docs/agent/
codex/                          Codex adapter and reusable prompts
cursor/                         Cursor rules and commands
distribution/                   Release installation instructions
```

## Installation choices

For the complete command and lifecycle reference, see [Agent Relay Usage](docs/AGENT_RELAY_USAGE.en-US.md) or the [Chinese guide](docs/AGENT_RELAY_USAGE.md).

For a new repository, prefer the Skill's built-in initializer. It copies only missing files and preserves existing instructions and project state.

For a manual installation, follow [distribution/INSTALL.md](distribution/INSTALL.md). The automatic initializer deliberately excludes `TASK-EXAMPLE-001`; manual source copying may include it as documentation only, never as an active task.

Migrating an existing v1.4 installation? Read [v1.5 migration](docs/migration-v1.5.md), including the explicit handoff package for uncommitted work.

Release ZIP archives and SHA-256 checksums are published as GitHub Release assets. They are not tracked in the source repository.

## Safety boundaries

- This is a Relay protocol, not a scheduler, permission system, automatic handoff mechanism, Git replacement, or distributed lock. It does not automatically synchronize machines or worktrees.
- The helper lock protects coordination state only within one checkout; it does not lock product code, coordinate machines, merge, release, or deploy.
- The default model is one active task and one writer session in one working directory.
- Different worktrees and machines require explicit Git synchronization and version checks.
- `DONE` means task acceptance only; it never authorizes merge, deployment, release, deletion, rollback, or takeover.
- If a host blocks `.agents/` writes, the workflow falls back to the loaded global Skill plus `docs/agent/protocol.md`.

## Validation and contribution

Run the release-equivalent validation before contributing:

```bash
bash .github/scripts/validate-release.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md). The project is licensed under [Apache-2.0](LICENSE).
