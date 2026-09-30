---
name: launchdarkly-metric-create
description: 创建一个 LaunchDarkly 指标，用于衡量实验或发布过程中重要的指标。当用户需要创建指标、跟踪事件、测量页面浏览量、按钮点击次数、转化率、延迟、错误率或任何自定义的数值或二元结果时使用。首先在需要时对事件进行仪器化（包括 SDK 设置和 .env），然后创建并验证该指标。
---

# LaunchDarkly 指标创建

您正在使用一个将引导您完成创建 LaunchDarkly 指标的技能。对于自定义指标，**首先需要让事件开始流动**——在创建指标之前。您的工作是确定正确的指标类型，如果事件尚未流动，则进行instrument（包括SDK设置和环境连接），检查重复项，提出指标配置，获取明确确认，然后创建并验证。

## 前置条件

此技能需要在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-metric` — 创建指标
- `get-metric` — 创建后验证
- `get-environment` — 在instrument时获取客户端SDK密钥

**可选的 MCP 工具（增强工作流）：**
- `list-metrics` — 检查具有相同事件键的现有指标并理解命名约定
- `list-metric-events` — 在提交之前发现哪些事件键有近期活动（仅限自定义指标）

## 两个不同的“项目”——切勿混淆它们

用户与两个完全独立的事物打交道，它们都被称为“项目”。您必须始终保持这些区分：

| | 它是什么 | 用户如何指代它 | 您如何使用它 |
|---|---|---|---|
| **LaunchDarkly 项目** | 用户在其 LD 账户中的项目中创建指标 | 通常听起来像环境或团队名称：`my-app`，`anthony-agent-dev-5000`，`production` | 将其作为 `projectKey` 传递给所有 MCP 工具调用 |
| **本地代码库** | 开发者在磁盘上的应用程序，您将使用 `track()` 调用对其进行instrument | 通常是一个文件夹名称、仓库名称或应用程序名称：`checkout_proj`，`frontend`，`my-react-app` | 用于查找和编辑源文件 |

**从用户输入中解析这些的规则：**

- 如果用户说 *"my application at X"* 或 *"my codebase"* 或 *"my repo"* → 他们指的是**本地代码库**。`X` 是一个文件夹路径或项目名称，不是 LaunchDarkly 密钥。
- 如果用户说 *"add it to X"* 或 *"in LaunchDarkly"* 或 *"my LD project"* → 他们指的是**LaunchDarkly 项目**。`X` 是 API 调用的 `projectKey`。
- 用户可以将他们的本地代码库命名为 `checkout_proj`，而他们的 LaunchDarkly 项目是 `anthony-agent-dev-5000`。这些是无关的。
- **切勿假设本地代码库名称是 LaunchDarkly 项目密钥。** 如果您不确定哪个是哪个，请直接询问：*"Just to confirm — what's your LaunchDarkly project key? (This is different from your local app name — you can find it in the LD UI under Account Settings > Projects.)"*

当两者都需要时（例如，对于需要instrument的自定义指标），在继续之前明确确认每个。

## 工作流

### 第一步：确定指标类型

LaunchDarkly 有三种指标类型。**在开始之前选择正确的类型。**

| 类型 | 事件如何收集 | 需要 |
|------|--------------------------|----------|
| `custom` | 开发者调用 `ldClient.track(eventKey)` 在代码中 | `eventKey` |
| `pageview` | 当用户访问匹配的 URL 时自动触发——**不需要 SDK 调用** | `urls` (URL 匹配规则) |
| `click` | 当用户点击匹配 URL 上的 CSS 选择器时自动触发——**不需要 SDK 调用** | `urls` + `selector` |

**决策规则：**
- 用户说 "track when someone views a page / visits a URL" → **`pageview`**（首选——不需要instrument）
- 用户说 "track when someone clicks a button / link" → **`click`**
- 用户说 "track a custom event" 或引用 `track()` 调用 → **`custom`**

当 `pageview` 或 `click` 可以工作时，建议它们而不是 `custom`——它不需要代码更改。

### 第二步：解析数据源

**对于 `pageview` 和 `click` 指标：**
- 询问要匹配的 URL(s)。确认 URL 匹配规则的类型：
  - `substring` — URL 包含此字符串（最常见）
  - `exact` — URL 必须完全匹配
  - `canonical` — 匹配规范 URL
  - `regex` — 完整正则表达式模式
- 对于 `click` 指标，还询问 CSS 选择器（例如 `.checkout-btn`，`#submit`）。
- 跳过 `list-metric-events` — 这些指标不使用事件键。
- 跳转到步骤 3。

