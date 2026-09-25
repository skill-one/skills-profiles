# Amazon SES

## 概述

> **推荐**: 使用具有 SES 权限的 [AWS MCP Server](https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html) 进行沙盒执行和 CloudTrail 审计日志记录。
> **未使用 MCP**: 所有操作均使用标准 AWS CLI 语法 (`aws sesv2 ...`)。

将非电子邮件认证专家的开发者从空的 AWS 账户引导至其收件箱中的真实、经过认证的电子邮件，并进一步引导至 AWS 批准请求的生产发送。

在触摸任何内容之前，请先阅读账户和身份状态，并仅完成实际缺失的域名设置部分。在域名设置完成后，并且用户已明确同意之前，请勿请求生产访问。测试发送是可选的：在用户要求时运行它，接收者必须是账户当前状态允许的。

## 路由

| 如果用户想要... | 阅读 |
|-------------------------|------|
| 开始使用 SES，设置电子邮件发送，发送第一封或测试邮件，退出沙盒，或诊断 `MessageRejected: Email address is not verified` | [SES 引导：从零到第一封送达邮件](references/onboarding.md) |
| 设置用于发送的域名，配置电子邮件认证，或排除 DKIM | [设置 SES 域身份](references/setting-up-ses-domain-identity.md) |

## 护栏 — 此技能自身文件的位置（MCP 与本地安装）

此技能可以通过两种方式加载，并且它们从不同的位置解析其自身的捆绑文件。在阅读参考之前，确定技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载**: 技能不在本地文件系统中。**你必须通过带有 `file` 参数的 `retrieve_skill` 来获取每个参考**（例如 `file="references/onboarding.md"`）。**不要在本地 `file_read` 这些路径** — 它们不存在于磁盘上。
- **本地安装**（例如 `~/.kiro/skills/amazon-ses/`，`.kiro/skills/amazon-ses/` 或 `~/.claude/skills/amazon-ses/`）：使用上述相对路径从本地技能目录读取文件。

这种区别仅适用于技能自身的捆绑文件。用户数据和会话工件始终从用户的当前工作目录读取和写入 — 永远不要通过 `retrieve_skill` 获取或写入客户数据。

## 关键规则

- **必须**使用 SES v2 API：`aws sesv2 ...`，绝不能使用 v1 `aws ses ...` 命令。v1 命令不会报告选择错误 API 的错误，因此错误是静默的，而此旅程需要的操作 — 生产访问请求，以及单个身份中 DKIM 和 MAIL FROM 属性的读取 — 仅存在于 v2 中。在已发布的 CLI 示例上训练的模型往往会默认使用 v1 语法。
- **绝不能**主动提供 API 版本机制、内部限制数字或其他管道。仅解释用户必须决定、同意、付费或采取行动的内容。仅在用户询问时、当用户的问题涉及它时，或当参考文件要求披露时才显示其余内容。
- **必须**在一个问题集中请求缺失的输入，而不是一次一个请求 — 并且**绝不能**请求请求不需要的输入。将问题范围限定为用户请求的内容：一个已经命名了域名和 MAIL FROM 子域的请求是一个完整的域名设置请求，因此读取状态并执行，而不是在发送时间或生产访问输入上停滞。如果为选定范围没有缺失的内容，则无需提问。
- **绝不能**在仍然可以解析的情况下询问使用哪个 AWS CLI 配置文件或区域。如果用户命名了一个配置文件，则仅尊重 `--profile`。**按以下顺序解析区域，取第一个有值的**：用户命名的区域；`AWS_REGION`；`AWS_DEFAULT_REGION`；`aws configure get region`，当用户命名了一个配置文件时添加 `--profile '{PROFILE}'`，因为配置文件可以携带自己的区域。最后一个命令仅读取 CLI 配置文件，并且**不会**看到环境，这就是为什么在它之前单独检查这两个环境变量的原因。**在任何修改之前声明解析的区域**，因为 SES 状态是按区域划分的，并且从 `aws sts get-caller-identity` 报告账户和主体。只有两种情况，并且只有这两种情况，你会询问：该链中没有产生区域，因为如果没有区域，每个 `aws sesv2` 调用都会失败；以及 `aws sts get-caller-identity` 在过期或无效凭证上失败，在这种情况下，一旦凭证刷新，请询问使用哪个账户（配置文件）和区域，因为配置默认值不再可信。将其中任何一个合并到一个问题集中，而不是花费额外的时间。
- **必须**将请求有效负载（更改批次和消息内容）作为内联 JSON 字符串传递给 CLI，绝不能作为 `file://` 路径 — `file://` 是 AWS-CLI 特有的，并且在通过 AWS MCP 服务器执行 CLI 时无法解析。
- **必须**在每一步之前读取当前状态并跳过已满足的步骤。特别是：永远不会为已经存在的身份调用 `create-email-identity`（它会返回 `AlreadyExistsException`），并且永远不会在 `DkimAttributes.Status` 为 `SUCCESS` 的身份上重新运行 `put-email-identity-dkim-signing-attributes`，因为重新初始化可能会更改其令牌。**根据状态而不是是否发布的 CNAME 解析来控制该调用** — 在一个 `FAILED` 身份上，记录通常会解析并且没有被尊重，这就是 `FAILED` 的含义，因此解析记录不是不提供恢复的原因。状态门控恢复路径，以及它们之前的前置 BYODKIM 检查，都属于 `setting-up-ses-domain-identity.md`。
- **对于域名设置，创建一个域名身份**。仅在用户明确选择验证该特定地址时，才创建电子邮件地址身份。

