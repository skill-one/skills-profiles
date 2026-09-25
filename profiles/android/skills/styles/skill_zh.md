## 限制

- 警告用户此功能为 EXPERIMENTAL 版本，需要升级到 Compose 的 alpha 版本并选择启用实验性 API。
- 此功能仅支持自定义 UI 组件和自定义主题。
- 此功能不支持 Material Design 组件样式。

## 前置条件

### 1. 升级依赖项

- 项目必须使用 `compileSdk` 版本 37 或更高。
- 项目必须使用 `androidx.compose.foundation:foundation` 版本 `1.12.0-alpha01` 或更高。
- 或者，项目必须使用 Compose BOM 版本 `2026.04.01` 或更高。
- 此 API 需要此确切包：`import androidx.compose.foundation.style.Style`

### 2. 配置编译器选项以启用实验性 API

您必须在项目级别选择启用实验性 API。将以下代码块添加到您的模块的 `build.gradle.kts` 文件中：

```kotlin
kotlin {
    compilerOptions {
        jvmTarget = JvmTarget.fromTarget("17")
        freeCompilerArgs.add("-opt-in=androidx.compose.foundation.style.ExperimentalFoundationStyleApi")
    }
}
```

## 核心工作流和指南

参考官方文档完成特定开发任务：

- 基本样式使用：要为组件设置背景、尺寸和对齐方式，请遵循 [Compose 样式基础指南](references/android/develop/ui/compose/styles/fundamentals.md)。
- 状态和过渡：要配置状态变化（如按下或悬停）的属性更改，请遵循 [动画和基于状态的样式指南](references/android/develop/ui/compose/styles/state-animations.md)。
- 架构权衡：要决定何时使用样式而不是标准 Modifier，请遵循 [样式与 Modifier 的比较](references/android/develop/ui/compose/styles/styles-vs-modifiers.md)。
- 主题级别集成：要将样式定义与自定义主题连接起来，请遵循 [使用样式进行主题化](references/android/develop/ui/compose/styles/theming.md) 和 [Compose 中的自定义主题](references/android/develop/ui/compose/designsystems/custom.md)。

## 分步迁移工作流

### 第 1 步：分析主题结构

1. 定位您的中心主题文件（例如 `Theme.kt`）。
2. 识别设计令牌。注意颜色、排版和形状的引用（例如，`LocalColorScheme`、`LocalTypography` 或 `LocalShapes`）。
3. 如果项目缺少 Jetpack Compose 依赖项，请停止。指示用户先迁移到 Jetpack Compose。
4. 如果项目导入 `androidx.compose.material.MaterialTheme`，建议在继续之前迁移到 Material 3。

### 第 2 步：建立 `ComponentStyles`

1. 在您的主题目录中创建一个名为 `ComponentStyles.kt` 的新文件。
2. 定义一个顶层数据类来保存您的组件样式，例如 Jetsnack 的样式称为 `JetsnackStyles`：

```kotlin
object ExampleComponentStyles {
    val customButtonStyle: Style = {

    }
    val customTextFieldStyle: Style = {

    }
}
```

<br />

3. 通过自定义主题以静态引用的方式暴露此类，此处不需要使用 `CompositionLocals`。

```kotlin
@Immutable
class JetsnackTheme(
    // 其他 Design system 属性
) {
    companion object {
        val colors: CustomThemingWithStyles.JetsnackColors
            @Composable @ReadOnlyComposable
            get() = LocalJetsnackTheme.current.colors
        // ...

        // 添加辅助静态引用
        val styles: ComponentStyles = ComponentStyles
    }
}
```

<br />

4. 在 `StyleScope` 上提供扩展，以直接引用使用 `CompositionLocals` 暴露的主题令牌。例如：

```kotlin
val StyleScope.colors: JetsnackColors
    get() = LocalJetsnackTheme.currentValue.colors

val StyleScope.typography: androidx.compose.material3.Typography
    get() = LocalJetsnackTheme.currentValue.typography

val StyleScope.shapes: Shapes
    get() = LocalJetsnackTheme.currentValue.shapes
```

