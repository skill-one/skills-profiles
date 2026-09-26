# 光学检测

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 Siamese 网络进行光学检测以发现缺陷。比较图像对以检测制造缺陷、异常或质量问题。

设置 `train.pretrained_model_path` 以指定预训练的 Siamese 权重。

对于 TAO Deploy TensorRT 操作 (`gen_trt_engine`, TensorRT `evaluate` 和 TensorRT `inference`)，请先阅读 `references/tao-deploy-optical-inspection.md`。父 PyT 容器不暴露 `optical_inspection gen_trt_engine`；TensorRT 引擎生成仅用于部署。部署规范模板位于此技能的 `references/` 文件夹中，以 `spec_template_deploy_*.yaml` 为前缀。

## 数据类模式

生成的 TAO Core 模式打包在 `schemas/<action>.schema.json` 中，`schemas/manifest.json` 列出可用操作。每个生成的模式还会从模式顶层 `default` 字段发出 `references/spec_template_<action>.yaml`。AutoML 启用声明在模型层 `references/skill_info.yaml` 中通过 `automl_enabled` 进行。可运行 AutoML 需要存在并解析 `schemas/<action>.schema.json` 和 `references/spec_template_<action>.yaml`。使用打包的选定操作模式进行 `automl_default_parameters`、`automl_disabled_parameters`、默认值、最小/最大边界、枚举、选项权重、数学条件、依赖项和常用参数。不要期望运行时存在 `~/tao-core`；维护者在打包技能库之前会重新生成模式/模板。

## 训练操作策略

此模型在模型层启用 AutoML。在处理任何训练阶段请求之前，请读取 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的流程请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将短语如 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 视为仅对此运行 `automl_policy: off`。当 `automl_policy: on`、`automl_enabled: true`，并且都打包了 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 时，默认通过 `tao-skill-bank:tao-run-automl` 路由训练操作，使用此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的情况下，报告此模型启用 AutoML 但不可运行，直到生成模式。

非训练操作（如 `evaluate`、`inference`、`export` 和部署流程）保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 训练要求

- **数据集类型：** optical_inspection
- **格式：** 默认
- **AutoML 训练指标：** `val_acc`，方向为 `maximize`
- **独立评估指标：** `test_acc`，方向为 `maximize`

### 每个操作的 数据集 要求

| 操作 | 规范键 | 源 | 文件 | 列表？ |
|---|---|---|---|---|
| evaluate | dataset.test_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| evaluate | dataset.test_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| inference | dataset.infer_dataset.images_dir | inference_dataset | images.tar.gz | 否 |
| inference | dataset.infer_dataset.csv_path | inference_dataset | dataset.csv | 否 |
| train | dataset.train_dataset.images_dir | train_datasets | images.tar.gz | 否 |
| train | dataset.train_dataset.csv_path | train_datasets | dataset.csv | 否 |
| train | dataset.validation_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| train | dataset.validation_dataset.csv_path | eval_dataset | dataset.csv | 否 |
| train | dataset.test_dataset.images_dir | eval_dataset | images.tar.gz | 否 |
| train | dataset.test_dataset.csv_path | eval_dataset | dataset.csv | 否 |

`images.tar.gz` 是传输工件。在准备/提取后，`dataset.*_dataset.images_dir` 必须指向直接包含 `golden/` 和 CSV 使用的板目录的内部目录。

## `dataset.csv` 合约

光学检测加载器按列名读取 CSV 并构建每个 Siamese 比较的两边：

```text
<images_dir>/<input_path>/<object_name>_<lighting><image_ext>
<images_dir>/<golden_path>/<object_name>_<lighting><image_ext>
```

加载器也接受绝对 `input_path` 和 `golden_path` 值；绝对值将替换 `images_dir`。推荐使用相对目录，因为它们在准备后仍然可移植。不要在任一路径列中放入文件名，也不要在 `object_name` 中放入照明后缀或扩展名。

