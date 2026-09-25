# LaunchDarkly 指标创建

您正在使用一个将指导您完成创建 LaunchDarkly 指标的技能。对于自定义指标，**首先需要让事件开始流动**——在创建指标之前。您的工作是确定正确的指标类型，如果事件尚未流动，则进行事件监控（包括 SDK 设置和环境连接），检查重复项，提出指标配置，获取明确确认，然后创建和验证。

## 前置条件

此技能要求在您的环境中配置远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-metric` — 创建指标
- `get-metric` — 创建后验证
- `get-environment` — 仪器化时获取客户端 SDK 密钥

**可选的 MCP 工具（增强工作流）：**
- `list-metrics` — 检查具有相同事件键的现有指标并理解命名约定
- `list-metric-events` — 提交之前发现哪些事件键有近期活动（仅限自定义指标）

## 两个不同的“项目”——切勿混淆

用户处理两个完全独立的事物，它们都被称为“项目”。您必须始终保持这些区分：

| | 它是什么 | 用户如何引用它 | 您如何使用它 |
|---|---|---|---|
| **LaunchDarkly 项目** | 用户在其 LD 账户中的项目中创建指标 | 通常听起来像环境或团队名称：`my-app`，`anthony-agent-dev-5000`，`production` | 作为 `projectKey` 传递给所有 MCP 工具调用 |
| **本地代码库** | 开发者磁盘上的应用程序，您将使用 `track()` 调用对其进行监控 | 通常是一个文件夹名称、仓库名称或应用程序名称：`checkout_proj`，`frontend`，`my-react-app` | 用于查找和编辑源文件 |

**从用户输入解析这些的规则：**

- 如果用户说 *"my application at X"* 或 *"my codebase"* 或 *"my repo"* → 他们指的是**本地代码库**。`X` 是一个文件夹路径或项目名称，不是 LaunchDarkly 密钥。
- 如果用户说 *"add it to X"* 或 *"in LaunchDarkly"* 或 *"my LD project"* → 他们指的是**LaunchDarkly 项目**。`X` 是 API 调用的 `projectKey`。
- 用户可以将他们的本地代码库命名为 `checkout_proj`，而他们的 LaunchDarkly 项目是 `anthony-agent-dev-5000`。这些是无关的。
- **切勿假设本地代码库名称是 LaunchDarkly 项目密钥。** 如果您不确定哪个是哪个，请直接询问：*"为了确认——您的 LaunchDarkly 项目密钥是什么？（这与您的本地应用程序名称不同——您可以在 LD UI 中找到它，路径为 Account Settings > Projects。）"*

当两者都需要时（例如，对于需要仪器化的自定义指标），在继续之前明确确认每个项目。

## 工作流

### 第 1 步：确定指标类型

LaunchDarkly 有三种指标类型。**在开始之前选择正确的类型。**

| 类型 | 事件收集方式 | 需要什么 |
|------|--------------------------|----------|
| `custom` | 开发者调用 `ldClient.track(eventKey)` 在代码中 | `eventKey` |
| `pageview` | 当用户访问匹配的 URL 时自动触发——**不需要 SDK 调用** | `urls` (URL 匹配规则) |
| `click` | 当用户点击匹配 URL 上的 CSS 选择器时自动触发——**不需要 SDK 调用** | `urls` + `selector` |

**决策规则：**
- 用户说 "跟踪当有人查看页面/访问 URL" → **`pageview`**（首选——不需要仪器化）
- 用户说 "跟踪当有人点击按钮/链接" → **`click`**
- 用户说 "跟踪自定义事件" 或引用 `track()` 调用 → **`custom`**

当 `pageview` 或 `click` 可以工作时，建议它们而不是 `custom`——它们不需要代码更改。

### 第 2 步：解析数据源

**对于 `pageview` 和 `click` 指标：**
- 询问要匹配的 URL(s)。确认 URL 匹配规则的类型：
  - `substring` — URL 包含此字符串（最常见）
  - `exact` — URL 必须完全匹配
  - `canonical` — 匹配规范 URL
  - `regex` — 完全正则表达式模式
- 对于 `click` 指标，还询问 CSS 选择器（例如 `.checkout-btn`，`#submit`）。
- 跳过 `list-metric-events`——这些指标不使用事件键。
- 跳转到第 3 步。

