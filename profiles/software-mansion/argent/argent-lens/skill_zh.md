> **前提条件 — 功能标志。** 此工作流受 `argent-lens` 标志控制（默认关闭）。在使用前，请运行一次 `argent enable argent-lens`。如果 `propose_variant` / `await_user_selection` 返回未找到，则表示该标志已关闭——请启用它并重试。

## 1. 概述

您实现多个候选设计，在设备上捕获每个设计的运行情况，并使用 `propose_variant` 将其整理。每个提议的元素会以浮动卡片的形式出现在 Argent Lens 窗口（一个会自动打开的原生窗口）中，该窗口旁边是实时模拟器流，并通过细线连接到实际元素。人类用户为每个元素进行选择，可以选择性地将自由形式的评论附加到元素上，然后点击 **完成选择**。`await_user_selection` 是唯一一个阻塞的调用，它将返回用户的决定。

**黄金法则：一个变体 = 一个真实的、_不同的_ 截图。** 如果一个提议的 `previewImage` 显示的是设备上实际渲染的变体，并且是在应用该特定变体之后捕获的，那么这个提议才有用。不要提议您尚未构建和在屏幕上看到的变体，也不要将两个变体指向同一个文件路径——如果两个捕获结果字节完全相同，则意味着您实际上没有进行任何更改，Argent Lens 会退化为相同的缩略图。计划 → 构建 → 导航 → 截图 → 提议，针对每个元素的每个变体重复此过程，然后等待一次。

## 2. 工具

| 工具                   | 阻塞？ | 目的                                                                 |
| ---------------------- | --------- | ----------------------------------------------------------------------- |
| `propose_variant`      | 否        | 为一个元素整理一个变体。每个变体调用一次。保持工作状态。             |
| `await_user_selection` | 是       | 在每个变体整理后调用一次。挂起直到人类完成。                     |

`propose_variant` 参数：`element`（人类名称），可选的 `match`（`{ by: "text"|"label"|"identifier"|"role", value }`），可选的 `udid`（您在设备上捕获变体的设备 ID），以及 `variant`（`{ name, summary, code?, filePath?, previewImage?, frame? }`）。使用相同的 `element` 重复调用会累积该元素的变体；不同的 `element` 值会创建单独的卡片。

**始终传递 `udid`**（与您截图和描述时使用的模拟器/模拟器 ID 相同）。预览窗口会直接流式传输该设备——人类用户无需选择模拟器。在第一轮的 `propose_variant` 中设置它；后续调用可以省略它（最后一个值将生效）。

## 3. 工作流

首先解决模拟器/模拟器（`argent-ios-simulator-setup` / `argent-android-emulator-setup`），对于 React Native，运行 `argent-react-native-app-workflow` 来运行应用程序并重新加载包。Argent 会将整理的变体显示在一个自动在用户屏幕上打开的原生预览窗口中；您不需要自己打开或显示任何内容。只需整理变体并调用 `await_user_selection`，窗口就会自行出现。

### 步骤 0 — 计划变体

在触摸代码之前，决定您要重新设计的元素及其每个元素的独特变体。将它们记录下来（例如："搜索字段：填充 / 轮廓 / 胶囊" — "主要 CTA：实心 / 渐变"）。每个变体必须是您可以独立应用、截图和还原的单个、自包含的更改。模糊或重叠的变体会产生无用的提议。

### 步骤 1 — 获取精确的匹配器

对于每个元素，在它所在的屏幕上运行 `describe`（对于 RN，运行 `debugger-component-tree`），并读取其确切的 `label` / `identifier` / `role`。将它们作为 `match` 传递，以便浮动卡片的连接器锚定到正确的元素：

- 稳定的 testID / accessibilityIdentifier → `{ by: "identifier", value: "search-input" }`（最可靠）
- 精确的 a11y 标签 → `{ by: "label", value: "Search" }`
- 否则 → `{ by: "text", value: "Search" }`（模糊包含；如果省略 `match`，则默认值）

省略 `match` 会默认为 `{ by: "text", value: element }`，这在元素的可见文本是唯一的情况下才适用。

### 步骤 2 — 对于每个变体：构建 → 导航 → 截图 → 提议

遍历每个元素的每个变体：

