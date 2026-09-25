# 本地SEO分析 (2026年3月)

## 关键统计数据

| 指标 | 数值 | 来源 |
|------|------|------|
| GBP信号在本地包权重中的占比 | 32% | Whitespark 2026 |
| 位置邻近性在排名差异中的占比 | 55.2% | Search Atlas机器学习研究 |
| 评论信号占比 (较16%有所提升) | ~20% | Whitespark 2026 |
| 搜索引擎寻求本地信息的比例 | 46% | 行业数据 |
| 移动端"附近"搜索在24小时内导致访问的比例 | 76% | Google确认 |
| 使用ChatGPT/AI进行本地推荐的占比 | 45% (较6%有所提升) | BrightLocal LCRS 2026 |
| ChatGPT本地转化率 | 15.9% | Seer Interactive |
| Google有机本地转化率 | 1.76% | Seer Interactive |
| 本地包广告增长 (2025年1月至2026年1月) | 从1%增长至22% | Sterling Sky |

---

## 商业类型检测

在分析前从页面信号进行检测。这决定了哪些检查适用。

### 实体店
- 页面内容或页脚中可见的物理街道地址
- 带有标记/路线的Google地图嵌入
- "访问我们", "位于", "来看看我们"
- LocalBusiness模式中的结构化地址

### 服务区域企业 (SAB)
- 无可见的物理地址
- 服务区域提及："服务[城市/区域]", "服务区域包括"
- "我们上门", "现场服务", "移动[服务]"
- schema中的`areaServed`属性不含`address.streetAddress`

### 混合型
- 同时存在物理地址和服务区域语言
- "访问我们的展厅"与"我们也服务[区域]"相结合

**对检查的影响**: SAB会跳过嵌入地图验证和物理地址一致性检查。实体店会获得完整的NAP + 地图检查。

---

## 行业垂直检测

从页面信号和GBP类别模式进行检测。路由到行业特定检查，参考`../seo/references/local-schema-types.md`。

| 垂直领域 | 检测信号 |
|----------|----------|
| **餐厅** | /menu, 菜单项, 预订, 菜系类型, 食物订购, "堂食", "外卖" |
| **医疗保健** | 接受的保险, 患者, 预约, NPI, 医学术语, "医生", HIPAA通知 |
| **法律** | 律师, 法律师, 实践领域, 律师协会认证, 案例结果, "免费咨询" |
| **家庭服务** | 服务区域, 紧急服务, "免费估价", 获得许可/保险/担保, "24/7" |
| **房地产** | 列表, MLS, 出售/出租的房产, 代理简介, 经纪公司, "开放日" |
| **汽车** | 库存, VIN, 试驾, 经销商, 服务部门, "新/二手/认证" |

如果未检测到垂直领域，则使用通用`LocalBusiness`分析路径。

---

## 分析维度

### 1. GBP信号 (25%)

