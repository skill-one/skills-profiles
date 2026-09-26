## 文档

- Cog 参考（单个文件）：<https://cog.run/llms.txt>
- `cog.yaml` 参考：<https://cog.run/yaml>
- Python 预测器参考：<https://cog.run/python>
- 示例：<https://github.com/replicate/cog-examples>
- 模板：<https://github.com/replicate/cog-template>

## 何时使用此技能

- 您有模型代码、权重或一个 HuggingFace/GitHub 项目，希望将其托管在 Replicate 上。
- 您正在编写或编辑 `cog.yaml`、`predict.py` 或 `train.py`。
- 要将构建好的模型推送到 Replicate，请参阅 `publish-models`。
- 要运行现有的 Replicate 模型，请参阅 `run-models`。

## 前置条件

- 本地运行 Docker。
- 已安装 Cog：`brew install replicate/tap/cog` 或 `sh <(curl -fsSL https://cog.run/install.sh)`。
- 可选：使用 `cog init` 来创建 `cog.yaml` 和 `predict.py` 的脚手架。

## 项目布局

标准的 Replicate 模型布局：

```
cog.yaml
predict.py
weights.py                 # 可选的下载辅助工具
requirements.txt
cog-safe-push-configs/
  default.yaml             # 参见 publish-models 技能
.github/workflows/
  ci.yaml
script/                    # github.com/github/scripts-to-rule-them-all
  lint
  test
  push
```

## cog.yaml 基础

GPU 模型的现代配置：

```yaml
build:
  gpu: true
  cuda: "12.8"
  python_version: "3.12"
  python_requirements: requirements.txt
  system_packages:
    - libgl1
    - libglib2.0-0
predict: predict.py:Predictor
```

注意：

- 将 Python 固定到特定的小版本，并将 `requirements.txt` 中的每一行都固定。浮点版本会导致冷启动失败。
- 一旦列表增长，使用 `python_requirements` 而不是内联 `python_packages`。
- `cuda` 需要与您的 torch 轮子匹配（例如 `12.8` 与 `torch==2.7.1+cu128` 配对）。
- 如果您的模型是可微调的，请添加 `train: train.py:train`。
- 添加 `image: r8.im/owner/name` 以启用裸 `cog push`。

对于异步预测器与持续批处理：

```yaml
concurrency:
  max: 32
```

## predict.py 基础

```python
from cog import BasePredictor, Input, Path

class Predictor(BasePredictor):
    def setup(self) -> None:
        """一次性加载。重工作在这里，而不是在 predict() 中。"""
        self.model = load_model("weights/")

    def predict(
        self,
        prompt: str = Input(description="用于生成的文本提示"),
        seed: int = Input(description="随机种子；留空为随机", default=None),
        num_steps: int = Input(description="去噪步数", ge=1, le=50, default=20),
        output_format: str = Input(description="输出图像格式", choices=["webp", "jpg", "png"], default="webp"),
    ) -> Path:
        """运行单次预测。"""
        if not prompt.strip():
            raise ValueError("prompt 不能为空")
        out = self.model.generate(prompt, seed=seed, steps=num_steps)
        return Path(out)
```

输入规则：

- 每个输入需要一个 `description`。描述会在模型架构和 Replicate 的 Web UI 中显示。
- 使用 `ge`/`le` 为数字设置边界，`choices=[...]` 为枚举，`regex=` 为字符串。
- 使用 `cog.Path` 处理文件输入和输出，绝不要使用原始字节。
- 使用 `cog.Secret` 处理任何 token 类型的输入（HF token、API 密钥），绝不要使用纯 `str`。
- 为分类输入提供在 `choices` 内的默认值。
- 在 `predict()` 中尽早验证输入并抛出 `ValueError`。

流式文本输出（用于 LLM）：

```python
from cog import BasePredictor, Input, ConcatenateIterator

class Predictor(BasePredictor):
    def predict(self, prompt: str = Input(description="提示")) -> ConcatenateIterator[str]:
        for token in self.model.stream(prompt):
            yield token
```

异步预测器与持续批处理（与 `concurrency.max` 在 cog.yaml 中配对）：

```python
from cog import BasePredictor, Input, AsyncConcatenateIterator

class Predictor(BasePredictor):
    async def setup(self) -> None:
        self.engine = await load_async_engine()

    async def predict(
        self,
        prompt: str = Input(description="提示"),
    ) -> AsyncConcatenateIterator[str]:
        async for token in self.engine.generate(prompt):
            yield token
```

从磁盘资源动态获取 `choices`（例如一个包含音频样本的 `voices/` 目录）：

