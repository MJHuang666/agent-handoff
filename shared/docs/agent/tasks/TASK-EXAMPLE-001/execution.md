# Execution — Example

> 文件名、提交和测试结果为虚构演示。

## Delivery 1

```yaml
delivery_id: TASK-EXAMPLE-001-delivery-1
status: REVIEWED_CHANGES_REQUESTED
participant_id: implementer-main
plan_version: 1
baseline: 0000000000000000000000000000000000000000
delivery_version: uncommitted-snapshot-example-1
workdir: /example/project
branch: example/request-id
completed_at: 2026-09-16T15:00:00+08:00
```

### Changed

- `src/request.ts`：生成或读取 request_id。
- `tests/request.test.ts`：新增缺失值测试。

### Deviations From Plan

- 漏掉了有效输入值保持测试；Reviewer 记录为 R1。

### Version Evidence

- 演示快照：`progress/002-implementation-cursor.md`；其中的指纹仅用于说明字段格式。

### Tests and Checks

| Command | Result | Environment | Time | Delivery ID |
|---|---|---|---|---|
| `npm test -- request.test.ts` | 演示 PASS | Node example | 2026-09-16 14:58 +08:00 | delivery-1 |

## Delivery 2

```yaml
delivery_id: TASK-EXAMPLE-001-delivery-2
status: VERIFIED
participant_id: implementer-main
plan_version: 1
baseline: 0000000000000000000000000000000000000000
delivery_version: uncommitted-snapshot-example-2
workdir: /example/project
branch: example/request-id
completed_at: 2026-09-16T15:48:00+08:00
```

### Rework

- R1：增加有效输入 request_id 保持测试，并让响应与日志读取同一上下文值。

### Tests and Checks

| Command | Result | Environment | Time | Delivery ID |
|---|---|---|---|---|
| `npm test -- request.test.ts` | 演示 PASS | Node example | 2026-09-16 15:46 +08:00 | delivery-2 |
| `npm test` | 演示 PASS | Node example | 2026-09-16 15:47 +08:00 | delivery-2 |
