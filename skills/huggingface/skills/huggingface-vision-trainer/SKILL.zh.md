---
name: huggingface-vision-trainer
description: 在Hugging Face Jobs云GPU上使用Hugging Face Transformers训练和微调目标检测（D-FINE、RT-DETR v2、DETR、YOLOS）、图像分类（timm模型——MobileNetV3、MobileViT、ResNet、ViT/DINOv3——以及任何Transformer分类器）和SAM/SAM2分割模型。涵盖COCO格式数据集准备、Albumentations数据增强、mAP/mAR评估、准确率指标、SAM分割（带bbox/点提示）、DiceCE损失、硬件选择、成本估算、Trackio监控和Hub持久化。当用户提到训练目标检测、图像分类、SAM、SAM2、分割、图像抠图、DETR、D-FINE、RT-DETR、ViT、timm、MobileNet、ResNet、边界框模型或在Hugging Face Jobs上微调视觉模型时使用。
---

# 在 Hugging Face Jobs 上进行视觉模型训练

在托管的云端 GPU 上训练目标检测、图像分类和 SAM/SAM2 分割模型。无需本地 GPU 设置——结果将自动保存到 Hugging Face Hub。

## 使用此技能的场景

当用户想要执行以下操作时，请使用此技能：
- 在云端 GPU 或本地微调目标检测模型（D-FINE、RT-DETR v2、DETR、YOLOS）
- 在云端 GPU 或本地微调图像分类模型（timm: MobileNetV3、MobileViT、ResNet、ViT/DINOv3 或任何 Transformer 分类器）
- 使用 bbox 或点提示微调 SAM 或 SAM2 模型进行分割/图像抠图
- 在自定义数据集上训练边界框检测器
- 在自定义数据集上训练图像分类器
- 在自定义掩码数据集上使用提示训练分割模型
- 在 Hugging Face Jobs 基础设施上运行视觉训练作业
- 确保训练的视觉模型永久保存到 Hub

## 相关技能

- **`hugging-face-jobs`** — 通用 HF Jobs 基础设施：令牌认证、硬件风味、超时管理、成本估算、密钥、环境变量、计划作业和结果持久化。**请参考 Jobs 技能以解决任何非训练相关的 Jobs 问题**（例如，“密钥如何工作？”、“有哪些硬件可用？”、“如何传递令牌？”）。
- **`hugging-face-model-trainer`** — 基于 TRL 的语言模型训练（SFT、DPO、GRPO）。使用该技能进行文本/语言模型微调。

## 本地脚本执行

辅助脚本使用 PEP 723 内联依赖项。使用 `uv run` 运行它们：
```bash
uv run scripts/dataset_inspector.py --dataset username/dataset-name --split train
uv run scripts/estimate_cost.py --help
```

## 前提条件清单

开始任何训练作业之前，请验证：

