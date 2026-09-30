---
name: portless
description: 为命名本地开发服务器 URL 设置和使用 portless（例如使用 https://myapp.localhost 而不是 http://localhost:3000）。在将 portless 集成到项目中、配置开发服务器名称、设置本地代理、处理 .localhost 域名或排查端口/代理问题时使用。
---

# 无端口

将端口编号替换为稳定的、命名的 .localhost URL。适用于人类和代理。

## 为什么无端口

- **端口冲突**：两个项目默认使用相同端口时出现 `EADDRINUSE`
- **记忆端口**：哪个应用在 3001 上 vs 8080？
- **刷新显示错误应用**：停止一个服务器，在同一端口启动另一个，陈旧的标签显示错误内容
- **单体仓库倍增器**：仓库中的每个服务都会放大每个问题
- **代理测试错误端口**：AI 代理猜测或硬编码错误的端口
- **Cookie/存储冲突**：`localhost` 上的 Cookie 跨应用泄露；端口更改时 localStorage 丢失
- **配置中硬编码端口**：CORS 允许列表、OAuth 重定向、`.env` 文件在端口更改时中断
- **与队友共享 URL**："什么端口在上面？" 变成一个 Slack 问题
- **浏览器历史记录无用**：`localhost:3000` 历史记录是多个不相关项目的混合

## 安装

全局安装（推荐）或作为项目开发依赖项安装。**不要**用于一次性执行使用 `npx` 或 `pnpm dlx`。

```bash
# 全局（可在任何地方使用）
npm install -g portless

# 或作为项目开发依赖项
npm install -D portless
```

当按项目安装时，通过 `package.json` 脚本或 `npx portless` 调用（由于包是本地的，npx 不会下载任何内容）。

## 快速入门

```bash
# 全局安装（或添加 -D 到项目）
npm install -g portless

# 运行您的应用（自动在端口 443 启动 HTTPS 代理）
portless run next dev
# -> https://<项目>.localhost

# 或使用显式名称
portless myapp next dev
# -> https://myapp.localhost
```

代理在运行应用时自动启动。您也可以使用 `portless proxy start` 明确启动它。自动启动会重用最近代理运行时的配置（端口、TLS、TLD），因此重启或重新启动不会静默恢复默认值。显式环境变量始终优先。

在非交互式环境（没有 TTY，或 `CI=1`）中，portless 会退出并显示描述性错误，而不是提示。像 turborepo 这样的任务运行器应该预先启动代理。

## 集成模式

### 无配置（推荐）

裸 `portless` 开箱即用。它通过代理运行 `package.json` 中的 `"dev"` 脚本，从包名、git 根目录或目录中推断应用名称：

```bash
portless        # -> 运行 "dev" 脚本，https://<项目>.localhost
pnpm dev        # -> 无需 portless，纯 "next dev"
```

使用可选的 `portless.json` 覆盖默认值（名称、脚本、端口）：

```json
{ "name": "myapp" }
```

```bash
portless        # -> 运行 "dev" 脚本，https://myapp.localhost
```

### 单体仓库

在仓库根目录下有一个 `portless.json`。Portless 从 `pnpm-workspace.yaml` 或 `package.json` 中的 `"workspaces"` 字段（npm、yarn、bun）发现包：

```json
{
  "apps": {
    "apps/web": { "name": "myapp" },
    "apps/api": { "name": "api.myapp" }
  }
}
```

```bash
portless                  # 从仓库根目录：启动所有具有 "dev" 脚本的项目
cd apps/web && portless   # 启动单个项目
portless --script start   # 运行 "start" 而不是 "dev"
```

`apps` 映射是可选的，仅提供名称覆盖。未列出的包会自动发现并推断名称。

如果没有 `apps` 映射，主机名遵循 `<包>.<项目>.localhost`。项目名称来自最常见的 npm 范围（例如 `@myorg/web` 和 `@myorg/api` 产生 `myorg`），如果无法找到，则回退到工作区根目录名称。如果包的短名称与项目名称匹配，则使用 `<项目>.localhost`。

### Turborepo

对于 turborepo 项目，将 portless 作为 `dev` 脚本使用，而真实命令在单独的脚本中：

