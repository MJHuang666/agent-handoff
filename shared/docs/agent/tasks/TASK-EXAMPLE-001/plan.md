# Plan — Example

## Goal

在示例请求入口解析或生成 request_id，并把同一值交给响应头与日志上下文。

## Scope

- Included：示例请求入口、响应头写入、日志字段和针对性测试。
- Excluded：认证、响应体、日志后端和部署配置。

## Design

请求入口产生唯一 request_id，后续响应和日志只读取该请求上下文值，避免分别生成。

## Steps

1. 添加输入保留与缺失生成测试。
2. 在入口建立请求上下文。
3. 响应与日志读取同一值。
4. 运行针对性和现有测试。

## Risks and Verification

- 风险：响应与日志使用不同值；通过同一次请求的联合断言验证。
- AC-1 至 AC-3 都必须绑定交付版本。

## Approval

```yaml
plan_version: 1
status: APPROVED
approved_by: example-user
approved_at: 2026-09-16T14:20:00+08:00
authorization_ref: progress/001-planning-codex.md#authorization
```
