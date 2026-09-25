# Prometheus 配置

Prometheus 设置、指标收集、抓取配置和记录规则的完整指南。

## 目的

配置 Prometheus 以实现基础设施和应用程序的全面指标收集、告警和监控。

## 使用场景

- 设置 Prometheus 监控
- 配置指标抓取
- 创建记录规则
- 设计告警规则
- 实现服务发现

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **为指标使用一致的命名**（前缀名称单位）
2. **设置适当的抓取间隔**（典型值为 15-60 秒）
3. **使用记录规则**处理昂贵的查询
4. **实现高可用性**（多个 Prometheus 实例）
5. **根据存储容量配置保留策略**
6. **使用重标记**进行指标清理
7. **监控 Prometheus 本身**
8. **为大型部署实现联邦**
9. **使用 Thanos/Cortex 实现长期存储**
10. **记录自定义指标**

## 故障排除

**检查抓取目标：**

```bash
curl http://localhost:9090/api/v1/targets
```

**检查配置：**

```bash
curl http://localhost:9090/api/v1/status/config
```

**测试查询：**

```bash
curl 'http://localhost:9090/api/v1/query?query=up'
```

## 相关技能

- `grafana-dashboards` - 用于可视化
- `slo-implementation` - 用于 SLO 监控
- `distributed-tracing` - 用于请求跟踪
