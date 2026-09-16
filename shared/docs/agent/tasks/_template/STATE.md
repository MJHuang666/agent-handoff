# Task State

```yaml
task: "<TASK-ID>"
title: "<task-title>"
language: "<zh-CN|en-US>"
status: DRAFT
revision: 1
stage_round: 1
assignments:
  planner: "<planner-participant-id>"
  implementer: "<implementer-participant-id>"
  reviewer: "<reviewer-participant-id>"
current_role: planner
current_participant: "<planner-participant-id>"
writer_session: null
execution: idle
subagent_policy: UNSELECTED
subagent_decision_ref: null
previous_role: null
previous_participant: null
previous_progress: null
latest_checkpoint: null
plan_version: null
approval_ref: null
code_delivery_ref: null
next_expected_output: requirement.md
blocked_reason: null
unblock_condition: null
resume_status: null
updated_at: "<ISO-8601>"
```

## State Notes

- 业务写入前确认本任务等于 `PROJECT_STATUS.md` 的 active_task。
- 每次 STATE 修改都增加 revision；阶段或责任参与者变化时增加 stage_round。
- 字段组合和合法流转以 `../../workflow.md` 为准。
