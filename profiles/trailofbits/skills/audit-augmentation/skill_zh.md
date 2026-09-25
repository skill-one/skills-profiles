# 审计增强

将外部工具（SARIF）和人工审计员（weAudit）的项目发现结果
作为注释和子图叠加到 Trailmark 代码图上。Trailmark 0.4.0+ 还可以通过
`engine.augment_binary()` 导入外部二进制分析图 JSON 导出。

## 使用场景

- 将 Semgrep、CodeQL 或其他 SARIF 生成工具的结果导入到图中
- 将 weAudit 审计注释导入到图中
- 将二进制分析图数据导入到源图（Trailmark 0.4.0+）
- 将静态分析结果与爆炸半径或污染数据交叉引用
- 查询哪些函数有高严重性发现
- 在代码结构旁边可视化审计覆盖率
- 为 `trailmark-finding-triage` 准备一个 SARIF 或 weAudit 结果

## 不应使用场景

- 运行静态分析工具（直接使用 semgrep/codeql，然后导入）
- 构建代码图本身（使用 `trailmark` 技能）
- 生成图表（在增强后使用 `diagramming-code` 技能）

## 拒绝理由

| 拒绝理由 | 为什么错误 | 必要操作 |
|-----------------|----------------|-----------------|
| "用户只询问了 SARIF，跳过预分析" | 没有预分析，无法将发现结果与爆炸半径或污染交叉引用 | 增强前始终运行 `engine.preanalysis()` |
| "不匹配的发现不重要" | 不匹配的发现可能表示解析差距或超出范围的文件 | 报告不匹配计数并在较高时进行调查 |
| "一个严重性子图就足够了" | 不同的严重性需要不同的筛选工作流 | 查询所有严重性子图，而不仅仅是 `error` |
| "SARIF 结果说明了一切" | 没有图上下文的发现结果缺乏爆炸半径和污染可达性 | 与预分析子图交叉引用 |
| "weAudit 和 SARIF 重叠，选择一个" | 人工审计员和工具发现不同的事情 | 当可用时导入两者 |
| "工具未安装，我将手动操作" | 手动分析遗漏了工具可以捕获的内容 | 首先安装 trailmark |

---

## 安装

**强制要求：** 如果 `uv run trailmark` 失败，请先安装 trailmark：

```bash
uv tool install trailmark
# Python 代码片段：uv run --with trailmark python -   (工具环境不可导入)
```

## 版本门禁

SARIF 和 weAudit 增强是 v0.2 安全的。二进制图增强仅限于 Trailmark 0.4.0+。在调用 `engine.augment_binary()` 之前，请检查：

```python
if not hasattr(engine, "augment_binary"):
    raise RuntimeError("Binary 增强需要 Trailmark >= 0.4.0")
```

在 Trailmark 0.5.0+ 中，源函数与导入的二进制或外部端点之间的已知链接也可以在 `.trailmark/links.toml` 中声明一次（参见主 `trailmark` 技能的“仓库链接”部分），而不是每次会话重新推导。声明的外部端点在每个解析过程中都会以 `proxy.external:<symbol>` 节点形式出现。

## 快速入门

### 命令行

```bash
# 使用 SARIF 增强增强
uv run trailmark augment {targetDir} --sarif results.sarif

# 使用 weAudit 增强增强
uv run trailmark augment {targetDir} --weaudit .vscode/alice.weaudit

# 同时使用两者，输出 JSON
uv run trailmark augment {targetDir} \
    --sarif results.sarif \
    --weaudit .vscode/alice.weaudit \
    --json
```

二进制图增强在 Trailmark 0.4.0+ 中是程序化的；如果 `trailmark augment --help` 没有显示标志，请不要编造标志。

### 程序化 API

```python
from trailmark.query.api import QueryEngine

engine = QueryEngine.from_directory("{targetDir}", language="auto")

# 首先运行预分析以进行交叉引用
engine.preanalysis()

# 使用 SARIF 增强增强
result = engine.augment_sarif("results.sarif")
# result: {matched_findings: 12, unmatched_findings: 3, subgraphs_created: [...]}

# 使用 weAudit 增强增强
result = engine.augment_weaudit(".vscode/alice.weaudit")

# 使用外部二进制图导出增强（v0.4+）
if hasattr(engine, "augment_binary"):
    result = engine.augment_binary("binary_graph.json")

# 查询发现结果
engine.findings()                                       # 所有发现结果
engine.subgraph("sarif:error")                          # 高严重性 SARIF
engine.subgraph("weaudit:high")                         # 高严重性 weAudit
engine.subgraph("sarif:semgrep")                        # 按工具名称
engine.annotations_of("function_name")                  # 按节点查找
```

