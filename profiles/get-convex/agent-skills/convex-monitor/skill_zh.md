<!-- GENERATED from convex-agents content/capabilities/monitor.json — do not edit by hand. -->

# 等待下一个需要响应的事项

阻塞等待下一个输入事件，而不是轮询。竞争本地错误日志、部署订阅和Sentinel生产错误行；返回第一个触发的事件（或一个静默的心跳）。

## 工作流程

1. 使用 `{project_dir, event_kinds, timeout_ms}` 调用 `wait_for_event`。
2. 当 `kind=convex_error/next_error` 时：解码并修复它。当 `kind=prod_error` 时：进行分诊（参见Sentinel）并修复。当 `kind=feature_request` 时：构建它。当 `kind=quiet` 时：循环。
3. 当一个套件没有阻塞的MCP（例如Copilot云）时，包会运行一个具有相同事件契约的轮询循环——行为相同，机制不同。

## 规则

- 优先使用阻塞工具；仅在阻塞MCP较弱时才回退到轮询循环。
- 事件模式是固定的且版本化的——相同的触发器会产生相同的类型事件。
- 生产事件（`kind=prod_error`）需要一个部署的云应用加上Sentinel。
