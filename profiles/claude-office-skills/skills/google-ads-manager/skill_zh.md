# Google Ads 管理器

全面的 Google Ads 营销活动管理，包括活动设置、关键词研究、广告文案生成、出价优化和绩效报告。

## 概述

本技能涵盖：
- 活动结构和设置
- 关键词研究和分组
- 广告文案创建（RSA 格式）
- 出价策略选择
- 绩效分析和优化

---

## 活动结构

### 账户层级结构

```
账户
├── 活动 1：品牌
│   ├── 广告组：品牌关键词
│   │   ├── 关键词：[品牌名称]，[品牌+产品]
│   │   └── 广告：3-5 个 RSAs
│   └── 广告组：品牌+竞争对手
│       ├── 关键词：[品牌 vs 竞争对手]
│       └── 广告：3-5 个 RSAs
│
├── 活动 2：非品牌 - 搜索
│   ├── 广告组：产品类别 A
│   │   ├── 关键词：[类别关键词]
│   │   └── 广告：3-5 个 RSAs
│   ├── 广告组：产品类别 B
│   └── 广告组：问题/解决方案
│
├── 活动 3：竞争对手
│   ├── 广告组：竞争对手 A
│   └── 广告组：竞争对手 B
│
└── 活动 4：绩效最大
    └── 资产组：[图片、视频、标题、描述]
```

### 活动设置模板

```yaml
活动:
  名称："[产品] - 搜索 - 非品牌"
  类型：SEARCH
  预算： 
    金额：100  # 每日
    配送：STANDARD
  
  出价：
    策略：TARGET_CPA  # 或 MAXIMIZE_CONVERSIONS
    目标 CPA：50
    
  定位：
    地点：[US, CA, UK]
    语言：[en]
    目标受众： 
      - 市场内："Business Software"
      - 自定义意图："project management tools"
    
  网络：
    搜索：true
    展示：false
    合作伙伴：false
    
  时间表：
    天：[MON, TUE, WED, THU, FRI]
    小时："8:00-20:00"
    时区："America/New_York"
    
  广告轮换：OPTIMIZE
  
  负面关键词：
    活动级别：
      - free
      - cheap
      - download
      - jobs
      - salary
```

---

## 关键词研究

### 关键词类别

```yaml
关键词类型:
  品牌:
    示例：["[品牌名称]", "[品牌] login", "[品牌] pricing"]
    意图：导航
    预期 CPC：低
    优先级：高
    
  竞争对手:
    示例：["[竞争对手] alternative", "[竞争对手] vs"]
    意图：商业
    预期 CPC：中高
    优先级：中
    
  产品:
    示例：["project management software", "task tracking tool"]
    意图：商业
    预期 CPC：高
    优先级：高
    
  问题:
    示例：["how to manage remote team", "track project deadlines"]
    意图：信息/商业
    预期 CPC：中
    优先级：中
    
  长尾:
    示例：["best project management tool for small teams"]
    意图：商业
    预期 CPC：中
    优先级：高 (高意图)
```

### 关键词研究流程

```yaml
研究步骤:
  1. 种子关键词：
      来源：
        - 头脑风暴：核心产品术语
        - 竞争对手：分析竞争对手广告
        - 客户：调查/访谈术语
        - 支持：常见问题
        
  2. 使用工具扩展：
      Google 关键词规划师：
        - 获取想法：从种子关键词
        - 过滤：按搜索量、竞争程度、CPC
        
      其他工具：
        - semrush：竞争对手关键词
        - ahrefs：目标有机关键词
        - answerthepublic：问题关键词
        
  3. 关键词分组：
      方法：SKAG 或主题分组
      最大每组：15-20
      标准：相同意图、相似着陆页
      
  4. 匹配类型：
      广泛匹配：发现、高搜索量
      短语匹配：平衡覆盖/相关性
      精确匹配：高意图、控制
      
  5. 负面关键词：
      识别：不相关的搜索术语
      级别：活动、广告组、账户
```

### 关键词分组示例

