# 多 Agent 项目状态共享模板设计规格

版本：1.3.0，2026-09-17。本文记录已实现的设计基线：身份、活动任务、交接、检查点、恢复、语言选择、子代理门禁及 Agent 动态更换均已落入模板。结构、初始化和关键行为已做本地验证；没有经过全新工具会话验证的第三方适配仍必须标为未验证。

## 1. 目标

构建一个可复制到任意软件仓库的纯 Markdown 模板，使 Codex、Cursor、Claude Code、WorkBuddy、Zcode、Trae 及其他编码 Agent 能够围绕同一项目按角色接力工作。

系统不依赖某个聊天窗口保存上下文。项目事实、角色分工、任务状态、阶段动作、结论、验证证据和下一步交接全部写入仓库文件，由 Git 作为共享总线。

## 2. 设计原则

1. 角色与 Agent 解耦。Planner、Implementer、Reviewer 可以绑定到任意受支持的 Agent。
2. 首次注册后复用。绑定唯一且无占用冲突时，后续会话直接继承；身份有歧义时只确认身份，不重复询问项目背景。
3. 单一实时状态源。只有当前任务的 `STATE.md` 决定现在轮到哪个角色和哪个 Agent。
4. 总览与明细分离。`PROJECT_STATUS.md` 只做项目级索引；任务事实保存在任务目录。
5. 正式交付物与过程历史分离。角色交付物保存在固定文件中，阶段动作和结论保存在追加式 `progress/` 记录中。
6. 非当前执行者只读。如果任务没有轮到当前角色或 Agent，不得修改代码、状态或任务文档。
7. 验证证据优先。没有与验收条件相匹配的证据，Reviewer 不得将任务标记为 `DONE`。
8. Markdown-first。所有事实保持人类可读；可选的 Python 3 标准库脚本仅为协调状态提供短时本地锁、revision CAS 和原子写入，Python 不可用时降级为人工单写入协议。
9. 第一版默认同一个工作目录、一个活动任务、一个写入会话串行接力。可以登记多个待办任务，但不同时推进。
10. 文件记录不会自动唤醒另一个工具。用户在接棒窗口输入“继续”；角色尚未轮到时报告等待并结束本轮，不后台轮询。

## 3. 核心角色

系统只定义三个角色：

### 3.1 Planner

负责理解需求、识别范围和非目标、记录约束与决策、设计实现方案、列出风险，并定义可执行的验收和验证要求。

Planner 的正式交付物是 `plan.md`，必要时向 `decisions.md` 添加决策。Planner 不修改产品代码，不代替 Implementer 写执行结论，也不代替 Reviewer 给出审查结果。

### 3.2 Implementer

负责按已批准的计划修改代码、补充测试、执行计划要求的验证，并记录实际变更、计划偏差、测试结果、已知问题和审查重点。

Implementer 的正式交付物是 `execution.md`。当 Reviewer 请求修改时，同一个角色负责返修并更新执行记录。Implementer 不自行批准任务，也不改写 Reviewer 的结论。

### 3.3 Reviewer

负责独立读取需求、计划、执行记录、阶段历史和真实代码差异，检查正确性、回归风险、兼容性、测试覆盖及验收证据。

Reviewer 的正式交付物是 `review.md`。Reviewer 可以请求修改，也负责最终验证并决定任务能否进入 `DONE`。Reviewer 默认不直接修复自己发现的问题，以保持审查独立性。

## 4. 支持的 Agent

首次注册提供以下选项：

1. Codex
2. Cursor
3. Claude Code
4. WorkBuddy
5. Zcode
6. Trae
7. 其他

文件路径使用规范化的小写标识：`codex`、`cursor`、`claude-code`、`workbuddy`、`zcode`、`trae`。选择“其他”时，由用户提供显示名称，系统将其转换成稳定的文件夹标识；不得覆盖已有 Agent 目录。

同一个 Agent 可以在不同任务中承担不同角色，也可以拥有多个角色 Profile。项目默认绑定保存在 `role-bindings.md`，单个任务可以在 `STATE.md` 中覆盖默认绑定。

身份分为三层：`tool` 是工具类型，如 `codex`；`role` 是职责，如 `planner`；`participant_id` 是持久参与者标识，如 `planner-main`。工具类型不能唯一标识执行者。不同 Codex 窗口可以选择不同参与者，但不得同时以同一个参与者写入。

`role-bindings.md` 登记 participant_id、tool、role 和 Profile 路径。任务 STATE 的 `assignments` 保存本任务三个角色的参与者绑定快照；修改项目默认绑定不会自动改变活动任务。更换任务参与者须由用户明确指定，确认原写入会话已停止，并记录接管原因。

