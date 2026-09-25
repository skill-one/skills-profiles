# iOS Swift 开发

## 目录

- [概述](#概述)
- [何时使用](#何时使用)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

使用 Swift 和现代框架（包括 SwiftUI、Combine 以及 async/await 模式）构建高性能原生 iOS 应用程序。

## 何时使用

- 创建具有最佳性能的原生 iOS 应用程序
- 利用 iOS 特定功能和 API
- 构建需要紧密硬件集成的应用程序
- 使用 SwiftUI 进行声明式 UI 开发
- 实现复杂的动画和过渡效果

## 快速入门

最小可工作示例：

```swift
import Foundation
import Combine

struct User: Codable, Identifiable {
  let id: UUID
  var name: String
  var email: String
}

class UserViewModel: ObservableObject {
  @Published var user: User?
  @Published var isLoading = false
  @Published var errorMessage: String?

  private let networkService: NetworkService

  init(networkService: NetworkService = .shared) {
    self.networkService = networkService
  }

  @MainActor
  func fetchUser(id: UUID) async {
    isLoading = true
    errorMessage = nil

// ... (参考指南中查看完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [MVVM 架构设置](references/mvvm-architecture-setup.md) | MVVM 架构设置 |
| [使用 URLSession 的网络服务](references/network-service-with-urlsession.md) | 使用 URLSession 的网络服务 |
| [SwiftUI 视图](references/swiftui-views.md) | SwiftUI 视图 |

## 最佳实践

### ✅ 应该

- 使用 SwiftUI 进行现代 UI 开发
- 实现 MVVM 架构
- 使用 async/await 模式
- 将敏感数据存储在 Keychain 中
- 优雅地处理错误
- 使用 @StateObject 为 ViewModel
- 正确验证 API 响应
- 实现持久化存储 Core Data
- 在多个 iOS 版本上测试
- 使用依赖注入
- 遵循 Swift 代码风格指南

### ❌ 不应该

- 将令牌存储在 UserDefaults 中
- 在主线程上进行网络请求
- 使用已弃用的 UIKit 模式
- 忽略内存泄漏
- 忽略错误处理
- 使用强制解包 (!)
- 将密码存储在代码中
- 忽略无障碍功能
- 部署未经测试的代码
- 使用硬编码的 API URL
