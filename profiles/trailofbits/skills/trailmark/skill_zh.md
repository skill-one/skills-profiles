# Trailmark

解析源代码，生成函数、类、调用和语义元数据的定向图，用于安全分析。

## 使用场景

- 从用户输入映射到敏感函数的调用路径
- 查找复杂度热点以进行审计优先级排序
- 识别攻击面和入口点
- 理解不熟悉代码库中的调用关系
- 跨多语言项目进行安全审查或审计准备
- 为代码单元添加 LLM 推断的注释（假设、前置条件）
- 导入外部二进制分析图以连接源代码和二进制视图
- 查询传递切片、入口点路径、子图边或类型引用
- 为可疑函数或候选发现生成图证据
- 变异测试（基因毒性技能）或绘图前的预分析

## 不应使用场景

- 单文件脚本，其中调用图没有价值（直接读取文件）
- 不是从代码派生的架构图（使用 `diagramming-code` 技能或手绘）
- 变异测试筛选（使用基因毒性技能，该技能内部调用 trailmark）
- 运行时行为分析（trailmark 是静态的，不是动态的）

## 拒绝的理由

| 理由 | 为什么错误 | 必要操作 |
|------|----------|----------|
| "我会手动读取源文件" | 手动读取会遗漏调用路径、影响范围和污染数据 | 安装 trailmark 并使用 API |
| "快速查询不需要预分析" | 影响范围、污染和权限数据只有在 `preanalysis()` 之后才可用 | 始终在将任务交给其他技能之前运行 `engine.preanalysis()` |
| "图太大，我会采样" | 采样会遗漏跨模块的攻击路径 | 构建完整图；使用子图查询来聚焦 |
| "不确定的边不重要" | 动态分发是类型混淆漏洞隐藏的地方 | 在安全声明中考虑 `uncertain` 边 |
| "单语言分析就足够了" | 多语言存储库在 FFI 边界处有漏洞聚集 | 使用正确的 `--language` 标志 per 组件 |
| "复杂度热点是唯一值得检查的东西" | 低复杂度但在污染路径上的函数是高价值目标 | 将复杂度与污染和影响范围数据结合起来 |
| "文档提到一个版本控制的函数，所以我可以在任何地方调用它" | 许多环境仍然安装了 Trailmark 0.2.x | 在使用 v0.4+/v0.5+ 功能之前检查安装版本或探测功能可用性 |

---

## 安装

**强制要求：** 如果找不到 `trailmark`，在执行任何其他操作之前安装 CLI：

```bash
uv tool install trailmark
```

工具安装仅提供 CLI —— 它不会使 `import trailmark` 可解析。
用 `uv run --with trailmark python -` 运行此技能中的 Python 代码片段；这，而不是安装，是解决代码片段中的导入错误或 ModuleNotFoundError 的方法。

**不要** 落后于“手动验证”、“手动分析”或手动读取源文件，作为运行 trailmark 的替代方案。必须安装并程序化使用该工具。如果安装失败，请向用户报告错误，而不是静默切换到手动代码读取。

## 版本控制

Trailmark 0.4.0 扩展了图模型和查询表面，0.5.0 添加了 SQL 解析器、存储库链接配置和更丰富的入口点元数据。在使用标记为 **v0.4+** 或 **v0.5+** 的功能之前，请检查安装版本：

```bash
trailmark --version 2>/dev/null || uv run trailmark --version 2>/dev/null
```

按数值（而不是按字典序）比较报告的版本。`0.4.0` 或更新版本表示 v0.4 表面完全可用。版本命令本身是在 0.2.2 中添加的，因此失败意味着要么是 0.2.2 之前的安装，要么完全缺少 trailmark —— 用 `trailmark analyze --help` 来区分。在程序化工作时，用 `hasattr()` 探测，而不是假设存在 v0.4 仅有的方法：

```python
if hasattr(engine, "subgraph_edges"):
    edges = engine.subgraph_edges("tainted")
else:
    # v0.2 回退：过滤 engine.to_json() 边缘，其端点都在 engine.subgraph("tainted")
    edges = []
```