**对于 `custom` 指标——首先检查事件，如果需要则进行仪器化：**

立即调用 `list-metric-events` 查看哪些事件键已经流动：

```
list-metric-events(projectKey, environmentKey?)
```

**情况 A——事件键已在列表中：** 与用户确认键，然后转到第 3 步。不需要仪器化。

**情况 B——事件键不在列表中：** 指标在没有事件的情况下无法测量。**现在立即进行事件仪器化**，然后再创建指标。不要只是警告并询问是否继续——将仪器化视为默认的下一步操作。

遵循以下仪器化子工作流，然后重新检查 `list-metric-events` 确认事件正在流动，然后再转到第 3 步。除非用户明确表示他们想先创建指标，稍后再连接事件，否则不要跳过仪器化——在这种情况下，在最后提醒他们，直到事件被跟踪，指标才会产生数据。

### 第 2b 步：仪器化事件（当事件未流动时）

此子工作流将 `track()` 调用放入代码库，并将应用程序连接到正确的 LaunchDarkly 环境。在返回主工作流之前完成所有步骤。

**1. 在代码库中找到正确的位置。**
定位事件自然发生的位置或处理程序（例如，结账提交处理程序、表单提交回调）。在做出更改之前，阅读相关源文件以了解现有结构。

**2. 确定事件键。**
如果用户没有指定，请提议一个描述性的 kebab-case 键，该键与代码正在做的事情匹配（例如 `checkout-completed`，`signup-submitted`）。在使用它之前与用户确认。

**3. 获取客户端 SDK 密钥。**
询问用户他们想连接到哪个环境（例如 "test"，“production”，“staging”）——只是环境名称。然后调用：

```
get-environment(projectKey, environmentKey)
```

使用响应中的 `clientSideId`。

**4. 编写环境文件。**
检查是否存在 `.env` 文件（或等效文件——`.env.local`，`.env.development` 等）。

- 如果文件**不存在**，则创建它。
- 如果文件**存在且已包含密钥**（例如 `VITE_LD_CLIENT_SIDE_ID`），则比较存储的值与 `get-environment` 返回的 `clientSideId`。如果它们不同，请向用户显示差异：
  > "您的 `.env` 已经有 `VITE_LD_CLIENT_SIDE_ID=<old>`，但 `get-environment` 为 `<env>` 环境返回 `<new>`。我应该更新它吗？"
  不要默默保留旧值——客户端 ID 不匹配意味着事件将发送到错误的项目或环境。
- 如果文件存在但键不存在，则添加它，不要触摸其他值。

使用与项目构建工具相应的变量名（例如，对于 Vite 使用 `VITE_LD_CLIENT_SIDE_ID`，对于 CRA 使用 `REACT_APP_LD_CLIENT_SIDE_ID`，对于 Next.js 使用 `NEXT_PUBLIC_LD_CLIENT_SIDE_ID`）。

**4b. 如果用户不在 app.launchdarkly.com 上，则设置 SDK 基础 URL。**
SDK 默认为所有流量使用 `app.launchdarkly.com`。如果用户在不同的 LaunchDarkly 部署上（例如内部 staging 环境 catamorphic 或专用实例），事件和标志评估将静默地发送到错误的主机。

通过检查 MCP API 响应中的任何 `_links` 或 UI URL 来检测这一点——如果它们指向 `app.launchdarkly.com` 以外的主机，则表示您处于非生产环境。如有疑问，请询问：
> "您连接到 app.launchdarkly.com 还是不同的 LaunchDarkly 实例？（例如内部或 staging 环境）"

如果它们在非标准主机上，请将三个附加变量添加到 `.env` 文件中：

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

**5. 如果 SDK 尚未存在，则安装并初始化它。**
检查 `package.json`（或等效依赖文件）以查找现有的 LD SDK。如果没有找到，请为项目的堆栈安装正确的 SDK：
- React → `launchdarkly-react-client-sdk`
- 浏览器 JS → `launchdarkly-js-client-sdk`
- Node.js 服务器 → `@launchdarkly/node-server-sdk`

