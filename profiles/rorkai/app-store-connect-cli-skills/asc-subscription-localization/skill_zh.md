# asc 订阅本地化

使用此功能可以批量创建或批量更新订阅、订阅组和应用内购买的显示名称，并在支持的情况下提供描述，适用于 App Store Connect 的所有地区。这消除了在 App Store Connect 中逐个语言点击设置相同显示名称的繁琐手动过程。

## 前置条件
- 配置认证 (`asc auth login` 或 `ASC_*` 环境变量)。
- 知道你的应用 ID (`ASC_APP_ID` 或 `--app`)。
- 订阅组和订阅已存在。

## 首先选择 API 范围

API 4.4.1 为应用内购买、订阅和订阅组添加了独立的版本。版本 ID 与其产品、订阅或组 ID 不同。

- 使用 `asc ... versions localizations ...` 进行所有新的本地化工作。
- 不要使用产品或组范围的 v1 本地化命令。API 4.4.1 已弃用这些资源，CLI 现在会为它们的兼容性命令发出迁移警告。
- 永远不要将产品、订阅或组 ID 传递给版本范围的命令。

在本地化之前解决或创建版本：

```bash
asc iap versions list --iap-id "IAP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output table
asc subscriptions versions list --subscription-id "SUB_ID" --state PREPARE_FOR_SUBMISSION --paginate --output table
asc subscriptions groups versions list --group-id "GROUP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output table
```

在每个列表结果上独立分支：零匹配表示创建，一个匹配表示重用该版本 ID，多个匹配表示停止并需要显式的版本 ID。仅对零匹配分支运行以下命令：

```bash
# 如果且仅如果 IAP 版本列表返回零匹配：
asc iap versions create --iap-id "IAP_ID" --output json
# 如果且仅如果订阅版本列表返回零匹配：
asc subscriptions versions create --subscription-id "SUB_ID" --output json
# 如果且仅如果组版本列表返回零匹配：
asc subscriptions groups versions create --group-id "GROUP_ID" --output json
```

这三个版本系列都没有版本删除命令。列出并重用唯一的 `PREPARE_FOR_SUBMISSION` 版本；仅对零匹配创建，存在多个匹配时停止。由于父级删除不会级联 IAP 或订阅版本，因此不要假设父级删除会清理为测试创建的版本。

## 支持的 App Store 地区

这些是 App Store Connect 支持的订阅和应用内购买本地化的地区：

```
ar-SA, ca, cs, da, de-DE, el, en-AU, en-CA, en-GB, en-US,
es-ES, es-MX, fi, fr-CA, fr-FR, he, hi, hr, hu, id, it,
ja, ko, ms, nl-NL, no, pl, pt-BR, pt-PT, ro, ru, sk,
sv, th, tr, uk, vi, zh-Hans, zh-Hant
```

## 工作流：批量本地化订阅版本（v2）

列出现有本地化，创建缺失的地区，然后验证：

```bash
asc subscriptions versions localizations list --version-id "VERSION_ID" --paginate --output table
asc subscriptions versions localizations create --version-id "VERSION_ID" --locale "LOCALE" --name "显示名称" --description "描述"
asc subscriptions versions localizations list --version-id "VERSION_ID" --paginate --output table
```

更新区分省略的值、非空字符串和 JSON `null`：

```bash
asc subscriptions versions localizations update --id "LOC_ID" --name "新名称" --description "更新描述"
```

不要将值标志与其匹配的 `--clear-name` 或 `--clear-description` 标志组合。4.4.1 模式允许 JSON `null`，但 Apple 的实时服务目前拒绝订阅版本本地化的空 `--description` 和 `--clear-description`，因为描述必须至少包含一个字符。

因此，创建缺失的订阅版本本地化需要一个非空描述。仅运行显示名称的命令可以更新现有本地化的名称，但必须等到用户提供非空的本地化特定或共享回退描述后才能创建缺失的地区。

## 工作流：批量本地化订阅组版本（v2）

```bash
asc subscriptions groups versions localizations list --version-id "VERSION_ID" --paginate --output table
asc subscriptions groups versions localizations create --version-id "VERSION_ID" --locale "LOCALE" --name "组显示名称" --custom-app-name "我的应用"
asc subscriptions groups versions localizations update --id "LOC_ID" --name "更新组显示名称" --custom-app-name "我的应用"
asc subscriptions groups versions localizations list --version-id "VERSION_ID" --paginate --output table
```

