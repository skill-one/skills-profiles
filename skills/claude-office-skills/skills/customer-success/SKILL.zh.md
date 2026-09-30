---
name: customer-success
description: 客户成功管理——入职引导、健康度评分、季度业务回顾（QBR）、扩展增长手册及客户留存策略
---

# 客户成功

全面的客户成功管理，涵盖客户入职、健康评分、季度业务回顾（QBR）、业务拓展方案和客户留存策略。

## 概述

本技能涵盖：
- 客户入职项目
- 健康评分和监控
- 季度业务回顾（QBR）模板
- 业务拓展和追加销售方案
- 客户留存和流失预防

---

## 客户入职

### 入职项目结构

```yaml
onboarding_phases:
  phase_1_kickoff:
    duration: "第1周"
    goals:
      - 建立关系
      - 设定预期
      - 收集需求
    activities:
      - 启动会议：60分钟
      - 介绍支持渠道
      - 分享入职计划
      - 安排实施
    deliverables:
      - 成功计划文档
      - 带里程碑的时间表
      
  phase_2_实施：
    duration: "第2-3周"
    goals:
      - 技术设置
      - 数据迁移
      - 集成配置
    activities:
      - 实施会议：2-3次
      - 技术支持
      - 测试和验证
    deliverables:
      - 可用环境
      - 集成上线
      
  phase_3_培训：
    duration: "第3-4周"
    goals:
      - 用户赋能
      - 管理员培训
      - 工作流设置
    activities:
      - 管理员培训：90分钟
      - 最终用户培训：60分钟
      - 工作流研讨会
    deliverables:
      - 已培训用户
      - 文档化工作流
      
  phase_4_上线：
    duration: "第4-5周"
    goals:
      - 正式上线
      - 采用跟踪
      - 快速见效
    activities:
      - 上线会议
      - 监控采用情况
      - 庆祝成果
    deliverables:
      - 用户活跃
      - 实现首次价值
      
  phase_5_交接：
    duration: "第6周"
    goals:
      - 过渡到客户成功经理（CSM）
      - 建立节奏
      - 记录成功
    activities:
      - 交接会议
      - 安排检查会议
      - NPS调查
    deliverables:
      - 持续的CSM关系
      - 基线指标
```

### 入职检查清单

```yaml
onboarding_checklist:
  pre_kickoff:
    - [ ] 审查销售记录和需求
    - [ ] 准备成功计划模板
    - [ ] 安排启动会议
    - [ ] 发送欢迎邮件
    
  启动：
    - [ ] 介绍和角色
    - [ ] 审查目标和时间表
    - [ ] 确定关键利益相关者
    - [ ] 定义成功指标
    - [ ] 安排实施会议
    
  实施：
    - [ ] 账户设置完成
    - [ ] 用户配置完成
    - [ ] SSO配置（如适用）
    - [ ] 集成连接
    - [ ] 数据迁移
    - [ ] 测试完成
    
  培训：
    - [ ] 管理员培训交付
    - [ ] 最终用户培训交付
    - [ ] 共享培训材料
    - [ ] 提供自助服务资源
    - [ ] 介绍认证计划
    
  上线：
    - [ ] 确认正式上线
    - [ ] 用户登录
    - [ ] 完成首个工作流
    - [ ] 实现快速见效
    - [ ] 庆祝上线
    
  交接：
    - [ ] 介绍CSM
    - [ ] 安排定期节奏
    - [ ] 明确支持升级路径
    - [ ] 发送NPS调查
    - [ ] 完成入职文档
```

---

## 健康评分

### 健康评分模型

