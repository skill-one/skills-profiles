---
name: book-to-skill
description: 将书籍和文档（PDF、EPUB、DOCX、HTML、Markdown、纯文本、RTF、MOBI/AZW，使用Calibre转换MOBI/AZW）转换为结构化的代理技能，提取框架、心智模型、原则、技巧和反模式。当用户希望通过GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenCode或OpenClaw学习文档时，或在工作中应用作者的框架，或从文件构建可重用的知识库时使用。
---

交叉代理备注（信息性；主机代理忽略）：
  - 兼容技能根：GitHub Copilot CLI (~/.copilot/skills, ~/.agents/skills, .github/skills, .claude/skills, .agents/skills), Amp (.agents/skills, ~/.config/agents/skills, ~/.config/amp/skills), Claude Code (~/.claude/skills), Hermes Agent ($HERMES_HOME/skills, .hermes/skills, .agents/skills), OpenClaw (${OPENCLAW_STATE_DIR:-~/.openclaw}/skills, .agents/skills, skills/; ~/.agents/skills 仅在默认状态下使用)。OpenCode (~/.config/opencode/skills, ~/.claude/skills, .opencode/skills, ~/.agents/skills, .agents/skills)。
  - `allowed-tools` 故意省略以保持代理中立：Copilot CLI 使用 `shell`/MCP-server 名称，Claude 使用 `Bash`/`Read`/`Write`/`Glob`/`Grep`，Amp 添加 `shell_command`。该技能需要 shell（以运行 extract.py）和文件读写——每个主机将在首次使用时提示这些内容。
  - 参数提示：<文档文件夹路径或通配符>... [技能名称缩写]

# 书籍到技能转换器

通过提取结构而非生成摘要，将书面知识转化为可操作的代理技能。

## 哲学

书籍包含结晶化的专业知识：花费数年开发的框架、原则和技术。此技能将这种知识提取为 GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenCode、OpenClaw 或其他兼容代理可以重复利用的格式。
**提取结构，而非摘要。** 技能不是书评。它是一套工具箱，包含：
- 命名框架（具有明确应用的思维模型）
- 可操作的准则（指导决策的规则）
- 技术（分步方法）
- 反模式（避免的内容和原因）
- 语气校准（作者的思维和沟通方式）

**保留作者的精确性。** 框架通常有特定名称的原因。 "五个为什么" 不能与 "多次询问为什么" 互换。捕获确切的表述。

**适当分层深度。** 简单书籍 → 简单技能。具有 10 个以上框架的复杂书籍 → 具有参考文件和按需章节的技能。

---

## 操作模式

有四种路径可用。根据用户请求进行路由：

### 1. 完整转换（默认）
**触发：** 用户提供一个或多个文档/目录/通配符路径而没有特殊说明
**操作：** 运行以下所有步骤（步骤 0–9）
**输出：** 完整技能，包含 SKILL.md、chapters/、词汇表、模式、速查表

### 2. 仅分析
**触发：** 用户说 "analyze"、"just extract" 或 "我想在生成之前进行审查"
**操作：** 运行步骤 0–3，然后生成结构化提取报告（发现的框架、原则、技术）。停止——不要生成技能文件。
**输出：** 供用户审查的分析报告

### 3. 从先前的分析生成
**触发：** 用户有现有的分析笔记或之前运行了仅分析
**操作：** 跳过步骤 0–3，使用提供的分析作为输入，运行步骤 4–9
**输出：** 从提供的分析生成的技能文件

### 4. 更新/合并（现有技能）
**触发：** 用户提供一个或多个新源路径并指示他们要更新现有技能（通过指向现有技能文件夹、提供已存在于 `SKILLS_HOME` 中的技能缩写，或明确请求更新）。
**操作：** 运行步骤 0（范围外检查）、步骤 1（验证输入）、步骤 1.5（识别书籍类型）和步骤 2（提取新文件）。然后跳到步骤 5（识别/检测现有技能路径）并运行 **更新/合并工作流** 将新内容合并到现有技能文件中。
**输出：** 更新后的现有技能，包含新的/修订的章节摘要和合并的索引/词汇表。

---

## 技能位置

此转换器可以从多个技能系统运行。在查找此转换器的辅助脚本或编写生成的书籍技能时，按顺序优先选择这些位置：

1. GitHub Copilot CLI 个人技能：`~/.copilot/skills/`
2. 跨代理个人技能（Copilot、Amp、Codex；默认状态下的 OpenClaw）：`~/.agents/skills/`
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
11. OpenCode 个人技能：`~/.config/opencode/skills/` 或 `~/.agents/skills/`
12. OpenCode 项目技能：`.opencode/skills/` 或 `.agents/skills/`

对于 **生成的** 书籍技能，优先选择用户级跨代理根 `~/.agents/skills/`——一个物理副本服务于跨代理主机和默认状态下的 OpenClaw。Copilot CLI 和 Amp 原生发现它；Claude Code 需要从 `~/.claude/skills/<skill_name>` 创建符号链接（在步骤 10 中创建，见步骤 5 的规则）。仅在用户明确要求时选择主机私有或项目本地根。`BOOK_TO_SKILL_SCOPE=project` 或 `personal` 可以使该选择对自动化显式；不要因为两个范围都可用而强制询问范围问题。

---

## 步骤 0 — 范围外检查

如果未提供任何参数，停止并响应：
> "book-to-skill 需要一个支持的分文档路径、文件夹或通配符模式。用法：`book-to-skill <path-to-document-folder-or-glob>... [skill-name-slug]`"

