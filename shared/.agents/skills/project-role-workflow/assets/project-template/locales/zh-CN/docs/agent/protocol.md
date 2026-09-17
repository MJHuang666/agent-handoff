# 项目角色工作流协议

本仓库通过文件在 Planner、Implementer 和 Reviewer 三个角色之间共享项目状态。

## 语言

首先读取 `PROJECT_STATUS.md.language`。所有面向用户的消息和新建任务文档正文都必须使用该语言。文件名、YAML 键、状态枚举、参与者 ID、交付 ID 和审查问题 ID 保持稳定，不做翻译。

## 写入资格

只有同时满足以下条件，才允许写入业务文件：存在活动任务、参与者身份已确认、当前角色与分派一致、不存在其他写入会话，并且工作目录和版本证据已经核对。否则保持只读，并说明当前正在等待哪个参与者。

## 更换 Agent

接受“更换 Agent”“替换 Agent”“replace agent”和“switch agent”。旧 Agent 或新 Agent 都可以发起这一明确授权的管理操作。角色保持不变，每次选择 `current-task`、`project-default` 或 `both` 范围，并创建或复用同角色身份。优先使用 `.agents/skills/project-role-workflow/scripts/workflow_state.py` 提供短时本地锁、expected revision 校验和原子替换。

允许 A → B → A 多次切换，每次复用不可变 participant_id 并追加 MANAGEMENT 记录。当前责任参与者变化时增加 revision 和 stage_round，清空 writer/checkpoint；非当前角色绑定只增加 revision。Implementer 更换后重置子代理选择。不得自动释放锁或覆盖运行中的 writer；更换管理操作结束后，新参与者再单独执行“继续”。

## Implementer 子代理门禁

修改产品代码前，`STATE.md.subagent_policy` 必须是 `USE` 或 `DO_NOT_USE`。如果值为 `UNSELECTED`，先用项目语言询问用户，并把用户的明确选择记录到 `subagent_decision_ref`。只有选择 `USE` 才能使用子代理，同时必须记录委派内容、结果和证据。

## 角色

- Planner 负责需求、计划、决策和验收标准；Planner 不修改产品代码。
- Implementer 负责代码、测试、实施证据和返修；Implementer 不关闭审查问题。
- Reviewer 独立检查真实交付，并决定返修、退回规划、阻塞、验证或完成；Reviewer 不直接修复产品代码。

## 交接

完成本角色交付物，追加进度记录，以更新 `STATE.md` 作为交接提交点，清除写入者占用，最后刷新 `PROJECT_STATUS.md`。文件不会自动唤醒另一个工具；用户需要打开下一个工具并输入 `继续` 或 `continue`。

`DONE` 只表示任务验收完成，并不授权合并、发布、部署、删除、回滚或接管。
