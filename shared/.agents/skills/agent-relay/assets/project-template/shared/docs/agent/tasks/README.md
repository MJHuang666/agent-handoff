# Task Directories

新任务复制 `_template/` 为 `TASK-YYYYMMDD-NNN/`，然后由 Planner 在授权范围内填写 requirement、STATE 和首条 progress。项目默认参与者复制到 STATE assignments，形成任务级快照。

创建任务时，把 `PROJECT_STATUS.md.language` 快照写入任务 `STATE.md.language`，并让 requirement、plan、execution、review、decisions 和 progress 的正文使用该语言。新任务的 `subagent_policy` 必须从 `UNSELECTED` 开始，Implementer 在实施前取得用户选择。

每个任务固定包含：

- `STATE.md`：唯一实时状态源；
- `requirement.md`：目标、非目标、验收和约束；
- `plan.md`：Planner 正式交付；
- `execution.md`：Implementer 正式交付及返修记录；
- `review.md`：Reviewer 问题与最终结论；
- `decisions.md`：持久决策；
- `progress/`：追加式历史及检查点。

模板中的尖括号字段需要在创建任务时填写。无法确认的值使用 `null` 或明确的 `UNKNOWN`，不编造事实。
