开始处理当前仓库中的 Marshroom 购物车问题。

## 关键要求

- **必须更新 state.json**。创建分支后，你必须将问题状态更新为 `running`，路径为 `${MARSHROOM_STATE:-~/.config/marshroom/state.json}`。如果失败，请停止并报告错误——不要默默继续。
- 如果可用，使用 `marsh start`；否则回退到直接 `jq` 原子写入（见步骤 10）。

## 步骤

1. 读取 `${MARSHROOM_STATE:-~/.config/marshroom/state.json}` 并解析 JSON
2. 提取 `cart` 数组。如果购物车为空，告诉用户在 Marshroom 应用中添加问题
3. 运行 `git remote get-url origin` 获取当前仓库的远程 URL
4. 从远程 URL 中提取 `owner/repo`（处理 HTTPS 和 SSH 格式）
5. 过滤购物车条目，其中 `repoCloneURL`（HTTPS）或 `repoSSHURL`（SSH）与当前远程匹配。通过提取每个条目的 `owner/repo` 进行比较
6. 如果没有匹配的购物车条目，告诉用户这个仓库没有购物车问题
7. 如果 `$ARGUMENTS` 包含问题编号，找到该条目；否则如果有多个匹配，列出它们并要求用户选择一个
8. 运行 `git checkout main && git pull origin main` 确保主分支是最新的
9. 创建并切换到分支：`git checkout -b {branchName}` 分支名称应为 `Feature/#N` 或 `HotFix/#N`。`N` 是问题编号。
10. **更新问题状态（必须）**：
    - 首次尝试：`marsh start #{issueNumber}`
    - 如果 PATH 中找不到 `marsh`，回退到直接原子更新：
      ```bash
      STATE_FILE="${MARSHROOM_STATE:-~/.config/marshroom/state.json}"
      TMP="$(mktemp "${STATE_FILE}.XXXXXX")"
      jq --argjson n ISSUE_NUMBER '.cart |= map(if .issueNumber == $n then .status = "running" else . end)' \
        "$STATE_FILE" > "$TMP" && mv -f "$TMP" "$STATE_FILE"
      ```
    - 通过读取 state.json 并确认状态为 `running` 来验证更新是否成功
11. 注入问题上下文：
    - 从匹配的购物车条目中读取 `issueBody` 字段
    - 如果非空，在 "## 问题详情" 标题下显示它
    - 这为代理提供了关于需要做什么的完整上下文
12. 确认分支已创建并显示：
    - 问题：#{issueNumber} {issueTitle}
    - 分支：{branchName}
    - 仓库：{repoFullName}
    - 状态：running
13. 询问用户是否允许开始计划解决该问题。如果用户允许，使用 `/plan` 模式开始计划。
