# Role Bindings

Participant identities are unique within the project. A participant's `tool` and `role` are immutable. Status is `active`, `standby`, or `retired`; Agent replacement creates or reuses a same-role identity, and switching back reuses the original participant ID.

| Participant ID | Tool | Role | Profile | Status | Created At |
|---|---|---|---|---|---|

## Project Defaults

| Role | Participant ID |
|---|---|
| Planner | Unset |
| Implementer | Unset |
| Reviewer | Unset |

## Default Binding History

No replacement has been recorded. Default-Agent changes append transaction, time, role, old/new participants, reason, and authorization without overwriting prior entries.
