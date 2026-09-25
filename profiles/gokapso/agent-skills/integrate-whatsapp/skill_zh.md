# 集成 WhatsApp

## 设置

首选路径：
- 已安装并认证 Kapso CLI (`kapso login`)
- 在 onboarding 或 messaging 之前，使用 `kapso status` 确认项目访问权限

备用路径：
环境变量：
- `KAPSO_API_BASE_URL`（仅主机，不包含 `/platform/v1`）
- `KAPSO_API_KEY`
- `META_GRAPH_VERSION`（可选，默认 `v24.0`）

认证头部（直接 API 调用）：
```
X-API-Key: <api_key>
```

安装依赖（一次性）：
```bash
npm i
```

## 连接 WhatsApp（设置链接）

首选 onboarding 路径（CLI）：

1. 开始 onboarding：`kapso setup`
2. 如果设置被阻止，使用以下方式解决上下文：
   - `kapso projects list`
   - `kapso projects use <project-id>`
   - `kapso customers list`
   - `kapso customers new --name "<customer-name>" --external-id <external-id>`
   - `kapso setup --customer <customer-id>`
3. 完成托管 onboarding URL
4. 确认连接的号码：`kapso whatsapp numbers list --output json`
5. 解决您要操作的精确号码：`kapso whatsapp numbers resolve --phone-number "<display-number>" --output json`

备用 onboarding 流程（直接 API）：

1. 创建客户：`POST /platform/v1/customers`
2. 生成设置链接：`POST /platform/v1/customers/:id/setup_links`
3. 客户完成嵌入式注册
4. 使用 `phone_number_id` 发送消息和配置 webhook

检测连接：
- 项目 webhook `whatsapp.phone_number.created`（推荐）
- 成功重定向 URL 查询参数（用于前端 UX）

推荐的 Kapso setup-link 默认值：
```json
{
  "setup_link": {
    "allowed_connection_types": ["dedicated"],
    "provision_phone_number": true,
    "phone_number_country_isos": ["US"]
  }
}
```

注意：
- `kapso setup` 和 `kapso whatsapp numbers new` 默认使用 dedicated plus provisioning。
- 保持 `phone_number_country_isos`、`phone_number_area_code`、`language` 和重定向 URL 作为可选覆盖。

平台 API 基础：`/platform/v1`
Meta 代理基础：`/meta/whatsapp/v24.0`（消息、模板、媒体）
使用 `phone_number_id` 作为主要的 WhatsApp 标识符

## 接收事件（webhooks）

使用 webhooks 接收：
- 项目事件（连接生命周期、工作流事件）
- 号码事件（消息、会话、交付状态）

范围规则：
- **项目 webhooks**：仅项目级事件（连接生命周期、工作流事件）
- **号码 webhooks**：仅该 `phone_number_id` 的 WhatsApp 消息 + 会话事件
- WhatsApp 消息/会话事件 (`whatsapp.message.*`、`whatsapp.conversation.*`) 仅限号码

创建 webhook：
- 项目级：`node scripts/create.js --scope project --url <https://...> --events <csv>`
- 号码：`node scripts/create.js --phone-number-id <id> --url <https://...> --events <csv>`

创建/更新常用标志：
- `--url <https://...>` - webhook 目的地
- `--events <csv|json-array>` - 事件类型（Kapso webhooks）
- `--kind <kapso|meta>` - Kapso（基于事件）与原始 Meta 转发
- `--payload-version <v1|v2>` - 负载格式（推荐 `v2`）
- `--buffer-enabled <true|false>` - 启用 `whatsapp.message.received` 的缓冲
- `--buffer-window-seconds <n>` - 1-60 秒
- `--max-buffer-size <n>` - 1-100
- `--active <true|false>` - 启用/禁用

测试交付：
```bash
node scripts/test.js --webhook-id <id>
```

始终验证签名。参见：
- `references/webhooks-overview.md`
- `references/webhooks-reference.md`

## 发送和读取消息

### 首先发现 ID

需要两个 Meta ID 进行不同操作：

| ID | 用于 | 如何发现 |
|----|----------|-----------------|
| `business_account_id` (WABA) | 模板 CRUD | `kapso whatsapp numbers resolve --phone-number "<display-number>" --output json` 或 `node scripts/list-platform-phone-numbers.mjs` |
| `phone_number_id` | 发送消息、媒体上传 | `kapso whatsapp numbers resolve --phone-number "<display-number>" --output json` 或 `node scripts/list-platform-phone-numbers.mjs` |

### 首先使用 CLI 操作

