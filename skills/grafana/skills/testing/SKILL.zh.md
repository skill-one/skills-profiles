---
name: testing
description: 从 Grafana Cloud 探测、负载测试和监控前端。涵盖合成监控（HTTP / DNS / TCP / Ping / Traceroute / Multihttp / k6-browser 脚本化检查来自 20+ 全球探测器，`probe_success` + TLS 证书过期告警）、Grafana Cloud k6（跨 AWS 负载区分布式负载测试、场景、`http_req_duration` 阈值、通过 `grafana/k6-action` 的 CI 集成），以及使用 Faro Web SDK 的前端可观测性（RUM、核心网络指标、自定义事件、`pushError`、分布式追踪关联）。适用于从多个区域检查网站/API 健壮性、通过负载测试控制发布、监控 TLS 证书续期、为 React/Vue 应用添加监控、追踪核心网络指标，或将前端错误关联到后端追踪——即使用户说“我的登录流程正常吗？”、“监控我的 API”、“每分钟 ping 我们的端点”、“发布控制负载测试”、“浏览器性能监控”、“会话回放”或“RUM”而不提及合成监控/k6/Faro。
---

# Grafana Cloud 测试

> **文档**: https://grafana.com/docs/grafana-cloud/testing/

三大支柱：外部探测（合成监控）、负载测试（k6 Cloud）、真实用户监控（Faro）。

## 前置条件

- Grafana Cloud 堆栈
- 合成监控：SM 访问令牌（`sm:write`）
- k6 Cloud：一个 Grafana Cloud k6 令牌 + 项目ID
- Faro：一个 Faro 应用 + 来自 **前端可观察性 → 应用** 的写入令牌

## 常见工作流

### 1. 创建并验证合成 HTTP 检查

```bash
# 1. 创建检查（完整负载在 references/synthetic.md 中）
curl -X POST https://synthetic-monitoring-api.grafana.net/sm/checks \
  -H "Authorization: Bearer <sm-token>" -H "Content-Type: application/json" \
  -d '{"job":"website","target":"https://example.com","frequency":60000,"timeout":15000,
       "enabled":true,"probes":[1,5,10],
       "settings":{"http":{"method":"GET","validStatusCodes":[200]}}}'

# 2. 列出检查 — 确认其存在并已启用
curl -s https://synthetic-monitoring-api.grafana.net/sm/checks \
  -H "Authorization: Bearer <sm-token>" | jq '.[] | select(.job=="website")'

# 3. 验证 probe_success 到达（等待 ~60s 进行第一次运行）
#    在 Grafana Explore 的合成指标数据源上：
#      probe_success{job="website"}
#    期望从 `probes:[1,5,10]` 中的每个探测点返回 1。
#
# 回滚：DELETE /sm/checks/<id> 或设置 `"enabled": false`。
```

有关所有检查类型、PromQL 查询和告警规则的详细信息，请参阅 [`references/synthetic.md`](references/synthetic.md)。

### 2. 运行 k6 cloud 负载测试

```bash
# 1. 一次认证
k6 cloud login --token <grafana-cloud-k6-token>

# 2. 首先在本地验证脚本（冒烟运行，无云成本）
k6 run --vus 1 --duration 30s script.js

# 3. 在云端启动
k6 cloud script.js
# → 运行的 URL；阈值（p95<500ms，error<1%）决定通过/失败。

# 4. 在 CI 中验证 — 退出码 0 = 阈值通过，99 = 阈值失败。
echo $?
```

完整脚本 + 场景 + CI YAML：[`references/k6-and-faro.md`](references/k6-and-faro.md)。

### 3. 使用 Faro 仪器前端

```bash
# 1. 安装
npm install @grafana/faro-web-sdk @grafana/faro-web-tracing
```

```javascript
// 2. initializeFaro({ url, apiKey, app, instrumentations }) — 参见 references/k6-and-faro.md
// 3. 推送一个测试事件，以便我们有东西可以查找：
faro.api.pushEvent('faro_smoketest', { ts: Date.now().toString() });
```

```bash
# 4. 验证收集器是否接收（浏览器开发者工具 → 网络）
#    POST 到 /collect 应返回 202。如果 401 — apiKey 不匹配。

# 5. 在 Grafana 中验证
#    - 前端可观察性 → 你的应用 → 会话：应显示你的会话
#    - 在 Loki 上探索：`{kind="event"} |= "faro_smoketest"`
#    - 对于跟踪：在 Tempo 中按 `service.name="my-frontend"` 过滤
```

## 故障排除

- 合成检查卡在 `probe_success=0` → 检查 `probe_*_duration_seconds` 以查找失败的阶段；探测区域标签会告诉你哪个探测器出错
- k6 cloud 运行 "ABORTED_THRESHOLD" → 触发了某个阈值；检查运行页面以查看是哪个
- Faro 事件未到达 → 检查浏览器网络调用到 `/collect` 是否返回 202；常见原因是错误的 `apiKey` 或 `url`（必须与前端可观察性应用匹配）

## 参考

- 对于合成监控脚本（k6）和浏览器检查的深度编写（执行模型、断言、密钥、API/Terraform 负载）— 请参阅 [`synthetic-monitoring-checks`](../synthetic-monitoring-checks/SKILL.md) 技能
- [`references/synthetic.md`](references/synthetic.md) — 合成监控基础：检查类型、关键 PromQL 指标、告警规则
- [`references/synthetic-monitoring.md`](references/synthetic-monitoring.md) — 深入了解：完整的检查 CRUD API、探测选择、脚本（k6）检查、多步浏览器检查
- [`references/k6-and-faro.md`](references/k6-and-faro.md) — k6 cloud 脚本 + Faro Web SDK 初始化代码片段，用于端到端测试
- [`references/k6-cloud.md`](references/k6-cloud.md) — 深入了解：k6 cloud 配置（项目 + 负载区域 + 阈值）、CI 集成、运行分析

## 资源

- [合成监控文档](https://grafana.com/docs/grafana-cloud/testing/synthetic-monitoring/)
- [Grafana Cloud k6 文档](https://grafana.com/docs/grafana-cloud/testing/k6/)
- [Faro / 前端可观察性文档](https://grafana.com/docs/grafana-cloud/monitor-applications/frontend-observability/)