<br />

### 第 3 步：将组件迁移到样式 API

对于每个自定义组件（例如 `CustomButton`），完成以下步骤：

1. **建立视觉基线（如果可用模拟器）：**
   - **如果您不能运行 Android 模拟器：** 完全跳过此步骤，然后继续第 2 步。
   - **如果您可以运行 Android 模拟器：** 执行以下操作以捕获基线屏幕截图：
     - **选项 A：** 定位并运行组件的现有屏幕截图测试。
     - **选项 B（如果不存在测试）：** 使用项目的现有测试框架创建一个测试，然后运行它。
     - **选项 C（如果不存在框架）：** 使用 UI Automator 或 Espresso 创建一个最小的屏幕截图测试，然后运行它。
2. **移除单个样式参数**：从函数签名中移除样式参数，例如 `backgroundColor`、`shape`、`textStyle` 和 `contentPadding` - 任何 `StyleScope` 支持的参数。
3. **添加样式参数**：将 `style: Style = Style` 添加到函数签名中。始终确保默认值是确切的 `Style`（例如，`style: Style = Style`），而不是特定的样式默认值，如 `ChipStyleDefault` 或任何其他值。
4. **声明状态跟踪**：如果组件是可交互的，使用交互源创建一个 `MutableStyleState`。在 Composable 内部更新状态字段（例如 `isEnabled`）以正确跟踪状态。
5. **应用样式修饰符**：用 `Modifier.styleable()` 替换根元素上的特定布局修饰符。
6. **将默认值移至 `ComponentStyles`**：将组件定义中的硬编码值移动到 `ComponentStyles.kt` 中的专用 `Style` 实例。
7. **验证组件**：将开始时捕获的基线屏幕截图图像与新的 Composable 的 Compose 预览渲染进行比较。忽略字符串内容；关注布局和样式。在 Compose 代码上进行迭代，直到达到视觉一致性。验证后，为新的 Composable 编写一个 Compose UI 测试。

#### 迁移示例

迁移前：

```kotlin
@Composable
fun CustomButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    backgroundColor: Color = JetsnackTheme.colors.brandLight,
    disabledBackgroundColor: Color = JetsnackTheme.colors.brandSecondary,
    shape: Shape = JetsnackTheme.shapes.extraLarge,
    textStyle: TextStyle = JetsnackTheme.typography.labelLarge,
    enabled: Boolean = true,
    content: @Composable RowScope.() -> Unit,
) {
    val interactionSource = remember { MutableInteractionSource() }
    Row(
        modifier
            .clickable(onClick = onClick, indication = null, interactionSource = interactionSource)
            .background(if (enabled) backgroundColor else disabledBackgroundColor, shape)
            .defaultMinSize(58.dp, 40.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}
```

<br />

迁移后：

```kotlin
// 通过 ComponentStyles.kt 暴露
object ComponentStyles {
    val buttonStyle = Style {
        background(colors.brandLight)
        shape(shapes.extraLarge)
        minWidth(58.dp)
        minHeight(40.dp)
        textStyle(typography.labelLarge)
        disabled {
            background(colors.brandSecondary)
        }
    }
}

@Composable
fun CustomButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: Style = Style,
    enabled: Boolean = true,
    content: @Composable RowScope.() -> Unit,
) {
    val interactionSource = remember { MutableInteractionSource() }
    val styleState = rememberUpdatedStyleState(interactionSource) {
        it.isEnabled = enabled
    }
    Row(
        modifier
            .clickable(onClick = onClick, indication = null, interactionSource = interactionSource)
            .styleable(styleState, JetsnackTheme.styles.buttonStyle, style),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
        content = content,
    )
}
```

<br />

### 第 4 步：验证更改

1. 构建项目。验证没有编译错误。
2. 运行您的模块的屏幕截图测试。
3. 比较先前和更新组件的整个应用程序的视觉输出。验证没有视觉布局回归。