### 账户与认证
- Hugging Face 账户具有 [Pro](https://hf.co/pro)、[Team](https://hf.co/enterprise) 或 [Enterprise](https://hf.co/enterprise) 计划（Jobs 需要付费计划）
- 经过认证的登录：使用 `hf_whoami()`（工具）或 `hf auth whoami`（终端）检查
- 令牌具有 **写入** 权限
- **必须在作业密钥中传递令牌** — 有关语法，请参阅下方的指令 #3（MCP 工具与 Python API）

### 数据集要求 — 目标检测
- 数据集必须存在于 Hub 上
- 注释必须使用 `objects` 列，带有 `bbox`、`category`（可选 `area`）子字段
- Bbox 可以是 **xywh (COCO)** 或 **xyxy (Pascal VOC)** 格式 — 自动检测并转换
- 类别可以是 **整数或字符串** — 字符串将自动映射到整数 ID
- `image_id` 列是 **可选的** — 如果缺失，将自动生成
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 数据集要求 — 图像分类
- 数据集必须存在于 Hub 上
- 必须有一个 **`image` 列**（PIL 图像）和一个 **`label` 列**（整数类别 ID 或字符串）
- 标签列可以是 `ClassLabel` 类型（带有名称）或普通整数/字符串 — 字符串将自动映射
- 常见列名自动检测：`label`、`labels`、`class`、`fine_label`
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 数据集要求 — SAM/SAM2 分割
- 数据集必须存在于 Hub 上
- 必须有一个 **`image` 列**（PIL 图像）和一个 **`mask` 列**（二进制真实分割掩码）
- 必须有一个 **提示** — 要么：
  - 一个包含 `{"bbox": [x0,y0,x1,y1]}` 或 `{"point": [x,y]}` 的 JSON 的 **`prompt` 列**
  - 或者一个专用的 **`bbox`** 列，包含 `[x0,y0,x1,y1]` 值
  - 或者一个专用的 **`point`** 列，包含 `[x,y]` 或 `[[x,y],...]` 值
- Bbox 应该是 **xyxy** 格式（绝对像素坐标）
- 示例数据集：`merve/MicroMat-mini`（图像抠图，使用 bbox 提示）
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 关键设置
- **超时必须超过预期训练时间** — 默认 30 分钟太短。有关推荐值，请参阅指令 #6。
- **必须启用 Hub 推送** — `push_to_hub=True`，`hub_model_id="username/model-name"`，令牌在 `secrets` 中

## 数据集验证

**在启动 GPU 训练之前验证数据集格式，以防止最常见的训练失败原因：格式不匹配。**

**始终验证未知/自定义数据集或您之前未使用过的任何数据集。** **对于 `cppe-5`（训练脚本中的默认值）跳过验证。**

### 运行检查器

**选项 1：通过 HF Jobs（推荐 — 避免本地 SSL/依赖问题）：**
```python
hf_jobs("uv", {
    "script": "path/to/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

**选项 2：本地：**
```bash
uv run scripts/dataset_inspector.py --dataset username/dataset-name --split train
```

**选项 3：通过 `HfApi().run_uv_job()`（如果 hf_jobs MCP 不可用）：**
```python
from huggingface_hub import HfApi
api = HfApi()
api.run_uv_job(
    script="scripts/dataset_inspector.py",
    script_args=["--dataset", "username/dataset-name", "--split", "train"],
    flavor="cpu-basic",
    timeout=300,
)
```

### 读取结果

- **`✓ READY`** — 数据集兼容，可直接使用
- **`✗ NEEDS FORMATTING`** — 需要预处理（输出中提供映射代码）

## 自动 Bbox 预处理

目标检测训练脚本（`scripts/object_detection_training.py`）自动处理 bbox 格式检测（xyxy→xywh 转换）、bbox 清理、`image_id` 生成、字符串类别→整数映射和数据集截断。**无需手动预处理** — 只要确保数据集具有 `objects.bbox` 和 `objects.category` 列。

## 训练工作流

复制此清单并跟踪进度：

```
训练进度：
- [ ] 第 1 步：验证前提条件（账户、令牌、数据集）
- [ ] 第 2 步：验证数据集格式（运行 dataset_inspector.py）
- [ ] 第 3 步：询问用户关于数据集大小和验证拆分
- [ ] 第 4 步：准备训练脚本（OD: scripts/object_detection_training.py, IC: scripts/image_classification_training.py, SAM: scripts/sam_segmentation_training.py）
- [ ] 第 5 步：将脚本保存到本地，提交作业，并报告详细信息
```

**第 1 步：验证前提条件**

遵循上述前提条件清单。

**第 2 步：验证数据集**

在花费 GPU 时间之前运行数据集检查器。见“数据集验证”部分。

**第 3 步：询问用户偏好**

**始终使用 AskUserQuestion 工具，并使用选项样式格式：**

```python
AskUserQuestion({
    "questions": [
        {
            "question": "您想在运行完整训练之前先使用数据子集进行快速测试吗？",
            "header": "数据集大小",
            "options": [
                {"label": "快速测试运行（10% 的数据）", "description": "更快、更便宜 (~30-60 分钟，~$2-5) 以验证设置"},
                {"label": "完整数据集（推荐）", "description": "完整训练以获得最佳模型质量"}
            ],
            "multiSelect": false
        },
        {
            "question": "您想从训练数据中创建一个验证拆分吗？",
            "header": "拆分数据",
            "options": [
                {"label": "是（推荐）", "description": "自动拆分 15% 的训练数据用于验证"},
                {"label": "否", "description": "使用数据集现有的验证拆分"}
            ],
            "multiSelect": false
        },
        {
            "question": "您想使用哪种 GPU 硬件？",
            "header": "硬件风味",
            "options": [
                {"label": "t4-small ($0.40/小时)", "description": "1x T4, 16 GB VRAM — 足够用于所有参数少于 100M 的 OD 模型"},
                {"label": "l4x1 ($0.80/小时)", "description": "1x L4, 24 GB VRAM — 为大型图像或批处理大小提供更多空间"},
                {"label": "a10g-large ($1.50/小时)", "description": "1x A10G, 24 GB VRAM — 训练更快，更多 CPU/RAM"},
                {"label": "a100-large ($2.50/小时)", "description": "1x A100, 80 GB VRAM — 最快，适用于非常大的数据集或图像大小"}
            ],
            "multiSelect": false
        }
    ]
})
```

**第 4 步：准备训练脚本**

对于目标检测，使用 [scripts/object_detection_training.py](scripts/object_detection_training.py) 作为生产就绪模板。对于图像分类，使用 [scripts/image_classification_training.py](scripts/image_classification_training.py)。对于 SAM/SAM2 分割，使用 [scripts/sam_segmentation_training.py](scripts/sam_segmentation_training.py)。所有脚本都使用 `HfArgumentParser` — 所有配置都通过 CLI 参数（`script_args`）传递，而不是通过编辑 Python 变量。有关 timm 模型详细信息，请参阅 [references/timm_trainer.md](references/timm_trainer.md)。有关 SAM2 训练详细信息，请参阅 [references/finetune_sam2_trainer.md](references/finetune_sam2_trainer.md)。

**第 5 步：保存脚本、提交作业并报告**

1. **将脚本保存到本地**到工作区根目录下的 `submitted_jobs/`（如果需要则创建）并使用描述性名称，如 `training_<dataset>_<YYYYMMDD_HHMMSS>.py`。告诉用户路径。
2. **提交**使用 `hf_jobs` MCP 工具（首选）或 `HfApi().run_uv_job()` — 有关两种方法，请参阅上表。通过 `script_args` 传递所有配置。
3. **报告**作业 ID（来自 `.id` 属性）、监控 URL、Trackio 仪表板（`https://huggingface.co/spaces/{username}/trackio`）、预期时间和估计成本。
4. **等待用户**请求状态检查 — 不要自动轮询。训练作业异步运行，可能需要数小时。

## 关键指令

这些规则可防止常见错误。请准确遵循。

### 1. 作业提交：`hf_jobs` MCP 工具 vs Python API

**`hf_jobs()` 是一个 MCP 工具，而不是 Python 函数。** 不要尝试从 `huggingface_hub` 导入它。作为工具调用它：

```
hf_jobs("uv", {"script": training_script_content, "flavor": "a10g-large", "timeout": "4h", "secrets": {"HF_TOKEN": "$HF_TOKEN"}})
```

**如果 `hf_jobs` MCP 工具不可用**，直接使用 Python API：

```python
from huggingface_hub import HfApi, get_token
api = HfApi()
job_info = api.run_uv_job(
    script="path/to/training_script.py",  # 文件路径，不是内容
    script_args=["--dataset_name", "cppe-5", ...],
    flavor="a10g-large",
    timeout=14400,  # 秒（4 小时）
    env={"PYTHONUNBUFFERED": "1"},
    secrets={"HF_TOKEN": get_token()},  # 必须使用 get_token()，不是 "$HF_TOKEN"
)
print(f"Job ID: {job_info.id}")
```

**这两种方法之间的关键区别：**

| | `hf_jobs` MCP 工具 | `HfApi().run_uv_job()` |
|---|---|---|
| `script` 参数 | Python 代码字符串或 URL（不是本地路径） | `.py` 文件的文件路径（不是内容） |
| 令牌在密钥中 | `"$HF_TOKEN"`（自动替换） | `get_token()`（实际令牌值） |
| 超时格式 | 字符串（`"4h"`) | 秒（`14400`） |

