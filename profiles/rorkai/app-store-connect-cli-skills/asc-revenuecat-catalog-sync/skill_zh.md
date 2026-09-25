# asc RevenueCat 目录同步

使用此功能来保持 App Store Connect (ASC) 和 RevenueCat 的一致性，包括创建缺失的 ASC 项目并将它们映射到 RevenueCat 资源。

## 使用场景
- 您希望从现有的 ASC 目录中启动 RevenueCat。
- 您希望创建缺失的 ASC 订阅/IAP，然后将它们映射到 RevenueCat。
- 您需要在发布前进行漂移审计。
- 您希望基于标识符进行确定性产品映射。

## 前置条件
- `asc` 认证已配置 (`asc auth login` 或 `ASC_*` 环境变量)。
- RevenueCat MCP 服务器已配置并认证。
- 在 Cursor 和 VS Code 中，RevenueCat MCP 提供 OAuth 认证。API 密钥认证也受支持。
- 您知道：
  - ASC 应用 ID (`APP_ID`)
  - RevenueCat `project_id`
  - 目标 RevenueCat 应用类型 (`app_store` 或 `mac_app_store`) 和用于创建流程的捆绑 ID
- 应用更改时使用具有写入权限的 RevenueCat API v2 密钥。

## 安全默认值
- 以 **审计模式**（只读）启动。
- 在写入前需要明确确认。
- 在此工作流中永远不会删除资源。
- 在每个项目失败时继续，并在末尾报告所有失败。

## 规范标识符
- 主要跨系统密钥：ASC `productId` == RevenueCat `store_identifier`。
- 产品上线后，`productId` 保持稳定。
- 不要使用显示名称作为唯一标识符。

## 范围边界
- RevenueCat MCP 配置 RevenueCat 资源；它不会直接创建 App Store Connect 产品。
- 在 RevenueCat 映射之前，使用 `asc` 命令创建缺失的 ASC 订阅组、订阅和 IAP。

## 模式

### 1) 审计模式（默认）
1. 读取 ASC 源目录。
2. 读取 RevenueCat 目标目录。
3. 构建包含操作的差异：
   - ASC 中缺失
   - RevenueCat 中缺失
   - 映射冲突（标识符/类型/应用不匹配）
4. 展示计划。仅审计请求以发现结果结束；应用请求需要涵盖完整当前差异的批准。如果刷新的差异未更改，则可重用先前的批准。

### 2) 应用模式（显式）
按顺序执行已批准的操作：
1. 确保 ASC 组/订阅/IAP 存在。
2. 确保 RevenueCat 应用/产品存在。
3. 确保 权限和产品附件。
4. 确保 提供方案/包和包附件。
5. 验证并打印最终对账摘要。

## 分步工作流

### 步骤 A - 读取当前 ASC 目录

```bash
asc subscriptions groups list --app "APP_ID" --paginate --output json
asc iap list --app "APP_ID" --paginate --output json
# 对于每个订阅组：
asc subscriptions list --group-id "GROUP_ID" --paginate --output json
```

### 步骤 B - 读取当前 RevenueCat 目录（MCP）

使用这些 MCP 工具（适用时使用 `project_id` 和分页）：
- `mcp_RC_get_project`
- `mcp_RC_list_apps`
- `mcp_RC_list_products`
- `mcp_RC_list_entitlements`
- `mcp_RC_list_offerings`
- `mcp_RC_list_packages`

### 步骤 C - 构建映射计划

将 ASC 产品类型映射到 RevenueCat 产品类型：
- ASC 订阅 -> RevenueCat `subscription`
- ASC IAP `CONSUMABLE` -> RevenueCat `consumable`
- ASC IAP `NON_CONSUMABLE` -> RevenueCat `non_consumable`
- ASC IAP `NON_RENEWING_SUBSCRIPTION` -> RevenueCat `non_renewing_subscription`

建议的权限策略：
- 订阅：每个订阅组一个权限（或用户提供显式映射）
- 非消耗型 IAP：每个产品一个权限
- 消耗型 IAP：默认无权限，除非用户请求

### 步骤 D - 确保缺失的 ASC 项目（如果请求）

在写入前解决每个父级和版本。按确切引用名称匹配组，按 `productId` 匹配产品；永远不要将显示名称视为身份。资源已存在时重用规范 ID，当完全分页读取证明其缺失时才运行创建命令。RevenueCat 产品映射不能证明相应的 ASC 订阅已准备好审核。

