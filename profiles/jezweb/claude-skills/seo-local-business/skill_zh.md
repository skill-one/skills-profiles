# 本地企业 SEO

为本地企业网站生成完整的 SEO 套件。生成元标签、结构化数据、robots.txt 和 sitemap.xml。

## 生成内容

1. 完整的 `<head>` 部分，包含元标签、Open Graph、Twitter Cards
2. JSON-LD 结构化数据（LocalBusiness + Service + FAQ 模式）
3. `robots.txt`
4. `sitemap.xml`

## 工作流程

### 第一步：收集企业信息

询问（或从现有网站提取）：

| 必填项 | 可选项 |
|--------|----------|
| 企业名称 | ABN |
| 主要服务 | 营业时间 |
| 位置（城市/郊区） | 社交媒体 URL |
| 电话号码 | 价格范围 |
| 网站URL | 服务区域（郊区） |
| 企业描述 | GPS坐标 |

### 第二步：生成头部标签

在以下模板中填写占位符：

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- 主要元标签 -->
  <title>{{PAGE_TITLE}} | {{BUSINESS_NAME}}</title>
  <meta name="title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta name="description" content="{{META_DESCRIPTION}}">

  <!-- 指定URL -->
  <link rel="canonical" href="{{CANONICAL_URL}}">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{{CANONICAL_URL}}">
  <meta property="og:title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta property="og:description" content="{{META_DESCRIPTION}}">
  <meta property="og:image" content="{{OG_IMAGE_URL}}">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:url" content="{{CANONICAL_URL}}">
  <meta property="twitter:title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta property="twitter:description" content="{{META_DESCRIPTION}}">
  <meta property="twitter:image" content="{{OG_IMAGE_URL}}">

  <!-- 地理标签（本地SEO） -->
  <meta name="geo.region" content="{{GEO_REGION}}">
  <meta name="geo.placename" content="{{CITY}}">
  <meta name="geo.position" content="{{LATITUDE}};{{LONGITUDE}}">
  <meta name="ICBM" content="{{LATITUDE}}, {{LONGITUDE}}">

  <!-- Favoricons -->
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">

  <!-- 结构化数据 -->
  <script type="application/ld+json">
    {{JSON_LD_SCHEMA}}
  </script>
</head>
```

**标题标签模式**（最多50-60个字符）：

| 页面 | 模式 | 示例 |
|------|---------|---------|
| 首页 | `品牌 - 标语` | `纽卡斯尔水管工 - 24/7紧急服务` |
| 服务 | `服务在地点 \| 品牌` | `纽卡斯尔热水维修 \| ABC水管工` |
| 关于 | `关于我们 \| 品牌` | `关于我们 \| ABC水管工纽卡斯尔` |
| 联系 | `联系 \| 品牌` | `联系我们 \| ABC水管工纽卡斯尔` |

**元描述模式**（150-160个字符）：

| 页面 | 模式 |
|------|---------|
| 首页 | `[USP]. [服务]在[地点]. [CTA]. 联系[电话].` |
| 服务 | `专业的[服务]在[地点]. [利益]. [信任信号]. 今天免费报价。` |
| 关于 | `[X]年服务[地点]. [团队信息]. [资质]. 了解[品牌].` |
| 联系 | `联系[品牌]提供[服务]在[地点]. [营业时间]. 联系[电话]或在线请求报价。` |

### 第三步：生成结构化数据

**LocalBusiness**（首页 — 总是包含）：

使用 `LocalBusiness` 或更具体的子类型：

| 子类型 | 用于 |
|---------|---------|
| `Plumber` | 水管服务 |
| `Electrician` | 电气服务 |
| `RoofingContractor` | 屋顶工程 |
| `HVACBusiness` | 空调/供暖 |
| `AutoRepair` | 汽车维修 |
| `BeautySalon` | 美容美发 |
| `Dentist` | 牙科诊所 |
| `LegalService` | 律师事务所 |
| `AccountingService` | 会计服务 |
| `RealEstateAgent` | 房地产中介 |
| `Restaurant` | 餐厅/咖啡馆 |
| `BarOrPub` | 酒吧/酒馆 |
| `Hotel` | 住宿 |
| `Store` | 零售商店 |
| `ProfessionalService` | 通用专业服务 |

LocalBusiness 模式属性：

| 属性 | 必填 | 备注 |
|----------|----------|-------|
| `@type` | 是 | `LocalBusiness` 或上述子类型 |
| `name` | 是 | 向客户展示的企业名称 |
| `image` | 是 | 主要企业图片或标志 |
| `description` | 是 | 1-2句企业描述 |
| `@id` | 是 | 唯一ID，使用 `{url}/#organization` |
| `url` | 是 | 网站主页URL |
| `telephone` | 是 | 国际格式：`+61-2-4900-1234` |
| `address` | 是 | 邮政地址（见下文） |
| `email` | 推荐 | 主要联系邮箱 |
| `priceRange` | 推荐 | `$` 到 `$$$$` |
| `geo` | 推荐 | GeoCoordinates：纬度/经度 |
| `openingHoursSpecification` | 推荐 | 见下方时间格式 |
| `areaServed` | 推荐 | 服务城市/郊区 |
| `sameAs` | 推荐 | 社交媒体个人资料URL |
| `taxID` | 可选 | 澳大利亚企业的ABN |
| `logo` | 可选 | 企业标志URL |
| `foundingDate` | 可选 | ISO 8601日期 |
| `paymentAccepted` | 可选 | 例如："现金、信用卡、EFTPOS" |
| `currenciesAccepted` | 可选 | `AUD` |