```json
{
  "scripts": { "dev": "portless", "dev:app": "next dev" },
  "portless": { "name": "myapp", "script": "dev:app" }
}
```

`pnpm dev` 运行 turbo，turbo 在每个包中运行 `portless`。Portless 检测包管理器并通过代理运行 `pnpm run dev:app`。

当 `portless` 从工作区根目录运行时，它使用现有的 Turbo 集成来保留任务顺序，当 `turbo.json` 或 `turbo.jsonc` 可读时。在根 portless 配置中设置 `"turbo": false` 以使用直接启动。

### package.json 脚本

您仍然可以直接在脚本中使用 portless：

```json
{
  "scripts": {
    "dev": "portless run next dev"
  }
}
```

代理在运行应用时自动启动。或显式启动：`portless proxy start`。

### 带子域的多应用设置

```bash
portless myapp next dev          # https://myapp.localhost
portless api.myapp pnpm start    # https://api.myapp.localhost
portless docs.myapp next dev     # https://docs.myapp.localhost
```

默认情况下，仅明确注册的子域会被路由（严格模式）。使用 `--wildcard` 启动代理以允许任何注册路由的子域回退到该应用（例如 `tenant1.myapp.localhost` 路由到 `myapp` 应用）。精确匹配始终优先于通配符。

### Git 工作树

`portless run` 自动检测 git 工作树。在一个链接工作树中，分支名称作为子域前缀添加，以便每个工作树都有一个唯一的 URL：

```bash
# 主工作树（无前缀）
portless run next dev   # -> https://myapp.localhost

# 链接工作树在 "fix-ui" 分支上
portless run next dev   # -> https://fix-ui.myapp.localhost
```

无需配置更改。将 `portless run` 放在 `package.json` 中一次，它就会在所有工作树中工作。

### 跳过 portless

设置 `PORTLESS=0` 以直接运行命令而不使用代理：

```bash
PORTLESS=0 pnpm dev   # 跳过代理，使用默认端口
```

当代理命令被 Ctrl+C 停止时，portless 会等待其进程树退出。第二个 Ctrl+C 会转发另一个中断，并在短暂的宽限期后终止剩余的后代。

## 工作原理

1. `portless proxy start` 在端口 443 上启动 HTTPS 反向代理作为后台守护进程。在 macOS/Linux 上自动提升权限；如果无法使用 sudo，则回退到端口 1355。使用 `--no-tls` 在端口 80 上使用纯 HTTP。可通过 `-p` / `--port` 或 `PORTLESS_PORT` 环境变量配置。当您运行应用时，代理也会自动启动。
2. `portless <名称> <命令>` 通过 `PORT` 环境变量分配一个随机的空闲端口（4000-4999）并将应用注册到代理
3. 浏览器访问 `https://<名称>.localhost`；代理转发到应用的分配端口

在局域网模式外，代理及其 HTTP 重定向监听器仅绑定到 IPv4 和 IPv6 环回地址，`127.0.0.1` 和 `::1`。它们不接受通过局域网、VPN 或其他网络接口的连接。

`.localhost` 域名在 Chrome、Firefox 和 Edge 中原生解析为 `127.0.0.1`。Safari 依赖于系统 DNS 解析器，它可能无法处理所有配置中的 `.localhost` 子域。如果需要，运行 `portless hosts sync` 将条目添加到 `/etc/hosts`。

使用 `portless proxy start --tld localhost --tld test` 从一个代理为多个 TLD 下的相同应用名称提供服务。`PORTLESS_URL` 使用第一个配置的 TLD。当配置的 TLD 重叠时（例如 `example.com` 和 `dev.example.com`），主机名会根据最长的 TLD 首先匹配，而不管配置顺序如何。`PORTLESS_TLD` 接受相同的逗号分隔列表格式，例如 `PORTLESS_TLD=localhost,test`。

TLD 可以是多段 DNS 名称，例如 `dev.example.com`，因此本地 URL 可以镜像生产结构（`myapp.dev.example.com`）。每个标签都遵循 DNS 规则：小写字母、数字、内部连字符、每个标签 63 个字符、总共 253 个字符。严格的 OAuth 提供商拒绝 `.localhost` 重定向 URI 接受一个真实域名，例如 `https://myapp.dev.example.com/api/auth/callback/google`。

