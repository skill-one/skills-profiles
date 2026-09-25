# asc 签名设置

当您需要为 iOS/macOS 应用创建或续订签名资产时，请使用此功能。

## 前置条件
- 已配置 Auth (`asc auth login` 或 `ASC_*` 环境变量)。
- 您知道 Bundle ID 和目标平台。
- 您有用于证书创建的 CSR 文件，或者您将让 `asc certificates create --generate-csr` 生成一个。

## 工作流程
1. 创建或查找 Bundle ID：
   - `asc bundle-ids list --paginate`
   - `asc bundle-ids create --identifier "com.example.app" --name "Example" --platform IOS`
2. 配置 Bundle ID 能力：
   - `asc bundle-ids capabilities list --bundle "BUNDLE_ID"`
   - `asc bundle-ids capabilities add --bundle "BUNDLE_ID" --capability ICLOUD`
   - 在需要时添加能力设置：
     - `--settings '[{"key":"ICLOUD_VERSION","options":[{"key":"XCODE_6","enabled":true}]}]'`
   - 对于仅在开发者门户中使用的 `PRIVATE_CLOUD_COMPUTE` 能力，使用用户拥有的网络会话和开发者门户 Bundle ID 资源 ID：
     - `asc web bundle-ids capabilities enable --bundle-id "BUNDLE_RESOURCE_ID" --capability PRIVATE_CLOUD_COMPUTE --confirm`
     - 此能力无法通过公共 App Store Connect 能力枚举获取。如果缓存的会话无法访问开发者门户，请清除其作用域缓存，然后使用相同的二进制文件重新登录：
       - `asc web auth logout --apple-id "user@example.com"`
       - `asc web auth login --apple-id "user@example.com"`
   - 对于 App Groups，公共 API 可以启用 `APP_GROUPS`，但无法创建或关联 App Group 资源。使用账户持有人或管理员网络会话：
     - `asc web app-groups list --paginate --output table`
     - `asc web app-groups create --name "Example Shared" --identifier "group.com.example.app.shared" --confirm`
     - `asc web app-groups assign --group "GROUP_RESOURCE_ID" --bundle-id "BUNDLE_RESOURCE_ID" --confirm`
     - 使用 `asc web app-groups list` 解析不透明组 ID，使用 `asc bundle-ids list` 解析不透明 Bundle ID 资源 ID。更改分配会使包含该 App ID 的配置文件失效，因此在下一个签名构建之前重新生成受影响的配置文件。
3. 创建签名证书：
   - `asc certificates list --certificate-type IOS_DISTRIBUTION`
   - `asc certificates create --certificate-type IOS_DISTRIBUTION --csr "./cert.csr"`
   - 或者内联生成密钥和 CSR：
     - `asc certificates create --certificate-type IOS_DISTRIBUTION --generate-csr --key-out "./signing/dist.key" --csr-out "./signing/dist.csr"`
   - 对于 Wallet passes，首先创建 Pass Type ID，然后创建其证书：
     - `asc pass-type-ids create --identifier "pass.com.example" --name "Example Pass"`
     - `asc certificates create --certificate-type PASS_TYPE_ID --pass-type-id "PASS_TYPE_ID" --csr "./pass.csr"`
     - `asc pass-type-ids certificates list --pass-type-id "PASS_TYPE_ID" --paginate`
4. 创建配置文件：
   - `asc profiles create --name "AppStore Profile" --profile-type IOS_APP_STORE --bundle "BUNDLE_ID" --certificate "CERT_ID"`
   - 包含用于开发/非正式的设备：
     - `asc profiles create --name "Dev Profile" --profile-type IOS_APP_DEVELOPMENT --bundle "BUNDLE_ID" --certificate "CERT_ID" --device "DEVICE_ID"`
5. 下载配置文件：
   - `asc profiles download --id "PROFILE_ID" --output "./profiles/AppStore.mobileprovision"`
6. 在需要时本地检查并安装下载的配置文件：
   - `asc profiles inspect --path "./profiles/AppStore.mobileprovision" --output table`
   - `asc profiles inspect --path "./profiles/AppStore.mobileprovision" --entitlements --output markdown`
   - `asc profiles local install --path "./profiles/AppStore.mobileprovision"`
   - `asc profiles local list --output table`
   - 在 macOS 上，默认目录遵循活动的 Xcode：Xcode 16 或更新版本使用 `~/Library/Developer/Xcode/UserData/Provisioning Profiles`；Xcode 15 或更早版本使用 `~/Library/MobileDevice/Provisioning Profiles`。没有完整活动 Xcode 的主机会回退到传统目录并打印错误信息到 stderr。
   - 当自动化必须针对固定目录时，请传递 `--install-dir`。

## 旋转和清理
- 注销旧证书：
  - `asc certificates revoke --id "CERT_ID" --confirm`
