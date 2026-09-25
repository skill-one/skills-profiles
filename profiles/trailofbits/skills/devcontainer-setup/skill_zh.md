# Devcontainer 配置技能

创建一个预配置的 devcontainer，包含 Claude Code 和特定语言的工具。

## 使用场景

- 用户请求"设置 devcontainer"或"添加 devcontainer 支持"
- 用户需要一个沙箱化的 Claude Code 开发环境
- 用户需要隔离的开发环境，并具有持久配置

## 不适用场景

- 用户已经有一个 devcontainer 配置，只需要修改
- 用户询问关于 Docker 或容器的通用问题
- 用户想要部署生产容器（这仅用于开发）

## 工作流程

```mermaid
flowchart TB
    start([用户请求 devcontainer])
    recon[1. 项目侦察]
    detect[2. 检测语言]
    generate[3. 生成配置]
    write[4. 将文件写入 .devcontainer/]
    done([完成])

    start --> recon
    recon --> detect
    detect --> generate
    generate --> write
    write --> done
```

## 第一阶段：项目侦察

### 推断项目名称

按顺序检查（使用第一个匹配项）：

1. `package.json` → `name` 字段
2. `pyproject.toml` → `project.name`
3. `Cargo.toml` → `package.name`
4. `go.mod` → 模块路径（`/` 后的最后一段）
5. 目录名作为后备

转换为 slug：小写，用连字符替换空格/下划线。

### 检测语言栈

| 语言 | 检测文件 |
|------|----------|
| Python | `pyproject.toml`, `*.py` |
| Node/TypeScript | `package.json`, `tsconfig.json` |
| Rust | `Cargo.toml` |
| Go | `go.mod`, `go.sum` |

### 多语言项目

如果检测到多种语言，按以下优先级顺序配置所有语言：

1. **Python** - 主要语言，使用 Dockerfile 安装 uv + Python
2. **Node/TypeScript** - 使用 devcontainer 功能
3. **Rust** - 使用 devcontainer 功能
4. **Go** - 使用 devcontainer 功能

对于多语言 `postCreateCommand`，链式执行所有设置命令：
```
uv run /opt/post_install.py && uv sync && npm ci
```

所有检测到的语言的扩展和设置应合并到配置中。

## 第二阶段：生成配置

从 `resources/` 目录的基模板开始。替换：

- `{{PROJECT_NAME}}` → 人类可读的名称（例如，"我的项目"）
- `{{PROJECT_SLUG}}` → 用于卷的 slug（例如，"my-project"）

然后应用以下语言特定修改。

## 基模板功能

基模板包含：

- **Claude Code** 带有市场插件（anthropics/skills, trailofbits/skills, trailofbits/skills-curated）
- **沙箱** 通过 bubblewrap 和 socat
- **Python 3.13** 通过 uv（快速二进制下载）
- **Node 22** 通过 fnm（快速 Node 管理器）
- **ast-grep** 用于基于抽象语法树（AST）的代码搜索
- **网络隔离工具**（iptables, ipset）带有 NET_ADMIN 能力
- **安全挂载**：`.devcontainer/` 挂载为只读，防止容器逃逸
- **令牌转发**：`CLAUDE_CODE_OAUTH_TOKEN` 和 `ANTHROPIC_API_KEY` 通过 `remoteEnv`
- **现代 CLI 工具**：ripgrep, fd, fzf, tmux, git-delta

---

## 语言特定部分

### Python 项目

**检测**：`pyproject.toml`, `requirements.txt`, `setup.py` 或 `*.py` 文件

**Dockerfile 添加**：

基 Dockerfile 已经包含 Python 3.13 通过 uv。如果需要不同版本（从 `pyproject.toml` 检测），修改 Python 安装：

```dockerfile
# 通过 uv 安装 Python（快速二进制下载，非源代码编译）
RUN uv python install <version> --default
```

**devcontainer.json 扩展**：

添加到 `customizations.vscode.extensions`：
```json
"ms-python.python",
"ms-python.vscode-pylance",
"charliermarsh.ruff"
```

添加到 `customizations.vscode.settings`：
```json
"python.defaultInterpreterPath": ".venv/bin/python",
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  }
}
```

**postCreateCommand**：
如果存在 `pyproject.toml`，链式命令：
```
rm -rf .venv && uv sync && uv run /opt/post_install.py
```

