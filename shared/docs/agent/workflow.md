# Multi-Agent Workflow

## Daily Path

1. 读取 `PROJECT_STATUS.md.language`，后续交流和新文档统一使用该语言。
2. 确认身份：读取 `role-bindings.md` 和 Profile。唯一匹配时恢复；多个匹配时只确认 participant_id。
3. 检查轮次：读取 `PROJECT_STATUS.md` 和活动任务 `STATE.md`，核对 active_task、角色、参与者、execution 和 writer_session。
4. 读取输入：角色文件、requirement、上一阶段交付物、有效检查点、decisions 和真实代码版本。
5. 执行：登记本次 writer_session，按角色权限工作；Implementer 改代码前必须完成子代理选择门；暂停时写检查点。
6. 交接：完成正式交付物，追加 progress，更新 STATE，最后刷新总览缓存。

文件不会唤醒其他工具。交接后，用户在下一工具或窗口输入“继续”。

## Authority Split

- `PROJECT_STATUS.md` 的 `active_task` 决定唯一允许业务写入的任务。
- 活动任务 `STATE.md` 决定阶段、当前参与者和会话占用。
- `role-bindings.md` 决定 participant_id 的 tool、role 和 Profile；tool 和 role 创建后不可改变。
- requirement、plan、execution、review、decisions 保存正式事实；`progress/` 保存不可覆盖的过程历史。

## Starting Work

只有同时满足以下条件才能业务写入：

- 目标任务等于 active_task；
- 本会话已确认 participant_id；
- participant_id 等于 current_participant，角色和 assignments 一致；
- execution 不是 BLOCKED 场景下的 paused；
- 没有属于其他会话的 writer_session；
- 工作目录和代码交付版本已经核对。

开始时写入可追踪的 writer_session 并把 execution 设为 running，revision 递增。本模板依靠人为单写入约定；字段不是锁。

Implementer 在 `subagent_policy: UNSELECTED` 时不得进入产品代码修改阶段；必须先用项目语言获得用户的 `USE` 或 `DO_NOT_USE` 选择并写入 `subagent_decision_ref`。

## Normal State Flow

```text
DRAFT → PLANNING → READY → IMPLEMENTING → REVIEWING → VERIFYING → DONE
                                  ↑            │
                                  └─ CHANGES_REQUESTED
```

- Planner 把经批准的计划交给 Implementer。
- Implementer 把 delivery_id、代码证据和 execution 交给 Reviewer。
- Reviewer 可以交回 CHANGES_REQUESTED，或进入 VERIFYING 后完成任务。
- 范围或设计需要变化时回 PLANNING。
- 用户取消进入 CANCELLED；任何非终态可进入 BLOCKED。

## Handoff Commit Point

按以下顺序执行：

1. 完成本角色正式交付物并标明版本。
2. 新建 progress 记录，写明输入、动作、结论、证据、交付版本和下一参与者。
3. 核对引用与下一参与者后更新 STATE：递增 revision 和 stage_round，切换阶段与参与者，清空 writer_session 和 latest_checkpoint，execution 设 idle。STATE 更新是交接生效点。
4. 最后只把刚交出的 revision 刷新到 PROJECT_STATUS；若 STATE 已再次变化则不写。

STATE 更新前中断时，交接尚未生效；孤立 progress 只作为恢复证据。STATE 更新后总览未刷新时，由当前接棒参与者核对后刷新缓存。

## Pause, Block, and Recovery

- 主动暂停：写 CHECKPOINT，STATE 保持原 status，execution=paused，writer_session=null。
- CHECKPOINT 必须匹配 task、stage_round、role 和 participant_id；阶段交接或责任人变化时清空指针。
- BLOCKED：execution=paused，记录 blocked_reason、unblock_condition 和 resume_status；不靠时间自动抢占。
- running 且 writer_session 属于其他会话：即使同一 participant_id，也要确认原会话停止并获得明确接管授权。
- 异常退出后先只读核对 diff、进程和证据；无法确认的副作用标为 UNKNOWN。
- 状态或历史损坏由用户授权的修复会话补正，旧角色不能凭历史身份自行写入。

## Terminal States

DONE 或 CANCELLED 时：execution=idle；current_role、current_participant、writer_session、next_expected_output、latest_checkpoint 均为 null。完成转换的会话清空仍指向该任务的 active_task，不自动选择下一任务。

DONE 只代表任务验收完成，不等于合并、发布或部署授权。
