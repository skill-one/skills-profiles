# Apple 文档路由器

Apple 将面向 LLM 的 markdown 文档捆绑在 Xcode 中。这些是苹果工程师编写的权威、最新的指南和诊断信息。直接使用 Claude Code 的原生 **`Read`** 工具阅读它们——无需 MCP 服务器或特殊工具。

## 使用场景

- 您需要苹果的精确 API 签名或行为
- 一个 Axiom 技能引用了苹果框架，并且您需要官方来源
- 一个 Swift 编译器诊断需要解释
- 用户询问关于特定苹果框架功能

**优先级**：Axiom 技能提供主观指导（决策树、反模式、压力场景）。苹果文档提供权威的 API 详细信息。将两者结合使用。

## 如何阅读这些文档

会话启动钩子解析 Xcode 的位置，并将字面基目录回显到会话上下文中（查找“Apple for-LLM 文档：Xcode 检测到于 `<路径>`”）。使用 **`Read`** 工具与 `<那个基目录>/<文件名>`。

默认 Xcode 位置（`/Applications/Xcode.app`）的基目录：

| 内容 | 基目录 |
|---|---|
| AdditionalDocumentation 指南 | `/Applications/Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/AdditionalDocumentation/` |
| Swift 编译器诊断 | `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/share/doc/swift/diagnostics/` |

Claude 应该生成的示例调用：

```
Read /Applications/Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/AdditionalDocumentation/SwiftUI-Implementing-Liquid-Glass-Design.md
```

Xcode-beta 用户：会话启动钩子尊重 `AXIOM_XCODE_PATH` 并在会话上下文中报告解析的路径——使用那个路径，而不是上面的默认路径。

## 指南文件（AdditionalDocumentation）

20 个文件。使用路径模式 `{guides base}/{文件名}` 阅读它们。

### UI & 设计

| 主题 | 文件名 |
|---|---|
| SwiftUI 中的 Liquid Glass | `SwiftUI-Implementing-Liquid-Glass-Design.md` |
| UIKit 中的 Liquid Glass | `UIKit-Implementing-Liquid-Glass-Design.md` |
| AppKit 中的 Liquid Glass | `AppKit-Implementing-Liquid-Glass-Design.md` |
| WidgetKit 中的 Liquid Glass | `WidgetKit-Implementing-Liquid-Glass-Design.md` |
| SwiftUI 新的 toolbar 功能 | `SwiftUI-New-Toolbar-Features.md` |
| SwiftUI 样式化文本编辑 | `SwiftUI-Styled-Text-Editing.md` |
| SwiftUI WebKit 集成 | `SwiftUI-WebKit-Integration.md` |
| SwiftUI AlarmKit 集成 | `SwiftUI-AlarmKit-Integration.md` |
| Swift Charts 3D 可视化 | `Swift-Charts-3D-Visualization.md` |
| Foundation AttributedString 更新 | `Foundation-AttributedString-Updates.md` |

### 数据 & 持久化

| 主题 | 文件名 |
|---|---|
| SwiftData 类继承 | `SwiftData-Class-Inheritance.md` |

### 并发 & 性能

| 主题 | 文件名 |
|---|---|
| Swift 并发更新 | `Swift-Concurrency-Updates.md` |
| InlineArray 和 Span | `Swift-InlineArray-Span.md` |

### Apple Intelligence

| 主题 | 文件名 |
|---|---|
| Foundation Models（设备端 LLM） | `FoundationModels-Using-on-device-LLM-in-your-app.md` |

### 系统集成

| 主题 | 文件名 |
|---|---|
| App Intents 更新 | `AppIntents-Updates.md` |
| StoreKit 更新 | `StoreKit-Updates.md` |
| MapKit GeoToolbox PlaceDescriptors | `MapKit-GeoToolbox-PlaceDescriptors.md` |
| visionOS 的 Widgets | `Widgets-for-visionOS.md` |

### 可访问性

| 主题 | 文件名 |
|---|---|
| iOS 中的 Assistive Access | `Implementing-Assistive-Access-in-iOS.md` |

### 计算机视觉

| 主题 | 文件名 |
|---|---|
| iOS 中的 Visual Intelligence | `Implementing-Visual-Intelligence-in-iOS.md` |

## Swift 编译器诊断

诊断目录中有 46 个文件。使用路径模式 `{diagnostics base}/{文件名}` 阅读它们。

### 并发诊断

| 诊断 | 文件名 |
|---|---|
| 从非隔离上下文调用 actor-isolated | `actor-isolated-call.md` |
| 合规隔离 | `conformance-isolation.md` |
| 隔离的合规性 | `isolated-conformances.md` |
| 默认情况下非隔离的非发送 | `nonisolated-nonsending-by-default.md` |
| 可发送闭包捕获 | `sendable-closure-captures.md` |
| 可发送元类型 | `sendable-metatypes.md` |
| 显式可发送注释 | `explicit-sendable-annotations.md` |
| 发送闭包有数据竞争风险 | `sending-closure-risks-data-race.md` |
| 发送有数据竞争风险 | `sending-risks-data-race.md` |
| 可变全局变量 | `mutable-global-variable.md` |
| Preconcurrency 导入 | `preconcurrency-import.md` |
| 动态排他性 | `dynamic-exclusivity.md` |
| 排他性违规 | `exclusivity-violation.md` |

