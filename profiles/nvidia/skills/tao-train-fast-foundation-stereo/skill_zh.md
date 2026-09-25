# 深度网络快速立体

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 **FastFoundationStereo (FFS)** 进行实时立体深度估计 — 这是 FoundationStereo 的 bp2 商业提取变体。从校正的立体图像对中预测视差图，并使用每层剪枝宽度进行实时推理。

单目 / 立体 / 快速立体技能共享统一的 TAO `depth_net` CLI；FFS 通过 `model.model_type: FastFoundationStereo` 进行选择。FFS 与 `FoundationStereo` 的区别仅在于剪枝的每层宽度和一个序列化的前向路径；其余所有内容（入口点、动作动词、数据集类、部署链）与 `depth-net-stereo` 完全相同。

对于 TAO 部署 TensorRT 动作（`gen_trt_engine`、TensorRT `evaluate`、TensorRT `inference`），请先阅读 `references/tao-deploy-fast-foundation-stereo.md`。部署规范模板位于 `references/spec_template_deploy.yaml`。

## 使用场景

使用此技能对 TAO FastFoundationStereo 模型进行训练、评估、导出或运行推理。支持两种使用案例：

FFS 原始部署和 bp2-finetune 流程需要一个预训练的 bp2 商业检查点（`model_best_bp2_serialize.pth`）。默认的 PyT 图像不保证此文件存在于磁盘上，因此将检查点路径视为必需的用户/注册工件。如果没有 bp2 检查点可用，从头开始训练仍然可用于工作流验证，但生成的指标不能代表 bp2 模型。

1. **原始部署** — 直接使用 bp2 检查点。跳过 `train`；直接使用 bp2 文件作为动作的检查点运行 `inference` / `evaluate` / `export` / `gen_trt_engine`。
2. **在用户数据上进行微调** — 将 `train.pretrained_model_path` 设置为 bp2 文件，在用户数据上进行训练，然后验证并部署生成的检查点。支持完整的 7 动作序列（train → evaluate pyt → inference pyt → export → gen_trt_engine → inference deploy → evaluate deploy）。

## 训练动作策略

此模型在模型层具有 AutoML 功能。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的 workflow 请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将类似于“关闭 AutoML”、“禁用 AutoML”、“无 HPO”或“纯训练”的短语视为 `automl_policy: off`，仅针对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认将训练动作通过 `tao-skill-bank:tao-run-automl` 路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖，包括数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时才使用直接模型训练；在缺失模式的案例中，报告此模型启用 AutoML 但不可运行，直到模式生成。

FFS 共享 `depth_net_stereo` 模式，但其 bp2 架构宽度是固定的不变量。对于默认 AutoML，除非用户明确请求更宽的搜索范围，否则仅搜索 `train.optim.lr` 和 `train.optim.lr_decay`。不要将 FFS 架构字段（如 `model.volume_dim`、`model.hidden_dims` 或其他 bp2 宽度设置）包含在默认搜索空间中。
非训练动作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每次运行的 `automl_policy` 覆盖不会更改模型元数据。

## 工作流

### 前提条件 — 数据可访问性

您的数据集（用于训练/评估的左 + 右图像 + GT 视差，用于推理的左 + 右图像）必须可以从容器内部访问：
- **SDK 运行器**：将文件放置在运行器解析的 S3 路径（spec 覆盖中显示的 `S3_TRAIN` / `S3_EVAL` 占位符）。
- **直接 `docker run`**（例如本地测试）：将主机数据集根以只读方式挂载到相同的容器路径：

```
docker run ... -v <host_data_root>:<host_data_root>:ro <container> ...
```

相同的可访问性要求适用于所有动作写入的 `<output_dir>` 以及 bp2 检查点路径。

### 第 1 步 — 注释文件

由 `data_sources[*].data_file` 引用的每行注释文件。模式与 `depth-net-stereo` 相同：

| 列 | 格式 | 用途 |
|---|---|---|
| 2 | `<left> <right>` | 立体推理（无 GT） |
| 3 | `<left> <right> <disparity>` | 立体带 GT |
| 4 | `<left> <right> <disparity> <occlusion_mask>` | 立体带 GT 和遮挡掩码 |

如有需要，通过 `depth_net convert` 生成；有关 `convert_spec.yaml` 模板，请参阅 `depth-net-stereo` 技能。

### 第 2 步 — 根据您的数据匹配 `model_type` 和 `dataset_name`

使用 `model_type: FastFoundationStereo` 进行 FFS。`dataset_name` 的选择与立体技能类似 — 如果您的布局匹配注册的特定数据集类，请选择该类，否则选择 `GenericDataset`。

| 数据类别 | `model_type` | `dataset_name` |
|---|---|---|
| Middlebury | `FastFoundationStereo` | `Middlebury` |
| KITTI | `FastFoundationStereo` | `Kitti` |
| ETH3D | `FastFoundationStereo` | `Eth3d` |
| FSD 合成 | `FastFoundationStereo` | `FSD` |
| IsaacReal 合成 | `FastFoundationStereo` | `IsaacRealDataset` |
| Crestereo 合成 | `FastFoundationStereo` | `Crestereo` |
| 其他 / 非规范 | `FastFoundationStereo` | `GenericDataset` |

对于使用 2 列注释（左 + 右，无 GT）进行推理的情况，无论布局如何，都使用 `dataset_name: GenericDataset`。

### 第 3 步 — 设置 bp2 提取宽度覆盖

