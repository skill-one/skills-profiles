<概述>
`langgraph` 命令行工具（CLI）管理 LangGraph 应用的完整生命周期——从使用模板创建新项目到将其部署到 LangGraph 平台（LangSmith 部署）。

主要命令：
- **`langgraph new`** — 从模板创建项目
- **`langgraph dev`** — 本地运行并支持热重载（无需 Docker）
- **`langgraph build`** — 构建 Docker 镜像
- **`langgraph up`** — 通过 Docker Compose 本地启动
- **`langgraph deploy`** — 部署到 LangGraph 平台
- **`langgraph dockerfile`** — 生成 Dockerfile

所有命令（除 `new` 外）均从项目根目录下的 `langgraph.json` 配置文件读取。

</概述>

## 使用场景

当用户需要执行以下操作时，请使用此工具：
- 使用模板创建新的 LangGraph 项目
- 运行本地开发或类似生产环境的服务器
- 构建或部署 LangGraph 应用
- 查看或编辑 `langgraph.json` 配置
- 管理 LangSmith 部署（列出、删除、查看日志）

## 安装

```bash
# Python
pip install 'langgraph-cli[inmem]'   # 包含 langgraph dev 支持
pip install langgraph-cli             # 不包含 dev 服务器（仅 build/up/deploy）

# 如果使用 UV 作为包管理器
uv add "langgraph-cli[inmem]"       # 包含 langgraph dev 支持
uv add langgraph-cli                # 不包含 dev 服务器（仅 build/up/deploy）

# JavaScript
npx @langchain/langgraph-cli         # 按需使用
npm install -g @langchain/langgraph-cli  # 全局安装（可用作 langgraphjs）
```

## 命令

### `langgraph new [PATH]`

从模板创建新项目。

```bash
langgraph new                          # 交互式选择模板
langgraph new ./my-agent               # 在指定目录创建
langgraph new --template agent-python  # 跳过提示，直接使用模板
```

可用模板：`deep-agent-python`, `deep-agent-js`, `agent-python`, `new-langgraph-project-python`, `new-langgraph-project-js`

### `langgraph dev`

运行本地开发服务器并支持热重载。无需 Docker。

```bash
langgraph dev                              # 默认：localhost:2024
langgraph dev --port 8000                  # 自定义端口
langgraph dev --config ./langgraph.json    # 显式配置路径
langgraph dev --no-reload                  # 禁用热重载
langgraph dev --no-browser                 # 不自动打开 LangGraph Studio
langgraph dev --host 0.0.0.0              # 绑定到所有接口（仅限可信网络）
langgraph dev --tunnel                     # 通过 Cloudflare 隧道暴露以供远程访问
langgraph dev --debug-port 5678            # 启用远程调试器（需要 debugpy）
langgraph dev --n-jobs-per-worker 20       # 每个工作线程的最大并发任务数（默认：10）
```

### `langgraph build`

为 LangGraph API 服务器构建 Docker 镜像。

```bash
langgraph build -t my-image                # 必须标记镜像
langgraph build -t my-image --no-pull      # 使用本地构建的基镜像
langgraph build -t my-image -c langgraph.json  # 显式配置
langgraph build -t my-image --base-image langchain/langgraph-server:0.2.18  # 固定基版本
```

### `langgraph up`

通过 Docker Compose 本地启动 LangGraph API 服务器（包含 Postgres）。

```bash
langgraph up                               # 默认端口 8123
langgraph up --port 8000                   # 自定义端口
langgraph up --watch                       # 文件更改时重启
langgraph up --recreate                    # 强制重新构建（用于预部署验证）
langgraph up --postgres-uri postgresql://...  # 外部 Postgres
langgraph up --no-pull                     # 使用本地镜像（langgraph build 后）
langgraph up --image my-image              # 跳过构建，使用预构建镜像
langgraph up -d docker-compose.yml         # 添加额外的 Docker 服务
langgraph up --debugger-port 8124          # 提供调试器 UI
langgraph up --wait                        # 阻塞直到服务健康
```

