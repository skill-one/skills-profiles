---
name: levelplay-unity-integration
description: 通过 Ads Mediation 包集成 LevelPlay 广告中介 SDK。当用户询问添加奖励视频广告、插屏广告或横幅广告、中介或广告隐私设置、Android 或 iOS 广告依赖构建失败，或从 Unity Ads 或 IronSource API 迁移时使用。
---

# LevelPlay Unity 包/SDK 集成

基于实际项目进行编辑器端检查，而不是基于假设——读取项目文件，或在编辑器中要求用户确认。本技能生成的 C# 脚本是为用户保存到他们的项目中的 MonoBehaviour 文件，而不是用于内联执行。

本技能仅涵盖 LevelPlay 集成路径；它不涵盖其他中介 SDK。如果用户明确询问替代方案，请承认存在替代方案，并指向这些供应商自己的文档——不要描述、表征或声称竞争对手产品。

遵循步骤，仅提供本技能中描述的文件和配置。不要主动添加步骤、创建文件或根据一般知识提供建议。如果用户提出超出本技能范围的问题，请先检查技能和参考文件以确认是否涵盖。如果没有涵盖，请使用一般知识进行回答，但不要将附加步骤或文件纳入集成工作流。

按顺序遵循集成工作流，一次一步。仅询问当前步骤的问题——不要提前收集未来步骤的信息。在每个检查点等待用户的响应后再继续。

LevelPlay 是 Unity 的广告中介平台：它同时连接您的游戏到多个广告网络，并在多个广告网络和竞价者之间运行统一拍卖，以最大化每个展示的竞争。本指南将引导您完成完整集成：安装 SDK、配置 Android 和 iOS 的依赖项、在您的项目中初始化 LevelPlay，以及实现奖励、插播和横幅广告。如果您已经设置了部分内容，可以跳转到相关步骤。

**此 SKILL.md 是工作流骨干。它保留决策、检查点和确切问题；更长的代码、完整的 API 详细信息和边缘情况保存在 `references/` 中，并从相关步骤链接。当您到达该步骤时，请阅读链接的参考——不要用一般知识代替。**

## 集成工作流

### 0. 新集成或迁移？

询问：“您是开始新的 LevelPlay 集成、迁移现有集成（从较旧的 SDK 版本或从 Unity Ads）还是排错现有设置？”

- **新集成**：继续到步骤 1。
- **迁移**（SDK 升级、替换 IronSource.Agent API、从 Unity Ads 迁移或修复 Maven Central Android 构建失败）：阅读 `references/migration-sdk-9.md`。询问哪个五个场景适用——A = SDK 升级，B = 初始化 API 迁移，C = 广告单元 API 迁移，D = Maven Central 构建失败，E = Unity Ads 迁移——然后遵循匹配的场景。应用所有代码更改后，通读迁移完整检查清单（参考 C5 部分）——它捕获了逐行翻译遗漏的要求，因为遗留代码没有等效行。然后要求用户检查 Unity 控制台中的编译错误，并修复出现的任何错误后再呈现结果。如果您看不到控制台，不要阻塞或不断重试：列出您更改的文件，说明要查找的内容，然后继续。
- **排错或添加到现有设置**（ATT、GDPR、ILRD、测试套件、全新集成上的构建错误或向已工作的集成添加功能）：确定用户需要什么，并直接跳转到相关步骤或从“何时阅读详细参考”中引用。

### 1. 验证 Unity 环境

通过验证 Assets/ 和 ProjectSettings/ 目录是否存在来检查用户是否在 Unity 项目中工作。如果不在 Unity 项目中，请指示用户导航到他们的 Unity 项目目录。如果这些目录未找到但用户认为他们位于正确的位置，请询问：“看起来您可能不在项目根目录下——您可以导航到您的 Unity 项目的顶层文件夹并确认在那里可以看到 Assets/ 和 ProjectSettings/ 吗？”

### 2. 了解业务目标

在实现广告单元之前，确定用户的优化优先级以推荐适当的广告单元策略。询问：

**“您的首要优化目标是什么？”**
- **收入导向**：最大化广告收入和展示机会
- **用户体验导向**：优先考虑游戏流程和用户满意度  
- **平衡**：优化收入和用户体验
- **尚未确定**：默认为平衡并继续。在步骤 8 中，简要说明由于他们不确定而使用平衡，并邀请他们在看到格式选项后现在指示不同的偏好。

记录此答案，以便在步骤 8 中进行策略推荐。

### 3. 通过 UPM 安装 LevelPlay SDK

**如果 SDK 看起来已经安装**：不要轻信，也不要要求用户为您阅读包管理器窗口。读取 `Packages/packages-lock.json` 并查找 `com.unity.services.levelplay`。如果存在，说明解析的版本并继续到步骤 4。如果不存在，则无论之前的对话假设如何，它都没有安装：继续执行以下安装步骤。

