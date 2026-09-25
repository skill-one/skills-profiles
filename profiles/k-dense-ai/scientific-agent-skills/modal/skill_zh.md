# 模态

## 概述

模态是一个用于无服务器运行 Python 代码的云平台，专注于 AI/ML 工作负载。主要功能：
- **按需 GPU 计算**（T4、L4、A10、L40S、A100、H100、H200、B200）
- **无服务器函数**，支持从零到数千个容器的自动扩展
- **完全用 Python 代码构建的自定义容器镜像**
- **通过卷（Volumes）实现持久化存储**，用于模型权重和数据集
- **Web 端点**，用于服务模型和 API
- **通过 cron 或固定间隔的定时任务**
- **亚秒级冷启动**，用于低延迟推理

模态中的所有内容都以代码形式定义——无需 YAML 或 Dockerfile（尽管两者都受支持）。

## 何时使用此技能

使用此技能的情况：
- 在云端部署或服务 AI/ML 模型
- 运行 GPU 加速计算（训练、推理、微调）
- 创建无服务器 Web API 或端点
- 并行扩展批处理任务
- 调度定期任务（数据管道、重新训练、网络爬虫）
- 需要持久化云存储用于模型权重或数据集
- 希望在自定义容器环境中运行代码
- 构建任务队列或异步任务处理系统

## 安装和认证

### 安装

```bash
uv pip install modal
```

模态 Python SDK 支持 Python 3.10–3.14。此技能针对稳定的 `modal>=1.0` API（当前版本：1.4.x）。

### 认证

优先使用现有凭证，而不是创建新凭证。以下两个模态特定的变量是相关的——不要读取、加载或暴露任何其他环境变量或 `.env` 文件内容：

1. 检查当前环境中是否已设置 `MODAL_TOKEN_ID` 和 `MODAL_TOKEN_SECRET`。
2. 如果未设置，仅在本地 `.env` 文件中查找这两个键（忽略所有其他条目），并根据工作流程需要加载它们。
3. 只有在上述两个来源都不提供这两个值时，才回退到交互式 `modal setup` 或生成新令牌。

```bash
modal setup
```

这将打开浏览器进行认证。对于 CI/CD 或无头环境，请使用环境变量：

```bash
export MODAL_TOKEN_ID=<your-token-id>
export MODAL_TOKEN_SECRET=<your-token-secret>
```

如果环境中或 `.env` 中没有令牌，请在 https://modal.com/settings 生成它们。

模态提供每月 30 美元的免费套餐。

**参考**：有关详细设置和第一个应用程序的逐步指南，请参阅 `references/getting-started.md`。

## 核心概念

### 应用和函数

模态的 `App` 将相关的函数分组。使用 `@app.function()` 装饰的函数在云端远程运行：

```python
import modal

app = modal.App("my-app")

@app.function()
def square(x):
    return x ** 2

@app.local_entrypoint()
def main():
    # .remote() 在云端运行
    print(square.remote(42))
```

使用 `modal run script.py` 运行。使用 `modal deploy script.py` 部署。

**参考**：有关生命周期钩子、类、`.map()`、`.spawn()` 等内容，请参阅 `references/functions.md`。

### 容器镜像

模态从 Python 代码构建容器镜像。推荐的包安装器是 `uv`：

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .uv_pip_install("torch==2.12.0", "transformers==5.9.0", "accelerate==1.13.0")
    .apt_install("git")
)

@app.function(image=image)
def inference(prompt):
    from transformers import pipeline
    pipe = pipeline("text-generation", model="meta-llama/Llama-3-8B")
    return pipe(prompt)
