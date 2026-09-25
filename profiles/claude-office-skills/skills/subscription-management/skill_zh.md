# 订阅管理

全面的 SaaS 订阅生命周期管理，包括计费操作、升级/降级流程、流失预防策略和收入优化。

## 概述

本技能涵盖：
- 订阅生命周期管理
- 定价和包装策略
- 升级/降级工作流
- 流失预防自动化
- 计费操作和催款

---

## 订阅生命周期

### 生命周期阶段

```
┌─────────────────────────────────────────────────────────────────┐
│                    订阅生命周期                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  试用 ──▶ 转化 ──▶ 活跃 ──▶ 扩展 ──▶ 续订     │
│    │           │            │           │            │          │
│    ▼           ▼            ▼           ▼            ▼          │
│  [放弃]    [流失]     [降级]  [流失]     [流失]        │
│                            │                        │           │
│                            ▼                        ▼           │
│                       [挽回] ◀──────────── [挽回]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 阶段定义

```yaml
lifecycle_stages:
  trial:
    duration: 14_days
    goal: 激活 + 转化
    key_metrics:
      - trial_starts
      - activation_rate
      - trial_to_paid_conversion
    automation:
      - onboarding_emails
      - in_app_guidance
      - sales_touch (if qualified)
      
  active:
    goal: 价值交付 + 扩展
    key_metrics:
      - feature_adoption
      - nps_score
      - expansion_revenue
    automation:
      - health_scoring
      - usage_alerts
      - upsell_triggers
      
  at_risk:
    trigger: health_score < 40 OR usage_drop > 50%
    goal: 留存
    key_metrics:
      - save_rate
      - churn_reason
    automation:
      - csm_alert
      - retention_offer
      - executive_escalation
      
  churned:
    goal: 挽回
    key_metrics:
      - reactivation_rate
      - time_to_reactivate
    automation:
      - exit_survey
      - win_back_campaigns
      - competitive_monitoring
```

---

## 定价 & 包装

### 定价策略模板

```yaml
pricing_tiers:
  starter:
    price: $29/月
    billing: 月付或年付（免2个月）
    target: 个人创业者、小团队
    limits:
      users: 5
      storage: 10GB
      features: 核心功能
    positioning: "入门"
    
  professional:
    price: $79/月
    billing: 月付或年付
    target: 发展中的团队
    limits:
      users: 25
      storage: 100GB
      features: 核心功能 + 高级功能
    positioning: "最受欢迎"
    highlight: true
    
  business:
    price: $199/月
    billing: 月付或年付
    target: 扩张中的公司
    limits:
      users: 无限
      storage: 500GB
      features: 全部功能 + 优先支持
    positioning: "增长"
    
  enterprise:
    price: 定制
    billing: 仅年付
    target: 大型组织
    limits:
      users: 无限
      storage: 无限
      features: 全部功能 + SSO + API + SLA
    positioning: "联系销售"
    
add_ons:
  - extra_storage: $10/50GB
  - api_access: $50/月
  - priority_support: $100/月
  - dedicated_csm: $500/月
```

### 价值指标

```yaml
value_metric_options:
  per_seat:
    charge: 按活跃用户收费
    pros: 可预测，与增长一致
    cons: 可能限制采用
    best_for: 协作工具
    
  usage_based:
    charge: 按API调用、GB、交易收费
    pros: 低门槛，随价值扩展
    cons: 收入不可预测
    best_for: 基础设施、API
    
  feature_tiered:
    charge: 基于使用功能收费
    pros: 清晰的升级路径
    cons: 可能感觉受限
    best_for: 具有不同使用场景的软件
    
  hybrid:
    charge: 基础费 + 使用超额费
    pros: 可预测的基础 + 潜力
    cons: 解释复杂
    best_for: 成熟产品
