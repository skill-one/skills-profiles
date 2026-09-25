# asc Apple Ads

运行 Apple Ads 通过 `asc ads`。Apple Ads 凭证与应用商店连接 (App Store Connect) 凭证是分开的；`asc auth login` 不会配置 Ads。

## 首先选择 API

- 直接的 `asc ads <resource> ...` 命令使用 Apple Ads 平台 API v1 和广告账户 ID。
- 已弃用的 Campaign Management API v5 命令位于 `asc ads v5 ...` 下，并使用组织 ID。Apple 将在 2027 年 1 月 26 日弃用 v5。
- 永远不要用组织 ID 替换广告账户 ID。CLI 将它们保持分开。
- 在构建请求文件之前，使用 `--help` 运行确切的叶命令。平台 v1 的有效负载和响应信封与 v5 不同；CLI 不会翻译它们。
- 对于非交互式管道，传递 `--file -` 从标准输入读取 JSON 请求正文；当标准输入是终端时，CLI 会拒绝它。
- 资源、报告、上传和原始命令发出无损 JSON。使用 `jq` 进行投影，而不是请求表格或 Markdown 输出。

## 认证并固定账户

当配置文件必须支持 v1 和遗留 v5 时，存储两个上下文：

```bash
asc ads auth login \
  --name "Marketing" \
  --client-id "$ASC_ADS_CLIENT_ID" \
  --team-id "$ASC_ADS_TEAM_ID" \
  --key-id "$ASC_ADS_KEY_ID" \
  --private-key "$ASC_ADS_PRIVATE_KEY_PATH" \
  --ad-account "987654" \
  --org "123456" \
  --network
```

对于 CI，设置 Ads 特定的变量并绕过主机密钥库：

```bash
export ASC_ADS_CLIENT_ID="SEARCHADS_CLIENT_ID"
export ASC_ADS_TEAM_ID="SEARCHADS_TEAM_ID"
export ASC_ADS_KEY_ID="KEY_ID"
export ASC_ADS_PRIVATE_KEY_PATH="$HOME/.asc/apple-ads-private-key.pem"
export ASC_ADS_AD_ACCOUNT_ID="987654"
export ASC_ADS_BYPASS_KEYCHAIN=1
```

`ASC_ADS_PRIVATE_KEY` 和 `ASC_ADS_PRIVATE_KEY_B64` 也适用。如果另一个受信任的过程生成了短时效的令牌，设置 `ASC_ADS_ACCESS_TOKEN`；范围 v1 调用仍然需要广告账户 ID。

无打印令牌的情况下检查认证：

```bash
asc ads auth status --validate --output json
asc ads auth discover --ads-profile "Marketing" --output json
asc ads auth doctor --output json
```

发现调用 Platform v1 `GET /v1/me` 和 `GET /v1/acls`。比较每个 ACL 的广告账户 ID、名称、组织 ID 和角色；永远不要自动选择第一个结果。在任何变更之前打印所选账户，如果有多个配置文件或账户可用，则传递 `--ads-profile "Marketing"` 和 `--ad-account "987654"`。

对于命名配置文件，配置文件的 `ad_account_id` 和 `org_id` 独立存在；它们不会从其他配置文件或根配置继承上下文。v1 上下文优先级是 `--ad-account`、`ASC_ADS_AD_ACCOUNT_ID`、所选配置文件，然后是无配置文件的根配置。遗留 v5 使用匹配的 `--org` 和 `ASC_ADS_ORG_ID` 链。

## 开始只读

身份和 ACL 调用不需要广告账户上下文：

```bash
asc ads me view --ads-profile "Marketing" --output json
asc ads acls list --ads-profile "Marketing" --output json
asc ads orgs view --ads-profile "Marketing" --org-id "123456" --output json
```

然后用一个小型应用搜索来证明所选账户：

```bash
asc ads apps search \
  --ads-profile "Marketing" \
  --ad-account "987654" \
  --query "Example" \
  --limit 1 \
  --output json
```

应用搜索至少需要一个 `--query`、`--cpids` 或 `--return-owned-apps`。商店使用逗号分隔的 ISO alpha-2 代码。仅在需要每个搜索结果时才添加 `--paginate`。

使用每个资源的 `find` 命令进行库存管理。大多数 v1 查询将过滤器、排序和分页放在 JSON 对象中。从属资源过滤器如下所示：

```json
{
  "filters": [
    {"field": "campaignId", "operator": "EQUALS", "value": ["campaign-id"]}
  ],
  "pagination": {"offset": 0, "pageSize": 100, "fetchTotalCount": true}
}
```

