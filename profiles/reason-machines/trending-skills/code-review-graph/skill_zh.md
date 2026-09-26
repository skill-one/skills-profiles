# code-review-graph

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

`code-review-graph` 使用 Tree-sitter 构建代码库的持久化结构图，将其存储在本地 SQLite 图中，并通过 MCP 向 Claude 暴露。Claude 不再在每次任务时重新读取整个项目，而是查询图，并只读取变更影响范围内的文件 — 在大型单体仓库中，代码审查平均减少 6.8 倍的 token，日常编码任务最多减少 49 倍。

---

## 安装

### Claude 代码插件（推荐）

```bash
claude plugin marketplace add tirth8205/code-review-graph
claude plugin install code-review-graph@code-review-graph
```

安装后重启 Claude 代码。

### pip

```bash
pip install code-review-graph
code-review-graph install   # 将 MCP 服务器注册到 Claude 代码
```

需要 Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)。

### 可选：语义搜索支持

```bash
pip install code-review-graph[embeddings]
```

为 `semantic_search_nodes_tool` 启用 `sentence-transformers` 的向量嵌入。

---

## 初始设置

安装后，在 Claude 代码中打开您的项目并运行：

```
为这个项目构建代码审查图
```

或者使用斜杠命令：

```
/code-review-graph:build-graph
```

首次构建会解析整个代码库（500 个文件约需 10 秒）。之后，图会在每次文件保存和 git 提交时增量更新（2,900 个文件的项目增量解析时间少于 2 秒）。

---

## CLI 参考

```bash
# 将 MCP 服务器注册到 Claude 代码
code-review-graph install

# 将整个代码库解析到图中（首次运行）
code-review-graph build

# 仅重新解析已更改的文件（后续运行）
code-review-graph update

# 显示图统计信息：节点数、边数、语言分布
code-review-graph status

# 在保存文件时自动更新图（持续监控模式）
code-review-graph watch

# 生成交互式 D3.js HTML 图形可视化
code-review-graph visualize

# 手动启动 MCP 服务器（Claude 代码会自动启动）
code-review-graph serve
```

---

## Claude 代码中的斜杠命令

| 命令 | 功能 |
|---|---|
| `/code-review-graph:build-graph` | 从头开始构建或重建代码图 |
| `/code-review-graph:review-delta` | 审查自上次提交以来的变更 |
| `/code-review-graph:review-pr` | 带有影响范围分析的完整 PR 审查 |

---

## MCP 工具（Claude 自动使用）

构建图后，Claude 会自动调用这些工具，无需手动提示：

| 工具 | 目的 |
|---|---|
| `build_or_update_graph_tool` | 构建或增量更新图 |
| `get_impact_radius_tool` | 查找受变更影响的文件/函数 |
| `get_review_context_tool` | 返回用于审查的 token 优化结构摘要 |
| `query_graph_tool` | 查询调用者、被调用者、测试、导入、继承 |
| `semantic_search_nodes_tool` | 通过名称或含义搜索代码实体 |
| `embed_graph_tool` | 为语义搜索计算向量嵌入 |
| `list_graph_stats_tool` | 图大小和健康统计信息 |
| `get_docs_section_tool` | 检索文档部分 |
| `find_large_functions_tool` | 查找超过行数阈值的函数/类 |

---

## 配置：忽略路径

在仓库根目录创建 `.code-review-graphignore`：

```
generated/**
*.generated.ts
vendor/**
node_modules/**
dist/**
__pycache__/**
*.pyc
migrations/**
```

图在构建和更新时将跳过这些路径。

---

## Python API

图可以通过自定义工具或脚本进行程序化查询。

### 构建和更新图

```python
from code_review_graph import GraphBuilder

builder = GraphBuilder(repo_path="/path/to/your/project")

# 全部构建（首次）
stats = builder.build()
print(f"节点: {stats['nodes']}, 边: {stats['edges']}")

# 增量更新（后续运行 — 仅解析已更改的文件）
update_stats = builder.update()
print(f"重新解析: {update_stats['files_updated']} 个文件")
```

### 查询图

```python
from code_review_graph import GraphQuery

query = GraphQuery(repo_path="/path/to/your/project")

# 查找函数的所有调用者
callers = query.get_callers("authenticate_user")
print(callers)
# ['api/views.py::login_view', 'tests/test_auth.py::test_login']

# 查找函数的所有被调用者（被函数调用的函数）
callees = query.get_callees("process_payment")
print(callees)

# 查找覆盖文件的测试
tests = query.get_tests_for("payments/processor.py")
print(tests)

# 获取类的继承链
parents = query.get_inheritance("AdminUser")
print(parents)
# ['BaseUser', 'PermissionMixin']
```

### 影响范围分析

```python
from code_review_graph import ImpactAnalyzer

analyzer = ImpactAnalyzer(repo_path="/path/to/your/project")

# 如果这个文件变更，什么会被影响？
impact = analyzer.get_impact_radius("auth/models.py")
print(impact)
# {
#   "直接调用者": ["api/views.py", "middleware/auth.py"],
#   "传递依赖": ["api/tests/test_views.py", "integration/test_flow.py"],
#   "测试文件": ["tests/test_auth.py"],
#   "影响范围大小": 7
# }

# 多个已更改文件（例如来自 git diff）
changed_files = ["auth/models.py", "payments/processor.py"]
combined_impact = analyzer.get_impact_radius(changed_files)
```

### 语义搜索

