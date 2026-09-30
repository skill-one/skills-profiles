---
name: Amazon Seller
description: 自动化亚马逊卖家运营，包括库存、订单、定价和广告管理
---

# 亚马逊卖家

全面的技能，用于自动化亚马逊卖家运营和FBA管理。

## 核心工作流程

### 1. 卖家中心流水线

```
亚马逊卖家运营:
┌─────────────────────────────────────────────────────────┐
│                    商品上架管理                    │
│  创建 → 优化 → 定价 → 库存 → 监控                │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    订单履行                    │
│  FBA：亚马逊处理 │ FBM：卖家处理              │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    广告 (PPC)                    │
│  推广商品 │ 品牌推广 │ 展示                  │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    分析与增长                    │
│  销售报告 │ 利润分析 │ 市场调研              │
└─────────────────────────────────────────────────────────┘
```

### 2. 自动化触发器

```yaml
automations:
  - name: 库存不足警报
    trigger:
      metric: fba_inventory
      condition: "< 14天的供应量"
    actions:
      - send_alert: slack
      - 创建发货计划
      - 向供应商重新订购
      
  - name: 价格调整
    trigger:
      event: 竞争对手价格变动
      threshold: 5%
    actions:
      - recalculate_price
      - 更新商品信息
      - 记录变更
      
  - name: 评价请求
    trigger:
      event: 订单送达
      delay: 7天
    actions:
      - check_return_status
      - 发送评价请求
```

## 商品上架管理

### 商品优化

```yaml
listing_template:
  标题:
    格式: "{{品牌}} {{商品名称}} - {{关键特性}} | {{变体}}"
    最大字符数: 200
    规则:
      - 首字母大写
      - 无促销短语
      - 包含主要关键词
      
  项目符号:
    数量: 5
    格式: |
      • {{利益}} - {{特性描述}}
    指南:
      - 以主要利益开头
      - 包含尺寸/规格
      - 回答常见问题
      - 使用相关关键词
      
  描述:
    格式: enhanced_brand_content  # 或 basic_html
    部分:
      - 品牌故事
      - 关键特性
      - 规格
      - 使用说明
      
  后台关键词:
    最大字节数: 250
    策略:
      - 包含错别字
      - 添加同义词
      - 无标点符号
      - 无重复单词
```

### 关键词研究

```yaml
keyword_strategy:
  工具:
    - helium10
    - jungle_scout
    - amazon_brand_analytics
    
  类别:
    主要关键词:
      - 高搜索量
      - 高相关性
      - 中等竞争
      
    次要关键词:
      - 长尾变体
      - 提问短语
      - 比较关键词
      
    后台关键词:
      - 错别字
      - 缩写
      - 外语翻译
      
  跟踪:
    每日监控排名: daily
    每周跟踪竞争对手: weekly
```

## 库存管理

### FBA库存规划

```yaml
inventory_planning:
  重新订购规则:
    - sku: "PROD-001"
      重新订购点: 30天的供应量
      目标库存: 90天的供应量
      提前期: 21天
      最小订购数量: 500
      
  存储优化:
    老化库存:
      阈值: 180天
      操作:
        - 创建移除订单
        - 运行促销
        - 调整价格
      
    存储费用:
      监控: 每月
      优化目标: Q4  # 假日季节
      
  发货自动化:
    触发器: 库存低于重新订购
    工作流程:
      - 计算数量
      - 创建发货计划
      - 生成标签
      - 通知仓库
```

### 库存仪表盘

```
FBA库存状态
═══════════════════════════════════════

概览:
总SKU:        245
有库存:          198
库存不足:         32
缺货:      15

库存健康:
健康           ██████████████░░ 78%
过剩            ████░░░░░░░░░░░░ 12%
困滞          ██░░░░░░░░░░░░░░ 6%
老化 (180+天)  █░░░░░░░░░░░░░░░ 4%

畅销商品 (供应天数):
┌──────────────────┬───────────┬──────────┐
│ 商品          │ 库存     │ 天数     │
├──────────────────┼───────────┼──────────┤
│ Widget Pro       │ 1,245     │ 28 ⚠️    │
│ Gadget Plus      │ 856       │ 45 ✓     │
│ Accessory Kit    │ 2,340     │ 120 📈   │
└──────────────────┴───────────┴──────────┘

推荐操作:
• 重新订购 Widget Pro (28天供应)
• 创建移除过剩 Accessory Kit
• 调查15个困滞SKU
```

## 定价策略

### 动态定价

```yaml
pricing_rules:
  - name: 竞争购买框
    条件:
      - has_buy_box: false
      - competitor_price: "<= my_price"
    操作:
      调整: match_lowest - $0.01
      底价: min_profit_price
      
  - name: 基于需求
    条件:
      - sales_velocity: "> 2x_average"
      - stock_level: "> 60天的"
    操作:
      调整: "+5%"
      最高价: max_price
      
  - name: 清仓
    条件:
      - stock_age: "> 150天的"
      - sales_velocity: "< 0.5x_average"
    操作:
      调整: "-15%"
      底价: cost + fees
```

### 利润计算器

