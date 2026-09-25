## 第一步：分析当前的测试设置

要了解现有项目的测试设置，请在 `libs.versions.toml` 文件或构建文件中查找以下依赖项：

1. 使用的依赖注入框架。例如：Hilt、Koin、Anvil、纯 Dagger 等。
2. 该项目使用的单元（本地）测试框架。例如 JUnit4、JUnit5 等。
3. 用于单元测试、Instrumented 测试和 UI 测试的模拟框架（如果有）。例如：Mockito、Mockk 等。
4. Robolectric。它可以以三种方式使用：
   1. 用于单元测试以获取平台实体的伪造对象。
   2. 无需设备或模拟器即可运行行为 UI 测试。例如，用于运行 Espresso 或 Compose 测试。
   3. 使用 Roborazzi 进行截图测试。
5. 应用程序是 100% Compose、Views 还是混合的？
6. 行为 UI 测试：
   1. Compose 测试 (`androidx.compose.ui:ui-test-*`)
   2. Views 的 Espresso 测试。可能使用 Kaspresso 等包装器。依赖项：`androidx.test.espresso:espresso-core`、`androidx.test:runner`、`androidx.test:rules`。
7. 截图测试可以是：
   1. Instrumented（基于设备）。例如，使用 Dropshots。
   2. 基于 Robolectric，因此它们在本地运行。例如，使用 Roborazzi。
   3. 基于 LayoutLib，因此它们在本地运行。例如，Paparazzi 或 Compose 预览截图测试工具。
8. 端到端测试（也称为 Release Candidate 测试）始终在设备上运行，并使用高级框架，例如 UIAutomator、Appium 或 Robotium。
9. 生成一个包含分析结果的 Markdown 报告

## 第二步：为测试设置依赖注入框架

如果没有依赖注入框架，请安装一个：如果是多平台应用程序，请询问用户是否要安装 Koin 或 kotlin-inject。如果不是多平台应用程序，请安装 Hilt。

安装测试依赖项（例如 `com.google.dagger:hilt-compiler`，应使用 `kspAndroidTest` 配置应用）。

