# Solana 移动项目

设置和维护 Solana 移动应用。`solana-mobile` CLI 负责脚手架搭建、环境检查和模拟器管理 — 优先使用它而不是手动配置。

无需安装即可运行：

```bash
npx solana-mobile@latest --help
```

`pnpm dlx solana-mobile@latest` 和 `bunx solana-mobile@latest` 是等效的。匹配项目当前使用的包管理器，并保持 `@latest`，这样运行器就不会重复使用较旧的缓存版本。

| 命令 | 用途 |
| --- | --- |
| `create` | [创建新项目](#创建新项目) |
| `device` | [安装 APK、打开 URL、准备设备](#与连接的设备一起工作) |
| `doctor` | [检查工具链](#检查环境) |
| `emulator` (`emu`) | [创建和运行模拟器](#管理 Android 模拟器) |
| `localnet` | [设备可以连接的本地验证器](#运行本地验证器) |
| `playground` | [在不构建应用的情况下测试钱包](#在不使用应用的情况下测试钱包) |
| `templates` | 维护模板仓库 — 仅限模板作者 |
| `webshell` | 将现有 Web 应用封装在 Android WebView 壳中 |

每个命令的每个标志：[references/cli.md](references/cli.md)。不要猜测标志 — CLI 提供自己的帮助，并且任何命令上的 `--help` 都是权威的。

## 不可协商的限制

**移动钱包适配器需要开发版本。Expo Go 将无法工作** — MWA 依赖于 Expo Go 没有打包的原生 Android 模块。如果有人报告在 Expo Go 中钱包连接失败，那是因为此原因；没有解决方法，他们需要 `expo run:android`。

Android 是唯一支持钱包的平台。iOS 构建可以运行，但没有 MWA。

## 首先：确定你处于哪种情况

| 情况 | 执行此操作 |
| --- | --- |
| 尚无项目 | [创建新项目](#创建新项目) |
| 现有 Expo 应用，没有 Solana | 阅读 [references/add-to-existing-app.md](references/add-to-existing-app.md) |
| 项目已存在，构建或工具链损坏 | [检查环境](#检查环境) |
| 项目已存在，需要钱包功能 | 使用 `solana-mobile-wallet` 技能 |
| 钱包连接或签名需要测试 | [在不使用应用的情况下测试钱包](#在不使用应用的情况下测试钱包) |

## 创建新项目

```bash
npx solana-mobile@latest create
```

默认情况下是交互式的。要跳过提示，请指定项目名称和模板：

```bash
npx solana-mobile@latest create my-app --template expo-kit-wallet
```

有用的标志：

| 标志 | 效果 |
| --- | --- |
| `-t, --template <id>` | 非交互式选择模板 |
| `--pm <manager>` | 要使用的包管理器 |
| `--minimal` | 使用最小模板 |
| `--list-templates` | 打印模板目录 |
| `--list-template-ids` | 打印模板 ID 作为 JSON 数组 |
| `--skip-install` | 不安装依赖项 |
| `--skip-git` | 不初始化 git 仓库 |
| `-d, --dry-run` | 显示会发生什么，不写入任何内容 |

### 选择模板

模板分为两个系列。**选择 `expo-kit-*` 模板。** `@solana/kit` 是当前的 Solana 客户端库，CLI 最积极地维护这些模板。

只有在用户故意继续现有的 `@solana/web3.js` 代码库或要求指定名称时，才使用 `expo-web3js-*`。如果他们没有理由就要求，建议 kit 是更好的起点，然后再按其要求进行 — 基于 web3.js 的新应用在生命周期中需要迁移。

`expo-kit-minimal` 是 kit 组件如何组合的最清晰参考，即使构建在不同的模板上，也值得阅读。

| 模板 | 堆栈 | 用途 |
| --- | --- | --- |
| `expo-kit-wallet` | Kit + MWA + Uniwind | **最佳默认值。** 钱包连接、签名、发送已经配置好 |
| `expo-kit-minimal` | Kit | 最小起点，没有 UI 套件 |
| `expo-kit-uniwind` | Kit + Uniwind | Tailwind 风格的样式，尚未有钱包 |
| `expo-kit-privy` | Kit + Privy + Uniwind | 替代或与 MWA 一起使用的 Privy 认证 |
| `expo-web3js-wallet` | web3.js + MWA | 遗留钱包应用 |
| `expo-web3js-paper` | web3.js + RN Paper | 遗留，Material UI |
| `expo-web3js-minimal` | web3.js | 遗留最小起点 |

模板 ID 也接受完整的 `gh:solana-mobile/templates/mobile/<name>` 形式。如果模板似乎缺失，请重新运行 `--list-templates` 而不是信任此表格 — 目录随 CLI 提供，而不是随此技能提供。

### 脚手架搭建后

```bash
cd my-app && npm run android
```

这会运行 `expo run:android`，它会构建并安装开发版本。第一个 Android 构建很慢（Gradle 冷启动）；后续构建会重用缓存。

## 检查环境

在调试构建失败之前，检查工具链：

```bash
npx solana-mobile@latest doctor
```

它报告本地 Android 和 Node 工具链，并推荐任何缺失的内容。`--json` 提供一个稳定的报告，值得在需要根据特定检查分支时解析；`--verbose` 添加解析路径和诊断信息。

每当构建因原因失败且这些原因显然不在应用代码中时，首先运行 `doctor`。

## 管理 Android 模拟器

```bash
npx solana-mobile@latest emu list
npx solana-mobile@latest emu status
npx solana-mobile@latest emu create
npx solana-mobile@latest emu start my_phone
npx solana-mobile@latest emu stop my_phone
```

`emu` 是 `emulator` 的别名。子命令：`create`、`delete`、`images`、`list`、`start`、`status`、`stop`、`tune`。系统镜像位于 `emu images` (`install`、`list`、`delete`) 下。

在特定设备配置上创建命名的模拟器：

```bash
npx solana-mobile@latest emu create local_phone --device pixel_9
```

### 准备新的模拟器

新创建的 AVD 还未准备好进行钱包工作：它没有运行，其首次运行对话框仍然处于启用状态，并且没有钱包应用。按顺序对其进行调整，然后安装一个 — 因为 `device install` 需要一个已启动的设备来安装到它上面：

```bash
npx solana-mobile@latest emu start local_phone --tune
npx solana-mobile@latest device install fakewallet
```

`--tune` 禁用新 AVD 上位于应用上方的动画、首次运行对话框、锁屏和通知。调整是可选的 — `emu start` 和 `emu create --start` 仅在传递 `--tune` 时应用它 — 并且以这种形式它是非交互式的，这就是它在脚本中要使用的。`emu create` 接受 `--start --tune` 来在创建时执行所有这些操作。

`device install fakewallet` 将移动钱包适配器测试钱包放在正在运行的模拟器上。如果没有钱包应用，MWA 没有可以传递并静默连接的东西 — 最常见的“模拟器上的连接无反应”原因是此原因。

任何依赖于 Seeker Genesis Token 的内容仍然需要一个真实的 Seeker 设备；模拟器无法持有其中一个。请参阅 `seeker-genesis-token` 技能。

## 与连接的设备一起工作

`device` 涵盖所有通过 adb 的内容，无论是模拟器还是物理手机。

```bash
npx solana-mobile@latest device list                       # 序列号、状态、名称
npx solana-mobile@latest device install fakewallet         # 目录 APK
npx solana-mobile@latest device install ./app-release.apk  # 本地文件
npx solana-mobile@latest device open http://localhost:3000 # 在设备上打开
npx solana-mobile@latest device tune --all -y              # 准备自动化
```

`device open` 创建 `adb reverse` 以便本地主机 URL 本身，因此这台机器上的开发服务器可以从 USB 连接的手机访问。优先使用它而不是手写的 `adb reverse` 加上 `am start` 咒语。

`device tune` 和 `emu tune` 应用相同的调整，但有两处不同，第二处会在脚本中咬人。`device tune` 接受物理设备，接受 `--device <serial>` 或 `--all`，并回退到唯一连接的设备。`emu tune` 拒绝非模拟器序列号，接受 AVD 名称或序列号作为位置参数，并在没有提供时打开选择器 — 即使只有一个模拟器正在运行，甚至在使用 `-y` 时，都会跳过调整提示而不会跳过模拟器提示。在无人值守的情况下指定目标：`emu tune local_phone -y`。

## 运行本地验证器

```bash
npx solana-mobile@latest localnet start
npx solana-mobile@latest localnet check
```

`localnet start` 获取一个在主机上提供验证器的验证器，并将其端口转发到每个连接的设备，因此应用可以通过 `localhost:8899` 访问，就好像验证器在设备上运行一样。它重用它已经启动的本地网容器，连接到已经在这些端口上响应的验证器 — 原生验证器，根本不需要 Docker — 并仅在两者都不存在时启动容器。`check`
验证每个设备的可达性 — 这是在应用无法看到显然在这台机器上运行的验证器时要问的问题。

`localnet forward` 在插入新设备后重新应用转发，`logs`、`status` 和 `stop` 做它们所说的事情。

## 在不使用应用的情况下测试钱包

```bash
npx solana-mobile@latest playground
```

提供钱包测试页面，在设备上打开它，并将每个 MWA 交互流回终端：连接、登录（SIWS）、签名消息、签名交易、签名并发送。它默认针对 devnet 运行；`--cluster localnet` 指向 `localnet` 验证器，而主网需要你自己的 `--url`，因为公共端点拒绝浏览器源请求。

**使用此功能将应用错误与设置错误分开。** 如果 playground 无法签名，问题在于钱包或设备，而不是正在调试的代码。它需要一个 MWA 钱包安装 — 如果没有，则 `device install fakewallet`。
