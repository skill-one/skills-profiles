# Runpod Flash

在本地编写代码，使用 `flash dev` 进行迭代——它将在远程 Runpod 的 GPU/CPUs 上运行您的函数，并具有热重载和实时工作日志——然后使用 `flash deploy` 进行发布。`Endpoint` 负责资源分配。

`runpod-flash` 会按其自身节奏发布，因此 **`flash --help` 和 `flash <命令> --help` 是命令界面的权威说明**——这是心智模型、决策规则和易错点，有助于确保输出不包含错误。在确定子命令或标志不可用时，请先使用 `pip show runpod-flash` 确认已安装的版本。

**对于多步骤操作，首先提供示例。** Flash 出现在经过验证的端到端路径中——[03 变体 B（通过 Flash 的 whisper 端点）](../runpod/golden-paths/03-whisper-endpoint/variant-b-flash.md) 和 [08（微调 → 提供）](../runpod/golden-paths/08-finetune-to-serverless.md）；完整索引位于 [runpod/golden-paths/README.md](../runpod/golden-paths/README.md)。在规划发布前，请打开匹配的路径——它包含此技能仅总结的顺序和成本清理信息。

**按需加载——此技能保持心智模型 + 易错点一致；详细信息位于 [`reference/`](reference/)：**

| 需求 | 阅读 |
|------|------|
| 安装、认证、`flash init` 和完整的 `flash` 命令列表 | [reference/setup-and-cli.md](reference/setup-and-cli.md) |
| `Endpoint(...)` 构造函数参数、`NetworkVolume`/`PodTemplate`/`EndpointJob`、GPU & CPU 枚举表 | [reference/api.md](reference/api.md) |
| 示例模式——选择模型、热工作模型加载、CPU→GPU 管道、并行调用 | [reference/patterns.md](reference/patterns.md) |

快速入门：`uv tool install runpod-flash` → `flash login`（或 `export RUNPOD_API_KEY=...`）→ `flash init my-project` → `flash dev`。详细信息请参阅 [reference/setup-and-cli.md](reference/setup-and-cli.md)。

## 开发与发布

- `flash dev` — **迭代。** 本地服务器位于 `:8888`，但您的装饰函数在 **远程 GPU/CPU 工作器** 上执行。保存时进行热重载，并 **实时将工作器的日志流式传输到终端**。无需构建/上传/发布等待——在开发期间始终使用此功能。
- `flash deploy` — **发布。** 构建一个工件并部署一个稳定的端点。速度慢（构建 + 上传 + 资源分配）；仅在代码在 `flash dev` 下工作正常后执行此操作。

`flash dev` 仅将 **函数体** 发送到工作器，因此模块级名称的 `NameError` 会立即在此处显示。`flash deploy` 会导入整个模块，并可能掩盖该错误（参见易错点 #1）。使用 `flash dev` 进行开发，您可以首先捕获它。

## 自主开发循环

`flash dev` 是一个长时间运行的服务器。三条规则：
- **在后台运行它** — 不要阻塞等待它。
- **将其输出**捕获到日志文件。
- **通过 HTTP 驱动它。**

捕获的日志是远程工作器的实时流（冷启动、模型加载、`print`、tracebacks）——读取它以进行调试。

```bash
flash dev > /tmp/flash-dev.log 2>&1 &                          # 后台运行；不要阻塞
for i in $(seq 1 60); do grep -q "flash dev  localhost:" /tmp/flash-dev.log && break; sleep 2; done  # 约 2 分钟限制；如果未出现，请检查日志中的错误
URL=$(grep -o "localhost:[0-9]*" /tmp/flash-dev.log | head -1)               # 实际端口（如果 8888 被占用，端口会自动递增）
curl -s "$URL/main/predict" -d '{"data": {...}}'               # 分发到远程工作器
```

- **从日志中读取实际 URL** — Flash 如果 8888 正在使用中会自动递增端口，并打印 `✓ flash dev  localhost:<端口>` 以及路由表。
- **路由按文件命名空间化**：`main.py` 的 `/predict` 在 `/main/predict` 上提供。
- **两种路由形状、两种主体形状**（不匹配 → `422` 指定 `loc` 中的缺失字段）：
  - **负载均衡**（`@api.post("/predict")`）→ `POST /main/predict`，主体是顶层参数：处理程序 `def predict(data: dict)` 需要 `{"data": {...}}`（不是裸对象）。
  - **队列式**（裸 `@Endpoint` 装饰器）→ `POST /main/runsync`（本地开发服务器仅生成 `/runsync`；生产环境也公开 `/run`），主体是 **双重包装** 在 `input` 中：处理程序 `def synthesize(data: dict)` 需要 `{"input": {"data": {...}}}`。外层 `input` 是队列信封；内部键是处理程序的参数名。
- 编辑处理程序并保存——热重载重新同步主体；只需重新发送请求，无需重新部署。添加 `--auto-provision` 跳过首次调用的冷启动。完成时使用 `kill %1`。

## 端点：三种模式

完整的构造函数参数和 GPU/CPU 枚举表位于 [reference/api.md](reference/api.md)。

### 模式 1：您的代码（基于队列的装饰器）

一个函数 = 一个端点及其自己的工作器。

```python
from runpod_flash import Endpoint, GpuGroup

@Endpoint(name="my-worker", gpu=GpuGroup.AMPERE_80, workers=5, dependencies=["torch"])
async def compute(data):
    import torch  # 必须在函数内部导入（cloudpickle）
    return {"sum": torch.tensor(data, device="cuda").sum().item()}

result = await compute([1, 2, 3])
```

### 模式 2：您的代码（负载均衡路由）

多个 HTTP 路由共享一个工作器池。

```python
from runpod_flash import Endpoint, GpuGroup

api = Endpoint(name="my-api", gpu=GpuGroup.ADA_24, workers=(1, 5), dependencies=["torch"])

@api.post("/predict")
async def predict(data: list[float]):
    import torch
    return {"result": torch.tensor(data, device="cuda").sum().item()}

@api.get("/health")
async def health():
    return {"status": "ok"}
```

### 模式 3：外部镜像（客户端）

部署预构建的 Docker 镜像并通过 HTTP 调用。

```python
from runpod_flash import Endpoint, GpuGroup, PodTemplate

server = Endpoint(
    name="my-server",
    image="my-org/my-image:latest",
    gpu=GpuGroup.AMPERE_80,
    workers=1,
    env={"HF_TOKEN": "xxx"},
    template=PodTemplate(containerDiskInGb=100),
)

# 负载均衡式
result = await server.post("/v1/completions", {"prompt": "hello"})
models = await server.get("/v1/models")

# 基于队列式
job = await server.run({"prompt": "hello"})        # 可选：webhook="https://..." 用于完成回调
await job.wait()
print(job.output)
```

通过 ID 连接到现有端点（无需资源分配）：

```python
ep = Endpoint(id="abc123")
job = await ep.runsync({"prompt": "hello"})  # runsync 将此操作包装为 {"input": {"prompt": "hello"}}
print(job.output)
```

## 模式如何确定

| 参数 | 模式 |
|-----------|------|
| `name=` 仅设置 | 装饰器（您的代码） |
| `image=` 设置 | 客户端（部署镜像，然后 HTTP 调用） |
| `id=` 设置 | 客户端（连接到现有，无需资源分配） |

上表是 *如何* 从参数中选择模式的。*何时* 使用 `image=`：

### 何时使用 `image=`（自定义容器）而不是您的代码

默认情况下编写 Python（装饰器 / 路由）——它使用 `dependencies=[...]`/`system_dependencies=[...]` 运行任意代码，无需 Dockerfile。即使大型 HuggingFace 模型也保持装饰器模式（权重在运行时流式传输——参见 [reference/patterns.md → 加载 ML 模型](reference/patterns.md#loading-ml-models-warm-workers)）。仅在您需要时使用 `image=`：

- **预构建的推理服务器**—— vLLM、TensorRT-LLM (`image="vllm/vllm-openai:latest"`，或 `runpod/worker-vllm`、`runpod/worker-comfy`)
- **系统级依赖项无法通过 pip 安装**——特定的 CUDA/cuDNN、操作系统库
- **将模型嵌入镜像**——完全跳过运行时下载
- **现有的 Runpod 无服务器工作器**——您已经有一个可工作的镜像

权衡：`image=` 模式 **不能运行任意 Python**（镜像拥有所有逻辑），并且镜像必须实现 Runpod 无服务器处理程序。完整列表 + 示例：https://docs.runpod.io/flash/custom-docker-images

## 易错点

1. **仅函数体发送到工作器**——最常见的错误。将导入 *以及* 函数使用的任何模块级常量/辅助函数 *放在装饰的体内*。`flash deploy` 导入整个模块，因此模块全局变量碰巧工作；`flash dev` 仅发送函数体，因此模块级名称会引发 `NameError`。一个在部署时工作的处理程序可能在开发时中断——通过将所有内容移入体内来修复。
2. **忘记 await**——所有装饰函数和客户端方法都需要 `await`。
3. **缺少依赖项**——必须在 `dependencies=[]` 中列出。
4. **gpu/cpu 是互斥的**——每个端点选择一个。
5. **idle_timeout 是秒**——默认 60 秒，不是分钟。
6. **10MB 负载限制**——传递 URL，而不是大型对象。返回二进制（音频/图像/文件）作为 base64 嵌入 JSON (`{"audio_b64": ...}`)，并在客户端解码；对于较大的输出，写入 NetworkVolume 或上传到存储并返回 URL。
7. **客户端与装饰器**——`image=`/`id=` = 客户端。否则 = 装饰器。
8. **自动 GPU 切换需要工作器 >= 5**——传递 GPU 类型列表（例如 `gpu=[GpuGroup.ADA_24, GpuGroup.AMPERE_80]`）并设置 `workers=5` 或更高。平台仅在最大工作器至少为 5 时，根据供应自动切换 GPU 类型。
9. **`runsync` 超时为 60 秒**——冷启动可能超过 60 秒。对于首次请求使用 `ep.runsync(data, timeout=120)`，或使用 `ep.run()` + `job.wait()` 替代。
10. **请求主体形状（仅原始/外部 HTTP 调用者）**——匹配请求形状与端点类型：
    - **LB 路由** (`@api.post(...)`): 在顶层发送处理程序参数——`{"data": {...}}`。
    - **QB 端点**（裸 `@Endpoint`，通过 `.../run` 或 `.../runsync` 访问）：工作器调用 **`handler(**job_input)`**，因此请求的 `input` 键必须匹配处理程序的参数名——`def transcribe(input_data: dict)` 需要 `{"input": {"input_data": {...}}}`，并且 `def read(input: dict)` 需要 `{"input": {"input": {...}}}`。不匹配会以 `got an unexpected keyword argument …` 失败。如果处理程序忽略负载，请使用 `**kwargs`。
    - **永远不要发送空的 `input`。** 带有 `{"input": {}}` 的 QB 请求会被工作器 SDK 拒绝，因为 `Job has missing field(s): id or input`——始终至少包含一个键。
    - *上下文*：Flash 客户端 (`ep.runsync(x)`, `api.post(...)`) 隐藏了传播，因此这仅影响原始 HTTP/外部调用者（不匹配行为通过工作器日志在 2026-07-10 验证）。参见 *自主开发循环*。
11. **每个工作器加载一次模型（而不是每次调用）**——对于真实推理，使用 `@Endpoint` 类，其 `__init__` 每个工作器加载一次模型（参见 [reference/patterns.md → 加载 ML 模型](reference/patterns.md#loading-ml-models-warm-workers)）。在函数形式中，通过在体内缓存模块全局（如 #1 所述）来协调，以便在 `flash dev` 和 `deploy` 下都起作用：
    ```python
    global _MODEL
    try: _MODEL
    except NameError: _MODEL = load_model()   # 每个工作器运行一次，跨调用重用
    ```
12. **原生 CUDA 库也放在 `dependencies=[]` 中**——例如 CTranslate2/faster-whisper 需要 `nvidia-cublas-cu12` + `nvidia-cudnn-cu12`，否则会静默回退到 CPU。将它们与 Python 包一起添加。
13. **静默 401 认证失败**——设置 `RUNPOD_API_KEY` 环境变量会覆盖 `flash login` 令牌，因此错误的/过期的密钥会生效。失败是安静的：资源分配日志记录 `GraphQL request failed: 401`，但 `flash dev` 仍然打印其正常的就绪行（“failed endpoints deploy on-demand”），因此看起来健康。当端点无法资源分配时：
    1. 检查资源分配日志中的 `GraphQL request failed: 401`。
    2. 独立验证当前密钥：`curl -s -o /dev/null -w '%{http_code}' https://rest.runpod.io/v1/endpoints -H "Authorization: Bearer $RUNPOD_API_KEY"`（200 = 良好，401 = 错误）。
    3. 修复它：`unset RUNPOD_API_KEY` 以回退到 `flash login` 令牌，或 `export` 一个有效密钥。
14. **`system_dependencies=` 增加冷启动**——apt 包（例如 `["ffmpeg", "espeak-ng"]`）在工作器上安装，以便在首次使用前使用，因此初始调用速度较慢（在模型下载之上）；热调用不受影响。
15. **使用 `flash app delete <app>` 拆卸已发布的应用程序**——`flash undeploy list` 可能显示已发布并正在服务的应用程序为“无端点”；`flash app delete`（或 `runpodctl serverless delete <id>`）可靠地删除它。

## 资源

- 设置 & CLI：[reference/setup-and-cli.md](reference/setup-and-cli.md) · API & 计算枚举：[reference/api.md](reference/api.md) · 模式：[reference/patterns.md](reference/patterns.md)
- Flash 源：https://github.com/runpod/flash
- 可运行示例：https://github.com/runpod/flash-examples — 克隆并修改最接近的一个
- 包（PyPI）：https://pypi.org/project/runpod-flash/
- 文档：https://docs.runpod.io/flash/overview
  - 自定义 Docker 镜像（何时 + 如何）：https://docs.runpod.io/flash/custom-docker-images
  - 存储 / 网络卷：https://docs.runpod.io/flash/configuration/storage
