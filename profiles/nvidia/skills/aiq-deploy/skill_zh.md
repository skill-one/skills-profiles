# AIQ部署技能

## 目的

使用此技能来获取本地或自托管NVIDIA AI-Q蓝图服务器的运行和验证，以供`aiq-research`使用。

此技能拥有设置、部署、操作检查、故障排除和关闭。它本身不运行深入研究。部署健康后，将验证的服务器URL交给`aiq-research`。
工作流程保持明确，以便在支持代理客户端之间重复进行部署验证和交接。

## 前置条件

用户需要：

- 访问克隆或更新`https://github.com/NVIDIA-AI-Blueprints/aiq`。
- 命令行中可用Git。
- 一个部署运行时：
  - 默认持久本地部署的Docker Engine与Docker Compose v2。
  - 本地进程或CLI模式所需的Python 3.11+和`uv`。
  - 本地浏览器UI开发模式所需的Node.js 20+和`npm`。
  - Helm模式所需的`kubectl` 1.28+、Helm 3.12+以及Kubernetes集群访问权限。
- GitHub、NVIDIA托管模型端点以及任何选定搜索提供者的网络访问权限。
- 存储在聊天外部的凭证。托管模型使用需要`NVIDIA_API_KEY`；网络研究至少需要一个支持搜索提供者的密钥，例如`TAVILY_API_KEY`、`SERPER_API_KEY`或`EXA_API_KEY`。
- 系统容量以供所选运行时使用。Docker Compose模式默认启动AI-Q后端和PostgreSQL；浏览器UI模式也使用前端端口`3000`。自托管模型或RAG部署可能需要GPU资源。

在写入密钥之前，验证`deploy/.env`是否被忽略：

```bash
git check-ignore deploy/.env
```

预期输出：`deploy/.env`或匹配的忽略规则。如果未被忽略，停止并修复忽略规则，然后再将凭证放入文件中。

## 说明

1. 定位或克隆AI-Q仓库。
2. 确认预期仓库文件存在。
3. 选择部署模式。
4. 准备`deploy/.env`，不要覆盖用户密钥。
5. 检查所选路径的运行时前置条件。
6. 启动所选部署。
7. 运行基本验证。
8. 向`aiq-research`报告验证的`AIQ_SERVER_URL`。
9. 询问是否运行可选的深入研究完成验证。

### 第1步 - 定位或克隆AI-Q

如果不存在AI-Q检出，在克隆前阅读`references/locate-or-clone.md`。在现有检出中，确认所需文件：

```bash
pwd
test -f pyproject.toml
test -f deploy/.env.example
test -d configs
```

预期输出：`pwd`打印AI-Q仓库路径；`test`命令退出状态为0且无输出。

### 第2步 - 选择部署模式

如果用户要求安装、部署、设置或运行AI-Q而不指定模式，询问：

```text
您希望如何运行AI-Q？

1. 技能后端 - 仅后端服务，供aiq-research使用，无浏览器UI。
2. CLI - 交互式终端AI-Q。
3. UI - 带后端和前端的浏览器AI-Q应用。
4. 自定义 - 部署前选择现有AI-Q配置或查看高级自定义文档。
```

在开始服务前等待用户的回答。

当用户已经指定了模式（例如Docker Compose、Helm、UI、CLI或Agent Skill后端）时，不要询问此问题。当`aiq-research`路由到此位置时，因为深入研究请求需要后端，所以不要询问完整的模式问题。在这种情况下，优先选择Agent Skill后端，并在需要时仅询问是否启动它。

### 第3步 - 准备环境和密钥

在更改`deploy/.env`前阅读`references/env-and-secrets.md`。

```bash
if [ ! -f deploy/.env ]; then
  cp deploy/.env.example deploy/.env
  echo "从deploy/.env.example创建deploy/.env"
fi
```

预期输出：当文件缺失时，`从deploy/.env.example创建deploy/.env`。当文件已存在时，无输出，并保留现有文件。

永远不要打印密钥值。如果凭证缺失，请要求用户更新`deploy/.env`；不要要求他们将密钥值粘贴到聊天中。

### 第4步 - 路由到所选部署路径

匹配用户请求，然后在执行前阅读参考文件：

