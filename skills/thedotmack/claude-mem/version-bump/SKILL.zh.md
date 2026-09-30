---
name: version-bump
description: Claude 代码插件的自动化语义版本控制和发布工作流。处理 package.json、marketplace.json、plugin.json 配置文件中的版本增量、构建验证、git 标签、GitHub 发布以及版本变更日志生成。由于维护者提出了 npm 安全性问题，npm 发布是最终需要人工介入的交接环节。
---

# 版本更新与发布流程

**重要提示：** 在开始前，请制定详细计划并编写发布说明。

**关键要求：** 提交所有内容（包括构建产物）。在此流程结束时，不应有任何未提交或未推送的内容。流程结束后运行 `git status` 进行验证。

## 准备工作

1.  **分析**：确定变更类型为 **PATCH**（修复错误）、**MINOR**（新功能）还是 **MAJOR**（破坏性变更）。
2.  **环境**：从 `git remote -v` 识别存储库所有者/名称。
3.  **路径 — 所有包含版本字符串的文件**：
    - `package.json` — **npm/npx 发布的版本**（`npx claude-mem@X.Y.Z` 从此解析）
    - `plugin/package.json` — 打包插件运行时依赖
    - `.claude-plugin/marketplace.json` — `plugins[0].version` 内的版本
    - `.claude-plugin/plugin.json` — 顶层 Claude 插件清单
    - `plugin/.claude-plugin/plugin.json` — 打包的 Claude 插件清单
    - `.codex-plugin/plugin.json` — Codex 插件清单
    - `plugin/.codex-plugin/plugin.json` — 打包的 Codex 插件清单
    - `openclaw/openclaw.plugin.json` — OpenClaw 插件清单

    编辑前验证覆盖范围：`git grep -l "\"version\": \"<OLD>\""` 应列出所有八个文件。如果自本文档上次更新以来已添加新的清单，请更新此列表。

## 流程

1.  **更新**：在上述所有路径中递增版本字符串。不要触碰 `CHANGELOG.md` — 它将被重新生成。
2.  **验证**：`git grep -n "\"version\": \"<NEW>\""` — 确认所有八个文件匹配。`git grep -n "\"version\": \"<OLD>\""` — 应返回零条匹配。
3.  **构建和同步**：`npm run build-and-sync` 重新生成产物，同步本地市场副本，重启工作进程，并清空队列。不要使用普通的 `npm run build` 进行发布验证，因为它可能使本地市场/工作进程不同步。
4.  **提交**：`git add -A && git commit -m "chore: 将版本提升至 X.Y.Z"`。
5.  **打标签**：`git tag -a vX.Y.Z -m "版本 X.Y.Z"`。
6.  **推送**：`git push origin main && git push origin vX.Y.Z`。
7.  **GitHub 发布**：`gh release create vX.Y.Z --title "vX.Y.Z" --notes "RELEASE_NOTES"`。
8.  **发布说明**：通过项目的发布说明脚本重新生成：
    ```bash
    npm run changelog:generate
    ```
    （运行 `node scripts/generate-changelog.js`，该脚本从 GitHub API 拉取发布信息并重写 `CHANGELOG.md`。）
9.  **同步发布说明**：提交并推送更新的 `CHANGELOG.md`。
10. **发布前审计**：验证发布提交、标签、GitHub 发布和发布说明都已推送；确认发布工作树没有待处理的跟踪变更；并确保其构建依赖存在，因为 `prepublishOnly` 会重新构建包。如果 `npm view claude-mem@X.Y.Z version` 已解析，则跳过交接并继续执行发布后检查。
11. **最终人工交接 — 发布到 npm。** 不要在 npm 流程中途停止。首先完成所有代理拥有的准备工作，然后将其作为最终需要人工执行的操作。

    需要人工维护者的凭证/双因素认证。代理绝对不能运行 `npm publish`（或 `np` / `npm run release:*`，这些也会发布）。给出精确的发布工作树路径和此命令作为唯一请求的操作：
    ```bash
    npm publish   # 由人工执行 — prepublishOnly 会重新构建包
    ```
    等待确认。不要要求人工执行任何其他发布步骤。
12. **发布后验证和通知**：确认后，验证确切版本和最新 dist-tag：
    ```bash
    npm view claude-mem@X.Y.Z version
    npm view claude-mem version
    ```
    如果发布构建触发了跟踪的产物，运行 `npm run build-and-sync`，审查结果，并提交/推送任何合法变更。然后从 `~/Scripts/claude-mem/` 运行 Discord 通知（`.env` 包含 webhook 详细信息）：
    ```bash
    cd ~/Scripts/claude-mem/ && npm run discord:notify vX.Y.Z
    ```
    仅在 npm 验证后执行此操作，即使发布工作树没有本地 `.env`。
13. **最终完成**：`git status` — 工作区必须干净且所有内容都已推送。最终人工交接后，仅允许自动验证、通知和清理操作。

## 检查清单

- [ ] 所有八个配置文件版本匹配
- [ ] `git grep` 老版本返回零条匹配
- [ ] `npm run build-and-sync` 成功
- [ ] Git 标签创建并推送
- [ ] GitHub 发布创建并包含说明
- [ ] `CHANGELOG.md` 更新并推送
- [ ] 发布前审计通过；没有剩余的代理拥有的发布准备工作
- [ ] **NPM 发布作为最终需要人工执行的操作交接**（代理不执行）
- [ ] 确认人工发布后的确切 npm 版本和 `latest`
- [ ] 仅在 npm 验证后从 `~/Scripts/claude-mem/` 运行 Discord 通知
- [ ] `git status` 显示干净的工作区
