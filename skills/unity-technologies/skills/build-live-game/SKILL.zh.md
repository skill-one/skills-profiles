---
name: build-live-game
description: 使用 Unity Services 构建和运营实时游戏。当用户询问有关后端或实时运营功能（如玩家账户、云存档、排行榜、成就、进度和战斗通行证、经济系统、云代码或远程配置）时使用。
---

# 使用 Unity 游戏服务构建实时游戏

## UGS 包

| 包 | 最低版本 | 用途 |
|---|---|---|
| `com.unity.services.core` | 1.16.0 | 初始化、依赖关系图 |
| `com.unity.services.authentication` | 3.6.1 | 玩家登录和身份识别 |
| `com.unity.services.cloudcode` | 2.10.3 | 服务器端 C# 模块 |
| `com.unity.services.cloudsave` | 3.4.0 | 每个玩家和共享的键值存储 |
| `com.unity.remote-config` | 4.2.5 | 服务器端游戏配置 |
| `com.unity.services.deployment` | 1.7.2 | 从编辑器部署云资源 |
| `com.unity.services.tooling` | 1.4.1 | 访问控制和游戏覆盖 |
| `com.unity.services.apis` | 1.1.1 | 为所有 UGS 服务生成的 REST 客户端 |

- [初始化模式](#初始化模式)
- [包映射](#包映射)
- [架构 — 包如何组合](#架构--包如何组合)
- [核心服务 — 快速参考](#核心服务--快速参考)
- [资源商店构建模块](#资源商店构建模块)
- [现成功能蓝图](#现成功能蓝图)
- [常见架构模式](#常见架构模式)
- [验证](#验证)
- [部署清单](#部署清单)
- [详细参考](#详细参考)

## 初始化模式

每个 UGS 游戏都以相同的方式启动。`com.unity.services.core` 必须首先初始化，然后玩家登录：

```csharp
using Unity.Services.Core;
using Unity.Services.Authentication;

await UnityServices.InitializeAsync();
await AuthenticationService.Instance.SignInAnonymouslyAsync();
// 所有其他服务现在已准备就绪
```

`InitializeAsync()` 完成后，服务单例（例如 `CloudSaveService.Instance`、`CloudCodeService.Instance`）即可使用。

## 包映射

### 基础

| 包 | 用途 | 单例/入口点 |
|---|---|---|
| **核心** | 初始化、依赖关系图、组件注册 | `UnityServices.InitializeAsync()` |
| **身份验证** | 玩家登录（匿名、社交、Unity、用户名/密码）、身份识别 | `AuthenticationService.Instance` |
| **服务 API** | 为所有 UGS 服务生成的 REST 客户端；通过服务账户访问管理 API | 直接 API 类 |

### 玩家数据和配置

| 包 | 用途 | 单例/入口点 |
|---|---|---|
| **云保存** | 每个玩家的键值数据（默认、公开、受保护）和游戏范围的 Custom 数据 | `CloudSaveService.Instance.Data.Player` / `.Data.Custom` |
| **远程配置** | 服务器端游戏配置、功能标志、JSON 定义 | `RemoteConfigService.Instance` |
| **经济** | 虚拟货币、库存物品、购买、商店 | `EconomyService.Instance` |

### 服务器逻辑和安全

| 包 | 用途 | 单例/入口点 |
|---|---|---|
| **云代码** | 服务器端 C# 模块（用于受信任的写入和验证） | `CloudCodeService.Instance` → `CallModuleEndpointAsync` |
| **工具** | 编写和部署访问控制（`.ac`）和游戏覆盖（`.ugo`）文件 | 仅限编辑器（部署窗口） |
| **部署** | 从 Unity 编辑器部署云资源（`.rc`、`.ac`、`.ccmr`、`.lb` 等） | 仅限编辑器（服务 > 部署） |

### 社交和竞技

| 包 | 用途 | 单例/入口点 |
|---|---|---|
| **多人游戏** | 会话、匹配、大厅。构建模块：[多人会话、匹配会话、服务器会话](#资源商店构建模块) | `MultiplayerService.Instance` |
| **排行榜** | 分数提交、排名、等级、版本历史。构建模块：[排行榜](#资源商店构建模块) | `LeaderboardsService.Instance` |

### 远程监控

| 包 | 用途 | 单例/入口点 |
|---|---|---|
| **分析** | 自定义事件、标准事件、同意管理 | `AnalyticsService.Instance` |

## 架构 — 包如何组合

```
                    UnityServices.InitializeAsync()
                              │
                              ▼
                     AuthenticationService
                    (登录 → PlayerId)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Remote Config     Cloud Save      Economy
      (游戏配置,    (玩家状态,     (货币,
       定义,       进度,        库存,
       功能标志)    偏好设置)    购买)
              │               │               │
              └───────┬───────┘               │
                      ▼                       │
                 Cloud Code                   │
              (服务器端写入,           │
               验证,  ◄─────────┘
               反作弊逻辑)
                      │
              ┌───────┼───────┐
              ▼       ▼       ▼
         Cloud Save  Economy  Leaderboards
         (受保护写入) (服务器  (分数
          写入)    授予)  提交)
```

**关键原则：** 对于任何影响游戏完整性的数据（经验值、奖励、货币），请通过云代码模块路由写入。直接客户端写入仅适用于非敏感数据（偏好设置、显示设置）。

## 核心服务 — 快速参考

### 身份验证

**包：** `com.unity.services.authentication` (>= 3.6.1)

处理玩家身份。登录方法：匿名、社交提供者（Google、Apple、Steam、Facebook、Oculus 等）、Unity 浏览器、用户名/密码和设备代码流程。

登录后：`PlayerId` 和 `PlayerName` 即可使用。所有登录方法都会触发 `SignedIn` 事件。`PlayerAccountService`（用于 Unity 浏览器登录）位于一个**单独的程序集**（`Unity.Services.Authentication.PlayerAccounts`）中。

- **完整参考：** [references/authentication.md](references/authentication.md)
- **构建模块：** [玩家账户](#资源商店构建模块) — 现成的登录界面和身份管理

### 云代码

**包：** `com.unity.services.cloudcode` (>= 2.10.3)

运行服务器端 C# 模块（.NET 9）以进行受信任的操作。模块作为 `.ccmr` 文件部署。客户端调用：

```csharp
var result = await CloudCodeService.Instance.CallModuleEndpointAsync<TResult>(
    "ModuleName", "FunctionName", args);
```

推荐使用 C# 模块而不是 JavaScript 脚本进行生产。模块还支持通过订阅进行实时推送消息、事件触发和多人游戏会话范围。

- **完整参考：** [references/cloud-code.md](references/cloud-code.md)

### 云保存

**包：** `com.unity.services.cloudsave` (>= 3.4.0)

每个玩家的键值存储具有三种访问类别，以及游戏范围的 Custom 数据：

| 访问类别 | 读取 | 写入 | 用途 |
|---|---|---|---|
| 默认 | 所有者 | 所有者 | 私有设置、偏好设置 |
| 公开 | 任何人 | 所有者 | 公开配置文件、显示名称 |
| 受保护 | 所有者 | 服务器仅（云代码） | 反作弊数据、服务器授予状态 |
| 自定义 | 任何玩家 | 服务器仅 | 共享游戏状态、全局配置 |

值序列化为 JSON。支持通过 `SaveItem` 进行写锁并发控制、通过 `QueryAsync` 进行服务器端查询，以及二进制文件存储。

- **完整参考：** [references/cloud-save.md](references/cloud-save.md)
- **构建模块：** 由 [成就](#资源商店构建模块)（受保护桶）和 [玩家账户](#资源商店构建模块)（默认/公开数据）使用

### 远程配置

**包：** `com.unity.services.remote-config` (>= 4.2.5)

服务器端游戏配置。将游戏定义（成就列表、通行证等级、商店目录）作为可更新的 JSON 条目存储，而无需客户端构建。通过部署窗口通过 `.rc` 文件部署。

对于 A/B 测试和受众定位，请使用工具包中的游戏覆盖（`.ugo`）。

- **完整参考：** [references/remote-config.md](references/remote-config.md)
- **构建模块：** 由 [成就](#资源商店构建模块) 块用于服务器端定义

### 工具

**包：** `com.unity.services.tooling` (>= 1.4.1)

仅限编辑器的包。将**访问控制**（`.ac`）和**游戏覆盖**（`.ugo`）文件类型注册到部署窗口。访问控制策略基于 URN 基础上允许或拒绝玩家/服务账户对 UGS 服务的访问（拒绝优先于允许）。游戏覆盖通过为特定玩家段覆盖远程配置值来提供 A/B 测试和受众定位。

- **完整参考：** [references/tooling.md](references/tooling.md)

### 部署

**包：** `com.unity.services.deployment` (>= 1.7.2)

仅限编辑器的包，提供**部署窗口**（服务 > 部署）。将云资源部署到目标环境：

| 文件类型 | 扩展名 | 部署内容 |
|---|---|---|
| 远程配置 | `.rc` | 键值配置条目 |
| 访问控制 | `.ac` | 资源访问策略 |
| 云代码模块 | `.ccmr` | C# 服务器端模块（指向 `.sln`） |
| 排行榜 | `.lb` | 排行榜配置 |
| 经济 | `.ec*` | 货币/库存定义 |
| 游戏覆盖 | `.ugo` | 受受众定位影响的配置覆盖 |

- **完整参考：** [references/deployment.md](references/deployment.md)

### UGS CLI

[Unity 游戏服务 CLI](https://github.com/Unity-Technologies/unity-gaming-services-cli/) 是一个独立的命令行工具，用于在 Unity 编辑器外管理 UGS 资源。它可以部署和获取云资源文件（`.rc`、`.ac`、`.ccmr`、`.lb`、`.ec`、`.ugo`），通过 `fetch` 操作从远程环境更新本地可部署文件，部署和获取触发器和计划文件，生成触发器和计划配置的默认版本，并提供跨所有 UGS 服务的更细粒度的管理功能。

### 服务 API

**包：** `com.unity.services.apis` (>= 1.1.1)

为所有 UGS 服务自动生成的 REST 客户端。四种客户端类型：`IGameClient`（玩家）、`IAdminClient`（服务账户）、`IServerClient`（专用服务器）、`ITrustedClient`（提升服务器访问权限）。大多数开发者使用高级包 SDK，而使用服务 API 进行低级控制或管理 API 访问。

- **完整参考：** [references/apis.md](references/apis.md)

## 资源商店构建模块

Unity 在资源商店上提供了免费、可生产的**构建模块**包。每个包都是一个 `.unitypackage`，包含可直接导入项目的现成 UI、运行时代码、云代码模块和云资源文件。

| 构建模块 | 类型 | 关键依赖 | 资源商店 |
|---|---|---|---|
| **成就** | LiveOps | `cloudsave`、`remote-config`、`cloudcode`、`tooling`、`deployment`、`analytics`、`authentication` | [Unity 构建模块 — 成就](https://assetstore.unity.com/packages/essentials/tutorial-projects/unity-building-block-achievements-341918) |
| **排行榜** | LiveOps | `leaderboards`、`cloudcode`、`tooling`、`deployment`、`authentication` | [Unity 构建模块 — 排行榜](https://assetstore.unity.com/packages/essentials/tutorial-projects/unity-building-block-leaderboards-341926) |
| **玩家账户** | LiveOps | `authentication`、`cloudsave`、`cloudcode`、`deployment` | 通过 `com.unity.starter-kits` 提供 |
| **多人会话** | 多人游戏 | `multiplayer` | [Unity 构建模块 — 多人会话](https://assetstore.unity.com/packages/essentials/tutorial-projects/unity-building-block-multiplayer-session-341930) |
| **匹配会话** | 多人游戏 | `multiplayer`、`deployment` | [Unity 构建模块 — 匹配会话](https://assetstore.unity.com/packages/essentials/tutorial-projects/unity-building-block-matchmaker-session-341932) |
| **服务器会话** | 多人游戏 | `multiplayer`、`apis`、`deployment` | 通过 `com.unity.starter-kits` 提供 |
| **Vivox** | 多人游戏 | `vivox`、`authentication` | 通过 `com.unity.starter-kits` 提供 |
| **平台游戏启动套件** | 游戏玩法 | `multiplayer`、`netcode.gameobjects`、URP、Cinemachine、Input System | 通过 `com.unity.starter-kits` 提供 |

> **提示：** 在实现成就、排行榜、玩家账户或多人会话时，建议使用相应的构建模块作为起点。这些模块包含现成的 UI、云代码模块（`.ccmr`）、访问控制（`.ac`）和可部署的云资源，可节省大量实现时间。

### 相关示例项目

| 项目 | 描述 | 来源 |
|---|---|---|
| **用例示例** | 通行证、虚拟商店、每日奖励、启动包、云 AI 小游戏、A/B 测试 | [GitHub — com.unity.services.samples.use-cases](https://github.com/Unity-Technologies/com.unity.services.samples.use-cases) |
| **UGS 示例** | 身份验证流程、经济、远程配置、云代码集成 | [GitHub — com.unity.services.samples](https://github.com/Unity-Technologies/com.unity.services.samples) |
| **Gem Hunter Match** | 完整 2D 匹配 3 游戏，具有玩家中心、进度、社交功能、游戏内商店 | [资源商店](https://assetstore.unity.com/packages/essentials/tutorial-projects/gem-hunter-match-2d-sample-project-278941) |
| **Boss Room** | 使用 Netcode for GameObjects、身份验证、多人游戏服务的 8 玩家合作 RPG | [GitHub — com.unity.multiplayer.samples.coop](https://github.com/Unity-Technologies/com.unity.multiplayer.samples.coop) |

## 现成功能蓝图

适用于常见实时游戏功能的可立即使用的蓝图。每个蓝图都包含数据模型、服务 API 模式、完整工作代码和云资源定义。

| 功能 | 关键服务 | 蓝图 |
|---|---|---|
| **通行证** | `remote-config`、`cloudsave`、`cloudcode`、`economy`、`tooling`、`deployment` — 远程配置（通行证定义）+ 云保存受保护（进度）+ 云代码（XP 奖励、奖励领取、高级购买） | [references/battlepass.md](references/battlepass.md) |
| **成就** | `remote-config`、`cloudsave`、`cloudcode`、`tooling`、`deployment` — 远程配置（定义）+ 云保存（玩家记录）+ 云代码（服务器端权威解锁）+ 访问控制。**资源商店：** [成就构建模块](https://assetstore.unity.com/packages/essentials/tutorial-projects/unity-building-block-achievements-341918) | [references/achievements.md](references/achievements.md) |
| **玩家账户** | `authentication`、`cloudsave` — 身份验证（3 种登录方法）+ 云保存（默认/公开/受保护玩家数据）。**资源商店：** 玩家账户构建模块（通过 `com.unity.starter-kits`） | [references/player-account.md](references/player-account.md) |

## 常见架构模式

### 模式 1：配置 + 状态 + 服务器写入

由 **通行证** 和 **成就** 使用：

1. **定义** 在远程配置（`.rc` 文件）中 — 游戏中存在的内容
2. **玩家状态** 在云保存中 — 每个玩家的进度
3. **通过云代码写入** — 服务器端权威变异
4. **访问控制**（`.ac` 文件）— 阻止玩家直接写入敏感键

### 模式 2：客户端直接数据

由 **玩家账户**（偏好设置、显示设置）使用：

1. **玩家数据** 在云保存默认或公开访问类别中
2. **直接客户端写入** — 无需云代码的非敏感数据

### 模式 3：竞技功能

由 **排行榜** 和排名系统使用：

1. **分数提交** 通过排行榜 API（或通过云代码进行验证）
2. **排名** 客户端端获取，具有分页和相对玩家查询

在为实时游戏功能编写代码后：
1. 验证项目能否无错误地编译。
2. 检查初始化顺序是否正确：`UnityServices.InitializeAsync()` → 认证登录 → 服务调用。
3. 确认敏感数据写入（经验值、奖励、货币）都通过 Cloud Code 路由，而不是直接从客户端写入。
4. 验证 Access Control `.ac` 文件是否禁止玩家直接写入受保护的 Cloud Save 键。
5. 验证所有云资源文件（`.rc`、`.ac`、`.ccmr`、`.lb`、`.ec`）是否存在并可通过部署窗口部署。

## 部署清单

对于任何实时游戏功能，请通过部署窗口部署这些云资源：

- [ ] `.rc` 文件 — 远程配置条目（游戏定义、配置）
- [ ] `.ac` 文件 — 访问控制策略（禁止直接写入受保护键）
- [ ] `.ccmr` 文件 — Cloud Code 模块引用（指向模块 `.sln`）
- [ ] `.lb` 文件 — 排行榜配置（如果使用排行榜）
- [ ] `.ec` 文件 — 经济定义（如果使用虚拟货币/物品）
- [ ] `manifest.json` — 确保所有必需的包都列出了正确的版本
- [ ] **服务 > 部署** 设置中配置的环境

## 详细参考

### 服务参考
- **认证** — 登录方法、事件、配置文件、身份提供者、代码模板：[参考/认证.md](参考/认证.md)
- **Cloud Code** — 脚本、模块、订阅、触发器、模块创建、代码模板：[参考/CloudCode.md](参考/CloudCode.md)
- **Cloud Save** — 访问类、数据操作、文件、查询、代码模板：[参考/CloudSave.md](参考/CloudSave.md)
- **Remote Config** — 定义、`.rc` 格式、游戏覆盖、代码模板：[参考/RemoteConfig.md](参考/RemoteConfig.md)
- **工具** — 访问控制（`.ac`）策略、游戏覆盖（`.ugo`）、URN 参考：[参考/Tooling.md](参考/Tooling.md)
- **部署** — 文件类型、工作流、程序化 API：[参考/Deployment.md](参考/Deployment.md)
- **服务 API** — 四种客户端类型、服务区域、代码模板：[参考/apis.md](参考/apis.md)

### 功能蓝图
- **成就** — 完整实现，包括数据模型、客户端代码、Cloud Code 模块、云资源：[参考/Achievements.md](参考/Achievements.md)
- **通行证** — 完整实现，包括分层经验值、免费/付费轨道、Cloud Code 模块、云资源：[参考/BattlePass.md](参考/BattlePass.md)
- **玩家账号** — 登录流程、身份管理、Cloud Save 数据、代码模板：[参考/PlayerAccount.md](参考/PlayerAccount.md)

## 提醒

完成前请验证：
- 是否按顺序使用 `UnityServices.InitializeAsync()` → 认证登录 → 服务调用？
- 所有敏感写入（经验值、奖励、货币）是否都通过 Cloud Code 模块路由？
- 所有云资源文件（`.rc`、`.ac`、`.ccmr`）是否存在并可部署？
- Cloud Save 读取访问类是否与写入的桶匹配？