大多数框架（Next.js、Express、Nuxt 等）会自动尊重 `PORT` 环境变量。对于忽略 `PORT` 的框架（Vite、VitePlus、Astro、React Router、Angular、Expo、React Native），portless 会自动注入正确的 `--port` 标志，并在需要时注入匹配的 `--host` CLI 标志。注入通过以框架或已知运行器（`"dev": "vite"`，`"dev": "bunx vite"`）开头的包脚本传递。只有框架的服务器命令（`dev`、`serve`、`preview`、`start`、裸 `vite` 或 `vite [root]`）会获得这些标志；不提供服务的命令，如 `vite build`、`vite optimize`、`vp test` 或 `astro check`，会拒绝它们并保持原样。Expo 连接模式（`--localhost`、`--lan`、`--tunnel`）会被保留，同时分配的端口仍然会被注入。Portless 会保留无法分类的脚本：CLI 上的子命令之前的标志，其标志语法它不跟踪（`vp --mode dev build`）。当向它添加标志时，Portless 会保留脚本：复合命令（`&&`、`|`、`;`）、尾随 `#` 注释、它自己的 `--` 选项终止符、环境前缀（`NODE_ENV=production vite`）、委托到另一个脚本（`"dev": "npm run dev:vite"`）或脚本名称之前的运行器标志（`bun run --bun dev`）。这些会保留自己的端口，因此您需要在脚本中自行设置它。

### 状态目录

Portless 将其状态（路由、PID 文件、端口文件）存储在 `~/.portless` 中。当代理使用 sudo 运行时，这仍然是调用用户的家目录，因此无特权的应用和代理可以共享路由注册。通过 `PORTLESS_STATE_DIR` 环境变量覆盖。

### 环境变量

| 变量              | 描述                                                                    |
| --------------------- | ------------------------------------------------------------------------------ |
| `PORTLESS_PORT`       | 覆盖默认代理端口（默认：443 带有 HTTPS，80 不带）                            |
| `PORTLESS_APP_PORT`   | 为应用使用固定端口（跳过自动分配）                                        |
| `PORTLESS_HTTPS`      | 默认启用 HTTPS；设置为 `0` 以禁用（与 `--no-tls` 相同）                |
| `PORTLESS_LAN`        | 设置为 `1` 以始终启用局域网模式（自动检测局域网 IP）                     |
| `PORTLESS_LAN_IP`     | 为局域网模式固定特定 IP 地址                                             |
| `PORTLESS_TLD`        | 使用一个或多个 TLD，单段或多段（例如 localhost、dev.example.com） |
| `PORTLESS_WILDCARD`   | 设置为 `1` 以允许未注册的子域回退到父级                                     |
| `PORTLESS_SYNC_HOSTS` | 设置为 `0` 以禁用自动同步 /etc/hosts（默认启用）                  |
| `PORTLESS_TAILSCALE`  | 设置为 `1` 以在您的 Tailscale 网络上共享应用（与 `--tailscale` 相同）     |
| `PORTLESS_FUNNEL`     | 设置为 `1` 以通过 Tailscale Funnel 公开应用（与 `--funnel` 相同）    |
| `PORTLESS_NGROK`      | 设置为 `1` 以通过 ngrok 公开应用（与 `--ngrok` 相同）                |
| `PORTLESS_STATE_DIR`  | 覆盖状态目录                                                           |
| `PORTLESS=0`          | 跳过代理，直接运行命令                                                 |

### HTTP/2 + HTTPS

默认启用带有 HTTP/2 的 HTTPS（对于具有许多文件的开发服务器，页面加载更快）。WebSocket 通过 HTTP/1.1（Upgrade）和 HTTP/2（RFC 8441 扩展 CONNECT）工作，因此开发服务器 HMR 可以通过代理工作。第一次运行会生成本地 CA 并将其添加到系统信任存储。之后，不再需要提示，也不需要浏览器警告。

```bash
portless proxy start --cert ./c.pem --key ./k.pem  # 使用自定义证书
portless proxy start --no-tls                       # 禁用 HTTPS（纯 HTTP）
portless trust                                      # 后续添加 CA 到信任存储
```

