# 电子商务数据提取

使用 Apify 的电子商务抓取工具从任何电子商务平台提取产品数据、价格、评论和卖家信息。

## 前置条件

- `.env` 文件，包含 `APIFY_TOKEN`（位于 `~/.claude/.env`）
- Node.js 20.6+（用于原生 `--env-file` 支持）

## 工作流选择

| 用户需求 | 工作流 | 适用于 |
|-----------|----------|----------|
| 跟踪价格、比较产品 | 工作流 1：产品与价格 | 价格监控、MAP 合规性、竞争对手分析。添加 AI 摘要以获取洞察。 |
| 分析评论（情感或质量） | 工作流 2：评论 | 品牌认知、客户情感、质量问题、缺陷模式 |
| 在不同商店查找卖家 | 工作流 3：卖家 | 未经授权的转售商、通过 Google Shopping 发现供应商 |

## 进度跟踪

```
任务进度：
- [ ] 第 1 步：选择工作流并确定数据源
- [ ] 第 2 步：配置 Actor 输入
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行提取脚本
- [ ] 第 5 步：总结结果
```

---

## 工作流 1：产品与价格

**用例：** 提取产品数据、价格和库存状态。跟踪竞争对手价格、检测 MAP 违规、产品基准或市场调研。

**适用于：** 价格分析师、产品经理、市场研究人员。

### 输入选项

| 输入类型 | 字段 | 描述 |
|------------|-------|-------------|
| 产品 URL | `detailsUrls` | 直接指向产品页面的 URL（使用对象格式） |
| 分类 URL | `listingUrls` | 指向分类/搜索结果页面的 URL |
| 关键词搜索 | `keyword` + `marketplaces` | 在选定的市场中选择搜索词 |

### 示例 - 产品 URL
```json
{
  "detailsUrls": [
    {"url": "https://www.amazon.com/dp/B09V3KXJPB"},
    {"url": "https://www.walmart.com/ip/123456789"}
  ],
  "additionalProperties": true
}
```

### 示例 - 关键词搜索
```json
{
  "keyword": "Samsung Galaxy S24",
  "marketplaces": ["www.amazon.com", "www.walmart.com"],
  "additionalProperties": true,
  "maxProductResults": 50
}
```

### 可选：AI 摘要

添加这些字段以获取 AI 生成的洞察：

| 字段 | 描述 |
|-------|-------------|
| `fieldsToAnalyze` | 要分析的数据点：`["name", "offers", "brand", "description"]` |
| `customPrompt` | 自定义分析指令 |

**带 AI 摘要的示例：**
```json
{
  "keyword": "robot vacuum",
  "marketplaces": ["www.amazon.com"],
  "maxProductResults": 50,
  "additionalProperties": true,
  "fieldsToAnalyze": ["name", "offers", "brand"],
  "customPrompt": "总结价格范围并识别顶级品牌"
}
```

### 输出字段
- `name` - 产品名称
- `url` - 产品 URL
- `offers.price` - 当前价格
- `offers.priceCurrency` - 货币代码（可能因卖家地区而异）
- `brand.slogan` - 品牌名称（嵌套在对象中）
- `image` - 产品图片 URL
- 当 `additionalProperties: true` 时，提供额外的卖家/库存信息

> **注意：** 即使在美国搜索，结果中的货币也可能不同，因为价格反映了不同的卖家地区。

---

## 工作流 2：客户评论

**用例：** 提取评论用于情感分析、品牌认知监控或质量问题检测。

**适用于：** 品牌经理、客户体验团队、质量保证团队、产品经理。

### 输入选项

| 输入类型 | 字段 | 描述 |
|------------|-------|-------------|
| 产品 URL | `reviewListingUrls` | 从中提取评论的产品页面 |
| 关键词搜索 | `keywordReviews` + `marketplacesReviews` | 通过关键词搜索产品评论 |

### 示例 - 从产品提取评论
```json
{
  "reviewListingUrls": [
    {"url": "https://www.amazon.com/dp/B09V3KXJPB"}
  ],
  "sortReview": "Most recent",
  "additionalReviewProperties": true,
  "maxReviewResults": 500
}
```

### 示例 - 关键词搜索
```json
{
  "keywordReviews": "wireless earbuds",
  "marketplacesReviews": ["www.amazon.com"],
  "sortReview": "Most recent",
  "additionalReviewProperties": true,
  "maxReviewResults": 200
}
```

### 排序选项
- `Most recent` - 最新评论优先（推荐）
- `Most relevant` - 平台默认相关性
- `Most helpful` - 最高投票评论
- `Highest rated` - 5 星评论优先
- `Lowest rated` - 1 星评论优先

