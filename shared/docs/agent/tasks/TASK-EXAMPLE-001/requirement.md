# Requirement — Example

> 以下项目和验证结果均为流程演示。

## Goal

示例 HTTP 服务在响应头和结构化日志中使用同一个 request_id。

## Non-goals

- 不改变认证逻辑。
- 不引入新的日志后端。

## Acceptance Criteria

- AC-1：无输入 request_id 时生成非空值，并同时写入响应头与日志字段。
- AC-2：有效输入 request_id 时保持原值。
- AC-3：现有接口测试保持通过。

## Constraints

- 不改变响应体格式。
- request_id 只用于演示，不宣称符合某个真实项目协议。

## Authorization Record

- 2026-09-16：示例用户批准上述演示范围；引用 `progress/001-planning-codex.md`。
