# 在 Hugging Face Jobs 上进行视觉模型训练

在管理的云端 GPU 上训练目标检测、图像分类和 SAM/SAM2 分割模型。无需本地 GPU 设置——结果将自动保存到 Hugging Face Hub。

## 何时使用此技能

当用户想要执行以下操作时，请使用此技能：
- 在云端 GPU 或本地微调目标检测模型（D-FINE、RT-DETR v2、DETR、YOLOS）
- 在云端 GPU 或本地微调图像分类模型（timm：MobileNetV3、MobileViT、ResNet、ViT/DINOv3 或任何 Transformer 分类器）
- 使用 bbox 或点提示微调 SAM 或 SAM2 模型进行分割/图像抠图
- 在自定义数据集上训练边界框检测器
- 在自定义数据集上训练图像分类器
- 在自定义掩码数据集上训练分割模型（带提示）
- 在 Hugging Face Jobs 基础设施上运行视觉训练作业
- 确保训练的视觉模型永久保存到 Hub

## 相关技能

- **`hugging-face-jobs`** — 一般的 HF Jobs 基础设施：令牌认证、硬件风味、超时管理、成本估算、密钥、环境变量、计划作业和结果持久化。**对于任何非训练特定的 Jobs 问题，请参考 Jobs 技能**（例如，“密钥如何工作？”、“有哪些可用的硬件？”、“如何传递令牌？”）。
- **`hugging-face-model-trainer`** — 基于 TRL 的语言模型训练（SFT、DPO、GRPO）。对于文本/语言模型微调，请使用该技能。

## 本地脚本执行

辅助脚本使用 PEP 723 内联依赖项。使用 `uv run` 运行它们：
```bash
uv run scripts/dataset_inspector.py --dataset username/dataset-name --split train
uv run scripts/estimate_cost.py --help
```

## 前提条件清单

在开始任何训练作业之前，请验证：

