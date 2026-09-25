# /plan-zoom-integration

> 如果你看到不熟悉的占位符或需要检查哪些工具已连接，请参阅 [CONNECTORS.md](../../CONNECTORS.md)。

为 Zoom 集成或应用程序创建一个实用的构建计划。

## 使用方法

```text
/plan-zoom-integration $ARGUMENTS
```

## 工作流程

1.  捕获目标用户流程和成功标准。
2.  选择正确的 Zoom 表面和支持服务。
3.  定义认证要求、范围和账户假设。
4.  将实施分解为阶段：原型、核心集成、可靠性和发布。
5.  早期指出硬性风险：OAuth 设置、webhook 验证、SDK 环境限制、市场审核或 MCP 客户限制。
6.  以能证明架构的最小交付物结束。

## 输出

-  架构摘要
-  所需的 Zoom 产品和 API
-  认证和范围清单
-  交付阶段
-  风险、开放问题和立即执行的下一步行动

## 相关技能

-  [start](../start/SKILL.md)
-  [setup-zoom-oauth](../setup-zoom-oauth/SKILL.md)
-  [build-zoom-meeting-app](../build-zoom-meeting-app/SKILL.md)
-  [build-zoom-bot](../build-zoom-bot/SKILL.md)
