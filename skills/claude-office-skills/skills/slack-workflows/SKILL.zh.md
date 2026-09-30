---
name: slack-workflows
description: Slack 自动化和工作流构建器 - 通知、站会机器人、审批流程和跨平台集成
---

# Slack 工作流

通过智能工作流自动化工单通知、站会收集、审批流程和跨平台集成。基于 n8n 自动化模式。

## 概述

本技能涵盖：
- 自动化通知和警报
- 每日站会收集
- 审批工作流
- 跨平台集成
- 频道管理自动化

---

## 核心工作流

### 1. 每日站会机器人

```yaml
workflow: "异步站会"
schedule: "工作日 上午 9:00"

steps:
  1. send_prompt:
      channel: 每位团队成员 (私信)
      message: |
        👋 早上好！是站会时间了。
        
        请分享：
        1️⃣ 你昨天完成了什么？
        2️⃣ 你今天在做什么？
        3️⃣ 有什么阻碍？
        
        在此线程中回复 👇
        
  2. collect_responses:
      timeout: 2小时
      reminder: 1小时后提醒
      
  3. compile_summary:
      time: "上午 11:00"
      channel: "#团队站会"
      format: |
        📋 *每日站会 - {日期}*
        
        {遍历每个成员}
        *{姓名}*
        ✅ 昨天：{昨天完成}
        📌 今天：{今天工作}
        🚧 阻碍：{阻碍}
        
        ---
        {结束遍历}
        
        *总结：*
        • {总人数} 位团队成员回复
        • {阻碍数量} 个阻碍被标记
        
  4. flag_blockers:
      if: 阻碍数量 > 0
      notify: 经理
      action: 创建讨论线程
```

### 2. 审批工作流

```yaml
workflow: "费用审批"
trigger: 表单提交 OR 剪贴板命令

steps:
  1. receive_request:
      data:
        - 申请人
        - 金额
        - 类别
        - 描述
        - 收据链接
        
  2. route_approval:
      rules:
        - if: 金额 < 100
          approver: 直属经理
          
        - if: 金额 >= 100 AND 金额 < 1000
          approver: 部门主管
          
        - if: 金额 >= 1000
          approver: [部门主管, 财务]
          type: 顺序
          
  3. send_approval_request:
      channel: 申请人私信
      message: |
        📝 *费用审批请求*
        
        *来自：* {申请人}
        *金额：* ${金额}
        *类别：* {类别}
        *描述：* {描述}
        
        [查看收据]({收据链接})
        
      actions:
        - button: "✅ 批准"
          action: 批准
        - button: "❌ 拒绝"
          action: 拒绝
        - button: "💬 提问"
          action: 请求信息
          
  4. handle_response:
      approved:
        - notify_requester: "您的费用已批准！ 🎉"
        - create_task: 在会计系统中
        - log: 在费用追踪器中
        
      rejected:
        - notify_requester: "费用未批准。原因：{原因}"
        - log: 带拒绝原因
        
  5. escalate_if_no_response:
      timeout: 24小时
      action: 提醒审批人
      final_escalation: 48小时
```

### 3. 新员工入职

```yaml
workflow: "员工入职"
trigger: 新员工添加到 HRIS

timeline:
  入职前7天:
    - create_channels:
        - "#欢迎-{姓名}"
        - add_to: ["#general", "#团队-{部门}"]
    - notify_it: "为 {姓名} 设置笔记本电脑"
    - notify_manager: "入职将在7天后开始"
    
  入职当天:
    - 上午:
        - post_welcome: "#general"
          message: |
            🎉 请欢迎 *{姓名}* 加入团队！
            
            职位：{职位}
            团队：{部门}
            办公地点：{办公室}
            
            有趣的事实：{有趣的事实}
            
            大家打个招呼，让他们感受到欢迎！ 👋
            
        - dm_new_hire:
            message: |
              欢迎加入 {公司}！ 🚀
              
              您的第一步：
              1. [完成 HR 文件]({hr链接})
              2. [设置您的账户]({it链接})
              3. [认识团队]({组织架构图})
              
              您的伙伴是 @{伙伴姓名} - 随时联系！
              
    - 下午:
        - schedule_intros: 与关键利益相关者
        
  入职第3天:
    - check_in:
        dm: "你第一周过得怎么样？有什么问题吗？"
        
  入职第7天:
    - survey:
        question: "你的入职体验如何？"
        scale: 1-5
        
  入职第30天:
    - feedback_request:
        dm: "你已经入职一个月了！我们可以改进什么？"
```

### 4. 事件响应

```yaml
workflow: "事件警报"
trigger: 监控警报 OR 手动

严重程度等级:
  critical:
    - create_channel: "#事件-{时间戳}"
    - notify: "@频道 在 #工程团队"
    - page: 值班工程师
    - create_war_room: 视频链接
    - start_timer: 用于解决跟踪
    
  high:
    - notify: "#工程团队警报"
    - assign: 值班工程师
    - create_ticket: 在 Jira 中
    
  medium:
    - notify: "#工程团队警报"
    - create_ticket: 在 Jira 中
    
  low:
    - create_ticket: 在 Jira 中
    - notify: 下一个工作日

事件频道模板: |
  🚨 *事件：{标题}*
  
  *严重程度：* {严重程度}
  *状态：* 调查中
  *开始时间：* {时间戳}
  *指挥官：* @{指挥官}
  
  ---
  
  *受影响的系统：*
  {系统}
  
  *客户影响：*
  {影响}
  
  ---
  
  📋 *行动：*
  • [ ] 确定根本原因
  • [ ] 实施修复
  • [ ] 验证解决
  • [ ] 通知利益相关者
  
  🔗 *链接：*
  • [操作手册]({操作手册链接})
  • [仪表盘]({仪表盘链接})
  • [视频房间]({视频链接})

解决流程:
  1. commander_declares: "已解决"
  2. notify_stakeholders: 解决消息
  3. archive_channel: 24小时后
  4. create_postmortem: 在 Notion 中
  5. schedule_review: 在日历中
```