| 用户意图 | 参考 |
|---|---|
| 不存在AI-Q检出，安装AIQ，克隆AIQ，定位仓库 | `references/locate-or-clone.md` |
| 配置环境，检查API密钥，检查`.env` | `references/env-and-secrets.md` |
| 选择AI-Q工作流配置，理解配置文件，设置`BACKEND_CONFIG`或`CONFIG_FILE` | `references/configs.md` |
| 仅后端本地服务器，供`aiq-research`使用，AIQ作为Agent Skill | `references/skill-backend.md` |
| 终端助手，仅CLI运行，无Web UI | `references/terminal-cli.md` |
| 快速本地开发运行，无需容器启动UI/后端 | `references/local-web.md` |
| 默认持久本地部署，Docker Compose，容器，PostgreSQL | `references/docker-compose.md` |
| Kubernetes，Helm，集群部署 | `references/kubernetes-helm.md` |
| 基础RAG / FRAG集成 | `references/frag.md` |
| 基本健康检查，浅层冒烟检查，交接给`aiq-research` | `references/validation.md` |
| 可选的深入研究完成验证 | `references/end-to-end-validation.md` |
| 日志，不健康服务，端口冲突，配置失败 | `references/troubleshooting.md` |
| 停止服务，重启，重建，安全清理 | `references/shutdown.md` |

### 第5步 - 验证和交接

启动后，阅读`references/validation.md`并运行所选模式的适当检查。对于默认本地后端，验证健康：

```bash
curl -sf http://localhost:8000/health
```

预期输出：成功的JSON健康响应或根据服务器构建的空成功响应。如果命令失败，请阅读`references/troubleshooting.md`并进行诊断，然后再声称后端已准备好。

`aiq-research`需要一个可访问的AI-Q服务器URL。如果后端在默认端口上运行，无需额外配置：

```bash
AIQ_SERVER_URL=http://localhost:8000
```

如果后端运行在其他地方，请告知用户设置：

```bash
export AIQ_SERVER_URL="http://localhost:<PORT>"
```

除非用户要求或确认部署后验证提示，否则不要继续进入深入研究或深入研究完成验证。此技能的成功标准是部署并基本验证的服务器，而不是报告生成质量。

## 版本兼容性

**重要提示：** 此技能设计用于NVIDIA AI-Q蓝图版本2.1.0。

语义版本兼容性规则：

```text
技能版本：X.Y.Z
蓝图版本：A.B.C

兼容条件：
1. A == X（主版本必须匹配）
2. B >= Y（次版本必须相等或更高）
3. C可以是任何值（补丁版本不影响兼容性）
```

示例：

- 技能版本2.1.0与蓝图版本2.1.0兼容。
- 技能版本2.1.0与蓝图版本2.2.0兼容。
- 技能版本2.1.0与蓝图版本2.1.5兼容。
- 技能版本2.1.0与蓝图版本3.0.0不兼容。
- 技能版本2.1.0与蓝图版本2.0.0不兼容。

如果您的蓝图版本不兼容：

1. 检查是否有与您的蓝图版本匹配的更新技能版本。
2. 使用与此技能兼容的蓝图版本。
3. 只有在用户接受兼容性风险时才继续；部署命令或配置名称可能已更改。

## 安全最佳实践

- 永远不要打印密钥值。仅检查所需环境变量是否已设置。
- 将凭证存储在`deploy/.env`或环境变量中，而不是在聊天记录、命令行历史记录、提交文件或示例命令中。
- 当`deploy/.env`已存在时，不要覆盖它。
- 在执行破坏性清理（例如使用`down -v`删除Docker卷）前询问。
- 除非`RAG_SERVER_URL`和`RAG_INGEST_URL`都配置且可访问，否则不要声称FRAG已准备好。
- 在可能的情况下自行运行验证命令。

## 限制

- 此技能准备和验证AI-Q基础设施；它不评判深入研究报告质量。
- 它不能提供或检查密钥值。用户必须在聊天外配置凭证。
- Helm、FRAG、自定义配置和自托管模型路径取决于用户控制的底层基础设施。
- 破坏性清理（例如删除Docker卷）需要明确用户批准。

## 示例

### 示例1：使用Docker Compose部署仅后端技能服务器

