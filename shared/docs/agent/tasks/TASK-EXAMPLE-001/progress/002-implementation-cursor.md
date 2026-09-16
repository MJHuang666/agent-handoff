# Progress 002 — Implementation Example

```yaml
task: TASK-EXAMPLE-001
kind: HANDOFF
role: implementer
participant_id: implementer-main
tool: cursor
writer_session: cursor-example-impl-1
stage_round: 4
input_revision: 5
output_revision: 6
started_at: 2026-09-16T14:25:00+08:00
finished_at: 2026-09-16T15:00:00+08:00
```

## Actions and Evidence

- 生成 delivery 1；示例工作目录 `/example/project`，分支 `example/request-id`。
- 示例文件指纹：`src/request.ts sha256:1111...`、`tests/request.test.ts sha256:2222...`。
- 针对性测试演示 PASS；这些值不是实际验证证据。

## Unresolved and Handoff

- 未知是否覆盖有效输入值。
- Next participant: reviewer-main；重点检查 request_id 兼容行为。