指导用户使用 Unity Package Manager 安装 LevelPlay Unity 包：

1. 打开 Unity → Window > Package Manager
2. 选择 Unity Registry 下拉菜单或 Services 选项卡
3. 在包管理器搜索栏中，输入 **Ads Mediation**
4. 确认包名称完全匹配：正确的包标题为 **Ads Mediation**。不要安装以下任一包：
   - **Ads IAP Mediation Adaptor**（一个单独的应用内购买包，不是 LevelPlay SDK）
   - **Advertisement Legacy**（一个已弃用的包，与当前的 LevelPlay 集成不兼容）
5. 点击安装按钮
6. 等待包下载和导入

安装包时，您可能会看到提示安装 Mobile Dependency Resolver 的提示——如果出现，请点击 **Import**。更多详细信息将在下一步中介绍。

**然后通过读取项目来验证它是否解析，而不是通过询问。** 包 ID 是 `com.unity.services.levelplay`（其包管理器显示名称是 **Ads Mediation**；ID 是项目文件记录的）。检查两个文件：

- **`Packages/manifest.json`** 列出项目 *请求* 的内容。`com.unity.services.levelplay` 必须出现在 `dependencies` 下。
- **`Packages/packages-lock.json`** 记录 Unity 实际 *解析* 的内容。相同的 ID 也必须出现在这里，并带有具体版本。这是回答“是否安装”的文件，也是需要信任的文件。

这两个都是项目中的纯 JSON，因此此检查无需编辑器、无需 CLI，也无需用户提供任何内容。读取它们。

> **这是一个硬性门槛，而不是形式问题。** 在 `packages-lock.json` 中出现 `com.unity.services.levelplay` 之前，不要编写、生成或粘贴 LevelPlay 代码的任何一行。跳过前进会产生看起来正确的代码，无法编译，并且在每个 LevelPlay 符号上都会失败 `CS0246`。如果 ID 从 `manifest.json` 中缺失，则安装从未发生。如果它在 `manifest.json` 中存在但在 `packages-lock.json` 中不存在，则 Unity 尚未解析它：编辑器可能仍在导入，或者解析失败。说明您发现了哪两种情况，然后停止。
>
> **如果您自己将 ID 添加到 `manifest.json` 中，并且自那以后没有运行编辑器，锁定文件可能尚未显示它。这是预期的，而不是失败。** 从不自己将条目写入 `packages-lock.json`：该文件是 Unity 的解析输出，手动编辑它是迁移指南禁止的，并且您写入的条目是一个虚假的“已解析”信号，而不是通过的门。要求用户打开 Unity 编辑器以运行解析，然后重新读取文件。如果根本没有编辑器可用，请说明并停止。

报告您找到的解析版本。不要基于包管理器窗口、之前的对话或用户的记忆报告“已安装”。

**网络管理器**：随时访问 **Ads Mediation > Network Manager** 安装额外的广告网络适配器并检查 SDK 和适配器更新。

对于 iOS 构建，请注意稍后需要 SKAdNetwork 配置（准备好 iOS 构建时参考 `references/ios-setup.md`）。

### 4. 解决原生依赖项（关键）

**对 Android/iOS 构建关键**：LevelPlay 需要原生依赖项解析。没有它，代码在 Unity 编辑器中编译，但在平台构建期间（Android 的 gradle 或 iOS 的 CocoaPods）会出错。

**平台检查点——在继续之前询问**：“您要针对哪些平台——iOS、Android 或两者？”记录此内容。它决定了此处适用的依赖项解析步骤，是否需要 ATT（步骤 6.5），以及哪些测试步骤相关（步骤 10）。

**现在设置活动的构建目标。** 通过 **File ▸ Build Profiles**（在 Unity 6 之前称为 **Build Settings**）→ **Switch Platform** 切换项目的活动构建目标为 Android 或 iOS。这是进行任何测试前必需的：LevelPlay 仅在 Android/iOS 目标上运行，因此即使是在编辑器中的模拟广告（步骤 10）在目标为 Standalone/PC/Mac 时也无效。

**解决目标平台的依赖项。** LevelPlay 需要原生 Android/iOS 库，而 Unity 的包管理器无法处理这些库；依赖项管理器（MDR、UEDM 或 EDM4U）桥接了这一差距。完整程序——检查现有依赖项管理器、Android 与 iOS 的解析、如果用户没有则安装一个、验证以及较旧版本的 Custom Main Gradle Template——在 **`references/dependency-resolution.md`** 中。现在引导用户完成它，并且**如果同时针对 Android 和 iOS，则在继续之前完成两个平台的解析。**