```python
from pathlib import Path as _P
AVAILABLE_VOICES = sorted(p.stem for p in _P("voices").glob("*.wav"))

class Predictor(BasePredictor):
    def predict(
        self,
        speaker: str = Input(description="声音", choices=AVAILABLE_VOICES, default=AVAILABLE_VOICES[0]),
    ) -> Path: ...
```

## 快速加载权重

冷启动会主导用户感知的延迟。三种模式，按简单性排序：

### 1. 在构建时将权重嵌入到镜像中

适用于小或中等权重（< 5GB），希望零冷启动。

对于 torchvision：

```python
import os
os.environ["TORCH_HOME"] = "."  # 在导入 torch 之前设置
import torch
from torchvision import models
```

对于 HuggingFace：

```python
import os
os.environ["HF_HUB_CACHE"] = "./.cache"
os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
```

然后在 `cog build` 期间下载一次（例如在 `run:` 步骤中，或通过运行一个小型 fetcher 脚本作为构建的一部分）。权重成为镜像层的一部分。

### 2. 使用 pget 从 `weights.replicate.delivery` 拉取

适用于大权重，或希望跨多个模型共享权重。`pget` 是 Replicate 的并行 HTTP 获取器。

在 `cog.yaml` 中：

```yaml
build:
  run:
    - curl -o /usr/local/bin/pget -L "https://github.com/replicate/pget/releases/download/v0.8.2/pget_linux_x86_64"
    - chmod +x /usr/local/bin/pget
```

在 `setup()` 中：

```python
import subprocess
from pathlib import Path

WEIGHTS_URL = "https://weights.replicate.delivery/default/my-model/weights.tar"
WEIGHTS_DIR = Path("weights")

class Predictor(BasePredictor):
    def setup(self) -> None:
        if not WEIGHTS_DIR.exists():
            # -x 在内存中解压 tar；默认并发为 4 * NumCPU
            subprocess.check_call(["pget", "-x", WEIGHTS_URL, str(WEIGHTS_DIR)])
        self.model = load_from(WEIGHTS_DIR)
```

一次性获取多个文件：

```python
manifest = "\n".join([
    f"{base}/unet.safetensors weights/unet.safetensors",
    f"{base}/vae.safetensors  weights/vae.safetensors",
    f"{base}/text_encoder.safetensors weights/text_encoder.safetensors",
])
subprocess.run(["pget", "multifile", "-"], input=manifest, text=True, check=True)
```

### 3. HuggingFace Hub 使用 hf_transfer

设置 `HF_HUB_ENABLE_HF_TRANSFER=1` 并使用 `huggingface_hub.snapshot_download` 或 `from_pretrained`。比普通的 HF 下载更快。使用 `cog.Secret` 输入来处理受保护的模型。

## 用户提供的权重缓存

对于 LoRAs 或用户在预测时传递的任何权重 URL，使用 sha256 键化的磁盘缓存并带有 LRU 删除：

```python
import hashlib, shutil, subprocess
from pathlib import Path

class WeightsDownloadCache:
    def __init__(self, cache_dir: str = "/tmp/weights-cache", min_disk_free_gb: int = 10):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_disk_free = min_disk_free_gb * 1024**3

    def ensure(self, url: str) -> Path:
        key = hashlib.sha256(url.encode()).hexdigest()
        target = self.cache_dir / key
        if target.exists():
            target.touch()  # 增加 LRU mtime
            return target
        self._evict_until_room()
        subprocess.check_call(["pget", url, str(target)])
        return target

    def _evict_until_room(self) -> None:
        while shutil.disk_usage(self.cache_dir).free < self.min_disk_free:
            entries = sorted(self.cache_dir.iterdir(), key=lambda p: p.stat().st_mtime)
            if not entries:
                return
            entries[0].unlink()
```

参考 `replicate/cog-flux/weights.py` 以获取处理 HF、CivitAI、Replicate 和任意 `.safetensors` URL 的生产版本。

## 多 LoRA 组合

仅当 URL 变化时才重新加载；使用不同的比例组合两个 LoRAs：

```python
class Predictor(BasePredictor):
    def setup(self) -> None:
        self.pipe = load_base_pipeline()
        self.loaded = {"main": None, "extra": None}

    def _ensure_lora(self, slot: str, url: str | None) -> None:
        if url == self.loaded[slot]:
            return
        if self.loaded[slot] is not None:
            self.pipe.unload_lora_weights(adapter_name=slot)
        if url:
            path = self.cache.ensure(url)
            self.pipe.load_lora_weights(str(path), adapter_name=slot)
        self.loaded[slot] = url

    def predict(
        self,
        prompt: str = Input(description="提示"),
        lora_url: str = Input(description="主要 LoRA URL", default=None),
        lora_scale: float = Input(description="主要 LoRA 比例", ge=0.0, le=2.0, default=1.0),
        extra_lora_url: str = Input(description="可选的第二个 LoRA URL", default=None),
        extra_lora_scale: float = Input(description="第二个 LoRA 比例", ge=0.0, le=2.0, default=1.0),
    ) -> Path:
        self._ensure_lora("main", lora_url)
        self._ensure_lora("extra", extra_lora_url)
        adapters = [s for s, u in self.loaded.items() if u]
        scales = [lora_scale if s == "main" else extra_lora_scale for s in adapters]
        if adapters:
            self.pipe.set_adapters(adapters, adapter_weights=scales)
        return Path(self.pipe(prompt).images[0].save("/tmp/out.png"))
```