### 类型系统诊断

| 诊断 | 文件名 |
|---|---|
| 存在性 any | `existential-any.md` |
| 存在性成员访问限制 | `existential-member-access-limitations.md` |
| 普通类型 | `nominal-types.md` |
| 多重继承 | `multiple-inheritance.md` |
| 协议类型非合规 | `protocol-type-non-conformance.md` |
| 不透明类型推断 | `opaque-type-inference.md` |
| 外部引用类型 | `foreign-reference-type.md` |

### 构建与迁移诊断

| 诊断 | 文件名 |
|---|---|
| 已弃用的声明 | `deprecated-declaration.md` |
| 未来 Swift 版本中的错误 | `error-in-future-swift-version.md` |
| 严格语言功能 | `strict-language-features.md` |
| 严格内存安全 | `strict-memory-safety.md` |
| 仅实现已弃用 | `implementation-only-deprecated.md` |
| 成员导入可见性 | `member-import-visibility.md` |
| 已知路径上缺少模块 | `missing-module-on-known-paths.md` |
| 模块不可测试 | `module-not-testable.md` |
| 缺少模块版本 | `module-version-missing.md` |
| Clang 声明导入 | `clang-declaration-import.md` |
| 可用性未识别名称 | `availability-unrecognized-name.md` |
| 总是可用的域 | `always-available-domain.md` |
| 即将推出的语言功能 | `upcoming-language-features.md` |
| 未知警告组 | `unknown-warning-group.md` |
| 编译缓存 | `compilation-caching.md` |
| 嵌入限制 | `embedded-restrictions.md` |

### Swift 语言诊断

| 诊断 | 文件名 |
|---|---|
| 动态可调用要求 | `dynamic-callable-requirements.md` |
| 属性包装器要求 | `property-wrapper-requirements.md` |
| 结果构建器方法 | `result-builder-methods.md` |
| 字符串插值合规性 | `string-interpolation-conformance.md` |
| 闭包匹配 | `trailing-closure-matching.md` |
| 临时指针 | `temporary-pointers.md` |
| 语义副本 | `semantic-copies.md` |
| 性能提示 | `performance-hints.md` |

### 索引

| 诊断 | 文件名 |
|---|---|
| 诊断组（分类学） | `diagnostic-groups.md` |
| 所有诊断索引 | `diagnostics.md` |

如果您需要上面未列出的诊断，请首先列出诊断目录：

```
ls $AXIOM_XCODE_PATH/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/share/doc/swift/diagnostics/
```

文件名遵循诊断的短名称（小写、连字符）。

## 路由决策树

```
用户关于 Apple API/框架的问题？
├── 具体的编译器错误/警告 → Read {diagnostics base}/<诊断名称>.md
├── Liquid Glass 实现     → Read {guides base}/<框架>-Implementing-Liquid-Glass-Design.md
├── Swift 并发模式      → Read {guides base}/Swift-Concurrency-Updates.md
├── Foundation Models / 设备端 AI → Read {guides base}/FoundationModels-Using-on-device-LLM-in-your-app.md
├── SwiftData 功能              → Read {guides base}/SwiftData-Class-Inheritance.md
├── StoreKit / IAP                  → Read {guides base}/StoreKit-Updates.md
├── App Intents / Siri              → Read {guides base}/AppIntents-Updates.md
├── Charts / 可视化          → Read {guides base}/Swift-Charts-3D-Visualization.md
├── 文本编辑 / AttributedString → Read {guides base}/SwiftUI-Styled-Text-Editing.md 或 Foundation-AttributedString-Updates.md
├── WebKit in SwiftUI               → Read {guides base}/SwiftUI-WebKit-Integration.md
├── Toolbar 功能                → Read {guides base}/SwiftUI-New-Toolbar-Features.md
└── 其他                           → ls 基目录以查看可用内容
```

## Xcode 不可用时回退

如果 `AXIOM_XCODE_PATH` 未设置，或者路径不存在，或者 `IDEIntelligenceChat.framework` 目录缺失（旧版 Xcode），回退到：

1. **sosumi.ai**（developer.apple.com 的 markdown 镜像——参见 `skills/apple-docs-research.md`）
2. **WebFetch** 对应的 developer.apple.com URL
3. **建议**安装最新 Xcode 以获得完整的 Apple 文档覆盖范围

不要无声失败——当本地 Xcode 文档不可用时，告诉用户您使用的回退方法。

## MCP 便利路径

使用 axiom-mcp 的客户端也可以使用 `axiom_read_skill` 并用旧 ID（例如，`apple-guide-swiftui-implementing-liquid-glass-design`）。MCP 服务器读取相同的 Xcode 文件并返回相同的内容。两种路径都受支持——文件-Read 路径适用于所有地方；MCP 路径是针对目录/搜索工作流程的便利方法。

## 研究方法

有关 WWDC 文本捕获（Chrome 自动捕获）、sosumi.ai 文档访问和多会话研究工作流，请参阅 [skills/apple-docs-research.md](skills/apple-docs-research.md)。

## 资源

**技能**：axiom-swiftui, axiom-concurrency, axiom-data, axiom-ai, axiom-integration