FFS 需要 15 个模型部分宽度覆盖字段，其值必须与 bp2 商业检查点完全匹配。省略任何字段都会回退到 TAO 默认值，这些默认值**不**与 bp2 检查点匹配，并在前向时间产生形状不匹配错误。有关完整的“按原样复制” `model:` 块和注释，请参阅 `references/setup-and-run.md`。`references/spec_template_*.yaml` 中的规范模板包含此块作为规范来源。

### 第 4 步 — 从规范覆盖写入规范 YAML

复制 `references/spec-overrides.md` 中的动作块。替换：
- `model.model_type: FastFoundationStereo`（已设置）
- `dataset.<...>.data_sources[*].dataset_name` 从第 2 步获取
- `dataset.<...>.data_sources[*].data_file` 使用第 1 步的路径
- 对于原始部署用例（无训练）：将 `<action>.checkpoint` 设置为 bp2 文件路径
- 对于微调用例：将 `train.pretrained_model_path` 设置为 bp2 文件路径

有关链式训练 → 下一个动作检查点路径解析和形状一致性说明，请参阅 `references/setup-and-run.md`。SDK 运行器部署通过 `parent_job_id` 自动解析传递 — 请参阅 `references/parent-model-inference.md`。

### 第 5 步 — 运行

在挂载的输出路径内部创建可写的 home/cache 目录，然后使用 `--user` 启动 `docker run ... depth_net <action> -e <spec.yaml>`。有关完整的 `mkdir` + `docker run` 命令、`--user` 理由以及本地绑定挂载 `__pycache__` 小贴士，请参阅 `references/setup-and-run.md`。

### 第 6 步 — 验证

检查容器退出码 0 和填充的 `status.json` `kpi` 块。对于 `train`，直接检查每步 `train_loss`（即使损失是 NaN，入口点也会报告 `Execution status: PASS`）；对于 `evaluate`，依赖 `epe` / `bp1` / `bp2` / `bp3` / `d1` / `rmse`；对于 `inference`，检查 `results_dir` 下的工件。pyt-`deploy` KPI 命名空间差异和预期部署漂移在 `references/setup-and-run.md` 中详细说明。

### 7 动作部署流程

```
train (可选)            → 微调检查点
evaluate (pyt)              → PyT 紧急 EPE / bp 在验证 GT 上
inference (pyt)             → PyT 紧急视差样本（视觉检查）
export                      → 静态 fp32 ONNX（推荐 480×736 或 320×736）
gen_trt_engine             → 静态 ONNX 路径上的 fp16 TRT 引擎
inference (deploy)         → TRT 视差样本
evaluate (deploy)          → TRT EPE / bp 漂移与 PyT 紧急 fp32
```

对于原始 bp2 部署，跳过 `train`。其余 6 个动作（或从 `export` 开始的 4 个部署动词）涵盖两种用例。

## 训练要求

- **立体 `data_sources` 的有效 `dataset_name` 值**（不区分大小写）：`FSD`、`IsaacRealDataset`、`Crestereo`、`Middlebury`、`Eth3d`、`Kitti`、`GenericDataset`
- **监控指标**：val/loss

### 每个动作的数据集要求

| 动作 | Spec Key | 来源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_dataset.data_sources | eval_dataset | data_file: annotations.txt + dataset_name | 是 |
| inference | dataset.infer_dataset.data_sources | inference_dataset | data_file: annotations.txt + dataset_name | 是 |
| train | dataset.train_dataset.data_sources | train_datasets | data_file: annotations.txt + dataset_name | 是 |
| train | dataset.val_dataset.data_sources | eval_dataset | data_file: annotations.txt + dataset_name | 是 |

### 典型规范覆盖

数据源覆盖对于每个动作都是**必需的**。每个 `data_sources` 条目是一个包含**两个必需字段**的字典：`data_file` 和 `dataset_name`。`model.*` 宽度字段也是必需的 — 请参阅第 3 步。有关 `FFS_MODEL_BLOCK` 和每个动作（train / evaluate / inference / export）的 Python 覆盖字典，请参阅 `references/spec-overrides.md`。

## 评估数据集

可选。通过 `dataset.val_dataset.data_sources` 配置的验证数据集（每个条目都需要 `data_file` 和 `dataset_name`）。

## 重要参数

关键旋钮包括 `model.model_type`（`FastFoundationStereo`）、`model.encoder`（`vitl`）、`model.max_disparity`（显式设置 `192` — 模式默认 `416` 导致严重漂移）、`model.mixed_precision`（`false`）、`model.gwc_feature_normalize`（`true`）、`model.volume_dim`（`28`）、`model.valid_iters`（`8`）以及每个分片的 `batch_size` / `workers` / `crop_size` / `data_sources`。完整参数参考、评估指标、多 GPU / 多节点规范键、导出 / TRT 默认值、导出用例矩阵以及硬件指南在 `references/important-parameters.md` 中。

## 错误模式

对于 `shape mismatch`、`gwc_feature_normalize` 模式错误、`max_disparity` 漂移、负视差、`depth_net_stereo: not found`、pyt-`evaluate` `crop_size` 不对称、`Failed to import SAM3` 警告以及动态引擎步长不兼容的静默失败，请参阅 `references/error-patterns.md`。

## 规范参数 / 父模型推理

训练 / 评估 / 推理 / 导出 / gen_trt_engine 的模型特定推理映射（每个动作规范字段 → 推理函数），以及 `parent_job_id` / `parent_model` 解析和原始 bp2 显式检查点处理，在 `references/parent-model-inference.md` 中。生成的运行器应阅读该部分并使用 SDK 辅助程序在 `create_job()` 之前应用这些映射。

## 部署

- [tao-deploy-fast-foundation-stereo](references/tao-deploy-fast-foundation-stereo.md)