### `langgraph deploy`

构建并部署到 LangGraph 平台（LangSmith 部署）。需要 Docker。在 Apple Silicon（M1/M2/M3）上，还需要 Docker Buildx 才能进行跨编译到 `linux/amd64`。

```bash
langgraph deploy                           # 部署，名称默认为目录名
langgraph deploy --name my-agent           # 显式部署名称
langgraph deploy --deployment-type prod    # 生产部署（默认：dev）
langgraph deploy --tag v1.2.0              # 自定义镜像标签（默认：latest）
langgraph deploy --deployment-id <id>      # 通过 ID 更新现有部署
langgraph deploy --config ./langgraph.json # 显式配置路径
langgraph deploy --no-wait                 # 不等待部署状态
langgraph deploy --verbose                 # 显示详细服务器日志
```

前提条件：环境变量中包含 `LANGSMITH_API_KEY` 或 `.env` 文件。

`langgraph deploy` 也接受构建标志：`--base-image`, `--pull`/`--no-pull`。

#### `langgraph deploy list`

```bash
langgraph deploy list                      # 列出所有部署
langgraph deploy list --name-contains bot  # 按名称过滤
```

#### `langgraph deploy delete`

```bash
langgraph deploy delete <deployment-id>          # 交互式确认
langgraph deploy delete <deployment-id> --force  # 跳过确认
```

#### `langgraph deploy logs`

```bash
langgraph deploy logs                                  # 运行时日志，最后 100 条
langgraph deploy logs --name my-agent                  # 按部署名称
langgraph deploy logs --deployment-id <id>             # 按部署 ID
langgraph deploy logs --type build                     # 构建日志而非运行时日志
langgraph deploy logs -f                               # 跟踪/流式传输日志
langgraph deploy logs --level error                    # 按级别过滤（debug|info|warning|error|critical）
langgraph deploy logs -q "timeout"                     # 搜索过滤
langgraph deploy logs --limit 500                      # 更多条目
langgraph deploy logs --start-time 2026-03-08T00:00:00Z  # 时间范围
```

### `langgraph dockerfile <SAVE_PATH>`

无需构建即可生成 Dockerfile（以及可选的 Docker Compose 文件）。

```bash
langgraph dockerfile ./Dockerfile                      # 生成 Dockerfile
langgraph dockerfile ./Dockerfile --add-docker-compose # 同时生成 compose + .env + .dockerignore
```

## `langgraph.json` 参考

所有 CLI 命令（`dev`, `build`, `up`, `deploy`）使用的配置文件。默认位于当前目录的 `langgraph.json`。

### 最小配置（Python）

```json
{
    "dependencies": ["."],
    "graphs": {
        "agent": "./my_agent/agent.py:graph"
    },
    "env": "./.env"
}
```

### 最小配置（JavaScript）

```json
{
    "dependencies": ["."],
    "graphs": {
        "agent": "./src/agent.js:graph"
    },
    "env": "./.env"
}
```

### 完整配置（包含所有键）

```json
{
    "dependencies": [".", "langchain_openai", "./local_package"],
    "graphs": {
        "agent": "./my_agent/agent.py:graph",
        "retriever": "./my_agent/rag.py:rag_graph"
    },
    "env": "./.env",
    "python_version": "3.12",
    "pip_config_file": "./pip.conf",
    "dockerfile_lines": [
        "RUN apt-get update && apt-get install -y ffmpeg"
    ]
}
```

### 键参考

