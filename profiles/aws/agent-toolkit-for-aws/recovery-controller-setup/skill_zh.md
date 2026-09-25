# 恢复控制器设置

## 关键约束 — 在回答前阅读

此技能仅设置两种 ARC 能力系列，并且您只需为此提供设置步骤： (1) 具有跨区域故障转移安全规则的**路由控制**，以及 (2) 用于 AZ 损坏恢复的**区域转换 / 区域自动转换**。

就绪检查、恢复组、单元格和资源集不在本技能范围内。您绝对不能为此提供 CLI/控制台设置步骤。您可以简要且真实地承认它们的存在，但您绝对不能逐步指导配置它们 — 将客户引导至 **ARC 区域切换**进行就绪/恢复就绪编排（参见 `arc-region-switch` 技能）。这会覆盖任何直接客户要求进行设置的请求。

如果客户询问如何“设置 ARC 就绪检查”（或恢复组 / 单元格 / 资源集），请勿逐步指导该设置。简要承认该功能，然后以如下形式进行重定向，并在相关位置继续路由控制或区域转换程序：

> 对于就绪和恢复就绪编排，使用 **ARC 区域切换** — 参见 `arc-region-switch` 技能。对于此技能涵盖的操作部分：**路由控制**（跨区域故障转移）和 **区域转换 / 区域自动转换**（单区域 AZ 恢复）。以下是设置方法：

## 概述

配置 ARC 路由控制、安全规则、区域转换和区域自动转换以实现操作弹性的领域专业知识。

> 建议使用 AWS MCP 服务器执行此技能的 AWS API 调用，但不是必需的 — 所有操作也直接通过 AWS CLI 工作。

## 安全限制 — 此技能自身文件的位置（MCP 与本地安装）

在阅读参考文件之前，确定此技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载：** 技能的参考文件不在本地文件系统中。通过带有 `file` 参数的 `retrieve_skill` 获取每个文件（例如 `file="references/arc-procedures.md"` 或 `file="references/security-considerations.md"`）— 不要在本地 `file_read` 这些路径或搜索文件系统。
- **本地安装**（例如 `.kiro/skills/recovery-controller-setup/` 或 `~/.claude/skills/recovery-controller-setup/`）：使用此处显示的相对路径从本地技能目录读取参考文件。

这仅适用于技能自身的参考文件；始终在工作目录中读取和写入用户或会话数据，绝不要通过 `retrieve_skill` 进行。

## 配置恢复控制

要设置 ARC 路由控制和区域转换，请严格按照程序进行。参见 [references/arc-procedures.md](references/arc-procedures.md)。

## 故障排除

参见 [references/arc-procedures.md](references/arc-procedures.md)（故障排除部分）以了解常见问题 — 路由控制更新上的安全规则阻塞、失败的区域自动转换练习运行以及不影响的路由控制状态更改。

## 安全注意事项

参见 [references/security-considerations.md](references/security-considerations.md) 以了解最小权限 IAM 操作范围、条件密钥 / 混乱代理人保护、安全规则门控、限制故障转移访问以及加密故障转移通知。