**对于 `custom` 指标——首先检查事件，如果需要则instrument：**

立即调用 `list-metric-events` 查看哪些事件键已经流动：

```
list-metric-events(projectKey, environmentKey?)
```

**情况 A——事件键已在列表中：** 确认密钥并与用户确认，然后转到步骤 3。不需要instrument。

**情况 B——事件键不在列表中：** 指标在没有事件的情况下无法测量。**现在立即instrument事件**，然后再创建指标。不要只是警告并询问是否继续——将instrument视为默认的下一步操作。

遵循以下instrument子工作流，然后重新检查 `list-metric-events` 确认事件正在流动，然后再转到步骤 3。除非用户明确表示他们想先创建指标，然后再连接事件——在这种情况下，在最后提醒他们，指标在事件被跟踪之前不会产生数据。

### 第二步 b：Instrument 事件（当事件未流动时）

此子工作流将 `track()` 调用放入代码库，并将应用程序连接到正确的 LaunchDarkly 环境。在返回主工作流之前完成所有步骤。

**1. 在代码库中找到正确的位置。**
定位事件自然发生的位置的函数或处理程序（例如，结账提交处理程序、表单提交回调）。在做出更改之前，阅读相关的源文件以了解现有结构。

**2. 确定事件键。**
如果用户没有指定，请提出一个描述性的 kebab-case 键，该键与代码正在做的事情匹配（例如 `checkout-completed`，`signup-submitted`）。在使用它之前与用户确认。

**3. 获取客户端 SDK 密钥。**
询问用户他们想连接到哪个环境（例如 "test"，"production"，"staging"）——只是环境名称。然后调用：

```
get-environment(projectKey, environmentKey)
```

使用响应中的 `clientSideId`。

**4. 编写环境文件。**
检查是否存在 `.env` 文件（或等效文件——`.env.local`，`.env.development` 等）。

- 如果文件**不存在**，则创建它。
- 如果文件**存在并且已经包含密钥**（例如 `VITE_LD_CLIENT_SIDE_ID`），则比较存储的值与 `get-environment` 返回的 `clientSideId`。如果它们不同，请向用户显示差异：
  > "Your `.env` already has `VITE_LD_CLIENT_SIDE_ID=<old>`, but `get-environment` returned `<new>` for the `<env>` environment. Should I update it?"
  不要默默保留旧值——客户端 ID 不匹配意味着事件将发送到错误的项目或环境。
- 如果文件存在但密钥不存在，则添加它，不要触摸其他值。

使用与项目构建工具相应的变量名（例如 Vite 的 `VITE_LD_CLIENT_SIDE_ID`，CRA 的 `REACT_APP_LD_CLIENT_SIDE_ID`，Next.js 的 `NEXT_PUBLIC_LD_CLIENT_SIDE_ID`）。

**4b. 如果用户不在 app.launchdarkly.com 上，设置 SDK 基 URL。**
SDK 默认为所有流量指向 `app.launchdarkly.com`。如果用户在另一个 LaunchDarkly 部署上（例如内部 staging 环境 catamorphic 或专用实例），事件和标志评估将静默地发送到错误的主机。

通过检查 MCP API 响应中的任何 `_links` 或 UI URL 来检测这一点——如果它们指向 `app.launchdarkly.com` 之外的主机，则表示您在非生产环境中。如有疑问，请询问：
> "Are you connecting to app.launchdarkly.com or a different LaunchDarkly instance? (e.g. an internal or staging environment)"

如果他们在非标准主机上，请将三个附加变量添加到 `.env` 文件中：

```
VITE_LD_BASE_URL=https://<their-host>
VITE_LD_STREAM_URL=https://clientstream.<their-host-domain>
VITE_LD_EVENTS_URL=https://events.<their-host-domain>
```

并在初始化时将它们传递给 SDK `options`：

```js
asyncWithLDProvider({
  clientSideID,
  context: { kind: 'user', anonymous: true },
  options: {
    baseUrl: import.meta.env.VITE_LD_BASE_URL,
    streamUrl: import.meta.env.VITE_LD_STREAM_URL,
    eventsUrl: import.meta.env.VITE_LD_EVENTS_URL,
  },
})
```

如果他们在 `app.launchdarkly.com` 上，则完全省略 `options` 块——默认值是正确的，不需要额外配置。