## 不变性

这些在技能的每个地方都成立。参考文件应用它们，并且可能在其上添加特定于工作流的详细信息 — 参考文件可以说明在特定步骤如何检查不变量，或针对该步骤的状态进行细化。它们都不能与这里写的内容相矛盾或放宽。

- **域名设置完成**意味着在一个 `aws sesv2 get-email-identity` 响应中，这三个都是真的：`VerifiedForSendingStatus` 是 `true`，**并且** `DkimAttributes.Status` 是 `SUCCESS`，**并且** `MailFromAttributes.MailFromDomainStatus` 是 `SUCCESS`。三个中的两个不完整。当 `MailFromDomainStatus` 是 `PENDING`、`FAILED` 或 `TEMPORARY_FAILURE` 时，AWS 文档指出 SES 使用自定义 MAIL FROM 回退设置：使用 `USE_DEFAULT_VALUE` 它使用 `amazonses.com` 的子域发送，因此 SPF 验证，但信封发件人与 `From` 域不匹配，DMARC 无法通过其 SPF 部分；使用 `REJECT_MESSAGE` SES 返回 `MailFromDomainNotVerified` 并不尝试投递。这是其余技能称为“域名设置完成”的关卡。
- **沙盒接收者规则**。当 `ProductionAccessEnabled` 为 `false` 时，AWS 文档指出你只能向经过验证的电子邮件地址和域名发送，或向 Amazon SES 邮箱模拟器发送。这意味着，按此技能始终呈现它们的顺序：(1) 作为其自身电子邮件身份经过验证的地址，(2) Amazon SES 邮箱模拟器，或 (3) 账户中任何经过验证域名的任何地址 — 不仅仅是刚设置的域名。限制是针对接收者，而不是发送者：一个完全经过验证的发送域名不会解除限制，你必须永远不会试图绕过它。**生产访问仅由 `ProductionAccessEnabled` 控制** — 当它是 `false` 时，这三个选项适用，无论 `Details.ReviewDetails.Status` 说什么。当你向用户解释限制时，你必须按相同的编号命名当前起作用的三个接收者选项，然后才建议生产访问作为补救措施，并且你绝不能描述限制为“每个接收者必须单独验证”：一个经过验证的**域名**涵盖该域名下的每个地址。
- **发送者也必须在每个账户状态下经过验证**。AWS 文档指出，在账户进入生产后，“你仍然必须验证所有你用作 'From'、'Source'、'Sender' 或 'Return-Path' 地址的身份。” 因此 `MessageRejected: Email address is not verified` 有两个原因：沙盒中的不许可接收者和任何状态下未经验证的发送身份。在选择修复措施之前，请先读取错误中命名的地址，并检查发件地址是否位于此区域中经过验证的域名或地址。
- **经过验证的发送者是 SES 服务的最低要求；此技能的旅程要求更多**。SES 本身会接受来自即使 DKIM 未达到 `SUCCESS` 也经过验证身份的发送。此技能故意不在此停止：其目标是**送达、经过认证**的第一封电子邮件，因此在它声称域名设置或认证完成之前，以及在它发送之前，它要求 `DkimAttributes.Status: SUCCESS`。这个更严格的门槛在 `onboarding.md` 的域名验证步骤中声明为发送先决条件，并且每个发送路径都适用它。两者并不冲突 — 一个是服务强制执行的，另一个是此旅程向用户承诺的。
- **验证每个替换值，然后在其上下文中引用它**。直接插入到 shell 命令中的值是单引号；放在内联 JSON 中的值是 JSON 编码（根据 JSON 规则使用双引号），并且整个 JSON 块对于 shell 是单引号的 — 永远不要在 JSON 内部对单个值进行 shell 引用。这适用于此技能替换的**每个**用户提供的值 — `DOMAIN`、MAIL FROM 子域、`FROM_ADDRESS`、`TEST_RECIPIENT`、`CHOSEN_RECIPIENT`、`MAIL_TYPE`、`WEBSITE_URL`、`REGION`、`PROFILE` — 不仅仅是域名。拒绝包含单引号或双引号、反引号、`$`、`;`、反斜杠或空白的值，并要求用户重新提供它；永远不要将拒绝的值转换为形状。每个值的形状：`DOMAIN` 和 MAIL FROM 子域 — 仅限 DNS 标签，字母、数字、连字符和点；发件地址和**每个接收者值，`TEST_RECIPIENT` 和 `CHOSEN_RECIPIENT` 一样** — 一个带有 `@` 的单个地址，并拒绝逗号分隔列表（将多个接收者放在 `ToAddresses` 数组中而不是）；`MAIL_TYPE` — 恰好是 `TRANSACTIONAL` 或 `MARKETING`；`WEBSITE_URL` — 一个 1–1000 个字符的 `http`/`https` URL，它**不必**位于经过验证的域名，因为与邮件相关的任何业务网站对 AWS 都是可接受的，因此问题集可以仅提供 `https://{DOMAIN}` 作为建议默认值；`REGION` — 一个 AWS 区域代码；`PROFILE` — 一个 CLI 配置文件名称。从技能提供的选项而不是用户而不是 `CHOSEN_RECIPIENT` 绑定的值 — 邮箱模拟器地址 — 以相同方式验证。使用序列化器对任何用户提供的主题或正文文本进行 JSON 编码，而不是将其粘贴在引号之间。

