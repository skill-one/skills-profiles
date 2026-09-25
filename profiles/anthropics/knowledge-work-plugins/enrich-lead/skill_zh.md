# 丰富潜在客户信息

将任何标识符转换为完整的联系人档案。用户通过 "$ARGUMENTS" 提供识别信息。

## 示例

- `/apollo:enrich-lead Tim Zheng at Apollo`
- `/apollo:enrich-lead https://www.linkedin.com/in/timzheng`
- `/apollo:enrich-lead sarah@stripe.com`
- `/apollo:enrich-lead Jane Smith, VP Engineering, Notion`
- `/apollo:enrich-lead CEO of Figma`

## 第 1 步 — 解析输入

从 "$ARGUMENTS" 中提取可用的每个标识符：
- 名字、姓氏
- 公司名称或域名
- LinkedIn URL
- 电子邮件地址
- 职位（用作匹配提示）

如果输入是模糊的（例如，只是 "CEO of Figma"），首先使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 并使用相关的职位和域名过滤器来识别该人，然后继续丰富。

## 第 2 步 — 丰富个人信息

> **信用警告**：在调用之前，告知用户丰富信息会消耗 1 个 Apollo 信用点。

使用 `mcp__claude_ai_Apollo_MCP__apollo_people_match` 并使用所有可用的标识符：
- 如果知道姓名，则使用 `first_name`、`last_name`
- 如果知道公司，则使用 `domain` 或 `organization_name`
- 如果提供了 LinkedIn，则使用 `linkedin_url`
- 如果提供了电子邮件，则使用 `email`
- 将 `reveal_personal_emails` 设置为 `true`

如果匹配失败，尝试使用更宽松的过滤器使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 并提供前 3 名候选人。要求用户选择一个，然后重新丰富。

## 第 3 步 — 丰富其公司信息

使用 `mcp__claude_ai_Apollo_MCP__apollo_organizations_enrich` 并使用该人的公司域名来获取公司背景信息。

## 第 4 步 — 展示联系人卡

将输出格式化为如下所示：

---

**[全名]** | [职位]
[公司名称] · [行业] · [员工人数] 名员工

| 字段 | 详情 |
|---|---|
| 工作电子邮件 | ... |
| 个人电子邮件 | ... (如果公开) |
| 直接电话 | ... |
| 手机电话 | ... |
| 公司电话 | ... |
| 地址 | 城市、州、国家 |
| LinkedIn | URL |
| 公司域名 | ... |
| 公司收入 | 范围 |
| 公司融资 | 总融资额 |
| 公司总部 | 地址 |

---

## 第 5 步 — 提供后续操作选项

询问用户要采取哪个操作：

1. **保存到 Apollo** — 通过 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create` 创建此人作为联系人，并设置 `run_dedupe: true`
2. **添加到序列** — 询问哪个序列，然后运行序列加载流程
3. **查找同事** — 使用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 并设置 `q_organization_domains_list` 为该公司，搜索该公司的其他人
4. **查找类似的人** — 搜索其他公司中具有相同职位/级别的人