在整个工作流中：
- **首先解析目标根。** 在任何现有技能查找之前，确定此运行将写入的位置：用户主机的主机级或项目本地根，根据步骤 5 表格和选择规则——项目本地请求使用其项目本地根，永远不会使用个人根。下面，“解析的根”是指该目的地。
- 识别输入路径和可选的技能缩写。
- 如果最后一个参数不是存在的文件、文件夹或通配符，并且看起来像技能缩写（例如小写连字符、字母数字），将其视为 `SKILL_NAME`。
- 将所有其他参数视为 `INPUT_PATHS` 列表。
- 如果任何输入路径是现有技能目录（包含 `SKILL.md` 和 `chapters/` 子文件夹），或者 `SKILL_NAME` 匹配解析根中的现有技能缩写，将此运行标记为 **更新/合并** 操作（模式 4）。
- **重新运行守卫。** 在为完整转换开始提取之前，根据步骤 5 的命名选项派生潜在技能缩写——作者概念形式、按标题形式和任何给定的 `SKILL_NAME`——并检查解析根中是否存在匹配项。存在匹配项时，停止并询问用户："`<skill-name>` 已存在。选择：(1) 更新/合并（模式 4），(2) 验证现有技能是否完整并停止，或 (3) 强制完整再生。" 不要重新提取，直到用户选择。在断开连接后恢复上下文（网络中断、重播或继续对话）时，如果该目录仍然完整且仍然匹配当前输入和选项，则重用该运行报告的提取工作目录（`Workdir ->` 在其输出中，或您在 `BOOK_SKILL_WORKDIR` 中设置的路径）**——该目录存在，其 `metadata.json` 可读，它列出的 `sources` 与要转换的文件在文件名和内容指纹上一对一匹配（提取器在 `metadata.json` 中记录每个源的 `sha256`；重新计算当前每个文件的指纹并要求完全匹配——`reuse_is_safe()` 在 `book_to_skill/utils.py` 中是此检查的可执行形式）。如果它丢失（临时清理）、其 `metadata.json` 已丢失、源不再匹配（不同的文件名，或改变了内容指纹）、记录的元数据没有为源记录 `sha256`（记录指纹之前，因此无法确定新鲜度），或模式不同，请说明并开始全新提取而不是恢复。如有疑问，在丢弃或恢复之前先询问用户。

---

## 步骤 1 — 验证输入

验证至少有一个支持文件、文件夹或通配符模式在 `INPUT_PATHS` 中。
对于目录和通配符，将它们展开以找到匹配的支持文件（`.pdf`、`.epub`、`.docx`、`.txt`、`.md`、`.markdown`、`.rst`、`.adoc`、`.html`、`.htm`、`.rtf`、`.mobi`、`.azw`、`.azw3`）。

如果找不到支持文件，停止并显示清晰的错误消息。

---

## 步骤 1.5 — 识别内容类型

在提取之前，询问用户：

> "这些源包含什么类型的内容？这有助于我选择最佳提取方法。
>
> 1. **技术**——包含代码块、表格、公式、图表（例如编程书籍、学术论文、建筑指南）
> 2. **文本密集型**——主要是散文，几乎没有或没有表格/代码（例如管理、生产力、叙事非虚构）
> 3. **不确定**——我将使用快速方法，如果质量似乎有限，我会警告你"

将答案存储为 `BOOK_TYPE`：
- 选项 1 → `BOOK_TYPE=technical`
- 选项 2 → `BOOK_TYPE=text`
- 选项 3 → `BOOK_TYPE=text`

**如果 `BOOK_TYPE=technical`**，在继续之前通知用户：
> "📐 技术模式已选择——使用 Docling 进行结构感知提取（保留表格、代码块、公式为 markdown）。这需要大约每页 1.5 秒，因此对于较长的源，请预期几分钟。现在开始…"

