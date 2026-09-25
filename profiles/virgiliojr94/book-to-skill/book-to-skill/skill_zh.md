---
跨代理备注（信息性；主机代理忽略）：
  - 兼容技能根源：GitHub Copilot CLI (~/.copilot/skills, ~/.agents/skills, .github/skills, .claude/skills, .agents/skills), Amp (.agents/skills, ~/.config/agents/skills, ~/.config/amp/skills), Claude Code (~/.claude/skills), Hermes Agent ($HERMES_HOME/skills, .hermes/skills, .agents/skills), OpenClaw (${OPENCLAW_STATE_DIR:-~/.openclaw}/skills, .agents/skills, skills/; ~/.agents/skills 仅在默认状态下兼容).
  - `allowed-tools` 故意省略以保持代理中立：Copilot CLI 使用 `shell`/MCP-server 名称，Claude 使用 `Bash`/`Read`/`Write`/`Glob`/`Grep`，Amp 添加 `shell_command`。该技能需要 shell（以运行 extract.py）和文件读写 — 每个主机将在首次使用时提示这些内容。
  - 参数提示：<文档文件夹路径或 glob>... [技能名称缩写]

# 书籍到技能转换器

通过提取结构将书面知识转化为可操作的代理技能，而不是生成摘要。

## 哲学

书籍包含结晶化的专业知识：经过多年发展的框架、原则和技术。此技能将知识提取为 GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenClaw 或其他兼容代理可以重复利用的格式。

**提取结构，不是摘要。** 技能不是书评。它是一个工具包，包含：
- 命名框架（具有明确应用的思维模型）
- 可操作的原理（指导决策的规则）
- 技术（分步方法）
- 反模式（要避免的内容和原因）
- 语音校准（作者思考和沟通的方式）

**保留作者的精确性。** 框架通常具有特定名称，原因在于此。 "The 5 Whys" 与 "多次询问为什么" 不可互换。捕获确切的表述。

**适当分层深度。** 简单的书籍 → 简单的技能。具有 10 个以上框架的复杂书籍 → 具有参考文件和按需章节的技能。

---

## 操作模式

四种路径可用。根据用户请求进行路由：

### 1. 完整转换（默认）
**触发条件：** 用户提供一个或多个文档/目录/glob 路径，没有特殊指令
**操作：** 执行以下所有步骤（步骤 0-9）
**输出：** 完整的技能，包括 SKILL.md, chapters/, 词汇表, 模式, 快速参考表

### 2. 仅分析
**触发条件：** 用户说 "analyze", "just extract", 或 "我想在生成之前进行审查"
**操作：** 执行步骤 0-3，然后生成结构化提取报告（框架, 原理, 技术）。停止 — 不要生成技能文件。
**输出：** 用于用户审查的分析报告

### 3. 从先前的分析生成
**触发条件：** 用户具有现有的分析笔记或之前运行了仅分析模式
**操作：** 跳过步骤 0-3，使用提供的分析作为输入，执行步骤 4-9
**输出：** 从提供的分析生成的技能文件

### 4. 更新 / 合并（现有技能）
**触发条件：** 用户提供一个或多个新的源路径，并指示他们想要更新现有技能（通过指向现有技能文件夹, 提供 `SKILLS_HOME` 中已存在的技能缩写, 或明确请求更新）。
**操作：** 执行步骤 0（范围检查），步骤 1（验证输入），步骤 1.5（识别书籍类型），和步骤 2（提取新文件）。然后跳到步骤 5（识别/检测现有技能路径）并运行 **更新 / 合并工作流** 将新内容合并到现有技能文件中。
**输出：** 更新后的现有技能，包括新的/修订的章节摘要和合并的索引/词汇表。

---

## 技能位置

此转换器可以从多个技能系统运行。查找此转换器的辅助脚本或生成书籍技能时，请按顺序优先使用这些位置：

