# 序列加载

通过 "$ARGUMENTS" 提供的目标条件和序列名称，查找、丰富并将联系人加载到 outreach 序列中——端到端。用户通过 "$ARGUMENTS" 提供目标条件和序列名称。

## 示例

- `/apollo:sequence-load add 20 SaaS 公司的 VP 销售到我的 "Q1 Outbound" 序列`
- `/apollo:sequence-load 金融科技创业公司的 SDR 经理 → Cold Outreach v2`
- `/apollo:sequence-load list sequences` (显示所有可用序列)
- `/apollo:sequence-load 工程总监，500+ 员工，美国 → Demo Follow-up`
- `/apollo:sequence-load reload 15 more leads into "Enterprise Pipeline"`

## 第 1 步 — 解析输入

从 "$ARGUMENTS" 中提取：

**目标条件：**
- 职位名称 → `person_titles`
- 资历级别 → `person_seniorities`
- 行业关键词 → `q_organization_keyword_tags`
- 公司规模 → `organization_num_employees_ranges`
- 地点 → `person_locations` 或 `organization_locations`

**序列信息：**
- 序列名称（"to"、"into" 或 "→" 后面的文本）
- 数量——要添加的联系人数量（如果未指定，默认为 10）

如果用户只是说 "list sequences"，则跳到第 2 步并显示所有可用序列。

## 第 2 步 — 查找序列

使用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_search` 查找目标序列：
- 将 `q_name` 设置为输入中的序列名称

如果没有匹配项或多个匹配项：
- 在表格中显示所有可用序列：| 名称 | ID | 状态 |
- 让用户选择一个

## 第 3 步 — 获取邮箱账户

使用 `mcp__claude_ai_Apollo_MCP__apollo_email_accounts_index` 列出链接的邮箱账户。

- 如果只有一个账户 → 自动使用
- 如果有多个 → 显示它们并询问从哪个发送

## 第 4 步 — 查找匹配的联系人

使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 并使用目标条件。
- 将 `per_page` 设置为请求的数量（默认为 10）

在预览表格中显示候选人：

| # | 名称 | 职位 | 公司 | 地点 |
|---|---|---|---|---|

询问：**"将这些 [N] 联系人添加到 [序列名称]？这将消耗 [N] 个 Apollo 信用点用于丰富。"**

等待确认后再继续。

## 第 5 步 — 丰富并创建联系人

对于每个批准的线索：

1. **丰富** — 使用 `mcp__claude_ai_Apollo_MCP__apollo_people_bulk_match`（每调用最多批量处理 10 个）并使用：
   - 每个联系人的 `first_name`、`last_name`、`domain`
   - 将 `reveal_personal_emails` 设置为 `true`

2. **创建联系人** — 对于每个丰富后的联系人，使用 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create` 并使用：
   - `first_name`、`last_name`、`email`、`title`、`organization_name`
   - 如果可用，则提供 `direct_phone` 或 `mobile_phone`
   - 将 `run_dedupe` 设置为 `true`

收集所有创建的联系人 ID。

## 第 6 步 — 添加到序列

使用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_add_contact_ids` 并使用：
- `id`: 序列 ID
- `emailer_campaign_id`: 相同的序列 ID
- `contact_ids`: 创建的联系人 ID 数组
- `send_email_from_email_account_id`: 所选邮箱账户 ID
- `sequence_active_in_other_campaigns`: `false`（安全默认值）

## 第 7 步 — 确认加入

显示摘要：

---

**序列加载成功**

| 字段 | 值 |
|---|---|
| 序列 | [名称] |
| 添加的联系人 | [数量] |
| 从哪个发送 | [邮箱地址] |
| 消耗的信用点 | [数量] |

**已加入的联系人：**

| 名称 | 职位 | 公司 | 邮箱 |
|---|---|---|---|

---

## 第 8 步 — 提供下一步操作

询问用户：

1. **加载更多** — 查找并添加另一批线索
2. **查看序列** — 显示序列详情和所有已加入的联系人
3. **移除联系人** — 使用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_remove_or_stop_contact_ids` 移除特定联系人
4. **暂停联系人** — 使用 `status: "paused"` 和 `auto_unpause_at` 日期重新添加
