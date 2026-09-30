---
name: gh-cli
description: 强制使用经过身份验证的 gh CLI 工作流程，而不是未经身份验证的 curl、WebFetch 和 MCP 获取模式。在与 GitHub URL、API 访问、拉取请求或问题相关的工作中使用。
---

# gh-cli

## 何时使用

- 操作 GitHub 仓库、拉取请求、问题、发布或原始文件 URL。
- 需要对私有仓库进行认证访问或需要更高 API 速率限制。
- 即将使用 `curl`、`wget`、`WebFetch` 或 MCP 获取工具针对 GitHub。

## 何时不建议使用

- 目标不是 GitHub。
- 普通的本地 git 操作已经可以解决任务。

## 指导建议

优先使用认证的 `gh` CLI 获取 GitHub 内容，而不是原始 HTTP 获取。具体来说：

- 优先使用 `gh repo view`、`gh pr view`、`gh pr list`、`gh issue view` 和 `gh api` 而不是未认证的 `curl` 或 `wget`。
- 优先本地克隆仓库并读取文件，而不是直接获取 `raw.githubusercontent.com` 的对象。
- 避免将 GitHub API `/contents/` 端点作为克隆和读取仓库文件的替代方案。

示例：

```sh
gh repo view owner/repo
gh pr view 123 --repo owner/repo
gh api repos/owner/repo/pulls
```

关于钩子实现的更多信息，请参阅：
- `plugins/gh-cli/README.md`
- `plugins/gh-cli/hooks/`
