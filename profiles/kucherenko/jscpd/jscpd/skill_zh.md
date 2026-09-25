# jscpd

编程源代码的复制粘贴检测器，支持220多种语言。使用此技能运行 jscpd 并理解其输出。

## 快速入门

```bash
# 使用ai报告器运行（为代理优化的紧凑输出）
npx jscpd --reporters ai <路径>

# 带有忽略模式
npx jscpd --reporters ai --ignore "**/node_modules/**,**/dist/**" <路径>

# 限制于特定格式
npx jscpd --reporters ai --format "javascript,typescript" <路径>

# 第二遍，更嘈杂：仅名称和值不同的复制（Type-2，“重命名”）。
# 在采取行动之前，请先审查每个匹配项。
npx jscpd --reporters ai --ignore-identifiers --min-tokens 70 <路径>

# 第三遍，仍然更嘈杂：几行编辑或具有相同函数结构的复制（Type-3，“相似”）。
# 保持设置紧凑。
npx jscpd --reporters ai --max-gap-lines 1 --similarity 0.85 <路径>

# 首次重构的位置：克隆列表加上热点摘要
npx jscpd --reporters ai --summary <路径>

# 仅最复杂的文件，不进行克隆检测
npx jscpd --complexity --reporters ai <路径>
```

## AI报告器输出格式

`ai` 报告器生成紧凑、高效的标记输出，专为代理消费设计：

```
克隆：
src/ foo.ts:10-25 ~ bar.ts:42-57
src/utils/helpers.ts:100-120 ~ src/utils/other.ts:5-25
src/cart/ basket.js:1-9 ~ cart.js:1-9 (重命名)
src/api/ save-account.js:1-12 ~ save-user.js:1-11 [~0.91 gap]
src/billing/ credit-note.js:1-19 ~ invoice.js:1-17 [~0.75 ast]
---
5个克隆 · 4.2% 重复率
```

每一行代表一个克隆对：
- **相同文件**：`path/file.ts 10-25 ~ 45-60`（共享路径仅显示一次）
- **相同目录**：`shared/prefix/ file-a.ts:10-25 ~ file-b.ts:42-57`（公共前缀已提取）
- **不同路径**：`path/a.ts:10-25 ~ path/b.ts:42-57`

后缀表示克隆的**类型**；无后缀表示精确复制：
- `(重命名)`：两个块仅在标识符名称、字面值或注解上不同（Type-2）。仅在 `--ignore-identifiers`、`--ignore-literals` 或 `--ignore-annotations` 时出现。
- `[~0.91 gap]`：两个精确克隆跨越最多 `--max-gap-lines` 未匹配的行（Type-3）。数字是合并范围内的匹配标记数。
- `[~0.75 ast]`：两个函数的语法树结构至少重叠 `--similarity`（Type-3）。数字是结构相似度，名称和字面值不计入。

## 选项