## IAM 权限

仅授予工作流实际调用的操作，并且不要多给 — 永远不要 `ses:*` 或 `*FullAccess`。每个参考文件都有一个 `Required IAM actions` 部分列出了它确实调用的内容；使用该列表，而不是通配符。

将每个身份操作的范围限定为每个调用实际操作的身份：

- `arn:aws:ses:{region}:{account-id}:identity/{domain}` 用于域名操作。
- `arn:aws:ses:{region}:{account-id}:identity/{address}` 用于电子邮件地址身份 — 用于沙盒接收者验证的身份，并且同样是在发送者是一个单独经过验证的电子邮件地址而不是域名中的地址时用作发件地址。仅限于域名的策略会拒绝这些调用。**读取的范围与相同**：`ses:GetEmailIdentity` 语句必须包含实际读取的每个身份的 ARN，这包括接收者地址身份 — 对于沙盒接收者选项 3 — 用户命名的其他经过验证域名的确切身份 ARN。仅限于发送域名的策略会拒绝该读取，该读取被视为损坏的权限而不是缺少接收者。**发送由覆盖其 From 地址的身份授权**，因此将 `ses:SendEmail` 范围限定为该身份；三种情况在 `onboarding.md` 的 `Required IAM actions` 中列出。
- 将 Route 53 区域操作 (`route53:GetHostedZone`、`route53:ListResourceRecordSets`、`route53:ChangeResourceRecordSets`) 路由到 `arn:aws:route53:::hostedzone/{hosted_zone_id}`，使用**裸**区域 ID — `list-hosted-zones-by-name` 返回 `/hostedzone/Z123ABC`，因此在构建 ARN 或结果之前删除该前缀，否则结果会双前缀并匹配不到任何内容。区域**读取**在代理检查 Route 53 是否托管域名时始终需要；只有 `route53:ChangeResourceRecordSets` 取决于用户批准写入。

仅授予真正账户级和列表操作 (`sts:GetCallerIdentity`、`ses:GetAccount`、`ses:ListEmailIdentities`、`route53:ListHostedZonesByName`、`route53:TestDNSAnswer`)，并且必须在 `*` 上授予。故意授予 `ses:PutAccountDetails`，因为它会更改账户范围的发送立场。

## 安全注意事项

- **临时凭证**。使用 IAM 角色与 STS — 永远不要使用长期访问密钥。
- **同意关卡**。打开生产访问审查和发送真实消息都会以 API 无法撤销的方式提交用户，并且 Route 53 更改可能会影响实时流量。每个关卡 — 生产访问同意关卡、发送确认和 DNS 写入权限 — 都由执行操作的参考文件拥有；永远不要因为此文件总结了它而继续进行下一步。
- **投递 TLS 默认情况下是机会主义的**。AWS 文档指出 SES 总是尝试与接收邮件服务器建立安全连接，如果无法建立，则不解密发送消息，并且要求 TLS 意味着设置配置集的 `TlsPolicy` 为 `REQUIRE` — 配置集工作流不在本技能的范围内。
- **在进入 shell 命令或内联 JSON 之前验证并引用每个用户提供的值**。规则和字符集在上述不变量中。
- **永远不要将消息正文或接收者列表记录在日志中**。
- **永远不要在示例中硬编码凭证、端点或密钥**。将任何应用程序凭证存储在 AWS Secrets Manager 或 Parameter Store 中。
- **为 SES API 调用审计启用 CloudTrail**，并对重复的 `AccessDeniedException` 和异常发送量触发警报。使用 AWS KMS 密钥（SSE-KMS）加密跟踪的日志文件，并限制对跟踪的 S3 桶和 CloudWatch 日志组的访问，并使用 KMS 密钥（`--kms-key-id` 在 `create-log-group`）加密该日志组 — SES CloudTrail 条目包含电子邮件地址、域名和账户详细信息。

## 其他资源

- [请求生产访问](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)
- [SES 域验证](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html)
- [SES 中的 DKIM](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dkim.html)
- [自定义 MAIL FROM](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html)
- [DMARC 认证](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html)
- [SESv2 API 参考](https://docs.aws.amazon.com/ses/latest/APIReference-V2/Welcome.html)
