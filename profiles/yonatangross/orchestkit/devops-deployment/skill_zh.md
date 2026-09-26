# DevOps & 部署技能

CI/CD 管道、容器化、部署策略和基础设施自动化的全面框架。

> **注意：** 如果 `disableSkillShellExecution` 被启用（CC 2.1.91），Docker 安装检查将不会运行。验证 Docker 是否可用于容器操作：`docker --version`。

## 概述

- 设置 CI/CD 管道
- 应用程序容器化
- 部署到 Kubernetes 或云平台
- 实施 GitOps 工作流
- 将基础设施作为代码进行管理
- 规划发布策略

## 管道架构

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 代码     │─>│ 构建    │─>│ 测试     │─>│ 部署   │
│ 提交     │ │ 代码检查 │ │ 扫描     │ │ 发布  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
  触发器     产物    报告      监控
```

## 关键概念

### CI/CD 管道阶段

1. **代码检查 & 类型检查** - 代码质量门禁
2. **单元测试** - 带报告的测试覆盖率
3. **安全扫描** - npm audit + Trivy 漏洞扫描器
4. **构建 & 推送** - Docker 镜像到容器注册中心
5. **部署到预发布环境** - 环境门禁部署
6. **部署到生产环境** - 手动批准或自动

### 容器最佳实践

**多阶段构建** 最小化镜像大小：
- 阶段 1：仅安装生产依赖
- 阶段 2：使用开发依赖构建应用程序
- 阶段 3：生产运行时，最小占用

**安全加固**：
- 非根用户（uid 1001）
- 尽可能使用只读文件系统
- 健康检查用于编排器集成

### Kubernetes 部署

**核心清单**：
- 带滚动更新策略的部署
- 用于内部路由的服务
- 带 TLS 的外部访问的 Ingress
- 水平 Pod 自动缩放器用于缩放

**安全上下文**：
- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- 放弃所有能力

### 部署策略

| 策略 | 用例 | 风险 |
|------|------|------|
| **滚动** | 默认，渐进式替换 | 低 - 自动回滚 |
| **蓝绿** | 瞬间切换，轻松回滚 | 中等 - 双倍资源 |
| **金丝雀** | 逐步流量转移 | 低 - 渐进式暴露 |

**滚动更新**（Kubernetes 默认）：
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0  # 零停机时间
```

### 密钥管理

使用 External Secrets Operator 从云提供商同步：
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- GCP Secret Manager

---

## 参考

### Docker 模式
**加载：`Read("references/docker-patterns.md")`**

涵盖的关键主题：
- 多阶段构建示例，大小减少 78%
- 层缓存优化
- 安全加固（非根，健康检查）
- Trivy 漏洞扫描
- Docker Compose 开发设置

### OrchestKit Delta（内部规则）
**加载：`Read("references/ork-delta.md")`**

涵盖的关键主题：
- CI 并发组，小于 5 分钟的反馈预算，路径过滤
- 服务容器健康门禁，SHA 固定的部署，CDN 无效化顺序
- Kubernetes 探针预算，请求/限制基线，PodDisruptionBudget 底线
- External Secrets 刷新间隔，ArgoCD 剪枝加自愈，Terraform 状态锁定
- 告警阈值带停留窗口，请求 ID 日志绑定，回滚演练

### 铁路部署
**加载：`Read("rules/railway-deployment.md")`**

涵盖的关键主题：
- railway.json 配置，Nixpacks 构建
- 环境变量管理，数据库配置
- 多服务设置，Railway CLI 工作流
- 参考：`references/railway-json-config.md`，`references/nixpacks-customization.md`，`references/multi-service-setup.md`

### 部署策略
**加载：`Read("references/deployment-strategies.md")`**

涵盖的关键主题：
- 滚动部署（`maxUnavailable` / `maxSurge`）
- 蓝绿部署（服务选择器切换和回滚）
- 金丝雀发布（副本比率流量分割）

---

## 上游覆盖（不要重复陈述）

此技能封装了第三方产品。供应商机制在此不重复陈述；从下方来源获取。如果某行说“OrchestKit 的子集保留在 X 中”，则该文件仅保留 OrchestKit 的阈值、配置或排序决策，而不是供应商教程。

