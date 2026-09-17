# Tool Integrations

Files being present proves only that the protocol is readable. Verify each automatic entry with a fresh real session.

| Tool | Protocol Readable | Automatic Entry | Template Supplied | Verification Status | Verified Version / Date |
|---|---:|---|---:|---|---|
| Codex | Yes | Root `AGENTS.md` + `.agents/skills/` | Yes | Pending | - |
| Cursor | Yes | `.cursor/rules/` + `.cursor/commands/` + `.agents/skills/` | Yes | Pending | - |
| Claude Code | Yes | Configure for the target version | No | Not configured | - |
| WorkBuddy | Yes | Configure for the target version | No | Not configured | - |
| ZCode | Yes | Configure for the target version | No | Not configured | - |
| Trae | Yes | Configure for the target version | No | Not configured | - |
| DeepSeek Harness | Yes | Root `AGENTS.md` + `.agents/skills/agent-relay/`; enable `dsh-agent-instructions` and filesystem skill loading | Yes | Static verification complete; fresh session pending | Local source / 2026-09-17 |
| OpenCode | Yes | Root `AGENTS.md` + `.agents/skills/agent-relay/` | Yes | Verified | 1.3.17 / 2026-09-17 |
| Other | Yes | Record the entry supported by that tool | No | Not configured | - |

Start a fresh session, say only `continue`, and verify that the tool reads project status, task state, language, identity, and role before changing this table to verified.

DeepSeek Harness and OpenCode share `.agents/skills/agent-relay/` as the single source of truth. Do not create duplicate `.dsh/skills` or `.opencode/skills` trees. If OpenCode does not discover the skill, check skill permissions and higher-priority same-name copies.
