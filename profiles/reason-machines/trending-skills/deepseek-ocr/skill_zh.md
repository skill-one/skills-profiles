# DeepSeek-OCR

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

DeepSeek-OCR 是一种用于光学字符识别（OCR）的视觉语言模型，具有“上下文光学压缩”功能。它支持原生和动态分辨率，多种提示模式（文档转Markdown、自由OCR、图表解析、基础定位），可以通过 vLLM（高吞吐量）或 HuggingFace Transformers 运行。它可以处理图像和PDF文件，输出结构化文本或Markdown格式。

---

## 安装

### 前置条件
- CUDA 11.8+，PyTorch 2.6.0
- Python 3.12.9（推荐通过conda安装）

### 设置

```bash
git clone https://github.com/deepseek-ai/DeepSeek-OCR.git
cd DeepSeek-OCR

conda create -n deepseek-ocr python=3.12.9 -y
conda activate deepseek-ocr

# 使用CUDA 11.8安装PyTorch
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
  --index-url https://download.pytorch.org/whl/cu118

# 从 https://github.com/vllm-project/vllm/releases/tag/v0.8.5 下载vllm-0.8.5 whl
pip install vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl

pip install -r requirements.txt
pip install flash-attn==2.7.3 --no-build-isolation
```

### 备选方案：上游vLLM（夜间版）

```bash
uv venv
source .venv/bin/activate
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

---

## 模型下载

模型可在HuggingFace上获取：`deepseek-ai/DeepSeek-OCR`

```python
from huggingface_hub import snapshot_download
snapshot_download(repo_id="deepseek-ai/DeepSeek-OCR")
```

---

## 推理：vLLM（推荐用于生产）

### 单图像 — 流式传输

```python
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

image = Image.open("document.png").convert("RGB")
prompt = "<image>\n自由OCR."

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,
        window_size=90,
        whitelist_token_ids={128821, 128822},  # <td>, </td> 用于表格支持
    ),
    skip_special_tokens=False,
)

outputs = llm.generate(
    [{"prompt": prompt, "multi_modal_data": {"image": image}}],
    sampling_params
)

print(outputs[0].outputs[0].text)
```

### 批量图像

```python
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

image_paths = ["page1.png", "page2.png", "page3.png"]
prompt = "<image>\n<|grounding|>将文档转换为Markdown. "

model_input = [
    {
        "prompt": prompt,
        "multi_modal_data": {"image": Image.open(p).convert("RGB")}
    }
    for p in image_paths
]

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,
        window_size=90,
        whitelist_token_ids={128821, 128822},
    ),
    skip_special_tokens=False,
)

outputs = llm.generate(model_input, sampling_params)

for path, output in zip(image_paths, outputs):
    print(f"=== {path} ===")
    print(output.outputs[0].text)
```

### PDF处理（通过vLLM脚本）

```bash
cd DeepSeek-OCR-master/DeepSeek-OCR-vllm
# 编辑config.py：设置INPUT_PATH, OUTPUT_PATH, 模型路径等
python run_dpsk_ocr_pdf.py   # 在A100-40G上约2500 tokens/s
```

### 基准评估

```bash
cd DeepSeek-OCR-master/DeepSeek-OCR-vllm
python run_dpsk_ocr_eval_batch.py
```

---

## 推理：HuggingFace Transformers

```python
import os
import torch
from transformers import AutoModel, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

model_name = "deepseek-ai/DeepSeek-OCR"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation="flash_attention_2",
    trust_remote_code=True,
    use_safetensors=True,
)
model = model.eval().cuda().to(torch.bfloat16)

# 文档转Markdown
res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>将文档转换为Markdown. ",
    image_file="document.jpg",
    output_path="./output/",
    base_size=1024,
    image_size=640,
    crop_mode=True,
    save_results=True,
    test_compress=True,
)
print(res)
```

### Transformers脚本

```bash
cd DeepSeek-OCR-master/DeepSeek-OCR-hf
python run_dpsk_ocr.py
```

---

## 提示参考

| 用例 | 提示 |
|---|---|
| 文档 → Markdown | `<image>\n<|grounding|>将文档转换为Markdown. ` |
| 一般OCR | `<image>\n<|grounding|>OCR此图像. ` |
| 自由OCR（无布局） | `<image>\n自由OCR. ` |
| 解析图表/图像 | `<image>\n解析此图表. ` |
| 一般描述 | `<image>\n详细描述此图像. ` |
| 基础定位REC | `<image>\n定位 <\|ref\|>TARGET_TEXT<\|/ref\|> 在图像中. ` |

```python
PROMPTS = {
    "document_markdown": "<image>\n<|grounding|>将文档转换为Markdown. ",
    "ocr_image":         "<image>\n<|grounding|>OCR此图像. ",
    "free_ocr":          "<image>\n自由OCR. ",
    "parse_figure":      "<image>\n解析此图表. ",
    "describe":          "<image>\n详细描述此图像. ",
    "rec":               "<image>\n定位 <|ref|>{target}<|/ref|> 在图像中. ",
}
```

---

## 支持的分辨率

| 模式 | 分辨率 | 视觉Token |
|---|---|---|
| Tiny | 512×512 | 64 |
| Small | 640×640 | 100 |
| Base | 1024×1024 | 256 |
| Large | 1280×1280 | 400 |
| Gundam（动态） | n×640×640 + 1×1024×1024 | 可变 |

```python
# Transformers: 通过infer()参数控制分辨率
res = model.infer(
    tokenizer,
    prompt=prompt,
    image_file="image.jpg",
    base_size=1024,   # 512, 640, 1024, 或 1280
    image_size=640,   # 动态模式下的patch大小
    crop_mode=True,   # True = Gundam动态分辨率
)
```

---

## 配置（vLLM）

编辑 `DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py`:

```python
# 关键配置字段（示例）
MODEL_PATH = "deepseek-ai/DeepSeek-OCR"   # 或本地路径
INPUT_PATH = "/data/input_images/"
OUTPUT_PATH = "/data/output/"
TENSOR_PARALLEL_SIZE = 1                   # 用于张量并行的GPU数量
MAX_TOKENS = 8192
TEMPERATURE = 0.0
NGRAM_SIZE = 30
WINDOW_SIZE = 90
```

---

## 常见模式

### 处理图像目录

```python
import os
from pathlib import Path
from PIL import Image
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor

