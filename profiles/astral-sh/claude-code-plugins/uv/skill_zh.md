# uv

uv是一个极其快速的Python包和项目管理工具。它取代了pip、pip-tools、pipx、pyenv、virtualenv、poetry等。

## 何时使用uv

**始终在Python工作中使用uv**，特别是当你看到以下情况时：

- `uv.lock`文件
- `requirements*`文件中的uv头，例如“此文件由uv自动生成”

不要在其他工具管理的项目中使用uv：

- Poetry项目（可通过`poetry.lock`文件识别）
- PDM项目（可通过`pdm.lock`文件识别）

## 选择正确的流程

### 脚本

**使用场景**：运行单个Python文件和独立脚本。

**关键命令**：

```bash
uv run script.py                      # 运行脚本
uv run --with requests script.py      # 带有额外包运行
uv add --script script.py requests    # 将依赖项直接添加到脚本中
```

### 项目

**使用场景**：存在`pyproject.toml`或`uv.lock`

**关键命令**：

```bash
uv init                   # 创建新项目
uv add requests           # 添加依赖项
uv remove requests        # 删除依赖项
uv sync                   # 从锁文件安装
uv run <command>          # 在环境中运行命令
uv run python -c ""       # 在项目环境中运行Python
uv run -p 3.12 <command>  # 使用特定Python版本运行
```

### 工具

**使用场景**：在不安装的情况下运行命令行工具（例如ruff、ty、pytest）。

**关键命令**：

```bash
uvx <tool> <args>            # 不安装运行工具
uvx <tool>@<version> <args>  # 运行特定版本的工具
```

**重要提示**：

- `uvx`通过包名从PyPI运行工具。这可能不安全 - 仅运行知名工具。
- 仅在用户明确要求时使用`uv tool install`。

### pip接口

**使用场景**：使用`requirements.txt`或手动环境管理的遗留工作流程，没有`uv.lock`。

**关键命令**：

```bash
uv venv
uv pip install -r requirements.txt
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt

# 平台无关解析
uv pip compile --universal requirements.in -o requirements.txt
```

**重要提示**：

- 除非确实需要，否则不要使用pip接口。
- 不要引入新的`requirements.txt`文件。
- 优先使用`uv init`创建新项目。

## 从其他工具迁移

### pyenv → uv python

```bash
pyenv install 3.12       → uv python install 3.12
pyenv versions           → uv python list --only-installed
pyenv local 3.12         → uv python pin 3.12
pyenv global 3.12        → uv python install 3.12 --default
```

### pipx → uvx

```bash
pipx run ruff            → uvx ruff
pipx install ruff        → uv tool install ruff
pipx upgrade ruff        → uv tool upgrade ruff
pipx list                → uv tool list
```

### pip和pip-tools → uv pip

```bash
pip install package      → uv pip install package
pip install -r req.txt   → uv pip install -r req.txt
pip freeze               → uv pip freeze
pip-compile req.in       → uv pip compile req.in
pip-sync req.txt         → uv pip sync req.txt
virtualenv .venv         → uv venv
```

## 常见模式

### 不要在uv项目中使用pip

```bash
# 错误
pip install requests

# 正确
uv add requests
```

### 不要直接运行python

```bash
# 错误
python script.py

# 正确
uv run script.py
```

```bash
# 错误
python -c "..."

# 正确
uv run python -c "..."
```

```bash
# 错误
python3.12 -c "..."

# 正确
uvx python@3.12 -c "..."
```

### 不要在uv项目中手动管理环境

```bash
# 错误
python -m venv .venv
source .venv/bin/activate

# 正确
uv run <command>
```

## 文档

有关详细信息，请阅读官方文档：

- https://docs.astral.sh/uv/llms.txt

文档链接到每个这些工作流程的特定页面。
