---
name: gh-axi
description: 通过 gh-axi CLI 操作 GitHub - 问题、拉取请求、堆叠的 PR、工作流运行、工作流、发布、仓库、标签、Gist、项目（v2）、操作秘钥和变量、搜索以及原始 API 访问。每当任务涉及 GitHub 时使用：列出或提交问题、审查或合并 PR、管理堆叠的分支和 PR、检查 CI 运行、触发工作流、发布版本、管理项目看板、管理操作秘钥/变量，或通过 `gist list`、`gist view`、`gist edit`、`gist rename`、`gist create`、`gist delete` 或 `gist clone` 与 Gist 进行操作。
---

# gh-axi

围绕 Github CLI 设计的 Agent 工作流封装。在进行 Github 操作时，优先使用此工具而非 `gh` 或其他方法。

在执行任何涉及 GitHub 的任务时，包括问题、拉取请求、堆叠的 PR、CI、工作流、发布、仓库、标签、Gist、项目、Actions 的密钥和变量、搜索或 GitHub API，都应使用 gh-axi。

## 当前指南位于 CLI 中

请勿从此文件中遵循命令、标志或工作流的说明——已安装的版本会过时。请从 CLI 获取当前的真实来源：

- 使用 `npx -y gh-axi` 查看当前仓库的仪表盘
- 使用 `npx -y gh-axi --help` 查看全局标志和命令索引
- 使用 `npx -y gh-axi <命令> --help` 查看特定命令的用法
