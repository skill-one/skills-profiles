# Trello 自动化

全面的技能，用于自动化 Trello 板管理和看板工作流。

## 核心概念

### 板结构

```
TRELLO 板解剖结构：
┌─────────────────────────────────────────────────────────┐
│ 📋 项目板                                        │
├───────────┬───────────┬───────────┬───────────┬────────┤
│  待办事项  │   待办   │   进行中   │  审核中   │  已完成  │
├───────────┼───────────┼───────────┼───────────┼────────┤
│ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │        │
│ │卡片 1 │ │ │卡片 3 │ │ │卡片 5 │ │ │卡片 7 │ │        │
│ │标签   │ │ │@Mike  │ │ │@Sarah │ │ │@Lisa  │ │        │
│ │截止日期 │ │ │截止日期:3天 │ │ │       │ │ │       │ │
│ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │        │
│ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │           │        │
│ │卡片 2 │ │ │卡片 4 │ │ │卡片 6 │ │           │        │
│ └───────┘ │ └───────┘ │ └───────┘ │           │        │
└───────────┴───────────┴───────────┴───────────┴────────┘
```

### 卡片组件

```yaml
卡片结构:
  title: "{{task_name}}"
  description: "{{detailed_description}}"
  
  元数据:
    标签:
      - name: "Bug"
        color: red
      - name: "功能"
        color: green
      - name: "紧急"
        color: orange
        
    成员: ["@member1", "@member2"]
    截止日期: "2024-01-20"
    开始日期: "2024-01-15"
    
  附件:
    - type: file
      url: "{{attachment_url}}"
    - type: link
      url: "{{external_link}}"
      
  复查清单:
    - name: "验收标准"
      items:
        - "需求 1"
        - "需求 2"
        - "需求 3"
        
  自定义字段:
    story_points: 5
    sprint: "Sprint 15"
```

## Butler 自动化

### 自动化规则

```yaml
butler_rules:
  - name: 移动到进行中时自动分配
    trigger:
      type: card_moved_to_list
      list: "进行中"
    action:
      - join_card
      - set_due_date: "+3 days"
      - add_label: "进行中"
      
  - name: 截止日期提醒
    trigger:
      type: due_date_approaching
      days: 1
    action:
      - post_comment: "@card 提醒: 明天截止!"
      - move_to_list: "紧急"
      
  - name: 完成清理
    trigger:
      type: card_moved_to_list
      list: "已完成"
    action:
      - mark_due_complete
      - remove_all_members
      - add_label: "已完成"
      
  - name: 定时归档
    trigger:
      type: schedule
      frequency: 每周
      day: 星期日
    action:
      - archive_cards_in_list: "已完成"
      - older_than: 7_days
```

### 按钮命令

```yaml
card_buttons:
  - name: "开始工作"
    actions:
      - move_to_list: "进行中"
      - join_card
      - set_due_date: "+3 days"
      - remove_label: "待办事项"
      - add_label: "进行中"
      
  - name: "提交审核"
    actions:
      - move_to_list: "审核中"
      - add_checklist:
          name: "审核清单"
          items:
            - "代码已审核"
            - "测试通过"
            - "文档已更新"
      - mention: "@reviewer"
      
  - name: "标记完成"
    actions:
      - check_all_items
      - move_to_list: "已完成"
      - mark_due_complete
      - post_comment: "✅ 已完成!"
```

## 板模板

### Sprint 板

```yaml
sprint_board_template:
  name: "Sprint {{number}}"
  
  列表:
    - name: "Sprint 待办事项"
      position: 1
    - name: "待办"
      position: 2
    - name: "进行中"
      position: 3
      wip_limit: 5
    - name: "代码审核"
      position: 4
      wip_limit: 3
    - name: "测试"
      position: 5
    - name: "已完成"
      position: 6
      
  标签:
    - name: "Bug"
      color: red
    - name: "功能"
      color: green
    - name: "技术债务"
      color: 黄色
    - name: "阻塞"
      color: 紫色
      
  自定义字段:
    - name: "故事点"
      type: number
    - name: "优先级"
      type: 下拉菜单
      options: ["高", "中", "低"]
```

### 内容日历

```yaml
content_calendar_template:
  name: "内容日历 - {{month}}"
  
  列表:
    - name: "想法"
    - name: "计划"
    - name: "写作"
    - name: "编辑"
    - name: "已计划"
    - name: "已发布"
    
  标签:
    - name: "博客"
      color: 蓝色
    - name: "社交"
      color: 粉色
    - name: "视频"
      color: 紫色
    - name: "简报"
      color: 绿色
      
  卡片模板:
    name: "{{content_title}}"
    description: |
      **主题:** {{topic}}
      **目标受众:** {{audience}}
      **关键词:** {{keywords}}
      **发布日期:** {{date}}
    复查清单:
      - name: "内容工作流"
        items:
          - "研究完成"
          - "大纲已批准"
          - "初稿"
          - "编辑通过"
          - "图形准备"
          - "SEO 优化"
          - "已计划"
```

