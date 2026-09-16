# Repository Initialization

Use this procedure when the user asks to initialize Project Role Workflow, using either `初始化当前仓库` or `initialize this repository`, or explicitly invokes the Skill in a repository without `docs/agent/PROJECT_STATUS.md`.

The template source is `assets/project-template/`, resolved relative to this Skill directory. No Python runtime is required.

## Preflight

1. Resolve the target repository root from the current workspace. Never initialize a parent directory, home directory, or another repository by inference.
2. Inspect existing `AGENTS.md`, `.agents/`, `.cursor/`, and `docs/agent/` paths before writing.
3. If the target is not clear, ask for the repository path. If it is clear, proceed without asking for confirmation again.
4. Do not initialize inside this Skill's own `assets/` directory.

## Choose Language First

Before asking which tools serve the roles, ask the user to select exactly one project language:

1. 中文（`zh-CN`）
2. English（`en-US`）

Write the choice to `docs/agent/PROJECT_STATUS.md` as `language: zh-CN` or `language: en-US`. If the user uses a bilingual command but does not choose a language, ask this question and pause role selection until it is answered. All subsequent user-facing communication and newly authored task documents use the selected language. Stable YAML keys and enum values remain unchanged.

## Install the Baseline

Copy the shared documentation from `assets/project-template/shared/docs/` into repository root `docs/`. Do not copy `tasks/TASK-EXAMPLE-001`; examples are distribution documentation, not initialized project state.

Then try to copy the project runtime Skill:

```text
.agents/skills/project-role-workflow/
```

If the host sandbox blocks writes to `.agents/`, do not fail or create workaround files. Continue with the already loaded global Skill plus `docs/agent/protocol.md`, install the Codex/Cursor adapters, and report project-level Skill installation as pending. A later trusted installer may copy it. The workflow must remain usable without the project-level Skill. Treat this host-policy denial as an expected compatibility fallback, not as a workflow error; do not create repository-local error logs such as `.learnings/` solely because of it.

Overlay the corresponding files from `assets/project-template/locales/<language>/` after the baseline copy. The overlay must not replace pre-existing project files; it only localizes files created in this initialization.

Then install tool adapters:

- Codex: if root `AGENTS.md` is absent, copy `assets/project-template/adapters/codex/AGENTS.md`. If it exists and lacks the marked Project Role Workflow block, append that block without changing existing text. If the block exists, leave it unchanged.
- Cursor: copy missing files from `assets/project-template/adapters/cursor/.cursor/` to root `.cursor/`. Preserve any existing same-path file and report it for manual comparison.

For all other same-path collisions, preserve the target file. Fill only missing files and report differing files. Never replace `PROJECT_STATUS.md`, `role-bindings.md`, Profiles, task records, architecture constraints, or product instructions with template content.

Ignore `._*` and `.DS_Store` files.

## Configure Identities

The copied baseline intentionally has `active_task: null` and no real participant registrations.

After the language is recorded, ask the user for the tool that will serve each role:

1. Planner
2. Implementer, including rework
3. Reviewer

Supported labels include Codex, Cursor, Claude Code, WorkBuddy, ZCode, Trae, and Other. One tool may serve multiple roles, but every identity needs a unique `participant_id`.

For each identity, create a Profile from `docs/agent/profiles/_templates/participant.md` and register the immutable `(participant_id, tool, role)` tuple in `docs/agent/role-bindings.md`. Do not infer these choices from the current tool or create a real task during initialization.

## Verify

Before reporting success, verify:

- `docs/agent/PROJECT_STATUS.md` exists and keeps `active_task: null`.
- all three role files and every task template file exist.
- `docs/agent/protocol.md` exists; the project-level Skill is either installed or explicitly reported pending because the host denied `.agents/` writes.
- the Codex block is present in root `AGENTS.md` without losing prior content.
- Cursor rule and command files exist unless preserved collisions were reported.
- local Markdown links resolve.
- no product code or real task was created.

Report created files, preserved collisions, configured language and identities, and adapters that still require a real new-session verification.
