# Maton API Gateway

为第三方应用程序提供管理的 API 路由，由 [Maton](https://maton.ai) 提供。

## 安装

### NPM
```bash
npm install -g @maton/cli
```

### Homebrew
```bash
brew install maton-ai/cli/maton
```

## 认证

### OAuth（推荐）
```bash
maton login --oauth
```

在浏览器中打开 OAuth 登录页面并等待授权。完成后，它将在 config.toml（例如 $HOME/.config/maton/config.toml）中创建一个配置文件，并将访问令牌和刷新令牌存储在操作系统的凭证存储中（macOS 上的 Keychain、Windows 上的 Credential Manager、Linux 上的 Secret Service），在过期时自动续期。CLI 在需要时读取它们；其他任何东西都不应该。

### API 密钥
```bash
maton login --interactive
```

需要手动从 [设置](https://maton.ai/settings) 复制一个 API 密钥，这很容易出错。完成后，它也会在 config.toml 中创建一个配置文件，并将密钥存储在相同的凭证存储中。它比 `export MATON_API_KEY=...` 更受青睐，后者会将长期凭证暴露给每个子进程。当 `MATON_API_KEY` 设置时，它将覆盖活动的配置文件。如果无法安装 CLI，请参阅 [附录：没有 CLI 的环境](#appendix-environments-without-the-cli) 以获取原始 HTTP 表单和处理密钥的规则。

### 验证
```bash
maton whoami --json
```
```json
{
  "authenticated": true,
  "profile_name": "alice@example.com",
  "auth_type": "oauth"
}
```
- 如果 `authenticated` 为 `false`，请停止并使用 `maton login --oauth` 重新登录。
- 如果 `auth_type` 为 `api_key`，建议使用 `maton login --oauth` 登录并避免保留长期凭证。

## 连接

### 列出连接
```bash
maton connection list slack --status ACTIVE
```
```json
{
  "connections": [
    {
      "connection_id": "{connection_id}",
      "status": "ACTIVE",
      "creation_time": "2025-12-08T07:20:53.488460Z",
      "last_updated_time": "2026-01-31T20:03:32.593153Z",
      "url": "https://connect.maton.ai/?session_token=5e9...",
      "app": "slack",
      "method": "OAUTH2",
      "metadata": {}
    }
  ]
}
```
参考 `maton connection list --help` 以获取可能的标志和值。

### 创建连接
> **需要明确用户批准。** 确认特定的应用程序，并确认用户打算授权访问。切勿自行创建连接。

```bash
maton connection create slack
```
参考 `maton connection create --help` 以获取可能的标志和值。

### 获取连接
```bash
maton connection get {connection_id}
```
```json
{
  "connection": {
    "connection_id": "{connection_id}",
    "status": "PENDING",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=5e9...",
    "app": "slack",
    "metadata": {}
  }
}
```
在浏览器中打开返回的 URL 以完成应用程序的授权。如果应用程序提供作用域选择，请仅选择当前任务需要的作用域。

参考 `maton connection get --help` 以获取可能的标志和值。

### 删除连接
```bash
maton connection delete {connection_id} --yes
```
参考 `maton connection delete --help` 以获取可能的标志和值。

### 指定连接
如果同一应用程序有多个连接，请指定要使用的连接，以确保请求发送到预期的帐户：

```bash
maton slack channel list --types public_channel --limit 10 --connection {connection_id}
```

## 网关

### 应用程序命令
```bash
maton slack --help                # 应用程序下的资源
maton slack message --help        # 资源下的动词
maton slack message send --help   # 标志、要求、示例
```
参考 `maton --help` 以获取支持的应用程序列表。

### API 命令
使用 `maton api` 调用没有应用程序命令的 API 端点。

```bash
maton api '/google-mail/gmail/v1/users/me/messages'
maton api '/slack/api/conversations.list?types=public_channel&limit=10'
maton api '/airtable/v0/meta/bases/{base_id}/tables'
```
第一个路径段是应用程序标识符。它之后的内容是本地 API 路径，将原始路径不变地转发到上游主机，包括查询字符串。检查 [参考资料](references/) 下的应用程序参考。

参考 `maton api --help` 以获取可能的标志和值。

## 函数

### 列出函数
```bash
maton function list --visibility PRIVATE -L 20
```
```json
{
  "functions": [
    {
      "function_id": "{function_id}",
      "name": "my-fn",
      "description": null,
      "runtime": "python3.12",
      "visibility": "PRIVATE",
      "account_id": "{account_id}",
      "url": "https://my-fn-3k9xq2v.maton.app",
      "star_count": 0,
      "view_count": 0
    }
  ],
  "next_token": "gAAAAABqN6tD5X7..."
}
```
参考 `maton function list --help` 以获取可能的标志和值。

### 搜索函数
```bash
maton function search 'stripe refund'
maton function search '"def handler("' --context 2
maton function search '/def\s+handler/' --owner ALL
```
参考 `maton function search --help` 以获取可能的标志和值。

### 创建函数
```python title="main.py"
def handler(event, context):
    return {"hello": "ada"}
```
```bash
maton function create --name my-fn --file main.py
```
参考 `maton function create --help` 以获取可能的标志和值。

### 更新函数
```python title="main.py"
import json

def handler(event):
    body = json.loads(event.get("body") or "{}")
    return {"hello": body.get("name")}
```
```bash
maton function update {function_id} --file main.py        # 发布新代码作为新版本
maton function update {function_id} --version 1           # 回滚
maton function update {function_id} --name new-name       # 重新分配 URL
```
参考 `maton function update --help` 以获取可能的标志和值。

### 部署函数
```python title="my-fn/main.py"
def handler(event):
    return {"hello": "ada"}
```
```bash
cd my-fn && maton function deploy --yes
```
参考 `maton function deploy --help` 以获取可能的标志和值。

### 获取函数
```bash
maton function get {function_id}
```
```json
{
  "function_id": "{function_id}",
  "name": "my-fn",
  "description": null,
  "runtime": "python3.12",
  "visibility": "PRIVATE",
  "account_id": "{account_id}",
  "version": 3,
  "network_policy": "ALLOW_ALL",
  "url": "https://my-fn-3k9xq2v.maton.app",
  "star_count": 0,
  "view_count": 0,
  "created_at": "2026-08-20T18:11:04.512331Z",
  "updated_at": "2026-08-31T22:40:15.883210Z"
}
```
参考 `maton function get --help` 以获取可能的标志和值。

### 删除函数
```bash
maton function delete {function_id} --yes
```
参考 `maton function delete --help` 以获取可能的标志和值。

### 运行函数
部署的函数是一个 HTTP 处理程序，`maton api` 已经将给定的 URL 与活动配置文件的凭证附加到其中：

```bash
maton api https://my-fn-3k9xq2v.maton.app -f name=ada -i
```
参考 `maton api --help` 以获取可能的标志和值。

### 下载代码
```bash
maton function code download -f {function_id} --version 2 --dir ./v2
```
参考 `maton function code download --help` 以获取可能的标志和值。

### 列出版本
```bash
maton function version list --function {function_id}
```
参考 `maton function version list --help` 以获取可能的标志和值。

### 获取版本
```bash
maton function version get 2 --function {function_id}
```
```json
{
  "version": 2,
  "code_size": 4096,
  "runtime": "python3.12",
  "created_at": "2026-08-30T01:12:44.019283Z",
  "code_sha256": "9f2b...c41d",
  "handler": "main.handler"
}
```
参考 `maton function version get --help` 以获取可能的标志和值。

### 列出环境变量
```bash
maton function env list --function {function_id}
```
参考 `maton function env list --help` 以获取可能的标志和值。

### 创建环境变量
```bash
maton function env create GREETING -f {function_id} --value hi --type PLAIN
maton function env create TOKEN -f {function_id}                   # 提示输入，不回显
maton function env create -f {function_id} --env-file .env
```
参考 `maton function env create --help` 以获取可能的标志和值。

### 更新环境变量
```bash
maton function env update GREETING -f {function_id} --value hello
maton function env update TOKEN -f {function_id}                   # 提示输入，不回显
maton function env update -f {function_id} --env-file .env
```
参考 `maton function env update --help` 以获取可能的标志和值。

### 删除环境变量
```bash
maton function env delete GREETING -f {function_id} --yes
```
参考 `maton function env delete --help` 以获取可能的标志和值。

### 列出运行记录
```bash
maton function run list --function {function_id} -L 5
```
参考 `maton function run list --help` 以获取可能的标志和值。

### 获取运行记录
```bash
maton function run get {run_id} --function {function_id}
```
```json
{
  "run_id": "{run_id}",
  "function_id": "{function_id}",
  "version": 3,
  "request": {
    "method": "POST",
    "path": "/",
    "headers": {"authorization": "[REDACTED]", "content-type": "application/json"},
    "body": "{\"name\": \"ada\"}",
    "source_ip": "203.0.113.7",
    "user_agent": "maton/0.3.0"
  },
  "response": {
    "status": 200,
    "headers": {"content-type": "application/json"},
    "body": {"greeting": "hi ada"}
  },
  "created_at": "2026-08-31T22:41:02.113004Z",
  "started_at": "2026-08-31T22:41:02.240118Z",
  "ended_at": "2026-08-31T22:41:02.398772Z"
}
```
参考 `maton function run get --help` 以获取可能的标志和值。

### 列出日志
```bash
maton function run log list -f {function_id} --run {run_id} --since 10m
```
参考 `maton function run log list --help` 以获取可能的标志和值。

### 尾部日志
```bash
maton function run log tail -f {function_id}
```
参考 `maton function run log tail --help` 以获取可能的标志和值。

### 处理程序

运行时调用处理程序，并提供 `event` 和可选的 `context`，将其返回值转换为 HTTP 响应。

#### 事件

```json
{
  "version": 1,
  "rawPath": "/",
  "rawQueryString": "a=1",
  "cookies": ["k=v"],
  "headers": { "host": "greet-a1b2c3.maton.app" },
  "queryStringParameters": { "a": "1" },
  "requestContext": {
    "accountId": "...",
    "domainName": "greet-a1b2c3.maton.app",
    "domainPrefix": "greet-a1b2c3",
    "http": {
      "method": "POST",
      "path": "/",
      "protocol": "HTTP/1.1",
      "sourceIp": "...",
      "userAgent": "..."
    },
    "runId": "...",
    "time": "30/Aug/2026:17:24:03 +0000",
    "timeEpoch": 1788000000000
  },
  "body": "{\"name\":\"ada\"}",
  "isBase64Encoded": false
}
```

#### 上下文（可选）

**Python**

```python
context.run_id              # "..."
context.function_name       # "greet"
context.function_version    # "1"
context.function_id         # "..."
context.account_id          # "..."
context.memory_limit_in_mb  # 128
```

**Node**

```jsonc
{
  "runId": "...",
  "functionName": "greet",
  "functionVersion": "1",
  "functionId": "...",
  "accountId": "...",
  "memoryLimitInMB": "128"
}
```

#### 环境

沙盒可以看到来自 `function env` 的变量，以及注入的运行时 `MATON_API_KEY` 作用域为所有者帐户。当函数作为触发目标运行时，这也适用。

#### 响应

处理程序返回的任何不是包含 `statusCode` 键的字典的内容都将作为响应正文发送，状态码为 `200`。返回的字符串将被 JSON 编码，因此 `return "hello"` 返回为 `"hello"` 并带引号。要设置状态或标头，请返回一个包含 `statusCode` 的信封：

```python
def handler(event, context):
    return {
        "statusCode": 201,
        "headers": {"content-type": "text/plain"},
        "body": "created",
    }
```

## 触发器

### 列出触发器
```bash
maton trigger list --source github --status ENABLED -L 50
```
```json
{
  "triggers": [
    {
      "trigger_id": "{trigger_id}",
      "source": "github",
      "event_type": "pull_request.opened",
      "name": "PR opened",
      "description": null,
      "parameters": {"repo": "maton-ai/cli"},
      "connection_id": "{connection_id}",
      "destinations": [
        {
          "destination_id": "{destination_id}",
          "url": "{destination_url}",
          "name": null,
          "status": "ENABLED",
          "reason": null
        }
      ],
      "status": "ENABLED",
      "reason": null,
      "created_at": "2026-05-25T23:24:38.079501Z",
      "updated_at": "2026-05-25T23:24:38.079501Z"
    }
  ],
  "next_token": "gAAAAABqN6tD5X7..."
}
```
参考 `maton trigger list --help` 以获取可能的标志和值。

### 创建触发器
```bash
maton trigger create --source github --event-type pull_request.opened \
  --connection-id {connection_id} \
  --parameter repo=maton-ai/cli \
  --destination '{"url":"https://my-fn-3k9xq2v.maton.app","method":"POST","name":"prod"}'
```
参考 `maton trigger create --help` 以获取可能的标志和值。此外，每个源的事件类型及其 `parameters` 都在 `references/{source}/triggers.md` 中记录（例如 [google-mail](references/google-mail/triggers.md)）。除了应用程序源之外，特殊的 [`time`](references/time/triggers.md) 源根据 cron 时间表 (`schedule.elapsed`) 触发，无需活动的连接。

### 获取触发器
```bash
maton trigger get {trigger_id}
```
```json
{
  "trigger": {
    "trigger_id": "{trigger_id}",
    "source": "stripe",
    "event_type": "charge.succeeded",
    "name": "Charges",
    "description": null,
    "parameters": {"event_type": "charge.succeeded"},
    "connection_id": "{connection_id}",
    "destinations": [
      {
        "destination_id": "{destination_id}",
        "url": "{destination_url}",
        "name": null,
        "status": "ENABLED",
        "reason": null
      }
    ],
    "status": "ENABLED",
    "reason": null,
    "created_at": "2026-05-25T23:27:50.166333Z",
    "updated_at": "2026-05-25T23:27:50.166333Z"
  }
}
```
参考 `maton trigger get --help` 以获取可能的标志和值。

### 更新触发器
```bash
maton trigger update {trigger_id} --parameter repo=maton-ai/cli
```
参考 `maton trigger update --help` 以获取可能的标志和值。

### 删除触发器
```bash
maton trigger delete {trigger_id} --yes
```
参考 `maton trigger delete --help` 以获取可能的标志和值。

### 列出目标
```bash
maton trigger destination list --trigger {trigger_id}
```
```json
{
  "destinations": [
    {
      "destination_id": "{destination_id}",
      "url": "{destination_url}",
      "name": null,
      "status": "ENABLED",
      "reason": null
    }
  ]
}
```
参考 `maton trigger destination list --help` 以获取可能的标志和值。

### 创建目标
> **⚠ 持久数据转发：** 目标会导致所有匹配的触发事件自动且持续地传递到指定的 URL。这是一个持续的出站通道，而不是一次性操作。它需要自己的独立批准：绝不从隐式意图中获取，也绝不将其作为更广泛自动化的一部分。披露要求在 [创建目标](#create-destination) 中。

```bash
maton trigger destination create --trigger {trigger_id} \
  --url https://my-fn-3k9xq2v.maton.app --method POST --name prod \
  --header X-Signature-Key={{ your_receiver_key }}
```
参考 `maton trigger destination create --help` 以获取可能的标志和值。

**模板占位符：**
- `{{ payload }}` — 完整的事件负载，作为 JSON 内联
- `{{ payload.x.y.z }}` — 钻取负载中的嵌套字段
- `{{ trigger_id }}`, `{{ trigger_name }}`, `{{ event_id }}`, `{{ source }}`, `{{ event_type }}` — 标量元数据
- `{{ received_at }}` — 事件接收时间

### 获取目标
```bash
maton trigger destination get {destination_id} --trigger {trigger_id}
```
```json
{
  "destination": {
    "destination_id": "{destination_id}",
    "url": "{destination_url}",
    "method": "POST",
    "headers": {},
    "signing_secret": "••••••••••",
    "name": null,
    "body_template": null,
    "status": "ENABLED",
    "reason": null,
    "created_at": "2026-05-25T23:27:50.166333Z",
    "updated_at": "2026-05-25T23:27:50.166333Z"
  }
}
```
`signing_secret` 被遮罩；仅在创建时或通过 **旋转目标密钥** 才能获取明文值。

参考 `maton trigger destination get --help` 以获取可能的标志和值。

### 更新目标
> **⚠ 持久数据转发：** 更新目标 URL 会导致所有未来的事件交付重定向到新的主机。使用与创建目标时相同的披露要求与用户确认。

```bash
maton trigger destination update {destination_id} --trigger {trigger_id} --url https://new.dev/hook
```
参考 `maton trigger destination update --help` 以获取可能的标志和值。

### 删除目标
```bash
maton trigger destination delete {destination_id} --trigger {trigger_id} --yes
```
参考 `maton trigger destination delete --help` 以获取可能的标志和值。

### 旋转目标密钥
```bash
maton trigger destination rotate-secret {destination_id} --trigger {trigger_id}
```
```json
{
  "signing_secret": "whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```
新的目标密钥仅在明文返回时返回一次。

参考 `maton trigger destination rotate-secret --help` 以获取可能的标志和值。

### 列出事件
```bash
maton trigger event list --trigger {trigger_id} -L 1
```
参考 `maton trigger event list --help` 以获取可能的标志和值。

### 重放事件
```bash
maton trigger event replay {event_id} --trigger {trigger_id}
```
参考 `maton trigger event replay --help` 以获取可能的标志和值。

### 获取事件
```bash
maton trigger event get {event_id} --trigger {trigger_id}
```
```json
{
  "event": {
    "event_id": "{event_id}",
    "received_at": "2026-06-20T16:00:09.938161Z",
    "payload": {
      "scheduled_for": "2026-06-20T16:00:00Z",
      "cron_expression": "0 9 * * *",
      "timezone": "America/Los_Angeles"
    },
    "deliveries": [
      {
        "delivery_id": "{delivery_id}",
        "destination_id": "{destination_id}",
        "status": "SUCCEEDED",
        "reason": null,
        "attempts": 1,
        "last_response_status": 200,
        "last_response_body": "{}",
        "last_response_duration": 105,
        "last_error_message": null,
        "destination_url": null,
        "destination_method": null,
        "last_attempt_at": "2026-06-20T16:00:33.860432Z",
        "created_at": "2026-06-20T16:00:09.938161Z",
        "finished_at": "2026-06-20T16:00:33.860432Z"
      }
    ]
  }
}
```
参考 `maton trigger event get --help` 以获取可能的标志和值。

### 观察事件
`maton trigger event watch` 轮询事件并打印它们。如果没有 `--exec`，请使用它来检查触发器生成的内容。

```bash
maton trigger event watch -t {trigger_id}
```
> **⚠ `--exec` 在不受信任的输入上运行本地代码。** 处理程序是一个本地程序，CLI 每次事件都会调用它，其中包含第三方事件数据。这些数据可能受到攻击者的影响：电子邮件正文、评论、问题标题或表单字段可以由任何可以访问连接应用程序的人编写。在使用 `--exec` 之前：
>
> - **处理程序必须是由用户提供的一个脚本。** 不要在同一口气中编写处理程序并开始观察。如果用户要求提供处理程序，请向他们展示脚本以供他们保存和审查，解释它如何针对每个事件执行，并在运行之前获得明确的批准。绝不将 `--exec` 指向从 API 响应、webhook 负载或任何其他不受信任的源中获取的路径。
>
> - **将负载视为数据，切勿视为代码。** 从 stdin 读取它，将其解析为 JSON，并将字段作为离散参数传递（如下面的示例所示）。切勿将负载字段插入到 shell 字符串、`eval`、管道到 shell 的命令、SQL 字符串或文件路径。
>
> - **观察是一个长时间运行的自动化。** 它会一直作用于新事件，直到停止，因此每个事件都可能触发写入、发送或花费，而无需人工干预。将处理程序的范围限制为任务需要的最窄操作，并确认用户希望它在不监督的情况下运行。
>
> - **当目标是仅查看事件时，请使用 `watch` 或 `maton trigger event list`。** 当需要针对每个事件进行自动化时，请使用 `--exec`。

```bash
maton trigger event watch -t {trigger_id} --exec ./handle.sh
```
```bash title="handle.sh"
#!/usr/bin/env bash
EVENT_JSON="$(cat)" python <<'EOF'
import json, os, subprocess
event = json.loads(os.environ["EVENT_JSON"])
subprocess.run(
    [
        "maton", "slack", "message", "send",
        "--channel", "C0123456789",
        "--text", f"New email: {event['payload']['snippet']}",
    ],
    check=True,
)
EOF
```
电子邮件片段是不受信任的文本，因此它被作为离散的 `subprocess.run` 参数传递，而不是构建到 shell 字符串中。保持这种方式。

## 错误处理

| 状态 | 含义 |
|------|---------|
| 400 | 请求的应用程序缺少连接 |
| 401 | 无效、缺少或过期的 Maton 凭证 |
| 429 | 速率限制（每个帐户每秒 10 个请求） |
| 500 | 内部服务器错误 |
| 4xx/5xx | 来自目标 API 的透传错误 |

目标 API 的错误会连同原始状态码和响应正文一起透传。

### 故障排除：无效的应用程序名称

1. 验证路径是否以正确的应用程序名称开头。它必须以 `/google-mail/` 开头。例如：

- 正确: `/google-mail/gmail/v1/users/me/messages`
- 错误: `/gmail/v1/users/me/messages`

2. 确保为该应用程序有活动的连接：

```bash
maton connection list google-mail --status ACTIVE
```

### 故障排除：服务器错误

500 错误可能表示服务授权已过期。尝试通过上述连接管理部分创建新的连接并完成服务授权。如果新的连接是 "ACTIVE"，请删除旧的连接以确保 Maton 使用新的连接。