participant_id 在项目内唯一，其 tool、role 创建后不可变，也不得删除后复用为另一身份。更换工具或角色须创建新的 participant_id，再显式更新任务 assignments 和当前执行者（如涉及）。旧身份保留供历史引用，可标为停用。Profile 的普通项目偏好可以授权修订，但不能通过修订改变身份字段；注册表与 Profile 的身份字段不一致时停止执行并报告。

身份状态为 active、standby、retired。更换 Agent 可以创建或复用同角色身份，允许 A → B → A 多次切换；standby 重新被选中时恢复 active，retired 需要明确重新启用授权。当前任务、未来默认或两者的影响范围每次由用户选择。当前责任参与者变化时增加 stage_round；非当前角色绑定变化只增加 revision。每次更换写入独立 MANAGEMENT 记录，并由标准库辅助脚本在同一 checkout 内执行短时锁、expected revision 校验和原子文件替换。

## 5. 模板仓库结构

本仓库作为分发源，不直接假设自己就是目标软件项目：

```text
多agent项目状态共享/
├── README.md
├── shared/
│   ├── .agents/
│   │   └── skills/
│   │       └── project-role-workflow/
│   │           └── SKILL.md
│   └── docs/
│       └── agent/
│           ├── README.md
│           ├── PROJECT_STATUS.md
│           ├── role-bindings.md
│           ├── workflow.md
│           ├── conventions.md
│           ├── integrations.md
│           ├── roles/
│           │   ├── planner.md
│           │   ├── implementer.md
│           │   └── reviewer.md
│           ├── architecture/
│           │   ├── overview.md
│           │   └── constraints.md
│           ├── profiles/
│           │   ├── README.md
│           │   ├── _templates/
│           │   │   └── participant.md
│           │   ├── codex/
│           │   ├── cursor/
│           │   ├── claude-code/
│           │   ├── workbuddy/
│           │   ├── zcode/
│           │   ├── trae/
│           │   └── other/
│           └── tasks/
│               ├── README.md
│               ├── _template/
│               │   ├── STATE.md
│               │   ├── requirement.md
│               │   ├── plan.md
│               │   ├── execution.md
│               │   ├── review.md
│               │   ├── decisions.md
│               │   └── progress/
│               │       └── README.md
│               └── TASK-EXAMPLE-001/
│                   └── 一套填写完整的示例
├── codex/
│   ├── AGENTS.md
│   └── prompts/
│       ├── plan-task.md
│       ├── implement-task.md
│       ├── review-task.md
│       ├── fix-review.md
│       ├── verify-task.md
│       └── resume-task.md
└── cursor/
    └── .cursor/
        ├── rules/
        │   └── agent-collaboration.mdc
        └── commands/
            ├── plan-task.md
            ├── implement-task.md
            ├── review-task.md
            ├── fix-review.md
            ├── verify-task.md
            └── resume-task.md
```

虽然源码分为 `codex/` 和 `cursor/`，两端都依赖 `shared/` 中的同一套状态协议和 Skill。平台入口不得复制出两套不同版本的工作流规则。

通用职责只在 `roles/<role>.md` 维护。Profile 使用 `profiles/<tool>/<participant_id>.md`，只保存身份、通用角色文件引用和项目差异，不复制完整职责。例如 `profiles/codex/planner-main.md`、`profiles/codex/reviewer-main.md`。未使用的工具目录不必预建。

## 6. 安装到目标项目

复制关系固定如下：

| 模板仓库来源 | 目标项目位置 | 用途 |
|---|---|---|
| `shared/docs/agent/` | `docs/agent/` | 项目状态、角色、任务和历史 |
| `shared/.agents/` | `.agents/` | 两端共用的项目级 Skill |
| `codex/AGENTS.md` | `AGENTS.md` | Codex 自动读取的项目规则 |
| `cursor/.cursor/` | `.cursor/` | Cursor 自动规则和快捷命令 |

目标项目原有 `AGENTS.md`、`.agents/`、`.cursor/` 或 `docs/agent/` 时，说明书要求逐项合并，不允许整目录覆盖。

`codex/AGENTS.md` 中只写平台无冲突的项目协作规则，因为部分其他工具也可能读取根目录 `AGENTS.md`。Cursor 专属行为放在 `.cursor/rules/agent-collaboration.mdc`。

### 6.1 工具适配范围

`integrations.md` 区分协议可读与入口自动加载。第一版提供 Codex、Cursor 的入口模板；安装后必须从新会话检查能否读到项目总览、Skill 和角色规则，检查通过后才能标为“已验证”。Claude Code、WorkBuddy、Zcode、Trae 和其他工具可以阅读相同协议，但其自动入口初始标为“待配置、未验证”。按对应工具支持的项目指令方式配置并走查后，再记录入口路径、工具版本和验证日期。创建 Profile 不等于已配置自动加载。