```

镜像的关键方法：
- `.uv_pip_install()` — 使用 uv 安装 Python 包（推荐）
- `.pip_install()` — 使用 pip 安装（回退）
- `.apt_install()` — 安装系统包
- `.run_commands()` — 在构建期间运行 shell 命令
- `.run_function()` — 在构建期间运行 Python（例如，下载模型权重）
- `.add_local_python_source()` — 添加本地模块
- `.env()` — 设置环境变量

**参考**：有关 Dockerfile、micromamba、缓存、GPU 构建步骤，请参阅 `references/images.md`。

### GPU 计算

通过 `gpu` 参数请求 GPU：

```python
@app.function(gpu="H100")
def train_model():
    import torch
    device = torch.device("cuda")
    # GPU 训练代码
```

# 多 GPU
@app.function(gpu="H100:4")
def distributed_training():
    ...

# GPU 回退链
@app.function(gpu=["H100", "A100-80GB", "A100-40GB"])
def flexible_inference():
    ...

```

可用的 GPU：T4、L4、A10、L40S、A100-40GB、A100-80GB、RTX-PRO-6000、H100、H200、B200、B200+
- GPU 始终指定为 **字符串**（例如 `gpu="H100"`，`gpu="H100:4"`）。旧版 `modal.gpu.*` 对象自 v0.73.31 起已弃用。
- 每个容器最多 8 个 GPU（A10 除外：最多 4 个）
- L40S 推荐用于推理（成本/性能平衡，48 GB VRAM）
- H100/A100 可自动升级为 H200/A100-80GB，无需额外费用
- 使用 `gpu="H100!"` 防止自动升级

**参考**：有关 GPU 选择指南和多 GPU 训练，请参阅 `references/gpu.md`。

### 卷（持久化存储）

卷提供分布式持久化文件存储：

```python
vol = modal.Volume.from_name("model-weights", create_if_missing=True)

@app.function(volumes={"/data": vol})
def save_model():
    # 写入挂载路径
    with open("/data/model.pt", "wb") as f:
        torch.save(model.state_dict(), f)

@app.function(volumes={"/data": vol})
def load_model():
    model.load_state_dict(torch.load("/data/model.pt"))
```

- 优化用于一次性写入、多次读取的工作负载（模型权重、数据集）
- CLI 访问：`modal volume ls`，`modal volume put`，`modal volume get`
- 每隔几秒自动提交
- 使用 `vol.with_mount_options(read_only=True, sub_path="subset")` 挂载为只读或限制为子目录

**参考**：有关 v2 卷、并发写入和最佳实践，请参阅 `references/volumes.md`。

### 密钥

安全地将凭证传递给函数：

```python
@app.function(secrets=[modal.Secret.from_name("my-api-keys")])
def call_api():
    import os
    api_key = os.environ["API_KEY"]
    # 使用密钥
```

通过 CLI 创建：`modal secret create my-api-keys API_KEY=sk-xxx`

或从 `.env` 文件创建：`modal.Secret.from_dotenv()`

**参考**：有关仪表板设置、多个密钥和模板，请参阅 `references/secrets.md`。

### Web 端点

将模型和 API 作为 Web 端点服务：

```python
@app.function()
@modal.fastapi_endpoint()
def predict(text: str):
    return {"result": model.predict(text)}
```

- `modal serve script.py` — 开发时热重载和临时 URL
- `modal deploy script.py` — 生产部署和永久 URL
- 支持 FastAPI、ASGI（Starlette、FastHTML）、WSGI（Flask、Django）、WebSocket
- 请求体最多 4 GiB，响应大小无限制

**参考**：有关 ASGI/WSGI 应用、流式传输、认证和 WebSocket，请参阅 `references/web-endpoints.md`。

### 定时任务

按计划运行函数：

```python
@app.function(schedule=modal.Cron("0 9 * * *"))  # 每天上午 9 点 UTC
def daily_pipeline():
    # ETL、重新训练、网络爬虫等
    ...

@app.function(schedule=modal.Period(hours=6))
def periodic_check():
    ...
```

使用 `modal deploy script.py` 部署以激活计划。

- `modal.Cron("...")` — 标准 cron 语法，跨部署稳定
- `modal.Period(hours=N)` — 固定间隔，重新部署时重置
- 在模态仪表板中监控运行情况