常用命令：
```bash
kapso whatsapp numbers list --output json
kapso whatsapp numbers resolve --phone-number "<display-number>" --output json
kapso whatsapp messages send --phone-number-id <PHONE_NUMBER_ID> --to <wa-id> --text "Hello from Kapso"
kapso whatsapp messages list --phone-number-id <PHONE_NUMBER_ID> --limit 50 --output json
kapso whatsapp messages get <MESSAGE_ID> --phone-number-id <PHONE_NUMBER_ID> --output json
kapso whatsapp conversations list --phone-number-id <PHONE_NUMBER_ID> --output json
kapso whatsapp templates list --phone-number-id <PHONE_NUMBER_ID> --output json
kapso whatsapp templates get <TEMPLATE_ID> --phone-number-id <PHONE_NUMBER_ID> --output json
```

### SDK 设置

安装：
```bash
npm install @kapso/whatsapp-cloud-api
```

创建客户端：
```ts
import { WhatsAppClient } from "@kapso/whatsapp-cloud-api";

const client = new WhatsAppClient({
  baseUrl: "https://api.kapso.ai/meta/whatsapp",
  kapsoApiKey: process.env.KAPSO_API_KEY!
});
```

### 发送文本消息

通过 SDK：
```ts
await client.messages.sendText({
  phoneNumberId: "<PHONE_NUMBER_ID>",
  to: "+15551234567",
  body: "Hello from Kapso"
});
```

### 发送模板消息

1. 发现 ID：`node scripts/list-platform-phone-numbers.mjs`
2. 从 `assets/template-utility-order-status-update.json` 起草模板负载
3. 创建：`node scripts/create-template.mjs --business-account-id <WABA_ID> --file <payload.json>`
4. 检查状态：`node scripts/template-status.mjs --business-account-id <WABA_ID> --name <name>`
5. 发送：`node scripts/send-template.mjs --phone-number-id <ID> --file <send-payload.json>`

### 发送交互式消息

交互式消息需要激活的 24 小时会话窗口。对于窗口外的出站通知，使用模板。

1. 发现 `phone_number_id`
2. 从 `assets/send-interactive-*.json` 选择负载
3. 发送：`node scripts/send-interactive.mjs --phone-number-id <ID> --file <payload.json>`

对于联系人信息请求，使用 `interactive.type: "request_contact_info"` 和 `action.name: "request_contact_info"`。包含 `body`，但省略 `header` 和 `footer`。

### 读取收件箱数据

首选路径：
- CLI：`kapso whatsapp messages ...`、`kapso whatsapp conversations ...`、`kapso whatsapp templates ...`

备用路径：
- 代理：`GET /{phone_number_id}/messages`、`GET /{phone_number_id}/conversations`
- SDK：`client.messages.query()`、`client.messages.get()`、`client.conversations.list()`、`client.conversations.get()`、`client.templates.get()`

### 嵌入收件箱

当用户希望将 Kapso 的收件箱嵌入到他们自己的应用中时，使用 Platform API 收件箱嵌入。

创建：
- `POST /platform/v1/inbox_embeds`
- 信封：`inbox_embed`
- 公共范围：`project`、`customer`、`phone_number`
- `scope_id` 对 `project` 为空，对 `customer` 为客户 UUID，对 `phone_number` 为 WhatsApp `phone_number_id`
- `language` 控制嵌入收件箱 UI 语言；支持值是 `en` 和 `es`
- 创建后返回 `token` 和 `embed_url`。存储 `embed_url`；列表/获取/更新忽略密钥。

示例：
```json
{
  "inbox_embed": {
    "name": "Support inbox",
    "scope_type": "phone_number",
    "scope_id": "1234567890",
    "allowed_origins": ["https://app.example.com"],
    "default_mode": "system",
    "language": "es"
  }
}
```

管理：
- `GET /platform/v1/inbox_embeds`
- `GET /platform/v1/inbox_embeds/:id`
- `PATCH /platform/v1/inbox_embeds/:id`
- `DELETE /platform/v1/inbox_embeds/:id`（撤销）

### 模板规则

创建：
- 使用 `parameter_format: "NAMED"` 与 `{{param_name}}`（优先于位置）
- 在使用变量于 HEADER/BODY 时包含示例
- 使用 `language`（不是 `language_code`）
- 不要交错 QUICK_REPLY 与 URL/PHONE_NUMBER 按钮
- URL 按钮变量必须在 URL 的末尾，并使用位置 `{{1}}`
- 对于 `REQUEST_CONTACT_INFO` 按钮，省略 `text`；WhatsApp 提供标签

发送时：
- 对于 NAMED 模板，在 header/body params 中包含 `parameter_name`
- URL 按钮需要一个 `button` 组件，`sub_type: "url"` 和 `index`
- 媒体头部使用 `id` 或 `link`（不能同时使用）

## WhatsApp 流程

使用 Flows 构建原生 WhatsApp 表单。编辑 Flow JSON 之前，请阅读 `references/whatsapp-flows-spec.md`。

### 创建和发布 Flow

