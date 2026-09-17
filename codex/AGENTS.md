<!-- agent-relay:start -->
# Multi-Agent Project Rules

Accept both Chinese and English explicit commands:

- `$agent-relay 初始化当前仓库` / `$agent-relay initialize this repository`
- `$agent-relay 继续` / `$agent-relay continue`
- `$agent-relay 更换 Agent` / `$agent-relay 替换 Agent` / `$agent-relay replace agent` / `$agent-relay switch agent`

During initialization ask for project language (`zh-CN` or `en-US`) before role-tool selection. Use the recorded language for all communication and new task documents. Before an Implementer edits product code, require an explicit `USE` or `DO_NOT_USE` subagent choice in task STATE.

When this repository contains `docs/agent/PROJECT_STATUS.md`, any request to create, plan, implement, resume, review, repair, verify, switch, or close a task must use the global or project `agent-relay` Skill. If the project Skill is unavailable, read `docs/agent/protocol.md` and `docs/agent/workflow.md` directly.

Before any task write:

1. Read `docs/agent/PROJECT_STATUS.md`, skim `docs/agent/knowledge-index.md`, and then read the active task `STATE.md`.
2. Resolve the session participant from `docs/agent/role-bindings.md`; if this tool has multiple identities, ask the user to select a participant_id.
3. Verify active task, current participant, role, assignment, writer_session, workdir, and delivery version.
4. Read the participant Profile, its shared role file, required task inputs, relevant knowledge-index sources, and the Skill protocol.

If the task or identity is not current, or another session is writing, remain read-only and report the awaited role and participant. Never infer identity from the role currently needed, never take over a running session because it appears stale, and never use chat history as a substitute for project records.

Project state files coordinate behavior; they are not locks or authorization to merge, release, deploy, delete, reset, or overwrite work.

Agent replacement is a separate management operation. Keep the role fixed, select current-task/project-default/both scope, and use the Skill's `workflow_state.py` helper for lock, expected-revision, and atomic-write protection. Repeated A → B → A switching reuses immutable participant IDs. Never auto-release a state lock or combine replacement with product edits.
<!-- agent-relay:end -->
