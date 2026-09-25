# 技能：Jupyter Notebook 编写

以 DevRel 工作流的形式编写 Milvus 应用级别的 Jupyter Notebook 示例。采用 Markdown 优先的方法——AI 编辑 `.md` 文件，然后通过 `jupyter-switch` 转换为 `.ipynb`。

> **前提条件**：Python >= 3.10, uv (`uvx` 命令可用)

---

## 使用场景

用户想要创建或编辑 Jupyter Notebook 示例，通常在应用程序上下文中（如 RAG、语义搜索、混合搜索等）展示 Milvus 的使用方法。

---

## 核心工作流：Markdown 优先编辑

Jupyter `.ipynb` 文件包含复杂的 JSON 数据，其中包含元数据、输出和执行次数——对 AI 来说直接编辑非常困难。相反：

1. **编写/编辑 `.md` 文件**——AI 使用干净的 Markdown
2. **转换为 `.ipynb`**——使用 `jupyter-switch` 创建可运行的 Notebook
3. **保持两个文件同步**——`.md` 是编辑的源文件

### 格式约定

在 `.md` 文件中：
- **Python 代码块** (` ```python ... ``` `) 变为 Notebook 中的 **代码单元**
- **其他内容** 变为 **Markdown 单元**
- 单元输出不会保留在 `.md` 中（运行 Notebook 时才会生成）

### 转换命令

```bash
# Markdown -> Jupyter Notebook
uvx jupyter-switch example.md
# 生成 example.ipynb

# Jupyter Notebook -> Markdown
uvx jupyter-switch example.ipynb
# 生成 example.md
```

- 原始输入文件不会被修改或删除
- 如果输出文件已存在，会自动创建 `.bak` 备份

---

## 步骤详解

### 创建新 Notebook

1. 创建 `example.md` 文件并添加内容（见下方结构）
2. 转换：`uvx jupyter-switch example.md`
3. 现在 `example.md` 和 `example.ipynb` 都存在

### 编辑现有 Notebook

1. 如果只有 `.ipynb` 存在，先转换：`uvx jupyter-switch example.ipynb`
2. 编辑 `.md` 文件
3. 转换回：`uvx jupyter-switch example.md`

### 测试 / 运行

#### 1. 确定 Jupyter 执行环境

在运行任何 Notebook 之前，你必须确定要使用哪个 Python 环境。系统默认的 `jupyter execute` 可能没有安装所需的包。

**步骤 A — 检测可用环境。**

```bash
# 发现 conda/mamba 环境
conda env list 2>/dev/null || mamba env list 2>/dev/null

# 发现注册的 Jupyter 核心
jupyter kernelspec list 2>/dev/null

# 检查系统默认 Python
which python3 2>/dev/null && python3 --version 2>/dev/null

# 检查工作目录中的本地虚拟环境
ls -d .venv/ venv/ 2>/dev/null

# 检查 uv 管理的项目（pyproject.toml + .venv）
test -f pyproject.toml && test -d .venv && echo "uv/pip 项目 venv 检测到"
```

**步骤 B — 询问用户要使用哪个环境。** 提供一个编号列表供选择。包括所有检测到的环境：

1. **系统默认**——直接运行 `jupyter execute`，无需 `--kernel_name`
2. **每个检测到的 conda/mamba 环境**——显示名称和路径
3. **每个注册的 Jupyter 核心**——显示核心名称
4. **本地 venv**（如果工作目录中找到 `.venv/` 或 `venv/`）——该 venv 中的 Python
5. **自定义**——让用户输入 Python 路径或环境名称

> **关于 uv 项目的说明**：如果工作目录有 `pyproject.toml` + `.venv/`（一个 uv 管理的项目），本地 venv 选项涵盖了这种情况。如果 jupyter 是项目依赖，用户也可以直接运行 `uv run jupyter execute example.ipynb`。

示例提示：

```
我应该使用哪个 Python 环境来运行这个 Notebook？

1. 系统默认（直接运行 jupyter execute）
2. conda: myenv (/path/to/envs/myenv)
3. Jupyter 核心: some-kernel
4. 本地 venv (.venv/)
5. 自定义——输入路径或环境名称
```

**步骤 C — 应用选择的环境：**

| 场景 | 操作 |
|------|------|
| 已注册为 Jupyter 核心的环境 | 使用 `jupyter execute --kernel_name=<name>` |
| 尚未注册为核心的 Conda 环境 | 首先注册：`<env-python> -m ipykernel install --user --name <name> --display-name "<label>"`，然后使用 `--kernel_name=<name>` |
| 自定义 Python 路径 | 同上——先注册为核心，然后使用 `--kernel_name` |

#### 2. 准备 Notebook 以执行

