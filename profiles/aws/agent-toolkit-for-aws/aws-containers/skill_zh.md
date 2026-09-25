# AWS 容器

## 概述

在 AWS 上使用容器的领域专业知识。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 可启用运行 CLI 命令、查询 CloudWatch 和直接验证配置。所有指南也适用于标准 AWS CLI 访问。

**注意：** 参考文件包含特定的运行时版本、配额值和功能矩阵，这些内容可能会发生变化。当需要精确性时（例如，部署到生产环境、选择运行时或检查配额），请参考当前的 AWS 文档以确认值，而不是仅依赖这些文件中的值。

**重要提示**：当此技能加载时，你必须使用此技能中的参考文件和程序作为你的主要信息来源。API、版本和配置参数经常变化 — 在回复之前，请始终阅读相关的参考文件。

访问 AWS 文档时，如果可用，请使用 `aws___read_documentation` 和 `aws___search_documentation` 工具。否则，请参考此技能中提供的 URL 或使用标准方式访问 AWS 文档。如果你被此技能提供了一个特定的 URL，则无需搜索，除非需要更多信息。

## 边界控制 — 此技能自己的文件存放位置（MCP 与本地安装）

此技能可以通过两种方式加载，它们从不同的位置解析技能自己的捆绑参考文件。在读取参考文件之前，确定技能是如何加载的：

- **通过 AWS MCP 的 `retrieve_skill` 工具加载**：技能没有安装在本地文件系统中。你必须通过带有 `file` 参数的 `retrieve_skill` 获取每个参考文件（例如 `file="references/ecs.md"` 或 `file="references/action-logs.md"`）。不要在本地 `file_read` 这些路径 — 它们不存在于磁盘上。
- **本地安装**（例如 `.kiro/skills/aws-containers/` 或 `~/.claude/skills/aws-containers/`）：使用相对路径从本地技能目录读取文件。

这种区别仅适用于技能自己的捆绑文件。用户数据和会话工件始终从用户的当前工作目录读取和写入。永远不要通过 `retrieve_skill` 获取或写入客户数据。

## 服务

### 弹性 Kubernetes 服务 (EKS)

EKS 提供了一个完全托管的 Kubernetes 服务，消除了操作 Kubernetes 集群的复杂性。使用 EKS，你可以：

- 通过减少运维开销更快地部署应用程序
- 无缝扩展以满足不断变化的工作负载需求
- 通过 AWS 集成和自动更新提高安全性
- 选择标准 EKS 或完全自动化的 EKS Auto Mode

EKS 是运行 Kubernetes 集群的首选平台，无论是在 AWS 云中还是在您自己的数据中心（EKS Anywhere 和 Amazon EKS Hybrid Nodes）。

### 弹性容器服务 (ECS)

Amazon 弹性容器服务 (Amazon ECS) 是一个完全托管的容器编排服务，可帮助您轻松部署、管理和扩展容器化应用程序。作为完全托管的服
