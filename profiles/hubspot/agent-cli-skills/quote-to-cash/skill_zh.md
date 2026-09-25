## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/q2c-essentials.md` | 六字段速查表、关联方向、发票/订阅/订单/购物车的门户注意事项。 |

## 基础知识

先阅读 `bulk-operations/SKILL.md` — JSONL 管道、批量读取、分页以及破坏性操作的 dry-run/digest/confirm 流程都在那里。重塑配方（读取→写入负载）在 `bulk-operations/resources/json-patterns.md`。

`hubspot <命令> --help` 是权威来源。对象类型是复数形式（`products`、`line_items`、`quotes`、`invoices`、`subscriptions`）。切勿硬编码属性表 — `hubspot properties list --type <type>` 只需一个调用即可。使用 `hubspot properties get --type <type> --name <property>` 验证代理即将写入的任何枚举值，并读取 `options[].value`。

门户注意事项：`invoices`、`subscriptions`、`orders`、`carts` 在 `hubspot objects types` 中显示空的 `objectTypeId`。当 token 具有匹配的范围（`invoices-read`、`subscriptions-read` 等）时，它们通过 `objects search`/`list` 工作，否则返回 403。CLI 创建的报价始终为 `DRAFT`；审批路由、分享链接、PDF 生成和发票创建通常需要 HubSpot UI。

## 1. 创建产品

```bash
hubspot objects create --type products \
  --property name="Enterprise License" \
  --property price=12000 \
  --property hs_sku=ENT-001
```

对于周期性产品，设置 `recurringbillingfrequency`；首先使用 `hubspot properties get --type products --name recurringbillingfrequency --format json | jq -r '.options[].value'` 检查 API 枚举值。通过将 `{"properties":{...}}` 的 JSONL 管道到 `hubspot objects create --type products --dry-run` 批量导入目录。

## 2. 构建报价：行项目 → 报价 → 关联

`objects create` 每行标准输入输出一个结果行，按输入顺序。这允许您构建行项目、捕获它们的 ID，并在三个管道中将它们关联到新报价 — 无需每个记录的 shell 循环。

```bash
DEAL_ID=12345

# 1. 创建行项目。items.jsonl 每行包含 {"name":..,"qty":..,"price":..,"product_id":..}。
jq -c '{properties:{
    name:.name, quantity:(.qty|tostring), price:(.price|tostring),
    hs_product_id:.product_id, hs_line_item_currency_code:"USD"
  }}' items.jsonl \
| hubspot objects create --type line_items > /tmp/lineitems.jsonl

# 2. 创建报价。
QUOTE_ID=$(hubspot objects create --type quotes \
  --property hs_title="Acme Corp - 2026" \
  --property hs_expiration_date=2026-06-30 \
  --property hs_currency=USD \
  --format json | jq -r '.data.id // .id')

# 3. 在一个管道中将每个新行项目关联到报价。
jq -r '.id' /tmp/lineitems.jsonl \
| jq -cR --arg q "$QUOTE_ID" '{from:("quotes:" + $q), to:("line_items:" + .)}' \
| hubspot associations create

# 4. 将报价链接到交易。
hubspot associations create --from "deals:$DEAL_ID" --to "quotes:$QUOTE_ID"
```

折扣处理 — `discount` 是可写入的百分比（`10` = 10% 折扣）。`hs_total_discount` 是 HubSpot 计算的；切勿设置它。在使用不属于您的门户之前，使用 `hubspot properties get --type line_items --name hs_total_discount` 验证（查找 `modificationMetadata.readOnlyValue:true`）。

准备好分享时，将报价从 `DRAFT` 推广：

```bash
hubspot objects update --type quotes <quote_id> --property hs_status=APPROVAL_NOT_NEEDED
```

验证您的门户的 `hs_status` 枚举值：`hubspot properties get --type quotes --name hs_status --format json | jq -r '.options[].value'`。

## 3. 追踪发票

CLI 读取发票数据并更新状态；创建通常需要 HubSpot Commerce + UI。按 `hs_invoice_status` 和日期筛选。

```bash
# 所有未支付的发票
hubspot objects search --type invoices \
  --filter "hs_invoice_status=OUTSTANDING" \
  --properties hs_number,hs_amount_billed,hs_balance,hs_due_date

# 过期（逾期）发票，动态日期
hubspot objects search --type invoices \
  --filter "hs_due_date<$(date +%Y-%m-%d) AND hs_invoice_status!=PAID" \
  --properties hs_number,hs_due_date,hs_balance

# 过去 30 天内开具的发票
hubspot objects search --type invoices \
  --filter "hs_invoice_date>=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d '30 days ago' +%Y-%m-%d)" \
  --properties hs_number,hs_amount_billed,hs_invoice_date
```

以相同方式验证状态枚举：`hubspot properties get --type invoices --name hs_invoice_status --format json | jq -r '.options[].value'`。

## 4. 追踪订阅

相同结构，按 `hs_subscription_status` 筛选。在写入筛选器之前验证枚举值 — 不要硬编码 `ACTIVE`/`CANCELLED`/`PAST_DUE`：

```bash
hubspot properties get --type subscriptions --name hs_subscription_status --format json \
  | jq -r '.options[].value'

# 然后筛选（大小写敏感）
hubspot objects search --type subscriptions \
  --filter "hs_subscription_status=<value-from-above>" \
  --properties hs_mrr,hs_arr,hs_subscription_status

# 跨所有活跃订阅汇总 MRR
hubspot objects search --type subscriptions \
  --filter "hs_subscription_status=<active-value>" --format json \
  | jq '[.data[].properties.hs_mrr | select(. != null) | tonumber] | add'
```

## 已知的限制

- `invoices`、`subscriptions`、`orders`、`carts` 需要在活动 token 上具有匹配的读取范围；403 表示用户的 OAuth 登录或 private-app token 缺少范围。
- 破坏性操作（`objects delete` 在 products/quotes/line_items 上）通常需要一个 private-app token：`export HUBSPOT_ACCESS_TOKEN=<token>`。在批量删除目录记录之前，请参阅 `bulk-operations/SKILL.md` 中的 dry-run → digest → confirm 流程。
- 报价分享链接、PDF 生成、审批路由和从头创建发票都是 UI 唯一 — CLI 更新记录但无法将报价发送给客户。
- 行项目的 `hs_total_discount` 是只读的 — 设置 `discount`（百分比）而不是。