**5. 安装和初始化 SDK** 如果它尚未存在。
检查 `package.json`（或等效的依赖文件）以查找现有的 LD SDK。如果没有找到，请为项目的堆栈安装正确的 SDK：
- React → `launchdarkly-react-client-sdk`
- 浏览器 JS → `launchdarkly-js-client-sdk`
- Node.js 服务器 → `@launchdarkly/node-server-sdk`

在应用程序的入口点初始化 SDK（例如，用 `LDProvider` 包裹 React 根，在服务器入口配置 `LDClient.init()` 等）。从环境文件中传递客户端 ID。除非应用程序已经管理用户上下文，否则使用匿名用户/上下文作为默认值。

**6. 添加 `track()` 调用。**
在步骤 1 中确定的位置，在动作完成之前或之后立即添加调用：

- 计数/发生指标：`ldClient.track('event-key')`
- 数值指标：`ldClient.track('event-key', null, numericValue)`

在客户端代码中使用可选链 (`ldClient?.track(...)`)，因为客户端可能尚未初始化。

**7. 验证事件正在流动。**
在instrument更改之后，提醒用户运行应用程序并至少触发一次事件。然后再次调用 `list-metric-events` 确认键出现，然后再转到指标创建。

### 第三步：检查现有指标

在创建任何东西之前，使用 `list-metrics` 扫描项目：

1. **检查重复项。** 搜索具有相同事件键、URL 模式或类似名称的指标。避免创建第二个测量相同内容的指标——相反，标记现有指标并询问用户是否要重用它。
2. **学习命名约定。** 指标键是 `kebab-case` 还是 `snake_case`？是否有常见的标签模式？匹配已存在的。
3. **理解标签分类法。** 标签如 `team:growth`，`area:checkout` 或 `type:guardrail` 可能已经存在。根据用户描述提出相关标签。

### 第四步：提出指标配置

在调用任何 API 之前，以纯语言向用户展示拟议的配置以供确认或编辑。

**确定测量类型。** 正确的选择取决于用户试图了解的内容以及他们如何使用指标——在实验、受保护的发布或发布策略中使用。**不要假设。** 当事件是用户可以重复执行的事件（点击、添加到购物车、查看页面等）时，始终在提出之前询问：

> "Are you trying to measure **how many times** this event happens in total (`count`), or **what percentage of users** triggered it at least once (`occurrence`)?"

将问题与他们的上下文联系起来：
- **实验** — 发生率对于转化目标很常见（治疗是否导致更多用户执行 X？）；计数对于参与度或数量目标更好（治疗是否导致更多总操作？）
- **受保护的发布 / 发布策略** — 发生率对于错误率护栏很典型（多少比例的用户遇到错误？）；计数适合绝对数量护栏（总错误事件）
- **如果用户明确说 "percent of users" 或 "conversion rate"** → `occurrence`
- **如果用户明确说 "number of times" 或 "total events"** → `count`

只有在意图从上下文中明确（例如 "API latency" → `value`，"error rate" → `count`，"signup conversion" → `occurrence`）的情况下才跳过询问。

| 用户想要测量的内容 | 测量类型 | 含义 |
|-------------------------------|-------------|-------|
| 事件发生的总次数 | `count` | 每个分析单元的原始事件计数 |
| 每个用户是否触发了事件 | `occurrence` | 转化/二元（是否发生？） |
| 附加到事件的数值 | `value` | 延迟、收入、分数等。 |

**确定成功标准：**

- **越高越好** → `HigherThanBaseline`（转化率、收入、参与度）
- **越低越好** → `LowerThanBaseline`（延迟、错误率、跳出率）

**使用常见模板作为默认值**，当用户的意图很明确时：

| 用户意图 | kind | 测量类型 | 成功标准 | 单位 |
|-------------|------|-------------|-----------------|------|
| 页面访问 / 访问率 | `pageview` | `occurrence` | `HigherThanBaseline` | — |
| 按钮 / 链接点击率 | `click` | `occurrence` | `HigherThanBaseline` | — |
| API 延迟 / 页面加载时间 | `custom` | `value` (平均) | `LowerThanBaseline` | `ms` |
| 注册 / 转化率 | `custom` | `occurrence` | `HigherThanBaseline` | — |
| 错误计数 / 率 | `custom` | `count` | `LowerThanBaseline` | — |
| 每用户收入 | `custom` | `value` (总和) | `HigherThanBaseline` | `USD` |

**在创建之前展示拟议的配置**——不要默默触发 API：

