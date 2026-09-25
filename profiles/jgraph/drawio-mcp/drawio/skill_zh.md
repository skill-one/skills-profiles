# Draw.io 图表技能

生成 draw.io 图表为原生 `.drawio` 文件。以 **Mermaid**（简洁文本，draw.io 桌面 CLI 转换并布局）或直接以 **draw.io XML** 方式编写每个图表。可选择自动布局以 **ELK** 编写的 XML 图表，将图表 XML 嵌入其中导出到 PNG/SVG/PDF（因此导出的文件可在 draw.io 中保持可编辑），或生成一个浏览器 URL 以直接在 draw.io 编辑器中打开图表。

## 编写：Mermaid 或 XML？

桌面 CLI 可以将 Mermaid 转换为原生 `.drawio` 文件，因此对于它处理得好的图表类型**优先使用 Mermaid**——它的解析器自动布局图表，这比在 XML 中手动定位单元格要可靠得多。

| 编写为 | 最佳用途 | 是否需要桌面 CLI |
|-------|----------|--------------------|
| **Mermaid** | 流程图、时序图、类图、状态图、ER 图、甘特图、思维导图、时间线、用户旅程、象限图、C4、git 图、饼图和其他标准类型 | 是——用于转换为 `.drawio` |
| **XML** | 自定义样式、精确/手动定位、特定形状库（AWS、Azure、网络、UML 详细信息……）或当未安装桌面 CLI 时 | 否（可选 ELK `--layout` 需要CLI） |

