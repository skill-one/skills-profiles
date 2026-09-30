---
name: agentmail-cli
description: 使用官方 CLI 从 Shell 操作 AgentMail。当用户需要用于列出或创建收件箱、阅读或搜索邮件、发送或回复、管理草稿或脚本 JSON/YAML 输出等命令时使用；不应用于 SDK 代码、MCP 设置或框架适配器。
---

# AgentMail CLI

通过环境变量安装 CLI 并提供 API 密钥。

```bash
npm install -g agentmail-cli
export AGENTMAIL_API_KEY="am_..."
```

嵌套在另一个资源下的子命令使用冒号，例如 `inboxes:messages`、`inboxes:threads`、`pods:inboxes`、`pods:threads`。

## 收件箱

```bash
agentmail inboxes list
agentmail inboxes get --inbox-id <inbox_id>
agentmail inboxes create --display-name "支持代理" --username support
agentmail inboxes delete --inbox-id <inbox_id>
```

在运行具有破坏性的删除命令前，请确认收件箱的准确性。

## 消息和线程

```bash
agentmail inboxes:messages list --inbox-id <inbox_id>
agentmail inboxes:messages get --inbox-id <inbox_id> --message-id <message_id>

agentmail inboxes:messages send --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "你好" \
  --text "消息正文"

# 使用 HTML 正文而不是纯文本
agentmail inboxes:messages send --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "你好" \
  --html "<h1>你好</h1>"

agentmail inboxes:messages reply --inbox-id <inbox_id> \
  --message-id <message_id> \
  --text "回复正文"

agentmail inboxes:messages forward --inbox-id <inbox-id> \
  --message-id <message_id> \
  --to "someone@example.com"

agentmail inboxes:threads list --inbox-id <inbox_id>
agentmail inboxes:threads get --inbox-id <inbox_id> --thread-id <thread_id>
```

使用消息 ID 进行回复。在依赖正文内容前，先获取完整消息。

## 草稿

```bash
agentmail inboxes:drafts create --inbox-id <inbox_id> \
  --to "recipient@example.com" \
  --subject "待审批" \
  --text "草稿正文"

agentmail inboxes:drafts list --inbox-id <inbox_id>
agentmail inboxes:drafts get --inbox-id <inbox_id> --draft-id <draft_id>
agentmail inboxes:drafts send --inbox-id <inbox_id> --draft-id <draft_id>
```

## Pods

Pods 将收件箱分组在一起。

```bash
agentmail pods create --name "我的 Pod"
agentmail pods list

agentmail pods:inboxes create --pod-id <pod_id> --display-name "Pod 收件箱"
agentmail pods:inboxes list --pod-id <pod_id>

agentmail pods:threads list --pod-id <pod_id>
agentmail pods:threads get --pod-id <pod_id> --thread-id <thread_id>
```

## Webhooks

```bash
agentmail webhooks create --url "https://example.com/webhook" --event-type message.received
agentmail webhooks list
```

## 域名

```bash
agentmail domains create --domain example.com

# 可选：将退回/投诉通知路由到您的收件箱。
agentmail domains create --domain example.com --feedback-enabled

agentmail domains verify --domain-id <domain_id>
agentmail domains get-zone-file --domain-id <domain_id>
```

## 全局标志

| 标志 | 目的 |
| --- | --- |
| `--api-key` | 覆盖本次调用的 `AGENTMAIL_API_KEY` |
| `--base-url` | 指向非默认 API 主机 |
| `--environment` | 选择命名环境 |
| `--format` | 输出格式（见下文） |
| `--format-error` | 控制结构化错误输出 |
| `--transform` | 成功响应的 GJSON 投影 |
| `--transform-error` | 错误响应的 GJSON 投影 |
| `--debug` | 详细请求/响应日志 |

## 输出格式

`--format` 接受：`auto`（默认）、`pretty`、`json`、`jsonl`、`yaml`、`raw`、`explore`。

在使用未在此涵盖的行政命令前，请运行 `agentmail --help` 和相关资源的 `--help`。
