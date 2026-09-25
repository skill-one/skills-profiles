# 安全监控

全面的安全监控、威胁检测和事件响应自动化技能。

## 核心架构

### 安全监控堆栈

```
安全监控架构：
┌─────────────────────────────────────────────────────────┐
│                     数据源                         │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ 防火墙   │ 终端     │ 云       │ 网络     │ 应用程序  │
│ 日志     │ 日志     │ 日志     │ 流量     │ 日志       │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴─────┬──────┘
     │          │          │          │           │
     └──────────┴──────────┴────┬─────┴───────────┘
                                ▼
┌─────────────────────────────────────────────────────────┐
│                   日志聚合                        │
│              (SIEM / 安全数据湖)                 │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   检测引擎                       │
│  • 基于规则的检测    • 机器学习异常检测       │
│  • 关联规则       • 威胁情报        │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   响应与操作                      │
│  • 报警        • 自动化响应                 │
│  • 工单       • 隔离                        │
└─────────────────────────────────────────────────────────┘
```

## 检测规则

### 规则类别

```yaml
detection_rules:
  身份验证:
    - name: brute_force_login
      description: "多次失败的登录尝试"
      query: |
        event.type == "authentication" AND
        event.outcome == "failure" AND
        COUNT(*) > 5 WITHIN 5 minutes
        GROUP BY source.ip
      severity: 高
      actions:
        - create_alert
        - block_ip_temporarily
        
    - name: impossible_travel
      description: "来自地理位置遥远的登录"
      query: |
        event.type == "authentication" AND
        event.outcome == "success" AND
        geo_distance(prev_location, current_location) > 500km AND
        time_diff < 1 hour
      severity: 严重
      actions:
        - create_alert
        - require_mfa_verification
        - notify_user
        
  数据窃取:
    - name: large_data_transfer
      description: "异常的数据外发量"
      query: |
        event.type == "network" AND
        direction == "outbound" AND
        bytes_transferred > 100MB WITHIN 1 hour
        GROUP BY user.id
      severity: 中
      actions:
        - create_alert
        - capture_network_session
        
  恶意软件:
    - name: known_malware_hash
      description: "文件匹配已知恶意软件签名"
      query: |
        event.type == "file" AND
        file.hash.sha256 IN threat_intelligence.malware_hashes
      severity: 严重
      actions:
        - quarantine_file
        - isolate_endpoint
        - create_incident
```

### 关联规则

```yaml
correlation_rules:
  - name: lateral_movement_detection
    description: "检测潜在横向移动"
    events:
      - type: authentication_success
        from: internal_network
      - type: process_execution
        name: ["psexec", "wmic", "powershell"]
        within: 5_minutes
      - type: network_connection
        to: different_internal_host
        within: 10_minutes
    severity: 高
    
  - name: privilege_escalation_chain
    description: "检测权限提升尝试"
    events:
      - type: authentication
        account_type: standard_user
      - type: process_execution
        elevated: true
        within: 30_minutes
      - type: account_modification
        action: add_to_admin_group
        within: 1_hour
    severity: 严重
```

## 报警管理

### 报警配置

```yaml
alert_config:
  severity_levels:
    严重:
      response_time: 15_minutes
      notifications:
        - pagerduty: security_oncall
        - slack: "#security-critical"
        - email: security-team@company.com
      auto_escalation: 30_minutes
      
    高:
      response_time: 1_hour
      notifications:
        - slack: "#security-alerts"
        - email: security-team@company.com
        
    中:
      response_time: 4_hours
      notifications:
        - slack: "#security-alerts"
        
    低:
      response_time: 24_hours
      notifications:
        - ticket_only: true
        
  deduplication:
    enabled: true
    window: 1_hour
    key_fields:
      - rule_id
      - source.ip
      - destination.ip
```

### 报警模板

```yaml
alert_template:
  title: "[{{severity}}] {{rule_name}}"
  
  body: |
    ## 安全报警
    
    **规则:** {{rule_name}}
    **严重性:** {{severity}}
    **时间:** {{timestamp}}
    
    ### 详情
    - **源IP:** {{source.ip}}
    - **源用户:** {{user.name}}
    - **目标:** {{destination.ip}}
    - **操作:** {{event.action}}
    
    ### 上下文
    {{event_context}}
    
    ### 推荐操作
    {{#each recommended_actions}}
    - {{this}}
    {{/each}}
    
    ### 相关事件
    {{related_events_link}}
```

## 事件响应

### 事件工作流

