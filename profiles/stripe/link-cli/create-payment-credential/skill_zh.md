# 创建支付凭证

使用 [Link](https://link.com) 从 Link 钱包获取安全的、一次性使用的支付凭证来完成购买。

CLI 可以生成两种凭证类型之一：
- 虚拟卡（PAN），用于与标准网页结账表单一起使用。发出的卡可以在任何地方使用。
- 共享支付令牌（SPT），当卖家在 Stripe 网络中并接受程序化支付时（例如使用机器支付协议）。

它还可以创建与 Link Pay 令牌（LPT）绑定的 SpendRequest，用于支持的 Stripe 结账界面。LPT 是卡片流程的执行模式，而不是第三种凭证类型。

## 安装

使用 `npm install -g @stripe/link-cli` 安装。或者直接使用 `npx @stripe/link-cli` 运行。

## 运行命令

Link CLI 可以作为 **MCP 服务器** 或 **独立的 CLI** 运行。

**MCP：** 将以下内容添加到您的 MCP 客户端配置（`.mcp.json` 等）中。

```json
{
  "mcpServers": {
    "link": {
      "command": "npx",
      "args": ["@stripe/link-cli", "--mcp"]
    }
  }
}
```

直接使用 `npx @stripe/link-cli@latest --mcp` 运行 MCP 服务器。

调用 `tools/list` 查看所有可用的 MCP 工具。

### 常用命令/选项

- 列出所有命令：`link-cli --llms`
- 列出所有带参数的命令：`link-cli --llms-full`
- 使用 `--schema` 获取命令的确切架构。例如，`link-cli spend-request create --schema`
- 多步命令返回 `_next` 操作。例如，身份验证或创建 spend request 返回一个 `_next.command`，必须运行它以完成流程。如果提供结构化表单（`mpp pay` 返回 `_next.pay_argv`），请优先使用该表单，无需通过 shell 调用——请参阅安全说明。
- 默认情况下所有输出都是 `toon` 格式。传递 `--format [json|md|yaml]` 以更改输出格式。
- 某些命令返回验证或批准 URL。**这些** 必须清楚地展示给用户以供其操作。
- `--auth <path>` 标志将认证凭证存储在特定文件中，而不是默认位置。`auth login` 写入此文件；所有其他命令从此文件读取。示例：`link-cli auth login --auth credentials.json`

_推荐_：运行 `link-cli --llms` 了解所有可用命令。`--llms-full` 输出是参数名称、类型和有效值的规范参考。在调用命令之前传递 `--schema` 以了解其参数和约束。

## 核心流程

复制此清单并跟踪进度：

- 步骤 1：使用 Link 进行整个任务的认证
- 步骤 2：评估商家网站（确定凭证类型）
- 步骤 3：获取支付方式
- 步骤 4：使用正确的凭证类型创建 spend request
- 步骤 5：完成支付

### 步骤 1：使用 Link 进行整个任务的认证

检查认证状态：

```bash
link-cli auth status
```

认证后，响应还将报告会话的 `scope` 和 `authorization_details`（当令牌端点返回它们时）。如果响应包含 `update` 字段，则表示有更新的 `link-cli` 版本可用——运行该字段中的 `update_command` 在继续之前进行升级。

如果未认证：

```bash
link-cli auth login --client-name "<your-agent-name>"
```

将 `<your-agent-name>` 替换为您的代理或应用程序的名称（例如，`"Personal Assistant"`，`"Shopping Bot"`）。此名称在用户批准连接时出现在他们的 Link 应用中。使用清晰、唯一、可识别的名称。

响应包括 `_next` 命令——运行它以轮询直到认证。如果您的环境无法在单独的轮询命令阻塞 I/O 时传递验证码，请使用内联轮询：`auth login --client-name "<name>" --interval 5 --timeout 300`。这将立即提供代码，然后在同一命令中轮询。

如果用户的电子邮件已知，通过将它们作为 URL 编码的 `fromEmail` 查询参数添加到任何 `app.link.com` 验证或操作 URL 来节省时间；保留现有的查询参数。

**在用户使用 Link 认证之前不要继续。**

始终在开始新的登录流程之前检查当前的认证状态——用户可能已经登录。

如果用户已经认证，但您需要更广泛的访问权限（额外的 `scope`，`--source-actions` 或 `--authorization-detail`），请使用 `auth upgrade` 而不是 `auth login`。它接受相同的标志，但与“已经登录”的消息不同，它会将您请求的内容与当前的 `scope`/`authorization_details` 合并，并开始新的批准，以便进行超集——因此现有的访问权限永远不会丢失。首先检查 `auth status` 以了解已经授予的内容。当前会话在批准期间保持有效，只有在用户批准新的会话后才会替换，因此被放弃的升级会保留现有的会话工作。

可选地，在购买之前，运行 `link-cli user-info retrieve` 以检查余额资格、地址、适用的支出限额和验证要求。可选的 `eligible_for_balance` 字段表示用户的余额是否可用于代理钱包使用。有限限额值为分，而 `null` 限额或剩余值表示无限。当 `agent_wallet_verification_requirement.action_url` 存在时，请引导用户前往以完成所需操作。

### 步骤 2：在创建 spend request 之前评估商家网站

**关键：** 在调用 `spend-request create` 之前，您必须完成此清单：
1. 了解商家接受支付的方式（卡片或机器支付或其他）。**不要** 默认为 `card` 凭证类型。商家决定凭证类型——您无法在不检查的情况下知道它。跳过此步骤将生成具有错误凭证类型的 spend request。
2. 确定所需的最终总金额。包括任何运费、税费或其他费用。跳过此步骤将生成一个无法覆盖所需全部金额的 spend request，并且将被拒绝。
3. 清晰的上下文和对用户正在购买的内容的理解。确保知道尺寸、颜色、运费选项等。跳过此步骤将生成一个用户不认识或不理解的 spend request。

**确定商家接受支付的方式：**

1. **导航到商家页面**——浏览它，阅读页面内容，并了解网站如何接受支付。
2. **如果结账页面包含 AI-agent 指导块**（找到“我是一个 AI agent”复选框，或 `.AiAgentPaymentSteering` 容器——在 DOM 中视觉隐藏但存在，通常在 Stripe iframe 内）——它可能支持 **Link Pay Token 流**（步骤 5，“Link Pay Token”部分）。**需要浏览器自动化。** 在创建 LPT 请求之前，请检查复选框并验证同一框架中是否存在 `input[name="link_pay_token"]` 和 `data-stripe-merchant-account`。从该属性中读取账户 ID。如果其中任何一个标记**不**出现，请按照块上的页面说明使用 `card`。如果没有浏览器自动化，请使用 `card`。
3. **如果页面有一个信用卡表单且没有 AI-agent 指导块**（没有“我是一个 AI agent”复选框 / `.AiAgentPaymentSteering`）——使用 `card`。
4. **如果页面描述了 API 或程序化支付流程**——向相关端点发起请求。如果它返回 **HTTP 402** 并带有 `www-authenticate` 标头，请使用 `shared_payment_token`。

您发现的内容决定了要使用的凭证类型：

| 您看到的内容 | 凭证类型 | 要请求的内容 |
|---|---|---|
| `.AiAgentPaymentSteering` 块 / “我是一个 AI agent”复选框，选中它后显示 `input[name="link_pay_token"]` 和 `data-stripe-merchant-account` | (无需) | Link Pay Token 流（否则 `card`） |
| 信用卡表单，没有 AI-agent 指导块 | `card`（默认） | 卡 |
| 带有 `method="stripe"` 的 `www-authenticate` 的 HTTP 402 | `shared_payment_token` | 共享支付令牌（SPT） |
| 没有 `method="stripe"` 的 `www-authenticate` 的 HTTP 402 | 不支持 | 不要继续 |

**对于 402 响应：** 使用 `mpp pay`——它自动处理整个流程（探测 URL、解析挑战、选择支付方式、创建 spend request、获取批准并付款）。见步骤 5。

### 步骤 3：确认支付方式，可能需要运费地址

Link 将自动使用账户上的默认支付方式。如果用户明确要求使用特定的卡或银行支付，请使用列表命令显示可用选项。请注意，用户的所有支付方式可能不会全部出现；这将过滤在“agentic-ready”支付类型上。

```bash
link-cli payment-methods list
```

如果商家结账需要运费或交付地址，请获取用户保存的运费地址。除非用户指定否则使用默认地址。

```bash
link-cli shipping-address list
```

### 步骤 4：使用正确的凭证类型创建 spend request

对于卡片和共享支付令牌流程，使用以下命令。对于 Link Pay Token，**不要** 创建此通用请求：在您在步骤 5 中读取了商家账户 ID 后，请遵循 LPT 说明。

```bash
link-cli spend-request create \
  --amount <cents> \
  --context "<description>" \
  --merchant-name "<name>" \
  --merchant-url "<url>" \
  --line-item "name:<product>,unit_amount:<cents>,quantity:<n>" \
  --total "type:total,display_text:Total,amount:<cents>" \
 
```

**`--line-item` 键：** `name`（必需），`quantity`，`unit_amount`，`description`，`sku`，`url`，`image_url`，`product_url`。可重复用于多个项目。

**`--total` 键：** `type`（必需；之一：`subtotal`，`tax`，`total`，`items_base_amount`，`items_discount`，`discount`，`fulfillment`，`shipping`，`fee`，`gift_wrap`，`tip`，`store_credit`），`display_text`（必需），`amount`（必需）。可重复（例如，`subtotal` + `tax` + `shipping` + `total`）。

在请求仍为 `created` 或 `pending_approval` 时不要继续到支付。如果轮询退出 `POLLING_TIMEOUT`，请继续等待或询问用户是否要继续轮询。如果他们拒绝，请询问下一步该做什么。如果用户想要放弃，请取消 spend request：

```bash
link-cli spend-request cancel <id>
```

`spend-request retrieve <id> --interval 2` 等待初始状态变化，当它是 `created`，`pending_approval` 或 `requires_action` 时 `auto_resume`。所有其他状态，包括 `submitted` 和不熟悉的 API 值，都会立即返回。状态变化不一定意味着批准：检查返回的状态，如果它仍然在等待，请再次检索。

建议用户使用 [Link 应用](https://link.com/download) 批准。显示下载 URL。

**测试模式：** 添加 `--test` 以创建测试模式凭证而不是真实凭证。适用于开发和集成测试。Link Pay Token 不支持测试模式。

**批准详情：** 对于委托/预批准流程，将 `--approval-detail` 作为 JSON 对象（MCP/代理）或 JSON 字符串（CLI）传递。必需字段：`approved_at`（Unix 时间戳），`approval_method`（`click`|`programmatic`|`voice`），`app_name`，`external_user_id`。可选：`ip_address`，`user_agent`，`device_type` (`mobile`|`web`），`agent_log_id`，`external_user_name`，`external_session_id`，`authentication_method` (`biometric_face`|`biometric_fingerprint`|`passkey`).

**元数据：** 使用可重复的 `--metadata "key:value"` 标志（CLI）或 `{ key: value }` 对象（MCP/代理）附加任意字符串数据。最多 50 个键，键 ≤ 40 个字符，值 ≤ 500 个字符。示例：`--metadata "order_id:ord_123" --metadata "team:growth"`.

如果响应包含 `status: "requires_action"`，请读取 `status_details.requires_action.next_action`（`type`，`display_message`，`action_url`，`resolution`）。向用户展示 `display_message`；如果存在 `action_url`，请清晰地展示给用户。
- 如果 `resolution` 是 `auto_resume`（目前只有 `three_d_secure`），请自行运行返回的 `_next.command`（轮询 `spend-request retrieve <id> --interval 2 --max-attempts 300`）。轮询在状态变化时返回；检查结果，这可能是在用户完成银行的挑战后 `approved`，`submitted` 或 `succeeded`。
- 否则（`resolution` 是 `create_new_spend_request` 或 `create_new_spend_request_after_completion`——涵盖 `ssn_verification`，`identity_verification`，`contact_support`，`select_payment_method`，`add_payment_method`，`update_payment_method`，`re_authorize`，`three_d_secure_retry`），请让用户完成指示的操作，然后创建一个新的 spend request——旧请求将自行过期。

此相同的 `requires_action` 状态也可能在步骤 5 中从 `spend-request retrieve` 出现——`update_payment_method`，`re_authorize` 和 `three_d_secure_retry` 只会以这种方式出现，并且它们都使用 `create_new_spend_request`。在此处应用基于 `resolution` 的分支。

### 步骤 5：完成支付

**卡片：** 运行 `link-cli spend-request retrieve <id> --include card` 以获取 `card` 对象，其中包含 `number`，`cvc`，`exp_month`，`exp_year`，`billing_address`（姓名，line1，line2，城市，州，邮政编码，国家）和 `valid_until`（Unix 时间戳——卡片在此时间后失效）。将这些详细信息输入商家的结账表单。

**安全的凭证传递：** 为了避免将卡片数据泄露到转录或日志中，请添加 `--output-file <path>` 将完整的卡片写入本地文件（使用 `0600` 权限创建），而 stdout 仅显示部分数据。使用 `--force` 覆盖现有文件。示例：

```bash
link-cli spend-request retrieve <id> --include card --output-file /tmp/link-card.json --format json
```

**带有 402 流的 SPT：** `mpp pay` 处理整个机器支付流程端到端。它探测 URL 以获取 402 挑战，解析 `www-authenticate` 标头以提取网络 ID 和金额，创建 spend request，获取用户批准，检索 SPT 并付款。SPT 是一次性使用的。

```bash
link-cli mpp pay <url> --context "<description>" [-X POST] [-d '<body>'] [-H 'Name: Value'] [--test]
```

金额和货币自动从 402 挑战中导出。传递 `--amount` 以覆盖。`--context` 是必需的（最小 100 个字符）——描述购买的原因，以便用户了解他们正在批准什么。默认支付方式将用于除非指定 `--payment-method-id`。

SPT 是**一次性使用**——如果支付失败，请再次运行 `mpp pay`（它将创建一个新的 spend request）。

**预批准的 spend request：** 如果您已经有一个批准的 spend request，其中 `credential_type: "shared_payment_token"`，请传递 `--spend-request-id <id>` 跳过创建/批准步骤：

```bash
link-cli mpp pay <url> --spend-request-id <id> [-X POST] [-d '<body>'] [-H 'Name: Value']
```

**Link Pay Token：** 某些结账页面嵌入了一个 AI-agent 指导块（`.AiAgentPaymentSteering` 组件），允许代理使用 Link Pay Token 支付，而无需处理卡号。此流程需要浏览器自动化。

该块在视觉上隐藏，可能位于 Stripe 帧内。不要假设固定的位置：在顶层文档和 Stripe 帧中搜索 `.AiAgentPaymentSteering` 或“我是一个 AI agent”复选框，并在包含它的帧中执行以下步骤。

1. 打开商家结账页面并定位指导块。

2. **选中“我是一个 AI agent”复选框以显示该块。因为控制是键盘隐藏的，所以使用 DOM 级别的 `click()`：

   ```javascript
   document.querySelector('.AiAgentPaymentSteering input[type="checkbox"]').click();
   ```

3. **在创建 SpendRequest 之前确认绑定的令牌路径可用。** 在几秒钟内，同一帧必须包含 `input[name="link_pay_token"]` 和 steering block 上的 `data-stripe-merchant-account="acct_..."` 属性。

   ```javascript
   const merchantAccountId = document
     .querySelector(
       '.AiAgentPaymentSteering [data-stripe-merchant-account]',
     )
     ?.getAttribute('data-stripe-merchant-account');
   ```

如果其中任何一个标记缺失或 `merchantAccountId` 为空，则**不要** 创建 LPT 请求。使用正常的 `card` 流程。

4. **创建与商家绑定的 SpendRequest。** 使用 DOM 派生的账户 ID；不要发送 `--merchant-name` 或 `--merchant-url`。Link 在用户批准之前解析规范商家身份。

   ```bash
   link-cli spend-request create \
     --execution-method link_pay_token \
     --merchant-account-id <acct_...> \
     --payment-method-id <id> \
     --amount <cents> \
     --context "<description>" \
     --line-item "name:<product>,unit_amount:<cents>,quantity:<n>" \
     --total "type:total,display_text:Total,amount:<cents>"
   ```

   LPT 使用默认的 `card` 凭证类型。不要设置 `--credential-type shared_payment_token`，`--network-id` 或 `--test`。
   在获取批准之前展示批准 URL 并等待批准。见步骤 5 中的 LPT 说明。

5. **在注入之前立即检索令牌。** 每个返回的 LPT 最多有效期为 30 分钟，或直到 SpendRequest 过期：

   ```bash
   link-cli spend-request retrieve <id> --include link_pay_token --format json
   ```

6. **注入令牌** 到 `input[name="link_pay_token"]` 使用原生值设置器。不要逐个字符地输入它：

   ```javascript
   const input = document.querySelector('input[name="link_pay_token"]');
   Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')
     .set.call(input, token);
   input.dispatchEvent(new Event('input', { bubbles: true }));
   ```

7. **等待交换和登录完成。** 卡片表单被替换为显示消费者电子邮件的单一保存卡。然后在表单中点击 Pay/Submit 按钮。

**如果它没有转换，停止——不要循环。** 如果注入延迟，请检索一个新鲜的令牌并重试一次。如果保存卡没有替换表单，请取消绑定的 SpendRequest 并创建一个新的正常卡片请求，或者报告 `blocked`。不要在不同的结账界面上重用 LPT。

**Link Pay Token 流的重要说明：**
- 账户 ID 是浏览器提供的输入，不是商家身份的证明。Link 在服务器端解析它，并在用户批准之前向消费者显示规范商家身份。
- 控制对人类不可见，可能位于 Stripe 帧内——在包含块的帧中程序化操作它们。
- 不需要卡号——令牌直接使用存储在文件中的消费者保存卡授权支付。
- 代理使用令牌支付，而不是交互式 Link 登录。如果复选框缺失，一个已登录的 Link 会话可能显示 Link 钱包而不是卡片表单；在未登录 Link 的上下文中重试。
- 绑定的 LPT 请求不是备用虚拟卡请求。在创建之前如果缺少标记，请创建正常的卡片 SpendRequest。

## 购物目录（UCP）

通用商业协议 (UCP) 命令允许您无需浏览器或商家结账页面即可编程地购物和结账。将业务目标从目录搜索传递到结账创建和完成。

将 `--test` 添加到每个命令中以在 **演示模式** 下运行：端点返回自我一致的合成数据，而无需实时目录或收费。这是尝试端到端流程的安全方式。

步骤：

1. **搜索目录** 以获取产品和捕获其 `sku`（以及业务——每个产品都返回 `profile_id`，您将将其传递到下一步中的 `--business`）。`--query` 始终是必需的；过滤器（例如 `--brand`，`--category` 和 `--business`）可以缩小结果。

   ```bash
   link-cli ucp catalog search --query "running shoes" --business <np_...> --limit 5 --format json
   ```

2. **为业务和您想要的 SKU 创建结账**。这返回一个状态为 `requires_payment` 的会话，其中 `amount_total` — 您必须支付的金额（包括运费/税费等）。

   ```bash
   link-cli ucp checkout create \
     --business <np_...> \
     --line-item "id:<sku>,quantity:1" \
     --format json
   ```

   `--line-item` 可重复，使用 `key:value` 格式，键 `id`（必需）和 `quantity`（必需，正整数）。CLI 将 `id` 发送到 UCP API 作为 `sku_id`。可选地传递 `--fulfillment-details` 作为 JSON（例如，一个运费地址）。

3. **为结账总金额创建 spend request**。使用 `shared_payment_token` 凭证类型。Spend requests 调用 UCP 业务值称为网络 ID，因此将相同的值传递给 `--network-id`：

   ```bash
   link-cli spend-request create \
     --credential-type shared_payment_token \
     --network-id <business> \
     --amount <amount_total> \
     --context "<at least 100 characters describing the purchase and rationale>" \
     --request-approval
   ```

   向用户展示批准 URL 并轮询直到批准——见上一步和 SPT/402 指导。保留批准的 spend request ID；结账完成会内部解析其支付凭证。

4. **仅完成结账一次** 使用批准的 spend request ID 和用于创建结账的相同业务。两者 `--spend-request-id` 和 `--business` 都是必需的，并且必须非空。保留两者 ID。完成结账启动支付，但本身并不能证明复合操作成功。

   ```bash
   link-cli ucp checkout complete <checkout_id> \
     --spend-request-id <spend_request_id> \
     --business <np_...> \
     --format json
   ```

5. **在轮询之前仅检索复合状态一次**。将 spend request 视为支付执行的来源和所需操作的真相。结账 `completed` 在支付期间不是单调的：结账可以暂时 `completed`，而 spend request 是 `requires_action`。

   按顺序分支：

   - 如果结账 `status` 是 `expired`，停止并报告失败。
   - 如果 spend request 具有终端失败状态（`expired`，`denied`，`failed` 或 `canceled`），停止并报告失败。
   - 如果 spend request `status` 是 `requires_action`，无论结账状态如何，请检查 `spend_request.status_details.requires_action.next_action` (`type`，`display_message`，`action_url`，`resolution`)。向用户展示 `display_message`；如果存在 `action_url`，请清晰地展示给用户。
   - 如果 `resolution` 是 `auto_resume`（目前只有 `three_d_secure`），请自行运行返回的 `_next.command`（轮询 `spend-request retrieve <id> --interval 2 --max-attempts 300`)。轮询在状态变化时返回；检查结果，这可能是在用户完成银行的挑战后 `approved`，`submitted` 或 `succeeded`。
   - 否则 (`resolution` 是 `create_new_spend_request` 或 `create_new_spend_request_after_completion`——涵盖 `ssn_verification`，`identity_verification`，`contact_support`，`select_payment_method`，`add_payment_method`，`update_payment_method`，`re_authorize`，`three_d_secure_retry`），请停止并执行指示的恢复操作，而不是轮询。

   ```bash
   link-cli ucp checkout retrieve <checkout_id> \
     --spend-request-id <spend_request_id> \
     --format json
   ```

6. **仅在状态可以无替换 spend request 的情况下轮询。**
   缺失、`null` 或空的 `next_action` 是终端：报告卡片错误并不要轮询或再次调用 `checkout complete`。对于 `auto_resume`，显示操作并等待用户完成它；然后调用相同的检索命令并传递 `--poll`。不要在操作完成之前开始轮询，因为检索将正确返回 `action_required`。对于 `create_new_spend_request` 或 `create_new_spend_request_after_completion`，停止并执行指示的恢复操作，而不是轮询。

   ```bash
   link-cli ucp checkout retrieve <checkout_id> \
     --spend-request-id <spend_request_id> \
     --poll \
     --timeout 600 \
     --format json
   ```

   仅当 `outcome: success` 时报告成功，这需要结账 `completed` 和 spend request `succeeded`。将 `timed_out` 视为不确定，包括最新状态；不要从超时中推断成功或失败。

注意：
- 从不省略 `--spend-request-id` 或 `--business` 从 `ucp checkout complete` 中。使用批准的 spend request 的 ID 和结账的原始业务值。
- 不要在轮询时重试 `ucp checkout complete`。底层支付凭证是一次性使用的；如果需要恢复，请遵循返回的操作或失败结果。

## 报告结果

在购买尝试之后，鼓励您报告结果——无论它成功、被阻止还是被放弃。这是可选的，但有助于 Stripe 改进代理的结账。

```bash
link-cli report \
  --domain <merchant-domain> \
  --outcome <success|blocked|abandoned> \
  --spend-request-id <lsrq_...> \
  [--tag <tag>] \
  [--step <step>] \
  [--freeform-context "<details>"] \
  [--attempt-trace "<step-by-step account>"]
```

### 报告时间

- **success** — 支付完成且订单确认
- **blocked** — 代理无法完成支付，由于障碍（验证码、WAF、速率限制等）
- **abandoned** — 代理选择停止（用户取消、网站错误、超时等）

### 标签

添加一个或多个 `--tag` 标志来分类发生了什么。优先使用最具体的标签；仅在没有任何其他标签适用时使用 `other`，并在 `--freeform-context` 中描述发生了什么。

| 标签 | 含义 |
|---|---|
| `stripe_checkout` | 商家使用 Stripe 结账 |
| `captcha` | 被验证码阻止 |
| `anti_bot_script` | 被反机器人脚本阻止 |
| `cdn_block` | 被 CDN (Cloudflare 等) 阻止 |
| `waf_block` | 被 WAF 阻止 |
| `dns_block` | DNS 级别阻止 |
| `rate_limited` | 速率限制 |
| `login_required` | 登录墙阻止结账 |
| `3ds_challenge` | 3DS 挑战无法完成 |
| `page_inaccessible` | 页面返回错误或无法加载 |
| `timeout` | 操作超时 |
| `site_error` | 商家网站返回错误 |
| `payment_declined` | 支付被处理器拒绝 |
| `other` | 其他（在 freeform-context 中描述） |

### 尝试跟踪

`--attempt-trace` 是您在域上采取的路径的逐步说明，以便另一个代理可以跟随它。`--step` 记录您在结果发生时所在的位置；整个路径是跟踪。

发送它以供每个结果，而不仅仅是 `success`。失败的尝试中的死胡同是防止下一个代理在它们上花费令牌的原因。

将每个步骤写成编号行。在每一行中给出 URL 路径、可见标签或选择器、操作以及您观察到的内容。逐字引用错误消息和挑战文本。当您失败时，说明您尝试了什么以及每个尝试失败的具体原因。

不要将买家的个人数据放入其中——没有电子邮件、姓名、地址、电话、卡号或订单号。将 `[email]`，`[address]` 等代替。

```
1. / — 点击顶部导航中的 "Shop" → 分类网格
2. /collections/mice — 点击产品缩略图 "Magic Mouse" → PDP
3. /products/magic-mouse — 点击 "添加到购物车" → 购物车抽屉打开
4. /checkout — 在运费表单解锁之前需要电子邮件字段；输入 [email]
5. /checkout — "继续到运费" 禁用，直到输入 ZIP；输入 [address]
6. /checkout — 支付步骤以跨源 iframe 标题 "安全支付" 渲染。检测 Payment Element，使用 Link 凭证
7. /checkout — 点击 "立即支付" → 出现 hCaptcha 挑战，文本："验证您是人类"。重试一次，挑战没有重新出现。
8. /checkout/thank_you — 订单确认
OUTCOME: success. Notes: 电子邮件必须在运费表单解锁之前输入——先输入运费，再输入运费会默默地清除它。
```

最后一行是值得保留的细节：没有标签或枚举可以捕获它。

超过 8000 个字符的跟踪将被服务器截断，而不是拒绝，并且报告仍然被记录。发送完整的叙述，而不是修剪它或跳过报告。

### 示例

```bash
# 成功购买
link-cli report --domain shop.example.com --outcome success --spend-request-id lsrq_abc123

# 被 captcha 阻止
link-cli report --domain shop.example.com --outcome blocked --spend-request-id lsrq_abc123 --tag captcha --step "checkout page"

# 由于网站错误而放弃
link-cli report --domain shop.example.com --outcome abandoned --spend-request-id lsrq_abc123 --tag site_error --freeform-context "500 错误在支付提交时"

# 成功，并记录路径供下一个代理使用
link-cli report --domain shop.example.com --outcome success --spend-request-id lsrq_abc123 \
  --attempt-trace "$(cat <<'EOF'
1. / — 点击顶部导航中的 "Shop" → 分类网格
2. /products/magic-mouse — 点击 "添加到购物车" → 购物车抽屉打开
3. /checkout — 电子邮件在运费解锁之前已知；输入 [email]
4. /checkout — 点击 "立即支付" → 订单确认
OUTCOME: success.
EOF
)"
```

报告输出是代理专用的（用户不可见）。鼓励报告，但不是必需的，包括当购买失败时。

## 更多文档

- MPP/x402 协议：https://mpp.dev/protocol.md, https://mpp.dev/protocol/http-402.md, https://mpp.dev/protocol/challenges.md
- Link: https://link.com/agents
- Link 应用（用于账户管理）：https://app.link.com
- Link 支持（如果用户需要帮助使用 Link）：https://support.link.com/topics/about-link