**两种方法的规则：**
- 训练脚本必须包含 PEP 723 内联元数据，其中包含依赖项
- 不要使用 `image` 或 `command` 参数（它们属于 `run_job()`，而不是 `run_uv_job()`）

### 2. 通过作业密钥 + 显式 hub_token 注入进行认证

**作业配置** 必须在密钥中包含令牌——语法取决于提交方法（见上表）。

**训练脚本要求：** 当 `push_to_hub=True` 时，Transformers `Trainer` 在 `__init__()` 中调用 `create_repo(token=self.args.hub_token)`。训练脚本必须在解析参数后但在创建 `Trainer` 之前将 `HF_TOKEN` 注入到 `training_args.hub_token` 中。模板 `scripts/object_detection_training.py` 已经包含此内容：

```python
hf_token = os.environ.get("HF_TOKEN")
if training_args.push_to_hub and not training_args.hub_token:
    if hf_token:
        training_args.hub_token = hf_token
```

如果您编写自定义脚本，您必须在 `Trainer(...)` 调用之前包含此令牌注入。

- 不要在自定义脚本中调用 `login()`，除非复制 `scripts/object_detection_training.py` 中的完整模式
- 不要依赖隐式令牌解析（`hub_token=None`）——在 Jobs 中不可靠
- 有关完整详细信息，请参阅 `hugging-face-jobs` 技能 → *令牌使用指南*