1. 创建 Flow：`node scripts/create-flow.js --phone-number-id <id> --name <name>`
2. 更新 JSON：`node scripts/update-flow-json.js --flow-id <id> --json-file <path>`
3. 发布：`node scripts/publish-flow.js --flow-id <id>`
4. 测试：`node scripts/send-test-flow.js --phone-number-id <id> --flow-id <id> --to <phone>`

### 附加数据端点（动态 Flow）

1. 设置加密：`node scripts/setup-encryption.js --flow-id <id>`
2. 创建端点：`node scripts/set-data-endpoint.js --flow-id <id> --code-file <path>`
3. 部署：`node scripts/deploy-data-endpoint.js --flow-id <id>`
4. 注册：`node scripts/register-data-endpoint.js --flow-id <id>`

### Flow JSON 规则

静态 Flow（无数据端点）：
- 使用 `version: "7.3"`
- `routing_model` 和 `data_api_version` 是可选的
- 参见 `assets/sample-flow.json`

动态 Flow（带数据端点）：
- 使用 `version: "7.3"` 与 `data_api_version: "3.0"`
- `routing_model` 是必需的（定义有效屏幕转换）
- 参见 `assets/dynamic-flow.json`

### 数据端点规则

处理器签名：
```js
async function handler(request, env) {
  const body = await request.json();
  // body.data_exchange.action: INIT | data_exchange | BACK
  // body.data_exchange.screen: 当前屏幕 ID
  // body.data_exchange.data: 用户输入
  return Response.json({
    version: "3.0",
    screen: "NEXT_SCREEN_ID",
    data: { }
  });
}
```

- 不要使用 `export` 或 `module.exports`
- 完成使用 `screen: "SUCCESS"` 与 `extension_message_response.params`
- 不要包含 `endpoint_uri` 或 `data_channel_uri`（Kapso 注入这些）

### 故障排除

- 在深入每个资源端点之前搜索日志：`kapso logs search --query "<wamid-flow-id-request-id-or-endpoint>" --period 7d --source all --limit 20 --output json`
- 预览显示 `"flow_token is missing"`：Flow 是动态的，没有数据端点。附加一个并刷新。
- 加密设置错误：在设置中为号码/WABA 启用加密。
- OAuthException 139000（Integrity）：WABA 必须在 Meta 安全中心验证。

## 脚本

### Webhooks

| 脚本 | 目的 |
|--------|---------|
| `list.js` | 列出 webhooks |
| `get.js` | 获取 webhook 详情 |
| `create.js` | 创建 webhook |
| `update.js` | 更新 webhook |
| `delete.js` | 删除 webhook |
| `test.js` | 发送测试事件 |

### 消息和模板

| 脚本 | 目的 | 必需 ID |
|--------|---------|-------------|
| `list-platform-phone-numbers.mjs` | 发现 business_account_id + phone_number_id | — |
| `list-connected-numbers.mjs` | 列出 WABA 号码 | business_account_id |
| `list-templates.mjs` | 列出模板（带过滤器） | business_account_id |
| `template-status.mjs` | 检查单个模板状态 | business_account_id |
| `create-template.mjs` | 创建模板 | business_account_id |
| `update-template.mjs` | 更新现有模板 | business_account_id |
| `send-template.mjs` | 发送模板消息 | phone_number_id |
| `send-interactive.mjs` | 发送交互式消息 | phone_number_id |
| `upload-media.mjs` | 上传发送时头部媒体 | phone_number_id |

### Flows

| 脚本 | 目的 |
|--------|---------|
| `list-flows.js` | 列出所有 Flows |
| `create-flow.js` | 创建新 Flow |
| `get-flow.js` | 获取 Flow 详情 |
| `read-flow-json.js` | 读取 Flow JSON |
| `update-flow-json.js` | 更新 Flow JSON（创建新版本） |
| `publish-flow.js` | 发布 Flow |
| `get-data-endpoint.js` | 获取数据端点配置 |
| `set-data-endpoint.js` | 创建/更新数据端点代码 |
| `deploy-data-endpoint.js` | 部署数据端点 |
| `register-data-endpoint.js` | 将数据端点注册到 Meta |
| `get-encryption-status.js` | 检查加密状态 |
| `setup-encryption.js` | 设置 Flow 加密 |
| `send-test-flow.js` | 发送测试 Flow 消息 |
| `delete-flow.js` | 删除 Flow |
| `list-flow-responses.js` | 列出存储的 Flow 响应 |
| `list-function-logs.js` | 列出函数日志 |
| `list-function-invocations.js` | 列出函数调用 |

### OpenAPI

| 脚本 | 目的 |
|--------|---------|
| `openapi-explore.mjs` | 探索 OpenAPI（搜索/op/schema/where） |

