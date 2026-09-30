---
name: book-to-skill
description: 将书籍和文档（PDF、EPUB、DOCX、HTML、Markdown、纯文本、RTF、MOBI/AZW，使用Calibre转换MOBI/AZW）转换为结构化的代理技能，提取框架、心智模型、原则、技巧和反模式。当用户希望通过GitHub Copilot CLI、Amp、Claude Code、Hermes Agent或OpenClaw学习文档时，或在工作中应用作者的框架，或从文件构建可重用的知识库时使用。
---

交叉代理备注（信息性；被主机代理忽略）：
  - 兼容技能根源：GitHub Copilot CLI (~/.copilot/skills, ~/.agents/skills, .github/skills, .claude/skills, .agents/skills), Amp (.agents/skills, ~/.config/agents/skills, ~/.config/amp/skills), Claude Code (~/.claude/skills), Hermes Agent ($HERMES_HOME/skills, .hermes/skills, .agents/skills), OpenClaw (${OPENCLAW_STATE_DIR:-~/.openclaw}/skills, .agents/skills, skills/; ~/.agents/skills 仅在默认状态下使用）。
  - `allowed-tools` 是有意省略以保持代理中立：Copilot CLI 使用 `shell`/MCP-server 名称，Claude 使用 `Bash`/`Read`/`Write`/`Glob`/`Grep`，Amp 添加 `shell_command`。该技能需要 shell（以运行 extract.py）和文件读写——每个主机将在首次使用时提示这些内容。
  - 参数提示：<文档文件夹路径或 glob>... [技能名称缩写]

# 书籍到技能转换器

通过提取结构而非生成摘要，将书面知识转化为可操作的代理技能。

## 哲学

书籍包含结晶化的专业知识：花费数年开发的框架、原则和技术。此技能将这些知识提取为 GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenClaw 或其他兼容代理可以重复利用的格式。

**提取结构，而非摘要。** 技能不是书评。它是一套工具箱，包含：
- 命名框架（具有明确应用的思维模型）
- 可操作的原理（指导决策的规则）
- 技术（分步方法）
- 反模式（避免的内容和原因）
- 语音校准（作者的思维和沟通方式）

**保留作者的精确性。** 框架通常有特定名称的原因。 "The 5 Whys" 不能与 "多次询问为什么" 互换。捕获确切的表述。

**适当分层深度。** 简单书籍 → 简单技能。具有 10+ 框架的复杂书籍 → 具有参考文件和按需章节的技能。

---

## 操作模式

四种路径可用。根据用户请求进行路由：

### 1. 完整转换（默认）
**触发：** 用户提供一个或多个文档/目录/glob 路径而没有特殊说明
**操作：** 运行以下所有步骤（步骤 0–9）
**输出：** 完整技能，包含 SKILL.md、chapters/、词汇表、模式、速查表

### 2. 仅分析
**触发：** 用户说 "analyze"、"just extract" 或 "我想在生成前进行审查"
**操作：** 运行步骤 0–3，然后生成结构化提取报告（发现的框架、原理、技术）。停止——不要生成技能文件。
**输出：** 供用户审查的分析报告

### 3. 从先前的分析生成
**触发：** 用户有现有的分析笔记或之前运行了仅分析模式
**操作：** 跳过步骤 0–3，使用提供的分析作为输入，运行步骤 4–9
**输出：** 从提供的分析生成的技能文件

### 4. 更新/合并（现有技能）
**触发：** 用户提供一个或多个新源路径并指示他们要更新现有技能（通过指向现有技能文件夹、提供已存在于 `SKILLS_HOME` 中的技能缩写，或明确请求更新）。
**操作：** 运行步骤 0（范围外检查）、步骤 1（验证输入）、步骤 1.5（识别书籍类型）和步骤 2（提取新文件）。然后跳到步骤 5（识别/检测现有技能路径）并运行 **更新/合并工作流** 将新内容合并到现有技能文件中。
**输出：** 更新后的现有技能，包含新的/修订的章节摘要和合并的索引/词汇表。

---

## 技能位置

此转换器可以从多个技能系统运行。在查找此转换器的辅助脚本或编写生成的书籍技能时，请按顺序优先选择这些位置：

1. GitHub Copilot CLI 个人技能：`~/.copilot/skills/`
2. 跨代理个人技能（Copilot、Amp、Codex；OpenClaw 使用其默认状态）：`~/.agents/skills/`
3. Claude Code 个人技能：`~/.claude/skills/`
4. 项目本地 Copilot 技能：`.github/skills/`
5. 项目本地 Claude 技能：`.claude/skills/`
6. 项目本地 Amp / Copilot / OpenClaw 技能：`.agents/skills/`
7. Amp 全局技能：`~/.config/agents/skills/`
8. Amp 遗留全局技能：`~/.config/amp/skills/`
9. Hermes Agent 个人技能：`$HERMES_HOME/skills/`（默认为 `~/.hermes/skills/`）
10. Hermes Agent 项目技能：`.hermes/skills/` 或 `.agents/skills/`
11. OpenClaw 个人技能：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`（活动状态；`~/.agents/skills/` 仅与默认状态共享）
12. OpenClaw 项目技能：`.agents/skills/` 或 `skills/`

对于 **生成的** 书籍技能，优先选择用户级跨代理根 `~/.agents/skills/`——一个物理副本服务于跨代理主机和 OpenClaw（在其默认状态下使用）。Copilot CLI 和 Amp 原生发现它；Claude Code 需要从 `~/.claude/skills/<skill_name>` 创建符号链接（在步骤 10 中创建，见步骤 5 的规则）。仅在用户明确要求时选择主机私有或项目本地根。`BOOK_TO_SKILL_SCOPE=project` 或 `personal` 可以使该选择对自动化明确；不要因为两个范围都可用而强制询问范围问题。

---

## 步骤 0 — 范围外检查

如果未提供任何参数，停止并响应：
> "book-to-skill 需要一个支持的文档路径、文件夹或 glob 模式。用法：`book-to-skill <path-to-document-folder-or-glob>... [skill-name-slug]`"

在整个工作流程中：
- 识别输入路径和可选的技能缩写。
- 如果最后一个参数不是存在的文件、文件夹或 glob，并且看起来像技能缩写（例如小写连字符、字母数字），将其视为 `SKILL_NAME`。
- 将所有其他参数视为 `INPUT_PATHS` 列表。
- 如果任何输入路径是现有的技能目录（包含 `SKILL.md` 和 `chapters/` 子文件夹），或者 `SKILL_NAME` 匹配 `SKILLS_HOME` 中的现有技能缩写，将此运行标记为 **更新/合并** 操作（模式 4）。

---

## 步骤 1 — 验证输入

验证 `INPUT_PATHS` 中至少有一个支持文件、目录或 glob 模式。
对于目录和 glob，将它们展开以找到匹配的支持文件（`.pdf`、`.epub`、`.docx`、`.txt`、`.md`、`.markdown`、`.rst`、`.adoc`、`.html`、`.htm`、`.rtf`、`.mobi`、`.azw`、`.azw3`）。

如果没有找到支持文件，使用清晰的错误消息停止。

---

## 步骤 1.5 — 识别内容类型

在提取之前，询问用户：

> "这些源包含什么类型的内容？这有助于我选择最佳提取方法。
>
> 1. **技术**——包含代码块、表格、公式、图表（例如编程书籍、学术论文、建筑指南）
> 2. **文本为主**——主要是散文，几乎没有或没有表格/代码（例如管理、生产力、叙事非虚构）
> 3. **不确定**——我将使用快速方法，如果质量似乎有限，我会警告你"

将答案存储为 `BOOK_TYPE`：
- 选项 1 → `BOOK_TYPE=technical`
- 选项 2 → `BOOK_TYPE=text`
- 选项 3 → `BOOK_TYPE=text`

**如果 `BOOK_TYPE=technical`**，在继续之前通知用户：
> "📐 技术模式已选择——使用 Docling 进行结构感知提取（保留表格、代码块、公式为 markdown）。这需要每页约 1.5 秒，因此对于较长的源，请预期几分钟。现在开始…"

**如果 `BOOK_TYPE=text`**，通知：
> "📄 文本模式已选择——使用最适合每种文件类型的快速提取器。纯文本/Markdown/HTML 通常在几秒钟内准备好；PDF 使用 pdftotext（如果可用）。"

---

## 步骤 2 — 从源文档中提取文本

运行提取脚本，传递输入路径：

```bash
SCRIPT_PATH=""
HERMES_HOME_RESOLVED="${HERMES_HOME:-$HOME/.hermes}"
OPENCLAW_STATE_DIR_RESOLVED="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
HERMES_PROJECT_TRUSTED=false
if [ -n "$PROJECT_ROOT" ] && [ "${HERMES_AGENT:-}" = true ] && \
  command -v hermes >/dev/null 2>&1 && \
  command -v python3 >/dev/null 2>&1 && \
  hermes config get skills.trusted_project_dirs --json 2>/dev/null | PROJECT_ROOT="$PROJECT_ROOT" python3 -c 'import json, os, pathlib, sys; root=pathlib.Path(os.environ["PROJECT_ROOT"]).resolve(); sys.exit(not any(pathlib.Path(p).expanduser().resolve() == root for p in json.load(sys.stdin)))' 2>/dev/null
then
  HERMES_PROJECT_TRUSTED=true
fi

CANDIDATES=(
  "$HOME/.copilot/skills/book-to-skill/scripts/extract.py"
  "$HOME/.agents/skills/book-to-skill/scripts/extract.py"
  "$HOME/.claude/skills/book-to-skill/scripts/extract.py"
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills/book-to-skill/scripts/extract.py"
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
  "$HERMES_HOME_RESOLVED/skills/book-to-skill/scripts/extract.py"
  "$HERMES_HOME_RESOLVED"/skills/*/book-to-skill/scripts/extract.py
)
if [ "${HERMES_AGENT:-}" != true ]; then
  CANDIDATES+=(
    ".github/skills/book-to-skill/scripts/extract.py"
    ".claude/skills/book-to-skill/scripts/extract.py"
    ".agents/skills/book-to-skill/scripts/extract.py"
    "skills/book-to-skill/scripts/extract.py"
    "skills"/*/book-to-skill/scripts/extract.py
    "skills"/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
  )
  if [ -n "$PROJECT_ROOT" ]; then
    CANDIDATES+=(
      "$PROJECT_ROOT/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/skills"/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
    )
  fi
fi
CANDIDATES+=(
  "$HOME/.config/agents/skills/book-to-skill/scripts/extract.py"
  "$HOME/.config/amp/skills/book-to-skill/scripts/extract.py"
)
if [ "$HERMES_PROJECT_TRUSTED" = true ]; then
  CANDIDATES=(
    "$PROJECT_ROOT/.hermes/skills/book-to-skill/scripts/extract.py"
    "$PROJECT_ROOT/.hermes/skills"/*/book-to-skill/scripts/extract.py
    "$PROJECT_ROOT/.agents/skills/book-to-skill/scripts/extract.py"
    "$PROJECT_ROOT/.agents/skills"/*/book-to-skill/scripts/extract.py
    "${CANDIDATES[@]}"
  )
fi
for candidate in "${CANDIDATES[@]}"
do
  if [ -f "$candidate" ]; then
    SCRIPT_PATH="$candidate"
    break
  fi
done

if [ -z "$SCRIPT_PATH" ]; then
  echo "Could not find scripts/extract.py for book-to-skill" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" "$SCRIPT_PATH" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask
```

在提取之前，脚本检查检测到的格式所需的可选 Python 包。如果缺少更好的提取器，它会提示用户使用可用的回退。非交互式会话默认使用回退，除非安装模式明确为 `yes`。

**提示——预检环境：** 运行 `"$PYTHON_BIN" "$SCRIPT_PATH" --check` 以打印每个格式的报告，说明已安装的提取器以及确切的命令来安装缺少的内容，而不会处理任何文件。在用户报告设置或质量问题时很有用。

这会创建一个 **每次运行** 的工作目录——`<tempdir>/book_skill_work-<pid>/` 默认，或您在 `BOOK_SKILL_WORKDIR` 中设置的精确路径——包含：
- `full_text.txt` — 所有源组合提取的文本，具有清晰的视觉边界。
- `metadata.json` — 总组合大小、字数、页数、令牌计数、丢弃的 EPUB 图片计数、解析的 `workdir`，以及单个处理源的详细列表。

完成运行时，打印所有三个路径（`Workdir ->`、`Text ->`、`Meta ->`）。**从该输出（或从 `metadata.json` 的 `workdir` 字段）获取路径，而不是假设固定位置**——每个运行的目录名称都不同，因此同一台机器上的并发提取不会覆盖彼此的结果。

检查该运行的 `metadata.json` 以检查结果。

**始终确认提取是您请求的文档**，然后再生成任何内容：检查 `filename` / `source_file` 在 `metadata.json` 中，或 `full_text.txt` 的第一行的 `SOURCE:` 标头。如果您正在等待后台运行，请等待 *其* 特定的工作目录——轮询共享路径可能会显示不同运行的结果。

---

## 步骤 2.5 — 预检成本估算

读取此运行的 `metadata.json`（提取输出的 `Meta ->` 路径）并在执行任何生成之前向用户展示估算：

```
📖 检测到的源：<total_sources> 个源
<列出源元数据列表中的每个源文件和格式>
<如果 images_dropped > 5：警告未读取的 N 个源图像>
📄 组合页数/章节：~<N> | 字数：~<N> | 总令牌数：~<N>K

💰 估计令牌成本（完整转换 / 更新）：
   输入（读取 + 提示）：~<N>K 令牌
   输出（生成/更新的技能文件）：  ~<N>K 令牌
   总计：                           ~<N>K 令牌

   成本：将上述令牌计数乘以您的模型的当前输入/输出每 1M 令牌的费率（价格和模型名称经常变化——不要硬编码它们；引用今天的费率并标记为估算）。

   ⏱ 估计时间：~<N> 分钟

📁 将生成的/更新的文件：
   SKILL.md + 章节文件 + 词汇表 + 模式 + 速查表

➡  继续完整转换 / 更新？（或输入 "analyze only" 以预览）
```

**如何估算：**
- 输入令牌 ≈ `estimated_tokens` 从元数据 × 1.3（每个章节遍历的提示开销）
- 输出令牌 ≈ 章节 × 每章节预算 + 4,000（SKILL.md）+ 4,500（词汇表 + 模式 + 速查表）
  - 每章节预算的中点由 `BOOK_TYPE` 决定（DEPTH 在步骤 4 的后面决定，可能会提高它）：`text` ≈ 1,000，`technical` ≈ 1,800。如果用户已经指示参考仅 vs 深入研究，请使用步骤 7 矩阵的匹配行。
- 成本：报告令牌计数并乘以用户当前的每 1M 令牌输入/输出费率。不要硬编码美元金额——模型名称和价格会变化；如果您显示一个，请将其标记为估算并注明日期。

等待用户确认后再继续。如果他们说 "analyze only"，切换到模式 2。

---

## 步骤 2.6 — 大型书籍的 REPL 风格访问（> 50k 令牌）

受递归语言模型（RLM）范式启发：将 `full_text.txt` 视为可查询的语料库，而不是单个读取。将整个文件加载到上下文中会消耗您稍后用于生成的预算。

对于超过 ~50k 令牌的书籍，优先选择程序化探测而不是无限制的 `Read(full_text.txt)`：

```bash
# 大小检查在任何 Read 之前
wc -w "$FULL_TEXT_PATH"

# 查找章节偏移而不加载整个文件
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# 仅提取您需要的章节（行从 start 到 end 包含）
sed -n '<start>,<end>p' "$FULL_TEXT_PATH"

# 在声称 SKILL.md 中实际提到框架之前验证框架
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"

# 带有偏移/限制的靶向 Read 避免转储整个文件
# Read(file_path=full_text.txt, offset=<line>, limit=<lines>)
```

使用此方法进行第 3 步（结构分析）、第 7 步（每章摘要）和第 8 步（术语表/模式提取）。对于少于 50k 个 token 的书籍，单个 `Read` 就足够了。

**原因是什么：** 一本 200 页的书大约是 75k 个 token。每章重读一次（28 次遍历）的成本约为 2M 输入 token；使用 grep + sed 仅提取相关片段可以将生成成本与输出保持一致，而不是与源代码保持一致。

---

## 第 3 步 — 分析书籍结构

读取提取的 `full_text.txt` 的前 8,000 个字符，以识别：
- 书籍**标题**和**作者**
- **章节结构**（查找“第 N 章”、“第一部分”、编号标题、目录）
- **核心主题**和学科领域
- 大约章节数量

然后，如果存在，则读取目录部分以映射所有章节。

**如果模式是“仅分析”：** 现在生成提取报告并停止。结构：
```
## 提取报告 — <标题>

### 作者的核心框架
- **<框架名称>**: <是什么以及在何时应用>

### 关键原则
- <原则>: <可操作的规则>

### 技术 & 方法
- <技术>: <分步或如何操作>

### 反模式
- <要避免的内容>: <原因>

### 建议的技能名称
`{作者姓氏}-{核心概念}` — 例如 `cialdini-influence`

### 检测到的章节
| # | 标题 | 主要框架 |
```

---

## 第 4 步 — 询问目的（仅限完整转换）

在生成之前，询问用户：

> “这个技能应该帮助您做什么？（选择一个或多个）
> 1. 在工作时应用作者的框架
> 2. 使用作者的思维模型进行思考
> 3. 引用特定章节和概念
> 4. 以上所有”

使用答案来权衡在 SKILL.md 核心部分突出显示的内容。

**从答案中推导 `DEPTH`（无需额外提示）：**
- 答案**仅**是选项 3（引用）→ `DEPTH=reference` — 轻量级、快速查找章节。
- 答案包括选项 1、2 或 4 → `DEPTH=study` — 更深入的章节，包含更多工作细节、示例和推理。

`DEPTH` 和 `BOOK_TYPE` 一起在第 7 步中设置了每个章节的 token 预算。**不要**单独询问“学习 vs 引用”的问题——在这里会推断出来。（在模式 2/3 中，跳过第 4 步时，默认 `DEPTH=study`。）

---

## 第 5 步 — 确定技能名称

如果提供了 `SKILL_NAME`，则将其用作技能别名。
否则，提供两个选项并让用户选择：
- **按作者概念**：`{作者姓氏}-{核心概念}`（例如 `cialdini-influence`、`meadows-systems`）
- **按标题**：从书名中提取的小写连字符（例如 `designing-data-intensive-apps`）

如果书籍具有强烈的方法学身份，则默认使用作者概念格式。

选择目标技能根 (`SKILLS_HOME`)。首先从明确的用户请求或 `BOOK_TO_SKILL_SCOPE` 中解析**范围**，然后探测**主机**。对项目本地/项目输出的请求选择项目本地行；对个人/全局输出的请求选择个人行。如果未请求任何范围，则保留已建立的默认个人设置（`~/.agents/skills` 对于非 Hermes 主机）。不要仅因为存在项目本地根而强制询问范围问题。选择的根可能仍需要在写入之前获得主机批准。

| 主机代理 | 个人技能根 | 项目本地根 |
|---|---|---|
| **GitHub Copilot CLI** | `~/.agents/skills`（原生发现） | `.github/skills` → `.claude/skills` → `.agents/skills` |
| **Amp** | `~/.agents/skills`（原生发现） | `.agents/skills` |
| **OpenAI Codex** | `~/.agents/skills`（原生发现；遵循符号链接） | `.agents/skills` |
| **Hermes Agent** | `$HERMES_HOME/skills/<category>`（默认为 `~/.hermes/skills/<category>`） | `.hermes/skills/<category>` → `.agents/skills` |
| **Claude Code** | `~/.agents/skills` + 从 `~/.claude/skills/<skill_name>` 的符号链接 | `.claude/skills` |
| **OpenClaw** | `${OPENCLAW_STATE_DIR:-~/.openclaw}/skills`（活动状态；仅默认状态为 `~/.agents/skills`） | `.agents/skills` → `skills/` |

Hermes Agent 是唯一保留其个人根的主机：它按类别划分个人技能，并且不扫描跨代理根。使用活动配置文件的 `HERMES_HOME` 并选择与生成的技能主题匹配的类别。不要手动构建配置文件路径。如果用户选择项目本地 Hermes 根，则在生成后运行 `hermes skills trust <project-root>` 并使用 `hermes skills list` 验证发现；项目技能在项目被信任之前不可用。

对于 OpenClaw，使用活动状态目录的 `skills/` 根：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`。共享的 `~/.agents/skills` 兼容根仅在 `OPENCLAW_STATE_DIR` 未设置或等于默认的 `$HOME/.openclaw` 时才可发现；否则使用活动状态根或项目/额外目录。生成后使用 `openclaw skills list` 验证发现。

选择规则：
1. 个人安装：将 `SKILLS_HOME` 设置为 `~/.agents/skills`（如果缺失则创建该目录）。一个例外，因此默认不会在其他人的家里发明约定：如果 `~/.agents/skills` 不存在**并且**主机的私有根已经包含技能，则使用私有根，并在报告中说明原因。
2. **Claude Code 不扫描 `~/.agents/skills`** — 生成完成后，第 10 步将技能链接到 `ln -sfn "$HOME/.agents/skills/<skill_name>" "$HOME/.claude/skills/<skill_name>"`。
3. **Hermes Agent 个人安装使用上面的 Hermes 行，而不是跨代理根，并且不使用符号链接。**
4. 如果用户明确要求主机私有根（`~/.copilot/skills`、`~/.claude/skills`、`~/.config/agents/skills`、`~/.config/amp/skills`），则尊重它并跳过符号链接。
5. 如果用户明确要求项目本地输出，则使用其主机的项目本地行。
6. 如果选择需要知道主机（项目本地输出、Hermes 个人根、OpenClaw 状态根或 Claude Code 符号链接）并且无法识别，则询问：“您在运行哪个代理——OpenClaw、Hermes Agent、GitHub Copilot CLI、Amp、Codex 或 Claude Code？”
7. 对于 OpenClaw 个人输出，使用 `${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/skills`。共享的 `~/.agents/skills` 根仅在 `OPENCLAW_STATE_DIR` 未设置或等于默认的 `$HOME/.openclaw` 时才是有效的 OpenClaw 目标；否则使用活动状态根或项目/额外目录。
8. 如果用户明确要求 OpenClaw 管理的个人根，则使用活动状态根并使用 `openclaw skills list` 验证。

将 `SKILLS_HOME` 设置为选定的根并检查 `$SKILLS_HOME/<skill_name>/` 是否已存在。在 Claude Code 中，还检查 `~/.claude/skills/<skill_name>` 是否存在为**真实目录**（不是符号链接）——之前的安装可能在那里；如果是，则提出迁移它（将目录移动到 `~/.agents/skills/` 并用符号链接替换原始路径）然后继续。
如果技能已存在，提示用户选择：
1. **更新/合并**（模式 4）— 将新文件/内容集成到现有技能组件中。
2. **覆盖**— 删除并从头开始重新生成技能。
3. **重命名**— 添加 `-2` 或使用不同的自定义别名。

如果用户选择**更新/合并**，则在完成第 2.5 步后立即进入**更新/合并工作流**部分（跳过第 3、4、6、7、8、9 步）。

---

## 第 6 步 — 创建技能目录结构

```bash
mkdir -p "$SKILLS_HOME/<skill_name>/chapters"
```

---

## 第 7 步 — 生成章节摘要

**TOKEN 预算规则——关键（自适应）：**

每个章节的预算随 `BOOK_TYPE` 和 `DEPTH` 而变化。技术章节需要空间来容纳代码和表格；学习深度需要空间来容纳推理。从以下矩阵中选择预算：

| | `DEPTH=reference` | `DEPTH=study` |
|---|---|---|
| `BOOK_TYPE=text` | 800–1,200 token | 1,000–1,800 token |
| `BOOK_TYPE=technical` | 1,200–1,800 token | 2,000–3,000 token |

- 这些是每个文件的靶标，不是硬性上限——密集章节可能会超出，薄的章节可能会低于。密度仍然优于长度（质量规则 #3）：永远不要为了达到数字而填充。
- 文件按需加载，因此较大的章节只有在实际读取该章节时才会产生 token 成本。
- 在两个单元格之间不确定时（例如混合内容书籍），使用较低的预算，并让深度来自精确度，而不是数量。

**`DEPTH=study` 是通过内容获得的，而不是通过更大的数字。** 标准部分模板（核心思想 → 连接到）自然会导致密集的散文章节在 700–900 token 左右。要诚实地达到学习预算（不是通过填充）——学习深度的章节必须添加具体材料：
- **重制或重建**章节中的一个具体示例或工件（例如示例新闻稿、样本对话、填写模板、作者逐步演示的决策）在 `## Worked Example` 部分下。这是最大的杠杆，也是学习者返回的主要内容。
- **将每个框架的“如何”扩展为明确的步骤或标准，而不是一句话。**
- **在顶部 1–2 个框架**下添加一个简短的“为什么有效/失败模式”注释。

如果一个章节确实没有具体示例并且难以扩展，则让它低于学习底线，而不是填充——并指出该章节的核心思想很薄。相比之下，`reference`-深度章节故意省略了具体示例，并仅保留决策就绪的基本要素。

对于每个在第 3 步中识别的章节/主要部分：

读取提取的 `full_text.txt` 的相应部分（使用字符偏移或 grep 查找章节标题）。

使用以下结构创建 `$SKILLS_HOME/<skill_name>/chapters/ch<NN>-<slug>.md`。

**根据 `BOOK_TYPE` 调整强调重点：**
- `technical` → 优先考虑“代码示例”、“参考表格”和“命令 & API”部分；保留确切语法
- `text` → 优先考虑“引入的框架”、“思维模型”和“关键要点”；跳过空的技术部分

```markdown
# 第 N 章: <完整标题>

## 核心思想
<1–2 句话：本章教给的最重要的事情>

## 引入的框架
- **<框架名称>**: <确切表述——保留作者的命名>
  - 何时使用：<特定情况>
  - 如何：<步骤或标准>

## 关键概念
- **<术语>**: <一句话中的精确定义>
(本章 5–10 个最重要的术语)

## 思维模型
<2–4 个框架或思维工具。写为“在 X 时使用 Y”或“将 X 视为 Y">

## 反模式
- **<要避免的内容>**: <为什么失败>

## 代码示例 *(仅限技术书籍——如果 BOOK_TYPE=text 则省略)*
<!-- 复制本章中最具指导性的片段。保留缩进完全一致。 -->
```<语言>
<本章的关键代码示例>
```
- **它展示了什么**: <一句话>

## 参考表格 *(仅限技术书籍——如果 BOOK_TYPE=text 则省略)*
<!-- 在 markdown 中复制本章中的任何比较矩阵、参数表或决策表。 -->

## 具体示例 *(仅限 DEPTH=study —— DEPTH=reference 则省略)*
<!-- 重制或重建作者在章节中工作通过的一个具体示例：一个样本文档、一段对话、一个填写模板、一个前后对比，或一个逐步演示的决策。这是学习章节值得其预算的内容。保持对源内容的忠实；永远不要复制长篇原始段落——紧凑地重建示例。 -->

## 关键要点
1. <可操作的见解>
2. <可操作的见解>
3. <可操作的见解>
(3–7 个从业者必须记住的见解)

## 连接到
- **Ch N**: <为什么本章相关>
- **<概念>**: <与之连接的外部概念或标准>
```

---

## 第 8 步 — 生成支持文件

### glossary.md
创建 `$SKILLS_HOME/<skill_name>/glossary.md`：
- 书籍中每个重要术语，按字母顺序排列
- 格式：`**术语** — 定义 (Ch N)`
- 最大 1,500 token

### patterns.md
创建 `$SKILLS_HOME/<skill_name>/patterns.md`：
- 书籍中所有具体技术、设计模式、算法
- 格式：`## 模式名称\n**何时使用**： ...\n**如何**： ...\n**权衡**： ...`
- 最大 2,000 token

### cheatsheet.md
创建 `$SKILLS_HOME/<skill_name>/cheatsheet.md`：

**这是技能最差异化的层次——将其视为推理辅助工具，而不是关键词列表。** 任何人都可以通过 grep 查找术语。cheatsheet 捕获了作者的*判断*：他们会做出的决策和原因。这是将“我知道这些术语”转化为“我会像作者一样行动”的文件。

按顺序优先考虑：
1. **决策规则** — “在 X 时，做 Y，因为 Z。” 作者应用的 if/then 逻辑，这样读者可以在不重读书籍的情况下应用它。
2. **决策树/流程图**（作为嵌套项目符号或小表）——用于有两个以上分支的选择。
3. **权衡矩阵** — 在作者关心的维度上评分的竞争选项，以便读者可以根据自己的约束进行选择。
4. **阈值 & 默认值** — 作者承诺的具体数字、比率或规则（例如“保持函数在 ~20 行以内”、“当错误预算 < 10% 时发出警报”）。
5. **迹象 & 嗅觉** — 用于快速识别情况的启发式方法（“如果你看到 X，你可能在 Y 有麻烦”）。

避免：裸术语→定义行（那是术语表），和散文段落（那是章节）。每一行都应该帮助读者*做出*决定。

- 主要以紧凑表格和决策规则格式化；内容是你希望在旁边保持的单页打印页，以便在工作时参考。
- 最大 1,200 token。

---

## 第 9 步 — 生成主 SKILL.md

**关键 TOKEN 预算：保持 SKILL.md 正文在 4,000 token 以下。**
压缩会从末尾截断——将最重要的内容放在最前面。

创建 `$SKILLS_HOME/<skill_name>/SKILL.md`：

```markdown
---
name: <skill_name>
description: "来自 \"<完整标题>\" 的知识库，作者为 <作者>。在应用 <作者> 的框架以 <关键主题，3–6 个术语>、学习这本书或引用其概念时使用。"
---

<!-- argument-hint: [主题、框架名称或章节编号] -->

# <完整标题>
**作者**: <作者> | **页数**: ~<N> | **章节**: <N> | **生成**: <YYYY-MM-DD>

## 如何使用此技能

- **无参数** — 加载核心框架以供参考
- **带主题** — 询问关于 `replication`、`pricing` 或其他索引主题；我会找到并读取相关章节
- **带章节** — 询问 `ch05`；我会加载该特定章节
- **浏览** — 询问“你有哪些章节？”以查看完整索引

当你询问一个在以下核心框架中未涵盖的主题时，我会在回答之前读取相关章节文件。

---

## 核心框架 & 思维模型
<!-- ~2,000 token：作者最重要的命名框架和原则。
     保留确切名称。写为“在 X 时使用 Y”、“优先选择 X 而不是 Y，因为 Z”。
     这是一个工具包，而不是摘要。 -->

<在此处生成 2,000 token 的最关键框架和见解>

---

## 章节索引

| # | 标题 | 主要框架 |
|---|-------|----------------|
| [ch01](chapters/ch01-<slug>.md) | <标题> | <framework1>, <framework2> |
| [ch02](chapters/ch02-<slug>.md) | <标题> | <framework1>, <framework2> |
...

## 主题索引

<!-- 按字母顺序排列。主要术语/框架 → 涵盖它们的章节。 -->
- **<术语>** → ch<N>[, ch<N>]
- **<术语>** → ch<N>

## 支持文件

- [glossary.md](glossary.md) — 所有关键术语及其定义
- [patterns.md](patterns.md) — 所有技术和设计模式
- [cheatsheet.md](cheatsheet.md) — 快速参考表格和决策指南

---

## 范围 & 限制

此技能仅涵盖书籍内容。对于在您的代码库中的实际应用，
请结合项目特定工具。对于本书以外的主题，请检查相关技能
或直接询问代理。
<如果 images_dropped > 5: 说明未读取 N 张源图像>
```

---

## 第 9.5 步 — 扫描生成的技能

在报告成功、在另一个会话中加载技能或发布之前，运行建议的安全扫描：

```bash
SKILL_CONVERTER_ROOT="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
"$PYTHON_BIN" "$SKILL_CONVERTER_ROOT/tools/scan_generated_skill.py" "$SKILLS_HOME/<skill_name>"
```

如果扫描器以非零状态退出，停止并要求人工审查其文件/行发现。不要在生成文件上静默重写，直到发现的问题得到解决或明确接受，才加载或发布技能。

---

## 第 10 步 — 清理和报告

如果主机是 Claude Code 且 `SKILLS_HOME` 是 `~/.agents/skills`（默认个人安装），通过符号链接将技能暴露给 Claude Code — Claude Code 仅扫描 `~/.claude/skills`：

```bash
mkdir -p "$HOME/.claude/skills"
LINK="$HOME/.claude/skills/<skill_name>"
TARGET="$HOME/.agents/skills/<skill_name>"
if [ -d "$LINK" ] && [ ! -L "$LINK" ]; then
  CLAUDE_STATUS="skipped-realdir"                 # 第 5 步迁移拒绝；保留旧目录
else
  ln -sfn "$TARGET" "$LINK" 2>/dev/null || true
  # 读取链接回 — 不要相信 `ln` 是否按请求执行。在 Windows/MSYS
  # `ln -s` 可能复制而不是链接（或需要开发者模式 / 提升权限的 shell），并且
  # PowerShell/cmd 完全没有 `ln`。报告必须反映磁盘上的情况，而不是命令执行的事实。
  if [ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$TARGET" ]; then
    CLAUDE_STATUS="linked"
  elif [ -e "$LINK" ]; then
    CLAUDE_STATUS="copy"                           # 实际文件/目录落位而不是链接
  else
    CLAUDE_STATUS="absent"                         # `ln` 不可用或拒绝
  fi
fi
```

实际目录保护是必需的：`ln -sfn` 到现有实际目录会将链接嵌套在其中 (`~/.claude/skills/<skill_name>/<skill_name>`), 导致 Claude Code 加载过时的副本。如果用户拒绝了第 5 步迁移，跳过符号链接并在报告中说明 — Claude Code 会继续使用旧目录，直到迁移完成。

**在报告任何关于它的信息之前，请先读取链接。** 符号链接是一个声明，不是事实：从 `CLAUDE_STATUS`（磁盘上实际的内容）填充“可发现”行，而不是“命令已发出”。**当链接缺失或是一个复制时，不要硬失败** — 技能存在于中心，其他主机仍然可以找到它；诚实的报告是“写入到 `~/.agents/skills/<skill_name>`；Claude Code 不会看到它，直到链接创建”，而不是中止。 (Windows 领导，未验证：一个目录连接 — 在提升权限的 `cmd` 中使用 `mklink /J`，或在 PowerShell 中使用 `New-Item -ItemType Junction` — 既不需要开发者模式也不需要符号链接权限；如果你尝试它，它不会改变读取回然后报告的规则。)

当用户选择主机私有或项目本地根（第 5 步，规则 3-4）时，跳过此步骤。

然后清理提取工作目录：

```bash
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

删除**此运行实际使用的工目录** — 提取输出的 `Workdir ->` 路径，它也存储为 `metadata.json` 中的 `workdir`。永远不要删除你没有创建的目录：另一个提取可能正在你的旁边运行。

```bash
# WORKDIR 是此运行报告的路径；如果路径中有空格，请引号包裹。
rm -rf "$WORKDIR"
```

或者，如果你仍然有元数据文件：

```bash
"$PYTHON_BIN" - "$WORKDIR_METADATA_JSON" <<'PY'
import json
import shutil
import sys
from pathlib import Path

meta_path = Path(sys.argv[1])
workdir = json.loads(meta_path.read_text(encoding="utf-8")).get("workdir")
if workdir:
    shutil.rmtree(workdir, ignore_errors=True)
PY
```

此文件的旧版本删除了一个固定的 `book_skill_work` 目录。该路径不再使用，因此这种清理现在是无害的 no-op，而不是可能删除并发运行输出的操作。

然后向用户报告：

```
✅ 技能创建：$SKILLS_HOME/<skill_name>/

📚 书籍：<全标题> — <作者>
📄 页面：~<N> | 章节：<N>

生成的文件：
  SKILL.md         — 核心框架 + 索引   (~X tokens)
  chapters/        — <N> 章节摘要     (~X tokens 每个，~X 总计)
  glossary.md      — 关键术语                 (~X tokens)
  patterns.md      — 技巧 & 模式     (~X tokens)
  cheatsheet.md    — 快速参考           (~X tokens)
  ─────────────────────────────────────────────────────
  技能总大小：~X tokens（按需加载，不是一次性全部加载）

💡 提示：检查你的代理的会话成本/使用命令，以查看实际 token 使用情况。

使用方法：
  询问 <skill_name>                  → 加载核心框架
  询问 <skill_name> 关于 <主题>        → 查找并解释一个主题
  询问 <skill_name> 对于 ch<N>            → 深入特定章节

可发现： <仅对所选目标真实的内容 — 见下文>

其他地方？  mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> \
                   && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>

每个文件都请求权限？这是你的主机限制工作目录外写入的答案。说“保存到此项目中”并重新运行以在它内部写入。

重新加载（如果你的代理不自动检测新技能）：
  GitHub Copilot CLI:  /skills reload
  Claude Code:         重新启动会话
  Amp:                 重新启动会话
  Hermes Agent:         启动新会话
  OpenClaw:             openclaw skills list (如果禁用监视器则为新会话)

分享此技能（可选）：
  GitHub 仓库，可在任何主机上安装（第 11 步）：  说“发布”
  Copilot 生态系统：  gh skill publish $SKILLS_HOME/<skill_name>
```

从 `CLAUDE_STATUS`（读取回结果）填充“可发现”行，而不是 `ln` 运行的实际情况 — 对于 `~/.agents/skills` 安装：
- `linked` → "Copilot CLI, Amp, Codex (原生)；Claude Code 通过符号链接 ~/.claude/skills/<skill_name>"
- `skipped-realdir` → "Copilot CLI, Amp, Codex (原生)；**不** Claude Code — 首先迁移实际目录到 ~/.claude/skills/<skill_name>"
- `copy` 或 `absent` → "Copilot CLI, Amp, Codex (原生)；**不** Claude Code — 主机无法创建符号链接（一个纯复制会在下一次 Update/Fold-in 中漂移）。启用开发者模式 / 手动创建链接，或从 ~/.agents/skills 运行技能"
- Hermes Agent 个人根 → "Hermes Agent (从 `$HERMES_HOME/skills/<category>`)"; 没有符号链接声明，也没有跨代理声明，因为其他主机不扫描 Hermes 根
- 其他主机私有或项目本地根 → 仅命名扫描该根的主机；没有符号链接声明

“其他地方？”重新定位行必须对实际使用的路径正确，因此它永远不会破坏运行刚创建的符号链接。**`mv` 始终针对最终技能目录 `<dest_root>/<skill_name>`，而不是 `<dest_root>` 本身。** `mv ~/.agents/skills/mybook ~/.copilot/skills && ln -sfn ~/.copilot/skills ~/.claude/skills/mybook` 看起来有效，并且不是：技能落在 `~/.copilot/skills/mybook`，而链接指向上一级在根，所以 Claude Code 解析到一个没有 `SKILL.md` 的目录，这正是此行存在的目的避免的。替换用户实际命名的目标，以便打印的命令包含真实路径，并且没有剩余的解释：
- `~/.agents/skills` + 符号链接 → `mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>`
- 主机私有根，包括 Hermes Agent → `mv <src_root>/<skill_name> <dest_root>/<skill_name>`
- 项目本地根 → `mv <project_root>/<skill_name> <dest_root>/<skill_name>`

“每个文件都请求权限？”行是主机限制工作目录外写入的答案（任何个人范围根都在工作目录外）：目的地已在上面宣布，并且旁边有一个单行修复 — 重新运行以在它内部请求项目本地根。仅保留个人范围安装；当用户已经选择了项目本地时，删除它。

---

## 第 11 步 — 将生成的技能发布到 GitHub（可选）

在第 10 步报告后，仅当第 9.5 步扫描通过时，提供一次 — 并且仅此一次：

> "我想将此技能发布到 GitHub，以便任何 Agent Skills 主机都可以使用 `npx skills add` 安装它？(是 / 跳过)"

如果用户拒绝，停止在此。要求：`gh` CLI，已认证（检查 `gh auth status`）。如果 `gh` 缺失或未认证，提供设置它的选项 (`brew install gh` 或 https://cli.github.com，然后 `gh auth login`) — 或者使用无 `gh` 路径：用户在 GitHub 网页 UI 中创建一个具有所选可见性的空仓库，然后你运行下面的 `git init`/`add`/`commit` 命令，然后 `git remote add origin <repo-url> && git push -u origin main`。下面的可见性规则对网页创建的仓库完全相同。

**可见性是一个独立的封闭问题 — 永远不推断，永远不从未知答案中读取。** 一旦用户接受，单独询问它，并要求一个单词的回复：

> "私有或公共仓库？回复一个单词：`private` 或 `public`。”

**回复必须是 `public`，而不仅仅是包含它 — 这是一个硬性规则，不是建议。** 在所有情况下，除了一个：可见性问题的答案是裸词 `public`。子字符串匹配是禁止的，因为关于 **源许可证的句子不是可见性答案** — "它是公共领域"，"书是公共领域"，"它是公开可用的" 都描述了材料，而不是仓库，并且都解析为 `--private`。释义、句子、模糊答案、沉默或你自己的推断都不是同意：重新询问一次，如果回复仍然不是裸词，则使用 `--private` 并在报告中说明。私有仓库可以稍后变为公共；书籍衍生内容的公共推送无法撤回。

**版权门 — 始终在创建仓库之前应用：** 章节文件是综合摘要，不是原始文本，但它们仍然源自源材料。根据 README 的版权 & 合理使用政策，从第三方版权书籍生成的技能必须保持私有；仅在源是用户自己的写作、开放许可的内容或用户明确确认他们有权公开重新分发时提供公共，并说明哪种情况适用。有内部公司材料访问权限并不意味着你有权披露它：来自内部文档的技能保持 **私有**，除非用户声明他们拥有发布权利。

如果接受：

1. 在 `$SKILLS_HOME/<skill_name>/` 内添加一个仓库 `README.md`（永远不要覆盖现有文件）— 技能标题、一个段落描述（“Agent 技能由 <Author> 使用 [book-to-skill](https://github.com/virgiliojr94/book-to-skill) 从 *<Title>* 生成的”）、第 3 步的安装命令、文件清单，以及一个说明内容是综合摘要，不是书文本的注释。
2. 将技能文件夹初始化为 git 仓库并创建远程（默认仓库名 `<skill_name>`；允许用户覆盖 — 有些人更喜欢 `<skill_name>-skill` 后缀）。**嵌套仓库保护：** 首先检查技能文件夹是否已经位于一个 git 仓库中 (`git -C "$SKILLS_HOME/<skill_name>" rev-parse --show-toplevel` — 对于 `.claude/skills/` 等项目本地根始终如此）。如果它确实如此，不要在原地 `git init`：外层仓库会将文件夹记录为嵌入仓库（gitlink，模式 160000）而没有 `.gitmodules`，并且外层项目的最新克隆会静默忽略技能。相反，将技能文件夹复制到临时目录，从副本运行下面的命令，并告诉用户发布的仓库 — 不是项目本地文件夹 — 是远程的工作副本。

```bash
cd "$SKILLS_HOME/<skill_name>"
git init -b main
git add -A
git commit -m "添加 <skill_name> 技能"
gh repo create <repo_name> --private --source . --push
# --private 是默认值；仅在上述可见性规则下替换 --public
# (可见性答案是裸词 "public" 并且版权门允许它)
```

3. 报告仓库 URL 和跨主机安装命令：

```
✅ 发布：https://github.com/<owner>/<repo_name> (<private|public>)
```

在任何 Agent Skills 主机上安装：
  npx skills add https://github.com/<owner>/<repo_name> --skill <skill_name>
```

   当嵌套仓库守卫触发并且仓库是从一个草稿副本发布时，添加一行——这个本地文件夹永远不会获得远程仓库，所以 Update/Fold-in 推送提议将永远不会出现：

```
⚠️  从副本发布：<skill 文件夹> 位于另一个 git 仓库内部，所以它没有
    自己的远程仓库。要发布后续更新，请重新运行第 11 步，或者克隆
    https://github.com/<owner>/<repo_name> 并将新材料合并到克隆的副本中。
```

根级别的 `SKILL.md` 布局正是 `skills` CLI 检测到的内容，所以仓库可以原样安装——无需重新结构化。在嵌套仓库情况下之外，本地文件夹保持为这台机器的实时安装，并且是远程仓库的工作副本，所以后续的 Update/Fold-in 运行可以将其更改提交并推送到同一个远程仓库。

---

## 更新 / 合并工作流

当对 `$SKILLS_HOME/<skill_name>/` 中的现有技能执行 Update/Fold-in 操作时：

### 1. 读取现有技能结构
读取并解析现有技能的文件：
- 读取 `$SKILLS_HOME/<skill_name>/SKILL.md` 以解析现有的 **章节索引**、**主题索引**、元数据（作者、总章节数）和 **核心框架**。
- 列出 `$SKILLS_HOME/<skill_name>/chapters/` 中的所有文件，以找到最高的章节编号（例如 `ch12`）。
- 读取 `$SKILLS_HOME/<skill_name>/glossary.md`、`$SKILLS_HOME/<skill_name>/patterns.md` 和 `$SKILLS_HOME/<skill_name>/cheatsheet.md`，以查看已经索引的术语和框架。

### 2. 匹配内容并识别修订与新增
分析本次运行中 `full_text.txt`（从提取输出中的 `Text ->` 路径）中的新提取文本，以识别新内容是否代表：
- **对现有章节的更新/修订**：如果新内容中的某个部分直接更新或扩展了现有章节的主题，则读取现有章节文件，将新细节合并到其中，并重写文件。
- **新增内容**：如果内容引入了新章节、论文或独立部分，则在 `chapters/` 下创建 **新的章节摘要文件**。从现有最高章节编号之后开始编号这些文件（例如，如果现有章节到 `ch12` 结束，则创建 `ch13-*.md`、`ch14-*.md` 等）。

### 3. 生成或更新章节摘要文件
对于每个新修订的章节：
- 读取提取的新文本的相应部分。
- 遵循 **第 7 步** 中的格式指南来构建摘要。
- 在 `$SKILLS_HOME/<skill_name>/chapters/` 中写入/更新文件。

### 4. 合并支持文件
- **合并 glossary.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/glossary.md`。
  - 从新内容中提取所有新术语和定义（第 8 步的 glossary 指南）。
  - 合并并按字母顺序排列现有和新术语的列表。
  - 如果术语已存在，则将新的章节/来源引用追加到它（例如 `**术语** — 定义 (Ch 4, Ch 13)`）。
  - 使用完全合并的、按字母顺序排列的列表重写 `$SKILLS_HOME/<skill_name>/glossary.md`。
- **合并 patterns.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/patterns.md`。
  - 从新内容中提取任何新技术、算法或模式。
  - 追加新模式，确保格式一致，并保持总长度简洁（少于 2,500 个 token）。
- **合并 cheatsheet.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/cheatsheet.md`。
  - 提取新的比较规则、决策表或参数指南。
  - 将它们干净地集成到速查表结构中。

### 5. 重新生成主 SKILL.md
更新主技能文件 `$SKILLS_HOME/<skill_name>/SKILL.md`：
- **元数据**：增加章节数量，更新估计页数，并在适当的情况下添加新的来源名称。将 `Generated` 日期更新为当前日期。
- **核心框架**：将新内容中最具影响力的心智模型或原则合并进来（确保整个文件长度保持在 4,000 个 token 以下）。
- **章节索引**：将新章节追加到索引表格中，链接到新创建的文件。
- **主题索引**：按字母顺序合并新主题。如果现有主题也在新章节中涵盖，则将其新章节链接追加到该行（例如 `- **主题** → ch05, ch13`）。

### 6. 扫描、清理和报告
一旦文件成功写入和合并，运行 **第 9.5 步**，然后继续到 **第 10 步** 进行清理并打印自定义更新报告，总结新添加的章节、合并的术语和更新的索引。如果技能文件夹是一个具有远程仓库的 git 仓库（通过 **第 11 步** 发布），则提供提交更新并推送的选项。

---

## 质量规则

1. **提取结构，而非摘要** — 捕获命名框架、精确表述、反模式；不是章节回顾
2. **保留作者的精确性** — "The 5 Whys" ≠ "多次问为什么"；保持精确命名
3. **密度优先于完整性** — 1,000 个 token 的摘要胜过 10,000 个 token 的摘录
4. **实践者语气** — 写 "在 Y 时使用 X"，而不是 "书籍解释 X"
5. **SKILL.md 优先** — 压缩保留前 5,000 个 token；最重要的内容放在最前面
6. **章节文件按需生成** — 它们只有在加载时才计入技能预算
7. **永不复制原始书籍文本** — 始终综合、摘要、提取信号
8. **主题索引至关重要** — 它是代理导航到正确章节文件的方式
