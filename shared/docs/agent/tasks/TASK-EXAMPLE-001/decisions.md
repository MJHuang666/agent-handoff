# Decisions — Example

## ADR-001: 单次请求只产生一个 request_id

- Date: 2026-09-16
- Status: ACCEPTED
- Decision: 响应与日志读取请求入口建立的同一个上下文值。
- Reason: 避免追踪标识不一致。
- Rejected: 响应和日志各自生成。
- Constraints: 不改变响应体。
- Authorization Ref: `plan.md#approval`
- Supersedes: null
