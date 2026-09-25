# 服务等级目标 (SLO)

在 Elastic Observability 中创建和管理 SLO。SLO 使用从 Elasticsearch 数据中计算出的服务等级指标 (SLI) 来跟踪服务性能，并对照可衡量的目标进行监控。

## 认证

SLO 操作通过 Kibana API 进行。可以使用 API 密钥或基本认证进行认证：

```bash
# API 密钥
curl -H "Authorization: ApiKey <base64-encoded-key>" -H "kbn-xsrf: true" <KIBANA_URL>/api/observability/slos

# 基本认证
curl -u "$KIBANA_USER:$KIBANA_PASSWORD" -H "kbn-xsrf: true" <KIBANA_URL>/api/observability/slos
```

对于非默认空间，请添加路径前缀：`/s/<space_id>/api/observability/slos`。

在所有 POST、PUT 和 DELETE 请求中包含 `kbn-xsrf: true`。

## SLI 类型

| 类型                    | API 值                      | 用例                                    |
| ----------------------- | ------------------------------ | ------------------------------------------- |
| 自定义 KQL              | `sli.kql.custom`               | 原始日志 — 使用 KQL 查询的 good/total 统计 |
| 自定义指标           | `sli.metric.custom`            | 指标字段 — 带聚合的方程式                |
| 时间片指标           | `sli.metric.timeslice`         | 指标字段 — 每片阈值检查                  |
| 直方图指标           | `sli.histogram.custom`         | 直方图字段 — 范围/值计数                |
| APM 延迟             | `sli.apm.transactionDuration`  | APM — 延迟阈值                          |
| APM 可用性        | `sli.apm.transactionErrorRate` | APM — 成功率                          |
| 合成器可用性        | `sli.synthetics.availability`  | 合成器监控器 — 运行时间百分比            |

## 指南

- `objective.target` 是一个介于 0 和 1 之间的十进制数（例如 `0.995` 表示 99.5%）。
- 时间片指标指标需要 `budgetingMethod: "timeslices"`。
- 更新 SLO 会重置底层转换 — 历史数据将被重新计算。
- 集群需要具有 `transform` 和 `ingest` 角色的节点。
- 当 SLO 卡住或索引映射更改后，使用 `POST .../slos/{id}/_reset`。
- 分组 SLO 为每个唯一值创建一个实例 — 避免高基数字段。
- 合成器 SLO 会根据监控器和位置自动分组；不要手动设置 `groupBy`。
- 燃烧率告警规则不会通过 API 自动创建 — 需要单独设置。

## 其他参考

有关官方文档，请参考以下资源：

### SLO 文档

- [服务等级目标 (SLO)](https://www.elastic.co/docs/solutions/observability/incident-management/service-level-objectives-slos)
  — 概念、SLI 类型、预算方法以及仪表板面板。
- [创建 SLO](https://www.elastic.co/docs/solutions/observability/incident-management/create-an-slo) — 在 Kibana UI 中创建 SLO 的分步指南。
- [查看和管理 SLO](https://www.elastic.co/docs/solutions/observability/incident-management/slo-management) — 搜索、过滤和管理现有 SLO。

### Kibana SLO API

- [创建 SLO](https://www.elastic.co/docs/api/doc/kibana/operation/operation-createsloop) — 包含所有 SLI 类型有效载荷的完整请求体模式。
- [获取 SLO](https://www.elastic.co/docs/api/doc/kibana/operation/operation-getsloop) |
  [更新](https://www.elastic.co/docs/api/doc/kibana/operation/operation-updatesloop) |
  [删除](https://www.elastic.co/docs/api/doc/kibana/operation/operation-deletesloop) |
  [重置](https://www.elastic.co/docs/api/doc/kibana/operation/operation-resetsloop)
- [启用](https://www.elastic.co/docs/api/doc/kibana/operation/operation-enablesloop) |
  [禁用](https://www.elastic.co/docs/api/doc/kibana/operation/operation-disablesloop) |
  [获取定义](https://www.elastic.co/docs/api/doc/kibana/operation/operation-getdefinitionsop)

### 故障排除和访问

- [故障排除 SLO](https://www.elastic.co/docs/troubleshoot/observability/troubleshoot-service-level-objectives-slos)
- [配置 SLO 访问](https://www.elastic.co/docs/solutions/observability/incident-management/configure-service-level-objective-slo-access)
- [创建 SLO 燃烧率规则](https://www.elastic.co/docs/solutions/observability/incident-management/create-an-slo-burn-rate-rule)