## 工作流自动化

### 卡片移动规则

```yaml
workflow_rules:
  to_do:
    entry_actions:
      - require_due_date
      - require_labels
    exit_requirements:
      - has_assignee
      
  in_progress:
    entry_actions:
      - start_timer
      - add_comment: "工作已开始"
    constraints:
      wip_limit: 3
      
  review:
    entry_actions:
      - notify_reviewers
      - add_checklist: review_checklist
    exit_requirements:
      - all_checklist_complete
      
  done:
    entry_actions:
      - stop_timer
      - calculate_cycle_time
      - notify_stakeholders
```

### 复查清单模板

```yaml
checklist_templates:
  bug_fix:
    name: "Bug 修复清单"
    items:
      - "复现 Bug"
      - "识别根本原因"
      - "编写修复"
      - "添加测试"
      - "本地测试"
      - "代码审核"
      - "部署到预发布环境"
      - "验证修复"
      
  feature:
    name: "功能清单"
    items:
      - "需求已记录"
      - "设计已批准"
      - "实现完成"
      - "单元测试已编写"
      - "集成测试"
      - "文档已更新"
      - "演示已准备"
```

## Power-Up 集成

### 热门 Power-Up

```yaml
power_ups:
  calendar:
    description: "可视化带截止日期的卡片"
    view: calendar
    sync: true
    
  custom_fields:
    fields:
      - name: "优先级"
        type: 下拉菜单
      - name: "估算"
        type: number
      - name: "客户"
        type: 文本
        
  card_aging:
    enable: true
    mode: regular  # 或 pirate mode
    
  voting:
    enable: true
    one_vote_per_member: true
```

### Slack 集成

```yaml
slack_integration:
  通知:
    - trigger: card_created
      channel: "#项目更新"
      
    - trigger: card_moved_to
      list: "已完成"
      channel: "#胜利"
      
    - trigger: comment_added
      notify: card_members
      
  命令:
    /trello:
      - add_card
      - search_cards
      - my_cards
```

## 报告与分析

### 板指标

```
板分析 - Sprint 15
═══════════════════════════════════════

卡片:
总数:        45
已完成:    28 (62%)
进行中:  12
阻塞:      2

速度:
本次 Sprint:  28 张卡片
平均:      25 张卡片
趋势:        +12%

周期时间:
平均:      3.2 天
最短:     0.5 天
最长:      8 天

按标签:
功能    █████████████░░░░ 18
Bug        ████████░░░░░░░░ 12
技术债务  █████░░░░░░░░░░░ 8
其他      ███░░░░░░░░░░░░░ 7

按成员:
Sarah     ████████████░░░ 15
Mike      ██████████░░░░░ 12
Lisa      ████████░░░░░░ 10
Alex      ██████░░░░░░░░ 8
```

### 燃尽图

```
Sprint 燃尽图
│ 45 ┤ ▪
│    │  ▪▪
│    │    ▪▪ ← 理想
│    │      ▪▪
│ 22 ┤        ●●
│    │          ●● ← 实际
│    │            ▪▪●●
│    │              ▪▪●●
│  0 ┤                ▪▪●●
└────┴────────────────────────
     第 1 天              第 14 天

按计划: ✓ 2 张卡片提前完成
```

## API 示例

### 创建卡片

```javascript
// 创建带完整详情的卡片
const card = await trello.cards.create({
  name: "实现用户认证",
  desc: "添加 Google 和 GitHub 的 OAuth2 支持",
  idList: "list_id",
  idLabels: ["label_id_1", "label_id_2"],
  idMembers: ["member_id"],
  due: "2024-01-20T17:00:00.000Z",
  pos: "top"
});

// 添加复查清单
await trello.cards.createChecklist(card.id, {
  name: "实现任务"
});

// 添加复查清单项
await trello.checklists.createCheckItem(checklistId, {
  name: "设置 OAuth 提供商",
  checked: false
});
```

### 移动卡片

```javascript
// 移动卡片到不同列表
await trello.cards.update(cardId, {
  idList: "new_list_id",
  pos: "bottom"
});

// 添加评论
await trello.cards.createComment(cardId, {
  text: "移动到审核。@reviewer 请检查。"
});
```

## 最佳实践

1. **简单列表**: 最多 5-7 个列表
2. **清晰标签**: 一致的色彩编码
3. **截止日期**: 设置现实的截止日期
4. **WIP 限制**: 防止瓶颈
5. **定期清理**: 归档已完成的卡片
6. **复查清单**: 将复杂任务分解
7. **Butler 规则**: 自动化重复操作
8. **板模板**: 标准化工作流
