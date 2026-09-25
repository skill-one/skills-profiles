# DevOps自动化

自动化DevOps工作流，包括CI/CD流水线、监控、事件管理和基础设施操作。基于n8n的IT运维工作流模板。

## 概述

本技能涵盖：
- CI/CD流水线自动化
- 监控和告警
- 事件管理
- 基础设施自动化
- 部署工作流

---

## CI/CD自动化

### GitHub Actions集成

```yaml
workflow: "GitHub CI/CD通知"

triggers:
  - github_push
  - github_pull_request
  - github_workflow_run
  
on_push:
  action:
    - trigger_ci: if_main_branch
    - notify_slack:
        channel: "#部署"
        message: |
          📦 *新推送至{分支}*
          
          提交: `{commit_sha_short}`
          作者: {author}
          消息: {commit_message}
          
          [查看差异]({compare_url})

on_pr_opened:
  action:
    - notify_slack:
        channel: "#代码评审"
        message: |
          🔀 *新拉取请求*
          
          标题: {pr_title}
          作者: {author}
          分支: {head} → {base}
          
          [评审PR]({pr_url})
    - assign_reviewers: based_on_codeowners
    - run_ci_checks

on_workflow_complete:
  action:
    - notify_slack:
        message: |
          {status_emoji} *构建{status}*
          
          工作流: {workflow_name}
          分支: {branch}
          持续时间: {duration}
          
          {if_failed: [查看日志]({logs_url})}
```

### 部署流水线

```yaml
deployment_pipeline:
  阶段:
    build:
      触发: push_to_main
      步骤:
        - checkout_code
        - install_dependencies
        - run_tests
        - build_artifact
        - push_to_registry
        
    staging:
      触发: build_success
      步骤:
        - deploy_to_staging
        - run_integration_tests
        - notify_qa
        
    production:
      触发: manual_approval
      步骤:
        - create_backup
        - deploy_to_production
        - run_smoke_tests
        - notify_team
        
  回滚:
    触发: deployment_failed OR manual
    步骤:
      - revert_to_previous
      - notify_team
      - create_incident
```

---

## 监控与告警

### 告警路由

```yaml
alert_routing:
  来源:
    - prometheus
    - datadog
    - cloudwatch
    - new_relic
    
  严重程度级别:
    critical:
      响应时间: 5分钟
      渠道: [pagerduty, slack_urgent, sms]
      升级: 立即
      
    high:
      响应时间: 15分钟
      渠道: [slack_alerts, email]
      升级: 15分钟后
      
    medium:
      响应时间: 1小时
      渠道: [slack_alerts]
      
    low:
      响应时间: 24小时
      渠道: [slack_logging]
      
  路由规则:
    - if: service == "payments"
      team: payments_oncall
      严重程度提升: +1
      
    - if: service == "auth"
      team: security_oncall
      
    - default:
      team: platform_oncall
```

### 告警模板

```yaml
alert_templates:
  基础设施:
    cpu_high:
      标题: "🔥 高CPU使用率"
      正文: |
        服务器: {host}
        CPU: {cpu_percent}%
        持续时间: {duration}
        
        阈值: {threshold}%
        
        [查看仪表盘]({grafana_url})
        
    memory_critical:
      标题: "💾 临界内存"
      正文: |
        服务器: {host}
        内存: {memory_percent}%
        可用: {available_mb}MB
        
        [SSH到服务器]({ssh_link})
        
    disk_full:
      标题: "💿 磁盘空间临界"
      正文: |
        服务器: {host}
        磁盘: {disk_percent}%
        可用: {available_gb}GB
        
        建议: 清理日志或扩展卷
        
  应用:
    error_spike:
      标题: "📈 错误率激增"
      正文: |
        服务: {service}
        错误率: {error_rate}%
        正常: {baseline}%
        
        顶部错误:
        {top_errors}
        
    latency_high:
      标题: "🐢 高延迟"
      正文: |
        服务: {service}
        P99延迟: {p99_ms}ms
        阈值: {threshold_ms}ms
```

---

## 事件管理

### 事件工作流