1. GitHub Copilot CLI 个人技能：`~/.copilot/skills/`
2. 跨代理个人技能（Copilot, Amp, Codex; OpenClaw 使用其默认状态）：`~/.agents/skills/`
3. Claude Code 个人技能：`~/.claude/skills/`
4. 项目本地 Copilot 技能：`.github/skills/`
5. 项目本地 Claude 技能：`.claude/skills/`
6. 项目本地 Amp / Copilot / OpenClaw 技能：`.agents/skills/`
7. Amp 全局技能：`~/.config/agents/skills/`
8. Amp 遗留全局技能：`~/.config/amp/skills/`
9. Hermes Agent 个人技能：`$HERMES_HOME/skills/`（默认为 `~/.hermes/skills/`）
10. Hermes Agent 项目技能：`.hermes/skills/` 或 `.agents/skills/`
11. OpenClaw 个人技能：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`（活动状态; `~/.agents/skills/` 仅在默认状态下共享）
12. OpenClaw 项目技能：`.agents/skills/` 或 `skills/`

对于 **生成的** 书籍技能，请优先使用用户级跨代理根 `~/.agents/skills/` — 一个物理副本服务于跨代理主机和 OpenClaw 在其默认状态下使用。Copilot CLI 和 Amp 原生发现它; Claude Code 需要一个从 `~/.claude/skills/<skill_name>` 的符号链接（在步骤 10 中创建，步骤 5 中的规则见步骤）。仅在用户明确要求时才选择主机私有或项目本地根。`BOOK_TO_SKILL_SCOPE=project` 或 `personal` 可以使该选择对自动化明确。不要因为两个范围都可用而询问强制范围问题。

---

## 步骤 0 — 范围检查

如果未提供任何参数，停止并响应：
> "book-to-skill 需要一个支持文档路径、文件夹或 glob 模式。用法: `book-to-skill <路径到文档文件夹或 glob>... [技能名称缩写]`"

在工作流程中：
- 识别输入路径和可选技能缩写。
- 如果最后一个参数不是存在的文件、文件夹或 glob 匹配任何文件，并且看起来像技能缩写（例如 lowercase hyphens, alphanumeric），将其视为 `SKILL_NAME`。
- 将所有其他参数视为 `INPUT_PATHS` 列表。
- 如果任何输入路径是现有的技能目录（包含 `SKILL.md` 和 `chapters/` 子文件夹），或者 `SKILL_NAME` 匹配 `SKILLS_HOME` 中现有的技能缩写，将此运行标记为 **更新/Fold-in** 操作（模式 4）。

---

## 步骤 1 — 验证输入

验证 `INPUT_PATHS` 中至少存在一个支持文件、目录或 glob 模式。
对于目录和 glob，将它们展开以找到匹配的支持文件（`.pdf`, `.epub`, `.docx`, `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.html`, `.htm`, `.rtf`, `.mobi`, `.azw`, `.azw3`）。

如果找不到支持文件，停止并使用清晰的错误消息。

---

## 步骤 1.5 — 识别内容类型

提取之前，询问用户：

> "这些源包含什么类型的内容？这有助于我选择最佳提取方法。
>
> 1. **技术** — 包含代码块、表格、公式、图表（例如编程书籍、学术论文、建筑指南）
> 2. **文本为主** — 主要为散文，几乎没有或没有表格/代码（例如管理、生产力、叙事非虚构类）
> 3. **不确定** — 我将使用快速方法，如果质量似乎有限，我会警告你

将答案存储为 `BOOK_TYPE`：
- 选项 1 → `BOOK_TYPE=technical`
- 选项 2 → `BOOK_TYPE=text`
- 选项 3 → `BOOK_TYPE=text`

**如果 `BOOK_TYPE=technical`**，在继续之前通知用户：
> "📐 技术模式选定 — 使用结构感知提取（保留表格、代码块、公式）。这需要每页约 1.5 秒，所以对于较长的源，请预期几分钟。现在开始…"

**如果 `BOOK_TYPE=text`**，通知：
> "📄 文本模式选定 — 使用每个文件类型的最快合适的提取器。纯文本/Markdown/HTML 通常几秒钟内准备好; PDFs 使用 pdftotext（如果可用）。

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
  command -v hermes >/dev/null 2>&dev/null && \
  command -v python3 >/dev/null 2>&dev/null && \
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
  "$HERMES_HOME"/skills/*/book-to-skill/scripts/extract.py
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
    "skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
  )
  if [ -n "$PROJECT_ROOT" ]; then
    CANDIDATES+=(
      "$PROJECT_ROOT/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/skills"/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/book-to-skill/scripts/extract.py
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
if ! command -v "$PYTHON_BIN" >/dev/null 2>&dev/null; then
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" "$SCRIPT_PATH" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask
```

