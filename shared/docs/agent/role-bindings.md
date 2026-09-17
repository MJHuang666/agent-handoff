# Role Bindings

参与者身份在项目内唯一。`participant_id` 对应的 `tool` 和 `role` 创建后不可改变。状态为 `active`、`standby` 或 `retired`；更换 Agent 时创建或复用同角色身份，切回旧 Agent 时复用原 participant_id。

| Participant ID | Tool | Role | Profile | Status | Created At |
|---|---|---|---|---|---|

## Project Defaults

| Role | Participant ID |
|---|---|
| Planner | 未设置 |
| Implementer | 未设置 |
| Reviewer | 未设置 |

项目默认值只用于新任务。活动任务的绑定快照保存在该任务 `STATE.md` 的 `assignments` 中。

## Default Binding History

尚无更换记录。通过工作流更换项目默认 Agent 时，追加 Transaction、时间、角色、旧/新 participant、原因和授权，不覆盖旧记录。
