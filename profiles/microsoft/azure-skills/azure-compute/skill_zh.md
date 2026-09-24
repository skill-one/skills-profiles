# Azure Compute Skill

将 Azure VM 和 Virtual Machine Scale Set (VMSS) 请求路由到正确的工作流。

## When to Use This Skill

- 用户想要 **推荐、比较或定价** VM 或 VMSS
- 用户想要 **创建、配置或部署** VM 或 VMSS
- 用户询问 **容量预留组 (CRG)** —— 预留、保障容量、预配置
- 用户询问 **核心机器管理 (EMM)** —— 机器注册、监控

**与 `azure-prepare` 进行消歧：** 如果用户想要部署 **应用程序**（Docker 服务、Web 应用、API、无服务器工作负载），请路由到 `azure-prepare`。`vm-creator` 仅用于 **裸 VM/VMSS 基础设施**。

## Routing

**强制先路由到工作流：** 切勿直接路由到 `references/*` 文件。首先对以下用户意图进行分类，打开匹配的工作流文件，然后仅加载该工作流请求的参考文件。参考文件是辅助材料，不是入口点。如果意图不明确，请提出澄清问题以区分不同工作流。

| 工作流 | 文件 | 适用场景 |
|---|---|---|
| **VM 推荐器** | [vm-recommender.md](workflows/vm-recommender/vm-recommender.md) | 用户询问选择哪个 VM/VMSS、是否使用 VMSS/自动伸缩、需要定价，或希望比较选项 |
| **VM 创建器** | [vm-creator.md](workflows/vm-creator/vm-creator.md) | 用户想要创建、配置或部署裸 VM 或 VMSS（非应用程序部署） |
| **容量预留** | [capacity-reservation.md](workflows/capacity-reservation/capacity-reservation.md) | 用户需要预留 / 保障 VM 容量（创建 / 关联 / 解关联 CRG） |
| **核心机器管理** | [essential-machine-management.md](workflows/essential-machine-management/essential-machine-management.md) | 用户询问 EMM / 机器注册 / 监控 |