### 5. 跨平台同步

```yaml
workflow: "CRM 到 Slack 通知"

triggers:
  hubspot_deal_won:
    channel: "#胜利"
    message: |
      🎉 *交易成功！*
      
      *公司：* {公司}
      *金额：* ${金额}
      *代表：* @{销售代表}
      *产品：* {产品}
      
      恭喜！ 🚀
      
  hubspot_deal_lost:
    channel: "#销售团队"
    message: |
      📊 *交易失败*
      
      *公司：* {公司}
      *金额：* ${金额}
      *原因：* {失败原因}
      *竞争对手：* {竞争对手}
      
      线程用于学习 👇
      
  github_pr_merged:
    channel: "#工程团队"
    message: |
      ✅ PR 合并：*{pr标题}*
      by @{作者}
      
      {pr描述摘要}
      
  stripe_payment_failed:
    channel: "#收入警报"
    message: |
      ⚠️ *支付失败*
      
      *客户：* {客户邮箱}
      *金额：* ${金额}
      *原因：* {失败原因}
      
      [在 Stripe 中查看]({stripe链接})
```

---

## 剪贴板命令

### 自定义命令

```yaml
剪贴板命令:
  /kudos:
    description: "给队友认可"
    usage: "/kudos @人 因 [原因]"
    action:
      - post_to: "#认可"
      - format: |
          🌟 *认可！*
          
          @{发送者} 给了 @{接收者} 认可
          
          > {原因}
          
      - track: 在认可电子表格中
      
  /pto:
    description: "申请休假"
    usage: "/pto [开始日期] 到 [结束日期] 因 [原因]"
    action:
      - create_approval: pto审批流程
      - update_calendar: 拒绝日期
      - notify_team: 如果批准
      
  /standup:
    description: "提交异步站会"
    usage: "/standup"
    action:
      - open_modal: 站会表单
      - collect_responses: 昨天，今天，阻碍
      - post_to: "#团队站会"
      
  /poll:
    description: "创建快速投票"
    usage: "/poll '问题' '选项1' '选项2' ..."
    action:
      - create_message: 带有反应
      - track_votes: 通过反应计数
      - close_poll: 24小时后或手动
```

---

## 频道管理

```yaml
频道自动化:
  项目频道:
    trigger: jira项目创建
    action:
      - create_channel: "#proj-{项目键}"
      - add_members: 项目团队
      - set_topic: "{项目名称} - {项目描述}"
      - pin_message: 项目资源
      - archive: 项目完成后
      
  客户频道:
    trigger: 交易成功
    action:
      - create_channel: "#客户-{公司}"
      - add_members: [客户成功经理, 销售代表, 支持]
      - set_purpose: "支持频道 {公司}"
      - integrate: Zendesk警报
      
  清理:
    schedule: 每月
    rules:
      - archive_if:
          无消息：90天
          AND:
            not_pinned: true
            not_customer_channel: true
      - notify_before_archive: 7天
```

---

## 输出示例

**请求**: "在 Slack 中设置交易成功通知"

**输出**:

```markdown
# 交易成功通知设置

## 工作流配置

```yaml
trigger: hubspot_deal阶段变更
condition: 新阶段 == "已关闭成功"

action:
  channel: "#胜利"
  message: see_below
```

## 消息模板

```
🎉 *交易成功！*

━━━━━━━━━━━━━━━━━━━━━━

🏢 *公司：* {公司名称}
💰 *金额：* ${交易金额}
👤 *销售代表：* @{所有者slack_id}
📦 *产品：* {产品线}

━━━━━━━━━━━━━━━━━━━━━━

*交易总结：*
• 销售周期：{管道天数} 天
• 领源：{领源}
• 行业：{行业}

🎊 团队恭喜！
```

## n8n 实现

```javascript
// HubSpot 触发器 → Slack 节点
{
  "nodes": [
    {
      "name": "HubSpot 触发器",
      "type": "n8n-nodes-base.hubspotTrigger",
      "parameters": {
        "eventsUi": {
          "eventValues": ["deal.propertyChange"]
        },
        "property": "dealstage",
        "value": "closedwon"
      }
    },
    {
      "name": "格式化消息",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "message": "🎉 *交易成功！*\n\n🏢 {{$json.company}}\n💰 ${{$json.amount}}"
        }
      }
    },
    {
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#胜利",
        "text": "={{$json.message}}"
      }
    }
  ]
}
```

## 示例输出

```
🎉 *交易成功！*

━━━━━━━━━━━━━━━━━━━━━━

🏢 *公司：* Acme Corporation
💰 *金额：* $45,000
👤 *销售代表：* @alice.chen
📦 *产品：* 企业计划

━━━━━━━━━━━━━━━━━━━━━━

*交易总结：*
• 销售周期：45 天
• 领源：入站 - 网站
• 行业：技术

🎊 团队恭喜！
```
```

---

*Slack 工作流技能 - 隶属于 Claude 办公技能*
