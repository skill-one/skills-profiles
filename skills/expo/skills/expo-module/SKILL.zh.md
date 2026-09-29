---
name: expo-module
description: 框架（开源）。使用Expo Modules API（Swift、Kotlin、TypeScript）创建和编写Expo原生模块和视图的指南。涵盖模块定义DSL、原生视图、共享对象、配置插件、生命周期钩子、自动链接和类型系统。在构建或修改Expo原生模块时使用。不适用于将现有的Swift模块从定义DSL迁移到Expo Modules API 2.0宏；此时请使用expo-migrate-module（来自expo-experiments插件）。
---

# 编写 Expo 模块

使用 Expo 模块 API 构建原生模块和视图的完整参考。涵盖 Swift (iOS)、Kotlin (Android) 和 TypeScript。

## 何时使用

- 创建新的 Expo 原生模块或原生视图
- 为 Expo 应用添加原生功能（相机、传感器、系统 API）
- 封装平台 SDK 以供 React Native 使用
- 构建修改原生项目文件的配置插件
- 为现有的 Expo 模块添加 Android、Apple 或 Web 支持
- 编辑 `expo-module.config.json`、配置插件或生命周期钩子

要将现有的 Swift 模块从定义 DSL 迁移到 Expo 模块 API 2.0 宏 (`@ExpoModule`、`@JS`、`@Event`)，请使用 `expo-migrate-module` 功能（来自 `expo-experiments` 插件）。

## 参考

根据需要查阅这些资源：

```
references/
  create-expo-module.md      模板和 add-platform-support 工作流、默认值和特殊情况
  native-module.md           模块定义 DSL：名称、函数、AsyncFunction、属性、常量、事件、类型系统、共享对象
  native-view.md             原生视图组件：视图、属性、事件调度器、视图生命周期、基于引用的函数
  lifecycle.md               生命周期钩子：模块、iOS 应用/AppDelegate、Android 活动应用程序监听器
  config-plugin.md           配置插件：修改 Info.plist、AndroidManifest.xml、在原生代码中读取值
  module-config.md           expo-module.config.json 字段、文件位置和自动链接行为
```

## 快速入门

优先使用 `create-expo-module` 而不是手动创建原生模块文件和目录。在实践中，通常的最佳路径是先创建模板，然后在其基础上进行构建。模板会设置预期的布局、`expo-module.config.json`、podspec 或 Gradle 文件、TypeScript 绑定和独立的示例应用流程。

如果现有的 Expo 模块只需要另一个平台，请使用 `create-expo-module add-platform-support` 而不是手动复制原生目录。

在模板化或扩展模块之前，请参阅 [references/create-expo-module.md](references/create-expo-module.md)。它涵盖了：

- 本地模块与独立模块
- `--platform`、`--features`、`--barrel`、`--package-manager` 和非交互模式
- `expo.autolinking.nativeModulesDir`
- `add-platform-support` 行为和特殊情况

## 推荐工作流程

1. 首先选择模板类型：
   - **本地模块**用于单个应用
   - **独立模块**用于重用、单仓库或发布
2. 确定您需要的原生 `expo-module` 功能。
   - 根据用户指令确定哪些功能模板化将是有用的。
   - 可用功能：`Constant`、`Function`、`AsyncFunction`、`Event`、`View`、`ViewEvent`、`SharedObject`
3. 故意模板化：
   - 传递显式的 slug 或路径
   - 有意选择 `--platform` 而不是依赖默认值
   - 使用 `--features` 选择代码示例，您将在下一步中修改以匹配实际实现。
4. 用实际实现替换生成的示例代码。
5. 如果您稍后添加了新平台，请优先使用 `add-platform-support` 而不是手动文件复制。

## 实用模板化规则

- 功能示例是**可选**的。如果未选择任何功能，新模板化的模块可能非常简略。
- `ViewEvent` 意味着 `View`。
- 本地模块默认情况下**不**生成 `index.ts` 巴雷尔。如果您需要，才使用 `--barrel`。
- 在非交互式本地模板化中，显式传递位置 slug 或路径。`--name` 修改原生类名，而不是文件夹名。
- 本地模块在配置时位于 `expo.autolinking.nativeModulesDir`，否则位于 `modules/`。
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
如果您在模板化中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-module" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 功能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
