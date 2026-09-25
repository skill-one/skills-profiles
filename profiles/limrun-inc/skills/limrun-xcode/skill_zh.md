# 远程 Xcode 构建

在任何环境（Linux、Windows、macOS、虚拟机、容器）中构建 Apple 项目到 Limrun 的远程 Xcode。`lim xcode build` 将您的源代码同步到远程 Xcode 实例，在那里进行构建，（当连接了模拟器时）安装并重新启动应用程序。永远不会回退到本地 Xcode、本地模拟器或本地构建工具。您的工作不会在绿色的构建结束时结束：让应用程序运行起来，验证它是否正常工作，并迭代直到用户满意。

一旦应用程序运行起来（点击、输入、元素树、截图、录制），请使用 **`limrun-ios-simulator`** 功能。对于 Bazel 工作区，请使用 **`limrun-xcode-bazel`** 而不是这个功能。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（它可能设置在项目外部，所以不要因为 `.env` 或 shell 中没有就询问它）。CLI 是真相来源：这个功能中的命令是经过验证的，但如果一个标志出错或您需要这里没有显示的标志，请检查 `--help` 而不是猜测：

```bash
lim xcode --help
lim xcode build --help
```

## 构建

用以下命令代替 `xcodebuild` 进行构建：

```bash
lim xcode build .
```

这将创建或重用记住的 Xcode 目标，同步当前目录，并通过标准输出和标准错误流传输构建日志。

如果项目有多个方案或使用工作区文件，请使用 `--scheme` 和 `--workspace`：

```bash
lim xcode build . --scheme MyApp --workspace MyApp.xcworkspace
```

使用 `--configuration Debug` 或 `--configuration Release` 为特定的 Xcode 配置。如果省略，Limrun 使用 limbuild 的项目类型默认值：为原生 Xcode 构建使用 `Debug`，为 React Native / Expo 构建使用 `Release`。

```bash
lim xcode build . --configuration Debug
```

### 分离构建和日志

使用 `--detach` 一旦构建被接受就返回；webhook 是可选的。`logs` 读取最新的构建，而不需要执行 ID，包括实例删除后的持久日志；添加 `--follow` 以等待完成。

```bash
lim xcode build . --detach
lim xcode logs
lim xcode logs --follow
```

### 选择 Xcode 版本

一个沙盒使用其 node 的默认 Xcode 构建（今天是 26.4）。舰队携带每个主要版本的一个发布（GA）Xcode 加上一个测试版，而 Apple 正在分发一个：今天是 26.4 GA、27.0 GA 和 27.1 测试版。两个选择器涵盖了它们：

- 一个主要版本（27）绑定该主要版本的最新 GA 发布，永远不会是测试版，并且会自行跟随 Apple 的点发布。用于 App Store 构建。
- 一个主要版本.次要版本（27.1）固定该确切版本。这是您选择测试版的方式。

为工作区设置一次偏好；以后的构建、测试、RBE 会话和新沙盒都将遵循它，并且该标志会覆盖一次命令：

```bash
lim xcode version list      # 选择器是您要输入的值，Channel 是 ga 或 beta；* 标记的是正在使用的那个
lim xcode use xcode@27      # 为此工作区优先使用 Xcode 27 GA；现在切换记住的沙盒
lim xcode build .           # 使用 27 构建
lim xcode version           # "27.0 (27A266a)" 显示沙盒当前的 Xcode
lim xcode version set 27.1  # 而不是 27.1 测试版
lim xcode build . --xcode-version 26   # 一次性覆盖，不记住
lim xcode version unset     # 忘记偏好；沙盒回到 node 默认
```

将 Xcode 和 mise 选择器结合起来使用 `lim xcode use xcode@27 node@24`。

对于脚本，`lim xcode version list --quiet` 每行打印一个选择器（`26`、`27`、`27.1`），`--json` 返回 `{ installed, bound, preferred }`（`installed[].channel` 是 `ga` 或 `beta`）。表格用 `*` 标记正在使用的 Xcode。`lim xcode version set` 不会记录 node 缺少的版本（错误会列出可用的版本），但在沙盒只是忙时会保留它。

