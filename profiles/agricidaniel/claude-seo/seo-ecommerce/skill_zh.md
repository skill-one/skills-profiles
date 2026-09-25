# 电子商务SEO分析

全面的商品页面优化、市场情报和竞争性价格分析。可独立使用（页面内+模式）或与DataForSEO Merchant API配合使用，获取实时Google Shopping和Amazon数据。

## 命令

| 命令 | 目的 | DataForSEO? |
|------|------|-------------|
| `/seo ecommerce <url>` | 商品页面或店铺的全面电子商务SEO分析 | 可选 |
| `/seo ecommerce products <keyword>` | Google Shopping竞争分析 | 必须使用 |
| `/seo ecommerce gaps <domain>` | 关键词差距：有机搜索与Shopping可见性 | 必须使用 |
| `/seo ecommerce schema <url>` | 商品模式验证和增强 | 不需要 |

---

## 1. 商品页面分析（不需要DataForSEO）

获取并解析任何商品页面，用于页面内SEO质量分析。

### 工作流程

```
1. "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run render_page.py <url> --mode auto → 原始/渲染的HTML
2. "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run parse_html.py --url <url>   → SEO元素
3. 分析特定商品信号（如下）
```

### 商品SEO检查清单

#### 标题标签
- [ ] 包含主要商品关键词
- [ ] 包含品牌名称
- [ ] 60个字符以内（SERP中不会截断）
- [ ] 格式：`[商品名称] - [主要功能] | [品牌]`

#### 元描述
- [ ] 包含商品关键词+利益点
- [ ] 包含价格或"从$XX"（触发丰富片段兴趣）
- [ ] 行动号召存在（立即购买、购买、免费配送）
- [ ] 155个字符以内

#### 标题结构
- [ ] 单个H1匹配主要商品名称
- [ ] H2用于：功能、规格、评论、相关商品
- [ ] 商品变体之间没有重复的H1标签

#### 商品图片
- [ ] Alt文本包含商品名称+区分性特征
- [ ] 文件名具有描述性（不是`IMG_001.jpg`）
- [ ] 提供WebP格式（带JPEG回退）
- [ ] 每个商品至少3张图片（主图、细节图、生活方式图）
- [ ] 高分辨率图片：Google建议至少50K像素（宽度x高度）用于商家列表；常见做法是更大（例如800px+），但不是规则
- [ ] 仅对折叠下方的图片进行懒加载

#### 内部链接
- [ ] 面包屑导航：首页 > 分类 > 子分类 > 商品
- [ ] 相关商品部分（交叉销售/追加销售）
- [ ] 使用关键词丰富的锚链接返回分类页面
- [ ] 评论部分链接到完整评论页面（如果分开）

#### 内容质量
- [ ] 独特的商品描述（不是制造商复制粘贴）
- [ ] 商品描述正文字数>=200
- [ ] 规格表格存在（不只是散文）
- [ ] 页面上的用户评论（UGC信号）

### 评分

| 类别 | 权重 | 标准 |
|------|------|------|
| 模式完整性 | 25% | 必需+推荐的商品字段 |
| 标题和元数据 | 15% | 关键词位置、长度、格式 |
| 图片优化 | 20% | Alt文本、格式、尺寸、数量 |
| 内容质量 | 20% | 独特描述、规格、评论 |
| 内部链接 | 10% | 面包屑、相关商品、分类 |
| 技术 | 10% | 页面速度、移动渲染、规范 |

---

## 2. Google Shopping情报（DataForSEO Merchant API）

来自Google Shopping结果的实时竞争分析。

### 成本控制（强制）

在每次Merchant API调用之前：
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py check merchant_google_products_search
```

- `"status": "approved"` -- 继续
- `"status": "needs_approval"` -- 显示成本，询问用户
- `"status": "blocked"` -- 停止，通知用户

每次调用后：
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py log merchant_google_products_search <成本>
```

### 工作流程

```bash
# 商品搜索：谁在什么价格销售什么
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_merchant.py search "<keyword>" --marketplace google

# 卖家分析：商家评分和主导地位
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_merchant.py sellers "<keyword>"

# 规范化结果用于分析
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_normalize.py results.json --module merchant
```

### 分析输出

#### 定价情报
- 价格分布：最小值、最大值、中位数、P25、P75
- 价格异常值（>中位数2个标准差）
- 价格与评分的相关性
- 货币归一化为美元（或用户指定）

#### 卖家格局
- 按列表数量排名的前10名卖家
- 商家评分分布
- 免费配送的普及率
- 新卖家与成熟卖家

#### 商品列表质量
- 顶级列表中的标题关键词模式
- 平均评分和评论数量基准
- 每个列表的图片数量
- 可用性状态分布

