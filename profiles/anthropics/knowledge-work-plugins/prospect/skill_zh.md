# 潜在客户

通过 "$ARGUMENTS" 一次性将 ICP 描述转换为排名靠前、信息丰富的潜在客户列表。用户通过 "$ARGUMENTS" 描述其理想客户。

## 示例

- `/apollo:prospect 美国系列 B+ 级 SaaS 公司的工程副总裁，200-1000 名员工`
- `/apollo:prospect 欧洲电商公司的营销负责人`
- `/apollo:prospect 50-500 名员工的金融科技初创公司的首席技术官，纽约`
- `/apollo:prospect 1000 名以上员工的制造公司的采购经理`
- `/apollo:prospect 使用 Salesforce 和 Outreach 的公司的 SDR 领导者`

## 第 1 步 — 解析 ICP

从 "$ARGUMENTS" 中的自然语言描述中提取结构化筛选条件：

**公司筛选条件：**
- 行业/垂直关键词 → `q_organization_keyword_tags`
- 员工数量范围 → `organization_num_employees_ranges`
- 公司位置 → `organization_locations`
- 特定域名 → `q_organization_domains_list`

**人员筛选条件：**
- 职位 → `person_titles`
- 资历级别 → `person_seniorities`
- 人员位置 → `person_locations`

如果 ICP 含糊不清，在进行下一步之前，请提出 1-2 个澄清问题。至少需要职位/角色和行业或公司规模。

## 第 2 步 — 搜索公司

使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_companies_search` 并结合公司筛选条件：
- `q_organization_keyword_tags` 用于行业/垂直
- `organization_num_employees_ranges` 用于规模
- `organization_locations` 用于地理区域
- 将 `per_page` 设置为 25

## 第 3 步 — 丰富排名靠前的公司

使用 `mcp__claude_ai_Apollo_MCP__apollo_organizations_bulk_enrich` 并结合前 10 个结果中的域名。这可以揭示收入、融资、员工人数和公司概况数据，以帮助对公司进行排名。

## 第 4 步 — 找到决策者

使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 并结合：
- 从 ICP 中获取的 `person_titles` 和 `person_seniorities`
- `q_organization_domains_list` 限定为已丰富公司的域名
- 将 `per_page` 设置为 25

## 第 5 步 — 丰富排名靠前的潜在客户

> **信用警告**：在进行下一步之前，明确告知用户将消耗多少信用。

使用 `mcp__claude_ai_Apollo_MCP__apollo_people_bulk_match` 并结合：
- 每个人的 `first_name`、`last_name`、`domain`
- 将 `reveal_personal_emails` 设置为 `true`

如果超过 10 个潜在客户，请分批进行多次调用。

## 第 6 步 — 展示潜在客户表格

以排名表格的形式展示结果：

### 符合：[ICP 摘要]

| # | 名称 | 职位 | 公司 | 员工人数 | 收入 | 邮箱 | 电话 | ICP 匹配度 |

**ICP 匹配度评分：**
- **强** — 职位、资历级别、公司规模和行业都匹配
- **良好** — 4 项标准中有 3 项匹配
- **部分** — 4 项标准中有 2 项匹配

**摘要**：在 Y 家公司中找到 X 个潜在客户。消耗 Z 个信用。

## 第 7 步 — 提供下一步操作建议

询问用户：

1. **全部保存到 Apollo** — 通过 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create` 批量创建联系人，并设置 `run_dedupe: true` 对每个潜在客户
2. **加载到序列** — 询问哪个序列，并运行这些联系人的序列加载流程
3. **深入分析一家公司** — 对列表中的任何一家公司运行 `/apollo:company-intel`
4. **优化搜索** — 调整筛选条件并重新运行
5. **导出** — 将潜在客户格式化为 CSV 风格的表格，便于复制粘贴
