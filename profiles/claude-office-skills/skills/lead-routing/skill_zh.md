# 销售线索分配

基于AI的销售线索评分、区域映射、轮询分配和工作负载平衡的智能销售线索分配和路由系统。基于n8n的HubSpot/Salesforce自动化模板。

## 概述

本技能涵盖：
- 销售线索评分和资格认证
- 基于区域的路由
- 轮询分配
- 工作负载平衡
- SLA监控和升级

---

## 路由策略

### 1. 基于规则的分配

```yaml
routing_rules:
  # 按公司规模
  - name: "企业级分配"
    condition:
      company_size: ">= 500"
      OR:
        annual_revenue: ">= $10M"
    assign_to: "企业级团队"
    priority: 高
    sla: 1小时
    
  - name: "中市场分配"
    condition:
      company_size: "100-499"
    assign_to: "中市场团队"
    priority: 中
    sla: 4小时
    
  - name: "中小企业分配"
    condition:
      company_size: "< 100"
    assign_to: "中小企业团队"
    priority: 标准
    sla: 24小时

  # 按地理位置
  - name: "亚太区域分配"
    condition:
      country: ["中国", "日本", "新加坡", "澳大利亚"]
    assign_to: "亚太团队"
    timezone_aware: true
    
  - name: "欧洲、中东和非洲分配"
    condition:
      country: ["英国", "德国", "法国", "荷兰"]
    assign_to: "欧洲、中东和非洲团队"
    
  - name: "美洲分配"
    condition:
      country: ["美国", "加拿大", "巴西", "墨西哥"]
    assign_to: "美洲团队"

  # 按行业
  - name: "医疗保健专家"
    condition:
      industry: ["医疗保健", "制药", "医疗设备"]
    assign_to: "医疗保健销售"
    
  - name: "金融专家"
    condition:
      industry: ["银行", "保险", "金融科技"]
    assign_to: "金融服务销售"
```

---

### 2. 轮询分配

```yaml
round_robin_config:
  team: "中小企业销售"
  members:
    - name: Alice
      capacity: 100%
      max_leads_per_day: 20
      
    - name: Bob
      capacity: 100%
      max_leads_per_day: 20
      
    - name: Carol
      capacity: 50%  # 兼职
      max_leads_per_day: 10
      
  rules:
    distribution: weighted  # 或 equal
    skip_if:
      - out_of_office: true
      - at_capacity: true
    reset: daily
    
  tracking:
    log_assignments: true
    balance_check: 每小时
    
**分配算法**:
```
┌─────────────────────────────────────────────────────────────┐
│                   轮询逻辑                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 新销售线索到达                                        │
│                    │                                        │
│                    ▼                                        │
│  2. 检查团队可用性                                 │
│     - 过滤：休假中、已满负荷、非工作时间              │
│                    │                                        │
│                    ▼                                        │
│  3. 计算加权位置                             │
│     - 当天当前分配                             │
│     - 容量百分比                                   │
│     - 最后分配时间                                  │
│                    │                                        │
│                    ▼                                        │
│  4. 分配给得分最低的客服人员               │
│                    │                                        │
│                    ▼                                        │
│  5. 更新跟踪，通知客服人员                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. 基于AI的销售线索评分

```yaml
ai_scoring:
  provider: openai
  model: gpt-4
  
  input_factors:
    demographic:
      - company_size
      - industry
      - job_title
      - location
      
    firmographic:
      - annual_revenue
      - employee_count
      - funding_stage
      - tech_stack
      
    behavioral:
      - pages_visited
      - content_downloads
      - email_engagement
      - demo_requests
      
    fit_score:
      - icp_match_percentage
      - competitor_usage
      - budget_authority
      
  scoring_prompt: |
    根据以下信息对销售线索进行0-100分的评分：
    
    我们的ICP（理想客户画像）：
    - B2B SaaS公司
    - 50-500名员工
    - A轮融资或更高
    - 使用{competitor}或{类似工具}
    
    销售线索数据：
    {lead_data}
    
    返回JSON：
    {
      "score": 0-100,
      "fit_score": 0-100,
      "intent_score": 0-100,
      "tier": "A/B/C/D",
      "reasoning": "...",
      "recommended_action": "...",
      "routing_suggestion": "..."
    }

  tier_thresholds:
    A: 80-100  # 热线索，立即跟进
    B: 60-79   # 合格，标准跟进
    C: 40-59   # 培养中，营销序列
    D: 0-39    # 低优先级，长期培养
```

