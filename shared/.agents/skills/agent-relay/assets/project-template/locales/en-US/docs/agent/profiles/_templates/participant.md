# Participant Profile

```yaml
participant_id: "<unique-id>"
display_name: "<human-readable-name>"
tool: "<codex|cursor|claude-code|workbuddy|zcode|trae|deepseek-harness|opencode|other-id>"
role: "<planner|implementer|reviewer>"
role_file: "../../roles/<role>.md"
status: "<active|standby|retired>"
created_at: "<ISO-8601>"
```

## Project-specific Agreements

- Record only confirmed project preferences that differ from the shared role rules.

## Change History

- Record creation date and source. Identity fields must not be repurposed.
- A standby identity may be reactivated by an authorized replacement; a retired identity requires an explicit reactivation decision.
