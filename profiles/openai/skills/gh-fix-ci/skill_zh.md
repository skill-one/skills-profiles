# Gh Pr Checks Plan Fix

## 概述

使用 gh 定位失败的 PR 检查，获取 GitHub Actions 日志以查找可操作的失败记录，总结失败片段，然后提出修复计划并在明确批准后实施。
- 如果有面向计划的技能（例如 `create-plan`），则使用它；否则，内联起草简洁的计划并请求批准后再实施。

前提条件：使用标准 GitHub CLI 进行一次身份验证（例如，运行 `gh auth login`），然后使用 `gh auth status` 进行确认（通常需要仓库 + 工作流范围）。

## 输入

- `repo`: 仓库内的路径（默认 `.`）
- `pr`: PR 编号或 URL（可选；默认为当前分支的 PR）
- `gh` 对仓库主机的身份验证

## 快速入门

- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
- 如果需要机器友好的输出以进行总结，请添加 `--json`。

## 工作流程

1. 验证 gh 身份验证。
   - 在仓库中运行 `gh auth status`。
   - 如果未通过身份验证，请要求用户在继续之前运行 `gh auth login`（确保包含仓库 + 工作流范围）。
2. 解析 PR。
   - 优先使用当前分支的 PR：`gh pr view --json number,url`。
   - 如果用户提供了 PR 编号或 URL，则直接使用该值。
3. 检查失败的检查（仅限 GitHub Actions）。
   - 推荐方法：运行捆绑脚本（处理 gh 字段漂移和工作日志回退）：
     - `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
     - 添加 `--json` 以获取机器友好的输出。
   - 手动回退：
     - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
       - 如果某个字段被拒绝，请使用 `gh` 报告的可用字段重新运行。
     - 对于每个失败的检查，从 `detailsUrl` 中提取运行 ID 并运行：
       - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
       - `gh run view <run_id> --log`
     - 如果运行日志显示仍在进行中，请直接获取作业日志：
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`
4. 限定非 GitHub Actions 检查。
   - 如果 `detailsUrl` 不是 GitHub Actions 运行，则将其标记为外部，并仅报告 URL。
   - 不要尝试 Buildkite 或其他提供者；保持工作流简洁。
5. 为用户总结失败。
   - 提供失败的检查名称、运行 URL（如果有）和简洁的日志片段。
   - 明确指出缺失的日志。
6. 创建计划。
   - 使用 `create-plan` 技能起草简洁的计划并请求批准。
7. 批准后实施。
   - 应用批准的计划，总结差异/测试，并询问是否打开 PR。
8. 重新检查状态。
   - 更改后，建议重新运行相关测试和 `gh pr checks` 以确认。

## 捆绑资源

### scripts/inspect_pr_checks.py

获取失败的 PR 检查，拉取 GitHub Actions 日志并提取失败片段。当存在失败时退出非零，以便可用于自动化。

使用示例：
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40`
