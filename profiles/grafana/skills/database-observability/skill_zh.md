# Grafana Cloud 数据库可观测性

> **文档**: https://grafana.com/docs/grafana-cloud/monitor-applications/database-observability/

无需修改应用代码即可获取 MySQL 和 PostgreSQL 的查询级洞察（RED 指标、查询样本、执行计划）。自 2026 年 4 月起提供 GA 功能。

## 常见工作流

### PostgreSQL 设置

```sql
-- 1. 启用 pg_stat_statements（需要重启）
--    在 postgresql.conf 中：shared_preload_libraries = 'pg_stat_statements'
--    然后重启 PostgreSQL。

-- 2. 创建最小权限的监控用户
CREATE USER grafana_monitoring WITH PASSWORD 'secret';
GRANT pg_monitor TO grafana_monitoring;
GRANT CONNECT ON DATABASE mydb TO grafana_monitoring;

-- 3. 在每个被监控的数据库上启用扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 4. 验证
SELECT count(*) FROM pg_stat_statements;
-- 应返回 >= 0（不是错误）。如果 "relation does not exist"：步骤 3 未执行。
```

5. 添加 [来自 references/alloy-config.md § PostgreSQL 的 Alloy 配置块](references/alloy-config.md#postgresql)
6. 重启 Alloy 并等待约 60 秒进行首次抓取
7. **在 Grafana Cloud 中验证** → 数据库可观测性 — 实例应显示非空的 `db_query_total{db_instance="mydb"}` 系列。如果 2 分钟后为空：检查 Alloy 日志中的连接错误，然后重新验证 pg_stat_statements 权限。

### MySQL 设置

```sql
-- 1. 创建最小权限的监控用户
CREATE USER 'grafana_monitoring'@'%' IDENTIFIED BY 'secret';
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO 'grafana_monitoring'@'%';
GRANT SELECT ON performance_schema.* TO 'grafana_monitoring'@'%';
FLUSH PRIVILEGES;

-- 2. 验证 performance_schema 是否启用（MySQL 8+ 的默认设置）
SELECT @@performance_schema;
-- 返回 1 → 已启用。0 → 在 my.cnf 中设置 performance_schema=ON 并重启。
```

3. 添加 [来自 references/alloy-config.md § MySQL 的 Alloy 配置块](references/alloy-config.md#mysql)
4. 重启 Alloy，等待约 60 秒，验证实例在 Grafana Cloud → 数据库可观测性 中出现

## 支持的数据库

| 数据库 | 变体 |
|----------|---------|
| **MySQL** | 自托管、RDS MySQL、Aurora MySQL、Cloud SQL MySQL、Azure Database for MySQL |
| **PostgreSQL** | 自托管、RDS PostgreSQL、Aurora PostgreSQL、Cloud SQL PostgreSQL、Azure Database for PostgreSQL |

对于托管数据库（RDS / Cloud SQL / Azure），`pg_stat_statements` 已预装但被禁用 — 通过参数组/标志启用它，然后在数据库级别重新创建扩展。

## 您将获得

- **查询性能仪表板**（自动配置）：按总时间/调用次数/平均延迟排序的顶级查询，带参数的采样查询文本，可视化执行计划，每个查询摘要的 RED 指标
- **APM 关联**：通过 `db.statement` / `db.system` / `db.name` OTel 属性从慢服务延迟段钻取到特定慢 SQL — 查看 [references/queries-alerts.md § 跟踪关联](references/queries-alerts.md#trace-correlation)
- **告警**：针对查询延迟、错误率和连接池饱和 — 完整告警 YAML 在 [references/queries-alerts.md § 告警规则](references/queries-alerts.md#alert-rules)

## 参考

- [`references/alloy-config.md`](references/alloy-config.md) — 完整 Alloy `database_observability.postgres` / `database_observability.mysql` 配置块 + 收集器参考（`pg_stat_statements`，`query_samples`，`schema_details`，`explain_plans`）
- [`references/queries-alerts.md`](references/queries-alerts.md) — 关键 PromQL 查询、告警规则 YAML 和跟踪关联设置
