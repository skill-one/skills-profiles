# 编写 Expo 模块

使用 Expo 模块 API 构建 native 模块和视图的完整参考。涵盖 Swift (iOS)、Kotlin (Android) 和 TypeScript。

## 何时使用

- 创建新的 Expo native 模块或 native 视图
- 为 Expo 应用添加 native 功能（相机、传感器、系统 API）
- 封装平台 SDK 以供 React Native 使用
- 构建修改 native 项目文件的配置插件
- 为现有的 Expo 模块添加 Android、Apple 或 web 支持
- 编辑 `expo-module.config.json`、配置插件或生命周期钩子

要将现有的 Swift 模块从定义 DSL 迁移到 Expo 模块 API 2.0 宏 (`@ExpoModule`、`@JS`、`@Event`)，请使用 `expo-migrate-module` 功能（来自 `expo-experiments` 插件）。

## 参考

按需查阅这些资源：

```
references/
  create-expo-module.md      Scaffolding 和 add-platform-support 工作流、默认值和特殊情况
  native-module.md           模块定义 DSL：名称、函数、AsyncFunction、属性、常量、事件、类型系统、共享对象
  native-view.md             Native 视图组件：视图、属性、事件调度器、视图生命周期、基于 ref 的函数
  lifecycle.md               生命周期钩子：模块、iOS 应用/AppDelegate、Android activity/application 监听器
  config-plugin.md           配置插件：修改 Info.plist、AndroidManifest.xml、在 native 代码中读取值
  module-config.md           expo-module.config.json 字段、文件位置和自动链接行为
```

## 快速入门

优先使用 `create-expo-module` 而不是手动创建 native 模块文件和目录。在实践中，通常的最佳路径是先创建脚手架，然后在此基础上构建。脚手架会设置预期的布局、`expo-module.config.json`、podspec 或 Gradle 文件、TypeScript 绑定和独立的示例应用流程。

如果现有的 Expo 模块只需要另一个平台，请使用 `create-expo-module add-platform-support` 而不是手动复制 native 目录。

在脚手架或扩展模块之前，请参阅 [references/create-expo-module.md](references/create-expo-module.md)。它涵盖了：

- 本地模块与独立模块
- `--platform`、`--features`、`--barrel`、`--package-manager` 和非交互模式
- `expo.autolinking.nativeModulesDir`
- `add-platform-support` 行为和特殊情况

## 推荐工作流程

1. 首先选择脚手架类型：
   - **本地模块** 用于单个应用
   - **独立模块** 用于重用、单仓库或发布
2. 确定您需要的 native `expo-module` 功能。
   - 根据用户指令确定哪些功能脚手架将是有用的。
   - 可用功能：`Constant`、`Function`、`AsyncFunction`、`Event`、`View`、`ViewEvent`、`SharedObject`
3. 有意地脚手架：
   - 传递显式的 slug 或路径
   - 故意选择 `--platform` 而不是依赖默认值
   - 使用 `--features` 选择代码示例，您将在下一步中修改以匹配实际实现。
4. 用实际实现替换生成的示例代码。
5. 如果您稍后添加了新平台，请优先使用 `add-platform-support` 而不是手动文件复制。

## 实用脚手架规则

- 功能示例是**可选**的。如果未选择任何功能，新脚手架的模块可能非常简略。
- `ViewEvent` 意味着 `View`。
- 本地模块默认情况下**不**生成 `index.ts` 巴雷尔。如果您需要，请仅使用 `--barrel`。
- 在非交互式本地脚手架中，显式传递位置 slug 或路径。`--name` 修改 native 类名，而不是文件夹名。
- 本地模块位于配置的 `expo.autolinking.nativeModulesDir` 中，否则位于 `modules/`。
- 独立模块有自己的包元数据、脚本，并且通常有一个示例应用。本地模块使用宿主应用的工具。

## 核心文件结构

Swift 和 Kotlin DSL 共享相同结构。Swift 通常是更清晰的示例；请参阅参考文档以获取特定功能的详细信息。

## 模块结构参考

Swift 和 Kotlin DSL 共享相同结构。这里展示了两个平台以供参考——在其他参考文件中，除非 Kotlin 模式有显著差异，否则 Swift 会作为主要语言展示。

**Swift (iOS):**

```swift
import ExpoModulesCore

public class MyModule: Module {
  public func definition() -> ModuleDefinition {
    Name("MyModule")

    Function("hello") { (name: String) -> String in
      return "Hello \(name)!"
    }
  }
}
```

**Kotlin (Android):**

```kotlin
package expo.modules.mymodule

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class MyModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("MyModule")

    Function("hello") { name: String ->
      "Hello $name!"
    }
  }
}
```

**TypeScript:**

```typescript
import { requireNativeModule } from "expo";

const MyModule = requireNativeModule("MyModule");

export function hello(name: string): string {
  return MyModule.hello(name);
}
```

### expo-module.config.json

```json
{
  "platforms": ["android", "apple"],
  "apple": {
    "modules": ["MyModule"]
  },
  "android": {
    "modules": ["expo.modules.mymodule.MyModule"]
  }
}
```

注意：iOS 仅使用类名；Android 使用完全限定类名（包 + 类）。请参阅 `references/module-config.md` 获取所有字段。

## 提交反馈
如果您在当前技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-module" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
