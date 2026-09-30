---
name: drawio
description: 始终在用户要求创建、生成、绘制或设计图表、流程图、架构图、ER图、时序图、类图、网络图、模型图、线框图或UI草图时使用，或者提及draw.io、drawio、drawoi或.drawio文件，或提到将图表导出为PNG/SVG/PDF。
---

# draw.io 图表技能

生成 draw.io 图表，并以本地的 `.drawio` 文件格式保存。可以以 **Mermaid**（简洁的文本，draw.io 桌面版 CLI 会将其转换并布局）或直接以 **draw.io XML** 的形式创建每个图表。可选择性地使用 **ELK** 自动布局以 XML 方式创建的图表，将图表 XML 嵌入其中导出为 PNG/SVG/PDF（这样导出的文件可以在 draw.io 中保持可编辑性），或生成一个浏览器 URL，直接在 draw.io 编辑器中打开图表。

## 创建方式：Mermaid 或 XML？

桌面版 CLI 可以将 Mermaid 转换为本地 `.drawio` 文件，因此对于它处理效果良好的图表类型（其解析器会自动布局图表，这比手动定位 XML 中的单元格要可靠得多），**优先选择 Mermaid**。

| 创建方式 | 最佳用途 | 是否需要桌面版 CLI |
|----------|----------|--------------------|
| **Mermaid** | 流程图、时序图、类图、状态图、ER 图、甘特图、思维导图、时间线、用户旅程、象限图、C4、Git 图、饼图以及其他标准类型 | 是 — 用于转换为 `.drawio` |
| **XML** | 自定义样式、精确/手动定位、特定形状库（AWS、Azure、网络、UML 细节等）或当未安装桌面版 CLI 时 | 否（可选的 ELK `--layout` 需要 CLI） |