```yaml
incident_workflow:
  检测:
    来源: [monitoring, user_report, automated_check]
    
  初步处理:
    自动严重程度:
      - if: affects_payments
        严重程度: critical
      - if: affects_auth
        严重程度: critical
      - if: affects_api AND error_rate > 10%
        严重程度: high
        
  响应:
    critical:
      - create_incident_channel: "#inc-{timestamp}"
      - page_oncall: immediately
      - notify_stakeholders: [engineering_lead, product]
      - start_war_room: zoom_link
      - create_status_page: incident
      
    high:
      - create_incident_channel
      - notify_oncall: slack
      - create_ticket: jira
      
  沟通:
    内部:
      频率: 每30分钟
      渠道: incident_channel
      模板: |
        📊 *事件更新*
        
        状态: {status}
        影响: {impact}
        下次更新: {next_update_time}
        
        当前操作:
        {action_items}
        
    外部:
      渠道: status_page
      模板: 客户面对更新
      
  解决:
    步骤:
      - confirm_resolution
      - update_status_page: resolved
      - notify_stakeholders
      - schedule_postmortem
      - close_incident_channel: after_24h
```

### 事后分析模板

```yaml
postmortem_template:
  部分:
    summary:
      - incident_title
      - duration
      - 严重程度
      - 影响
      
    时间线:
      格式: |
        | 时间 | 事件 |
        |------|-------|
        | {time} | {event} |
        
    根本原因:
      - what_happened
      - why_it_happened
      - contributing_factors
      
    影响:
      - users_affected
      - revenue_impact
      - sla_breach
      
    解决:
      - how_it_was_fixed
      - time_to_detect
      - time_to_resolve
      
    行动项:
      格式: |
        | 行动 | 负责人 | 截止日期 | 状态 |
        |--------|-------|----------|--------|
        
    学到的教训:
      - what_went_well
      - what_went_poorly
      - lucky_breaks
```

---

## 基础设施自动化

### 服务器配置

```yaml
provisioning_workflow:
  触发: jira_ticket OR slack_request
  
  步骤:
    1. validate_request:
        检查: [budget_approval, security_review]
        
    2. create_infrastructure:
        terraform:
          - vpc
          - security_groups
          - ec2_instances
          - load_balancer
          
    3. configure_server:
        ansible:
          - base_configuration
          - security_hardening
          - monitoring_agent
          - application_setup
          
    4. validate:
        - health_check
        - security_scan
        - performance_baseline
        
    5. notify:
        slack: "✅ 服务器 {hostname} 已准备就绪"
        include: [ssh_access, dashboard_link]
```

### 定时维护

```yaml
maintenance_automation:
  任务:
    certificate_renewal:
      时间表: "到期前30天"
      操作:
        - request_new_cert: letsencrypt
        - deploy_cert
        - verify_ssl
        - notify: if_failure
        
    security_patching:
      时间表: "每周"
      操作:
        - check_updates
        - if_critical: immediate_patch
        - else: schedule_maintenance_window
        
    log_rotation:
      时间表: "每天"
      操作:
        - rotate_logs
        - compress_old
        - upload_to_s3
        - delete_local: older_than_7_days
        
    backup_verification:
      时间表: "每周"
      操作:
        - restore_to_test_env
        - run_integrity_checks
        - report_status
```

---

## Kubernetes自动化

### K8s工作流

```yaml
kubernetes_automation:
  部署:
    触发: docker_image_pushed
    步骤:
      - update_manifest: with_new_image_tag
      - apply_to_staging
      - run_tests
      - if_success: apply_to_production
      
  扩缩容:
    触发: metric_threshold
    规则:
      - if: cpu > 80%
        action: scale_up
        max_replicas: 10
      - if: cpu < 20%
        action: scale_down
        min_replicas: 2
        
  回滚:
    触发: health_check_failed
    操作:
      - kubectl_rollout_undo
      - notify_team
      - create_incident
```

---

## 输出示例

**请求**: "为GitHub Actions设置部署通知"

**输出**:

```markdown
# GitHub Actions部署通知

## n8n工作流

```yaml
trigger: GitHub Webhook
events: [workflow_run]
```

## 通知模板

**构建开始**:
```
🚀 *部署开始*

分支: main
提交: abc1234
作者: @developer
触发: 推送

[查看工作流](https://github.com/...)
```

**构建成功**:
```
✅ *部署成功*

环境: 生产
持续时间: 3m 42s
版本: v1.2.3

变更:
• 功能X
• 缺陷修复Y

[查看部署](https://app.example.com)
```

**构建失败**:
```
❌ *部署失败*

阶段: 测试
错误: npm test失败

[查看日志](https://github.com/...)
[重试](https://github.com/...)
```

## Slack集成

```yaml
channel: "#部署"
mention_on_failure: "@oncall"
thread_replies: true
```
```

---

*DevOps自动化技能 - 部分Claude办公技能*