**如果 `BOOK_TYPE=text`**，通知：
> "📄 文本模式已选择——使用最适合每种文件类型的提取器。纯文本/Markdown/HTML 通常在几秒钟内准备好；PDF 使用 pdftotext（如果可用）。"

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
  "$HOME/.config/opencode/skills/book-to-skill/scripts/extract.py"
  "$HERMES_HOME_RESOLVED/skills/book-to-skill/scripts/extract.py"
  "$HERMES_HOME_RESOLVED"/skills/*/book-to-skill/scripts/extract.py
)
if [ "${HERMES_AGENT:-}" != true ]; then
  # 项目本地根针对 git 工作树，而不是当前目录：代理可以从项目的任何位置调用（例如 `src/nested`），这些根仍然需要找到——这就是 OpenCode 和其他主机发现项目技能的方式。保留相对于当前目录的符号形式，以便在 git 仓库外也工作。
  if [ -n "$PROJECT_ROOT" ]; then
    CANDIDATES+=(
      "$PROJECT_ROOT/.github/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.claude/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.agents/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.opencode/skills/book-to-skill/scripts/extract.py"
    )
  fi
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
    ".opencode/skills/book-to-skill/scripts/extract.py"
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

**提示——预检环境：** 运行 `"$PYTHON_BIN" "$SCRIPT_PATH" --check` 以打印每种格式的报告，说明已安装哪些提取器以及确切的安装命令，而不会处理任何文件。在用户报告设置或质量问题时很有用。

这会创建一个 **每次运行** 的工作目录——`<tempdir>/book_skill_work-<pid>/` 默认，或您在 `BOOK_SKILL_WORKDIR` 中设置的精确路径——包含：
- `full_text.txt` — 所有源组合提取的文本，具有清晰的视觉边界。
- `metadata.json` — 总组合大小、单词数、页数、令牌计数、丢弃的 EPUB 图片计数、解析的 `workdir`，以及详细的单个处理 `sources` 列表。

完成运行时，它会打印所有三个路径（`Workdir ->`、`Text ->`、`Meta ->`）。**从该输出（或从 `metadata.json` 的 `workdir` 字段）获取路径，而不是假设固定位置**——每个运行的目录名称不同，因此同一台机器上的并发提取不会互相覆盖结果。

读取该运行的 `metadata.json` 以检查结果。

**始终在生成任何内容之前确认提取的文档是否为你所请求的文档**：检查 `metadata.json` 中的 `filename` / `source_file`，或在 `full_text.txt` 的第一行 `SOURCE:` 标题中查找。如果你正在等待后台运行，请等待 *其* 特定的工作目录——轮询共享路径可能会暴露不同运行的输出。

---

## 第 2.5 步 — 预飞行成本估算

在执行任何生成操作之前，读取此运行的 `metadata.json`（从提取输出中的 `Meta ->` 路径），并向用户提供一个估算：

```
📖 检测到的源：<total_sources> 个源
列出每个源文件名和格式（来自源元数据列表）
<如果 images_dropped > 5：警告未读取的 N 个源图像>
📄 合并页面/章节：~<N> | 字数：~<N> | 总令牌数：~<N>K

💰 预估令牌成本（完整转换 / 更新）：
   输入（读取 + 提示）：~<N>K 令牌
   输出（生成的/更新的技能文件）：~<N>K 令牌
   总计：                           ~<N>K 令牌

   成本：将上述令牌计数乘以你模型的当前输入/输出每 100 万令牌的费率（价格和模型名称经常变化——不要硬编码它们；引用今天的费率并标记为估算）。

   ⏱ 预估时间：~<N> 分钟

📁 将要生成/更新的文件：
   SKILL.md + 章节文件 + 词汇表 + 模式 + 折叠表

➡  继续进行完整转换 / 更新？ （或输入 "仅分析" 以预览）
```

**如何估算：**
- 输入令牌 ≈ `estimated_tokens` 从元数据 × 1.3（每章节传递的提示开销）
- 输出令牌 ≈ 章节 × 每章节预算 + 4,000（SKILL.md）+ 4,500（词汇表 + 模式 + 折叠表）
  - 根据 `BOOK_TYPE` 确定的每章节预算中点（DEPTH 在步骤 4 中稍后决定并可能提高）：`text` ≈ 1,000，`technical` ≈ 1,800。如果用户已经指示了仅参考与深度学习，请使用步骤 7 矩阵的匹配行。
- 成本：报告令牌计数并乘以用户的当前每 100 万令牌输入/输出费率。不要硬编码美元金额——模型名称和价格会变化；如果你显示一个，请将其标记为估算并注明日期。

在用户确认之前等待。如果他们说 "仅分析"，请切换到模式 2。

---

## 第 2.6 步 — 大型书籍（> 50k 令牌）的 REPL 风格访问

受递归语言模型（RLM）范式的启发：将 `full_text.txt` 视为可查询的语料库，而不是一次性读取。将整个文件加载到上下文中会消耗你稍后生成所需的预算。

对于超过 ~50k 令牌的书籍，请优先选择程序化探测，而不是无限制的 `Read(full_text.txt)`：

```bash
# 在任何 Read 之前进行大小检查
wc -w "$FULL_TEXT_PATH"

# 在不加载整个文件的情况下查找章节偏移量
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# 仅提取您需要的章节（行从 start 到 end，包含在内）
sed -n '<start>,<end>p' "$FULL_TEXT_PATH"

# 在 SKILL.md 中声明之前，验证框架是否确实被提及
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"

# 带有偏移量/限制的定向 Read 避免转储整个文件
# Read(file_path=full_text.txt, offset=<line>, limit=<lines>)
```

使用此方法进行步骤 3（结构分析）、步骤 7（每章节摘要）和步骤 8（词汇表 / 模式提取）。对于少于 50k 令牌的书籍，单个 `Read` 即可。

为什么这很重要：一本 200 页的书约为 75k 令牌。每章节重新读取一次（28 次）的成本约为 2M 输入令牌；使用 grep + sed 仅提取相关片段可将生成成本与输出保持比例，而不是源。

---

## 第 3 步 — 分析书籍结构

读取提取的 `full_text.txt` 的前 8,000 个字符，以识别：
- 书籍 **标题** 和 **作者**
- **章节结构**（查找 "Chapter N"、"PART I"、编号标题、目录）
- **核心主题** 和学科领域
- 章节的大致数量

然后如果存在，读取目录部分以映射所有章节。

**如果模式是 "仅分析"：** 现在生成提取报告并停止。结构：

```
## 提取报告 — <标题>

### 作者的核心框架
- **<框架名称>**：<是什么以及何时应用>

### 关键原则
- <原则>：<可操作的规则>

### 技巧与方法
- <技巧>：<分步或如何操作>

### 反模式
- <要避免的>：<原因>

### 建议的技能名称
`{author-lastname}-{核心概念}` — 例如 `cialdini-influence`

### 检测到的章节
| # | 标题 | 主要框架 |
```

---

## 第 4 步 — 询问目的（仅完整转换）

在生成之前，询问用户：

> "这个技能应该帮助你做什么？（选择一个或多个）
> 1. 在工作时应用作者的框架
> 2. 使用作者的思维模型进行思考
> 3. 引用特定章节和概念
> 4. 以上所有"

使用答案来权衡 SKILL.md 核心部分突出显示的内容。

**根据答案推导 `DEPTH`（无需额外提示）：**
- 答案**仅**是选项 3（参考）→ `DEPTH=reference` — 轻量级、快速查找章节。
- 答案包括选项 1、2 或 4 → `DEPTH=study` — 更深入的章节，包含更多已完成的细节、示例和推理。

`DEPTH` 和 `BOOK_TYPE` 一起在步骤 7 中设置每章节令牌预算。**不要**单独询问 "学习与参考" 的问题——在这里推断。 (在模式 2/3 中，跳过步骤 4，默认 `DEPTH=study`。)

---

## 第 5 步 — 确定技能名称

如果提供了 `SKILL_NAME`，则将其用作技能缩写。
否则，提供两个选项并让用户选择：
- **按作者概念**：`{author-lastname}-{核心概念}`（例如 `cialdini-influence`，`meadows-systems`）
- **按标题**：从书名中提取的小写连字符（例如 `designing-data-intensive-apps`）

如果书籍具有强烈的方法论身份，则默认为作者概念格式。

选择目标技能根 (`SKILLS_HOME`)。首先从显式的用户请求或 `BOOK_TO_SKILL_SCOPE` 中解析**范围**，然后探测**主机**。对项目本地/项目输出的请求选择项目本地行；对个人/全局输出的请求选择个人行。如果未请求任何范围，则保留已建立的默认个人设置（`~/.agents/skills` 对于非 Hermes 主机）。仅因为存在项目本地根而强制请求范围问题。选择的根可能仍需要在写入之前获得主机批准。

| 主机代理 | 个人技能根 | 项目本地根 |
|---|---|---|
| **GitHub Copilot CLI** | `~/.agents/skills`（原生发现） | `.github/skills` → `.claude/skills` → `.agents/skills` |
| **Amp** | `~/.agents/skills`（原生发现） | `.agents/skills` |
| **OpenAI Codex** | `~/.agents/skills`（原生发现；遵循符号链接） | `.agents/skills` |
| **Hermes Agent** | `$HERMES_HOME/skills/<category>`（默认为 `~/.hermes/skills/<category>`） | `.hermes/skills/<category>` → `.agents/skills` |
| **Claude Code** | `~/.agents/skills` + 从 `~/.claude/skills/<skill_name>` 创建的符号链接 | `.claude/skills` |
| **OpenClaw** | `${OPENCLAW_STATE_DIR:-~/.openclaw}/skills`（活动状态；`~/.agents/skills` 仅在默认状态下） | `.agents/skills` → `skills/` |

Hermes Agent 是唯一保留其个人根的主机：它按类别划分个人技能，并且不扫描跨代理根。使用活动配置文件的 `HERMES_HOME` 并选择与生成的技能主题匹配的类别。不要手动构建配置文件路径。如果用户选择项目本地 Hermes 根，生成后运行 `hermes skills trust <project-root>` 并使用 `hermes skills list` 验证发现；项目技能在项目被信任之前不可用。

对于 OpenClaw，使用活动状态目录的 `skills/` 根：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`。共享的 `~/.agents/skills` 兼容根仅在 `OPENCLAW_STATE_DIR` 未设置或等于默认 `~/.openclaw` 时可发现；对于非默认状态，不要声称 OpenClaw 将看到共享根安装。生成后使用 `openclaw skills list` 验证发现。
| **OpenCode** | `~/.agents/skills`（原生发现；`~/.config/opencode/skills` 和 `~/.claude/skills` 也被读取） | `.opencode/skills` → `.agents/skills` → `.claude/skills` |

Hermes Agent 是唯一保留其个人根的主机：它按类别划分个人技能，并且不扫描跨代理根。使用活动配置文件的 `HERMES_HOME` 并选择与生成的技能主题匹配的类别。不要手动构建配置文件路径。如果用户选择项目本地 Hermes 根，生成后运行 `hermes skills trust <project-root>` 并使用 `hermes skills list` 验证发现；项目技能在项目被信任之前不可用。

OpenCode 原生扫描跨代理的 `~/.agents/skills` 根，因此上述生成的技能默认已满足它——无需符号链接和信任步骤。它还读取其管理的 `~/.config/opencode/skills` 根和 Claude 兼容根 `~/.claude/skills`；仅在用户请求时使用 OpenCode 管理的根。项目技能通过从工作目录向上遍历到 git 工作树来发现，因此生成后如果技能未出现，请开始新会话。 (`~/.cache/opencode/skills` 是来自 `skills.urls` 的远程技能下载缓存，不是作者根——永远不会在那里写入生成的技能。)

选择规则：
1. 个人安装：将 `SKILLS_HOME` 设置为 `~/.agents/skills`（如果缺失则创建目录）。一个例外，因此默认不会在其他人的家里发明约定：如果 `~/.agents/skills` 不存在**并且**主机的私有根已经包含技能，则使用私有根，并在报告中说明原因。
2. **Claude Code 不扫描 `~/.agents/skills`**——生成完成后，步骤 10 使用 `ln -sfn "$HOME/.agents/skills/<skill_name>" "$HOME/.claude/skills/<skill_name>"` 将技能链接起来。
3. **Hermes Agent 个人安装使用上述 Hermes 行**，而不是跨代理根，并且不创建符号链接。
4. 如果用户明确要求主机私有根（`~/.copilot/skills`，`~/.claude/skills`，`~/.config/agents/skills`，`~/.config/amp/skills`），请尊重它并跳过符号链接。
5. 如果用户明确要求项目本地输出，请使用其主机的项目本地行。
6. 如果选择需要知道主机（项目本地输出、Hermes 个人根、OpenClaw 状态根或 Claude Code 符号链接）并且无法识别，请询问："你正在运行哪个代理——OpenCode、OpenClaw、Hermes Agent、GitHub Copilot CLI、Amp、Codex 或 Claude Code？"
7. 对于 OpenClaw 个人输出，使用 `${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/skills`。共享的 `~/.agents/skills` 根仅在 `OPENCLAW_STATE_DIR` 未设置或等于默认 `$HOME/.openclaw` 时才是有效的 OpenClaw 目标；否则使用活动状态根或项目/额外目录。
8. 如果用户明确要求 OpenClaw 管理的个人根，请使用活动状态根并使用 `openclaw skills list` 验证。

将 `SKILLS_HOME` 设置为选定的根并检查 `$SKILLS_HOME/<skill_name>/` 是否已存在。在 Claude Code 中，还检查 `~/.claude/skills/<skill_name>` 是否存在作为**真实目录**（不是符号链接）——之前的安装可能在那里；如果是，请提供迁移建议（将目录移动到 `~/.agents/skills/` 并用符号链接替换原始路径）然后继续。
如果技能已存在，提示用户选择：
1. **更新 / 合并**（模式 4）— 将新文件/内容集成到现有技能组件中。
2. **覆盖**——删除并从头开始重新生成技能。
3. **重命名**——追加 `-2` 或使用不同的自定义缩写。

如果用户选择 **更新 / 合并**，请在步骤 2.5 后立即进行 **更新 / 合并工作流**，跳过步骤 3、4、6、7、8、9。

---

## 第 6 步 — 创建技能目录结构

```bash
mkdir -p "$SKILLS_HOME/<skill_name>/chapters"
```

---

## 第 7 步 — 生成章节摘要

**令牌预算规则——关键（自适应）：**

每章节预算随 `BOOK_TYPE` 和 `DEPTH` 缩放。技术章节需要空间来容纳代码和表格；学习深度需要空间来容纳已完成的推理。从以下矩阵中选择预算：

| | `DEPTH=reference` | `DEPTH=study` |
|---|---|---|
| `BOOK_TYPE=text` | 800–1,200 令牌 | 1,000–1,800 令牌 |
| `BOOK_TYPE=technical` | 1,200–1,800 令牌 | 2,000–3,000 令牌 |

- 这些是每个文件的靶标，不是硬性上限——密集章节可能会超出，薄的章节可能会低于。密度仍然优于长度（质量规则 #3）：永远不要为了达到数字而填充。
- 文件按需加载，因此较大的章节只有在实际读取该章节时才会消耗令牌。
- 在两个单元格之间不确定时（例如，混合内容书籍），使用较低的预算，并让深度来自精度，而不是数量。

**`DEPTH=study` 是通过内容获得的，而不是更大的数字。** 标准部分模板（核心思想 → 连接到）自然会导致密集的散文章节约为 700–900 令牌。要诚实地达到学习预算——不是通过填充——学习深度的章节必须添加具体材料：
- **复制一个章节中的已完成的示例或工件**（例如，示例新闻稿、样本对话、填好的模板、作者逐步解释的决策）在 `## 已完成示例` 部分下。这是最大的杠杆，也是学习者返回的主要东西。
- **将每个框架的 "如何" 扩展为明确的步骤或标准，而不是一句话。**
- **在顶部 1–2 个框架下添加一个简短的 "为什么有效 / 失效模式" 注释。**

如果一个章节确实没有已完成的示例并且难以扩展，让它低于学习底线，而不是填充——并注意该章节的核心思想很薄。相比之下，`reference`-深度章节故意省略已完成的示例，并仅保留决策就绪的要点。

对于每个在步骤 3 中识别的章节/主要部分：

读取提取的 `full_text.txt` 的相应部分（使用字符偏移量或查找章节标题的 grep）。

使用以下结构创建 `$SKILLS_HOME/<skill_name>/chapters/ch<NN>-<slug>.md`。

**根据 `BOOK_TYPE` 调整重点：**
- `technical` → 优先考虑 "代码示例"、"参考表格" 和 "命令 & API" 部分；保留确切语法
- `text` → 优先考虑 "引入的框架"、"思维模型" 和 "关键要点"；跳过空的技术部分

```markdown
# 第 N 章：<完整标题>

## 核心思想
<1–2 句话：本章教授的最重要的事情>

## 引入的框架
- **<框架名称>**：<精确表述——保留作者的命名>
  - 何时使用：<具体情境>
  - 如何操作：<步骤或标准>

## 关键概念
- **<术语>**：<精确定义，一句话>
(本章 5–10 个最重要的术语)

## 心智模型
<2–4 个框架或思维工具。写法为“在 Y 时使用 X”或“将 X 视为 Y”>

## 反模式
- **<要避免的内容>**：<为什么它失败>

## 代码示例 *(仅限技术书籍——如果 BOOK_TYPE=text 则省略)*
<!-- 从本章复制最有指导意义的代码片段。保留缩进完全一致。 -->
```<语言>
<本章的关键代码示例>
```
- **它展示了什么**：<一句话>

## 参考表格 *(仅限技术书籍——如果 BOOK_TYPE=text 则省略)*
<!-- 在 markdown 中重现本章中的任何比较矩阵、参数表或决策表。 -->

## 例解 *(DEPTH=study 仅限——对于 DEPTH=reference 则省略)*
<!-- 复制或重建作者详细讲解的一个具体示例：一个示例文档、对话、填好的模板、前后对比，或一个端到端的决策过程。这是使研究章节值得其预算的东西。保持对原始资料的忠实；永远不要复制长篇原始段落——紧凑地重建示例。 -->

## 关键要点
1. <可操作的见解>
2. <可操作的见解>
3. <可操作的见解>
(3–7 个实践者必须记住的要点)

## 相关内容
- **第 N 章**：<为什么本章相关>
- **<概念>**：<它连接的外部概念或标准>

---

## 第 8 步 — 生成支持文件

### glossary.md
创建 `$SKILLS_HOME/<技能名>/glossary.md`：
- 书中每个重要术语，按字母顺序排序
- 格式：`**术语** — 定义 (Ch N)`
- 最大 1,500 个 token

### patterns.md
创建 `$SKILLS_HOME/<技能名>/patterns.md`：
- 书中所有具体技术、设计模式、算法
- 格式：`## 模式名称\n**何时使用**：...\n**如何操作**：...\n**权衡**：...`
- 最大 2,000 个 token

### cheatsheet.md
创建 `$SKILLS_HOME/<技能名>/cheatsheet.md`：

**这是技能中最具差异化的层次——将其视为推理辅助工具，而不是关键词列表。** 任何人都可以通过 grep 查找词汇表中的术语。速查表捕获了作者的*判断*：他们会做出的决策及其原因。这是将“我知道这些术语”转化为“我会像作者一样行动”的文件。

按顺序优先级：
1. **决策规则** — “在 X 时，执行 Y，因为 Z。” 作者应用的 if/then 逻辑，以使读者无需重读书籍即可应用它。
2. **决策树/流程图**（作为嵌套的圆点或一个小表格）— 用于有两个以上分支的选择。
3. **权衡矩阵** — 在作者关心的维度上对竞争选项进行评分，以便读者可以根据自己的约束进行选择。
4. **阈值和默认值** — 作者承诺的具体数字、比率或经验法则（例如，“保持函数在 ~20 行以内”， “当错误预算 < 10% 时发出警报”）。
5. **迹象和气味** — 用于识别情况的快速启发式方法（“如果你看到 X，你很可能遇到 Y”）。

避免：裸术语→定义行（那是词汇表），和散文段落（那是章节）。每一行都应该帮助读者*做出决定*。

- 格式主要为紧凑的表格和决策规则；内容是你希望在旁边保持的单页打印页上想要的内容。
- 最大 1,200 个 token。

---

## 第 9 步 — 生成主 SKILL.md

**关键 token 预算：保持 SKILL.md 正文在 4,000 个 token 以下。**
压缩会从末尾截断——将最重要的内容放在最前面。

创建 `$SKILLS_HOME/<技能名>/SKILL.md`：

```markdown
---
name: <技能名>
description: "来自 \"<完整标题>\" 的知识库，由 <作者> 编写。在应用 <作者> 的框架以研究 <关键主题，3–6 个术语>、研究书籍或参考其概念时使用。"
---

<!-- argument-hint: [主题、框架名称或章节编号] -->

# <完整标题>
**作者**：<作者> | **页数**：~<N> | **章节**：<N> | **生成**：<YYYY-MM-DD>

## 如何使用此技能

- **不带参数** — 加载核心框架以供参考
- **带主题** — 询问 `replication`、`pricing` 或其他索引主题；我查找并阅读相关章节
- **带章节** — 询问 `ch05`；我加载该特定章节
- **浏览** — 询问“你有哪些章节？”以查看完整索引

当你询问一个在核心框架下未涵盖的主题时，我会在回答前阅读相关章节文件。

---

## 核心框架和心智模型
<!-- ~2,000 个 token：作者最重要的命名框架和原则。
     保留确切名称。写法为“在 Y 时使用 X”，“优先选择 X 而非 Y 因为 Z”。
     这是一个工具包，而不是摘要。 -->

<在此处生成 2,000 个 token 的最关键框架和见解>

---

## 章节索引

| # | 标题 | 关键框架 |
|---|-------|----------------|
| [ch01](chapters/ch01-<slug>.md) | <标题> | <框架1>, <框架2> |
| [ch02](chapters/ch02-<slug>.md) | <标题> | <框架1>, <框架2> |
...

## 主题索引

<!-- 按字母顺序排列。主要术语/框架→涵盖它们的章节。 -->
- **<术语>** → ch<N>[, ch<N>]
- **<术语>** → ch<N>

## 支持文件

- [glossary.md](glossary.md) — 所有关键术语及其定义
- [patterns.md](patterns.md) — 所有技术和设计模式
- [cheatsheet.md](cheatsheet.md) — 快速参考表格和决策指南

---

## 范围和限制

此技能仅涵盖书籍内容。对于在您的代码库中进行实际实现，请结合项目特定工具。对于本书以外的主题，请检查相关技能或直接询问代理。
<如果 images_dropped > 5：说明未读取 N 张源图像>
```

---

## 第 9.5 步 — 扫描生成的技能

在报告成功、在另一个会话中加载技能或发布之前，运行顾问安全扫描：

```bash
SKILL_CONVERTER_ROOT="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
"$PYTHON_BIN" "$SKILL_CONVERTER_ROOT/tools/scan_generated_skill.py" "$SKILLS_HOME/<技能名>"
```

如果扫描器以非零状态退出，停止并要求人类审查其文件/行发现。不要静默地重写生成的文件，并且在发现被解决或明确接受之前，不要加载或发布技能。

---

## 第 10 步 — 清理和报告

如果主机是 Claude Code 且 `SKILLS_HOME` 是 `~/.agents/skills`（默认个人安装），请使用符号链接将技能暴露给 Claude Code —— Claude Code 仅扫描 `~/.claude/skills`：

```bash
mkdir -p "$HOME/.claude/skills"
LINK="$HOME/.claude/skills/<技能名>"
TARGET="$HOME/.agents/skills/<技能名>"
if [ -d "$LINK" ] && [ ! -L "$LINK" ]; then
  CLAUDE_STATUS="skipped-realdir"                 # Step 5 迁移被拒绝；保留旧目录
else
  ln -sfn "$TARGET" "$LINK" 2>/dev/null || true
  # 读取链接回——不要信任 `ln` 是否按请求执行。在 Windows/MSYS
  # `ln -s` 可能会复制而不是链接（或需要开发者模式 / 一个提升的 shell），并且
  # PowerShell/cmd 没有链接。报告必须反映磁盘上的内容，而不是命令运行的事实。
  if [ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$TARGET" ]; then
    CLAUDE_STATUS="linked"
  elif [ -e "$LINK" ]; then
    CLAUDE_STATUS="copy"                           # 实际文件/目录落在了那里而不是链接
  else
    CLAUDE_STATUS="absent"                         # ln 不可用或被拒绝
  fi
fi
```

实际目录保护是必需的：`ln -sfn` 到一个现有的实际目录会将链接嵌套在里面（`~/.claude/skills/<技能名>/<技能名>`），留下 Claude Code 加载过时的副本。如果用户拒绝了 Step 5 迁移，请跳过符号链接并在报告中说明——Claude Code 会继续使用旧目录，直到它被迁移。

**在报告任何关于它之前，请读取链接回。** 符号链接是一个声明，不是一个事实：从 `CLAUDE_STATUS`（磁盘上实际的内容）填充“Discoverable by”行，而不是“命令被发出”。**当链接缺失或是一个副本时不要硬失败**——技能在中心存在，其他主机仍然可以找到它；诚实的报告是“写入到 `~/.agents/skills/<技能名>`；Claude Code 将不会看到它，直到链接被创建”，而不是中止。 （Windows 领导，未验证：一个目录连接——在提升的 `cmd` 中 `mklink /J`，或在 PowerShell 中 `New-Item -ItemType Junction`——不需要开发者模式或链接权限；如果你尝试它，它不会改变读取回然后报告的规则。）

当用户选择了主机私有或项目本地根（Step 5，规则 3-4）时跳过此步骤。

然后清理提取工作目录：

```bash
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

删除**此运行实际使用的工目录**——提取输出中的 `Workdir ->` 路径，它也存储为 `workdir` 在 `metadata.json` 中。永远不要删除你没有创建的目录：另一个提取可能正在你的旁边运行。

```bash
# WORKDIR 是此运行报告的路径；如果路径中有空格，请引用它。
rm -rf "$WORKDIR"
```

等效地，如果你仍然有元数据文件：

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

此文件的旧版本删除了一个固定的 `book_skill_work` 目录。该路径不再使用，因此这种清理现在是无害的 no-op，而不是可能删除并发运行输出的东西。

然后向用户报告：

```
✅ 技能创建：$SKILLS_HOME/<技能名>/

📚 书籍：<完整标题> — <作者>
📄 页数：~<N> | 章节：<N>

生成的文件：
  SKILL.md         — 核心框架 + 索引   (~X token)
  chapters/        — <N> 章节摘要     (~X token 每个章节，~X 总计)
  glossary.md      — 关键术语         (~X token)
  patterns.md      — 技术和模式     (~X token)
  cheatsheet.md    — 快速参考           (~X token)
  ─────────────────────────────────────────────────────
  技能总大小：~X token（按需加载，不会一次性全部加载）

💡 提示：检查你的代理的会话成本/使用命令以查看实际 token 使用情况。

使用方法：
  询问 <技能名>                  → 加载核心框架
  询问 <技能名> 关于 <主题>        → 查找并解释一个主题
  询问 <技能名> 对于 ch<N>            → 深入特定章节

可发现性：<仅对所选目标真实的内容——见下文>

其他地方？  mv ~/.agents/skills/<技能名> <dest_root>/<技能名> \
                   && ln -sfn <dest_root>/<技能名> ~/.claude/skills/<技能名>

每次文件都请求权限？那是你的主机限制在工作目录外的写入。说“保存它在此项目中”并重新运行以将其写入其中。

重新加载（如果你的代理不会自动检测新技能）：
  GitHub Copilot CLI:  /skills reload
  Claude Code:         重新启动会话
  Amp:                 重新启动会话
  Hermes Agent:         开始新会话
  OpenClaw:             openclaw skills list (如果禁用监视器则开始新会话)
  OpenCode:             开始新会话
```

分享此技能（可选）：
  GitHub 仓库，可在任何主机上安装（第 11 步）：说“发布”
  Copilot 生态系统：gh skill publish $SKILLS_HOME/<skill_name>

```

根据 `CLAUDE_STATUS`（回读结果）填写“可发现性”行，而不是根据 `ln` 是否运行来填写 —— 对于 `~/.agents/skills` 安装：
- `linked` → "Copilot CLI, Amp, Codex（原生）；Claude 代码通过软链接 ~/.claude/skills/<skill_name>"
- `skipped-realdir` → "Copilot CLI, Amp, Codex（原生）；**不**是 Claude 代码 —— 首先迁移真实目录 ~/.claude/skills/<skill_name>"
- `copy` 或 `absent` → "Copilot CLI, Amp, Codex（原生）；**不**是 Claude 代码 —— 主机无法创建软链接（纯复制会在下次 Update/Fold-in 时漂移）。启用开发者模式 / 手动创建链接，或从 ~/.agents/skills 运行技能"
- Hermes Agent 个人根目录 → "Hermes Agent（来自 `$HERMES_HOME/skills/<category>`）"；不声明软链接，也不声明跨代理声明，因为其他主机不扫描 Hermes 根目录
- 其他主机私有或项目本地根目录 → 仅命名扫描该根目录的主机；不声明软链接

“在其他地方？”重新定位行必须对实际路径正确，因此它永远不会破坏刚运行的软链接。**`mv` 始终针对最终技能目录 `<dest_root>/<skill_name>`，而不是 `<dest_root>` 本身。** `mv ~/.agents/skills/mybook ~/.copilot/skills && ln -sfn ~/.copilot/skills ~/.claude/skills/mybook` 读取为有效，而 `mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>` 不是：技能最终位于 `~/.copilot/skills/mybook`，而链接指向上一级在根目录，所以 Claude 代码解析到一个没有 `SKILL.md` 的目录，这正是此行存在的目的来避免这种情况。替换用户实际命名的目标，因此打印的命令包含真实路径，并且没有剩余的解释内容：
- `~/.agents/skills` + 软链接 → `mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>`
- 主机私有根目录，包括 Hermes Agent → `mv <src_root>/<skill_name> <dest_root>/<skill_name>`
- 项目本地根目录 → `mv <project_root>/<skill_name> <dest_root>/<skill_name>`

“是否每次都请求文件权限？”行是对一个限制工作目录外写入的主机（任何个人范围根目录都在工作目录外）的回答：目的地已在上面宣布，单行修复——重新运行请求项目本地根目录——紧挨着它。仅保留个人范围安装；当用户已经选择项目本地时，删除它。

---

## 第 11 步 — 将生成的技能发布到 GitHub（可选）

在步骤 10 报告之后，仅当步骤 9.5 扫描通过时提供一次：

> "我想将此技能发布到 GitHub，以便任何 Agent Skills 主机都可以使用 `npx skills add` 安装它？(是 / 跳过)"

如果用户拒绝，则停止。要求：`gh` CLI，经过身份验证（检查 `gh auth status`）。如果 `gh` 缺失或未经过身份验证，提供设置它的选项（`brew install gh` 或 https://cli.github.com，然后 `gh auth login`）——或者使用无 `gh` 路径：用户在 GitHub 网页 UI 中创建一个空仓库，选择所需的可见性，然后你运行下面的 `git init`/`add`/`commit` 命令，然后 `git remote add origin <repo-url> && git push -u origin main`。下面的可见性规则同样适用于网页创建的仓库。

**可见性是一个独立封闭的问题——从不推断，从不从先前的答案中读取出来。** 一旦用户接受，单独询问它，并要求一个单词的回复：

> "私有或公共仓库？用一句话回复：`private` 或 `public`。"

**回复必须是 `public`，而不仅仅是包含它——这是一个硬性规则，而不是建议。** 在所有情况下，除了可见性问题的答案是裸词 `public` 之外，都使用 `--private` 运行 `gh repo create`。禁止子字符串匹配，因为关于 **源许可证的句子不是可见性答案**——"它是公共领域的"、"这本书是公共领域的"、"它是公开可用的" 都描述了材料，而不是仓库，并且都解析为 `--private`。释义、句子、模糊答案、沉默或你自己的推断都不是同意：重新询问一次，如果回复仍然不是裸词，则使用 `--private` 并在报告中说明。私有仓库可以稍后改为公共；书派生内容的公共推送无法撤回。

**版权门——在创建仓库之前始终应用：** 章节文件是综合摘要，不是原始文本，但它们仍然源自源材料。根据 README 的版权和合理使用政策，从 **第三方版权书籍生成的技能必须保持私有**；仅在源是用户自己的写作、开放许可内容或用户明确确认他们有权公开重新分发时才提供公共——并说明哪种情况适用。能够访问内部公司材料并不代表有权披露它：来自内部文档的技能保持 **私有**，除非用户声明他们拥有发布权。

如果接受：

1. 在 `$SKILLS_HOME/<skill_name>/` 内添加一个仓库 `README.md`（永远不会覆盖现有文件）——技能标题、一段一行的描述（“Agent 技能由 <Author> 使用 [book-to-skill](https://github.com/virgiliojr94/book-to-skill) 从 *<Title>* 生成的”）、步骤 3 中的安装命令、文件清单，并注明内容是综合摘要，不是书文本。
2. 将技能文件夹初始化为 git 仓库并创建远程（默认仓库名 `<skill_name>`；允许用户覆盖——有些人更喜欢 `<skill_name>-skill` 后缀）。**嵌套仓库保护：** 首先检查技能文件夹是否已经位于一个 git 仓库中（`git -C "$SKILLS_HOME/<skill_name>" rev-parse --show-toplevel`——对于 `.claude/skills/` 等项目本地根目录始终如此）。如果它是，不要在原地 `git init`：外层仓库会将文件夹记录为嵌入仓库（gitlink，模式 160000）而没有 `.gitmodules`，外层项目的最新克隆会静默忽略技能。相反，将技能文件夹复制到临时目录，从副本运行下面的命令，并告知用户发布的仓库——不是项目本地文件夹——是远程的工作副本。

```bash
cd "$SKILLS_HOME/<skill_name>"
git init -b main
git add -A
git commit -m "添加 <skill_name> 技能"
gh repo create <repo_name> --private --source . --push
# --private 是默认值；仅当可见性规则上述时替换 --public
# （可见性答案是裸词 "public" 并且版权门允许它）
```

3. 报告仓库 URL 和跨主机安装命令：

```
✅ 发布：https://github.com/<owner>/<repo_name> (<private|public>)

在任何 Agent Skills 主机上安装：
  npx skills add https://github.com/<owner>/<repo_name> --skill <skill_name>
```

   当嵌套仓库保护触发并且从临时副本发布时，添加一行——本地文件夹永远不会获得远程，因此 Update/Fold-in 推送提议永远不会出现在它上面：

```
⚠️  从副本发布：<skill 文件夹> 位于另一个 git 仓库中，所以它没有
    自己的远程。要发布后续更新，重新运行步骤 11，或克隆
    https://github.com/<owner>/<repo_name> 并将新材料折叠到克隆中。
```

根级别的 `SKILL.md` 布局与 `skills` CLI 检测的完全相同，因此仓库可以按原样安装——不需要重新结构。在嵌套仓库情况下之外，本地文件夹保持此机器的实时安装，并且是远程的工作副本，因此后续 Update/Fold-in 运行可以将其更改提交并推送到同一远程。

---

## 更新 / Fold-in 工作流

在 `$SKILLS_HOME/<skill_name>/` 对现有技能执行 Update/Fold-in 操作时：

### 1. 读取现有技能结构
读取并解析现有技能的文件：
- 读取 `$SKILLS_HOME/<skill_name>/SKILL.md` 以解析现有的 **章节索引**、**主题索引**、元数据（作者、总章节数）和 **核心框架**。
- 列出 `$SKILLS_HOME/<skill_name>/chapters/` 中的所有文件以找到最高章节编号（例如 `ch12`）。
- 读取 `$SKILLS_HOME/<skill_name>/glossary.md`、`$SKILLS_HOME/<skill_name>/patterns.md` 和 `$SKILLS_HOME/<skill_name>/cheatsheet.md` 以查看已经索引的术语和框架。

### 2. 匹配内容并识别修订与新增
分析此轮提取的新文本 `full_text.txt`（提取输出中的 `Text ->` 路径）以识别新内容是否代表：
- **对现有章节的更新/修订**：如果新内容中的某个部分直接更新或扩展了现有章节的主题，读取现有章节文件，将新细节合并到其中，并重写文件。
- **新增内容**：如果内容引入了新章节、论文或单独的章节，创建 **新的章节摘要文件** 在 `chapters/` 下。从现有章节编号的最高编号开始编号这些文件（例如，如果现有章节停在 `ch12`，创建 `ch13-*.md`、`ch14-*.md` 等）。

### 3. 生成或更新章节摘要文件
对于每个新修订的章节：
- 读取提取的新文本的相应部分。
- 遵循 **步骤 7** 中的格式指南来构建摘要。
- 在 `$SKILLS_HOME/<skill_name>/chapters/` 中写入/更新文件。

### 4. 合并支持文件
- **合并 glossary.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/glossary.md`。
  - 从新内容中提取所有新术语和定义（步骤 8 glossary 指南）。
  - 合并并按字母顺序排列现有和新术语的列表。
  - 如果术语已经存在，将新的章节/来源引用附加到它（例如 `**Term** — 定义 (Ch 4, Ch 13)`）。
  - 使用完全合并的、按字母顺序排列的列表重写 `$SKILLS_HOME/<skill_name>/glossary.md`。
- **合并 patterns.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/patterns.md`。
  - 从新内容中提取任何新技术、算法或模式。
  - 添加新模式，确保一致的格式，并保持总长度简洁（少于 2,500 个 token）。
- **合并 cheatsheet.md**：
  - 读取现有的 `$SKILLS_HOME/<skill_name>/cheatsheet.md`。
  - 提取新的比较规则、决策表或参数指南。
  - 清晰地集成到-cheatsheet 结构中。

### 5. 重新生成主 SKILL.md
更新主技能文件 `$SKILLS_HOME/<skill_name>/SKILL.md`：
- **元数据**：增加章节计数，更新估计页数，如果适当则添加新源名称。将 `Generated` 日期更新为当前日期。
- **核心框架**：从新内容中折叠最具影响力的心智模型或原则（确保整个文件保持在 4,000 个 token 以下）。
- **章节索引**：将新章节追加到索引表，链接到新创建的文件。
- **主题索引**：按字母顺序合并新主题。如果现有主题也在新章节中涵盖，则将新章节链接追加到其行（例如 `- **Topic** → ch05, ch13`）。

### 6. 扫描、清理和报告
一旦文件成功写入和合并，运行 **步骤 9.5**，然后继续到 **步骤 10** 执行清理并打印自定义更新报告，总结新添加的章节、合并的术语和更新的索引。如果技能文件夹是一个具有远程的 git 仓库（通过 **步骤 11** 发布），则提供提交更新并推送它的选项。

---

## 质量规则

1. **提取结构，而不是摘要**——捕获命名框架、精确表述、反模式；不是章节回顾
2. **保留作者的精确性**——"The 5 Whys" ≠ "ask why multiple times"；保持精确命名
3. **密度胜于完整性**——1,000 个 token 的摘要胜过 10,000 个 token 的摘录
4. **实践者声音**——写 "Use X when Y"，而不是 "The book explains X"
5. **前移 SKILL.md**——压缩保留前 5,000 个 token；最重要的内容首先出现
6. **章节文件是按需加载的**——它们不计入技能预算，直到加载
7. **永不复制原始书文本**——始终综合、摘要、提取信号
8. **主题索引至关重要**——它是代理导航到正确章节文件的方式
