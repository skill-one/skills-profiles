# Xcode 构建 和 导出

当您需要从源代码构建应用程序并准备提交到 App Store Connect 时，请使用此技能。在适合项目的情况下，优先使用 `asc xcode archive` 和 `asc xcode export` 而不是原始的 `xcodebuild` 菜单。

## 前置条件

- 已安装 Xcode 和命令行工具。
- 可用签名身份和配置文件，或已启用自动签名。
- 当需要上传或构建查找时，已配置 App Store Connect 认证。

## 管理版本和构建编号

```bash
asc xcode version view
asc xcode version edit --version "1.3.0" --build-number "42"
asc xcode version edit --next-build-number --app "APP_ID" --platform IOS
asc xcode version bump --type build
asc xcode version bump --type patch
asc xcode version bump --type build --next-build-number --app "APP_ID" --platform IOS
```

当不在项目根目录下运行时，使用 `--project-dir "./MyApp"`。当目录包含多个项目时，使用 `--project "./MyApp/App.xcodeproj"`。在多目标或多配置项目中，使用 `--target "App"` 和 `--configuration "Release"` 以实现确定性的读写。

为了避免构建编号过低被拒绝，在一个命令中解决并应用远程安全的构建编号：

```bash
asc xcode version edit --next-build-number --app "APP_ID" --platform IOS --output json
```

版本变更会在写入前验证完整变更，并返回结构化输出以标识已更改的配置和文件。编辑器遵循递归 xcconfig 包含，并保留无关的项目和 xcconfig 内容。当您只想检查远程安全值而不更改项目时，单独使用 `asc builds next-build-number`。

版本命令会读取项目和 xcconfig 设置，而无需启动 Xcode。当这些设置无法解析版本值时，默认的 `--xcodebuild-settings-lookup auto` 会回退到 `xcodebuild -showBuildSettings` 并在标准错误输出中警告。在必须隐式启动 Xcode 的自动化中，使用 `--xcodebuild-settings-lookup never`。

## 无需归档的编译

使用 `asc xcode build` 进行普通的模拟器、设备或 CI 验证构建。提供恰好一个项目或工作区以及一个方案。

```bash
asc xcode build \
  --project "App.xcodeproj" \
  --scheme "App" \
  --destination "platform=iOS Simulator,name=iPhone 17 Pro Max,OS=27.0" \
  --no-code-signing \
  --result-bundle-path ".asc/artifacts/App.xcresult" \
  --output json
```

当省略 `--derived-data-path` 时，asc 会使用源代码检出外部的稳定缓存。结果包的路径必须不存在。Xcode 日志输出到标准错误，结构化结果输出到标准输出。

## 推荐的 iOS/tvOS/visionOS 构建流程

### 1. 使用 asc 归档

```bash
asc xcode archive \
  --workspace "App.xcworkspace" \
  --scheme "App" \
  --configuration Release \
  --clean \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --xcodebuild-flag=-destination \
  --xcodebuild-flag=generic/platform=iOS \
  --output json
```

对于仅包含项目应用，使用 `--project "App.xcodeproj"` 而不是 `--workspace`。

### 2. 使用 asc 导出

默认情况下，`asc xcode export` 会生成带有自动签名的 App Store Connect 导出选项。除非设置 `--wait`，否则它会使用本地导出目标；如果设置 `--wait`，则使用直接上传：

```bash
asc xcode export \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --ipa-path ".asc/artifacts/App.ipa" \
  --xcodebuild-flag=-allowProvisioningUpdates \
  --output json
```

当需要审查、重用或手动签名时，单独生成 plist：

```bash
asc xcode export-options generate \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --output-path ".asc/ExportOptions.plist" \
  --output json
```

对于手动签名，添加 `--signing-style manual`，并可选地添加 `--team-id "TEAM_ID"`。现有文件需要 `--overwrite`。

对于可在注册设备上安装的 IPA，使用 Xcode 的当前 `release-testing` 方法。Xcode 已弃用旧的 `ad-hoc` 书写方式，`asc` 也不接受它：

