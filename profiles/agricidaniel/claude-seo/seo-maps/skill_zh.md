# 地图智能分析 (2026年3月)

本地企业地图平台分析工具。通过与外部API合作，评估企业在谷歌地图、必应地点、苹果地图和OpenStreetMap上的展示情况。

**与seo-local的界限：** 此技能通过API分析地图平台上的企业。seo-local分析网站上的本地SEO信号（通过HTML抓取）。不要重复seo-local的页面分析。建议使用`/seo local <url>`进行网站级别的检查。

---

## 快速参考

| 命令 | 功能 | 等级 |
|------|------|------|
| `/seo maps <url>` | 完整地图存在性审计（自动选择等级） | 0+ |
| `/seo maps grid <关键词> <位置>` | 地理网格排名扫描（7x7，默认1个关键词） | 1+ |
| `/seo maps reviews <企业> <位置>` | 跨平台评论智能分析 | 1+ |
| `/seo maps competitors <关键词> <位置>` | 竞争对手半径映射 | 0+ |
| `/seo maps nap <企业名称>` | 跨平台NAP验证 | 0+ |
| `/seo maps schema <企业名称>` | 从数据生成LocalBusiness JSON-LD | 0+ |
| `/seo maps gbp <企业> <位置>` | GBP完整性审计 | 1+ |

---

## 三级能力检测

在进行分析之前，检测可用的能力等级：

### 等级 0 (免费)
**检测：** DataForSEO MCP工具不可用。
**功能：** Overpass API竞争对手发现、Geoapify POI搜索、Nominatim地理编码、静态GBP清单、模式生成、跨平台NAP指导。
**加载：** `../seo/references/maps-free-apis.md`

### 等级 1 (DataForSEO)
**检测：** `business_data_business_listings_search` MCP工具可用。
**功能：** 等级0的所有功能 PLUS 地理网格排名跟踪、实时GBP资料审计、评论智能分析（速度、情感、分布）、GBP发布活动、问答数据、Tripadvisor/Trustpilot评论。
**加载：** `../seo/references/maps-api-endpoints.md`

### 等级 2 (DataForSEO + Google Maps平台)
**检测：** 等级1可用且环境中有Google Maps API密钥。
**功能：** 等级1的所有功能 PLUS Google Places详细信息、实时企业状态、AI驱动的地点摘要、照片分析。
**注意：** Google ToS限制存储仅限于`place_id`。经纬度最多缓存30天。

**始终在分析开始时向用户传达检测到的等级。**

---

## 地理网格排名跟踪 (等级 1+)

模拟从多个GPS坐标进行的谷歌地图搜索，以显示地理区域内的排名变化。需要DataForSEO。

**加载：** `../seo/references/maps-geo-grid.md` 用于算法、SoLV公式、热图格式。
**加载：** `../seo/references/maps-api-endpoints.md` 用于地图SERP端点详细信息。

### 工作流程

1. 将企业地址地理编码以获取中心经纬度
2. 使用Haversine偏移公式生成网格点（默认：7x7，5公里半径）
3. **在继续之前显示成本估算并请求确认**
4. 使用每个网格点的`location_coordinate`发出DataForSEO地图SERP API调用
5. 在每个点找到目标企业排名
6. 计算SoLV：`(top_3_count / total_points) * 100`
7. 渲染ASCII热图输出

### 成本警告 (必需)

在每次地理网格扫描之前，显示：
```
地理网格扫描：[关键词] 在 [位置]
网格：7x7 (49个点) | 关键词：[N] | 预计成本：$[金额]
DataForSEO积分将被消耗。继续？
```

---

## GBP资料审计 (等级 1优先，等级 0手动)

审计影响谷歌企业资料质量和排名的25个字段。

**加载：** `../seo/references/maps-gbp-checklist.md` 用于完整清单和评分。

> **AI & 2026背景 (第三方报告)：** **Ask Maps**，由AP新闻报告为2026年3月12日推出的Gemini对话式地图功能（iOS/Android，美国+印度）。**AI模式**（1B+ MAU，据2026年谷歌I/O主题演讲报道；未在谷歌自有来源上确认）
> 越来越多地出现在第三方术语中的1-2个本地企业AI界面，以及为本地服务（家庭维修、美容、宠物护理）推出的**代理式预订/致电**，将于2026年夏季向所有美国用户推出（谷歌可以代表用户致电企业）。
> 2026年GBP API新增：评论媒体URL、定期本地发布计划、评论回复状态/审核、邀请Place ID。来源：
> blog.google/products-and-platforms/products/search/search-io-2026/ ·
> developers.google.com/my-business/content/latest-updates

### 等级 1 工作流程

1. 通过DataForSEO My Business Info API获取企业资料（关键词或CID）
2. 将API响应字段映射到25字段清单
3. 对每个字段进行评分：存在+优化=2分，存在=1分，缺失=0分
4. 应用特定行业的权重乘数
5. 归一化到0-100分

### 等级 0 工作流程

1. 通过WebFetch获取企业网站
2. 提取任何可见的GBP信号（地图嵌入、地点引用、评论小部件）
3. 基于可检测信号应用静态清单
4. 将无法检测的字段标记为“未知（需要DataForSEO获取实时数据）”

---

## 评论智能分析 (等级 1+)

跨平台评论分析：速度、情感、评分分布、假评论检测。

**参考：** `../seo/references/local-seo-signals.md` 用于基准（与seo-local共享）。

### 工作流程