提取之前，脚本检查可选的 Python 包，这些包对于检测到的格式是必需的。如果缺少更好的提取器，它将提示用户可用的回退。非交互式会话默认使用回退，除非安装模式明确为 `yes`。

**提示 — 预检环境：** 运行 `"$PYTHON_BIN" "$SCRIPT_PATH" --check` 以打印每个格式的提取器安装报告和确切的安装命令，而不会处理任何文件。当用户报告设置或质量问题时，这很有用。

此步骤创建一个 **每次运行** 的工作目录 — `<tempdir>/book_skill_work-<pid>/` 默认，或 `BOOK_SKILL_WORKDIR` 中设置的精确路径 — 其中包含：
- `full_text.txt` — 所有源文档的合并提取文本，具有清晰的视觉边界。
- `metadata.json` — 总合并大小、单词、页数、令牌计数、丢弃的 EPUB 图像计数、解析的 `workdir`，以及单个处理 `sources` 的详细列表。

完成运行后，打印所有三个路径：

(`Workdir ->`, `Text ->`, `Meta ->`). **从输出中获取这些路径（或从 `metadata.json` 的 `workdir` 字段中获取），而不是假设固定位置** — 每次运行的目录名称都不同，这样同一台机器上的并发提取不会互相覆盖结果。

检查该运行的 `metadata.json` 以检查结果。

**始终确认提取的文档是你请求的文档**，在生成任何内容之前：检查 `metadata.json` 中的 `filename` / `source_file`，或 `full_text.txt` 的第一行的 `SOURCE:` 标头。如果你正在等待后台运行，请等待 *它的* 特定工作目录 — 轮询共享路径可能会显示不同运行的输出。

---

## 步骤 2.5 — 预检成本估计

读取此运行的 `metadata.json`（提取输出中的 `Meta ->` 路径）并在生成任何内容之前向用户显示估计：

```
📖 检测到的源: <total_sources> 个源
<从源元数据列表中列出每个源文件和格式>
<如果 images_dropped > 5: 警告未读取的 N 个源图像>
📄 合并页数/章节: ~<N> | 单词: ~<N> | 总令牌: ~<N>K

💰 估计令牌成本（完整转换 / 更新）:
   输入 (读取 + 提示): ~<N>K 令牌
   输出 (生成的/更新的技能文件):  ~<N>K 令牌
   总计:                           ~<N>K 令牌

   成本: 将上述令牌计数乘以您模型的当前输入/输出每 1M 令牌的费率（价格和模型名称经常变化 — 不要硬编码它们；引用今天的费率并标记为估计）。

   ⏱ 估计时间: ~<N> 分钟

📁 要生成的文件/更新:
   SKILL.md + 章节文件 + 词汇表 + 模式 + 快速参考表

➡  Proceed with Full Conversion / Update? (或输入 "analyze only" 以预览)
```

**如何估计:**
- 输入令牌 ≈ `estimated_tokens` 从元数据 × 1.3（每个章节传递的提示开销）
- 输出令牌 ≈ 章节 × 每个章节预算 + 4,000 (SKILL.md) + 4,500 (词汇表 + 模式 + 快速参考表)
  - 每个章节预算的中点 `BOOK_TYPE`（深度在步骤 4 中稍后决定，可以提高它）：`text` ≈ 1,000, `technical` ≈ 1,800。如果用户已经指示了参考仅 vs 深度学习，请使用步骤 7 矩阵中匹配的行。