### 账户与认证
- Hugging Face 账户具有 [Pro](https://hf.co/pro)、[Team](https://hf.co/enterprise) 或 [Enterprise](https://hf.co/enterprise) 计划（Jobs 需要付费计划）
- 经过认证的登录：使用 `hf_whoami()`（工具）或 `hf auth whoami`（终端）检查
- 令牌具有 **写入** 权限
- **必须在作业密钥中传递令牌**——有关语法，请参阅下方的指令 #3（MCP 工具与 Python API）

### 数据集要求——目标检测
- 数据集必须存在于 Hub 上
- 注释必须使用 `objects` 列，带有 `bbox`、`category`（以及可选的 `area`）子字段
- Bboxes 可以是 **xywh (COCO)** 或 **xyxy (Pascal VOC)** 格式——自动检测并转换
- 类别可以是 **整数或字符串**——字符串将自动映射到整数 ID
- `image_id` 列是 **可选的**——如果缺失，将自动生成
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 数据集要求——图像分类
- 数据集必须存在于 Hub 上
- 必须有一个 **`image` 列**（PIL 图像）和一个 **`label` 列**（整数类 ID 或字符串）
- 标签列可以是 `ClassLabel` 类型（带有名称）或普通的整数/字符串——字符串将自动映射
- 常见列名自动检测：`label`、`labels`、`class`、`fine_label`
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 数据集要求——SAM/SAM2 分割
- 数据集必须存在于 Hub 上
- 必须有一个 **`image` 列**（PIL 图像）和一个 **`mask` 列**（二进制真实分割掩码）
- 必须有一个 **提示**——要么：
  - 一个包含 `{"bbox": [x0,y0,x1,y1]}` 或 `{"point": [x,y]}` 的 JSON 的 **`prompt` 列**
  - 或者一个专用的 **`bbox`** 列，包含 `[x0,y0,x1,y1]` 值
  - 或者一个专用的 **`point`** 列，包含 `[x,y]` 或 `[[x,y],...]` 值
- Bboxes 应该是 **xyxy** 格式（绝对像素坐标）
- 示例数据集：`merve/MicroMat-mini`（使用 bbox 提示的图像抠图）
- **始终在 GPU 训练之前验证未知数据集**（见数据集验证部分）

### 关键设置
- **超时必须超过预期训练时间**——默认 30 分钟太短。有关推荐值，请参阅指令 #6。
- **必须启用 Hub 推送**——`push_to_hub=True`，`hub_model_id="username/model-name"`，令牌在 `secrets` 中

## 数据集验证

**在启动 GPU 训练之前验证数据集格式，以防止训练失败的常见原因：格式不匹配。**

**始终验证**未知/自定义数据集或您之前未使用过的任何数据集。**对于** `cppe-5`（训练脚本中的默认值）**跳过**。

### 运行检查器

**选项 1：通过 HF Jobs（推荐——避免本地 SSL/依赖问题）：**
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

目标检测训练脚本（`scripts/object_detection_training.py`）自动处理 bbox 格式检测（xyxy→xywh 转换）、bbox 清理、`image_id` 生成、字符串类别→整数重新映射和数据集截断。**无需手动预处理**——只需确保数据集具有 `objects.bbox` 和 `objects.category` 列。

## 训练工作流

复制此清单并跟踪进度：

```
Training Progress:
- [ ] 步骤 1：验证前提条件（账户、令牌、数据集）
- [ ] 步骤 2：验证数据集格式（运行 dataset_inspector.py）
- [ ] 步骤 3：询问用户关于数据集大小和验证分割
- [ ] 步骤 4：准备训练脚本（OD：scripts/object_detection_training.py，IC：scripts/image_classification_training.py，SAM：scripts/sam_segmentation_training.py）
- [ ] 步骤 5：将脚本保存在本地，提交作业，并报告详细信息
```

**步骤 1：验证前提条件**

遵循上方的前提条件清单。

**步骤 2：验证数据集**

在花费 GPU 时间之前运行数据集检查器。见上方的“数据集验证”部分。

**步骤 3：询问用户偏好**

**始终**使用带选项格式的 AskUserQuestion 工具：

```python
AskUserQuestion({
    "questions": [
        {
            "question": "您想在运行完整数据集之前先使用数据子集进行快速测试吗？",
            "header": "数据集大小",
            "options": [
                {"label": "快速测试运行（10% 的数据）", "description": "更快、更便宜（~30-60 分钟，~$2-5）以验证设置"},
                {"label": "完整数据集（推荐）", "description": "进行完整训练以获得最佳模型质量"}
            ],
            "multiSelect": false
        },
        {
            "question": "您想从训练数据中创建一个验证分割吗？",
            "header": "分割数据",
            "options": [
                {"label": "是（推荐）", "description": "自动分割 15% 的训练数据用于验证"},
                {"label": "否", "description": "使用数据集现有的验证分割"}
            ],
            "multiSelect": false
        },
        {
            "question": "您想使用哪种 GPU 硬件？",
            "header": "硬件风味",
            "options": [
                {"label": "t4-small ($0.40/小时)", "description": "1x T4，16 GB VRAM——足以支持所有参数少于 100M 的 OD 模型"},
                {"label": "l4x1 ($0.80/小时)", "description": "1x L4，24 GB VRAM——为大型图像或批处理大小提供更多空间"},
                {"label": "a10g-large ($1.50/小时)", "description": "1x A10G，24 GB VRAM——训练更快，CPU/RAM 更多"},
                {"label": "a100-large ($2.50/小时)", "description": "1x A100，80 GB VRAM——最快，适用于非常大的数据集或图像大小"}
            ],
            "multiSelect": false
        }
    ]
})
```

**步骤 4：准备训练脚本**

对于目标检测，使用 [scripts/object_detection_training.py](scripts/object_detection_training.py) 作为生产就绪模板。对于图像分类，使用 [scripts/image_classification_training.py](scripts/image_classification_training.py)。对于 SAM/SAM2 分割，使用 [scripts/sam_segmentation_training.py](scripts/sam_segmentation_training.py)。所有脚本都使用 `HfArgumentParser`——所有配置都通过 CLI 参数（`script_args`）传递，而不是通过编辑 Python 变量。有关 timm 模型详情，请参阅 [references/timm_trainer.md](references/timm_trainer.md)。有关 SAM2 训练详情，请参阅 [references/finetune_sam2_trainer.md](references/finetune_sam2_trainer.md)。

**步骤 5：保存脚本，提交作业，并报告**

1. **将脚本保存在本地**到工作区根目录下的 `submitted_jobs/`（如果需要则创建）中，并使用描述性名称，例如 `training_<dataset>_<YYYYMMDD_HHMMSS>.py`。告诉用户路径。
2. **提交**使用 `hf_jobs` MCP 工具（首选）或 `HfApi().run_uv_job()`——有关两种方法的详细信息，请参阅指令 #1。通过 `script_args` 传递所有配置。
3. **报告**作业 ID（来自 `.id` 属性）、监控 URL、Trackio 仪表板（`https://huggingface.co/spaces/{username}/trackio`）、预期时间和估计成本。
4. **等待用户**请求状态检查——不要自动轮询。训练作业异步运行，可能需要数小时。

## 关键指令

这些规则可防止常见错误。请严格按照这些规则执行。

### 1. 作业提交：`hf_jobs` MCP 工具与 Python API

**`hf_jobs()` 是一个 MCP 工具，而不是 Python 函数。** 不要尝试从 `huggingface_hub` 导入它。将其作为工具调用：

```
hf_jobs("uv", {"script": training_script_content, "flavor": "a10g-large", "timeout": "4h", "secrets": {"HF_TOKEN": "$HF_TOKEN"}})
```

**如果 `hf_jobs` MCP 工具不可用**，则直接使用 Python API：

```python
from huggingface_hub import HfApi, get_token
api = HfApi()
job_info = api.run_uv_job(
    script="path/to/training_script.py",  # 文件路径，不是内容
    script_args=["--dataset_name", "cppe-5", ...],
    flavor="a10g-large",
    timeout=14400,  # 秒（4 小时）
    env={"PYTHONUNBUFFERED": "1"},
    secrets={"HF_TOKEN": get_token()},  # 必须使用 get_token()，而不是 "$HF_TOKEN"
)
print(f"Job ID: {job_info.id}")
```

**两种方法之间的关键区别：**

| | `hf_jobs` MCP 工具 | `HfApi().run_uv_job()` |
|---|---|---|
| `script` 参数 | Python 代码字符串或 URL（不是本地路径） | 文件路径到 `.py` 文件（不是内容） |
| 令牌在 secrets 中 | `"$HF_TOKEN"`（自动替换） | `get_token()`（实际令牌值） |
| 超时格式 | 字符串 (`"4h"`) | 秒 (`14400`) |

**两种方法的规则：**
- 训练脚本**必须**包含 PEP 723 内联元数据，其中包含依赖项
- 不要使用 `image` 或 `command` 参数（这些属于 `run_job()`，而不是 `run_uv_job()`）

### 2. 通过作业密钥进行认证 + 显式 hub_token 注入

**作业配置****必须**在密钥中包含令牌——语法取决于提交方法（见上表）。

**训练脚本要求：** Transformers `Trainer` 在 `__init__()` 中调用 `create_repo(token=self.args.hub_token)`，当 `push_to_hub=True` 时。训练脚本**必须**在解析参数后、但在创建 `Trainer` 之前将 `HF_TOKEN` 注入到 `training_args.hub_token`。模板 `scripts/object_detection_training.py` 已经包含此内容：

```python
hf_token = os.environ.get("HF_TOKEN")
if training_args.push_to_hub and not training_args.hub_token:
    if hf_token:
        training_args.hub_token = hf_token
```

如果您编写自定义脚本，您**必须**在 `Trainer(...)` 调用之前注入此令牌。

- 不要在自定义脚本中调用 `login()`，除非要复制 `scripts/object_detection_training.py` 中的完整模式
- 不要依赖隐式令牌解析（`hub_token=None`）——在 Jobs 中不可靠
- 有关完整详细信息，请参阅 `hugging-face-jobs` 技能 → *令牌使用指南*

### 3. JobInfo 属性

使用 `.id` 访问作业标识符（**不要**使用 `.job_id` 或 `.name`——这些不存在）：

```python
job_info = api.run_uv_job(...)  # 或 hf_jobs("uv", {...})
job_id = job_info.id  # 正确的 -- 返回像 "687fb701029421ae5549d998" 这样的字符串
```

### 4. 必要的训练标志和 HfArgumentParser 布尔语法

`scripts/object_detection_training.py` 使用 `HfArgumentParser`——所有配置都通过 `script_args` 传递。布尔参数有两种语法：

- **`bool` 字段**（例如，`push_to_hub`、`do_train`）：作为裸标志（`--push_to_hub`) 或使用 `--no_` 前缀否定（`--no_remove_unused_columns`)
- **`Optional[bool]` 字段**（例如，`greater_is_better`）：必须传递显式值（`--greater_is_better True`）。裸 `--greater_is_better` 会导致 `error: expected one argument`

