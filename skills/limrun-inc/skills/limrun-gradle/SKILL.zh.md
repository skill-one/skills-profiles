---
name: limrun-gradle
description: 通过远程 Gradle 沙箱使用 `lim gradle build` 构建 Android 应用，替代本地 Gradle 或 Android Studio，支持从任意环境（Linux、Windows、macOS、虚拟机、容器）运行。适用于以下场景：用户需要构建 APK 或 AAB、使用上传密钥为发布版本签名、准备 Play 商店发布、查看构建日志，或在原生 Android 项目、React Native 及 Expo 项目中选择沙箱工具并运行 Shell 命令。若要在模拟器上运行、点击、截图或以其他方式与已构建的 APK 进行交互，请使用 limrun-android-emulator。若需构建 iOS 应用，请使用 limrun-xcode 或 limrun-expo-development。
---

# 远程 Gradle 构建

在 Limrun 的远程 Gradle 沙盒中构建 Android 项目，可在任何环境（Linux、Windows、macOS、虚拟机、容器）中进行。`lim gradle build` 会将您的源代码同步到远程实例，在那里运行项目的 Gradle 包装器，并流式传输构建输出。此工作流程在远程实例上构建；它不包括本地 Gradle、本地 Android SDK 和本地模拟器。完成的运行会在 Limrun 模拟器上运行应用程序或交付工件。

对于 iOS 构建，请使用 **`limrun-xcode`** 而不是此技能。对于两个平台上的 Expo 开发客户端循环（Metro、热重载），请使用 **`limrun-expo-development`**；它将返回此处以进行 Android 调试构建。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（即使 `.env` 和 shell 没有显示，它也可能已经在用户的环境中设置；在要求它之前进行检查）。CLI 是事实来源：此技能中的命令是经过验证的，但如果一个标志出错或您需要这里未显示的标志，请检查 `--help` 而不是猜测：

```bash
lim gradle --help
lim gradle build --help
```

## 构建 APK

用以下方式代替 `./gradlew` 进行构建：

```bash
lim gradle build .
```

这将创建或重用记住的 Gradle 实例，同步当前目录，并默认运行 `assembleDebug`。使用 `--task` 明确选择任务（可重复）：

```bash
lim gradle build . --task :app:assembleRelease
```

当 Gradle 根目录嵌套且自动发现不明确时（例如一个没有 `android/` 目录的纯 React Native 仓库，其中 Gradle 位于 `android/` 中；服务器通常可以自行找到它）使用 `--project-path`：

```bash
lim gradle build . --project-path android
```

Expo 管理工作流项目（没有 `android/` 目录）会自动检测：沙盒在 Gradle 之前安装依赖项并运行 `expo prebuild`。设置 `--expo-app-dir`（单体仓库）或 `--abi` 会强制使用该管道，并在未检测到 Expo 应用时出错：

```bash
lim gradle build ./my-monorepo --expo-app-dir apps/mobile
```

对于使用 Metro 和热重载而不是普通构建来迭代 Expo 应用，请使用 **`limrun-expo-development`**。

## 分离构建和日志

使用 `--detach` 在构建被接受后返回；webhook 是可选的。`logs` 读取最新的构建，而不需要 exec ID，包括实例删除后的持久化日志；添加 `--follow` 以等待完成。

```bash
lim gradle build . --detach
lim gradle logs
lim gradle logs --follow
```

## 工具版本和 shell 命令

