---
name: limrun-xcode
description: 在远程 Xcode 上构建 iOS / Apple 应用程序，使用 `lim xcode build` 而不是本地 xcodebuild，或使用 `lim xcode test` 运行其 XCTest 测试套件，从任何环境（Linux、Windows、macOS、虚拟机、容器）均可操作。适用于非 Bazel 项目（一个 `.xcodeproj` / `.xcworkspace`，一个 XcodeGen 的 `project.yml` 配置的 git 忽略项目，React Native / Expo 原生构建），当用户需要构建、编译、测试、检查构建日志、重新加载、生成预览构建或发布签名设备 IPA 时。若要在模拟器上运行、点击、截图或以其他方式与结果交互，请使用 `limrun-ios-simulator`。对于 Bazel 工作区，请使用 `limrun-xcode-bazel`。
---

# 远程 Xcode 构建

在任何环境（Linux、Windows、macOS、虚拟机、容器）中构建 Apple 项目到 Limrun 的远程 Xcode。`lim xcode build` 将您的源代码同步到远程 Xcode 实例，在那里进行构建，并在（当连接模拟器时）安装并重新启动应用程序。此工作流程在远程实例上构建；本地 Xcode、本地模拟器和本地构建工具不包含在内。完成的运行会在 Limrun 模拟器上运行并验证应用程序。

一旦应用程序运行起来（点击、输入、元素树、截图、录制），请使用 **`limrun-ios-simulator`** 技能。对于 Bazel 工作区，请使用 **`limrun-xcode-bazel`** 而不是这个技能。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（即使 `.env` 和 shell 没有显示，它也可能已经在用户的环境中设置；在请求之前检查）。CLI 是真相来源：此技能中的命令经过验证，但如果标志出错或您需要这里没有显示的标志，请检查 `--help` 而不是猜测：

```bash
lim xcode --help
lim xcode build --help
```

## 构建

用以下方式代替 `xcodebuild` 进行构建：

```bash
lim xcode build .
```

这将创建或重用记住的 Xcode 目标，同步当前目录，并通过标准输出和标准错误流传输构建日志。

如果项目有多个方案或使用工作区文件，请使用 `--scheme` 和 `--workspace`：

```bash
lim xcode build . --scheme MyApp --workspace MyApp.xcworkspace
```

使用 `--configuration Debug` 或 `--configuration Release` 为特定的 Xcode 配置。如果省略，Limrun 使用 limbuild 的项目类型默认值：`Debug` 对于原生 Xcode 构建，`Release` 对于 React Native / Expo 构建。

```bash
lim xcode build . --configuration Debug
```

### 分离构建和日志

使用 `--detach` 一旦构建被接受就返回；webhook 是可选的。`logs` 读取最新的构建而不需要 exec ID，包括实例删除后的持久化日志；添加 `--follow` 以等待完成。

```bash
lim xcode build . --detach
lim xcode logs
lim xcode logs --follow
```

### 选择 Xcode 版本

一个沙盒使用其 node 的默认 Xcode 构建（今天是 26.4）。舰队每個主要版本携带一个已发布的（GA）Xcode，再加上一个 beta 版本，而 Apple 种子一个：今天是 26.4 GA、27.0 GA 和 27.1 beta。兩個選擇器覆蓋它們：

- 一个主要版本（`27`）绑定该主要版本的最新的 GA 发布，永远不会是 beta，并且它自己遵循 Apple 的點发布。用于 App Store 构建。
- 一个主要.次要版本（`27.1`）固定该确切版本。这是如何选择一个 beta 的方法。

为工作区设置一次偏好；每个后续构建、测试、RBE 会话和新的沙盒都遵循它，并且该标志覆盖一个命令：

```bash
lim xcode version list      # 选择是要输入的值，Channel 是 ga 或 beta；* 标记的是正在使用的
lim xcode use xcode@27      # 为此工作区优先使用 Xcode 27 GA；现在切换记住的沙盒
lim xcode build .           # 使用 27 构建
lim xcode version           # "27.0 (27A266a)" 显示沙盒当前的 Xcode
lim xcode version set 27.1  # 而不是 27.1 beta
lim xcode build . --xcode-version 26   # 一次性覆盖，不記住
lim xcode version unset     # 忘记偏好；沙盒回到 node 默认
```