目标检测的必要标志：

```
--no_remove_unused_columns          # 必须的：保留 image 列以用于 pixel_values
--no_eval_do_concat_batches         # 必须的：图像具有不同数量的目标框
--push_to_hub                       # 必须的：环境是暂时的
--hub_model_id username/model-name
--metric_for_best_model eval_map
--greater_is_better True            # 必须显式传递 "True" (Optional[bool])
--do_train
--do_eval
```

图像分类的必要标志：

```
--no_remove_unused_columns          # 必须的：保留 image 列以用于 pixel_values
--push_to_hub                       # 必须的：环境是暂时的
--hub_model_id username/model-name
--metric_for_best_model eval_accuracy
--greater_is_better True            # 必须显式传递 "True" (Optional[bool])
--do_train
--do_eval
```

SAM/SAM2 分割的必要标志：

```
--remove_unused_columns False       # 必须的：保留 input_boxes/input_points
--push_to_hub                       # 必须的：环境是暂时的
--hub_model_id username/model-name
--do_train
--prompt_type bbox                  # 或 "point"
--dataloader_pin_memory False       # 必须的：避免 pin_memory 问题与自定义 collator
```

### 5. 超时管理

默认 30 分钟对于目标检测来说太短。设置最小 2-4 小时。增加 30% 的缓冲区，用于模型加载、预处理和 Hub 推送。

