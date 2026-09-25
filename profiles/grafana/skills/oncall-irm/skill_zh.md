# Grafana OnCall & IRM

> **OnCall 文档**: https://grafana.com/docs/oncall/latest/
> **IRM 文档**: https://grafana.com/docs/grafana-cloud/alerting-and-irm/

> Grafana OnCall OSS 已进入维护模式（2026年3月归档）。云用户 → **IRM**。概念（链、计划、集成）完全相同。

## 前置条件

- 带有IRM/OnCall功能的Grafana Cloud堆栈
- API令牌（`Authorization: <token>`）
- Slack工作区 + 管理员权限以安装OnCall应用（用于ChatOps）

## 核心概念

| 概念 | 描述 |
|---------|-------------|
| **集成** | 接收告警的Webhook URL；每个源一个 |
| **路由** | 映射到告警升级链的Jinja2条件（第一个为True者生效） |
| **升级链** | 等待 / 通知计划 / 通知团队 / Webhook / 自动解决步骤 |
| **计划** | 基于日历的轮换（Web / iCal / Terraform） |
| **告警组** | 通过分组ID模板折叠的相关告警 |
| **通知策略** | 按用户分组的渠道 — Slack、移动推送、SMS、电话、邮件 |

流程：告警 → 集成 → 路由模板 → 升级链 → 通知 → 确认/解决。

## 常见工作流

### 1. 将Alertmanager线路连接到IRM并验证路由

```yaml
# 1. 在IRM中：新建集成 → Alertmanager。复制Webhook URL。
# 2. alertmanager.yml（参考references/integrations.md获取完整块）:
receivers:
  - name: grafana-oncall
    webhook_configs:
      - url: https://<stack>.grafana.net/integrations/v1/alertmanager/<id>/
        send_resolved: true
        max_alerts: 100
```

```bash
# 3. 在正式上线前测试路由模板（UI: 集成 → 路由 → "预览")
#    粘贴一个样本负载（使用真实的Alertmanager测试Webhook）。预期：
#      路由结果：True
#      选择的升级链：<预期链>
#    如果为False — 你的Jinja表达式有误；修复后重新预览。

# 4. 端到端测试 — 向URL发射amtool（或任何测试Webhook）
amtool alert add foo severity=critical team=platform --alertmanager.url http://localhost:9093

# 5. 在IRM → 告警组中验证（应在~5秒内出现） — 确认：
#    - 正确的路由被触发
#    - 正确的计划/用户被通知
#    - 配置的频道中出现了Slack消息
```

路由模板语法 + Jinja辅助函数：[`references/templates-schedules.md`](references/templates-schedules.md)。
其他集成（Grafana告警、通用Webhook、Slack）：[`references/integrations.md`](references/integrations.md)。

### 2. 构建升级链并验证

```
1. 通知"主要值班人员"（重要通知）
2. 等待5分钟
3. 通知"主要值班人员"（默认通知）
4. 等待10分钟
5. 通知团队"平台"
6. 触发外部Webhook（PagerDuty / 工单）
```

```bash
# 验证：创建一个测试告警（UI → 集成 → "发送演示告警"），
# 然后观察告警组时间线按步骤1 → 6推进。
# 如果可用，使用IRM → 升级链 → "测试"；否则，演示告警是标准的检查方式。
```

### 3. 从iCal创建计划并验证"现在谁在值班"

```bash
# 1. 创建计划
curl -X POST https://<stack>.grafana.net/api/v1/schedules/ \
  -H "Authorization: <token>" -H "Content-Type: application/json" \
  -d '{"name":"Platform On-Call",
       "ical_url_primary":"https://calendar.example.com/platform.ics",
       "slack":{"channel_id":"C123456ABC","user_group_id":"S123456ABC"}}'

# 2. 验证计划是否创建
curl -s https://<stack>.grafana.net/api/v1/schedules/ \
  -H "Authorization: <token>" | jq '.results[] | select(.name=="Platform On-Call")'

# 3. 验证现在谁在值班
curl -s https://<stack>.grafana.net/api/v1/schedules/<schedule_id>/next_shifts/ \
  -H "Authorization: <token>" | jq '.results[0]'
# 预期一个现在开始（或最近开始）且具有正确user_id的班次。
```

Terraform变体 + 班次块：[`references/templates-schedules.md`](references/templates-schedules.md)。

## 最佳实践

- 保持链≤4级，并有明确的最终步骤（Webhook到PagerDuty或自动解决）
- 始终在Alertmanager中设置`send_resolved: true`以便OnCall自动解决
- 在Alertmanager Webhook配置中使用`max_alerts: 100`
- 结合Slack + 移动推送以提高交付可靠性
- 将集成/计划分配给团队以实现RBAC

## 资源

- [OnCall API](https://grafana.com/docs/oncall/latest/oncall-api-reference/)
- [IRM文档](https://grafana.com/docs/grafana-cloud/alerting-and-irm/)
- [路由模板辅助函数](https://grafana.com/docs/oncall/latest/configure/jinja2-template-functions/)