| 列 | 类型 | 必填 | 允许值和含义 |
|---|---|---|---|
| `input_path` | 字符串目录路径 | 是 | 板/捕获组件目录，相对于 `images_dir` 或绝对路径。 |
| `golden_path` | 字符串目录路径 | 是 | 金色/参考组件目录，相对于 `images_dir` 或绝对路径。 |
| `label` | 字符串 | 是 | 精确大小写敏感的 `PASS` 表示非缺陷（类别 0）。任何其他非空缺陷名称表示缺陷（类别 1），例如 `missing`、`shift`、`excess_solder`、`lifted_lead`、`polarity`、`tombstone` 或 `upside down`。`pass` 无效，因为加载器会将其静默处理为缺陷。 |
| `object_name` | 字符串文件名主干 | 是 | 组件标识符，如 `C1018@1`；无目录、`_SolderLight` 或 `.jpg`。加载器强制此列转换为字符串，因此看起来像数字的标识符保留其文本形式。 |

允许额外的元数据列，但此加载器会忽略它们。空值无效。一个基于生产布局的完整行是：

```csv
input_path,golden_path,label,object_name
690-5G190-0510-001P1/AOI_B/FXLH_690-5G190-0510-001P1_30332_P_AOI_B_20230317130332/PerComponent,golden/images/690-5G190-0510-001P1BOT/,PASS,C1018@1
```

使用标准的四灯配置，每行需要八个文件：

```text
<images_dir>/
├── golden/images/690-2G133-0210-000BOT/
│   ├── R821@1_LowAngleLight.jpg
│   ├── R821@1_SolderLight.jpg
│   ├── R821@1_UniformLight.jpg
│   └── R821@1_WhiteLight.jpg
└── 690-2G133-0210-000/AOI_B/<capture>/PerComponent/
    ├── R821@1_LowAngleLight.jpg
    ├── R821@1_SolderLight.jpg
    ├── R821@1_UniformLight.jpg
    └── R821@1_WhiteLight.jpg
```

三个选择字段必须一致：

- `input_map` 键是精确的文件名照明后缀。当前加载器行为迭代 YAML 键插入顺序；它不会按整数值排序。保持值连续并按匹配顺序 (`0..N-1`)。
- `num_input` 必须等于 `input_map` 条目的数量。加载器打开每个键，因此不匹配的值不会限制文件列表并产生张量/导出形状不匹配。
- `concat_type: linear` 沿图像高度按键顺序堆叠输入。使用四个 128×128 输入这将产生 512×128 张量；`grid_map` 被忽略。
- `concat_type: grid` 需要偶数的 `num_input` 和 `grid_map.x * grid_map.y == num_input`。放置按键顺序按行主序排列。对于标准的 `2 x 2` 映射：LowAngle 在左上角，Solder 在右上角，Uniform 在左下角，White 在右下角。

如果数据集确实只包含 `*_SolderLight.jpg`，请使用 `num_input: 1`、`input_map: {SolderLight: 0}` 和 `concat_type: linear`。当有三个变体缺失时，不要声明四个输入。

在训练、评估或推理之前运行打包的预检，使用与规范相同的 数据集 设置：

```bash
python3 skills/models/tao-train-optical-inspection/scripts/validate_dataset.py \
  --csv /data/optical-inspection/train/dataset.csv \
  --images-dir /data/optical-inspection/train/images \
  --num-input 4 \
  --concat-type grid \
  --grid-x 2 --grid-y 2
```

对于自定义映射，按 YAML 键顺序重复 `--input-map LIGHT=INDEX` 并传递规范的 `--image-ext`。验证器报告缺失列、不安全的 PASS 案例、无法解析的行目录以及每个缺失照明文件及其 CSV 行号。一个两行路径桩固定装置位于 `tests/fixtures/dataset/valid/` 下；它验证合约，但不是 PCB 训练数据。

没有发布的 光学检测 样本数据集可从此技能库发现。从您的产品或组织的数据集所有者处获取转换的 AOI 数据，然后将其准备到容器挂载的路径中。不要使用提交的验证器固定装置进行模型训练。

### 典型规范覆盖

数据源覆盖对于每个操作都是**强制性的**——代理必须根据上表中的 每个操作的 数据集 要求构建数据源路径，并将其包含在 `spec_overrides` 中。

