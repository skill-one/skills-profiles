# 无端口

将端口编号替换为稳定的、命名的 .localhost URL。为人类和代理。

## 为什么无端口

- **端口冲突**：两个项目默认使用相同端口时出现 `EADDRINUSE`
- **记忆端口**：哪个应用程序在 3001 上而不是 8080？
- **刷新显示错误的应用程序**：停止一个服务器，在同一端口上启动另一个，陈旧的标签显示错误的内容
- **单体仓库倍增器**：每个仓库中的每个服务都会放大每个问题
- **代理测试错误端口**：AI 代理猜测或硬编码错误的端口
- **Cookie/存储冲突**：`localhost` 上的 cookie 跨应用程序传播；端口更改时 localStorage 丢失
- **配置中硬编码端口**：CORS 允许列表、OAuth 重定向、`.env` 文件在端口更改时中断
- **与队友共享 URL**："那个端口是什么？" 变成一个 Slack 问题
- **浏览器历史记录无用**：`localhost:3000` 历史记录是多个不相关项目的混合

## 安装

建议全局安装，或作为项目开发依赖项安装。**不要**使用 `npx` 或 `pnpm dlx` 进行一次性执行。

```bash
# 全局（可在任何地方使用）
npm install -g portless

# 或作为项目开发依赖项
npm install -D portless
```

当按项目安装时，通过 `package.json` 脚本或 `npx portless` 调用（由于包是本地的，npx 不会下载任何内容）。

## 快速入门

```bash
# 安装全局（或添加 -D 到项目）
npm install -g portless

# 运行您的应用程序（自动在端口 443 上启动 HTTPS 代理）
portless run next dev
# -> https://<project>.localhost

# 或使用显式名称
portless myapp next dev
# -> https://myapp.localhost
```

代理在您运行应用程序时自动启动。您也可以使用 `portless proxy start` 明确启动它。自动启动会重用最近代理运行时的配置（端口、TLS、TLD），因此重启或重新启动不会静默恢复为默认值。显式环境变量始终优先。

在非交互式环境中（没有 TTY，或 `CI=1`），portless 会显示描述性错误而不是提示。像 turborepo 这样的任务运行器应该预先启动代理。

## 集成模式

### 无配置（推荐）

裸 `portless` 开箱即用。它通过代理运行 `package.json` 中的 `"dev"` 脚本，并从包名、git 根或目录中推断应用程序名称：

```bash
portless        # -> 运行 "dev" 脚本，https://<project>.localhost
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

仓库根目录有一个 `portless.json`。Portless 从 `pnpm-workspace.yaml` 发现包，或从 `package.json` 中的 `"workspaces"` 字段（npm、yarn、bun）发现：

```json
{
  "apps": {
    "apps/web": { "name": "myapp" },
    "apps/api": { "name": "api.myapp" }
  }
}
```

```bash
portless                  # 从仓库根目录：启动所有具有 "dev" 脚本的服务
cd apps/web && portless   # 启动单个包
portless --script start   # 运行 "start" 而不是 "dev"
```

`apps` 映射是可选的，仅提供名称覆盖。未列出的包会自动发现并推断名称。

没有 `apps` 映射时，主机名遵循 `<package>.<project>.localhost`。项目名称来自最常见的 npm 范围（例如 `@myorg/web` 和 `@myorg/api` 产生 `myorg`），如果项目名称与项目名称匹配，则使用 `<project>.localhost`。

### Turborepo

对于 turborepo 项目，将 portless 作为 `dev` 脚本使用，而真实命令在单独的脚本中：

```json
{
  "scripts": { "dev": "portless", "dev:app": "next dev" },
  "portless": { "name": "myapp", "script": "dev:app" }
}
```

`pnpm dev` 运行 turbo，它在每个包中运行 portless。Portless 检测包管理器并通过代理运行 `pnpm run dev:app`。

当 portless 从工作区根目录运行时，它使用现有的 Turbo 集成来保留任务顺序，当 `turbo.json` 或 `turbo.jsonc` 可读时。在根 portless 配置中设置 `"turbo": false` 以使用直接启动而不是 turborepo。

### package.json 脚本

您仍然可以直接在脚本中使用 portless：

```json
{
  "scripts": {
    "dev": "portless run next dev"
  }
}
```

代理在您运行应用程序时自动启动。或者显式启动：`portless proxy start`。

### 带子域的多应用程序设置

```bash
portless myapp next dev          # https://myapp.localhost
portless api.myapp pnpm start    # https://api.myapp.localhost
portless docs.myapp next dev     # https://docs.myapp.localhost
```

默认情况下，仅明确注册的子域会被路由（严格模式）。使用 `--wildcard` 启动代理以允许任何注册路由的子域回退到该应用程序（例如 `tenant1.myapp.localhost` 路由到 `myapp` 应用程序）。精确匹配始终优先于通配符。

### Git 工作树

`portless run` 自动检测 git 工作树。在一个链接工作树中，分支名称作为子域前缀添加，以便每个工作树都有一个唯一的 URL：

```bash
# 主工作树（无前缀）
portless run next dev   # -> https://myapp.localhost