```yaml
health_score_components:
  product_engagement: # 40%权重
    metrics:
      - dau_mau_ratio:
          excellent: >0.5
          good: 0.3-0.5
          at_risk: 0.1-0.3
          critical: <0.1
          
      - feature_adoption:
          measure: core_features_used / total_core_features
          excellent: >80%
          good: 60-80%
          at_risk: 40-60%
          critical: <40%
          
      - depth_of_use:
          measure: actions_per_user_per_week
          benchmark: vs_similar_customers
          
  relationship: # 25%权重
    metrics:
      - nps_score:
          promoter: 9-10
          passive: 7-8
          detractor: 0-6
          
      - csm_engagement:
          regular_meetings: true/false
          responsive_to_outreach: true/false
          
      - executive_sponsor:
          identified: true/false
          engaged: true/false
          
  financial: # 20%权重
    metrics:
      - payment_history:
          on_time: excellent
          late_1x: good
          late_2x+: at_risk
          
      - growth_trajectory:
          expanding: excellent
          stable: good
          contracting: at_risk
          
  sentiment: # 15%权重
    metrics:
      - support_tickets:
          sentiment_trend: positive/neutral/negative
          resolution_satisfaction: score
          
      - feedback:
          product_feedback: positive/neutral/negative
          feature_requests: engaged/silent
          
scoring_formula:
  total: (engagement × 0.4) + (relationship × 0.25) + (financial × 0.2) + (sentiment × 0.15)
  
tiers:
  healthy: 80-100 (绿色)
  stable: 60-79 (黄色)
  at_risk: 40-59 (橙色)
  critical: 0-39 (红色)
```

### 健康评分自动化

```yaml
health_automation:
  critical_score:
    trigger: score < 40
    actions:
      - alert: csm立即
      - alert: cs经理
      - schedule: 24小时内保存通话
      - pause: 营销邮件
      
  at_risk_score:
    trigger: score drops below 60
    actions:
      - alert: csm同日
      - schedule: 检查会议
      - review: 团队会议
      
  health_improvement:
    trigger: score increases by 20+
    actions:
      - flag: 扩张机会
      - schedule: 成功故事访谈
      - request: 证言或推荐
```

---

## 季度业务回顾（QBR）

### QBR模板

```markdown
# 季度业务回顾
## {公司名称} | {季度}{年份}

---

### 议程（60分钟）
1. 业务更新 (10分钟)
2. 成功指标回顾 (15分钟)
3. 产品使用分析 (10分钟)
4. 路线图预览 (10分钟)
5. 战略讨论 (10分钟)
6. 行动项和下一步 (5分钟)

---

### 1. 执行摘要

**关系健康度**: 🟢 健康 (分数: 85)

**主要亮点:**
- ✅ 超额完成采用目标15%
- ✅ 新上线3个部门
- ✅ NPS从7提升至9
- ⚠️ 待处理的特性请求: {特性}

**本季度ROI:**
- 节省时间: 500+小时
- 成本降低: $50,000
- 效率提升: 25%

---

### 2. 成功指标

| 目标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 用户采用 | 80% | 92% | ✅ 超额完成 |
| 每日活跃用户 | 100 | 120 | ✅ 超额完成 |
| 支持工单 | <10/月 | 8/月 | ✅ 符合预期 |
| NPS分数 | >8 | 9 | ✅ 超额完成 |

**趋势图表:**
[包含使用趋势、采用曲线]

---

### 3. 产品使用分析

**最常用的特性:**
1. {特性1} - 95%采用率
2. {特性2} - 87%采用率
3. {特性3} - 72%采用率

**未充分利用的特性:**
- {特性X} - 15%采用率
  - 建议: 培训课程
- {特性Y} - 22%采用率
  - 建议: 工作流研讨会

**核心用户:**
- {用户1}: 倡导者，可主导培训
- {用户2}: 重度API用户

---

### 4. 路线图预览

**下季度将推出:**
- 🚀 {特性1} - 回应您于{日期}的请求
- 🚀 {特性2} - 改进{工作流}
- 🚀 {集成} - 连接{工具}

**测试机会:**
- 您希望提前试用{特性}吗？

---

### 5. 战略讨论

**您的问题:**
1. 下季度您的首要任务是什么？
2. 有任何组织变化我们需要了解？
3. 您仍在哪些方面遇到摩擦？

**增长机会:**
- 部门X可受益于{产品}
- {用例}现在可通过新特性实现
- {等级}提供批量折扣

---

### 6. 行动项

| 项目 | 负责人 | 截止日期 |
|------|--------|----------|
| 安排{特性}培训 | CSM | {日期} |
| 与IT联系集成 | 客户 | {日期} |
| 分享测试访问权限 | 产品 | {日期} |
| 审查扩张提案 | 客户 | {日期} |

---

### 下季度QBR: {日期}
```

---

## 业务拓展方案

### 业务拓展触发因素

