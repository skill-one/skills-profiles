# Hreflang & 国际 SEO

验证现有的 hreflang 实现，或为多语言和多地区的网站生成正确的 hreflang 标签。支持 HTML、HTTP 头和 XML 站点地图实现。

## 验证检查

### 1. 自引用标签
- 每个页面都必须包含指向自身的 hreflang 标签
- 自引用 URL 必须与页面的规范 URL 完全匹配
- 缺少自引用标签会导致 Google 忽略整个 hreflang 集合

### 2. 返回标签
- 如果页面 A 通过 hreflang 链接到页面 B，页面 B 必须返回链接到页面 A
- 每个 hreflang 关系必须是双向的（A→B 和 B→A）
- 缺少返回标签会使两个页面的 hreflang 信号失效
- 检查所有语言版本都相互引用（完整网格）

### 3. x-default 标签
- 当存在选择器/回退 URL 时推荐使用：指定未匹配语言/地区的回退页面
- 通常指向语言选择页面或英文版本
- 每组替代品只能有一个 x-default
- 也必须从所有其他语言版本返回链接

### 4. 语言代码验证
- 必须使用 ISO 639-1 两个字母代码（例如，`en`、`fr`、`de`、`ja`）
- 可选的 ISO 15924 脚本子标签是文档中记录的、官方的脚本机制：`zh-Hant`（繁體） / `zh-Hans`（简体中文）。脚本可以与地区组合，例如 `zh-Hans-US` 是有效的（语言 + 脚本 + 地区）。
- 常见错误：
  - `eng` 而不是 `en`（ISO 639-2，hreflang 无效）
  - `jp` 而不是 `ja`（日语的错误代码）
  - `zh` 对于特定脚本的页面是有效的，但模糊；在针对特定脚本时，优先使用 `zh-Hans` 或 `zh-Hant`

### 5. 地区代码验证
- 可选的地区限定符使用 ISO 3166-1 Alpha-2（例如，`en-US`、`en-GB`、`pt-BR`）
- 格式：`language-REGION`（小写语言，大写地区）
- 单独的国家代码是无效的，你不能在没有语言的情况下指定地区（Google 自己的坏例子是 `be`，实际上是白俄罗斯 *语言* 代码，而不是比利时）。
- 常见错误：
  - `en-uk` 而不是 `en-GB`（英国不是一个有效的 ISO 3166-1 地区代码）
  - `EU` / `UN` 作为地区（不是有效的 ISO 3166-1 值）
  - `es-LA`（拉丁美洲不是一个国家；使用具体国家）
  - 没有语言前缀的地区

### 5b. 地区定位信号层次结构
- 实用的语言环境信号启发式方法：**ccTLD > hreflang 注释 > 服务器位置/IP > 地址/语言/货币/业务简介**。不要将其呈现为确认的 Google 排名顺序。hreflang 是一个 **提示，不是指令**。Google **忽略** 定位元标签和 HTML 地区定位属性。
- 搜索控制台 **国际定位报告和手动国家定位设置已于 2022 年移除**，**不要** 建议在 GSC 中设置国家定位；hreflang 是剩余的杠杆。

### 5c. 地区特定搜索单元（EEA、南非、土耳其）
- Google 文档记录了仅在特定地区存在的搜索体验（文档添加于 2026-09-08；https://developers.google.com/search/docs/appearance/aggregator-features）：
  - **仅 EEA**：聚合单元和供应商单元（酒店、航班、地面交通、产品和自 2026-09-18 的本地企业），生态系统轮播和职位网站功能。
  - **土耳其**：地点网站功能（酒店、本地企业）。
  - **南非**：旅行、产品、汽车租赁、食品配送和地面交通的徽章和细化芯片。
  - **所有三个地区的结构化数据轮播**，具有不同的查询类型。
  合格性和参与情况按单元记录；它们不是排名信号。
- 当网站使用 hreflang 变体为这些地区提供服务时，请在报告中注明业务是聚合商还是直接供应商，并指向区域文档，以便客户在这些市场不会对不同的结果布局感到惊讶。

### 6. 规范 URL 对齐
- hreflang 标签只能出现在规范 URL 上
- 如果页面有 `rel=canonical` 指向其他地方，该页面的 hreflang 将被忽略
- 规范 URL 和 hreflang URL 必须完全匹配（包括尾随斜杠）
- 非规范页面不应在任何 hreflang 集合中