邮政地址：

| 属性 | 示例 |
|----------|---------|
| `streetAddress` | `123 Hunter Street` |
| `addressLocality` | `Newcastle` |
| `addressRegion` | `NSW` |
| `postalCode` | `2300` |
| `addressCountry` | `AU` |

示例：

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "ABC Plumbing Newcastle",
  "image": "https://www.abcplumbing.com.au/og-image.jpg",
  "description": "纽卡斯尔和Lake Macquarie的专业水管服务。",
  "@id": "https://www.abcplumbing.com.au/#organization",
  "url": "https://www.abcplumbing.com.au",
  "telephone": "+61-2-4900-1234",
  "email": "info@abcplumbing.com.au",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Hunter Street",
    "addressLocality": "Newcastle",
    "addressRegion": "NSW",
    "postalCode": "2300",
    "addressCountry": "AU"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -32.9283,
    "longitude": 151.7817
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "07:00",
      "closes": "17:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Saturday"],
      "opens": "08:00",
      "closes": "12:00"
    }
  ],
  "areaServed": [
    { "@type": "City", "name": "Newcastle" },
    { "@type": "City", "name": "Lake Macquarie" }
  ],
  "sameAs": [
    "https://www.facebook.com/abcplumbing",
    "https://www.instagram.com/abcplumbing"
  ]
}
```

**Service**（服务页面 — 每个服务添加）：

| 属性 | 必填 | 备注 |
|----------|----------|-------|
| `name` | 是 | 服务名称 |
| `description` | 是 | 服务提供的内容 |
| `provider` | 是 | `{ "@id": "{url}/#organization" }` |
| `areaServed` | 推荐 | 城市/地区 |
| `serviceType` | 推荐 | 服务类别 |
| `offers` | 可选 | 定价/可用性 |

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Hot Water System Installation",
  "description": "纽卡斯尔专业的热水系统安装和更换。",
  "provider": { "@id": "https://www.abcplumbing.com.au/#organization" },
  "areaServed": { "@type": "City", "name": "Newcastle" },
  "serviceType": "Plumbing",
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "priceRange": "$$"
  }
}
```

**FAQ**（带有FAQ部分的页面）：

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "纽卡斯尔水管工费用是多少？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "纽卡斯尔水管工出诊费通常在$80-150。"
      }
    }
  ]
}
```

### 第四步：生成 robots.txt 和 sitemap.xml

**robots.txt:**

```
User-agent: *
Allow: /

Sitemap: {{SITE_URL}}/sitemap.xml
```

**sitemap.xml:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{{SITE_URL}}/</loc>
    <lastmod>{{DATE}}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- 每页添加一个 <url>. 优先级：1.0首页，0.8服务，0.6其他 -->
</urlset>
```

### 第五步：验证

在 https://validator.schema.org/ 测试结构化数据

常见验证错误：
- 缺少 `@context` — 每个JSON-LD块都需要它
- 电话格式错误 — 必须是国际格式 (`+61-...`)
- 缺少 `@id` — 需要用于模式之间的交叉引用
- `areaServed` 为空 — 至少包含一个城市

## 澳大利亚特定模式

### 电话号码

```html
<!-- 链接：国际格式。显示：本地格式。 -->
<a href="tel:+61249001234">(02) 4900 1234</a>
```

Schema 电话：`"+61-2-4900-1234"`

| 前缀 | 国际 |
|--------|---------|
| 02 | +612 |
| 04 | +614 |
| 1300 | 保持原样 |

### ABN

在LocalBusiness模式中提供时添加：

```json
{ "taxID": "12 345 678 901" }
```

### 澳大利亚州代码

| 州 | 代码 | 地理区域 |
|--------|------|----------|
| 新南威尔士州 | NSW | AU-NSW |
| 维多利亚州 | VIC | AU-VIC |
| 昆士兰州 | QLD | AU-QLD |
| 南澳大利亚州 | SA | AU-SA |
| 西澳大利亚州 | WA | AU-WA |
| 塔斯马尼亚州 | TAS | AU-TAS |
| 北领地 | NT | AU-NT |
| ACT | ACT | AU-ACT |

### 服务区域

使用 `areaServed` 与澳大利亚城市和郊区名称（见LocalBusiness示例）。