在 Linux 上，`portless trust` 支持 Debian/Ubuntu、Arch、Fedora/RHEL/CentOS 和 openSUSE（通过 `update-ca-certificates` 或 `update-ca-trust`）。在 Windows 上，它使用 `certutil` 将 CA 添加到系统信任存储。在 WSL 上，它会更新 Linux 信任存储和 Windows 当前用户 Root 存储，以便 Windows 浏览器信任 portless HTTPS 证书。

### 局域网模式

```bash
portless proxy start --lan
portless proxy start --lan --https
portless proxy start --lan --ip 192.168.1.42
```

`--lan` 明确地将代理绑定到 IPv4 和 IPv6 未指定地址，`0.0.0.0` 和 `::`，并宣传 `<名称>.local` 主机名，以便同一 Wi-Fi 上的设备可以访问您的应用。Portless 自动检测您的局域网 IP 并自动遵循网络更改，但您可以使用 `--ip <地址>` 或 `PORTLESS_LAN_IP` 环境变量固定特定地址。设置 `PORTLESS_LAN=1` 以每次代理启动时默认为局域网模式。

Portless 通过 `proxy.lan` 记住局域网模式，因此如果您停止一个局域网代理并重新启动，它将保持在局域网模式。所有代理设置（端口、TLS、TLD、局域网）在自动启动时都会保留并重用，除非被显式标志或环境变量覆盖。使用 `PORTLESS_LAN=0` 对于一次启动以切换回 `.localhost` 模式。如果代理已经以不同的显式局域网/TLS/TLD 设置运行，portless 会警告您并要求您先停止它。

局域网模式依赖于 portless 启动系统 mDNS 帮助程序：macOS 包括 `dns-sd`，而 Linux 使用 `avahi-publish-address` 从 `avahi-utils`（通过 `sudo apt install avahi-utils` 或您的发行版的工具）。

- **Next.js**：将您的 `.local` 主机名添加到 `allowedDevOrigins`：

  ```js
  // next.config.js
  module.exports = {
    allowedDevOrigins: ["myapp.local", "*.myapp.local"],
  };
  ```

- **Expo / React Native**：portless 始终注入 `--port`。React Native 还会获得 `--host 127.0.0.1`。Expo 在局域网模式外获得 `--host localhost`，但在局域网模式下，portless 会保留 Metro 的默认局域网主机行为，而不是强制 `--host` 或 `HOST`。

### Tailscale 共享

使用 `--tailscale` 在您的 Tailscale 网络上与队友共享开发服务器，或使用 `--funnel` 向公共互联网公开：

```bash
portless myapp --tailscale next dev
# -> https://myapp.localhost           (本地)
# -> https://devbox.yourteam.ts.net    (tailnet)

portless myapp --funnel next dev
# -> https://myapp.localhost           (本地)
# -> https://devbox.yourteam.ts.net    (公共互联网)
```

在使用 `--tailscale` 或 `--funnel` 之前，必须启用 Tailscale HTTPS 证书才能注册 HTTPS URL。`--funnel` 还必须在 tailnet 和节点上启用才能注册公共 URL。如果任何设置缺失，portless 会在启动子进程之前退出。

每个 `--tailscale` 应用都根挂载在其自己的 Tailscale HTTPS 端口（443，然后 8443，8444 等），因此不需要框架 `basePath` 配置。设置 `PORTLESS_TAILSCALE=1` 以默认共享每个应用。`portless list` 显示本地和 tailnet URL。Tailscale serve 注册会在应用退出时清理。需要安装 `tailscale` CLI 并连接，并启用 Tailscale HTTPS 证书。

### ngrok 共享

使用 `--ngrok` 通过 ngrok 公开开发服务器：

```bash
portless myapp --ngrok next dev
# -> https://myapp.localhost           (本地)
# -> https://abc123.ngrok.app          (公共互联网)
```

设置 `PORTLESS_NGROK=1` 以在 portless 运行应用时默认启用 ngrok。`portless list` 显示本地和 ngrok URL。ngrok 隧道会在应用退出时清理。需要安装 `ngrok` CLI 并使用 `ngrok config add-authtoken <token>` 进行身份验证。