**v0.2 安全基线：** CLI `analyze`、`diff`、`entrypoints`、`augment` 和 `--language auto`；`QueryEngine.from_directory()`、`callers_of()`、`callees_of()`、`paths_between()`、`ancestors_of()`、`reachable_from()`、`entrypoint_paths_to()`、`complexity_hotspots()`、`attack_surface()`、`summary()`、`to_json()`、`preanalysis()`、`annotate()`、`annotations_of()`、`nodes_with_annotation()`、`clear_annotations()`、`findings()`、`subgraph()`、`subgraph_names()`、`diff_against()`、`augment_sarif()` 和 `augment_weaudit()`。

**在 0.2.2 中添加：** CLI `--version` 标志和 `version` 子命令。

**在 0.3.x 中添加：** `trailmark.parse` 模块，包含模块级的 `detect_languages()` 和 `supported_languages()`。`detect_languages()` 本身通过 `from trailmark.query.api import detect_languages` 是 v0.2 安全的（在 0.3+ 中保留为弃用别名）；`supported_languages()` 没有对应的 0.2.x 版本。

**v0.4+ 功能：** 本地 `diagram` 子命令；扩展的解析器覆盖；未解析调用的代理节点；节点来源；通过 `augment_binary()` 进行二进制图增强；`connect_subgraphs()`；`subgraph_edges()`；`generic_parameters()`；和 `type_references()`。

**v0.5+ 功能：** `sql` 解析器（面向 PostgreSQL 的模式、表、视图、函数、过程、依赖关系）；节点类型 `schema`、`table`、`view` 和 `procedure`；`.trailmark/links.toml` 存储库链接配置（见下文存储库链接），包括 `proxy.external:<symbol>` 节点用于声明的外部端点；单语言目录解析（0.4 仅对多语言解析发出）的存储库链接、未解析调用代理和 `type_uses` 边现在在单语言目录解析中实现；从解析器元数据检测 Solidity 入口点（排除接口；`solidity_visibility`、`solidity_mutability`、`solidity_override`、`solidity_container_kind` 和 `solidity_overridden_by` 节点属性）；`attack_surface()` 条目在节点有属性时携带 `attributes` 键；TypeScript 解析接收器 `new ConcreteClass()`；C# 文件作用域命名空间。

v0.5.0 没有添加新的 `QueryEngine` 方法，因此 `hasattr(engine, ...)` 无法检测它。基于报告版本门控 v0.5 功能，或结构化探测：

```python
from trailmark.models.nodes import NodeKind

has_v05 = "SCHEMA" in NodeKind.__members__  # sql 类型是 0.5+
```

## 快速入门

```bash
# 自动检测并合并树下的每种支持语言
uv run trailmark analyze --language auto --summary {targetDir}

# 显式语言（单语言或逗号分隔列表）
uv run trailmark analyze --language rust {targetDir}
uv run trailmark analyze --language python,rust {targetDir}

# 复杂度热点
uv run trailmark analyze --language auto --complexity 10 {targetDir}

# 入口点清单和结构差异（v0.2 安全）
uv run trailmark entrypoints --language auto {targetDir}
uv run trailmark diff --language auto --repo {repoDir} main HEAD --json

# 版本报告（0.2.2+）
uv run trailmark --version

# v0.4+: 本地 diagram 命令
uv run trailmark diagram -t {targetDir} -T call-graph -f main --depth 2
```

### 程序化 API