| 选项 | 描述 |
|------|------|
| `--reporters ai` | 使用AI优化的报告器（为代理优化的紧凑克隆列表） |
| `--reporters html` | 生成HTML报告 |
| `--reporters json` | 输出JSON报告 |
| `--min-tokens N` | 将N个标记视为重复的最小值（默认：50） |
| `--min-lines N` | 将N行视为重复的最小值（默认：5） |
| `--threshold N` | 如果重复率超过N，则退出并报错 |
| `--ignore "glob"` | 忽略模式（逗号分隔） |
| `--format "list"` | 限制于特定语言（例如 `typescript,javascript`） |
| `--cross-formats "groups"` | 检测跨相关格式的克隆（例如 `javascript,typescript` 或 `js-ts` 预设） |
| `--ignore-identifiers` | 将所有标识符视为相等，因此仅在变量、函数或类型名称上不同的块匹配（Type-2，报告为 `重命名`） |
| `--ignore-literals` | 将所有字符串字面值视为相等，并将所有数值字面值视为相等（Type-2） |
| `--ignore-annotations` | 在匹配之前删除 `@Name` / `@Name(...)` 注解和装饰器，在 `@` 表示一个的编程语言中（Type-2） |
| `--max-gap-lines N` | 将一个文件对中最多N行未匹配的克隆合并为一个 `相似` 克隆（Type-3，默认：0 = 关闭） |
| `--similarity RATIO` | 报告JavaScript/TypeScript函数对，其语法树相似度达到RATIO，在 `(0, 1]` 中，作为 `相似` 克隆（Type-3，默认：1 = 仅精确匹配） |
| `--summary` | 追加代码库摘要：按标记、行数、大小、复杂度排序的顶级文件/文件夹，以及重复率 |
| `--summary-top N` | 每个摘要列表中的条目数（默认：10） |
| `--summary-by metric` | 摘要排名指标：`tokens`、`lines`、`size`、`complexity`（默认：`tokens`） |
| `--kind list` | 仅报告这些克隆类型：`exact`、`renamed`、`similar`、`gap`、`ast`（永远不会启用检测器） |
| `--complexity` | 仅报告复杂度表，不进行克隆检测（报告器：console、ai、json） |
| `--dead-code` | 查找未使用的文件、导出、模块私有声明和导入 — JavaScript、TypeScript、JSX、TSX、Vue、Svelte、Astro、Python。每个发现都带有0-100的置信度分数 |
| `--dead-code-categories list` | 限制 `--dead-code`/`--dashboard` 于类别：`unused-file`、`unused-export`、`unused-symbol`、`unused-import` |
| `--min-confidence N` | `--dead-code`/`--dashboard` 发现的底部，0-100（默认：60） |
| `--entry "glob"` | 除 `package.json`/`pyproject.toml`/框架约定推断之外，额外的入口点，用于未使用代码分析 |
| `--include-tests` | 将仅测试的用法计为“已使用”，用于未使用代码分析（默认排除） |
| `--include-entry-exports` | 同时标记入口文件自己的未使用导出（默认排除：其导出是公共API） |
| `--dashboard` | 一屏：健康徽章、项目大小和最大代码文件、重复率、复杂度、未使用代码（JS/TS/Python）； `-r json` 写入 `jscpd-dashboard.json` |
| `--health` | 仅项目健康徽章：0-100分数和等级，来自重复率、未使用代码和复杂度（`-r ai` 一行，`-r json`，`-r badge`） |
| `--health-input FILE` | 将其他工具（覆盖率、测试、安全）的指标添加到健康分数中 |
| `--pattern "glob"` | 选择文件的Glob模式 |
| `--no-gitignore` | 不尊重 `.gitignore`（默认尊重） |
| `--output "path"` | 写入报告的目录 |
| `--silent` | 抑制控制台输出（与文件报告器和 `--output` 一起使用时有用） |
| `--list` | 列出所有支持的格式并退出 |
| `--no-tips` | 禁用输出中的提示（当stdout不是TTY或 `CI` 或 `JSCPD_NO_TIPS` 设置时自动跳过） |
| `--config "path"` | .jscpd.json配置文件的路径 |

## 克隆类型：精确、重命名、相似

默认情况下，jscpd 仅报告**精确**克隆：标记序列完全相同（空白、布局和，取决于模式，注释不计入）。两个可选系列扩大了范围。将它们作为默认扫描的单独遍历运行，因为它们找到更多和更长的克隆，并改变了“克隆”的含义。

**这些遍历是设计上嘈杂的。** 精确克隆几乎总是真实的副本。重命名或相似的克隆是*候选者*：标志故意忽略了通常使两个块不同的东西（名称、值、一个语句或两条语句）。预期会产生误报：

- 热身板应看起来相似：DTO和模型、配置表、类似枚举的映射、路由或处理器注册、构建器
- 测试文件：`describe`/`it`块、固定和设置代码故意重复相同的形状
- 生成代码、迁移、序列化器、协议绑定
- 语言习语：两个 `reduce` 循环或两个 `switch` 语句共享结构但不共享逻辑
- 小块：在 `--ignore-identifiers` 下，50个标记的块大部分是占位符，因此提高 `--min-tokens`

管理噪声的规则：

