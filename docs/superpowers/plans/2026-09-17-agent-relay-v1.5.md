# Agent Relay v1.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `project-role-workflow` 全面升级为 `agent-relay` v1.5.0，新增长期知识索引和全新 clone 恢复端到端验证，同时保证现有 v1.4 项目可安全迁移。

**Architecture:** `shared/.agents/skills/agent-relay/` 成为唯一完整 Skill 事实源，新命令统一为 `$agent-relay`。`knowledge-index.md` 只索引经验证的长期架构、约束、决策和经验，不复制任务全文。本地 Git clone 端到端测试证明仅依赖已提交仓库文件即可恢复活动任务；v1.5 保留一个无资产的旧 Skill 跳转壳，v2.0 删除。

**Tech Stack:** Markdown/MDC、YAML frontmatter、Python 3 标准库 `unittest`、Git CLI、Bash 发行校验。

**Spec:** `docs/superpowers/specs/2026-09-16-multi-agent-project-state-sharing-design.md`

## Global Constraints

- 发行版本固定为 `1.5.0`，公开品牌和 Skill 名固定为 `Agent Relay` / `agent-relay`。
- 新命令是 `$agent-relay 初始化当前仓库`、`$agent-relay 继续`、`$agent-relay 更换 Agent`及对应英文。
- 新项目只安装 `.agents/skills/agent-relay/`，不安装旧完整 Skill 副本。
- v1.5 兼容壳 `compat/project-role-workflow/SKILL.md` 只做旧命令跳转，不包含 `assets/`、`references/` 或 `scripts/`。
- 活动 README、使用手册、安装文档、Skill、适配器和模板不再把旧名称当作正式名称；旧名只允许出现在兼容壳、迁移说明、历史 Changelog 和旧计划中。
- 不改变 Planner、Implementer、Reviewer 三角色、状态枚举、participant_id 不可变性和单写入边界。
- Knowledge Index 仅保存摘要和相对链接；没有证据的聊天结论不得晋升为长期知识。
- clone 恢复测试不访问网络、不调用付费模型，必须在 GitHub Actions Ubuntu 上稳定运行。
- 兼容旧锁 `project-role-workflow.lock`：新 helper 发现旧锁时必须阻止写入，不得视为无锁。
- 实施可创建本地提交，但不推送 GitHub、不创建 Release。

---

### Task 1: 先建立 v1.5 命名与兼容合同测试

**Files:**
- Create: `tests/test_agent_relay_contract.py`
- Modify: `.github/scripts/validate-release.sh`

**Interfaces:**
- Consumes: v1.4 源码树、发行脚本和当前 Skill 镜像规则。
- Produces: 重命名后必须满足的路径、frontmatter、命令、兼容壳和禁止旧副本的自动断言。

- [ ] **Step 1: 新增失败的命名合同测试**

  `tests/test_agent_relay_contract.py` 必须断言：

  ```python
  CANONICAL = ROOT / "shared/.agents/skills/agent-relay"
  LEGACY = ROOT / "shared/.agents/skills/project-role-workflow"

  def test_canonical_skill_identity():
      assert (CANONICAL / "SKILL.md").is_file()
      assert "name: agent-relay" in (CANONICAL / "SKILL.md").read_text()
      assert not LEGACY.exists()

  def test_legacy_compatibility_is_thin():
      shim = ROOT / "compat/project-role-workflow/SKILL.md"
      assert shim.is_file()
      assert not (shim.parent / "assets").exists()
      assert not (shim.parent / "scripts").exists()
  ```

- [ ] **Step 2: 新增公开命令扫描**

  对 README、`distribution/`、`codex/`、`cursor/`、当前设计规格和 `shared/` 扫描，要求公开命令使用 `$agent-relay`。旧词允许列表仅包含 `compat/`、`CHANGELOG.md` 的历史条目、迁移指南和 2026-09-16 历史计划。

- [ ] **Step 3: 运行测试并确认 RED**

  ```bash
  python3 -m unittest -v tests/test_agent_relay_contract.py
  ```

  Expected: FAIL，因为 `agent-relay` 路径和兼容壳尚不存在。

- [ ] **Step 4: 将发行验证改为 unittest discover**

  ```bash
  python3 -m unittest discover -s tests -p 'test_*.py' -v
  ```

- [ ] **Step 5: 提交测试基线**

  ```bash
  git add tests/test_agent_relay_contract.py .github/scripts/validate-release.sh
  git commit -m "test: define agent relay v1.5 contract"
  ```

