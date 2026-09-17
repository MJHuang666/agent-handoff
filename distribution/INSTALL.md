# Project Role Workflow Skill Pack

版本：1.4.0

这个安装包把多智能体协作所需的 Skill、共享状态模板、状态安全脚本和工具入口放在一起。安装后，Planner、Implementer、Reviewer 通过目标仓库中的 `docs/agent/` 交接；对话框只负责触发命令，不再承担唯一上下文。正式 ZIP 与 SHA-256 校验文件应作为 GitHub Release 附件发布，而不是提交到源码仓库。

安装全局 Skill 后，可以在空白仓库中说 `$project-role-workflow 初始化当前仓库` 或 `$project-role-workflow initialize this repository`。Skill 会先询问中文/英文，再从内置 `assets/project-template/` 安装对应语言模板，最后询问三个角色的工具分配。

初始化后，`继续` 和 `continue` 等价。项目语言会约束后续选项、对话、需求、计划、执行记录、审查与验收报告。Implementer 在修改产品代码前还会要求用户明确选择本次任务是否使用子代理。

`更换 Agent`、`替换 Agent`、`replace agent` 和 `switch agent` 等价。它们允许旧 Agent 或新 Agent 在明确授权下更换某个角色的当前任务绑定、未来默认绑定或两者，并通过 Python 3 标准库脚本保护状态 revision。没有 Python 3 时工作流仍可手工串行使用，但会报告缺少锁、CAS 和原子写入保护。

## 包内内容

| 路径 | 用途 | 是否必装 |
|---|---|---:|
| `shared/.agents/skills/project-role-workflow/` | 核心 Skill 和协议 | 是 |
| `shared/docs/agent/` | 项目状态、角色、参与者、任务模板和示例 | 是 |
| `codex/AGENTS.md` | Codex 项目入口 | 使用 Codex 时 |
| `codex/prompts/` | Codex 可复用提示词 | 可选 |
| `cursor/.cursor/rules/` | Cursor 自动规则 | 使用 Cursor 时 |
| `cursor/.cursor/commands/` | Cursor 命令模板 | 可选 |

## 交给智能体安装

把整个压缩包交给目标智能体，并附上 `INSTALL_PROMPT.md` 的内容。安装智能体必须先检查目标仓库中的同名文件；存在时合并，不允许整目录覆盖。

## 安装为个人 Skill

要让 Skill 可以在空白仓库中自举，先把包内 `shared/.agents/skills/project-role-workflow/` 安装到当前工具的个人 Skill 目录：

| Tool | Personal Skill destination |
|---|---|
| Codex | `~/.codex/skills/project-role-workflow/` |
| Claude Code | `~/.claude/skills/project-role-workflow/` |
| DeepSeek Harness | 个人 Skill 目录，或直接使用项目 `.agents/skills/project-role-workflow/` |
| OpenCode | 个人 Skill 目录，或直接使用项目 `.agents/skills/project-role-workflow/` |
| 支持 Agent Skills 的其他工具 | 该工具声明的个人 Skills 目录 |

完成后进入新仓库调用：

```text
$project-role-workflow 初始化当前仓库
# or
$project-role-workflow initialize this repository
```

Skill 会从自身 `assets/project-template/` 安装缺失文件。已有文件仍按保留与合并规则处理。自动初始化不会复制 `TASK-EXAMPLE-001`，避免示例任务被误认为真实项目状态。

## 手工安装映射

在目标仓库根目录执行文件合并：

| 安装包来源 | 目标仓库位置 |
|---|---|
| `shared/docs/agent/` | `docs/agent/` |
| `shared/.agents/skills/project-role-workflow/` | `.agents/skills/project-role-workflow/` |
| `codex/AGENTS.md` | `AGENTS.md`，与已有规则合并 |
| `codex/prompts/` | 可放入团队约定的 Codex 提示词目录 |
| `cursor/.cursor/rules/` | `.cursor/rules/` |
| `cursor/.cursor/commands/` | `.cursor/commands/` |

### Claude Code

初始化完成的项目会保留通用副本 `.agents/skills/project-role-workflow/`。如果当前 Claude Code 版本不能发现它，再把项目级核心 Skill 复制到：

```text
.claude/skills/project-role-workflow/
```

两处并存时，以 `.agents/skills/project-role-workflow/` 为唯一维护源；Claude 副本只作为兼容入口。更新后必须重新同步并验证。

### ZCode

可用 ZCode 的 Skill Import 导入 `shared/.agents/skills/project-role-workflow/`，范围选择 Current Project。若支持 Copy/Symlink，优先 Symlink 以避免双份内容漂移；不支持时选择 Copy，并记录同步责任。项目根 `AGENTS.md` 可使用 Codex 入口的内容，但必须与已有规则合并。

### DeepSeek Harness

目标项目保留根 `AGENTS.md` 和 `.agents/skills/project-role-workflow/`。DeepSeek Harness 需启用 `dsh-agent-instructions`，并启用能扫描项目 `.agents/skills/` 的文件系统 Skill 加载器。不要创建 `.dsh/skills` 副本；未用真实新会话验证前，集成状态保持“待验证”。

### OpenCode

OpenCode 可直接读取根 `AGENTS.md` 和项目 `.agents/skills/`。如果 `project-role-workflow` 没有出现，检查 Skill 权限，并检查 `.opencode/skills/` 是否存在同名高优先级副本。不要创建 `.opencode/skills` 副本，以 `.agents/skills/project-role-workflow/` 为唯一事实源。

### WorkBuddy、Trae 和其他智能体

如果工具支持项目 Skill，导入 `shared/.agents/skills/project-role-workflow/`。如果只支持 Rules/Instructions，就创建一个很短的项目入口，要求在涉及任务规划、实施、审查、恢复或状态变更时，读取：

```text
.agents/skills/project-role-workflow/SKILL.md
.agents/skills/project-role-workflow/references/protocol.md
docs/agent/PROJECT_STATUS.md
```

不要把整份协议复制进多个规则文件；核心协议应只有一个维护源。

## 安装后的首次配置

1. 若采用手工完整复制，保留 `docs/agent/tasks/TASK-EXAMPLE-001/` 作为示例，但绝不把它设为活动任务；使用自动初始化时该示例不会被复制。
2. 在 `docs/agent/PROJECT_STATUS.md` 填写项目名称和目标。
3. 为 Planner、Implementer、Reviewer 分配工具和唯一 `participant_id`。
4. 从 `docs/agent/profiles/_templates/participant.md` 创建参与者 Profile，并登记到 `role-bindings.md`。
5. 打开全新会话，只输入“继续”。智能体应主动报告活动任务、身份、角色以及当前是否轮到自己。
6. 把真实验证结果记录到 `docs/agent/integrations.md`。没有经过新会话验证的入口继续标记为“待验证”。

## 更新已有安装

- 先比较目标仓库的本地修改和安装包版本。
- 合并 Skill 与协议，不覆盖目标项目自己的角色绑定、任务记录、架构约束和项目状态。
- `docs/agent/tasks/`、`profiles/`、`role-bindings.md`、`PROJECT_STATUS.md` 属于目标项目运行数据，升级时不得用空模板覆盖。
- 更新完成后重新执行“只说继续”的新会话验证。

## 边界

- 安装只建立文件协作协议，不会自动唤醒下一个智能体。
- 辅助脚本的短时锁只保护同一 checkout 的协调状态事务；产品代码、不同 worktree 和不同机器仍依赖单写入约定与显式同步。
- `DONE` 只代表任务验收完成，不自动授权合并、发布、部署、删除或回滚。
