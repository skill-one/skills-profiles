# EAS 更新

> **EAS 服务 - 可能产生费用。** EAS Update 可在免费套餐中使用；发布和交付使用更新、带宽和存储配额，付费套餐具有更高的限制。请参阅 https://expo.dev/pricing。

使用 EAS Update 将兼容的 JavaScript、样式和资源更改交付给已安装的应用程序，而无需提交新的原生二进制文件。原生代码更改仍需新的构建。

## 从支持的配置路径开始

更改任何内容之前，检查 `package.json`、Expo 应用程序配置、如果存在则检查 `eas.json`，以及是否跟踪 `ios/` 或 `android/`。在审查 CLI 的更改时使用您发现的内容：

- 保留现有的动态或平台特定的应用程序配置。
- 如果存在 `eas.json`，保留其配置文件和现有的频道分配。CLI 仅在构建配置文件尚未具有一个频道的情况下，为匹配配置文件名称的频道添加一个频道。
- 如果 `eas.json` 不存在，不要手动创建它。CLI 可能会指示用户单独运行 `eas build:configure`。
- 对于跟踪的原生项目，预期 CLI 将同步平台的原生更新配置。如果没有它们，预期在后续构建期间应用原生配置。

在安装包或解释版本特定行为之前检测 Expo SDK 版本。

如果未安装 `expo-updates`，请安装与 SDK 兼容的版本：

```bash
npx expo install expo-updates
```

从项目根目录进行配置：

```bash
npx eas-cli@latest update:configure
```

使用 `eas update:configure` 而不是手动发明 `updates.url`、`runtimeVersion`、原生元数据或构建配置文件频道。该命令理解 EAS 项目链接、持续原生生成以及具有已提交原生目录的项目。审查并解释其生成的差异。

如果命令无法继续进行，因为项目未链接或用户未授权所需的远程操作，请在任何独立的合法包安装后停止，并解释剩余内容。不要通过添加运行时版本策略、配置插件、更新 URL 或频道来部分重现 `update:configure`。

对于动态应用程序配置、非 EAS 构建，或无法自动完成的命令，请遵循当前设置文档，而不是猜测：https://docs.expo.dev/eas-update/getting-started.md。

## 保持模型清晰

- **构建：** 已安装的原生应用程序。它包含原生代码、嵌入式更新、平台、运行时版本，通常在构建时固定频道。
- **更新：** 为一个平台和运行时版本发布的 JavaScript 包、资源和元数据。
- **分支：** 更新的有序流。其最新的兼容更新是活动的。
- **频道：** 构建中嵌入的稳定部署目标。在服务器上，它指向一个分支。
- **运行时版本：** 更新和构建中原生代码之间的兼容性边界。

只有当平台和运行时版本匹配，并且构建的频道指向包含该更新的分支时，构建才会接收更新：

```text
已安装的构建（频道：生产，运行时：1.1.1，平台：ios）
  -> 生产频道
  -> 生产分支
  -> 运行时 1.1.1 和 ios 的最新更新
```

频道和分支通常具有相同的名称，但它们是不同的对象。`eas channel:edit` 更改频道的服务器端分支映射，适用于该频道上的每个构建。它不会更改单个安装的嵌入式频道。

使用此模型做出决策，但只需解释用户请求所需的必要概念，而不是每次都复述整个模型。

## 判断更新是否兼容

使用更新来更改已安装的原生运行时已经支持的 JavaScript、样式和捆绑资源。

当更改添加或修改原生代码或原生配置时，创建新的原生构建，包括大多数原生库添加和 SDK 升级。不要绕过运行时不匹配或暗示发布可以为现有构建添加原生功能。请参阅 https://docs.expo.dev/eas-update/runtime-versions.md。

不要作为附带修复更改项目的运行时版本策略。解释当前策略如何影响兼容性；将更改它视为一个单独的决策，因为它会更改哪些已安装的构建可以接收未来的更新。

