# MSW Painter

一个用于将手绘像素艺术精灵注册为精灵资源的流程。**首先调用 `msw-search`，只有在找不到合适的 RUID 时才调用此技能。**

此技能专用于精灵类别。它不处理动画 / 音频 / 头像 / 图集。

Painter 支持**两种像素艺术风格**：**粗像素**（复古，图标/瓦片感）和**枫木卡通**（受 MapleStory 启发，角色/NPC 感）。在编写代码之前选择一个——见下文步骤 2。

---

## 调用时机

| 情况 | 操作 |
|-----------|--------|
| 用户想要一个特定的精灵 | 首先使用 `msw-search`（资源搜索部分，精灵类别） |
| `msw-search` 返回一个匹配意图的 RUID | 直接使用该 RUID。**不要调用 painter。** |
| 没有搜索结果，或者所有结果都不合适 | 调用 painter → 直接创建 |
| 用户明确说 "我需要一个手绘风格的字符/图标" | 直接调用 painter |

---

## 工作流程

1. **选择媒介** — SVG / Canvas / HTML 之一。见下文 "选择媒介"。
2. **选择风格** — `chunky` 或 `maple`。见下文 "选择风格"。
3. **决定大小** — 见 [references/size-guide.md](references/size-guide.md)。默认是 128×128。
4. **编写代码** — 遵循所选风格的规则：
   - `chunky` → [references/style-chunky-pixel.md](references/style-chunky-pixel.md)
   - `maple` → [references/style-maple-cartoon.md](references/style-maple-cartoon.md)
5. **渲染为 PNG** — 运行 `scripts/render.cjs`。
6. **上传资源** — msw-mcp 资源上传工具，两步预签名模式（§5）。如果连接的 MCP 没有上传工具，请要求用户通过 Maker 注册 PNG，然后继续使用他们提供的 RUID（或通过 `msw-search` 定位）。
7. **注册精灵属性** — 上传后立即调用 `asset_update_resource_storage_info`：`filter_mode` / `wrap_mode` / pivot，以及 UI 帧精灵的 9 切片边框。见下文 "步骤 4"。
8. **报告结果** — RUID + 一两句话的描述（包括使用的风格）。实体放置 / 脚本应用不在 painter 的范围内。

---

## 1. 选择媒介

| 媒介 | 推荐用途 | 优势 |
|--------|-----------------|-----------|
| **SVG** | 图标，标志，简单角色，基于形状的像素艺术 | 代码直观，容易放置 1px `<rect>` 点 |
| **Canvas** | 程序化图案，迭代逻辑（循环绘制的纹理 / 噪声） | 通过 JS 编程逻辑生成复杂图案 |
| **HTML** | 可以通过 CSS 快速样式化的组合布局 | 很少使用——SVG/Canvas 通常更适合像素艺术 |

### 最小 SVG 模板

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"
     width="100%" height="100%" preserveAspectRatio="xMidYMid meet"
     style="image-rendering: pixelated;">
  <rect x="6" y="2" width="1" height="1" fill="#4A90D9"/>
  <!-- 用 1px 的 rect 逐个放置点 -->
</svg>
```

> ⚠️ 使用 `width="100%" height="100%"`（**不是**固定像素数）。SVG 元素在其自身的声明大小内绘制在 render.cjs 视口中——如果你硬编码 128 但渲染为 `--width 1024`，SVG 仅填充左上角的 128px，PNG 的其余部分是透明的。`100%` 使 SVG 填充 `--width`/`--height` 指定的任何画布。

### 最小 Canvas 模板

```javascript
// `c`（画布元素）和 `ctx`（2D 上下文）由 render.cjs 自动暴露。
// ctx.imageSmoothingEnabled = false 也会自动应用。
// 重要提示：从 c.width 派生比例，而不是硬编码的常数——否则
// 不同的 --width 会使画布右下角空白。
const GRID = 16;
const scale = c.width / GRID;  // 16×16 逻辑网格 → 画布大小的输出
ctx.fillStyle = '#4A90D9';
ctx.fillRect(6 * scale, 2 * scale, scale, scale);
```

### 最小 HTML 模板

```html
<!doctype html>
<html><body style="margin:0; image-rendering: pixelated;">
  <!-- 你喜欢的任何内容 -->
