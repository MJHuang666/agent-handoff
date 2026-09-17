# Agent Relay

> 让记忆属于项目，而不是属于某个 Agent。

[English](README.md) · [最新版本](https://github.com/MJHuang666/multi-agent-relay/releases/latest) · [使用手册](docs/AGENT_RELAY_USAGE.md)

[![Release](https://img.shields.io/github/v/release/MJHuang666/multi-agent-relay?display_name=tag&color=7C3AED)](https://github.com/MJHuang666/multi-agent-relay/releases/latest)
[![License](https://img.shields.io/badge/license-Apache--2.0-0EA5E9)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/MJHuang666/multi-agent-relay/validate-release.yml?label=validation)](https://github.com/MJHuang666/multi-agent-relay/actions)

<img width="1672" height="941" alt="Agent Relay 工作流" src="https://github.com/user-attachments/assets/2d9e7307-8cb5-4f12-b91d-ca0beef9d3fd" />

**Agent Relay 是一个轻量级多 Agent 接力协作框架，解决不同 Coding Agent 上下文不共享的问题。** 它让多个 Agent 围绕同一代码仓库持续完成 Plan → Implement → Review → Handoff，并把一次次对话沉淀成可迁移、可恢复、与 Agent 解耦的项目认知。

Agent 不需要共享 Conversation Context（对话上下文），只需要 Relay（接力）项目状态。

## 它解决的不是“聊天”，而是项目认知会丢失

Agent 可能停止，聊天窗口可能结束，模型可能更换，电脑可能迁移，开发环境也可能被重装。

但项目长期积累的“认知资产”不能跟着消失。

Agent Relay 把真正需要继承的内容保存在仓库中：需求、计划、架构约束、决策、实施证据、审查结论、交接记录，以及紧凑的长期知识索引。无论哪个 Agent 在什么时候加入，都能读取这些项目状态，恢复这个项目已经积累的有效认知，而不必重新翻找或复述旧对话。

```text
临时的对话上下文                              可持久化的项目认知
────────────────                              ──────────────────
一个窗口 · 一个模型 · 一台电脑       ──►      仓库文件 · Git 历史 · 可验证证据
                                                   ↓
                                      任意兼容 Agent 都可以接力恢复
```

## 一个仓库，一条接力链

```text
需求 → 计划 → 实施 → 审查 → 返修 → 验证 → 交接
       docs/agent/tasks/<TASK-ID>/
```

每次交接都会留下：做了什么、为什么这样做、验证了什么、下一步由谁执行。接棒的 Agent 读取项目接力记录，而不是从不完整的聊天窗口里猜测上下文。

| 被保存下来的认知 | 为什么重要 |
|---|---|
| `PROJECT_STATUS.md` + `STATE.md` | 恢复活动任务、当前角色、参与者、revision 与交接位置。 |
| `knowledge-index.md` | 让已经验证的架构、约束、决策和经验可以跨任务复用。 |
| 需求、计划、实施、审查、决策文件 | 明确区分目标、实施证据与独立验收。 |
| 追加式 progress 记录 | 保留推理与执行轨迹，又不会把文档变成聊天记录垃圾场。 |
| 绑定 Git 的交付证据 | 让新环境可以确认被审查的究竟是哪一份代码。 |

## 为角色协作而设计，而不是依赖一个“全能 Agent”

| 角色 | 负责 | 边界 |
|---|---|---|
| **Planner** | 范围、非目标、计划、决策、验收标准 | 不修改产品代码。 |
| **Implementer** | 代码、测试、实施证据、审查返修 | 不自行批准交付。 |
| **Reviewer** | 独立审查、验证、完成决策 | 不直接修复产品代码。 |

角色与工具解耦。同一个工具可以承担多个角色；同一角色也可以在不同工具之间切换，而项目状态不会丢失。

<img width="1672" height="941" alt="Planner Implementer Reviewer 交接" src="https://github.com/user-attachments/assets/868c75bd-016f-4ed0-812b-20d53c51bd5e" />

## 三步开始

### 1. 安装 Skill

将 `agent-relay` 安装为个人 Skill，或下载[最新发行包](https://github.com/MJHuang666/multi-agent-relay/releases/latest)。

### 2. 初始化仓库

```text
$agent-relay 初始化当前仓库
# 或
$agent-relay initialize this repository
```

初始化器会先询问项目语言，再为 Planner、Implementer、Reviewer 绑定工具。它只补齐缺失文件，不会覆盖已有项目状态。

### 3. 持续接力

每次交接后，打开分配给下一位参与者的工具并输入：

```text
$agent-relay 继续
# 或
$agent-relay continue
```

Agent 会确认自己的 participant Profile，读取项目接力状态，判断是否轮到自己；若未轮到，就明确报告当前正在等待的参与者。

## 工具无关，项目优先

Agent Relay 为 Codex 与 Cursor 提供直接入口，并为 DeepSeek Harness 和 OpenCode 提供一等共享入口说明。Claude Code、WorkBuddy、ZCode、Trae 及其他 Coding Agent 也可以使用同一套仓库协议。

真正长期稳定的契约不是某个厂商的对话格式，而是项目仓库本身。

| 现实场景 | Relay 如何处理 |
|---|---|
| 某个 Agent 的 token 用完 | 安全替换同角色参与者，记录管理交接并进行 revision 校验。 |
| 切换电脑或 worktree | 显式同步仓库、核验交付版本，再从接力状态恢复。 |
| 聊天或环境重置 | 读取项目总览、知识索引、任务状态和上一个交接记录。 |
| 迁移时存在未提交工作 | 使用已文档化的未提交状态交接包；Git clone 只能恢复已提交状态。 |

## 安全更换 Agent

旧 Agent 或新 Agent 都可以发起同角色参与者更换。A → B → A 可以多次来回切换，每次都会留下可审计的管理记录。

```text
$agent-relay 更换 Agent
$agent-relay 替换 Agent
$agent-relay replace agent
$agent-relay switch agent
```

可选 Python 辅助脚本提供短时本地锁、expected revision 校验和原子化协调写入。它还能识别 v1.4 的旧锁名，并在新旧锁同时存在时拒绝含糊的自动恢复。

## 仓库中的接力结构

```text
.agents/skills/agent-relay/     项目级 Skill 与状态安全脚本
docs/agent/
  PROJECT_STATUS.md              项目入口与活动任务索引
  knowledge-index.md             已验证、可复用的项目认知
  role-bindings.md               稳定的角色与参与者身份
  tasks/<TASK-ID>/               需求、计划、证据、审查与交接
```

完整生命周期请阅读：[中文使用手册](docs/AGENT_RELAY_USAGE.md)、[English guide](docs/AGENT_RELAY_USAGE.en-US.md) 与 [v1.5 迁移说明](docs/migration-v1.5.md)。

## 清晰的边界

Agent Relay 有意保持轻量。它不是调度器、权限系统、Git 替代品、分布式锁或自动部署服务。

- 文件不会自动唤醒另一个 Agent；用户需要打开下一工具继续接力。
- 辅助锁只保护单个 checkout 的协调状态，不锁产品代码，也不协调多台机器。
- Git 同步、合并、发布与部署仍是需要人明确授权的操作。
- `DONE` 只代表任务验收完成。

## 验证与贡献

贡献前运行与发行等价的校验：

```bash
bash .github/scripts/validate-release.sh
```

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)、[SECURITY.md](SECURITY.md) 和 [CHANGELOG.md](CHANGELOG.md)。Agent Relay 使用 [Apache-2.0](LICENSE) 许可证。
