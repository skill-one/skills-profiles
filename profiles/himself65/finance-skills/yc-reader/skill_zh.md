# Y Combinator Reader (只读)

从 [yc-oss/api](https://github.com/yc-oss/api) 获取 Y Combinator 公司数据，这是一个非官方的开源 API，索引了所有公开推出的 YC 公司。数据来源于 YC 的 Algolia 搜索索引，并通过 GitHub Actions 每日更新。

**这是一个只读数据源。** 它提供公司简介、批量列表、行业/标签细分、招聘状态和多元化数据。不存在写入操作——该 API 仅供静态 JSON 文件服务。

**无需认证。** 该 API 是公开且免费的。只需使用 `curl` 获取 JSON 端点。

---

## 第 1 步：验证先决条件

此技能只需要 `curl`（用于获取数据）和 `jq`（用于解析/过滤 JSON）。两者在大多数系统上都是预安装的。

```
!`(command -v curl > /dev/null && echo "CURL_OK" || echo "CURL_MISSING") && (command -v jq > /dev/null && echo "JQ_OK" || echo "JQ_MISSING")`
```

如果 `JQ_MISSING`，请安装它：

```bash
# macOS
brew install jq

# Linux (Debian/Ubuntu)
sudo apt-get install jq
```

如果 `jq` 不可用，您仍然可以使用 `curl` 获取原始 JSON，并使用 Python 或其他工具进行内联解析——但 `jq` 使过滤更加容易。

---

## 第 2 步：确定用户需求

将用户的请求匹配到相应的端点。参见 `references/api_reference.md` 获取完整详情。

| 用户请求 | 端点 | 备注 |
|---|---|---|
| 总体 YC 统计 | `meta.json` | 公司数量、批量列表、行业/标签列表 |
| 所有公司 | `companies/all.json` | 完整数据集 (~5,700 家公司) — 响应较大 |
| 顶尖公司 | `companies/top.json` | ~91 家表现优异的 YC 公司 |
| 招聘中的公司 | `companies/hiring.json` | ~1,400 家目前招聘的公司 |
| 非营利公司 | `companies/nonprofit.json` | YC 支持的非营利组织 |
| 多元化数据 | `companies/black-founded.json`, `hispanic-latino-founded.json`, `women-founded.json` | 创始人多元化 |
| 特定批量 | `batches/{batch-name}.json` | 例如，`winter-2026.json`, `spring-2026.json`, `fall-2025.json` |
| 单个公司简介 | `batches/{batch-name}/{slug}.json` | 例如，`batches/summer-2009/stripe.json`, `batches/winter-2009/airbnb.json` |
| 按行业 | `industries/{industry}.json` | 例如，`fintech.json`, `healthcare.json` |
| 按标签 | `tags/{tag}.json` | 例如，`ai.json`, `developer-tools.json` |

### 批量名称格式

批量使用 `{季节}-{年份}` 格式：`winter-2026`, `spring-2026`, `summer-2026`, `fall-2025`。较旧的批量遵循相同模式回溯到 `summer-2005`。简短形式 (`w09`, `s21`) 也适用于每个公司端点。

### 行业和标签名称格式

对于多词名称，使用小写和连字符：`real-estate`, `developer-tools`, `machine-learning`。

---

## 第 3 步：执行请求

### 基础 URL

```
https://yc-oss.github.io/api/
```

### 通用模式

```bash
# 获取并格式化输出
curl -s https://yc-oss.github.io/api/companies/top.json | jq .

# 统计结果中的公司数量
curl -s https://yc-oss.github.io/api/batches/winter-2025.json | jq length

# 按字段过滤（例如，批量中招聘的公司）
curl -s https://yc-oss.github.io/api/batches/winter-2025.json | jq '[.[] | select(.isHiring == true)]'

# 提取特定字段
curl -s https://yc-oss.github.io/api/companies/top.json | jq '.[] | {name, one_liner, batch, team_size, website}'

# 按名称搜索（不区分大小写）
curl -s https://yc-oss.github.io/api/companies/all.json | jq '[.[] | select(.name | test("stripe"; "i"))]'
```

### 关键规则

1. **使用 `-s` 标志**与 `curl` 结合以抑制进度输出
2. **通过 `jq` 管道**获取可读输出和过滤
3. **除非必要，避免获取 `companies/all.json`** — 响应较大 (~5,700 家公司)。尽可能使用更具体的端点（批量、行业、标签）
4. **使用 `jq` 选择/过滤**在 API 没有特定端点满足用户需求时，在客户端缩小结果
5. **批量名称使用小写和连字符** — `winter-2025` 而不是 `Winter 2025` 或 `W25`
6. **标签和行业名称使用小写和连字符** — `developer-tools` 而不是 `Developer Tools`

### 常用 `jq` 过滤器

| 过滤器 | 目的 |
|---|---|
| `jq length` | 统计结果 |
| `jq '.[0]'` | 第一个公司 |
| `jq '.[:10]'` | 前 10 家公司 |
| `jq '[.[] \| select(.isHiring == true)]'` | 仅招聘中的公司 |
| `jq '[.[] \| select(.status == "Active")]'` | 仅活跃公司 |
| `jq '[.[] \| select(.team_size > 100)]'` | 100 名以上员工的公司 |
| `jq '.[] \| {name, one_liner, batch, website}'` | 选择特定字段 |
| `jq '[.[] \| select(.name \| test("query"; "i"))]'` | 按名称搜索 |
| `jq 'sort_by(-.team_size) \| .[:10]'` | 按团队规模前 10 |

---

## 第 4 步：展示结果

获取数据后，清晰地展示结果以供创业/风险研究：

1. **总结关键数据** — 公司名称、一句话简介、批量、团队规模、状态和网站
2. **突出招聘状态** — 注意哪些公司正在积极招聘（增长信号）
3. **包含网站 URL**当用户可能想访问公司时
4. **对于批量列表**，总结批量规模和知名公司
5. **对于行业/标签查询**，突出趋势（多少家公司，哪些是顶尖/招聘中）
6. **对于研究查询**，提供汇总统计（数量、常见行业、团队规模分布）
7. **注意数据新鲜度** — API 每日更新，因此数据接近实时

---

## 第 5 步：诊断

如果请求失败：

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `404 Not Found` | 无效的批量、行业或标签名称 | 检查 `meta.json` 获取有效名称 |
| 空数组 `[]` | 没有公司匹配查询 | 放宽搜索范围或检查拼写 |
| `curl: Could not resolve host` | 没有互联网连接 | 检查网络连接 |
| 大/慢响应 | 获取 `companies/all.json` (5,700+ 条目) | 使用更具体的端点或添加 `jq` 过滤器 |

要发现有效的批量、行业和标签名称：

```bash
# 列出所有批量
curl -s https://yc-oss.github.io/api/meta.json | jq '.batches[].name'

# 列出所有行业
curl -s https://yc-oss.github.io/api/meta.json | jq '.industries[].name'

# 列出所有标签（有 333+ 个）
curl -s https://yc-oss.github.io/api/meta.json | jq '.tags[].name'
```

---

## 参考文件

- `references/api_reference.md` — 完整端点参考，包含公司字段模式、所有端点 URL 和研究工作流示例

当您需要确切的公司字段模式、有效的批量/行业/标签名称或详细研究工作流模式时，请阅读参考文件。