| 情景 | 超时 |
|------|------|
| 快速测试（100-200 张图像，5-10 个 epoch） | 1h |
| 开发（500-1K 张图像，15-20 个 epoch） | 2-3h |
| 生产（1K-5K 张图像，30 个 epoch） | 4-6h |
| 大数据集（5K+ 张图像） | 6-12h |

### 6. Trackio 监控

Trackio 在对象检测训练脚本中**始终启用**——它调用 `trackio.init()` 和 `trackio.finish()` 自动。无需传递 `--report_to trackio`。项目名称取自 `--output_dir`，运行名称取自 `--run_name`。对于图像分类，在 `TrainingArguments` 中传递 `--report_to trackio`。

仪表板位于：`https://huggingface.co/spaces/{username}/trackio`

## 模型与硬件选择

### 推荐的目标检测模型

| 模型 | 参数 | 用例 |
|-------|--------|----------|
| `ustc-community/dfine-small-coco` | 10.4M | 最佳起点——快速、便宜、SOTA 质量 |
| `PekingU/rtdetr_v2_r18vd` | 20.2M | 轻量级实时检测器 |
| `ustc-community/dfine-large-coco` | 31.4M | 更高的精度，仍然高效 |
| `PekingU/rtdetr_v2_r50vd` | 43M | 强大的实时基线 |
| `ustc-community/dfine-xlarge-obj365` | 63.5M | 最佳精度（在 Objects365 上预训练） |
| `PekingU/rtdetr_v2_r101vd` | 76M | 最大的 RT-DETR v2 变体 |

从 `ustc-community/dfine-small-coco` 开始进行快速迭代。对于更好的精度，请升级到 D-FINE Large 或 RT-DETR v2 R50。

### 推荐的图像分类模型

所有 `timm/` 模型都可以通过 `AutoModelForImageClassification`（加载为 `TimmWrapperForImageClassification`）开箱即用。有关详细信息，请参阅 [references/timm_trainer.md](references/timm_trainer.md)。

| 模型 | 参数 | 用例 |
|-------|--------|----------|
| `timm/mobilenetv3_small_100.lamb_in1k` | 2.5M | 超轻量级——移动/边缘，最快训练 |
| `timm/mobilevit_s.cvnets_in1k` | 5.6M | 移动 Transformer——良好的精度/速度权衡 |
| `timm/resnet50.a1_in1k` | 25.6M | 强大的 CNN 基线——可靠，经过充分研究 |
| `timm/vit_base_patch16_dinov3.lvd1689m` | 86.6M | 最佳精度——DINOv3 自监督 ViT |

从 `timm/mobilenetv3_small_100.lamb_in1k` 开始进行快速迭代。对于更好的精度，请升级到 `timm/resnet50.a1_in1k` 或 `timm/vit_base_patch16_dinov3.lvd1689m`。