- 在删除或旋转之前审计远程配置文件：
  - `asc profiles list --profile-state ACTIVE,INVALID --paginate --output json`
  - Apple 的 `profileState` 不是完整的过期信号：某些配置文件可能有过去的 `expirationDate` 而仍报告 `ACTIVE`。对于真正的过期配置文件审计，请比较 `expirationDate` 与当前日期，而不是仅依赖 `INVALID`。
- 删除旧配置文件：
  - `asc profiles delete --id "PROFILE_ID" --confirm`
- 清理本地 Xcode 配置文件：
  - `asc profiles local clean --expired --dry-run`
  - `asc profiles local clean --expired --confirm`
  - 在确认之前检查干运行输出中的解析目录，或使用 `--install-dir` 固定它。

## 使用 `asc signing sync` 的共享团队存储
当您需要一个轻量级、非交互式的 fastlane match 替代方案，用于加密的 git 支持的证书/配置文件存储时，请使用此功能。

```bash
# 在使用前保护秘密输入
chmod 600 "./signing-sync-password" "./distribution.p12" "./distribution-p12-password"

# 推送可用的私有身份及其匹配的证书和配置文件
asc signing sync push \
  --bundle-id "com.example.app" \
  --profile-type IOS_APP_ADHOC \
  --repo "git@github.com:team/certs.git" \
  --password-file "./signing-sync-password" \
  --identity "./distribution.p12" \
  --identity-password-file "./distribution-p12-password" \
  --output json

# 拉取并解密到本地目录
asc signing sync pull \
  --repo "git@github.com:team/certs.git" \
  --password-file "./signing-sync-password" \
  --output-dir "./signing" \
  --output json
```

注意：
- App Store Connect 永远不会返回私钥。使用 `--identity` 提供本地 PKCS#12，或使用 `--private-key` 与 `--identity-sha256` 选择其匹配的 App Store Connect 证书。多身份 PKCS#12 也需要 `--identity-sha256`。
- 优先使用 `--password-file`；`ASC_SIGNING_SYNC_PASSWORD` 是非文件回退。`--password` 在 5.0.0 中已移除并拒绝。`ASC_MATCH_PASSWORD` 不再读取，如果设置则被忽略。
- 仅证书/配置文件同步仍然受支持，但报告 `identityPresent: false`；它本身不是可用的签名身份。
- `pull` 在 `sensitiveFiles` 中报告私有身份，并以模式 `0600` 写入它们。导入或使用拉取的身份仍然是一个显式的步骤。
- 私有身份同步拒绝 `MAC_APP_DIRECT` 和 `MAC_CATALYST_APP_DIRECT`；仅证书/配置文件同步仍然可用。

## 调整非正式设备和配置文件

使用实验性的调整工作流程，从 Xcode 归档和受保护的期望设备文件派生确定性、可加性更改：

```bash
asc signing reconcile plan \
  --archive-path ".asc/artifacts/App.xcarchive" \
  --devices-file ".asc/distribution/devices.json" \
  --output json

asc signing reconcile apply \
  --plan ".asc/distribution/signing/plan.json" \
  --confirm \
  --output json
```

规划不会进行任何变更，可能返回 `ready: false`。应用可以注册缺失的设备、创建安全的基线 App ID 并创建后续的非正式配置文件；它永远不会删除或修补资源、启用能力或创建证书。在 `--confirm` 之前查看计划。当这些签名效果应该绑定到端到端分发计划哈希时，使用 `asc-ad-hoc-distribution` 技能。

## 使用临时身份运行一个命令

在 macOS 上，通过包装子命令避免持久登录密钥链和配置文件更改：

```bash
asc signing run \
  --identity "./signing/App.p12" \
  --identity-password-file "./signing/App-password" \
  --profile "./signing/App.mobileprovision" \
  --receipt ".asc/distribution/signing-run.json" \
  -- xcodebuild -exportArchive \
    -archivePath ".asc/artifacts/App.xcarchive" \
    -exportPath ".asc/artifacts/release-testing" \
    -exportOptionsPlist ".asc/ExportOptions.release-testing.plist"
```

命令直接运行，不使用 shell，保留子命令的退出码，使用隔离的临时密钥链，并清理其临时配置文件。它不会打印成功数据，因此子命令拥有 stdout。永远不要内联传递身份密码。

## 注意事项
- 始终检查 `--help` 获取确切的枚举值（证书类型、配置文件类型）。
- 对于大型账户，请使用 `--paginate`。
- `--certificate` 接受逗号分隔的 ID，当需要多个证书时。
- 设备管理使用 `asc devices` 命令（需要 UDID）。
- `asc profiles inspect` 和 `asc profiles local ...` 操作于本地磁盘状态，而不是 App Store Connect API 资源。
