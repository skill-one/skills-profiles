# 实现路由和深度链接

## 目录
- [核心概念](#核心概念)
- [工作流：初始化应用程序和路由器](#工作流初始化应用程序和路由器)
- [工作流：配置平台深度链接](#工作流配置平台深度链接)
- [工作流：实现嵌套导航](#工作流实现嵌套导航)
- [示例](#示例)

## 核心概念

使用 `go_router` 包在 Flutter 中进行声明式路由。它为复杂的路由场景、深度链接和嵌套导航提供了强大的 API。

- **GoRouter**：定义应用程序路由树的中心配置对象。
- **GoRoute**：将 URL 路径映射到 Flutter 屏幕的标准路由。
- **ShellRoute / StatefulShellRoute**：将子路由包装在持久化 UI 壳中（例如，`BottomNavigationBar`）。`StatefulShellRoute` 维护并行导航分支的状态。
- **路径 URL 策略**：从 Web URL 中移除默认的 `#` 片段，对于跨平台的干净深度链接至关重要。

## 工作流：初始化应用程序和路由器

按照以下工作流使用 `go_router` 启动新的 Flutter 应用程序并配置根路由机制。

### 任务进度
- [ ] 创建 Flutter 应用程序。
- [ ] 添加 `go_router` 依赖项。
- [ ] 配置 Web/深度链接的 URL 策略。
- [ ] 实现 `GoRouter` 配置。
- [ ] 将路由绑定到 `MaterialApp.router`。

### 1. 搭建应用程序
运行以下命令创建应用程序并添加所需的路由包：
```bash
flutter create <app-name>
cd <app-name>
flutter pub add go_router
```

### 2. 配置路由器
定义一个顶层 `GoRouter` 实例。使用 `redirect` 参数处理身份验证或基于状态的路由。

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_web_plugins/url_strategy.dart';

void main() {
  // 使用路径 URL 策略从 Web URL 中移除 '#'
  usePathUrlStrategy();
  runApp(const MyApp());
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'details/:id',
          builder: (context, state) => DetailsScreen(id: state.pathParameters['id']!),
        ),
      ],
    ),
  ],
  errorBuilder: (context, state) => ErrorScreen(error: state.error),
);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: _router,
      title: 'Routing App',
    );
  }
}
```

## 工作流：配置平台深度链接

配置原生平台以拦截特定 URL 并将它们路由到 Flutter 应用程序。

### 任务进度
- [ ] 确定目标平台（iOS、Android 或两者）。
- [ ] 对 Android 应用条件配置（Manifest + Asset Links）。
- [ ] 对 iOS 应用条件配置（Plist + Entitlements + AASA）。
- [ ] 运行验证器 -> 查看错误 -> 修复。

### 如果配置为 Android：
1. **修改 `AndroidManifest.xml`**：在 `.MainActivity` 的 `<activity>` 标签内添加意图过滤器。
```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="http" android:host="yourdomain.com" />
    <data android:scheme="https" />
</intent-filter>
```
2. **托管 `assetlinks.json`**：在 `https://yourdomain.com/.well-known/assetlinks.json` 处提供以下 JSON。
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.yourcompany.yourapp",
    "sha256_cert_fingerprints": ["YOUR_SHA256_FINGERPRINT"]
  }
}]
```

### 如果配置为 iOS：
1. **修改 `Info.plist`**：选择 Flutter 的默认深度链接处理程序。
*注意：如果使用第三方深度链接插件（例如，`app_links`），将此设置为 `NO` 以防止冲突。*
```xml
<key>FlutterDeepLinkingEnabled</key>
<true/>
```
2. **修改 `Runner.entitlements`**：添加相关域名。
```xml
<key>com.apple.developer.associated-domains</key>
<array>
  <string>applinks:yourdomain.com</string>
</array>
```
3. **托管 `apple-app-site-association`**：在 `https://yourdomain.com/.well-known/apple-app-site-association` 处提供以下 JSON（不带 `.json` 扩展名）。
```json
{
  "applinks": {
    "apps": [],
    "details": [{
      "appIDs": ["TEAM_ID.com.yourcompany.yourapp"],
      "paths": ["*"],
      "components": [{"/": "/*"}]
    }]
  }
}
```

### 验证循环
运行验证器 -> 查看错误 -> 修复。
- **Android**：使用 ADB 测试。
  ```bash
  adb shell 'am start -a android.intent.action.VIEW -c android.intent.category.BROWSABLE -d "https://yourdomain.com/details/123"' com.yourcompany.yourapp
  ```
- **iOS**：在启动的模拟器上使用 `xcrun` 测试。
  ```bash
  xcrun simctl openurl booted https://yourdomain.com/details/123
  ```

## 工作流：实现嵌套导航

使用 `StatefulShellRoute` 实现持久化 UI 壳（如底部导航栏），这些壳维护其子路由的状态。

### 任务进度
- [ ] 在 `GoRouter` 配置中定义 `StatefulShellRoute.indexedStack`。
- [ ] 为每个导航标签创建 `StatefulShellBranch` 实例。
- [ ] 使用 `StatefulNavigationShell` 实现壳组件。

```dart
final GoRouter _router = GoRouter(
  initialLocation: '/home',
  routes: [
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return ScaffoldWithNavBar(navigationShell: navigationShell);
      },
      branches: [
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/home',
              builder: (context, state) => const HomeScreen(),
            ),
          ],
        ),
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: '/settings',
              builder: (context, state) => const SettingsScreen(),
            ),
          ],
        ),
      ],
    ),
  ],
);
```

## 示例

### 高保真壳组件实现
实现消耗 `StatefulNavigationShell` 以处理分支切换的 UI 壳。

```dart
class ScaffoldWithNavBar extends StatelessWidget {
  const ScaffoldWithNavBar({
    required this.navigationShell,
    super.key,
  });

  final StatefulNavigationShell navigationShell;

  void _goBranch(int index) {
    navigationShell.goBranch(
      index,
      // 支持点击活动标签时导航到初始位置。
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: _goBranch,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
```

### 命令式导航
使用 `go_router` 提供的 `context.go()` 和 `context.push()` 扩展方法。

```dart
// 用目标路由替换当前路由栈（声明式）
context.go('/details/123');

// 将目标路由推到现有栈（命令式）
context.push('/details/123');

// 使用命名路由和路径参数导航
context.goNamed('details', pathParameters: {'id': '123'});

// 弹出当前路由
context.pop();
```
