# Azure Cloud Migrate

> 该技能用于将现有云工作负载的**评估与代码迁移**工作处理到 Azure。

## 规则

1. 按顺序执行各个阶段——不得跳过
2. 在任何代码迁移之前生成评估
3. 加载场景参考文档并遵循其规则
4. 使用 `mcp_azure_mcp_get_azure_bestpractices` 和 `mcp_azure_mcp_documentation` MCP 工具
5. 为目标服务使用最新支持的运行时
6. 破坏性操作需调用 `ask_user` — [functions global-rules](references/services/functions/global-rules.md) | [app-service global-rules](references/services/app-service/global-rules.md)
7. **向用户报告进度** — 在长时间运行操作（部署、镜像推送）期间，提供资源级状态更新，确保用户不会在没有反馈的情况下等待——参见 [workflow-details.md](references/workflow-details.md)
8. **审计应用代码中的服务发现** — Kubernetes DNS 名称（例如 `http://order-service:3001`）在 Container Apps 中无法解析。在评估阶段，扫描源代码中 HTTP 客户端的硬编码主机名/端口，并标记以便进行基于环境变量的 URL 注入

## 迁移场景

| 源服务 | 目标服务 | 参考文档 |
|--------|--------|-----------|
| AWS Lambda | Azure Functions | [lambda-to-functions.md](references/services/functions/lambda-to-functions.md) ([assessment](references/services/functions/assessment.md), [code-migration](references/services/functions/code-migration.md)) |
| AWS Elastic Beanstalk | Azure App Service | [beanstalk-to-app-service.md](references/services/app-service/beanstalk-to-app-service.md) |
| Heroku | Azure App Service | [heroku-to-app-service.md](references/services/app-service/heroku-to-app-service.md) |
| Google App Engine | Azure App Service | [app-engine-to-app-service.md](references/services/app-service/app-engine-to-app-service.md) |
| AWS Fargate (ECS) | Azure Container Apps | [fargate-to-container-apps.md](references/services/container-apps/fargate-to-container-apps.md) ([assessment](references/services/container-apps/fargate-assessment-guide.md), [deployment](references/services/container-apps/fargate-deployment-guide.md)) |
| Kubernetes (GKE/EKS/Self-hosted) | Azure Container Apps | [k8s-to-container-apps.md](references/services/container-apps/k8s-to-container-apps.md) |
| GCP Cloud Run | Azure Container Apps | [cloudrun-to-container-apps.md](references/services/container-apps/cloudrun-to-container-apps.md) |
| Spring Boot (Azure Spring Apps/VMs) | Azure Container Apps | [spring-apps-to-aca.md](references/services/container-apps/spring-apps-to-aca.md) |

> 未匹配到对应场景？请使用 `mcp_azure_mcp_documentation` 和 `mcp_azure_mcp_get_azure_bestpractices` 工具。

## 输出目录

所有输出均存放于工作区根目录下的 `<workspace-root-basename>-azure/` 目录中，其中 `<workspace-root-basename>` 为顶层工作区目录自身的名称（非其内部子目录）。不得修改源目录。

## 步骤

1. **创建** `<workspace-root-basename>-azure/` 工作区根目录
2. **评估** — 分析源环境，映射服务，使用场景特定的评估指南生成报告 → [functions assessment](references/services/functions/assessment.md) | [app-service assessment](references/services/app-service/assessment.md)
3. **迁移** — 使用场景特定的迁移指南转换代码和配置文件 → [functions code-migration](references/services/functions/code-migration.md) | [app-service code-migration](references/services/app-service/code-migration.md)
4. **询问用户** — "迁移完成。是否在本地测试或部署到 Azure？"
5. **移交** azure-prepare，由其负责基础设施、测试与部署工作

在 `migration-status.md` 中跟踪进度——参见 [workflow-details.md](references/workflow-details.md)。
