---
name: solana-mobile-publishing
description: 使用 dapp-store CLI 为 Solana dApp Store 构建、签名并发布 Android APK。适用于首次将 Solana 移动应用发布到 dApp Store、发布更新、签名发布 APK、设置发布者账户和 App NFT，或调试在调试模式下运行正常的发布构建。
---

# 发布到 Solana dApp Store

发布到 dApp Store 分为一次性设置和每次发布循环中的构建、签名、发布。一次性设置部分包含不可逆的决策，因此应在首次发布前而不是之后正确完成。

```bash
npm install -g @solana-mobile/dapp-store-cli@latest
```

需要 Node 18 或更高版本。如果不想全局安装，可以使用 `npx @solana-mobile/dapp-store-cli`。

**使用 1.0.1 或更高版本。** 更早版本已弃用且无法使用。

## 不可协商的限制

**仅限 APK。`.aab` 会被拒绝。** 使用 `assembleRelease` 构建，而不是 `bundleRelease`。这可以避免那些肌肉记忆来自 Google Play 的人，在 Google Play 中，默认情况下是使用捆绑包。

**密钥库和发布者钱包都是永久的。** 更新必须使用与之前发布相同的密钥签名，并且 App NFT 存储在发布者钱包中。丢失任何一个都没有恢复路径，也没有支持票可以修复它——只能从新身份重新列出应用程序。它们都不应存储在存储库中：在生成密钥库之前询问它应该存储在哪里，并确保它不在项目树中。

**如果您也发布到 Google Play，请使用不同的签名密钥。** 每个商店一个密钥。共享一个密钥意味着妥协或丢失会影响两个列表。

## 首先：确定您处于哪种情况