```bash
asc xcode export \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --ipa-path ".asc/artifacts/App.ipa" \
  --method release-testing \
  --signing-style manual \
  --team-id "TEAM_ID" \
  --output json
```

当需要审查或重用时，单独生成 `release-testing` plist：

```bash
asc xcode export-options generate \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --method release-testing \
  --signing-style manual \
  --team-id "TEAM_ID" \
  --output-path ".asc/ExportOptions.release-testing.plist" \
  --output json
```

`release-testing` 总是本地导出，不能与 `--wait` 结合使用。显式的 `--export-options` plist 不能与 `--method`、`--signing-style` 或 `--team-id` 结合使用。对于设备/配置文件协调、隔离签名、私有发布、可恢复性和实时验证，请使用 `asc-ad-hoc-distribution` 技能，而不是手动组合这些阶段。

要通过 Xcode 直接上传并等待 App Store Connect 处理，省略 `--export-options` 并添加 `--wait`：

```bash
asc xcode export \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --ipa-path ".asc/artifacts/App.ipa" \
  --wait \
  --output json
```

### 3. 上传或发布

上传导出的 IPA：

```bash
asc builds upload --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --wait
```

分发到 TestFlight：

```bash
asc publish testflight --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --group "GROUP_ID" --wait
```

发布到 App Store：

```bash
asc publish appstore --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --version "1.2.3" --wait
asc publish appstore --app "APP_ID" --ipa ".asc/artifacts/App.ipa" --version "1.2.3" --wait --submit --confirm
```

## macOS App Store 流程

使用辅助工具归档：

```bash
asc xcode archive \
  --project "MacApp.xcodeproj" \
  --scheme "MacApp" \
  --configuration Release \
  --clean \
  --archive-path ".asc/artifacts/MacApp.xcarchive" \
  --xcodebuild-flag=-destination \
  --xcodebuild-flag=generic/platform=macOS \
  --output json
```

如果您的 macOS 导出生成 `.pkg`，请使用辅助工具导出，然后上传包：

```bash
asc xcode export \
  --archive-path ".asc/artifacts/MacApp.xcarchive" \
  --pkg-path ".asc/artifacts/MacApp.pkg" \
  --xcodebuild-flag=-allowProvisioningUpdates \
  --output json

asc builds upload \
  --app "APP_ID" \
  --pkg ".asc/artifacts/MacApp.pkg" \
  --version "1.0.0" \
  --build-number "123" \
  --wait
```

对于 `.pkg` 上传，需要 `--version` 和 `--build-number`，因为它们不像 IPA 元数据那样自动提取。当项目需要自定义导出配置时，添加 `--export-options "ExportOptions.plist"`。

## 原始 xcodebuild 回退

仅在 `asc xcode archive --help` 或 `asc xcode export --help` 未涵盖特定项目选项时使用原始 `xcodebuild`。优先通过 `--xcodebuild-flag` 首先传递额外参数。

```bash
xcodebuild -showBuildSettings -scheme "App"
```

## 故障排除

### 导出时缺少捆绑 ID 的配置文件

- 将 `--xcodebuild-flag=-allowProvisioningUpdates` 添加到 `asc xcode export`。
- 验证 Apple ID 是否已登录到 Xcode。
- 使用 `asc-signing-setup` 技能验证配置文件。

### CFBundleVersion 太低

```bash
asc xcode version edit --next-build-number --app "APP_ID" --platform IOS
```

然后重新构建并再次上传。

### 构建因缺少 macOS 图标而被拒绝

macOS 要求所有必需大小的 ICNS 图标。修复资产目录，重新构建，然后再次导出/上传。

## 注意事项

- 优先使用 `asc xcode archive` 和 `asc xcode export` 以生成确定性的本地工件。
- 默认生成的导出方法仍然是 `app-store-connect`；显式请求 `--method release-testing` 以进行注册设备安装。
- 仅在有意替换现有本地工件时使用 `--overwrite`。
- 在上传/发布路径上使用 `--wait`，因为下一步依赖于已处理的构建。
- 对于提交准备情况，使用 `asc-submission-health`。