```bash
# 通过确切 referenceName 解析 GROUP_ID。
asc subscriptions groups list --app "APP_ID" --paginate --output json
# 仅当完全分页列表为零确切匹配时：
asc subscriptions groups create --app "APP_ID" --reference-name "Premium" --output json
# 匹配一个，重用其 ID。超过一个，停止并要求明确的 GROUP_ID。

# 在 GROUP_ID 内通过确切 productId 解析 SUB_ID。仅针对缺失的父级或相同产品 ID 的明确批准的协调运行设置。
asc subscriptions list --group-id "GROUP_ID" --paginate --output json
# 仅当完全分页列表为零确切匹配时，运行设置：
asc subscriptions setup \
  --app "APP_ID" \
  --group-id "GROUP_ID" \
  --reference-name "Monthly" \
  --product-id "com.example.premium.monthly" \
  --subscription-period ONE_MONTH \
  --review-screenshot "./review.png" \
  --price "3.99" \
  --price-territory "USA" \
  --territories "USA" \
  --no-verify \
  --output json
# 匹配一个，重用其 ID。超过一个，停止并要求明确的 SUB_ID。
# 仅对现有 SUB_ID 运行设置，如果存在明确批准的协调。

# 解析此审核生命周期中唯一的可变组版本。
asc subscriptions groups versions list --group-id "GROUP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 仅当列表为零匹配时：
asc subscriptions groups versions create --group-id "GROUP_ID" --output json
# 匹配一个，重用 .data[0].id。超过一个，停止并要求明确的 GROUP_VERSION_ID。

# 解析 GROUP_VERSION_ID 上的 en-US 本地化。仅当缺失时创建；当其值不同时更新解析的本地化 ID。
asc subscriptions groups versions localizations list --version-id "GROUP_VERSION_ID" --paginate --output json
asc subscriptions groups versions localizations create --version-id "GROUP_VERSION_ID" --locale "en-US" --name "Premium" --output json
asc subscriptions groups versions localizations update --id "GROUP_LOC_ID" --name "Premium"

# 解析此审核生命周期中唯一的可变订阅版本。
asc subscriptions versions list --subscription-id "SUB_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 仅当列表为零匹配时：
asc subscriptions versions create --subscription-id "SUB_ID" --output json
# 匹配一个，重用 .data[0].id。超过一个，停止并要求明确的 SUBSCRIPTION_VERSION_ID。
asc subscriptions versions localizations list --version-id "SUBSCRIPTION_VERSION_ID" --paginate --output json
asc subscriptions versions localizations create --version-id "SUBSCRIPTION_VERSION_ID" --locale "en-US" --name "Premium Monthly" --description "Unlock all premium features." --output json
asc subscriptions versions localizations update --id "SUBSCRIPTION_LOC_ID" --name "Premium Monthly" --description "Unlock all premium features."

# 读取上述确切版本，然后运行最终严格验证器。
asc subscriptions groups versions localizations list --version-id "GROUP_VERSION_ID" --paginate --output table
asc subscriptions versions localizations list --version-id "SUBSCRIPTION_VERSION_ID" --paginate --output table
asc validate subscriptions --app "APP_ID" --strict --output table

# 通过确切 productId 解析 IAP_ID。
asc iap list --app "APP_ID" --paginate --output json
# 仅当完全分页列表为零确切匹配时：
asc iap create \
  --app "APP_ID" \
  --type NON_CONSUMABLE \
  --ref-name "Lifetime" \
  --product-id "com.example.lifetime" \
  --output json
# 匹配一个，重用其 ID。超过一个，停止并要求明确的 IAP_ID。

# 解析此审核生命周期中唯一的可变 IAP 版本。
asc iap versions list --iap-id "IAP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 仅当列表为零匹配时：
asc iap versions create --iap-id "IAP_ID" --output json
# 匹配一个，重用 .data[0].id。超过一个，停止并要求明确的 IAP_VERSION_ID。
asc iap versions localizations list --version-id "IAP_VERSION_ID" --paginate --output json
asc iap versions localizations create --version-id "IAP_VERSION_ID" --locale "en-US" --name "Lifetime" --description "Unlock all premium features." --output json
asc iap versions localizations update --localization-id "IAP_LOC_ID" --name "Lifetime" --description "Unlock all premium features."
asc iap versions localizations list --version-id "IAP_VERSION_ID" --paginate --output table
```

上述相邻的创建/更新对是条件性的，不是盲目运行序列：列表无匹配时创建，解析匹配项值不同时更新，已匹配时则不操作。从创建响应中捕获 `.data.id` 或从前列表中捕获 `.data[].id` 作为后续命令使用的规范 ID。对于每个版本列表，零 `PREPARE_FOR_SUBMISSION` 匹配意味着创建，一个意味着重用该 ID，超过一个意味着停止并要求用户选择明确的版本 ID。不要创建版本来解决歧义：父级删除在实时测试中未可靠级联 IAP 或订阅版本。

`subscriptions setup` 完成父级、App Review 照片交付、完整 App Store 价格矩阵和销售可用性。版本范围命令完成 RevenueCat 无法处理的组和订阅本地化。将销售可用性限制在请求的区域；价格仍需 Apple 的完整均衡区域矩阵。`--no-verify` 在此分割工作流中是故意的，因为最终验证必须等到版本元数据存在；显式读取回调和验证器是最终关卡。

如果现有 API 创建的订阅即使在选定的基础价格未更改的情况下仍为 `MISSING_METADATA`，请使用 `--repair` 重新运行相同的设置输入。修复原子性地重建和重新保存完整的均衡价格矩阵；它不是重复的单价 POST。

对于每个解析的 ASC 订阅，在创建或附加其 RevenueCat 产品之前需要此最终关卡。即使订阅及其选定的版本在未进行任何 ASC 写入的情况下被重用，也要在最终 ASC 对账后运行它：

