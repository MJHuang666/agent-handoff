# Collaboration Conventions

## Naming

- 任务编号：`TASK-YYYYMMDD-NNN`。
- participant_id：小写字母、数字和连字符，例如 `planner-main`。
- 阶段记录：三位递增编号、动作、工具，例如 `003-review-codex.md`。
- 检查点记录：同一编号规则，动作使用 `checkpoint`。

## Time and Versions

- 时间使用带时区的 ISO 8601，例如 `2026-09-16T14:30:00+08:00`。
- Git 提交使用完整提交 ID；未提交交付使用唯一 delivery_id 和 SHA-256 内容指纹或完整差异快照。
- 测试证据写明命令、结果、时间、环境和对应 delivery_id。

## Language

- 项目可自行选择中英文，但同一字段名保持稳定。
- `status`、`execution`、`role`、`participant_id` 等机器可读字段使用本模板规定的英文值。
- 未验证的结果写“未验证”或 `UNKNOWN`，不根据聊天内容推断成功。

## History

- `progress/` 文件创建后不覆盖、不重命名。
- 纠正历史时新增记录，并引用被纠正文件。
- 聊天总结不是项目状态；重要事实必须落入任务文件。