服务默认使用无端口模式，除非提供安装选项或 `PORTLESS_*` 环境变量：443 端口的 HTTPS，使用 `.localhost` 域名。`service install` 接受代理选项，包括 `--port`、`--no-tls`、`--lan`、`--ip`、`--tld`、`--wildcard`、`--cert` 和 `--key`。使用 `--state-dir <路径>` 或 `PORTLESS_STATE_DIR=<路径>` 来选择服务状态和日志的存储位置。

选择的服务配置会写入 launchd、systemd 或任务计划程序，并在重启后重用。`portless service status` 报告已安装的端口、HTTPS 模式、TLD、LAN 模式、通配符模式和状态目录。macOS 和 Linux 安装一个以 root 身份运行的服务，以便 443 端口可以在启动时绑定。Windows 安装一个任务计划程序启动任务，以 SYSTEM 身份运行。安装和删除可能需要管理员权限。`portless clean` 会自动删除服务。

## CLI 参考

| 命令                                           | 描述                                                    |
| ------------------------------------------------- | -------------------------------------------------------------- |
| `portless`                                        | 通过代理运行 dev 脚本                                   |
| `portless`                                        | 从单体仓库根目录：运行所有工作区包                     |
| `portless --script <名称>`                        | 运行特定的 package.json 脚本（默认：dev）              |
| `portless run [cmd] [args...]`                    | 从项目名推断，通过代理运行（自动启动）                 |
| `portless run --name <名称> <cmd>`                | 覆盖推断的基本名称（工作区前缀仍然适用）                |
| `portless <名称> <cmd> [args...]`                 | 在 `https://<名称>.localhost` 运行应用（自动启动代理）      |
| `portless get <名称>`                             | 打印服务的 URL（用于跨服务连接）                       |
| `portless get <名称> --no-worktree`               | 不带工作区前缀打印 URL                                  |
| `portless list`                                   | 显示活动路由                                             |
| `portless doctor`                                 | 检查代理、路由、DNS、CA 信任和 LAN 前提条件              |
| `portless trust`                                  | 将本地 CA 添加到系统信任存储（用于 HTTPS）                 |
| `portless clean`                                  | 删除状态、CA 信任条目和 `/etc/hosts` 块             |
| `portless prune`                                  | 杀死来自崩溃会话的无主开发服务器                    |
| `portless prune --force`                          | 用 SIGKILL 而不是 SIGTERM 杀死孤儿                   |
| `portless proxy start`                            | 以守护进程方式启动 HTTPS 代理（端口 443，自动提升权限）        |
| `portless proxy start --no-tls`                   | 不使用 HTTPS（端口 80 上的普通 HTTP）                    |
| `portless proxy start --lan`                      | 以 LAN 模式启动（mDNS `.local`，自动跟随 LAN IP 变化） |
| `portless proxy start -p <数字>`                | 在自定义端口启动代理                               |
| `portless proxy start --tld test`                 | 使用 .test 而不是 .localhost                                |
| `portless proxy start --tld localhost --tld test` | 从一个代理服务两个 TLDs                                 |
| `portless proxy start --tld dev.example.com`      | 使用多段 TLD 用于生产一致性 URL             |
| `portless proxy start --foreground`               | 以前台方式启动代理（用于调试）                  |
| `portless proxy start --wildcard`                 | 允许未注册的子域名回退到父路由                       |
| `portless proxy stop`                             | 停止代理                                                 |
| `portless service install`                        | 在操作系统启动时启动 HTTPS 代理                       |
| `portless service install --lan`                  | 以 LAN 模式启动服务                                  |
| `portless service install --wildcard`             | 在启动服务中持久化通配符路由                         |
| `portless service status`                         | 显示服务和代理状态                                  |
| `portless service uninstall`                      | 删除启动服务                                     |
| `portless alias <名称> <端口>`                    | 注册静态路由（例如，用于 Docker 容器）           |
| `portless alias <名称> <端口> --force`            | 覆盖现有路由                                    |
| `portless alias --remove <名称>`                  | 删除静态路由                                          |
| `portless hosts sync`                             | 与 `/etc/hosts` 一致化路由（修复 Safari）                |
| `portless hosts clean`                            | 从 `/etc/hosts` 删除 portless 条目                        |
| `portless <名称> --app-port <n> <cmd>`            | 使用固定端口而不是自动分配运行应用                |
| `portless <名称> --tailscale <cmd>`               | 在您的 Tailscale 网络上共享应用（tailnet）              |
| `portless <名称> --funnel <cmd>`                  | 通过 Tailscale Funnel 公开共享应用                    |
| `portless <名称> --ngrok <cmd>`                   | 通过 ngrok 公开共享应用                               |
| `portless <名称> --force <cmd>`                   | 杀死现有进程并接管其路由                          |
| `portless --name <名称> <cmd>`                    | 强制 `<名称>` 作为应用名称（绕过子命令分派）      |
| `portless <名称> -- <cmd> [args...]`              | 停止标志解析；`--` 之后的所有内容都传递给子进程    |
| `portless --help` / `-h`                          | 显示帮助                                                      |
| `portless run --help`                             | 显示子命令的帮助（也适用于 alias、hosts、clean）         |
| `portless --version` / `-v`                       | 显示版本                                                   |

