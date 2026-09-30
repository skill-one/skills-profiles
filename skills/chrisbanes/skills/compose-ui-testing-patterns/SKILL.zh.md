---
name: compose-ui-testing-patterns
description: 在编写或审查 Jetpack Compose UI 测试、截图测试或基线录制证据、预览、语义断言、模拟图片加载、键盘输入、焦点断言、交互状态（悬停/按下/聚焦）或纯状态驱动 UI 可组合组件的测试时使用。
---

# 组成：UI 测试模式

## 核心原则

测试能够证明行为的最小 UI 合约。优先使用纯状态驱动 UI 测试配合回调。仅在生命周期、导航、依赖注入或平台行为是测试目标时才添加集成。

## 流程

1.  说明任务要求你证明的行为和测试关注点。
2.  检查现有测试针对该关注点，并从下表中选择最小的充分接口。
3.  将修改聚焦于请求的测试关注点内。不要将仅用于测试的辅助函数移动到生产代码中，除非该生产边界本身也在被测试。
4.  驱动受控状态或输入，必要时通过 Compose 同步，并断言可观察的语义、视觉或回调结果。
5.  当现有测试已使用最窄的有效接口并证明请求行为时，无需修改即可完成。

## 测试目标选择

| 你需要证明的内容 | 测试形式 |
|---|---|
| 文本、按钮、加载/错误分支、条件内容 | 纯 UI Compose 测试 |
| 点击/输入的回调连接 | 纯 UI Compose 测试 |
| 聚焦导航或键盘行为 | 带键盘输入的 Compose 测试 |
| 视觉布局、裁剪、提升、排版、图像组合 | 截图测试 |
| 状态持有者正确更新 UI | 状态持有者/单元测试加一个连接冒烟测试 |
| 悬停、按下、聚焦、拖拽交互状态 | 带MutableInteractionSource的纯 UI 测试 |
| 导航、生命周期、依赖注入集成 | 集成测试 |

## 优先使用纯 UI 测试

如果屏幕有状态持有者/UI 分割，测试纯 UI 可组合项：

```kotlin
composeTestRule.setContent {
    ProfileScreen(
        state = ProfileUiState(name = "Ada", canSave = true),
        onNameChange = {},
        onSaveClick = { saved = true },
        onBackClick = {},
    )
}

composeTestRule.onNodeWithText("Ada").assertIsDisplayed()
composeTestRule.onNodeWithText("Save").performClick()

assertThat(saved).isTrue()
```

这避免了为布局行为构建 ViewModel、组件、仓库、导航和依赖图。

## 语义优先

在行为是语义时断言语义：

- 文本存在：`onNodeWithText`。
- 按钮启用/禁用：`assertIsEnabled`，`assertIsNotEnabled`。
- 内容被选中/聚焦/切换：使用语义断言。
- 内容不存在：`assertDoesNotExist`。

对没有稳定用户可见文本的节点或多个节点共享文本的节点使用测试标签。不要将标签作为所有断言的首选；用户可见语义通常更强。

## 回调测试

使用简单的计数器或捕获值：

```kotlin
var selectedId: String? = null

composeTestRule.setContent {
    ItemList(
        items = listOf(ItemUi("movie-1", "Movie")),
        onItemClick = { selectedId = it },
    )
}

composeTestRule.onNodeWithText("Movie").performClick()

assertThat(selectedId).isEqualTo("movie-1")
```

对于纯捕获回调值，通常在操作后直接断言即可。当断言需要在 Compose 完成快照状态应用、重组或排队 UI 工作之前读取结果时，使用 `runOnIdle`。

## 保持 UI 测试确定性

对于布局、分支和回调行为，使用 `setContent` 渲染受控状态，而不是构建生产应用图。生产依赖注入、仓库、生命周期观察器和后台效果会添加与纯 UI 合约无关的异步工作，并可能使测试变得不稳定。

不要使用 `Thread.sleep` 等待 Compose。将 UI 驱动到已知状态，然后使用语义断言和 Compose 同步（`waitForIdle`，`runOnIdle`，或用于真实异步条件的受限制 `waitUntil`）。将全应用集成保留给实际依赖于导航、生命周期、依赖注入或平台连接的行为。

## 交互状态与 MutableInteractionSource

当交互状态是关注点时，在编写或审查测试前完整阅读
[交互状态流程](references/interaction-state.md)。它需要直接、注入的交互状态，而不是脆弱的指针模拟。

## 键盘和聚焦

对于键盘、电视和桌面 UI，使用与用户相同的输入模型（键/方向键）驱动导航，而不仅仅是点击。断言聚焦语义，而不是颜色或缩放；将截图保留用于视觉聚焦处理。
如果被检查的可组合项没有可以改变状态的输入表面，在提出键驱动测试前命名缺失的主机或父交互接口；不要假设提供的 UI 中存在选择器或控件。

细节——聚焦图、`FocusRequester`、恢复、键处理器和测试模式：[`compose-focus-navigation`](../compose-focus-navigation/SKILL.md)。

## 截图测试

使用截图证明语义无法证明的视觉合约：

- 布局间距/对齐。
- 主题颜色、排版、提升、阴影。
- 图像组合、渐变、叠加。
- 聚焦高亮外观。
- 加载骨架或密集视觉状态。

保持截图状态确定性：

- 使用固定状态数据。
- 在可能时冻结时钟或动画进度。
- 使用假或预览处理器替换网络/图像加载。
- 避免断言动态文本，如当前时间，除非受控。

### 当截图默认值变化时

- 在测试中保留一个故意更改的命名预设或默认值，并更新其基线。不要用原始值替换以保留旧图像；保留断言和容差，除非有独立理由。
- 当固定分辨率或几何形状是合约时，保留一个明确的固定值。
- 分离验证和比较：检查预期的工件路径和故意基线差异。从测试中读取确切的输出路径，确认工件存在，并在验证证据中命名该字面路径。当验证日志报告通过时，说明什么通过了，然后独立检查记录；通过的比较并不能证明记录写入了工件。如果工件或基线差异不可用，报告该差距，而不是声称记录成功。将特定于工具的命令保留在仓库运行说明书中。

## 假图像和平台服务

当图像内容无关紧要时，伪造加载器并断言请求的模型（如果那是行为）。确切的钩子取决于你的图像库；项目辅助函数可能如下所示：

```kotlin
val requestedModels = mutableListOf<Any?>()

// 示例辅助函数，不是 Compose API。
setContentWithFakeImageLoader { request ->
    requestedModels += request.data
    errorPainter()
}
```

当图像外观重要时，提供确定性的本地绘制器/位图，而不是网络数据。
