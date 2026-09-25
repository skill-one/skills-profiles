# 远程 Gradle 构建

在任何环境（Linux、Windows、macOS、虚拟机、容器）中构建 Android 项目，使用 Limrun 的远程 Gradle 沙盒。`lim gradle build` 将您的源代码同步到远程实例，在那里运行项目的 Gradle 包装器，并流式传输构建输出。永远不会回退到本地 Gradle、本地 Android SDK 或本地模拟器。您的工作不会在绿色的构建后结束：让应用程序运行或交付工件，并迭代直到用户满意。

对于 iOS 构建，请使用 **`limrun-xcode`** 而不是这个技能。在任一平台上，对于 Expo 开发客户端循环（Metro、热重载），请使用 **`limrun-expo-development`**；它将返回这里进行 Android 调试构建。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（它可能设置在项目外部，所以不要因为 `.env` 或 shell 中缺失就询问它）。CLI 是事实来源：本技能中的命令是经过验证的，但如果一个标志出错或您需要这里未显示的标志，请检查 `--help` 而不是猜测：

```bash
lim gradle --help
lim gradle build --help
```

## 构建 APK

用以下方式代替 `./gradlew` 构建：

```bash
lim gradle build .
```

这将创建或重用记住的 Gradle 实例，同步当前目录，并默认运行 `assembleDebug`。使用 `--task` 明确选择任务（可重复）：

```bash
lim gradle build . --task :app:assembleRelease
```

当 Gradle 根目录嵌套且自动发现不明确时（例如一个没有 `android/` 目录的纯 React Native 仓库，其中 Gradle 位于 `android/` 中；服务器通常能自行找到它）：

```bash
lim gradle build . --project-path android
```

Expo 管理工作流项目（没有 `android/` 目录）会自动检测：沙盒在 Gradle 之前安装依赖项并运行 `expo prebuild`。设置 `--expo-app-dir`（单体仓库）或 `--abi` 会强制该流程，并在未检测到 Expo 应用时出错：

```bash
lim gradle build ./my-monorepo --expo-app-dir apps/mobile
```

对于使用 Metro 和热重载而不是普通构建来迭代 Expo 应用，请使用 **`limrun-expo-development`**。

## 分离构建和日志

使用 `--detach` 在构建被接受后返回；webhook 是可选的。`logs` 读取最新的构建，而不需要执行 ID，包括实例删除后的持久化日志；添加 `--follow` 以等待完成。

```bash
lim gradle build . --detach
lim gradle logs
lim gradle logs --follow
```

## 工具版本和 shell 命令