### 推荐的 SAM/SAM2 分割模型

| 模型 | 参数 | 用例 |
|-------|--------|----------|
| `facebook/sam2.1-hiera-tiny` | 38.9M | 最快的 SAM2——适用于快速实验 |
| `facebook/sam2.1-hiera-small` | 46.0M | 最佳起点——良好的质量/速度平衡 |
| `facebook/sam2.1-hiera-base-plus` | 80.8M | 更高的容量，适用于复杂的分割 |
| `facebook/sam2.1-hiera-large` | 224.4M | 最佳 SAM2 精度——需要更多 VRAM |
| `facebook/sam-vit-base` | 93.7M | 原始 SAM——ViT-B 主干 |
| `facebook/sam-vit-large` | 312.3M | 原始 SAM——ViT-L 主干 |
| `facebook/sam-vit-huge` | 641.1M | 原始 SAM——ViT-H，最佳 SAM v1 精度 |

从 `facebook/sam2.1-hiera-small` 开始进行快速迭代。SAM2 模型通常比 SAM v1 在相似质量下更高效。默认情况下，仅掩码解码器被训练（视觉和提示编码器被冻结）。

### 硬件推荐

所有推荐的目标检测和图像分类模型参数都少于 100M——**`t4-small`（16 GB VRAM，$0.40/小时）足以支持所有模型。** 图像分类模型通常比目标检测模型更小更快——`t4-small` 甚至可以轻松处理 ViT-Base。对于 `sam2.1-hiera-base-plus` 以上的 SAM2 模型，`t4-small` 足够，因为仅训练掩码解码器。对于 `sam2.1-hiera-large` 或 SAM v1 模型，请使用 `l4x1` 或 `a10g-large`。只有在您因大型批处理大小而出现 OOM 时才升级。首先减少批处理大小，然后再切换硬件。常见的升级路径：`t4-small` → `l4x1` ($0.80/小时，24 GB) → `a10g-large` ($1.50/小时，24 GB)。

有关完整硬件风味列表：请参考 `hugging-face-jobs` 技能。有关成本估算：运行 `scripts/estimate_cost.py`。

## 快速入门——目标检测

下面的 `script_args` 对于两种提交方法都是相同的。有关两种方法之间关键区别的信息，请参阅指令 #1。

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

- `--model_name_or_path` — 推荐的：`"ustc-community/dfine-small-coco"`（见模型表 above）
- `--dataset_name` — Hub 数据集 ID
- `--image_square_size` — 480（快速迭代）或 800（更好的精度）
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — 30 典型的，用于收敛
- `--train_val_split` — 用于验证的训练数据分割比例（默认 0.15），如果数据集缺少验证分割，请设置
- `--max_train_samples` / `--max_eval_samples` — 截断用于快速测试

## 快速入门——图像分类

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

- `--model_name_or_path` — 任何 `timm/` 模型或 Transformers 分类模型（见模型表 above）
- `--dataset_name` — Hub 数据集 ID
- `--image_column_name` — 包含 PIL 图像的列（默认：`"image"`)
- `--label_column_name` — 包含类标签的列（默认：`"label"`)
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — 3-5 典型的，用于分类（比目标检测少）
- `--per_device_train_batch_size` — 16-64（分类模型使用比目标检测模型更少的内存）
- `--train_val_split` — 用于验证的训练数据分割比例（默认 0.15），如果数据集缺少验证分割，请设置
- `--max_train_samples` / `--max_eval_samples` — 截断用于快速测试

## 快速入门——SAM/SAM2 分割

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

- `--model_name_or_path` — SAM 或 SAM2 模型（见模型表 above）；自动检测 SAM 与 SAM2
- `--dataset_name` — Hub 数据集 ID（例如，`merve/MicroMat-mini`）
- `--prompt_type` — `"bbox"` 或 `"point"`——数据集中的提示类型
- `--prompt_column_name` — 包含 JSON 编码提示的列（默认：`"prompt"`)
- `--bbox_column_name` — 专用的 bbox 列（作为 JSON 提示列的替代方案）
- `--point_column_name` — 专用的点列（作为 JSON 提示列的替代方案）
- `--mask_column_name` — 包含真实分割掩码的列（默认：`"mask"`)
- `--hub_model_id` — `"username/model-name"` 用于 Hub 持久化
- `--num_train_epochs` — 20-30 典型的，用于 SAM 微调
- `--per_device_train_batch_size` — 2-4（SAM 模型使用大量内存）
- `--freeze_vision_encoder` / `--freeze_prompt_encoder` — 冻结编码器权重（默认：两者都冻结，仅掩码解码器训练）
- `--train_val_split` — 用于验证的训练数据分割比例（默认 0.1）