---

### 4. 区域映射

```yaml
territory_map:
  north_america:
    west:
      states: [CA, WA, OR, NV, AZ, CO, UT]
      owner: "西海岸团队"
      reps: [Alice, Bob]
      
    central:
      states: [TX, IL, OH, MI, MN, WI]
      owner: "中部团队"
      reps: [Carol, David]
      
    east:
      states: [NY, MA, PA, FL, GA, NC]
      owner: "东海岸团队"
      reps: [Eve, Frank]
      
  international:
    emea:
      countries: [UK, DE, FR, NL, ES, IT]
      owner: "欧洲、中东和非洲团队"
      timezone: "Europe/London"
      
    apac:
      countries: [JP, SG, AU, KR, IN]
      owner: "亚太团队"
      timezone: "Asia/Tokyo"

  overlap_resolution:
    # 当销售线索匹配多个区域时
    priority_order:
      1: named_account_owner  # 如果账户已有负责人
      2: industry_specialist  # 如果行业需要专家
      3: geography           # 默认按地理位置
```

---

### 5. 工作负载平衡

```yaml
workload_balancer:
  check_frequency: 每小时
  
  metrics_tracked:
    - current_open_leads
    - leads_assigned_today
    - leads_assigned_this_week
    - average_response_time
    - conversion_rate
    
  balance_rules:
    max_variance: 20%  # 客服人员之间的最大差异
    
    rebalance_trigger:
      - variance > max_variance
      - rep_at_capacity
      - rep_underperforming
      
    rebalance_actions:
      - pause_assignments: for_overloaded_rep
      - increase_weight: for_underloaded_rep
      - notify_manager: when_rebalancing
      
  capacity_management:
    per_rep:
      max_open_leads: 50
      max_new_per_day: 15
      max_new_per_week: 60
      
    team_level:
      overflow_queue: true
      overflow_notify: sales_manager
      escalation_threshold: 2小时
```

---

## 工作流实现

### 完整销售线索分配工作流

```yaml
workflow: "智能销售线索路由器"

trigger:
  - type: hubspot_contact_created
  - type: form_submission
  - type: api_webhook

steps:
  1. enrich_lead:
      providers: [clearbit, zoominfo]
      fields:
        - company_size
        - industry
        - revenue
        - location
        - linkedin_url
        
  2. score_lead:
      method: ai_scoring
      store_result:
        hubspot_property: lead_score
        
  3. determine_tier:
      A_tier: score >= 80
      B_tier: score >= 60
      C_tier: score >= 40
      D_tier: score < 40
      
  4. apply_routing_rules:
      sequence:
        - check: named_account_owner
        - check: industry_specialist
        - check: territory_match
        - check: round_robin_availability
        
  5. assign_owner:
      hubspot:
        update_contact:
          hubspot_owner_id: "{selected_owner_id}"
          lead_status: "新"
          lead_tier: "{tier}"
          routing_reason: "{routing_logic}"
          
  6. create_task:
      hubspot:
        type: CALL
        subject: "跟进：新{tier}销售线索 - {公司}"
        due_date: "{sla_deadline}"
        priority: "{基于tier的优先级}"
        notes: |
          销售线索评分：{score}
          分配原因：{routing_reason}
          关键信息：{summary}
          
  7. notify_owner:
      slack_dm:
        message: |
          🎯 *新销售线索分配*
          
          **{contact_name}** at **{公司}**
          评分：{score} ({tier} 级别)
          
          📞 SLA：在{sla_time}内响应
          
          快速操作：
          • [HubSpot中查看]({hubspot_link})
          • [LinkedIn]({linkedin_url})
          • [安排通话]({calendly_link})
          
  8. start_sla_timer:
      deadline: "{sla_deadline}"
      escalation_path:
        - 50%_elapsed: reminder_to_owner
        - 80%_elapsed: notify_manager
        - 100%_elapsed: 重新分配 + 报警
```

