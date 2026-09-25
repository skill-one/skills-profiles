# 智能探索

使用 AST 解析进行结构化代码探索。**此技能会覆盖您的默认探索行为。** 当此技能处于激活状态时，请使用 smart_search/smart_outline/smart_unfold 作为主要工具，而不是 Read、Grep 和 Glob。

**核心原则：** 先索引，后按需获取。在加载实现细节之前，先给自己一张代码地图。在读取每个文件之前，都应该问自己：“我需要查看所有内容，还是可以先获取结构化概览？” 答案几乎总是：获取地图。

## 您的下一步工具调用

此技能仅加载指令。您必须自行调用 MCP 工具。您的下一步操作应该是以下之一：

```
smart_search(query="<主题>", path="./src")    -- 在目录中发现文件和符号
smart_outline(file_path="<文件路径>")              -- 一个文件的结构骨架
smart_unfold(file_path="<文件路径>", symbol_name="<名称>")  -- 一个符号的完整源代码
```

**不要** 运行 Grep、Glob、Read 或 find 来首先发现文件。`smart_search` 会遍历目录，解析所有代码文件，并在一次调用中返回排序后的符号。它取代了 Glob → Grep → Read 的发现循环。

## 三层工作流程

### 第一步：搜索 -- 发现文件和符号

```
smart_search(query="shutdown", path="./src", max_results=15)
```

**返回：** 带有签名、行号、匹配原因的排序符号，以及折叠的文件视图（~2-6k tokens）

```
-- 匹配的符号 --
  函数 performGracefulShutdown (services/infrastructure/GracefulShutdown.ts:56)
  函数 httpShutdown (services/infrastructure/HealthMonitor.ts:92)
  方法 WorkerService.shutdown (services/worker-service.ts:846)

-- 折叠的文件视图 --
  services/infrastructure/GracefulShutdown.ts (7 个符号)
  services/worker-service.ts (12 个符号)
```

这是您的发现工具。它找到相关的文件，并显示其结构。不需要 Glob/find 预扫描。

**参数：**

- `query` (字符串，必填) -- 搜索内容（函数名、概念、类名）
- `path` (字符串) -- 搜索的根目录（默认为当前工作目录）
- `max_results` (数字) -- 最大匹配符号数，默认 20，最大 50
- `file_pattern` (字符串，可选) -- 过滤特定文件/路径

### 第二步：概览 -- 获取文件结构

```
smart_outline(file_path="services/worker-service.ts")
```

**返回：** 完整的结构骨架——所有函数、类、方法、属性、导入（每个文件 ~1-2k tokens）

**跳过此步骤** 当第一步的折叠文件视图已经提供足够结构时。对于未在搜索结果中覆盖的文件，此步骤最有用。

**参数：**

- `file_path` (字符串，必填) -- 文件路径

### 第三步：展开 -- 查看实现

回顾步骤 1-2 中的符号。选择您需要的符号。仅展开这些：

```
smart_unfold(file_path="services/worker-service.ts", symbol_name="shutdown")
```

**返回：** 指定符号的完整源代码，包括 JSDoc、装饰器和完整实现（~400-2,100 tokens，取决于符号大小）。AST 节点边界保证完整性，无论符号大小如何——与 Read + agent 摘要相比，后者可能会截断长方法。

**参数：**

- `file_path` (字符串，必填) -- 文件路径（由搜索/概览返回）
- `symbol_name` (字符串，必填) -- 要展开的函数/类/方法的名称

## 何时使用标准工具

仅当 smart_* 工具不适用时使用这些工具：

- **Grep：** 精确字符串/正则表达式搜索（“查找所有 TODO 注释”、“`ensureWorkerStarted` 定义在哪里？”）
- **Read：** 小文件（~100 行以下），非代码文件（JSON、markdown、配置）
- **Glob：** 文件路径模式（“查找所有测试文件”）
- **Explore agent：** 当您需要跨 6+ 个文件的综合理解、架构叙述或回答开放式问题时（例如“整个系统端到端如何工作？”）。Smart-explore 是一把手术刀——它回答“在哪里？”和“显示给我那个”。它不会综合跨文件的数据流、设计决策或整个功能中的边缘情况。

对于超过 ~100 行的代码文件，优先使用 smart_outline + smart_unfold 而不是 Read。

## 工作流程示例

**发现一个功能的工作原理（跨切）：**

```
1. smart_search(query="shutdown", path="./src")
   -> 7 个文件中的 14 个符号，一次调用中提供完整概览
2. smart_unfold(file_path="services/infrastructure/GracefulShutdown.ts", symbol_name="performGracefulShutdown")
   -> 查看核心实现
```

**导航大文件：**