当沙盒在不同于工作区偏好的 Xcode 上时，下一次构建会指出这一点并首先切换它。切换会使使用其他版本创建的构建缓存失效（下一次构建从冷启动），并且在构建、同步或 `lim xcode rbe` 堆栈运行时会被拒绝。使用持久构建缓存（`--cache-key`），为每个 Xcode 路线使用一个单独的密钥，例如 `myapp-27` 和 `myapp-27.1`：存档按密钥存储，并在使用不同 Xcode 时被擦除。

一个主要版本.次要版本的选择会持续到舰队退役该版本；然后 `lim xcode build` 会显示守护程序的消息并提示运行 `lim xcode version set 27` 或 `lim xcode version unset`。当一个测试版成为 GA 时，它会替换相同主要版本.次要版本选择器下的测试版（一次冷启动）；裸主要版本跟随其主要版本的最新发布 Xcode，所以它会在 27.1 成为 GA 时立即移动到 27.1。

从测试版 Xcode 上上传到 App Store 会被 Apple 拒绝，所以请保持 `--upload-to-appstore` 在裸主要版本上（`27`，而不是 `27.1`）。基于 `channel` 而不是 `betaSeed` 进行门控：Apple 的 27.1 种子没有种子编号。

`--dev-server-url` 仅在 `--configuration Debug` 用于 React Native / Expo 构建时受支持。它是一个安装后启动的 URL：limbuild 验证它是一个可解析的绝对 URL，然后在连接的模拟器上安装后不变地打开它。特定框架的功能会构建正确的 URL。

```bash
lim xcode build . --configuration Debug --dev-server-url '<absolute-url>'
```

如果应用程序没有使用预期的 URL 就启动了，请显式打开它以将构建/安装问题与 URL 路由分开：

```bash
lim ios open-url --id <ios-instance-id> '<absolute-url>'
```

## 开发者工具版本

