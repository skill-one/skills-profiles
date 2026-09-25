# 组合：UI 测试模式

## 核心原则

测试能够证明行为的最小 UI 合约。优先使用纯状态驱动 UI 测试配合回调。仅在生命周期、导航、依赖注入或平台行为是测试目标时，才添加集成。

## 程序步骤

1.  说明任务要求你证明的行为和测试关注点。
2.  检查现有测试，并根据以下表格选择最小的充分接口。
3.  在请求的测试关注点内保持专注的修改。不要将测试专用的辅助函数移动到生产代码中，除非该生产边界本身也在被测试。
4.  驱动受控状态或输入，在需要时通过 Compose 同步，并断言可观察的语义、视觉或回调结果。
5.  当现有测试已经使用最窄的有效接口并证明请求的行为时，完成时无需修改。

## 测试目标选择

| 你需要证明的内容 | 测试形式 |
|---|---|
| 文本、按钮、加载/错误分支、条件内容 | 纯 UI Compose 测试 |
| 点击/输入的回调连接 | 纯 UI Compose 测试 |
| 聚焦导航或键盘行为 | 带键盘输入的 Compose 测试 |
| 视觉布局、裁剪、阴影、排版、图像组合 | 截图测试 |
| 状态持有者正确更新 UI | 状态持有者/单元测试加一个连接冒烟测试 |
| 悬停、按下、聚焦、拖拽交互状态 | 带有 MutableInteractionSource 的纯 UI 测试 |
| 导航、生命周期、依赖注入集成 | 集成测试 |

## 优先使用纯 UI 测试

如果屏幕有状态持有者/UI 分割，测试纯 UI 组合项：

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
- 按钮启用/禁用：`assertIsEnabled`、`assertIsNotEnabled`。
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

对于纯捕获回调值，通常在操作后直接断言就足够了。当断言需要在 Compose 完成快照状态应用、重组或排队 UI 工作后读取结果时，使用 `runOnIdle`。

## 保持 UI 测试确定性

对于布局、分支和回调行为，使用 `setContent` 渲染受控状态，而不是构建生产应用图。生产依赖注入、仓库、生命周期观察者和后台效果添加异步工作，这与纯 UI 合约无关，并可能导致测试不稳定。

不要使用 `Thread.sleep` 等待 Compose。驱动 UI 到已知状态，然后使用语义断言和 Compose 同步（`waitForIdle`、`runOnIdle` 或一个有界的 `waitUntil` 用于真实的异步条件）。保留全应用集成用于实际依赖于导航、生命周期、依赖注入或平台连接的行为。

## 交互状态与 MutableInteractionSource

当交互状态是关注点时，在编写或审查测试前完整阅读
[交互状态程序](references/interaction-state.md)。它需要直接、注入的交互状态，而不是脆弱的指针模拟。

## 键盘和聚焦

对于键盘、电视和桌面 UI，使用与用户相同的输入模型驱动导航（键/方向键），而不仅仅是点击。断言聚焦语义，而不是颜色或缩放；保留截图用于视觉聚焦处理。

细节——聚焦图、`FocusRequester`、恢复、键处理器和测试模式：[`compose-focus-navigation`](../compose-focus-navigation/SKILL.md)。

## 截图测试

使用截图证明语义无法证明的视觉合约：

- 布局间距/对齐。
- 主题颜色、排版、阴影、渐变。
- 图像组合、渐变、叠加。
- 聚焦高亮外观。
- 加载骨架或密集视觉状态。

保持截图状态确定性：

- 使用固定状态数据。
- 在可能时冻结时钟或动画进度。
- 使用假或预览处理器替换网络/图像加载。
- 除非有独立理由，否则避免断言动态文本，如当前时间。

### 当截图默认值变化时

- 在测试中保留一个故意更改的命名预设或默认值，并更新其基线。不要用原始值替换以保留旧图像；保留断言和容差，除非有独立理由。
- 当固定分辨率或几何形状是合约时，保留显式固定值。
- 分别验证录制和比较：检查预期的工件路径和故意基线差异。通过的比较并不证明录制发生。在仓库运行说明书中保留特定于工具的命令。

## 假图像和平台服务

当图像内容无关紧要时，伪造加载器并断言请求的模型（如果这是行为）。确切的钩子取决于你的图像库；项目辅助函数可能如下所示：

```kotlin
val requestedModels = mutableListOf<Any?>()

// 示例辅助函数，不是 Compose API。
setContentWithFakeImageLoader { request ->
    requestedModels += request.data
    errorPainter()
}
```

当图像外观重要时，提供确定性的本地绘制器/位图，而不是网络数据。
