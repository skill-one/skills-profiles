# 按地区定价 (PPP定价)

使用此功能根据购买力平价 (PPP) 或您自己的区域定价策略创建或更新跨地区的本地化定价。

优先使用当前的高层流程：
- `asc subscriptions setup` 和 `asc iap setup` 用于父项创建和定价，
  然后是版本范围的元数据命令
- `asc subscriptions pricing ...` 用于订阅定价更改
- `asc iap pricing summary` 和 `asc iap pricing schedules ...` 用于IAP定价更改

## 前置条件
- 确保凭证已设置 (`asc auth login` 或 `ASC_*` 环境变量)。
- 优先使用 `ASC_APP_ID` 或显式传递 `--app`。
- 确定您的基准地区（通常是 `USA`）和基线价格。
- 如果您需要支持的地区ID，请使用 `asc pricing territories list --paginate`。

## 订阅PPP工作流

### 新订阅：使用 `setup` 引导父项和定价
使用 `setup` 创建组和订阅，上传App Review截图，形成完整的等价价格矩阵，并设置销售可用性。之后创建API 4.4.1的组和订阅版本；`setup` 上的本地化标志使用已弃用的v1资源，不得用于新工作流。

```bash
asc subscriptions setup \
  --app "APP_ID" \
  --group-reference-name "Pro" \
  --reference-name "Pro Monthly" \
  --product-id "com.example.pro.monthly" \
  --subscription-period ONE_MONTH \
  --review-screenshot "./review.png" \
  --price "9.99" \
  --price-territory "USA" \
  --territories "USA,CAN,GBR" \
  --no-verify \
  --output json
```

从设置JSON中捕获 `.groupId` 和 `.subscriptionId`，然后添加版本范围的元数据。`--no-verify` 是有意为之的：在没有弃用的v1本地化的情况下，父项可以保持 `MISSING_METADATA`，直到v2步骤完成。

```bash
asc subscriptions groups versions list --group-id "GROUP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 如果列表为零匹配：
asc subscriptions groups versions create --group-id "GROUP_ID" --output json
# 如果有一个匹配，重用 .data[0].id。如果有多个，停止并要求显式的 GROUP_VERSION_ID。
asc subscriptions groups versions localizations list --version-id "GROUP_VERSION_ID" --paginate --output json
# 如果只有 en-US 缺失：
asc subscriptions groups versions localizations create --version-id "GROUP_VERSION_ID" --locale "en-US" --name "Pro"
# 否则，如果解析的 en-US 名称不同：
asc subscriptions groups versions localizations update --id "GROUP_LOC_ID" --name "Pro"
# 否则，不做任何事。

asc subscriptions versions list --subscription-id "SUB_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 如果列表为零匹配：
asc subscriptions versions create --subscription-id "SUB_ID" --output json
# 如果有一个匹配，重用 .data[0].id。如果有多个，停止并要求显式的 SUBSCRIPTION_VERSION_ID。
asc subscriptions versions localizations list --version-id "SUBSCRIPTION_VERSION_ID" --paginate --output json
# 如果只有 en-US 缺失：
asc subscriptions versions localizations create --version-id "SUBSCRIPTION_VERSION_ID" --locale "en-US" --name "Pro Monthly" --description "Unlock everything"
# 否则，如果解析的 en-US 值不同：
asc subscriptions versions localizations update --id "SUBSCRIPTION_LOC_ID" --name "Pro Monthly" --description "Unlock everything"
# 否则，不做任何事。
asc subscriptions groups versions localizations list --version-id "GROUP_VERSION_ID" --paginate --output table
asc subscriptions versions localizations list --version-id "SUBSCRIPTION_VERSION_ID" --paginate --output table
asc validate subscriptions --app "APP_ID" --output table
```

对于每个版本列表，重用其单个 `PREPARE_FOR_SUBMISSION` 结果。当结果为空时才创建；如果返回多个结果，停止并要求显式的版本ID，而不是创建另一个不可删除的版本。每个本地化创建/更新对也是条件性的：为缺失的语言环境创建，仅当值不同时更新已解析的本地化，否则不做任何事。

