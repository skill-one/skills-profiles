# Earth2Studio 安装技巧

## 绝不自动安装软件包

你**绝对不能**代表用户安装、升级或修改软件包。提供确切的命令；由用户自行执行。没有例外。

**禁止操作：** 运行 `pip install`、`uv pip install`、`uv add`、`uv sync`、`conda install`、`apt install` 或任何软件包管理器。

**替代方法：** 提供确切的命令并要求用户自行执行。解释为什么需要该软件包。

当需要软件包时：

1. 识别软件包
2. 提供确切的命令
3. 解释为什么需要它
4. **等待用户确认已执行**

即使用户说“直接安装吧”，也要提供命令并要求他们自行执行。

## 目的

帮助用户根据其使用场景正确安装 Earth2Studio 及其可选模型依赖项。此技巧处理软件包安装、可选额外组件选择、环境变量配置和安装验证。

## 前置条件

- Python 3.10+（推荐 3.13）
- 具备 CUDA 功能的 GPU 及兼容驱动程序（用于 GPU 额外组件）
- uv（推荐）或 pip 软件包管理器
- 互联网访问（从 PyPI 和 GitHub 安装软件包）

你正在帮助用户安装 Earth2Studio 及其可选模型依赖项。你的唯一任务是确保根据他们的使用场景正确安装软件包——不要编写推理代码，不要编排工作流。

## 核心原则：文档是权威来源

Earth2Studio 安装命令、版本标签和额外组件名称在不同版本之间会发生变化。**在执行或推荐任何安装命令之前，获取实时安装文档：**

```text
https://nvidia.github.io/earth2studio/userguide/about/install.html
```

解析页面以获取当前版本标签、可用额外组件以及任何特殊构建说明。以下工作流是结构化指导——具体命令来自实时页面。

## 说明

### 第 1 步。获取实时文档

使用 WebFetch 对上述安装 URL 进行操作。提取：

- 当前发布版本标签（例如 `@0.14.0`）
- 按类别列出的可用可选额外组件
- 已知的构建问题（例如 `--no-build-isolation` 用于 pip，手动预安装）

将此数据保存在工作内存中，供后续步骤使用。

### 第 2 步。了解用户的环境

提问（最多 3 个问题，跳过用户已回答的内容）：

1. **软件包管理器**—— uv（推荐）还是 pip？如果不确定，推荐 uv 并链接 <https://docs.astral.sh/uv/getting-started/installation/>
2. **项目上下文**—— 新项目还是添加到现有项目？
3. **Python 版本**—— 推荐文档中的版本（当前为 3.13）

### 第 3 步。基础安装

根据他们的回答从实时文档提供命令：

- **uv** 使用 git 源（不是 PyPI）来处理基于 URL 的传递依赖关系
- **pip** 从 PyPI 安装，但某些额外组件需要手动预安装步骤

用户运行安装后，验证：

```python
import earth2studio
earth2studio.__version__
```

### 第 4 步。选择模型和额外组件

按使用场景组织呈现可用的额外组件。询问用户计划做什么——不要未经提示就抛出所有选项。文档中的类别：

| 类别         | 示例额外组件          |
|--------------|----------------------|
| 预测（预测） | aifs、aurora、graphcast、pangu、sfno、stormcast、... |
| 诊断（后处理） | corrdiff、climatenet、precip-afno、... |
| 数据同化（Beta） | da-healda、da-interp、da-stormcast |
| 子模块       | data、perturbation、statistics |

确切列表来自实时文档——引用那些，而不是这个表格。

提问：

1. 计划使用哪些模型？
2. 是否需要子模块额外组件（数据源、扰动方法、统计）？
3. 还是安装所有内容？（uv 仅限：`--extra all`）

### 第 5 步。安装选定的额外组件

根据他们的选择从实时文档提供确切的命令。关键警告：

- **缓慢构建**：flash-attention（AIFS 变体）、natten（Atlas、StormScope）、torch-harmonics CUDA 扩展（FCN3、SFNO）——可能需要 10-30+ 分钟
- **pip 特定手动步骤**：某些模型需要 `--no-build-isolation` 或预安装 earth2grid、torch-harmonics 或 makani
- **数据同化模型**：需要 CuPy + cuDF（CUDA 12）

### 第 6 步。配置（提供，不要强制）

提及用户可能希望设置的環境变量——仅在相关时（例如有限磁盘、共享文件系统、CI 环境）：

| 变量               | 目的               |
|-------------------|--------------------|
| `EARTH2STUDIO_CACHE` | 通用缓存目录       |
| `EARTH2STUDIO_DATA_CACHE` | 数据源缓存（覆盖通用） |
| `EARTH2STUDIO_MODEL_CACHE` | 模型检查点缓存（覆盖通用） |
| `EARTH2STUDIO_PACKAGE_TIMEOUT` | 模型下载的最大秒数 |

## 故障排除

如果安装失败，请将用户指向：

- <https://nvidia.github.io/earth2studio/userguide/support/troubleshooting.html>
- <https://nvidia.github.io/earth2studio/userguide/support/faq.html>

常见问题：

- **PyTorch/CUDA 不匹配**：首先验证 `torch.cuda.is_available()`
- **flash-attention 构建失败**：CUDA 工具包版本必须与 PyTorch CUDA 匹配
- **ONNX Runtime GPU**：可能需要针对其 CUDA 的特定版本安装
- **ecCodes 缺失**：用于 GRIB 数据处理；通过 `sudo apt-get install libeccodes-dev`（Debian/Ubuntu）或 `conda install -c conda-forge eccodes` 安装
- **Python.h: No such file or directory**：缺少 Python 开发头文件；通过 `sudo apt-get install python3-dev` 安装

## 限制

- 无法帮助处理与缺失依赖无关的运行时错误
- 不涵盖模型检查点下载（那些在首次推理时发生）
- 超出范围的数据源设置（超出 `data` 额外组件）
- 无法编写推理或训练代码，或编排 Earth2Studio 工作流

## 责任范围和超出范围

**负责：** 软件包安装、可选额外组件选择、环境变量配置、安装验证。

**不负责：** 编写推理或训练代码、编排 Earth2Studio 工作流、超出 `data` 额外组件的数据源设置、模型检查点下载（那些在运行时发生）、处理与缺失依赖无关的运行时错误。