- **当桌面 CLI 可用时，优先使用 Mermaid**——编写简洁的 Mermaid 并让 draw.io 进行布局。
- **使用 XML** 进行精确控制，或作为通用回退方案：XML 无需 CLI，因此当未安装桌面应用程序时（输出 `.drawio` 文件或 `url`）是唯一选项。
- 对于以 XML 编写的图表，您可以要求 CLI 应用 **ELK 自动布局** (`--layout`) 而不是自己计算坐标——与 draw.io 编辑器的 *排列 ▸ 布局* 菜单应用的相同布局，以及 draw.io MCP 应用服务器使用的相同引擎。参见 [ELK 布局 for XML](#elk-layout-for-xml)。

如果您不确定桌面 CLI 是否存在，请先检测它（参见 [定位 CLI](#locating-the-cli)）。无 CLI → 以 XML 编写并交付 `.drawio` 文件或 `url`。

## 管道

每个图表首先变为原生 `.drawio` 文件，然后以请求的输出格式交付。这确保了无论您是使用 Mermaid 还是 XML，交付步骤都相同。

1. **编写 → `.drawio`**
   - **Mermaid**：将 Mermaid 写入 `.mmd` 文件，然后使用 CLI 转换它：
     ```bash
     drawio -x -f xml -o diagram.drawio diagram.mmd
     ```
     转换后删除 `.mmd`——`.drawio` 是最终产物。draw.io 的 Mermaid 解析器已经布局了图表，因此不需要 `--layout`。
   - **XML**：将 mxGraphModel XML 写入 `diagram.drawio`（参见 [XML 格式](#xml-format)）。可选择应用 ELK 布局（参见 [ELK 布局 for XML](#elk-layout-for-xml)）。
2. **交付**（对两种来源都相同）：
   - *(无格式)* → 保留 `diagram.drawio` 并在 draw.io 中打开。
   - **png / svg / pdf** → 从 `.drawio` 导出，其中嵌入 XML，然后删除源 `.drawio`：
     ```bash
     drawio -x -f png -e -b 10 -o diagram.drawio.png diagram.drawio
     ```
   - **url** → 从 `.drawio` XML 生成浏览器 URL，在浏览器中打开它，并保留 `.drawio` 作为本地副本（参见 [Browser URL 输出](#browser-url-output)）。
3. **打开结果**——导出的文件、URL 或 `.drawio`。如果打开命令失败，请打印绝对路径（或 URL），以便用户可以手动打开它。

**始终先将 Mermaid 转换为 `.drawio`，然后导出**——不要直接将 `.mmd` 导出到图像。当前的 draw.io 桌面版中直接 Mermaid → PNG 导出是损坏的（嵌入-XML 步骤崩溃）；转换、然后导出 `.drawio` 的两步路径是可靠的，并产生可编辑的嵌入。参见 [故障排除](#troubleshooting)。

如果请求 Mermaid 但没有桌面 CLI，则回退到直接以 XML 编写相同的图表。

## ELK 布局 for XML

以 XML 编写的图表可以通过 CLI 的 `--layout` 路径进行自动定位——与编辑器的 *排列 ▸ 布局* 菜单相同的 ELK 布局，以及 draw.io MCP 应用服务器使用的相同引擎。生成单元格时使用近似（甚至 `0,0`）位置，让 ELK 放置它们；您只需要正确地获取图的 *结构*——节点和边。

在任何读取您的 XML 的 CLI 调用中添加 `--layout <name>`。最简单的形式是在您编写文件后原地布局（支持读取并覆盖同一路径）：

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

或者将布局与导出组合在一个调用中（适用于 XML 输入）：

```bash
drawio -x -f png -e -b 10 --layout verticalFlow -o diagram.drawio.png diagram.drawio
```

### 布局预设

| 名称 | 布局 |
|------|--------|
| `verticalFlow` | 层次，自上而下——流程图、管道 |
| `horizontalFlow` | 层次，自左向右 |
| `verticalTree` | 树，自上而下——层次结构、组织结构图 |
| `horizontalTree` | 树，自左向右 |
| `radialTree` | 径向树 |
| `organic` | 力导向——网络、类似思维导图的图表 |

### 自定义布局 JSON

为了更精细的控制，传递一个 JSON **数组**（以 `[` 开头）而不是预设名称——与编辑器的自定义布局对话框相同的格式：

```bash
drawio -x -f xml --layout '[{"layout":"elkLayered","config":{"elk.direction":"RIGHT"}}]' -o diagram.drawio diagram.drawio
```

每个条目是 `{"layout": <算法>, "config": { … }}`：

- **算法**：`elkLayered`, `elkTree`, `elkRadial`, `elkOrganic`, `elkStress`, `elkBox`。
- **`config`**：以 `elk.` 开头的键是 ELK 选项——例如 `elk.direction` (`UP` / `DOWN` / `LEFT` / `RIGHT`), `elk.spacing.nodeNode`, `elk.layered.spacing.nodeNodeBetweenLayers`。键 `edgeStyle`（例如 `orthogonal`）和 `corners`（例如 `rounded`）控制连接器渲染。

### 正交边路由

`--layout libavoid` 将边正交地路由到形状周围（编辑器的 *排列 ▸ 布局 ▸ 正交路由*），而不移动任何顶点——上述节点布局的补充。将其用作手动定位的 XML 的原地传递，其连接器穿过形状：

```bash
drawio -x -f xml --layout libavoid -o diagram.drawio diagram.drawio
```

在流程/树预设之后跳过它——那些已经路由它们的边。

**何时使用它**：以 XML 编写图结构，而不用担心坐标，然后应用 `verticalFlow` / `horizontalFlow` 用于流程式图表或 `organic` 用于网络。以 Mermaid 编写的图表已经布局——不要添加 `--layout`。

## Mermaid 语法参考

编写 Mermaid 时，获取并遵循共享的 Mermaid 参考（所有支持图表类型加上流程图样式——`style`, `classDef`, `linkStyle`）：

https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/mermaid-reference.md

使图表标签的语言与用户的语言匹配。

## 选择输出格式

检查用户的请求格式偏好。示例：

- `/drawio:drawio 创建流程图` → Mermaid → `flowchart.drawio`
- `/drawio:drawio png 登录流程图` → Mermaid → `login-flow.drawio.png`
- `/drawio:drawio svg: ER 图` → Mermaid → `er-diagram.drawio.svg`
- `/drawio:drawio pdf AWS 架构概述` → XML（需要 AWS 形状）→ `architecture-overview.drawio.pdf`
- `/drawio:drawio url 登录流程图` → 在 `app.diagrams.net` 的浏览器中打开图表，保留 `login-flow.drawio` 本地

如果未提及格式，只需生成 `.drawio` 文件并在 draw.io 中打开它。用户始终可以要求稍后导出。

### 支持的导出格式

| 格式 | 嵌入 XML | 备注 |
|--------|-----------|-------|
| `png` | 是 (`-e`) | 可在任何地方查看，可在 draw.io 中编辑 |
| `svg` | 是 (`-e`) | 可缩放，可在 draw.io 中编辑 |
| `pdf` | 是 (`-e`) | 可打印，可在 draw.io 中编辑 |
| `jpg` | 否 | 有损，不支持嵌入 XML |

PNG、SVG 和 PDF 都支持 `--embed-diagram`——导出的文件包含完整的图表 XML，因此将其在 draw.io 中打开可恢复可编辑的图表。

## Browser URL 输出

当用户请求 `url` 格式时，生成一个 draw.io URL，直接在浏览器编辑器中打开图表（在 `app.diagrams.net` 中），无需 draw.io 桌面版即可查看它。（以 Mermaid 编写的图表仍然需要桌面 CLI 转换为 `.drawio`；如果未安装 CLI，则作为 XML 编写图表并从那里构建 URL。）

### 工作原理

1. `.drawio` 文件像平常一样写入磁盘（为用户提供可持久化的本地副本，他们可以重新编辑）
2. XML 使用 Node.js 的内置 `zlib` 压缩并 base64 编码
3. 结果嵌入在 `https://app.diagrams.net/#create=...` URL 中
4. 在默认浏览器中打开 URL

这仅使用 Node.js 内置模块（`zlib`, `child_process`）——没有外部依赖。

### URL 生成

运行此 `node -e` 单行代码以读取 `.drawio` 文件并打印 URL（将 `DIAGRAM.drawio` 替换为实际文件名）：

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

URL 格式与 MCP Tool Server 匹配。Node.js 的 `zlib.deflateRawSync` 和 `pako.deflateRaw` 都实现 RFC 1951 并产生相同的输出，因此来自任何来源的 URL 都是可互换的。

### 打开 URL

| 环境 | 命令 |
|-------------|---------|
| macOS | `open "$URL"` |
| Linux (原生) | `xdg-open "$URL"` |
| WSL2 | 写一个临时 `.url` 文件，通过 `cmd.exe` 打开（见下文） |
| Windows (原生) | 写一个临时 `.url` 文件，通过 `start` 打开（见下文） |

**为什么在 Windows/WSL2 上使用 `.url` 工作绕过？** `cmd.exe` 的 `start` 命令将 `&` 视为命令分隔符，并删除 URL 中 `#` 之后的所有内容。图表有效负载位于 `#create=...` 片段中，因此直接传递 URL 会导致它被静默丢失。`.url` 快捷方式保留了 URL 的完整性。

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

**不要**使用 `echo URL=%URL%` 构建 `.url` 文件。生成的 URL 包含 `&` 字符（`?grid=0&pv=0&...`），`cmd.exe` 将其视为命令分隔符，因此快捷方式被截断，图表有效负载丢失——这正是 `.url` 文件旨在防止的故障。让 Node 直接写入文件（它已经持有 URL 字符串）并仅打开生成的路径，该路径不包含 `&`：

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

从 bash 或 cmd shell 运行它：

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File find-drawio.ps1
```

在每个调用中引用路径——它几乎总是包含空格：

```
& "D:\Program Files\draw.io\draw.io.exe" -x -f xml -o diagram.drawio diagram.mmd
```

只有当每个步骤都为空时，才应将 CLI 视为缺失，并回退到以 XML 编写并使用 `.drawio` / `url` 输出。当您找到它不在 PATH 中时，请告知用户将此文件夹（例如 `D:\Program Files\draw.io`）添加到 PATH 可使其在下一次发现。

### 转换 / 布局 / 导出命令

**将 Mermaid 转换为 `.drawio`:**

```bash
drawio -x -f xml -o diagram.drawio diagram.mmd
```

**对 XML 应用 ELK 布局**（参见 [ELK 布局 for XML](#elk-layout-for-xml)）：

```bash
drawio -x -f xml --layout verticalFlow -o diagram.drawio diagram.drawio
```

**导出到图像格式:**

```bash
drawio -x -f <格式> -e -b 10 -o "<输出>" "<输入.drawio>"
```

**WSL2 导出示例:**

```bash
"/mnt/c/Program Files/draw.io/draw.io.exe" -x -f png -e -b 10 -o "diagram.drawio.png" "diagram.drawio"
```

关键标志：
- `-x` / `--export`：导出模式（也用于 Mermaid 转换和布局传递）
- `-f` / `--format`：输出格式 (`xml`, png, svg, pdf, jpg) —— 使用 `xml` 生成 `.drawio` 或进行布局
- `--layout`：在写入输出之前运行布局——ELK 预设名称、`libavoid` 边路由传递或自定义布局 JSON 数组
- `--mermaid-image 1`：将 Mermaid 转换为单个静态 SVG 图像单元格（Mermaid 源保留在单元格中以便重新编辑），而不是可编辑图表——仅在用户明确要求非可编辑图像单元格时使用
- `-e` / `--embed-diagram`：嵌入图表 XML 在输出中（PNG, SVG, PDF 仅限）
- `-o` / `--output`：输出文件路径
- `-b` / `--border`：图表周围的边框宽度（默认：0）
- `-t` / `--transparent`：透明背景（PNG 仅限）
- `-s` / `--scale`：缩放图表大小
- `--width` / `--height`：适应指定尺寸（保持宽高比）
- `-a` / `--all-pages`：导出所有页面（PDF 仅限）
- `-p` / `--page-index`：选择特定页面（1 基）
- `--disable-gpu`：跳过 GPU 初始化——在命令因 `GPU process isn't usable` 而失败时添加它（Windows 远程桌面会话、虚拟机、CI 运行器）；没有转换、布局或导出路径需要 GPU

### 打开结果

| 环境 | 命令 |
|-------------|---------|
| macOS | `open <file>` |
| Linux (原生) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Windows | `start <file>` |

**WSL2 注意事项：**
- `wslpath -w <file>` 将 WSL2 路径（例如 `/home/user/diagram.drawio`）转换为 Windows 路径（例如 `C:\Users\...`）。这是必需的，因为 `cmd.exe` 无法解析 `/mnt/c/...` 风格的路径。
- `start` 后的空字符串 `""` 是必需的，以防止 `start` 将文件名解释为窗口标题。

**WSL2 示例:**

```bash
cmd.exe /c start "" "$(wslpath -w diagram.drawio)"
```

## 文件命名

- 基于图表内容使用描述性文件名（例如，`login-flow`, `database-schema`）
- 使用小写和连字符表示多词名称
- 编写 Mermaid 时，将其写入匹配的 `.mmd` 文件，转换为 `.drawio`，然后删除 `.mmd`——`.drawio` 是最终产物
- 导出时使用双扩展名：`name.drawio.png`, `name.drawio.svg`, `name.drawio.pdf`——这表明文件包含嵌入的图表 XML
- 导出成功后，删除中间的 `.drawio` 文件——导出的文件包含完整的图表
- 对于 `url` 模式，保留 `.drawio` 文件（无双扩展名）——URL 是查看/编辑的句柄，本地文件是持久副本

## XML 格式

`.drawio` 文件是原生 mxGraphModel XML。编写 XML 时，直接生成它；Mermaid 由 CLI 转换为相同的格式 (`-f xml`)，因此两种编写路线最终都成为原生 `.drawio`。

### 基本结构

每个图表都必须具有此结构：

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- 图表单元格在这里，parent="1" -->
  </root>
</mxGraphModel>
```

- 细胞 `id="0"` 是根层
- 细胞 `id="1"` 是默认父层
- 所有图表元素使用 `parent="1"`，除非使用多个层
- **容器内的单元格** 使用 `parent="<容器_id>"` 并相对于该容器使用坐标
- **边属于包含两个端点的最内层容器**——相同容器（在任何嵌套深度）→ 该容器的 id；一个端点在所有容器之外 → `parent="1"`。自动布局读取边的坐标在其父容器的框架内，因此边比其端点更外围定位时会布局在错误的位置

（上面的示例使用 XML 注释仅在指出单元格位置——在真实输出中从不发出注释；参见 [XML well-formedness](#critical-xml-well-formedness)。）

## XML 参考

有关完整的 draw.io XML 参考，包括常见样式、边路由、容器、层、标签、元数据、暗黑模式颜色和 XML well-formedness 规则，请获取并遵循位于以下位置的说明：
https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| draw.io CLI 未找到 | 桌面应用程序未安装或不在 PATH | 以 XML 编写并交付 `.drawio` 文件或 `url`（Mermaid 转换、ELK 布局和图像导出都需要桌面应用程序）。告知用户他们可以安装 draw.io 桌面应用程序以启用这些功能 |
| Mermaid → PNG 导出崩溃 | 当前 draw.io 桌面版中直接 `.mmd` → PNG 使用 `-e` 是损坏的（嵌入-XML 步骤） | 使用两步路径：首先将 Mermaid 转换为 `.drawio` (`-f xml`), 然后导出 `.drawio` 到 PNG——中间文件嵌入正确 |
| 从 Mermaid 获得空白图表 | 类型关键字拼写错误，或语法错误（错误的节点 ID、未加引号的标签） | 检查 [Mermaid reference](#mermaid-syntax-reference)；第一个非指令行中的关键字选择图表类型 |
| 布局无任何操作/错误 | 未知预设名称、自定义 JSON 不是数组，或桌面构建太旧，无法使用 `--layout` / `.mmd` 输入 | 使用 [Layout presets](#layout-presets) 中的预设或以 `[` 开头的 JSON 数组；在旧桌面构建上，以 XML 编写显式位置并告知用户更新 draw.io 桌面应用程序可启用 Mermaid 转换和布局 |
| 导出产生空/损坏的文件 | 无效 XML（例如，注释中双连字符、未转义的特殊字符） | 在写入之前验证 XML well-formedness；参见下文的 XML well-formedness 部分 |
| 图表打开但看起来为空 | 缺少根单元格 `id="0"` 和 `id="1"` | 确保基本 mxGraphModel 结构完整 |
| 边未渲染 | 边 mxCell 是自闭合的（没有 child mxGeometry 元素） | 每个边必须具有 `<mxGeometry relative="1" as="geometry" />` 作为子元素 |
| 导出后文件无法打开 | 文件路径不正确或缺少文件关联 | 打印绝对文件路径以便用户可以手动打开它 |
| `GPU process isn't usable. Goodbye.` 在转换/布局/导出期间 | Electron 无法启动 GPU 进程——在 Windows 远程桌面会话、虚拟机和 CI 运行器中很常见。打印的 `os_crypt` / `Failed to decrypt` 行与其无关 | 使用 `--disable-gpu` 添加相同的命令；draw.io 桌面应用程序自己的 `--disable-acceleration` 开关有相同效果 |
| 在 `url` 模式下浏览器打开时图表为空 | `cmd.exe` 删除了 `#create=...` 片段 | 在 Windows/WSL2 上使用 `.url` 临时文件工作绕过（见 [Opening the URL](#opening-the-url)）——永远不要将 URL 直接传递给 `cmd.exe /c start` |
| URL 太长无法被浏览器处理 | 非常大的图表超出浏览器 URL 长度限制 | 回退到写入 `.drawio` 文件并本地打开它 |

## CRITICAL: XML well-formedness

- **绝对不要**在输出中包含任何 XML 注释 (`<!-- -->`)。XML 注释是严格禁止的——它们浪费 token，可能导致解析错误，并且在图表 XML 中没有任何用途。
- 在属性值中转义特殊字符：`&amp;`, `&lt;`, `&gt;`, `&quot;`
- 对每个 `mxCell` 使用唯一的 `id` 值
