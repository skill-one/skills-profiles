# Google Cloud 架构设计良好框架中运营卓越支柱的技能

## 概述

Google Cloud 架构设计良好框架中的运营卓越支柱为在 Google Cloud 上高效运行工作负载提供建议。云中的运营卓越涉及设计、实施和管理提供价值、性能、安全和可靠性的云解决方案。此支柱中的建议帮助您持续改进和调整工作负载，以满足云中不断变化和不断发展的需求。

## 核心原则

架构设计良好框架中运营卓越支柱的建议与以下核心原则保持一致：

-   **确保运营就绪**：定义和衡量工作负载被视为生产就绪的标准，包括人员配备、流程和治理。基础文档：https://docs.cloud.google.com/architecture/framework/operational-excellence/operational-readiness-and-performance-using-cloudops.md.txt

-   **管理事件和问题**：建立结构化的流程，用于事件响应、沟通和根本原因分析，以最大程度地减少影响并防止再次发生。基础文档：https://docs.cloud.google.com/architecture/framework/operational-excellence/manage-incidents-and-problems.md.txt

-   **管理和优化云资源**：监控资源利用率并调整环境大小，以在确保运营效率的同时保持性能。基础文档：https://docs.cloud.google.com/architecture/framework/operational-excellence/manage-and-optimize-cloud-resources.md.txt

-   **自动化和管理变更**：使用基础设施即代码（IaC）和 CI/CD 管道，以确保一致、可重复且低风险的部署和配置变更。基础文档：https://docs.cloud.google.com/architecture/framework/operational-excellence/automate-and-manage-change.md.txt

-   **持续改进和创新**：定期审查架构、监控行业趋势，并调整运营以满足不断变化的业务需求。基础文档：https://docs.cloud.google.com/architecture/framework/operational-excellence/continuously-improve-and-innovate.md.txt

## 相关的 Google Cloud 产品

以下是与运营卓越相关的 Google Cloud 产品和功能的示例：

-   **可观察性和监控**
    -   **Cloud Monitoring**：适用于 Google Cloud 和混合环境的全栈可观察性。
    -   **Cloud Logging**：大规模实时日志管理和分析。
    -   **Error Reporting**：聚合并显示运行云服务的错误。
    -   **Service Monitoring**：用于定义和跟踪服务等级目标（SLO）的工具。

-   **自动化和 CI/CD**
    -   **Cloud Build**：用于构建、测试和部署软件的无服务器平台。
    -   **Cloud Deploy**：适用于 GKE、Cloud Run 和 GCE 的托管持续交付服务。
    -   **Terraform / Infrastructure Manager**：用于基础设施即代码（IaC）自动化的托管服务。
    -   **Artifact Registry**：用于管理构建工件和容器镜像的中心存储库。

-   **资源管理和优化**
    -   **Recommender (Active Assist)**：自动识别闲置资源和调整大小机会。
    -   **Resource Manager**：跨组织、文件夹和项目的分层资源管理。

-   **事件响应**
    -   **Incident response & management (IRM)**：用于管理运营中断的结构化工具和流程。

## 工作负载评估问题

提出适当的问题，以了解工作负载及其用户组织的运营相关需求和限制。从以下列表中选择问题：

-   **运营就绪和性能**
    -   您如何定义和衡量云工作负载的运营就绪，以及您使用哪些具体标准或指标？
    -   描述您定义、跟踪和实现关键工作负载的 SLO 的流程。

-   **事件和问题管理**
    -   描述您的事件管理流程，包括角色、职责和沟通渠道。
    -   您如何进行事后回顾（PIR）以识别根本原因并实施预防措施？

-   **资源管理和优化**
    -   您如何确保您的云资源适合您的工作负载，以及您使用哪些工具或技术？

-   **变更自动化**
    -   描述您的变更管理流程，包括审批工作流、测试程序和部署策略。
    -   您如何自动化部署，确保其一致性并管理配置？

-   **持续改进**
    -   您如何确保您的云运营持续适应不断变化的业务需求和技术进步？

## 验证清单

使用以下清单评估架构与运营卓越建议的一致性：

-   **运营就绪**
    -   [ ] 在生产部署前存在正式框架或标准来评估运营就绪。
    -   [ ] 服务等级目标（SLO）已明确定义并使用自动化工具进行监控。

-   **事件管理**
    -   [ ] 事件响应角色和沟通渠道已明确定义并记录在案。
    -   [ ] 所有重大事件都遵循结构化的、无指责的事后分析流程。

-   **变更自动化**
    -   [ ] 所有基础设施变更都使用基础设施即代码（IaC）执行，以确保一致性。
    -   [ ] CI/CD 管道与所有部署变更的自动化测试集成。

-   **资源优化**
    -   [ ] 使用 Active Assist 的建议或性能数据定期审查资源利用率。

-   **改进文化**
    -   [ ] 已制定文档化的策略，用于定期审查和调整云运营以适应行业进步。