清除元数据是一个单独的显式选择操作。在确认用户要删除现有的自定义应用名称后，运行：

```bash
asc subscriptions groups versions localizations update --id "LOC_ID" --clear-custom-app-name
```

不要在标准批量本地化工作流中包含 `--clear-name` 或 `--clear-custom-app-name`。仅在故意打算使用 JSON `null` 时使用这些标志；省略标志将保留该属性不变。

## 工作流：批量本地化应用内购买版本（v2）

```bash
asc iap versions localizations list --version-id "VERSION_ID" --paginate --output table
asc iap versions localizations create --version-id "VERSION_ID" --locale "LOCALE" --name "显示名称" --description "描述"
asc iap versions localizations update --localization-id "LOC_ID" --description "更新描述"
asc iap versions localizations list --version-id "VERSION_ID" --paginate --output table
```

Apple 的实时服务也拒绝应用内购买版本本地化的空描述和 `--clear-description`，尽管 4.4.1 模式允许 JSON `null`。与订阅类似，仅运行显示名称的命令可以更新现有的应用内购买本地化，但必须等到提供非空描述后才能创建缺失的地区。

## 批量本地化应用中的所有订阅版本

对于具有多个订阅组和订阅的完整应用：

```bash
# 1. 列出组并解决每个组的唯一可变版本。
asc subscriptions groups list --app "APP_ID" --paginate --output json
asc subscriptions groups versions list --group-id "GROUP_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json

# 2. 本地化每个组版本。
asc subscriptions groups versions localizations list --version-id "GROUP_VERSION_ID" --paginate --output json
asc subscriptions groups versions localizations create --version-id "GROUP_VERSION_ID" --locale "LOCALE" --name "组显示名称"

# 3. 列出订阅并解决每个订阅的唯一可变版本。
asc subscriptions list --group-id "GROUP_ID" --paginate --output json
asc subscriptions versions list --subscription-id "SUB_ID" --state PREPARE_FOR_SUBMISSION --paginate --output json

# 4. 本地化每个订阅版本。
asc subscriptions versions localizations list --version-id "SUBSCRIPTION_VERSION_ID" --paginate --output json
asc subscriptions versions localizations create --version-id "SUBSCRIPTION_VERSION_ID" --locale "LOCALE" --name "显示名称" --description "描述"
```

对每个版本列表应用相同的零/一/多规则：零匹配创建版本，一个匹配重用该版本 ID，多个匹配时停止并需要显式的版本 ID。

## 代理行为

- 仅使用版本范围的 v2 资源进行新的本地化工作。
- 保持版本 ID 与产品、订阅和组 ID 分开。
- 始终首先列出现有本地化以避免重复创建错误。
- 创建缺失的地区，当现有值不同时更新解析的本地化 ID，当现有值已匹配时不做任何操作。
- 当用户提供单个显示名称时，用于所有地区（所有地区名称相同）。
- 当用户提供每个地区的翻译名称时，用于每个地区的本地化特定名称。
- 对于订阅和应用内购买版本本地化，要求每个创建操作的非空 `--description`。如果用户提供仅显示名称，通过解析的 ID 更新现有本地化，跳过缺失地区的创建，并在创建它们之前要求提供本地化特定描述或一个非空回退描述。
- 在现有订阅或应用内购买版本本地化的更新中，除非用户提供了一个新的非空值，否则省略 `--description`；永远不会推断空值或清除它。
- 订阅组版本本地化没有描述字段。正常创建或更新它们的名称，仅在用户提供该值时使用 `--custom-app-name`。
- 使用 `--output table` 进行验证步骤，以便用户可以 visually 确认。
- 使用显式的 `--output json` 进行中间自动化步骤；输出默认为 TTY-aware。
- 批量写入后，始终运行列表命令以验证完整性。
- 对于具有许多订阅的应用，按组顺序处理它们以保持输出可读。
- 如果创建或更新调用对某个地区失败，记录该地区和错误，然后继续处理剩余地区。批处理完成后，将所有失败报告在一起，以便用户可以处理它们。

## 注意事项
- 订阅显示名称是用户在订阅管理表和购买对话框中看到的。
- 为已存在的地区创建本地化将失败；首先列出并更新解析的 ID，当需要更改时。
- 没有批量 API；每个地区需要单独的创建调用。
- 在列表命令中使用 `--paginate` 以确保返回所有现有本地化。
- 如果只有应用名称而没有 ID，请使用 `asc-id-resolver` 功能。
