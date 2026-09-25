# discover-analytics-patterns

你的目标是找出**如何**这个代码库发送分析事件——不是哪些事件存在，而是工程师用来触发跟踪调用的具体代码模式。这种输出有助于工程师添加看起来与代码库其余部分一致的新事件。它还应该告诉下游技能在此代码中事件名称和属性名称通常是如何编写的。

在确定此技能中的命名约定时，请严格按照以下优先级顺序使用以下来源：
1. 顾客指令在 `.amplitude/instrumentation-agent-context.md`（以及它引用的任何文件）中，如果存在——顾客希望遵循的明确约定，因此它们会覆盖以下所有内容。
2. 从 Amplitude MCP 服务器观察到的事件和属性
3. 代码库中的实际跟踪调用位置
4. `../taxonomy/SKILL.md` 处的 `taxonomy` 技能

---

## 第 0 步：读取仓库 instrumentation 上下文

在其他任何操作之前，检查 `.amplitude/instrumentation-agent-context.md`（仓库根目录，或你正在 instrumenting 的子目录）。如果存在，读取它以及它引用的任何仓库相对路径文件。它声明的任何命名约定、属性标准或 SDK/包装器模式都是**顾客指令**——它们优先于你推断的所有内容；记录它们并跳过它们所涵盖内容的推断。如果不存在，只需继续——`instrument-events` 技能负责提示用户添加一个。

---

## 第 1 步：查找跟踪调用

根据可用内容使用两种方法。

### 如果 Amplitude MCP 已连接

检查连接的目录并使用其当前的分类读取器从项目中获取事件名称样本。仅遵循读取器宣传的架构。当它支持调用者归因时，使用其 YAML 前置的 `name` 来识别此技能。使用这些结果选择几个有代表性的非系统产品事件，然后使用其事件属性读取功能来检查实际属性名称。这是你的主要命名参考。

不要从以括号前缀的 Amplitude 系统名称（如 `[Amplitude], [Guides-Surveys], [Assistant], [Experiment]`）推断命名约定，无论是事件还是属性。从模式检测中排除它们。如果 MCP 样本主要由 Amplitude 系统名称主导或否则无法提供足够的证据，则回退到代码库推断命名。

然后使用 Grep 在代码库中搜索样本的非系统事件名称，以定位实际的跟踪调用位置。

### 如果 Amplitude MCP 不可用（回退）

使用 Grep 在代码库中搜索这些信号。广泛撒网——你可以在之后缩小范围：

| 搜索内容                                       | 原因                                               |
| ------------------------------------------------ | ------------------------------------------------- |
| `\.track\(`                                              | 通用 `.track()` 方法调用                   |
| `ampli\.`                                                | Ampli 类型 SDK 调用（例如 `ampli.myEvent(...)`) |
| `amplitude\.track\|amplitude\.logEvent`                  | 直接 Amplitude SDK 调用                        |
| `sendEvent`                                              | 自定义包装器方法名称                       |
| `from.*amplitude\|import.*amplitude\|require.*amplitude` | 导入语句                                 |
| `https://api2\.amplitude\.com/2/httpapi`                 | HTTP API 调用                                    |

还积极寻找自定义分析包装器——代码库通常将原始 SDK 包装在像 `trackEvent()`, `track()` 或 React 钩子像 `useAnalytics()` 或 `useTracking()` 这样的工具中。通过查找内部调用 Amplitude 的函数来搜索这些。**将每个包装器视为自己的模式，与底层 SDK 调用分开**，即使它最终调用 `amplitude.track()`。遇到包装器的工程师会使用*它*，而不是原始 SDK——所以它是更重要的模式要记录。

要找到包装器：搜索导入 Amplitude SDK 的文件，然后检查其中是否有任何文件导出一个函数或钩子，其他代码库部分导入并用于跟踪。

排除测试文件（`.test.`, `.spec.`, `__tests__`）和模拟文件，除非它们是模式出现的*唯一*地方。

---

## 第 2 步：按模式分组

