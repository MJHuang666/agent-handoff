# 任务状态

```yaml
task: "<TASK-ID>"
title: "<任务标题>"
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

业务写入前，本任务必须等于 `PROJECT_STATUS.md.active_task`。每次修改 STATE 增加 `revision`；阶段或责任人变化时增加 `stage_round`。