```
事件响应工作流:
┌─────────────────┐
│    检测    │
│  (报警触发)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│     分流      │
│  - 验证     │
│  - 分类     │
│  - 优先级   │
└────────┬────────┘
         ▼
┌─────────────────┐
│   隔离   │
│  - 隔离      │
│  - 阻止        │
│  - 保留     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  调查  │
│  - 收集      │
│  - 分析      │
│  - 关联    │
└────────┬────────┘
         ▼
┌─────────────────┐
│   根除   │
│  - 移除       │
│  - 补丁        │
│  - 强化       │
└────────┬────────┘
         ▼
┌─────────────────┐
│    恢复    │
│  - 恢复      │
│  - 验证       │
│  - 监控      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  事后事件  │
│  - 文档     │
│  - 审查       │
│  - 改进      │
└─────────────────┘
```

### 演练自动化

```yaml
playbooks:
  - name: ransomware_response
    trigger:
      alert_type: ransomware_detected
    steps:
      - name: isolate_endpoint
        action: network_isolate
        target: "{{affected_host}}"
        
      - name: disable_account
        action: disable_ad_account
        target: "{{user.name}}"
        
      - name: preserve_evidence
        action: capture_memory_image
        target: "{{affected_host}}"
        
      - name: notify_stakeholders
        action: send_notification
        channels:
          - security_team
          - it_leadership
          - legal_if_needed
          
      - name: create_incident
        action: create_ticket
        priority: 严重
        template: ransomware_incident
        
  - name: phishing_response
    trigger:
      alert_type: phishing_reported
    steps:
      - name: analyze_email
        action: extract_iocs
        extract:
          - sender_address
          - urls
          - attachments
          
      - name: check_recipients
        action: query_email_logs
        find: all_recipients
        
      - name: block_sender
        action: add_to_blocklist
        target: "{{sender_address}}"
        
      - name: remove_emails
        action: delete_from_mailboxes
        target: all_recipients
```

## 合规监控

### 合规框架

```yaml
compliance_checks:
  pci_dss:
    - requirement: "10.2.1"
      description: "记录所有对持卡人数据的访问"
      query: |
        SELECT * FROM audit_logs
        WHERE data_classification = 'cardholder'
        AND timestamp > NOW() - INTERVAL '24 hours'
      expected: all_access_logged
      
    - requirement: "10.6.1"
      description: "每日审查日志"
      check: daily_log_review_completed
      
  hipaa:
    - requirement: "164.312(b)"
      description: "审计控制"
      checks:
        - audit_logging_enabled
        - log_retention_6_years
        - tamper_protection
        
  soc2:
    - control: "CC6.1"
      description: "逻辑访问安全"
      checks:
        - mfa_enabled
        - password_policy_enforced
        - access_reviews_quarterly
```

### 合规仪表盘

```
合规状态仪表盘
═══════════════════════════════════════

PCI-DSS:      ████████████░░░░ 92% ✓
HIPAA:        ██████████████░░ 98% ✓
SOC 2:        █████████████░░░░ 95% ✓
GDPR:         ████████████████ 100% ✓

按严重性分类的发现:
严重  ░░░░░░░░░░░░░░░░░ 0
高      ██░░░░░░░░░░░░░░ 3
中    ████░░░░░░░░░░░░ 8
低    ██████░░░░░░░░░ 15

即将到期的截止日期:
• 1月30日: 季度访问审查
• 2月15日: 渗透测试安排
• 2月28日: 年度审计准备
```

## 安全指标

### KPI 仪表盘

```
安全运营指标
═══════════════════════════════════════

检测:
MTTD (平均检测时间): 4.2小时
报警量: 每天1,234
真阳性率: 78%

响应:
MTTR (平均响应时间): 1.8小时
已解决事件: 每周23
SLA合规性: 96%

覆盖范围:
监控资产: 2,456/2,500 (98%)
日志源: 45个活跃
检测规则: 234个活跃

威胁态势:
阻止攻击: 每月12,456
漏洞: 89个开放
补丁合规性: 94%
```

### 报告

```yaml
reports:
  - name: daily_security_briefing
    schedule: "0 8 * * *"
    recipients: security_team
    sections:
      - overnight_alerts
      - active_incidents
      - threat_intelligence_updates
      
  - name: weekly_executive_summary
    schedule: "0 9 * * 1"
    recipients: leadership
    sections:
      - key_metrics
      - significant_incidents
      - risk_posture
      - recommendations
      
  - name: monthly_compliance_report
    schedule: "0 9 1 * *"
    recipients: compliance_team
    sections:
      - control_status
      - audit_findings
      - remediation_progress
```

## 最佳实践

1. **纵深防御**: 多层检测
2. **最小权限**: 最小化访问权限
3. **记录一切**: 完整的审计跟踪
4. **自动化响应**: 减少MTTR
5. **定期测试**: 验证控制
6. **威胁情报**: 保持信息
7. **事件演练**: 练习响应
8. **持续改进**: 从事件中学习