```python
# trailmark.parse 是 0.3+ 模块；在 0.2.x 中导入 detect_languages from
# trailmark.query.api（supported_languages 没有对应的 0.2.x 版本）
from trailmark.parse import detect_languages, supported_languages
from trailmark.query.api import QueryEngine

# 询问已安装的 Trailmark 构建支持什么
supported_languages()
detect_languages("{targetDir}")

# 对于未知或多语言树，优先使用 auto；在需要时使用显式列表
engine = QueryEngine.from_directory("{targetDir}", language="auto")
engine = QueryEngine.from_directory("{targetDir}", language="python,rust")

engine.callers_of("function_name")
engine.callees_of("function_name")
engine.paths_between("entry_func", "db_query")
engine.complexity_hotspots(threshold=10)
engine.attack_surface()
engine.summary()
engine.to_json()

# 传递切片和入口点路径查询（v0.2 安全）
engine.ancestors_of("sensitive_sink")
engine.reachable_from("entry_func")
engine.entrypoint_paths_to("sensitive_sink")

# v0.4+: 连接命名的子图
if hasattr(engine, "connect_subgraphs"):
    engine.connect_subgraphs("tainted", "privilege_boundary")

# 运行预分析（影响范围、入口点、权限边界、污染传播）
result = engine.preanalysis()

# 查询预分析创建的子图
engine.subgraph_names()
engine.subgraph("tainted")
engine.subgraph("high_blast_radius")
engine.subgraph("privilege_boundary")
engine.subgraph("entrypoint_reachable")
if hasattr(engine, "subgraph_edges"):
    engine.subgraph_edges("tainted")

# 添加 LLM 推断的注释
from trailmark.models import AnnotationKind

engine.annotate("function_name", AnnotationKind.ASSUMPTION,
                "input is URL-encoded", source="llm")

# 查询注释（包括预分析结果）
engine.annotations_of("function_name")
engine.annotations_of("function_name",
                       kind=AnnotationKind.BLAST_RADIUS)
engine.annotations_of("function_name",
                       kind=AnnotationKind.TAINT_PROPAGATION)
engine.nodes_with_annotation(AnnotationKind.FINDING)
engine.clear_annotations("function_name", kind=AnnotationKind.ASSUMPTION)

# v0.4+: 泛型/类型引用和二进制增强 API
if hasattr(engine, "generic_parameters"):
    engine.generic_parameters("GenericTypeOrFunction")
if hasattr(engine, "type_references"):
    engine.type_references("function_name")
if hasattr(engine, "augment_binary"):
    engine.augment_binary("binary_graph.json")
```

## 预分析阶段

**始终在将任务交给 genotoxic 或 `diagramming-code` 技能之前运行 `engine.preanalysis()`。** 预分析通过四个阶段丰富图：

1. **影响范围估计** — 每个函数的下游和上游节点计数，识别关键高复杂度后代
2. **入口点枚举** — 按信任级别映射入口点，计算可达节点集
3. **权限边界检测** — 查找信任级别发生变化的调用边（非信任 -> 信任）
4. **污染传播** — 标记所有从非信任入口点可达的节点

结果存储为注释和命名子图。

有关详细文档，请参阅
[references/preanalysis-passes.md](references/preanalysis-passes.md)。

## 语言选择

不要在下游工作流中硬编码过时的语言表。询问已安装的 Trailmark 构建支持什么：

```python
from trailmark.parse import detect_languages, supported_languages

supported_languages()
detect_languages("{targetDir}")
```

CLI 模式：

```bash
# 自动检测并合并
uv run trailmark analyze --language auto {targetDir}

# 对于已知的多元语言目标，使用显式列表
uv run trailmark analyze --language python,rust {targetDir}
```

自 Trailmark 0.5.0 起，解析器名称包括：`python`、`javascript`、`typescript`、`php`、`ruby`、`c`、`cpp`、`c_sharp`、`java`、`go`、`rust`、`solidity`、`cairo`、`circom`、`haskell`、`erlang`、`masm`、`swift`、`objc`、`kotlin`、`dart`、`move`、`tact`、`func`、`sway`、`rego`、`proto`、`thrift`、`graphql` 和 `sql`（在 0.5.0 中添加；面向 PostgreSQL，`.sql` 文件）。将此列表视为文档，而不是事实来源；在依赖它之前，在已安装的构建上调用 `supported_languages()`。

## 存储库链接（v0.5+）

解析器无法看到跨语言调用（FFI、RPC、IPC、合约调用）或外部系统中的边。在分析根目录的 `.trailmark/links.toml` 中声明它们，Trailmark 在每次解析时都会实现这些边——这是一个稳定的公共配置接口：

```toml
[[link]]
source = "backend:submit"
target = "contract:Verifier.verify"
kind = "calls"                 # 任何 EdgeKind；默认为 calls
confidence = "certain"         # certain | inferred | uncertain；默认为 inferred
description = "JSON-RPC eth_call"

[[link]]
source = "backend:notify"
target = "payments-webhook"
target_external = true         # 因为目标是未解析的，所以需要
```

