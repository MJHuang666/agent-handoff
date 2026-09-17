# Agent Relay

> Make memory belong to the project, not the Agent.

[简体中文](README.zh-CN.md) · [Release](https://github.com/MJHuang666/multi-agent-relay/releases/latest) · [Usage guide](docs/AGENT_RELAY_USAGE.en-US.md)

[![Release](https://img.shields.io/github/v/release/MJHuang666/multi-agent-relay?display_name=tag&color=7C3AED)](https://github.com/MJHuang666/multi-agent-relay/releases/latest)
[![License](https://img.shields.io/badge/license-Apache--2.0-0EA5E9)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/MJHuang666/multi-agent-relay/validate-release.yml?label=validation)](https://github.com/MJHuang666/multi-agent-relay/actions)

<img width="1672" height="941" alt="Agent Relay workflow" src="https://github.com/user-attachments/assets/c613f203-32b8-4056-aa8e-1f53f6ec1200" />

**Agent Relay is a lightweight multi-Agent collaboration framework for sustained work in one code repository.** It turns fragmented Coding Agent conversations into durable, portable project cognition: Plan → Implement → Review → Handoff.

Agents do not need to share a Conversation Context. They only need to relay the project state stored in the repository.

## The problem it solves

An Agent can run out of context. A chat can disappear. A model can change. A machine can be replaced. An environment can be rebuilt.

The project’s accumulated understanding must not disappear with any of them.

Agent Relay keeps the durable part of that understanding in versioned, human-readable project files: requirements, plans, decisions, constraints, execution evidence, reviews, handoffs, and a compact knowledge index. Any Agent can join later, read the relay, and recover the effective context without replaying every prior conversation.

```text
Temporary conversation context                 Durable project cognition
─────────────────────────────                ───────────────────────────
one chat · one model · one machine   ──►     repository files · Git history · evidence
                                               ↓
                                      any compatible Agent can resume
```

## One repository, one relay

```text
Requirement → Plan → Implement → Review → Rework → Verify → Handoff
                    docs/agent/tasks/<TASK-ID>/
```

Every handoff records what happened, why it happened, what was verified, and who acts next. The next Agent reads the relay instead of guessing from an incomplete chat window.

| What becomes durable | Why it matters |
|---|---|
| `PROJECT_STATUS.md` + `STATE.md` | Restores the active task, current role, participant, revision, and handoff point. |
| `knowledge-index.md` | Makes verified architecture, constraints, decisions, and lessons reusable across tasks. |
| Requirement, plan, execution, review, and decisions | Separates intent, implementation evidence, and independent acceptance. |
| Append-only progress records | Preserves the reasoning trail without turning docs into chat logs. |
| Git-bound delivery evidence | Lets a new environment verify exactly what was reviewed. |

## Built for role collaboration, not one “super Agent”

| Role | Owns | Guardrail |
|---|---|---|
| **Planner** | Scope, non-goals, plan, decisions, acceptance criteria | Does not change product code. |
| **Implementer** | Code, tests, execution evidence, review rework | Does not self-approve delivery. |
| **Reviewer** | Independent review, verification, completion decision | Does not directly fix product code. |

Roles are independent from tools. The same tool can serve multiple roles; a role can move between tools without losing the project’s shared state.

<img width="1672" height="941" alt="Planner Implementer Reviewer handoff" src="https://github.com/user-attachments/assets/be8dc516-a6e7-4c4e-9027-4321259445e7" />

## Start in three steps

### 1. Install the Skill

Install `agent-relay` as a personal Skill, or download the [latest release](https://github.com/MJHuang666/multi-agent-relay/releases/latest).

### 2. Initialize the repository

```text
$agent-relay initialize this repository
# or
$agent-relay 初始化当前仓库
```

The initializer asks for the project language first, then binds a tool to Planner, Implementer, and Reviewer. It copies only missing files and preserves existing project state.

### 3. Relay the work

At every handoff, open the assigned tool and say:

```text
$agent-relay continue
# or
$agent-relay 继续
```

The Agent identifies its participant profile, reads the project relay, checks whether it is its turn, and either works or reports the participant currently awaited.

## Tool-agnostic by design

Agent Relay provides direct entry points for Codex and Cursor, plus first-class shared entry guidance for DeepSeek Harness and OpenCode. Claude Code, WorkBuddy, ZCode, Trae, and other Coding Agents can use the same repository protocol.

The durable contract is the repository, not a vendor-specific conversation format.

| Need | Relay behavior |
|---|---|
| Change Agent because a token budget ends | Replace the same-role participant with revision checks and a recorded management handoff. |
| Move to another computer or worktree | Sync the repository deliberately, verify the delivery version, then resume from the relay. |
| Recover after a chat or environment reset | Read project status, knowledge index, task state, and the preceding handoff. |
| Preserve dirty work during migration | Build the documented uncommitted-state handoff package; a Git clone alone carries committed state only. |

## Safe Agent replacement

The old or new Agent can initiate a same-role replacement. A → B → A is supported, and each switch leaves a traceable management record.

```text
$agent-relay replace agent
$agent-relay switch agent
$agent-relay 更换 Agent
$agent-relay 替换 Agent
```

The optional Python helper adds a short-lived local lock, expected-revision validation, and atomic coordination writes. It recognizes the legacy v1.4 lock name during migration and refuses ambiguous double-lock recovery.

## Repository layout

```text
.agents/skills/agent-relay/     Project-local Skill and safety helper
docs/agent/
  PROJECT_STATUS.md              Project entry point and active-task index
  knowledge-index.md             Verified reusable project cognition
  role-bindings.md               Stable role and participant identities
  tasks/<TASK-ID>/               Requirement, plan, evidence, review, handoff
```

For the full lifecycle, see the [English usage guide](docs/AGENT_RELAY_USAGE.en-US.md), [Chinese usage guide](docs/AGENT_RELAY_USAGE.md), and [v1.5 migration guide](docs/migration-v1.5.md).

## Clear boundaries

Agent Relay is deliberately small. It is not a scheduler, a permissions system, a Git replacement, a distributed lock, or an automatic deployment service.

- Files do not wake another Agent automatically; the user opens the next tool and continues the relay.
- The helper lock protects coordination state in one checkout, not product code or multiple machines.
- Git synchronization, merges, releases, and deployment remain explicit human-authorized operations.
- `DONE` means task acceptance only.

## Validate and contribute

Run the release-equivalent validation before contributing:

```bash
bash .github/scripts/validate-release.sh
```

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md). Agent Relay is licensed under [Apache-2.0](LICENSE).