| 情况 | 执行此操作 |
| --- | --- |
| 尚无发布者账户 | [一次性设置](#一次性设置) |
| 发布者已存在，正在发布版本 | [构建已签名的 APK](#构建已签名的-apk)，然后 [发布](#发布) |
| 正在向已发布的应用程序发布更新 | [发布更新](#发布更新) |
| 发布构建崩溃但调试正常 | 阅读 [references/signing.md](references/signing.md#release-only-failures) |
| 发布中途失败 | [恢复失败的发布](#恢复失败的发布) |
| 应用程序是一个包装的 Web 应用程序，而不是 React Native | [Web 应用程序](#web-apps) |

## 一次性设置

### 首先是发布者密钥对

CLI 以发布者身份签名，使用密钥**文件**，在浏览器门户中连接钱包不会生成一个。在注册任何内容之前解决该文件，因为门户中连接的钱包必须是相同的密钥——以其他顺序到达意味着将浏览器钱包的私钥导出到磁盘，这在各个方面都更糟。

如果已经存在用于此目的的密钥对，请使用其路径，并询问哪个，而不是伸手去拿 `~/.config/solana/id.json` 中持有的任何内容——那通常是可丢弃的开发密钥，使用错误的密钥意味着门户不识别发布者。

如果还没有密钥对，**开发者生成它，而不是代理**：

```bash
solana-keygen new --silent --outfile ~/.config/solana/publisher.json
```

`--silent` 抑制种子短语。如果没有它，十二个词会输出到 stdout，而代理的 stdout 是一个记录和日志文件——钱包以明文形式存储在无人看管的地方。仅在终端输出不被记录的情况下才丢弃 `--silent`，并以任何方式备份密钥对文件：在抑制短语的情况下，该文件是唯一副本。代理应该只被交给路径。

将文件与发布密钥库完全一样对待：它控制的应用程序 NFT 与之一样永久，因此它属于秘密存储或密码管理器，永远不会在存储库中。有关相同推理应用于 Android 密钥的说明，请参阅 [references/signing.md](references/signing.md#create-the-keystore)。

### 然后注册发布者

将密钥对导入您长期控制的钱包，并使用它在 https://publish.solanamobile.com 注册。门户创建发布者，获取 dApp 列表详细信息，并铸造 App NFT。

创建列表与铸造 App NFT 不是同一个步骤，CLI 都无法执行——它发布已存在的应用程序的版本。一个已填写但 App NFT 从未铸造的列表在门户中看起来完整，但在发布的第二步失败，提示 `App NFT and wallet authority must exist before publishing a version`。在首次发布之前确认列表既有 App NFT 又有钱包授权。

在开始之前为钱包充值——门户目前要求大约 0.2 SOL 来覆盖交易费和元数据存储。将此数字视为指示，并阅读门户实际引用的数字，因为它随着租金和存储定价而变化。这是注册成本，并且与 CLI 自己的预发布分离，除非签名者持有 0.016 SOL，否则它拒绝启动发布。

然后在 **Dashboard > Settings > API keys** 处铸造一个 API 密钥，并将其放入环境：

```bash
export DAPP_STORE_API_KEY='paste-the-portal-api-key'
```

`DAPP_STORE_API_KEY` 是 CLI 默认读取的变量。在交互式提示符中键入，该 `export` 也会出现在 shell 的历史文件中，因此最好从秘密管理器中提取它，而不是粘贴它。`--api-key-env <name>` 指向不同的变量，而 `--api-key-stdin` 从 stdin 读取密钥，这在 CI 中更容易导出而不是管道，是更好的选择：

```text
printf '%s' "$DAPP_STORE_API_KEY" | dapp-store --api-key-stdin <publish flags>
```

这只是传递形状——完整的调用在 [发布](#发布) 下，此时您还没有构建 APK。

两个标志用于指向非生产门户：`--local-dev` 允许本地主机门户并跳过自我更新门，而 `--skip-self-update` 跳过自己的门——但只能与 `--local-dev` 一起使用，单独传递它将失败，提示 `` `--skip-self-update` is only allowed together with `--local-dev` ``。本地开发模式会拒绝任何不是本地的门户 URL，因此它不是到达托管暂存门户的方式；使用 `--portal-url`。

## 构建已签名的 APK

适用的命令取决于谁持有密钥库——与 [references/signing.md](references/signing.md#which-signing-path-applies) 中的分割相同。

**EAS 管理的凭据。** 使用 `dapp-store` 配置文件构建，它强制使用 APK：

```bash
eas build --platform android --profile dapp-store
```

EAS 签名它并返回下载 URL，因此在此流程中没有 `android/app/build/outputs/` 路径。要么下载工件并发布本地文件，要么将 URL 传递给 `--apk-url` 并跳过下载——但对于更新，需要下载它，因为 `--apk-url` 也跳过了下面的签名检查。

**本地签名**——纯 React Native，或本地构建的 Expo：

```bash
(cd android && ./gradlew :app:assembleRelease)
```

子 shell 很重要：如果没有它，`cd` 会持续存在，并且每个后续命令中的存储库根相对路径都会解析到 `android/` 并失败。

APK 会落在 `android/app/build/outputs/apk/release/app-release.apk`。

**无论如何，在上传之前确认 APK 都是由您预期的密钥签名的。** `$APK` 在此和 [发布](#发布) 中是构建生成的哪个文件——上面的 Gradle 输出路径，或从 EAS 下载的工件。

```bash
"$ANDROID_HOME"/build-tools/<version>/apksigner verify --print-certs "$APK"
```

`apksigner` 在正常 Android SDK 安装中不在 `PATH` 上——一个简单的 `apksigner` 会得到 `command not found`。它位于 `$ANDROID_HOME/build-tools/<version>/` 下；选择安装的最新版本。

`apksigner verify` 读取 APK 并无其他——没有密钥库，没有私钥——因此它适用于下载的 EAS 工件，就像适用于本地构建一样。在更新中，比较打印的 SHA-256 指纹与之前的发布。这种比较是上传前唯一捕获使用错误密钥库构建的方法，更新中的错误密钥是唯一没有恢复路径的失败。

**阅读证书名称，而不仅仅是退出代码。** 一个标准的 Expo 预构建将发布变体连接到*调试*密钥库，因此未配置的发布 APK 是签名的——只是用错误的密钥。`apksigner verify` 愉快地通过它。如果打印的 DN 是 `CN=Android Debug`，则签名配置从未生效；请参阅
[references/signing.md](references/signing.md#gradle-signing-config)。

上传前值得检查的最后一件事：默认的 React Native 发布 APK 捆绑了每个 ABI，并且运行到 100 MB 以上。为单个架构构建（`./gradlew :app:assembleRelease -PreactNativeArchitectures=arm64-v8a`）通常可以将大小减少一半以上。

密钥库创建、Gradle 签名配置、EAS 构建配置以及仅在发布构建中出现的失败模式：[references/signing.md](references/signing.md)。

## 发布

一个命令，用于首次发布和之后的每个发布：

```bash
dapp-store \
  --apk-file "$APK" \
  --keypair ~/.config/solana/publisher.json \
  --whats-new "Initial release"
```

`$APK` 是构建步骤的文件——Gradle 输出路径或下载的 EAS 工件。没有默认值，并且只有当您自己复制到那里时，`./app-release.apk` 才有效。EAS 构建 URL 可以直接到 `--apk-url https://…`，这会发布托管的 APK 而无需本地副本。

`--keypair <path>` 选择 Solana 签名者。CLI 假设没有默认密钥对路径，因此需要显式传递它；上面的路径是持有发布者身份的密钥对的占位符。`--verbose` 打印发布和会话标识符，这是如果运行失败时您需要的东西。

门户本身驱动发布，因此没有配置用于此目的的 RPC 端点。`--rpc-url <url>` 存在，但它在 `--help` 中隐藏，并且它只用于在提交前检查签名者的余额。门户本身默认为 `https://publish.solanamobile.com`；`--portal-url <url>` 或 `DAPP_STORE_PORTAL_URL` 重定向它，您只有在 Solana Mobile 给您暂存门户时才需要它。

**重定向门户也意味着重定向 RPC。** 那个预发布读取 whatever `--portal-url` 说的主网，因此开发网上的暂存门户在发布开始前会拒绝已资助的钱包：

```text
Signer <address> has 0.000000 SOL, but publishing needs at least 0.016000 SOL available
```

余额是真实的，只是在另一个集群上。一起传递 `--portal-url` 和 `--rpc-url`：

```bash
dapp-store \
  --apk-file "$APK" \
  --keypair ~/.config/solana/publisher.json \
  --whats-new "Initial release" \
  --portal-url https://staging.publish.solanamobile.com \
  --rpc-url https://api.devnet.solana.com
```

CLI 在启动时调用 `dotenv.config()`，因此工作目录中的 `.env` 提供了该变量和 API 密钥，而无需说明。在自己的项目中很方便，但在克隆的您未创建的存储库中是一个隐患：其他人提交的 `DAPP_STORE_PORTAL_URL` 将您的 API 密钥发送到他们的主机，并且关于它的唯一检查是它是 HTTPS。在从您未创建的存储库发布之前读取 `.env`，并显式传递 `--portal-url` 以覆盖它设置的任何内容。

门户根据 APK 的包名推断它是更新哪个应用程序，因此该名称必须与设置期间创建的列表匹配。不匹配会读取为缺少应用程序，而不是命名错误。该名称来自 Expo 的 `expo.android.package` 和纯项目的 `android/app/build.gradle` 中的 `applicationId`——检查您的项目实际拥有的。

如果您正在脚本化此操作，请传递 `--idempotency-key <key>`，并**在重试该发布的每个尝试中重复相同的值**。省略它不是一个中性的默认值：CLI 每次调用生成一个 `randomUUID()`，因此重试看起来像一个新的发布，并且可能会发布两次。在第一次尝试之前捕获密钥和发布 ID。

### 恢复失败的发布

发布是一个多步骤会话。失败是否留下任何要恢复的内容取决于它在哪里失败：在铸造步骤期间失败的会话会被回滚，并且 CLI 会说明这一点——`Rolling back failed publication release` / `Failed publication release cleaned up`。在此消息之后没有会话剩余，并且发布一个新发布是正确的操作。当运行因网络中断而失败时，请使用 `resume`：

```bash
dapp-store resume \
  --release-id "$RELEASE_ID" \
  --keypair ~/.config/solana/publisher.json
```

`resume` 以与发布相同的方式验证 `--keypair`，如果没有它，会失败，提示 `--keypair is required` 错误。传递 **恰好一个** 的 `--release-id` 或 `--session-id`——同时提供两者会被直接拒绝，尽管 `--help` 中的使用行显示它们一起出现。

这两个标识符都来自原始运行的输出，这是任何非交互式操作的 `--verbose` 的参数。注意 `--verbose` 打印*何时*：发布 ID 和发布会话 ID 只在 APK 摄入成功后才会发出。一个在摄入期间失败的运行只打印一个**摄入**会话 ID，这是一个不同的标识符——`--session-id` 想要发布会话 ID，并且不会接受它。一个早期失败的会话没有任何要恢复的；修复原因并再次发布。

## 发布更新

与首次发布相同的命令。有三个条件必须满足，否则它会失败或无声地不发布任何新内容：

- **增加 `versionCode`** — 但在真正拥有它的文件中。在一个纯项目中，它是 `android/app/build.gradle`。在 Expo 中，它是 `app.json` 或 `app.config.*` 中的 `expo.android.versionCode`，并且编辑那里的 `build.gradle` 是无意义的，因为预构建会重新生成它。一个新创建的 Expo 应用程序通常在 `app.json` 中根本没有 `expo.version` 或 `expo.android.versionCode`——Expo 会回退到 `1.0.0` 和 `1`。在首次发布之前添加这两个键，而不是在需要更高版本时才发现它们缺失。如果 `cli.appVersionSource` 是 `"remote"`，EAS 完全拥有 `versionCode`：在构建配置文件上设置 `autoIncrement` 而不是编辑任何本地文件。Android 按此整数排序发布，并且这是商店用来决定什么是更新的。

- **也增加 `versionName`** — Expo 上的 `expo.version`，纯项目上的 `build.gradle` 中的 `versionName`。CLI 将两者作为发布元数据提交，并且 `versionName` 是用户在列表中看到的字符串。没有拒绝未更改的，因此仅移动 `versionCode` 的更新会无声地显示以前的版本。

- **使用原始密钥库签名。** 请参阅上面的约束；没有恢复。

## 审查

提交将进入人工审查，这需要几天时间——从文档中读取当前数字，而不是根据此处引用的数字来计划发布。常见的拒绝原因是未签名的 APK、不匹配列表的包名、缺少隐私政策以及超出发布者政策的内容。政策是关于最后一个的权威，并且它会变化——阅读它而不是猜测。

## Web 应用程序

一个包装的 Web 应用程序采取不同的路线：一个 Web-manifest、一个 Bubblewrap 构建，以及发布在 `/.well-known/assetlinks.json` 处的 Digital Asset Links。只有当应用程序确实是一个被包装的 PWA 时才去那里。一个 React Native 应用程序遵循上面的原生 APK 路径，并且 Bubblewrap 只会添加一个会破坏 Mobile Wallet Adapter 的层。

完整步骤：https://docs.solanamobile.com/recipes/general/publishing-a-web-app

## 参考资料

- [references/signing.md](references/signing.md) — 密钥库创建、Gradle 签名配置、EAS 构建配置，以及包括 ProGuard 脚枪在内的发布仅失败

## 相关技能

- `solana-mobile` — 框架、工具链检查、开发构建
- `solana-mobile-wallet` — 必须在发布构建中生存的钱包集成

## 链接

- dApp Store 文档：https://docs.solanamobile.com/dapp-store/intro
- 发布 CLI：https://docs.solanamobile.com/dapp-store/publishing-cli
- 构建和签名 APK：https://docs.solanamobile.com/dapp-store/build-and-sign-an-apk
- 发布者政策：https://docs.solanamobile.com/dapp-store/publisher-policy
- 发布门户：https://publish.solanamobile.com
- CLI 和工具源代码：https://github.com/solana-mobile/dapp-publishing