- 在处理精确克隆后运行它们，一次一个系列，以便每个匹配项可归因于一个标志。
- 从保守开始：`--ignore-identifiers` 单独使用（仅在知道常量是问题时添加 `--ignore-literals`），`--max-gap-lines 1` 或 `2`，`--similarity 0.85` 或更高，以及 `--min-tokens 70` 或更多用于标识符遍历。仅在紧密运行返回空时才放宽。
- 将每个 `(重命名)` 或 `[~…]` 行视为要阅读的线索，而不是要修复的缺陷。不要在CI上设置门禁（`--threshold`，`--fail-on-new-clones`）在这些遍历上，除非团队已审查代码库上报告的内容。
- 从规范化运行中永远不会声称“找到N个重复”而未说明是哪些标志产生的。

### Type-2：重命名克隆（`--ignore-identifiers`、`--ignore-literals`、`--ignore-annotations`）

有人重命名变量或更改常量的副本：

```bash
npx jscpd --reporters ai --ignore-identifiers <路径>                      # function a(x) {…} 匹配 function b(y) {…}
npx jscpd --reporters ai --ignore-identifiers --ignore-literals <路径>    # …以及 10 匹配 25，'dev' 匹配 'prod'
npx jscpd --reporters ai --ignore-annotations <路径>                      # @Override / @Deprecated 不再分割一个克隆
```

```
克隆：
basket.js:1-9 ~ cart.js:1-9 (重命名)
limits-dev.js:1-13 ~ limits-prod.js:1-13 (重命名)
---
```

- 关键字保持其含义（`return` 永远不匹配 `retry`），因此结构仍然必须匹配。
- `--ignore-annotations` 仅在Java、Kotlin、Scala、Groovy、Python、Dart、Swift、JavaScript和TypeScript中起作用；在Ruby、Perl、T-SQL、Razor和CSS中 `@` 表示其他含义，因此保持不变。
- 报告中的位置仍然指向原始源。
- 配置键：`ignoreIdentifiers`、`ignoreLiterals`、`ignoreAnnotations`。

### Type-3：近似克隆（`--max-gap-lines`、`--similarity`）

几行编辑的副本，或具有相同形状重写的函数：

```bash
npx jscpd --reporters ai --max-gap-lines 2 <路径>      # 一个最多有2行插入/更改的副本成为一个克隆
npx jscpd --reporters ai --similarity 0.8 <路径>       # ≥80%共享语法树结构的JS/TS函数
```

```
克隆：
save-account.js:1-12 ~ save-user.js:1-11 [~0.91 gap]
credit-note.js:1-19 ~ invoice.js:1-17 [~0.75 ast]
---
```

- `--max-gap-lines N` 仅连接精确运行已找到的克隆，因此它移除碎片而不是发明匹配；它在每种语言中都起作用。当间隙中的标记数多于共享的一半时，拒绝合并（相似度会低于 `0.5`）。
- `--similarity RATIO` 通过其语法树节点类型的4-gram包来比较整个函数，因此重命名副本得分为 `1.0`，插入一行约 `0.9`，添加两个语句和重命名约 `0.75`。目前它仅适用于JavaScript、TypeScript、JSX和TSX；其他格式是静默无操作。从 `0.85` 开始近似结构，并降低到 `0.7` 仅当寻找线索时；低于 `0.8` 时，大部分对仅共享一个习语，因此阅读两个函数后再相信分数。
- `similar` 在两者都适用时优先于 `renamed`（合并后的克隆即使在规范化后也不再是精确匹配）。
- 配置键：`maxGapLines`、`similarity`。

### 类型显示的位置

- `console`：`Clone found (javascript, renamed)`，`Clone found (javascript, similar (gap) ~0.91)`，`Clone found (javascript, similar (ast) ~0.75)`。
- `json`：`"kind": "exact" | "renamed" | "similar"`，加上 `"similarity"` 和 `"method": "gap" | "ast"` 对于相似克隆。
- `sarif`：规则 `jscpd/duplicate-code`，`jscpd/renamed-code`，`jscpd/similar-code`；Code Climate使用相同的三个 `check_name` 值。
- 默认运行仅报告 `exact` 克隆，其输出不受这些功能的影响。
- 规范化运行产生的克隆指纹与精确运行不同：为每个配置保留一个单独的 `--baseline` 文件。

## 代码库摘要（`--summary`）

`--summary` 追加重构热点概述到运行输出 — 使用它来决定**首次重构的位置**，然后再深入到单个克隆：