### Task 2: 重命名核心 Skill、命令、锁和升级路径

**Files:**
- Rename: `shared/.agents/skills/project-role-workflow/` → `shared/.agents/skills/agent-relay/`
- Rename: nested bootstrap `.agents/skills/project-role-workflow/` → `.agents/skills/agent-relay/`
- Create: `compat/project-role-workflow/SKILL.md`
- Create: `shared/.agents/skills/agent-relay/references/migration-v1.5.md`
- Modify: `shared/.agents/skills/agent-relay/SKILL.md`
- Modify: `shared/.agents/skills/agent-relay/references/{initialization,protocol,state-helper}.md`
- Modify: `shared/.agents/skills/agent-relay/scripts/workflow_state.py`
- Modify: `codex/AGENTS.md`, `codex/prompts/*.md`, `cursor/.cursor/{rules,commands}/**`
- Modify: all adapter mirrors under `assets/project-template/adapters/`
- Test: `tests/test_workflow_state.py`, `tests/test_agent_relay_contract.py`

**Interfaces:**
- Consumes: Task 1 命名合同。
- Produces: `$agent-relay` 调用、`.agents/skills/agent-relay/` 自举模板、`agent-relay.lock` 和可回退的 v1.4 升级说明。

- [ ] **Step 1: 用 `git mv` 重命名唯一事实源和嵌套自举副本**

  先移动顶层 Skill 目录，再移动其 `assets/project-template/shared/.agents/skills/` 中的嵌套 Skill 目录。不通过拷贝保留两份完整 Skill。

- [ ] **Step 2: 更新 Skill 身份和公开命令**

  `SKILL.md` frontmatter 使用 `name: agent-relay`，标题使用 `Agent Relay`，命令表改为 `$agent-relay ...`，初始化目标路径改为 `.agents/skills/agent-relay/`。

- [ ] **Step 3: 新增一个无资产兼容壳**

  `compat/project-role-workflow/SKILL.md` 只包含合法 frontmatter、弃用通知和路由要求：将旧命令的参数原样交给同级 `../agent-relay/SKILL.md`，不复制协议、脚本或模板。

- [ ] **Step 4: 定义 v1.4 → v1.5 项目升级算法**

  `migration-v1.5.md` 固定以下顺序：检查旧项目 Skill 是否有本地改动；安装新 Skill；更新 AGENTS 标记块、Cursor 规则和文档引用；将旧 Skill 替换为兼容壳；运行 status；用新命令开启新会话验证。发现本地改动时停止自动替换并报告冲突。

- [ ] **Step 5: 更新 AGENTS 标记块迁移规则**

  新标记为 `<!-- agent-relay:start -->` / `<!-- agent-relay:end -->`。初始化时如发现旧标记块，在保留块外用户内容的前提下原位替换，不追加第二个块。

- [ ] **Step 6: 实现新旧锁兼容**

  helper 写入新锁 `agent-relay.lock`，但任何变更前同时检查 `agent-relay.lock` 和 `project-role-workflow.lock`。任一存在即阻止写入；两者同时存在时拒绝自动选择。`release-stale-lock` 需显式报告实际锁路径并保留原授权门禁。

- [ ] **Step 7: 补充锁迁移测试**

  新增断言：旧锁阻止 `replace-agent`；新锁位于正确 Git worktree gitdir；两锁并存时拒绝释放；获授权释放单一旧锁后可重新读取状态。

- [ ] **Step 8: 运行合同和 helper 测试**

  ```bash
  python3 -m unittest -v tests/test_agent_relay_contract.py tests/test_workflow_state.py
  ```

- [ ] **Step 9: 提交 Skill 迁移**

  ```bash
  git add shared compat codex cursor tests
  git commit -m "feat: rename workflow skill to agent relay"
  ```

### Task 3: 新增可验证的长期 Knowledge Index

**Files:**
- Create: `shared/docs/agent/knowledge-index.md`
- Create: `shared/.agents/skills/agent-relay/assets/project-template/locales/en-US/docs/agent/knowledge-index.md`
- Create: `shared/.agents/skills/agent-relay/assets/project-template/locales/zh-CN/docs/agent/knowledge-index.md`
- Modify: bootstrap shared copy under `assets/project-template/shared/docs/agent/`
- Modify: `shared/docs/agent/{README,workflow,protocol}.md`
- Modify: `shared/docs/agent/roles/{planner,reviewer}.md`
- Modify: `shared/.agents/skills/agent-relay/SKILL.md`
- Test: `tests/test_agent_relay_contract.py`