同步后，`lim gradle use` 选择沙盒中的工具并安装缺失的版本。运行 `lim gradle tools install` 以进行同步项目的工具选择（[详情](https://docs.limrun.com/docs/android/build-with-gradle)）。构建保留项目的 `gradlew`；Android SDK/NDK/CMake 使用 `sdkmanager`。

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

将创建输出中的签名流 URL 与用户共享，作为 Markdown 链接，例如 `[Live emulator](<signed-stream-url>)`。对于重建迭代，请在原地修补已安装的 APK，而不是重新创建实例：

```bash
lim android sync ./path/to/app-debug.apk
```

对于设备上的其他内容（点击、输入、元素树、截图、视频、logcat over adb），请使用 **limrun-android-emulator**。

## 签署发布 AAB

默认的签名路径不需要用户的凭证：

```bash
lim gradle build . --sign --upload myapp.aab
```

首次使用时，Limrun 生成一个上传密钥库，将其作为该组织在此应用程序上的签名密钥托管，并使用它进行签名。同一应用程序的后续 `--sign` 构建从任何机器或 CI 都使用相同的密钥，因此 Play Store 上传保持匹配。密钥由 Android 应用程序 ID 命名，从 `app.json`（Expo）或 `app/build.gradle(.kts)` 检测；如果检测失败或选择了错误的变体，请传递 `--application-id <id>`。

`--sign` 使 `bundleRelease` 成为默认任务，并且在启动之前，如果显式的 `--task` 列表不包含捆绑任务，构建将失败。成功的构建意味着 AAB 包含签名（服务器在上传之前验证它），因此除非用户要求，否则不要重新验证工件。

构建开始前，预期会出现以下其中一行并传达其含义：

- `Signing with the organization's upload key for <app> (newly generated).`:
  此应用程序的首个构建；现在该密钥已存在于整个组织中。
- `Signing with the organization's upload key for <app> (existing).`: 重用
  托管的密钥，如预期。

## 带自己的上传密钥

当应用程序已经有一个注册的上传密钥（一个现有的 Play 列表）时，用户可以使用自己的密钥库进行签名。密钥库路径、密钥别名和两个密码都由用户在自己的机器上提供，作为 `--keystore`、`--key-alias`、`--keystore-password` 和 `--key-password` 标志或 `LIM_KEYSTORE_PASSWORD` 和 `LIM_KEY_PASSWORD` 环境变量（`lim gradle build --help` 列出了它们）。永远不要在对话中要求或处理这些值；如果缺少一个，请命名要设置的标志或变量。所有四个值一起传递。添加
`--save-key` 以托管提供的密钥，以便后续构建可以省略标志并使用普通的 `--sign`。`--save-key` 拒绝覆盖：如果应用程序已经托管了不同的密钥，则在创建任何实例之前都会失败。

密钥库文件本身保留在用户的机器上：永远不要将其提交或将其字节粘贴到文件中。`keytool -list -keystore <file>` 在用户不知道别名时显示别名。

在带自己的密钥路径上需要识别的失败字符串：

- `The organization already has a different upload key escrowed for <app>`:
  `--save-key` 冲突。使用 `--sign` 的构建使用托管的密钥；丢弃
  `--save-key` 仅为此构建签名提供的密钥库，或询问用户哪个密钥是真正的上传密钥。
- `Signing with your own key requires ... as well`: BYO 标志组不完整；消息列出了确切的缺失标志。
- `signing <field> contains an unsupported character`: 密码或别名包含 ISO-8859-1 外部的字符。使用 keytool
  (`-storepasswd`, `-keypasswd`, 或 `-changealias`) 在原地将其更改为拉丁-1 值。永远不要重新生成密钥本身：那会改变上传密钥。

## 发布到 Play Store

当用户在自己的机器上配置了 Play 凭证（服务账户 JSON 文件或访问令牌，通过 `--playstore-service-account` 或 `--playstore-access-token` 标志传递）时，构建会直接发布已签名的发布 AAB，无需浏览器。永远不要在对话中要求这些凭证：

```bash
lim gradle build . --sign --upload-to-playstore --playstore-service-account sa.json --auto-version-code
```

`--auto-version-code` 使服务器在构建之前从 Google Play 解析下一个可用的 `versionCode` 并将其戳入工作区副本
（Expo 项目中的 `expo.android.versionCode` 在 app.json 中，常规 `app/` 模块构建脚本中的单个字面量 `versionCode` 对于原生 Gradle 项目），因此重复发布不会冲突。如果没有它，或者对于具有计算或变体拆分 `versionCode` 的项目（它在请求时拒绝），请像下面这样自行管理 `versionCode`。没有 Play 凭证，您无法运行发布本身：它是一个带有 Google 登录的浏览器流程。准备工件，将其作为资产上传，然后交出：

```bash
lim gradle build . --sign --upload <app>-v<versionCode>.aab
```

告诉用户打开 https://console.limrun.com 并，在 **Secrets** 页面上，点击 **Connect Play Console** 以使用具有应用程序发布访问权限的 Google 账户登录（会话仅存在于浏览器中；不会存储任何内容）。然后在 **Registry** 页面上，他们点击上传的 AAB 上的 **Publish to Play Store** 并输入包名（应用程序 ID）。应用程序列表必须已经存在于 Play Console 中。Google Play 需要一个它从未见过的 `versionCode`：`--auto-version-code` 在发布构建中处理这一点；如果没有它，请在构建之前在 `app/build.gradle(.kts)` 中增加 `versionCode`（Expo：
`expo.android.versionCode` 在 app.json 中）。

在 `--sign` 路径上需要识别的失败字符串：

- `Cannot determine the Android application ID for signing`: 检测到没有 `app.json` android.package，并且在 `app/build.gradle(.kts)` 中没有 `applicationId`；传递 `--application-id <id>`。
- `--sign produces a Play-ready signed AAB; include a bundle task`: 显式的 `--task` 列表没有捆绑任务；添加 `bundleRelease` 或丢弃 `--task`。
- `the built AAB carries no signature`: 服务器的构建后检查发现未签名的捆绑包；签名配置未应用。不是用户代码的问题；重试，如果它仍然存在，请报告。

## 注意事项

- **构建错误是工作的一部分。** 如果构建失败，请阅读错误输出，修复代码，并在报告之前重新构建。
- **实例重用是针对 git 工作树的。** 命令从您 cwd 的工作树解析记住的实例；传递 `--id <gradle-instance-id>`
  （从 `lim gradle list` 获取）以针对特定的实例。
- **versionCode 必须为每个 Play 上传增加。** 在发布构建上优先使用
  `--auto-version-code`。拒绝发布说 `version code` 已经存在意味着增加，重新构建，重新发布。如果发布重试报告它，则之前的尝试已经成功；不要再次发布。
- **应用程序 ID 检测读取第一个未注释的 `applicationId`。** 变体特定的 ID 和动态 Gradle 逻辑不在其范围内；使用
  `--application-id`。
- **密钥库密码必须非空且为 ISO-8859-1。** 空密码和拉丁-1 外部的字符在请求时被拒绝，而不是在构建进行几分钟后才失败。
- **保持同步文件小且不在构建目录中。** 根级别的 `build/`、`.gradle`、`.kotlin` 和任何 `local.properties` 都不会同步，并且 `.gitignore`
  文件（包括嵌套的）会受到尊重。使用 `--ignore <regex>` 以进行其他大型本地工件，并使用 `--include <regex>` 强制同步构建需要的 git 忽略输入。
