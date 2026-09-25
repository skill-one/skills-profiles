# macOS 签名认证

当您需要为 App Store 外部分发而签名 macOS 应用时，请使用此技能。

## 前置条件
- 已安装 Xcode 并配置了命令行工具。
- 已配置 Auth（`asc auth login` 或 `ASC_*` 环境变量）。
- 本地密钥链中有一个 Developer ID Application 证书。
- 应用的 Xcode 项目已为 macOS 构建。

## 预检查：验证签名身份

在归档之前，确认存在有效的 Developer ID Application 身份：

```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

如果没有找到身份，请在 https://developer.apple.com/account/resources/certificates/add 创建一个（App Store Connect API 不支持创建 Developer ID 证书）。

### 检查信任设置

如果 `codesign` 或 `xcodebuild` 失败并显示 "无效的信任设置" 或 "errSecInternalComponent"，则证书可能具有自定义信任覆盖，导致链断裂：

```bash
# 检查自定义信任设置
security dump-trust-settings 2>&1 | grep -A1 "Developer ID"
```

这些错误本身并不能证明信任覆盖是问题的原因。在提出修复建议之前，请检查受影响的证书。更改信任设置需要对该证书的明确授权；不要作为诊断步骤删除信任覆盖或重新签名任意应用。

## 第 1 步：归档

```bash
xcodebuild archive \
  -scheme "YourMacScheme" \
  -configuration Release \
  -archivePath /tmp/YourApp.xcarchive \
  -destination "generic/platform=macOS"
```

## 第 2 步：使用 Developer ID 导出

创建用于 Developer ID 分发的 ExportOptions plist：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>developer-id</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
</dict>
</plist>
```

导出归档：

```bash
xcodebuild -exportArchive \
  -archivePath /tmp/YourApp.xcarchive \
  -exportPath /tmp/YourAppExport \
  -exportOptionsPlist ExportOptions.plist
```

这将生成一个使用 Developer ID Application 签名的 `.app` 包和一个安全的时戳。

### 验证导出

验证导出的应用的现有签名和嵌套代码，然后显示其签名详细信息：

```bash
codesign --verify --deep --strict --verbose=2 "/tmp/YourAppExport/YourApp.app" && \
  codesign --display --verbose=4 "/tmp/YourAppExport/YourApp.app" 2>&1
```

确认：
- 验证命令成功退出；仅显示签名详细信息并不能验证签名
- 权威链是 Developer ID Application → Developer ID Certification Authority → Apple Root CA，具有预期的 TeamIdentifier
- 存在时戳

如果验证失败或签名身份意外，请在打包或上传前停止。诊断失败原因，并在再次检查之前重新构建或重新导出预期的应用。这些检查不会修改包，也不会建立签名认证接受。

不要在验证中添加 `--sign` 或 `--force`。[Apple 的代码签名指南](https://developer.apple.com/library/archive/technotes/tn2206/) 区分了使用 `--deep` 的递归验证与使用 `--deep --force` 的签名，后者强制重新签名嵌套代码。

## 第 3 步：创建用于签名认证的 ZIP 文件

```bash
ditto -c -k --keepParent "/tmp/YourAppExport/YourApp.app" "/tmp/YourAppExport/YourApp.zip"
```

## 第 4 步：提交用于签名认证

### 一键提交
```bash
asc notarization submit --file "/tmp/YourAppExport/YourApp.zip"
```

### 等待结果
```bash
asc notarization submit --file "/tmp/YourAppExport/YourApp.zip" --wait
```

### 自定义轮询
```bash
asc notarization submit --file "/tmp/YourAppExport/YourApp.zip" --wait --poll-interval 30s --timeout 1h
```

## 第 5 步：检查结果

### 状态
```bash
asc notarization status --id "SUBMISSION_ID" --output table
```

### 开发者日志（用于失败）
```bash
asc notarization log --id "SUBMISSION_ID"
```

获取日志 URL 以查看详细问题：
```bash
curl -sL "LOG_URL" | python3 -m json.tool
```

### 列出之前的提交
```bash
asc notarization list --output table
asc notarization list --limit 5 --output table
```

## 第 6 步：绑定（可选）

签名认证成功后，绑定票证以便应用离线工作：

```bash
xcrun stapler staple "/tmp/YourAppExport/YourApp.app"
```

对于 DMG 或 PKG 分发，在创建容器后绑定：
```bash
# 创建 DMG
hdiutil create -volname "YourApp" -srcfolder "/tmp/YourAppExport/YourApp.app" -ov -format UDZO "/tmp/YourApp.dmg"
xcrun stapler staple "/tmp/YourApp.dmg"
```

## 支持的文件格式

| 格式 | 用例 |
|------|------|
| `.zip`  | 最简单；zip 签名的 `.app` 包 |
| `.dmg`  | 拖放安装的磁盘映像 |
| `.pkg`  | 安装程序包（需要 Developer ID Installer 证书） |

## PKG 签名认证

要签名 `.pkg` 文件，您需要一个 **Developer ID Installer** 证书（与 Developer ID Application 不同）。此证书类型无法通过 App Store Connect API 获取——在 https://developer.apple.com/account/resources/certificates/add 创建它。

签名包：
```bash
productsign --sign "Developer ID Installer: YOUR NAME (TEAM_ID)" unsigned.pkg signed.pkg
```

然后提交：
```bash
asc notarization submit --file signed.pkg --wait
```

## 故障排除

### 导出时出现 "无效的信任设置"
自定义信任覆盖是可能的原因之一。使用预检查中的只读检查，识别受影响的证书，并在更改其信任设置之前获得授权。

### "二进制文件未使用有效的 Developer ID 证书签名"
应用使用开发或 App Store 证书签名。在 ExportOptions.plist 中使用 `method: developer-id` 重新导出。

### "签名不包含安全时戳"
在手动 `codesign` 调用中添加 `--timestamp`，或使用 `xcodebuild -exportArchive`，后者会自动添加时戳。

### 大文件上传超时
设置更长的上传超时：
```bash
ASC_UPLOAD_TIMEOUT=5m asc notarization submit --file ./LargeApp.zip --wait
```

### 签名认证返回 "无效" 但签名看起来正确
获取开发者日志以查看具体问题：
```bash
asc notarization log --id "SUBMISSION_ID"
```

常见原因：未签名的嵌套二进制文件、缺少硬化运行时、没有时戳的嵌入式库。

## 注意事项
- `asc notarization` 命令使用 Apple Notary API v2，而不是 `xcrun notarytool`。
- 身份验证使用与其他 `asc` 命令相同的 API 密钥。
- 文件直接上传到 Apple 的 S3 桶，使用流式传输（无完整文件缓冲）。
- 超过 5 GB 的文件自动使用分片上传。
- 始终使用 `--help` 验证标志：`asc notarization submit --help`。