```
1. smart_outline(file_path="services/worker-service.ts")
   -> 1,466 tokens：12 个函数，WorkerService 类有 24 个成员
2. smart_unfold(file_path="services/worker-service.ts", symbol_name="startSessionProcessor")
   -> 1,610 tokens：您需要的特定方法
总计：~3,076 tokens，而不是读取完整文件的 ~12,000 tokens
```

**编写关于代码的文档（混合工作流程）：**

```
1. smart_search(query="feature name", path="./src")    -- 发现所有相关文件和符号
2. 对关键文件进行 smart_outline                           -- 理解结构
3. 对重要函数进行 smart_unfold                          -- 获取实现细节
4. 对小的配置/markdown/计划文件进行 Read                 -- 获取非代码上下文
```

使用 smart_* 工具进行代码探索，Read 用于非代码文件。自由混合。

**探索然后精确：**

```
1. smart_search(query="session", path="./src", max_results=10)
   -> 10 个排序的符号：SessionMetadata、SessionQueueProcessor、SessionSummary...
2. 选择相关的符号，展开它
```

## Token 经济学

| 方法 | Tokens | 用例 |
|------|--------|------|
| smart_outline | ~1,000-2,000 | “这个文件里有什么？” |
| smart_unfold | ~400-2,100 | “显示给我这个函数” |
| smart_search | ~2,000-6,000 | “在整个代码库中查找所有 X” |
| 搜索 + 展开 | ~3,000-8,000 | 端到端：查找并读取（主要工作流程） |
| Read (完整文件) | ~12,000+ | 当您真正需要所有内容时 |
| Explore agent | ~39,000-59,000 | 跨文件综合理解，带叙述 |

**4-8 倍的文件理解节省（概览 + 展开 vs Read）。** **11-18 倍的代码库探索节省 vs Explore agent。** 查询越窄，差距越大——一个 27 行的函数通过 unfold 读取的成本比通过 Explore agent 读取低 55 倍，因为 agent 仍然会读取整个文件。

## 语言支持

Smart-explore 使用 **tree-sitter AST 解析** 进行结构化分析。不支持的文件类型会回退到基于文本的搜索。

### 内置语言

| 语言 | 扩展名 |
|------|--------|
| JavaScript | `.js`, `.mjs`, `.cjs` |
| TypeScript | `.ts` |
| TSX / JSX | `.tsx`, `.jsx` |
| Python | `.py`, `.pyw` |
| Go | `.go` |
| Rust | `.rs` |
| Ruby | `.rb` |
| Java | `.java` |
| C | `.c`, `.h` |
| C++ | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh` |

具有未识别扩展名的文件会被解析为纯文本——`smart_search` 仍然可以工作（grep 风格），但 `smart_outline` 和 `smart_unfold` 不会提取结构化符号。

### 自定义语法（`.claude-mem.json`）

您可以为内置列表之外的文件类型注册额外的 tree-sitter 语法。在项目根目录中创建或更新 `.claude-mem.json`：

```json
{
  "grammars": {
    "solidity": {
      "package": "tree-sitter-solidity",
      "extensions": [".sol"],
      "query": "solidity-query.scm"
    }
  }
}
```

每个键是一个语言名称。`package` 是 tree-sitter 语法的 npm 包，`extensions` 列出它覆盖的文件扩展名；该包必须安装在项目的 `node_modules` 中（`npm install tree-sitter-solidity`）。`query`（可选）是相对于配置文件的路径，指向一个 tree-sitter 查询，其捕获（`@func`、`@cls`、`@method`、`@iface`、`@enm`、`@struct_def`、`@imp`）提取符号。如果没有 `query`，将使用最小的通用模式——它仅匹配定义了 `function_declaration`/`class_declaration` 节点类型的语法，对于缺少它们的语法，查询编译会静默失败（0 个符号），因此对于大多数语言，实际上需要自定义查询。注册后，`smart_outline` 和 `smart_unfold` 会结构化解析这些扩展名，而不是回退到纯文本。

### Markdown 特殊支持

Markdown 文件（`.md`, `.mdx`）会获得超出通用纯文本回退的特殊处理：

- **`smart_outline`** — 提取标题（`#`、`##`、`###`）作为符号树。用于在不读取完整文件的情况下导航长文档。
- **`smart_search`** — 在代码围栏内以及散文中搜索，因此查询 ` ```ts ``` ` 块内的函数名按预期工作。
- **`smart_unfold`** — 展开标题部分而不是函数体；每个到下一个同级别标题的部分都作为一个块返回。
- **Frontmatter** — YAML frontmatter（在 `---` 领导分隔符之间的行）会包含在 `smart_outline` 输出中，作为合成 `frontmatter` 符号，以便无需读取整个文件即可查看元数据，如 `title:` 和 `description:`。