def batch_ocr(image_dir: str, output_dir: str, prompt: str = "<image>\n自由OCR."):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    llm = LLM(
        model="deepseek-ai/DeepSeek-OCR",
        enable_prefix_caching=False,
        mm_processor_cache_gb=0,
        logits_processors=[NGramPerReqLogitsProcessor],
    )
    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=8192,
        extra_args=dict(ngram_size=30, window_size=90, whitelist_token_ids={128821, 128822}),
        skip_special_tokens=False,
    )
    
    image_files = list(Path(image_dir).glob("*.png")) + list(Path(image_dir).glob("*.jpg"))
    
    inputs = [
        {"prompt": prompt, "multi_modal_data": {"image": Image.open(f).convert("RGB")}}
        for f in image_files
    ]
    
    outputs = llm.generate(inputs, sampling_params)
    
    for img_path, output in zip(image_files, outputs):
        out_file = Path(output_dir) / (img_path.stem + ".txt")
        out_file.write_text(output.outputs[0].text)
        print(f"保存：{out_file}")

batch_ocr("/data/scans/", "/data/results/")
```

### 将PDF页面转换为Markdown

```python
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor

def pdf_to_markdown(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    llm = LLM(
        model="deepseek-ai/DeepSeek-OCR",
        enable_prefix_caching=False,
        mm_processor_cache_gb=0,
        logits_processors=[NGramPerReqLogitsProcessor],
    )
    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=8192,
        extra_args=dict(ngram_size=30, window_size=90, whitelist_token_ids={128821, 128822}),
        skip_special_tokens=False,
    )
    
    prompt = "<image>\n<|grounding|>将文档转换为Markdown. "
    inputs = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
        inputs.append({"prompt": prompt, "multi_modal_data": {"image": img}})
    
    outputs = llm.generate(inputs, sampling_params)
    return [o.outputs[0].text for o in outputs]

pages = pdf_to_markdown("report.pdf")
full_markdown = "\n\n---\n\n".join(pages)
print(full_markdown)
```

### 基础定位REC

```python
import torch
from transformers import AutoModel, AutoTokenizer

model_name = "deepseek-ai/DeepSeek-OCR"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation="flash_attention_2",
    trust_remote_code=True,
    use_safetensors=True,
).eval().cuda().to(torch.bfloat16)

target = "总金额"
prompt = f"<image>\n定位 <|ref|>{target}<|/ref|> 在图像中. "

res = model.infer(
    tokenizer,
    prompt=prompt,
    image_file="invoice.jpg",
    output_path="./output/",
    base_size=1024,
    image_size=640,
    crop_mode=False,
    save_results=True,
)
print(res)  # 返回边界框/位置信息
```

---

## 故障排除

### `transformers` 版本与vLLM冲突
vLLM 0.8.5 需要 `transformers>=4.51.1` — 如果在同一环境中运行两者，此错误可安全忽略，根据项目文档。

### Flash Attention构建错误
```bash
# 确保在安装flash-attn前安装torch
pip install flash-attn==2.7.3 --no-build-isolation
```

### CUDA内存不足
- 使用较小分辨率：`base_size=512` 或 `base_size=640`
- 禁用 `crop_mode=False` 以避免多裁剪动态分辨率
- 减少vLLM输入的批处理大小

### 模型输出乱码/重复
确保传递 `NGramPerReqLogitsProcessor` 给 `LLM` — 这对于正确解码是必需的：
```python
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
llm = LLM(..., logits_processors=[NGramPerReqLogitsProcessor])
```

### 表格渲染不正确
将表格Token ID添加到白名单：
```python
whitelist_token_ids={128821, 128822}  # <td> 和 </td>
```

### 多GPU推理
```python
llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    tensor_parallel_size=4,  # GPU数量
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor],
)
```

---

## 关键文件

```
DeepSeek-OCR-master/
├── DeepSeek-OCR-vllm/
│   ├── config.py                  # vLLM配置
│   ├── run_dpsk_ocr_image.py      # 单图像推理
│   ├── run_dpsk_ocr_pdf.py        # PDF批量推理
│   └── run_dpsk_ocr_eval_batch.py # 基准评估
└── DeepSeek-OCR-hf/
    └── run_dpsk_ocr.py            # HuggingFace Transformers推理
```