## 检查作业状态

**MCP 工具（如果可用）：**
```
hf_jobs("ps")                                   # 列出所有作业
hf_jobs("logs", {"job_id": "your-job-id"})      # 查看日志
hf_jobs("inspect", {"job_id": "your-job-id"})   # 作业详细信息
```

**Python API 降级方案：**
```python
from huggingface_hub import HfApi
api = HfApi()
api.list_jobs()                                  # 列出所有作业
api.get_job_logs(job_id="your-job-id")           # 查看日志
api.get_job(job_id="your-job-id")                # 作业详细信息
```

## 常见失败模式

### OOM（CUDA out of memory）
减少 `per_device_train_batch_size`（尝试 4，然后 2），减少 `IMAGE_SIZE` 或升级硬件。

### 数据集格式错误
首先运行 `scripts/dataset_inspector.py`。训练脚本自动检测 bbox 格式（xyxy→xywh 转换）、bbox 清理、`image_id` 生成、字符串类别→整数重新映射和数据集截断。**无需手动预处理**——只需确保数据集具有 `objects.bbox` 和 `objects.category` 列。

### Hub 推送失败（401）
验证：
(1) 作业密钥中包含令牌（见指令 #2），(2) 脚本设置 `training_args.hub_token` 在创建 `Trainer` 之前，(3) `push_to_hub=True` 已设置，(4) 正确的 `hub_model_id`，(5) 令牌具有写入权限。

### 作业超时
增加超时（见指令 #5 表格），减少 epoch/数据集，或使用带有 `hub_strategy="every_save"` 的检查点策略。

### KeyError: 'test'（缺少测试分割）
对象检测训练脚本会优雅地处理此问题——它会回退到 `validation` 分割。确保您使用的是最新的 `scripts/object_detection_training.py`。

### 单类数据集：“迭代一个 0-d 张量”
`torchmetrics.MeanAveragePrecision` 在只有一个类时返回标量（0-d）张量，用于每个类的指标。模板 `scripts/object_detection_training.py` 会调用 `.unsqueeze(0)` 在这些张量上。确保您使用的是最新的模板。

### 检测性能差（mAP < 0.15）
增加 epoch（30-50），确保 500+ 张图像，检查每个类的 mAP 以平衡类，尝试不同的学习率（1e-5 到 1e-4），增加图像大小。

对于全面的故障排除：见 [references/reliability_principles.md](references/reliability_principles.md)

## 参考文件

- [scripts/object_detection_training.py](scripts/object_detection_training.py) — 生产就绪的目标检测训练脚本
- [scripts/image_classification_training.py](scripts/image_classification_training.py) — 生产就绪的图像分类训练脚本（支持 timm 模型）
- [scripts/sam_segmentation_training.py](scripts/sam_segmentation_training.py) — 生产就绪的 SAM/SAM2 分割训练脚本（bbox & point 提示）
- [scripts/dataset_inspector.py](scripts/dataset_inspector.py) — 验证 OD、分类和 SAM 分割数据集格式
- [scripts/estimate_cost.py](scripts/estimate_cost.py) — 估算任何视觉模型的训练成本（包括 SAM/SAM2）
- [references/object_detection_training_notebook.md](references/object_detection_training_notebook.md) — 目标检测训练工作流、增强策略和训练模式
- [references/image_classification_training_notebook.md](references/image_classification_training_notebook.md) — 图像分类训练工作流，ViT、预处理和评估
- [references/finetune_sam2_trainer.md](references/finetune_sam2_trainer.md) — 使用 MicroMat 数据集的 SAM2 微调演练，DiceCE 损失和 Trainer 集成
- [references/timm_trainer.md](references/timm_trainer.md) — 使用 HF Trainer（TimmWrapper, transforms, 完整示例）
- [references/hub_saving.md](references/hub_saving.md) — 详细的 Hub 持久化指南和验证清单
- [references/reliability_principles.md](references/reliability_principles.md) — 来自生产经验的故障预防原则

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