### 3. JobInfo 属性

使用 `.id`（不是 `.job_id` 或 `.name` — 这些不存在）访问作业标识符：

```python
job_info = api.run_uv_job(...)  # 或 hf_jobs("uv", {...})
job_id = job_info.id  # 正确的 -- 返回字符串，如 "687fb701029421ae5549d998"
```

### 4. 必需的训练标志和 HfArgumentParser 布尔语法

`scripts/object_detection_training.py` 使用 `HfArgumentParser` — 所有配置都通过 `script_args` 传递。布尔参数有两种语法：

- **`bool` 字段**（例如，`push_to_hub`、`do_train`）：作为裸标志使用（`--push_to_hub`）或使用 `--no_` 前缀否定（`--no_remove_unused_columns`）
- **`Optional[bool]` 字段**（例如，`greater_is_better`）：必须传递显式值（`--greater_is_better True`）。裸 `--greater_is_better` 导致 `error: expected one argument`

目标检测所需的标志：

```
--no_remove_unused_columns          # 必须保留图像列以用于 pixel_values
--no_eval_do_concat_batches         # 必须保留图像具有不同数量的目标框
--push_to_hub                       # 必须保留环境是暂时的
--hub_model_id username/model-name
--metric_for_best_model eval_map
--greater_is_better True            # 必须显式传递 "True"（Optional[bool]）
--do_train
--do_eval
```

图像分类所需的标志：

```
--no_remove_unused_columns          # 必须保留图像列以用于 pixel_values
--push_to_hub                       # 必须保留环境是暂时的
--hub_model_id username/model-name
--metric_for_best_model eval_accuracy
--greater_is_better True            # 必须显式传递 "True"（Optional[bool]）
--do_train
--do_eval
```

SAM/SAM2 分割所需的标志：

```
--remove_unused_columns False       # 必须保留 input_boxes/input_points
--push_to_hub                       # 必须保留环境是暂时的
--hub_model_id username/model-name
--do_train
--prompt_type bbox                  # 或 "point"
--dataloader_pin_memory False       # 必须避免 pin_memory 问题与自定义 collator
```

### 5. 超时管理

默认 30 分钟对于目标检测来说太短。设置最小 2-4 小时。增加 30% 的缓冲区以用于模型加载、预处理和 Hub 推送。

| 场景 | 超时 |
|------|-----|
| 快速测试（100-200 张图像，5-10 个 epoch） | 1h |
| 开发（500-1K 张图像，15-20 个 epoch） | 2-3h |
| 生产（1K-5K 张图像，30 个 epoch） | 4-6h |
| 大数据集（5K+ 张图像） | 6-12h |

