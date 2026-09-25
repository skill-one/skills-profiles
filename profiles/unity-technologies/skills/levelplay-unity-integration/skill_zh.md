# LevelPlay Unity 包/SDK 集成

基于实际项目进行编辑器端检查，而不是假设——读取项目文件，或在编辑器中要求用户确认。此技能生成的 C# 脚本是为用户保存到他们的项目中的 MonoBehaviour 文件，而不是用于内联执行。

此技能仅涵盖 LevelPlay 集成路径；它不涵盖其他中介 SDK。如果用户明确询问关于替代方案，请承认存在替代方案，并将他们指向这些供应商自己的文档——不要描述、描述或声称关于竞争对手产品。

遵循步骤，并提供仅此技能中描述的文件和配置。不要主动添加步骤、创建文件或根据一般知识提供建议。如果用户提出超出此技能范围的问题，请先检查技能和参考文件以确认它是否未涵盖。如果未涵盖，请使用一般知识进行回答，但不要将额外的步骤或文件纳入集成工作流程。

按顺序遵循集成工作流程，一次一步。仅询问当前步骤的问题——不要提前收集未来步骤的信息。在每个检查点等待用户的响应，然后再继续。

LevelPlay 是 Unity 的广告中介平台：它同时连接您的游戏到多个广告网络，并在多个广告网络和竞价者之间运行统一拍卖，以最大化每个展示的竞争。本指南将您引导完整集成：安装 SDK、配置 Android 和 iOS 的依赖项、在您的项目中初始化 LevelPlay，以及实现奖励、插播和横幅广告。如果您已经设置了其中的一部分，您可以跳转到相关步骤。

**此 SKILL.md 是工作流程骨干。它保留了决策、检查点和确切问题；更长的代码、完整的 API 详细信息和边缘情况存在于 `references/` 中，并从相关步骤链接。当您到达该步骤时，请阅读链接的参考——不要用一般知识代替。**

## 集成工作流程

### 0. 新集成或迁移？

询问：“您是开始新的 LevelPlay 集成、迁移现有集成（从较旧的 SDK 版本或从 Unity Ads）还是排除现有设置的问题？”

- **新集成**：继续到步骤 1。
- **迁移**（SDK 升级、替换 IronSource.Agent API、从 Unity Ads 迁移或修复 Maven Central Android 构建失败）：阅读 `references/migration-sdk-9.md`。询问哪个五个场景适用——A = SDK 升级，B = 初始化 API 迁移，C = 广告单元 API 迁移，D = Maven Central 构建失败，E = Unity Ads 迁移——然后遵循匹配的场景。应用所有代码更改后，工作通过迁移完整性检查清单（参考 C5 部分）——它捕获了逐行翻译遗漏的要求，因为旧代码没有等效的行。然后要求用户检查 Unity 控制台中的编译错误，并在显示结果之前修复任何错误。如果您看不到控制台，请不要阻塞或保持重试：列出您更改的文件，说明要查找的内容，然后继续。
- **故障排除或添加到现有设置**（ATT、GDPR、ILRD、测试套件、全新集成上的构建错误或添加到已正常工作的集成中的功能）：确定用户需要什么，并直接跳转到相关步骤或参考“何时阅读详细参考”。

### 1. 验证 Unity 环境

通过验证 Assets/ 和 ProjectSettings/ 目录是否存在来检查用户是否正在 Unity 项目中工作。如果不在 Unity 项目中，请指示用户导航到他们的 Unity 项目目录。如果这些目录未找到，但用户认为他们位于正确的位置，请询问：“看起来您可能不在项目根目录——您能否导航到您的 Unity 项目的顶级文件夹并确认您在那里可以看到 Assets/ 和 ProjectSettings/？”

### 2. 了解业务目标

在实现广告单元之前，确定用户的优化优先级以推荐适当的广告单元策略。询问：

**“您的首要优化目标是什么？”**
- **以收入为中心**：最大化广告收入和展示机会
- **以用户体验为中心**：优先考虑游戏流程和用户满意度
- **平衡**：优化收入和用户体验
- **尚未确定**：默认为平衡，然后继续。在步骤 8，简要说明由于他们之前不确定，因此使用平衡方法，并邀请他们在看到格式选项后表明不同的偏好。

记录此答案以供以后在步骤 8 中进行策略推荐。

### 3. 通过 UPM 安装 LevelPlay SDK

