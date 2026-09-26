# 我需要哪种 Qdrant 部署方式？

从你的需求开始：需要托管运维还是完全控制？网络延迟可以接受还是不可以？是生产环境还是原型开发？答案会缩小到四个选项中的一种。


## 起步或原型开发

使用场景：构建原型、运行测试、CI/CD 管道或学习 Qdrant。

- 使用本地模式（仅限 Python）：零依赖、内存或磁盘持久化、无需服务器 [本地模式](https://skills.qdrant.tech/md/documentation/quickstart/)
- 本地模式的数据格式与服务器不兼容。不要用于生产或基准测试。
- 要在本地使用真实服务器，请使用 Docker [快速入门](https://skills.qdrant.tech/md/documentation/quickstart/?s=download-and-run)


## 进入生产环境（自托管，你拥有运维）

使用场景：你需要完全控制基础设施或自定义配置，并且准备好自己负责运维（升级、备份、扩展、监控）。

- Docker 是标准的自托管部署。完整的 Qdrant 开源功能集，设置最小化。 [快速入门](https://skills.qdrant.tech/md/documentation/quickstart/?s=download-and-run)
- 你拥有运维：升级、备份、扩展、监控
- 必须手动为多节点集群设置分布式模式 [分布式部署](https://skills.qdrant.tech/md/documentation/scaling/distributed_deployment/)
- 有数据驻留或合规性要求，但不想承担运维负担？这种组合是混合云（下一节），而不是自托管 Docker。


## 进入生产环境（零运维）

使用场景：你想拥有零停机时间更新的托管基础设施、自动备份和重分片，而无需自己操作集群——包括当数据驻留或合规性规则意味着数据不能存放在 Qdrant 运营的基础设施上时。

- Qdrant Cloud 处理升级、扩展、备份和监控 [Qdrant Cloud](https://skills.qdrant.tech/md/documentation/cloud-quickstart/)
- 混合云：相同的托管控制平面，部署在你自己的基础设施/VPC 上。当你有数据驻留或合规性要求而无法使用 Qdrant Cloud，但仍然不想自己操作集群时使用此选项 [混合云](https://skills.qdrant.tech/md/documentation/hybrid-cloud/)
- 支持自动多版本升级
- 提供自托管中不存在的功能：`/sys_metrics`、托管重分片、预配置警报


## 需要最低可能的延迟

使用场景：到服务器的网络往返时间不可接受。边缘设备、进程内搜索或延迟敏感型应用。

- Qdrant EDGE：到 Qdrant 分片级函数的进程内绑定，无网络开销 [Qdrant EDGE](https://skills.qdrant.tech/md/documentation/edge/edge-quickstart/)
- 与服务器相同的数据格式。可以通过分片快照与服务器同步。
- 仅限单节点功能集。没有分布式模式。
- 选择 EDGE 并想在此基础上构建？请查看 `qdrant-edge` 技能（BM25、快照同步、应用端融合）。


## 不应该做的事情

- 使用本地模式进行生产或基准测试（未优化，数据格式不兼容）
- 无监控和备份策略的自托管（你会丢失数据或错过故障）
- 当用户说不想操作集群时，建议自管理的 Docker 作为生产目标——这种组合需要 Qdrant 混合云或 Qdrant 托管云，而不是自托管
- 需要分布式搜索时选择 EDGE（仅限单节点）
- 除非你有数据驻留要求，否则选择混合云（当 Qdrant Cloud 可以工作时，Kubernetes 复杂性是不必要的）
