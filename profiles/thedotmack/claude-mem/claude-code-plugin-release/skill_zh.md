# 版本更新与发布流程

**重要提示：** 在开始之前，请制定详细发布说明并撰写。

**关键提示：** 提交所有内容（包括构建产物）。在此流程结束时，不应有任何未提交或未推送的内容。流程结束后运行 `git status` 进行验证。

## 准备工作

1.  **分析**：确定变更类型是 **PATCH**（修复错误）、**MINOR**（功能）还是 **MAJOR**（破坏性变更）。
2.  **环境**：从 `git remote -v` 中识别存储库所有者/名称。
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
7.  **发布到 npm — 交由人工处理。** 由于人工维护者提出了 npm 安全问题，因此现在发布需要他们才能提供的凭证/双因素认证。代理绝对不能自行运行 `npm publish`（或 `np` / `npm run release:*`，这些也会发布）。**现在将 npm 发布交由人工处理**：停止并告知他们版本已提交、打标签并推送，他们必须发布到 npm 以使 `npx claude-mem@X.Y.Z` 解析。给他们命令：
    ```bash
    npm publish   # 由人工运行 — prepublishOnly 脚本会重新构建包
    ```
    等待人工确认他们已发布，然后验证是否已发布：
    ```bash
    npm view claude-mem@X.Y.Z version   # 应打印 X.Y.Z
    ```
    如果发布构建修改了本地产物，之后再次运行 `npm run build-and-sync`。
8.  **GitHub 发布**：`gh release create vX.Y.Z --title "vX.Y.Z" --notes "RELEASE_NOTES"`。
9.  **变更日志**：通过项目的变更日志脚本重新生成：
    ```bash
    npm run changelog:generate
    ```
    （运行 `node scripts/generate-changelog.js`，该脚本从 GitHub API 拉取发布并重写 `CHANGELOG.md`。）
10. **同步变更日志**：提交并推送更新的 `CHANGELOG.md`。
11. **通知**：从 `~/Scripts/claude-mem/` 运行 Discord 通知，其中包含 Discord webhook 详细信息的 `.env` 文件：
    ```bash
    cd ~/Scripts/claude-mem/ && npm run discord:notify vX.Y.Z
    ```
    即使发布工作树没有本地 `.env`，也请执行此操作。
12. **完成**：`git status` — 工作树必须干净。

## 检查清单

- [ ] 所有八个配置文件版本匹配
- [ ] `git grep` 搜索旧版本返回零条匹配
- [ ] `npm run build-and-sync` 成功
- [ ] Git 标签创建并推送
- [ ] **NPM 发布交由人工处理**（代理不运行 `npm publish` — 人工提出了安全问题）；一旦他们发布，`npm view claude-mem@X.Y.Z version` 确认已发布（以便 `npx claude-mem@X.Y.Z` 解析）
- [ ] GitHub 发布创建并包含说明
- [ ] `CHANGELOG.md` 更新并推送
- [ ] 从 `~/Scripts/claude-mem/` 运行 Discord 通知
- [ ] `git status` 显示干净的工作树
