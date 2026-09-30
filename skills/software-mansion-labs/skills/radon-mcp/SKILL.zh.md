---
name: radon-mcp
description: 使用 Radon IDE 的 MCP 工具进行 React Native 和 Expo 应用的开发、调试和检查的最佳实践。在与通过 Radon IDE 运行中的应用交互时使用——查看截图、读取日志、检查组件树、调试网络请求、重新加载应用，或查询 React Native 文档和库信息。触发条件：'debug React Native'、'fix UI'、'network issues'、'build issues'、'Radon IDE'、'view screenshot'、'app logs'、'component tree'、'network inspector'、'reload app'、'React Native docs'、'library description'、'emulator'、'development viewport'、'view_screenshot'、'view_application_logs'、'view_component_tree'、'reload_application'、'view_network_logs'、'view_network_request_details'、'query_documentation'、'get_library_description'，以及任何在 Radon IDE 会话中涉及实时应用检查、调试或开发的请求。
---

# Radon IDE MCP工具

Radon IDE的MCP工具用于实时React Native/Expo应用的检查和调试的最佳实践。

阅读相关工具的参考文档。所有参考文档都在`references/`目录下。

## 参考文档

| 文件                                         | 何时阅读                                                                                       |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `references/view-application-logs.md`        | 调试任何问题时 - 首先调用`view_application_logs`查看构建、原生和运行时日志 |
| `references/view-screenshot.md`              | 检查应用的当前视觉状态、修复视觉错误、进行UI更改                      |
| `references/view-component-tree.md`          | 理解挂载组件结构、解决布局问题、查找上下文提供者                      |
| `references/view-network-logs.md`            | 检查网络请求 - 来自和进入应用的HTTP流量分页列表                      |
| `references/view-network-request-details.md` | 深入查看特定网络请求的头部、正文和元数据                             |
| `references/reload-application.md`           | 重新加载应用 - 选择JS重新加载、进程重启或完整重建                     |
| `references/query-documentation.md`          | 从精选知识库中查找React Native/Expo API文档                         |
| `references/get-library-description.md`      | 评估npm库的作用以及是否适合任务                                   |
