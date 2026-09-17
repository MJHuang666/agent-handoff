# Agent Relay 使用手册

本文对应 `agent-relay` Skill v1.5.0，说明初始化、任务接力、Agent 更换、暂停恢复、状态查询和最终验收。

## 1. 初始化仓库

```text
$agent-relay 初始化当前仓库
$agent-relay initialize this repository
```

Skill 会先检查仓库，然后按顺序询问项目语言（中文 `zh-CN` / English `en-US`）、Planner、Implementer、Reviewer 的 Agent，最后建立项目文件、Profile 和绑定。

初始化不创建真实任务，不覆盖既有项目文件、任务记录或产品代码。

## 2. Agent 选择

| 选项 | 稳定 Tool ID |
|---|---|
| Codex | `codex` |
| Cursor | `cursor` |
| Claude Code | `claude-code` |
| WorkBuddy | `workbuddy` |
| ZCode | `zcode` |
| Trae | `trae` |
| DeepSeek Harness | `deepseek-harness` |
| OpenCode | `opencode` |
| Other | 用户提供稳定 ID |

同一 Agent 可承担多个角色，但每个参与者必须有唯一 `participant_id`。

## 3. 创建任务

```text
创建一个任务，实现用户登录功能
```

```text
docs/agent/tasks/<TASK-ID>/
├── STATE.md          # 唯一实时状态源
├── requirement.md    # 需求、范围、验收标准
├── plan.md           # Planner 交付
├── execution.md      # Implementer 交付和返修
├── review.md         # Reviewer 审查和结论
├── decisions.md      # 持久决策
└── progress/         # 追加式过程记录
```

## 4. 统一接力

```text
继续
continue
$agent-relay 继续
$agent-relay continue
```

每次接棒都会先读取 `PROJECT_STATUS.md`、任务 `STATE.md`、`role-bindings.md`、Profile、角色文件和上一阶段交付物。未轮到当前 Agent 时仅报告等待，不修改代码或状态。

## 5. Planner

```text
请作为 Planner 规划当前任务
```

Planner 负责需求、范围、约束、风险、决策、`plan.md` 和验收标准，不修改产品代码。

## 6. Implementer

```text
请作为 Implementer 实施当前已批准计划
```

修改产品代码前必须先选择：

```text
USE          # 使用子代理
DO_NOT_USE   # 不使用子代理
```

Implementer 按批准计划修改代码和测试，记录 `delivery_id`、测试证据和 `execution.md`，然后交给 Reviewer。Reviewer 返回问题后：

```text
请处理 Reviewer 当前提出的修改意见
```

返修必须新建交付证据，不覆盖历史记录。

## 7. Reviewer 与关闭

```text
请作为 Reviewer 审查当前任务
请验证当前任务并关闭
```

Reviewer 独立检查需求、计划、代码差异、测试和交付版本，并返回 `CHANGES_REQUESTED`、`VERIFYING`、`PLANNING`、`BLOCKED` 或 `DONE`。

`DONE` 只表示任务验收完成，不自动合并、发布、部署、删除或推送。

## 8. 更换 Agent

```text
$agent-relay 更换 Agent
$agent-relay 替换 Agent
$agent-relay replace agent
$agent-relay switch agent
```

然后选择角色、范围 `current-task` / `project-default` / `both`、同角色参与者、原因和授权。支持重复切换：

```text
Codex → Cursor → OpenCode → Codex
```

旧身份、历史和 MANAGEMENT 记录会保留。当前责任参与者变化时会增加 `stage_round`，并清除旧写入会话和检查点。

## 9. 暂停、恢复和阻塞

```text
暂停当前任务，记录检查点
继续
当前任务被 API 凭证问题阻塞，请记录阻塞状态
```

恢复前必须核对磁盘差异、进程、副作用和交付证据，不能盲目重复上次操作。

## 10. 状态查询和辅助脚本

```bash
python3 .agents/skills/agent-relay/scripts/workflow_state.py \
  --repo . status
```

该脚本提供短时本地锁、`revision` CAS 和原子写入，只保护协调状态，不锁产品代码。

```bash
python3 .agents/skills/agent-relay/scripts/workflow_state.py \
  --repo . replace-agent \
  --role implementer \
  --from cursor-impl \
  --to opencode-impl \
  --scope current-task \
  --expected-revision 10 \
  --reason "Cursor quota exhausted" \
  --authorization "User approved in the current conversation"
```

只有在确认旧会话已停止并获得授权后，才能使用 `release-stale-lock`。

## 11. 写入权限和等待

只有当任务等于 `PROJECT_STATUS.md` 的 `active_task`、身份与 `STATE.md` 一致、assignment 匹配、无其他 writer 且已核对工作目录和交付版本时，才允许业务写入。

任务不是活动任务、不是当前参与者、有其他 writer、revision 不匹配或状态矛盾时，必须只读等待。

## 12. 工具共享入口

Codex、Cursor、DeepSeek Harness 和 OpenCode 共用根 `AGENTS.md`、`docs/agent/` 和 `.agents/skills/agent-relay/`。DeepSeek Harness 需启用 `dsh-agent-instructions` 和项目 Skill 加载；OpenCode 直接发现根 `AGENTS.md` 和 `.agents/skills/`。不创建 `.dsh/skills` 或 `.opencode/skills` 副本。

## 13. 标准流程

```text
初始化 → 选择语言和角色 Agent
       → Planner 规划
       → Implementer 实施
       → Reviewer 审查
       → Implementer 返修（如有）
       → Reviewer 验证
       → DONE
```

更多细节见 [Skill 主说明](../shared/.agents/skills/agent-relay/SKILL.md)、[初始化参考](../shared/.agents/skills/agent-relay/references/initialization.md)、[协作协议](../shared/.agents/skills/agent-relay/references/protocol.md)、[安装说明](../distribution/INSTALL.md)。
