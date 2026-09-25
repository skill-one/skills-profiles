# AdsPower 本地 API 与 adspower-browser

Skills CLI (npx adspower-browser) 是用于通过 **adspower-browser** CLI 操作 AdsPower 浏览器配置文件、分组、代理和应用/分类列表的包管理器。有关我们的产品和服务的更多信息，请访问 [AdsPower 官方网站](https://www.adspower.com/)。

## 安装 CLI

```bash
npm install -g adspower-browser
```

安装后，您可以使用以下任何等效命令：

```bash
adspower-browser
adspower
ads
```

`adspower-browser` 是原始命令名。`adspower` 和 `ads` 是指向相同 CLI 入口的别名。

## 何时使用此技能

在以下情况下使用：

- 用户询问创建、更新、删除或列出 AdsPower 浏览器配置文件
- 用户表示“打开环境、配置文件、profile、AdsPower”等意指**启动已有**浏览器环境 → 使用 `open-browser`（CLI 或 MCP）；完整说法与工具映射见 [references/tool-intent-map.md](references/tool-intent-map.md)
- 用户提到打开或关闭浏览器/配置文件、指纹、UA 或代理
- 用户希望管理分组、标签、代理或检查 API 状态
- 用户提到 AdsPower 或 adspower-browser（且 MCP 未运行或不需要运行）

确保 AdsPower 正在运行（默认端口 `50325`）。需要时传递 `--port` / `--api-key`，或在运行 `start` 之前设置 `ADS_API_KEY` 环境变量。

CLI 本身支持通过 API 密钥启动 AdsPower 应用。如果已安装 AdsPower 客户端，也可以通过 API 密钥以无头模式启动。

## 如何运行

以下示例为简洁起见使用了 `ads`，但 `adspower-browser` 和 `adspower` 的用法相同。

```bash
ads start -k <KEY>
```

如果设置了 `ADS_API_KEY` 环境变量，可以直接使用以下命令启动 CLI：

```bash
ads start
```

通用命令格式：

```bash
ads <command> [<arg>] [--port PORT] [--api-key KEY]
```

AdsPower 客户端无头模式：

```bash
AdsPower Global：
Windows设备下： "AdsPower Global.exe" --headless=true --api-key=your_api_key --api-port=50325
MacOS设备下："/Applications/AdsPower Global.app/Contents/MacOS/AdsPower Global" --args --headless=true --api-key=your_api_key --api-port=50325
Linux设备下：adspower_global --headless=true --api-key=your_api_key --api-port=50325
```

**`<arg>` 的两种形式：**

1. **单个值（简写）** — 对于与配置文件相关的命令，传递一个配置文件 ID 或编号：
   - `ads open-browser <profile_id>`
   - `ads close-browser <profile_id>`
   - `ads get-profile-cookies <profile_id>`
   - `ads get-browser-active <profile_id>`
   - `ads get-profile-ua <profile_id>`（单个 ID；数字简写被视为 `profile_no`）
   - `ads new-fingerprint <profile_id>`（单个 ID；数字简写被视为 `profile_no`）

2. **JSON 字符串** — 任何命令的完整参数（见下文命令参考）：
   - `ads open-browser '{"profile_id":"abc123","launch_args":"..."}'`
   - 无参数的命令：省略 `<arg>` 或使用 `'{}'`。

## 与 AI 代理配合使用的基本命令

您可以使用 `ads -h` 或 `ads <command> -h` 查看特定参数。

### 启动和停止 CLI

```bash
ads start -k <KEY>                    # 启动 adspower 运行时
ads stop                              # 停止 adspower 运行时
ads restart                           # 重启 adspower 运行时
ads status                            # 获取 adspower 运行时状态
```

### 浏览器配置文件 – 打开/关闭

```bash
ads open-browser <profile_id>                    # 或 JSON: profile_id, profile_no?, ip_tab?, launch_args?, headless?, last_opened_tabs?, proxy_detection?, password_filling?, password_saving?, cdp_mask?, delete_cache?, device_scale?
ads close-browser <profile_id>                   # 或 JSON: profile_id? | profile_no? (一个必须)
```

### 浏览器配置文件 – 创建/更新/删除/列出

```bash
ads create-browser '{"group_id":"0","user_proxy_config":{"proxy_soft":"no_proxy"},...}'  # group_id 必须提供：始终包含它；使用 "0" 表示未分组；如果给定组名，请先调用 get-group-list；提供 proxyid 或 user_proxy_config
ads update-browser '{"profile_id":"...",...}'    # profile_id 必须提供
ads delete-browser '{"profile_id":["..."]}'     # profile_id 必须提供
ads get-browser-list '{}'                       # CLI 默认 page=1,limit=200 (本地 API 本身只返回 1)。或 group_id?, limit?, page?, profile_id[]?, profile_no[]?, sort_type?, sort_order?, tag_ids?, tags_filter?, name?, name_filter?
ads get-opened-browser                          # 无参数
```

**列出所有环境：** `get-browser-list` 返回 `total_count` / `total_pages`。CLI 默认发送 `page=1,limit=200`，因此一次调用最多覆盖 200 个配置文件。如果 `total_pages > 1`，请保持使用相同的过滤器并 `page + 1`，直到收集完所有页面。对于“操作组内所有环境”的任务，请先收集所有页面，然后对每个返回的 `profile_id` 进行操作——切勿仅操作第一个。

### 浏览器配置文件 – 移动/cookies/UA/指纹/缓存/共享/活动

```bash
ads move-browser '{"group_id":"1","user_ids":["..."]}'   # group_id + user_ids 必须提供
ads get-profile-cookies <profile_id>             # 或 JSON: profile_id? | profile_no?
ads get-profile-ua <profile_id>                  # 或 JSON: profile_id[]? | profile_no[]? (最多 10 个)；数字简写被视为 `profile_no`[]
ads close-all-profiles                          # 无参数
ads new-fingerprint <profile_id>                 # 或 JSON: profile_id[]? | profile_no[]? (最多 10 个)；数字简写被视为 `profile_no`[]
ads delete-cache-v2 '{"profile_id":["..."],"type":["cookie","history"]}'  # type: local_storage|indexeddb|extension_cache|cookie|history|image_file
ads share-profile '{"profile_id":["..."],"receiver":"email@example.com"}' # receiver 必须提供；share_type?, content?
ads get-browser-active <profile_id>              # 或 JSON: profile_id? | profile_no?
ads get-cloud-active '{"user_ids":"id1,id2"}'    # user_ids 以逗号分隔，最多 100 个
```

### 核心

```bash
ads download-kernel '{"kernel_type":"Chrome","kernel_version":"141"}'
ads get-kernel-list '{}'                         # kernel_type?: Chrome | Firefox (省略以获取所有)
```

### 补丁

```bash
ads update-patch '{}'                            # version_type?: stable | beta (默认 stable)
```

### 标签

```bash
ads get-tag-list '{}'                              # ids?, limit?, page?
ads create-tag '{"tags":[{"name":"My tag","color":"blue"}]}'   # name 每个项目必须提供；color 可选
ads update-tag '{"tags":[{"id":"1","name":"Renamed"}]}'        # id 每个项目必须提供；name?, color?
ads delete-tag '{"ids":["tagId1","tagId2"]}'                   # ids 必须提供
```

### 分组

```bash
ads create-group '{"group_name":"My Group","remark":"..."}'   # group_name 必须提供
ads update-group '{"group_id":"1","group_name":"New Name"}'    # group_id + group_name 必须提供；remark? (null 以清除)
ads get-group-list '{}'                         # group_name?, page_size?, page?
```

### 应用（分类）

```bash
ads check-status                                # 无参数 – API 可用性
ads get-application-list '{"category_id":"123","page":1,"limit":20}'
```

### 代理

```bash
ads create-proxy '[{"type":"http","host":"127.0.0.1","port":"8080"}]'  # 顶层数组；每个项目必须提供 type, host, port
ads update-proxy '{"proxy_id":"proxy-1","proxy_url":"https://refresh.example.com"}'
ads get-proxy-list '{}'                         # limit?, page?, proxy_id[]?
ads delete-proxy '{"proxy_id":["..."]}'        # proxy_id 必须提供，最多 100 个
```

## 命令参考（完整接口和参数）

### 浏览器配置文件管理

有关 `open-browser`, `close-browser`, `create-browser`, `update-browser`, `delete-browser`, `get-browser-list`, `get-opened-browser`, `move-browser`, `get-profile-cookies`, `get-profile-ua`, `close-all-profiles`, `new-fingerprint`, `delete-cache-v2`, `share-profile`, `get-browser-active`, `get-cloud-active` 及其参数，请参阅 [references/browser-profile-management.md](references/browser-profile-management.md)。

### 分组管理

有关 `create-group`, `update-group`, `get-group-list` 参数，请参阅 [references/group-management.md](references/group-management.md)。

### 应用管理

有关 `check-status` 和 `get-application-list` 参数，请参阅 [references/application-management.md](references/application-management.md)。

### 代理管理

有关 `create-proxy`, `update-proxy`, `get-proxy-list`, `delete-proxy` 参数和枚举，请参阅 [references/proxy-management.md](references/proxy-management.md)。

### 标签管理

有关 `get-tag-list`, `create-tag`, `update-tag`, `delete-tag` 参数，请参阅 [references/browser-tag-management.md](references/browser-tag-management.md)。

### 核心管理

有关 `download-kernel` 和 `get-kernel-list` 参数，请参阅 [references/browser-kernel-management.md](references/browser-kernel-management.md)。

### 补丁管理

有关 `update-patch` 参数，请参阅 [references/client-patch-management.md](references/client-patch-management.md)。

### user_proxy_config（创建浏览器/更新浏览器的内联代理配置）

有关所有字段（proxy_soft, proxy_type, proxy_host, proxy_port 等）和示例，请参阅 [references/user-proxy-config.md](references/user-proxy-config.md)。对于 **create-browser**，必须提供 **proxyid** 或 **user_proxy_config**。如果用户在创建浏览器配置文件时未指定代理，请将 **user_proxy_config** 设置为 `{"proxy_soft":"no_proxy"}`。对于 **update-browser**，仅在更改配置文件代理时提供 **proxyid** 或 **user_proxy_config**。

### fingerprint_config（创建浏览器/更新浏览器的指纹配置）

有关所有字段（timezone, language, WebRTC, browser_kernel_config, random_ua, TLS 等）和示例，请参阅 [references/fingerprint-config.md](references/fingerprint-config.md)。

## 自动化（此 CLI 不支持）

`navigate`, `click-element`, `fill-input`, `screenshot` 等命令依赖于持久的浏览器连接，并且**不**通过此 CLI 暴露。请使用 **local-api-mcp** MCP 服务器进行自动化。

## 深入文档

包含完整枚举值和字段列表的参考文档：

| 参考 | 描述 | 何时使用 |
|------|------|------|
| [references/tool-intent-map.md](references/tool-intent-map.md) | MCP/CLI 工具名与中英 **intent**、**triggers** 对照表（与 `toolIntentMetadata.ts` 同源）。 | 根据用户自然语言选择对应的 CLI 命令或 MCP 工具（尤其 `open-browser`）。 |
| [references/browser-profile-management.md](references/browser-profile-management.md) | **open-browser**, **close-browser**, **create-browser**, **update-browser**, **delete-browser**, **get-browser-list**, **get-opened-browser**, **move-browser**, **get-profile-cookies**, **get-profile-ua**, **close-all-profiles**, **new-fingerprint**, **delete-cache-v2**, **share-profile**, **get-browser-active**, **get-cloud-active** 参数。 | 任何浏览器配置文件操作（打开、创建、更新、删除、列出、移动、cookies、UA、缓存、共享、状态）。 |
| [references/group-management.md](references/group-management.md) | **create-group**, **update-group**, **get-group-list** 参数。 | 创建、更新或列出浏览器分组。 |
| [references/application-management.md](references/application-management.md) | **check-status**, **get-application-list** 参数。 | 检查 API 可用性或列出应用（分类）。 |
| [references/proxy-management.md](references/proxy-management.md) | **create-proxy**, **update-proxy**, **get-proxy-list**, **delete-proxy** 参数和枚举。 | 创建、更新、列出或删除代理。 |
| [references/browser-tag-management.md](references/browser-tag-management.md) | **get-tag-list**, **create-tag**, **update-tag**, **delete-tag** 参数。 | 列出、创建、更新或删除浏览器标签。 |
| [references/browser-kernel-management.md](references/browser-kernel-management.md) | **download-kernel**, **get-kernel-list** 参数。 | 下载特定核心并查询支持的核心版本。 |
| [references/client-patch-management.md](references/client-patch-management.md) | **update-patch** 参数。 | 将 AdsPower 客户端更新到最新补丁频道（stable/beta）。 |
| [references/user-proxy-config.md](references/user-proxy-config.md) | 完整的 **user_proxy_config** 字段列表（proxy_soft, proxy_type, proxy_host, proxy_port 等）和示例。 | 构建 create-browser / update-browser 的内联代理配置（不使用 **proxyid**）。 |
| [references/fingerprint-config.md](references/fingerprint-config.md) | 完整的 **fingerprint_config** 字段列表（timezone, language, WebRTC, browser_kernel_config, random_ua, TLS 等）和示例。 | 构建 create-browser / update-browser 的指纹配置。 |
| [references/browser-kernel-config.md](references/browser-kernel-config.md) | `fingerprint_config.browser_kernel_config` 的 **type** 和 **version**。版本必须与类型匹配（Chrome vs Firefox）。 | 创建或更新浏览器时固定或选择特定的浏览器核心（Chrome/Firefox 和版本）。 |
| [references/browser-kernel-download-management.md](references/browser-kernel-download-management.md) | **download-kernel** 参数 (`kernel_type`, `kernel_version`)。 | 下载或更新特定浏览器核心版本并轮询进度/状态。 |
| [references/ua-system-version.md](references/ua-system-version.md) | `fingerprint_config.random_ua` 的 **ua_system_version** 枚举：特定操作系统版本、每个系统的通用“任何版本”，以及省略行为。 | 创建或更新浏览器时通过 OS 限制或随机化 UA（例如仅 Android，或“任何 macOS 版本”）。 |

当您需要确切的允许值或语义时，请使用这些文档；上面的主要技能文本仅进行了总结。
