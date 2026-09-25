# LaunchDarkly 指标监控

您正在使用一个技能，它将指导您如何在代码库中添加一个 `track()` 调用来使 LaunchDarkly 指标能够测量它。您的工作是检测正在使用的 SDK，找到代码中添加调用的正确位置，正确编写它，并验证事件是否已到达 LaunchDarkly。

## 前置条件

此技能需要在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `list-metric-events` — 验证事件在监控后是否正在流动

**可选的 MCP 工具（增强工作流程）：**
- `get-project` — 在需要初始化 SDK 时检索正确环境的 SDK 密钥

## 工作流程

### 第 1 步：检测 SDK

在编写任何代码之前，了解此代码库中已有的 LaunchDarkly 设置。

1. **搜索现有的 `track()` 调用。** 这是最快的信号：
   - 查找 `ldClient.track(`, `.track(`, `ld.track(`
   - 如果存在，它们会告诉您 SDK 类型、调用签名和上下文模式，只需镜像这些即可。

2. **如果不存在 `track()` 调用，则搜索 SDK 导入和初始化：**
   - 检查 `package.json`、`requirements.txt`、`go.mod`、`Gemfile`、`*.csproj` 以查找 LD SDK 依赖项
   - 查找 `LDClient`、`ldclient`、`launchdarkly-server-sdk`、`launchdarkly-node-server-sdk`、`launchdarkly-react-client-sdk` 等
   - 找到初始化块以了解客户端如何在代码库中访问

3. **确定客户端端或服务器端。** 这是最重要的区别——它决定了 `track()` 签名：

   | SDK 类型 | `track()` 签名 | 备注 |
   |----------|---------------------|-------|
   | 服务器端（Node、Python、Go、Java、Ruby、.NET） | `ldClient.track(eventKey, context, data?, metricValue?)` | 每次调用都需要上下文 |
   | 客户端端（React、浏览器 JS） | `ldClient.track(eventKey, data?, metricValue?)` | 上下文在初始化时设置，不是每次调用 |

   参考 [SDK Track Patterns](references/sdk-track-patterns.md) 获取每种语言的全示例。

### 第 2 步：安装和初始化（如果 SDK 不存在）

如果代码库中已经存在 SDK，则跳过此步骤。

1. **从锁定文件检测包管理器：** `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` → npm/yarn/pnpm；`Pipfile.lock` / `poetry.lock` → pip/poetry；`go.sum` → go 模块；`Gemfile.lock` → bundler。

2. **使用检测到的包管理器安装适当的 SDK。** 参考 [SDK Track Patterns](references/sdk-track-patterns.md) 获取每种语言的正确包名。

3. **使用 `get-project` 获取 SDK 密钥** — 获取项目并选择用户要监控的环境的密钥（通常为 `production` 或 `staging` 用于初始测试）。

4. **按照此代码库中已有的模式添加 SDK 初始化。** 如果有中央配置或服务层，将 LD 客户端添加到那里。参考 [SDK Track Patterns](references/sdk-track-patterns.md) 获取初始化示例。

### 第 3 步：找到正确的位置

定位代码中用户操作或事件发生的位置。

1. **如果您不确定操作发生的位置，请询问。** 不要猜测位置——在错误的位置（例如渲染方法而不是提交处理程序）调用 `track()` 会产生误导性数据。

2. **查找正确的位置信号：**
   - 表单提交、按钮点击处理程序、API 路由完成、变异钩子
   - 现有的分析调用（`segment.track()`、`mixpanel.track()`、`gtag()`）——这些通常与 LD track 调用应该放置的位置相同
   - 注释如 `// TODO: track this`

3. **在编写任何内容之前向用户展示候选位置：**
   ```
   我将在结账提交处理程序中添加 track() 调用（src/checkout/CheckoutForm.tsx，第 47 行）。
   这样看起来对吗？
   ```

4. **一旦确认（或如果您足够自信从代码库信号中判断）即可继续。**