> [!IMPORTANT]
> **重要提示**：始终查阅相关框架的文档以了解有关测试的信息（例如：[Hilt 测试指南](references/android/training/dependency-injection/hilt-testing.md)、[Koin Instrumented 测试](https://insert-koin.io/docs/reference/koin-android/instrumented-testing))。

对于 Instrumented 测试，创建并配置（通过在构建 gradle 文件中添加 `testInstrumentationRunner`）一个新的测试运行器，并应用框架所需的测试规则（例如，在 Hilt 中，用 `@HiltAndroidTest` 注解您的测试类，并应用 `HiltAndroidRule`）。其他框架使用其他机制，请查阅其文档。

## 第三步：安装框架

除非另有说明，否则尊重当前的测试框架堆栈。

如果不存在测试框架，并且用户没有指定任何偏好，请安装以下内容：

- 用于本地和 Instrumented 测试的 JUnit4
- 用于测试覆盖率的 Jacoco
- 对于 UI 测试：如果项目有 Views，则使用 Espresso。如果它是完全 Compose 的，请使用 Compose 测试 API。
- 使用 Robolectric 运行 UI 测试
- 使用 Compose 预览截图测试工具进行截图测试 - 查看 [设置文档](references/android/studio/preview/compose-screenshot-testing.md) 并严格遵循它。
- 使用 Dropshots 进行设备截图测试
- 如果需要模拟框架，请安装 Mockk (`io.mockk:mockk`)。除非有明确的必要性，否则不要安装它。

如果请求 Instrumented 截图测试，请安装 Dropshots。

如果请求端到端测试，请安装 UI Automator。

## 第四步：重构并创建用于测试的伪造对象

### **为单元测试重构**

在接下来的部分中，您将被要求创建测试。如果您依赖于 Android 框架类，或者实体不属于代码库：

- 首先，使用一个伪造对象。如果不存在，请为该类创建一个接口和一个“默认”实现，其中包含现有代码。将伪造版本添加到测试源集（test 或 androidTest）。

- 如果无法使用伪造对象（例如：无法访问类或接口），请模拟依赖项。

### **为 UI 测试重构**

如果您需要伪造组件以使测试更简单、更快、更可靠，请用伪造对象替换慢速和有问题的依赖项。使用安装的依赖注入框架使用运行时伪造对象：

- **模拟**不同的用户场景（错误的凭据、重置密码流程等）、服务器（无连接、服务器宕机、来自服务器的错误 JSON）或平台组件（权限不足、磁盘空间不足、前置摄像头不可用）
- **提高**速度和可靠性（用内存数据库替换数据库、用内存伪造对象替换仓库以避免访问网络）

## 第五步：单元测试

为包含业务逻辑的每个文件（ViewModels、Repositories、与数据库相关的类（例如 DAOs）等）创建一个任务以添加或审查单元测试。不要为 Activities、Compose 布局或依赖注入配置文件创建单元测试。

## 第六步：UI 测试

Espresso 或 Compose UI 测试位于 `test` 源集中，因为它们将使用 Robolectric 运行。如果请求 Instrumented（模拟器或设备）测试，请将它们放在 `androidTest` 源集中。

## 第七步：测试数据库

如果数据库使用 SQLite（使用 Room、SQLDelight 等），请使用内存数据库创建 Instrumented 测试，以确保它们在设备上与 SQLite 引擎兼容。

## 第八步：截图测试

无论使用哪个框架，截图测试都关注两种类型的测试：

- 屏幕级别的截图测试，其中每个屏幕在 9 种不同的大小下进行测试，结合紧凑、中等和扩展宽度（400、610、900 dp）和高度（400、500 和 1000 dp）。
- 屏幕级别的变化。添加一个移动（400x500）截图：
  - 如果使用所有替代主题。
  - 字体缩放设置为 1.5。
- 组件级别的截图测试，其中每个组件在不同主题和字体缩放下进行测试。

行为不会用截图测试，但请测试不同常见场景，如果它们的 UI 依赖于状态变化很大。例如，通过向 UI 注入加载状态或使用伪造对象模拟它来测试加载屏幕。

## 第九步：UI 行为测试

使用行为测试测试 UI 逻辑，这确保了当传递不同的状态以及执行用户操作时，UI 会按预期反应。

### **Compose UI 行为测试**

- 使用 `ComponentActivity` 和 ComposeTestRule 访问资源，例如字符串。
- 始终首先尝试使用语义匹配器。如果编写匹配器过于复杂（使用超过 3 个匹配器来查找单个元素），请使用 `testTag`。
- 始终验证状态恢复

### **Views (XML) UI 行为测试**

使用 Espresso 匹配视图并与它们交互。

## 第十步：导航测试

创建一个测试套件以验证导航逻辑。包括：

- 后退处理
- 深链接
- 特殊模式，如“通过主屏幕退出”，具有多个后退堆栈。

## 第十一步：模拟不同的窗口大小和设置

对于 Compose 布局，使用 "[UI 测试常见模式](references/android/develop/ui/compose/testing/common-patterns.md)" 中描述的 `DeviceConfigurationOverride` 来模拟不同的窗口大小、字体缩放

## 第十二步：端到端测试

创建少量（约 5% 的所有测试）端到端测试，涵盖大的用户旅程。使用 Compose 测试 API 或 Espresso。如果您必须访问平台功能（通知、系统 UI 等），请使用 UI Automator。

如果您需要在设备上运行的应用程序中截图，请使用 [Dropshots](https://raw.githubusercontent.com/dropbox/dropshots/refs/heads/main/README.md)。在验证与系统 UI 的交互时（例如：边缘到边缘渲染、通知、画中画），您需要一个设备进行截图测试

### 第十三步：Instrumented 截图测试

在模块中安装 `com.dropbox.dropshots` 插件和一个 `Dropshots()` JUnit 规则。为应用程序的一个功能创建一个新的 Instrumented 截图测试。

### 第十四步：安装 jacoco

为本地测试代码覆盖率安装 jacoco。

- 将 `jacoco` 插件添加到包含测试的每个模块。

## 最后步骤

- 询问是否要记录分析结果和应用于测试策略的更改。如果用户同意：

  - 如果项目中存在 `AGENTS.md` 文件，请使用您对测试策略所做的任何更改更新它。

  - 如果没有 `AGENTS.md` 文件，请创建一个新文件（docs/testing.md），其中包含测试策略的描述，包括运行每种类型测试所需的命令、截图参考文件的位置等。还创建一个根目录中的新 `AGENTS.md` 文件，并创建一个到 `docs/testing.md` 的链接。