**Interfaces:**
- Consumes: 已有 `architecture/`、任务 `decisions.md`、`review.md`、`execution.md` 和 progress 证据。
- Produces: 每次会话可快速读取的长期认知索引及可审查的知识晋升规则。

- [ ] **Step 1: 先添加 Knowledge Index 结构测试**

  断言中英文模板和 bootstrap 副本都存在，并包含 `Architecture`、`Constraints`、`Decisions`、`Verified Lessons`、`Superseded` 五类索引。

- [ ] **Step 2: 创建仅索引的数据格式**

  每条固定字段为 `ID | Summary | Scope | Source | Evidence | Status | Last Verified`，`Status` 只允许 `ACTIVE | SUPERSEDED | RETIRED`。`Source` 和 `Evidence` 必须是仓库内相对链接，不在索引中复制完整 ADR 或任务经过。

- [ ] **Step 3: 定义知识晋升权限**

  Planner 在任务 `decisions.md` 中提出长期知识候选；Reviewer 在 `VERIFYING` 阶段核对代码、文档和验收证据后才能将其写入索引。替代旧知识时保留旧条目并标记 `SUPERSEDED`。

- [ ] **Step 4: 更新 Agent 读取顺序**

  新会话先读 `PROJECT_STATUS.md`，再读紧凑的 `knowledge-index.md`，然后只跟随当前任务相关链接。索引本身不得记录聊天摘要、未验证猜测或短期待办。

- [ ] **Step 5: 同步唯一事实源、bootstrap 和语言 overlay**

  中文和英文 overlay 只本地化说明文字，表头、ID 和状态枚举保持一致。

- [ ] **Step 6: 运行测试并提交**

  ```bash
  python3 -m unittest -v tests/test_agent_relay_contract.py
  git add shared tests/test_agent_relay_contract.py
  git commit -m "feat: add durable project knowledge index"
  ```

### Task 4: 增加全新 clone 后任务恢复端到端测试

**Files:**
- Create: `tests/test_clone_recovery.py`
- Modify: `.github/scripts/validate-release.sh`

**Interfaces:**
- Consumes: `.agents/skills/agent-relay/`、`docs/agent/`、Codex `AGENTS.md`、Knowledge Index 和 `workflow_state.py status` JSON。
- Produces: 在新路径 clone 后可恢复活动任务的 CI 证据。

- [ ] **Step 1: 编写失败的 clone 恢复测试**

  `tests/test_clone_recovery.py` 使用 `tempfile.TemporaryDirectory`，在源仓库中复制初始化所需的 `docs/agent/`、`.agents/skills/agent-relay/` 和根 `AGENTS.md`，删除示例任务，然后写入一个可恢复的 `TASK-RECOVERY-001`。

- [ ] **Step 2: 创建真实 Git 基线和全新 clone**

  ```python
  run("git", "init", "-b", "main", cwd=source)
  run("git", "config", "user.name", "Agent Relay Test", cwd=source)
  run("git", "config", "user.email", "relay@example.invalid", cwd=source)
  run("git", "add", ".", cwd=source)
  run("git", "commit", "-m", "fixture: active relay task", cwd=source)
  (source / "UNCOMMITTED-SENTINEL.txt").write_text("must not migrate")
  run("git", "clone", str(source), str(clone))
  ```

- [ ] **Step 3: 在 clone 中只用仓库文件恢复**

  运行 clone 内 `.agents/skills/agent-relay/scripts/workflow_state.py --repo <clone> status`，解析 JSON 并断言：`active_task=TASK-RECOVERY-001`、预期 revision/stage_round、当前 role/participant、writer 为 null、lock 不存在。

- [ ] **Step 4: 断言认知和交接资产完整**

  验证 requirement、plan、previous progress、decisions、Knowledge Index 条目和其相对链接都存在，文本中不得包含源临时目录绝对路径。

- [ ] **Step 5: 断言 Git 边界**

  `UNCOMMITTED-SENTINEL.txt` 不得出现在 clone，以明确证明 v1.5 clone 恢复只承诺已提交资产，未提交迁移包留待后续版本。

