# Project Role Workflow

[简体中文](README.zh-CN.md)

If you subscribe to the $20 ChatGPT Plus plan, you can delegate planning, design, and review to GPT-6 Astra or GPT-5.6 Sol, while handing off the heavy implementation work to Cursor 5.6, DeepSeek, or other tools.

The best part is that communication between agents doesn’t need to rely on conversation context at all.

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/596acdcc-4126-460f-bb8a-5ed35359d4a4" />

Project Role Workflow is a Markdown-first collaboration protocol for coding agents. Planner, Implementer, and Reviewer share project state through files in the repository rather than relying on one chat window's memory.

It supports Codex and Cursor entry points today, while keeping roles independent from tools. Claude Code, WorkBuddy, ZCode, Trae, and other tools can use the same shared protocol when configured with a thin project-level instruction.

## Why it exists

Agent conversations do not naturally share context. This template makes the repository the durable handoff surface:

```text
Requirement → Plan → Implementation → Review → Rework → Verification
               docs/agent/tasks/<TASK-ID>/
```

Each role writes fixed deliverables and append-only progress records. The next agent reads the project summary, task state, and prior role output before acting.

## Roles

| Role | Owns | Does not do |
|---|---|---|
| Planner | Requirement, scope, plan, decisions, acceptance criteria | Change product code |
| Implementer | Code, tests, execution evidence, rework | Close review issues |
| Reviewer | Independent review, verification, completion decision | Directly fix product code |

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/be8dc516-a6e7-4c4e-9027-4321259445e7" />


## Quick start

1. Install `shared/.agents/skills/project-role-workflow/` as a personal Skill for your tool.
2. Open a new repository and run either command:

   ```text
   $project-role-workflow initialize this repository
   $project-role-workflow 初始化当前仓库
   ```
<img width="814" height="628" alt="9a3c8948164a8b340d70ad3fc11335e4" src="https://github.com/user-attachments/assets/0d171199-0a2a-45ef-802d-3aadf5998133" />


3. Select `English` or `中文` before assigning a tool to each role.
4. Create the first task with the Planner.
5. Open the next role's tool and say `continue` or `继续` at each handoff.

<img width="840" height="362" alt="2c7493b4c6a7366e669c5f0bcb1274c5" src="https://github.com/user-attachments/assets/d285da83-36d3-43ce-9a30-0d2ef4a8211d" />


The selected language controls later user-facing conversation and task prose. Stable file names, YAML keys, IDs, and status enums remain unchanged.

Before product-code work, an Implementer must ask whether to use subagents. The explicit choice is recorded in the task state; no code work starts while the choice is unselected.

## Repository layout

```text
shared/                         Canonical protocol, task templates, and Skill
  .agents/skills/project-role-workflow/
  docs/agent/
codex/                          Codex adapter and reusable prompts
cursor/                         Cursor rules and commands
distribution/                   Release installation instructions
```

## Installation choices

For a new repository, prefer the Skill's built-in initializer. It copies only missing files and preserves existing instructions and project state.

For a manual installation, follow [distribution/INSTALL.md](distribution/INSTALL.md). The automatic initializer deliberately excludes `TASK-EXAMPLE-001`; manual source copying may include it as documentation only, never as an active task.

Release ZIP archives and SHA-256 checksums are published as GitHub Release assets. They are not tracked in the source repository.

## Safety boundaries

- This is a file protocol, not a scheduler, file lock, permission system, or automatic agent handoff mechanism.
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