```

---

## 升级/降级流程

### 升级自动化

```yaml
upgrade_triggers:
  usage_based:
    - trigger: approaching_user_limit (80%)
      action:
        - in_app_notification: "您接近用户限额"
        - email: upgrade_suggestion
        - if_ignored: soft_limit_warning
        
    - trigger: feature_blocked (tried advanced feature)
      action:
        - in_app_modal: feature_preview + upgrade_cta
        - track: feature_interest
        
    - trigger: consistent_overage (3+ months)
      action:
        - csm_outreach: proactive_upgrade_discussion
        
  behavior_based:
    - trigger: power_user_behavior
      condition: >5h/周使用 AND >10位团队成员邀请
      action:
        - flag_as: expansion_opportunity
        - assign: csm_for_outreach
        
  time_based:
    - trigger: 90_days_on_same_plan
      action:
        - email: "您是否充分利用了{产品}？"
        - include: feature_comparison

upgrade_flow:
  steps:
    1. show_comparison: current_vs_recommended
    2. highlight_value: features_they've_tried_to_use
    3. offer_discount: if_annual (可选)
    4. prorate_billing: charge_difference_immediately
    5. unlock_features: immediately
    6. send_confirmation: email + in_app
    7. trigger_onboarding: for_new_features
```

### 降级预防

```yaml
downgrade_flow:
  steps:
    1. intercept_request:
        show: "在您离开前..."
        offer: 
          - 暂停订阅: 1-3个月
          - 折扣: 3个月20%_折扣
          - 免费月: 如果是年付
          
    2. collect_reason:
        options:
          - 太贵
          - 未使用功能
          - 切换到竞争对手
          - 公司规模缩小
          - 暂时暂停
          
    3. tailored_response:
        too_expensive:
          - offer: lower_tier_suggestion
          - show: cost_per_user_value
          
        not_using_features:
          - offer: training_session
          - show: quick_wins_tutorial
          
        switching_to_competitor:
          - ask: which_competitor
          - offer: competitive_discount
          - flag: for_win_back_later
          
    4. if_proceeds:
        - schedule_downgrade: 结算周期结束
        - preserve_data: for_potential_return
        - send_survey: detailed_feedback
        
    5. track:
        - reason
        - offers_presented
        - offers_accepted/declined
        - revenue_impact
```

---

## 流失预防

### 健康评分

```yaml
customer_health_score:
  components:
    product_usage: 40%
      signals:
        - daily_active_users: vs_licensed_seats
        - feature_adoption: core_features_used
        - login_frequency: weekly_active
        - depth_of_use: actions_per_session
        
    engagement: 30%
      signals:
        - email_opens: last_30_days
        - support_sentiment: positive_vs_negative
        - nps_score: latest
        - community_participation: if_applicable
        
    relationship: 20%
      signals:
        - csm_touchpoints: recent_calls
        - executive_sponsor: identified
        - contract_length: multi_year_bonus
        
    financial: 10%
      signals:
        - payment_history: on_time_payments
        - expansion_history: upgrades_vs_downgrades
        - invoice_disputes: count
        
  scoring:
    90-100: 健康 (绿色)
    70-89: 稳定 (黄色)
    40-69: 风险 (橙色)
    0-39: 危急 (红色)
    
  automation:
    critical:
      - immediate: csm_alert + call_scheduled
      - if_no_response: manager_escalation
      
    at_risk:
      - same_day: csm_notification
      - action: health_check_call
      
    stable:
      - weekly: review_in_team_meeting
      
    healthy:
      - monthly: expansion_opportunity_review
```

### 催款管理

```yaml
dunning_sequence:
  payment_failed:
    day_0:
      - retry_payment: automatic
      - email: "付款失败 - 请更新"
      - in_app: banner_notification
      
    day_3:
      - retry_payment: automatic
      - email: "需要操作: 更新付款"
      - include: direct_update_link
      
    day_7:
      - retry_payment: automatic
      - email: "您的账户有风险"
      - sms: if_enabled
      - downgrade_warning: true
      
    day_14:
      - final_retry: automatic
      - email: "最终通知前暂停"
      - csm_call: for_high_value_accounts
      
    day_21:
      - suspend_account: read_only_access
      - email: "账户暂停"
      - preserve_data: 90_days
      
    day_90:
      - delete_data: after_warning
      - final_email: account_closure
      
  recovery_metrics:
    track:
      - involuntary_churn_rate
      - recovery_rate_by_day
      - avg_days_to_recovery
      - revenue_recovered
