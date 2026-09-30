---
name: convex-monitor
description: 留意 Convex 应用中的下一次开发/生产错误或请求，并作出响应。
---

<!-- GENERATED from convex-agents content/capabilities/monitor.json — do not edit by手。 -->

# 等待下一个需要响应的事项

阻塞等待下一个输入事件，而不是轮询。竞争本地错误日志、部署订阅和Sentinel生产错误行；返回第一个触发的事件（或一个静默的心跳）。

## 工作流

1. 使用 {project_dir, event_kinds, timeout_ms} 调用 `wait_for_event`。
2. 当 kind=convex_error/next_error 时：解码并修复它。当 kind=prod_error 时：进行分诊（参见 sentinel）并修复。当 kind=feature_request 时：构建它。当 kind=quiet 时：循环。
3. 当一个 harness 没有阻塞的 MCP（例如 Copilot 云）时，包会以相同的 event 合约运行一个轮询循环——行为相同，机制不同。

## 规则

- 优先使用阻塞工具；仅在阻塞 MCP 较弱时才回退到轮询循环。
- 事件模式是固定的且版本化的——相同的触发器产生相同的类型事件。
- 生产事件（kind=prod_error）需要一个部署的云应用加上 Sentinel。