# 链接工作树在 "fix-ui" 分支上
portless run next dev   # -> https://fix-ui.myapp.localhost
```

无需配置更改。将 `portless run` 放在 `package.json` 中一次，它就会在所有工作树中工作。

### 绕过 portless

设置 `PORTLESS=0` 以直接运行命令而不使用代理：

```bash
PORTLESS=0 pnpm dev   # 绕过代理，使用默认端口
```

当代理命令使用 Ctrl+C 停止时，portless 会等待其进程树退出。第二个 Ctrl+C 会转发另一个中断，并在短暂的宽限期后终止剩余的后代。

## 工作原理

1. `portless proxy start` 在端口 443 上启动 HTTPS 反向代理作为后台守护程序。在 macOS/Linux 上自动提升权限；如果无法使用 sudo，则回退到端口 1355。使用 `--no-tls` 在端口 80 上使用纯 HTTP。使用 `-p` / `--port` 或 `PORTLESS_PORT` 环境变量进行配置。当您运行应用程序时，代理也会自动启动。
2. `portless <name> <cmd>` 通过 `PORT` 环境变量分配一个随机空闲端口（4000-4999）并将应用程序注册到代理
3. 浏览器访问 `https://<name>.localhost`；代理转发到应用程序的分配端口

在局域网模式下，代理及其 HTTP 重定向监听器仅绑定到 IPv4 和 IPv6 环回地址，`127.0.0.1` 和 `::1`。它们不接受通过局域网、VPN 或其他网络接口的连接。

`.localhost` 域名在 Chrome、Firefox 和 Edge 中原生解析为 `127.0.0.1`。Safari 依赖于系统 DNS 解析器，它可能无法处理所有配置中的 `.localhost` 子域。如果需要，运行 `portless hosts sync` 将条目添加到 `/etc/hosts`。

使用 `portless proxy start --tld localhost --tld test` 从一个代理在多个 TLD 下为同一应用程序提供服务。`PORTLESS_URL` 使用第一个配置的 TLD。当配置的 TLD 重叠时（例如 `example.com` 和 `dev.example.com`），主机名会根据最长的 TLD 首先匹配，而不管配置顺序如何。`PORTLESS_TLD` 接受相同的逗号分隔列表格式，例如 `PORTLESS_TLD=localhost,test`。

TLD 可以是多段 DNS 名称，例如 `dev.example.com`，因此本地 URL 可以镜像生产结构（`myapp.dev.example.com`）。每个标签都遵循 DNS 规则：小写字母、数字、内部连字符、每个标签 63 个字符、总共 253 个字符。严格的 OAuth 提供商拒绝 `.localhost` 重定向 URI 接受像 `https://myapp.dev.example.com/api/auth/callback/google` 这样的真实域名。

大多数框架（Next.js、Express、Nuxt 等）会自动尊重 `PORT` 环境变量。对于忽略 `PORT` 的框架（Vite、VitePlus、Astro、React Router、Angular、Expo、React Native），portless 会自动注入正确的 `--port` 标志，并在需要时注入匹配的 `--host` CLI 标志。注入通过以框架或已知运行器开头的包脚本实现，并且仅针对框架的服务器命令（`dev`、`serve`、`preview`、`start` 或裸 `vite`）；`vite build`、`vite optimize`、`vp test` 或 `astro check` 等不提供服务的命令会拒绝标志，因此它们保持不变，任何 portless 无法分类的脚本也是如此：复合命令（`&&`、`|`、`;`）、尾随 `#` 评论、自己的 `--` 选项终止符、环境前缀（`NODE_ENV=production vite`）、委托给另一个脚本或脚本名称之前的运行器标志——每个这些都保持自己的端口，因此您需要自己在脚本中设置端口。

对于其他不读取 `PORT` 的框架，手动传递端口：

- **Webpack Dev Server**：使用 `--port $PORT`
- **自定义服务器**：读取 `process.env.PORT` 并在其上监听

### 状态目录

Portless 将其状态（路由、PID 文件、端口文件）存储在 `~/.portless` 中。当代理使用 sudo 运行时，这仍然是调用用户的家目录，因此无特权的应用程序和代理共享路由注册。使用 `PORTLESS_STATE_DIR` 环境变量覆盖。

### 环境变量

| 变量              | 描述                                                                    |
| --------------------- | ------------------------------------------------------------------------------ |
| `PORTLESS_PORT`       | 覆盖默认代理端口（默认：443 带有 HTTPS，80 无）          |
| `PORTLESS_APP_PORT`   | 为应用程序使用固定端口（跳过自动分配）                            |
| `PORTLESS_HTTPS`      | 默认启用 HTTPS；设置为 `0` 以禁用（与 `--no-tls` 相同）                |
| `PORTLESS_LAN`        | 设置为 `1` 以始终启用局域网模式（自动检测局域网 IP）                     |
| `PORTLESS_LAN_IP`     | 固定特定局域网 IP 用于局域网模式                                             |
| `PORTLESS_TLD`        | 使用一个或多个 TLD，单段或多段（例如 localhost,dev.example.com） |
| `PORTLESS_WILDCARD`   | 设置为 `1` 以允许未注册的子域回退到父级             |
| `PORTLESS_SYNC_HOSTS` | 设置为 `0` 以禁用自动同步 /etc/hosts（默认启用）                  |
| `PORTLESS_TAILSCALE`  | 设置为 `1` 以通过 Tailscale 网络共享应用程序（与 `--tailscale` 相同）     |
| `PORTLESS_FUNNEL`     | 设置为 `1` 以通过 Tailscale Funnel 公开应用程序（与 `--funnel` 相同）    |
| `PORTLESS_NGROK`      | 设置为 `1` 以通过 ngrok 公开应用程序（与 `--ngrok` 相同）                |
| `PORTLESS_STATE_DIR`  | 覆盖状态目录                                                   |
| `PORTLESS=0`          | 绕过代理，直接运行命令                                             |

