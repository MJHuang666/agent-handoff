# Role Bindings

参与者身份在项目内唯一。`participant_id` 对应的 `tool` 和 `role` 创建后不可改变；更换工具或角色时创建新身份并停用旧身份。

| Participant ID | Tool | Role | Profile | Status | Created At |
|---|---|---|---|---|---|

## Project Defaults

| Role | Participant ID |
|---|---|
| Planner | 未设置 |
| Implementer | 未设置 |
| Reviewer | 未设置 |

项目默认值只用于新任务。活动任务的绑定快照保存在该任务 `STATE.md` 的 `assignments` 中。