**参考**：有关 cron 语法和管理，请参阅 `references/scheduled-jobs.md`。

### 扩展和并发

模态自动扩展容器。配置限制：

```python
@app.function(
    max_containers=100,    # 上限
    min_containers=2,      # 保持热状态以降低延迟
    buffer_containers=5,   # 预留容量
    scaledown_window=300,  # 空闲秒数后关闭
)
def process(data):
    ...
```

使用 `.map()` 并行处理输入：

```python
results = list(process.map([item1, item2, item3, ...]))
```

使用 `@modal.concurrent` 启用每个容器的并发请求处理。在 `max_inputs`（硬上限）下方设置 `target_inputs`（自动扩展器每容器的目标），以在扩展时保持余量：

```python
@app.function()
@modal.concurrent(max_inputs=10, target_inputs=8)
async def handle_request(req):
    ...
```

在不重新部署的情况下重新配置已部署的 Function 或 Cls，使用 `Function.with_options()` / `Function.with_concurrency()` / `Function.with_batching()`（以及 `Cls.with_options()`）：

```python
Model = modal.Cls.from_name("my-app", "Model")
fast = Model.with_options(gpu="H200", max_containers=20)
fast().generate.remote(prompt)
```

**参考**：有关 `.map()`、`.starmap()`、`.spawn()` 和限制，请参阅 `references/scaling.md`。

### 资源配置

```python
@app.function(
    cpu=4.0,              # 物理核心（不是 vCPU）
    memory=16384,         # MiB
    ephemeral_disk=51200, # MiB（最高 3 TiB）
    timeout=3600,         # 秒
)
def heavy_computation():
    ...
```

默认值：0.125 CPU 核心，128 MiB 内存。按最大（请求、使用）计费。

**参考**：有关限制和计费详情，请参阅 `references/resources.md`。

## 带生命周期钩子的类

用于有状态工作负载（例如，加载一次模型并服务许多请求）：

```python
@app.cls(gpu="L40S", image=image)
class Predictor:
    @modal.enter()
    def load_model(self):
        self.model = load_heavy_model()  # 容器启动时运行一次

    @modal.method()
    def predict(self, text: str):
        return self.model(text)

    @modal.exit()
    def cleanup(self):
        ...  # 容器关闭时运行
```

调用方式：`Predictor().predict.remote("hello")`

## 沙盒

用于运行不受信任或动态生成的代码（例如，AI-agent 输出或代码解释器），使用 `modal.Sandbox`——一个您可编程创建和控制而非装饰的函数的隔离容器：

```python
app = modal.App.lookup("sandbox-demo", create_if_missing=True)

# 隔离容器；限制出站连接以用于不受信任的工作负载
sb = modal.Sandbox.create(
    app=app,
    image=modal.Image.debian_slim(),
    outbound_cidr_allowlist=["10.0.0.0/8"],
)

# 通过文件系统 API（beta）流式传输文件进出
sb.filesystem.write_text("print(2 ** 10)\n", "/tmp/job.py")
contents = sb.filesystem.read_text("/tmp/job.py")

sb.terminate()
```

- 使用其 `exec` 方法在沙盒内运行命令（例如，运行 `python /tmp/job.py`）并从返回的进程句柄读取 stdout——请参阅 `references/api_reference.md`
- 使用 `outbound_cidr_allowlist=[...]` / `inbound_cidr_allowlist=[...]` 限制连接
- 使用 `sb.snapshot_filesystem()` 快照文件系统以将其用作基础镜像
- 适用于代码解释器、agent 工具执行和用户隔离

## 常见工作流模式

### GPU 模型推理服务