```bash
test -f deploy/.env || cp deploy/.env.example deploy/.env
git check-ignore deploy/.env
cd deploy/compose
BUILD_TARGET=release docker compose --env-file ../.env -f docker-compose.yaml config --quiet
BUILD_TARGET=release docker compose --env-file ../.env -f docker-compose.yaml up -d --build aiq-agent
curl -sf http://localhost:8000/health
```

预期输出：

```text
deploy/.env
<docker compose启动aiq-agent和依赖项>
<健康端点返回成功响应>
```

如果Docker、端口、凭证或健康检查失败，在重试前请阅读`references/troubleshooting.md`。

### 示例2：将非默认后端URL交接给aiq-research

```bash
export AIQ_SERVER_URL="http://localhost:8100"
curl -sf "$AIQ_SERVER_URL/health"
```

预期输出：成功的健康响应。然后告知用户在调用`aiq-research`前保持`AIQ_SERVER_URL`设置。

## 参考

| 主题 | 文档 |
|---|---|
| 定位或克隆AI-Q | `references/locate-or-clone.md` |
| 环境和密钥 | `references/env-and-secrets.md` |
| 工作流配置 | `references/configs.md` |
| Agent Skill后端 | `references/skill-backend.md` |
| CLI部署 | `references/terminal-cli.md` |
| 本地Web部署 | `references/local-web.md` |
| Docker Compose部署 | `references/docker-compose.md` |
| Kubernetes和Helm部署 | `references/kubernetes-helm.md` |
| FRAG集成 | `references/frag.md` |
| 基本验证 | `references/validation.md` |
| 端到端验证 | `references/end-to-end-validation.md` |
| 故障排除 | `references/troubleshooting.md` |
| 关闭和清理 | `references/shutdown.md` |

## 常见问题

### 问题：后端端口已被占用

**症状：**

- Docker Compose无法绑定端口`8000`。
- `curl -sf http://localhost:8000/health`连接到意外服务或失败。

**原因：**

- 另一个AI-Q后端或本地开发服务器已正在运行。
- `deploy/.env`中的`PORT`与现有进程冲突。

**解决方案：**

1. 确定进程：
   ```bash
   lsof -nP -iTCP:8000 -sTCP:LISTEN
   ```
2. 经用户批准停止冲突进程，或在`deploy/.env`中设置不同端口，例如`PORT=8100`。
3. 重新启动所选部署路径并验证：
   ```bash
   curl -sf http://localhost:8100/health
   ```

### 问题：所需凭证缺失

**症状：**

- 基础设施启动，但模型支持的聊天或研究请求失败。
- 日志提到未授权、禁止、无效密钥或缺少提供者配置。

**原因：**

- `NVIDIA_API_KEY`缺失或为空。
- 没有为网络研究配置支持搜索提供者的密钥。

**解决方案：**

1. 按照不打印值的方式检查存在性，遵循`references/env-and-secrets.md`。
2. 要求用户更新`deploy/.env`；不要要求他们将密钥值粘贴到聊天中。
3. 用户更新凭证后重新运行`references/validation.md`。

### 问题：后端健康但与aiq-research不兼容

**症状：**

- `/health`成功，但`/chat`或`/v1/jobs/async/agents`失败。
- `aiq-research`报告异步代理不可用。

**原因：**

- 所选配置是CLI模式或未暴露技能期望的Web/API后端。
- `BACKEND_CONFIG`或`CONFIG_FILE`指向错误的AI-Q配置。

**解决方案：**

1. 阅读`references/configs.md`并确认所选配置支持API。
2. 对于默认技能后端，使用`configs/config_web_default_llamaindex.yml`。
3. 重新启动后端并重新运行`references/validation.md`。

### 问题：Docker清理会删除有用状态

**症状：**

- 故障排除建议`docker compose down -v`。
- 用户可能希望保留本地PostgreSQL作业或检查点数据。

**原因：**

- `down -v`删除Docker卷。
- 配置或镜像更改通常可以通过重建和重启解决。

**解决方案：**

1. 优先使用`references/shutdown.md`中的正常重启。
2. 在运行卷删除前请求明确批准。
3. 清理后，从所选路径重新运行部署和验证。