- [ ] **Step 6: 运行单测和全量测试**

  ```bash
  python3 -m unittest -v tests/test_clone_recovery.py
  python3 -m unittest discover -s tests -p 'test_*.py' -v
  ```

- [ ] **Step 7: 提交 clone 恢复证据**

  ```bash
  git add tests/test_clone_recovery.py .github/scripts/validate-release.sh
  git commit -m "test: verify recovery from a fresh clone"
  ```

### Task 5: 将 Relay 升级为正式品牌并统一活动文档

**Files:**
- Modify: `README.md`, `README.zh-CN.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`
- Rename: `docs/PROJECT_ROLE_WORKFLOW_USAGE.md` → `docs/AGENT_RELAY_USAGE.md`
- Rename: `docs/PROJECT_ROLE_WORKFLOW_USAGE.en-US.md` → `docs/AGENT_RELAY_USAGE.en-US.md`
- Modify: `docs/superpowers/specs/2026-09-16-multi-agent-project-state-sharing-design.md`
- Modify: `distribution/INSTALL.md`, `distribution/INSTALL_PROMPT.md`
- Modify: active files under `shared/docs/agent/` and locale/bootstrap mirrors
- Create: `docs/migration-v1.5.md`

**Interfaces:**
- Consumes: Tasks 2-4 已验证的新名称、知识层和 clone 恢复能力。
- Produces: 统一的 Agent Relay 中英文定位、用法、迁移指南和设计基线。

- [ ] **Step 1: 固定品牌核心句**

  English:

  ```text
  Agent Relay is a lightweight multi-Agent collaboration framework. Coding Agents do not share conversation context; they relay durable project state through the repository.
  ```

  中文：

  ```text
  Agent Relay 是一个轻量级多 Agent 接力协作框架。Coding Agent 不需要共享对话上下文，只需要通过代码仓库接力可持久的项目状态。
  ```

- [ ] **Step 2: 明确 Relay 边界**

  README 和设计文档必须同时说明：Relay 不自动唤醒 Agent、不自动跨机同步、不替代 Git、不是分布式锁、不自动合并/发布/部署。

- [ ] **Step 3: 重命名使用手册并更新所有链接**

  中英文手册的标题、命令、Skill 路径、helper 路径和跳转链接全部使用 `agent-relay`。

- [ ] **Step 4: 写 v1.5 迁移指南**

  `docs/migration-v1.5.md` 覆盖全局 Skill、项目 Skill、AGENTS 块、Cursor 入口、旧锁、新命令和回退方式。回退只恢复备份的 v1.4 Skill 和引用，不回滚项目任务数据。

- [ ] **Step 5: 处理历史文档**

  2026-09-16 旧计划和 v1.1-v1.4 Changelog 保留当时名称，在文档顶部添加“Legacy name before Agent Relay v1.5”注记，不改写历史事实。

- [ ] **Step 6: 运行链接和旧名扫描**

  ```bash
  bash .github/scripts/validate-release.sh
  rg -n 'project-role-workflow|Project Role Workflow' README.md README.zh-CN.md distribution shared codex cursor docs
  ```

  Expected: 旧名命中仅剩 allowlist 中的迁移、兼容和历史文档。

- [ ] **Step 7: 提交品牌与文档迁移**

  ```bash
  git add README.md README.zh-CN.md CONTRIBUTING.md LICENSE CHANGELOG.md docs distribution shared codex cursor
  git commit -m "docs: establish the Agent Relay v1.5 identity"
  ```

### Task 6: 升级 CI、发行包和版本

**Files:**
- Modify: `distribution/VERSION`
- Modify: `.github/scripts/validate-release.sh`
- Modify: `.github/workflows/ci.yml` only if job labels need the new brand
- Generate locally: `dist/agent-relay-skill-pack-v1.5.0.zip`
- Generate locally: `dist/agent-relay-skill-pack-v1.5.0.zip.sha256`

**Interfaces:**
- Consumes: 全部 v1.5 源码、模板、兼容壳和测试。
- Produces: 可发布的 v1.5.0 安装包和防漂移 CI。

- [ ] **Step 1: 版本升级到 `1.5.0`**

  更新 `distribution/VERSION` 和 Changelog v1.5.0，记录 Agent Relay 重命名、Knowledge Index、clone 恢复测试和兼容周期。

- [ ] **Step 2: 重写发行包名和根目录**

  发行脚本生成 `agent-relay-skill-pack-v1.5.0.zip`，ZIP 内根目录为 `agent-relay-skill-pack/`，包含 `shared/`、`codex/`、`cursor/`、`compat/` 和安装文件。

