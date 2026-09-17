# 给安装智能体的提示词

请把这个压缩包中的 Project Role Workflow 安装到当前项目，并遵守以下要求：

1. 先只读检查项目根目录、现有 `AGENTS.md`、`.agents/`、`.cursor/`、`.claude/` 和 `docs/agent/`；不要假设它们为空。
2. 阅读安装包内的 `INSTALL.md`、核心 `SKILL.md` 和 `references/protocol.md`。
3. 把共享 Skill（包括 `scripts/workflow_state.py`）安装到项目根 `.agents/skills/project-role-workflow/`，把共享状态模板安装到 `docs/agent/`。如果宿主策略禁止写入 `.agents/`，继续使用已加载的全局 Skill 和 `docs/agent/protocol.md`，并报告项目级 Skill 为 pending；不要把它当作安装失败。
4. 根据你实际使用的工具安装对应入口。已有同名文件时逐段合并，保留项目原有构建、测试、安全规则和现有协作记录；禁止整目录覆盖。
5. 如果目标项目已经有运行中的任务、参与者、角色绑定或状态文件，不要用模板重置。只补缺失结构，并报告冲突。
6. 清除 macOS AppleDouble 文件（文件名以 `._` 开头），不要把它们安装进项目；不要安装或复制 `.learnings/`、`dist/` 等本地生成目录。
7. 安装后检查 Markdown 本地链接、Skill frontmatter，并在 Python 3 可用时运行 `workflow_state.py --repo <target> status`；再启动或指导用户启动一个全新会话，只输入“继续”进行真实入口验证。
8. 最终报告：安装了哪些文件、合并了哪些既有规则、保留了哪些项目状态、哪些工具入口已验证、哪些仍待验证。

初始化新仓库时必须先让用户选择中文（`zh-CN`）或 English（`en-US`），再询问角色工具。后续交流和新建任务文档使用该语言。Implementer 实施前必须让用户选择 `USE` 或 `DO_NOT_USE` 子代理。

安装不授权修改产品代码，也不授权切换活动任务、接管写入会话、合并、发布、部署、删除或回滚。

如果用户要求安装为个人或全局 Skill，则把 `shared/.agents/skills/project-role-workflow/` 安装到当前工具的个人 Skills 目录。安装完成后，在空白仓库中调用 `$project-role-workflow 初始化当前仓库` 或 `$project-role-workflow initialize this repository` 即可自举项目文件。