- 成本：报告令牌计数，并将其乘以用户当前的每 1M 令牌输入/输出费率。不要硬编码美元金额 — 模型名称和价格会变化；如果你显示了一个，请将其标记为估计并注明日期。

等待用户确认后再继续。如果他们说 "analyze only", 切换到模式 2。

---

## 步骤 2.6 — 大型书籍的 REPL 风格访问（> 50k 令牌）

受递归语言模型 (RLM) 范式启发：将 `full_text.txt` 视为可查询的语料库，而不是单个读取。将整个文件加载到上下文中会消耗你后来用于生成的预算。

对于超过 ~50k 令牌的书籍，请优先使用程序化探测，而不是无限制地使用 `Read(full_text.txt)`：

```bash
# 大小检查之前
wc -w "$FULL_TEXT_PATH"

# 查找章节偏移量，而无需加载整个文件
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# 提取所需的章节（行从 start 到 end 包含）
sed -n '<start>,<end>p' "$FULL_TEXT_PATH"

# 验证框架是否实际提到，然后再在 SKILL.md 中声明
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"

# 带偏移量/限制的定向读取避免了转储整个文件
# Read(file_path=full_text.txt, offset=<line>, limit=<lines>)
```

使用此方法进行步骤 3（结构分析）、步骤 7（每章摘要）和步骤 8（词汇表/模式提取）。对于少于 50k 令牌的书籍，单个 `Read` 就可以了。

为什么这很重要：一本 200 页的书籍大约是 75k 令牌。每次每章重新读取它（28 次）将花费 ~2M 输入令牌；使用 grep + sed 提取相关片段，使生成成本与输出成正比，而不是与源成正比。

---

## 步骤 3 — 分析书籍结构

读取提取的 `full_text.txt` 的前 8,000 个字符以识别：
- 书籍 **标题** 和 **作者**
- **章节结构**（寻找 "Chapter N", "PART I", 编号标题, 目录）
- **核心主题** 和学科领域
- 近似章节数量

然后如果存在，读取目录部分以映射所有章节。

**如果模式是 "Analyze Only":** 现在生成提取报告并停止。结构：
```
## 提取报告 — <标题>

### 作者的核心框架
- **<框架名称>**: <它是什么，何时应用>

### 关键原理
- <原理>: <可操作的规则>

### 技术 & 方法
- <技术>: <分步说明或如何做>

### 反模式
- **<要避免的内容>: <原因>

## 建议的技能名称
`{author-lastname}-{核心概念}` — 例如 `cialdini-influence`

### 检测到的章节
| # | 标题 | 主要框架 |
```

---

## 步骤 4 — 询问目的（仅完整转换）

在生成之前，询问用户：

> "这个技能应该帮助你做什么？(选择一个或多个)
> 1. 在工作时应用作者的框架
> 2. 使用作者的思维模型进行思考
> 3. 引用特定章节和概念
> 4. 以上所有"

使用答案来确定 SKILL.md 核心部分突出显示的内容。

**从答案派生 `DEPTH`（无需额外提示）:**
- 答案仅是选项 3（引用）→ `DEPTH=reference` — 简洁的快速查找章节。
- 答案包含选项 1, 2 或 4 → `DEPTH=study` — 更深的章节，包含更多工作示例、示例和推理。

`DEPTH` 和 `BOOK_TYPE` 一起设置了步骤 7 中每个章节的令牌预算。**不要** 提问单独的“研究 vs 参考”问题 — 它在这里推断。 （在模式 2/3 中，跳过步骤 4，默认 `DEPTH=study`。）

---

## 步骤 5 — 确定技能名称

如果提供了 `SKILL_NAME`，将其用作技能缩写。
否则，建议两个选项并让用户选择：
- **按作者概念**: `{author-lastname}-{核心概念}`（例如 `cialdini-influence`, `meadows-systems`)
- **按标题**: 书籍标题中的 lowercase hyphens（例如 `designing-data-intensive-apps`）

