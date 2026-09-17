# Participant Profile

```yaml
participant_id: "<unique-id>"
display_name: "<human-readable-name>"
tool: "<codex|cursor|claude-code|workbuddy|zcode|trae|other-id>"
role: "<planner|implementer|reviewer>"
role_file: "../../roles/<role>.md"
status: "<active|standby|retired>"
created_at: "<ISO-8601>"
```

## Project-specific Agreements

- 仅记录该参与者与通用角色规则不同的、经确认的项目偏好。

## Change History

- 创建身份时记录日期和来源；身份字段不得改作另一身份。
- `standby` 可在授权更换时重新激活；`retired` 必须经过明确的重新启用决定。
