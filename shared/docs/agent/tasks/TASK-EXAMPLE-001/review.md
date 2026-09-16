# Review — Example

> 结论和证据均为流程演示。

## Review Round 1

```yaml
participant_id: reviewer-main
delivery_id: TASK-EXAMPLE-001-delivery-1
review_result: CHANGES_REQUESTED
reviewed_version: uncommitted-snapshot-example-1
reviewed_at: 2026-09-16T15:20:00+08:00
```

| ID | Status | Location | Problem | Risk | Required Outcome | Resolution Evidence |
|---|---|---|---|---|---|---|
| R1 | RESOLVED | `tests/request.test.ts` | 未验证有效输入值保持 | 可能覆盖调用方追踪 ID | 增加测试并统一上下文取值 | Delivery 2 + 验证记录 |

## Review Round 2 and Final Verification

```yaml
participant_id: reviewer-main
delivery_id: TASK-EXAMPLE-001-delivery-2
review_result: APPROVED
reviewed_version: uncommitted-snapshot-example-2
reviewed_at: 2026-09-16T16:25:00+08:00
result: PASS
mandatory_acceptance_criteria_met: true
open_blocking_issues: 0
accepted_risk_refs: []
```

### Verified

- AC-1：演示的联合断言通过。
- AC-2：新增保持输入值测试通过。
- AC-3：演示全套测试通过。

该 DONE 只演示任务验收，不表示已提交、合并、发布或部署。
