# Qdrant 监控

先路由，再回答。在表格中匹配用户的症状，`读取`该文件，并从中回答。
不要仅从本页面回答：它只包含路由信息，不包含指导。如果两行都匹配，则读取两行。

| 用户说 | 读取 |
|---|---|
| 想要设置 Prometheus、Grafana 或健康检查 | `setup/SKILL.md` |
| 需要知道要跟踪哪些指标 | `setup/SKILL.md` |
| 设置告警、日志集中或混合云指标 | `setup/SKILL.md` |
| 优化器卡住或运行无限期 | `debugging/SKILL.md` |
| 生产环境中的内存持续增长 | `debugging/SKILL.md` |
| 请求缓慢，需要找出原因 | `debugging/SKILL.md` |
| Qdrant 目前是否健康 | `debugging/SKILL.md` |

Qdrant 监控跟踪性能和健康状态，并在问题成为停机事件之前捕获问题。在调整任何内容之前，请先查看指标参考：
[监控文档](https://skills.qdrant.tech/md/documentation/ops-monitoring/monitoring/)
