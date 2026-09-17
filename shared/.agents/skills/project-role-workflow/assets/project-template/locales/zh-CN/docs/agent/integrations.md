# 工具集成

文件存在只表示协议可读，不代表工具已经自动加载。每个入口都要用新的真实会话验证。

| 工具 | 协议可读 | 自动入口 | 已提供模板 | 验证状态 | 已验证版本 / 日期 |
|---|---:|---|---:|---|---|
| Codex | 是 | 根 `AGENTS.md` + 全局或项目 Skill | 是 | 待验证 | - |
| Cursor | 是 | `.cursor/rules/` + `.cursor/commands/` | 是 | 待验证 | - |
| Claude Code | 是 | 按目标版本配置 | 否 | 未配置 | - |
| WorkBuddy | 是 | 按目标版本配置 | 否 | 未配置 | - |
| ZCode | 是 | 按目标版本配置 | 否 | 未配置 | - |
| Trae | 是 | 按目标版本配置 | 否 | 未配置 | - |
| DeepSeek Harness | 是 | 根 `AGENTS.md` + `.agents/skills/project-role-workflow/`；启用 `dsh-agent-instructions` 和文件系统 Skill 加载 | 是 | 静态验证完成，待真实会话 | 本地源码 / 2026-09-17 |
| OpenCode | 是 | 根 `AGENTS.md` + `.agents/skills/project-role-workflow/` | 是 | 已验证 | 1.3.17 / 2026-09-17 |
| 其他 | 是 | 记录该工具支持的入口 | 否 | 未配置 | - |

启动全新会话，只说“继续”，确认工具主动读取项目状态、任务状态、语言、身份和角色后再标记已验证。

DeepSeek Harness 和 OpenCode 以 `.agents/skills/project-role-workflow/` 为唯一事实源，不创建 `.dsh/skills` 或 `.opencode/skills` 副本。OpenCode 无法发现 Skill 时，检查 Skill 权限和高优先级同名副本。
