# Pull Request 创建者

此技能指导您创建符合仓库标准的优质 Pull Request。

## 工作流程

按照以下步骤创建 Pull Request：

1.  **分支管理**：**关键**：确保您**不**在 `main` 分支上工作。
    - 运行 `git branch --show-current`。
    - 如果当前分支是 `main`，您**必须**创建并切换到一个描述性的新分支：
      ```bash
      git checkout -b <new-branch-name>
      ```

2.  **提交变更**：验证所有预期变更都已提交。
    - 运行 `git status` 检查未暂存或未提交的变更。
    - 如果存在未提交的变更，请在继续之前暂存并提交它们，附带描述性信息。**永远不要直接提交到 `main`**。
      ```bash
      git add .
      git commit -m "type(scope): description"
      ```

3.  **定位模板**：在仓库中搜索 Pull Request 模板。
    - 检查 `.github/pull_request_template.md`
    - 检查 `.github/PULL_REQUEST_TEMPLATE.md`
    - 如果存在多个模板（例如，在 `.github/PULL_REQUEST_TEMPLATE/` 中），请询问用户使用哪个模板，或根据上下文选择最合适的模板（例如，`bug_fix.md` 与 `feature.md`）。

4.  **阅读模板**：阅读已识别的模板文件的内容。

5.  **草拟描述**：创建一个严格遵循模板结构的 PR 描述。
    - **标题**：保留模板中的所有标题。
    - **清单**：检查每个项目。如果已完成，用 `[x]` 标记。如果某个项目不适用，保持未选中或根据模板说明标记为 `[ ]`，或者如果模板允许灵活性，则删除它（但优先选择保持未选中以提高透明度）。
    - **内容**：用清晰简洁的摘要填写各个部分。
    - **相关问题**：链接与此 PR 修复或相关的问题（例如，“Fixes #123”）。

6.  **预检**：在创建 PR 之前，运行工作区预检脚本以确保所有构建、代码检查和测试检查都通过。
    ```bash
    npm run preflight
    ```
    如果任何检查失败，请在继续创建 PR 之前解决这些问题。

7.  **推送分支**：将当前分支推送到远程仓库。
    **关键安全措施**：推送前再次检查您的分支名称。**永远不要**在当前分支是 `main` 时推送。
    ```bash
    # 验证当前分支不是 main
    git branch --show-current
    # 非交互式推送
    git push -u origin HEAD
    ```

8.  **创建 PR**：使用 `gh` CLI 创建 PR。为了避免多行 Markdown 导致的 shell 转义问题，请先将描述写入临时文件。
    ```bash
    # 1. 将草拟的描述写入临时文件
    # 2. 使用 --body-file 标志创建 PR
    gh pr create --title "type(scope): 简洁描述" --body-file <temp_file_path>
    # 3. 删除临时文件
    rm <temp_file_path>
    ```
    - **标题**：如果仓库使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式，请确保标题遵循该格式（例如，`feat(ui): 添加新按钮`，`fix(core): 解决崩溃`）。

## 原则

- **安全第一**：**永远不要**推送至 `main`。这是您的最高优先级。
- **合规性**：**永远不要**忽略 PR 模板。它存在是有原因的。
- **完整性**：填写所有相关部分。
- **准确性**：不要勾选您未完成任务的方框。
