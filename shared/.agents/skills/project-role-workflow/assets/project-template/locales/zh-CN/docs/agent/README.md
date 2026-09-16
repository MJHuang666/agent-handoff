# 多 Agent 协作说明

本目录是所有 Agent 的共享项目上下文。开始工作前先读 `PROJECT_STATUS.md`、活动任务 `STATE.md`、`protocol.md` 和 `workflow.md`。

## 语言

`PROJECT_STATUS.md.language` 是项目语言。交流、需求、计划、执行记录、审查、进度、决策和验收报告全部使用该语言。文件名、YAML 字段、状态值、参与者 ID 和交付 ID 保持稳定。

## 文件职责

| 文件或目录 | 权威内容 |
|---|---|
| `PROJECT_STATUS.md` | 项目总览和唯一活动任务 |
| `tasks/<task>/STATE.md` | 任务阶段、参与者、会话和证据 |
| `role-bindings.md` | 参与者身份和默认绑定 |
| `roles/` | 角色职责和权限 |
| `protocol.md` | 核心角色、写入和交接协议 |
| `workflow.md` | 状态流转、交接和恢复规则 |
| `tasks/` | 任务模板、交付物和追加式历史 |

在对应工具说“继续”。如果未轮到当前参与者，Agent 只读并报告正在等待的角色和参与者。