```python
TRAIN_ROOT = "/data/optical-inspection/train"
EVAL_ROOT = "/data/optical-inspection/eval"
INFERENCE_ROOT = "/data/optical-inspection/inference"
```

这些是在从其所有者处获取和准备数据后的容器内挂载点示例；它们不是下载位置。

**train (强制数据源):**
```python
{
    "train.num_epochs": 30,
    "train.checkpoint_interval": 10,
    "train.validation_interval": 10,
    "train.num_gpus": 1,
    "dataset.batch_size": 8,
    "dataset.train_dataset.images_dir": f"{TRAIN_ROOT}/images",
    "dataset.train_dataset.csv_path": f"{TRAIN_ROOT}/dataset.csv",
    "dataset.validation_dataset.images_dir": f"{EVAL_ROOT}/images",
    "dataset.validation_dataset.csv_path": f"{EVAL_ROOT}/dataset.csv",
    "dataset.test_dataset.images_dir": f"{EVAL_ROOT}/images",
    "dataset.test_dataset.csv_path": f"{EVAL_ROOT}/dataset.csv",
}
```

**evaluate (强制数据源):**
```python
{
    "evaluate.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.test_dataset.images_dir": f"{EVAL_ROOT}/images",
    "dataset.test_dataset.csv_path": f"{EVAL_ROOT}/dataset.csv",
}
```

使用工作流的检查点解析器而不是猜测文件名进行下游操作。对于 光学检测 烟雾运行，AutoML 可能生成 `model_epoch_000_step_00006.pth`；然后可以生成 `model_epoch_001_step_00012.pth`。最佳检查点操作应使用 AutoML 最佳子作业选择的检查点，特定于 epoch 的操作应传递精确的 epoch/step 检查点，并且仅显式的 "latest" 请求应解析为最新检查点。

**export:**
```python
{
    "export.checkpoint": "<选定的 train/AutoML 检查点>",
    "export.onnx_file": "/results/optical_inspection.onnx",
    "export.input_width": 128,
    "export.input_height": 512,
    "export.batch_size": 1,
}
```

**inference (强制数据源):**
```python
{
    "inference.checkpoint": "<选定的 train/AutoML 检查点>",
    "dataset.infer_dataset.images_dir": f"{INFERENCE_ROOT}/images",
    "dataset.infer_dataset.csv_path": f"{INFERENCE_ROOT}/dataset.csv",
}
```

## 数据集转换

光学检测的数据集转换是可选的。如果数据集已经是 TAO-就绪的光学检测格式，请直接从 `images.tar.gz` 加 `dataset.csv` 分割开始，并在转换的数据上运行 `train`、`evaluate`、`inference` 和下游检查点/导出/部署操作。

PyT 容器暴露 `optical_inspection dataset_convert`，但此模型技能不打包 `dataset_convert` 操作/模板。转换器期望原始工厂 PCB 布局 (`root_dataset_dir`、训练/验证/所有 PCB 目录、`golden_csv_dir`、`project_name` 和 `bot_top`)。数据所有者也可以提供预转换的光学检测 `images.tar.gz` 加 `dataset.csv` 分割，而无需原始 PCB/金色 CSV 源。不要合成假的 PCB 数据集。在模型验证报告中，当只有转换数据可用时，将数据集转换标记为 `not run: preconverted dataset provided` 而不是失败或阻止。

在使用预转换的传输存档时，在写入规范之前验证提取的目录。存档可能会解包一个 `images/` 包装目录；将 `dataset.*.images_dir` 指向包含 `golden/` 和 `dataset.csv` 引用的板/图像文件夹的内部目录，例如 `.../<split>/images/images`，而不是外层包装。

产品端的后续操作仍然是：发布一个许可的、可训练的样本数据集，并将现有的容器 `dataset_convert` 入口点打包为技能操作及其自己的模式/模板。这两者都没有在此文档中实现，并且预检没有更改。

## 评估数据集

可选。评估数据集使用相同的格式（图像 + CSV）。

## 重要参数

