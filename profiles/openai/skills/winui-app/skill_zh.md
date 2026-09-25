# WinUI 应用

使用此技能处理需要可靠设置指导、应用启动、现代 Windows 用户体验决策或具体实现模式的 WinUI 3 和 Windows App SDK 工作。

## 必要流程

1. 将任务分类为环境/设置、新应用启动、设计、实现、审查或故障排除。
2. 如果任务涉及为 WinUI 准备机器、审计准备情况或创建全新应用，请在更广泛的设计、实现或故障排除工作之前，从本技能捆绑的设置和脚手架流程开始：
   - 当请求创建新应用时，选择应用名称。
   - 当已经是安全的文件夹名称时，使用用户提供的确切名称。
   - 如果用户未提供名称，从请求中派生短小的 PascalCase 名称，并说明您选择的内容。
   - 在用户未要求其他位置的情况下，在用户的当前工作区创建项目。
   - 除非用户明确要求覆盖现有文件，否则不要使用 `--force`。
   - 从技能目录运行捆绑的 WinGet 配置，以使相对路径保持 `config.yaml`：

```powershell
winget configure -f config.yaml --accept-configuration-agreements --disable-interactivity
```

   - 将配置视为旨在启用开发者模式、安装或更新 Visual Studio Community 2026，并安装 WinUI 开发所需的托管桌面、通用和 Windows App SDK C# 组件。
   - 评估配置结果后再继续。成功则继续。如果失败，则检查输出而不是猜测。如果 `winui` 模板已可用且工具链可用，则记录部分失败并继续。如果先决条件仍然缺失，则停止并明确报告阻止因素。
   - 在脚手架之前验证模板是否可用：

```powershell
dotnet new list winui
```

   - 对于仅用于诊断的环境请求，解释捆绑的启动可能会更改机器，并在运行之前获取确认。如果用户拒绝更改，请使用 `references/foundation-environment-audit-and-remediation.md` 中的手动验证指南，并总结准备情况（`present`、`missing`、`uncertain`）和推荐的可选工具。
   - 对于全新应用，使用 `dotnet new winui -o <name>` 进行脚手架。仅在用户要求时才添加模板选项。支持的选项：`-f|--framework net10.0|net9.0|net8.0`、`-slnx|--use-slnx`、`-cpm|--central-pkg-mgmt`、`-mvvm|--use-mvvm`、`-imt|--include-mvvm-toolkit`、`-un|--unpackaged`、`-nsf|--no-solution-file`、`--force`。不要编造不支持的标志。如果用户要求打包行为，请传递 `--unpackaged false`。否则保持模板默认。
   - 通过确认预期的项目文件存在并运行 `dotnet build` 对生成的 `.csproj` 来验证新的脚手架。
   - 通过正确的路径启动新脚手架的应用，并确认存在实际顶级窗口，而不是仅依赖启动器进程退出代码。

3. 阅读 `references/_sections.md`，然后仅加载与任务匹配的参考文件。
4. 在创建或重构应用之前，明确包装模型。对于类似商店的产品工作流程和 Visual Studio 部署/F5 流程，默认为打包。当用户期望可重复的 CLI 构建和运行循环或每次更改后直接 `.exe` 启动时，默认为未打包。
5. 当任务是无形的 XAML 编译器失败（如 `MSB3073` 或 `XamlCompiler.exe`）时，请阅读 `references/foundation-template-first-recovery.md` 并简化回当前为选定包装模型选择的 `dotnet new winui` 脚手架，而不是编造自定义恢复结构。
6. 对于任何创建或更改 WinUI 应用的工作，请进行完整但最小的编辑集，然后构建应用并运行它，再回复用户。即使用户未明确要求验证，也默认执行此操作。如果正在运行的应用实例在更多工作剩余时锁定输出，请停止它、重新构建、重新启动，并继续验证。当工作完成且启动验证成功时，除非用户明确要求，否则请保留最终验证的应用实例运行。
7. 将启动验证视为未完成，直到应用显示客观成功信号，如响应的顶级窗口、预期的窗口标题或其他明确的启动行为。仅生成进程本身是不够的。
8. 优先使用 Microsoft Learn 获取需求、API 预期和平台指导。
9. 优先使用 WinUI Gallery 获取具体控件用法、外壳组合和设计细节。
10. 优先使用 WindowsAppSDK-Samples 获取场景级 API，如窗口、生命周期、通知、部署和自定义控件。
11. 首先面向 WinUI 和 Fluent 指导。将原生 WinUI 外壳、控件、交互和控件边框视为默认实现路径。
12. 对于文档操作、编辑器格式化、视图切换或页面级工具栏等分组命令表面，优先使用原生的 `CommandBar` 或其他标准 WinUI 命令表面，而不是使用 `Grid`、`StackPanel`、`Border` 或临时按钮分组构建自定义行。
13. 除非用户明确要求此定制、现有产品设计系统已要求或验证的平台差距没有干净的本地选项，否则不要编造特定应用的控件、定制的组件库或自定义边框来替代标准 WinUI 行为。
14. 当需要定制时，首先组合、模板或重置内置 WinUI 控件和系统资源，然后再添加 CommunityToolkit 依赖项或编写新的自定义控件。
15. 仅当内置 WinUI 控件或辅助工具无法清晰覆盖需求时，才使用 CommunityToolkit。
16. 默认支持亮色和暗色模式。将单主题输出视为需要明确用户请求或现有产品约束的例外。
17. 在构建或修订 UI 时，使用主题感知资源、系统画刷和 WinUI 样式钩子，而不是硬编码仅亮色或仅暗色的颜色。
18. 为集合布局明确滚动所有权。当页面已经垂直滚动时，不要假设嵌套的 `GridView` 或其他拥有滚动的集合仍能正确渲染水平海报轨道。
19. 除非边框正在执行包含控件或父表面未提供的独特工作，否则不要在区域、列表或卡片周围添加额外的 `Border` 包装。避免“双卡片”组合，其中区域 `Border` 包装已渲染为卡片的子项。
20. 将响应性视为外壳加页面的问题，而不仅仅是控件缩放问题。为导航、填充、内容密度和页脚/工具区域计划明确的宽、中、手机宽度行为，并在宽度缩小时简化或隐藏非必要 UI。

