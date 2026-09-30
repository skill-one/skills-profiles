---
name: platform-trial-org-create
description: 使用此技能创建 Salesforce 试用版、开发者版或 Trialforce 组织，目标是对已认证的主组织进行操作，就像开发者/Trialforce 网页注册表单进行配置一样。当用户要求创建试用组织、注册新的试用版或开发者组织、从模板配置 Trialforce 组织，或检查他们启动的试用组织注册状态时，请调用该技能。触发短语：'创建试用组织'、'注册试用组织'、'创建开发者组织'、'Trialforce 注册'、'从模板配置试用组织'、'检查我的试用组织注册状态'。不要用于从零开始创建组织（使用 dx-org-manage），也不要用于检查现有组织的试用到期日期（使用 dx-org-trial-expiration-check）。
---

## 这个技能的作用

通过插入 `SignupRequest` sObject 使用 `sf` CLI 创建 Salesforce **试用组织** — 这与 Trialforce/开发者 **网络注册表单** 在底层使用的相同请求。没有专门的注册端点：注册 = 向经过身份验证的 **主机组织**（有权创建试用组织的 Trialforce 源组织 / 环境中心 / 合作伙伴组织）插入 `SignupRequest`（键前缀 `0SR`）。

流程是 **两个 CLI 调用**：(1) 创建 `SignupRequest`，(2) 读取它以获取分配的组织 ID（创建是异步的 — 组织 ID 在插入后不久出现）。

## 前提条件 — 执行前确认