```yaml
profit_calculation:
  收入:
    - 销售价格
    - 运输信用
    
  成本:
    - 产品成本
    - 运输至FBA
    - FBA履行费
    - 推荐费 (典型15%)
    - 存储费
    - 广告成本
    
  公式: |
    利润 = 销售价格
             - 产品成本
             - FBA费 (基于尺寸)
             - 推荐费 (典型15%)
             - 存储费 (每月)
             - 运输费用
             - PPC成本 (基于ACoS)
             
  示例:
    销售价格: $29.99
    产品成本: $8.00
    fba_fee: $4.75
    referral_fee: $4.50
    storage_fee: $0.25
    运输: $1.50
    ppc_cost: $2.00
    利润: $8.99 (30%利润率)
```

## 广告 (PPC)

### 营销活动结构

```yaml
ppc_structure:
  推广商品:
    自动活动:
      - name: "{{product}}_Auto_Research"
        定位: 自动
        预算: $20/天
        目的: keyword_discovery
        
    手动活动:
      - name: "{{product}}_Exact"
        匹配类型: exact
        关键词: top_performers
        预算: $50/天
        
      - name: "{{product}}_Phrase"
        匹配类型: phrase
        关键词: mid_performers
        预算: $30/天
        
      - name: "{{product}}_Broad"
        匹配类型: broad
        关键词: discovery
        预算: $20/天
        
  出价优化:
    目标ACoS: 25%
    规则:
      - 条件: "acos < 20%"
        操作: "increase_bid_10%"
      - 条件: "acos > 35%"
        操作: "decrease_bid_15%"
      - 条件: "no_sales_7_days"
        操作: "pause_keyword"
```

### PPC仪表盘

```
PPC表现 - 过去30天
═══════════════════════════════════════

概览:
支出:        $4,523
销售额:        $18,750
ACoS:         24.1%
TACoS:        8.2%
订单:       625

按活动类型:
推广商品  ████████████████ $3,200
品牌推广    ████░░░░░░░░░░░░ $823
展示广告   ██░░░░░░░░░░░░░ $500

顶级关键词:
┌────────────────────┬────────┬───────┬──────┐
│ 关键词            │ 支出  │ 销售 │ ACoS │
├────────────────────┼────────┼───────┼──────┤
│ wireless charger   │ $450   │ $2,100│ 21%  │
│ fast charging pad  │ $320   │ $1,450│ 22%  │
│ phone charger      │ $280   │ $980  │ 29%  │
└────────────────────┴────────┴───────┴──────┘

建议:
• 增加 "wireless charger" 的出价 (+15%)
• 添加否定关键词: "car charger" (0转化)
• 测试新关键词: "qi charger" (竞争对手)
```

## 订单管理

### 订单处理

```yaml
order_workflows:
  fba订单:
    # 亚马逊处理履行
    自动化:
      - 监控退货
      - 回应消息
      - 请求评价
      
  fbm订单:
    # 卖家处理履行
    工作流程:
      - 接收订单
      - 拣货包装
      - 生成标签
      - 发货
      - 确认发货
      - 上传追踪信息
      
  多渠道:
    # FBA处理非亚马逊订单
    来源:
      - shopify
      - ebay
      - 网站
    操作: create_mcf_order
```

### 客户沟通

```yaml
messaging_automation:
  订单已发货:
    延迟: 立即
    模板: |
      Hi {{buyer_name}},
      
      您的订单已发货！追踪号: {{tracking}}
      
      预计送达: {{delivery_date}}
      
      感谢您的购买!
      
  评价请求:
    延迟: 交付后7天
    条件:
      - no_return_requested
      - no_negative_feedback
    模板: seller_central_request_review
```

## 分析与报告

### 销售仪表盘

```
销售表现 - 本月
═══════════════════════════════════════

收入:      $45,230 (+12% MoM)
销量:        1,892 (+8% MoM)
订单:       1,654 (+10% MoM)

利润分解:
毛收入    $45,230
- 产品成本   $15,200 (33.6%)
- 亚马逊费用    $12,450 (27.5%)
- 广告    $3,680 (8.1%)
= 净利润     $13,900 (30.7%)

按商品:
Widget Pro    ████████████░░░░ $18,500
Gadget Plus   ████████░░░░░░░░ $12,300
Accessory     ██████░░░░░░░░░░ $8,430
Bundle        ████░░░░░░░░░░░░ $6,000

购买框%:
Widget Pro    ████████████████ 95%
Gadget Plus   ██████████████░░ 88%
Accessory     ████████████░░░░ 78%
```

## API集成

### SP-API示例

```python
# 获取订单
orders = sp_api.orders.get_orders(
    MarketplaceIds=["ATVPDKIKX0DER"],
    CreatedAfter="2024-01-01T00:00:00Z",
    OrderStatuses=["Unshipped", "PartiallyShipped"]
)

# 更新库存
sp_api.fba_inventory.create_inbound_shipment_plan(
    ShipFromAddress=warehouse_address,
    InboundShipmentPlanRequestItems=[
        {
            "SellerSKU": "PROD-001",
            "Quantity": 500
        }
    ]
)

# 获取商品费用
fees = sp_api.products.get_my_fees_estimate_for_sku(
    SellerSKU="PROD-001",
    MarketplaceId="ATVPDKIKX0DER",
    PriceToEstimateFees={"ListingPrice": {"Amount": 29.99}}
)
```

## 最佳实践

1. **优化商品信息**: 关键词、图片、A+内容
2. **监控购买框**: 保持竞争性定价
3. **管理库存**: 避免缺货和过剩
4. **控制ACoS**: 优化PPC效率
5. **快速响应**: 24小时消息回复
6. **跟踪指标**: 每日销售和利润审查
7. **为季节做准备**: Q4库存准备
8. **保持合规**: 遵守亚马逊政策