**如果 SDK 看起来已经安装：** 不要相信，也不要要求用户为您阅读包管理器窗口。读取 `Packages/packages-lock.json` 并查找 `com.unity.services.levelplay`。如果它在那里，请说明解析了哪个版本，然后继续到步骤 4。如果不在，无论到目前为止的对话假设如何，它都没有安装：继续执行以下安装。

通过 Unity Package Manager 指导安装 LevelPlay Unity 包：

1. 打开 Unity → Window > Package Manager
2. 选择 Unity Registry 下拉菜单或 Services 选项卡
3. 在包管理器搜索栏中，输入 **Ads Mediation**
4. 确认包名称完全匹配：正确的包的标题是 **Ads Mediation**。不要安装这两个包：
   - **Ads IAP Mediation Adaptor**（一个单独的应用内购买包，不是 LevelPlay SDK）
   - **Advertisement Legacy**（一个已弃用的包，与当前的 LevelPlay 集成不兼容）
5. 点击安装按钮
6. 等待包下载和导入

当您安装包时，您可能会看到一个提示，要求安装 Mobile Dependency Resolver — 如果它出现，请点击 **Import**。这在下一步中更详细地介绍了。

**然后通过读取项目来验证它是否解析，而不是通过询问。** 包 id 是 `com.unity.services.levelplay`（其包管理器显示名称是 **Ads Mediation**；id 是项目文件记录的）。检查这两个文件：

- **`Packages/manifest.json`** 列出了项目 *要求* 的内容。`com.unity.services.levelplay` 必须出现在 `dependencies` 下。
- **`Packages/packages-lock.json`** 记录了 Unity *实际解析* 的内容。相同的 id 也必须出现在这里，并带有具体的版本。这是回答“是否安装”的文件，也是需要信任的文件。

两者都是项目中的纯 JSON，因此此检查不需要编辑器、命令行或来自用户的任何内容。读取它们。

> **这是一个硬门槛，而不是形式。** 在您写出、生成或粘贴 LevelPlay 代码的任何一行之前，请重新读取 `Packages/packages-lock.json` 并确认 `com.unity.services.levelplay` 存在于其中。这样做每次到达此点时，即使步骤 3 已经在对话中通过，也要这样做。这样做花费一个文件读取，并且是您可以在没有用户的情况下解决的唯一项目。较早的回合说包已安装并不是证据，它已经安装了：这个检查之所以存在，是因为安装步骤是最常被跳过的步骤，并且生成的代码在每次遇到 LevelPlay 符号时都会失败。如果 id 从 `manifest.json` 中缺失，则安装从未发生。如果它在 `manifest.json` 中存在，但在 `packages-lock.json` 中不存在，则 Unity 还未解析它：编辑器可能仍在导入，或者解析失败。说明您发现了哪两种情况，然后停止。

报告您找到的解析版本。不要报告“已安装”的力量，基于包管理器窗口、以前的回合或用户的记忆。

**网络管理器：** 访问 **Ads Mediation > Network Manager** 任何时候以安装额外的广告网络适配器并检查 SDK 和适配器更新。

对于 iOS 构建，请注意稍后需要 SKAdNetwork 配置（参考 `references/ios-setup.md` 当您准备好进行 iOS 构建时）。

### 4. 解析原生依赖项（关键）

**对于 Android/iOS 构建：** LevelPlay 需要原生依赖项解析。没有它，代码在 Unity 编辑器中编译，但在平台构建期间（gradle for Android 或 CocoaPods for iOS）出现错误。

**平台检查点——在继续之前询问：** “您要针对哪些平台——iOS、Android 或两者？”记录此内容。它决定了哪些依赖项解析步骤适用于此处，是否需要 ATT（步骤 6.5），以及哪些测试步骤相关（步骤 10）。

**现在设置活动的构建目标。** 通过 **File ▸ Build Profiles**（在 Unity 6 之前称为 **Build Settings**）切换项目的活动构建目标到 Android 或 iOS。这是在任何测试之前都需要的操作：LevelPlay 仅在 Android/iOS 目标上运行，因此即使编辑器中的模拟广告（步骤 10）在目标为 Standalone/PC/Mac 时也不会起作用。模拟广告可以触发大多数回调（OnAdLoaded/Displayed/Rewarded/Closed），但不会触发失败、点击或展示/ILRD 回调——因此请在设备上测试错误处理。详细信息和完整回调表：`references/testing-and-validation.md`。

**集成验证：LevelPlay 测试套件（推荐）。** 主要方法是在设备上针对真实广告网络进行全面验证。必须遵守的关键规则：