### 6.2 工作目录和 Git 交接

默认所有参与者打开同一个目标项目工作目录。开始前核对真实仓库、分支、HEAD 和脏文件，保护与任务无关的修改。代码交接记录仓库标识、工作目录、分支、基线提交及交付版本。

已提交变更使用完整提交 ID 标识代码版本；未提交变更须明确标记，并列出修改、暂存、未跟踪文件及可核对的差异快照或内容摘要。审查基线到交付版本必须覆盖本任务全部代码修改。测试证据记录命令、结果、时间、环境和对应代码版本；代码变化后重新评估受影响的审查和测试，不能沿用旧版通过结论。

此处“内容摘要”指明确算法的文件内容指纹（例如 SHA-256），不是自然语言概述。未提交交付物使用唯一 delivery_id，记录基线、文件路径、增删类型及内容指纹，或保存包含未跟踪文件内容的完整差异快照。二进制文件以内容指纹核对；已删除文件明确记录删除。可将清单或差异写入 Markdown 证据文件，无须引入脚本。审查和验证引用同一 delivery_id，并核对现场内容。

交付版本区分产品变更与协作记录。仅修改进度、身份登记、交接状态等协作文档，不自动使产品测试失效；产品代码、测试、依赖、构建配置、运行环境或行为规范变化时，须重新评估受影响的审查和验证。需求或计划的验收语义变化时，即使代码未变，也要重新核对验收覆盖。交付清单应明确分类及排除理由，不能将影响产品行为的文件归为协作记录来绕过验证。

不同 worktree 或机器不会自动共享未提交的文档或代码。如确需换目录，先停止原写入会话，通过用户授权的 Git 操作或明确的交接包同步代码和任务文档，再核对两端内容后接棒。协议本身不授权自动提交、合并或覆盖工作区。无 Git 的项目使用文件清单和差异快照，并注明缺少提交基线。

## 7. 永久规则与共享 Skill

### 7.1 永久规则

Codex 通过根目录 `AGENTS.md` 自动获得最小、稳定、始终有效的约束。Cursor 通过 `alwaysApply: true` 的 `.cursor/rules/agent-collaboration.mdc` 获得同类约束。

永久规则至少要求：

- 每次开始或恢复工作时读取 `docs/agent/PROJECT_STATUS.md`。
- 找到当前任务后读取任务的 `STATE.md`。
- 确认任务 ID 等于 PROJECT_STATUS 的 active_task；直接指定其他任务不构成切换授权。
- 读取当前 Agent 对应的角色 Profile。
- 工作前确认 `current_role`、`current_participant`、登记的 tool 和本会话身份是否一致，并确认没有其他写入会话。
- 不匹配时保持只读，并在对话中说明正在等待的角色和 Agent。
- 匹配时读取上一个阶段记录和本角色需要的正式交付物。
- 阶段结束时按第 14 节顺序更新交付物、历史、任务状态和总览。
- 不得用聊天总结代替项目文件。

### 7.2 共享 Skill

`.agents/skills/project-role-workflow/SKILL.md` 承载完整操作流程。它同时供支持 Agent Skills 标准的 Codex 和 Cursor 使用，并为其他 Agent 提供可直接阅读的协议。

Skill 应在以下意图下触发：创建任务、规划任务、实施计划、继续当前任务、处理审查意见、审查变更、最终验证和关闭任务。

永久规则要求这些场景必须遵循 Skill，因此流程不依赖模型偶然判断是否调用。快捷 Prompt 或命令只是方便入口，不是唯一入口。

以上是模型应遵守的行为约定，不是权限隔离或进程锁；安装验证需检查模型实际加载了哪些文件。

### 7.3 一页日常操作入口

Skill 首屏和项目使用说明提供同一份简短操作路径，详细异常规则按需引用：

1. 确认本会话身份：读取登记及 Profile，唯一匹配时恢复，有歧义时只选择身份。
2. 检查是否轮到自己：核对 active_task、阶段、参与者、会话占用和阻塞条件；不满足则只读并报告。
3. 读取输入：需求、通用角色规则、上一阶段交付物、本轮检查点及代码版本。
4. 执行：登记写入会话，在本角色权限和任务范围内工作；遇到暂停或异常走对应恢复规则。
5. 留证据并交接：完成交付物、追加历史、更新 STATE、刷新总览，给出下一步提示。

快捷入口引用共享规则，不复制另一套状态机。精简入口不能省略身份、活动任务和写权限检查。

## 8. 首次注册与 Profile 继承

Skill 第一次运行时执行以下判断：

