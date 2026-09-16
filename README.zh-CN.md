# 多 Agent 项目状态共享框架

[English](README.md)


<img width="1672" height="941" alt="ba14332458141704b359c20a8d40f1a0" src="https://github.com/user-attachments/assets/e07e4a0d-58a7-4622-915b-943da26f310a" />

Project Role Workflow 是一套纯 Markdown 的多智能体协作协议。Planner、Implementer 与 Reviewer 不依赖同一个聊天窗口保存上下文，而是通过仓库中的文件交接项目状态。

它目前提供 Codex 与 Cursor 的入口文件；Claude Code、WorkBuddy、ZCode、Trae 或其他工具也可以通过项目级薄入口读取同一份协议。角色不绑定特定工具。

## 解决什么问题

不同 Agent 的对话上下文通常不共享。本模板把仓库变成持久协作面：

如果你订阅了 20 美元的 ChatGPT Plus 服务，就可以把规划、设计和审核工作交由 GPT-6 或 GPT-5.6 处理，同时将繁重的落地实现工作交给 Cursor 5.6 或 DeepSeek 或者其他。

最棒的一点是：智能体之间的通信完全不需要依赖对话上下文。
```text
需求 → 计划 → 实施 → 审查 → 返修 → 验证
       docs/agent/tasks/<TASK-ID>/
```

固定交付物保存结论，追加式 `progress/` 保存每阶段动作与证据。下一个角色先读取项目总览、任务状态和上一角色交付物，再开始工作。

## 三个角色

| 角色 | 负责 | 不负责 |
|---|---|---|
| Planner | 需求、边界、计划、决策、验收标准 | 修改产品代码 |
| Implementer | 代码、测试、实施证据、返修 | 关闭审查问题 |
| Reviewer | 独立审查、验证、完成决策 | 直接修复产品代码 |

<img width="1672" height="941" alt="b6983acc7f20aa6e7e05b30de4db7f88" src="https://github.com/user-attachments/assets/868c75bd-016f-4ed0-812b-20d53c51bd5e" />


## 快速开始

1. 将 `shared/.agents/skills/project-role-workflow/` 安装为当前工具的个人 Skill。
2. 打开新仓库，输入以下任一命令：

   ```text
   $project-role-workflow 初始化当前仓库
   $project-role-workflow initialize this repository
   ```
<img width="814" height="628" alt="9a3c8948164a8b340d70ad3fc11335e4" src="https://github.com/user-attachments/assets/86761441-3621-49b5-aabb-ba9c50e9ca38" />

3. 先选择中文或 English，再为三个角色指定工具。
4. 让 Planner 创建第一个任务。
5. 每次交接时打开下一个角色的工具，只说“继续”或 `continue`。
<img width="840" height="362" alt="2c7493b4c6a7366e669c5f0bcb1274c5" src="https://github.com/user-attachments/assets/148b6c2c-5b17-4d09-b746-be12990c0e61" />

所选语言会约束后续面向用户的交流和新增任务文档正文；文件名、YAML 键、ID 与状态枚举保持稳定。

Implementer 修改产品代码前必须询问是否使用子代理，并把明确选择写入任务状态；未选择时不得开始代码实施。

## 仓库结构

```text
shared/                         协议、任务模板和核心 Skill 的唯一事实源
  .agents/skills/project-role-workflow/
  docs/agent/
codex/                          Codex 入口与可复用提示词
cursor/                         Cursor 规则与命令
distribution/                   发布包安装说明
```

## 安装方式

新仓库优先使用 Skill 内置初始化器。它只复制缺失文件，并保留已有项目指令和运行状态。

手工安装请阅读 [distribution/INSTALL.md](distribution/INSTALL.md)。自动初始化会刻意排除 `TASK-EXAMPLE-001`；手工复制完整源码时可以保留示例，但它只能用于说明，不能成为活动任务。

ZIP 安装包和 SHA-256 校验文件通过 GitHub Release 发布，不提交到源码仓库。

## 边界

- 这是文件协议，不是调度器、文件锁、权限系统或自动唤醒机制。
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