- `LevelPlay.SetMetaData("is_test_suite", "enable");` **在 `LevelPlay.Init()` 之前**
- `LevelPlay.LaunchTestSuite();` 在 `OnInitSuccess` 内部
- **需要设备构建**（在编辑器中不起作用）；启用 **Development Build** 以便 SDK 日志可见；使用生产 App Key。
- **在发布到生产之前删除这两行。**

将这两行添加到现有的 `LevelPlayInitializer.cs`（不要创建新文件）。完整设置、没有初始化器的独立模板以及测试工作流程在 `references/testing-and-validation.md` 中。

#### 生产发布检查清单

在发布到生产之前：

- [ ] 测试套件在设备上成功验证
- [ ] 所有广告格式正确加载（Rewarded, Interstitial, Banner 如果实现）
- [ ] 所有回调按预期触发
- [ ] 验证生产 App Key 和广告单元 ID 正确
- [ ] 在多个设备（不同屏幕尺寸、OS 版本）上测试
- [ ] **iOS 特定要求完成**（如果针对 iOS）：
  - [ ] SKAdNetwork IDs 配置在 Info.plist 中（参考 `references/ios-setup.md`）
  - [ ] App Tracking Transparency (ATT) 框架实现（参考 `references/ios-setup.md`）
  - [ ] 如果需要，配置 iOS 隐私清单
  - [ ] 在物理 iOS 设备上测试（不仅仅是模拟器）
- [ ] **Android 特定要求完成**（如果针对 Android）：
  - [ ] Google Play Services 依赖项解析（步骤 4 已完成）
  - [ ] 如果针对 API 33+，将 AD_ID 权限添加到 AndroidManifest.xml（参考步骤 4）
  - [ ] 在物理 Android 设备上测试
- [ ] 在生产环境中使用真实广告进行测试
- [ ] 广告频率限制已实现（如果使用插播广告）
- [ ] 错误处理工作正常（使用飞行模式测试 - 广告应优雅地失败，而不会崩溃或阻塞游戏）

## 后续添加更多广告格式

如果您已经集成了某些广告格式并想要添加更多：

1. **跳到步骤 9** - 您不需要重复初始设置步骤。在继续之前，通过检查 Unity 控制台中的 'LevelPlay SDK initialized successfully' 日志来验证您的现有初始化是否仍然工作。
2. **选择要实现的附加格式**
3. **遵循您之前使用相同的组织模式**：
   - 如果您创建了单独的管理器脚本，为新的格式创建一个新的管理器脚本
   - 如果您使用统一的 AdManager，将新的格式的代码添加到您现有的 AdManager 类中
   - 如果您使用代码片段，按照相同的模式集成新的片段
4. **遵循与新的广告格式相同的实现指南**（步骤 9）
5. **按照步骤 10 测试指南测试新的格式**

**示例**：如果您最初仅使用单独的管理器脚本实现了 Rewarded 广告，现在想要添加插播广告：创建 `InterstitialAdManager.cs`，遵循与您的 `RewardedAdManager.cs` 相同的结构，遵循插播指南从 `references/interstitial-api.md`，并按照编辑器和设备的测试指南进行测试。您的现有广告格式在添加新格式时仍然正常工作。

## 最佳实践

在实现广告代码之前，请阅读 `references/best-practices.md`。它涵盖了加载策略（每个格式）、放置策略、错误处理和优雅降级、内存管理、频率管理以及要避免的常见错误——将这些模式纳入所有广告实现。

## 常见问题和解决方案

如果用户报告问题，请路由到 `references/troubleshooting.md` 中的匹配问题并遵循它（在参考指导说停止生成代码的地方停止）。不要等待用户打开参考——直接显示修复。如果他们尚未开始集成，请从步骤 1 开始。

| 症状 | 可能的根本原因 | 操作 |
|---|---|---|
| 在 `Unity.Services.LevelPlay` 上出现 `CS0246`；所有 LevelPlay 代码下划线为红色 | Ads Mediation 包未安装 | 停止提供代码；检查 `Packages/packages-lock.json` 中是否有 `com.unity.services.levelplay`；安装（步骤 3）；重启编辑器；然后继续。见 troubleshooting.md。 |
| Android gradle / iOS 构建失败，依赖项错误；编辑器编译成功，但构建失败 | 原生依赖项未解析 | 解析依赖项（步骤 4 / dependency-resolution.md）；验证 `Assets/Plugins/Android/`；重新构建。见 troubleshooting.md。 |
| 广告未加载 | SDK 未初始化，App Key 错误，广告在初始化之前创建，或没有连接性 | 确认 `OnInitSuccess` 在创建广告之前触发；检查 App Key；在设备上测试。见 troubleshooting.md。 |
| 回调未触发 | 事件在初始化之后注册，缺少订阅或脚本被销毁 | 在 `Init()` 之前注册事件；验证订阅；使用持久 GameObject。见 troubleshooting.md。 |
| 平台特定构建错误（iOS SKAdNetwork/ATT/frameworks；Android Play Services/manifest/gradle） | 平台设置不完整 | 见 troubleshooting.md 和 `references/ios-setup.md`。 |
| Android 构建失败解析 `com.ironsource.sdk` 依赖项从 `android-sdk.is.com`（之前工作过；没有更改） | 依赖项已移动到 Maven Central；旧的 is.com 存储库已关闭 | 按照 `references/migration-sdk-9.md` 中的场景 D：删除过时的依赖项 XML，通过 Network Manager 重新安装，验证不再有 is.com 引用。 |