**保留名称：** `run`、`get`、`alias`、`hosts`、`list`、`doctor`、`trust`、`clean`、`prune`、`proxy` 和 `service` 是子命令，不能直接用作应用名称。使用 `portless run <cmd>` 推断名称，或使用 `portless --name <名称> <cmd>` 强制任何名称，包括保留名称。

## portless.json

可选配置文件。Portless 在当前目录中查找它。

| 字段     | 类型    | 默认                    | 描述                                              |
| --------- | ------- | -------------------------- | -------------------------------------------------------- |
| `name`    | string  | inferred from package.json | 基本应用名称（工作区前缀仍然适用）            |
| `script`  | string  | `"dev"`                    | 要运行的 package.json 脚本名称                     |
| `appPort` | number  | auto-assigned              | 子进程的固定端口                         |
| `proxy`   | boolean | auto-detected              | 是否通过代理路由（`false` 对于任务）   |
| `apps`    | object  |                            | 工作区包的覆盖，按相对路径键值对             |
| `turbo`   | boolean | `true`                     | 设置 `false` 以使用直接启动而不是 turborepo  |

每个 `apps` 条目具有相同的形状（`name`、`script`、`appPort`、`proxy`）。当 `apps` 存在时，顶层字段仅在单应用模式下适用。

### package.json "portless" 键

而不是单独的 `portless.json`，您可以将 `"portless"` 键添加到您的 `package.json`。字符串值是设置名称的简写：

```json
{ "portless": "myapp" }
```

对象支持所有每个应用的字段（`name`、`script`、`appPort`、`proxy`）：

```json
{ "portless": { "name": "myapp", "script": "dev:app" } }
```

优先级（最近者胜出）：CLI 标志 > package.json `"portless"` 键 > portless.json 应用条目 > 默认。

## 故障排除

### 运行诊断

当本地路由或 HTTPS 行为看起来不正确时，首先使用 `portless doctor`。它是只读的，并检查 Node.js、状态目录权限、代理活动性、路由条目、主机名解析、本地 CA 信任和 LAN 模式前提条件。

### 代理未运行

当您使用 `portless <名称> <cmd>` 运行应用时，代理会自动启动。如果它没有启动（例如，端口冲突），请手动启动它：

```bash
portless proxy start
```

### 端口已被使用

另一个进程绑定到代理端口。要么先停止它，要么使用不同的端口：

```bash
portless proxy start -p 8080
```

### 框架不尊重 PORT

Portless 自动注入正确的 `--port` 标志，并在需要时注入匹配的 `--host` 标志，用于忽略 `PORT` 环境变量的框架：**Vite**、**VitePlus** (`vp`)、**Astro**、**React Router**、**Angular**、**Expo** 和 **React Native**。SvelteKit 内部使用 Vite，并自动处理。注入通过以框架或已知运行器开头的命令开始的包脚本传递，并且仅针对框架的服务器命令（`dev`、`serve`、`preview`、`start` 或裸 `vite`）—— `vite build`、`vite optimize`、`vp test` 和其他非服务命令拒绝标志，因此它们保持不变，portless 无法分类的任何调用（`vp --mode dev build`）也是如此。它还跳过复合命令（`&&`、`|`、`;`）、尾随 `#` 注释、自己的 `--` 选项终止符、环境前缀（`NODE_ENV=production vite`）、委托给其他脚本以及脚本名称之前的运行器标志（`bun run --bun dev`）—— 每个都保持自己的端口，应用返回 502，因此请自行在脚本中设置端口。