- [ ] **Step 3: 新增事实源和镜像一致性校验**

  CI 对 `SKILL.md`、helper、Knowledge Index、中英 overlay、嵌套 bootstrap Skill 使用 `cmp`；校验兼容壳不含其他资产；校验 ZIP 无 `._*`、`.DS_Store`、示例活动任务或旧完整 Skill 副本。

- [ ] **Step 4: 执行完整发行验证**

  ```bash
  COPYFILE_DISABLE=1 bash .github/scripts/validate-release.sh
  git diff --check
  unzip -tqq dist/agent-relay-skill-pack-v1.5.0.zip
  shasum -a 256 -c dist/agent-relay-skill-pack-v1.5.0.zip.sha256
  ```

- [ ] **Step 5: 提交发行源码**

  ```bash
  git add distribution .github CHANGELOG.md
  git commit -m "release: prepare Agent Relay v1.5.0"
  ```

  `dist/` 保持 Git ignored，只作本地验证和后续 GitHub Release 附件。

### Task 7: 迁移当前 Codex 安装并做新会话验证

**Files:**
- Install: `/Users/mj/.codex/skills/agent-relay/**`
- Replace with shim: `/Users/mj/.codex/skills/project-role-workflow/SKILL.md`
- Backup: `/Users/mj/.codex/skill-backups/project-role-workflow-v1.4.0/`

**Interfaces:**
- Consumes: 已通过发行验证的源 Skill 和兼容壳。
- Produces: 可使用 `$agent-relay` 的本机 Codex 安装，以及一个可恢复的 v1.4 备份。

- [ ] **Step 1: 确认旧安装未漂移**

  用 `diff -qr --exclude='._*'` 比较当前安装与 v1.4 Git 源。如有用户本地改动，停止覆盖并报告差异。

- [ ] **Step 2: 做可恢复备份**

  将旧完整 Skill 备份到 `/Users/mj/.codex/skill-backups/project-role-workflow-v1.4.0/`，不把备份放在 Skill 自动发现目录中。

- [ ] **Step 3: 安装新 Skill 并替换旧目录**

  将源 `shared/.agents/skills/agent-relay/` 安装到 `/Users/mj/.codex/skills/agent-relay/`，完整比对后，将旧 `/Users/mj/.codex/skills/project-role-workflow/` 替换为仅含兼容 `SKILL.md` 的薄壳。

- [ ] **Step 4: 验证新旧调用**

  在临时仓库中用新会话调用 `$agent-relay continue`，确认它自动读取 `PROJECT_STATUS.md`、Knowledge Index 和当前 `STATE.md`。再调用一次旧命令，确认只产生弃用提示并路由到新 Skill，不使用旧资产。

- [ ] **Step 5: 最终发行门禁**

  ```bash
  diff -qr --exclude='._*' shared/.agents/skills/agent-relay /Users/mj/.codex/skills/agent-relay
  python3 -m unittest discover -s tests -p 'test_*.py' -v
  COPYFILE_DISABLE=1 bash .github/scripts/validate-release.sh
  git diff --check
  git status --short --branch
  ```

  只有当源码、嵌套模板、安装 Skill、clone 恢复和发行包全部通过时，才报告 v1.5.0 完成。

## Acceptance Criteria

- `$agent-relay` 是唯一公开主命令，新项目 Skill 路径是 `.agents/skills/agent-relay/`。
- 完整旧 Skill 不再存在于源 `shared/` 和新 bootstrap 模板；v1.5 仅保留薄兼容壳。
- 旧锁不会被新 helper 忽略，新锁使用 `agent-relay.lock`。
- `knowledge-index.md` 在中英文初始化中都存在，且只索引有证据的长期知识。
- 全新本地 clone 能恢复活动任务、当前参与者、上一交接、决策和 Knowledge Index，不依赖原路径或对话。
- clone 测试明确证明未提交文件不会自动迁移。
- README 和设计文档将 Relay 定义为仓库状态接力协议，同时保留非调度器、非网络同步、非分布式锁的边界。
- `agent-relay-skill-pack-v1.5.0.zip` 可解压、校验和安装，不含 macOS 元数据或重复完整 Skill。
- 本机 Codex 新 Skill 与源完全一致，旧 Skill 已备份并缩减为兼容壳。