1. 读取 `role-bindings.md`。
2. 优先采用用户明确指定的 participant_id 或本会话已经确认的身份；否则查找与已知工具匹配的参与者。
3. 只有唯一匹配且无占用冲突时才自动恢复。多个匹配时列出身份、角色和 Profile 路径，询问一次“继续哪个身份”。不得根据当前轮到的角色擅自认领身份。
4. 若不存在，先询问角色，再询问 Agent 类型。
5. 确定 participant_id，从 `profiles/_templates/participant.md` 创建 `profiles/<tool>/<participant_id>.md`，引用 `roles/<role>.md`。工具自报信息不明确时由用户确认。
6. 在用户要求的初始化或注册操作中串行登记；复用已有 Profile，已有绑定不因注册而被静默替换。

角色选择提示固定为：

```text
请选择你的角色：

1. Planner：规划需求、边界、风险和验收条件
2. Implementer：实施计划，并负责处理返修
3. Reviewer：独立审查、验证和决定是否通过
```

Agent 选择提示固定为：

```text
请选择当前 Agent：

1. Codex
2. Cursor
3. Claude Code
4. WorkBuddy
5. Zcode
6. Trae
7. 其他
```

已有 Profile 不得被初始化流程覆盖。用户授权调整时可以修订有效约束并留下变更记录，废弃条目标明已被替代，避免无限追加矛盾规则。角色注册属于明确请求的管理操作，不允许等待中的会话自行触发注册来抢占任务。

## 9. 项目级总进度

`docs/agent/PROJECT_STATUS.md` 是所有 Agent 每次都读的项目入口。它记录：

- 项目名称和目标；
- 当前活动任务；
- 全部任务的状态、当前角色、当前 Agent 和任务路径；
- 最近一次交接摘要；
- 已完成任务索引；
- 项目级阻塞项。

项目只保留一个 `active_task`。没有活动任务时，在用户要求新建任务后，由已选定的 Planner 创建任务文件并设为 DRAFT；第一个阶段的历史指针可以为空。切换任务由用户指定，并先确认原任务已交接、暂停或终止且没有写入会话。任务列表的状态列只是缓存，附 task revision，不作为授权依据；历史任务移到归档索引，保留稳定链接。

PROJECT_STATUS 对“哪个任务处于活动状态”具有权威性，任务 STATE 对“该任务的阶段及执行者”具有权威性。只有任务 ID 等于 active_task 才允许业务写入；非活动任务即使角色匹配也只能读取，先经用户授权完成切换才能推进。active_task 为空时不得自行从待办中挑选任务。初始化、任务切换和授权状态修复属于管理操作例外。

初始化允许 Planner 创建全部空白交付物模板，但不得填写其他角色的执行或审查结论。目录示例和已完成示例不自动成为活动任务。

该文件不复制任务的详细过程，不保存完整计划、审查问题或测试日志。所有明细都通过链接指向任务目录，避免总进度文件无限膨胀。

## 10. 任务级实时状态

每个任务的 `STATE.md` 是该任务唯一实时状态源。推荐使用可读的 YAML 代码块：

```yaml
task: TASK-20260916-001
status: REVIEWING
revision: 3
assignments:
  planner: planner-main
  implementer: implementer-main
  reviewer: reviewer-main
current_role: reviewer
current_participant: reviewer-main
writer_session: null
execution: idle
previous_role: implementer
previous_participant: implementer-main
previous_progress: progress/002-implementation-cursor.md
latest_checkpoint: null
stage_round: 3
plan_version: 1
approval_ref: plan.md#approval-v1
code_delivery_ref: execution.md#delivery-1
next_expected_output: review.md
updated_at: 2026-09-16T14:30:00+08:00
```

以上为字段示意，引用必须在实际任务中存在。`current_participant` 的角色必须与 current_role 及 assignments 一致。tool 从参与者注册表读取，避免重复存储冲突。终态的 current_role、current_participant 均为 null。

`execution` 为 idle、running 或 paused。开始写入前登记 writer_session（本次会话标识）并设 running；交接完成或主动暂停时释放 writer_session。新会话遇到 running 不得自行认领，即使 participant_id 相同，也要确认原会话停止后由用户授权接管。

会话标识优先使用工具可靠提供的会话 ID，并加 tool 前缀；无法取得时，在首次登记时生成项目内未使用的 `participant_id-时间戳-短随机后缀`，记录在阶段历史中。本会话后续轮次复用同一标识。不能确认是原会话时按新会话处理，不能复制磁盘中的 writer_session 来冒充原写入者。会话标识用于追踪，不是认证凭据或锁。

`stage_round` 是阶段轮次，从 1 开始；阶段发生变化或授权更换责任参与者时递增，包括返修后再次进入同名阶段。同阶段检查点、暂停及恢复只增加 revision，不增加 stage_round。检查点必须匹配 task、stage_round、current_role、current_participant 才能用于恢复。