## 冷启动技巧

从生产扩散模型如 `replicate/cog-flux` 和 `replicate/cog-flux-kontext`：

- 在 `setup()` 中一次性设置性能标志：
  ```python
  import torch
  torch.set_float32_matmul_precision("high")
  torch.backends.cuda.matmul.allow_tf32 = True
  torch.backends.cudnn.benchmark = True
  ```
- 编译并预热：
  ```python
  self.model = torch.compile(self.model, dynamic=True)
  _ = self.predict(prompt="warmup", num_steps=1)  # 在 setup 中吸收编译成本
  ```
- 使用元设备 + `assign=True` 加载大权重以避免双重分配：
  ```python
  with torch.device("meta"):
      model = build_model_skeleton()
  state = torch.load("weights.pt", map_location="cpu")
  model.load_state_dict(state, assign=True)
  ```
- 跨多个管道（例如基础 + img2img + inpaint）共享 VAE / 文本编码器，而不是加载三个副本。
- 对于 fp8/int8，提前保存量化权重并直接加载；不要在启动时量化。

## 本地开发

```
cog init                                    # 创建 cog.yaml + predict.py 的脚手架
cog predict -i prompt="hello"               # 构建 + 运行单次预测
cog predict -i image=@input.jpg -o out.png  # 文件输入和输出
cog serve -p 8393                           # 匹配生产的 HTTP 服务器
cog exec python                             # 在构建环境中交互式 shell
```

## 构建

```
cog build -t my-model
cog build --separate-weights -t my-model    # 权重在单独的镜像层中
cog build --secret id=hf,src=$HOME/.hf_token -t my-model
```

技巧：

- 对于任何权重 > ~1GB 的模型，使用 `--separate-weights`。它加快了冷启动和注册推送。
- 在 `run:` 步骤中使用 `--mount=type=cache,target=/root/.cache/pip` 以跨构建缓存 pip。
- 使用 `--secret` 而不是 `ARG` 以防止 token 进入镜像历史。
- 默认的 Cog 基础镜像（`--use-cog-base-image=true`）比自建更快。

## 训练

如果您的模型支持微调，请在 `cog.yaml` 中添加 `train: train.py:train` 并编写一个返回 `TrainingOutput(weights=Path("model.tar"))` 的 `train()` 函数。然后预测器会通过 `setup(self, weights)` 或 `COG_WEIGHTS` 环境变量接受 URL。参考 <https://cog.run/training> 和 `replicate/flux-fine-tuner` 获取完整示例。

## 指南

- 将 `setup()` 用于一次性加载；保持 `predict()` 快速且形状确定性。
- 固定 Python 和所有依赖项。如果您的 torch 较旧，使用 `numpy<2`。
- 描述每个输入。没有描述的架构在 Web UI 上无法使用。
- 使用 `cog.Path` 处理文件和 `cog.Secret` 处理 token。
- 将 `pget` 固定到特定版本（`v0.8.2`）以实现可重复性。
- 每次调用 HuggingFace Hub 时设置 `HF_HUB_ENABLE_HF_TRANSFER=1`。
- 权重加载后设置 `TRANSFORMERS_OFFLINE=1` 以防止运行时 HF 查找。
- 在推送前使用 `cog predict` 进行测试。如果本地无法工作，生产中也不会工作。

## 生产参考

- <https://github.com/replicate/cog-examples> — 最小模式（resnet、hello-world、流式、训练）
- <https://github.com/replicate/cog-template> — 新模型库的脚手架
- <https://github.com/replicate/cog-flux> — 多变体 FLUX 模型、权重缓存、fp8 + torch.compile
- <https://github.com/replicate/cog-flux-kontext> — 元设备加载、预热编译
- <https://github.com/replicate/cog-vllm> — 异步 LLM 服务器带持续批处理、训练作为打包
- <https://github.com/replicate/cog-comfyui> — ComfyUI 工作流作为 Cog 模型、自定义节点辅助
- <https://github.com/replicate/flux-fine-tuner> — 多 LoRA 组合、共享管道组件
- <https://github.com/replicate/vibevoice> — 动态 `choices` 的 TTS、最小的 cog.yaml
- <https://github.com/replicate/pget> — 并行权重获取器
