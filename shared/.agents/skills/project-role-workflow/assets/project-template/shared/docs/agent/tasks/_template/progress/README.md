# Progress Records

阶段记录使用 `NNN-<action>-<tool>.md`，创建后不覆盖、不重命名。

````markdown
# Progress NNN

```yaml
task: <TASK-ID>
kind: HANDOFF | CHECKPOINT | REPAIR | MANAGEMENT
role: planner | implementer | reviewer
participant_id: <participant-id>
tool: <tool-id>
writer_session: <session-id>
stage_round: <number>
input_revision: <number>
output_revision: <number-or-null>
started_at: <ISO-8601>
finished_at: <ISO-8601-or-null>
```

## Inputs Read
- <文件及版本>

## Actions
- <实际动作>

## Conclusions
- <结论>

## Evidence
- Workdir: <path>
- Branch: <branch-or-null>
- Baseline: <commit-or-snapshot>
- Delivery: <delivery-id-or-null>
- Changed files / fingerprints: <list-or-reference>
- Tests: <command, result, environment, time, delivery-id>

## Unresolved
- <未解决问题>

## Handoff
- Next role: <role-or-null>
- Next participant: <participant-id-or-null>
- Expected output: <file-or-null>
- Focus: <next action>
````

CHECKPOINT 还必须记录未完成动作、仍运行进程和恢复前需要核对的副作用。检查点只在 task、stage_round、role、participant_id 全部匹配时有效。
