# Azure 计算技能

将 Azure 虚拟机 (VM) 和虚拟机规模集 (VMSS) 请求路由到正确的流程。

## 何时使用此技能

- 用户希望**推荐、比较或定价**虚拟机或 VMSS
- 用户希望**创建、配置或部署**虚拟机或 VMSS
- 用户询问**容量预留组** (CRG) — 预留、保证容量、预配置
- 用户询问**基础机器管理** (EMM) — 机器注册、监控

**与 `azure-prepare` 区分：** 如果用户希望部署**应用程序**（Docker 服务、Web 应用、API、无服务器工作负载），请路由到 `azure-prepare`。`vm-creator` 仅用于**裸机/VMSS 基础设施**。

## 路由

**强制先流程后引用文件路由：** 不要直接路由到 `references/*` 文件。首先根据用户意图分类，打开匹配的流程文件，然后仅加载流程请求的引用文件。引用文件是辅助材料，不是入口点。如果意图不明确，请提出澄清问题以区分不同流程。

| 流程 | 文件 | 使用场景 |
|---|---|---|
| **虚拟机推荐器** | [vm-recommender.md](workflows/vm-recommender/vm-recommender.md) | 用户询问选择哪个 VM/VMSS、是否使用 VMSS/自动缩放、需要定价或需要比较选项 |
| **虚拟机创建器** | [vm-creator.md](workflows/vm-creator/vm-creator.md) | 用户希望创建、配置或部署裸机或 VMSS（非应用程序部署） |
| **容量预留** | [capacity-reservation.md](workflows/capacity-reservation/capacity-reservation.md) | 用户需要预留/保证虚拟机容量（CRG 创建 / 关联 / 解除关联） |
| **基础机器管理** | [essential-machine-management.md](workflows/essential-machine-management/essential-machine-management.md) | 用户询问 EMM / 机器注册 / 监控 |