```bash
mkdir -p "./audit"
asc validate subscriptions --app "APP_ID" --strict --output json --pretty \
  > "./audit/subscriptions-validation.json"
```

对于每个解析的 ASC IAP，在创建或附加其 RevenueCat 产品之前需要 IAP 关卡。即使 IAP 及其选定的版本在未进行任何 ASC 写入的情况下被重用，也要在最终 ASC 对账后运行它：

```bash
mkdir -p "./audit"
asc validate iap --app "APP_ID" --strict --output json --pretty \
  > "./audit/iap-validation.json"
```

这两个命令都是严格映射关卡，不是写入后的冒烟测试。验证报告警告、错误、`MISSING_METADATA`、未完成的审核照片或价格覆盖不完整或未验证时，不要映射任何解析或重用的订阅。当其验证器报告警告或错误时，不要映射任何解析或重用的 IAP。零写入审计或应用运行必须执行适用的关卡，并在 RevenueCat 产品创建或附加之前要求零退出状态。直接重定向保留每个验证器的退出状态。保留 `./audit/subscriptions-validation.json` 和 `./audit/iap-validation.json` 作为最终审计证据。

### 步骤 E - 确保 RevenueCat 应用和产品

使用 MCP：
- 缺失时创建应用：`mcp_RC_create_app`
- 创建产品：`mcp_RC_create_product`
  - `store_identifier` = ASC `productId`
  - `app_id` = RevenueCat 应用 ID
  - `type` 来自上述映射

### 步骤 F - 确保 权限和附件

使用 MCP：
- 列表/创建权限：`mcp_RC_list_entitlements`，`mcp_RC_create_entitlement`
- 附加产品：`mcp_RC_attach_products_to_entitlement`
- 验证附件：`mcp_RC_get_products_from_entitlement`

### 步骤 G - 确保 提供方案和包（可选）

使用 MCP：
- 列表/创建/更新提供方案：
  - `mcp_RC_list_offerings`
  - `mcp_RC_create_offering`
  - `mcp_RC_update_offering` (`is_current=true` 仅当请求时)
- 列表/创建包：
  - `mcp_RC_list_packages`
  - `mcp_RC_create_package`
- 附加产品到包：
  - `mcp_RC_attach_products_to_package` 使用 `eligibility_criteria: "all"`

推荐的包键：
- `ONE_WEEK` -> `$rc_weekly`
- `ONE_MONTH` -> `$rc_monthly`
- `TWO_MONTHS` -> `$rc_two_month`
- `THREE_MONTHS` -> `$rc_three_month`
- `SIX_MONTHS` -> `$rc_six_month`
- `ONE_YEAR` -> `$rc_annual`
- 终身 IAP -> `$rc_lifetime`
- 自定义 -> `$rc_custom_<name>`

## 预期输出格式

返回最终摘要，包括：
- ASC 创建计数（组/订阅/IAP）
- RevenueCat 创建计数（应用/产品/权限/提供方案/包）
- 附件计数（权限-产品，包-产品）
- 跳过的现有项目
- 失败项目及可操作错误

示例：

```text
ASC: created groups=1 subscriptions=2 iap=1, skipped=14, failed=0
RC: created apps=0 products=3 entitlements=2 offerings=1 packages=2, skipped=27, failed=1
Attachments: entitlement_products=3 package_products=2
Failures:
- com.example.premium.annual: duplicate store_identifier exists on another RC app
```

## 代理行为
- 始终先运行审计，即使在应用模式下。
- 重用涵盖完整当前差异的批准用于其创建/更新操作。仅在批准缺失或附加或实质性更改的操作超出其范围时再次询问。
- 首先通过 `store_identifier` 匹配。
- 使用完整分页（`--paginate` for ASC，`starting_after` for RevenueCat 工具）。
- 在每个项目失败后继续处理，并一起报告所有失败。
- 在此技能中永远不会自动删除 ASC 或 RevenueCat 资源。
- 对于每个解析的订阅，包括重用的无写入匹配，运行 `asc validate subscriptions --app "APP_ID" --strict --output json --pretty`，保存其 JSON，并在 RevenueCat 创建或附加之前阻止，除非关卡以零状态退出且无缺失元数据或不完整价格。

- 对于每个解析的 IAP，包括重用的无写入匹配，运行 `asc validate iap --app "APP_ID" --strict --output json --pretty`，保存其 JSON，并在 RevenueCat 创建或附加之前阻止，除非关卡以零状态退出。

## 常见陷阱
- 错误的 RevenueCat `project_id` 或应用 ID。
- 在错误平台应用下创建 RC 产品。
- 意外将消耗型产品分配给权限。
- 跳过创建后的 ASC 重新读取步骤。
- 在 ASC 设置完成本地化、审核照片交付、完整价格矩阵和可用性之前映射 RevenueCat 产品。
- 产品创建后缺少提供方案/包验证。

## 额外资源
- 工作流示例：[examples.md](examples.md)
- 源引用：[references.md](references.md)