| 状态组合 | 字段约束 |
|---|---|
| 普通非终态，execution=idle | current_role 和 current_participant 有效，writer_session=null，等待当前参与者开始 |
| 普通非终态，execution=running | 有效当前参与者，writer_session 非空，且任务是 active_task |
| 普通非终态，execution=paused | 保留当前角色及参与者，writer_session=null；有检查点或暂停原因 |
| BLOCKED | execution=paused，writer_session=null；保留责任人，必须有 blocked_reason、unblock_condition、resume_status |
| DONE 或 CANCELLED | execution=idle；current_role、current_participant、writer_session、next_expected_output、latest_checkpoint 均为 null |

解除 BLOCKED 时清除活动阻塞字段，原因保留在历史中；恢复阶段设 idle，再由责任会话登记 running。进入终态时清除活动阻塞字段，保留 assignments、交付版本和历史指针供追溯。矛盾字段组合必须报告并修复，不能猜测其中哪一项有效。

`revision` 每次修改 STATE 都递增；写入前重新核对。它只能发现部分过期读取：两个会话可能同时检查通过，因此它和 writer_session 都不是锁，也不能保证并发安全。第一版的前提是人为保持单写入会话；不通过超时或心跳缺失自动抢占。

## 11. 状态机与角色权限

允许的状态流转如下：

```text
DRAFT
  → PLANNING
  → READY
  → IMPLEMENTING
  → REVIEWING
      ├→ CHANGES_REQUESTED → IMPLEMENTING
      └→ VERIFYING → DONE
```

| 状态 | 当前角色 | 允许的主要动作 |
|---|---|---|
| `DRAFT` | Planner | 整理需求，补齐验收条件 |
| `PLANNING` | Planner | 编写计划和决策 |
| `READY` | Implementer | 接受已批准计划并开始实施 |
| `IMPLEMENTING` | Implementer | 修改代码、测试并记录执行结果 |
| `REVIEWING` | Reviewer | 独立审查代码和证据 |
| `CHANGES_REQUESTED` | Implementer | 只处理未解决的审查问题 |
| `VERIFYING` | Reviewer | 执行最终验收并核对真实结果 |
| `DONE` | 无 | 任务关闭，仅允许新增后续任务 |

补充状态和转移：

- PLANNING → READY：plan.md 记录计划版本及用户批准来源。可引用本次会话已有授权的日期、原意和范围，不为手续重复请求批准；没有授权则留在 PLANNING 并说明待确认内容。
- REVIEWING 或 VERIFYING → CHANGES_REQUESTED：问题和证据写入 review.md 后交给 Implementer。
- IMPLEMENTING、REVIEWING 或 VERIFYING → PLANNING：发现需要变更范围或设计时，记录原因并交给 Planner；新的计划版本必须确认仍处于已有授权范围，否则待用户批准。
- 任一非终态 → BLOCKED：保留责任参与者，记录 blocked_reason、unblock_condition、resume_status 和需要谁提供什么输入，释放写入会话。条件满足后由责任参与者按证据恢复原阶段；若涉及新范围先回 PLANNING。
- 用户取消时进入 CANCELLED，记录原因及代码留存情况，不自动回滚。DONE 与 CANCELLED 均无当前执行者。
- 终态收尾由完成该转换的会话将总览中仍指向本任务的 active_task 清空，并更新该任务行；不自动激活下一任务。若 active_task 已指向其他任务，不得覆盖它。
- 主动暂停保持原 status，execution 设 paused，记录检查点；恢复时核对身份和现场，再继续原阶段。

READY、REVIEWING 等阶段的接棒仅允许指向已经登记的参与者。缺少下一角色绑定时留在当前阶段并报告等待配置，不编造身份。

所有角色可读全部任务文件。写权限如下，除管理操作外都要求本会话是当前执行者：

| 文件或动作 | 写入者及条件 |
|---|---|
| 产品代码、任务测试 | Implementer，按批准范围；Reviewer 的验证不得混入产品修复 |
| requirement.md、decisions.md | Planner 在用户授权范围内维护，未批准建议明确标注 |
| plan.md | Planner；批准记录仅转录真实授权 |
| execution.md | Implementer，包括返修回应和交付版本 |
| review.md | Reviewer；问题关闭由 Reviewer 复核，Implementer 只在 execution.md 回应 |
| progress 新记录 | 当前执行者；历史记录不覆盖 |
| STATE.md、总览的当前任务行 | 当前执行者按合法流转更新，总览不得覆盖其他任务记录 |
| 参与者注册、接管、活动任务切换、状态修复 | 用户明确授权的管理操作，单会话执行并记录原因 |
| 永久规则、共享职责、项目级约束 | 用户授权修改 |