- **model.model_type**: Siamese 变体。选项包括 Siamese、Siamese_3。
- **model.model_backbone**: 默认自定义。
- **model.embedding_vectors**: 嵌入维度数量。默认 5。
- **train.optim.lr**: 学习率。默认 5e-4。
- **dataset.batch_size**: 训练批大小。必须大于 1；使用 `2` 或更高进行最小的烟雾运行。
- **dataset.num_input**: 每个比较的输入图像数量。
- **dataset.input_map**: 输入通道/图像对映射。

## 多 GPU / 多节点

**启动方法：** Lightning 管理的（单个 `python` 进程，Lightning 生成工作进程）。

| 规范键 | 描述 | 默认 |
|---|---|---|
| `train.num_gpus` | GPU 数量 | 1 |
| `train.gpu_ids` | GPU 设备索引 | [0] |

- 策略：`auto`（Lightning 自动选择最佳策略）
- 没有 `num_nodes` 或 `distributed_strategy` 配置——仅单节点
- 轻量级 Siamese 网络，单个 GPU 通常足够

## 硬件

至少 1 个 GPU(s)，推荐 1 个 GPU(s)。每个 GPU 8GB+ VRAM。用于检测的 Siamese 网络是轻量级的。单个 GPU 足够。

## 错误模式

**CSV 格式错误**：要求 `input_path,golden_path,label,object_name`，然后在启动前使用规范的 `images_dir`、照明映射、`num_input`、连接、网格和图像扩展运行 `scripts/validate_dataset.py`。

**提取图像根路径不匹配**：如果训练、评估或推理无法从 `dataset.csv` 找到路径，请检查提取的 `images.tar.gz` 树。TAO-就绪的根必须包含 `golden/` 加 CSV 中引用的板文件夹。对于传输存档，这可以是提取目标的下一级，例如 `images/images`。

**训练批大小断言**：光学检测数据加载器拒绝 `dataset.batch_size: 1` 用于训练。对于正常运行，请保留模板默认值 8，或设置 `dataset.batch_size: 2` 用于最小的 AutoML 烟雾验证。

**PyTorch 下游操作检查点加载失败**：对于由相同的可信 TAO 训练/AutoML 工作流生成的检查点，如果当前的 PyTorch 默认阻止加载完整检查点，请为评估、推理、导出和恢复作业设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`。不要使用此环境变量进行不可信的检查点。

## 规范参数 / 父模型推理

特定于模型的推理映射属于此 MD 文件，而不是 `config.json`。生成的运行者应在此部分读取此映射并使用 SDK 帮助程序在 `create_job()` 之前应用映射。这反映了旧的微服务 `infer_params.py` 流程。

来自 TAO Core `optical_inspection.config.json` 的推理映射：

| 操作 | 规范字段 | 推理函数 | 含义 |
|---|---|---|---|
| evaluate | `encryption_key` | `key` | 加密密钥 |
| evaluate | `evaluate.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| evaluate | `results_dir` | `output_dir` | 当前作业结果目录 |
| export | `encryption_key` | `key` | 加密密钥 |
| export | `export.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| export | `export.onnx_file` | `create_onnx_file` | 输出 ONNX 路径 |
| export | `results_dir` | `output_dir` | 当前作业结果目录 |
| inference | `encryption_key` | `key` | 加密密钥 |
| inference | `inference.checkpoint` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `inference.trt_engine` | `parent_model` | 从父作业结果文件夹推断的模型文件 |
| inference | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `encryption_key` | `key` | 加密密钥 |
| train | `results_dir` | `output_dir` | 当前作业结果目录 |
| train | `train.pretrained_model_path` | `ptm_if_no_resume_model` | 当没有恢复检查点时 PTM |
| train | `train.resume_training_checkpoint_path` | `resume_model` | 从当前作业结果文件夹推断的模型文件 |

对于 `parent_model` 或 `parent_model_folder`，将上游训练/导出/AutoML 子作业 ID 作为 `parent_job_id` 传递。SDK 列出父结果文件夹，过滤检查点工件，并返回选定的模型文件或文件夹。不要将这些映射重新添加到 `config.json`，也不要修补生成的运行者脚本以猜测检查点路径。

## 部署

- [tao-deploy-optical-inspection](references/tao-deploy-optical-inspection.md)
