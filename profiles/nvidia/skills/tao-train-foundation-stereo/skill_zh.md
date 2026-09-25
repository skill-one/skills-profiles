# 深度网络立体

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 FoundationStereo 架构进行立体深度估计。从立体图像对中预测视差图，用于 3D 重建。

使用预训练的 Depth Anything v2 和 EdgeNeXt 编码器。设置 `model.stereo_backbone.depth_anything_v2_pretrained_path` 和 `model.stereo_backbone.edgenext_pretrained_path`。

单目和立体技能都在容器内调用统一的 TAO `depth_net` CLI；通过 `model.model_type`（例如 `FoundationStereo`）选择单目/立体系列。

此模型技能打包的 PyT 动作：`train`、`evaluate`、`inference`、`export` 和 `quantize`。当前的 TAO 镜像中的 PyT `depth_net` 入口点不接受 `gen_trt_engine` 动作；仅通过部署工作流构建 TensorRT 引擎。

对于 TAO Deploy TensorRT 动作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`），请先阅读 `references/tao-deploy-foundation-stereo.md`。部署规范模板位于此技能的 `references/spec_template_deploy.yaml` 中。

## 训练动作策略

此模型在模型层支持 AutoML。在处理任何训练阶段请求之前，请阅读 `references/skill_info.yaml` 并从显式的 `automl_policy` 值或用户的 workflow 请求中解析运行覆盖。默认使用 `automl_policy: on` 并仅在新的启动提示中暴露 `on` / `off`。将 "关闭 AutoML"、"禁用 AutoML"、"无 HPO" 或 "纯训练" 等短语视为 `automl_policy: off`，仅针对此运行。当 `automl_policy: on`、`automl_enabled: true`，并且 `schemas/train.schema.json` 和 `references/spec_template_train.yaml` 都被打包时，默认将训练动作通过 `tao-skill-bank:tao-run-automl` 路由到此模型的 `skill_dir`。保留工作流/应用程序覆盖的数据集、规范、输出目录、GPU/平台设置、父检查点和 `automl_policy`。仅在 `automl_policy: off` 或打包的训练模式/模板缺失时使用直接模型训练；在缺失模式的案例中，在模式生成之前报告此模型启用但不可运行。

如 `evaluate`、`inference`、`export` 和部署流程等非训练动作保留在此模型技能中。每运行的 `automl_policy` 覆盖不会更改模型元数据。

## 工作流

### 前置条件 — 数据可访问性

您的数据集（左 + 右图像 + GT 视差）必须可以从容器内部访问：
- **SDK 运行器**：将文件放置在运行器解析的 S3 路径（规范覆盖中显示的 `S3_TRAIN` / `S3_EVAL` 占位符）。运行器透明地处理 S3 → 容器路径挂载。
- **直接 `docker run`**（例如本地测试）：将主机数据集根以只读方式挂载到相同的容器路径：

```
docker run ... -v <host_data_root>:<host_data_root>:ro <container> ...
```

所有动作写入的 `<output_dir>` 也适用相同的可访问性要求。

### 第 1 步 — 注释文件

由 `data_sources[*].data_file` 引用的每行注释文件：

| 列 | 格式 | 用途 |
|---|---|---|
| 2 | `<left> <right>` | 立体推理（无 GT） |
| 3 | `<left> <right> <disparity>` | 立体带 GT |
| 4 | `<left> <right> <disparity> <occlusion_mask>` | 立体带 GT 和遮挡掩码 |

如果您已经有了，请指向它。否则通过 `depth_net convert` 生成：

```
depth_net convert -e <convert_spec.yaml>
```

`convert_spec.yaml` 模板（立体）：

```yaml
results_dir: <生成的注释文件写入的目录>
data_root: <其直接子级为包含您的图像+深度文件的场景文件夹的目录；convert 递归遍历 data_root 但期望在下一级有一个每场景子目录>
image_dir_pattern: [<匹配左图像路径的子字符串>]
right_dir_pattern: [<匹配右图像路径的子字符串>]
depth_dir_pattern: [<匹配 GT 视差路径的子字符串>]
nocc_dir_pattern: []                 # 可选，遮挡掩码路径
image_extension: '.png'  # 始终包含点号
depth_extension: '.png'  # 形式必须匹配 image_extension（交换是子字符串替换）
nocc_extension: ''
split_ratio: 0.0        # 0.0/1.0 = 仅测试；0.8 = 80/20 训练+验证
```

`convert` 递归遍历 `data_root`，选择路径的路径字符串包含 `image_dir_pattern` 中的所有子字符串（AND 过滤器），然后通过将 `image_dir_pattern[0]` 替换为相应模式的第一元素加上扩展名交换来导出右 / 深度 / 掩码路径。检查您的数据集的目录布局并识别区分左、右和 GT 的子字符串（例如 `im0` vs `im1` vs `disp0GT` for Middlebury）。

### 第 2 步 — 根据您的数据匹配 `model_type` 和 `dataset_name`

当您的布局匹配支持的一个时，优先使用数据集特定的类——它应用类特定的路径约定、评估裁剪，以及在适用的情况下处理遮挡掩码。仅在布局不匹配任何注册类时回退到 `GenericDataset`。

| 数据类别 | `model_type` | `dataset_name` |
|---|---|---|
| Middlebury 数据 | `FoundationStereo` | `Middlebury` |
| KITTI 数据 | `FoundationStereo` | `Kitti` |
| ETH3D 数据 | `FoundationStereo` | `Eth3d` |
| FSD 合成数据 | `FoundationStereo` | `FSD` |
| IsaacReal 合成数据 | `FoundationStereo` | `IsaacRealDataset` |
| Crestereo 合成数据 | `FoundationStereo` | `Crestereo` |
| 其他 / 非规范布局 | `FoundationStereo` | `GenericDataset` |

立体 `data_sources` 的有效 `dataset_name` 值（不区分大小写）：`FSD`、`IsaacRealDataset`、`Crestereo`、`Middlebury`、`Eth3d`、`Kitti`、`GenericDataset`。

相同的 `dataset_name` 值适用于训练和评估动作（所有动作都使用 3 列或 4 列带 GT 视差的注释）。部署侧的 `evaluate` 动作遵循相同规则——见 `references/tao-deploy-foundation-stereo.md`。对于使用 2 列注释（左 + 右，无 GT）的推理，无论数据布局如何，都使用 `dataset_name: GenericDataset`——数据集特定的类（`Middlebury` / `Kitti` / `Eth3d` / `FSD` / `IsaacRealDataset` / `Crestereo`）需要 3 列输入并在数据加载器级别拒绝 2 列注释。对于使用 3 列注释（左 + 右 + GT）的推理，数据集特定的类是合适的。

### 第 3 步 — 从规范覆盖写入规范 YAML

从 `references/spec-overrides-foundation-stereo.md` 复制动作块。替换：
- `model.model_type` 从第 2 步（通常为 `FoundationStereo`）
- `dataset.<...>.data_sources[*].dataset_name` 从第 2 步
- `dataset.<...>.data_sources[*].data_file` 为第 1 步的路径
- 对于部署侧 `evaluate`：强制 `dataset.test_dataset.batch_size: 1`（见 `references/tao-deploy-foundation-stereo.md`）。

形状一致性：`dataset.test_dataset.augmentation.crop_size` 中的 `crop_size` 应与 `export.input_height` / `input_width` 匹配，以便训练模型评估器和部署侧 TensorRT 评估器在相同形状下运行。注意 `crop_size` 在 pyt `evaluate` 路径上是装饰性的，但在部署 `evaluate` 侧是权威的——见 `references/troubleshooting-foundation-stereo.md` 和 `references/tao-deploy-foundation-stereo.md`。

新鲜安装的冒烟测试在 `crop_size: [128, 128]`、`dataset.max_disparity: 128` 和 `model.max_disparity: 128` 下验证。避免 112×112 裁剪，并避免将 `max_disparity` 设置小于方形裁剪边长进行冒烟测试：这些组合可能在 FoundationStereo 中因特征图或损失掩码形状不匹配而在生成检查点之前失败。

数据源覆盖对每个动作都是**必需的**。每个 `data_sources` 条目是一个包含两个必需字段的字典：`data_file` 和 `dataset_name`。见 `references/spec-overrides-foundation-stereo.md` 的每动作数据集要求表、每个动作的覆盖块，以及 `quantize` 已知问题说明。

### 第 4 步 — 运行

在使用 `--user` 之前，在挂载的输出路径内创建可写的 home/cache 目录。某些 TAO 容器没有主机 UID 的 `/etc/passwd` 条目，并且当以该 UID 运行时，PyTorch / matplotlib 需要可写的缓存路径。

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

没有 `--user "$(id -u):$(id -g)"`，容器将输出作为 `nobody:nogroup`，这将阻止主机侧清理/重试。

### 第 5 步 — 验证

- 容器退出码 0
- `status.json` `kpi` 块已填充
- 对于 `train`：直接检查每步 `train_loss`（入口点即使在损失为 NaN 时也会报告 `Execution status: PASS`）
- 对于 `evaluate`：依赖 `epe` / `bp1` / `bp2` / `bp3` / `d1` / `rmse`（评估器还会发出 `abs_rel` / `sq_rel` / `rmse_log`，这些对于立体是无意义的——见 `references/parameters-foundation-stereo.md`）
- 对于 `inference`：`results_dir` 下的工件

对于 TAO Deploy TensorRT 动作（`gen_trt_engine`、TensorRT `evaluate` 和 TensorRT `inference`），请先阅读 `references/tao-deploy-foundation-stereo.md`。部署规范模板位于此技能的 `references/` 文件夹中，前缀为 `spec_template_deploy_*.yaml`。

## 训练要求

- **AutoML 指标契约**：当使用打包的 `evaluate` 动作对推荐进行评分时，使用 `val/epe` 并指定最小化方向。
- **训练监控指标**：`val/loss`
  仅用于实时训练损失监控。
- **AutoML/评估 KPI**：`val/epe`，最小化。打包的 `evaluate`
  动作将此键写入 `status.json`；使用 `val/loss` 作为 AutoML
  目标会导致试验指标提取失败。其 Lightning 控制台表格标记相同的评估器输出 `test/epe`，因此当验证运行时，比较 AutoML 记录的 `val/epe` 值与控制台的 `test/epe` 值。
- **推荐的 AutoML 训练参数**：`train.optim.lr` 和
  `train.optim.weight_decay`。不要搜索验证/测试/推理增强字段，并且不要搜索 `model.volume_dim`，因为当前实现不消费它。
- **评估数据集**：可选。通过 `dataset.val_dataset.data_sources` 配置验证数据集（每个条目需要 `data_file` 和 `dataset_name`）。

见 `references/spec-overrides-foundation-stereo.md` 的每动作数据集要求表和每个动作的必需数据源覆盖块。

## 参数、指标、多 GPU、导出/TRT、硬件

见 `references/parameters-foundation-stereo.md` 的完整重要参数列表（包括 `model.encoder` `vits` 覆盖、`model.max_disparity` 默认 416、`model.volume_dim` 无操作说明、`dataset.baseline`、`dataset.focal_x`、`train.precision`、`export.batch_size`）、评估指标表、多 GPU / 多节点启动键、导出 / TRT 默认（`opset_version`/`on_cpu` 配对、NGC 576×960 设置）和硬件要求。

## 错误模式及故障排除

见 `references/troubleshooting-foundation-stereo.md` 的视差溢出、冒烟测试形状不匹配、缺失预训练路径、`encoder` / `dataset_name` 结构错误、`depth_net_stereo: not found` 入口点说明、pyt-与部署 `crop_size` 讨论，以及部署 `evaluate` 标量转换失败。

## 规范参数 / 父模型推理

见 `references/checkpoint-inference-mappings-foundation-stereo.md` 的检查点解析规则（`model_epoch_<epoch>_step_<step>.pth`、`dn_model_latest.pth` 策略）、缺少父 PyT `gen_trt_engine`，以及从 `depth_net_stereo.config.json` 的完整每动作推理映射表（包括 `parent_model` / `parent_job_id` 解析）。

## 部署

- [tao-deploy-foundation-stereo](references/tao-deploy-foundation-stereo.md)