## 故意发布

在依赖记住的标志之前，检查当前的 CLI 帮助：

```bash
npx eas-cli@latest update --help
```

对于基于频道的常见流程：

```bash
npx eas-cli@latest update \
  --channel <channel> \
  --message "<message>" \
  --environment <environment>
```

SDK 55 及更高版本需要 EAS 环境进行发布。有意选择环境，以便导出的代码接收预期的变量。

发布会更改远程状态，并可能影响已安装的应用程序。在运行它之前，确定确切的项目、频道、环境、平台、运行时版本和消息。仅在用户明确请求或批准的情况下发布到生产；如果授权或目标是模糊的，请在命令执行前停止并询问。不要仅从当前的 Git 分支推断生产目标。

优先使用预览或 staging 频道进行验证。在推广经过测试的更新时，使用文档中记录的部署流程，以便生产尽可能接收相同的工件：https://docs.expo.dev/eas-update/deployment.md。

## 根据构建类型进行测试

### 开发构建

使用开发构建的 Extensions UI、EAS 仪表板或 Expo Orbit 预览更新。正常的 `expo-dev-client` 开发构建不会像发布构建的自动启动更新流程那样运行。

### 预览、TestFlight 和生产构建

发布构建通常优先考虑启动速度。在默认启动行为下，应用程序可能会在下载新发布的更新时启动其当前嵌入式或缓存的更新。下载的更新将在后续重启时应用。

对于手动 QA，完全终止应用程序，而不是将其置于后台，重新打开它，允许更新时间下载，如果更改不可见，再次完全终止并重新打开它。将其描述为**最多两次冷启动**，而不是 TestFlight 特定的仪式：

1. 一个启动可以发现并下载更新。
2. 下一个启动可以运行下载的更新。

不要自动更改 `fallbackToCacheTimeout` 以避免第二个启动。在启动时等待会以启动延迟和可靠性为代价换取更快的更新激活。如果应用程序需要一个有意更新的用户体验，请考虑 `expo-updates` API 用于检查、获取和显示非阻塞重启操作。使用检测到的项目 SDK 版本的 `expo-updates` API 参考。

## 调试未更新的构建

按顺序检查：

1. 确认更新已发布到预期的 EAS 项目、频道或分支、平台和环境。
2. 比较已安装构建的平台和运行时版本与发布的更新。
3. 确认构建确实包含预期的更新 URL 和频道；app-config 更改仅在重新编译的构建中生效。
4. 检查频道到分支的映射和该分支上的活动更新。
5. 完全终止发布构建，并允许正常下载-应用生命周期。
6. 使用当前的调试指南进行原生日志、导出问题和配置检查：https://docs.expo.dev/eas-update/debug.md。

永远不要绕过兼容性或反死机保护，仅仅为了让更新看起来像已更新。

## 高级和相邻工作流

- **频道浏览：** 单个发布构建可以覆盖其 `expo-channel-name` 请求标头以请求另一个兼容的频道。这与更改服务器端频道到分支映射不同。请遵循 https://docs.expo.dev/eas-update/channel-surfing.md 并保留其访问控制、持久性、恢复和兼容性限制。
- **更新健康：** 发布后加载 `eas-update-insights` 以进行采用、启动失败、崩溃率、有效负载大小和发布监控。
- **商店发布：** 当原生更改需要新的 TestFlight、App Store 或 Play Store 构建时，加载 `eas-app-stores`。

## 官方参考

- 设置：https://docs.expo.dev/eas-update/getting-started.md
- 概念和匹配：https://docs.expo.dev/eas-update/how-it-works.md
- 部署：https://docs.expo.dev/eas-update/deployment.md
- 调试：https://docs.expo.dev/eas-update/debug.md
- 当前 EAS CLI 参考：https://docs.expo.dev/eas/cli.md

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-update" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含尽可能多的相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