如果书籍具有强烈的方方法身份，请默认使用作者概念格式。

选择目标技能根 (`SKILLS_HOME`)。首先从显式用户请求或 `BOOK_TO_SKILL_SCOPE` 中解析 **范围**，然后探测 **主机**。如果用户明确要求项目本地/项目输出，则选择项目本地行；如果用户明确要求个人/全局输出，则选择个人行。如果既不要求范围，则保留已建立的个人默认（非 Hermes 主机为 `~/.agents/skills`）。不要因为项目本地根存在而询问强制范围问题。选择的根可能仍需主机批准才能写入。

| 主机代理 | 个人技能根 | 项目本地根 |
|---|---|---|
| **GitHub Copilot CLI** | `~/.agents/skills`（原生发现） | `.github/skills` → `.claude/skills` → `.agents/skills` |
| **Amp** | `~/.agents/skills`（原生发现） | `.agents/skills` |
| **OpenAI Codex** | `~/.agents/skills`（原生发现; 遵循符号链接） | `.agents/skills` |
| **Hermes Agent** | `$HERMES_HOME/skills/<category>`（默认为 `~/.hermes/skills/<category>`） | `.hermes/skills/<category>` → `.agents/skills` |
| **Claude Code** | `~/.agents/skills` + 从 `~/.claude/skills/<skill_name>` 的符号链接 | `.claude/skills` |
| **OpenClaw** | `${OPENCLAW_STATE_DIR:-~/.openclaw}/skills`（活动状态; `~/.agents/skills` 仅在默认状态下共享） | `.agents/skills` → `skills/` |

Hermes Agent 是唯一一个保留其自己的个人根的主机：它按类别保留个人技能，并且不扫描跨代理根。使用活动配置的 `HERMES_HOME` 并选择与生成的技能主题匹配的类别。不要手动构建配置路径。如果用户选择项目本地 Hermes 根，运行 `hermes skills trust <project-root>` 后验证发现，使用 `hermes skills list` 验证项目技能是否可用。

对于 OpenClaw，使用活动状态目录的 `skills/` 根：`${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/skills/`。共享的 `~/.agents/skills` 根仅在 `OPENCLAW_STATE_DIR` 未设置或等于默认值 `$HOME/.openclaw` 时才是 OpenClaw 的有效目标。否则使用活动状态根或项目/额外目录。

选择 `SKILLS_HOME` 为选定的根并检查 `$SKILLS_HOME/<skill_name>/` 是否已存在。对于 Claude Code，还检查 `~/.claude/skills/<skill_name>` 是否存在为 **真实目录**（不是符号链接）—— 可能存在先前的安装位于那里；如果存在，请提出要将目录移动到 `~/.agents/skills/` 并用符号链接替换原始路径，然后继续。
如果技能已存在，提示用户选择：
1. **更新 / 合并**（模式 4）— 将新文件/内容合并到现有技能组件中。
2. **覆盖** — 删除并从头开始重新生成技能。
3. **重命名** — 添加 `-2` 或使用不同的自定义缩写。

如果用户选择 **更新 / 合并**，请在步骤 2.5（跳过步骤 3, 4, 6, 7, 8, 9）之后立即转到 **更新 / 合并工作流** 部分进行合并新内容。

---

## 质量规则

1. **提取结构，不是摘要** — 捕获命名框架、确切的表述、反模式；不是章节回顾
2. **保留作者的精确性** — "The 5 Whys" ≠ "多次询问为什么"; 保留确切的名称
3. **密度胜于完整性** — 1,000 个令牌的摘要比 10,000 个令牌的摘录更好
4. **实践者声音** — 写 "Use X when Y", 不要写 "The book explains X"
5. **SKILL.md 前置加载** — 压缩保留前 5,000 个令牌；最重要的内容首先出现
6. **章节文件是按需加载的** — 它们不会计入技能预算，直到加载
7. **从不复制原始书籍文本** — 始终合成、总结、提取信号
8. **主题索引至关重要** — 它是代理导航到正确章节文件的方式