1. **构建变体。** 在代码中实现该变体。
2. **在设备上应用它。** 重新加载 RN 包（`debugger-reload-metro`）或按需重新构建，以便正在运行的应用程序显示此变体。
3. **导航到它。** 驱动应用程序（`argent-device-interact`）到元素可见的屏幕——如果元素实际上在屏幕上，截图才有意义。
4. **截图。** 调用 `screenshot` 并将返回的文件路径**直接传递**作为 `variant.previewImage`。**绝对不要手裁剪、调整大小、重新编码或复制截图到另一个文件夹**（例如，`crop.py` 到 `/tmp/variants/`）：这将导致预览窗口自己的裁剪进行双重裁剪，并且服务器不会提供该图像（"无预览"）。捕获整个屏幕——预览窗口会使用 `variant.frame`（步骤 5）为您裁剪。您获得的路径必须是一个新文件；如果您怀疑设备冻结或变体未应用（与之前的捕获相比没有可见变化），请在提议前与之前的路径进行 diff（`shasum -a 256`）——字节完全相同的捕获表示变体尚未在屏幕上。在提议前修复这个问题，不要无论如何都提议。
5. **提议。** 调用 `propose_variant`，使用 `element`、`match`、`udid`（您捕获的设备）和 `variant.previewImage` 设置为该截图路径。该工具**自动捕获裁剪框架**：它在提议时描述设备并匹配元素，因此每个缩略图都会裁剪到其自己的当前布局——只要在调用 `propose_variant` 时变体仍然在屏幕上（在截图后立即调用，在还原之前）。您可以传递 `variant.frame`（在 `describe` 中匹配节点的规范化 `{x, y, width, height}` 在 0..1 中，针对此变体）来覆盖自动捕获——当元素在提议时无法保持在屏幕上时，这很有用。在有用的情况下添加 `summary`（发生了什么以及为什么）和 `code`/`filePath`。
6. **还原。** 在构建下一个变体之前将变体更改回滚——一次只有一个变体可以在屏幕上。继续进行；`propose_variant` 不会阻塞。

`previewImage` 接受本地截图路径（从操作系统临时目录 / 当前工作目录提供）、`http(s)` URL 或 `data:` URI。强烈建议使用实际运行变体的本地截图。

### 步骤 3 — 等待人类的决定（一次）

在所有元素的每个变体整理完毕后，调用一次 `await_user_selection`。它返回：

- `{ status: "completed", selections: [{ element, chosenVariant, comment? }], unselected, annotations: [{ target, match, comment }], globalComment }` — 对每个元素应用 `chosenVariant`；跳过 `unselected` 中的元素。将每个 `annotations` 条目（人类用户附加到元素上的检查器评论）和 `globalComment` 视为变更请求。
- `{ status: "pending", proposedElements }` — `timeoutSeconds` 过期，不是错误。提议仍然有效；再次调用 `await_user_selection`。
- `{ status: "no_proposals" }` — 您在 `propose_variant` 之前调用了它。首先整理变体。

### 步骤 4 — 应用结果

为每个选定的元素实现所选变体，处理每个注释/评论，并报告您应用了什么以及跳过了什么。如果人类评论但跳过了一个变体，评论仍然重要——请采取行动。

## 4. 规则

- **每个元素至少有两个变体。** 选择需要替代方案——您提议的每个元素必须具有 ≥2 个不同的变体（至少两次调用 `propose_variant`）。如果您只有一个元素的查找，要么产生一个真实的替代方案，要么根本不提议该元素；一个孤立的变体不是一个选择。
- **在提议之前构建。** 每个 `previewImage` 必须是设备上实际运行的该变体的截图。没有草图，没有猜测，没有提议未构建的想法。
- **每个变体一个不同的截图。** 在两个变体之间重用 `previewImage` 路径——或者捕获两个路径的字节结果相同——会使整个 Argent Lens 失去意义。如果您无法生成可见不同的捕获（例如，应用程序是只读的，无障碍性损坏以至于您无法导航，包不会热重载），请停止并告诉用户，而不是整理重复项。
- **一个阻塞调用。** `propose_variant` 从不阻塞——自由整理。`await_user_selection` 是唯一一个等待的调用，并且您只调用一次，最后一次。
- **准确锚定。** 从 `describe` 中提取匹配器；错误的 `match` 会使卡片指向错误的元素或无锚定浮动。
- **一次一个变体在屏幕上。** 应用 → 截图 → 还原下一个变体，以便截图永远不会混合在一起。
- **`pending` 是正常的。** 在 `pending` 上，只需再次等待——提议在超时期间持续存在。
- **重新提议开始一个新轮次。** 在消耗一轮后调用 `propose_variant` 开始轮次 N+1 并清除上一轮的元素；每轮整理一套完整的元素。

## 5. 示例

```
describe { udid }                                  # 读取确切的 label/identifier
propose_variant { element: "Search field",
  match: { by: "identifier", value: "search-input" },
  variant: { name: "Outlined", summary: "1pt border, transparent fill",
             previewImage: "/var/folders/.../search-outlined.png" } }
propose_variant { element: "Search field",
  match: { by: "identifier", value: "search-input" },
  variant: { name: "Pill", summary: "Fully rounded, filled grey",
             previewImage: "/var/folders/.../search-pill.png" } }
propose_variant { element: "Primary CTA",
  match: { by: "label", value: "Get started" },
  variant: { name: "Gradient", summary: "Accent gradient fill",
             previewImage: "/var/folders/.../cta-gradient.png" } }
await_user_selection {}                             # 一个阻塞调用 → 人类选择
→ { status: "completed",
    selections: [ { element: "Search field", chosenVariant: { name: "Pill" } },
                  { element: "Primary CTA",  chosenVariant: { name: "Gradient" } } ],
    annotations: [ { target: "Tab bar", comment: "raise contrast" } ] }
# → 应用 Pill + Gradient，并提高 tab-bar 对比度。
```
