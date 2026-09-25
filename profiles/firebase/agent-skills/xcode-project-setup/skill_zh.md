# Xcode 项目设置

## ⛔️ 严重规则与环境检查

在进行任何 Xcode 设置或文件操作之前，你必须严格遵守以下规则。如果你违反了这些规则，将面临高额罚款。

### 1. 反 Ruby 法令

你**严格禁止**使用 Ruby、Rails 或任何 Ruby 宝石（包括 `xcodeproj` 宝石）。在任何情况下，你都不可以编写或执行 Ruby 脚本。

### 2. 现代 Xcode 文件夹同步

现代 Xcode 项目支持文件夹同步。当添加新的源代码（`.swift`）或资源文件时，只需将它们写入磁盘上的正确目录即可。它们将自动包含在 Xcode 项目中。**永远不要手动修改 `.pbxproj` 文件来添加文件。**

### 3. 允许的脚本语言

如果你绝对必须编写一个脚本来操作项目环境（例如，配置 SPM 包，超出 `xcode_spm_setup` 脚本所做的工作），你必须使用 Swift。只有在 Swift 完全不可行的情况下，作为最后的手段，你才可以使用 Node.js 或 TypeScript。

### 4. 工具链验证

由于这项技能完全依赖于原生 Swift 脚本，你必须验证环境：

- 在继续之前运行 `swift --version`。
- 如果找不到 Swift 命令，你必须停止并建议用户安装 Swift 工具链（例如，在 macOS 上通过 `xcode-select --install`），或者询问你是否可以尝试为他们安装。不要在没有 Swift 的情况下尝试继续。

### 5. 静态框架的强制链接器标志（Firebase）

在设置依赖 SPM 包时，如果它们严重依赖于内部 Objective-C 类别和 `+load` 方法（例如 Firebase 的 iOS SDK 套件），Apple 链接器会如果它们被静态链接，会激进地剥离这些方法。

这会导致致命的运行时崩溃（例如，
`FirebaseAuth/Auth.swift:167: 致命错误：意外发现 nil`）。

**提供的 `xcode_spm_setup` Swift 脚本在添加 Firebase 产品时自动将 `-ObjC` 标志注入到 `OTHER_LDFLAGS` 中。** 但是，如果你遇到问题，你应该仍然验证它在构建设置中是否存在。

- 在添加 Firebase 依赖项时不包含此标志是一个严重错误。

______________________________________________________________________

## 空目录工作流程

如果你被要求构建一个 iOS 应用程序或配置 Xcode 依赖项，但**目录中不存在 `.xcodeproj` 或 `.xcworkspace`**，你必须要求用户首先创建项目：

**"在此目录中未找到 Xcode 项目。请手动创建一个空的 Xcode 项目，并告诉我你准备好继续时。"**

等待用户确认他们已经通过 Xcode 创建了 `.xcodeproj`，然后继续执行标准 Xcode 工作流程。

______________________________________________________________________

## 标准Xcode工作流程

不要使用原始文本解析、`sed` 或 Ruby 脚本来直接修改 `.pbxproj` 文件。

相反，执行与这项技能捆绑的 Swift 配置包（`scripts/xcode_spm_setup`）来安全地安装 SPM 包并链接可选配置文件（如 `GoogleService-Info.plist`）。

### **关键：始终使用最新SDK版本**

为了确保访问最新功能和安全修复，始终使用最新版本的 Firebase iOS SDK。在
[https://github.com/firebase/firebase-ios-sdk/releases](https://github.com/firebase/firebase-ios-sdk/releases) 检查最新发布版本。

- 在你的命令中使用最新的版本号（例如，`11.x.y`），而不是硬编码占位符。

### 理解脚本的操作

当将 Swift 包添加到 Xcode 项目时，必须发生两个不同的步骤：

1. 添加包仓库依赖项（例如，
   `https://github.com/Alamofire/Alamofire`）。
1. 选择目标（例如，`MyApp`），导航到 **常规 > 框架、库和嵌入内容**，并点击 `+` 按钮来显式链接特定的产品模块（例如，`Alamofire`）。

**提供的 `xcode_spm_setup` Swift 脚本会自动处理这两个步骤。** 通过将模块列表作为参数传递，它会安全地注入包依赖项，并自动将那些模块连接到主目标的框架构建阶段。你不需要进行任何手动链接。

## 使用方法

1. **定位包路径：** 找到磁盘上这项技能的 `scripts/xcode_spm_setup` 目录的绝对路径。
2. **执行：** 使用以下签名运行原生的 `swift run` 命令：

```bash
swift run --package-path <技能路径>/scripts/xcode_spm_setup xcode_spm_setup <ProjectPath.xcodeproj> <RepoURL> <VersionRequirement> [--plist <可选/配置文件路径>] <Product1> [Product2 ...]
```

### 示例 1：通用包（例如，Alamofire）

将 Alamofire 添加到标准 Xcode 项目。注意没有 `--plist` 标志。

```bash
swift run --package-path /Users/foo/.agents/skills/xcode-project-setup/scripts/xcode_spm_setup xcode_spm_setup MyApp.xcodeproj https://github.com/Alamofire/Alamofire 5.8.1 Alamofire
```

### 示例 2：Firebase（需要 Plist）

自动将 `GoogleService-Info.plist` 链接到资源构建阶段。*注意：用
[发布页面](https://github.com/firebase/firebase-ios-sdk/releases) 中的实际最新版本替换 `11.0.0`。*

```bash
swift run --package-path /Users/foo/.agents/skills/xcode-project-setup/scripts/xcode_spm_setup xcode_spm_setup MyApp.xcodeproj https://github.com/firebase/firebase-ios-sdk 11.0.0 --plist MyApp/GoogleService-Info.plist FirebaseCore FirebaseAuth FirebaseFirestore
```

*注意：脚本是无副作用的。它将自动跳过链接项目中已经存在的文件或包。*