等待中的参与者不修复状态或总览，只报告。用户授权的修复不是业务接棒，不能顺带修改产品代码。Reviewer 的“独立”要求使用独立审查会话读取代码与证据，不要求换工具；实施会话不能未经角色交接自行改成 Reviewer 批准自己的实现。

## 12. 固定读取顺序

每次开始工作必须按以下顺序恢复上下文：

1. `docs/agent/PROJECT_STATUS.md`
2. 当前任务的 `STATE.md`
3. `docs/agent/workflow.md` 和 `conventions.md`
4. role-bindings.md、已确认参与者 Profile 及其引用的通用角色规则
5. 当前任务的 `requirement.md`
6. `STATE.md` 指向的上一个阶段进度文件和最新检查点（存在时）
7. 当前角色需要的正式交付物
8. 与当前任务相关的架构说明、决策和实际 Git diff

如果身份与 current_role、current_participant 不匹配，或已有别的写入会话，只返回当前任务、状态、等待的角色和参与者、工具及交接文件。匹配后核对工作区和交付版本再执行。不存在前序阶段的 DRAFT 是正常情况，不要求伪造历史。被回交到某个角色时，还要读取该角色上一轮交付物，不能只读紧邻的一条历史。

任务不等于 active_task 时同样保持只读。latest_checkpoint 只按第 10 节的轮次和身份约束解释；不匹配的指针属于状态错误，不能执行其中的“下一步”。

## 13. 正式交付物

### 13.1 `requirement.md`

包含背景、目标、非目标、验收条件、约束和用户批准记录。需求未达到可验证程度时不得进入 `READY`。

### 13.2 `plan.md`

包含目标、范围、设计、实施步骤、风险、兼容要求和验证方案。它描述意图与边界，不写成逐行代码指令。

### 13.3 `execution.md`

包含实施状态、实际修改文件、计划偏差及原因、测试结果、已知问题和希望 Reviewer 重点检查的区域。返修时追加新的修订小节，不抹掉上一轮记录。

### 13.4 `review.md`

包含审查结论、阻塞问题、非阻塞建议、已验证内容、缺失证据和最终验收结果。每个问题使用稳定编号，并标记 `OPEN`、`RESOLVED` 或 `ACCEPTED_RISK`。

审查及验证结论绑定 code_delivery_ref 和实际核对的代码版本。ACCEPTED_RISK 必须引用用户或用户指定的风险负责人的明确接受记录，Reviewer 不能自行豁免。未满足的强制验收条件须由用户明确修订，并让 Planner 更新需求和计划后才能重新评估 DONE。DONE 要求所有强制验收条件有对应证据、阻塞问题已复核解决或经授权处置；它不隐含合并、发布或部署授权。

### 13.5 `decisions.md`

保存任务产生的简化 ADR：Decision、Reason、Rejected、Constraint 和 Date。计划可以变化，已批准的架构决策不得静默删除。

## 14. 追加式阶段记录

每次角色完成一段可交接工作，都在 `progress/` 新建顺序编号文件：

```text
001-planning-codex.md
002-implementation-cursor.md
003-review-claude-code.md
004-rework-cursor.md
005-verification-claude-code.md
```

每个阶段记录必须包含：

- Role 与 Agent；
- participant_id、会话标识、输入和输出 revision；
- 开始和结束时间；
- 读取过的输入；
- 执行动作；
- 关键结论；
- 证据及其真实范围；
- 工作目录、基线与代码交付标识、未提交文件清单（如有）；
- 未解决问题；
- 下一角色、建议 Agent 和交接重点。

进度记录创建后视为历史事实，不覆盖、不重命名。需要纠正时创建下一条记录并引用被纠正的文件。

### 14.1 交接顺序

1. 当前会话核对身份、revision 和工作区，完成自己的正式交付物并标明版本。
2. 追加阶段记录，引用交付物和代码证据，标明拟交给谁。此时只是交接准备，不代表接棒生效。
3. 核对引用存在、下一参与者已注册且输出完整后，更新 STATE：递增 revision 和 stage_round、切换身份与阶段、指向新记录、清空 latest_checkpoint 和 writer_session，并设 execution 为 idle。此步骤是交接生效点。进入终态时无需下一参与者，按终态字段约束收尾；BLOCKED 等异常转换按对应字段约束执行。
4. 最后刷新 PROJECT_STATUS 当前任务的缓存及 revision，并在对话中给出接棒提示。这是交出方权限的唯一收尾例外：只允许将刚交出的 revision 同步到总览，若 STATE 已再次变化则不写。接收者经用户唤起后复核 STATE 和全部引用再开始。

