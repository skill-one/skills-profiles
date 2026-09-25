# SaaS 指标

全面的 SaaS 指标分析，涵盖 MRR、ARR、流失率、LTV、CAC、队列分析以及投资者报告。对 SaaS 创始人、财务团队和投资者至关重要。

## 概述

此技能可实现：
- 收入指标计算（MRR、ARR、NRR）
- 流失率和留存分析
- 单位经济（LTV、CAC、LTV:CAC）
- 队列分析和预测
- 投资者报告准备

---

## 核心指标框架

### 1. 收入指标

```
┌─────────────────────────────────────────────────────────────┐
│                    MRR 水falls                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  起始 MRR                          $100,000             │
│  + 新增 MRR (新客户)              +$15,000            │
│  + 扩张 MRR (升级)             +$8,000             │
│  + 恢复 MRR                     +$2,000             │
│  - 收缩 MRR (降级)             -$3,000             │
│  - 流失 MRR (取消)            -$7,000             │
│  ─────────────────────────────────────              │
│  = 结束 MRR                          $115,000             │
│                                                             │
│  净新增 MRR = $15,000                                      │
│  MRR 增长率 = 15%                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**计算**：
```yaml
mrr_metrics:
  # 月度经常性收入
  MRR: sum(all_active_subscriptions.monthly_value)
  
  # 年度经常性收入
  ARR: MRR × 12
  
  # MRR 组成部分
  new_mrr: sum(new_subscriptions_this_month)
  expansion_mrr: sum(upgrades_this_month)
  contraction_mrr: sum(downgrades_this_month)
  churn_mrr: sum(cancelled_subscriptions_mrr)
  reactivation_mrr: sum(reactivated_subscriptions)
  
  # 净新增 MRR
  net_new_mrr: new_mrr + expansion_mrr + reactivation_mrr - contraction_mrr - churn_mrr
  
  # 增长率
  mrr_growth_rate: (ending_mrr - starting_mrr) / starting_mrr × 100
  mom_growth: (current_mrr - previous_mrr) / previous_mrr × 100
```

---

### 2. 流失指标

```yaml
churn_metrics:
  # Logo 流失 (客户数量)
  logo_churn_rate: 
    formula: customers_lost / customers_start_of_period × 100
    benchmark: <5% 每月 for SMB, <2% for Enterprise
  
  # 收入流失 (MRR)
  gross_revenue_churn:
    formula: churned_mrr / starting_mrr × 100
    benchmark: <3% 每月
  
  # 净收入流失 (包括扩张)
  net_revenue_churn:
    formula: (churned_mrr - expansion_mrr) / starting_mrr × 100
    target: 负数 (净扩张)
  
  # 净收入留存 (NRR)
  nrr:
    formula: (starting_mrr - churn + expansion) / starting_mrr × 100
    benchmark:
      good: 100-110%
      great: 110-120%
      best_in_class: >120%
```

**流失分析模板**：
```markdown
## 流失分析 - {月份}

### 概要
| 指标 | 数值 | 基准 | 状态 |
|--------|-------|-----------|--------|
| Logo 流失 | 3.2% | <5% | ✅ |
| 收入流失 | 2.8% | <3% | ✅ |
| 净收入留存 | 108% | >100% | ✅ |

### 流失分解
| 原因 | 客户数量 | 流失 MRR | 占比 |
|--------|-----------|----------|------------|
| 价格 | 5 | $2,500 | 35% |
| 竞争对手 | 3 | $1,800 | 25% |
| 不再需要 | 4 | $1,500 | 21% |
| 产品问题 | 2 | $800 | 11% |
| 其他 | 2 | $600 | 8% |