### 7. 协议一致性
- hreflang 集合中的所有 URL 必须使用相同的协议（HTTPS 或 HTTP）
- hreflang 集合中的 HTTP/HTTPS 混合会导致验证失败
- HTTPS 迁移后，更新所有 hreflang 标签为 HTTPS

### 8. 跨域支持
- hreflang 可在不同的域之间工作（例如，example.com 和 example.de）
- 跨域 hreflang 要求两个域都有返回标签
- 在需要时使用 Google 搜索控制台验证进行监控或跨站点站点地图提交
- 推荐使用基于站点地图的实现进行跨域设置

## 常见错误

| 问题 | 严重性 | 修复 |
|------|--------|------|
| 缺少自引用标签 | 关键 | 添加指向相同页面 URL 的 hreflang |
| 缺少返回标签（A→B 但没有 B→A） | 关键 | 在所有替代品上添加匹配的返回标签 |
| 缺少 x-default 当需要回退行为时 | 中等 | 添加指向回退/选择器页面的 x-default |
| 无效语言代码（例如，`eng`） | 高 | 使用 ISO 639-1 两个字母代码 |
| 无效地区代码（例如，`en-uk`） | 高 | 使用 ISO 3166-1 Alpha-2 代码 |
| 非规范 URL 上的 hreflang | 高 | 仅将 hreflang 移至规范 URL |
| HTTP/HTTPS URL 不匹配 | 中等 | 标准化所有 URL 为 HTTPS |
| 尾随斜杠不一致 | 中等 | 完全匹配规范 URL 格式 |
| HTML 和站点地图中的 hreflang | 低 | 选择一种方法（推荐站点地图用于大型网站） |
| 需要地区时没有地区 | 低 | 为地理定位内容添加地区限定符 |

## 实现方法

### 方法 1：HTML 链接标签
适用于每页少于 50 个语言/地区变体的网站。

```html
<link rel="alternate" hreflang="en-US" href="https://example.com/page" />
<link rel="alternate" hreflang="en-GB" href="https://example.co.uk/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

放在 `<head>` 部分。每个页面都必须包含所有替代品，包括自身。

### 方法 2：HTTP 头
适用于非 HTML 文件（PDF、文档）。

```
Link: <https://example.com/page>; rel="alternate"; hreflang="en-US",
      <https://example.com/fr/page>; rel="alternate"; hreflang="fr",
      <https://example.com/page>; rel="alternate"; hreflang="x-default"
```

通过服务器配置或 CDN 规则设置。

### 方法 3：XML 站点地图（推荐用于大型网站）
适用于具有许多语言变体、跨域设置或 50+ 页面的网站。

见下方的 Hreflang 站点地图生成部分。

### 方法比较

| 方法 | 适用于 | 优点 | 缺点 |
|------|--------|------|------|
| HTML 链接标签 | 小型网站（<50 变体） | 易于实现，源代码可见 | 增加头部大小，难以大规模维护 |
| HTTP 头 | 非HTML文件 | 适用于 PDF、图像 | 服务器配置复杂，HTML 中不可见 |
| XML 站点地图 | 大型网站、跨域 | 可扩展，集中管理 | 页面上不可见，需要站点地图维护 |

## Hreflang 生成

### 流程
1. **检测语言**：扫描网站以查找语言指示器（URL 路径、子域名、TLD、HTML lang 属性）
2. **映射页面等价物**：跨语言/地区匹配相应页面
3. **验证语言代码**：验证所有代码是否符合 ISO 639-1 和 ISO 3166-1
4. **生成标签**：为每个页面创建 hreflang 标签，包括自引用
5. **验证返回标签**：确认所有关系都是双向的
6. **添加 x-default**：为每个页面集设置回退
7. **输出**：生成实现代码（HTML、HTTP 头或站点地图 XML）

## Hreflang 站点地图生成

### 带有 Hreflang 的站点地图

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/page</loc>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.de/page" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
  </url>
  <url>
    <loc>https://example.com/fr/page</loc>
    <xhtml:link rel="alternate" hreflang="en-US" href="https://example.com/page" />
    <xhtml:link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.de/page" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/page" />
  </url>
</urlset>
```