### 第 4 步：编写 `track()` 调用

按照第 1 步中发现的模式编写调用。

**服务器端 SDK** — 需要上下文：
```typescript
ldClient.track('checkout-completed', context);
```

**客户端端 SDK** — 上下文是隐式的：
```typescript
ldClient.track('checkout-completed');
```

**对于 `value` 指标** — 包含 `metricValue` 与数值测量：
```typescript
// 服务器端：延迟指标（毫秒）
ldClient.track('api-response-time', context, null, responseTimeMs);

// 客户端端：收入指标
ldClient.track('purchase-completed', { orderId }, purchaseAmountUSD);
```

**关键规则：**
- **匹配现有上下文。** 不要内联构造新的上下文。找到代码库已经构建其上下文/用户对象的位置（用于 `variation()` 调用），并使用相同的上下文。这是 LD 如何将事件关联到正确的实验参与者。
- **`metricValue` 仅用于 `value` 指标。** 对于 `count` 和 `occurrence` 指标，完全省略 `metricValue`。
- **尊重包装模式。** 如果代码库在工具后面包装 LD 调用（`featureFlags.track()`、`analytics.ldTrack()`），通过该包装器添加新调用——不是直接调用 `ldClient`。
- **精确匹配事件键。** `track()` 事件键区分大小写。使用创建指标时使用的确切字符串。

参考 [SDK Track Patterns](references/sdk-track-patterns.md) 获取每种语言的全示例。

### 第 5 步：验证

**指导用户在其本地或 staging 环境中触发操作。** 然后使用 `list-metric-events` 确认事件键出现：

```
list-metric-events(projectKey, environmentKey)
```

**如果事件键出现：** 确认成功并显示摘要。

**如果触发后事件键不存在，** 按照以下清单进行处理：

| 问题 | 检查 |
|---------|-------|
| 事件键大小写错误 | `track()` 调用是否与指标的 event key 精确匹配？ |
| SDK 未初始化 | `ldClient` 是否在 `track()` 调用运行之前初始化？ |
| 服务器端：上下文错误 | 传递给 `track()` 的上下文是否与 `variation()` 调用使用的上下文相同？ |
| 客户端端：未先进行标志评估 | SDK 是否在调用 `track()` 之前初始化并识别了用户？ |
| 环境错误 | `list-metric-events` 是否查询了与触发操作相同的环境？ |
| 数据延迟 | `list-metric-events` 显示最后 90 天，最多延迟约 5 分钟——稍后再试 |

验证后显示摘要：

```
✓ 事件正在流动：checkout-completed
  在：production
  
下一步：此事件现在可以支持一个指标。使用 metric-create 技能设置一个指标，
或将现有指标附加到您的实验。
```

## 重要上下文

- **`track()` 调用在标志首先评估时才计入实验。** 事件因为 LD 从该上下文看到了 `variation()` 调用而被关联到实验参与者。如果用户在评估任何标志之前触发操作，事件可能仍然被摄取，但不会出现在实验结果中。
- **客户端端 SDK 按间隔（默认约 30 秒）或页面卸载时刷新事件。** 在测试中，您可能需要显式调用 `ldClient.flush()` 以立即看到事件出现。
- **服务器端 SDK 也缓冲事件。** 在开发中调用 `ldClient.flush()` 后 `track()` 确保在进程退出或测试结束时发送事件。
- **`metricValue` 单位必须与指标定义匹配。** 如果指标使用单位 `ms` 创建，请传递毫秒。将秒传递给毫秒指标将产生无声的错误结果。
- **`data` 参数用于自定义元数据，而不是指标值。** 在 `data` 中传递额外上下文（订单 ID、类别等）。在 `metricValue` 中传递数值测量。

## 参考

- [SDK Track Patterns](references/sdk-track-patterns.md) — 每种支持 SDK 的 `track()` 调用语法、初始化和包名
