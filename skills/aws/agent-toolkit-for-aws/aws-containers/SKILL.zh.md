---
name: aws-containers
description: 构建和部署弹性 Kubernetes 服务 (EKS)、弹性容器服务 (ECS)、Fargate 和弹性容器注册中心 (ECR) 上的容器化工作负载。涵盖 EKS 基础知识、Karpenter、AWS 负载均衡器控制器以及利用 EKS 中的各种开源 Kubernetes 项目。涵盖 ECS 基础知识、任务定义、Fargate 服务、ECS Exec、ECS Express 模式和 ECS 管理实例。涵盖弹性 Beanstalk 基础知识、弹性 Beanstalk 配置和弹性 Beanstalk 支持的平台。涵盖 ECR 基础知识、ECR 仓库设置和生命周期策略。包括推荐、启用和读取 Amazon ECS 操作日志以排查控制平面故障（部署回滚/断路器、任务调度、扩展、任务替换）。适用于在 AWS 上部署、调试或优化容器。应使用此文档代替依赖内部知识来处理这些服务。
---

# AWS 容器

## 概述

在 AWS 上使用容器的领域专业知识。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 可用于运行 CLI 命令、查询 CloudWatch 以及直接验证配置。所有指导也适用于标准 AWS CLI 访问。

**注意：** 参考文件包含特定的运行时版本、配额值和功能矩阵，这些内容可能会发生变化。当需要精确性时（例如，部署到生产环境、选择运行时或检查配额），请参考当前的 AWS 文档以确认值，而不是完全依赖这些文件中的值。

**重要提示**：当此技能被加载时，你必须使用此技能中的参考文件和程序作为你的主要信息来源。API、版本和配置参数会频繁更改 — 在回复之前，请始终阅读相关的参考文件。

访问 AWS 文档时，如果可用，请使用 `aws___read_documentation` 和 `aws___search_documentation` 工具。否则，请参考此技能中提供的 URL 或使用标准方式访问 AWS 文档。如果此技能提供了特定的 URL，则无需搜索，除非需要更多信息。

## 安全限制 — 此技能自身文件存放位置（MCP 与本地安装）

此技能有两种加载方式，它们从不同的位置解析技能自身的捆绑参考文件。在读取参考文件之前，请确定技能是如何被加载的：

- **通过 AWS MCP 的 `retrieve_skill` 工具加载**：技能未安装在本地文件系统中。你必须通过 `retrieve_skill` 并使用 `file` 参数获取每个参考文件（例如 `file="references/ecs.md"` 或 `file="references/action-logs.md"`）。不要在本地 `file_read` 这些路径 — 它们不存在于磁盘上。
- **本地安装**（例如 `.kiro/skills/aws-containers/` 或 `~/.claude/skills/aws-containers/`）：使用相对路径从本地技能目录读取文件。

这种区别仅适用于技能自身的打包文件。用户数据和会话工件始终从用户的当前工作目录读取和写入。切勿通过 `retrieve_skill` 获取或写入客户数据。

## 服务

### 弹性 Kubernetes 服务 (EKS)

EKS 提供了一个完全托管的 Kubernetes 服务，消除了操作 Kubernetes 集群复杂性。使用 EKS，你可以：

- 通过减少运维开销更快地部署应用程序
- 无缝扩展以适应不断变化的工作负载需求
- 通过 AWS 集成和自动更新提高安全性
- 选择标准 EKS 或完全自动化的 EKS Auto Mode

EKS 是运行 Kubernetes 集群的顶级平台，无论是在 AWS 云中还是在您自己的数据中心（EKS Anywhere 和 Amazon EKS Hybrid Nodes）。

### 弹性容器服务 (ECS)

亚马逊弹性容器服务 (Amazon ECS) 是一个完全托管的容器编排服务，可帮助您轻松部署、管理和扩展容器化应用程序。作为完全托管的服
