# Agent Relay

> 多 Agent 项目状态共享框架

[English](README.md)

让记忆属于项目，而不是属于 Agent。

一个面向 Coding Agent 的轻量级项目认知接力框架，让项目认知持久化、可迁移，并与 Agent 解耦。

最棒的一点是：智能体之间的通信完全不需要依赖对话上下文。

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/2d9e7307-8cb5-4f12-b91d-ca0beef9d3fd" />


Agent Relay 是一个轻量级多 Agent 接力协作框架。Coding Agent 不需要共享对话上下文，只需要通过代码仓库接力可持久化的项目状态。Planner、Implementer 与 Reviewer 不依赖同一个聊天窗口保存上下文，而是把可复用的项目认知保存在仓库文件中；可选的标准库 Python 辅助脚本为状态写入增加短时文件锁、revision 校验和原子替换。

它提供 Codex 与 Cursor 专用入口，并正式支持 DeepSeek Harness 和 OpenCode 复用统一入口。Claude Code、WorkBuddy、ZCode、Trae 或其他工具也可以通过项目级薄入口读取同一份协议。角色不绑定特定工具。

## 解决什么问题

不同 Agent 的对话上下文通常不共享。本模板把仓库变成持久协作面：

```text
需求 → 计划 → 实施 → 审查 → 返修 → 验证
       docs/agent/tasks/<TASK-ID>/
```

固定交付物保存结论，追加式 `progress/` 保存每阶段动作与证据。下一个角色先读取项目总览、紧凑的 `knowledge-index.md`、任务状态和上一角色交付物，再开始工作。因此 Agent、对话、电脑或模型发生切换后，项目长期积累的有效认知仍可恢复。

## 三个角色

| 角色 | 负责 | 不负责 |
|---|---|---|
| Planner | 需求、边界、计划、决策、验收标准 | 修改产品代码 |
| Implementer | 代码、测试、实施证据、返修 | 关闭审查问题 |
| Reviewer | 独立审查、验证、完成决策 | 直接修复产品代码 |

<img width="1672" height="941" alt="b6983acc7f20aa6e7e05b30de4db7f88" src="https://github.com/user-attachments/assets/868c75bd-016f-4ed0-812b-20d53c51bd5e" />


## 快速开始

1. 将 `shared/.agents/skills/agent-relay/` 安装为当前工具的个人 Skill。
2. 打开新仓库，输入以下任一命令：

   ```text
   $agent-relay 初始化当前仓库
   $agent-relay initialize this repository
   ```
<img width="814" height="628" alt="9a3c8948164a8b340d70ad3fc11335e4" src="https://github.com/user-attachments/assets/86761441-3621-49b5-aabb-ba9c50e9ca38" />

3. 先选择中文或 English，再为三个角色指定工具。
4. 让 Planner 创建第一个任务。
5. 每次交接时打开下一个角色的工具，只说“继续”或 `continue`。
<img width="840" height="362" alt="2c7493b4c6a7366e669c5f0bcb1274c5" src="https://github.com/user-attachments/assets/148b6c2c-5b17-4d09-b746-be12990c0e61" />

所选语言会约束后续面向用户的交流和新增任务文档正文；文件名、YAML 键、ID 与状态枚举保持稳定。

内置工具选项为 Codex、Cursor、Claude Code、WorkBuddy、ZCode、Trae、DeepSeek Harness、OpenCode 和其他。DeepSeek Harness 与 OpenCode 共用根 `AGENTS.md` 和 `.agents/skills/agent-relay/`；初始化器不创建重复的 `.dsh` 或 `.opencode` Skill 目录。

Implementer 修改产品代码前必须询问是否使用子代理，并把明确选择写入任务状态；未选择时不得开始代码实施。

## 更换 Agent

旧 Agent 或新 Agent 都可以发起：

```text
$agent-relay 更换 Agent
$agent-relay 替换 Agent
$agent-relay replace agent
$agent-relay switch agent
```

每次选择 Planner、Implementer 或 Reviewer，以及“仅当前任务”“仅未来任务”或“两者”。角色不变，只更换同角色 participant；A → B → A 可反复切换并保留每次管理记录。运行中的 writer 不会因为超时自动被抢占，旧会话停止和残留锁释放都需要明确授权。更换完成后，在新 Agent 中另行说“继续”。

## 仓库结构

```text
shared/                         协议、任务模板和核心 Skill 的唯一事实源
  .agents/skills/agent-relay/
  docs/agent/
codex/                          Codex 入口与可复用提示词
cursor/                         Cursor 规则与命令
distribution/                   发布包安装说明
```

## 安装方式

完整的中文命令、角色接力和异常恢复用法见：[Agent Relay 使用手册](docs/AGENT_RELAY_USAGE.md)；也可查看 [English guide](docs/AGENT_RELAY_USAGE.en-US.md)。

新仓库优先使用 Skill 内置初始化器。它只复制缺失文件，并保留已有项目指令和运行状态。

手工安装请阅读 [distribution/INSTALL.md](distribution/INSTALL.md)。自动初始化会刻意排除 `TASK-EXAMPLE-001`；手工复制完整源码时可以保留示例，但它只能用于说明，不能成为活动任务。

从 v1.4 迁移已有安装时，请阅读 [v1.5 迁移说明](docs/migration-v1.5.md)，其中包含未提交工作状态的明确交接包流程。

ZIP 安装包和 SHA-256 校验文件通过 GitHub Release 发布，不提交到源码仓库。

## 边界

- 这是 Relay 协议，不是调度器、权限系统、自动唤醒机制、Git 替代品或分布式锁；它不会自动同步机器或 worktree。
- 辅助锁只保护同一 checkout 中的协调状态，不锁产品代码、不跨机器，也不自动合并、发布或部署。
- 默认只允许同一工作目录中的一个活动任务和一个写入会话串行推进。
- 不同 worktree 或机器需要显式同步 Git 状态并核对版本。
- `DONE` 只表示任务验收完成，不授权合并、部署、发布、删除、回滚或接管。
- 宿主禁止写入 `.agents/` 时，工作流降级为已加载的全局 Skill 加 `docs/agent/protocol.md`。

## 验证与贡献

贡献前运行与 CI 等价的校验：

```bash
bash .github/scripts/validate-release.sh
```

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)、[SECURITY.md](SECURITY.md) 和 [CHANGELOG.md](CHANGELOG.md)。项目使用 [Apache-2.0](LICENSE) 许可证。
