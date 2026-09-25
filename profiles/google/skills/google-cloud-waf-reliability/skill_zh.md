# Google Cloud 架构设计良好框架可靠性支柱技能

## 概述

Google Cloud 架构设计良好框架的可靠性支柱提供原则和建议，帮助您在 Google Cloud 中设计、部署和管理可靠、弹性和高可用的工作负载。可靠的系统在定义条件下始终执行其预期功能，能够抵御故障，并在中断后优雅地恢复，从而最大限度地减少停机时间，提升用户体验，并确保数据完整性。

## 核心原则

架构设计良好框架可靠性支柱中的建议与以下核心原则一致：

-  **基于用户体验目标定义可靠性**：可靠性测量应反映系统用户的实际体验，而不仅仅是依赖基础设施指标。关注对用户最重要的结果。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/define-reliability-based-on-user-experience-goals.md.txt

-   **为可靠性设定现实目标**：确定适当的业务水平目标（SLO），在最大化可用性的成本和复杂性与企业需求之间取得平衡。提供基于监控信号、错误预算和用户体验目标定义业务水平目标（SLO）的指导。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/set-targets.md.txt

-  **通过资源冗余构建高可用系统**：通过跨区域和区域复制关键组件来消除单点故障，以在局部故障期间保持运行。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/build-highly-available-systems.md.txt

-   **利用水平可扩展性**：设计系统架构以进行水平扩展（添加更多实例），以无缝适应负载波动并提高整体容错能力。结合主动容量规划，监控和调整项目配额和资源可用性，以预期突发负载峰值。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/horizontal-scalability.md.txt

-   **通过可观察性检测潜在故障**：实施全面的监控、日志记录和警报系统，以主动检测、诊断和解决异常，防止其引发用户可见问题。监控黄金信号（延迟、流量、错误和饱和度），并在信号超过指定阈值时设置警报。使用 Cloud Monitoring 为黄金信号构建综合仪表板。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/observability.md.txt

-   **设计优雅降级**：架构系统以在依赖项失败或系统经历极端压力时保持关键功能，即使性能降低或功能有限。为避免级联故障，建议设置警报以早期检测故障，使用断路器模式，有效处理超时以释放阻塞资源，利用指数退避和抖动重试以避免压垮恢复的后端系统，并返回自定义错误响应或静态回退页面。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/graceful-degradation.md.txt

-  **进行故障恢复测试**：通过持续模拟故障并验证自动和手动恢复程序的有效性，建立系统弹性的信心。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/perform-testing-for-recovery-from-failures.md.txt

-  **进行数据丢失恢复测试**：定期测试备份和恢复协议，确保从数据损坏或丢失中快速恢复，并在定义的恢复时间目标（RTO）和恢复点目标（RPO）内。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/perform-testing-for-recovery-from-data-loss.md.txt

-  **进行彻底的事后分析**：通过全面调查中断来培养无指责文化，了解根本原因，然后实施防止重发的措施。基础文档：https://docs.cloud.google.com/architecture/framework/reliability/conduct-postmortems.md.txt

## 相关的 Google Cloud 产品

以下是与可靠性相关的 Google Cloud 产品和功能的示例：

- **计算**：Compute Engine 管理实例组（MIGs）、Google Kubernetes Engine (GKE)、Cloud Run
- **网络**：Cloud Load Balancing、Cloud CDN、Cloud DNS
- **存储和数据库**：Cloud Storage（多区域）、Cloud SQL 高可用性、Spanner、Filestore、Firestore
- **运维**：Cloud Monitoring、Cloud Logging、Google Cloud Managed Service for Prometheus
- **灾难恢复**：Backup and DR Service、Filestore 备份

## 工作负载评估问题

提出适当的问题，以了解工作负载及其用户组织的可靠性相关需求和限制。从以下列表中选择问题：

- 您的组织如何定义和衡量系统在用户体验方面的可靠性？
- 您的组织如何处理为服务设定可靠性目标？
- 您的组织如何通过资源冗余确保高可用性？
- 您的组织如何利用水平可扩展性以保持性能和可靠性？
- 您的组织如何利用可观察性（指标、日志、跟踪）以获取洞察并检测潜在故障？
- 您的组织如何管理基于可观察性数据的警报，以确保及时响应重大问题而不会导致警报疲劳？
- 您的组织采取了哪些措施以确保系统在高负载或部分故障期间可以优雅降级？
- 您的组织多久以及多全面地测试系统故障恢复（例如，区域故障转移、发布回滚）？
- 您的组织如何测试数据丢失恢复？
- 您的组织如何进行和利用事件后的事后分析？

## 验证清单

使用以下清单评估架构与可靠性建议的一致性：

- 明确定义并积极监控面向用户的 SLI 和 SLO。
- 架构通过跨区域或跨区域冗余避免单点故障。
- 启用自动缩放以处理可变需求而无需人工干预。
- 配置应用程序和基础设施健康检查以触发自动故障转移。
- 设置定期备份计划，并常规测试恢复过程。
- 系统架构结合了断路器、指数退避重试和速率限制等模式以支持优雅降级。
- 定期举行游戏日或混沌工程实践以验证故障恢复。
- 存在一个正式的无指责事后分析流程，以确保组织从运营事件中学习。