如果目标自动检测错误，请使用显式语言或逗号分隔列表（如 `python,rust`）重新运行。

## 工作流程

```
增强进度：
- [ ] 第 1 步：构建图并运行预分析
- [ ] 第 2 步：定位 SARIF/weAudit/二进制图文件
- [ ] 第 3 步：运行增强
- [ ] 第 4 步：检查结果和子图
- [ ] 第 5 步：与预分析交叉引用
```

**第 1 步：** 构建图并运行预分析以获取爆炸半径和污染上下文：

```python
engine = QueryEngine.from_directory("{targetDir}", language="auto")
engine.preanalysis()
```

如果目标自动检测错误，请使用显式语言或逗号分隔列表（如 `python,rust`）重新运行。

**第 2 步：** 定位输入文件：
- **SARIF**：通常由像 `semgrep --sarif -o results.sarif` 或 `codeql database analyze --format=sarif-latest` 这样的工具输出
- **weAudit**：存储在 `.vscode/<username>.weaudit` 中
- **二进制图（v0.4+）**：外部 JSON 包含 `artifact`、`functions` 和 `calls` 字段。Trailmark 导入此图；它本身不会反汇编二进制文件。

**第 3 步：** 通过 `engine.augment_sarif()` 或 `engine.augment_weaudit()` 运行增强。对于二进制图，只有在版本门禁成功后才能运行 `engine.augment_binary()`。检查 SARIF 和 weAudit 结果中的 `unmatched_findings` — 这些是文件/行位置与任何解析的代码单元不重叠的发现结果。

**第 4 步：** 查询发现结果和子图。使用 `engine.findings()` 列出所有注释节点。使用 `engine.subgraph_names()` 查看可用子图。

**第 5 步：** 与预分析数据交叉引用以优先处理：
- 污染节点上的发现：重叠 `sarif:error` 与 `tainted` 子图
- 高爆炸半径节点上的发现：重叠 `high_blast_radius`
- 特权边界上的发现：重叠 `privilege_boundary`

对于需要可达性判断或 PoC 交接的一个候选发现，继续使用 `trailmark-finding-triage` 并将增强节点作为边界候选。

## 注释格式

发现结果作为标准 Trailmark 注释存储：

- **类型**：`finding`（工具生成）或 `audit_note`（人工笔记）
- **来源**：`sarif:<tool_name>` 或 `weaudit:<author>`
- **描述**：紧凑的单行：
  `[严重性] rule-id: 消息 (工具)`

## 生成的子图

| 子图 | 内容 |
|----------|----------|
| `sarif:error` | 具有高严重性 SARIF 发现的节点 |
| `sarif:warning` | 具有中严重性 SARIF 发现的节点 |
| `sarif:note` | 具有低严重性 SARIF 发现的节点 |
| `sarif:<tool>` | 由特定工具标记的节点 |
| `weaudit:high` | 具有高严重性 weAudit 发现的节点 |
| `weaudit:medium` | 具有中严重性 weAudit 发现的节点 |
| `weaudit:low` | 具有低严重性 weAudit 发现的节点 |
| `weaudit:findings` | 所有 weAudit 发现（entryType=0） |
| `weaudit:notes` | 所有 weAudit 笔记（entryType=1） |
| `binary:<artifact>` | 从 v0.4+ 二进制图导入的二进制函数节点 |

## 匹配机制

发现结果通过文件路径和行范围重叠与图节点匹配：

1. 发现的文件路径相对于图的 `root_path` 进行规范化
2. 节点的 `location.file_path` 匹配且行范围重叠的节点被选中
3. 最紧密的匹配（最小跨度）优先
4. 如果发现的位置不与任何节点重叠，则计为不匹配

SARIF 路径可以是相对的、绝对的或 `file://` URI — 所有路径都得到处理。weAudit 使用 0 索引行，会自动转换为 1 索引。

二进制图导入创建 `origin=binary` 函数节点、`origin=proxy` 外部代理节点以解析二进制调用，并在二进制函数映射回源节点时推断 `corresponds_to` 边。预期的 JSON 形状故意保持简单：

```json
{
  "artifact": {"name": "libexample", "architecture": "x86_64", "sha256": "..."},
  "functions": [
    {"symbol": "parse_packet", "address": "0x401000",
     "source": {"file": "src/parser.c", "line": 42}}
  ],
  "calls": [
    {"source": "parse_packet", "target": "malloc", "confidence": "inferred"}
  ]
}
```

## 支持文档

- **[references/formats.md](references/formats.md)** — SARIF 2.1.0 和 weAudit 文件格式字段参考