加载`references/marketplace-endpoints.md`获取完整的API参数详情。

---

## 3. Amazon市场（DataForSEO）

跨市场情报，比较Google Shopping和Amazon。

### 成本控制（强制）

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py check merchant_amazon_products_search
```

Amazon端点在`warn_endpoints`集合中——始终需要用户批准。

### 工作流程

```bash
# Amazon商品搜索
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_merchant.py search "<keyword>" --marketplace amazon

# 跨市场比较
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_merchant.py compare "<keyword>"
```

### 跨市场报告

| 指标 | Google Shopping | Amazon |
|------|---------------|--------|
| 平均价格 | $ | $ |
| 中位数评分 | X.X | X.X |
| 平均评论数量 | N | N |
| 顶级卖家份额 | % | % |
| 免费配送 % | % | % |

---

## 4. 市场关键词差距

识别有机搜索和Shopping可见性之间的不匹配。

### 工作流程

1. 通过seo-dataforseo获取有机排名：
   `dataforseo_labs_google_ranked_keywords`用于域名
2. 通过Merchant REST脚本获取Google Shopping存在性（不是MCP工具；成本账本键是`merchant_google_products_search`）：
   `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_merchant.py search <keyword>`
   用于顶级有机关键词
3. 交叉参考结果

### 差距类型

| 差距类型 | 含义 | 行动 |
|----------|------|------|
| **有机搜索仅** | 有机搜索排名但无Shopping广告 | 创建Google Merchant Center数据源，对关键词出价 |
| **Shopping仅** | Shopping可见但有机弱/无 | 创建内容（购买指南、比较页面）用于这些关键词 |
| **两者都存在** | 在两个渠道中可见 | 优化：确保价格一致性，增强模式 |
| **两者都无** | 在任一渠道中无可见性 | 低优先级，除非高流量 |

### 输出格式

```
## 关键词差距分析：example.com

### 机会：有机搜索→Shopping（12个关键词）
| 关键词 | 有机排名 | 流量 | CPC | 推荐行动 |
|--------|----------|------|-----|----------|

### 机会：Shopping→有机搜索（8个关键词）
| 关键词 | Shopping排名 | 流量 | CPC | 需要的内容类型 |
|--------|-------------|------|-----|--------------|
```

---

## 5. 商品模式增强

验证并生成符合Google当前要求的商品模式。

### 确认必需属性（Google Merchant）

确认必需字段是`name`、`image`和`offers`；商家列表使用`Offer`，而不是`AggregateOffer`。商家列表要求`price`大于零，且设置`price`时必须设置`priceCurrency`。

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "",
  "image": [""],
  "offers": {
    "@type": "Offer",
    "url": "",
    "priceCurrency": "USD",
    "price": "49.00",
    "availability": "https://schema.org/InStock"
  }
}
```

### 推荐属性（增强丰富结果）

- `sku` -- 商品标识符
- `description`, `brand`, `offers.seller` -- 推荐上下文字段
- `gtin13` / `gtin14` / `mpn` -- 全球贸易标识符
- `aggregateRating` -- 星级评分+评论数量
- `review` -- 单个评论（至少1个）
- `color`, `material`, `size` -- 变体属性
- `shippingDetails` -- ShippingDetails带运费和交付时间（商家级配送通过`ShippingService`也受支持；搜索控制台中的运费/退货可以在没有Merchant Center账户的情况下设置）
- `hasMerchantReturnPolicy` -- MerchantReturnPolicy带类型和天数
- `hasAdultConsideration` -- **成人导向产品必需**（2026-05-20添加到Product变体/商家列表）；Google搜索仅支持值`https://schema.org/SexualContentConsideration`
- `category` -- `Text`、`CategoryCode`或两者混合的数组。使用自定义文本用于商家定义的商品类型，`CategoryCode`带Google分类URL和`codeValue`用于Google商品分类。

### 验证规则

1. `price`必须是数字字符串，不是`$29.99`（无货币符号）
2. `availability`必须使用完整的Schema.org URL枚举
3. `image`应该是包含>=1张高分辨率图片URL的数组
4. `priceCurrency`必须是ISO 4217（USD、EUR、GBP）
5. 如果`brand`存在，`brand.name`不能为空或"N/A"
6. 销售期使用`validFrom`加上`validThrough`或`priceValidUntil`，以ISO 8601格式。已知时包含时间和时区。
7. 如果`aggregateRating`存在：`ratingValue`和`reviewCount`必需（商家列表文档列出`reviewCount`；评论片段文档也接受`ratingCount`）
8. 不要在可见内容或结构化数据中包含虚假评论或未披露的激励性评论。明确且突出显示激励措施。

### 模式评分

