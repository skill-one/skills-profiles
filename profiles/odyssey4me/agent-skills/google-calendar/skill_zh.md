# Google Calendar

与 Google Calendar 交互，用于事件管理、日程安排和可用性检查。

## 安装

**依赖项**: `pip install --user google-auth google-auth-oauthlib google-api-python-client keyring pyyaml`

## 配置验证

安装后，验证技能是否正确配置：

```bash
$SKILL_DIR/scripts/google-calendar.py check
```

这将检查：
- Python 依赖项（google-auth, google-auth-oauthlib, google-api-python-client, keyring, pyyaml）
- 身份验证配置
- 与 Google Calendar API 的连接

如果缺少任何内容，检查命令将提供配置说明。

## 身份验证

Google Calendar 使用 OAuth 2.0 进行身份验证。完整的配置说明请参阅：

1. [GCP 项目配置指南](https://github.com/odyssey4me/agent-skills/blob/main/docs/gcp-project-setup.md) - 创建项目、启用 Calendar API
2. [Google OAuth 配置指南](https://github.com/odyssey4me/agent-skills/blob/main/docs/google-oauth-setup.md) - 配置凭证

### 快速入门

1. 创建 `~/.config/agent-skills/google.yaml`：
   ```yaml
   oauth_client:
     client_id: your-client-id.apps.googleusercontent.com
     client_secret: your-client-secret
   ```

2. 运行 `$SKILL_DIR/scripts/google-calendar.py check` 以触发 OAuth 流程并验证配置。

在范围或身份验证错误的情况下，请参阅 [OAuth 故障排除指南](https://github.com/odyssey4me/agent-skills/blob/main/docs/google-oauth-setup.md#troubleshooting)。

## 脚本使用

请参阅 [permissions.md](references/permissions.md) 了解每个命令的读写分类。

```bash
# 配置和身份验证
$SKILL_DIR/scripts/google-calendar.py check
$SKILL_DIR/scripts/google-calendar.py auth setup --client-id ID --client-secret SECRET
$SKILL_DIR/scripts/google-calendar.py auth reset
$SKILL_DIR/scripts/google-calendar.py auth status

# 日历
$SKILL_DIR/scripts/google-calendar.py calendars list
$SKILL_DIR/scripts/google-calendar.py calendars get CALENDAR_ID

# 事件
$SKILL_DIR/scripts/google-calendar.py events list
$SKILL_DIR/scripts/google-calendar.py events get EVENT_ID
$SKILL_DIR/scripts/google-calendar.py events create --summary TITLE --start TIME --end TIME
$SKILL_DIR/scripts/google-calendar.py events update EVENT_ID --summary TITLE
$SKILL_DIR/scripts/google-calendar.py events delete EVENT_ID

# 可用性
$SKILL_DIR/scripts/google-calendar.py freebusy --start TIME --end TIME
```

所有命令都支持 `--calendar CALENDAR_ID`（默认："primary"）。时间使用 RFC3339 格式（例如，`2026-01-24T10:00:00Z`）或 `YYYY-MM-DD` 用于全天事件。

请参阅 [command-reference.md](references/command-reference.md) 了解完整的参数细节和示例。

## 示例

### 安排带有与会者的会议

```bash
$SKILL_DIR/scripts/google-calendar.py events create \
  --summary "团队例会" \
  --start "2026-01-25T09:00:00-05:00" \
  --end "2026-01-25T09:30:00-05:00" \
  --location "Zoom" \
  --attendees "team@example.com"
```

### 跨日历查找可用时间

```bash
$SKILL_DIR/scripts/google-calendar.py freebusy \
  --start "2026-01-24T08:00:00-05:00" \
  --end "2026-01-24T17:00:00-05:00" \
  --calendars "primary,colleague@example.com"
```

### 列出本周的事件

```bash
$SKILL_DIR/scripts/google-calendar.py events list \
  --time-min "2026-01-24T00:00:00Z" \
  --time-max "2026-01-31T23:59:59Z"
```

## Agent 指导 — 分页

事件列表会自动通过所有结果进行分页。当指定时间范围时，将返回所有匹配的事件，无论数量如何——结果永远不会被静默截断。

## Agent 指导 — 被拒绝的事件

在列出事件时，被拒绝的会议默认情况下会被排除。脚本输出将指示是否过滤掉了被拒绝的邀请（例如："3 被拒绝的邀请未显示"）。当出现此提示时，告知用户存在被拒绝的邀请，并根据需要提供显示它们的选项。要包括被拒绝的事件，请使用 `--include-declined` 重新运行。

## 错误处理

**身份验证和范围错误是不可重试的。** 如果命令因身份验证错误、权限不足错误或权限被拒绝错误（退出码 1）而失败，**停止并告知用户**。不要重试或尝试自动修复问题——这些错误需要用户交互（基于浏览器的 OAuth 同意）。将用户指向 [OAuth 故障排除指南](https://github.com/odyssey4me/agent-skills/blob/main/docs/google-oauth-setup.md#troubleshooting)。

**可重试的错误**：速率限制（HTTP 429）和临时服务器错误（HTTP 5xx）在短暂等待后重试可能会成功。所有其他错误应报告给用户。

## 模型指导

此技能需要结构化输入/输出的 API 调用。建议使用标准能力模型。

## 故障排除

### 事件未找到

验证事件 ID 和日历 ID 是否正确。事件 ID 在每个日历中是唯一的。

### 时区问题

始终使用带有明确时区偏移的 RFC3339 格式，或 UTC（Z 后缀）。对于全天事件，使用 YYYY-MM-DD 格式，并可选指定 `--timezone`。