```python
import modal

app = modal.App("llm-service")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .uv_pip_install("vllm")
)

@app.cls(gpu="H100", image=image, min_containers=1)
class LLMService:
    @modal.enter()
    def load(self):
        from vllm import LLM
        self.llm = LLM(model="meta-llama/Llama-3-70B")

    @modal.method()
    @modal.fastapi_endpoint(method="POST")
    def generate(self, prompt: str, max_tokens: int = 256):
        outputs = self.llm.generate([prompt], max_tokens=max_tokens)
        return {"text": outputs[0].outputs[0].text}
```

### 批处理处理管道

```python
app = modal.App("batch-pipeline")
vol = modal.Volume.from_name("pipeline-data", create_if_missing=True)

@app.function(volumes={"/data": vol}, cpu=4.0, memory=8192)
def process_chunk(chunk_id: int):
    import pandas as pd
    df = pd.read_parquet(f"/data/input/chunk_{chunk_id}.parquet")
    result = heavy_transform(df)
    result.to_parquet(f"/data/output/chunk_{chunk_id}.parquet")
    return len(result)

@app.local_entrypoint()
def main():
    chunk_ids = list(range(100))
    results = list(process_chunk.map(chunk_ids))
    print(f"Processed {sum(results)} total rows")
```

### 定时数据管道

```python
app = modal.App("etl-pipeline")

@app.function(
    schedule=modal.Cron("0 */6 * * *"),  # 每 6 小时
    secrets=[modal.Secret.from_name("db-credentials")],
)
def etl_job():
    import os
    db_url = os.environ["DATABASE_URL"]
    # 提取、转换、加载
    ...
```

## CLI 参考

| 命令 | 描述 |
|------|------|
| `modal setup` | 使用模态进行认证 |
| `modal run script.py` | 运行脚本的本地入口点 |
| `modal serve script.py` | 带热重载的开发服务器 |
| `modal deploy script.py` | 部署到生产环境 |
| `modal volume ls <name>` | 列出卷中的文件 |
| `modal volume put <name> <file>` | 将文件上传到卷 |
| `modal volume get <name> <file>` | 从卷下载文件 |
| `modal secret create <name> K=V` | 创建密钥 |
| `modal secret list` | 列出密钥 |
| `modal app list` | 列出已部署的应用 |
| `modal app stop <name>` | 停止已部署的应用 |

## 安全注意事项

- **凭证**：只需要 `MODAL_TOKEN_ID` 和 `MODAL_TOKEN_SECRET` 进行认证。不要读取、记录或转发任何其他环境变量或 `.env` 条目。
- **子进程/自定义服务器**：某些模式（多 GPU 训练启动器、`@modal.web_server` 应用）在构建期间调用 `subprocess.run`/`subprocess.Popen` 或 shell 命令。保持参数列表固定和硬编码。永远不要从未清理的用户输入构造子进程或 shell 参数——将不受信任的值作为数据（文件、环境变量、stdin）传递，而不是作为命令参数。
- **不受信任的代码**：在 `modal.Sandbox` 中运行用户或模型生成的代码（见上文），而不是常规函数，并使用 CIDR 允许列表限制网络访问。

## 参考文件

每个主题的详细文档：

- `references/getting-started.md` — 安装、认证、第一个应用
- `references/functions.md` — 函数、类、生命周期钩子、远程执行
- `references/images.md` — 容器镜像、包安装、缓存
- `references/gpu.md` — GPU 类型、选择、多 GPU、训练
- `references/volumes.md` — 持久化存储、文件管理、v2 卷
- `references/secrets.md` — 凭证、环境变量、dotenv
- `references/web-endpoints.md` — FastAPI、ASGI/WSGI、流式传输、认证、WebSocket
- `references/scheduled-jobs.md` — Cron、周期性计划、管理
- `references/scaling.md` — 自动扩展、并发、.map()、限制
- `references/resources.md` — CPU、内存、磁盘、超时配置
- `references/examples.md` — 常见用例和模式
- `references/api_reference.md` — 关键 API 类和方法

当需要超出此概述的详细信息时，请阅读这些文件。