| 完整性 | 分数 |
|-------|------|
| 所有必需字段 | 50/100 |
| + aggregateRating | 65/100 |
| + sku/gtin/mpn | 75/100 |
| + shippingDetails | 85/100 |
| + merchantReturnPolicy | 90/100 |
| + 评论（3个+） | 100/100 |

---

## 跨技能集成

| 技能 | 集成点 |
|------|--------|
| **seo-schema** | 委托商品模式生成；重用验证逻辑 |
| **seo-images** | 商品图片审计（Alt文本、格式、尺寸），加上`DigitalSourceType: TrainedAlgorithmicMedia` IPTC标签用于AI生成的商品图片（Merchant Center要求） |
| **seo-content** | 商品描述E-E-A-T和独特性分析 |
| **seo-dataforseo** | 有机关键词排名用于差距分析 |
| **seo-technical** | 商品页面的核心Web Vitals（LCP在主图上） |
| **seo-hreflang** | 区域特定结果单元：在EEA，商品查询可以显示聚合器和供应商单元；EEA、南非和土耳其也有结构化数据轮播，每个都有其自身的资格规则（记录于2026-09-08） |
| **seo-google** | GSC索引+商品URL的性能数据（不是Merchant Center数据源验证，那是在Merchant Center/**Merchant API**；旧版购物内容API将于2026-08-18停用） |

## UCP：通用商业协议（实时）

由Google发起的开放标准（与Shopify、Etsy、Wayfair、Target、Walmart共同开发；支付合作伙伴Visa/Mastercard/Stripe/Adyen/Amex），
允许AI代理发现、协商和与商家交易，无需一次性集成。Google确认在AI模式下搜索中的对话式购买有首个参考实现。
更广泛的Universal Cart推广细节来自Google I/O 2026主旨演讲报道；未在Google拥有的源上确认。ucp.dev列出了**2026-08-25**作为最新规范发布（Google的商家指南仍记录2026-04-08）在其**基于日期的版本**方案中，不是`1.0`；两条集成路径：**原生**（默认）和**嵌入式**（批准商家）。与**AP2**（据报道正转向FIDO治理）配对。规范：developers.google.com/merchant/ucp和ucp.dev。

已在**Google Merchant Center**上使用干净商品模式的商家可以声明UCP配置文件在`/.well-known/ucp`列出功能
(`dev.ucp.shopping.checkout`, `.fulfillment`, `.discount`)。参见
`references/ucp-universal-commerce-protocol.md`获取审计标准、功能示例以及与AP2（Agent Payments Protocol）的关系。

### 审计命令

```bash
# 发现和验证UCP配置文件
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run ucp_check.py https://store.example.com --json

# 带端点可达性探测（对每个声明的功能进行HEAD）
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run ucp_check.py https://store.example.com --probe-endpoints --json
```

脚本返回：配置文件存在、版本、声明功能、结构问题（缺少字段、未知功能ID），以及（带`--probe-endpoints`）每个端点的可达性。SSRF阻止的端点明确报告。缺少配置文件报告为机会，不是失败。UCP本身是实时的；早期的是广泛的商家采用。将字面`"version": "1.0"`标记为无效（UCP版本基于日期，例如`2026-04-08`）。

---

## 错误处理

| 错误 | 原因 | 响应 |
|------|------|------|
| 未找到商品模式 | 页面缺少JSON-LD | 分析页面内容，生成推荐模式 |
| DataForSEO凭证缺失 | 环境变量未设置 | 无需市场数据运行分析，注意限制 |
| 成本检查阻止 | 每日预算超出 | 通知用户，提供仅免费分析 |
| 空Shopping结果 | 关键词无商品 | 建议更广泛的关键词，检查位置设置 |
| Amazon API超时 | 网络/速率限制 | 带退避重试，回退到仅Google |
| 无效URL | 输入格式错误 | 通过`google_auth.validate_url()`验证，显示错误 |
| 非商品页面 | URL是分类/主页 | 运行商店级检查（UCP配置文件、分类结构、数据源）并请求商品URL进行商品级检查 |

---

## 输出模板

```
## 电子商务SEO报告：[URL或关键词]

### 总体分数：XX/100

### 商品页面SEO
- 模式完整性：XX/100
- 标题和元数据：XX/100
- 图片优化：XX/100
- 内容质量：XX/100
- 内部链接：XX/100

### 市场情报（如果DataForSEO可用）
- Google Shopping列表：N个商品找到
- 价格范围：$XX - $XX（中位数：$XX）
- 顶级卖家：[名称]（XX%市场份额）
- Amazon比较：[可用/未检查]

### 顶级建议
1. [关键] ...
2. [高] ...
3. [中] ...

生成PDF报告？使用`/seo google report`
```
