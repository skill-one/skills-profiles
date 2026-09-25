# Steam 发布 (Steamworks + SteamPipe)

将一个完成的构建部署到 Steam 商店页面。有两个并行运行的流程，两者都必须获得批准才能发布：**商店页面**（存在性）和**构建**（SteamPipe 上传 + 发布检查清单）。这项技能是操作检查清单；深入的构建脚本、CI/CD 和故障排除细节位于 `references/steampipe-build-scripts.md`。

## 何时使用

- 在设置 Steam 应用、构建/编辑商店页面、配置仓库和包、通过 SteamPipe/steamcmd 上传构建、管理测试分支或发布和更新 Steam 标题时使用。
- 触发器：`steam_appid.txt`、Steamworks SDK `tools/ContentBuilder`、`app_build_*.vdf`、`steamcmd`、"在 Steam 上发布"、"仓库"、"设置构建上线"。

**不使用时的情况**：在 itch.io 上发布（使用 `itch-publish`）；在游戏中编写 Steamworks **API**（成就/云/覆盖层存在于引擎 SDK 集成中，而不是这里）；商店/财务 *建议*（定价策略、税务）——将用户引导至 Steamworks 文档和其自身的咨询。

## 前置条件（按顺序一次性完成）

1. **合作伙伴账户 + Steam Direct 费用。** 每个新应用都需要 Steam Direct 可收回费用（撰写时为每个应用 100 美元）。您将获得一个 **App ID** — 在您的 Steamworks 主页上找到它。将 App ID 视为以下所有内容的密钥。
2. **一个具有最低权限的专用构建账户。** 构建需要一个位于您的合作伙伴组中的 Steam 账户，具有 **编辑应用元数据** 和 **将应用更改发布到 Steam**。创建一个仅具有这些权限的*单独*构建账户（不是您的管理员登录）。发布应用还需要 **管理定价和折扣**。
3. **在上传机器上下载 Steamworks SDK。** SteamPipe 工具位于 `tools/ContentBuilder/` 下。

> 安全提示：永远不要将账户密码或 `config.vdf` 登录令牌提交到仓库中。参见参考中的 CI/CD 部分以了解支持的令牌工作流程。

## 核心工作流程

1. **配置应用 (App Admin)。**
   - 在 *安装* 下设置 **启动选项**（可执行路径 + 每个操作系统的参数）。对于子文件夹可执行文件，将子文件夹放入可执行字段 — 不要有前导斜杠/点。
   - 在 *仓库* 页面上添加 **仓库**（仓库是一堆文件）。为每个仓库命名（"基础内容"、"Windows 内容"）。除非仓库确实是特定于操作系统或语言的，否则保留 *[所有语言]* / *[所有操作系统]*。
   - **授予自己仓库权限**：将它们添加到您的 **开发者组件** 包中，位于 *关联包和 DLC* 页面，否则您将无法拥有您上传的内容。
   - **发布** 配置。未发布的配置是上传失败的最常见原因。
2. **构建商店页面（存在性流程）。** 填充图形资源、描述、标签、预告片、系统要求。完成后，点击 **标记为准备审核**。商店审核需要 3-5 个工作日；至少在您希望它上线前 **7 天** 提交。它必须在发布前至少在 **即将推出** 中存在 **2 周**。
3. **创建您的构建脚本。** 从以下模式中的简单应用构建 `.vdf` 开始；对于多仓库/多平台应用使用仓库脚本（参见参考）。脚本将本地文件映射到仓库，并指定构建输出/日志的位置。
4. **引导 steamcmd 和上传。** 运行 `steamcmd` 一次以自我更新，然后运行构建（模式）。steamcmd 将文件分块（约 1 MB），仅上传更改的块，并注册一个全局 **BuildID**。
5. **在分支上设置构建上线。** 转到 `https://partner.steamgames.com/apps/builds/<AppID>`，选择构建，**预览更改**，然后为分支 **立即设置构建上线**。首先在测试分支上测试（参见 `references/steampipe-build-scripts.md` 中的分支设置）。
6. **运行游戏构建检查清单** 并 **标记为准备审核**（商店存在性必须在构建审核之前提交）。两个流程都必须获得批准。
7. **手动发布。** 批准后且即将推出已运行其时间，使用绿色的 **发布应用** 按钮→ **立即发布** → **立即发布**。批准的应用不会自行发布。
8. **稍后更新** 通过上传新构建并在 `default` 上设置上线（手动）或首先发送到测试分支。参见 `references/steampipe-build-scripts.md`。

## 模式

