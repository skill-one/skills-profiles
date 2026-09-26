# iOS 应用开发

使用 XcodeGen 和 Swift Package Manager 构建、配置和部署 iOS 应用。

## 严重警告

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| "无法加载库: @rpath/Framework" | XcodeGen 不会自动嵌入 SPM 动态框架 | **首先在 Xcode GUI 中构建**（而不是 xcodebuild）。参见 [故障排除](#spm-dynamic-framework-not-embedded) |
| `xcodegen generate` 丢失签名 | 覆写了项目设置 | 在 `project.yml` 目标设置中配置，而不是全局配置 |
| 命令行签名失败 | 免费Apple ID限制 | 使用 Xcode GUI 或付费开发者账号（每年99美元） |
| "在自动调整视频镜像时无法设置" | 在未禁用自动调整的情况下设置了 `isVideoMirrored` | 首先设置 `automaticallyAdjustsVideoMirroring = false`。参见 [相机](#camera--avfoundation) |
| 尽管有证书，应用仍以adhoc方式签名 | `@electron/packager` 默认 `continueOnError: true` | 在 osxSign 中设置 `continueOnError: false`。参见 [代码签名](#macos-code-signing--notarization) |
| "无法使用密码凭证，API密钥凭证..." | 使用API密钥认证将 `teamId` 传递给 `@electron/notarize` | **移除 `teamId`**。`notarytool` 从API密钥推断团队。参见 [代码签名](#macos-code-signing--notarization) |
| 签名期间出现 EMFILE（大型嵌入运行时） | `@electron/osx-sign` 遍历.app包中的所有文件 | 在CI中添加 `ignore` 过滤器 + `ulimit -n 65536`。参见 [代码签名](#macos-code-signing--notarization) |

## 快速参考

| 任务 | 命令 |
|------|---------|
| 生成项目 | `xcodegen generate` |
| 构建模拟器 | `xcodebuild -destination 'platform=iOS Simulator,name=iPhone 17' build` |
| 构建设备（付费账号） | `xcodebuild -destination 'platform=iOS,name=DEVICE' -allowProvisioningUpdates build` |
| 清理 DerivedData | `rm -rf ~/Library/Developer/Xcode/DerivedData/PROJECT-*` |
| 查找设备名称 | `xcrun xctrace list devices` |

## XcodeGen 配置

### 最小化的 project.yml

```yaml
name: AppName
options:
  bundleIdPrefix: com.company
  deploymentTarget:
    iOS: "16.0"

settings:
  base:
    SWIFT_VERSION: "6.0"

packages:
  SomePackage:
    url: https://github.com/org/repo
    from: "1.0.0"

targets:
  AppName:
    type: application
    platform: iOS
    sources:
      - path: AppName
    settings:
      base:
        INFOPLIST_FILE: AppName/Info.plist
        PRODUCT_BUNDLE_IDENTIFIER: com.company.appname
        CODE_SIGN_STYLE: Automatic
        DEVELOPMENT_TEAM: TEAM_ID_HERE
    dependencies:
      - package: SomePackage
```

### 代码签名配置

**个人（免费）账号**：仅在 Xcode GUI 中工作。命令行构建需要付费账号。

```yaml
# 在目标设置中
settings:
  base:
    CODE_SIGN_STYLE: Automatic
    DEVELOPMENT_TEAM: TEAM_ID  # 从 Xcode → 设置 → 账户获取
```

**获取 Team ID**:
```bash
security find-identity -v -p codesigning | head -3
```

## iOS 版本兼容性

### 各版本API变更

| 仅限iOS 17+ | 兼容iOS 16 |
|--------------|-------------------|
| `.onChange { old, new in }` | `.onChange { new in }` |
| `ContentUnavailableView` | 自定义 VStack |
| `AVAudioApplication` | `AVAudioSession` |
| `@Observable` 宏 | `@ObservableObject` |
| SwiftData | CoreData/Realm |

### 降低部署目标

1. 更新 `project.yml`:
```yaml
deploymentTarget:
  iOS: "16.0"
```

2. 修复不兼容的API:
```swift
// iOS 17
.onChange(of: value) { oldValue, newValue in }
// iOS 16
.onChange(of: value) { newValue in }

// iOS 17
ContentUnavailableView("Title", systemImage: "icon")
// iOS 16
VStack {
    Image(systemName: "icon").font(.system(size: 48))
    Text("Title").font(.title2.bold())
}

// iOS 17
AVAudioApplication.shared.recordPermission
// iOS 16
AVAudioSession.sharedInstance().recordPermission
```

3. 重新生成: `xcodegen generate`

## 设备部署

### 首次设置

1. 通过USB连接设备
2. 在设备上信任计算机
3. 在Xcode中: 设置 → 账户 → 添加 Apple ID
4. 在方案下拉菜单中选择设备
5. 运行 (`Cmd + R`)
6. 在设备上: 设置 → 通用 → VPN与设备管理 → 信任

### 命令行构建（需要付费账号）

```bash
xcodebuild \
  -project App.xcodeproj \
  -scheme App \
  -destination 'platform=iOS,name=DeviceName' \
  -allowProvisioningUpdates \
  build
```

### 常见问题

| 错误 | 解决方案 |
|-------|----------|
| "无法加载库: @rpath/Framework" | SPM 动态框架未嵌入。首先在Xcode GUI中构建，然后CLI即可工作 |
| "没有团队账号" | 在Xcode设置 → 账户中添加Apple ID |
| "未找到配置文件" | 免费账号限制。使用Xcode GUI或获取付费账号 |
| 设备未列出 | 重新连接USB，在设备上信任计算机，重启Xcode |
| DerivedData无法删除 | 首先关闭Xcode: `pkill -9 Xcode && rm -rf ~/Library/Developer/Xcode/DerivedData/PROJECT-*` |

### 免费与付费开发者账号

| 功能 | 免费Apple ID | 付费（每年99美元） |
|---------|---------------|-----------------|
| Xcode GUI构建 | ✅ | ✅ |
| 命令行构建 | ❌ | ✅ |
| 应用有效期 | 7天 | 1年 |
| App Store | ❌ | ✅ |
| CI/CD | ❌ | ✅ |

## SPM 依赖项

### SPM 动态框架未嵌入

**根本原因**：XcodeGen不会为SPM动态框架（如RealmSwift、Realm）生成“嵌入框架”构建阶段。应用构建成功但在启动时崩溃，显示：

```
dyld: 无法加载库: @rpath/RealmSwift.framework/RealmSwift
  参考自: /var/containers/Bundle/Application/.../App.app/App
  原因: 图像未找到
```

**为什么会发生**：
- 静态框架（大多数SPM包）会链接到二进制文件中 - 无需嵌入
- 动态框架（RealmSwift等）必须复制到应用包中
- XcodeGen生成链接阶段，但**不**为SPM包生成嵌入阶段
- `embed: true` 在project.yml中会导致构建错误（XcodeGen限制）

**修复方法**（手动，每个项目一次性）：
1. 在Xcode GUI中打开项目
2. 选择目标 → 通用 → 框架、库
3. 找到动态框架（RealmSwift）
4. 将“不嵌入”改为“嵌入并签名”
5. 首先在Xcode GUI中构建和运行

**修复后**：命令行构建（`xcodebuild`）将工作，因为Xcode会持久化嵌入设置到project.pbxproj。

**识别动态框架**：
```bash
# 检查框架是否为动态
file ~/Library/Developer/Xcode/DerivedData/PROJECT-*/Build/Products/Debug-iphoneos/FRAMEWORK.framework/FRAMEWORK
# 动态: "Mach-O 64位动态链接共享库"
# 静态: "current ar archive"
```

### 添加包

```yaml
packages:
  AudioKit:
    url: https://github.com/AudioKit/AudioKit
    from: "5.6.5"
  RealmSwift:
    url: https://github.com/realm/realm-swift
    from: "10.54.6"

targets:
  App:
    dependencies:
      - package: AudioKit
      - package: RealmSwift
        product: RealmSwift  # 当包有多个产品时显式指定产品名称
```

### 解决依赖项（中国代理）

```bash
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082
xcodebuild -scmProvider system -resolvePackageDependencies
```

**永远不要清除全局SPM缓存**（`~/Library/Caches/org.swift.swiftpm`）。重新下载很慢。

## 相机 / AVFoundation

相机预览需要真实设备（模拟器没有相机）。

### 快速调试清单

1. **权限**：是否在Info.plist中添加了 `NSCameraUsageDescription`？
2. **设备**：是否在真实设备上运行，而不是模拟器？
3. **会话运行**：是否在后台线程调用了 `session.startRunning()`？
4. **视图大小**：UIViewRepresentable是否有非零边界？
5. **视频镜像**：在设置 `isVideoMirrored` 之前是否禁用了自动调整？

### 视频镜像（前置相机）

**关键**：必须先禁用自动调整，然后才能设置手动镜像：

```swift
// 错误 - 会崩溃，提示 "在自动调整视频镜像时无法设置"
connection.isVideoMirrored = true

// 正确 - 首先禁用自动调整
connection.automaticallyAdjustsVideoMirroring = false
connection.isVideoMirrored = true
```

### UIViewRepresentable 尺寸问题

ZStack中的UIViewRepresentable可能具有零边界。使用显式框架修复：

```swift
// 差的: UIViewRepresentable可能在ZStack中获取零大小
ZStack {
    CameraPreviewView(session: session)  // 可能不可见！
    OtherContent()
}

// 好的: 显式尺寸
ZStack {
    GeometryReader { geo in
        CameraPreviewView(session: session)
            .frame(width: geo.size.width, height: geo.size.height)
    }
    .ignoresSafeArea()
    OtherContent()
}
```

### 调试日志模式

添加日志以跟踪相机流程：

```swift
import os
private let logger = Logger(subsystem: "com.app", category: "Camera")

func start() async {
    logger.info("start() called, isRunning=\(self.isRunning)")
    // ... 设置代码 ...
    logger.info("session.startRunning() completed")
}

// 对于CGRect（不遵循 CustomStringConvertible）
logger.info("bounds=\(NSCoder.string(for: self.bounds))")
```

在Console.app中按子系统过滤。

**有关详细相机实现**：参见 [references/camera-avfoundation.md](references/camera-avfoundation.md)

## macOS 代码签名与Notarization

对于在App Store外分发macOS应用（Electron或原生应用），需要签名+Notarization。否则用户会看到“Apple无法检查此应用是否存在恶意软件”。

**5步清单**：

| 步骤 | 操作 | 关键细节 |
|------|------|-----------------|
| 1 | 在Keychain Access中创建CSR | 常用名不重要；选择“保存到磁盘” |
| 2 | 在developer.apple.com申请**Developer ID Application**证书 | 选择**G2 Sub-CA**（不是Previous Sub-CA） |
| 3 | 安装.cer → 必须选择**`login`密钥链** | iCloud/系统 → 错误-25294（私钥不匹配） |
| 4 | 从`login`密钥链导出P12并设置密码 | Base64: `base64 -i cert.p12 \| pbcopy` |
| 5 | 创建App Store Connect API密钥（开发者角色） | 下载.p8一次；记录Key ID + Issuer ID |

**GitHub Secrets需要（5个秘密）**：

| 秘密 | 来源 |
|--------|--------|
| `MACOS_CERT_P12` | 步骤4 base64 |
| `MACOS_CERT_PASSWORD` | 步骤4密码 |
| `APPLE_API_KEY` | 步骤5 .p8 base64 |
| `APPLE_API_KEY_ID` | 步骤5 Key ID |
| `APPLE_API_ISSUER` | 步骤5 Issuer ID |

> **`APPLE_TEAM_ID` 不需要。** `notarytool` 从API密钥推断团队。将 `teamId` 传递给 `@electron/notarize` v2.5.0 会导致凭证冲突错误。

**Electron Forge osxSign关键设置**：

```typescript
osxSign: {
  identity: 'Developer ID Application',
  hardenedRuntime: true,
  entitlements: 'entitlements.mac.plist',
  entitlementsInherit: 'entitlements.mac.plist',
  continueOnError: false,  // 关键：默认为true，会静默回退到adhoc
  // 跳过大型嵌入运行时中的非二进制文件（防止EMFILE）
  ignore: (filePath: string) => {
    if (!filePath.includes('python-runtime')) return false;
    if (/\.(so|dylib|node)$/.test(filePath)) return false;
    return true;
  },
  // CI: 明确指定密钥链（apple-actions/import-codesign-certs使用signing_temp.keychain）
  ...(process.env.MACOS_SIGNING_KEYCHAIN
    ? { keychain: process.env.MACOS_SIGNING_KEYCHAIN }
    : {}),
},
```

**快速失败三层防御**：

1. `@electron/osx-sign`: `continueOnError: false` — 签名错误立即抛出
2. `postPackage`钩子: `codesign --verify --deep --strict` + adhoc检测
3. 发布触发脚本: 验证本地HEAD是否与远程匹配，然后才分发

**验证签名**:
```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

有关完整分步指南、权限、工作流示例和完整故障排除（7个真实错误及其根本原因）：**[references/apple-codesign-notarize.md](references/apple-codesign-notarize.md)**

---

## 资源

- [references/xcodegen-full.md](references/xcodegen-full.md) - 完整的project.yml选项
- [references/swiftui-compatibility.md](references/swiftui-compatibility.md) - iOS版本API差异
- [references/camera-avfoundation.md](references/camera-avfoundation.md) - 相机预览调试
- [references/testing-mainactor.md](references/testing-mainactor.md) - 测试 @MainActor类（状态机、回归测试）
- [references/apple-codesign-notarize.md](references/apple-codesign-notarize.md) - Apple Developer签名+Notarization（macOS/Electron CI/CD）
