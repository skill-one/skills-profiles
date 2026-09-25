# Sentry (只读可观察性)

## 快速入门

- 如果尚未认证，请提示用户运行 `sentry auth login` 或将 `SENTRY_AUTH_TOKEN` 设置为环境变量。
- CLI 会自动从 `.env` 文件、源代码、配置默认值和目录名称中检测 org/project。如果自动检测失败或选择了错误的目标，请指定 `<org>/<project>`。
- 默认值：时间范围 `24h`，环境 `production`，限制 20。
- 处理程序输出时始终使用 `--json`。使用 `--json --fields` 选择特定字段以减少输出大小。
- 使用 `sentry schema <resource>` 快速发现 API 端点。

如果未安装 CLI，请向用户提供以下步骤：
1. 安装 Sentry CLI：`curl https://cli.sentry.dev/install -fsS | bash`
2. 认证：`sentry auth login`
3. 确认认证：`sentry auth status`
- 不要要求用户在聊天中粘贴完整令牌。请指示他们本地设置并确认准备就绪。

## 核心任务（使用 Sentry CLI）

使用 `sentry` CLI 进行所有查询。它自动处理认证、org/project 检测、分页和重试。使用 `--json` 获取机器可读输出。

### 1) 列出问题（按最新顺序排序）

```bash
sentry issue list \
  --query "is:unresolved environment:production" \
  --period 24h \
  --limit 20 \
  --json --fields shortId,title,priority,level,status
```

如果自动检测无法解析 org/project，请显式传递它们：
```bash
sentry issue list {your-org}/{your-project} \
  --query "is:unresolved environment:production" \
  --period 24h \
  --limit 20 \
  --json
```

### 2) 通过短 ID 解析问题详情

```bash
sentry issue view {ABC-123} --json
```

使用短 ID 格式（例如 `ABC-123`），而不是数字 ID。

### 3) 问题详情

```bash
sentry issue view {ABC-123}
```

### 4) 问题事件

```bash
sentry issue events {ABC-123} --limit 20 --json
```

### 5) 事件详情

```bash
sentry event view {your-org}/{your-project}/{event_id} --json
```

### 6) AI 驱动的根本原因分析

```bash
sentry issue explain {ABC-123}
```

### 7) AI 驱动的修复计划

```bash
sentry issue plan {ABC-123}
```

## 备用方案：任意 API 访问

对于 CLI 命令未涵盖的端点，使用 `sentry api`：
```bash
sentry api /api/0/organizations/{your-org}/ --method GET
```

使用 `sentry schema` 发现可用的 API 端点：
```bash
sentry schema issues
```

## 输入和默认值

- `org_slug`, `project_slug`：CLI 从 DSN、环境变量和目录名称自动检测。如果自动检测失败，请使用位置参数 `{your-org}/{your-project}` 覆盖。
- `time_range`：默认 `24h`（作为 `--period 24h` 传递）。
- `environment`：默认 `prod`（作为 `--query` 的一部分传递，例如 `environment:production`）。
- `limit`：默认 20（作为 `--limit` 传递）。
- `search_query`：可选的 `--query` 参数，使用 Sentry 搜索语法（例如 `is:unresolved`，`assigned:me`）。
- `issue_short_id`：直接与 `sentry issue view` 一起使用。

## 输出格式规则

- 问题列表：显示标题、short_id、状态、首次出现、最后出现、计数、环境、顶级标签；按最新顺序排序。
- 事件详情：包括罪魁祸首、时间戳、环境、发布版本、URL。
- 如果没有结果，请明确说明。
- 输出中屏蔽 PII（电子邮件、IP 地址）。不要打印原始堆栈跟踪。
- 不要回显认证令牌。

## 黄金测试输入

- 组织：`{your-org}`
- 项目：`{your-project}`
- 问题短 ID：`{ABC-123}`

示例提示："列出过去 24 小时内 prod 的前 10 个开放问题。"
预期：按最新顺序排列的包含标题、短 ID、计数、最后出现的列表。