> **注意：** `sortReview: "Lowest rated"` 选项可能在不同市场不始终一致。对于质量分析，收集大量样本并在后处理中按评分筛选。

### 质量分析技巧
- 设置较高的 `maxReviewResults` 以确保统计显著性
- 查找重复关键词："broke", "defect", "quality", "returned"
- 如果排序不起作用，按评分筛选结果
- 与竞争对手产品进行交叉参考以进行基准测试

---

## 工作流 3：卖家情报

**用例：** 在不同商店查找卖家、发现未经授权的转售商、评估供应商选项。

**适用于：** 品牌保护团队、采购、供应链经理。

> **注意：** 此工作流使用 Google Shopping 在不同商店中查找卖家。不直接支持直接卖家资料 URL。

### 输入配置
```json
{
  "googleShoppingSearchKeyword": "Nike Air Max 90",
  "scrapeSellersFromGoogleShopping": true,
  "countryCode": "us",
  "maxGoogleShoppingSellersPerProduct": 20,
  "maxGoogleShoppingResults": 100
}
```

### 选项
| 字段 | 描述 |
|-------|-------------|
| `googleShoppingSearchKeyword` | 要搜索的产品名称 |
| `scrapeSellersFromGoogleShopping` | 设置为 `true` 以提取卖家 |
| `scrapeProductsFromGoogleShopping` | 设置为 `true` 以提取产品详细信息 |
| `countryCode` | 目标国家（例如，`us`、`uk`、`de`） |
| `maxGoogleShoppingSellersPerProduct` | 每个产品的最大卖家数量 |
| `maxGoogleShoppingResults` | 总结果限制 |

---

## 支持的市场

### 亚马逊（20+ 地区）
`www.amazon.com`、`www.amazon.co.uk`、`www.amazon.de`、`www.amazon.fr`、`www.amazon.it`、`www.amazon.es`、`www.amazon.ca`、`www.amazon.com.au`、`www.amazon.co.jp`、`www.amazon.in`、`www.amazon.com.br`、`www.amazon.com.mx`、`www.amazon.nl`、`www.amazon.pl`、`www.amazon.se`、`www.amazon.ae`、`www.amazon.sa`、`www.amazon.sg`、`www.amazon.com.tr`、`www.amazon.eg`

### 主要美国零售商
`www.walmart.com`、`www.costco.com`、`www.costco.ca`、`www.homedepot.com`

### 欧洲零售商
`allegro.pl`、`allegro.cz`、`allegro.sk`、`www.alza.cz`、`www.alza.sk`、`www.alza.de`、`www.alza.at`、`www.alza.hu`、`www.kaufland.de`、`www.kaufland.pl`、`www.kaufland.cz`、`www.kaufland.sk`、`www.kaufland.at`、`www.kaufland.fr`、`www.kaufland.it`、`www.cdiscount.com`

### IKEA（40+ 国家/语言组合）
支持所有主要 IKEA 区域网站，具有多种语言选项。

### Google Shopping
用于跨多个商店发现卖家。

---

## 运行提取

### 第 1 步：设置技能路径
```bash
SKILL_PATH=~/.claude/skills/apify-ecommerce
```

### 第 2 步：运行脚本

**快速回答（在聊天中显示）：**
```bash
node --env-file=~/.claude/.env $SKILL_PATH/reference/scripts/run_actor.js \
  --actor "apify/e-commerce-scraping-tool" \
  --input 'JSON_INPUT'
```

**CSV 导出：**
```bash
node --env-file=~/.claude/.env $SKILL_PATH/reference/scripts/run_actor.js \
  --actor "apify/e-commerce-scraping-tool" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.csv \
  --format csv
```

**JSON 导出：**
```bash
node --env-file=~/.claude/.env $SKILL_PATH/reference/scripts/run_actor.js \
  --actor "apify/e-commerce-scraping-tool" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.json \
  --format json
```

### 第 3 步：总结结果

报告：
- 提取的项目数量
- 文件位置（如果导出）
- 基于工作流的键洞察：
  - **产品：** 价格范围、异常值、MAP 违规
  - **评论：** 平均评分、情感趋势、质量问题
  - **卖家：** 卖家数量、发现的未经授权的卖家

---

## 错误处理

| 错误 | 解决方案 |
|-------|----------|
| `APIFY_TOKEN not found` | 确保 `~/.claude/.env` 包含 `APIFY_TOKEN=your_token` |
| `Actor not found` | 验证 Actor ID：`apify/e-commerce-scraping-tool` |
| `Run FAILED` | 检查错误输出中的 Apify 控制台链接 |
| `Timeout` | 减少 `maxProductResults` 或增加 `--timeout` |
| `No results` | 验证 URL 是否有效且可访问 |
| `Invalid marketplace` | 检查市场值是否与支持列表完全匹配 |