同步后，`lim gradle use` 选择沙盒中的工具并安装缺失的版本。运行 `lim gradle tools install` 以同步项目的工具选择（[详情](https://docs.limrun.com/docs/android/build-with-gradle)）。构建保留项目的 `gradlew`；Android SDK/NDK/CMake 使用 `sdkmanager`。

```bash
lim gradle tools
# Node 包括 npm/npx。
lim gradle use node@24 pnpm@10 yarn@4 bun@1 java@temurin-17 bundletool@1
lim gradle tools install
lim gradle run -- mise use --pin node@24.5.0
lim gradle run --env APP_ENV=staging -- npm run generate
lim gradle build . --env APP_ENV=staging
```

## 在模拟器上运行

将构建的 APK 作为命名资产上传，然后在 Android 实例上安装它：

```bash
lim gradle build . --upload myapp.apk
lim android create --install-asset=myapp.apk
```

构建上传默认为 14 天的 TTL：每次构建都会将资产的过期时间推至上传后的 14 天。使用 `--upload-ttl` 并传递 Go 时长（例如 `720h`；`1d` 无效）来更改它。

将创建输出的签名流 URL 与用户共享，作为 Markdown 链接，例如 `[Live emulator](<signed-stream-url>)`。对于重建迭代，原地修补已安装的 APK 而不是重新创建实例：

```bash
lim android sync ./path/to/app-debug.apk
```

对于设备上的其他内容（点击、输入、元素树、截图、视频、logcat over adb），请使用 **limrun-android-emulator**。

## 签署发布 AAB

默认的签名路径不需要用户的凭证：

```bash
lim gradle build . --sign --upload myapp.aab
```

首次使用时，Limrun 生成一个上传密钥库，将其作为该组织在此应用的签名密钥进行托管，并使用它进行签名。同一应用的后续 `--sign` 构建从任何机器或 CI 都使用相同的密钥，因此 Play 商店的上传保持匹配。密钥由 Android 应用 ID 命名，从 `app.json`（Expo）或 `app/build.gradle(.kts)` 检测；当检测失败或选择错误的风味时，传递 `--application-id <id>`。

`--sign` 使 `bundleRelease` 成为默认任务，并且在显式的 `--task` 列表中不包含捆绑任务的情况下，构建在开始之前会失败。成功的构建意味着 AAB 包含签名（服务器在上传前会验证它），所以除非用户要求，否则不要重新验证工件。

构建开始前会显示其中一行并传达其含义：

- `Signing with the organization's upload key for <app> (newly generated).`:
  此应用的首次构建；现在该密钥对整个组织都存在。
- `Signing with the organization's upload key for <app> (existing).`: 重用
  托管的密钥，如预期。

## 带自己的上传密钥

当应用已经有一个注册的上传密钥（现有的 Play 列表）时，使用用户的密钥库进行签名：

```bash
lim gradle build . \
  --keystore upload.jks --keystore-password "$KS_PASS" \
  --key-alias upload --key-password "$KEY_PASS" \
  --upload myapp.aab
```

所有四个标志一起传递；密码可以来自 `LIM_KEYSTORE_PASSWORD` 和 `LIM_KEY_PASSWORD` 而不是 argv。添加 `--save-key` 以托管提供的密钥，以便后续构建可以省略标志并使用普通的 `--sign`。`--save-key` 拒绝覆盖：如果应用已经托管了不同的密钥，它会在创建任何实例之前失败。

从用户那里收集：

- 密钥库文件路径（`.jks` 或 `.p12`）；永远不要将其提交或将其字节粘贴到文件中，
- 密钥库密码和密钥密码（通常是相同的值），
- 密钥别名（如果未知，可以使用 `keytool -list -keystore <file>` 显示它）。

在带自己的密钥路径上需要识别的失败字符串：

- `The organization already has a different upload key escrowed for <app>`:
  `--save-key` 冲突。使用 `--sign` 的构建使用托管的密钥；省略 `--save-key` 仅为此构建签名提供的密钥，或询问用户哪个密钥是真正的上传密钥。
- `Signing with your own key requires ... as well`: BYO 标志组不完整；消息列出了确切缺失的标志。
- `signing <field> contains an unsupported character`: 密码或别名包含 ISO-8859-1 外部的字符。使用 keytool (`-storepasswd`, `-keypasswd`, 或 `-changealias`) 在原地将其更改为拉丁-1 值。永远不要重新生成密钥本身：这将更改上传密钥。

## 发布到 Play 商店

使用 Play 凭证（通过 `--playstore-service-account` 的服务账户 JSON，或通过 `--playstore-access-token` 的访问令牌），构建会直接发布已签名的发布 AAB，无需浏览器参与：

```bash
lim gradle build . --sign --upload-to-playstore --playstore-service-account sa.json --auto-version-code
```

`--auto-version-code` 使服务器在构建之前从 Google Play 解析下一个可用的 `versionCode` 并将其戳入工作区副本（Expo 项目中的 `expo.android.versionCode` 在 `app.json` 中，常规的 `app/` 模块构建脚本中的单个字面量 `versionCode` 对于原生 Gradle 项目），因此重复发布不会冲突。如果没有它，或在具有计算或风味分割 `versionCode` 的项目中（它在请求时拒绝），请像下面这样自行管理 `versionCode`。如果没有 Play 凭证，您无法运行发布本身：这是一个带有 Google 登录的浏览器流程。准备工件，将其作为资产上传，然后交出：

```bash
lim gradle build . --sign --upload <app>-v<versionCode>.aab
```

告诉用户打开 https://console.limrun.com，并在 **Secrets** 页面点击 **Connect Play Console** 以使用具有应用发布访问权限的 Google 账户登录（会话仅存在于浏览器中；不会存储任何内容）。然后在 **Registry** 页面，他们点击上传的 AAB 上的 **Publish to Play Store** 并输入包名（应用程序 ID）。应用列表必须已经存在于 Play Console 中。Google Play 需要一个它从未见过的 `versionCode`：`--auto-version-code` 在发布构建中处理这一点；如果没有它，请在构建前在 `app/build.gradle(.kts)`（Expo：`expo.android.versionCode` 在 `app.json`）中增加 `versionCode`。

在 `--sign` 路径上需要识别的失败字符串：

- `Cannot determine the Android application ID for signing`: 检测到没有 `app.json` android.package，也没有在 `app/build.gradle(.kts)` 中的 `applicationId`；传递 `--application-id <id>`。
- `--sign produces a Play-ready signed AAB; include a bundle task`: 显式的 `--task` 列表没有捆绑任务；添加 `bundleRelease` 或省略 `--task`。
- `the built AAB carries no signature`: 服务器在构建后检查发现未签名的捆绑包；签名配置未应用。这不是用户代码的问题；重试，如果仍然存在，请报告它。

## 注意事项

- **构建错误是您的工作来修复。** 如果构建失败，请阅读错误输出，修复代码，然后重新构建。不要要求用户修复构建错误。
- **实例重用是针对 git 工作区的。** 命令从您当前工作目录的工作区解析记住的实例；传递 `--id <gradle-instance-id>`（来自 `lim gradle list`）以目标特定的实例。
- **versionCode 必须为每个 Play 上传增加。** 在发布构建上优先使用 `--auto-version-code`。一个拒绝发布说 `version code` 已经存在，意味着增加、重新构建、重新发布。如果发布重试报告它，则之前的尝试已经成功；不要再次发布。
- **应用程序 ID 检测读取第一个未注释的 `applicationId`。** 风味特定的 ID 和动态 Gradle 逻辑不在其范围内；使用 `--application-id`。
- **密钥库密码必须非空且为 ISO-8859-1。** 空密码和拉丁-1 外部的字符在请求时被拒绝，而不是在构建进行到几分钟时失败。
- **保持同步文件小且不在构建目录中。** 根级别的 `build/`、`.gradle`、`.kotlin` 以及任何 `local.properties` 都不会同步，并且 `.gitignore` 文件（包括嵌套的）会被尊重。使用 `--ignore <regex>` 来处理其他大型本地工件，并使用 `--include <regex>` 来强制同步构建需要的被 git 忽略的输入。