### 6. Trackio 监控

Trackio 在目标检测训练脚本中**始终启用** — 它调用 `trackio.init()` 和 `trackio.finish()` 自动。无需传递 `--report_to trackio`。项目名称取自 `--output_dir`，运行名称取自 `--run_name`。对于图像分类，在 `TrainingArguments` 中传递 `--report_to trackio`。

仪表板位于：`https://huggingface.co/spaces/{username}/trackio`

## 模型与硬件选择

### 推荐的目标检测模型

| 模型 | 参数 | 用例 |
|------|------|------|
| `ustc-community/dfine-small-coco` | 10.4M | 最佳起点 — 快速、便宜、SOTA 质量 |
| `PekingU/rtdetr_v2_r18vd` | 20.2M | 轻量级实时检测器 |
| `ustc-community/dfine-large-coco` | 31.4M | 更高精度，仍然高效 |
| `PekingU/rtdetr_v2_r50vd` | 43M | 强大的实时基线 |
| `ustc-community/dfine-xlarge-obj365` | 63.5M | 最佳精度（在 Objects365 上预训练） |
| `PekingU/rtdetr_v2_r101vd` | 76M | 最大的 RT-DETR v2 变体 |

从 `ustc-community/dfine-small-coco` 开始进行快速迭代。移至 D-FINE Large 或 RT-DETR v2 R50 以获得更好的精度。

### 推荐的图像分类模型

所有 `timm/` 模型都可以通过 `AutoModelForImageClassification`（作为 `TimmWrapperForImageClassification` 加载）开箱即用。有关详细信息，请参阅 [references/timm_trainer.md](references/timm_trainer.md)。

| 模型 | 参数量 | 应用场景 |
|------|--------|----------|
| `timm/mobilenetv3_small_100.lamb_in1k` | 2.5M | 超轻量级 — 移动/边缘端，训练最快 |
| `timm/mobilevit_s.cvnets_in1k` | 5.6M | 移动端 Transformer — 准确率/速度平衡良好 |
| `timm/resnet50.a1_in1k` | 25.6M | 强大的 CNN 基线 — 可靠，经过充分研究 |
| `timm/vit_base_patch16_dinov3.lvd1689m` | 86.6M | 最佳准确率 — DINOv3 自监督 ViT |

从 `timm/mobilenetv3_small_100.lamb_in1k` 开始快速迭代。然后迁移到 `timm/resnet50.a1_in1k` 或 `timm/vit_base_patch16_dinov3.lvd1689m` 以获得更好的准确率。

### 推荐的 SAM/SAM2 分割模型

| 模型 | 参数量 | 应用场景 |
|-------|--------|----------|
| `facebook/sam2.1-hiera-tiny` | 38.9M | 最快的 SAM2 — 适用于快速实验 |
| `facebook/sam2.1-hiera-small` | 46.0M | 最佳起点 — 良好的质量/速度平衡 |
| `facebook/sam2.1-hiera-base-plus` | 80.8M | 更高的容量，适用于复杂分割 |
| `facebook/sam2.1-hiera-large` | 224.4M | 最佳 SAM2 准确率 — 需要更多 VRAM |
| `facebook/sam-vit-base` | 93.7M | 原始 SAM — ViT-B 主干 |
| `facebook/sam-vit-large` | 312.3M | 原始 SAM — ViT-L 主干 |
| `facebook/sam-vit-huge` | 641.1M | 原始 SAM — ViT-H，最佳 SAM v1 准确率 |

从 `facebook/sam2.1-hiera-small` 开始快速迭代。SAM2 模型在相似质量下通常比 SAM v1 更高效。默认情况下仅训练掩码解码器（视觉和提示编码器被冻结）。

### 硬件推荐