多文件写入不具备事务性。STATE 更新前发生中断，由原参与者恢复并核对已写交付物；孤立历史记录不自动视为成功交接。STATE 更新后总览未更新，由当前接棒参与者在核对后修正缓存；等待中的参与者只报告。STATE 指向缺失交付物时停止，由用户授权修复，不猜测应前进还是回退。

终态后没有接棒参与者；终态总览收尾由交出方按上述例外完成。若其已中断，则由用户授权的修复会话清理残留 active_task 和缓存，不重新开启产品工作。

### 14.2 检查点和中断恢复

在可恢复的阶段边界及主动暂停前追加 CHECKPOINT 记录，包含已完成动作、已修改文件、未完成动作、测试结果、仍运行的进程和下一步；STATE 的 latest_checkpoint 指向它，保留 previous_progress 作为上一阶段交接记录。检查点不转移角色。

每条 CHECKPOINT 记录 task、stage_round、role 和 participant_id。阶段交接或责任人变更时清空活动检查点指针，原文件继续作为历史证据；接棒者可以阅读历史，但不得把上一角色的待办直接当成本轮指令。同阶段暂停恢复保留指针，新会话接管同一参与者时仍需遵守会话接管约定。

异常退出可能来不及写检查点。恢复会话须核对磁盘差异、实际进程和最近记录，区分已执行与仅计划的动作，避免重复运行迁移、发布等有副作用的操作。无法确认的结果标为未知并先做只读检查；身份或接管不明确时由用户裁决。需要补正历史时追加记录。

## 15. 等待、缺失和冲突处理

### 15.1 未轮到当前 Agent

保持只读并报告等待信息，不抢占工作，也不自行改写 current_participant 或 writer_session。

### 15.2 找不到上一个阶段记录

停止执行并指出 STATE 中失效的路径，由用户授权一个修复会话核对现场并补正。上一角色交出后已无业务写权限，只有获得修复授权才能补齐；不得凭旧身份自行写入。修复记录包含原因、证据和受影响引用，不擅自改变任务范围或产品代码。

### 15.3 Profile 缺失

在任务尚未开始写入时，可以通过首次注册流程创建；任务已处于活动写入阶段时，先请求用户确认身份和角色，避免误注册。

### 15.4 状态与总览不一致

任务 STATE 优先。只有当前执行者或用户明确授权的修复会话可以刷新该任务的总览缓存；其他参与者只报告。先核对 STATE 的引用和交接完整性，再修正缓存，不得用旧总览覆盖任务状态。

### 15.5 并发修改

比较 `STATE.md` 的 `revision` 和最近进度编号。发现 revision 或编号已经变化时，放弃基于旧上下文的写入，重新读取全部当前状态。

发现重复写入会话时停止双方继续写入，保留各自差异，请用户选择一个会话协调恢复；不得自动覆盖或回滚他人的变更。纯 Markdown 不能阻止竞态，验证应检查“发现后停止”的流程，不能声称已验证锁定能力。

### 15.6 Agent 无法识别自己

不得猜测。新身份展示角色和工具选项；已有多个匹配身份则展示 participant_id 和对应角色。用户确认后复用登记；新聊天窗口不一定能无歧义恢复身份，但无需复述任务背景。

## 16. 示例任务

模板提供一个完整的 `TASK-EXAMPLE-001`，展示：

1. Codex 作为 Planner 创建计划；
2. Cursor 作为 Implementer 完成实施；
3. Claude Code 作为 Reviewer 提出修改；
4. Cursor 返修；
5. Claude Code 完成验证并关闭任务。

示例只用于说明文件如何配合，不把上述 Agent 绑定当作强制默认值。

示例使用 planner-main、implementer-main、reviewer-main，并展示批准来源、代码交付标识、检查点和交接 revision。所有测试结果标为虚构演示，不作为本模板已运行验证的证据。同工具多身份、验证失败、阻塞恢复和交接中断通过说明书场景补充。

## 17. 说明书范围

根目录 `README.md` 和 `shared/docs/agent/README.md` 必须覆盖：

- 这套系统解决什么问题以及不解决什么问题；
- 三个角色及其权限边界；
- 模板如何复制到已有项目；
- 已有文件如何安全合并；
- 第一次注册角色和 Agent；
- 如何创建第一个任务；
- 如何规划、实施、审查、返修、验证和关闭；
- 如何从新聊天窗口恢复；
- 如何更换某个角色对应的 Agent；
- 如何处理等待、缺失文件、状态冲突和并发修改；
- 如何清理或归档已完成任务；
- 一套从需求到完成的可复制对话示例。
- 同工具多身份的选择、串行写入约定、用户授权接管和活动任务切换；
- 代码版本核对、同目录接力和不同 worktree 的显式同步；
- 检查点、交接中断、最终验证失败、阻塞、重新规划和取消；
- 各工具入口的配置与验证状态，以及文件不会自动唤醒工具的边界。