注意：
- `setup` 从选定的基准价格形成Apple的完整等价价格矩阵。此分割工作流将最终验证推迟到v2本地化存在时。
- 在此分割的v2引导之外，请省略 `--no-verify`，以便 `setup` 执行其正常的回读验证。
- 当您的工作流是按层级驱动时，请使用 `--tier` 或 `--price-point-id` 而不是 `--price`。
- 如果现有订阅在相同的选定基准价格下保持 `MISSING_METADATA`，请使用 `--repair` 重新运行设置输入以原子性地重建和重新保存矩阵。

### 在更改前检查当前订阅定价
当您想要紧凑的当前状态快照时，首先使用摘要视图。

```bash
asc subscriptions pricing summary --subscription-id "SUB_ID" --territory "USA"
asc subscriptions pricing summary --subscription-id "SUB_ID" --territory "IND"
asc subscriptions pricing prices list --subscription-id "SUB_ID" --paginate
```

使用 `summary` 进行快速前后检查，当您需要原始价格记录时使用 `prices list`。

### 从一个订阅派生本地化价格到另一个订阅
当目标订阅在所有地区应保持接近源订阅的固定倍数时，请使用 `derive`，例如年定价接近月定价的10倍。Apple的阶梯在地区间不均匀缩放，因此在应用它们之前请预览选定的目标点和实现的倍数。

```bash
asc subscriptions pricing derive \
  --source-subscription-id "MONTHLY_SUB_ID" \
  --target-subscription-id "YEARLY_SUB_ID" \
  --multiplier "10" \
  --round nearest \
  --dry-run \
  --output table
```

当Apple不提供所需价格时，选择如何解析所需价格：

- `exact` 除非计算金额存在于目标阶梯上，否则失败。
- `nearest` 选择最接近的金额；如果存在平局，则选择较低的金额。
- `up` 选择计算值上或等于的最小可用金额。
- `down` 选择计算值下或等于的最大可用金额。

确认命令获取当前价格并构建一个新计划；它不会重用前面的干运行结果。当应用的值必须与已审阅的值匹配时，请在确认前立即重新运行 `--dry-run`，然后应用：

```bash
asc subscriptions pricing derive \
  --source-subscription-id "MONTHLY_SUB_ID" \
  --target-subscription-id "YEARLY_SUB_ID" \
  --multiplier "10" \
  --round nearest \
  --confirm \
  --output table
```

源和目标必须是具有现有标准 `UPFRONT` 价格的不同订阅。此操作是一次快照，不是持久链接。当任何地区无法解析时，它在突变之前失败关闭，跳过已匹配的目标价格，并通过回读验证应用的价格。使用 `--territory "SWE"` 进行聚焦预览或分阶段一国更新；省略它以派生当前所有源地区。
默认情况下，当未提供 `--start-date` 时，已批准或正在运行的目標在 `--auto-start-date` 默认为true的情况下安排在明天。传递 `--auto-start-date=false` 以立即应用，或在协调发布时使用明确日期。
该命令不会更改订阅销售可用性。

### 优先的批量PPP更新：导入CSV并干运行
对于广泛的PPP发布，请优先使用订阅定价导入命令，而不是手动逐个添加地区价格。

示例CSV：

```csv
territory,price,start_date,preserved
IND,2.99,2026-04-01,false
BRA,4.99,2026-04-01,false
MEX,4.99,2026-04-01,false
DEU,8.99,2026-04-01,false
```

干运行首先：

```bash
asc subscriptions pricing prices import \
  --subscription-id "SUB_ID" \
  --input "./ppp-prices.csv" \
  --dry-run \
  --output table
```

实际应用：

```bash
asc subscriptions pricing prices import \
  --subscription-id "SUB_ID" \
  --input "./ppp-prices.csv" \
  --confirm \
  --output table
```

注意：
- `--dry-run` 验证行并解析价格点，而不会创建价格。
- `--continue-on-error=false` 提供快速失败模式。
- CSV必需列：`territory`, `price`
- CSV可选列：`currency_code`, `start_date`, `preserved`, `preserve_current_price`, `price_point_id`
- 当省略 `price_point_id` 时，CLI会自动解析与行地区和价格匹配的价格点。
- 导入中的地区输入可以是3字母ID、2字母代码或可以清晰映射的常用地区名称。

