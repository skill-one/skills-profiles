# 深度网络单目

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 Metric Depth Anything v2 或 Relative Depth Anything 架构进行单目深度估计。从单个 RGB 图像中预测每个像素的深度。

预训练检查点加载因模型变体和使用案例而异——请参阅 `references/parameters.md` 中的 **预训练检查点加载——使用案例矩阵**。

单目和立体技能都在容器内调用统一的 TAO `depth_net` CLI；单目/立体系列通过 `model.model_type` 选择（见 `references/parameters.md`）。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`, TensorRT `evaluate` 和 TensorRT `inference`), 首先阅读 `references/tao-deploy-depth-anything-v2.md`。部署规范模板位于此技能的 `references/spec_template_deploy.yaml` 中。

此模型技能打包的 PyT 操作：`train`, `evaluate`, `inference`, `export` 和 `quantize`。当前的 TAO 图像中 PyT `depth_net` 入口点不接受 PyT 端的 `gen_trt_engine` 操作。`gen_trt_engine` 操作元数据必须在 TAO Deploy 容器中运行，部署工作流保持为部署特定的入口点。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 的短语视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认将训练操作通过 `tao-skill-bank:tao-run-automl` 路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖，包括数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在模式生成之前报告此模型启用 AutoML 但不可运行。

非训练操作（如 `evaluate`, `inference`, `export` 和部署流程）保持在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 工作流

### 前置条件——数据可访问性

您的数据集（RGB 图像 + GT 深度文件）必须可以从容器内部访问：
- **SDK 运行器**：将文件放置在运行器解析的 S3 路径（**典型规范覆盖**中显示的 `S3_TRAIN` / `S3_EVAL` 占位符）。运行器透明地处理 S3 → 容器路径挂载。
- **直接 `docker run`**（例如本地测试）：将主机数据集根以只读方式挂载到相同的容器路径：

```
docker run ... -v <host_data_root>:<host_data_root>:ro <container> ...
```

所有操作写入的 `<output_dir>` 也适用相同的可访问性要求。

### 第 1 步——标注文件

由 `data_sources[*].data_file` 引用的每行标注文件：

| 列 | 格式 | 用途 |
|---|---|---|
| 1 | `<image>` | 单目推理（无 GT） |
| 2 | `<image> <gt_depth>` | 单目带 GT |

不要将立体标注行（如 `<left_image> <right_image> <gt_depth>`）直接传递给单目训练/评估/推理。如果只有立体深度数据集可用，则通过保留左图像和 GT 深度列来派生单目标注文件，然后将图像/深度存档挂载或暂存到与该派生标注文件引用的相同容器路径。

如果您已经有了，请指向它。否则通过 `depth_net convert` 生成：

```
depth_net convert -e <convert_spec.yaml>
```

`convert_spec.yaml` 模板：

```yaml
results_dir: <生成的标注文件写入的目录>
data_root: <其直接子级包含您的图像+深度文件的目录；convert 递归遍历 data_root，但期望在下一级有一个场景/样本子目录>
image_dir_pattern: [<匹配左/RGB 图像路径的子字符串>]
depth_dir_pattern: [<匹配 GT 深度路径的子字符串>]
image_extension: ''     # 可选 .endswith 过滤器，例如 '.jpg'
depth_extension: ''     # 可选，在深度派生期间交换，例如 '.png'
split_ratio: 0.0        # 0.0/1.0 = 仅测试；0.8 = 80/20 训练+验证
```

`convert` 递归遍历 `data_root`，选择路径的路径字符串包含 `image_dir_pattern` 中的所有子字符串（AND 过滤器），然后通过将 `image_dir_pattern[0]` 替换为 `depth_dir_pattern[0]` 并将 `image_extension` 替换为 `depth_extension` 来派生深度路径。检查您的数据集的目录布局并识别区分 RGB 图像和深度文件的子字符串（例如 `rgb_` vs `sync_depth_`）。

`data_root` 必须指向包含每个场景子目录的父目录（例如，对于 NYU 评估，使用 `/data/nyu_v2/eval/test`，而不是 `/data/nyu_v2/eval/test/bathroom`——后者将遍历限制为单个场景）。始终在 `image_extension` / `depth_extension` 中包含点（例如 `'.jpg'` 而不是 `'jpg'`）；子字符串交换对格式敏感，不匹配会静默损坏派生路径。

### 第 2 步——根据您的数据匹配 `model_type` 和 `dataset_name`

默认——每个任务的通用类别：

| 数据类别 | `model_type` | `dataset_name` |
|---|---|---|
| 差分编码数据（像素） | `RelativeDepthAnything` | `RelativeMonoDataset` |
| 比例深度（米） | `MetricDepthAnything` | `MetricMonoDataset` |
| 单目推理（无 GT，任何图像） | 匹配训练选择 | `RelativeMonoDataset` 或 `MetricMonoDataset` |

数据集特定类别——当数据需要通用类别未执行的预处理时切换：

| 特殊案例 | `model_type` | `dataset_name` | 类别添加的内容 |
|---|---|---|---|
| NYU `sync_depth_*.png`（原始 uint16 毫米）——相对 | `RelativeDepthAnything` | `NYUDV2Relative` | mm→m 单位转换 + Eigen 评估裁剪 |
| NYU `sync_depth_*.png`（原始 uint16 毫米）——比例 | `MetricDepthAnything` | `NYUDV2` | 相同 |

在需要单位转换的数据（例如原始 NYU uint16 PNG）上使用通用类别会导致空的有效掩码和静默 `train_loss = NaN`。将类别与您数据编码匹配。

对于相对单目数据 (`RelativeMonoDataset` 或 `NYUDV2Relative`)，将 `dataset.min_depth` 和 `dataset.max_depth` 不设置或都设置为 `null`。非空的度量深度范围传递给相对数据集构造函数并失败，因为 `BaseRelativeMonoDataset.__init__()` 获得了意外的关键字参数 'min_depth'。

### 第 3 步——从典型规范覆盖编写 spec yaml

从 **典型规范覆盖** (`references/spec-overrides.md`) 中复制操作块。替换：
- 第 2 步中的 `model.model_type`
- 第 2 步中的 `dataset.<...>.data_sources[*].dataset_name`
- 用第 1 步的路径替换 `data_sources[*].data_file`（SDK 运行器下的 S3 路径，直接 docker 的主机路径）
- 对于度量微调：另外应用 `references/finetuning-recipes.md` 中的 **度量变体微调配方**。

对于单目训练，设置 `train.precision: fp32`（推荐）或 `bf16`（Ampere SM80+，替代）。

### 第 4 步——运行

在使用 `--user` 之前，在挂载的输出路径内创建可写入的 home/cache 目录。一些 TAO 容器没有主机 UID 的 `/etc/passwd` 条目，并且当以该 UID 运行时，PyTorch / matplotlib 需要可写入的缓存路径。

```bash
mkdir -p <output_dir>/home \
         <output_dir>/.cache/matplotlib \
         <output_dir>/.cache/torchinductor \
         <output_dir>/.cache/xdg
