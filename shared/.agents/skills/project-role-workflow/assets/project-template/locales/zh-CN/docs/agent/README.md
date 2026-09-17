# Agent Collaboration Guide

本目录是安装后所有 Agent 的项目上下文入口。开始工作先读 `PROJECT_STATUS.md`，再读活动任务的 `STATE.md` 和 `workflow.md`。

## What Each File Owns

| File or directory | Authority |
|---|---|
| `PROJECT_STATUS.md` | 项目总览及唯一 active_task |
| `tasks/<task>/STATE.md` | 当前任务阶段、参与者、会话、版本引用和异常状态 |
| `role-bindings.md` | participant_id、tool、role、Profile 及项目默认绑定 |
| `roles/` | 三个角色的通用职责和权限 |
| `profiles/` | 参与者身份及项目差异 |
| `workflow.md` | 日常流程、状态、交接和恢复规则 |
| `protocol.md` | 在项目级 Skill 不可用时仍可读取的核心角色与写入协议 |
| `conventions.md` | 命名、时间、版本和历史规范 |
| `integrations.md` | 各工具自动入口及实际验证状态 |
| `architecture/` | 跨任务长期架构事实和约束 |
| `tasks/` | 任务模板、正式交付物和追加式历史 |

## Register Participants

首次使用 Skill 时，先选择并记录项目语言：

```text
1. 中文（zh-CN）
2. English（en-US）
```

语言必须先写入 `PROJECT_STATUS.md`，之后才询问角色和工具：

```text
角色：Planner / Implementer / Reviewer
工具：Codex / Cursor / Claude Code / WorkBuddy / ZCode / Trae / DeepSeek Harness / OpenCode / 其他
```

为身份选择稳定的 participant_id，例如 `planner-main`、`implementation-cursor`、`review-codex`。复制 `profiles/_templates/participant.md` 到 `profiles/<tool>/<participant_id>.md`，填写真实字段，并在 `role-bindings.md` 登记。

participant_id、tool、role 创建后不可更改或改作另一身份。身份状态分为 active、standby、retired；更换 Agent 时创建或复用同角色身份，之后可以 A → B → A 多次切换。若一个工具有多个身份，新会话只需要选择 participant_id，不需要重述任务背景。

## Create the First Task

1. 确认 active_task 为 null，或用户已经授权切换任务。
2. 复制 `tasks/_template/` 为新的 `TASK-YYYYMMDD-NNN/`。
3. 从项目默认绑定生成 STATE assignments，形成任务级快照。
4. Planner 填写 requirement 和 STATE，创建首条 planning progress。
5. 把 PROJECT_STATUS active_task 指向新任务，并增加任务索引行。
6. Planner 读取真实代码和架构，完成 plan。授权已经在当前会话明确给出时可直接引用；没有授权时保持 PLANNING。

初始化可以创建空白 execution、review 和 decisions 模板，但 Planner 不填写其他角色的结论。

## Continue From a New Chat

在对应工具说“继续”或 `continue`。Agent 应：

1. 恢复或确认 participant_id；
2. 核对 active_task 和 STATE；
3. 发现多个同工具身份时只询问选哪个；
4. 发现其他 writer_session 为 running 时保持只读；
5. 轮到自己时读取角色文件、requirement、上一交付物、有效 checkpoint、decisions 和实际代码版本；
6. 登记本会话后开始工作。

轮到 Implementer 时，如果任务 `subagent_policy` 还是 `UNSELECTED`，必须先询问本次实施“使用子代理 / 不使用子代理”，记录选择后才允许修改产品代码。

如果旧 writer_session 仍为 running，“旧窗口可能卡死”或长时间沉默都不足以自动接管。先通过只读信息确认原会话已经停止，再取得明确接管授权并记录管理事件。

## 更换 Agent

旧 Agent 或新 Agent 都可以说 `$project-role-workflow 更换 Agent`、`替换 Agent`、`replace agent` 或 `switch agent`。工作流会依次选择角色、影响范围（当前任务/未来默认/两者）及同角色的新 participant，并在确认后调用标准库 Python 辅助脚本完成短时文件锁、revision 校验和原子写入。

更换只迁移角色责任，不修改角色本身。旧身份和历史保留；不再被默认值或非终态任务引用时转为 standby，之后可再次切回。更换 Implementer 会重新询问是否使用子代理。更换完成后，在新 Agent 单独说“继续”，管理操作不会顺带修改产品代码。

Python 不可用时仍可按 Markdown 协议人工串行操作，但必须明确标记为降级模式；此时没有技术性的锁与 CAS 保护。

## Work and Handoff

完整规则见 `workflow.md`。交接顺序固定为：

1. 完成本角色正式交付物及版本证据；
2. 追加 progress 记录；
3. 更新 STATE，使交接生效；
4. 最后刷新 PROJECT_STATUS 缓存；
5. 告诉用户下一位 participant/tool，并提示在对应窗口说“继续”。

只有 STATE 更新会改变当前执行者。孤立的 progress 文件不代表已经交接。

## Switch Tasks

非活动任务始终只读，即使参与者和角色匹配。切换前由用户指定目标任务，并确认原活动任务已经暂停、阻塞、终止或完成，且没有写入会话。更新 PROJECT_STATUS active_task 后，新任务才允许业务写入。active_task 为空时，Agent 不自行从待办中挑任务。

## Pause, Block, Repair, and Cancel

- 暂停：写 CHECKPOINT，execution=paused，清空 writer_session；阶段不变。
- 阻塞：另记原因、解除条件、恢复状态和责任参与者；不靠时间自动恢复。
- 修复：状态、引用或历史损坏时，由用户授权单独的修复会话；等待者和已交出的旧角色都不能自行修正。
- 取消：进入 CANCELLED，记录代码如何保留，不自动回滚。
- 终态：清空执行者、会话和 active_task，不自动挑下一个任务。

## Different Worktrees or Machines

默认在同一工作目录串行接力。如果必须换 worktree 或机器：

1. 停止原会话并清除写入占用；
2. 使用用户授权的 Git 操作或明确交接包同步代码和全部任务文档；
3. 核对仓库、分支、完整提交 ID、脏文件、未跟踪文件和 delivery_id；
4. 在新目录确认内容一致后再登记会话。

协议本身不授权自动提交、合并或覆盖任何工作区。

## Archive

DONE 或 CANCELLED 的任务保留完整目录和稳定链接。将任务从主表移到 PROJECT_STATUS 的 Archive 索引，不修改历史文件。归档只整理索引，不删除任务证据。