### 一次性订阅地区更改
对于少量手动覆盖，请使用标准的 `set` 命令。

```bash
asc subscriptions pricing prices set --subscription-id "SUB_ID" --price "2.99" --territory "IND"
asc subscriptions pricing prices set --subscription-id "SUB_ID" --tier 5 --territory "BRA"
asc subscriptions pricing prices set --subscription-id "SUB_ID" --price-point "PRICE_POINT_ID" --territory "DEU"
```

注意：
- 添加 `--start-date "YYYY-MM-DD"` 以安排未来更改。
- 添加 `--preserved` 当您想要保留当前价格关系时。
- 该命令处理初始定价和后续价格更改。

### 仅在需要时发现原始价格点
当您想要直接检查Apple的本地化阶梯或固定精确价格点ID时，使用价格点查找和等价化。

```bash
asc subscriptions pricing price-points list --subscription-id "SUB_ID" --territory "USA" --paginate --price "9.99"
asc subscriptions pricing price-points equalizations --price-point-id "PRICE_POINT_ID" --paginate
asc subscriptions pricing price-points adjusted-equalizations --price-point-id "PRICE_POINT_ID" --upfront-price-point-id "UPFRONT_PRICE_POINT_ID" --plan-type MONTHLY --subscription-id "SUB_ID" --paginate
```

使用 `equalizations` 用于Apple的标准本地化阶梯。使用 `adjusted-equalizations` 当您需要API 4.4.1订阅特定的调整时。对于新的 `adjusted-equalizations` 请求，传递 `--upfront-price-point-id` 和 `--plan-type`；`--subscription-id` 和 `--territory` 是可选过滤器。将 `--next` 视为不透明的继续URL。在恢复的 `equalizations` 或 `adjusted-equalizations` 请求中，仅传递 `--next` 而不传递原始所有者 `--price-point-id`、过滤器、稀疏字段、包括或限制；继续URL已经包含该查询状态。`--paginate` 和显式的输出标志仍可使用。

### 应用后验证
更改后重新运行摘要和原始列表视图。

```bash
asc subscriptions pricing summary --subscription-id "SUB_ID" --territory "IND"
asc subscriptions pricing summary --subscription-id "SUB_ID" --territory "BRA"
asc subscriptions pricing prices list --subscription-id "SUB_ID" --paginate
```

在版本元数据存在后，您可以重新运行 `asc subscriptions setup` 以启用验证，重新检查父项、定价、截图和可用性状态。

### 订阅可用性
底层的订阅可用性资源在App Store Connect API 4.4.1中已弃用。仅当普通 upfront 地区可用性仍然需要时，才保留此命令系列以保持兼容性；Apple不提供该情况的一对一替换。对于带12个月承诺的月订阅，请使用 `asc subscriptions pricing monthly-commitment enable|disable|list` 代替。

```bash
asc subscriptions pricing availability edit --subscription-id "SUB_ID" --territories "USA,CAN,IND,BRA"
asc subscriptions pricing availability view --subscription-id "SUB_ID"
```

## IAP PPP工作流

### 新IAP：使用 `setup` 引导父项和定价
使用 `setup` 创建产品和初始价格计划。它的本地化标志使用已弃用的v1资源，因此设置后通过API 4.4.1 IAP版本添加本地化。

```bash
asc iap setup \
  --app "APP_ID" \
  --type NON_CONSUMABLE \
  --reference-name "Pro Lifetime" \
  --product-id "com.example.pro.lifetime" \
  --price "9.99" \
  --base-territory "USA" \
  --output json
```

从设置JSON中捕获 `.iapId`，然后创建版本和元数据：