### 队列表现
- Q1 2025 队列：6 个月留存率 95%
- Q4 2024 队列：9 个月留存率 88%
- 企业部门：留存率 97% (最佳)
```

---

### 3. 单位经济

```
┌─────────────────────────────────────────────────────────────┐
│                   单位经济                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  客户终身价值 (LTV)                              │
│  ────────────────────────────                               │
│  ARPU × 毛利率 %                                      │
│  ─────────────────────── = LTV                              │
│     流失率                                              │
│                                                             │
│  示例:                                                   │
│  $100 ARPU × 80% 毛利率 / 3% 流失率 = $2,667 LTV             │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  客户获取成本 (CAC)                            │
│  ────────────────────────────────                           │
│  销售 & 营销支出                                    │
│  ─────────────────────────── = CAC                          │
│    新获取的客户数量                                   │
│                                                             │
│  示例:                                                   │
│  $50,000 S&M / 50 客户 = $1,000 CAC                    │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│  LTV:CAC 比率 = $2,667 / $1,000 = 2.67x                   │
│  CAC 回收期 = $1,000 / ($100 × 80%) = 12.5 个月         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**基准**：
```yaml
unit_economics_benchmarks:
  ltv_cac_ratio:
    poor: <1x
    acceptable: 1-2x
    good: 2-3x
    great: 3-5x
    excellent: >5x
  
  cac_payback_months:
    enterprise: <18
    mid_market: <12
    smb: <6
    consumer: <3
  
  毛利率:
    saas_typical: 70-85%
    基础设施: 50-70%
    服务密集型: 40-60%
```

---

### 4. 队列分析

```yaml
cohort_analysis:
  # 按注册月份定义队列
  cohort_definition: signup_month
  
  # 跟踪随时间变化的留存率
  retention_matrix:
    columns: [Month_0, Month_1, Month_2, ..., Month_12]
    rows: [Jan_cohort, Feb_cohort, Mar_cohort, ...]
    values: active_customers / initial_customers × 100

  # 跟踪收入留存
  revenue_cohort:
    values: current_mrr / initial_mrr × 100
    
  # 队列 LTV 计算
  cohort_ltv:
    formula: sum(all_revenue_from_cohort) / initial_cohort_size
```

**队列表示例**：
```
按队列的留存率 (% 仍活跃的客户)

         Month 0  Month 1  Month 2  Month 3  Month 6  Month 12
Jan '25   100%     92%      87%      84%      78%      65%
Feb '25   100%     94%      89%      86%      80%       -
Mar '25   100%     93%      88%      85%       -        -
Apr '25   100%     95%      90%       -        -        -
May '25   100%     94%       -        -        -        -
Jun '25   100%      -        -        -        -        -

平均   100%     94%      89%      85%      79%      65%
```

---

## 快速比率

```yaml
quick_ratio:
  formula: (new_mrr + expansion_mrr) / (contraction_mrr + churn_mrr)
  
  解释:
    "<1": 收缩 (失去的比获得的更多)
    "1-2": 可持续增长
    "2-4": 良好增长效率
    ">4": 优秀 (高增长潜力)
  
  示例:
    new_mrr: 15000
    expansion_mrr: 8000
    contraction_mrr: 3000
    churn_mrr: 7000
    quick_ratio: (15000 + 8000) / (3000 + 7000) = 2.3
```

---

## 投资者报告模板

### 月度指标仪表板

```markdown
# {公司} - 月度指标报告
## {月份 年份}

### 关键指标概要
| 指标 | 当前 | 上月 | 变化 | 基准 |
|--------|---------|----------|--------|-----------|
| ARR | $1.38M | $1.20M | +15% | - |
| MRR | $115K | $100K | +15% | - |
| 净新增 MRR | $15K | $12K | +25% | - |
| NRR | 108% | 105% | +3pp | >100% ✅ |
| Logo 流失 | 3.2% | 3.5% | -0.3pp | <5% ✅ |
| LTV:CAC | 2.7x | 2.5x | +0.2x | >3x ⚠️ |
| CAC 回收期 | 12.5mo | 13mo | -0.5mo | <12mo ⚠️ |

### MRR 水falls
```
起始 MRR:    $100,000
+ 新增:           +$15,000  (12 客户)
+ 扩张:      +$8,000  (25 升级)
+ 恢复:       +$2,000  (5 返回)
- 收缩:          -$3,000  (15 降级)
- 流失:          -$7,000  (18 取消)
═════════════════════════════
结束 MRR:      $115,000
```

### 客户指标
| 阶段 | 客户数量 | MRR | ARPU | 流失 |
|---------|-----------|-----|------|-------|
| 企业 | 45 | $45K | $1,000 | 1.5% |
| 中市场 | 120 | $36K | $300 | 2.8% |
| SMB | 350 | $34K | $97 | 4.5% |
| **总计** | **515** | **$115K** | **$223** | **3.2%** |

### 跑道 & 燃烧
- 现金余额: $2.5M
- 月度燃烧: $85K
- 跑道: 29 个月
- 收入/燃烧比率: 1.35x

### 目标 vs 实际
| 目标 | 目标 | 实际 | 状态 |
|------|--------|--------|--------|
| 新客户 | 15 | 12 | 🔴 80% |
| 净新增 MRR | $12K | $15K | 🟢 125% |
| NRR | 105% | 108% | 🟢 103% |
| CAC 回收期 | 12mo | 12.5mo | 🟡 96% |

### 下月展望
- 销售管道: $45K 合格机会
- 预计成交: 8-10 客户
- 预测 MRR: $125-130K
- 主要风险: 企业交易延迟、假日放缓
```