| 主题 | 从中获取 |
|------|--------|
| GitHub Actions 工作流语法，矩阵构建，产物上传/下载，缓存机制 | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax (OrchestKit 的缓存键子集保留在 `rules/devops-ci-caching.md`) |
| 触发器过滤器（`on.push.paths`，计划，`workflow_dispatch`） | https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow |
| 集成测试的服务容器 | https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers |
| 部署环境和批准门禁 | https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments |
| 受保护的分支和必需的状态检查 | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches (OrchestKit 的批准计数保留在 `rules/devops-branch-protection.md`) |
| Kubernetes 探针语义和每个探针字段 | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ (OrchestKit 的探针数字保留在 `references/ork-delta.md`) |
| 请求，限制，配额和 QoS 类 | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ (OrchestKit 的基线保留在 `references/ork-delta.md`) |
| PodDisruptionBudget 语义和驱逐 API | https://kubernetes.io/docs/tasks/run-application/configure-pdb/ (OrchestKit 的 `minAvailable` 底线保留在 `references/ork-delta.md`) |
| StatefulSets，序号身份，volumeClaimTemplates | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ |
| Helm 图表编写，模板和值文件 | https://helm.sh/docs/topics/charts/ (我们使用的图表目录布局保留在 `references/checklists-and-templates.md`) |
| External Secrets Operator CRD 字段和后端 | https://external-secrets.io/latest/api/externalsecret/ (OrchestKit 的刷新/创建策略保留在 `references/ork-delta.md`) |
| ArgoCD 自动同步，剪枝和自愈 | https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/ (OrchestKit 的重试/退避保留在 `references/ork-delta.md`) |
| Terraform S3 后端和状态锁定 | https://developer.hashicorp.com/terraform/language/backend/s3 (OrchestKit 的后端配置保留在 `references/ork-delta.md`) |
| Terraform 模块组合和变量文件 | https://developer.hashicorp.com/terraform/language/modules |
| Alembic 修订，升级和降级 CLI | https://alembic.sqlalchemy.org/en/latest/tutorial.html (零停机时间迁移排序保留在 `rules/devops-db-migrations.md`) |
| Prometheus 客户端 instrumentation（计数器，直方图，暴露） | https://prometheus.github.io/client_python/ |
| PromQL 函数（`rate`，`histogram_quantile`）用于仪表板 | https://prometheus.io/docs/prometheus/latest/querying/functions/ |
| Prometheus 告警规则语法 | https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ (OrchestKit 的阈值和停留窗口保留在 `references/ork-delta.md`) |
| OpenTelemetry FastAPI 自动 instrumentation 和手动跨度 | https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html |
| structlog 上下文绑定 | https://www.structlog.org/en/stable/contextvars.html (绑定后调用的排序保留在 `references/ork-delta.md`) |
| Trivy 严重性过滤和扫描配置 | https://trivy.dev/latest/docs/configuration/filtering/ (OrchestKit 的镜像扫描 CI 接线保留在 `references/docker-patterns.md`，每周扫描计划和严重性底线在 `references/ork-delta.md`) |
| CloudFront 无效化语义和成本 | https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html (同步后无效化顺序保留在 `references/ork-delta.md`) |
| 预发布安全，负载测试和监控清单 | `ork:security-patterns`，`ork:testing-perf`，`ork:monitoring-observability` (部署日清单保留在 `references/checklists-and-templates.md`) |

---

## 部署清单和模板

加载：`Read("references/checklists-and-templates.md")` 用于部署前/中/后清单，Helm 图表结构和模板参考表。

---

## 相关技能

- `ork:security-patterns` - CI/CD 管道的代码扫描和加固模式
- `ork:monitoring-observability` - Prometheus，Grafana 和部署应用的告警
- `ork:database-patterns` - Python/Alembic 迁移工作流用于后端部署
- `portless`（上游） - 多服务本地开发命名的 `.localhost` URL（`portless alias api 8080`）

## 关键决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 容器用户 | 非根（uid 1001） | 安全最佳实践，许多编排器要求 |
| 部署策略 | 滚动更新（默认） | 零停机时间，自动回滚，资源高效 |
| 密钥管理 | External Secrets Operator | 与云提供商同步，GitOps 兼容 |
| 健康检查 | 分离的启动/存活/就绪 | 防止过早流量，启用优雅关闭 |

## 能力详情

加载：`Read("references/capability-details.md")` 用于 6 个能力（ci-cd，docker，kubernetes，基础设施作为代码，部署策略，可观察性）的完整关键字索引和问题-解决方案映射。