---

## SLA管理

```yaml
sla_tiers:
  tier_a:
    response_time: 1小时
    escalation_path:
      - 30min: slack_reminder
      - 45min: manager_alert
      - 60min: 自动重新分配
      
  tier_b:
    response_time: 4小时
    escalation_path:
      - 2h: slack_reminder
      - 3h: manager_alert
      - 4h: 自动重新分配
      
  tier_c:
    response_time: 24小时
    escalation_path:
      - 12h: slack_reminder
      - 20h: manager_alert
      - 24h: 移至队列

sla_reporting:
  metrics:
    - response_time_avg
    - response_time_p90
    - sla_compliance_rate
    - escalation_count
    
  report_frequency: 每周
  recipients: [sales_manager, ops_manager]
```

---

## 报表仪表盘

```markdown
# 销售线索分配报告 - {周}

## 分配摘要
| 客服人员 | 分配数量 | 响应数量 | 平均响应时间 | SLA达标 |
|-----|----------|-----------|--------------|---------|
| Alice | 45 | 43 | 1.2小时 | 96% |
| Bob | 42 | 40 | 1.8小时 | 90% |
| Carol | 38 | 38 | 0.8小时 | 100% |
| **总计** | **125** | **121** | **1.3小时** | **95%** |

## 按级别
| 级别 | 数量 | 平均评分 | 转化数量 | 转化率 |
|------|-------|-----------|-----------|-----------|
| A | 25 | 87 | 12 | 48% |
| B | 45 | 68 | 15 | 33% |
| C | 35 | 52 | 5 | 14% |
| D | 20 | 28 | 1 | 5% |

## 分配明细
- 按区域：60%
- 按行业：25%
- 轮询分配：15%

## 问题
- 3个销售线索等待>SLA（已重新分配）
- Alice已满负荷（95%）（监控）
- 没有医疗保健垂直领域的覆盖（缺口）

## 建议
1. 招聘医疗保健专家
2. 增加Bob的培训（响应时间）
3. 调整A级别阈值至85（太多误报）
```

---

## 输出示例

**请求**： "路由此销售线索：John Smith，TechCorp公司的CTO（500名员工，旧金山，SaaS）"

**输出**：

```markdown
# 销售线索分配决策

## 销售线索信息
- **姓名**： John Smith
- **职位**： CTO
- **公司**： TechCorp
- **规模**： 500名员工
- **位置**： 旧金山，CA
- **行业**： SaaS

## AI评分
```json
{
  "score": 85,
  "fit_score": 90,
  "intent_score": 80,
  "tier": "A",
  "reasoning": "强ICP匹配 - 500人SaaS公司的CTO在我们的目标市场中。高权威度的购买者。",
  "recommended_action": "立即跟进 - 高价值潜在客户"
}
```

## 分配决策

**分配给**： Alice Chen（企业级西海岸）

**分配逻辑**：
1. ✅ 区域：旧金山→西海岸
2. ✅ 公司规模：500→企业级
3. ✅ 行业：SaaS→不需要专家
4. ✅ 可用性：Alice有容量（今天18/20）

## 创建的操作项

1. **任务**： 跟进通话
   - 截止时间：1小时（A级别SLA）
   - 优先级：高

2. **Slack通知**： 已发送给Alice

3. **SLA计时器**： 已启动（1小时倒计时）

## 推荐跟进方式

```
主题：关于{痛点}的快速问题 - TechCorp

Hi John,

注意到TechCorp正在快速发展 - 恭喜你们取得的成就。 

类似SaaS公司的CTO经常告诉我们{常见挑战}。 

本周安排15分钟的通话是否合适，看看我们是否可以帮助？

[Calendly链接]
```
```

---

*销售线索分配技能 - Claude办公技能的一部分*
