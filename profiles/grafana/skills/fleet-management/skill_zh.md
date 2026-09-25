# Grafana Fleet Management + Alloy 配置

> **文档**: https://grafana.com/docs/grafana-cloud/send-data/fleet-management/

通过 OpAMP 将远程管道分发到 Alloy 收集器 — 一次编写，使用匹配器目标，热应用（无需重启）。

## 前置条件

- 启用了 Fleet Management 的 Grafana Cloud 堆栈
- 具有 Fleet Management 访问权限的 API 令牌 (`Authorization: Bearer <STACK_ID>:<TOKEN>`)
- 目标上安装了 Alloy ≥ 1.0（独立安装或通过 `grafana/alloy` Helm 图表）
- 本地安装 `alloy` CLI 用于 `alloy fmt` 语法验证

## 概念

- **收集器** — 具有唯一 ID 和属性的 Alloy 实例
- **管道** — 存储在 Fleet Management 中的命名 Alloy River 配置
- **匹配器** — 通过属性将管道映射到收集器的选择器
- **属性** — 收集器上的键/值标签 (`env`, `team`, `region`)

## 常见工作流

### 1. 编写、验证和部署管道

```bash
# 1. 将管道保存到本地文件（在远程发送前通过 lint 捕获拼写错误）
cat > pipeline.alloy <<'EOF'
prometheus.scrape "default" {
  targets    = []
  forward_to = [prometheus.remote_write.grafana_cloud.receiver]
  scrape_interval = "60s"
}

prometheus.remote_write "grafana_cloud" {
  endpoint {
    url = "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push"
    basic_auth {
      username = "<METRICS_USERNAME>"
      password = env("GRAFANA_CLOUD_API_KEY")
    }
  }
}
EOF

# 2. 在发送到 Fleet Management 之前本地验证语法
alloy fmt pipeline.alloy            # 原地重写或显示行号错误
alloy validate pipeline.alloy       # 完整的语义检查（较新的 Alloy 版本）

# 3. 通过 API 创建管道（参考 `references/api.md` 获取有效载荷模式）
BASE=https://fleet-management-prod-us-east-0.grafana.net
TOKEN=<STACK_ID>:<API_TOKEN>
PAYLOAD=$(jq -n --rawfile c pipeline.alloy '{
  name:"k8s-metrics", contents:$c,
  matchers:[{name:"env",value:"production",type:"EQUAL"}]
}')
curl -s -X POST "$BASE/pipeline.v1.PipelineService/CreatePipeline" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq

# 4. 验证是否已部署 — 每个目标收集器应在 1-2 次轮询内报告为 APPLIED
curl -s -X POST "$BASE/collector.v1.CollectorService/ListCollectors" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}' \
  | jq '.collectors[] | select(.attributes[]?.value=="production")
        | {name, remoteConfigStatus}'
# 预期每行：remoteConfigStatus == "REMOTE_CONFIG_STATUS_APPLIED"
```

### 2. 解决 `REMOTE_CONFIG_STATUS_FAILED` 收集器问题

```bash
# 1. 查找失败的收集器并显示错误消息
curl -s -X POST "$BASE/collector.v1.CollectorService/ListCollectors" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}' \
  | jq '.collectors[] | select(.remoteConfigStatus=="REMOTE_CONFIG_STATUS_FAILED")
        | {name, msg:.remoteConfigStatusMessage}'

# 2. 本地重新验证有问题的管道
alloy fmt pipeline.alloy

# 3. 直接检查 Alloy — 端口 12345 的 UI 显示每个组件的健康状态
#    http://<COLLECTOR_HOST>:12345 → 图表 / 组件 / 聚类选项卡
kubectl -n monitoring logs -l app.kubernetes.io.name=alloy --tail=100 | grep -iE 'remote|error'

# 4. 修复后重新推送，重新列出收集器并确认行变为 APPLIED。
```

错误消息解码表：[`references/api.md`](references/api.md)。

### 3. 使用引导块 onboard 新的 Alloy

引导 `remotecfg` 块是唯一需要的本地配置：

```alloy
remotecfg {
  url = "https://<FLEET_MANAGEMENT_HOST>"
  basic_auth { username = "<STACK_ID>"; password = env("GRAFANA_CLOUD_API_KEY") }
  poll_frequency = "1m"
  attributes = { "env" = env("ENVIRONMENT"), "team" = "platform" }
}
```

```bash
# 启动后验证
curl -s http://localhost:12345/api/v0/web/components \
  | jq '.[] | select(.id=="remotecfg") | {id, health:.health.state}'
# health.state == "healthy"
```

完整引导（独立安装 + Helm）+ Assistant 工具列表：[`references/bootstrap.md`](references/bootstrap.md)。

## 资源

- [Fleet Management 文档](https://grafana.com/docs/grafana-cloud/send-data/fleet-management/)
- [Alloy 组件](https://grafana.com/docs/alloy/latest/reference/components/)
- [OpAMP 规范](https://github.com/open-telemetry/opamp-spec)