- 当桌面版 CLI 可用且请求是上述标准类型之一时，**优先选择 Mermaid** — 编写简洁的 Mermaid，让 draw.io 进行布局。
- **使用 XML** 进行精确控制，或作为通用回退方案：XML 无需 CLI，因此在未安装桌面应用时是唯一选项（输出 `.drawio` 文件或 `url`）。
- 对于 XML 创建的图表，可以要求 CLI 应用 ELK 自动布局 (`--layout`) 而不是自行计算坐标 — 与 draw.io 编辑器中的 *排列 ▸ 布局* 菜单使用的相同布局，以及 draw.io MCP 应用服务器使用的相同引擎。参见 [XML 的 ELK 布局](#elk-layout-for-xml)。

如果您不确定桌面版 CLI 是否存在，请先检测（参见 [定位 CLI](#locating-the-cli)）。无 CLI → 以 XML 方式创建，并交付 `.drawio` 文件或 `url`。

## 管道流程

每个图表首先转换为本地的 `.drawio` 文件，然后以请求的输出格式交付。无论您是以 Mermaid 还是 XML 创建图表，交付步骤都保持一致。

1. **创建 → `.drawio`**
   - **Mermaid**：将 Mermaid 写入 `.mmd` 文件，然后用 CLI 转换：
     ```bash
     drawio -x -f xml -o diagram.drawio diagram.mmd
     ```
     转换后删除 `.mmd` 文件 — `.drawio` 是最终产物。draw.io 的 Mermaid 解析器已经自动布局了图表，因此无需 `--layout`。
   - **XML**：将 mxGraphModel XML 写入 `diagram.drawio`（参见 [XML 格式](#xml-format)）。可选择应用 ELK 布局（参见 [XML 的 ELK 布局](#elk-layout-for-xml)）。
2. **交付**（对两种来源都相同）：
   - *(无格式)* → 保留 `diagram.drawio` 并在 draw.io 中打开。
   - **png / svg / pdf** → 从 `.drawio` 导出，嵌入 XML，然后删除源 `.drawio`：
     ```bash
     drawio -x -f png -e -b 10 -o diagram.drawio.png diagram.drawio
     ```
   - **url** → 从 `.drawio` XML 生成浏览器 URL，在浏览器中打开 draw.io 编辑器，并将 `.drawio` 作为本地副本保留（参见 [浏览器 URL 输出](#browser-url-output)）。
3. **打开结果** — 导出的文件、URL 或 `.drawio`。如果打开命令失败，请打印绝对路径（或 URL），以便用户手动打开。

**始终先转换 Mermaid 为 `.drawio`，然后导出** — 不要直接将 `.mmd` 导出为图像。当前的 draw.io 桌面版中直接 Mermaid → PNG 导出会出问题（嵌入 XML 步骤崩溃）；两步路径（转换，然后导出 `.drawio`）是可靠的，并产生可编辑的嵌入。参见 [故障排除](#troubleshooting)。

如果请求 Mermaid 但没有桌面版 CLI，则回退为直接以 XML 方式创建相同的图表。

## XML 的 ELK 布局

XML 创建的图表可以通过 CLI 的 `--layout` 阶段自动定位 — 与编辑器中的 *排列 ▸ 布局* 菜单和 draw.io MCP 应用服务器使用的相同 ELK 布局。生成具有近似（甚至 `0,0`）位置的单元格，让 ELK 定位它们；您只需要确保图 *结构*（节点和边）正确。

在任何读取您的 XML 的 CLI 调用中添加 `--layout <name>`。最简单的形式是在您写入文件后原地布局（支持读取并覆盖同一路径）：

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

或者将布局与导出合并为单次调用（适用于 XML 输入）：

```bash
drawio -x -f png -e -b 10 --layout verticalFlow -o diagram.drawio.png diagram.drawio
```

### 布局预设

| 名称 | 布局 |
|------|--------|
| `verticalFlow` | 层叠式，自上而下 — 流程图、管道 |
| `horizontalFlow` | 层叠式，自左向右 |
| `verticalTree` | 树状，自上而下 — 层级结构、组织结构图 |
| `horizontalTree` | 树状，自左向右 |
| `radialTree` | 径向树 |
| `organic` | 力导向式 — 网络、类似思维导图的图表 |

### 自定义布局 JSON

为了更精细的控制，传递一个 JSON **数组**（以 `[` 开头）而不是预设名称 — 与编辑器的自定义布局对话框相同的格式：

```bash
drawio -x -f xml --layout '[{"layout":"elkLayered","config":{"elk.direction":"RIGHT"}}]' -o diagram.drawio diagram.drawio
```

每个条目是 `{"layout": <算法>, "config": { … }}`：

- **算法**：`elkLayered`、`elkTree`、`elkRadial`、`elkOrganic`、`elkStress`、`elkBox`。
- **`config`**：以 `elk.` 开头的键是 ELK 选项 — 例如 `elk.direction` (`UP` / `DOWN` / `LEFT` / `RIGHT`), `elk.spacing.nodeNode`, `elk.layered.spacing.nodeNodeBetweenLayers`。键 `edgeStyle`（例如 `orthogonal`）和 `corners`（例如 `rounded`）控制连接器的渲染。

### 正交边路由

`--layout libavoid` 将 **边** 正交地绕形状路由（编辑器中的 *排列 ▸ 布局 ▸ 正交路由*），而不会移动任何顶点 — 上述节点布局的补充。用于手动定位的 XML，其连接器交叉形状：

```bash
drawio -x -f xml --layout libavoid -o diagram.drawio diagram.drawio
```

在流程/树预设之后跳过它 — 那些已经路由了它们的边。

**何时使用它**：以 XML 创建图结构，无需担心坐标，然后应用 `verticalFlow` / `horizontalFlow` 用于流程式图表或 `organic` 用于网络。Mermaid 创建的图表已经布局 — 不要添加 `--layout`。

## Mermaid 语法参考

创建 Mermaid 时，获取并遵循共享的 Mermaid 参考（所有支持的图表类型加上流程图样式 — `style`、`classDef`、`linkStyle`）：

https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/mermaid-reference.md

使图表标签的语言与用户语言匹配。

## 选择输出格式

检查用户的请求格式偏好。示例：

- `/drawio:drawio 创建流程图` → Mermaid → `flowchart.drawio`
- `/drawio:drawio png 流程图用于登录` → Mermaid → `login-flow.drawio.png`
- `/drawio:drawio svg: ER 图` → Mermaid → `er-diagram.drawio.svg`
- `/drawio:drawio pdf AWS 架构概述` → XML（需要 AWS 形状）→ `architecture-overview.drawio.pdf`
- `/drawio:drawio url 流程图用于用户登录` → 在 `app.diagrams.net` 中打开浏览器中的图表，本地保留 `login-flow.drawio`

如果未提及格式，只需生成 `.drawio` 文件并在 draw.io 中打开。用户可以随时要求导出。

### 支持的导出格式

| 格式 | 嵌入 XML | 备注 |
|--------|-----------|-------|
| `png` | 是 (`-e`) | 可在任何地方查看，在 draw.io 中可编辑 |
| `svg` | 是 (`-e`) | 可缩放，在 draw.io 中可编辑 |
| `pdf` | 是 (`-e`) | 可打印，在 draw.io 中可编辑 |
| `jpg` | 否 | 有损压缩，不支持嵌入 XML |

PNG、SVG 和 PDF 都支持 `--embed-diagram` — 导出的文件包含完整的图表 XML，因此打开它可以在 draw.io 中恢复可编辑的图表。

## 浏览器 URL 输出

当用户请求 `url` 格式时，生成一个 draw.io URL，直接在浏览器编辑器中打开图表（位于 `app.diagrams.net`），无需 draw.io 桌面版即可 *查看* 它。（Mermaid 创建的图表仍需要桌面版 CLI 转换为 `.drawio`；如果未安装 CLI，则从 XML 创建图表并构建 URL。）

### 工作原理

1. 像往常一样将 `.drawio` 文件写入磁盘（为用户提供可重新编辑的持久本地副本）
2. 使用 Node.js 的内置 `zlib` 压缩 XML 并 base64 编码
3. 将结果嵌入 `https://app.diagrams.net/#create=...` URL
4. 在默认浏览器中打开 URL

这仅使用 Node.js 内置模块（`zlib`、`child_process`）— 无需外部依赖。

### URL 生成

运行此 `node -e` 一行代码以读取 `.drawio` 文件并打印 URL（将 `DIAGRAM.drawio` 替换为实际文件名）：

```bash
URL=$(node -e '
const fs = require("fs");
const zlib = require("zlib");
const xml = fs.readFileSync(process.argv[1], "utf8");
const compressed = zlib.deflateRawSync(encodeURIComponent(xml)).toString("base64");
const payload = encodeURIComponent(JSON.stringify({ type: "xml", compressed: true, data: compressed }));
console.log("https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#create=" + payload);
' "DIAGRAM.drawio")
```

URL 格式与 MCP 工具服务器匹配。Node.js 的 `zlib.deflateRawSync` 和 `pako.deflateRaw` 都实现 RFC 1951 并产生相同输出，因此来自任一源的 URL 都是可互换的。

### 打开 URL

| 环境 | 命令 |
|-------------|---------|
| macOS | `open "$URL"` |
| Linux (原生) | `xdg-open "$URL"` |
| WSL2 | 创建临时 `.url` 文件，通过 `cmd.exe` 打开（见下文） |
| Windows (原生) | 创建临时 `.url` 文件，通过 `start` 打开（见下文） |

**为什么 Windows/WSL2 上的 `.url` 工作绕过？** `cmd.exe` 的 `start` 命令将 `&` 视为命令分隔符，并删除 URL 中 `#` 后面的所有内容。图表负载位于 `#create=...` 片段中，因此直接传递 URL 会导致其被静默丢失。`.url` 快捷方式保留了 URL 的完整性。

**macOS / Linux 示例:**

```bash
open "$URL"      # macOS
xdg-open "$URL"  # Linux
```

**WSL2 示例:**

```bash
TMPFILE=$(mktemp --suffix=.url)
printf '[InternetShortcut]\r\nURL=%s\r\n' "$URL" > "$TMPFILE"
cmd.exe /c start "" "$(wslpath -w "$TMPFILE")"
```

**Windows (原生) 示例:**

不要用 `echo URL=%URL%` 构建 `.url` 文件。生成的 URL 包含 `&` 字符（`?grid=0&pv=0&...`），`cmd.exe` 将其视为命令分隔符，因此快捷方式被截断，图表负载丢失 — 这正是 `.url` 文件旨在防止的精确失败。让 Node 直接写入文件（它已经持有 URL 字符串），仅打开生成的路径，该路径从不包含 `&`：

```bash
TMPFILE=$(node -e '
const fs = require("fs");
const os = require("os");
const path = require("path");
const p = path.join(os.tmpdir(), "drawio.url");
fs.writeFileSync(p, "[InternetShortcut]\r\nURL=" + process.argv[1] + "\r\n");
process.stdout.write(p);
' "$URL")
cmd.exe /c start "" "$TMPFILE"
```

### 打开后

打印 URL 以便用户复制或分享，并确认本地文件路径：

```
浏览器中打开: <URL>
本地文件: DIAGRAM.drawio
```

`.drawio` 文件保留在磁盘上，以便用户稍后重新编辑、附加到其他地方或在需要时导出为图像格式。

### URL 长度

URL 嵌入了压缩后的完整图表，位于其哈希片段中。非常大的图表可能会达到浏览器 URL 长度限制（通常为 ~32K–2MB，具体取决于浏览器）。对于超出限制的复杂图表，回退为在本地写入 `.drawio` 文件并打开它。

## draw.io CLI

draw.io 桌面应用包含一个命令行界面，用于 **将 Mermaid 转换为 `.drawio`**、应用 **ELK 布局**（`--layout`）以及 **导出** 为 PNG/SVG/PDF。所有这些都需要安装桌面应用。

### 定位 CLI

首先检测环境，然后相应地定位 CLI。在 Windows（原生和 WSL2）上，安装程序**不会**将 draw.io 放在 PATH 中，且安装目录是用户可选的，因此在使用整个回退链之前不要断定 CLI 缺失。

#### WSL2（Windows 子系统 for Linux）

当 `/proc/version` 包含 `microsoft` 或 `WSL` 时检测到 WSL2：

```bash
grep -qi microsoft /proc/version 2>/dev/null && echo "WSL2"
```

在 WSL2 上，使用 Windows draw.io 桌面版可执行文件，通过 `/mnt/c/...`：

```bash
DRAWIO_CMD="/mnt/c/Program Files/draw.io/draw.io.exe"
```

将路径用引号括起来，以便 `Program Files` 中的空格被视为路径的一部分。**不要**用反引号括起来 — 在 bash 中，反引号是命令替换，这会尝试在定位时*执行*二进制文件，而不是存储其路径。

如果 draw.io 安装在非默认位置，检查常见替代方案：

```bash
# 默认安装路径
"/mnt/c/Program Files/draw.io/draw.io.exe"

# 每个用户的安装（如果上述不存在）
"/mnt/c/Users/$WIN_USER/AppData/Local/Programs/draw.io/draw.io.exe"
```

如果都不存在，则安装在其他驱动器或自定义目录上 — 扫描其他挂载的驱动器，然后查询注册表：

```bash
# 其他驱动器上的 Program Files (D:, E:, …)
ls /mnt/*/Program\ Files/draw.io/draw.io.exe 2>/dev/null | head -1

# 注册表 — 安装程序记录用户选择的位置
for KEY in 'HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall' \
           'HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall' \
           'HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'; do
  WIN_DIR=$(reg.exe query "$KEY" /s /v InstallLocation 2>/dev/null |
            grep -i 'REG_SZ.*draw\.io' | head -1 |
            sed 's/.*REG_SZ[[:space:]]*//' | tr -d '\r')
  [ -n "$WIN_DIR" ] && DRAWIO_CMD="$(wslpath -u "${WIN_DIR%\\}")/draw.io.exe" && break
done
```

#### macOS

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io
```

#### Linux (原生)

```bash
drawio   # 通常通过 snap/apt/flatpak 在 PATH 上
```

使用 `which drawio` 确认它在 PATH 上。

#### Windows (原生，非 WSL2)

按顺序检查 — 缺少 PATH 条目或非 `C:` 安装驱动器是正常的，不是 draw.io 缺失的迹象：

1. **PATH**：`where.exe draw.io`（注意点 — 可执行文件是 `draw.io.exe`，不是 `drawio.exe`）
2. **默认安装路径**：`C:\Program Files\draw.io\draw.io.exe`，然后是每个用户的安装 `%LOCALAPPDATA%\Programs\draw.io\draw.io.exe`
3. **注册表**的卸载键，记录用户选择的位置
4. **其他驱动器**：`D:`, `E:` 上的 `Program Files\draw.io\draw.io.exe`，…

将此保存为 `find-drawio.ps1`，以便一次运行整个链 — 它会打印找到的第一个可执行文件，如果 draw.io 真的未安装，则什么也不打印：

```powershell
$c = @()
$c += (where.exe draw.io 2>$null)
$c += "$env:ProgramFiles\draw.io\draw.io.exe", "$env:LOCALAPPDATA\Programs\draw.io\draw.io.exe"
$c += Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
                       'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
                       'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
      Where-Object { $_.DisplayName -like '*draw.io*' } |
      ForEach-Object { if ($_.InstallLocation) { Join-Path $_.InstallLocation 'draw.io.exe' } else { ($_.DisplayIcon -split ',')[0] } }
$c += (Get-PSDrive -PSProvider FileSystem).Root | ForEach-Object { Join-Path $_ 'Program Files\draw.io\draw.io.exe' }
$c | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
```

从 bash 或 cmd shell 运行它：

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File find-drawio.ps1
```

在每次调用时用引号括起结果路径 — 它几乎总是包含空格：

```
& "D:\Program Files\draw.io\draw.io.exe" -x -f xml -o diagram.drawio diagram.mmd
```

只有在每一步都为空时，才应将 CLI 视为缺失并回退到使用 `.drawio` / `url` 输出的 XML 编写。当你发现它不在 PATH 中时，应告知用户将此文件夹（例如 `D:\Program Files\draw.io`）添加到 PATH 中可以在下次使其可发现。

### 转换 / 布局 / 导出命令

**将 Mermaid 转换为 `.drawio`：**

```bash
drawio -x -f xml -o diagram.drawio diagram.mmd
```

**将 XML 应用于 ELK 布局**（参见 [ELK 布局用于 XML](#elk-layout-for-xml)）：

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

**导出为图像格式：**

```bash
drawio -x -f <format> -e -b 10 -o "<output>" "<input.drawio>"
```

**WSL2 导出示例：**

```bash
"/mnt/c/Program Files/draw.io/draw.io.exe" -x -f png -e -b 10 -o "diagram.drawio.png" "diagram.drawio"
```

关键标志：
- `-x` / `--export`：导出模式（也用于 Mermaid 转换和布局传递）
- `-f` / `--format`：输出格式 (`xml`, png, svg, pdf, jpg) — 使用 `xml` 生成 `.drawio`（从 Mermaid 或布局传递）或布局
- `--layout`：在写入输出之前运行布局 — ELK 预设名称、`libavoid` 边缘路由传递或自定义布局 JSON 数组
- `--mermaid-image 1`：将 Mermaid 转换为单个静态 SVG 图像单元（Mermaid 源代码保留在单元中以供重新编辑），而不是可编辑的图表 — 仅当用户明确要求非可编辑图像单元时
- `-e` / `--embed-diagram`：将图表 XML 嵌入输出（PNG、SVG、PDF 仅限）
- `-o` / `--output`：输出文件路径
- `-b` / `--border`：图表周围的边框宽度（默认：0）
- `-t` / `--transparent`：透明背景（PNG 仅限）
- `-s` / `--scale`：缩放图表大小
- `--width` / `--height`：适应指定尺寸（保持宽高比）
- `-a` / `--all-pages`：导出所有页面（PDF 仅限）
- `-p` / `--page-index`：选择特定页面（基于 1）
- `--disable-gpu`：跳过 GPU 初始化 — 当命令以 `GPU 进程不可用`（Windows 远程桌面会话、虚拟机、CI 运行者）失败时添加；没有转换、布局或导出路径需要 GPU

### 打开结果

| 环境 | 命令 |
|-------|------|
| macOS | `open <file>` |
| Linux (原生) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Windows | `start <file>` |

**WSL2 注意事项：**
- `wslpath -w <file>` 将 WSL2 路径（例如 `/home/user/diagram.drawio`）转换为 Windows 路径（例如 `C:\Users\...`）。这是必需的，因为 `cmd.exe` 无法解析 `/mnt/c/...` 风格的路径。
- `start` 后的空字符串 `""` 是必需的，以防止 `start` 将文件名解释为窗口标题。

**WSL2 示例：**

```bash
cmd.exe /c start "" "$(wslpath -w diagram.drawio)"
```

## 文件命名

- 基于图表内容使用描述性文件名（例如 `login-flow`、`database-schema`）
- 对于多词名称，使用小写和连字符
- 在编写 Mermaid 时，将其写入匹配的 `.mmd` 文件，转换为 `.drawio`，然后删除 `.mmd` — `.drawio` 是最终产物
- 对于导出，使用双扩展名：`name.drawio.png`、`name.drawio.svg`、`name.drawio.pdf` — 这表示文件包含嵌入的图表 XML
- 导出成功后，删除中间的 `.drawio` 文件 — 导出的文件包含完整的图表
- 对于 `url` 模式，保留 `.drawio` 文件（无双扩展名）— URL 是查看/编辑句柄，本地文件是持久副本

## XML 格式

`.drawio` 文件是原生 mxGraphModel XML。在 XML 编写时，直接生成它；CLI（`-f xml`）将 Mermaid 转换为相同的格式，因此两种编写路径最终都成为原生 `.drawio`。

### 基本结构

每个图表都必须具有此结构：

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- 图表单元位于此处，parent="1" -->
  </root>
</mxGraphModel>
```

- 单元 `id="0"` 是根层
- 单元 `id="1"` 是默认父层
- 所有图表元素使用 `parent="1"`，除非使用多个层
- **容器内的单元** 使用 `parent="<容器_id>"` 并相对于该容器使用坐标
- **边属于同时包含两个端点的最内层容器** — 相同容器（任何嵌套深度）→ 该容器的 id；一个端点在所有容器之外 → `parent="1"`。自动布局读取边的坐标在其父级的框架中，因此超出其端点的边布局在错误的位置

（上面的示例仅使用 XML 注释来指出单元的位置 — 在实际输出中永远不要发出注释；参见 [XML 规范性](#critical-xml-well-formedness)。）

## XML 参考

有关完整的 draw.io XML 参考，包括常见样式、边缘路由、容器、层、标签、元数据、暗黑模式颜色和 XML 规范性规则，请获取并遵循以下说明：
https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| draw.io CLI 未找到 | 桌面应用程序未安装或不在 PATH 中 | 作为 XML 编写并交付 `.drawio` 文件或 `url`（Mermaid 转换、ELK 布局和图像导出都需要桌面应用程序）。告知用户他们可以安装 draw.io 桌面应用程序以启用这些功能 |
| Mermaid → PNG 导出崩溃 | 直接 `.mmd` → PNG 使用 `-e` 在当前 draw.io 桌面应用程序中损坏（嵌入-XML 步骤） | 使用两步路径：首先将 Mermaid 转换为 `.drawio`（`-f xml`），然后将 `.drawio` 导出为 PNG — 中间文件正确嵌入 |
| 从 Mermaid 获得空白图表 | 类型关键字拼写错误，或语法错误（坏的节点 ID、未加引号的标签） | 检查 [Mermaid 语法参考](#mermaid-syntax-reference)；第一行非指令的关键字选择图表类型 |
| 布局无操作 / 出错 | 未知预设名称、自定义 JSON 不是数组，或桌面版本太旧无法使用 `--layout` / `.mmd` 输入 | 使用 [布局预设](#layout-presets) 中的预设或以 `[` 开头的 JSON 数组；对于旧桌面版本，使用显式位置作为 XML 编写并告知用户更新 draw.io 桌面应用程序可以启用 Mermaid 转换和布局 |
| 导出产生空/损坏的文件 | 无效的 XML（例如注释中双连字符、未转义的特殊字符） | 在写入之前验证 XML 规范性；参见下方的 XML 规范性部分 |
| 图表打开但看起来为空 | 缺少根单元 `id="0"` 和 `id="1"` | 确保基本的 mxGraphModel 结构完整 |
| 边未渲染 | 边的 mxCell 是自闭合（没有子 mxGeometry 元素） | 每个边必须有一个 `<mxGeometry relative="1" as="geometry" />` 作为子元素 |
| 导出后文件无法打开 | 文件路径不正确或缺少文件关联 | 打印绝对文件路径，以便用户可以手动打开它 |
| `GPU 进程不可用。再见。` 在转换/布局/导出期间 | Electron 无法启动 GPU 进程 — 典型出现在 Windows 远程桌面会话、虚拟机和 CI 运行者。它之前的 `os_crypt` / `Failed to decrypt` 行打印的是无关的噪音 | 使用 `--disable-gpu` 重新尝试相同命令；draw.io 桌面应用程序自己的 `--disable-acceleration` 开关具有相同效果 |
| 在 `url` 模式下浏览器打开空图表 | `cmd.exe` 剥离了 `#create=...` 片段 | 在 Windows/WSL2 上使用 `.url` 临时文件工作方法（参见 [打开 URL](#opening-the-url)）— 永远不要将 URL 直接传递给 `cmd.exe /c start` |
| URL 对浏览器来说太长 | 非常大的图表超过了浏览器 URL 长度限制 | 回退到写入 `.drawio` 文件并在本地打开 |

## 关键：XML 规范性

- **永远不要在输出中包含任何 XML 注释 (`<!-- -->`)。** XML 注释是严格禁止的 — 它们浪费标记，可能导致解析错误，并且在图表 XML 中没有用途。
- 在属性值中转义特殊字符：`&amp;`、`&lt;`、`&gt;`、`&quot;`
- 对每个 `mxCell` 使用唯一的 `id` 值