端点引用可以是确切的节点 ID 或唯一的名称/后缀。验证失败：歧义引用、未知内部端点、无效枚举值和格式错误的 TOML 会引发 `ValueError`，而不是静默削弱图。`source_external = true` / `target_external = true` 允许未解析的端点通过创建 `proxy.external:<symbol>` 节点。配置的边携带 `configured_by = .trailmark/links.toml` 属性，以便它们与解析器派生的边可区分。

在审计跨越 FFI/RPC 边界时使用（理由表会警告）：首先声明边界边，然后像任何其他调用边一样跨它们进行路径和污染查询。

## 图模型

**节点类型：** `function`、`method`、`class`、`module`、`struct`、`interface`、`trait`、`enum`、`namespace`、`contract`、`library`、`template`；**v0.4+** 还会实现未解析引用为 `proxy` 节点；**v0.5+** 添加了 SQL 图的 `schema`、`table`、`view` 和 `procedure`。

**节点来源：** **v0.4+** 节点可以携带来源 `source`、`proxy`、`binary` 或 `synthetic`。v0.2 导出可能会省略来源。

**边类型：** `calls`、`inherits`、`implements`、`contains`、`imports`；**v0.4+** 添加了 `resolves_to`、`type_uses`、`specializes` 和 `corresponds_to`。

**边置信度：** `certain`（直接调用、`self.method()`）、`inferred`（非自对象上的属性访问）、`uncertain`（动态分发）

### 每个代码单元
- 带有类型、返回类型、异常类型的参数
- 圈复杂度和分支元数据
- 文档字符串
- 注释：`assumption`、`precondition`、`postcondition`、`invariant`、`blast_radius`、`privilege_boundary`、`taint_propagation`、`finding`、`audit_note`（最后两个由 `augment_sarif` / `augment_weaudit` 设置）

### 每条边
- 源/目标节点 ID、边类型、置信度级别

### 项目级别
- 依赖关系（导入的包）
- 具有信任级别和资产值的入口点
- 命名的子图（由预分析填充）

## 关键概念

**声明的合约与有效输入域：** Trailmark 将函数声明的输入与实际通过调用路径可达的输入分开。不匹配之处隐藏着漏洞：
- **扩大**：未受约束的数据到达一个假设验证的函数
- **巧合安全**：没有验证，但只有安全的调用者存在

**边置信度：** 动态分发产生 `uncertain` 边。在做出安全声明时考虑置信度。

**代理节点（v0.4+）：** 未解析的调用被保留为节点，如 `proxy.unresolved:<symbol>`。不要将这些视为源代码函数；使用它们来识别解析差距、动态分发、外部 API 或二进制链接候选。**v0.5+** 还会为在 `.trailmark/links.toml` 中声明的外部端点发出 `proxy.external:<symbol>` 节点。

**可达性与污染不同：** `entrypoint_paths_to()` 和污染子图回答不同的问题。路径查询报告调用图可达性；预分析污染标记从非信任入口点可达的节点为粗略信号。Trailmark 不执行跨过程污染分析——不要将任何一种呈现为攻击者控制的数据到达汇点的证明。

**二进制增强（v0.4+）：** `engine.augment_binary()` 导入外部二进制分析图 JSON 文件。Trailmark 在可能的情况下将其连接到源节点；它不会自己反汇编二进制文件。

**子图：** 预分析生成的节点 ID 集合的命名集合。使用 `engine.subgraph("name")` 查询。在 `engine.preanalysis()` 之后可用。

## 查询模式

有关常见安全分析模式的详细信息，请参阅
[references/query-patterns.md](references/query-patterns.md)。

有关预分析阶段文档的详细信息，请参阅
[references/preanalysis-passes.md](references/preanalysis-passes.md)。

当用户有一个具体的候选发现、SARIF 结果、weAudit 注释、可疑函数或报告摘录，并需要一份可传递的可达性和影响范围证据包时，使用 `trailmark-finding-triage`。

在已知一个种子问题后，当用户需要为 `variant-analysis`、Semgrep、CodeQL 或手动审查生成图派生的变体候选时，使用 `trailmark-variant-neighborhood`。