</body></html>
```

---

## 2. 选择风格

| 风格 | 推荐用途 | 视觉风格 | 逻辑网格 | 轮廓 | 阴影 |
|-------|-----------------|-------------|--------------|---------|---------|
| **`chunky`** | 图标，按钮，瓦片，块，简单道具 | 复古 / 8-bit / NES-SNES | 小 (16×16, 32×32) | 黑色或白色，1px | 2–4 步阶级别，**无**抗锯齿 |
| **`maple`** | 角色，NPC，怪物，可爱的吉祥物 | MapleStory / 故事书 / 卡通 | 较大 (32×32 ~ 128×128) | **Selout**（填充颜色的较暗版本） | 4–6 步阶级别 + **选择性抗锯齿**在轮廓 + 可选 2×2 邻接 |

### 不确定时的默认值

- 图标 / 按钮 / 瓦片 / 块 → **`chunky`**
- 角色 / NPC / 怪物 / 吉祥物 / "可爱"请求 / "画一个史莱姆" → **`maple`**
- 用户说 "复古" / "8-bit" / "NES" / "极简" → **`chunky`**
- 用户说 "MapleStory" / "可爱" / "卡通" / "Q版" / "插图" → **`maple`**

每种风格的完整规则：
- [references/style-chunky-pixel.md](references/style-chunky-pixel.md)
- [references/style-maple-cartoon.md](references/style-maple-cartoon.md)

两种风格共享相同的禁止 API（无曲线 API，无渐变 API，无分数坐标，无 `filter: blur`/`drop-shadow`）。它们在调色板丰富度，轮廓颜色，抗锯齿和工作网格上有所不同。

---

## 3. 尺寸指南（摘要）

| 用途 | 推荐尺寸 |
|-----|------------------|
| 图标 / 按钮 | 48×48 ~ 64×64 |
| 角色 / 物品 / NPC / 怪物 | 96×96 ~ 128×128 |
| 瓦片 / 地板 / 块 | 64×64 ~ 128×128 |
| 背景 / 大对象 | 256×256 或更大（仅在明确请求时） |

默认是 **128×128**。对于特定风格的工 作网格表（chunky 使用较小的逻辑网格，如 16×16；maple 使用较大的网格，如 64×64）和 SD 角色比例，见 [references/size-guide.md](references/size-guide.md)。

> 如果请求的输出**低于 64×64**，`maple` 风格没有足够的像素用于 selout + 抗锯齿 + 脸部特征——要么将输出尺寸增加到 64+，要么切换到 `chunky`。

---

## 4. PNG 渲染 — `render.cjs`

### 一次性依赖安装

```bash
cd scripts && npm ci
```

这会从提交的 `package-lock.json` 安装 `puppeteer`（包括无头 Chromium，约 200MB）。它与其他基础技能依赖分离，因此仅在第一次使用 painter 时运行。

> 🔒 使用 `npm ci`，**不是** `npm install`。`npm ci` 安装 `package-lock.json` 中固定版本，如果锁文件和 `package.json` 不一致则失败——这是 W012 的供应链完整性保证。永远不要手动编辑 `package-lock.json`；如果你需要提升 puppeteer，请在本地运行 `npm install puppeteer@<版本>` 并提交重新生成的锁文件。

### 沙盒和网络安全隔离

`render.cjs` 默认以启用 OS 沙盒的方式运行无头 Chromium，并阻止渲染页面发出的**所有**网络请求。页面还通过 `data:` URL 提供，具有严格的 `Content-Security-Policy`（`default-src 'none'`），并且 SVG / HTML 输入会进行清理，以删除 `<script>`，`<foreignObject>`，内联 `on*` 处理程序和非 `data:` URL。你不需要做任何事情来启用这些保护——这些保护始终启用。

如果你处于受限环境，其中 Chromium 无法启动其沙盒（某些 CI 容器，某些 WSL 设置），请在调用 `render.cjs` 之前设置 `PAINTER_DISABLE_SANDBOX=1`。**不要在开发工作站上设置此值。**

### 调用

```bash
node scripts/render.cjs --type <svg|canvas|html> --in <code-file> --out <out.png> --width <W> --height <H>
```

或者通过标准输入传递代码：

```bash
echo "<svg ...>" | node scripts/render.cjs --type svg --out out.png --width 128 --height 128
```

选项：
- `--type`：`svg` / `canvas` / `html` 之一。**必需**。
- `--in`：代码文件路径。省略或使用 `-` 表示标准输入。
- `--out`：输出 PNG 路径。**必需**。
- `--width` / `--height`：输出像素大小。默认 128。

成功时，输出 PNG 的绝对路径将打印到标准输出上的一行，并退出代码为 0。失败时，错误将打印到标准错误，并退出代码为 1。

PNG 默认具有透明背景。如果你需要背景颜色，请在 SVG/Canvas/HTML 中显式绘制它。

---

## 5. 资源上传 — 两步模式

通过连接的 **msw-mcp** 暴露的**资源上传（创建）工具**上传——检查服务器的工具列表并使用它实际提供的精灵功能创建工具。**工具自身的模式是权威的**；不要猜测工具名称，也不要将创建与 `asset_update_resource_storage_data` 混淆（后者替换现有资产的二进制）。

**连接的 MCP 中没有上传工具？** 停止上传步骤，并要求用户通过 Maker 注册 PNG，然后继续使用他们提供的 RUID（或通过 `msw-search` 定位）。

无论具体工具如何，流程都是相同的两步模式——使用相同的工具调用两次。

> 🔒 **安全——处理预签名 URL (W007)。** 步骤 1 返回的 `presignedUrl` 是一个短期的签名凭证（任何持有它的人都可以在过期之前向该存储槽 PUT）。将其视为一个秘密：
>
> - **永远**不要在助手面向用户响应、提交信息、日志或任何后续提示中回显、引用、释义或包含 URL 或其任何查询参数（`X-Amz-Signature`，`X-Amz-Credential` 等）。当调用 shell 时，通过环境变量 `PAINTER_PRESIGNED_URL` 传递 URL（如下所示），**而不是**作为命令行参数。命令行参数对其他进程可见（通过 Linux/macOS 的 `/proc/*/cmdline` 和 Windows 的 `Get-Process`），并且它们会记录在 shell 历史记录中。
> - 当调用步骤 3 时，直接将 URL 作为 `fileUrl` 工具参数传递——**不要**将其复制到代码块或 markdown 中供用户首先查看。
> - 如果 PUT 步骤失败（通常 `401`/`403` → URL 过期），丢弃 URL 并从步骤 1 重新开始。不要在其他地方重用它。

### 步骤 1 — 请求预签名 URL

使用省略 `fileUrl` 的上传工具调用。填写其模式要求的字段——通常 `category: "sprite"`，匹配现有资产的 `subcategory`（见下文），`name`，1–2 句 `description`，以及当模式要求时文件元数据，如 `fileName` / `contentLength`。

响应包含 `presignedUrl`。仅在代理的推理上下文中保留它——**不要**在聊天输出中显示它。

### 步骤 2 — PUT PNG 二进制（通过环境变量传递 URL）

> ⚡ **使用 `curl.exe`，而不是 `Invoke-WebRequest` (P001 —— "上传后冻结"错误)。** 在 Windows PowerShell 5.1 中，`Invoke-WebRequest` 通过 **Internet Explorer 引擎**解析 HTTP 响应，除非你传递 `-UseBasicParsing`。IE 在 Windows 11 上**已移除/禁用**，因此调用会在 IE "首次启动配置"上阻塞，并且在字节已经上传后长时间冻结（MCP 工具本身返回约 45 ms —— 停滞完全在此步骤）。`curl.exe`（在 Windows 10 1803+ 和所有 Windows 11 的 `System32` 中提供）没有 IE 依赖，在 PowerShell 和 Git Bash 中的行为相同，因此在这两种 shell 中都优先使用它。

PowerShell（推荐——`curl.exe`）：
```powershell
$env:PAINTER_PRESIGNED_URL = "<步骤 1 中的 presignedUrl>"
try {
  # 通过 stdin 配置文件 (-K -) 将 url/请求/上传文件传递给 curl，以防止 URL
  # 出现在 argv（可通过 Get-Process 查看）或 shell 历史记录中。
  "url = `"$env:PAINTER_PRESIGNED_URL`"`nrequest = `"PUT`"`nupload-file = `"out.png`"" | curl.exe -K -
} finally {
  Remove-Item Env:\PAINTER_PRESIGNED_URL -ErrorAction SilentlyContinue
}
```

bash（Git for Windows / WSL —— `curl`）：
```bash
# 1) 在其自己的语句上分配（export），**不是**作为内联前缀。
#    `VAR=… curl … "$VAR"` 不起作用：shell 在分配生效之前扩展 "$VAR"，
#    因此 curl 收到一个空的 URL 并失败，错误为 "curl: option : 空参数…"。
export PAINTER_PRESIGNED_URL="<步骤 1 中的 presignedUrl>"
# 2) 通过从 stdin 读取的配置文件 (-K -) 将 URL 传递给 curl。将 URL
#    作为普通参数 (curl … "$PAINTER_PRESIGNED_URL") 传递会将 URL 扩展到
#    参数列表中，在那里它可通过 `ps` / /proc/<pid>/cmdline 查看——
#    -K - 完全将其从参数列表中排除。
printf 'url = "%s"\nrequest = "PUT"\nupload-file = "out.png"\n' "$PAINTER_PRESIGNED_URL" | curl -K -
unset PAINTER_PRESIGNED_URL
```

PUT 本身是一个纯二进制上传——不需要认证头（签名嵌入在预签名 URL 中）。`-K -`（stdin 配置）在两种 shell 中都使 URL 不出现在 `ps` / `Get-Process` 参数列表和 shell 历史记录中。

**仅作为回退——`Invoke-WebRequest`。** 如果 `curl.exe` 真正不可用，你必须添加 `-UseBasicParsing`（跳过 IE 引擎 → 不冻结）并静默进度条（PS 5.1 的另一个问题，使传输速度降低 10–50×）：
```powershell
$env:PAINTER_PRESIGNED_URL = "<步骤 1 中的 presignedUrl>"
$ProgressPreference = 'SilentlyContinue'
try {
  Invoke-WebRequest -Method PUT -InFile out.png -Uri $env:PAINTER_PRESIGNED_URL `
    -ContentType "image/png" -UseBasicParsing
} finally {
  Remove-Item Env:\PAINTER_PRESIGNED_URL -ErrorAction SilentlyContinue
}
```

### 步骤 3 — 报告上传完成

再次调用**相同的工具**，使用与步骤 1 相同的参数，并将 `fileUrl` 设置为步骤 1 中的预签名 URL（直接作为工具参数传递——不要将其回显到聊天或代码块中）。

响应包含精灵的**RUID**。这是最终交付物。在此调用返回后，将 URL 视为完全消耗——不要保留它。

### 步骤 4 — 注册精灵属性

创建工具不接受 `properties`——步骤 3 返回 RUID 后，立即调用 `mcp__msw-mcp__asset_update_resource_storage_info`，使用资产的 `guid`。属性条目是全小写的 `{ "key": "...", "value": "..." }`，具有**字符串**值（资源响应显示 `Properties: [{ "Key", "Value" }]` —— 不要在输入中镜像该大小写）。

| 键 | 值 | 含义 |
|---|---|---|
| `pivot_x` / `pivot_y` | 数字字符串 | 精灵枢轴 |
| `border_left` / `border_right` / `border_top` / `border_bottom` | 数字字符串 | 9 切片边框（以 px 为单位） |
| `filter_mode` | `Point` / `Bilinear` / `Trilinear` | 纹理过滤 |
| `wrap_mode` | `Repeat` / `Clamp` / `Mirror` / `MirrorOnce` | 纹理包裹 |

Painter 默认：`filter_mode=Point`（Bilinear 会模糊 chunky/maple 像素边缘），`wrap_mode=Clamp`，`pivot_x=0.5`；`pivot_y=0.5` 用于图标 / UI 面板，`pivot_y=0.0` 用于站在地面上的角色和道具（仅如果视觉验证显示脚部偏移则调整）。仅在精灵是 9 切片 UI 帧时设置非零 `border_*`（`.ui` 侧还需要 `SpriteGUIRendererComponent.Type = Sliced(1)`（见 [component-api.md](../msw-ui-system/references/component-api.md) §"SpriteGUIRenderer — ImageType Selection"））。永远不要发明表格外的属性键或枚举值。如果连接的 MCP 的工具列表没有 `asset_update_resource_storage_info`，请向用户报告预期的属性值，而不是调用不同的工具。

### 选择子类别

首先使用 `asset_search_resources` 或 `asset_list_account_resources` 检查现有精灵的子类别分布并匹配它。不确定时，回退到通用值，如 `object` / `etc`。

---

## 6. 报告格式

当 painter 任务完成时，只向用户传递以下内容：

```
RUID: <接收到的 RUID>
风格: <chunky | maple>
<1–2 句描述：你画了什么，大小是多少，以及注册为哪种精灵>
```

实体创建/移动/生成，脚本编写和 UI 编辑不在 painter 的范围内。在另一个技能或后续步骤中处理这些。