```
拟议的指标：
  键：              checkout-page-viewed
  名称：             Checkout Page Viewed
  类型：             pageview (在 URL 访问时自动跟踪——不需要代码更改)
  URL：             substring "/checkout"
  测量类型：         occurrence (每个用户是否访问了页面?)
  成功标准：         HigherThanBaseline

继续，还是您想更改任何内容？
```

**在此停止。** 不要调用任何 API。不要转到步骤 5。等待用户明确确认后再做任何其他事情。用户必须响应批准（例如 "yes"，"looks good"，"proceed"）之前，您才能调用 `create-metric`。如果拟议的配置有任何歧义——例如在 `sum` 与 `average` 之间的选择，或事件键名称——请在提案中提出该问题，并在继续之前等待答案。

### 第五步：创建指标

**只有在用户在步骤 4 中明确确认了拟议的配置后才能继续。** 如果您尚未收到确认，请返回并等待。

一旦用户确认，请调用 `create-metric`。该工具处理从 `measureType` 到底层 API 字段的转换——您永远不需要直接传递 `isNumeric` 或 `unitAggregationType`。

```
create-metric(
  projectKey,
  key,
  name,
  kind,              // "custom" | "pageview" | "click"
  eventKey?,         // 仅当 kind="custom"
  urls?,             // 仅当 kind="pageview" 或 "click": [{ kind, url }]
  selector?,         // 仅当 kind="click": CSS 选择器字符串
  measureType,       // "count" | "occurrence" | "value"
  successCriteria,   // "HigherThanBaseline" | "LowerThanBaseline"
  valueAggregation?, // 仅当 measureType="value": "average" (默认) 或 "sum"
  unit?,             // 显示标签: "ms", "USD", 等.
  description?,
  tags?
)
```

### 第六步：验证

使用 `get-metric` 确认指标是否以正确的配置创建：

1. **键和名称与请求的匹配。**
2. **kind 是正确的** — `custom`，`pageview` 或 `click`。
3. **measureType 是正确的** — 通过阅读 `measureType` 字段进行双重检查，而不仅仅是 `isNumeric`。
4. **eventKey / urls / selector** 设置为预期的值。
5. **successCriteria 是正确的。**

向用户展示摘要：

```
✓ Metric created: checkout-page-viewed
  类型:     pageview (自动在 URL 访问时跟踪)
  URL:     substring "/checkout"
  测量:     occurrence (转化率)
  目标:     越高越好

在 LaunchDarkly 中查看: {_links.ui from the create-metric response}
```

`create-metric` 工具返回一个 `_links.ui` 字段，其中包含正在使用的环境的正确 URL。始终使用该值——永远不要硬编码 `app.launchdarkly.com`。

## 测量类型参考

`create-metric` 工具内部将 `measureType` 翻译为 LD API 字段。您永远不需要直接设置 `isNumeric` 或 `unitAggregationType`。

| measureType | isNumeric | unitAggregationType | 用途 |
|-------------|-----------|---------------------|---------|
| `count` | false | sum | 原始事件计数 — 错误率、点击次数 |
| `occurrence` | false | average | 转化 — 用户是否执行了该操作？ |
| `value` (average) | true | average | 按用户平均 — 平均延迟、平均会话时长 |
| `value` (sum) | true | sum | 按用户总计 — 总收入、总购买商品数量 |

对于 `value` 指标，`valueAggregation` 默认为 `"average"`。需要总收入或累积总计时，请传递 `valueAggregation: "sum"`。

## 重要背景

- **尽可能优先使用 `pageview` 和 `click` 而非 `custom`。** 它们无需 SDK 仪器化，在浏览器环境中自动生效。
- **事件键区分大小写。** `checkout-completed` 和 `Checkout-Completed` 是不同的事件。请确保与 `track()` 调用中出现的键完全匹配。
- **无事件的自定义指标不会产生数据。** 自定义指标只有在生产环境（或相关环境）中开始主动追踪其事件键时才有用。如果用户在事件仪器化之前创建了指标，请提醒他们。
- **指标键不可变。** 创建后，指标的键无法更改。请谨慎选择。
- **指标是项目范围的。** 在一个项目中创建的指标在另一个项目中不可见。确保 `projectKey` 与实验或标志所在的场所匹配。
- **每个实验一个主要指标。** 将此指标附加到实验时，请明确它是主要指标（决定成功或失败的指标）还是次要指标（限速或辅助信号）。请参阅 LaunchDarkly 文档了解实验设置。
