# 设置 Link CLI

为用户的预期用途设置和认证 Link CLI。设置完成后，使用专门的功能进行支付或财务洞察工作。

## 1. 确定用途

仅在用户意图明确时推断用途：

- **代理支付**：购买、支付、结账或获取支付凭证。
- **财务洞察**：读取交易记录、余额、关联账户或支出模式。
- **两者**：启用支付和财务洞察。

如果预期用途不明确，请首先提供**两者**，并在安装、认证或选择权限之前明确推荐它作为默认选项：

```text
您打算如何使用 Link？
1. （推荐）两者：代理支付和财务洞察
2. 仅代理支付
3. 仅财务洞察
```

如果用户要求默认选项、接受推荐或没有偏好，请选择**两者**。否则，在用户选择或以其他方式澄清其意图之前不要继续。

## 2. 首先检查认证

一旦确定用途，请运行 `auth status` 作为第一个 Link CLI 命令。在运行 `auth login`、`auth upgrade` 或任何支付或财务数据命令之前，始终执行此操作：

```bash
link-cli auth status --format json
```

如果 `link-cli` 不可用，请使用 `npm install -g @stripe/link-cli` 安装它，然后运行状态命令。或者，用 `npx @stripe/link-cli@latest` 替换每个命令中的 `link-cli`。

### 常用命令/选项

- 列出所有命令：`link-cli --llms`
- 列出所有带参数的命令：`link-cli --llms-full`
- 使用 `--schema` 获取命令的确切架构。例如，`link-cli auth login --schema`
- 多步命令返回 `_next` 操作。例如，认证会返回一个 `_next.command`，必须运行它才能完成流程。
- 默认情况下所有输出都是 `toon` 格式。传递 `--format [json|md|yaml]` 以更改输出格式。
- 某些命令会返回验证或批准 URL。**这些**必须清晰地呈现给用户以供其操作。
- `--auth <path>` 标志将认证凭证存储在特定文件中，而不是默认位置。`auth login` 写入此文件；所有其他命令从中读取。示例：`link-cli auth login --auth credentials.json --format json`

_推荐_：运行 `link-cli --llms` 了解所有可用命令。`--llms-full` 输出是参数名称、类型和有效值的规范参考。在调用命令之前传递 `--schema` 以了解其参数和约束。

当存在时，检查 `scope` 和 `authorization_details` 以获取所选用途所需的访问权限。源操作会以 `type: "source"` 出现在授权详细信息中。如果响应包含 `update` 字段，请运行其 `update_command`，然后再次检查状态。

- 如果没有活动会话，请使用 `auth login`。
- 如果活动会话已经具有所需的访问权限，则不要启动另一个授权流程。
- 不要仅仅为了添加访问权限而注销。保留更广泛的现有访问权限，除非用户明确要求用更窄的访问权限替换它。

如果用户已经认证，但需要更广泛的访问权限（额外的 `scope`、`--source-actions` 或 `--authorization-detail`），请使用 `auth upgrade` 而不是 `auth login`。它接受相同的标志，但不会在“已经登录”的消息中停止，而是将您请求的内容与当前的 `scope`/`authorization_details` 合并，并启动一个新的批准流程以获取超集——因此现有的访问权限永远不会丢失。首先检查 `auth status` 以了解已经授予的内容。当前会话在批准期间保持有效，只有在用户批准新的会话后才会被替换，因此被放弃的升级会保留现有会话。

令牌端点可能会省略 `scope` 或 `authorization_details`，环境提供的访问令牌可能不会暴露授予权限的元数据。不要声称未报告的权限存在。如果存储的会话的授予权限无法验证，请使用 `auth upgrade` 并提供所需的访问权限。不要在不询问用户的情况下替换环境提供的会话。

## 3. 为用途请求访问权限

使用此访问权限映射：

| 用途 | Scope | 源操作 |
|---|---|---|
| 仅代理支付 | `userinfo:read payment_methods.agentic` | 无 |
| 仅财务洞察 | `userinfo:read` | 请求的洞察所需的操作 |
| 两者 | `userinfo:read payment_methods.agentic` | 请求的洞察所需的操作 |

将财务洞察需求映射到源操作：

| 预期洞察 | 源操作 |
|---|---|
| Link 处理的交易 | `read_link_transactions` |
| 从关联银行导入的交易 | `read_external_transactions` |
| 账户余额 | `read_balances` |
| 关联源详情和描述 | `read_source_details` |

仅请求特定声明任务所需的操作。如果用户要求一般设置财务洞察，请请求所有四个。对于**两者**，将代理支付范围与适用的源操作组合。

根据状态结果、清晰的代理或应用程序客户端名称以及映射中的范围使用 `login` 或 `upgrade`：

```bash
link-cli auth login \
  --client-name "<your-agent-name>" \
  --scope "<selected-scopes>" \
  --format json
```

将 `<your-agent-name>` 替换为您的代理或应用程序的名称（例如，`"个人助理"`、`"购物机器人"`）。此名称在用户批准连接时出现在他们的 Link 应用中。使用清晰、唯一、可识别的名称。

在扩展活动会话时将 `login` 更改为 `upgrade`。对于财务洞察，为每个所需操作添加一个 `--source-actions <action>` 标志。不要传递占位符字面值。

## 4. 完成用户批准

授权是一个多步骤流程：

1. 清晰地向用户展示返回的 `verification_url` 和短语。
2. 立即运行返回的 `_next.command` 以轮询批准；不要在等待另一个用户回复之前轮询。
3. 仅在结果报告成功认证和所需授予权限时继续。

如果用户的电子邮件地址已知，请通过将 URL 编码的 `fromEmail` 查询参数添加到任何 `app.link.com` 验证或操作 URL 来节省时间；保留现有查询参数。

响应包括 `_next` 命令——运行它以轮询直到认证。如果您的环境无法在单独的轮询命令阻塞 I/O 时传递验证代码，请通过在初始 `auth login` 或 `auth upgrade` 命令中添加 `--interval 5 --timeout 300` 使用内联轮询。这将立即提供代码，然后在同一命令中轮询。

**直到用户通过 Link 认证后才能继续。**

如果批准被拒绝、过期或超时，请报告该结果。不要在不经用户指示的情况下重复创建新的授权流程。永远不要暴露访问令牌、刷新令牌或认证文件内容。

## 5. 交由用途技能处理

仅认证不会授权单个购买，也不会回答财务数据问题。

- 对于购买和支付凭证，使用 `create-payment-credential` 技能。
- 对于交易、余额、源和摘要，使用 `financial-insights` 技能。
- 对于选择两者的用户，为每个后续任务加载相关的下游技能。