```python
from code_review_graph import SemanticSearch

# 需要: pip install code-review-graph[embeddings]
search = SemanticSearch(repo_path="/path/to/your/project")

# 嵌入图（一次性，缓存）
search.embed()

# 通过概念搜索代码实体
results = search.search("rate limiting middleware", top_k=5)
for r in results:
    print(r["node"], r["file"], r["score"])
```

### 查找大型函数

```python
from code_review_graph import GraphQuery

query = GraphQuery(repo_path="/path/to/your/project")

# 查找超过 50 行的函数/类（适合重构目标）
large = query.find_large_functions(threshold=50)
for item in large:
    print(f"{item['name']} in {item['file']}: {item['lines']} 行")
```

---

## 常见模式

### 模式：仅审查当前分支中更改的内容

```bash
# 在 Claude 代码中，在做出更改后：
/code-review-graph:review-delta
```

Claude 将：
1. 调用 `build_or_update_graph_tool` 以同步图与您的编辑
2. 对已更改文件调用 `get_impact_radius_tool`
3. 调用 `get_review_context_tool` 获取紧凑的结构摘要
4. 仅审查相关的 ~15 个文件，而不是整个代码库

### 模式：开发期间持续监控

```bash
# 终端 1：在编码时保持图最新
code-review-graph watch

# 终端 2：您的正常开发工作流程
```

任何文件保存都会触发仅对该文件及其依赖的增量解析。

### 模式：预提交钩子

```bash
# .git/hooks/pre-commit
#!/bin/sh
code-review-graph update
```

在 Claude 看到提交之前使图始终保持最新。

### 模式：可视化依赖图

```bash
code-review-graph visualize
# 在您的浏览器中打开交互式 D3.js 力导向图
# 切换边类型：调用、导入、继承、测试覆盖
# 通过名称搜索节点
```

### 模式：检查图健康状态

```bash
code-review-graph status
# 示例输出：
# 图: .code-review-graph/graph.db
# 节点: 4,821 (函数: 2,103 | 类: 487 | 文件: 312)
# 边: 11,204 (调用: 7,891 | 导入: 2,108 | 继承: 205 | 测试: 1,000)
# 语言: Python (180), TypeScript (98), JavaScript (34)
# 最后更新: 2026-03-26 01:22:11 (3 个文件已更改)
```

---

## 支持的语言

Python、TypeScript、JavaScript、Vue、Go、Rust、Java、C#、Ruby、Kotlin、Swift、PHP、Solidity、C/C++

每种语言都有完整的 Tree-sitter 语法支持：函数、类、导入、调用位点、继承链和测试检测。

---

## 添加新语言

编辑 `code_review_graph/parser.py`：

```python
# 1. 添加文件扩展名映射
EXTENSION_TO_LANGUAGE = {
    # ... 现有条目 ...
    ".ex": "elixir",
    ".exs": "elixir",
}

# 2. 添加新语言 AST 节点类型映射
_CLASS_TYPES["elixir"] = {"defmodule"}
_FUNCTION_TYPES["elixir"] = {"def", "defp"}
_IMPORT_TYPES["elixir"] = {"alias", "import", "use", "require"}
_CALL_TYPES["elixir"] = {"call"}
```

然后添加测试用例到 `tests/fixtures/elixir/` 并打开 PR。

---

## 图存储位置

图存储在本地 `.code-review-graph/graph.db`（SQLite）。没有外部数据库，没有云依赖，且数据不会离开您的机器。如果您不想提交，将其添加到 `.gitignore`：

```bash
echo ".code-review-graph/" >> .gitignore
```

或者提交以与您的团队共享预构建的图（为每个开发者节省 ~10 秒的首次构建时间）。

---

## 故障排除

### 图已过时 / 未反映最近的变更

```bash
code-review-graph update    # 已更改文件的增量解析
# 或者，如果似乎有问题：
code-review-graph build     # 从头开始重建
```

### MCP 服务器无法连接到 Claude 代码

```bash
# 重新注册 MCP 服务器
code-review-graph install

# 验证是否已注册
claude mcp list
```

然后重启 Claude 代码。

### `uv` 未找到

```bash
# 安装 uv（MCP 服务器运行器所需）
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或者
pip install uv
```

### 语义搜索不工作

```bash
# 安装嵌入扩展
pip install "code-review-graph[embeddings]"

# 计算嵌入（安装后需要调用一次）
code-review-graph embed    # 或者通过 Claude 调用 embed_graph_tool
```

### 某种语言没有被解析

确保文件扩展名在 `EXTENSION_TO_LANGUAGE` 中，并且相应的 Tree-sitter 语法已安装。运行 `code-review-graph status` 查看项目中检测到的语言。

### 首次构建缓慢

正常 — Tree-sitter 解析每个文件。500 个文件的项目需要 ~10 秒。所有后续的 `update` 调用都在 2 秒内完成，因为仅重新解析已更改的文件（通过 SHA-256 哈希比较检测）。

---

## token 减少的工作原理

在每次审查或编码任务中：

1. **图查询**：Claude 调用 `get_impact_radius_tool` 使用已更改的文件
2. **影响范围跟踪**：图沿着调用边、导入边和测试边查找每个受影响的节点
3. **紧凑摘要**：`get_review_context_tool` 返回 156–207 token 的结构摘要（调用者、依赖项、测试覆盖差距、依赖链）
4. **目标读取**：Claude 仅读取影响范围内的 ~15 个文件，而不是整个代码库

在 Next.js 单体仓库（27,732 个文件）中：没有图时 Claude 读取 ~739K token；有图时读取 ~15K token — 减少 49 倍。