## 18. 验证方案

由于第一版只有 Markdown，验证采用结构检查和场景走查：

1. 文件清单检查：设计中要求的每个文件存在，内部链接目标有效。
2. 规则一致性检查：Codex、Cursor 和共享 Skill 对角色、状态和文件所有权的描述一致。
3. 首次注册走查：无绑定时会询问角色与 Agent，并只创建缺少的 Profile。
4. 继承走查：已有唯一匹配 Profile 时不覆盖、不重复询问；多个匹配时只确认身份。
5. 正常流程走查：Planner → Implementer → Reviewer 审查及最终验证能完成全部状态流转。
6. 返修流程走查：Reviewer → CHANGES_REQUESTED → Implementer → REVIEWING 能保留全部历史。
7. 等待走查：非当前 Agent 只报告等待状态，不产生修改。
8. 新会话恢复走查：只依赖仓库文件即可说出当前任务、当前角色、上一结论和下一动作。
9. 冲突走查：`revision` 变化或总览不一致时停止基于旧状态写入。
10. 安装走查：将模板复制到一个空示例仓库后，Codex 和 Cursor 的入口文件位于各自可发现的位置。
11. 同工具多身份：两个 Codex Profile 并存时询问身份，不按当前阶段自动认领；同身份另一会话 running 时不自动接管。
12. 版本走查：切错 worktree、缺少交付版本、代码在审查后变化时，不复用旧的审查通过结论。
13. 中断走查：分别在交付物写入后、历史写入后、STATE 写入后模拟停止，核对接棒是否生效及有权修复者。
14. 异常流转：验证失败回到返修；范围变化回到规划；BLOCKED 按条件恢复；取消不回滚代码。
15. 权限走查：等待者不修正总览；Implementer 不关闭 review 问题；Reviewer 不自行接受风险或批准计划。
16. 审阅规格时只做文本一致性检查；模板实现后才能报告结构、场景和安装验证结果。未实际使用某工具验证时标为未验证，不以文件存在代替加载成功。
17. 活动任务检查：任务 A 暂停、切换到 B 后，直接要求旧会话继续 A 时应报告非活动任务；角色匹配不能绕过切换。
18. 身份稳定性：尝试修改已有 participant_id 的 tool 或 role 时要求创建新身份；默认绑定变化不改变活动任务快照。
19. 检查点隔离：实施检查点在交给 Reviewer 后指针清空；返修新轮次不误用旧轮次的下一步。
20. 字段约束及终态收尾：BLOCKED、paused、running 和终态均符合字段表；正常终态清空本任务的 active_task，中断后的清理由授权修复会话完成。
21. 证据有效性：协作记录更新不自动作废产品测试；代码、配置或验收语义变化需要评估重新验证，未提交版本能按指纹或完整快照核对。
22. 缺失交接修复：已交出的角色保持只读，授权修复会话才可补正历史引用。

## 19. 验收条件

模板完成时必须满足：

- 只包含 Markdown 或 Markdown 衍生格式 `.mdc`，不包含执行脚本；
- 三个角色不绑定固定 Agent；
- 已登记身份唯一时自动恢复，有歧义时仅选择身份即可恢复角色和项目上下文；
- 每个任务只有一个实时状态源；
- 每个阶段都有不可覆盖的动作与结论记录；
- 非当前角色会明确等待而不是越权行动；
- 新对话无需复述历史即可继续；
- Codex 和 Cursor 使用同一套共享 Skill 和状态协议；
- 说明书足以让没有参与设计的人完成安装和首个任务；
- 完整示例覆盖规划、实施、审查、返修、验证和关闭。
- 代码审查和测试证据绑定可核对的交付版本；
- 串行写入边界、交接生效点、检查点与异常恢复有明确规则；
- 批准、风险接受、取消和接管引用真实授权，不伪造或重复索取已有授权；
- 不将文本 owner、revision 或 Skill 指令表述为并发锁或强制权限系统；
- 对未适配或未实测的工具明确标注自动加载状态。
- 非活动任务不能因身份匹配而获得业务写入权限；
- 参与者身份字段稳定，检查点按阶段轮次隔离，终态和阻塞字段组合明确；
- 提供一页日常操作入口，异常处理按需引用同一份共享协议。

## 20. 非目标

本版本不实现自动编排器、后台进程、数据库、网络同步、自动调用不同 Agent、自动提交 Git、任务看板 UI 或第三方项目管理平台集成。辅助文件锁仅保护一个 checkout 内的短时协调状态事务，不锁产品代码、不跨机器，也不替代人工授权。仓库可使用 CI 校验源码和发布包。