---

## 预测模型

### 自下而上的收入预测

```yaml
forecast_model:
  # 起始点
  base_mrr: 115000
  
  # 增长假设
  assumptions:
    new_customers_monthly: 15
    avg_new_customer_mrr: 1250
    expansion_rate: 2%  # 现有 MRR 的百分比
    contraction_rate: 0.5%
    logo_churn_rate: 3%
  
  # 月度计算
  monthly_forecast:
    new_mrr: new_customers × avg_mrr
    expansion_mrr: existing_mrr × expansion_rate
    contraction_mrr: existing_mrr × contraction_rate
    churn_mrr: existing_mrr × churn_rate
    
    ending_mrr: |
      starting_mrr 
      + new_mrr 
      + expansion_mrr 
      - contraction_mrr 
      - churn_mrr
```

### 12 个月预测

```
月份   起始   新增      扩张  流失    结束    增长
Jan     $115,000   $18,750  $2,300     $3,450   $132,600  15.3%
Feb     $132,600   $18,750  $2,652     $3,978   $150,024  13.1%
Mar     $150,024   $18,750  $3,000     $4,501   $167,274  11.5%
...
Dec     $285,000   $18,750  $5,700     $8,550   $300,900  5.6%

年度总结:
- 起始 ARR: $1.38M
- 结束 ARR: $3.61M
- 增长: 162%
```

---

## 细分分析

```yaml
segment_analysis:
  by_plan:
    - name: Starter
      mrr: 20000
      customers: 300
      arpu: 67
      churn: 6%
      
    - name: Professional
      mrr: 45000
      customers: 150
      arpu: 300
      churn: 3%
      
    - name: Enterprise
      mrr: 50000
      customers: 50
      arpu: 1000
      churn: 1.5%
  
  by_industry:
    - tech: {mrr: 60000, churn: 2.5%}
    - finance: {mrr: 30000, churn: 2%}
    - retail: {mrr: 25000, churn: 5%}
  
  by_company_size:
    - 1-50: {arpu: 100, churn: 5%}
    - 51-200: {arpu: 350, churn: 3%}
    - 201+: {arpu: 1200, churn: 1.5%}
```

---

## 输出示例

**请求**: "计算我公司的 SaaS 指标"

**输出**:
```markdown
# SaaS 指标分析

## 执行摘要
您的 SaaS 业务显示出健康的增长，并在一些方面需要优化。

### 优势 ✅
- 净收入留存率 108% (高于 100% 基准)
- 快速比率为 2.3x (良好增长效率)
- 企业部门显示留存率 97%

### 需改进的领域 ⚠️
- LTV:CAC 比率 2.7x (目标: >3x)
- CAC 回收期 12.5 个月 (目标: <12 个月)
- SMB 部门流失率 4.5% (目标: <4%)

### 建议
1. **降低 CAC**: 专注于低成本获取渠道
2. **提高 SMB 留存率**: 添加入职流程
3. **扩展企业业务**: 更高 ARPU，更低流失率
4. **增加扩张收入**: 上售/交叉销售计划

### 关键指标概览
| 指标 | 数值 | 状态 |
|--------|-------|--------|
| ARR | $1.38M | 📈 +15% MoM |
| NRR | 108% | ✅ 健康 |
| LTV:CAC | 2.7x | ⚠️ 改进 |
| 跑道 | 29 个月 | ✅ 安全 |
```

---

*SaaS 指标技能 - 隶属于 Claude 办公技能*