### HTTP/2 + HTTPS

默认情况下启用带有 HTTP/2 的 HTTPS（对于具有许多文件的开发服务器，页面加载更快）。WebSockets 通过 HTTP/1.1（Upgrade）和 HTTP/2（RFC 8441 扩展 CONNECT）工作，因此开发服务器 HMR 可以通过代理工作。第一次运行会生成本地 CA 并将其添加到系统信任存储中。之后，不再提示，浏览器也不会显示警告。

```bash
portless proxy start --cert ./c.pem --key ./k.pem  # 使用自定义证书
portless proxy start --no-tls                       # 禁用 HTTPS（纯 HTTP）
portless trust                                      # 之后添加 CA 到信任存储
```

在 Linux 上，`portless trust` 支持 Debian/Ubuntu、Arch、Fedora/RHEL/CentOS 和 openSUSE（通过 `update-ca-certificates` 或 `update-ca-trust`）。在 Windows 上，它使用 `certutil` 将 CA 添加到系统信任存储中。在 WSL 上，它更新 Linux 信任存储和 Windows 当前用户根存储，以便 Windows 浏览器信任 portless HTTPS 证书。

### 局域网模式

```bash
portless proxy start --lan
portless proxy start --lan --https
portless proxy start --lan --ip 192.168.1.42
```

`--lan` 明确绑定代理到 IPv4 和 IPv6 未指定地址，`0.0.0.0` 和 `::`，并使用 mDNS 广播 `<name>.local` 主机名，以便同一 Wi-Fi 上的设备可以访问您的应用程序。Portless 自动检测您的局域网 IP 并自动跟踪网络更改，但您可以使用 `--ip <address>` 或 `PORTLESS_LAN_IP` 环境变量固定特定地址。设置 `PORTLESS_LAN=1` 以在代理每次启动时默认为局域网模式。

Portless 通过 `proxy.lan` 记住局域网模式，因此如果您停止一个局域网代理并再次启动，它将保持在局域网模式。所有代理设置（端口、TLS、TLD、LAN）在自动启动时都会保留并重用，除非被显式标志或环境变量覆盖。使用 `PORTLESS_LAN=0` 为一次启动切换回 `.localhost` 模式。如果代理已经使用不同的显式局域网/TLS/TLD 设置运行，portless 会警告您并要求您首先停止它。

局域网模式依赖于 portless 启动系统 mDNS 帮助程序：macOS 包括 `dns-sd`，而 Linux 使用 `avahi-publish-address` 从 `avahi-utils`（通过 `sudo apt install avahi-utils` 或您的发行版的工具）。

- **Next.js**: 将您的 `.local` 主机名添加到 `allowedDevOrigins`:

  ```js
  // next.config.js
  module.exports = {
    allowedDevOrigins: ["myapp.local", "*.myapp.local"],
  };
  ```

- **Expo / React Native**: portless 始终注入 `--port`。React Native 还会获得 `--host 127.0.0.1`。Expo 在局域网模式外获得 `--host localhost`，但在局域网模式下，portless 会保留 Metro 的默认局域网主机行为，而不是强制 `--host` 或 `HOST`。

### Tailscale 共享

使用 `--tailscale` 与您 Tailscale 网络上的队友共享开发服务器，或使用 `--funnel` 向公共互联网公开：

```bash
portless myapp --tailscale next dev
# -> https://myapp.localhost           (本地)
# -> https://devbox.yourteam.ts.net    (tailnet)

portless myapp --funnel next dev
# -> https://myapp.localhost           (本地)
# -> https://devbox.yourteam.ts.net    (公共互联网)
```

Tailscale HTTPS 证书必须在 `--tailscale` 或 `--funnel` 可以注册 HTTPS URL 之前启用。Funnel 也必须在 tailnet 和节点上启用才能注册公共 URL。如果任何设置缺失，portless 在启动子进程之前会退出。

每个 `--tailscale` 应用程序都在其自己的 Tailscale HTTPS 端口（443，然后 8443，8444 等）上根挂载，因此无需框架 `basePath` 配置。设置 `PORTLESS_TAILSCALE=1` 以默认共享每个应用程序。`portless list` 显示本地和 tailnet URL。Tailscale serve 注册在应用程序退出时清理。需要安装 `tailscale` CLI（https://tailscale.com/download）并在 PATH 上。