```yaml
expansion_signals:
  usage_based:
    - 接近座位限制：已授权80%
    - 特性使用达到上限：使用高级特性
    - API调用量增加：增长趋势
    - 存储空间接近上限：使用80%+
    
  行为:
    - 倡导者推广：内部宣传
    - 新部门兴趣：跨团队请求
    - 高管使用产品：C级使用
    - 特性请求：更高等级特性
    
  业务:
    - 公司融资：宣布新轮
    - 公司增长：招聘增加
    - 新计划：宣布项目
    - 即将到期续订：90天外
```

### 业务拓展对话框架

```yaml
expansion_framework:
  discover:
    questions:
      - "您计划哪些新举措？"
      - "哪些其他团队可能受益？"
      - "今天什么在限制您？"
    listen_for:
      - 增长计划
      - 痛点
      - 预算周期
      
  align:
    approach:
      - 关联他们的目标
      - 量化当前价值
      - 预测扩展价值
    messaging: |
      "基于您在{$X价值}中看到的{当前用例}，扩展到{新用例}可能带来{预测价值}。"
      
  propose:
    elements:
      - 具体建议
      - 定价选项
      - 实施时间表
      - ROI预测
      
  close:
    tactics:
      - 高管对齐
      - 倡导者支持
      - 测试选项
      - 续订捆绑包
```

---

## 客户留存策略

### 流失风险方案

```yaml
churn_indicators:
  high_risk:
    - no_login_30_days
    - usage_drop_50%
    - 支持投诉增加
    - 高管赞助人离职
    - 提及竞争对手
    
  根据风险采取行动:
    critical:
      - csm_call_within_24h
      - manager_escalation
      - executive_outreach
      - save_offer_prepared
      
    at_risk:
      - csm_call_within_48h
      - health_check_meeting
      - re_training_offered
      - success_plan_review
      
save_offers:
  by_reason:
    price:
      - discount: 3个月20%折扣
      - annual_commitment: 额外折扣
      - downgrade_option: 较低等级
      
    未使用:
      - training: 免费强化课程
      - implementation: 专业服务
      - 暂停: 1-3个月
      
    竞争对手:
      - 竞争性折扣
      - 特性承诺
      - 高管会议
      
    组织:
      - 合同灵活性
      - 暂停选项
      - 减少座位数
```

---

## 输出示例

**请求**: "为客户创建QBR演示文稿"

**输出**:

```markdown
# QBR演示文稿 - Acme公司
## 2025年Q4

---

## 幻灯片1：执行摘要

### 健康分数: 85/100 🟢

本季度成果:
- 📈 用户采用: 85% → 92%
- 💰 ROI实现: $150,000
- ⭐ NPS: 8 → 9

重点关注:
- 扩展到营销团队
- 增加API使用
- 准备续订

---

## 幻灯片2：成功指标

| 指标 | Q3 | Q4 | 变化 |
|------|----|----|------|
| 活跃用户 | 150 | 180 | +20% |
| 项目创建 | 500 | 750 | +50% |
| 节省时间 | 200小时 | 350小时 | +75% |

**ROI计算:**
- 节省时间: 350小时 × $50/小时 = $17,500/月
- 年价值: $210,000
- 投资: $60,000
- **ROI: 3.5倍**

---

## 幻灯片3：采用分析

**最常用的特性:**
1. 任务管理: 95%
2. 时间跟踪: 82%
3. 报告: 75%

**机会特性:**
- 自动化: 25% (已安排培训)
- 集成: 30% (提供Slack集成)

---

## 幻灯片4：路线图对齐

下季度将推出:
- ✅ AI助手 (回应您的特性请求)
- ✅ Salesforce集成
- ✅ 高级分析

**测试访问:**
您希望提前试用AI特性吗？

---

## 幻灯片5：战略讨论

1. 营销团队兴趣 → 扩张机会
2. API使用增长 → 考虑开发者等级
3. 续订在90天内 → 提供多年折扣

---

## 幻灯片6：行动项

| 行动 | 负责人 | 日期 |
|------|-------|------|
| 营销演示 | Acme | 1月15日 |
| API等级提案 | CSM | 1月20日 |
| 续订讨论 | 双方 | 2月1日 |

**下次QBR: 2026年4月**
```

---

*客户成功技能 - 隶属于Claude办公技能*