所有推荐的 OD 和 IC 模型参数量均小于 100M — **`t4-small`（16 GB VRAM，$0.40/小时）足以处理所有模型。** 图像分类模型通常比目标检测模型更小、更快 — `t4-small` 甚至可以轻松处理 ViT-Base。对于 `sam2.1-hiera-base-plus` 及以下的 SAM2 模型，`t4-small` 足够，因为仅训练掩码解码器。对于 `sam2.1-hiera-large` 或 SAM v1 模型，使用 `l4x1` 或 `a10g-large`。仅在遇到大型批次导致的 OOM 时才升级硬件 — 在切换硬件之前先减少批次大小。常见的升级路径：`t4-small` → `l4x1`（$0.80/小时，24 GB）→ `a10g-large`（$1.50/小时，24 GB）。

硬件风味列表完整信息：参考 `hugging-face-jobs` 技能。成本估算：运行 `scripts/estimate_cost.py`。

## 快速入门 — 目标检测

下面的 `script_args` 对两种提交方法都相同。请参考指令 #1 了解它们之间的关键差异。

```python
OD_SCRIPT_ARGS = [
    "--model_name_or_path", "ustc-community/dfine-small-coco",
    "--dataset_name", "cppe-5",
    "--image_square_size", "640",
    "--output_dir", "dfine_finetuned",
    "--num_train_epochs", "30",
    "--per_device_train_batch_size", "8",
    "--learning_rate", "5e-5",
    "--eval_strategy", "epoch",
    "--save_strategy", "epoch",
    "--save_total_limit", "2",
    "--load_best_model_at_end",
    "--metric_for_best_model", "eval_map",
    "--greater_is_better", "True",
    "--no_remove_unused_columns",
    "--no_eval_do_concat_batches",
    "--push_to_hub",
    "--hub_model_id", "username/model-name",
    "--do_train",
    "--do_eval",
]
```

```python
from huggingface_hub import HfApi, get_token
api = HfApi()
job_info = api.run_uv_job(
    script="scripts/object_detection_training.py",
    script_args=OD_SCRIPT_ARGS,
    flavor="t4-small",
    timeout=14400,
    env={"PYTHONUNBUFFERED": "1"},
    secrets={"HF_TOKEN": get_token()},
)
print(f"Job ID: {job_info.id}")
```

### 关键 OD `script_args`

- `--model_name_or_path` — 推荐：`"ustc-community/dfine-small-coco"`（见上表模型）
- `--dataset_name` — Hub 数据集 ID
- `--image_square_size` — 480（快速迭代）或 800（更好准确率）
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — 典型收敛次数：30
- `--train_val_split` — 用于验证的分割比例（默认 0.15），如果数据集缺少验证分割则设置
- `--max_train_samples` — 截断训练集（用于快速测试运行，例如 `"785"` 表示 7.8K 数据集的 ~10%）
- `--max_eval_samples` — 截断评估集

## 快速入门 — 图像分类

```python
IC_SCRIPT_ARGS = [
    "--model_name_or_path", "timm/mobilenetv3_small_100.lamb_in1k",
    "--dataset_name", "ethz/food101",
    "--output_dir", "food101_classifier",
    "--num_train_epochs", "5",
    "--per_device_train_batch_size", "32",
    "--per_device_eval_batch_size", "32",
    "--learning_rate", "5e-5",
    "--eval_strategy", "epoch",
    "--save_strategy", "epoch",
    "--save_total_limit", "2",
    "--load_best_model_at_end",
    "--metric_for_best_model", "eval_accuracy",
    "--greater_is_better", "True",
    "--no_remove_unused_columns",
    "--push_to_hub",
    "--hub_model_id", "username/food101-classifier",
    "--do_train",
    "--do_eval",
]
```

```python
from huggingface_hub import HfApi, get_token
api = HfApi()
job_info = api.run_uv_job(
    script="scripts/image_classification_training.py",
    script_args=IC_SCRIPT_ARGS,
    flavor="t4-small",
    timeout=7200,
    env={"PYTHONUNBUFFERED": "1"},
    secrets={"HF_TOKEN": get_token()},
)
print(f"Job ID: {job_info.id}")
```

### 关键 IC `script_args`

