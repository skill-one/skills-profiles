# 现代Python

基于 [trailofbits/cookiecutter-python](https://github.com/trailofbits/cookiecutter-python) 的现代Python工具和最佳实践指南。

## 何时使用此技能

- 创建新的Python项目或包
- 设置 `pyproject.toml` 配置
- 配置开发工具（代码检查、格式化、测试）
- 编写具有外部依赖的Python脚本
- 从旧工具迁移（当用户要求时）

## 何时**不**使用此技能

- **用户希望保留旧工具**: 如果明确要求，请尊重现有的工作流程
- **需要Python < 3.11**: 这些工具针对现代Python
- **非Python项目**: 混合代码库中Python不是主要语言

## 应避免的反模式

| 避免 | 使用替代方案 |
|-------|-------------|
| `[tool.ty]` python-version | `[tool.ty.environment]` python-version |
| `uv pip install` | `uv add` 和 `uv sync` |
| 手动编辑pyproject.toml添加依赖 | `uv add <pkg>` / `uv remove <pkg>` |
| `hatchling` 构建后端 | `uv_build`（更简单，对大多数情况足够） |
| Poetry | uv（更快、更简单、更好的生态系统集成） |
| requirements.txt | 脚本使用PEP 723，项目使用pyproject.toml |
| mypy / pyright | ty（更快，来自Astral团队） |
| `[project.optional-dependencies]` 用于开发工具 | `[dependency-groups]` (PEP 735) |
| 手动激活虚拟环境 (`source .venv/bin/activate`) | `uv run <cmd>` |
| pre-commit | prek（更快，无需Python运行时） |

**关键原则:**
- 始终使用 `uv add` 和 `uv remove` 来管理依赖
- 永远不要手动激活或管理虚拟环境——所有命令都使用 `uv run`
- 使用 `[dependency-groups]` 而不是 `[project.optional-dependencies]` 来管理开发/测试/文档依赖

## 决策树

```
你在做什么？
│
├─ 单文件带依赖的脚本？
│   └─ 使用PEP 723内联元数据 (./references/pep723-scripts.md)
│
├─ 新的多文件项目（非分发）？
│   └─ 最小化uv设置（见快速入门部分）
│
├─ 新的可重用包/库？
│   └─ 完整项目设置（见完整设置部分）
│
└─ 迁移现有项目？
    └─ 见迁移指南部分
```

## 工具概述

| 工具 | 目的 | 替代 |
|------|---------|----------|
| **uv** | 包/依赖管理 | pip, virtualenv, pip-tools, pipx, pyenv |
| **ruff** | 代码检查和格式化 | flake8, black, isort, pyupgrade, pydocstyle |
| **ty** | 类型检查 | mypy, pyright（更快替代方案） |
| **pytest** | 带覆盖率的测试 | unittest |
| **prek** | 预提交钩子 ([setup](./references/prek.md)) | pre-commit（更快，Rust原生） |

### 安全工具

| 工具 | 目的 | 运行时机 |
|------|---------|--------------|
| **shellcheck** | Shell脚本代码检查 | pre-commit |
| **detect-secrets** | 密钥检测 | pre-commit |
| **actionlint** | 工作流语法验证 | pre-commit, CI |
| **zizmor** | 工作流安全审计 | pre-commit, CI |
| **pip-audit** | 依赖漏洞扫描 | CI, 手动 |
| **Dependabot** | 自动化依赖更新 | 定时任务 |

见 [security-setup.md](./references/security-setup.md) 获取配置和使用说明。

## 快速入门：最小化项目

对于不打算分发的简单多文件项目：

```bash
# 使用uv创建项目
uv init myproject
cd myproject

# 添加依赖
uv add requests rich

# 添加开发依赖
uv add --group dev pytest ruff ty

# 运行代码
uv run python src/myproject/main.py

# 运行工具
uv run pytest
uv run ruff check .
```

## 完整项目设置
如果从头开始，询问用户是否希望使用 Trail of Bits cookiecutter 模板来启动一个带有预配置工具的完整项目。

```bash
uvx cookiecutter gh:trailofbits/cookiecutter-python
```

### 1. 创建项目结构

```bash
uv init --package myproject
cd myproject
```

这会创建：
```
myproject/
├── pyproject.toml
├── README.md
├── src/
│   └── myproject/
│       └── __init__.py
└── .python-version
```

### 2. 配置pyproject.toml

见 [pyproject.md](./references/pyproject.md) 获取完整配置参考。

关键部分：
```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}, {include-group = "audit"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov"]
audit = ["pip-audit"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "COM812", "ISC001"]

[tool.pytest]
addopts = ["--cov=myproject", "--cov-fail-under=80"]

[tool.ty.terminal]
error-on-warning = true

[tool.ty.environment]
python-version = "3.11"

[tool.ty.rules]
# 新项目从第一天就严格
possibly-unresolved-reference = "error"
unused-ignore-comment = "warn"
```

### 3. 安装依赖

```bash
# 安装所有依赖组
uv sync --all-groups

# 或安装特定组
uv sync --group dev
```

### 4. 添加Makefile

```makefile
.PHONY: dev lint format test build

dev:
	uv sync --all-groups

lint:
	uv run ruff format --check && uv run ruff check && uv run ty check src/

format:
	uv run ruff format .

test:
	uv run pytest

build:
	uv build
```

## 迁移指南

当用户要求从旧工具迁移时：

### 从 requirements.txt + pip

首先确定代码的性质：

**对于独立脚本**: 转换为PEP 723内联元数据（见 [pep723-scripts.md](./references/pep723-scripts.md)）

**对于项目**:
```bash
# 在现有项目中初始化uv
uv init --bare

# 使用uv添加依赖（不要通过编辑pyproject.toml）
uv add requests rich  # 添加每个包

# 或从requirements.txt导入（添加前审查每个包）
# 注意：复杂的版本规范可能需要手动处理
grep -v '^#' requirements.txt | grep -v '^-' | grep -v '^\s*$' | while read -r pkg; do
    uv add "$pkg" || echo "Failed to add: $pkg"
done

uv sync
```

然后：
1. 删除 `requirements.txt`, `requirements-dev.txt`
2. 删除虚拟环境（`venv/`, `.venv/`）
3. 将 `uv.lock` 添加到版本控制

### 从 setup.py / setup.cfg

1. 运行 `uv init --bare` 创建pyproject.toml
2. 使用 `uv add` 添加 `install_requires` 中的每个依赖
3. 使用 `uv add --group dev` 添加开发依赖
4. 复制非依赖元数据（名称、版本、描述等）到 `[project]`
5. 删除 `setup.py`, `setup.cfg`, `MANIFEST.in`

### 从 flake8 + black + isort

1. 通过 `uv remove` 删除 flake8, black, isort
2. 删除 `.flake8`, `pyproject.toml [tool.black]`, `[tool.isort]` 配置
3. 添加ruff: `uv add --group dev ruff`
4. 添加ruff配置（见 [ruff-config.md](./references/ruff-config.md)）
5. 运行 `uv run ruff check --fix .` 应用修复
6. 运行 `uv run ruff format .` 格式化

### 从 mypy / pyright

1. 通过 `uv remove` 删除 mypy/pyright
2. 删除 `mypy.ini`, `pyrightconfig.json`, 或 `[tool.mypy]`/`[tool.pyright]` 部分
3. 添加ty: `uv add --group dev ty`
4. 运行 `uv run ty check src/`

## 快速参考：uv命令

| 命令 | 描述 |
|---------|-------------|
| `uv init` | 创建新项目 |
| `uv init --package` | 创建可分发包 |
| `uv add <pkg>` | 添加依赖 |
| `uv add --group dev <pkg>` | 添加到依赖组 |
| `uv remove <pkg>` | 删除依赖 |
| `uv sync` | 安装依赖 |
| `uv sync --all-groups` | 安装所有依赖组 |
| `uv run <cmd>` | 在虚拟环境中运行命令 |
| `uv run --with <pkg> <cmd>` | 带临时依赖运行 |
| `uv build` | 构建包 |
| `uv publish` | 发布到PyPI |

### 带有 `--with` 的临时依赖

使用 `uv run --with` 处理需要包但不在项目中的一次性命令：

```bash
# 带临时包运行Python
uv run --with requests python -c "import requests; print(requests.get('https://httpbin.org/ip').json())"

# 带临时依赖运行模块
uv run --with rich python -m rich.progress

# 多个包
uv run --with requests --with rich python script.py

# 与项目依赖结合（添加到现有虚拟环境）
uv run --with httpx pytest  # 项目依赖 + httpx
```

**何时使用 `--with` vs `uv add`:**
- `uv add`: 包是项目依赖（进入pyproject.toml/uv.lock）
- `--with`: 一次性使用、测试或项目上下文外的脚本

见 [uv-commands.md](./references/uv-commands.md) 获取完整参考。

## 快速参考：依赖组

```toml
[dependency-groups]
dev = ["ruff", "ty"]
test = ["pytest", "pytest-cov", "hypothesis"]
docs = ["sphinx", "myst-parser"]
```

安装：`uv sync --group dev --group test`

## 最佳实践检查清单

- [ ] 使用 `src/` 布局作为包
- [ ] 设置 `requires-python = ">=3.11"`
- [ ] 使用ruff配置 `select = ["ALL"]` 和显式忽略
- [ ] 使用ty进行类型检查
- [ ] 强制测试覆盖率最低（80%+）
- [ ] 使用依赖组而不是 extras 来管理开发工具
- [ ] 将 `uv.lock` 添加到版本控制
- [ ] 使用PEP 723处理独立脚本

## 下一步阅读

- [migration-checklist.md](./references/migration-checklist.md) - 迁移清理步骤
- [pyproject.md](./references/pyproject.md) - 完整pyproject.toml参考
- [uv-commands.md](./references/uv-commands.md) - uv命令参考
- [ruff-config.md](./references/ruff-config.md) - ruff代码检查/格式化配置
- [testing.md](./references/testing.md) - pytest和覆盖率设置
- [pep723-scripts.md](./references/pep723-scripts.md) - PEP 723内联脚本元数据
- [prek.md](./references/prek.md) - 使用prek的快速预提交钩子
- [security-setup.md](./references/security-setup.md) - 安全钩子和依赖扫描
- [dependabot.md](./references/dependabot.md) - 自动化依赖更新
