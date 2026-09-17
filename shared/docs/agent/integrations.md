# Tool Integrations

文件存在只表示协议可读，不表示工具已经自动加载。每个入口都要用新的真实会话验证。

| Tool | Protocol Readable | Automatic Entry | Template Supplied | Verification Status | Verified Version / Date |
|---|---:|---|---:|---|---|
| Codex | 是 | 根目录 `AGENTS.md` + 全局或项目 Skill；项目 Skill 不可写时读取 `docs/agent/protocol.md` | 是 | 待验证 | - |
| Cursor | 是 | `.cursor/rules/` + `.cursor/commands/`；项目 Skill 不可用时读取 `docs/agent/protocol.md` | 是 | 待验证 | - |
| Claude Code | 是 | 按目标版本配置项目入口 | 否 | 未配置 | - |
| WorkBuddy | 是 | 按目标版本配置项目入口 | 否 | 未配置 | - |
| ZCode | 是 | 按目标版本配置项目入口 | 否 | 未配置 | - |
| Trae | 是 | 按目标版本配置项目入口 | 否 | 未配置 | - |
| DeepSeek Harness | 是 | 根目录 `AGENTS.md` + `.agents/skills/project-role-workflow/`；需启用 `dsh-agent-instructions` 和文件系统 Skill 加载 | 是 | 静态验证完成，待真实会话 | 本地源码 / 2026-09-17 |
| OpenCode | 是 | 根目录 `AGENTS.md` + `.agents/skills/project-role-workflow/` | 是 | 已验证 | 1.3.17 / 2026-09-17 |
| 其他 | 是 | 记录该工具实际支持的入口 | 否 | 未配置 | - |

## Verification Procedure

1. 从目标仓库启动一个全新会话。
2. 只说“继续”，不手工粘贴协议。
3. 检查工具能否主动读取 `PROJECT_STATUS.md`、当前 `STATE.md`、身份 Profile 和角色文件。
4. 让工具说明当前活动任务、当前参与者和是否轮到自己。
5. 记录工具版本、入口文件和日期；失败时保持“待验证”或“未配置”。

## Shared-entry notes

- DeepSeek Harness 应让 `dsh-agent-instructions` 加载根 `AGENTS.md`，并启用能够扫描项目 `.agents/skills/` 的文件系统 Skill 加载器。不要创建 `.dsh/skills` 副本。
- OpenCode 直接使用根 `AGENTS.md` 和 `.agents/skills/`。如果 Skill 未出现，检查 Skill 权限以及 `.opencode/skills/` 中是否有同名高优先级副本；不要复制第二份。