主要类别是最重要的本地包因素 (Whitespark #1, 分数: 193)。主要类别不正确是最大的负面因素 (分数: 176)。

**检查内容:**
- 页面上可检测到的GBP嵌入或引用 (地图iframe, 地点ID, 评论小部件)
- 主要类别的适当性 (从页面内容与可见GBP数据推断)
- 次要类别的证据 (理想情况: 每个BrightLocal额外4个)
- GBP帖子存在 (根据WebFX, 没有直接排名影响, 但会触发帖子理由)
- 照片/视频证据 (Agency Jet, 照片可使方向请求增加45%)
- Q&A内容: Google于2025年11月3日停止了其Q&A API，公共Q&A据报道正在逐步淘汰; 在网站和业务描述中回答常见问题，并将任何剩余的公共Q&A视为加分项
- Google验证徽章资格 (2025年10月用Guaranteed/Screened替换)
- GBP链接URL策略: 不要链接到最强的网站页面 (Sterling Sky多样性更新 - 风险抑制有机排名)
- 页面上可见的营业时间 (在搜索时间营业的企业排名更高，因素#5)

**评分指南:**
- 完整: GBP嵌入存在，类别信号一致，帖子活跃，照片存在
- 部分完整: 部分GBP信号存在但未完整
- 低: 网站上没有可见的GBP集成

### 2. 评论与声誉 (20%)

评论速度比总数更重要。Sterling Sky的"18天规则": 如果3周内没有新评论，排名会急剧下降。

**检查内容:**
- 页面或schema中可见的Google评论总数 (魔法阈值: 10, Sterling Sky)
- 星级评分 (31%的消费者只使用4.5+星, 68%只使用4+星, BrightLocal 2026)
- 评论新鲜度指标 (74%只关心过去3个月的评论)
- schema中的`aggregateRating` (ratingValue, reviewCount, bestRating)
- 第三方评论存在 (消费者使用6个评论网站的加权平均数, BrightLocal 2026)
- 所有者响应模式 (88%会使用响应的企业, BrightLocal)
- 评论门控检测: 任何在引导至评论平台前筛选满意度的行为都违反了Google政策 (虚假参与政策) 和FTC (每项违规53,088美元)

**行业特定:**
- 医疗保健: HIPAA禁止在回复中确认/否认评论者是患者
- 法律: 回复中考虑律师-客户特权

**评分指南:**
- 完整: 10+评论, 4.5+星, 近期活动, 所有者响应, 多平台存在
- 部分完整: 有评论但存在新鲜度、评分或响应率差距
- 低: <10评论, 无近期活动, 无响应, 单一平台

### 3. 本地页面SEO (20%)

专用服务页面是#1本地有机因素和#2AI可见性因素 (Whitespark 2026)。

**检查内容:**
- 标题标签包含城市/服务关键词
- 带有本地意图的H1标签 (城市+服务)
- 页面HTML中可见的NAP (名称、地址、电话) (页脚、联系部分、页眉)
- 专用服务页面 (每个核心服务一个页面)
- 多地点网站的地点页面质量:
  - **>60-70%独特内容**最低标准 (行业共识, 无Google确认阈值)
  - **交换测试**: 如果可以交换城市名称而内容仍然合理，则为门户型页面 (RicketyRoo方法)。一家暖通空调公司在2024年3月核心更新后因此模式失去80%排名和63%流量
  - 本地照片、区域特定推荐信、本地常见问题解答
- 嵌入Google地图 (地理信号强化，非直接排名因素 - 懒加载以减轻速度影响)
- 可折叠的点击呼叫按钮 (`tel:`链接) 和联系表单
- 内部链接架构: 轮辐式, 每个关键页面在主页3次点击范围内
- 每1,000字2-5个上下文相关内部链接，带有描述性锚文本

**多地点特定:**
- 带有可爬取URL的门店定位器 (SSR/SSG优于CSR)
- 子目录结构: `domain.com/locations/city-name/` (子目录比主目录更好地整合链接权益, Bruce Clay: 50%+流量提升)
- 每个地点页面都有独特的LocalBusiness schema，通过`@id`链接到主页上的组织

**评分指南:**
- 完整: 城市在标题+H1, NAP可见，专用服务页面，无门户型风险，良好的内部链接
- 部分完整: 部分本地信号但缺少服务页面或门户型风险
- 低: 通用标题/H1, NAP不可见，地点页面内容单薄

### 4. NAP一致性及引用 (15%)

引用对传统包排名的影响正在下降，但3个最高AI可见性因素与引用相关 (Whitespark 2026)。Google 2025年7月文档更新中删除了"目录"在突出显示定义中的提及。

**检查内容:**
- NAP提取: 比较名称、地址、电话:
  1. 可见页面HTML (页脚、联系页面)
  2. LocalBusiness JSON-LD schema
  3. 任何可见的GBP数据
  - 标记这三个来源之间的任何差异
- 在一级目录上检测引用 (通过WebFetch或站点搜索模式检查):
  - 页面上的Google Business Profile信号
  - Yelp: `site:yelp.com "Business Name"`
  - BBB: `site:bbb.org "Business Name"`
  - Facebook业务页面引用
- **Apple Maps / Apple业务列表**意识: 声明并维护Apple列表; 将Apple Business统一平台启动/重命名声明视为TechRadar来源，并在断言前与Apple主要来源核实。
- Bing Places意识 (为ChatGPT、Copilot、Alexa提供支持 -- 建议声明并优化)
- 行业特定目录推荐: 加载`../seo/references/local-schema-types.md`获取每个垂直领域的引用来源
- 数据聚合器意识: Data Axle、Foursquare、Neustar/TransUnion (建议提交以供下游分发)
- 区域搜索单元: 自2026年9月18日起，在EEA，Google的聚合器和供应商单元也覆盖本地业务查询; 土耳其有单独的places-site功能 (见`seo-hreflang`部分5c); 注意这些市场

**评分指南:**
- 完整: 页面/Schema之间NAP一致，检测到一级目录引用，行业目录存在
- 部分完整: NAP存在但存在不一致，一些引用缺失
- 低: NAP差异，无可检测到的引用，无Schema地址

### 5. 本地Schema标记 (10%)

Schema不是直接排名因素 (John Mueller确认)。但可启用丰富结果 (CTR增加43%，Webstix案例研究) 并帮助AI系统解析业务信息。

**检查内容:**
- LocalBusiness schema存在 (提取JSON-LD块)
- 必要属性: `name`, `address` (邮政地址子属性)
- 推荐属性: `geo` (至少5位小数精度，已确认), `openingHoursSpecification`, `telephone`, `url`, `priceRange` (<100字符), `image`, `aggregateRating`
- **正确行业子类型** -- 加载`../seo/references/local-schema-types.md`:
  - 餐厅使用`Restaurant`而非通用`LocalBusiness`
  - 法律使用`LegalService`而非已弃用的`Attorney`
  - 汽车经销商使用`AutoDealer`而非已弃用的`VehicleListing`
  - 医疗保健使用`MedicalClinic`/`Hospital`/`Dentist`而非通用`MedicalBusiness`
- SAB特定: `areaServed`包含命名城市 (推荐，非Google官方列表但Schema.org支持)
- 多地点: 每个地点页面有独立的LocalBusiness，带有唯一`@id`，通过`branchOf`链接到主页上的组织
- 行业特定Schema模式 (参考`../seo/references/local-schema-types.md`):
  - 餐厅: Menu + MenuSection + MenuItem + ReserveAction (注意: 预订/订购操作不是Google支持的丰富结果; 价值在于机器可读的业务数据)
  - 医疗保健: Physician (Person) + MedicalSpecialty + 同步到NPI
  - 法律: LegalService + Person + Service (实践领域)
  - 家庭服务: 子类型 + areaServed + Service
  - 房地产: RealEstateAgent + Person + RealEstateListing

**评分指南:**
- 完整: 正确子类型，所有推荐属性，行业特定模式，有效的JSON-LD
- 部分完整: LocalBusiness存在但为通用类型或缺少推荐属性
- 低: 无本地Schema，或带有错误/占位符内容的Schema

### 6. 本地链接及权威信号 (10%)

链接对本地包的影响正在下降，但仍然是本地有机排名的~26% (Whitespark 2026, #2因素组)。 "最佳"列表位置是**#1 AI可见性引用因素**。

**检查内容:**
- 可从页面检测到的本地反向链接指标:
  - 商会提及或链接 (高信任流，~80%更多消费者访问，GlueUp)
  - BBB认证/徽章 (Google用于业务验证)
  - 本地新闻/媒体报道
  - 社区参与信号 (赞助、本地活动、合作)
- "最佳"列表存在 (Whitespark 2026中AI可见性因素)
- 数字公关信号: 66.2%的公关从业者现在将AI引用作为KPI (BuzzStream 2026)
- 品牌提及与传统反向链接相比**3倍更强烈**地与AI可见性相关 (Ahrefs: 0.664 vs 0.218相关性)
- 链接速度基准: 小型企业每月5-10个高质量本地链接 (共识)

**评分指南:**
- 完整: 可见本地权威信号 (商会、BBB、媒体)，社区参与明显
- 部分完整: 一些权威信号但有限的本地链接指标
- 低: 无可检测到的本地权威信号

---

## AI搜索对本地的影响

**不要重复seo-geo分析。** 提供本地特定AI上下文并建议`/seo geo <url>`进行完整分析。

本地AI关键事实:
- AI概述出现在高达68%的本地搜索中 (Whitespark 2025年第二季度)
- ChatGPT转化率为15.9%，Google有机为1.76% (Seer Interactive)
- 3个最高AI可见性因素与引用相关 (Whitespark 2026)
- ChatGPT不直接访问GBP -- 从Bing索引、Yelp、TripAdvisor、BBB、Reddit获取
- Bing Places至关重要: 为ChatGPT、Copilot、Alexa提供支持
- 第三方观察到的本地AI界面变化 (美国移动端) 可能只显示1-2家企业，显示数量减少32% (Sterling Sky)

**建议**: 运行`/seo geo <url>`进行全面的AI搜索可见性分析，包括可引用评分、llms.txt检查和品牌提及审计。

---

## 参考文件

按需加载:
- `../seo/references/local-seo-signals.md`: 排名因素，评论基准，引用层级，GBP功能状态，算法更新
- `../seo/references/local-schema-types.md`: 按行业分类的LocalBusiness子类型，Schema模式，每个垂直领域的引用来源

---

## 输出

生成`LOCAL-SEO-ANALYSIS-{domain}.md`，包含:

1. **本地SEO评分: XX/100** 与维度分解表
2. **商业类型**: 实体店 / SAB / 混合型
3. **检测到的行业垂直领域** + 行业特定发现
4. **GBP优化清单** (检测到的信号与缺失项)
5. **评论健康状况快照** (评分、数量、速度指标、响应模式)
6. **NAP一致性审计** (页面与Schema差异，跨源比较)
7. **引用存在检查** (一级目录状态)
8. **本地Schema状态** (存在/缺失/错误 + 可用修复方案)
9. **地点页面质量** (如果多地点: 独特内容%，门户型风险，门店定位器)
10. **10个优先行动项** (关键 > 高 > 中 > 低)
11. **限制免责声明**: 本分析无法评估的内容 (geo网格排名，域名权威性，全面反向链接，GBP Insights数据，实时本地包位置) 以及哪些付费工具可以填补这些空白

---

## 快速见效

1. 声明并优化Apple Maps / Apple业务列表; 首先核实任何Apple Business启动/重命名声明与Apple主要来源
2. 声明并优化Bing Places (为ChatGPT、Copilot、Alexa提供支持)
3. 修复页面、Schema和GBP之间的任何NAP差异
4. 添加带有正确行业子类型的LocalBusiness schema
5. 添加`geo`坐标，至少5位小数精度
6. 确保电话号码使用`tel:`链接进行点击呼叫
7. 在标题标签和H1中添加城市+服务关键词

## 中等努力

1. 为每个核心服务创建专用页面 (Whitespark: #1本地有机因素)
2. 建立评论生成策略，保持18天最低频率
3. 提交给三个数据聚合器 (Data Axle、Foursquare、Neustar/TransUnion) 以供下游分发
4. 声明行业特定目录列表 (按垂直领域推荐)
5. 添加行业特定Schema模式 (餐厅的Menu，医疗保健的Physician等)
6. 实施服务/地点页面的轮辐式内部链接

## 高影响

1. 建立本地数字公关策略，针对"最佳"列表 (#1 AI可见性因素)
2. 开发每个地点页面的独特、不可交换内容 (>60%独特)
3. 在ChatGPT从来源获取的平台 (Yelp、TripAdvisor、BBB、Reddit) 上建立存在
4. 追求商会和BBB会员资格 (权威性+验证信号)
5. 创建社区参与内容 (赞助、本地活动、合作)

---

## DataForSEO集成 (可选)

如果DataForSEO MCP工具可用，使用`business_data_business_listings_search`进行实时GBP/业务列表数据提取和跨目录引用审计，使用`serp_organic_live_advanced`进行实时本地包位置。

---

## 错误处理

| 情景 | 操作 |
|------|------|
| URL无法访问 (DNS失败，连接拒绝) | 清晰报告错误。不要猜测网站内容。建议用户验证URL并重试。 |
| 页面上未检测到本地信号 | 报告未在页面上发现本地业务指标。建议用户确认这是本地业务并提供GBP列表URL（如果可用）。 |
| 页面HTML中未找到NAP | 检查schema和元标签。如果仍然缺失，标记为关键问题。建议添加可见NAP到页脚和联系页面。 |
| 行业垂直不明确 | 显示前两个检测到的垂直领域及其支持信号。要求用户确认后再应用行业特定建议。 |
| 多地点50+地点页面 | 应用seo orchestrator的质量门控: 30+页面时发出警告 (强制执行60%+独特)，50+页面时停止 (要求用户在继续前提供理由)。 |
