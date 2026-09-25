# Grafana OSS

> **文档**: https://grafana.com/docs/grafana/latest.md

## 常见工作流程

### 从磁盘创建仪表板

1. 将仪表板 JSON 文件放置在 `/var/lib/grafana/dashboards/` 下
2. 在 `provisioning/dashboards/default.yaml` 中添加一个提供者（参见下文的 [§ 仪表板创建](#dashboard-provisioning)）
3. 重启 Grafana 以加载提供者配置
4. **验证仪表板是否已创建**:
   ```bash
   curl https://grafana.example.com/api/dashboards/uid/<uid> \
     -H "Authorization: Bearer <token>" | jq '.dashboard.title'
   ```
   返回标题 → 成功。404 → 创建未成功；检查 Grafana 服务器日志 (`journalctl -u grafana-server | grep -i provisioning`) 以查找解析错误。

### 创建数据源

1. 编写 `provisioning/datasources/datasources.yaml`（参见下文的 [§ 数据源创建](#data-source-provisioning)）
2. 重启 Grafana
3. **通过 API 检查数据源健康状况**:
   ```bash
   curl https://grafana.example.com/api/datasources/uid/<uid>/health \
     -H "Authorization: Bearer <token>"
   # { "status": "OK", "message": "..." } → 正常工作
   # { "status": "ERROR", ... } → URL 不可达或认证配置错误
   ```

### 创建服务账户 + 令牌

1. 通过 YAML 或 `POST /api/serviceaccounts` 创建（完整 API 参见 [参考资料/api.md § 用户 + 服务账户](references/api.md#users--service-accounts)）
2. 通过 `POST /api/serviceaccounts/{id}/tokens` 生成令牌
3. **验证令牌是否有效**:
   ```bash
   curl https://grafana.example.com/api/org \
     -H "Authorization: Bearer <new-token>"
   # 200 + org JSON → 令牌 + 角色分配正常
   # 401 → 令牌错误；403 → 角色错误
   ```

## 仪表板创建

```yaml
# provisioning/dashboards/default.yaml
apiVersion: 1
providers:
  - name: default
    folder: MyFolder
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

仪表板 JSON 结构本身（面板、查询、模板变量）参见 [参考资料/dashboard-json.md](references/dashboard-json.md)。

## 数据源创建

```yaml
# provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 15s
      httpMethod: POST

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100

  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki_uid
        tags: [{ key: "service.name", value: "app" }]
      serviceMap:
        datasourceUid: prometheus_uid
      nodeGraph:
        enabled: true

  - name: Pyroscope
    type: grafana-pyroscope-datasource
    url: http://pyroscope:4040
```

## RBAC (内置角色)

| 角色 | 权限 |
|------|-------------|
| **Viewer** | 读取仪表板、告警 |
| **Editor** | 创建/编辑仪表板、告警 |
| **Admin** | 管理数据源、用户、插件 |
| **GrafanaAdmin** | 全局管理员（超级用户） |

服务账户创建:

```yaml
# provisioning/access-control/service_accounts.yaml
apiVersion: 1
serviceAccounts:
  - name: ci-reader
    orgId: 1
    role: Viewer
    tokens:
      - name: ci-token
        # expires: 可选的 ISO 8601 时间戳；省略表示无过期令牌
```

(自定义 RBAC 角色具有细粒度权限仅限 Enterprise / Cloud — 如需这些功能，请参考 `grafana-cloud/admin` 技能。)

## 插件创建

```yaml
# provisioning/plugins/plugins.yaml
apiVersion: 1
apps:
  - type: grafana-pyroscope-app
    disabled: false
    jsonData:
      backendUrl: http://pyroscope:4040
```

重启后，通过 `GET /api/plugins/<plugin-id>/health` 验证。

## 参考资料

- [`references/dashboard-json.md`](references/dashboard-json.md) — 完整仪表板 JSON 模型 + 模板变量 + 常见问题（uid 唯一性、gridPos 运算、数据源 uid 匹配）
- [`references/dashboards.md`](references/dashboards.md) — 仪表板工作流程、设置、变量、注释、共享、版本、播放列表和代码化创建
- [`references/datasources.md`](references/datasources.md) — Prometheus、Loki、Tempo、SQL、CloudWatch 和插件的设置和查询示例
- [`references/panel-types.md`](references/panel-types.md) — 面板类型表格 + 选择合适面板的决策指南
- [`references/panels.md`](references/panels.md) — 面板编辑器、可视化选项、字段配置、转换、查询选项、检查和性能技巧
- [`references/alerting.md`](references/alerting.md) — 告警概念、联系点、通知策略、模板、静默和常见规则示例
- [`references/api.md`](references/api.md) — 完整 Grafana OSS API 参考资料（仪表板、数据源、用户、服务账户、注释）包含验证 curl 和常见错误模式
- [`references/config.md`](references/config.md) — `grafana.ini` 服务器/数据库/SMTP/认证/安全/功能开关配置 + 重启相关问题
