# Python 打包

使用现代打包工具、pyproject.toml 和发布到 PyPI 的全面指南，用于创建、构建和分发 Python 包。

## 何时使用这项技能

- 创建用于分发的 Python 库
- 构建具有入口点的命令行工具
- 发布包到 PyPI 或私有仓库
- 设置 Python 项目结构
- 创建带依赖项的安装包
- 构建轮子（wheels）和源分发（source distributions）
- 版本控制和发布 Python 包
- 创建命名空间包（namespace packages）
- 实现包元数据和分类器（classifiers）

## 核心概念

### 1. 包结构

- **源布局**：`src/package_name/`（推荐）
- **扁平布局**：`package_name/`（更简单但灵活性较低）
- **包元数据**：pyproject.toml、setup.py 或 setup.cfg
- **分发格式**：轮子（.whl）和源分发（.tar.gz）

### 2. 现代打包标准

- **PEP 517/518**：构建系统要求
- **PEP 621**：pyproject.toml 中的元数据
- **PEP 660**：可编辑安装
- **pyproject.toml**：单一配置源

### 3. 构建后端

- **setuptools**：传统、广泛使用
- **hatchling**：现代、有观点（opinionated）
- **flit**：轻量级、适用于纯 Python
- **poetry**：依赖管理 + 打包

### 4. 分发

- **PyPI**：Python 包索引（公共）
- **TestPyPI**：生产前测试
- **私有仓库**：JFrog、AWS CodeArtifact 等

## 快速入门

### 最小化包结构

```
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── module.py
└── tests/
    └── test_module.py
```

### 最小化 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
description = "A short description"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
]
```

## 包结构模式

### 模式 1：源布局（推荐）

```
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── utils.py
│       └── py.typed          # 用于类型提示
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
└── docs/
    └── index.md
```

**优点：**

- 防止意外从源代码导入
- 更干净的测试导入
- 更好的隔离

**源布局的 pyproject.toml：**

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### 模式 2：扁平布局

```
my-package/
├── pyproject.toml
├── README.md
├── my_package/
│   ├── __init__.py
│   └── module.py
└── tests/
    └── test_module.py
```

**更简单但：**

- 可以在不安装的情况下导入包
- 对于库来说不够专业

### 模式 3：多包项目

```
project/
├── pyproject.toml
├── packages/
│   ├── package-a/
│   │   └── src/
│   │       └── package_a/
│   └── package-b/
│       └── src/
│           └── package_b/
└── tests/
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。
