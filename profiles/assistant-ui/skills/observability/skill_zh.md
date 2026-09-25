# assistant-ui 可观测性

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

可观测性包含两个独立层级。Langfuse、LangSmith 和 Helicone 仪器后端模型调用。`@assistant-ui/react-o11y` 渲染应用程序已收集的 span 数据。它不会将追踪发送到提供方或从助手运行时派生 span。

## 参考

- [./references/langfuse.md](./references/langfuse.md) -- OpenTelemetry 设置、追踪属性以及 Langfuse 的无服务器刷新。
- [./references/langsmith.md](./references/langsmith.md) -- `wrapAISDK`、元数据和 LangSmith 的无服务器刷新。
- [./references/helicone.md](./references/helicone.md) -- AI SDK 和 OpenAI SDK 路由的 Helicone 代理设置。
- [./references/react-o11y.md](./references/react-o11y.md) -- `SpanResource`、每个导出的 span 基本部分、span 合同、时间线属性以及样式化的 TraceWaterfall 选项。

## 选择后端集成

根据您需要的数据模型使用一个提供方。

- **Langfuse** 在 `experimental_telemetry` 启用时接收 AI SDK 发送的 OpenTelemetry spans。使用它来跨代理回合、工具调用和模型调用进行分层追踪。
- **LangSmith** 通过 `wrapAISDK(ai)` 包装 AI SDK 函数。当追踪、评估和提示管理属于 LangChain 或 LangGraph 工具时使用它。
- **Helicone** 代理提供方请求。使用它来记录请求日志、成本、延迟和提示差异，而无需更改 AI SDK 调用形状。

Langfuse 和 Helicone 可以一起运行，因为一个消费 OpenTelemetry spans，而另一个代理提供方流量。LangSmith 是其自身的包装路径，因此请使用其包装的 AI SDK 函数而不是原始函数。

## 实现顺序

1. 选择拥有追踪目标地的提供方集成。
2. 添加其服务器环境变量和启动仪器或提供方配置。
3. 仪器一个路由并验证真实请求到达提供方控制面板。
4. 在将追踪视为生产中可靠之前添加无服务器刷新。
5. 仅当产品需要应用内追踪视图时，使用 react-o11y 渲染单独的 `SpanData[]` 源。

## 路由处理器边界

将提供方凭证和仪器保留在服务器上。每个示例使用 `openai("gpt-5.6-luna")`，等待 `convertToModelMessages(messages)`，并返回 AI SDK UI 消息响应。集成页面不使用 assistant-ui 路由辅助函数。如果路由需要，从 `@assistant-ui/ai-sdk` 导入它；`@assistant-ui/react-ai-sdk` 为旧版本重新导出相同的 API。

从真实认证和线程状态解析追踪属性。不要在客户端组件中放置提供方密钥、Langfuse 用户 ID、LangSmith 元数据或 Helicone 标头。

## 渲染收集的 spans

`SpanResource({ spans })` 接受完整的原始 `SpanData[]` 列表，规范化父级关系，按开始时间对可见 spans 进行排序，并拥有折叠状态。在隔离的提供方根目录挂载它：

```tsx
const config = AuiConfig({ span: SpanResource({ spans }) });

<AuiProvider extends={null} config={config}>
  <SpanPrimitive.Children components={{ Span: SpanRow }} />
</AuiProvider>;
```

`SpanRow` 组件自动作用域到一个可见 span。当行必须共享时间轴时，使用 `SpanPrimitive.Timeline` 和 `SpanPrimitive.TimelineBar`。当样式化的扁平消息和工具瀑布更适合您拥有的数据时，使用复制的 `TraceWaterfall` 元素。

## 常见问题

**在 Vercel、Lambda 或其他无服务器运行时追踪消失**

- Langfuse 在函数退出前需要 `await langfuseSpanProcessor.forceFlush()` 或部署特定的 `waitUntil` 路径。
- LangSmith 在函数退出前需要 `await client.awaitPendingTraceBatches()`。

**Langfuse 没有 spans**

- 在每个追踪的 `streamText` 或 `generateText` 调用上设置 `experimental_telemetry: { isEnabled: true }`。
- 仅在 Node 运行时注册 `LangfuseSpanProcessor`。OpenTelemetry 在边缘运行时不运行。

**LangSmith 不追踪路由**

- 从 `wrapAISDK(ai)` 调用解构函数，而不是从 `ai` 调用原始函数。
- 在运行时环境中设置 `LANGSMITH_TRACING=true`。

**Helicone 流量仍然直接发送到 OpenAI**

- 提供方 `baseURL` 必须是 `https://oai.helicone.ai/v1`，请求必须携带 `Helicone-Auth` 以及提供方授权标头。

**react-o11y 视图渲染没有行**

- 使用 `AuiConfig({ span: SpanResource({ spans }) })` 挂载 `SpanResource` 并在 `<AuiProvider extends={null} config={config}>` 下方渲染。
- 传递完整的 `SpanData[]` 列表。`SpanPrimitive.Children` 读取当前 span 作用域并不会获取追踪。

**缺少文档化的 span 组件**

- `SpanPrimitive.ChildByIndex` 没有被当前源重新导出。当需要显式索引作用域时，使用导出的 `SpanByIndexProvider` 与行组件一起使用。

## 相关技能

- [streaming](../streaming/SKILL.md) -- AI SDK 流传输和路由响应处理。
- [setup](../setup/SKILL.md) -- 项目创建、CLI 设置和运行时安装。
- [cloud](../cloud/SKILL.md) -- Assistant Cloud 持久化和运行报告配置。
- [elements](../elements/SKILL.md) -- 复制的样式化元素，包括 TraceWaterfall。