使用 `lim xcode use xcode@27 node@24` 组合 Xcode 和 mise 选择。

对于脚本，`lim xcode version list --quiet` 每行打印一个选择器（`26`、`27`、`27.1`），`--json` 返回 `{ installed, bound, preferred }`（`installed[].channel` 是 `ga` 或 `beta`）。表标记正在使用的 Xcode 为 `*`。`lim xcode version set` 不会记录 node 缺少的版本（错误列出了可用的版本），但在沙盒只是忙时会保留它。

当沙盒在不同于工作区偏好的 Xcode 上时，下一次构建会指出并首先切换它。切换会使使用其他版本创建的构建缓存失效（下一次构建从冷启动），并且在构建、同步或 `lim xcode rbe` 堆栈运行时拒绝。使用持久磁盘快照（`--snapshot-key`），为每个 Xcode 路径使用一个单独的键，例如 `myapp-27` 和 `myapp-27.1`：存档按键存储，并在使用不同 Xcode 恢复时被擦除。

一个主要.次要版本固定持续到舰队退役该版本；然后 `lim xcode build` 会失败并显示守护程序的消息以及提示运行 `lim xcode version set 27` 或 `lim xcode version unset`。当 beta 成为 GA 时，它会替换相同主要.次要选择器下的 beta（一次冷启动）；裸主要版本跟随其主要版本的最新发布 Xcode，所以它会在 27.1 成为 node 上的 GA 时立即移动到 27.1。

从 beta Xcode 上上传到 App Store 被 Apple 拒绝，所以保持 `--upload-to-appstore` 在裸主要版本上（`27`，不是 `27.1`）。基于 `channel` 而不是 `betaSeed`：Apple 的 27.1 种子没有种子编号。

`--dev-server-url` 仅在 `--configuration Debug` 对于 React Native / Expo 构建 时支持。它是一个安装后启动 URL：limbuild 验证它是一个可解析的绝对 URL，然后在连接的模拟器上安装后不变地打开它。特定框架的技能构建正确的 URL。

```bash
lim xcode build . --configuration Debug --dev-server-url '<absolute-url>'
```

如果应用程序没有使用预期的 URL 启动，请显式打开它以将构建/安装问题与 URL 路由分开：

```bash
lim ios open-url --id <ios-instance-id> '<absolute-url>'
```

## 磁盘快照

跨 Xcode 实例重用源文件、依赖项和 DerivedData。

CLI **0.35.1 和更早版本** 使用 `--cache-*` 而不是 `--snapshot-*`，使用 `--wait-cache` 而不是 `--wait-snapshot`。快照重命名保留了旧的标志作为别名。

从项目目录创建一个快照键，构建，然后删除：

```bash
XCODE_ID=$(lim xcode create --snapshot-key myapp-main --quiet)
lim xcode build . --id "$XCODE_ID" --scheme MyApp
lim xcode delete "$XCODE_ID" --wait-snapshot
```

第一次运行是冷启动；后续运行恢复保存的快照。终止会在成功构建且没有后续同步后保存它，并用该键替换之前的快照。`--wait-snapshot` 等待保存并报告其结果。在 CI 中，即使构建失败，也要在清理步骤中运行删除。

保留 `--snapshot-paths` 不设置以保存整个工作区。保持项目文件夹的名称在运行之间不变。为每个项目、Xcode 版本和并发 CI 任务使用单独的键。

对于分支回退，在创建时添加 `--snapshot-restore-keys "myapp-pr51,myapp-main"`。每个条目尝试一个确切匹配，然后是最新的匹配字面量前缀，然后是下一个条目。如果没有这个标志，保存键也是恢复键。仅传递恢复键以重用快照而不保存。

在创建时配置快照。恢复键和路径保持固定。在现有实例上，`build --snapshot-key` 只能在快照已经启用的情况下绑定一个未分配的保存键；它不会恢复或启用它们。