```yaml
广告组："Project Management Software"
主题：产品类别

关键词:
  精确匹配:
    - [project management software]
    - [project management tool]
    - [pm software]
    
  短语匹配:
    - "project management software"
    - "best project management"
    - "project tracking software"
    
  广泛匹配:
    - project management platform
    - team project software

负面关键词:
  - free
  - open source
  - template
  - excel
  - certification
```

---

## 广告文案框架

### 响应式搜索广告 (RSA) 结构

```yaml
rsa_requirements:
  标题:
    数量：15 (最小 3)
    最大字符数：30
    固定策略：
      位置 1：关键词/利益标题
      位置 2：价值主张/差异化
      位置 3：CTA
      
  描述:
    数量：4 (最小 2)
    最大字符数：90
    
  显示路径:
    部分：2
    每部分最大字符数：15
```

### 按类别划分的标题模板

```yaml
标题模板:
  关键词标题： # 固定在位置 1
    - "{Keyword} Software"
    - "Best {Keyword} Tool"
    - "#1 {Keyword} Platform"
    - "{Keyword} for Teams"
    
  利益标题:
    - "Save 10+ Hours/Week"
    - "Boost Productivity 40%"
    - "Manage Projects Easily"
    - "Never Miss Deadlines"
    
  信任标题:
    - "Trusted by 50,000+ Teams"
    - "4.8★ on G2 & Capterra"
    - "Award-Winning Software"
    - "Enterprise-Grade Security"
    
  CTA 标题： # 固定在位置 3
    - "Start Free Trial"
    - "Try Free for 14 Days"
    - "Get Started Today"
    - "Request a Demo"
    
  紧迫性标题:
    - "Limited Time: 30% Off"
    - "Special Offer Ends Soon"
    - "Save Now - Act Fast"
    
  差异化标题:
    - "No Credit Card Needed"
    - "Set Up in 2 Minutes"
    - "Cancel Anytime"
    - "All-in-One Solution"
```

### 描述模板

```yaml
描述模板:
  利益导向:
    - "Streamline your workflow with our all-in-one project management platform. Trusted by 50,000+ teams worldwide."
    - "Save 10+ hours per week with automated task tracking, team collaboration, and real-time reporting. Try free!"
    
  功能导向:
    - "Kanban boards, Gantt charts, time tracking, and team chat in one powerful platform. Start your free trial today."
    
  社会证明:
    - "Join 50,000+ teams who've transformed their productivity. Rated 4.8/5 on G2. No credit card required."
    
  紧迫性:
    - "Limited time: Get 30% off annual plans. All features included. Start your 14-day free trial now!"
```

---

## 出价策略

### 策略选择指南

```yaml
出价策略:
  maximize_conversions:
    使用条件：
      - 新活动：true
      - 目标：数量
      - 预算：灵活
    优点：设置简单，谷歌优化
    缺点：无成本控制
    
  target_cpa:
    使用条件：
      - 转化历史：每月 30+ 转化
      - 目标：效率
      - 已知 CPA 目标：true
    优点：成本控制，可预测
    缺点：可能限制数量
    
  target_roas:
    使用条件：
      - 电商：true
      - 转化价值跟踪：已启用
      - 目标：ROI 优化
    优点：以收入为中心
    缺点：需要价值数据
    
  maximize_clicks:
    使用条件：
      - 目标：流量
      - 新活动：认知
    优点：简单，适合测试
    缺点：无转化关注
    
  manual_cpc:
    使用条件：
      - 需要：完全控制
      - 小预算：true
      - 测试：关键词
    优点：粒度控制
    缺点：耗时

出价调整:
  设备：
    手机：-20% 到 +30%
    平板：-10% 到 +10%
  
  地点：
    高价值城市：+20%
    低价值地区：-30%
    
  时间表：
    工作时间：+15%
    非工作时间：-25%
    
  目标受众：
    再营销：+50%
    市场内：+20%
```

---

## 绩效报告

### 关键指标仪表板

