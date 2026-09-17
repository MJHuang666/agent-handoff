# 多 Agent 项目状态共享模板 Implementation Plan

> Historical note: `project-role-workflow` is the pre-v1.5 name of Agent Relay. This plan is preserved as an implementation record.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成一套可复制到任意代码仓库的纯 Markdown 多 Agent 状态共享模板、Codex/Cursor 入口和可自动发现的共享 Skill。

**Architecture:** `shared/` 是跨工具唯一事实源，包含状态协议、角色规则、任务模板、示例和 `.agents/skills/project-role-workflow`。`codex/` 与 `cursor/` 只提供各自可发现的薄入口，所有入口引用同一协议，避免规则分叉。

**Tech Stack:** Markdown、MDC、YAML frontmatter、Git 文本差异。

**Spec:** `docs/superpowers/specs/2026-09-16-multi-agent-project-state-sharing-design.md`

## Global Constraints

- 核心协作协议只包含 Markdown 或 Markdown 衍生格式 `.mdc`，不引入运行时程序脚本；发布前可使用独立 CI 校验源码与安装包。
- 只定义 Planner、Implementer、Reviewer 三个角色，角色不绑定固定工具。
- `PROJECT_STATUS.md` 决定活动任务；任务 `STATE.md` 决定任务内部阶段与当前参与者。
- 第一版默认同一工作目录、一个活动任务、一个写入会话串行接力。
- Codex 和 Cursor 使用同一 `.agents/skills/project-role-workflow/SKILL.md` 与共享协议。
- 模板不得宣称 Markdown owner、revision、writer_session 或 Skill 具备真正的锁和权限隔离能力。
- 当前目录不是 Git 仓库，因此本计划不执行提交；交付时明确说明这一限制。

---

### Task 1: 建立共享协议和空白模板

**Files:**
- Create: `shared/docs/agent/README.md`
- Create: `shared/docs/agent/PROJECT_STATUS.md`
- Create: `shared/docs/agent/role-bindings.md`
- Create: `shared/docs/agent/workflow.md`
- Create: `shared/docs/agent/conventions.md`
- Create: `shared/docs/agent/integrations.md`
- Create: `shared/docs/agent/roles/*.md`
- Create: `shared/docs/agent/profiles/README.md`
- Create: `shared/docs/agent/profiles/_templates/participant.md`
- Create: `shared/docs/agent/architecture/*.md`
- Create: `shared/docs/agent/tasks/README.md`
- Create: `shared/docs/agent/tasks/_template/*.md`
- Create: `shared/docs/agent/tasks/_template/progress/README.md`

**Interfaces:**
- Consumes: v0.3 设计规格中的身份、状态、权限、交接与证据约定。
- Produces: 共享 Skill、平台入口和示例任务引用的规范文件与模板字段。

- [x] 创建目录骨架和每个文件的唯一职责内容。
- [x] 确认模板字段覆盖 active_task、assignments、participant_id、writer_session、stage_round、版本证据和异常状态。
- [x] 搜索共享文件中的冲突术语，确保不再使用 `current_agent` 作为执行者身份。

### Task 2: 创建并验证共享 Skill

**Files:**
- Create: `shared/.agents/skills/project-role-workflow/SKILL.md`
- Create: `shared/.agents/skills/project-role-workflow/references/protocol.md`

**Interfaces:**
- Consumes: Task 1 的共享协议与模板路径。
- Produces: Codex、Cursor 可发现的项目工作流 Skill；入口描述只负责触发，详细流程按需读取 reference。

- [x] 在无 Skill 情况下运行等待、身份歧义、旧会话占用三个压力场景并记录基线行为。
- [x] 写最小 SKILL.md：描述只包含触发条件，正文提供五步入口和 reference 路由。
- [x] 将状态机、权限、恢复、交接和管理操作细节放入 `references/protocol.md`，不复制多份事实源。
- [x] 使用 skill-creator 的 `quick_validate.py` 验证 frontmatter、目录名和残留占位符。
- [x] 用相同压力场景加载 Skill 重新验证，修复观察到的歧义。

### Task 3: 创建 Codex、Cursor 入口和完整示例

**Files:**
- Create: `codex/AGENTS.md`
- Create: `codex/prompts/*.md`
- Create: `cursor/.cursor/rules/agent-collaboration.mdc`
- Create: `cursor/.cursor/commands/*.md`
- Create: `shared/docs/agent/tasks/TASK-EXAMPLE-001/**`

**Interfaces:**
- Consumes: Task 1 的路径和 Task 2 的 Skill 名称。
- Produces: 平台自动加载入口、手动快捷入口和可核对的完整生命周期示例。

- [x] 编写薄入口，要求读取共享状态和 Skill，不复制完整协议。
- [x] 示例覆盖规划、实施、审查、返修、验证、终态收尾，并明确所有测试数据为演示。
- [x] 示例引用有效文件、revision、stage_round、participant_id 和 delivery_id。
- [x] 核对 Cursor MDC frontmatter 与 Markdown 命令格式，Codex AGENTS 保持跨工具无冲突。

### Task 4: 完成安装说明和交付验证

**Files:**
- Create: `README.md`
- Modify: `shared/docs/agent/README.md`
- Modify: `shared/docs/agent/integrations.md`

**Interfaces:**
- Consumes: 全部生成文件。
- Produces: 可由新用户完成安装、首次注册、首个任务、接力、故障恢复和归档的说明书。

- [x] 写明从 `shared/`、`codex/`、`cursor/` 到目标仓库的合并安装步骤。
- [x] 提供一页日常操作、首次身份注册、任务切换、接管和异常恢复说明。
- [x] 验证完整文件清单、内部相对链接、Markdown/MDC 格式和术语一致性。
- [x] 在临时目录模拟安装，检查目标路径是 `AGENTS.md`、`.agents/skills/...`、`.cursor/...`、`docs/agent/...`。
- [x] 对未通过真实工具新会话验证的入口标注“待验证”，不把文件存在表述为加载成功。