```bash
asc ads campaigns find --ads-profile "Marketing" --ad-account "987654" --output json
asc ads ad-groups find --ads-profile "Marketing" --ad-account "987654" --file query.json --output json
asc ads ads find --ads-profile "Marketing" --ad-account "987654" --file query.json --output json
```

从 `campaigns find` 请求中省略 `--file` 会请求默认的第一页。要控制或耗尽结果集，在查询文件中使用 `pagination.offset`、`pageSize` 和 `fetchTotalCount`，读取响应分页，并推进偏移量直到完成。此命令没有 `--paginate` 标志。平台过滤器使用单数 `value`；不要复制 v5 `Selector` 字段，如 `conditions` 或复数 `values`，当前 `asc` 在认证之前会拒绝它们。

直接 v1 树还涵盖广告账户和广告商资源；应用资格、区域设置、产品页面和拒绝原因；品牌、商业类别、位置、位置组、创意和资产；地理定位和共享预算；应用和品牌的报告；洞察、建议、推荐和变更历史。发现确切的叶命令，而不是退回到原始 HTTP：

```bash
asc ads change-history --help
asc ads suggestions --help
asc ads rejection-reasons --help
asc ads reports brands --help
```

关键词查询需要一个选择器文件。定位关键词需要一个 `id`、`adGroupId` 或 `campaignId` 过滤器。否定关键词需要一个 `id` 或 `adGroupId`；层级否定关键词将 `campaignId` 与一个操作符为 `IS_NULL` 的 `adGroupId` 过滤器组合。

```bash
asc ads targeting-keywords find --ads-profile "Marketing" --ad-account "987654" --file keyword-query.json --output json
asc ads negative-keywords find --ads-profile "Marketing" --ad-account "987654" --file negative-keyword-query.json --output json
```

## 报告和优化

v1 报告需要一个端点特定的正文。日期位于 `timeRange` 下，页面控制使用 `offset` 和 `pageSize`，层级或广告组 ID 属于 `filters`：

```json
{
  "pagination": {"offset": 0, "pageSize": 20},
  "filters": [
    {"field": "campaignId", "operator": "EQUALS", "value": ["campaign-id"]}
  ],
  "groupBy": ["countryOrRegion"],
  "timeRange": {
    "start": "2026-08-01",
    "end": "2026-08-14",
    "timeZone": "ORTZ",
    "granularity": "DAILY"
  }
}
```

```bash
asc ads reports apps campaigns \
  --ads-profile "Marketing" \
  --ad-account "987654" \
  --file report.json \
  --output json
```

报告命令不接受 `--paginate`；在正文中更改分页。检查叶命令帮助，因为报告实体接受不同的 `groupBy` 和选项值。

建议和提议也使用端点特定的正文。应用或拒绝建议可能会改变支出，并需要 `--confirm`：

```bash
asc ads recommendations daily-budgets find --ads-profile "Marketing" --ad-account "987654" --file query.json
asc ads recommendations daily-budgets apply --ads-profile "Marketing" --ad-account "987654" --file recommendations.json --confirm
```

## 保护变更

在用户已批准广告账户、资源类型、目标 ID 并审查了有效负载之后，才进行变更。将请求 JSON 保存在文件中；永远不要从相关的 v5 架构中凭空创建字段。

创建活动可能会开始支出。`CampaignCreate` 需要 `adAccountId`、`billingEvent`、`dailyBudget`、`name`、`promotedObjectId`、`promotedObjectType` 和 `targeting`。CLI 会发送文件不变：`--ad-account` 选择请求上下文，但不会将 `adAccountId` 注入 JSON。从暂停的形状开始，用从所选账户中读取的值替换每个占位符，并重新检查当前 Apple v1 架构的任何账户特定要求：

```json
{
  "name": "ASC agent validation 2026-08-15T00:00:00Z",
  "status": "PAUSED",
  "adAccountId": 987654,
  "promotedObjectType": "APPSTORE_APP",
  "promotedObjectId": "123456789",
  "billingEvent": "TAPS",
  "dailyBudget": {"value": {"amount": "1", "currency": "USD"}},
  "startTime": "2030-01-01T00:00:00.000",
  "endTime": "2030-01-02T00:00:00.000",
  "targeting": {"countryOrRegion": {"include": ["US"]}},
  "bidStrategy": {"bidStrategyType": "MANUAL_CPT", "bidStrategyGoal": "TAP"}
}
```

具有显式顶层 `"status":"PAUSED"` 的有效负载可以在没有 `--confirm` 的情况下运行；省略或非暂停状态需要它。

```bash
asc ads campaigns create --ads-profile "Marketing" --ad-account "987654" --file paused-campaign.json
asc ads campaigns pause --ads-profile "Marketing" --ad-account "987654" --campaign "campaign-id"
asc ads campaigns resume --ads-profile "Marketing" --ad-account "987654" --campaign "campaign-id" --confirm
```

