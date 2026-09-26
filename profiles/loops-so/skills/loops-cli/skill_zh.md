# Loops CLI 工具

该工具用于辅助 Loops 终端工作流程。可用于安装、认证和配置、命令选择以及 shell 优先的操作任务。

## 使用场景

当用户需要执行以下操作时，请使用此工具：

- 安装、更新或排错 Loops CLI
- 从终端进行 Loops 认证
- 管理存储的团队密钥或在不同密钥间切换
- 运行一次性联系人、列表、事件或交易邮件命令
- 从 shell 创建草稿活动、更新邮件内容并上传图片
- 列出/获取 LMX 主题和可重用组件
- 本地检查 CLI 的文本或 JSON 输出

此工具适用于命令行使用，不适用于应用集成或邮件策略审查。

## 工作方式

当此工具处于激活状态时：

1. 优先使用 `loops agent-context` 获取精确的标志和最新的命令结构。
2. 优先使用 CLI 执行 shell 工作流、一次性操作任务、凭证验证和快速排错。
3. 当结果需要用于其他工具或脚本时，使用 `--output json`。
4. 当用户在多个 Loops 团队间工作时，使用命名的存储密钥加上 `--team`。
5. 避免打印密钥。优先使用密钥环认证或环境变量，而非硬编码的 API 密钥。
6. 如果任务变为应用代码集成或精确的 HTTP 负载设计，请使用单独的 `loops-api` 工具。

官方参考资料：

- CLI 文档：`https://loops.so/docs/cli`
- CLI 仓库：`https://github.com/loops-so/cli`
- CLI README：`https://github.com/loops-so/cli/blob/main/README.md`

## 类别路由

- 安装、认证流程、配置解析、全局标志和常见的 Loops CLI 工作流：
  阅读 `references/cli.md`
- 活动、邮件消息、主题、组件、修订处理、LMX 文件标志和上传：
  阅读 `references/cli.md`。对于 LMX 标记本身，也使用 `loops-lmx` 工具。

如果任务超出 CLI 范围，变为应用代码集成或精确的 HTTP 负载设计，请使用 `loops-api` 工具。

## 输出检查清单

目标是让用户获得：

- 执行任务的正确命令或安装路径
- 任何影响行为的认证或团队选择注意事项
- 凭证的安全处理
- 下一步验证步骤，例如 `loops --help`、`loops auth status`、`loops api-key` 或 `loops agent-context`
