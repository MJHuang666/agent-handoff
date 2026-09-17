# Agent Relay v1.5 migration / v1.5 迁移

v1.5 renames the public Skill and project directory from `project-role-workflow` to `agent-relay`. It keeps one thin legacy redirect until v2.0; the canonical implementation is now `.agents/skills/agent-relay/`.

v1.5 将公开 Skill 与项目目录从 `project-role-workflow` 更名为 `agent-relay`。在 v2.0 前保留一个薄的旧名称跳转层；唯一完整实现为 `.agents/skills/agent-relay/`。

## Safe order / 安全顺序

1. Stop or explicitly pause the active writer session. Do not migrate while a foreign writer is running.
2. Commit or otherwise preserve the current repository state before changing files.
3. Install the new canonical Skill, then update project instructions and project Skill.
4. Open a fresh Agent session and run `$agent-relay continue` / `$agent-relay 继续` in read-only recovery mode first.
5. Only after state, participant, revision, and delivery evidence match, register a new writer session.

## Global and project Skill / 全局与项目 Skill

- Back up a personal v1.4 `project-role-workflow` Skill before replacing it with personal `agent-relay`.
- Replace a project’s complete `.agents/skills/project-role-workflow/` directory with `.agents/skills/agent-relay/`; do not keep two full implementations.
- A legacy command can resolve through `compat/project-role-workflow/SKILL.md`, but all new instructions, prompts, and task records must use `$agent-relay`.
- Update root `AGENTS.md` marker blocks and Cursor rules/commands to point to `agent-relay`. Existing project-specific instructions must be merged, never overwritten.

## Lock transition / 锁迁移

The helper writes `agent-relay.lock` (or `.agent-relay.lock` outside Git). It still recognizes the old `project-role-workflow.lock` to prevent concurrent writes. If both exist, it deliberately refuses automatic release; inspect the two owners and obtain explicit authorization before resolving the conflict.

辅助脚本会写入 `agent-relay.lock`（Git 外为 `.agent-relay.lock`），同时识别旧 `project-role-workflow.lock`，避免并发写入。如果两者同时存在，脚本会拒绝自动释放；必须检查两个持有者，并在明确授权后解决冲突。

## Uncommitted-state handoff package / 未提交状态交接包

Git clone only recovers committed state. Before moving an active, dirty repository to another machine or Agent, create a **manual handoff package** outside the repository and transfer it with the target checkout:

```text
relay-handoff-<TASK-ID>-<timestamp>/
  manifest.md              source path, branch, HEAD, active task, revision, participant
  git-status.txt           porcelain v2 status
  git-diff.patch           tracked unstaged changes
  git-staged.patch         staged changes
  untracked/               copied untracked files, excluding secrets and build output
  docs-agent/              current docs/agent/ tree snapshot
```

Record hashes for every included file in `manifest.md`. Never put credentials, private keys, caches, or generated build directories in the package. On the target machine, verify branch/HEAD, manifest hashes, active task, revision, and `delivery_id` before applying patches or copying untracked files. Record the verification as a progress entry; only then may the assigned participant resume.

未提交状态不能依赖 clone 恢复。迁移前在仓库外创建上述交接包：记录分支、HEAD、活动任务、revision 和参与者，分别导出暂存/未暂存补丁，单独复制必要的未跟踪文件和 `docs/agent/` 快照。不得打包密钥、凭证、缓存或构建产物。目标端先校验清单哈希、分支/HEAD、任务状态与 `delivery_id`，再应用内容并写入 progress 证据。

## Rollback / 回退

Rollback restores only the backed-up Skill or adapter files. It must never overwrite `docs/agent/tasks/`, `PROJECT_STATUS.md`, `role-bindings.md`, Profiles, architecture records, or delivery evidence. Those are project data and remain authoritative throughout migration.