询问：“您是否已针对目标平台无错误地运行了依赖项解析？”

**Android API 33+（Android 13+）**：在 AndroidManifest.xml 中声明 AD_ID 权限：

```xml
<uses-permission android:name="com.google.android.gms.permission.AD_ID"/>
```

没有它，Android 13+ 设备上的广告 ID 访问会失败。详细信息在 `references/dependency-resolution.md`。

**如果依赖项解析失败**，请参考 `references/troubleshooting.md` 获取 gradle 和 CocoaPods 错误指导。

### 5. 获取应用密钥和广告单元 ID

在初始化 LevelPlay 之前，从 LevelPlay 仪表板收集凭证。

**仪表板**：https://platform.ironsrc.com/

**新用户？** 首先设置您的应用和广告单元：
- [添加您的应用](https://docs.unity.com/en-us/grow/levelplay/platform/get-started/add-app)
- [创建广告单元](https://docs.unity.com/en-us/grow/levelplay/platform/get-started/ad-units)

**应用密钥**：在仪表板中，转到左侧导航栏的 **Apps** → 找到您的应用 → 复制应用标题下显示的字母数字字符串。

**广告单元 ID**：转到左侧导航栏的 **Ad units** → 选择您的应用 → 复制您计划实现的每个格式的 ID（奖励、插播、横幅）。

**注意**：您现在需要应用密钥以进行初始化（步骤 7）。广告单元 ID 仅在步骤 9 中需要——如果您尚未决定要实现哪些广告格式，请现在复制您的应用密钥，然后在步骤 8 后返回这里。

保持两者都易于访问——您将在下一步中需要它们。

### 6. 配置 AdMob 密钥（如果使用 AdMob 网络）

**何时使用**：仅当在 LevelPlay 中使用 AdMob 作为中介网络适配器时。

如果使用 AdMob，请在 Unity 编辑器中配置平台特定的应用密钥：

**访问**：Ads Mediation > Developer Settings > LevelPlay Mediation Settings

**配置**：
- **Android App Key**：AdMob Android 应用密钥
- **iOS App Key**：AdMob iOS 应用密钥

此配置是 AdMob 作为 LevelPlay 中介网络正常工作所必需的。

**排错**：如果您在 Unity 编辑器中看不到“Ads Mediation”菜单，请验证 Ads Mediation 包是否已安装（步骤 3）并重新启动 Unity 编辑器。

### 6.5. 隐私和法规设置（如果需要）

> **注意**：此技能提供技术集成指南，包括 LevelPlay 的隐私 API。它不是法律建议，并且它不决定哪些法律适用于您的应用——这取决于您的用户、您的数据实践和您的分发。咨询您自己的法律顾问，并参考 [Unity 的法规高级设置](https://docs.unity.com/en-us/grow/levelplay/sdk/unity/regulation-advanced-settings) 以获取权威的 LevelPlay 文档。

询问用户：“您是否需要配置 GDPR、CCPA/CPRA（或某些州隐私消费者法案）或针对儿童导向应用的隐私设置？”

**如果回答任何“是”：**

隐私设置必须在 SDK 初始化 **之前** 配置。查看 `references/privacy-settings.md` 获取完整的实现指南（UI、同意管理、组合法规以及完整网络密钥列表）。

**GDPR——正确的 API 取决于用户的 SDK 版本**（在 **Ads Mediation > Network Manager** 中检查）：

**SDK 9.5.0+** — 全局同意布尔值：
```csharp
using Unity.Services.LevelPlay;

// true = 用户已授予权益，false = 用户未授予权益
LevelPlayPrivacySettings.SetGDPRConsent(true);
```

**SDK 9.4.x** — 每个网络同意字典（这是 9.4.x 上的当前 API，不是遗留的——它在 9.5.0+ 上才会变为 `[Obsolete]`；不要将其误标为已弃用）：
```csharp
using Unity.Services.LevelPlay;
using System.Collections.Generic;

// 为您安装的每个广告网络添加一个条目
LevelPlayPrivacySettings.SetGDPRConsents(new Dictionary<string, bool> {
    { "UnityAds", true },
    { "IronSource", true }
    // 查看 references/privacy-settings.md 获取完整网络密钥列表
});
```

如果这两个 API 都无法编译，您的 Unity 包/SDK 可能低于 9.4.0（遗留版）——建议通过 **Ads Mediation > Network Manager** 升级。如果用户无法升级，遗留的 `LevelPlay.SetConsent(bool)` API 在 `references/privacy-settings.md` 中有记录。

**CCPA（SDK 9.4.0+）**：
```csharp
LevelPlayPrivacySettings.SetCCPA(true); // 用户选择退出数据销售
```

**COPPA（SDK 9.4.0+）**：
```csharp
LevelPlayPrivacySettings.SetCOPPA(true); // 儿童导向应用
```

如果 CCPA 或 COPPA 无法编译，请通过 **Ads Mediation > Network Manager** 升级您的 Unity 包/SDK。在步骤 7 中的 `LevelPlay.Init()` 之前调用所有这些。

**对于 iOS 构建——无论上述隐私法规如何都需要**：在继续到步骤 7 之前，还必须实现 App Tracking Transparency (ATT)。Apple 要求在 iOS 14.5+ 上应用在您的应用跟踪用户或访问设备的广告标识符之前获得 ATT 授权。在调用 `LevelPlay.Init()` 之前请求 ATT 授权——这既是 Apple 平台要求，也是实现个性化广告所必需的（这也影响填充率）。查看 `references/ios-setup.md` 获取 ATT 实现代码。

**如果没有隐私法规且不针对 iOS**：跳过此步骤并继续到步骤 7。

### 7. 初始化 LevelPlay SDK

**安装检查点：**

**首先，重新读取 `Packages/packages-lock.json` 并确认 `com.unity.services.levelplay` 是否存在。**
每次到达这一点时，即使之前在对话中已经通过步骤 3，也要这样做。
它花费一个文件读取，并且是您唯一可以在不依赖用户的情况下确定的项。上一轮说包已安装并不是证据——这个检查存在是因为安装步骤是最常被跳过的，并且生成的代码在每个 LevelPlay 符号上都会失败 `CS0246`。如果 ID 缺失，请返回到步骤 3，不要编写初始化代码。

然后通过询问用户来确认剩余的先决条件，这些是文件无法回答的。
**如果用户确认他们不使用 AdMob，请省略步骤 6 的项目。** 如果步骤 4 已经在此对话中确认，请跳过该项目，并仅询问步骤 5 和步骤 6（如果 AdMob）。

请确认以下步骤是否正常工作：
- 第 4 步：您是否已针对目标平台（们）运行了依赖解析，且没有错误？
- 第 5 步：您是否已从 LevelPlay 仪表板复制了 App Key？
- 第 6 步（仅在使用 AdMob 时）：您是否已在 Unity 编辑器设置中配置了 AdMob 密钥？

在进行下一步之前，请验证这些步骤是否正常工作。

**如果包检查失败，或者他们回答“否”或不确定：**
- 包 ID 缺失在 `packages-lock.json` 中：代码将显示 `CS0246` 命名空间错误 → 直接跳转到第 3 步。这是您自己设置的；不要要求用户推翻它。
- 缺失第 4 步：代码可以编译，但 Android/iOS 构建将失败 → 直接跳转到第 4 步
- 缺失第 5 步：他们将没有初始化凭证 → 直接跳转到第 5 步
- 在他们确认所有步骤都完成后，才提供 C# 代码

**如果他们回答“是”：**
- **可选 — 分析：ILRD 线路。** 请逐字提问，不要总结或改述： “您是否使用分析或归因平台（Firebase、AppsFlyer、Adjust、Singular 或自定义后端）需要广告收入数据？如果是，初始化脚本将包含 Impression Level Revenue (ILRD) 的日志桩——3 行代码，无需设置分析平台。 (是 / 否 / 不确定 — 默认为是)” 记录答案。
- 继续进行初始化代码。

LevelPlay SDK 必须在加载或显示任何广告之前进行初始化。初始化应在应用程序生命周期早期进行。

**询问他们希望如何处理初始化。精确呈现以下四个选项，不要压缩或省略任何：**
1. 为 LevelPlay 初始化创建一个专用的脚本
2. 添加到他们已有的初始化/管理脚本中
3. 创建一个新的 LevelPlay 脚本，供您现有的管理器引用
4. 直接给我初始化代码——我会决定如何集成它

**每个选项的完整代码在 `references/initialization-api.md`（代码组织选项）。** 必须保持的行为：
- **选项 1（新脚本）：** 如果在第 6.5 步（iOS）中设置了 ATT，请使用 `references/ios-setup.md` 第 3 部分（`IEnumerator Start()` 协程变体）中的 `LevelPlayInitializer.cs`，而不是普通模板。
- **选项 4（直接代码）：** 提供完整的选项 1 初始化类作为独立片段——不要创建文件或添加 Inspector/GameObject 设置步骤——并附带说明：“保存为 `LevelPlayInitializer.cs`，将其附加到您第一个场景中的持久 GameObject 上，并在 Inspector 中设置 App Key 字段。”

**ILRD 线路（如果用户回答“是”或“不确定”）。** 正确的方法取决于 SDK 版本（在 **广告中介 > 网络管理器** 中检查）：
- **SDK 9.5.0+（当前）：** 不要向初始化器添加任何内容——ILRD 通过 `OnAdImpressionDataReady` 按每个广告实例交付，在步骤 9 中每个广告创建时线路连接。全局 `LevelPlay.OnImpressionDataReady` 事件在 9.5.0+ 中已**弃用**并会生成编译器警告——不要使用它。
- **SDK 9.4.x 及更早版本：** 在 `LevelPlay.Init()` 之前订阅全局 `LevelPlay.OnImpressionDataReady` 事件，添加一个日志桩，并在 `OnDestroy()` 中取消订阅。在 iOS 协程初始化器中，将订阅放在 `InitializeLevelPlay()` 内部，立即在 `LevelPlay.Init(appKey)` 之前。

每个选项的精确线路代码（包括 iOS 协程位置）在 `references/initialization-api.md`（版本感知 ILRD 初始化线路）。ILRD 回调不会在模拟广告中触发——需要设备构建来验证（见第 10 步）。高级选项（用户 ID、细分、同意管理），请参阅 `references/initialization-api.md`。

### 8. 推荐广告单元策略

根据在第 2 步中确定的优化目标，推荐一个广告单元策略。

**回想一下用户在第 2 步中的优化目标。** 如果对话很长或答案不明确，请确认：“您之前提到您的优化目标。为了确认，您主要关注收入、用户体验还是两者的平衡？”

**将答案映射到策略** 并给出简要建议（完整细节、基准和放置指南在 `references/best-practices.md` 下“按目标划分广告格式策略”中）：

- **收入导向** → **收入策略。** 奖励广告（主要变现，多个高价值时刻）→ 插播广告（次要；在过渡时；频率限制 3–5 分钟）→ 横幅广告（游戏过程中持续显示）。竞价底价是一个可选的收入杠杆，在第 9 步中配置。实现优先级：**奖励广告 → 插播广告 → 横幅广告**。
- **用户体验导向** → **用户体验策略。** 仅奖励广告，用户主动触发（明确选择），高价值奖励，**永远不要强制广告**。插播广告可选/谨慎地仅在会话边界处使用；横幅广告通常避免或仅在菜单中显示。实现优先级：**奖励广告**，或**奖励广告 → （可选）插播广告**。
- **平衡** → **平衡策略。** 奖励广告（2–3 个战略性位置）→ 插播广告（适度；自然断点；频率限制 5–7 分钟）→ 横幅广告（选择性；菜单/低注意力）。实现优先级：**奖励广告 → 插播广告 → 选择性横幅广告**。
- **“还不确定”**（来自第 2 步）→ 使用**平衡策略**，然后添加：“由于您之前不确定目标，我已采用平衡方法——如果您现在希望更偏向收入或用户体验，请告诉我。”
- 如果仍然不明确，请问：“您会优先考虑收入、用户体验还是两者的平衡？”

下一步将询问从此优先级列表中要实现哪些广告格式。如果用户希望不同于推荐的顺序，请满足他们的偏好。

### 9. 实现广告单元

**首先阅读 `references/best-practices.md`**——其“代码生成指南（第 9 步）”部分包含广告生命周期的一般模式、每个组织的代码生成规则、始终包含的要求（MonoBehaviour、`DestroyAd()` 在 `OnDestroy()` 中、放置限制的显示路径检查（当使用放置时）、事件取消订阅、空值检查、错误处理）以及竞价底价线路示例。将这些模式融入所有广告实现中。

**实现检查点：**

“在进行广告实现之前，请确认：
- 您是否在第 7 步中完成了 SDK 初始化？
- 您是否在 Unity 控制台中收到了 'LevelPlay SDK 初始化成功' 的日志消息？

在进行广告单元之前，请验证初始化是否正常工作。”

**如果他们回答“否”或不确定：** 直接跳转到第 7 步，并在初始化确认工作正常之前，不要提供广告实现代码。

**广告格式检查点——在生成任何代码之前提问：** “您想实现哪些广告格式？奖励广告、插播广告、横幅广告或组合？” 仅实现用户选择的格式。他们可以在稍后使用“添加更多广告格式”部分添加更多格式。

**首先，询问用户他们希望如何组织广告代码。在生成任何代码之前，他们必须回答：**

“您希望如何构建您的广告实现？”

1. **每个广告格式使用单独的管理脚本** - 创建单独的脚本，如 `RewardedAdManager.cs`、`InterstitialAdManager.cs`、`BannerAdManager.cs`（适用于较大项目，职责清晰分离）
2. **使用一个统一的 AdManager 脚本** - 创建一个单一的 `AdManager.cs` 脚本处理所有广告格式（更简单，所有内容在一个地方）
3. **直接给我代码片段** - 提供实现代码，不将其包装在特定文件中，以便您可以根据自己的喜好集成
4. **我已有广告管理代码** - 审查并帮助修复/更新现有实现

根据他们的回答，相应地调整您的回复（见 `references/best-practices.md` 中的代码生成指南）。

**如果用户已有广告代码（例如，现有的管理脚本），在生成任何代码之前请查看它**——以便您可以提供有针对性的修复，而不是从头开始编写新代码。这适用于他们选择的所有组织选项（选项 4 专门用于审查现有代码，但相同的“给我您的代码”适用于用户提到他们已有一些代码）。

**然后呈现可选的竞价底价功能（选项 4——审查现有代码时跳过）：**

仅针对用户在此会话中实现的格式呈现竞价底价范围。参考起始范围：奖励广告：$0.50–$2.00 | 插播广告：$0.20–$1.00 | 横幅广告：$0.05–$0.20。仅包含正在实现的格式的范围。

“**可选——高级：竞价底价**

大多数发布商最初跳过此功能，并在有实际仪表板数据后再添加。您可以安全地现在跳过并稍后返回。

如果您希望现在设置竞价底价：竞价底价设置每个广告单元的最低出价价格（美元）——它会提高您的平均 eCPM，但会降低填充率。起始范围：
[正在实现的格式的范围]

回复每个格式的值，或直接说'跳过'——您可以随时添加。”

记录每个格式的答案。将 `Config.Builder().SetBidFloor(...)` 线路到任何提供值的格式的广告构建中；标记为“跳过”的格式使用基本构造函数（见 `references/best-practices.md` 中的竞价底价示例）。

**如果他们选择选项 4（现有代码）：**
- 询问：“请分享您的现有广告管理代码以供审查”并等待。
- 分析实现：他们是否使用当前的 LevelPlay 广告单元 API（LevelPlayRewardedAd、LevelPlayInterstitialAd、LevelPlayBannerAd），是否使用**已弃用的 IronSource.Agent API**，是否正确注册/取消注册回调，以及是否缺少错误处理或内存泄漏。
- 提供具体指导：
  - 如果使用已弃用 API： “您正在使用旧的 IronSource.Agent API。以下是迁移到新 LevelPlay Ad Unit API 的方法：”（完整迁移细节在 `references/migration-sdk-9.md` — 初始化场景 B，每个广告格式场景 C 包括 C5 完整性检查清单）
  - 如果使用当前 API 但存在问题： “您的实现看起来很好，但我注意到 [具体问题]。以下是修复方法：”
  - 如果实现正确： “您的实现看起来很稳固。您想添加哪些其他广告格式？”
- 提供修复代码片段或建议重构。在审查后添加新格式，仅针对新格式呈现竞价底价提示，确认是否要匹配他们现有的组织模式或使用新模式，然后遵循与选项 1–3 相同的指南。

对于每个广告格式，遵循详细参考资料中的实现指南：

- **奖励广告**：见 `references/rewarded-api.md`
- **插播广告**：见 `references/interstitial-api.md`
- **横幅广告**：见 `references/banner-api.md`

**印象级收入跟踪（版本感知）**：见 `references/ilrd-api.md` 将印象数据转发到分析平台（Firebase、AppsFlyer、Adjust、Singular 或自定义后端）。
- **SDK 9.5.0+（当前）**：在创建每个广告对象后订阅其 `OnAdImpressionDataReady` 事件（并在 `OnDestroy()` 中取消订阅）。将此添加到您生成的每个广告管理器中——这是 9.5.0+ 中正确的 ILRD 路径。
- **SDK 9.4.x 及更早版本**：ILRD 使用单个全局 `LevelPlay.OnImpressionDataReady` 事件，在初始化脚本（第 7 步）中线路。如果用户在第 7 步中回答了“是”/“不确定”，它已经线路。如果他们说了“否”并想现在添加，请在现有的 `LevelPlay.Init()` 调用之前订阅 `LevelPlay.OnImpressionDataReady`。

### 10. 测试和验证

LevelPlay 提供了两种验证方法，用于开发的不同阶段。**完整细节——设置、回调行为表、测试套件初始化器模板和 iOS 协程位置——在 `references/testing-and-validation.md` 中。在用户测试时阅读它。**

**早期开发：Unity 编辑器中的模拟广告**。用于快速迭代和回调测试。在编辑器中按 Play 提供模拟广告自动——但**仅当活动构建目标是 Android 或 iOS**（独立/PC/Mac 返回无广告；这是最常见的“编辑器中无广告”原因——见第 4 步）。模拟广告适用于任何 App Key/广告单元 ID，但建议使用真实凭证，以免忘记。模拟广告触发大多数回调（OnAdLoaded/Displayed/Rewarded/Closed），但**不触发失败、点击或印象/ILRD 回调**——因此需要在设备上测试错误处理。详情和完整回调表：`references/testing-and-validation.md`。

**集成验证：LevelPlay 测试套件（推荐）**。在设备上针对真实广告网络进行综合验证的主要方法。必须保持的规则：
- `LevelPlay.SetMetaData("is_test_suite", "enable");` **在 `LevelPlay.Init()` 之前**
- `LevelPlay.LaunchTestSuite();` 在 `OnInitSuccess` 内部
- **需要设备构建**（在编辑器中不起作用）；启用**开发构建**以便 SDK 日志可见；使用生产 App Key。
- **在发布生产版本之前移除这两行。**
- iOS 协程初始化器：将 `SetMetaData` 作为 `InitializeLevelPlay()` 内部的第一行，在 `Init` 之前（不在 `Start()` 中）。

将两行添加到现有的 `LevelPlayInitializer.cs`（不要创建新文件）。完整设置、没有初始化器的独立模板以及测试工作流程在 `references/testing-and-validation.md` 中。

#### 生产发布检查清单

在发布到生产之前：

- [ ] 设备上测试套件验证成功
- [ ] 所有广告格式正确加载（奖励广告、插播广告、如果实现则横幅广告）
- [ ] 所有回调按预期触发
- [ ] App Key 和广告单元 ID 验证为生产版本正确
- [ ] 在多个设备上测试（不同屏幕尺寸、操作系统版本）
- [ ] **iOS 特定要求完成**（如果针对 iOS）：
  - [ ] SKAdNetwork ID 在 Info.plist 中配置（见 `references/ios-setup.md`）
  - [ ] App 追踪透明度（ATT）框架实现（见 `references/ios-setup.md`）
  - [ ] 如果需要，配置 iOS 隐私清单
  - [ ] 在物理 iOS 设备上测试（不只是模拟器）
- [ ] **Android 特定要求完成**（如果针对 Android）：
  - [ ] 解析 Google Play 服务依赖项（第 4 步完成）
  - [ ] 如果针对 API 33+，在 AndroidManifest.xml 中添加 AD_ID 权限（见第 4 步）
  - [ ] 在物理 Android 设备上测试
- [ ] 在生产环境中使用真实广告测试
- [ ] 实现广告频率限制（如果使用插播广告）
- [ ] 错误处理工作正常（使用飞行模式测试——广告应优雅失败，不会崩溃或阻塞游戏）

## 添加更多广告格式

如果您已集成一些广告格式并想添加更多：

1. **跳转到第 9 步**——您不需要重复初始设置步骤。在进行之前，通过检查 Unity 控制台是否有 'LevelPlay SDK 初始化成功' 的日志来验证您的现有初始化是否仍然工作。
2. **选择您想实现的附加格式**
3. **遵循您之前使用的相同组织模式**：
   - 如果您创建了单独的管理脚本，为新的格式创建一个新的管理脚本
   - 如果您使用统一的 AdManager，将新格式的代码添加到您现有的 AdManager 类中
   - 如果您使用代码片段，按照相同模式集成新的片段
4. **遵循新广告格式的相同实现指南**（来自第 9 步）
5. **按照第 10 步测试指南测试新格式**

**示例**：如果您最初仅使用单独的管理脚本实现了奖励广告，现在想添加插播广告：创建 `InterstitialAdManager.cs`，遵循与您的 `RewardedAdManager.cs` 相同的结构，遵循插播广告指南从 `references/interstitial-api.md`，并在编辑器和设备上测试。您的现有广告格式在您添加新格式时仍然有效。

## 最佳实践

在实现广告代码之前，请阅读 `references/best-practices.md`。它涵盖了加载策略（按格式）、放置策略、错误处理和优雅降级、内存管理、频率管理以及常见错误避免——将这些模式融入到所有广告实现中。

## 常见问题和解决方案

如果用户报告了问题，请将其路由到 `references/troubleshooting.md` 中的匹配问题，并遵循其指导（在指导说明停止生成代码的地方停止）。不要等待用户打开参考——直接展示修复方案。如果他们还没有开始集成，从步骤 1 开始。

| 症状 | 可能的根本原因 | 操作 |
|---|---|---|
| 在 `Unity.Services.LevelPlay` 上出现 `CS0246`；所有 LevelPlay 代码下划线为红色 | 未安装广告中介包 | 停止提供代码；检查 `Packages/packages-lock.json` 中的 `com.unity.services.levelplay`；安装（步骤 3）；重启编辑器；然后继续。参见 troubleshooting.md。 |
| 安卓 gradle / iOS 构建失败出现依赖错误；编辑器中编译成功但在构建时失败 | 未解析原生依赖 | 解析依赖（步骤 4 / dependency-resolution.md）；验证 `Assets/Plugins/Android/`；重新构建。参见 troubleshooting.md。 |
| 广告未加载 | SDK 未初始化、App Key 错误、初始化前创建广告或无网络连接 | 确认在创建广告之前触发 `OnInitSuccess`；检查 App Key；在设备上测试。参见 troubleshooting.md。 |
| 回调未触发 | 初始化后注册事件、缺少订阅或脚本被销毁 | 在 `Init()` 之前注册回调；验证订阅；使用一个持久的 GameObject。参见 troubleshooting.md。 |
| 平台特定的构建错误（iOS SKAdNetwork/ATT/框架；安卓 Play Services/清单/gradle） | 平台设置不完整 | 参见 troubleshooting.md 和 `references/ios-setup.md`。 |
| 安卓构建失败解析来自 `android-sdk.is.com` 的 `com.ironsource.sdk` 依赖（之前工作过；未更改任何内容） | 依赖已移至 Maven Central；旧的 is.com 仓库已关闭 | 按照 `references/migration-sdk-9.md` 中的场景 D 操作：删除过时的依赖 XML 文件，通过网络管理器重新安装，验证不再有 is.com 引用。 |

## 何时阅读详细参考

根据用户正在做什么，阅读特定的参考：

- **`references/dependency-resolution.md`**：解析原生依赖（步骤 4），或 gradle/CocoaPods 构建失败
- **`references/initialization-api.md`**：步骤 7 初始化代码组织选项和 ILRD 初始化接线；还包括用户 ID、细分、同意管理、高级配置
- **`references/privacy-settings.md`**：GDPR、CCPA 或 COPPA 合规（包括遗留的 `SetConsent` 和完整的网络密钥列表）
- **`references/ios-setup.md`**：iOS 构建——ATT、SKAdNetwork、iOS 协程初始化器
- **`references/rewarded-api.md`** / **`references/interstitial-api.md`** / **`references/banner-api.md`**：实现每种广告格式（步骤 9）
- **`references/best-practices.md`**：策略细节（步骤 8）、步骤 9 代码生成指南、优化、放置
- **`references/ilrd-api.md`**：将 ILRD 接线到分析平台
- **`references/testing-and-validation.md`**：模拟广告和测试套件（步骤 10）
- **`references/troubleshooting.md`**：编译/构建错误、广告未加载、回调未触发
- **`references/migration-sdk-9.md`**：从 IronSource 或旧版 LevelPlay API 迁移、将 SDK 升级到 9.x.x、从 Unity Ads 迁移或 Maven Central 依赖构建失败（步骤 0）

## 示例

**注意**：示例展示了简化的工作流以供说明。实际上，请按顺序遵循所有步骤 1–10。

**以收入为中心的游戏**（“在我的休闲解谜游戏中最大化广告收入”）：步骤 1–7 验证环境/目标/安装/依赖/App Key/AdMob/初始化 → 步骤 8 推荐收入策略 → 步骤 9 询问代码组织并生成所选结构 → 步骤 10 测试。

**以用户体验为中心的游戏**（“可选的奖励广告用于额外生命，不烦扰玩家”）：相同的骨架，但步骤 8 推荐用户体验策略（仅奖励、用户触发）和步骤 9 使用正确的模式实现奖励。

**现有项目**（“现有的 GameManager，在关卡之间添加插屏广告”）：相同的骨架，步骤 8 平衡，步骤 9 要求查看 `GameManager.cs` 然后提供 Option-2 片段。

## 核心规则（提醒）

这些重复了此文件顶部的规则——它们是最重要的指导方针，在此处重申，以便在长时间的工作流程结束时保持可见：

- 基于实际项目而不是假设进行编辑器端检查——阅读项目文件，或要求用户在编辑器中确认。在此技能中生成的 C# 脚本是用户保存到其项目的 MonoBehaviour 文件，而不是用于内联执行。
- 此技能仅涵盖 LevelPlay 集成路径；它不涵盖其他中介 SDK。如果用户明确询问关于替代方案，承认存在替代方案并将他们指向这些供应商自己的文档——不要描述、描述或声称竞争对手产品。
- 遵循步骤并提供本技能中描述的文件和配置。不要主动添加步骤、创建文件或根据一般知识提供建议。如果用户提出超出此技能范围的问题，请先检查技能和参考文件以确认是否未涵盖。如果不是，使用一般知识进行回应，但不要将额外的步骤或文件纳入集成工作流程。
- 按顺序遵循集成工作流程，一步一步地进行。仅询问当前步骤的问题——不要提前收集未来步骤的信息。在每个检查点等待用户的响应后再继续。
- 当一个步骤指向参考文件时，请阅读该参考并使用其内容——不要用一般知识替代。按原文呈现四个初始化选项（步骤 7）和四个组织选项（步骤 9），并逐字提问 ILRD 问题（步骤 7）。