| 键 | 是否必需 | 描述 |
|-----|----------|-------------|
| `dependencies` | 是 | 依赖数组。`"."` 通过 `pyproject.toml`, `setup.py`, `requirements.txt`, 或 `package.json` 查找本地包。也可以是子目录路径（`"./my_pkg"`）或包名（`"langchain_openai"`）。 |
| `graphs` | 是 | 图 ID 到路径的映射。格式：`./path/to/file.py:variable`（Python）或 `./path/to/file.js:function`（JS）。变量必须是 `CompiledGraph` 或返回该对象的函数。支持多个图。 |
| `env` | 否 | `.env` 文件路径（字符串）或环境变量名到值的内联映射（对象）。由 `langgraph dev` 和 `langgraph up` 本地使用。`langgraph deploy` 从此文件读取并添加变量作为部署密钥。 |
| `python_version` | 否 | `"3.11"`, `"3.12"`, 或 `"3.13"`。默认为 `"3.11"`。 |
| `node_version` | 否 | JS 项目的 Node.js 版本。 |
| `pip_config_file` | 否 | 用于自定义包索引的 pip 配置文件路径。 |
| `dockerfile_lines` | 否 | 在导入基镜像后追加的 Dockerfile 行数组。用于系统包、二进制文件或自定义设置。 |

## 典型工作流程

1. **创建项目** — 使用 `langgraph new` 从模板创建项目。
2. **配置** — 编辑 `langgraph.json`：设置依赖项，将 `graphs` 指向你的编译后的图，添加 `.env`。
3. **开发** — 使用 `langgraph dev` 进行快速本地迭代并支持热重载（无需 Docker，端口 2024）。
4. **验证** — 使用 `langgraph up --recreate` 在类似生产的 Docker 堆栈中测试（端口 8123，包含 Postgres）。
5. **部署** — 使用 `langgraph deploy` 部署到 LangGraph 平台（LangSmith 部署）。
6. **监控** — 使用 `langgraph deploy logs -f` 查看运行时日志；`--type build` 查看构建日志。

## `langgraph dev` 与 `langgraph up` 的区别

| 功能 | `langgraph dev` | `langgraph up` |
|---------|----------------|----------------|
| Docker 是否必需 | 否 | 是 |
| 安装 | `pip install 'langgraph-cli[inmem]'` | `pip install langgraph-cli` |
| 主要用途 | 快速开发与测试 | 类似生产的验证 |
| 状态持久化 | 内存/本地目录序列化 | PostgreSQL |
| 热重载 | 是（默认） | 可选（`--watch`） |
| 默认端口 | 2024 | 8123 |
| 资源使用 | 轻量级 | 更重（Docker 容器用于服务器、Postgres、Redis） |
| IDE 调试 | 内置 DAP 支持（`--debug-port`） | 容器调试 |

## 注意事项

- **`langgraph deploy` 需要 Docker** — 在 Apple Silicon（M1/M2/M3）上，还需要 Docker Buildx 才能进行跨编译到 `linux/amd64`。
- **`langgraph deploy` 只能更新自己的部署** — 通过 LangSmith UI 或 GitHub 集成创建的部署无法使用 `langgraph deploy` 更新。使用 UI 进行这些操作。
- **`dependencies` 必须包含所有包** — `langgraph.json` 中的 `dependencies` 数组必须指向你的包配置位置（例如 `"."` 为根目录）。实际包从该位置的 `pyproject.toml`、`requirements.txt` 或 `package.json` 解析。
- **`langgraph dev` 无需 Docker 即可运行** — 它直接在你的环境中运行。如果你的代码依赖系统包（例如 `ffmpeg`），则必须本地安装。使用 `langgraph up` 验证 Docker 构建。
- **JavaScript CLI** — 使用 `npx @langchain/langgraph-cli <command>`（或 `langgraphjs` 如果通过 `npm install -g @langchain/langgraph-cli` 全局安装）。
- **API 密钥** — `LANGSMITH_API_KEY` 对 `langgraph deploy` 是必需的。对于 `langgraph dev`，它是可选的——服务器无需它即可运行，但你在 LangSmith 中不会获得跟踪。也可以通过 `LANGGRAPH_HOST_API_KEY` 或 `LANGCHAIN_API_KEY` 设置。