1. **经过身份验证的主机组织 — 始终明确确认。** 您是从经过身份验证的主机组织注册，而不是匿名注册。`sf` CLI 对您已经登录过的组织（`sf org login web` 或 `sf org login`）进行操作。

   **始终在每个命令中传递明确的 `--target-org` (`-o`）以及主机组织的别名或用户名，并在创建前与用户确认目标** — 即使配置了默认组织也是如此。创建 `SignupRequest` 是一个真实的配置动作；不要让它针对任何默认组织运行。

   - **不要依赖默认组织的回退。** 没有 `-o`，CLI 从 `--target-org` → `SF_TARGET_ORG` 环境变量 → 本地然后全局 `target-org` 配置解析目标，如果没有设置则**出现错误 (`NoDefaultEnvError`)** — 它从不自动选择您的连接组织。该默认值可能是一个无关的 dev/scratch 组织，因此省略 `-o` 要么是错误组织，要么是硬错误。永远不要省略它。
   - **用户可能有多个经过身份验证的组织。** 运行 `sf org list`，如果预期的主机组织不明确或未提供，请询问用户要使用哪个别名/用户名。不要猜测。
   - **在创建前验证所选组织在 `sf org list` 中是否为 `Connected`**（陈旧的刷新令牌 / 过期的证书显示为错误状态，而不是 `Connected`）。
   - 永远不要编造凭证。
2. **主机组织必须有权创建试用组织**，并且调用用户必须在其中具有足够的权限。该技能**不会**运行单独的权限检查 — `sf data create record` 调用（步骤 1）是决定性的门控，检查将依赖相同的 API 强制执行。如果组织没有权，则 `SignupRequest` 实体不会公开，创建会以非零 `status` 和 `name`/`code` 的 `NOT_FOUND`（"请求的资源不存在"）或 `INVALID_TYPE`（"sObject 类型 'SignupRequest' 不受支持"）失败。此情况在步骤 1 的错误表中处理。

   当发生这种情况时，**停止**（它不能从 CLI 重试）并向用户报告：(a) **原始 CLI 错误原样** — CLI 返回的确切 `name`/`errorCode` 和 `message` — 以及 (b) 他们应该**联系 Salesforce 支持以启用组织试用组织创建功能，然后重试。** **不要诊断或命名缺少的权限** — 只需显示原始错误并将他们指向支持。

## 必须输入 — 在任何创建之前从调用用户那里收集

提示用户输入这些内容，并且**在提供所有内容之前不要继续**。不要编造值。**逐一询问；如果用户对某个字段不确定，请使用“如果用户不确定”列中的内容进行指导，然后再继续。**

**始终需要（5）** — 这些在 `SignupRequest` 实体上是 `required="true"`（`FirstName` 列出在这里是为了提示方便，但它是**可选**的）：

| 输入 | 备注 | 如果用户不确定 |
|-------|-------|-----------------------|
| `LastName` | 管理员的姓氏。最多 80 个字符。 | 任何新组织管理员用户的姓氏；它只是管理员联系人姓名，使用他们的。 |
| `FirstName` | **可选。** 管理员的名字。询问它，但如果用户不提供，则可以没有它继续。 | 可选 — 如果不确定，请留空；管理员用户只需要 `LastName`。 |
| `Username` | 管理员登录用户名。必须为 **电子邮件格式** 并在所有 Salesforce 组织中**全局唯一**。最多 80 个字符。保存时转换为小写。 | 它不必是一个真实的收件箱 — 它只需要看起来像电子邮件并且是唯一的。建议使用模式 `admin@<company>-<something-unique>.com`。如果冲突，您在创建时会收到重复用户名错误；选择另一个。 |
| `SignupEmail` | 管理员用户的**真实**电子邮件地址（欢迎/登录邮件将发送到此地址）。 | 这个必须是他们可以访问的**工作**收件箱 — 与 `Username` 不同，它应该是真实地址。 |
| `Company` | 公司/组织名称。最多 80 个字符。 | 要在试用组织中显示的组织名称；任何描述性名称都可以。 |
| `Country` | **ISO 国家代码**，最多 3 个字符，例如 `US`，`GB`，`IN`，`DE`。在运行时验证允许的代码（被冻结/无效的代码被拒绝）。 | 使用他们国家的 2 字母 ISO 代码（例如 `US` 代表美国，`GB` 代表英国）。不是自由文本国家名称。 |

**必须选择其中之一（必须选择一个，不能两者都选）：**

| 输入 | 备注 | 如果用户不确定 |
|-------|-------|-----------------------|
| `TemplateId` | Trialforce 模板 ID（键前缀 `0TT`，15 个字符）— 定义试用组织的产品/内容。 | 当他们想要特定的预构建产品/内容集时使用模板。要查找可用模板，请查询主机组织：`sf data query -o <HOST_ORG> -q "SELECT Id, TemplateName FROM TrialforceTemplate" --json`。如果他们只是想要一个普通的试用组织，请使用 `Edition`。 |
| `Edition` | 通用（非模板）试用组织的组织版本。通用值：`Developer`，`Group`，`Professional`，`Enterprise`（也 `ServiceProfessional`，`SalesEnterprise`）。合作伙伴/Trialforce 版本被永久锁定。 | 如果他们只是想要“一个用于尝试的 dev 组织”，请使用 `Developer`。合作伙伴版本（`PARTNER_*`，`TRIALFORCE_*`）只有在主机组织具有合作伙伴/TMC 权限时才有效 — 没有权限使用它们会返回 `noPartnerAccess` 错误。 |

询问用户选择**其中之一**的 `TemplateId` **或** `Edition`，而不是两者：
- **两者都不提供** → 停止并询问。没有模板和没有版本的创建会因 `missingEdition` (`ApiErrorCodes.INVALID_SIGNUP_OPTION`) 而失败。
- **两者都提供** → 请他们选择一个；只发送选择的字段。将它们组合在一起会失败，带有 `redundantTemplateId` 错误。它们不能与克隆/源组织字段组合使用。

此技能有意将用户收集的输入限制在上述字段（5 个始终需要的加上可选的 `FirstName`）。**不要**提示或显示其他字段。`SignupRequest` 实体支持其他可选和永久锁定的字段（`TrialDays`，`Subdomain`，`PreferredLanguage`，`SignupSource`，OAuth 返回对等体等.）；这些**不在此范围内**，留给服务器默认值。它们在 `references/signup_request_fields.md` 中仅作为参考记录 — 不要从此技能发送它们。

## 步骤 1 — 创建 SignupRequest

使用收集的输入调用创建脚本。它强制执行“`TemplateId`/`Edition` 其中一个”规则，组装并引用 `--values` 负载，运行插入，并在成功时打印分配的 `0SR…` ID。通过技能目录的**绝对路径**引用脚本（`<skill_dir>/scripts/…`） — 永远不要 `./scripts/`，它相对于用户的当前工作目录解析。

**使用模板：**
```bash
SR_ID=$(bash "<skill_dir>/scripts/create_signup_request.sh" \
  --target-org <HOST_ORG> \
  --last-name <LAST_NAME> --email <EMAIL> --username <UNIQUE_USERNAME> \
  --company "<COMPANY>" --country <ISO> --template-id 0TT... \
  --output-dir force-app/main/adk-eval-output)
```

**使用版本（通用试用，无模板）：** 将 `--template-id 0TT...` 替换为 `--edition Developer`（或 `Enterprise` 等）。仅在用户提供了它时添加 `--first-name <NAME>` — 此技能不会发送其他可选字段。脚本拒绝提供 `--template-id` 和 `--edition`，或两者都不提供。

传递 `--output-dir`（当它存在时使用 `force-app/main/adk-eval-output`）以便如果创建**被拒绝**，脚本仍然写入 `<output-dir>/signup-request-result.json` 捕获创建拒绝的结果和原始错误**原样** — 即使没有创建组织，此运行输出工件也是如此。成功时此写入由步骤 2 读取回代替换。

成功时脚本会打印 `0SR…` SignupRequest ID（将其捕获为 `SR_ID`）。传递 `--json` 而不是获取原始 `sf` 创建信封，该信封包装一个**句柄**，而不是组织：
```json
{ "status": 0, "result": { "id": "0SRxx0000000000", "success": true, "errors": [] } }
```

**处理创建错误（同步字段验证）。** 在创建被拒绝时，脚本会退出非零并打印**原始 CLI 错误**（`name`/`code` + `message`）到 stderr — 原样显示它并按照下表中的说明操作。当 `--output-dir` 被提供时，脚本还会将创建拒绝的工件（`{ "outcome": "create-rejected", "error": {…}, "CreatedOrgId": null, "Status": null }`）写入 `<output-dir>/signup-request-result.json`；不要手写此文件。这是字段验证，立即返回 — 与步骤 2 中的异步 `ErrorCode` 不同。这些是**服务器端**拒绝（记录到达组织并在插入时由平台拒绝） — 不要将它们描述为“客户端”；CLI 不在本地验证电子邮件/国家格式、选择列表值或字段长度。不要轮询失败的创建，也不要继续到步骤 2。

| 失败 | 含义 → 告诉用户什么 |
|---------|---------------------------------|
| `missingEdition` / `INVALID_SIGNUP_OPTION` | 未发送 `TemplateId` 或 `Edition` — 询问一个并重试。 |
| `redundantTemplateId` | 同时发送了 `TemplateId` 和 `Edition` — 放弃一个并重试。 |
| `noPartnerAccess` / `NO_PARTNER_PERMISSION` | 请求了合作伙伴/TSO 版本，但主机组织缺乏权限 — 使用通用版本（`Developer` 等）或获取权限。 |
| duplicate / invalid `Username` (`INVALID_EMAIL_ADDRESS`) | `Username` 不是电子邮件格式或不是全局唯一 — 询问一个不同的并重试。 |
| `INVALID_SIGNUP_COUNTRY` | `Country` 不是有效的/允许的 ISO 代码 — 修复并重试。 |
| `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST` | `Edition` 不是主机组织限制选择列表的接受值（例如 `Ultimate`） — 选择一个有效的通用版本并重试。 |
| `STRING_TOO_LONG` | 字段值超过最大长度（消息命名字段 + `max length`，例如 `LastName` 超过 80）— 缩短它并重试。 |
| `subdomainInUse` / 无效子域 | 所选 `Subdomain` 已被占用或无效 — 选择另一个。 |
| `NOT_FOUND` ("请求的资源不存在") 或 `INVALID_TYPE` ("sObject 类型 'SignupRequest' 不受支持") | `SignupRequest` 实体未公开 → 组织没有权创建试用组织。**不能**重试。停止并原样显示**原始 CLI 错误**（`name`/`errorCode` + `message`），然后告诉用户**联系 Salesforce 支持以启用组织**。**不要**命名或诊断缺少的权限。 |
| `INSUFFICIENT_ACCESS_OR_READONLY` | 实体已公开，但*用户*缺乏创建记录的权限 — 一个用户权限问题，与上述组织权能失败不同。修复用户的权限并重试。 |

对于完整目录和前缀 → `references/error_codes.md`。

- 对于完整必需/可选字段列表、类型和永久锁定字段 → 加载 `references/signup_request_fields.md`。
- 不要将 `TemplateId` 与克隆/源组织字段一起发送（`redundantTemplateId` 错误）。不要在没有主机组织合作伙伴/TMC 权限的情况下请求合作伙伴/Trialforce 版本。

## 步骤 2 — 组织 ID 可用后读取请求（创建是异步的）

配置在插入后异步发生，因此重新读取记录以获取分配的组织 ID。调用读取脚本 — 它在内部应用固定的、有界的读取回政策（一旦 `CreatedOrgId` 被填充或状态为终端就停止，并且永远不会无限期轮询），打印记录为 JSON，并在提供 `--output-dir` 时写入输出工件。然后根据脚本的**退出代码**（如下所示）操作 — 重试计数和延迟是脚本自己的确定性逻辑；您不需要在文本中重新实现或重新计数它们。如果组织 ID 尚未可用，脚本退出 `3`，您可以手将请求 ID 回给用户：

```bash
bash "<skill_dir>/scripts/get_signup_request.sh" \
  --target-org <HOST_ORG> --id "$SR_ID" [--output-dir <DIR>]
```

脚本将 `SignupRequest` 记录（`sf` 信封的 `result`）作为 JSON 打印。从它读取这些字段：
- `CreatedOrgId` — 新试用组织 ID（`00D…`，15 个字符）。一旦组织被分配（即使 `Status` 仍然是 `InProgress`），它就会被填充；这是脚本的停止信号。
- `CreatedOrgInstance` — 托管新组织的实例（在此处进行后续调用）。
- `Username` — 记录上的管理员登录用户名。报告从记录中**读取的值**，而不是原始输入 — 它在保存时转换为小写，因此存储的值是准确的值，要交给用户。
- `Status` — 生命周期 `New` → `InProgress` → `Success` | `Error`（大小写匹配）。
- `LoginUrl` — 仅当在创建时设置了 `IsSyncLogin`（永久锁定）时才存在。
- `AuthCode` — 仅当设置了 `ConnectedAppConsumerKey` + `ConnectedAppCallbackUrl` 时才存在。
- `ErrorCode` — 仅当 `Status = Error` 时填充。这是*异步配置*错误（与步骤 1 中的同步创建时验证不同），前缀为：
  - `C-` 组织创建错误 · `S-` 注册数据错误 · `T-` 模板错误（例如 `T-0002` = 模板未找到） · `SH-` 组织形状错误 · `VR-` 版本选择错误 · `X-0001`/`X-0002` 致命/不应该发生。

根据脚本的退出代码操作。**组织 ID 查找首先运行 — 在脚本返回之前不要向用户报告任何内容。** 只报告实际记录上的内容；永远不要编造或重新标记 `Status`：
- **`0`** — `CreatedOrgId` 已填充。继续到步骤 3 并报告组织 ID，以及记录的真实 `Status` 和 `Username`。
- **`3` — 组织 ID 尚未可用（不是错误）。** 组织尚未分配。脚本已经耗尽了有界读取回 — **不要**在循环中重新调用它以保持轮询。报告 **SignupRequest id (`0SR…`)**，记录的**`Status` 恰如返回**，以及 `Username`；告诉用户组织 ID 尚未可用，让他们稍后重新检查（见步骤 3）。
- **`1`** — `Status = Error`（停止并报告 `ErrorCode` 及其前缀含义，通过 `references/error_codes.md`；组织未创建），或读取本身失败（认证过期，`0SR` id 未找到） — 显示原始 CLI 错误并停止。

## 步骤 3 — 报告详细信息和状态检查交接

在步骤2查询返回后报告——而不是之前。当用户请求创建（或重新检查）组织时，应先执行读取操作并等待结果，然后一次性向用户报告所有可用详细信息。仅报告记录中的内容；切勿编造或重新标记值——特别是`Status`，它必须是响应对象携带的确切字符串：

- **SignupRequest id** — 步骤1中的`0SR…`请求id。**始终报告此信息**——这是用户（或后续检查）用于再次查询请求的句柄，如果组织id尚未可用，这是需要返回的主要信息。
- **CreatedOrgId** — 新试用组织id（`00D…`），当其被填充时。如果读取操作返回退出码`3`（组织id尚未可用），请明确说明：请求已接受，组织仍在配置中；目前无法分享组织id。
- **CreatedOrgInstance** — 如果存在，则为承载该组织的实例。
- **Username** — 管理员登录用户名**按记录存储**（保存时转为小写）。始终报告此信息——这是组织准备好后用户登录使用的用户名。
- **Status** — 记录中出现的`Status`值**确切内容**。回显响应携带的任何字符串；不要映射、翻译、推断或从固定列表中选择。在此阶段状态仍为待处理是正常的——配置在后台完成。
- **LoginUrl** / **AuthCode** — 仅当存在时。

同时告知用户**新组织的登录详情通过电子邮件发送**——一旦配置完成，将向`SignupEmail`地址发送欢迎/登录电子邮件，因此他们应关注该收件箱以完成登录。（这就是为什么`SignupEmail`必须是一个真实、可访问的地址。）

然后用平实的语言建议用户如何稍后重新检查状态——配置可能仍在进行中。告诉他们可以直接询问（技能将重新读取记录），例如：
- "检查我的试用组织**`00D…`**的状态"（通过组织id），或
- "检查注册请求**`0SR…`**的状态"（通过SignupRequest id）。

两者都会触发对同一`SignupRequest`记录的步骤2读取脚本的重新运行（组织id在该记录中查询）。后续检查应报告记录返回的当前`Status`**确切内容**。如果记录返回错误状态，还应通过`references/error_codes.md`报告`ErrorCode`及其前缀含义。

**输出工件。** 通过向步骤2读取脚本传递`--output-dir`将当前`SignupRequest`记录作为运行输出工件写入——脚本将写入`<output-dir>/signup-request-result.json`（如果需要则创建目录）。当存在时使用`force-app/main/adk-eval-output`作为输出目录：

```bash
bash "<skill_dir>/scripts/get_signup_request.sh" \
  --target-org <HOST_ORG> --id "$SR_ID" \
  --output-dir force-app/main/adk-eval-output
```

这是运行定义的输出——无需事先请求权限即可写入。

## 参考文件索引

| 文件 | 何时读取 |
|------|-------------|
| `references/signup_request_fields.md` | 完整字段参考——必需/可选字段、类型、默认值、权限控制字段、版本 |
| `references/error_codes.md` | 解释`ErrorCode`前缀和常见验证失败 |

## 示例文件

仅在需要查看有效载荷或响应的具体形状时加载这些文件——它们是带有占位符id（`0SRxx…`、`00Dxx…`）的说明性示例，不是要发送的值。

| 文件 | 何时读取 |
|------|-------------|
| `examples/create_request.json` | 在组装创建时——确认`SignupRequest`创建有效载荷的字段名称/形状 |
| `examples/success_response.json` | 在解释成功创建+读取回时——显示`CreatedOrgId`填充后的记录 |
| `examples/error_response.json` | 在解释创建失败时——显示常见验证/错误响应的形状 |