- `--model_name_or_path` — 任何 `timm/` 模型或 Transformers 分类模型（见上表模型）
- `--dataset_name` — Hub 数据集 ID
- `--image_column_name` — 包含 PIL 图像的列（默认：`"image"`）
- `--label_column_name` — 包含类别标签的列（默认：`"label"`）
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — 分类典型训练轮数：3-5（少于 OD）
- `--per_device_train_batch_size` — 16-64（分类模型比 OD 使用更少内存）
- `--train_val_split` — 用于验证的分割比例（默认 0.15），如果数据集缺少验证分割则设置
- `--max_train_samples` / `--max_eval_samples` — 截断用于快速测试

## 快速入门 — SAM/SAM2 分割

```python
SAM_SCRIPT_ARGS = [
    "--model_name_or_path", "facebook/sam2.1-hiera-small",
    "--dataset_name", "merve/MicroMat-mini",
    "--prompt_type", "bbox",
    "--prompt_column_name", "prompt",
    "--output_dir", "sam2-finetuned",
    "--num_train_epochs", "30",
    "--per_device_train_batch_size", "4",
    "--learning_rate", "1e-5",
    "--logging_steps", "1",
    "--save_strategy", "epoch",
    "--save_total_limit", "2",
    "--remove_unused_columns", "False",
    "--dataloader_pin_memory", "False",
    "--push_to_hub",
    "--hub_model_id", "username/sam2-finetuned",
    "--do_train",
    "--report_to", "trackio",
]
```

```python
from huggingface_hub import HfApi, get_token
api = HfApi()
job_info = api.run_uv_job(
    script="scripts/sam_segmentation_training.py",
    script_args=SAM_SCRIPT_ARGS,
    flavor="t4-small",
    timeout=7200,
    env={"PYTHONUNBUFFERED": "1"},
    secrets={"HF_TOKEN": get_token()},
)
print(f"Job ID: {job_info.id}")
```

### 关键 SAM `script_args`

- `--model_name_or_path` — SAM 或 SAM2 模型（见上表）；自动检测 SAM vs SAM2
- `--dataset_name` — Hub 数据集 ID（例如：`"merve/MicroMat-mini"`）
- `--prompt_type` — `"bbox"` 或 `"point"` — 数据集中的提示类型
- `--prompt_column_name` — 包含 JSON 编码提示的列（默认：`"prompt"`）
- `--bbox_column_name` — 专用 bbox 列（JSON 提示列的替代方案）
- `--point_column_name` — 专用点列（JSON 提示列的替代方案）
- `--mask_column_name` — 包含真实掩码的列（默认：`"mask"`）
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — SAM 微调典型轮数：20-30
- `--per_device_train_batch_size` — 2-4（SAM 模型使用大量内存）
- `--freeze_vision_encoder` / `--freeze_prompt_encoder` — 冻结编码器权重（默认：两者均冻结，仅掩码解码器训练）
- `--train_val_split` — 用于验证的分割比例（默认 0.1）

## 检查作业状态

**MCP 工具（如果可用）：**
```
hf_jobs("ps")                                   # 列出所有作业
hf_jobs("logs", {"job_id": "your-job-id"})      # 查看日志
hf_jobs("inspect", {"job_id": "your-job-id"})   # 作业详情
```

**Python API 备用方案：**
```python
from huggingface_hub import HfApi
api = HfApi()
api.list_jobs()                                  # 列出所有作业
api.get_job_logs(job_id="your-job-id")           # 查看日志
api.get_job(job_id="your-job-id")                # 作业详情
```

## 常见失败模式

### OOM（CUDA 内存不足）
减少 `per_device_train_batch_size`（尝试 4，然后 2），减少 `IMAGE_SIZE`，或升级硬件。

### 数据集格式错误
首先运行 `scripts/dataset_inspector.py`。训练脚本自动检测 xyxy vs xywh，将字符串类别转换为整数 ID，并在缺失时添加 `image_id`。确保 `objects.bbox` 包含绝对像素值的 4 值坐标列表，`objects.category` 包含整数 ID 或字符串标签。