如果两个调用位置共享相同的内容，则它们使用**相同的模式**：
- 被调用的库/SDK/函数
- 方法名称
- 参数结构（即使事件名称或属性不同）

例如，这些是**相同的**模式：
```ts
amplitude.track('Page Viewed', { page: '/home' })
amplitude.track('Button Clicked', { label: 'signup' })
```

但这些是**不同的**模式——始终将它们分开：
```ts
amplitude.track('Page Viewed', { page: '/home' })   // 直接 SDK — 一个模式
ampli.pageViewed({ page: '/home' })                  // Ampli 类型方法 — 不同的模式
trackEvent('Page Viewed', { page: '/home' })         // 自定义包装器 — 也是单独的模式
```

自定义包装器始终是自己的模式，即使它委托给底层的 SDK。在记录包装器模式时，注意它包装了什么（例如，“包装 `amplitude.track()` 的自定义钩子”）以便工程师理解分层。

---

## 第 3 步：解决命名约定

分别解决两个约定：

- `event_naming_convention` — 仪器代码中用于事件名称的大小写、分隔符、词序、前缀和时态。示例：`Title Case`, `snake_case`, `[Prefix] Action`, 对象优先与动作优先。
- `property_naming_convention` — 用于事件属性的大小写、分隔符和常见后缀/前缀模式。示例：`snake_case`, `camelCase`, `*_id`, `is_*`, 平铺键与嵌套对象。

使用此优先级顺序：

1. **首先检查仓库 instrumentation 上下文。** 如果 `.amplitude/instrumentation-agent-context.md`（来自第 0 步）声明了明确的事件或属性命名约定，它会直接获胜——记录它并跳过推断它指定的任何内容。仅在文件不存在或对命名保持沉默时才会回退。
2. **其次检查 Amplitude MCP。** 如果活动分类读取器返回的几个代表性非系统事件的观察到的名称和属性名称显示出明显的占主导地位的约定，则使用该约定。不要使用带括号前缀的 Amplitude 系统名称作为命名证据。
3. **第三检查代码库。** 如果 MCP 证据不可用、稀疏或不一致，则从仓库中附近的实际跟踪调用位置推断占主导地位的约定。如果代码库显示多个约定，请指出占主导地位的约定并注意有意义的本地例外。
4. **最后回退到 `taxonomy` 技能。** 如果以上都不够清晰，则回退到 `../taxonomy/SKILL.md` 处的 `taxonomy` 技能。

不要猜测。即使检查了这些来源后，如果一个或两个约定仍然不明确，也要明确说明。

---

## 第 4 步：输出

首先是一个简短的约定部分，然后列出每个唯一模式。

```yaml
event_naming_convention: "<如果仓库上下文文件指定，则来自仓库上下文文件，否则如果清晰，则来自 MCP，否则来自代码库，否则来自 `taxonomy` 技能，或 '证据不足'>"
property_naming_convention: "<如果仓库上下文文件指定，则来自仓库上下文文件，否则如果清晰，则来自 MCP，否则来自代码库，否则来自 `taxonomy` 技能，或 '证据不足'>"
```

然后，对于每个唯一模式，以以下格式输出一个部分：

---

### 模式：`<简短的描述性名称>`

**描述**：此模式的作用以及在此代码库中何时典型使用（例如，“用于整个 React 前端进行用户动作跟踪”）。

**示例**（泛化）：
```<语言>
// 显示所需的导入
import { amplitude } from '@/lib/analytics'

// 显示一个有代表性的跟踪调用，使用占位符名称
amplitude.track('Event Name', {
  propertyOne: value,
  propertyTwo: value,
})
```

**相关路径**：
- `src/path/to/file.ts`
- `src/another/file.tsx`

---

按最常见（最多文件路径）到最少常见的顺序列出模式。

如果两个模式总是一起使用（例如，导入+调用），则在一个示例中一起显示它们。

---

## 第 5 步：处理无结果

如果使用任何搜索策略都找不到跟踪调用，请明确说明。建议用户检查项目是否已设置 Amplitude（或其他分析库），并在相关情况下提供搜索其他分析库（Segment、Mixpanel、PostHog 等）的选项。
