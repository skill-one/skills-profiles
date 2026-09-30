---
name: gh-address-comments
description: 使用 gh CLI 检查当前分支的开放 GitHub PR，并处理其中的审查/问题评论；首先验证 gh auth，如果未登录，则提示用户进行身份验证。
---

# PR 评论处理器

指导如何查找当前分支的开放 PR 并使用 gh CLI 处理其评论。运行所有 `gh` 命令时需使用提升的网络访问权限。

前提条件：确保 `gh` 已通过身份验证（例如，运行一次 `gh auth login`），然后使用提升权限运行 `gh auth status`（包含 workflow/repo 范围），以确保 `gh` 命令成功。如果沙箱环境阻止 `gh auth status` 运行，请使用 `sandbox_permissions=require_escalated` 重新运行。

## 1) 检查需要关注的评论
- 运行脚本 `scripts/fetch_comments.py`，该脚本将打印出 PR 上的所有评论和评审线程。

## 2) 请求用户澄清
- 对所有评审线程和评论进行编号，并提供简要总结，说明需要采取哪些措施才能修复这些问题
- 询问用户应处理哪些编号的评论

## 3) 如果用户选择评论
- 对选定的评论应用修复

注意：
- 如果 gh 在运行中途遇到身份验证/速率限制问题，提示用户使用 `gh auth login` 重新进行身份验证，然后重试。