```bash
# 紧凑克隆列表 + 紧凑摘要，为代理优化
npx jscpd --reporters ai --summary --no-tips <路径>

# 按复杂度而不是标记排名，前5列表
npx jscpd --reporters ai --summary --summary-by complexity --summary-top 5 <路径>
```

使用 `ai` 报告器，摘要每条记录一行：

```
按标记摘要（321个文件，129个文件夹）：
files (tokens/lines/size/cx/dup%）：
src/files.ts 2052/363/11662/80/0.0%
long-line/theme-branded.js 498/15/2.5K/10/93.3%
...
folders (files/tokens/lines/size）：
src/core 8/5264/843/27136
...
```

如何阅读它：
- **顶级文件** 按摘要指标排名，但每一行都包含所有指标 — `tokens/lines/size/cx/dup%`。
- **cx** 是从标记流中获取的语言无关的圈复杂度估计（1 + 类似 `if`/`while`/`&&` 的决策点标记）；将其视为排名信号，而不是精确指标。
- **dup%** 是文件行中检测到的克隆的份额 — 一个具有高 `dup%` 的大文件是重构的最佳目标。它反映了当前运行的克隆，因此随着 Type-2/Type-3 标志它会相应增加。
- **文件夹** 将文件聚合到其直接父目录（没有累积祖先总计）。
- 在 `console` 报告器中，摘要以对齐表格呈现；在 `json` 报告中，它作为附加的 `summary` 键出现（当标志关闭时不出现）。

配置文件等效：`"summary": true`，`"summaryTop": 10`，`"summaryBy": "tokens"`。

## 跨格式克隆检测

默认情况下，每种格式仅与其自身比较。`--cross-formats` 定义了共享一个比较池的格式组，因此 `.js` 和 `.ts` 文件之间的副本会报告为克隆：

```bash
# 一个组：一起比较JavaScript和TypeScript文件
npx jscpd --reporters ai --cross-formats "javascript,typescript" <路径>

# 覆盖javascript、jsx、typescript、tsx的预设
npx jscpd --reporters ai --cross-formats "js-ts" <路径>

# 多个组由分号分隔
npx jscpd --reporters ai --cross-formats "javascript,typescript;css,scss" <路径>
```

注意：
- 当一个组混合TypeScript和JavaScript时，TS文件会与可擦除的类型语法剥离进行比较，因此 `function f(a: number): void` 匹配 `function f(a)`。报告的位置仍然指向原始源。
- 组至少需要两种格式；共享相同格式的组会合并为一个池。
- 在每个格式的统计中，跨格式克隆归属于组的其中一个成员格式。
- 在配置文件中，键是 `crossFormats`（或 `cross-formats`），接受字符串（`"javascript,typescript;css,scss"`）、字符串数组（`["javascript,typescript", "css,scss"]`）或数组数组（`[["javascript","typescript"],["css","scss"]]`）。

## 配置文件

在项目根目录中创建一个 `.jscpd.json`：

```json
{
  "threshold": 0,
  "reporters": ["ai"],
  "ignore": ["**/node_modules/**", "**/dist/**", "**/*.min.*"],
  "format": ["typescript", "javascript"],
  "minLines": 5,
  "minTokens": 50,
  "ignoreIdentifiers": false,
  "ignoreLiterals": false,
  "maxGapLines": 0,
  "similarity": 1,
  "summary": false,
  "output": "./reports/jscpd"
}
```

## 重构重复代码

一旦检测到克隆，使用**dry-refactoring**技能进行引导工作流程以消除它们，每个克隆类型都有策略：

→ **dry-refactoring** — 步步重构策略和工作流程，用于删除重复。安装方式：
  ```bash
  npx skills add https://github.com/kucherenko/jscpd --skill dry-refactoring
  ```

## 提高整体代码库健康

对于更广泛的“清理这个代码库”遍历 — 重复、然后未使用代码、然后最大/最复杂的文件，优先级从 `--health`/`--dashboard` 并在结束时重新测量 — 使用 **codebase-refactoring**：

  ```bash
  npx skills add https://github.com/kucherenko/jscpd --skill codebase-refactoring
  ```