```

---

## 收入运营

### 计费自动化

```yaml
billing_operations:
  invoice_generation:
    timing: 7_days_before_renewal
    include:
      - usage_summary
      - upcoming_charges
      - payment_method
      
  proration:
    upgrades: charge_immediately (prorated)
    downgrades: credit_at_next_billing
    mid_cycle_changes: calculate_daily
    
  discounts:
    types:
      - percentage: 10%, 20%, 30%
      - fixed: $X off
      - free_months: 1-3 months
    controls:
      - approval_required: >30%
      - expiration: always_set
      - one_per_customer: unless_approved
      
  revenue_recognition:
    method: ratable
    timing: 每月
    deferred_revenue: track_separately
```

### 报表仪表盘

```markdown
# 订阅指标仪表盘

## MRR 概要
| 指标 | 数值 | MoM 变化 |
|------|-------|------------|
| 总 MRR | $500K | +8% |
| 新 MRR | $50K | +15% |
| 扩展 MRR | $30K | +12% |
| 流失 MRR | $20K | -5% |
| 净新 MRR | $60K | +20% |

## 订阅健康度
| 等级 | 客户数 | MRR | 平均健康度 |
|------|-----------|-----|------------|
| 企业 | 50 | $200K | 85 |
| 商业 | 150 | $180K | 78 |
| 专业 | 400 | $100K | 72 |
| 入门 | 800 | $20K | 65 |

## 风险账户 (需要操作)
| 公司 | MRR | 健康 | 风险原因 |
|---------|-----|--------|-------------|
| Acme Co | $5K | 35 | 使用下降 60% |
| Tech Inc | $3K | 42 | 付款失败 |
| StartupX | $2K | 38 | 30天未登录 |

## 流失分析
- 自愿流失: 1.5% (目标: <2%) ✅
- 非自愿流失: 0.8% (目标: <1%) ✅
- 主要原因: 价格 (35%)
- 挽回率: 25%
```

---

## 输出示例

**请求**: "为 SaaS 产品创建流失预防工作流"

**输出**:

```markdown
# 流失预防工作流

## 早期预警系统

### 健康评分触发器

```yaml
triggers:
  critical_alert: # 健康 < 40
    - immediate: slack_alert_to_csm
    - same_day: schedule_call
    - email: "我们注意到您未登录..."
    - offer: free_training_session
    
  usage_drop: # >50% 下降
    - email: "一切正常吗？"
    - in_app: help_resources
    - csm_task: check_in_call
    
  support_escalation: # 负面情绪
    - flag: at_risk
    - csm_notification: with_context
    - executive_apology: if_major_issue
```

## 干预方案

### 场景: 低使用率

```
Day 1: 自动邮件
"您好{name}，我们注意到{产品}使用率下降。 
一切正常吗？这里提供3个快速获取价值的建议："

Day 3: 应用内消息
"需要帮助吗？预约15分钟免费咨询。"

Day 7: CSM 电话
议程: 了解障碍，提供解决方案

Day 14: 经理升级
如果无回应，内部升级
```

### 场景: 付款失败

```
Hour 0: 自动重试付款
Hour 1: 邮件更新链接
Day 3: 第二封邮件 + SMS
Day 7: CSM 电话 (高价值账户)
Day 14: 最终警告
Day 21: 暂停 (保留数据90天)
```

### 挽回方案矩阵

| 流失原因 | 方案 |
|--------------|-------|
| 太贵 | 3个月20%_折扣 |
| 未使用 | 免费培训 + 暂停选项 |
| 竞争对手 | 对比价格 + 迁移帮助 |
| 规模缩小 | 降级到低等级 |
| 暂时 | 1-3个月免费暂停 |

## 需要追踪的指标

- 挽回率: 目标 >25%
- 干预时间: <24h for critical
- 流失原因分布
- 方案接受率
- 挽回收入
```

---

*订阅管理技能 - 隶属于 Claude 办公技能*
