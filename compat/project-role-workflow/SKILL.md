---
name: project-role-workflow
description: Legacy v1.4 compatibility entry for Agent Relay. Redirects the former command name without carrying a second workflow implementation.
---

# Project Role Workflow compatibility entry

`project-role-workflow` was renamed to **Agent Relay** in v1.5. Use the
sibling `agent-relay` Skill and its current repository-local copy instead.

Map legacy calls directly:

| Legacy | Current |
|---|---|
| `$project-role-workflow 初始化当前仓库` | `$agent-relay 初始化当前仓库` |
| `$project-role-workflow 继续` | `$agent-relay 继续` |
| `$project-role-workflow 更换 Agent` / `$project-role-workflow 替换 Agent` | `$agent-relay 更换 Agent` / `$agent-relay 替换 Agent` |
| `$project-role-workflow initialize this repository` | `$agent-relay initialize this repository` |
| `$project-role-workflow continue` | `$agent-relay continue` |
| `$project-role-workflow replace agent` / `$project-role-workflow switch agent` | `$agent-relay replace agent` / `$agent-relay switch agent` |

Do not create, copy, or modify task state through this shim. Read
`../agent-relay/SKILL.md` and continue there. This compatibility entry is
scheduled for removal in v2.0.