在应用程序的入口点初始化 SDK（例如，用 `LDProvider` 包裹 React 根，在服务器入口处配置 `LDClient.init()` 等）。从 env 文件中传递客户端 ID。除非应用程序已经管理用户上下文，否则使用匿名用户/上下文作为默认值。

**6. 添加 `track()` 调用。**
在步骤 1 中确定的位置，在动作完成之前或之后立即添加调用：

- 计数/发生指标：`ldClient.track('event-key')`
- 值指标：`ldClient.track('event-key', null, numericValue)`

在客户端代码中，如果客户端尚未初始化，请使用可选链 (`ldClient?.track(...)`)。

**7. 验证事件是否正在流动。**
在仪器化更改后，提醒用户运行应用程序并至少触发一次事件。然后再次调用 `list-metric-events` 确认键出现，然后再转到指标创建。

### 第 3 步：检查现有指标

在创建任何内容之前，使用 `list-metrics` 扫描项目：

1. **检查重复项。** 搜索具有相同事件键、URL 模式或类似名称的指标。避免创建一个测量相同内容的第二个指标——相反，标记现有指标并询问用户是否想重用它。
2. **学习命名约定。** 指标键是 `kebab-case` 还是 `snake_case`？是否有常见的标签模式？匹配现有内容。
3. **理解标签分类。** 标签如 `team:growth`，`area:checkout` 或 `type:guardrail` 可能已经存在。根据用户描述建议相关标签。

### 第 4 步：提出指标配置

在调用任何 API 之前，以纯语言向用户展示拟议的配置，供用户确认或编辑。

**确定测量类型。** 正确的选择取决于用户试图了解的内容以及他们如何使用指标——在实验、受保护的发布或发布策略中使用。**不要假设。** 当事件是用户可以重复执行的事件（点击、添加到购物车、查看页面等）时，始终在提出之前询问：

> "您是想测量**此事件发生的总次数** (`count`)，还是**至少触发过一次的用户百分比** (`occurrence`)？"

将问题与他们的上下文联系起来：
- **实验** — 发生率对于转化目标很常见（处理是否导致更多用户执行 X？）；计数对于参与度或数量目标更好（处理是否导致更多总操作？）
- **受保护的发布/发布策略** — 发生率对于错误率保护栏很常见（有多少比例的用户遇到错误？）；计数适合绝对数量保护栏（总错误事件）
- **如果用户明确说“用户百分比”或“转化率”** → `occurrence`
- **如果用户明确说“次数”或“总事件”** → `count`

只有在意图从上下文中明确时才跳过询问（例如，“API 延迟”→ `value`，“错误率”→ `count`，“注册转化”→ `occurrence`）。

| 用户想测量什么 | 测量类型 | 含义 |
|-------------------------------|-------------|-------|
| 事件发生的总次数 | `count` | 每个分析单元的原始事件计数 |
| 每个用户是否触发过事件 | `occurrence` | 转化/二元（是否发生？） |
| 附加到事件上的数值 | `value` | 延迟、收入、分数等。 |

**确定成功标准：**

- **越高越好** → `HigherThanBaseline`（转化率、收入、参与度）
- **越低越好** → `LowerThanBaseline`（延迟、错误率、跳出率）

**使用常见模板作为默认值**，当用户的意图很明确时：

| 用户意图 | kind | 测量类型 | 成功标准 | 单位 |
|-------------|------|-------------|-----------------|------|
| 页面访问/查看率 | `pageview` | `occurrence` | `HigherThanBaseline` | — |
| 按钮/链接点击率 | `click` | `occurrence` | `HigherThanBaseline` | — |
| API 延迟/页面加载时间 | `custom` | `value` (平均) | `LowerThanBaseline` | `ms` |
| 注册/转化率 | `custom` | `occurrence` | `HigherThanBaseline` | — |
| 错误计数/率 | `custom` | `count` | `LowerThanBaseline` | — |
| 每用户收入 | `custom` | `value` (总和) | `HigherThanBaseline` | `USD` |

**在创建之前展示拟议的配置**——不要默默触发 API：

```
拟议的指标：
  键：              checkout-page-viewed
  名称：             Checkout Page Viewed
  类型：             pageview（在 URL 访问时自动跟踪——不需要代码更改）
  URL：             substring 匹配 "/checkout"
  测量类型：         occurrence（每个用户是否访问了页面？）
  成功标准：         HigherThanBaseline

继续，还是您想更改任何内容？
```