### 1. SteamPipe ContentBuilder 布局 (Steamworks SDK)

```text
tools/ContentBuilder/
  builder/         steamcmd.exe (Windows)   <- 运行一次以引导
  builder_linux/   steamcmd (Linux)
  builder_osx/     steamcmd (macOS)
  content/         <- 您的最终可运行构建位于此处（玩家获取的文件）
  output/          构建日志 + 块缓存（可以安全删除；加快重新上传速度）
  scripts/         <- 您的 *.vdf 构建脚本位于此处
```

### 2. 最小应用构建脚本 — `app_build_1000.vdf`

```text
// AppID 1000，一个仓库（1001）：递归上传 ../content 下的所有内容。
// VDF 是 Valve KeyValues："key" "value"，括号用于嵌套。调整 ID 以匹配您的应用。
"AppBuild"
{
    "AppID"       "1000"                 // 您的 App ID
    "Desc"        "1.0.0 启动构建"       // 仅内部可见；在您的构建中可见

    "ContentRoot" "..\content\"          // 要上传的文件根目录（相对于此文件）
    "BuildOutput" "..\output\"           // 日志 + 块缓存

    "Depots"
    {
        "1001"                           // 您的 Depot ID
        {
            "FileMapping"
            {
                "LocalPath"  "*"         // 从 ContentRoot 中的所有文件
                "DepotPath"  "."         // 映射到仓库根目录
                "recursive"  "1"         // 包括子文件夹
            }
        }
    }
}
```

### 3. 上传构建（Windows；在其他地方替换平台构建器）

```bat
REM 从 SDK 运行。引导一次，然后构建。使用构建账户，而不是您的管理员登录。
tools\ContentBuilder\builder\steamcmd.exe ^
  +login <build_account> <password> ^
  +run_app_build ..\scripts\app_build_1000.vdf ^
  +quit
```

```text
发生的事情：steamcmd 自我更新 -> 登录 -> 对于每个仓库，将文件哈希为 ~1 MB 块 -> 仅上传新块 -> 写入仓库清单 -> 以全局 BuildID 结束。构建尚未上线；按照工作流程设置上线。
```

### 4. 使用预览构建安全迭代（不进行上传）

```text
// 添加到 AppBuild 块中以验证文件映射而不上传：
"Preview" "1"     // 仅将日志 + 文件清单输出到 BuildOutput
// 并且在成功构建后自动在 BETA 分支上设置上线（永远不会 'default'）：
"SetLive" "beta-qa"
```

## 陷阱

- **`default` 分支不能自动设置上线。** `SetLive` 仅适用于 *beta* 分支；您必须手动在 App Admin 中设置默认（客户）构建上线。围绕这一点规划发布。
- **商店页面必须在构建之前获得批准。** 您不能在商店存在性提交后提交构建进行审核；两者都必须通过，且即将推出必须运行 ~2 周。
- **标题永远不会自动发布。** 即使批准后，也必须有人点击 **发布应用** 在选定的时刻。
- **Mac/Linux 什么也不安装。** 几乎总是：特定于操作系统的仓库不在包中。将每个仓库添加到 *关联包和 DLC* 中的包。
- **未发布的应用配置。** "无法获取应用信息" / 构建错误通常意味着仓库、启动选项或 App ID 配置从未 **发布**。
- **构建上的 `status = 6`。** 构建账户缺乏 App ID 的权限，或 `ContentRoot`/`LocalPath` 指向了错误（空）路径。
- **提交登录令牌。** `config.vdf` Steam Guard 令牌和账户密码是机密。将它们从仓库中移除；使用参考中的 CI 工作流程。
- **已发布应用的延迟安全。** 修改构建账户的电子邮件/电话会强制 **3 天** 等待，然后您才能为 *已发布* 的应用设置构建上线 — 不要在发布前重新配置账户。

## 参考

- 对于高级多仓库/多平台构建脚本、`FileExclusion`/`FileProperties`、beta 分支设置、CI/CD 登录令牌工作流程和 SteamPipe 故障排除表，请阅读 `references/steampipe-build-scripts.md`。
- 主要文档：Steamworks "上传到 Steam"（`partner.steamgames.com/doc/sdk/uploading`）、"发布流程"（`/doc/store/releasing`）、"分支（测试）"（`/doc/store/application/branches`）、"仓库"（`/doc/store/application/depots`）。

## 相关技能

- `itch-publish` — 相同的游戏在 itch.io 上发布，通常与 Steam 一起进行。
- `game-jam` / `prototype-fast` — 相同项目生命周期早期的阶段。