### Hub 推送失败（401）
验证：(1) 作业密钥包含 token（见指令 #2），(2) 脚本在创建 `Trainer` 之前设置 `training_args.hub_token`，(3) `push_to_hub=True` 被设置，(4) 正确的 `hub_model_id`，(5) token 具有写权限。

### 作业超时
增加超时（见指令 #5 表格），减少轮数/数据集，或使用 `hub_strategy="every_save"` 的检查点策略。

### KeyError: 'test'（缺少测试分割）
目标检测训练脚本会优雅地处理此问题 — 它会回退到 `validation` 分割。确保你使用的是最新的 `scripts/object_detection_training.py`。

### 单类别数据集："iteration over a 0-d tensor"
当只有一个类别时，`torchmetrics.MeanAveragePrecision` 返回标量（0-d）张量，用于每个类别的指标。模板 `scripts/object_detection_training.py` 通过在这些张量上调用 `.unsqueeze(0)` 来处理这种情况。确保你使用的是最新模板。

### 检测性能差（mAP < 0.15）
增加轮数（30-50），确保 500+ 图像，检查不平衡类别的每个类别 mAP，尝试不同的学习率（1e-5 到 1e-4），增加图像大小。

全面故障排除：参考 [references/reliability_principles.md](references/reliability_principles.md)

## 参考文件

- [scripts/object_detection_training.py](scripts/object_detection_training.py) — 生产级目标检测训练脚本
- [scripts/image_classification_training.py](scripts/image_classification_training.py) — 生产级图像分类训练脚本（支持 timm 模型）
- [scripts/sam_segmentation_training.py](scripts/sam_segmentation_training.py) — 生产级 SAM/SAM2 分割训练脚本（bbox & point 提示）
- [scripts/dataset_inspector.py](scripts/dataset_inspector.py) — 验证 OD、分类和 SAM 分割的数据集格式
- [scripts/estimate_cost.py](scripts/estimate_cost.py) — 估算任何视觉模型的训练成本（包括 SAM/SAM2）
- [references/object_detection_training_notebook.md](references/object_detection_training_notebook.md) — 目标检测训练工作流、增强策略和训练模式
- [references/image_classification_training_notebook.md](references/image_classification_training_notebook.md) — ViT、预处理和评估的图像分类训练工作流
- [references/finetune_sam2_trainer.md](references/finetune_sam2_trainer.md) — 使用 MicroMat 数据集、DiceCE 损失和 Trainer 集成的 SAM2 微调演练
- [references/timm_trainer.md](references/timm_trainer.md) — 使用 HF Trainer 的 timm 模型（TimmWrapper、变换、完整示例）
- [references/hub_saving.md](references/hub_saving.md) — 详细的 Hub 持久化指南和验证清单
- [references/reliability_principles.md](references/reliability_principles.md) — 生产经验中的故障预防原则

## 外部链接

- [Transformers 目标检测指南](https://huggingface.co/docs/transformers/tasks/object_detection)
- [Transformers 图像分类指南](https://huggingface.co/docs/transformers/tasks/image_classification)
- [DETR 模型文档](https://huggingface.co/docs/transformers/model_doc/detr)
- [ViT 模型文档](https://huggingface.co/docs/transformers/model_doc/vit)
- [HF Jobs 指南](https://huggingface.co/docs/huggingface_hub/guides/jobs) — 主 Jobs 文档
- [HF Jobs 配置](https://huggingface.co/docs/hub/en/jobs-configuration) — 硬件、密钥、超时、命名空间
- [HF Jobs CLI 参考](https://huggingface.co/docs/huggingface_hub/guides/cli#hf-jobs) — 命令行界面
- [目标检测模型](https://huggingface.co/models?pipeline_tag=object-detection)
- [图像分类模型](https://huggingface.co/models?pipeline_tag=image-classification)
- [SAM2 模型文档](https://huggingface.co/docs/transformers/model_doc/sam2)
- [SAM 模型文档](https://huggingface.co/docs/transformers/model_doc/sam)
- [目标检测数据集](https://huggingface.co/datasets?task_categories=task_categories:object-detection)
- [图像分类数据集](https://huggingface.co/datasets?task_categories=task_categories:image-classification)