```bash
asc iap versions list --iap-id "IAP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json
# 如果列表为零匹配：
asc iap versions create --iap-id "IAP_ID" --output json
# 如果有一个匹配，重用 .data[0].id。如果有多个，停止并要求显式的 IAP_VERSION_ID。
asc iap versions localizations list --version-id "IAP_VERSION_ID" --paginate --output json
# 如果只有 en-US 缺失：
asc iap versions localizations create --version-id "IAP_VERSION_ID" --locale "en-US" --name "Pro Lifetime" --description "Unlock everything forever"
# 否则，如果解析的 en-US 值不同：
asc iap versions localizations update --localization-id "IAP_LOC_ID" --name "Pro Lifetime" --description "Unlock everything forever"
# 否则，不做任何事。
```

重用单个 `PREPARE_FOR_SUBMISSION` 版本。列表为空时才创建，如果返回多个匹配则停止并要求显式的版本ID。仅当 `en-US` 缺失时才创建本地化，仅当值不同时更新已解析的ID，否则不做任何事。

注意：
- `setup` 默认验证创建的IAP和价格计划；使用其版本范围的列表命令验证版本本地化。
- 使用 `--start-date` 用于计划定价。
- 当您想要确定性层级或ID设置时，使用 `--tier` 或 `--price-point-id`。

### 在更改前检查当前IAP定价
使用 `asc iap pricing summary` 作为PPP工作的主要当前状态摘要。

```bash
asc iap pricing summary --iap-id "IAP_ID" --territory "USA"
asc iap pricing summary --iap-id "IAP_ID" --territory "IND"
```

这返回基准地区、当前价格、预计收益和请求地区的计划更改。

### 发现候选IAP价格点
当您想要检查或固定精确价格点ID时，使用价格点查找。

```bash
asc iap pricing price-points list --iap-id "IAP_ID" --territory "USA" --paginate --price "9.99"
asc iap pricing price-points equalizations --id "PRICE_POINT_ID"
```

### 创建或更新IAP价格计划
对于手动PPP更新，直接创建价格计划。

```bash
asc iap pricing schedules create --iap-id "IAP_ID" --base-territory "USA" --price "4.99" --start-date "2026-04-01"
asc iap pricing schedules create --iap-id "IAP_ID" --base-territory "USA" --tier 5 --start-date "2026-04-01"
asc iap pricing schedules create --iap-id "IAP_ID" --base-territory "USA" --prices "PRICE_POINT_ID:2026-04-01"
```

当您有意创建或替换计划条目时使用这些。对于更深入的检查：

```bash
asc iap pricing schedules view --iap-id "IAP_ID"
asc iap pricing schedules manual-prices --schedule-id "SCHEDULE_ID" --paginate
asc iap pricing schedules automatic-prices --schedule-id "SCHEDULE_ID" --paginate
```

### 应用后验证
在计划或应用定价更改后再次使用摘要命令。

```bash
asc iap pricing summary --iap-id "IAP_ID" --territory "USA"
asc iap pricing summary --iap-id "IAP_ID" --territory "IND"
```

对于未来日期的计划，请预期计划更改，而不是立即更新的当前价格。

## 常见的PPP策略模式

### 首先选择基准地区
- 选择一个基准地区，通常是 `USA`。
- 首先在该地区设置基准价格。
- 从该基准价格派生较低或较高的地区目标。

### 分层区域定价
- 高收入市场接近基准。
- 中收入市场获得适度折扣。
- 低收入市场获得更强的PPP调整。

### 电子表格驱动发布
- 在CSV中构建目标地区列表。
- 干运行导入。
- 修复任何解析失败。
- 应用导入。
- 对最重要的地区重新运行摘要检查。

## 注意
- 在文档和自动化中优先使用标准命令：`asc subscriptions pricing ...`
- `asc subscriptions pricing ...` 是支持的订阅定价系列；不要使用已移除的 `asc subscriptions prices ...` 路径。
- 在文档和自动化中优先使用标准IAP命令：`asc iap pricing ...`
- `asc subscriptions pricing prices import --dry-run` 是今天最安全的订阅批量PPP路径。
- `asc subscriptions setup` 和 `asc iap setup` 已经提供内置的创建后验证。
- 目前还没有一级的PPP前后差异命令；在应用前后使用当前的摘要命令。
- 价格更改可能需要时间才能在App Store Connect和商店中传播。