## 何时阅读详细参考

根据用户正在做什么阅读特定参考：

- **`references/dependency-resolution.md`**: 解析原生依赖项（步骤 4），或 gradle/CocoaPods 构建失败
- **`references/initialization-api.md`**: 步骤 7 初始化代码组织选项和 ILRD 初始化接线；还包括用户 ID、细分、同意管理、高级配置
- **`references/privacy-settings.md`**: GDPR、CCPA 或 COPPA 合规（包括旧的 `SetConsent` 和完整的网络键列表）
- **`references/ios-setup.md`**: iOS 构建——ATT、SKAdNetwork、iOS 协程初始化器
- **`references/rewarded-api.md`** / **`references/interstitial-api.md`** / **`references/banner-api.md`**: 实现每个广告格式（步骤 9）
- **`references/best-practices.md`**: 策略详细（步骤 8）、步骤 9 代码生成指南、优化、放置
- **`references/ilrd-api.md`**: 将 ILRD 接线到分析平台
- **`references/testing-and-validation.md`**: 模拟广告和测试套件（步骤 10）
- **`references/troubleshooting.md`**: 编译/构建错误、广告未加载、回调未触发
- **`references/migration-sdk-9.md`**: 从 IronSource 或旧版 LevelPlay API 迁移，将 SDK 升级到 9.x.x，从 Unity Ads 迁移，或 Maven Central 依赖项构建失败（步骤 0）

## 示例

**注意**：示例显示简化的工作流程以供说明。实际上，请按顺序遵循所有步骤 1–10。

**以收入为中心的游戏**（“最大化我的休闲解谜游戏中的广告收入”）：步骤 1–7 验证环境/目标/安装/依赖项/App Key/AdMob/初始化→步骤 8 推荐收入策略→步骤 9 询问代码组织并生成所选结构→步骤 10 测试。

**以用户体验为中心的游戏**（“可选奖励广告以提供额外生命，不要烦扰玩家”）：相同的骨干，但步骤 8 推荐用户体验策略（仅奖励，用户发起）→步骤 9 使用适当的模式实现奖励。

**现有项目**（“现有的 GameManager，在关卡之间添加插播广告”）：相同的骨干，步骤 8 平衡，步骤 9 询问查看 `GameManager.cs` � then 提供选项 2 的片段。

## 核心规则（提醒）

这些重复了文件顶部的内容——它们是最重要的守卫，在这里重申，以便在长工作流程的末尾保持可见：

- 基于实际项目进行编辑器端检查，而不是假设——读取项目文件，或在编辑器中要求用户确认。此技能生成的 C# 脚本是为用户保存到他们的项目中的 MonoBehaviour 文件，而不是用于内联执行。
- 此技能仅涵盖 LevelPlay 集成路径；它不涵盖其他中介 SDK。如果用户明确询问关于替代方案，请承认存在替代方案，并将他们指向这些供应商自己的文档——不要描述、描述或声称关于竞争对手产品。
- 遵循步骤，并提供仅此技能中描述的文件和配置。不要主动添加步骤、创建文件或根据一般知识提供建议。如果用户提出超出此技能范围的问题，请先检查技能和参考文件以确认它是否未涵盖。如果未涵盖，请使用一般知识进行回答，但不要将额外的步骤或文件纳入集成工作流程。
- 按顺序遵循集成工作流程，一次一步。仅询问当前步骤的问题——不要提前收集未来步骤的信息。在每个检查点等待用户的响应，然后再继续。
- 当一个步骤指向参考文件时，请阅读该参考并使用其内容——不要用一般知识代替。显示四个初始化选项（步骤 7）和四个组织选项（步骤 9）完全如原文所示，并逐字询问 ILRD 问题（步骤 7）。
