# Agent Email CLI

## 概述

使用此技能安全、可预测地操作 `agent-email` 命令，用于需要收件箱访问的代理工作流。

优先使用 JSON 原生命令输出，并在摘要中返回关键字段（`email`、`messageId`、`subject`、`createdAt`、`from.address`）。

## 工作流

1. 验证 CLI 是否可用。

```bash
command -v agent-email
agent-email --help
```

如果缺失，则安装：

```bash
npm install -g @zaddy6/agentemail
# 或
bun install -g @zaddy6/agentemail
```

2. 创建邮箱账户。

```bash
agent-email create
```

从 JSON 输出中记录以下字段：

- `data.email`
- `data.accountId`
- `data.activeEmail`

不要记录、重复或打印邮箱密码或令牌等秘密值。

3. 读取最新消息。

```bash
agent-email read <email|default>
```

用于收件箱等待/轮询：

```bash
agent-email read <email|default> --wait 30 --interval 2
```

用于完整消息负载：

```bash
agent-email read <email|default> --full
```

4. 详细检索一条消息。

```bash
agent-email show <email|default> <messageId>
```

当需要验证链接、代码或完整内容提取的正文/源详情时，使用 `show`。

5. 管理邮箱配置文件。

```bash
agent-email accounts list
agent-email use <email|default>
agent-email accounts remove <email>
```

避免在代理日志中输入需要输入秘密值的命令。

6. 在需要时删除已处理/无关的消息。

```bash
agent-email delete <email|default> <messageId>
```

## 运行指导

- 保持命令输出机器可读；除非被要求，否则避免强制人类输出。
- 当用户未指定邮箱时，优先使用 `default` 别名。
- 从命令输出中永远不要回显、存储或总结秘密值（`password`、`token`）。
- 如果命令失败，直接显示 JSON 错误 `code` 和 `hint` 字段。
- 对于认证失败（`AUTH_REQUIRED`/401），如果需要重新建立凭证，则重新运行命令并请求用户干预。
- 对于速率限制（`RATE_LIMITED`/429），稍作延迟后重试。

## 故障排除

- `command not found`：确保 `~/.bun/bin` 或 npm 全局 bin 路径在 `PATH` 中。
- `NO_ACTIVE_ACCOUNT`：运行 `agent-email create` 或 `agent-email use <email>`。
- `ACCOUNT_NOT_FOUND`：运行 `agent-email accounts list` 并选择一个有效地址。
- 在 npm 发布期间出现 `EOTP`：使用 npm 受信任发布用于 CI 或使用 OTP 本地发布。

## 参考

- 对于命令速查表和 JSON 字段映射，请阅读 [references/commands.md](references/commands.md)。