```markdown
# Google Ads 绩效报告 - {日期范围}

## 活动摘要
| 活动 | 支出 | 点击 | 转化 | CPA | ROAS |
|-------|------|------|------|-----|------|
| 品牌 | $500 | 1,200 | 80 | $6.25 | 15x |
| 非品牌 | $3,000 | 2,500 | 45 | $66.67 | 3.2x |
| 竞争对手 | $800 | 600 | 12 | $66.67 | 2.8x |
| **总计** | **$4,300** | **4,300** | **137** | **$31.39** | **5.1x** |

## 关键指标
- **CTR**: 3.2% (基准：2%)  ✅
- **转化率**: 3.2% (基准：3%)  ✅
- **平均 CPC**: $1.00
- **质量分数平均**: 7.2/10

## 表现最佳的关键词
| 关键词 | 点击 | 转化 | CPA | QS |
|--------|------|------|-----|-----|
| [品牌名称] | 800 | 60 | $5 | 9 |
| project management software | 300 | 15 | $40 | 7 |
| best pm tool for teams | 150 | 12 | $35 | 8 |

## 表现不佳（需要行动）
| 关键词 | 支出 | 转化 | CPA | 行动 |
|--------|------|------|-----|------|
| free project tool | $200 | 0 | - | 暂停 |
| pm software download | $150 | 1 | $150 | 暂停 |

## 建议
1. ⬆️ 增加品牌活动的预算 (CPA $6.25)
2. ⏸️ 暂停 5 个转化为 0 的关键词
3. 📝 测试新的广告文案（当前 CTR 低于基准）
4. 🎯 在负面关键词中添加 "free"
```

### 优化检查清单

```yaml
每周任务:
  - 审查搜索术语：
      行动：添加负面关键词，寻找新关键词
      
  - 检查质量分数：
      行动：改进 <6 QS 关键词
      
  - 审查广告表现：
      行动：暂停低 CTR 广告
      
  - 调整出价：
      行动：为高表现者增加
      
每月任务:
  - 竞争对手分析：
      检查：新竞争对手，信息
    
  - 着陆页审查：
      检查：按页面的转化率
    
  - 目标受众审查：
      检查：添加新受众，移除表现不佳者
    
  - 预算重新分配：
      检查：将预算移至表现最佳者
```

---

## 输出示例

**请求**："创建一个 CRM 软件的 Google Ads 活动结构"

**输出**：

```markdown
# Google Ads 活动结构 - CRM 软件

## 活动 1：品牌

**预算**：$50/天
**出价**：Maximize Conversions

### 广告组：品牌关键词
**关键词**：
- [acme crm]
- [acme crm login]
- [acme crm pricing]

**标题**：
1. Acme CRM - 官方网站
2. 受 10,000+ 团队信赖
3. 免费试用
...

---

## 活动 2：非品牌搜索

**预算**：$200/天
**出价**：Target CPA ($75)

### 广告组：CRM 软件
**关键词**：
- [crm software]
- [best crm software]
- "crm for small business"

**标题**：
1. 2026 最佳 CRM 软件
2. 关闭 40% 更多交易
3. 免费试用 14 天
...

### 广告组：销售软件
**关键词**：
- [sales management software]
- [sales tracking tool]
...

### 广告组：问题/解决方案
**关键词**：
- "如何跟踪销售线索"
- "管理客户关系"
...

---

## 活动 3：竞争对手

**预算**：$100/天
**出价**：Target CPA ($90)

### 广告组：Salesforce 替代品
**关键词**：
- [salesforce alternative]
- [salesforce vs]
- "cheaper than salesforce"

**标题**：
1. Salesforce 替代品
2. 成本降低 50%
3. 1 天内切换
...

---

## 负面关键词（账户级别）
- free
- jobs
- salary
- certification
- tutorial
- open source

---

## 预计绩效
| 活动 | 预计点击 | 预计转化 | 预计 CPA |
|------|----------|----------|----------|
| 品牌 | 1,500 | 150 | $8 |
| 非品牌 | 2,000 | 25 | $80 |
| 竞争对手 | 800 | 10 | $100 |
```

---

*Google Ads 管理器技能 - Claude 办公技能的一部分*