```

```
docker run --gpus 'device=0' --shm-size 16G --shm-size=8g \
  --user "$(id -u):$(id -g)" \
  -e USER="$(id -un)" \
  -e LOGNAME="$(id -un)" \
  -e HOME=<output_dir>/home \
  -e MPLCONFIGDIR=<output_dir>/.cache/matplotlib \
  -e TORCHINDUCTOR_CACHE_DIR=<output_dir>/.cache/torchinductor \
  -e XDG_CACHE_HOME=<output_dir>/.cache/xdg \
  -v <data_root>:<data_root>:ro \
  -v <output_dir>:<output_dir> \
  <container> \
  depth_net <action> -e <spec.yaml>
```

没有 `--user "$(id -u):$(id -g)"`，容器将输出作为 `nobody:nogroup`，这将阻止主机端清理和重试。

### 第 5 步——验证

- 容器退出代码 0
- `status.json` `kpi` 块填充
- 对于 `train`：直接检查每步 `train_loss`——入口点即使 `train_loss = NaN` 也会报告 `Execution status: PASS`（见度量变体微调配方→Sanity-run PASS 标准 in `references/finetuning-recipes.md`）
- 对于 `evaluate` / `inference`：`results_dir` 下的工件

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`, TensorRT `evaluate` 和 TensorRT `inference`), 首先阅读 `references/tao-deploy-depth-anything-v2.md`。部署规范模板位于此技能的 `references/` 文件夹中，前缀为 `spec_template_deploy_*.yaml`。

## 训练要求

- **单目 `data_sources` 的有效 `dataset_name` 值**（不区分大小写）：`ThreeDVLM`, `FSD`, `NvCLIP`, `IssacStereo`, `Crestereo`, `Middlebury`, `NYUDV2`, `NYUDV2Relative`, `RelativeMonoDataset`, `MetricMonoDataset`。`NYUDV2` 携带度量深度 GT（米）——与 `MetricDepthAnything` 配对；`NYUDV2Relative` 是相同的数据，但使用相对深度约定——与 `RelativeDepthAnything` 配对。
- **监控指标**：`val/d1`（最大化），`val/loss`（最小化）。
- **AutoML 指标契约**：对于打包的相对深度冒烟数据的 AutoML 意图运行，使用 `val/d1` 作为主要监控并最大化它。单目 `d1` 是 Delta-1 准确率：有效像素中 `max(pred/target, target/pred) < 1.25` 的比例。不要将立体 `d1` 错误率方向应用于此单目指标。`val/loss` 即使训练器成功退出并写入可用检查点也可能发出 `NaN`，因此除非运行的状态指标显示有限值，否则它不是可靠的 AutoML 目标。
- **单目 AutoML 搜索允许列表**：对于默认的相对深度训练工作流，使用 `train.optim.lr` 和 `train.optim.weight_decay`。不要搜索 `dataset.val_dataset`、`dataset.test_dataset` 或 `dataset.infer_dataset` 增强字段，因为它们改变评分/非训练行为，而不是训练。不要搜索 `model.corr_radius`、`model.cv_group` 或 `model.volume_dim` 对于单目；这些字段属于立体架构，并且对 `RelativeDepthAnything` 无效。

