# itch.io 发布（butler）

将构建部署到 itch.io 页面并保持更新。页面在浏览器中创建；所有上传都通过 **butler**，itch.io 的命令行工具，只需一个你将永远使用的命令：`butler push`。butler 与之前的构建进行差异比较，仅上传已更改的内容。深度 CI/CD 和标志详情位于 `references/butler-ci.md`。

## 使用场景

- 创建/更新 itch.io 项目页面时使用，安装或登录 butler，使用 `butler push` 上传构建，选择频道名称，版本化上传，或将 jam/演示/发布构建发送到 itch.io。
- 触发器：`butler push`，`butler login`，频道，`.itch.toml`，"在 itch 上发布"，“上传到 itch”。

**不使用场景**：在 Steam 上发布（使用 `steam-publish`）；jam *范围/规划*（使用 `game-jam` — 此技能仅是上传机制）；构建游戏本身（引擎技能）。

## 核心工作流程

1. **在 `itch.io/game/new` 创建项目页面**。设置 **项目类型**：为原生构建保留 *可下载*，或选择 **HTML** 用于浏览器可玩游戏（这是网页构建所必需的 — 见陷阱）。设置价格/可见性（准备就绪前设为草稿）。
2. **安装 butler 并登录**。从 `itchio.itch.io/butler` 下载，添加到 `PATH`，然后 `butler login`（在浏览器中授权）。使用 `butler version` 进行验证。对于 CI，使用 `BUTLER_API_KEY` — 见参考。
3. **准备一个可移植构建文件夹** — 玩家运行的确切文件，无额外内容。推送一个 **文件夹**（或该文件夹的 `.zip`），**不是安装程序**，**也不是压缩文件的压缩存档**（会损害补丁 — 见陷阱）。
4. **推送到频道**：`butler push <目录> <用户>/<游戏>:<频道>`。频道名称决定平台标签（见模式）。首次推送上传所有内容；后续推送到同一频道仅上传差异。
5. **在 *编辑游戏* 页面上设置平台/HTML 标签**，如果频道未正确自动标记，然后 **保存**。对于浏览器游戏，也切换到 **HTML** 标签频道 *可在浏览器中运行*。
6. **版本化你的构建**（可选但推荐）：`--userversion 1.2.0` 或 `--userversion-file build.txt`，以便你控制玩家和更新 API 看到的版本字符串。
7. **稍后更新**，再次推送到 *相同* 频道。使用 `butler status <用户>/<游戏>` 查看频道/构建，并使用 `butler push-preview` 在发送前查看推送将更改的内容。

## 模式

### 1. 你需要的唯一命令 — `butler push`

```bash
# butler push <目录或zip> <用户>/<游戏>:<频道>
butler push ./build/windows leafy/my-game:windows
butler push ./build/mac     leafy/my-game:osx
butler push ./build/linux   leafy/my-game:linux
butler push ./web           leafy/my-game:html   # 浏览器构建（也设置页面 Kind = HTML）
```

### 2. 频道命名控制平台标签（连字符，小写）

```text
频道名称中的子字符串 -> 自动应用的标签：
  win / windows  -> Windows        linux -> Linux
  mac / osx      -> macOS          android -> Android
一个频道中允许多个平台：例如一个 Java jar：
  butler push ./jar leafy/my-game:win-linux-mac
约定：小写单词用连字符分隔（windows-beta, osx-demo, soundtrack）。
标签只是初始猜测 — 随时在 *编辑游戏* 页面（然后保存）进行修正。
```

### 3. 版本、验证和预览

```bash
butler version                              # 打印版本；确认安装 + PATH
butler login                                # 授权此机器（打开浏览器）

# 设置显式版本字符串，而不是 itch 的自动递增整数：
butler push ./build leafy/my-game:windows --userversion 1.2.0
butler push ./build leafy/my-game:windows --userversion-file build_number.txt

butler status leafy/my-game                 # 列出频道 + 最新构建/版本
butler push-preview ./build leafy/my-game:windows   # NEW/MODIFIED/DELETED/SAME，不上传任何内容
```

### 4. 首次、隐藏和过滤推送

```bash
# 隐藏一个全新的频道，直到你准备好（仅限 NEW 频道）：
butler push ./build leafy/my-game:windows-beta --hidden

# 从上传中排除文件，不复制文件夹（--ignore 可重复）：
butler push ./build leafy/my-game:windows --ignore '*.pdb' --ignore '*.dSYM'

# 预览将要发送的内容，但不发送：
butler push ./build leafy/my-game:windows --dry-run
```

## 陷阱

- **推送安装程序**。itch.io 补丁 *可移植* 构建；安装程序（`.exe`/`.msi`）会破坏补丁和 itch 应用的自动更新，并且可能需要玩家没有权限的管理员权限。推送提取后的可运行文件夹。
- **预压缩构建**。推送一个高度压缩的存档（或存档的存档）会使补丁巨大 — 一个微小更改会重写整个压缩块。推送未压缩文件；itch.io 在其端压缩。
- **仅包含一个 `.zip` 的文件夹**。butler 自动解压并推送内容（避免“zip 在 zip 中”）。仅当确实想将 zip 作为单个不透明文件上传时，才传递 `--no-auto-unzip`。
- **HTML5 游戏显示为下载**。需要两个开关：将页面 **类型** 设置为 *HTML*，并在首次推送后 *编辑游戏* 页面上标记频道 *可在浏览器中运行* — 这两个都不会自动从频道名称发生。
- **`--hidden` 在现有频道上出错**。它仅在推送 *创建* 新频道时适用。稍后从 *编辑游戏* 中取消隐藏。
- **频道拼写错误导致重复插槽**。`windows` 和 `win-final` 是不同的频道，并创建单独的下载。提前决定你的频道名称并重复使用。
- **30 GB 限制**。itch.io 会拒绝总*未压缩*大小超过 30 GB 的构建。
- **CI 日志中的密钥**。在公共日志中打印的 `BUTLER_API_KEY` 被泄露 — 立即在该 API 密钥页面上撤销。见参考了解安全的 CI 使用。

## 参考

- 对于使用 `BUTLER_API_KEY` 的 CI/CD（GitHub Actions/GitLab）、通过 `broth` 自动安装、完整标志列表和更新检查 API，请阅读 `references/butler-ci.md`。
- 主要文档：butler 手册 — `itch.io/docs/butler`（安装、登录、推送）。

## 相关技能

- `steam-publish` — 通过 SteamPipe 在 Steam 上发布相同游戏（通常与 itch.io 一起使用）。
- `game-jam` — 大多数 jam 都在 itch.io 上托管；此技能处理上传步骤。
- `prototype-fast` — 在草稿/限制性 itch 页面上共享早期原型进行测试。
