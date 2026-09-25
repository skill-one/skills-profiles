这项技能指导您将现有的 Android XML 视图迁移到 Jetpack Compose。它通过遵循结构化的、10 步的方法论，执行稳定、安全且视觉一致的转换。这项技能仅迁移 UI（从 XML 到 Jetpack Compose）。

## 目标

系统地转换单个遗留 XML 布局为现代的、声明式的 Jetpack Compose UI，同时保持像素级完美的视觉一致性和功能完整性。

## 10 步迁移过程的摘要

1. **确定最佳的迁移 XML 候选**
2. **分析项目和布局**
3. **创建计划**
4. **捕获 XML 视图 UI**
5. **设置 Compose 依赖项和编译器**
6. **设置 Compose 主题**
7. **将 XML 布局迁移到 Compose**
8. **验证迁移**
9. **替换使用**
10. **删除 XML 代码**

## 详细步骤

### 第 1 步：确定最佳的迁移 XML 候选

如果用户明确指定了目标 XML 布局，请继续执行第 2 步。否则，通过遵循 [参考资料/确定最佳 XML 候选.md](references/identify-optimal-xml-candidate.md) 中的逻辑，分析代码库以确定最佳的迁移候选。

### 第 2 步：分析项目和布局

分析已识别的 XML 视图的结构、层次结构和实现细节。
使用 [参考资料/分析项目和布局.md](references/analysis-of-the-project-and-layout.md) 来指导您对布局及其周围项目上下文的技术审核。

### 第 3 步：创建计划

使用在第 1 步和第 2 步中生成的输出和分析，为迁移生成逐步计划。如果您支持用户交互，请在继续之前向用户展示并请求批准。如果您不支持用户交互，请按照生成的计划继续执行第 4 步。

### 第 4 步：捕获 XML 视图 UI

**如果**您支持用户交互，请要求用户上传 XML 视图 UI 的截图或提供文件的绝对路径。使用此图像作为第 7 步中布局迁移的视觉参考。
**否则如果**您能够运行 Android 模拟器，定位现有的 XML 候选截图测试。如果不存在，使用现有的项目测试框架创建一个。如果不存在框架，使用 **UI Automator** 或 **Espresso** 创建一个具有最小必要设置的截图测试。运行测试并捕获 XML UI 的基线截图。
**否则**继续执行第 5 步。

### 第 5 步：设置 Compose 依赖项和编译器

检查 `build.gradle` 或 `libs.versions.toml` 中的 Compose 依赖项和编译器设置。如果缺失，使用 [设置 Compose 依赖项和编译器](references/android/develop/ui/compose/setup-compose-dependencies-and-compiler.md)。
运行同步以确保依赖项解析无误。

### 第 6 步：设置 Compose 主题

如果项目已经设置了 Compose 主题，请继续执行第 7 步。如果缺少 Compose 主题，请初始化它。对于基于 Material 的项目，请遵循 [Material 3 迁移指南](references/android/develop/ui/compose/designsystems/migrate-xml-theme-to-compose.md)。对于自定义设计系统，应用专业判断来迁移 XML 主题并匹配现有样式。
**约束条件**：不要迁移整个主题。仅实现特定 XML 候选所需的最小主题。保留原始 XML 主题以实现互操作性。保留现有项目代码约定、模式、名称和值。

### 第 7 步：将 XML 视图迁移到 Compose

将 XML 候选转换为 Jetpack Compose 代码，参考 [参考资料/XML 布局迁移.md](references/xml-layout-migration.md) 和第 4 步中的图像。您必须为新建的 composable 包含一个 **Compose 预览**，以促进视觉验证。

### 第 8 步：替换使用

替换已迁移的 XML 布局的使用，以使用新的 Compose 组件。

- 要在视图中添加 Compose，请使用 [Compose in Views](references/android/develop/ui/compose/migrate/interoperability-apis/compose-in-views.md)。
- 要在 Compose 中添加视图，请使用 [Views in Compose](references/android/develop/ui/compose/migrate/interoperability-apis/views-in-compose.md)。

### 第 9 步：验证迁移

将第 4 步中的基线截图图像与新建 composable 的 Compose 预览渲染结果进行比较。忽略字符串内容；专注于布局和样式。对 Compose 代码进行迭代，直到实现视觉一致性。验证后，为新的 composable 编写 Compose UI 测试。

### 第 10 步：删除 XML 代码

删除已迁移的 XML 文件及其相关的遗留测试。**注意**：仅删除未由项目其他部分引用的代码和资源。