示例：
```bash
node scripts/openapi-explore.mjs --spec whatsapp search "template"
node scripts/openapi-explore.mjs --spec whatsapp op sendMessage
node scripts/openapi-explore.mjs --spec whatsapp schema TemplateMessage
node scripts/openapi-explore.mjs --spec platform ops --tag "WhatsApp Flows"
node scripts/openapi-explore.mjs --spec platform op setupWhatsappFlowEncryption
node scripts/openapi-explore.mjs --spec platform search "setup link"
```

## 资产

| 文件 | 描述 |
|------|-------------|
| `template-utility-order-status-update.json` | UTILITY 模板带命名参数 + URL 按钮 |
| `send-template-order-status-update.json` | 订单状态更新发送时负载 |
| `template-utility-named.json` | UTILITY 模板显示按钮排序规则 |
| `template-marketing-media-header.json` | MARKETING 模板带 IMAGE 头部 |
| `template-authentication-otp.json` | AUTHENTICATION OTP 模板（COPY_CODE） |
| `send-interactive-buttons.json` | 交互式按钮消息 |
| `send-interactive-list.json` | 交互式列表消息 |
| `send-interactive-cta-url.json` | 交互式 CTA URL 消息 |
| `send-interactive-location-request.json` | 位置请求消息 |
| `send-interactive-catalog-message.json` | 目录消息 |
| `sample-flow.json` | 静态 Flow 示例（无端点） |
| `dynamic-flow.json` | 动态 Flow 示例（带端点） |
| `webhooks-example.json` | Webhook 创建/更新负载示例 |

## 参考

- [references/getting-started.md](references/getting-started.md) - 平台 onboarding
- [references/platform-api-reference.md](references/platform-api-reference.md) - 完整端点参考
- [references/setup-links.md](references/setup-links.md) - Setup link 配置
- [references/detecting-whatsapp-connection.md](references/detecting-whatsapp-connection.md) - 连接检测方法
- [references/webhooks-overview.md](references/webhooks-overview.md) - Webhook 类型、签名验证、重试
- [references/webhooks-event-types.md](references/webhooks-event-types.md) - 可用事件
- [references/webhooks-reference.md](references/webhooks-reference.md) - Webhook API 和负载说明
- [references/templates-reference.md](references/templates-reference.md) - 模板创建规则、组件速查表、发送时组件
- [references/whatsapp-api-reference.md](references/whatsapp-api-reference.md) - Meta 代理消息和会话负载
- [references/whatsapp-cloud-api-js.md](references/whatsapp-cloud-api-js.md) - SDK 使用发送和读取消息
- [references/whatsapp-flows-spec.md](references/whatsapp-flows-spec.md) - Flow JSON 规范

## 相关技能

- `automate-whatsapp` - 工作流、代理和自动化
- `observe-whatsapp` - 调试、日志、健康检查

<!-- FILEMAP:BEGIN -->
```text
[integrate-whatsapp file map]|root: .
|.:{package.json,SKILL.md}
|assets:{dynamic-flow.json,sample-flow.json,send-interactive-buttons.json,send-interactive-catalog-message.json,send-interactive-cta-url.json,send-interactive-list.json,send-interactive-location-request.json,send-template-order-status-update.json,template-authentication-otp.json,template-marketing-media-header.json,template-utility-named.json,template-utility-order-status-update.json,webhooks-example.json}
|references:{detecting-whatsapp-connection.md,getting-started.md,platform-api-reference.md,setup-links.md,templates-reference.md,webhooks-event-types.md,webhooks-overview.md,webhooks-reference.md,whatsapp-api-reference.md,whatsapp-cloud-api-js.md,whatsapp-flows-spec.md}
|scripts:{create-flow.js,create-function.js,create-template.mjs,create.js,delete-flow.js,delete.js,deploy-data-endpoint.js,deploy-function.js,get-data-endpoint.js,get-encryption-status.js,get-flow.js,get-function.js,get.js,list-connected-numbers.mjs,list-flow-responses.js,list-flows.js,list-function-invocations.js,list-function-logs.js,list-platform-phone-numbers.mjs,list-templates.mjs,list.js,openapi-explore.mjs,publish-flow.js,read-flow-json.js,register-data-endpoint.js,send-interactive.mjs,send-template.mjs,send-test-flow.js,set-data-endpoint.js,setup-encryption.js,submit-template.mjs,template-status.mjs,test.js,update-flow-json.js,update-function.js,update-template.mjs,update.js,upload-media.mjs,upload-template-header-handle.mjs}
|scripts/lib:{args.mjs,cli.js,env.js,env.mjs,http.js,output.js,output.mjs,request.mjs,run.js,whatsapp-flow.js}
|scripts/lib/webhooks:{args.js,kapso-api.js,webhook.js}
```
<!-- FILEMAP:END -->