关键规则：
- 包含 `xmlns:xhtml` 命名空间声明
- 每个 `<url>` 条目必须包含所有语言替代品（包括自身）
- 每个替代品必须作为单独的 `<url>` 条目出现，并具有自己的完整集
- 以哪个先出现为准：50,000 个 URL 或 50MB 未压缩的每个站点地图文件

## 输出

### Hreflang 验证报告

#### 摘要
- 扫描页面总数：XX
- 检测到的语言变体：XX
- 发现的问题：XX（关键：X，高：X，中：X，低：X）

#### 验证结果

| 语言 | URL | 自引用 | 返回标签 | x-default | 状态 |
|------|-----|--------|----------|-----------|------|
| en-US | https://... | ✅ | ✅ | ✅ | ✅ |
| fr | https://... | ❌ | ⚠️ | ✅ | ❌ |
| de | https://... | ✅ | ❌ | ✅ | ❌ |

### 生成的 Hreflang 标签
- HTML `<link>` 标签（如果选择 HTML 方法）
- HTTP 头值（如果选择头方法）
- `hreflang-sitemap.xml`（如果选择站点地图方法）

### 建议
- 需要添加的缺失实现
- 需要修复的错误代码
- 方法迁移建议（例如，HTML 到站点地图以实现规模）

## 文化适应评估

在分析多语言网站时，除了技术 hreflang 验证外，还要评估内容是否针对每个目标市场进行了文化适应。

加载 `references/cultural-profiles.md` 获取预构建的配置文件（DACH、法语区、西班牙语区、日语）。

**评估步骤：**
1. 确定所有语言版本及其目标市场
2. 加载相关的文化配置文件
3. 检查 CTA 是否符合文化期望（直接 vs 间接）
4. 检查信任信号是否适合本地（认证、法律页面）
5. 检查本地化页面上的外国品牌引用
6. 检查数字/日期/货币格式一致性
7. 将文化适应问题标记为中等严重性

**输出：** 每个语言版本的 0-100 文化适应分数和具体发现。

## 内容一致性审计

**命令：** `/seo hreflang audit <目录或 URL>`

审计网站所有语言版本或本地内容目录之间的内容一致性。

加载 `references/content-parity.md` 获取完整的等价矩阵和评分方法。

**检查内容：**
- 跨所有声明语言的页面存在性
- 章节结构等价性（H2/H3 计数）
- SEO 元素一致性（标题、元、结构化数据本地化）
- 词数比例验证（DE 应比 EN 长 25-35%，JA 应比 EN 短 10-25%）
- 新鲜度跟踪（通过时间戳检测陈旧翻译）
- 文化标记扫描（外国品牌、错误的法律引用、未翻译的元素）

**输出：** 一致性矩阵表，包含每页分数和优先行动项。

## 本地化格式验证

加载 `references/locale-formats.md` 获取每个本地化的数字、日期、货币、地址和电话格式参考表。

**检查：**
- 数字格式一致性（例如，"1,000.00" 应在 de-DE 页面上为 "1.000,00"）
- 日期格式符合本地化期望
- 货币符号和位置正确
- 电话号码使用国际格式并带有正确的国家代码

## 参考文件

按需加载（不要在启动时加载所有文件）：
- `references/cultural-profiles.md`：DACH、法语区、西班牙语区、日语文化适应配置文件
- `references/locale-formats.md`：每个本地化的数字、日期、货币、地址、电话格式表
- `references/content-parity.md`：内容一致性审计方法和评分
- `references/machine-translation-qa.md`：标记未审核的机器翻译，Google 的垃圾邮件政策将其视为规模内容滥用

## 错误处理

| 情景 | 操作 |
|------|------|
| URL 不可达（DNS 失败、连接拒绝） | 清晰地报告错误。不要猜测网站结构。建议用户验证 URL 并重试。 |
| 未找到 hreflang 标签 | 报告缺失。检查其他国际化信号（子目录、子域名、ccTLD）并建议适当的 hreflang 实现方法。 |
| 检测到无效语言/地区代码 | 列出每个无效代码及其正确替换。提供准备好的修正 hreflang 标签集。 |
| 语言没有可用的文化配置文件 | 使用 `cultural-profiles.md` 中的默认配置文件清单。请注意，评估基于一般指南，而不是预构建配置文件。 |
| 内容一致性目录为空 | 报告未找到内容文件。建议验证目录路径或提供 URL 进行实时网站分析。 |