**在此停止。** 不要调用任何 API。不要转到第 5 步。等待用户明确确认后再做任何其他操作。用户必须响应批准（例如 "yes"，“看起来不错”，“proceed"）才能调用 `create-metric`。如果拟议的配置有任何歧义——例如在 `sum` 与 `average` 之间的选择，或事件键名称——请在提案中询问该问题，并在继续之前等待答案。

### 第 5 步：创建指标

**只有在用户在第 4 步中明确确认了拟议的配置后才能继续。** 如果您尚未收到确认，请返回并等待。

一旦用户确认，请调用 `create-metric`。该工具处理从 `measureType` 到底层 API 字段的转换——您永远不需要直接传递 `isNumeric` 或 `unitAggregationType`。

```
create-metric(
  projectKey,
  key,
  name,
  kind,              // "custom" | "pageview" | "click"
  eventKey?,         // 仅当 kind="custom" 时
  urls?,             // 仅当 kind="pageview" 或 "click" 时：[{ kind, url }]
  selector?,         // 仅当 kind="click" 时：CSS 选择器字符串
  measureType,       // "count" | "occurrence" | "value"
  successCriteria,   // "HigherThanBaseline" | "LowerThanBaseline"
  valueAggregation?, // 仅当 measureType="value" 时："average" (默认) 或 "sum"
  unit?,             // 显示标签： "ms"，"USD" 等。
  description?,
  tags?
)
```

### 第 6 步：验证

使用 `get-metric` 确认指标是否以正确的配置创建：

1. **键和名称与请求的匹配。**
2. **类型正确**——`custom`，`pageview` 或 `click`。
3. **measureType 正确**——通过读取 `measureType` 字段进行双重检查，而不仅仅是 `isNumeric`。
4. **eventKey / urls / selector** 设置为预期值。
5. **successCriteria 正确。**

向用户展示摘要：

```
✓ 指标创建：checkout-page-viewed
  类型：     pageview（在 URL 访问时自动跟踪）
  URL：     substring "/checkout"
  测量：     occurrence（转化率）
  目标：     越高越好

在 LaunchDarkly 中查看：{_links.ui 从 create-metric 响应中}
```

`create-metric` 工具返回一个 `_links.ui` 字段，其中包含正在使用的环境的正确 URL。始终使用该值——永远不要硬编码 `app.launchdarkly.com`。

## 测量类型参考

`create-metric` 工具内部将 `measureType` 翻译为 LD API 字段。您永远不需要直接设置 `isNumeric` 或 `unitAggregationType`。

| measureType | isNumeric | unitAggregationType | 用于 |
|-------------|-----------|---------------------|---------|
| `count` | false | sum | 原始事件计数——错误率、点击计数 |
| `occurrence` | false | average | 转化——用户是否执行了该操作？ |
| `value` (average) | true | average | 每用户平均值——平均延迟、平均会话长度 |
| `value` (sum) | true | sum | 每用户总计——总收入、购买商品总数 |

对于 `value` 指标，`valueAggregation` 默认为 `"average"`。传递 `valueAggregation: "sum"` 用于收入或累积总计。

## 重要上下文

- **在可能的情况下，优先选择 `pageview` 和 `click` 而不是 `custom`。** 它们不需要 SDK 仪器化，并且在浏览器环境中可以自动工作。
- **事件键区分大小写。** `checkout-completed` 和 `Checkout-Completed` 是不同的事件。键必须与 `track()` 调用中出现的键完全匹配。
- **没有事件的自定义指标不会产生数据。** 自定义指标只有在其事件键在生产环境（或相关环境）中积极跟踪时才有用。如果您在仪器化事件之前创建了指标，请提醒用户。
- **指标键是不可变的。** 创建后，无法更改指标的键。请谨慎选择。
- **指标是项目范围的。** 在一个项目中创建的指标在另一个项目中不可见。确保 `projectKey` 与实验或标志所在的匹配。
- **每个实验一个主要指标。** 在将此指标附加到实验时，请澄清它是否是主要指标（决定成功或失败的指标）还是次要指标（保护栏或支持信号）。有关实验设置的 LaunchDarkly 文档。