对于其他不读取 `PORT` 的框架，手动传递端口：

- **Webpack Dev Server**：使用 `--port $PORT`
- **自定义服务器**：读取 `process.env.PORT` 并在其上监听

### 权限错误

默认端口（HTTP 为 80，HTTPS 为 443）在 macOS 和 Linux 上需要 `sudo`。Portless 在需要时自动使用 sudo 提升权限。如果 sudo 不可用，它会回退到端口 1355（无需 sudo）。在 Windows 上，不需要提升权限。

```bash
portless proxy start --https           # Auto-elevates with sudo for port 443
portless proxy start -p 1355 --https   # No sudo needed (URLs include :1355)
portless proxy stop                    # Stop (use sudo if started with sudo)
```

### Safari 无法找到 .localhost URL

Safari 依赖于系统 DNS 解析器来解析 `.localhost` 子域，这在所有 macOS 配置中可能无法解析。Chrome、Firefox 和 Edge 具有内置处理。

修复：

```bash
portless hosts sync    # Reconcile current routes with /etc/hosts
portless hosts clean   # Remove entries later
```

默认情况下自动同步 `/etc/hosts` 对于路由主机名。设置 `PORTLESS_SYNC_HOSTS=0` 以禁用。如果路由主机名无法解析，注册它的命令会警告并指向 `portless hosts sync`。

手动同步使 portless 管理的条目与当前路由一致，并在没有路由时删除过时的条目。它需要在写入之前成功读取 hosts 文件，并验证每个写入。读取或验证失败将遵循正常的同步错误路径。

### 浏览器显示 --https 的证书警告

本地 CA 可能尚未受信任。运行：

```bash
portless trust
```

这将 portless 本地 CA 添加到您的系统信任存储。之后，重启浏览器。

### 从机器中删除 portless

```bash
portless clean
```

如果需要，停止代理，从信任存储中删除 portless CA（如果 portless 添加了它），删除状态目录下的已知文件，并删除 portless `/etc/hosts` 块。在 macOS/Linux 上可能需要 `sudo`。如果信任存储删除失败，portless 会保留其 CA 证书和密钥，以便稍后的 `portless clean` 可以安全重试。

### 代理循环（508 Loop Detected）

如果您的开发服务器将请求代理到另一个 portless 应用（例如，Vite 代理 `/api` 到 `api.myapp.localhost`），代理必须重写 `Host` 标头。如果没有这样做，portless 会将请求路由回原始应用，创建无限循环。

修复：在代理配置中设置 `changeOrigin: true`（Vite、webpack-dev-server 等）：

```ts
// vite.config.ts
proxy: {
  "/api": {
    target: "https://api.myapp.localhost",
    changeOrigin: true,
    ws: true,
  },
}
```

Portless 自动在子进程中设置 `NODE_EXTRA_CA_CERTS`，以便 Node.js 信任 portless CA。如果您在 portless 外部运行单独的 Node.js 进程，请手动指向 CA：`NODE_EXTRA_CA_CERTS=~/.portless/ca.pem`。或者，使用 `--no-tls` 对于普通 HTTP。

### Tailscale 不工作

如果 `--tailscale` 或 `--funnel` 失败：

```bash
tailscale status     # 检查是否连接
tailscale up         # 连接到您的 tailnet
```

需要安装 Tailscale CLI（https://tailscale.com/download）并将其放在 PATH 中。

### ngrok 不工作

如果 `--ngrok` 失败：

```bash
ngrok version                         # 检查是否安装
ngrok config add-authtoken <token>    # 配置身份验证
```

需要安装 ngrok CLI（https://ngrok.com/download）并将其放在 PATH 中。

### 要求

- Node.js 24+
- macOS、Linux 或 Windows
- `openssl`（用于 `--https` 证书生成；macOS 和大多数 Linux 发行版随附；在 Windows 上，通过 `winget install -e --id ShiningLight.OpenSSL.Dev` 安装或使用 Git for Windows 随附的副本）
- `tailscale` CLI（可选，用于 `--tailscale` 和 `--funnel）
- `ngrok` CLI（可选，用于 `--ngrok`）