同步后，`lim xcode use` 选择沙盒中的工具并安装缺失的版本。运行 `lim xcode tools install` 以同步项目的工具选择（[详细信息](https://docs.limrun.com/docs/ios/build-with-xcode)）。使用主要版本，或对于 Ruby、Flutter 和 Mint 等预 1.0 工具使用主要版本.次要版本。

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

如果存储库有一个 `project.yml` 并且 `.xcodeproj` 被 git 忽略，请不要在本地运行 xcodegen，也不要将缺失的项目视为错误。远程沙盒在构建之前从 `project.yml` 生成项目：

```bash
lim xcode build .
```

规范位于存储库根目录或下一级目录（如 `ios/`），不需要任何标志。项目在每次构建时都会重新生成，所以 `project.yml` 编辑只需重新构建即可生效。提交或强制同步的 `.xcodeproj` 总是获胜：沙盒仅在同步没有提供时才生成。

如果存储库的代码生成器产生 git 忽略的输入，构建需要（一个生成的本地 Swift 包、配置派生的源），请先在本地运行该步骤，然后使用 `--include` 强制同步其输出：

```bash
make generate   # 或者存储库的代码生成步骤是什么
lim xcode build . --include '^ios/GeneratedKit/'
```

`--include` 接受正则表达式，如 `--ignore`，而不是 gitignore 语法。要访问被整体忽略的目录下的文件，模式必须也匹配该目录路径本身，如上所示。

## 在模拟器上运行

`lim xcode build` 是构建并安装。在用户需要查看或与应用程序交互之前不要连接模拟器。检查/连接：

```bash
lim xcode get             # 模拟器已经连接了吗？
lim ios create --attach   # 连接一个（立即安装最后一个构建）
```

当您没有浏览器向用户展示时，请添加 `--no-open`；它会跳过在本地打开流 URL，但仍然打印出来以供共享。

如果连接输出包括一个已签名的流 URL，请将其作为 Markdown 链接与用户共享，例如 `[Live simulator](<signed-stream-url>)`。

当连接了模拟器时，每个成功的 `lim xcode build` 都会自动重新安装并重新启动应用程序，不需要单独的安装步骤。要点击、输入、读取元素树、截图或录制，请切换到 **`limrun-ios-simulator`**。

## 运行测试（XCTest）

`lim xcode test` 在沙盒上构建方案的测试目标，在连接的模拟器上运行它们（包括单元和 UI 目标），并按测试用例流式传输一行。当任何测试失败时，执行会退出非零，因此它可以用作 CI 门控。

```bash
lim xcode test .
lim xcode test ./MyProject --scheme MyApp
```

它会自动获取一个模拟器支持的靶标，如 `lim xcode build --ios`，并在重复运行时重用实例，所以迭代很快。方案必须配置测试操作（从 Xcode 源共享的方案在项目有测试目标时有一个）。`--xcode-version 27` 使用该主要版本的 GA 构建测试（27.1 选择测试版）；模拟器保持舰队默认运行时，所以运行时会警告并继续（可能存在依赖于运行时的失败）。

使用 xcodebuild 的标识符格式 `Target[/Class[/method]]` 选择子集；重复标志以用于多个条目。这两个标志是互斥的：

```bash
lim xcode test . --only-testing MyAppTests/LoginTests/testValidLogin
lim xcode test . --skip-testing MyAppUITests
```

一个裸目标名称选择或跳过整个目标。一个 `--only-testing` 条目命名构建没有生成的目标会导致运行失败而不是静默运行所有内容。

对于机器消费，`--json` 将原始每个用例事件作为 NDJSON 流式传输，并在最后以 `{"exitCode": N}` 记录结束：

```bash
lim xcode test . --json > results.ndjson
```

`--build-only` 编译测试目标但不获取模拟器；产品保留在沙盒中供后续运行使用。

如果 UI 测试在多次连续运行后在一个实例上的第一次交互处失败，请在下一次运行时使用 `--inactivity-timeout 30m` 优先使用新实例。

## 签名设备构建（IPA）

当用户有 App Store Connect 团队 API 密钥时，请优先使用 Apple 云签名。Apple 创建或重用云管理的证书和配置文件，所以用户不需要提供 p12 或 `.mobileprovision`：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method release-testing --team-id "$APPLE_TEAM_ID" \
  --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --upload myapp.ipa
```

签名方法：

- `debugging`：为注册的开发设备生成开发签名的 IPA。
- `release-testing`：为注册的测试设备生成分发签名的 IPA。
- `app-store-connect`：为 App Store Connect 生成分发签名的 IPA。

云签名需要一个设备 SDK（`--sdk iphoneos` 或 `--sdk watchos`）、一个具有发行者 ID 的团队 API 密钥，以及与该密钥的 Apple 开发者团队匹配的 `--team-id`。对于分发方法，API 密钥必须是管理员密钥或具有**访问云管理的分发证书**的权限。`Cloud signing permission error` 表示缺少权限。`No Account for Team` 表示团队 ID 和 API 密钥不匹配。`Failed Registering Bundle Identifier` 表示 Bundle ID 属于另一个团队，无法自动注册。

云签名仅从 `--entitlements` 获取权限，从不从项目的 `.entitlements` 文件获取：存档未签名，导出仅保留现有代码签名中的权限。任何使用功能（HealthKit、CloudKit、应用组、推送）的应用程序**必须**通过标志，否则功能将从 IPA 中被静默移除。一个裸路径针对应用程序；`<bundleId>=<path>` 针对一个嵌入式包（小部件、手表应用）；每个包重复一次：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method release-testing --team-id VMBY3VYW4U \
  --asc-key-id 2X9R4HXF34 --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --entitlements ./MyApp/MyApp.entitlements \
  --entitlements com.example.myapp.widgets=./Widgets/Widgets.entitlements \
  --upload myapp.ipa
```

plist 值必须完全展开（没有 `$(AppIdentifierPrefix)`；写具体的前缀），必须省略导出的键（`application-identifier`、`com.apple.developer.team-identifier`、`get-task-allow`、`beta-reports-active`），并且每个功能必须在开发者门户中的应用 ID 上启用，否则导出会失败并命名它。

当用户已经有一个 p12 和配置文件时，仍然可以使用手动签名：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --upload myapp.ipa
```

上传输出包括已签名 IPA 的下载 URL。一个成功的构建意味着签名已经在服务器上通过了 Apple 的验证器，所以不要自己重新验证 IPA，除非用户要求。无效的签名会大声失败，而不是生成损坏的工件。

如果应用程序嵌入扩展（WidgetKit 小部件、共享表单、意图）或手表应用，App Store 签名需要一个为相同的分发证书签发的每个 Bundle ID 的配置文件。重复 `--provisioning-profile` 每个包一次；每个配置文件都通过其内部的 `application-identifier` 与其 Bundle 匹配，所以顺序不重要：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --provisioning-profile widgets.mobileprovision \
  --upload myapp.ipa
```

使用多个配置文件时，每个配置文件都必须携带一个明确的（非通配符）Bundle ID。一个 `signing preflight failed: no provisioning profile covers ...` 错误命名了缺少配置文件的嵌入式包；请向用户要一个具有确切 Bundle ID 的配置文件。

使用包含其完整 CA 链的 p12，而不仅仅是叶证书。如果需要，可以使用链重新导出它：

```bash
openssl pkcs12 -export -inkey dist.key -in dist.pem -certfile wwdr.pem -out dist-chain.p12
```

构建输出中要识别的失败字符串：

- `Unknown issuer hash`：p12 缺少其 CA 链；像上面那样使用链重新导出它。
- `code signature verification failed`：平台的签名后检查拒绝了该工件。不是代码问题；重试或报告它。
- p12 密码错误：`--certificate-password` 与文件不匹配；请向用户要正确的密码。

## 上传到 App Store Connect

要上传已签名的 IPA 到 App Store Connect 以进行 TestFlight 或 App Store 分发，请在已签名的设备构建上传递 `--upload-to-appstore` 和 App Store Connect API 密钥标志：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --certificate-p12 dist.p12 --certificate-password "$P12_PASSWORD" \
  --provisioning-profile app.mobileprovision \
  --upload-to-appstore --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8
```

云签名可以使用相同的 API 密钥签名并上传：

```bash
lim xcode build . --sdk iphoneos --configuration Release \
  --signing-method app-store-connect --team-id "$APPLE_TEAM_ID" \
  --asc-key-id "$ASC_KEY_ID" --asc-issuer-id "$ASC_ISSUER_ID" \
  --asc-key AuthKey.p8 \
  --upload-to-appstore --auto-build-number
```

`--upload-to-appstore` 需要云签名或手动签名标志，加上 `--asc-key-id` 和 `--asc-key`。将它与 `--upload <asset-name>` 结合使用，当用户还想在资产存储中保留 IPA 时。

设备 IPA 包含应用程序的符号（`Symbols/` 位于 `Payload/` 旁边），所以 App Store Connect 会自动符号化崩溃报告，而无需单独的 dSYM 上传。这需要构建生成 dSYMs：`--configuration Release` 默认这样做；Debug 不这样做，并且 IPA 然后简单地没有符号地发货。

从用户那里收集（所有三个都位于 App Store Connect 的用户和访问、集成选项卡、App Store Connect API 下）：

- `--asc-key-id`：他们 API 密钥旁边的关键 ID。如果他们没有，请让他们指向具有**开发者**角色的团队密钥：可以上传构建的最少权限角色。创建团队密钥需要一个管理员帐户。
- `--asc-issuer-id`：集成页面顶部（团队值，不是每个密钥的）的发行者 ID。云签名需要一个团队密钥和这个标志。对于手动签名加上上传，对于单个 API 密钥，省略它。
- `--asc-key`：下载的 `.p8` 文件的路径。Apple 不会保留副本，并且离开页面后下载链接会消失；如果用户丢失了，他们必须生成一个新的密钥。永远不要提交 `.p8` 或将内容粘贴到文件中；传递文件系统路径。

默认情况下，构建一提交就返回，并将 Apple 的处理结果留给 App Store Connect（处理通常需要许多分钟）。传递 `--asc-wait-timeout <seconds>`（最大 1800）以等待结果再返回。从最后一行读取结果：

- `App Store Connect: upload accepted.`：完成；构建一旦 Apple 完成就会出现在 TestFlight 中。
- `App Store Connect: uploaded, still processing on Apple's side (upload <id>).`：退出码为 0，上传成功；Apple 仍在处理。**不要**重试构建。
- `App Store Connect upload failed; the build and signing succeeded.`：退出码为 1，前面有 Apple 的错误文本。只有交付失败了。

要识别的失败字符串：

- Apple 关于 Bundle 版本已使用的文本：增加 `CFBundleVersion`（Expo：`expo.ios.buildNumber` 在 app.json 中）并重新构建。
- `HTTP 401`：关键 ID / 发行者 ID / .p8 不匹配，或者密钥已被吊销。
- `HTTP 403`：密钥的角色不能上传构建；它需要开发者角色或更高权限。
- `no App Store Connect app with bundle id`：应用程序记录不存在；用户必须手动在 App Store Connect 中创建它（API 无法）。
- 构建后来在 TestFlight 中卡在“缺少合规性”：应用程序在构建时没有回答导出合规性问题。在 Info.plist 中设置 `ITSAppUsesNonExemptEncryption` 为 `NO`（Expo：`expo.ios.config.usesNonExemptEncryption: false` 在 app.json 中）并重新构建。

对于无人工干预的交付给测试人员，应用程序的内部 TestFlight 组必须启用自动分发（仅创建设置），并且必须设置上述合规性键；然后完全不存在后续上传步骤。

## 预览构建

仅在用户要求预览构建或您正在打开 PR 时才创建可重用的预览资产。构建并上传：

```bash
ASSET_NAME="<bundle id / pr number / or any session identifier>.zip"
lim xcode build . --upload ${ASSET_NAME}
# Debug 预览构建：
lim xcode build . --configuration Debug --upload ${ASSET_NAME}
```

构建上传默认有效期 14 天：每次构建都会将资产的过期时间推迟到上传后的 14 天。传递 `--upload-ttl` 并使用 Go 时长（例如 `720h`；`1d` 无效）来更改它。

然后构建预览链接，并将其包含在您的最后一条消息中（如果您打开 PR，请也包含在 PR 中）：

```
https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios
```

## 注意事项

- **构建错误需要您来修复。** 如果构建失败，请阅读错误输出，修复代码，然后重新构建。不要要求用户修复构建错误。
- **`lim ios` 命令的实例 ID。** 它从您 cwd 的 git 工作树解析当前实例，并且可能会因 `No instance ID provided and no recent ios instance found` 而失败。从 `lim xcode get` 获取 ID 并传递 `--id <ios-instance-id>`；limrun-ios-simulator 的“定位正确的实例”部分中有完整的配方。
- **Bundle ID 发现。** 如果您不知道 Bundle ID，请检查 Xcode 项目文件或运行 `lim ios list-apps` 后成功构建。
- **认证错误** 在已认证的命令上意味着会话过期或 `LIM_API_KEY` 不正确；请让用户运行 `lim login` 或提供密钥。
- **构建设置覆盖 Limrun 的默认值。** `--build-setting KEY=VALUE` 接受任何环境样式键，并用具有相同键的值替换管理的值。设备构建已经使用标准架构（嵌入式手表应用保留 `arm64_32`）并禁用覆盖率仪器，所以 App Store 上传不需要额外设置。
- **成功构建后找不到工件。** 服务器会自行解析构建的 .app，包括当方案名称与产品名称不同时（方案 "MyApp Dev" 构建 MyApp-dev.app）。如果上传仍然因 `built artifact not found` 失败，请使用 `--artifact-name MyApp-dev.app` 显式传递完整的 Bundle 文件名（包括 .app 扩展名）；服务器然后会从构建产品中逐字获取该名称。
- **保持同步文件大小。** 一个约 2MB+ 的单个文件可能在构建开始前因 ENOMEM 而导致客户端同步失败；压缩大型资源。
- **相对路径且位于根目录的符号链接会同步。** 一个目标为绝对路径的符号链接会被警告跳过；如果构建需要它，请使用相对目标重新创建它。一个从同步文件夹外逃逸的相对链接会导致同步失败；使用 `--ignore` 它或从包含目标的存储库根目录同步。
- **签名失败是响亮且具体的。** `Unknown issuer hash` 意味着 p12 缺少其 CA 链，所以像上面那样使用链重新导出它；`code signature verification failed` 意味着平台的签名后检查拒绝了工件，这不是代码问题，所以重试或报告它。