在运行之前，请在 `.md` 文件中注释掉“仅设置”的单元——这些单元是针对首次使用用户的，但在自动化测试环境中不应运行。具体：

- **`pip install` 单元**——依赖项应该已经安装在选择的 Jupyter 环境中。如果缺少任何包或需要升级，请在目标环境中外部安装它们（使用 `--upgrade`），而不是在 Notebook 内部。
- **API 密钥 / 凭证占位符单元**——例如 `os.environ["OPENAI_API_KEY"] = "sk-***********"`。相反，请在运行前外部设置环境变量（在 shell 中导出，或在 `jupyter execute` 之前通过代码注入）。
- **模拟 / 仅演示单元**——任何仅用于说明的单元，在真实运行中会失败或干扰。

要注释掉一个单元，请将其内容包裹在块注释中，这样单元仍然会执行（产生空输出）但不会执行任何操作：

```python
# # pip install --upgrade langchain pymilvus
# import os
# os.environ["OPENAI_API_KEY"] = "sk-***********"
```

这保持了 Notebook 结构的完整性（单元数量、顺序），同时防止与外部 Jupyter 环境冲突。

**对于环境变量**：要么在运行 `jupyter execute` 之前在 shell 中导出它们，要么在命令前添加它们：

```bash
OPENAI_API_KEY="sk-real-key" jupyter execute --kernel_name=<name> example.ipynb
```

#### 3. 转换并运行

1. 如果需要，将 `.md` 转换为 `.ipynb`
2. 在目标环境中外部安装任何缺失的依赖项：`<env-python> -m pip install --upgrade <packages>`
3. 运行：`jupyter execute --kernel_name=<name> example.ipynb`（如果使用系统默认，则省略 `--kernel_name`）
4. 如果发现错误，请在 `.md` 文件中修复，如有必要注释掉设置单元以进行调试，然后重新转换

---

## Notebook 结构模板

典型的 Milvus 示例 Notebook 遵循以下结构：

```markdown
# 标题

简要描述这个 Notebook 演示的内容。

## 前提条件

安装依赖项：

` ``python
!pip install pymilvus some-other-package
` ``

## 设置

导入和配置：

` ``python
from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530")
` ``

## 准备数据

加载或生成示例数据：

` ``python
# 数据准备代码
` ``

## 创建集合并插入数据

` ``python
# 集合创建和数据插入
` ``

## 查询 / 搜索

` ``python
# 搜索或查询示例
` ``

## 清理

` ``python
client.drop_collection("example_collection")
` ``
```

---

## 参考文档

此技能包含 `references/` 下两个参考文档。**在任务涉及其主题时阅读它们。**

| 参考 | 阅读时机 | 文件 |
|------|---------|------|
| **Bootcamp 格式** | 编写 Milvus 集成教程（徽章、文档结构、章节格式、示例布局） | `references/bootcamp-format.md` |
| **Milvus 代码风格** | 编写 pymilvus 代码（集合创建、MilvusClient 连接参数、模式模式、最佳实践） | `references/milvus-code-style.md` |

### Bootcamp 格式 (`references/bootcamp-format.md`)

在编写 **Bootcamp 仓库的 Milvus 集成教程** 时阅读此文档。它涵盖：
- 徽章格式（顶部 Colab + GitHub 徽章）
- 文档结构：标题 -> 前提条件 -> 主要内容 -> 结论
- 依赖项安装格式，附带 Google Colab 重启提示
- API 密钥占位符约定（`"sk-***********"`）
- 每个代码块之前应有简短的文本介绍

### Milvus 代码风格 (`references/milvus-code-style.md`)

在 Notebook 涉及 **pymilvus 代码** 时阅读此文档。关键规则：
- **始终使用 `MilvusClient` API**——绝不要使用遗留的 ORM 层（`connections.connect()`、`Collection()`、`FieldSchema()` 等）
- 始终显式定义模式（`create_schema` + `add_field`）——不要在不定义模式的情况下使用快捷方式 `create_collection(dimension=...)`
- 在创建集合之前添加 `has_collection` 检查
- 在 `create_collection()` 中添加注释 `consistency_level="Strong"` 行
- 无需调用 `load_collection()`——集合在创建时自动加载
- 第一个 MilvusClient 连接必须包含解释 `uri` 选项的块引用（Milvus Lite / Docker / Zilliz Cloud）

---

## 重要提示

- **始终编辑 `.md` 文件**，不要直接编辑 `.ipynb`。`.md` 更容易让 AI 读取和写入。
- **保留两个文件**——`.md` 用于编辑，`.ipynb` 用于运行/共享。
- 编辑 `.md` 后，始终重新运行 `uvx jupyter-switch example.md` 以同步 `.ipynb`。
