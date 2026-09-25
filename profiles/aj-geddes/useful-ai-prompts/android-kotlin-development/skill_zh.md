# Android Kotlin 开发

## 目录

- [概述](#概述)
- [何时使用](#何时使用)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

使用 Kotlin 结合现代架构模式、Jetpack 库和 Compose 构建健壮的原生 Android 应用程序，实现声明式 UI。

## 何时使用

- 使用最佳实践创建原生 Android 应用程序
- 使用 Kotlin 进行类型安全的开发
- 使用 Jetpack 实现 MVVM 架构
- 使用 Jetpack Compose 构建现代 UI
- 集成 Android 平台 API

## 快速入门

最小可运行示例：

```kotlin
// 模型
data class User(
  val id: String,
  val name: String,
  val email: String,
  val avatarUrl: String? = null
)

data class Item(
  val id: String,
  val title: String,
  val description: String,
  val imageUrl: String? = null,
  val price: Double
)

// 使用 Retrofit 的 API 服务
interface ApiService {
  @GET("/users/{id}")
  suspend fun getUser(@Path("id") userId: String): User

  @PUT("/users/{id}")
  suspend fun updateUser(
    @Path("id") userId: String,
    @Body user: User
// ... (参考指南中查看完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [模型 & API 服务](references/models-api-service.md) | 模型 & API 服务 |
| [使用 Jetpack 的 MVVM ViewModels](references/mvvm-viewmodels-with-jetpack.md) | 使用 Jetpack 的 MVVM ViewModels |
| [Jetpack Compose UI](references/jetpack-compose-ui.md) | Jetpack Compose UI |

## 最佳实践

### ✅ 应该

- 所有新的 Android 代码使用 Kotlin
- 使用 Jetpack 库实现 MVVM
- 使用 Jetpack Compose 进行 UI 开发
- 利用协程进行异步操作
- 使用 Room 进行本地数据持久化
- 实现适当的错误处理
- 使用 Hilt 进行依赖注入
- 使用 StateFlow 进行响应式状态管理
- 在多种设备类型上测试
- 遵循 Android 设计指南

### ❌ 不应该

- 将令牌存储在 SharedPreferences 中
- 在主线程上进行网络请求
- 忽略生命周期管理
- 跳过空安全检查
- 硬编码字符串和资源
- 忽略配置更改
- 在代码中存储密码
- 没有设备测试就部署
- 使用已弃用的 API
- 积累内存泄漏