---

### Node/TypeScript 项目

**检测**：`package.json` 或 `tsconfig.json`

**不需要 Dockerfile 添加**：基模板包含 Node 22 通过 fnm（快速 Node 管理器）。

**devcontainer.json 扩展**：

添加到 `customizations.vscode.extensions`：
```json
"dbaeumer.vscode-eslint",
"esbenp.prettier-vscode"
```

添加到 `customizations.vscode.settings`：
```json
"editor.defaultFormatter": "esbenp.prettier-vscode",
"editor.codeActionsOnSave": {
  "source.fixAll.eslint": "explicit"
}
```

**postCreateCommand**：
从锁文件检测包管理器并链式执行与基命令：
- `pnpm-lock.yaml` → `uv run /opt/post_install.py && pnpm install --frozen-lockfile`
- `yarn.lock` → `uv run /opt/post_install.py && yarn install --frozen-lockfile`
- `package-lock.json` → `uv run /opt/post_install.py && npm ci`
- 无锁文件 → `uv run /opt/post_install.py && npm install`

---

### Rust 项目

**检测**：`Cargo.toml`

**需要添加的功能**：

```json
"ghcr.io/devcontainers/features/rust:1": {}
```

**devcontainer.json 扩展**：

添加到 `customizations.vscode.extensions`：
```json
"rust-lang.rust-analyzer",
"tamasfe.even-better-toml"
```

添加到 `customizations.vscode.settings`：
```json
"[rust]": {
  "editor.defaultFormatter": "rust-lang.rust-analyzer"
}
```

**postCreateCommand**：
如果存在 `Cargo.lock`，使用锁定构建：
```
uv run /opt/post_install.py && cargo build --locked
```
如果无锁文件，使用标准构建：
```
uv run /opt/post_install.py && cargo build
```

---

### Go 项目

**检测**：`go.mod`

**需要添加的功能**：

```json
"ghcr.io/devcontainers/features/go:1": {
  "version": "latest"
}
```

**devcontainer.json 扩展**：

添加到 `customizations.vscode.extensions`：
```json
"golang.go"
```

添加到 `customizations.vscode.settings`：
```json
"[go]": {
  "editor.defaultFormatter": "golang.go"
},
"go.useLanguageServer": true
```

**postCreateCommand**：
```
uv run /opt/post_install.py && go mod download
```

---

## 参考资料

获取更多指导，请参阅：
- `references/dockerfile-best-practices.md` - 层优化，多阶段构建，架构支持
- `references/features-vs-dockerfile.md` - 何时使用 devcontainer 功能 vs 自定义 Dockerfile

---

## 添加持久卷

`devcontainer.json` 中新挂载模式的示例：

```json
"mounts": [
  "source={{PROJECT_SLUG}}-<用途>-${devcontainerId},target=<容器路径>,type=volume"
]
```

常见添加：
- `source={{PROJECT_SLUG}}-cargo-${devcontainerId},target=/home/vscode/.cargo,type=volume`（Rust）
- `source={{PROJECT_SLUG}}-go-${devcontainerId},target=/home/vscode/go,type=volume`（Go）

---

## 输出文件

在项目的 `.devcontainer/` 目录中生成以下文件：

1. `Dockerfile` - 容器构建指令
2. `devcontainer.json` - VS Code/devcontainer 配置
3. `post_install.py` - 创建后设置脚本
4. `.zshrc` - Shell 配置
5. `install.sh` - 管理 devcontainer 的 CLI 工具（`devc` 命令）

---

## 验证清单

在向用户展示文件之前，请验证：

1. 所有 `{{PROJECT_NAME}}` 占位符都已替换为人类可读的名称
2. 所有 `{{PROJECT_SLUG}}` 占位符都已替换为 slug 化的名称
3. `devcontainer.json` 中的 JSON 语法有效（无尾随逗号，正确的嵌套）
4. 为所有检测到的语言添加了语言特定扩展
5. `postCreateCommand` 包含所有必要的设置命令（使用 `&&` 链式执行）

---

## 用户说明

生成后，告知用户：

1. 如何启动："在 VS Code 中打开并选择'重新打开到容器'"
2. 替代方案：`devcontainer up --workspace-folder .`
3. CLI 工具：运行 `.devcontainer/install.sh self-install` 将 `devc` 命令添加到 PATH
