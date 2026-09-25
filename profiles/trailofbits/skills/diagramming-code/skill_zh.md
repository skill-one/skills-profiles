# 绘制代码图

从 Trailmark 的代码图中生成 Mermaid 图表。一个预制的脚本处理 Mermaid 语法生成；Claude 选择图表类型和参数。Trailmark 0.4.0 包含一个原生的 `trailmark diagram` 命令；在版本/命令检查后使用它，否则使用此技能捆绑的脚本。

## 使用场景

- 可视化函数之间的调用路径
- 绘制类继承层次结构
- 映射模块导入依赖关系
- 显示包含成员的类结构
- 使用颜色编码突出显示复杂度热点
- 追踪从入口点到敏感函数的数据流

## 不适用场景

- 无可视化查询图（使用 `trailmark` 技能）
- 变异测试筛选（使用 `genotoxic` 技能）
- 非代码派生的架构图（手绘）

## 前置条件

**trailmark** 必须已安装。如果 `uv run trailmark` 失败，运行：

```bash
uv tool install trailmark
# Python 代码片段：uv run --with trailmark python -   （工具环境不可导入）
```

**不要** 从源代码阅读中回退到手写 Mermaid。脚本使用 Trailmark 解析的图来保证准确性。如果安装失败，向用户报告错误。

## 版本门禁

检查原生 v0.4 图表支持是否存在：

```bash
trailmark diagram --help 2>/dev/null || uv run trailmark diagram --help 2>/dev/null
```

如果成功，你可以使用 `trailmark diagram`。如果失败，使用 `uv run {baseDir}/scripts/diagram.py`，这保留了旧的技能工作流程。不要假设 Trailmark 0.2.x 上存在原生 CLI。

---

## 快速入门

```bash
uv run {baseDir}/scripts/diagram.py \
    --target {targetDir} --language auto --type call-graph \
    --focus main --depth 2

# Trailmark 0.4.0+ 成功后等效
uv run trailmark diagram \
    --target {targetDir} --language auto --type call-graph \
    --focus main --depth 2
```

输出是原始的 Mermaid 文本。用代码块包裹：

````markdown
```mermaid
flowchart TB
    ...
```
````

---

## 图表类型

```
├─ "谁调用谁？"               → --type call-graph
├─ "类继承？"             → --type class-hierarchy
├─ "模块依赖？"           → --type module-deps
├─ "类成员和结构？"   → --type containment
├─ "复杂度最高在哪里？"   → --type complexity
└─ "从输入到函数的路径？"   → --type data-flow
```

有关每种类型的详细示例，请参阅
[references/diagram-types.md](references/diagram-types.md)。

---

## 工作流程

```
图表进度：
- [ ] 第 1 步：验证 trailmark 是否已安装
- [ ] 第 2 步：根据用户请求确定图表类型
- [ ] 第 3 步：确定焦点节点和参数
- [ ] 第 4 步：运行 diagram.py 脚本（或 v0.4+ 上的原生 trailmark diagram）
- [ ] 第 5 步：验证输出非空且格式良好
- [ ] 第 6 步：在响应中嵌入图表
```

**第 1 步：** 运行 `uv run trailmark analyze --language auto --summary {targetDir}`。如果失败则安装。然后通过程序化 API 运行预分析：

```python
from trailmark.query.api import QueryEngine

engine = QueryEngine.from_directory("{targetDir}", language="auto")
engine.preanalysis()
```

预分析用 blast radius、taint 传播和权限边界数据丰富图，这些数据用于 `data-flow` 图表。

如果目标自动检测错误，使用显式语言或逗号分隔列表（如 `python,rust`）重新运行。

**第 2 步：** 使用上述决策树将用户请求匹配到 `--type`。

**第 3 步：** 对于 `call-graph` 和 `data-flow`，确定焦点函数。默认 `--depth 2`。使用 `--direction LR` 用于依赖流。

**第 4 步：** 运行脚本并捕获 stdout。
如果原生 v0.4 CLI 可用，任一命令均可接受；当需要与此技能参考一致的行为时，优先使用捆绑脚本。

**第 5 步：** 检查：输出以 `flowchart` 或 `classDiagram` 开头，至少包含一个节点。如果为空或格式错误，请参阅
[references/mermaid-syntax.md](references/mermaid-syntax.md)。

**第 6 步：** 用 ` ```mermaid ``` ` 代码块包裹输出。

---

## 脚本参考

```
uv run {baseDir}/scripts/diagram.py [OPTIONS]
# 或，在 Trailmark 0.4.0+ 上：
uv run trailmark diagram [OPTIONS]
```

| 参数 | 短选项 | 默认值 | 描述 |
|---|---|---|---|
| `--target` | `-t` | 必填 | 分析目录 |
| `--language` | `-l` | `python` | 源语言 |
| `--type` | `-T` | 必填 | 图表类型（见上文） |
| `--focus` | `-f` | 无 | 将图表中心置于此节点 |
| `--depth` | `-d` | `2` | BFS 遍历深度 |
| `--direction` | | `TB` | 布局：`TB`（自上而下）或 `LR`（自左向右） |
| `--threshold` | | `10` | `complexity` 类型的最小复杂度 |

### 示例

```bash
# 以函数为中心的调用图
uv run {baseDir}/scripts/diagram.py -t src/ -T call-graph -f parse_file

# Rust 项目的类继承层次结构
uv run {baseDir}/scripts/diagram.py -t src/ -l rust -T class-hierarchy

# 从左到右的模块依赖图
uv run {baseDir}/scripts/diagram.py -t src/ -T module-deps --direction LR

# 类成员
uv run {baseDir}/scripts/diagram.py -t src/ -T containment

# 复杂度热力图（阈值 5）
uv run {baseDir}/scripts/diagram.py -t src/ -T complexity --threshold 5

# 从入口点到特定函数的数据流
uv run {baseDir}/scripts/diagram.py -t src/ -T data-flow -f execute_query
```

---

## 定制

**方向：** 使用 `TB`（默认）用于层次结构视图，`LR` 用于自左向右的依赖链。

**深度：** 增加 `--depth` 以查看更多调用图。减少以减少杂乱。如果图表超过 100 个节点，脚本会发出警告。

**焦点：** 对于非平凡的代码库，始终使用 `--focus` 进行 `call-graph`。对于 `data-flow`，省略焦点会自动定位前 10 个复杂度热点。

**语言：** 对于多语言或不熟悉的存储库，优先使用 `--language auto`。仅在知道目标是单语言或需要排除无关组件时使用显式语言。

---

## 支持文档

- **[references/diagram-types.md](references/diagram-types.md)** -
  每种图表类型的详细文档和 Mermaid 示例
- **[references/mermaid-syntax.md](references/mermaid-syntax.md)** -
  ID 清理、转义、样式定义和常见陷阱