## 常见路径

| 请求 | 首先阅读 |
| --- | --- |
| 检查此 PC 是否可以构建 WinUI 应用 | `references/foundation-environment-audit-and-remediation.md` |
| 安装缺失的 WinUI 先决条件 | `references/foundation-environment-audit-and-remediation.md` |
| 启动打包或未打包的新应用 | `references/foundation-setup-and-project-selection.md` |
| 从无形的 XAML 编译器或启动失败中恢复，同时锚定到模板脚手架 | `references/foundation-template-first-recovery.md` |
| 构建、运行或验证 WinUI 应用是否实际启动 | `references/build-run-and-launch-verification.md` |
| 审查应用结构、页面、资源和绑定 | `references/foundation-winui-app-structure.md` |
| 选择外壳、导航、标题栏或多窗口模式 | `references/shell-navigation-and-windowing.md` |
| 选择控件或响应式布局模式 | `references/controls-layout-and-adaptive-ui.md` |
| 应用 Mica、主题、排版、图标或 Fluent 样式 | `references/styling-theming-materials-and-icons.md` |
| 改进可访问性、键盘输入或本地化 | `references/accessibility-input-and-localization.md` |
| 诊断响应性或 UI 线程性能 | `references/performance-diagnostics-and-responsiveness.md` |
| 决定是否使用 CommunityToolkit | `references/community-toolkit-controls-and-helpers.md` |
| 处理生命周期、通知或部署 | `references/windows-app-sdk-lifecycle-notifications-and-deployment.md` |
| 运行审查清单 | `references/testing-debugging-and-review-checklists.md` |

## 环境规则

- 不要猜测机器是否准备好进行 WinUI 开发。请验证。
- 使用本技能中的捆绑设置和脚手架流程进行全新设置、修复和第一个项目脚手架，而不是委托给其他技能。
- 将本技能目录中的 `config.yaml` 视为捆绑启动的真实来源。
- 将不确定的环境信号视为不确定，而不是成功。
- 如果任务仅审计且用户拒绝机器更改，请使用 `references/foundation-environment-audit-and-remediation.md` 中的手动验证指南，并保持不确定信号明确，而不是暗示成功。
- 如果 `config.yaml` 缺失，请明确说明并回退到官方 Microsoft 工作流程，而不是假装捆绑路径存在。
- 将环境就绪、包装选择和应用启动验证作为单独的检查。通过一个并不能证明其他。
- 对模糊的启动结果采取封闭失败。如果应用没有明确打开，请继续调试。
- 在创建或编辑 WinUI 应用后，不要在成功构建后停止。启动应用，确认客观启动行为，并在将控制权交还给用户之前保留最终验证的应用实例运行，除非他们明确说不运行它。

## 参考规则

- 保持 C# 作为主要路径。仅在差异实质性时才提及 C++ 或 C++/WinRT。
- 保留现有代码库的约定，而不是将其强加给通用的示例结构。
- 将 WinUI 设计指南和原生控件视为基准。除非用户明确要求或现有代码库已经依赖它们，否则不要偏离定制的组件系统或特定应用的替代标准控件。
- 默认支持亮色和暗色模式，除非用户明确要求单主题结果或产品已经强制执行一个。
- 优先使用内置 WinUI 控件和系统样式钩子，而不是添加 CommunityToolkit 依赖项、自定义控件或特定应用的表面系统。
- 将详细的控件、主题、外壳、滚动、响应性、包装和恢复指南放在匹配的参考文件中，而不是在此处重复这些规则。
