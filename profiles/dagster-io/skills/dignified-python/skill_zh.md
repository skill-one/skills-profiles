# 高雅的 Python

针对编写干净、可维护、现代 Python 代码（版本 3.10-3.13）的 Python 风格指导。

## 何时使用此技能

在用户询问以下内容时自动调用：

- "让这个代码更 Pythonic" / "这个代码是否良好"
- "类型提示" / "类型注解" / "typing"
- "LBYL vs EAFP" / "异常处理"
- "pathlib vs os.path" / "路径操作"
- "CLI 模式" / "click 使用"
- "代码审查" / "改进这段代码"
- 任何与 Python 代码质量或标准相关的问题

**注意**：此技能是 **通用 Python 风格指导**，而非 Dagster 特定的。它捕获了一种明确的、倾向于 LBYL 的约定集；项目约定可以在需要时覆盖它。

## 何时使用此技能与其他技能的区别

| 用户需求                    | 使用此技能              | 替代技能         |
| ---------------------------- | --------------------------- | ------------------------- |
| "让这个代码更 Pythonic"         | ✅ 是 - Python 标准   |                           |
| "这个代码是否良好"        | ✅ 是 - 代码质量       |                           |
| "类型提示"                 | ✅ 是 - 类型指导    |                           |
| "LBYL vs EAFP"               | ✅ 是 - 异常模式      |                           |
| "pathlib vs os.path"         | ✅ 是 - 路径处理      |                           |
| "dagster 的最佳实践"         | ❌ 否                       | `/dagster-best-practices` |
| "实现 X 管道"       | ❌ 否                       | `/dg` 用于实现  |
| "使用哪个集成"       | ❌ 否                       | `/dagster-expert`         |
| "CLI 参数解析"       | ✅ 是 - CLI 模式       |                           |

## 核心知识（始终加载）

@dignified-python-core.md

## 版本检测

**通过以下顺序检查来识别项目的最低 Python 版本**：

1. `pyproject.toml` - 查找 `requires-python` 字段（例如，`requires-python = ">=3.12"`)
2. `setup.py` 或 `setup.cfg` - 查找 `python_requires`
3. `.python-version` 文件 - 包含版本信息，如 `3.12` 或 `3.12.0`
4. 如果未找到版本说明符，则默认为 Python 3.12

**一旦识别，加载相应的版本特定文件**：

- Python 3.10: 加载 `versions/python-3.10.md`
- Python 3.11: 加载 `versions/python-3.11.md`
- Python 3.12: 加载 `versions/python-3.12.md`
- Python 3.13: 加载 `versions/python-3.13.md`

## 条件加载（根据任务模式加载）

核心文件涵盖了 80%+ 的 Python 代码模式。仅在检测到特定模式时加载这些附加文件：

模式检测示例：

- 如果任务提到 "click" 或 "CLI" -> 加载 `cli-patterns.md`
- 如果任务提到 "subprocess" -> 加载 `subprocess.md`

## 参考文档结构

此技能的参考材料按主题组织：

### 核心参考

- **`dignified-python-core.md`** - 基本标准（始终加载）
- **`cli-patterns.md`** - 命令行界面模式（click, argparse）

### 版本特定参考 (`versions/`)

- **`python-3.10.md`** - Python 3.10+ 中可用的功能
- **`python-3.11.md`** - Python 3.11+ 中可用的功能
- **`python-3.12.md`** - Python 3.12+ 中可用的功能
- **`python-3.13.md`** - Python 3.13+ 中可用的功能

### 高级主题 (`references/advanced/`)

- **`exception-handling.md`** - LBYL 模式、错误边界
- **`interfaces.md`** - ABC 和 Protocol 模式
- **`typing-advanced.md`** - 高级类型模式
- **`api-design.md`** - API 设计原则

## 何时阅读每个参考文档

### `references/advanced/exception-handling.md`

**在以下情况下阅读**：

- 编写 try/except 块
- 包装可能引发异常的第三方 API
- 看到 `from e` 或 `from None`
- 不确定是否存在 LBYL 替代方案

### `references/advanced/interfaces.md`

**在以下情况下阅读**：

- 创建 ABC 或 Protocol 类
- 编写 @abstractmethod 装饰器
- 设计网关层接口
- 在 ABC 和 Protocol 之间进行选择

### `references/advanced/typing-advanced.md`

**在以下情况下阅读**：

- 使用 typing.cast()
- 创建 Literal 类型别名
- 在条件块中缩小类型

### `references/module-design.md`

**在以下情况下阅读**：

- 创建新的 Python 模块
- 添加模块级代码（超出简单常量）
- 在模块级别使用 @cache 装饰器
- 看到 Path() 或模块级计算
- 考虑内联导入

### `references/advanced/api-design.md`

**在以下情况下阅读**：

- 为函数添加默认参数值
- 定义具有 5 个或更多参数的函数
- 使用 ThreadPoolExecutor.submit()
- 审查函数签名

### `references/checklists.md`

**在以下情况下阅读**：

- 提交 Python 代码前的最终审查
- 不确定是否遵循了所有规则
- 需要快速查找要求

## 如何使用此技能

1. **核心知识** 自动加载（默认值、pathlib、导入、反模式）
2. **版本检测** 只发生一次 - 识别最低 Python 版本并加载相应的版本文件
3. **参考文档** 根据上述触发器按需加载
4. **附加模式** 可能需要额外加载（CLI 模式、subprocess）
5. **每个文件都是自包含的**，为其领域提供完整的指导
