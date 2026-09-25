# 从规范创建 GitHub Pull Request

为位于 `${workspaceFolder}/.github/pull_request_template.md` 的规范创建 GitHub Pull Request。

## 流程

1. 使用 'search' 工具分析 '${workspaceFolder}/.github/pull_request_template.md' 中的规范文件模板，提取需求。
2. 使用 'create_pull_request' 工具在 `${input:targetBranch}` 上创建 Pull Request 草稿模板，并确保当前分支不存在任何 Pull Request（使用 `get_pull_request` 工具检查）。如果存在，则继续步骤 4，跳过步骤 3。
3. 使用 'get_pull_request_diff' 工具获取 Pull Request 中的变更，分析 Pull Request 中已更改的信息。
4. 使用 'update_pull_request' 工具更新上一步创建的 Pull Request 正文和标题。将第一步获得的模板信息整合到正文中，按需更新标题和正文。
5. 使用 'update_pull_request' 工具将 Pull Request 从草稿状态切换为待审核状态，更新 Pull Request 状态。
6. 使用 'get_me' 工具获取创建 Pull Request 的用户名，并将其分配给 `update_issue` 工具，以分配 Pull Request。
7. 向用户响应创建 Pull Request 的 URL。

## 要求
- 完整规范使用单个 Pull Request
- Pull Request 标题（`pull_request_template.md`）清晰标识规范
- 在 `pull_request_template.md` 中填写足够的信息
- 创建前验证现有 Pull Request