1. 通过DataForSEO评论API获取谷歌评论（按最新排序）
2. 计算评论速度：过去6个月的月评论数
3. 检查18天规则（Sterling Sky）：任何3周缺口=排名风险
4. 分析评分分布：健康=向5星倾斜的钟形曲线
5. 计算所有者回复率：回复数/总评论数
6. 获取Tripadvisor和Trustpilot评论（如果可用）
7. 跨平台比较表

### 假评论检测信号

标记符合2个以上这些模式的评论：
- 统一时间（同一天/小时的多条评论）
- 带有有限历史记录或单条评论的评论者账号
- 地理位置不一致（评论者位置与业务位置）
- 仅5星速度激增（与历史基线相比）
- 评论中相同或几乎相同的文本
- 没有相应营销活动的突然数量激增

---

## 竞争对手半径映射 (等级 0+)

识别和分析定义半径内的竞争对手。

### 等级 0 (Overpass API)

**加载：** `../seo/references/maps-free-apis.md` 用于查询模板。

1. 将企业地址地理编码
2. 查询Overpass API以获取具有相同OSM标签且在半径内的企业
3. 解析结果：名称、地址、电话、网站、中心距离
4. 按距离排序，以竞争对手景观表呈现

### 等级 1 (DataForSEO)

1. 使用带有业务关键词+位置的地图SERP API
2. 提取具有完整资料的前20名竞争对手
3. 比较：评分、评论数、类别、照片、属性
4. 计算竞争密度分数：每平方公里竞争对手数

---

## 跨平台NAP验证 (等级 0+)

检查企业在谷歌、必应地点、苹果和OSM上的资料一致性。

### 工作流程

1. 在每个平台上搜索企业名称：
   - 谷歌：从GBP数据或地图SERP结果推断
   - 必应：`WebFetch https://www.bing.com/maps?q=BUSINESS+NAME+LOCATION`
   - 苹果：手动检查（没有公共API -- 验证/申领苹果企业资料；将苹果企业启动/重命名声明视为TechRadar来源，直到苹果主要确认）
   - OSM：Overpass或Nominatim搜索
2. 从每个来源提取NAP（名称、地址、电话）
3. 比较一致性：完全匹配、部分匹配、缺失或冲突
4. 将差异标记为关键（名称不匹配）、高（地址不匹配）、中（电话不匹配）
5. 建议申领未申领的资料

---

## 模式生成 (等级 0+)

从收集的数据生成LocalBusiness JSON-LD标记。

**参考：** `../seo/references/local-schema-types.md` 用于行业子类型（与seo-local共享）。

### 工作流程

1. 确定最具体的行业子模式
2. 填充必需属性：`@type`、`name`、`address`、`image`
3. 添加推荐属性：`telephone`、`url`、`geo`、`openingHoursSpecification`、`priceRange`
4. 为多地点添加策略属性：`branchOf`、`areaServed`、`sameAs`
5. 如果有评论数据，添加`aggregateRating`
6. 输出有效的JSON-LD块以供实施

**不要生成自利的评论标记** -- 谷歌会忽略企业自身的LocalBusiness评论标记。仅标记页面上的第三方评论。

---

## 参考文件

按需加载（不要在启动时加载所有文件）：
- `../seo/references/maps-api-endpoints.md`：DataForSEO端点详细信息、参数、成本
- `../seo/references/maps-free-apis.md`：Overpass、Geoapify、Nominatim查询模板
- `../seo/references/maps-geo-grid.md`：网格算法、SoLV公式、热图渲染
- `../seo/references/maps-gbp-checklist.md`：25字段GBP审计与行业权重
- `../seo/references/local-seo-signals.md`：排名因素、评论基准（共享）
- `../seo/references/local-schema-types.md`：按行业分类的LocalBusiness子类型（共享）

---

## 输出

生成`MAPS-ANALYSIS-{domain}.md`，包含：

1. **地图健康评分：XX/100** 与维度分解表
2. **检测到的能力等级**（等级0或等级1）以及可用功能的解释
3. **地理网格热图**（等级1）：ASCII网格，显示SoLV百分比和平均排名
4. **GBP资料审计**：按字段评分，带行业特定权重
5. **评论智能分析**：速度图表、评分分布、回复率、跨平台比较
6. **竞争对手景观**：半径内数量、前5名按评分/评论、竞争密度
7. **跨平台存在性**：谷歌/必应/苹果/OSM资料状态
8. **模式建议**：生成的LocalBusiness JSON-LD（如果缺失或不完整）
9. **前10个优先行动**（关键 > 高 > 中 > 低）
10. **成本报告**：分析期间消耗的DataForSEO积分（等级1仅限）
11. **限制免责声明**：当前等级无法评估的内容

---

## 跨技能委托

- 网站页面本地信号：建议`/seo local <url>`
- 完整AI搜索可见性：建议`/seo geo <url>`
- 模式验证和修复：建议`/seo schema <url>`
- 实时SERP和关键词数据：建议`/seo dataforseo [命令]`

---

## 错误处理

| 情景 | 动作 |
|------|------|
| DataForSEO MCP不可用 | 降至等级0。通知用户：“未检测到DataForSEO。正在执行免费级分析。要进行地理网格跟踪和评论智能分析，请安装DataForSEO扩展。” |
| 企业在地图SERP中未找到 | 尝试使用关键词的My Business Info。如果仍然找不到，报告“在此位置未在谷歌地图中找到企业。” |
| 地理编码失败（Nominatim） | 询问用户提供坐标或更具体的地址。 |
| API速率限制被触发 | 报告限制。建议等待或使用标准（排队）方法而不是实时方法。 |
| 未找到评论 | 报告零评论状态。建议评论生成策略，目标为18天间隔。 |
| 检测到多地点 | 询问用户要分析哪个位置，或提供批量模式，并估计每个位置的成本。 |