活动更新在它们可以改变预算、定位、出价、交付、日期或状态时需要 `--confirm`。仅名称更新或名称加上 `PAUSED` 状态不需要。删除、批量创建或更新、建议应用或拒绝调用、预算订单写入和其他操作风险变更需要在认证或网络访问之前确认。

广告组创建和关键词批量写入是始终确认交付或定位变更的示例。v1 批量关键词文件使用包装对象，如 `KeywordCreateBulkRequest`，而不是 v5 原始数组形状：

```bash
asc ads ad-groups create --ads-profile "Marketing" --ad-account "987654" --file ad-group.json --confirm
asc ads targeting-keywords create-bulk --ads-profile "Marketing" --ad-account "987654" --file keywords.json --confirm
asc ads targeting-keywords delete --ads-profile "Marketing" --ad-account "987654" --keyword "keyword-id" --confirm
```

共享预算使用 `budget-orders` 命令组。创建、更新和删除是无上下文的，但需要确认；查看和查找接受可选广告账户上下文。

```bash
asc ads budget-orders create --ads-profile "Marketing" --file shared-budget.json --confirm
asc ads budget-orders update --ads-profile "Marketing" --budget-order "budget-id" --file update.json --confirm
asc ads budget-orders delete --ads-profile "Marketing" --budget-order "budget-id" --confirm
```

广告账户创建也需要 `--confirm`，因为其账户家族不能更改，Apple 也不提供删除端点。包含 `delegations` 的广告账户更新需要确认，因为它会替换完整列表。

使用专用多部分命令上传品牌资产。轮询直到 Apple 完成处理：

```bash
asc ads assets upload --ads-profile "Marketing" --file ./brand.png --brand "BRAND_ID" --ad-account "987654"
asc ads assets view --ads-profile "Marketing" --asset "ASSET_UUID" --ad-account "987654"
```

仅在 `eligibility.status` 是 `ELIGIBLE` 时使用资产；对于 `LIMITED`，检查 `allowedGroups`。不要附加 `PENDING` 或 `INELIGIBLE` 资产。

## 原始请求

对于常规工作使用一级命令。原始 v1 请求只接受 `v1/...` 路径或 `https://api.ads.apple.com/v1/...` URL：

```bash
asc ads api request \
  --method POST \
  --path v1/campaigns/query \
  --ads-profile "Marketing" \
  --ad-account "987654" \
  --file query.json \
  --output json
```

未知的变更会失败关闭，而已知的危险变更需要 `--confirm`。原始命令会拒绝多部分资产上传；使用 `asc ads assets upload`。

保持遗留调用显式：

```bash
asc ads v5 api request \
  --method POST \
  --path v5/campaigns/find \
  --ads-profile "Marketing" \
  --org "123456" \
  --file selector.json \
  --output json
```

## 逐个命令迁移 v5

在每个脚本都有经过审查的 v1 正文和响应解析器之前，保持现有的 v5 有效负载在 `asc ads v5` 下。常见迁移：

| 已弃用的 v5 | 平台 API v1 |
| --- | --- |
| `asc ads v5 campaigns list` | `asc ads campaigns find` |
| `asc ads v5 apps localized-details` | `asc ads apps locales find` |
| `asc ads v5 product-pages list` | `asc ads product-pages find` |
| `asc ads v5 reports campaigns` | `asc ads reports apps campaigns` |
| `asc ads v5 campaigns pause` / `resume` | `asc ads campaigns pause` / `resume` |
| v5 活动或广告组否定关键词 | `asc ads negative-keywords ...` 在正文中指定范围 |

七个 v5 叶命令没有对应的单个命令 v1 替代：产品页面国家、产品页面设备、定位关键词批量删除、两个否定关键词批量删除、展示份额报告列表和查看。不要假装 `geo search`、`insights impression-share` 或单个资源删除保留了这些合同。

## 干净地完成实时测试

- 从 ACL 发现和一个结果的应用搜索开始。
- 使用唯一的时间戳名称和显式的 `PAUSED` 状态进行一次性活动测试。
- 保存从 JSON 输出中获取的每个创建的 ID。
- 在检查任何其他内容之前暂停支出资源。
- 用 `asc ads campaigns view --ads-profile "Marketing" --ad-account "987654" --campaign "campaign-id" --output json` 重新读取测试活动。
- 仅删除测试创建的活动，使用 `asc ads campaigns delete --ads-profile "Marketing" --ad-account "987654" --campaign "campaign-id" --confirm`；不要删除预存在的父活动。
- 再次运行相同的 `campaigns view`。将 Apple 的未找到响应视为清理证明；报告任何仍然存在或无法删除的活动。
