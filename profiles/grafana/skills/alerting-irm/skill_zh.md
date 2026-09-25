# Grafana 告警与 IRM

> **文档**: https://grafana.com/docs/grafana/latest/alerting.md

## 常见工作流

### 端到端配置新告警

1. **创建联系点**（通知发送的目标）:
   ```bash
   curl -X POST https://grafana.example.com/api/v1/provisioning/contact-points \
     -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json' \
     -d @contact-points.json
   ```
   验证:
   ```bash
   curl https://grafana.example.com/api/v1/provisioning/contact-points \
     -H 'Authorization: Bearer <token>' | jq '.[].name'
   ```

2. **添加通知策略**（告警发送到何处）— 请参考下方 [§ 通知策略](#notification-policies) 的匹配器模式。

3. **编写告警规则** — 选择类型:
   - Grafana 管理的 → 参考 [references/alerting.md § Grafana 管理的告警规则](references/alerting.md#grafana-managed-alert-rule-yaml-provisioning)
   - Prometheus/Mimir 规则 → 参考 [references/alerting.md § Prometheus / Mimir 告警规则](references/alerting.md#prometheus--mimir-alert-rule-ruler)
   - Loki LogQL → 参考 [references/alerting.md § Loki 告警规则](references/alerting.md#loki-alert-rule-logql)

4. **上线前验证路由**:
   ```bash
   # 从规则的 UI 强制触发测试告警，然后检查 Alertmanager 的视图
   curl https://grafana.example.com/api/alertmanager/grafana/api/v2/alerts \
     -H 'Authorization: Bearer <token>' | jq '.[] | {alertname: .labels.alertname, receiver: .receivers}'
   ```
   预期的接收者应该出现。如果出现错误的接收者，请重新检查策略的匹配器。

### 将告警路由到 IRM / 当班人员

1. 在 IRM 中创建类型为 "Grafana 告警 webhook" 的集成 → 复制集成 URL
2. 在 Grafana 告警中添加 webhook 联系点指向该 URL（完整的 YAML 在 [references/irm.md § 路由](references/irm.md#routing-from-grafana-alerting-to-irm)）
3. 添加通知策略匹配器将正确的严重性路由到新的联系点
4. 验证: 触发测试告警；它应该在 ~30 秒内出现在 IRM 中。完整的调试步骤在 [references/irm.md § 验证 IRM 集成](references/irm.md#verifying-the-irm-integration)。

### 定义 SLO

1. 通过 UI 或 API 创建 SLO → Grafana 自动生成记录规则、仪表板和消耗率告警（生成的 YAML 在 [references/slo.md](references/slo.md)）
2. **使用多窗口消耗率告警**，而不是单窗口 — 参考 [references/slo.md § 多窗口消耗率告警](references/slo.md#multi-window-burn-rate-alerts-recommended) 了解为什么单窗口会在噪音上触发
3. 使用 [references/slo.md § 验证 SLO 配置](references/slo.md#validating-slo-config) 中的 4 步模式进行验证

## 联系点 (YAML 配置)

```yaml
# provisioning/alerting/contact_points.yaml
apiVersion: 1
contactPoints:
  - orgId: 1
    name: pagerduty-critical
    receivers:
      - uid: pd-receiver
        type: pagerduty
        settings:
          integrationKey: YOUR_PAGERDUTY_KEY
          severity: critical

  - orgId: 1
    name: slack-alerts
    receivers:
      - uid: slack-receiver
        type: slack
        settings:
          url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
          channel: '#alerts'
```

对于邮件、webhook、Teams、Telegram、OnCall 和其他接收者类型，请参考 [references/alerting.md § 联系点接收者类型](references/alerting.md#contact-point-receiver-types)。

## 通知策略

带标签匹配器的分层路由树:

```yaml
# provisioning/alerting/notification_policies.yaml
apiVersion: 1
policies:
  - orgId: 1
    receiver: default-receiver
    group_by: ['alertname', 'cluster', 'service']
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 12h
    routes:
      # 严重告警 → PagerDuty
      - receiver: pagerduty-critical
        matchers:
          - severity = critical
        group_wait: 10s
        repeat_interval: 4h

      # 平台团队 → Slack，但严重告警时静音
      - receiver: slack-alerts
        matchers:
          - team = platform
        routes:
          - receiver: pagerduty-critical
            matchers:
              - severity = critical

      # 其他全部 → 邮件
      - receiver: email-alerts
        matchers:
          - severity =~ "warning|info"
```

## 静默

对匹配的告警进行抑制而不停止评估:

```bash
curl -X POST https://grafana.example.com/api/alertmanager/grafana/api/v2/silences \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "matchers": [
      {"name": "alertname", "value": "HighErrorRate", "isRegex": false},
      {"name": "env", "value": "staging", "isRegex": false}
    ],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T02:00:00Z",
    "comment": "维护窗口",
    "createdBy": "admin"
  }'

# 验证是否创建成功
curl https://grafana.example.com/api/alertmanager/grafana/api/v2/silences \
  -H 'Authorization: Bearer <token>' | jq '.[] | select(.status.state == "active")'
```

## 告警规则状态

| 状态 | 描述 |
|-------|-------------|
| **正常** | 条件未满足 |
| **待处理** | 条件满足，等待 `for` 持续时间 |
| **触发** | 条件满足 `for` 持续时间 |
| **无数据** | 查询返回无数据 |
| **错误** | 查询/评估错误 |
| **恢复** | 曾触发，条件不再满足 |

## 配置目录布局

```
provisioning/alerting/
├── alert_rules.yaml          # 告警和记录规则
├── contact_points.yaml       # 通知目标
├── notification_policies.yaml  # 路由树
├── templates.yaml            # 消息模板
└── mute_timings.yaml         # 定期静音窗口
```

## API 配置（保持 UI 可编辑）

添加 `X-Disable-Provenance: true` 以在 API 配置后保持资源在 UI 中可编辑:

```bash
curl -X PUT https://grafana.example.com/api/v1/provisioning/policies \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Disable-Provenance: true' \
  -H 'Content-Type: application/json' \
  -d @policy.json

curl -X POST https://grafana.example.com/api/v1/provisioning/alert-rules \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Disable-Provenance: true' \
  -H 'Content-Type: application/json' \
  -d @rule.json
```

## 参考

- [`references/alerting.md`](references/alerting.md) — 完整告警规则 YAML（Grafana 管理的 / Prometheus / Loki）+ 通知模板
- [`references/slo.md`](references/slo.md) — 生成的 SLO 记录规则 + 多窗口消耗率告警模式 + 验证步骤
- [`references/irm.md`](references/irm.md) — IRM 功能，集成源，告警 → IRM 路由 + 验证 + 常见故障模式