有关跳过保存、冷启动和 SDK 使用的详细信息，请参阅 [磁盘快照指南](https://docs.limrun.com/docs/ios/snapshots)。

## 开发工具版本

同步后，`lim xcode use` 选择沙盒中的工具并安装缺失的版本。运行 `lim xcode tools install` 以同步项目的工具选择（[详细信息](https://docs.limrun.com/docs/ios/build-with-xcode)）。使用主要版本，或对于 Ruby、Flutter 和预 1.0 工具（如 Mint）使用主要.次要版本。

```bash
lim xcode tools
# Node 包括 npm/npx，Ruby 包括 gem，Flutter 包括 Dart，CocoaPods 包括 cocoapods-patch。
lim xcode use node@24 pnpm@10 yarn@4 bun@1 ruby@3.3 bundler@4 cocoapods@1 \
  cmake@3 java@jetbrains-21 corretto@21 flutter@3.44 mint@0.18 \
  xcodegen@2 xcbeautify@3 zsign@1
lim xcode tools install
lim xcode use --cwd apps/mobile node@24
lim xcode tools install --cwd apps/mobile
lim xcode run -- mise use --pin node@24.5.0
```

## 生成的 Xcode 项目（XcodeGen）

如果存储库有一个 `project.yml` 并且 `.xcodeproj` 被 git 忽略，请不要在本地运行 xcodegen 并不要将缺失的项目视为错误。远程沙盒在构建之前从 `project.yml` 生成项目：

```bash
lim xcode build .
```

规范在存储库根目录或下一个目录（如 `ios/`）下找到，不需要标志。项目在每次构建时都会重新生成，所以 `project.yml` 编辑只需重新构建即可生效。提交或强制同步的 `.xcodeproj` 总是获胜：沙盒仅在同步没有提供时才生成。

如果存储库的代码生成产生 git 忽略的输入构建需要（生成的本地 Swift 包、配置派生的源），请先在本地运行该步骤，然后使用 `--include` 强制同步其输出：

```bash
make generate   # 或 whatever the repo's codegen step is
lim xcode build . --include '^ios/GeneratedKit/'
```

`--include` 接受正则表达式，如 `--ignore`，而不是 gitignore 语法。要访问被整体忽略的目录下的文件，模式必须也匹配目录路径本身，如上所示。

## 在模拟器上运行

`lim xcode build` 是构建和安装。在用户需要查看或与应用程序交互之前不要连接模拟器。检查/连接：

```bash
lim xcode get             # 模拟器已经连接了吗？
lim ios create --attach   # 连接一个（立即安装最后一个构建）
```

当您没有浏览器向用户展示时，请添加 `--no-open`；它跳过在本地打开流 URL，但仍打印用于共享。

如果连接输出包括一个签名的流 URL，请将其作为 Markdown 链接与用户分享，例如 `[Live simulator](<signed-stream-url>)`。

当连接了模拟器时，每个成功的 `lim xcode build` 都会自动重新安装并重新启动应用程序，不需要单独的安装步骤。要点击、输入、读取元素树、截图或录制，请切换到 **`limrun-ios-simulator`**。

## 运行测试（XCTest）

`lim xcode test` 在沙盒上构建方案的测试目标，在连接的模拟器上运行它们（单元和 UI 目标一样），并按每个测试用例一行流式传输。当任何测试失败时，exec 退出非零，因此它可以用作 CI 门。

```bash
lim xcode test .
lim xcode test ./MyProject --scheme MyApp
```

它自动获取一个模拟器支持的靶标，如 `lim xcode build --ios`，并在重复运行时重用实例，因此迭代很快。方案必须配置测试操作（从 Xcode 共享方案在项目有测试目标时有一个）。`--xcode-version 27` 使用该主要版本的 GA 构建 测试（27.1 选择 beta）；模拟器保持舰队默认运行时，所以运行会警告并继续（运行时相关的失败是可能的）。

使用 xcodebuild 的标识符格式 `Target[/Class[/method]]` 选择子集；重复标志以用于多个条目。这两个标志是互斥的：

```bash
lim xcode test . --only-testing MyAppTests/LoginTests/testValidLogin
lim xcode test . --skip-testing MyAppUITests
```

一个裸目标名称选择或跳过整个目标。一个 `--only-testing` 条目命名一个构建没有生成的目标会失败，而不是静默运行所有内容。

对于机器消耗，`--json` 将原始每个用例事件作为 NDJSON 流式传输，并在最后以 `{"exitCode": N}` 记录结束：

```bash
lim xcode test . --json > results.ndjson
```

`--build-only` 编译测试目标而不获取模拟器；产品保留在沙盒中供后续运行使用。

如果 UI 测试在多次连续运行后在一个实例上的第一次交互处失败，请在下一次运行时使用 `--inactivity-timeout 30m` 优先使用新实例。

## 签名设备构建（IPA）

当用户有 App Store Connect 团队 API 密钥时，请优先使用 Apple 云签名。Apple 创建或重用云管理的证书和配置文件，因此用户不需要提供 p12 或 `.mobileprovision`。密钥 ID、发行者 ID 和 `.p8` 文件由用户在他们的机器上配置为标志或环境变量；永远不要在对话中请求它们的值：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method release-testing --team-id "$APPLE_TEAM_ID" \
  --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --upload myapp.ipa
```

签名方法：

- `debugging`：为注册的开发设备开发签名的 IPA。
- `release-testing`：为注册的测试设备分发签名的 IPA。
- `app-store-connect`：为 App Store Connect 分发签名的 IPA。

云签名需要一个设备 SDK（`--sdk iphoneos` 或 `--sdk watchos`）、一个具有发行者 ID 的团队 API 密钥，并且 `--team-id` 与该密钥的 Apple 开发者团队匹配。对于分发方法，API 密钥必须是管理员密钥或已启用 **访问云管理的分发证书**。`Cloud signing permission error` 表示缺少权限。`No Account for Team` 表示团队 ID 和 API 密钥不匹配。`Failed Registering Bundle Identifier` 表示 Bundle ID 属于另一个团队并且无法自动注册。

云签名仅从 `--entitlements` 获取权限，从不从项目的 `.entitlements` 文件获取：存档未签名，导出仅保留现有代码签名中的权限。任何使用功能（HealthKit、CloudKit、应用组、推送）的应用程序都必须通过标志，否则功能将从 IPA 中被静默移除。一个裸路径针对应用程序；`<bundleId>=<path>` 针对一个嵌入式包（小部件、手表应用）；重复每个包：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method release-testing --team-id VMBY3VYW4U \
  --asc-key-id 2X9R4HXF34 --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --entitlements ./MyApp/MyApp.entitlements \
  --entitlements com.example.myapp.widgets=./Widgets/Widgets.entitlements \
  --upload myapp.ipa
```

plist 值必须完全展开（没有 `$(AppIdentifierPrefix)`；写具体的前缀），必须省略导出的管理键（`application-identifier`、`com.apple.developer.team-identifier`、`get-task-allow`、`beta-reports-active`），并且每个功能必须在开发者门户中的应用 ID 上启用，否则导出会失败并命名它。

当用户已经有一个 p12 和配置文件时，仍然可以使用手动签名：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --upload myapp.ipa
```

上传输出包括签名 IPA 的下载 URL。一个 SUCCEEDED 构建意味着签名已经在服务器上通过了 Apple 的验证器，所以除非用户要求，否则不要自己重新验证 IPA。无效签名会大声失败，而不是产生损坏的工件。

如果应用程序嵌入扩展（WidgetKit 小部件、共享表单、意图）或手表应用，App Store 签名需要一个为相同的分发证书签发的每个 Bundle ID 的配置文件。重复 `--provisioning-profile` 每个包一次；每个配置文件通过其内部的 `application-identifier` 匹配其 Bundle，所以顺序不重要：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --provisioning-profile widgets.mobileprovision \
  --upload myapp.ipa
```

有多个配置文件时，每个配置文件必须携带一个明确的（非通配符）Bundle ID。`signing preflight failed: no provisioning profile covers ...` 错误命名缺少配置文件的嵌入式包；请用户提供一个具有确切 Bundle ID 的配置文件。

使用包含其完整 CA 链的 p12，而不是仅包含叶证书。如果需要，使用链重新导出它：

```bash
openssl pkcs12 -export -inkey dist.key -in dist.pem -certfile wwdr.pem -out dist-chain.p12
```

在构建输出中识别的失败字符串：

- `未知发行者哈希`: p12 缺少其 CA 链；使用上述链重新导出。
- `代码签名验证失败`: 平台的签名后检查拒绝了该工件。不是用户代码的问题；重试，如果仍然存在，请报告。
- p12 密码错误: `--certificate-password` 与文件不匹配；用户需在他们的机器上更正该值。

## 上传到 App Store Connect

要上传已签名的 IPA 到 App Store Connect 用于 TestFlight 或 App Store 分发，请使用 App Store Connect API 密钥标志并传递 `--upload-to-appstore`：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --upload-to-appstore --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8
```

云签名可以使用相同的 API 密钥进行签名和上传：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method app-store-connect --team-id "$APPLE_TEAM_ID" \
  --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --upload-to-appstore --auto-build-number
```

`--upload-to-appstore` 需要 cloud signing 或手动签名标志，以及 `--asc-key-id` 和 `--asc-key`。当用户还想在 Asset Storage 中获取 IPA 时，请将其与 `--upload <asset-name>` 结合使用。

设备 IPA 包含应用符号（位于 `Payload/` 旁边的 `Symbols/`），因此 App Store Connect 可以自动符号化崩溃报告，而无需单独上传 dSYM。这需要构建生成 dSYMs：`--configuration Release` 默认会这样做；Debug 不会，并且生成的 IPA 将不包含符号。

用户在自己的机器上提供这些，作为标志或环境变量，CLI 在本地读取；它们不会被粘贴到对话中。这三个都位于 App Store Connect 的用户和访问权限下的集成选项卡中的 App Store Connect API：

- `--asc-key-id`: 旁边是其 API 密钥的 Key ID。如果没有，请指向具有 **开发者** 角色的团队密钥：可以上传构建权限最低的角色。创建团队密钥需要管理员账户。
- `--asc-issuer-id`: 集成页面顶部的发行者 ID（团队值，不是每个密钥）。云签名需要一个团队密钥和此标志。对于手动签名加上传，对于单个 API 密钥，请省略它。
- `--asc-key`: 下载的 `.p8` 文件的路径。Apple 不会保留副本，并且离开页面后下载链接会消失；如果用户丢失了它，他们必须生成一个新的密钥。切勿将 `.p8` 或其内容粘贴到文件中；传递文件系统路径。

默认情况下，构建在提交上传后立即返回，并将 Apple 的处理结果交给 App Store Connect（通常需要几分钟）。传递 `--asc-wait-timeout <seconds>`（最大 1800）以在返回前等待结果。从最后一行读取结果：

- `App Store Connect: upload accepted.`: 完成；构建在 Apple 完成后出现在 TestFlight 中。
- `App Store Connect: uploaded, still processing on Apple's side (upload <id>).`: 退出码为 0 且上传成功；Apple 仍在处理。**不要**重试构建。
- `App Store Connect upload failed; the build and signing succeeded.`: 退出码为 1，Apple 的错误文本在日志中较早的位置。只有交付失败。

需要识别的失败字符串：

- Apple 关于捆绑版本已使用的文本：增加 `CFBundleVersion`（Expo: `expo.ios.buildNumber` 在 app.json 中）并重新构建。
- `HTTP 401`: key ID / issuer ID / .p8 不匹配，或密钥已被吊销。
- `HTTP 403`: 密钥的角色不能上传构建；它需要开发者角色或更高权限。
- `no App Store Connect app with bundle id`: 应用记录不存在；用户必须手动在 App Store Connect 中创建它（API 无法做到）。
- 构建后卡在 TestFlight 的 "Missing Compliance"：应用在构建时没有回答导出合规性问题。在 Info.plist 中将 `ITSAppUsesNonExemptEncryption` 设置为 `NO`（Expo: `expo.ios.config.usesNonExemptEncryption: false` 在 app.json 中）并重新构建。

为了自动交付给测试人员，应用内部的 TestFlight 组必须启用自动分发（仅创建设置），并且必须设置上述合规性密钥；然后完全不存在上传后的步骤。

## 预览构建

仅当用户请求预览构建或您正在打开 PR 时才创建可重用的预览资产。构建并上传：

```bash
ASSET_NAME="<bundle id / pr number / or any session identifier>.zip"
lim xcode build . --upload ${ASSET_NAME}
# Debug 预览构建：
lim xcode build . --configuration Debug --upload ${ASSET_NAME}
```

构建上传默认为 14 天的 TTL：每个构建将资产的过期时间推至上传后的 14 天。传递 `--upload-ttl` 并使用 Go 时长（例如 `720h`；`1d` 无效）来更改它。

然后构建预览链接并将其包含在您的最后消息中（如果您打开 PR，请也包含在 PR 中）：

```
https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios
```

## 注意事项

- **构建错误是工作的一部分。** 如果构建失败，请阅读错误输出，修复代码，然后重新构建后再报告。
- **嵌入的 Xcode 沙盒已消失。** TypeScript SDK (0.54.0+) 和 `lim` (0.35.0+) 不再在 iOS 实例内创建 Xcode 沙盒。升级后的症状：在 `iosInstances.create` 上 `'sandbox' does not exist in type 'Spec'`，在代码读取 `status.sandbox.xcode.url` 的地方 `Property 'sandbox' does not exist on type 'Status'`，或来自 `lim xcode` 命令的 `Expected an Xcode instance (sandbox_...), got ios_...`。单独创建 Xcode 沙盒并将其附加到模拟器：`lim ios create --xcode`，或对于现有模拟器 `lim xcode create --attach --simulator-id <ios-instance-id>`；在 SDK 中 `xcodeInstances.create` 然后是 `attachNewSimulator()` 或 `attachSimulator(iosInstance)` 在其客户端上。将 `sandbox_` ID 传递给 `lim xcode` 命令，将 `ios_` ID 传递给 `lim ios` 命令。详情：https://docs.limrun.com/docs/ios/build-with-xcode#moving-off-the-embedded-xcode-sandbox
- **`lim ios` 命令的实例 ID。** 它从当前工作目录的 git 工作树解析当前实例，如果找不到最近的 ios 实例可能会失败。从 `lim xcode get` 获取 ID 并传递 `--id <ios-instance-id>`；limrun-ios-simulator 的 "Targeting the right instance" 部分中有完整配方。
- **捆绑 ID 发现。** 如果不知道捆绑 ID，请检查 Xcode 项目文件或在成功构建后运行 `lim ios list-apps`。
- **认证错误** 在认证命令上表示会话过期或 `LIM_API_KEY` 错误；用户机器上的 `lim login` 可重新生成会话。
- **构建设置覆盖 Limrun 的默认设置。** `--build-setting KEY=VALUE` 接受任何环境样式键，并用具有相同键的值替换管理值。设备构建已使用标准架构（嵌入的 Apple Watch 应用保持 `arm64_32`）并禁用覆盖率仪器，因此 App Store 上传不需要额外设置。
- **成功构建后未找到工件。** 服务器会自行解析构建的 .app，包括当方案名称与产品名称不同时（方案 "MyApp Dev" 构建 MyApp-dev.app）。如果上传仍然因 `built artifact not found` 而失败，请使用 `--artifact-name MyApp-dev.app`（包括 .app 扩展名）显式传递完整的捆绑文件名；服务器将从构建产品中直接获取该名称。
- **保持同步文件较小。** 单个 ~2MB+ 文件可能在构建开始前因 ENOMEM 失败客户端同步；压缩大型资源。
- **符号链接在相对且在根目录时同步。** 目标为绝对路径的符号链接会被警告跳过；如果构建需要它，请用相对目标重新创建。相对链接越出同步文件夹会失败同步；`--ignore` 它或从包含目标的代码库根同步。
- **签名失败是响亮且具体的。** `Unknown issuer hash` 表示 p12 缺少其 CA 链，因此请使用链重新导出；`code signature verification failed` 表示平台的签名后检查拒绝了工件，这不是代码问题，因此请重试或报告。
