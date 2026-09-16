# 多 Agent 工作流

## 日常流程

1. 读取项目语言并统一后续交流和新文档。
2. 从角色绑定和 Profile 确认参与者身份。
3. 核对活动任务、当前角色、参与者、执行状态和写入会话。
4. 读取角色规则、需求、上一交付、检查点、决策和真实代码版本。
5. 登记写入会话；Implementer 修改代码前必须完成子代理选择门。
6. 写正式交付物和进度记录，更新 STATE，再刷新项目总览。

## 正常状态流

```text
DRAFT → PLANNING → READY → IMPLEMENTING → REVIEWING → VERIFYING → DONE
                                  ↑            │
                                  └─ CHANGES_REQUESTED
```

## Implementer 子代理选择门

修改产品代码前读取 `STATE.md.subagent_policy`。如果是 `UNSELECTED`，先询问“本次实施是否使用子代理？使用 / 不使用”，记录 `USE` 或 `DO_NOT_USE` 及 `subagent_decision_ref`。未选择前不得实施。

## 交接

完成正式交付物，追加进度记录，更新 STATE 使交接生效，清除写入会话，再刷新 PROJECT_STATUS。文件不会自动唤醒下一工具，用户需切换窗口并说“继续”。