### 每个操作的 数据集 要求

| 操作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_dataset.data_sources | eval_dataset | data_file: annotations.txt + dataset_name | 是 |
| inference | dataset.infer_dataset.data_sources | inference_dataset | data_file: annotations.txt + dataset_name | 是 |
| quantize | dataset.train_dataset.data_sources | train_datasets | data_file: annotations.txt + dataset_name | 是 |
| quantize | dataset.val_dataset.data_sources | eval_dataset | data_file: annotations.txt + dataset_name | 是 |
| quantize | dataset.quant_calibration_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.train_dataset.data_sources | train_datasets | data_file: annotations.txt + dataset_name | 是 |
| train | dataset.val_dataset.data_sources | eval_dataset | data_file: annotations.txt + dataset_name | 是 |

### 典型规范覆盖

数据源覆盖对于每个操作都是**强制性的**——根据上表中的每操作数据集要求构建数据源路径，并将它们包含在 `spec_overrides` 中。每个 `data_sources` 条目是一个字典，具有**两个强制字段**：`data_file` 和 `dataset_name`。有关完整的每操作覆盖块（`train`、`evaluate`、`export`、`inference`、`quantize`）、`S3_TRAIN` / `S3_EVAL` 占位符、相对变体精度建议和 `quantize` 已知问题说明，请参阅 `references/spec-overrides.md`。

## 评估数据集

可选。通过 `dataset.val_dataset.data_sources` 配置的验证数据集（每个条目需要 `data_file` 和 `dataset_name`）。

## 重要参数

有关完整参数词汇表（模型、训练、数据集、导出和推理键及其选项、默认值和来源）和 **预训练检查点加载——使用案例矩阵**，请参阅 `references/parameters.md`。

## 微调配方

有关以下内容，请参阅 `references/finetuning-recipes.md`：
- **相对变体微调配方**——从 TAO 训练的 `RelativeDepthAnything` 检查点微调（lr `5e-6`、`LambdaLR`、意图与收敛指导、部署 LSQ 对齐说明）。
- **度量变体微调配方**——检查点兼容性、所需覆盖、训练和导出规范中所需的 `normalize_depth`/`min_depth`/`max_depth` 数据集规范化块、训练器强制默认值、精度、1-epoch 意图运行覆盖，以及 NaN 缓解顺序的 Sanity-run PASS 标准。

## 多 GPU / 多节点

**启动方法**：Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| Spec Key | 描述 | 默认 |
|----------|-------------|---------|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |
| `train.num_nodes` | 节点数量 | 1 |
| `train.distributed_strategy` | `ddp` 或 `fsdp` | `ddp` |

- `ddp` 带激活检查点：`find_unused_parameters=False`
- `ddp` 无：`find_unused_parameters=True`
- `fsdp` 强制精度为 FP16

**多节点环境变量**（由编排器设置）：`WORLD_SIZE`、`NODE_RANK`、`MASTER_ADDR`、`MASTER_PORT`、`NUM_GPU_PER_NODE`。

## 导出 / TRT 默认值

- TRT 数据类型：FP32、BF16（Ampere SM80+）。FP16 不支持 ViT-L 单目主干。
- 新安装 TRT 精度：`fp32`。BF16 在 Ampere SM80+ 硬件上受支持，但除非用户明确请求 BF16，否则保持冒烟测试在 FP32 上。

## 硬件

至少 1 GPU(s)，推荐 2 GPU(s)。每个 GPU 24GB+ VRAM。ViT-Large 编码器内存密集。使用 `fp32`（推荐）或 `bf16`（Ampere SM80+，替代）进行训练。激活检查点可用于更大的输入。

## 错误模式

有关完整错误模式目录（深度范围不匹配、相对数据集拒绝 `min_depth`、缺失预训练权重、`encoder` 键位置、`dataset_name` 不在结构中、`depth_net_mono` 未找到、度量变体超参数来源、导出 ONNX 覆盖）请参阅 `references/troubleshooting.md`。

## Spec Param / 父模型推理

有关模型特定推理映射（TAO Core `depth_net_mono.config.json` 操作表）、`<results_dir>/train/` 下的检查点文件命名、`dn_model_latest.pth` 策略、父 `gen_trt_engine` 理由以及 `parent_model` / `parent_job_id` 解析规则，请参阅 `references/spec-param-inference.md`。

## 部署

- [tao-deploy-depth-anything-v2](references/tao-deploy-depth-anything-v2.md)
