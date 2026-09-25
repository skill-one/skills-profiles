# NV-Generate-VAE-Finetune

## 目的
- 用于从用户提供的CT或MRI NIfTI训练体积微调NV-Generate-CTMR MAISI VAE/自动编码器。
- 不用于临床解释、监管使用或批准用于生产训练的合成数据。
- 目前上游文档中记录了`train_vae_tutorial.ipynb`中的VAE训练，并提供了配置/辅助工具，但没有`scripts.train_vae` CLI。此技能不会执行笔记本；它本地准备所需的配置/数据列表粘合剂，并使用上游辅助API。
- 资源清单I/O：输入是`datalist`和`data_base_dir`；输出是`autoencoder_checkpoint`、`discriminator_checkpoint`和`result_json`。
- 底层训练合同是上游配置/环境JSON（`config_maisi_vae_train.json` + `environment_maisi_vae_train.json`，如在`train_vae_tutorial.ipynb`中使用）。包装器为您准备这些JSON文件，并将最调优的字段作为CLI标志公开；下文记录了这些字段、它们的默认值以及如何监控/调优运行。

## 说明
- 在更改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 从Medical AI Skills仓库根目录运行`scripts/run_vae_finetune.py`。
- 如果主机代理公开`run_script`，请使用`run_script("scripts/run_vae_finetune.py", args=[...])`；否则运行下面的Bash/Python命令。
- 在检查新的数据列表时，首先使用`--preflight`；仅在用户明确希望启动GPU微调时才移除`--preflight`。
- 对于预置的preflight输入包目录，当这些文件存在时，使用`BUNDLE/preflight_datalist.json`作为数据列表，并使用`BUNDLE/preflight_dataset`作为`--data-base-dir`。

## 示例

从输入包验证和准备预置的微调检查（推荐的第一个步骤——无GPU，无训练）。这是唯一的规范命令；将`INPUT_BUNDLE`和`OUT_DIR`替换为您的路径：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python skills/nv-generate-vae-finetune/scripts/run_vae_finetune.py \
  INPUT_BUNDLE/preflight_datalist.json \
  --data-base-dir INPUT_BUNDLE/preflight_dataset \
  --output-dir OUT_DIR \
  --modality mri \
  --preflight
```

对于真实的GPU微调和其他变化，请参阅下文的[使用](#2-使用-单行训练)。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_vae_finetune.py` | 由`skill_manifest.yaml`声明的入口点。 | `DATALIST.json --data-base-dir DATA_DIR --output-dir OUT_DIR [--epochs N] [--modality mri] [--patch-size 64,64,64] [--preflight]` |

## 前置条件
- 显式的`NV_GENERATE_ROOT`可以指向调用者的本地检出，并且必须包含`configs/config_maisi_vae_train.json`、`scripts/transforms.py`和`scripts/utils.py`。结果记录其当前提交。
- 如果`NV_GENERATE_ROOT`未设置，包装器会搜索`.workbench_data/upstreams/NV-Generate-CTMR`。
- `CUDA_VISIBLE_DEVICES`是可选的，可用于选择用于真实训练的GPU。
- 运行时要求：真实训练需要NVIDIA CUDA GPU，上游`requirements.txt`中的Python包、`lpips`，以及除非使用`--train-from-scratch`，否则下载的VAE权重。
- 副作用：在调用者提供的`--output-dir`下写入预置的配置、检查点、TensorBoard日志和运行摘要；可能会在上游检出、`~/.cache/huggingface/`和`~/.cache/torch/`下写入模型缓存；可能会联系`https://huggingface.co`、`https://github.com`和`https://download.pytorch.org`。
- 数据列表是一个MONAI风格的JSON对象，具有非空的`training[]`和`validation[]`或`testing[]`。每个条目具有相对于`--data-base-dir`的`image`路径，以及可选的`class`或`modality`为`ct`或`mri`。

当没有本地检出时，创建推荐的固定默认检出一次：

```bash
if [ -z "${NV_GENERATE_ROOT:-}" ]; then
  export NV_GENERATE_COMMIT=61c4ec709b84cad468852243c48e250bec732074
  export NV_GENERATE_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7"
  if [ ! -d "$NV_GENERATE_ROOT/.git" ]; then
    git clone https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git "$NV_GENERATE_ROOT"
    git -C "$NV_GENERATE_ROOT" checkout --detach "$NV_GENERATE_COMMIT"
  fi
fi
```

## 1. 配置和环境JSON（根据您的数据调整）

包装器从`$NV_GENERATE_ROOT/configs`复制上游VAE配置/环境JSON，重写下述字段，并将预置副本写入`OUT_DIR/workflow/configs/`。通常您只需设置您的数据列表和数据根；当您需要时，列出的CLI标志会覆盖单个字段。

环境JSON (`environment_maisi_vae_train.json`)：

| 字段 | 设置自 | 备注 |
|---|---|---|
| `model_dir` | `--output-dir` | 存储autoencoder.pt/discriminator.pt和最佳检查点的位置。 |
| `tfevent_path` | `--output-dir` | TensorBoard事件目录。 |
| `finetune` | `--train-from-scratch` | `true`（默认）加载`trained_autoencoder_path`；该标志将其设置为`false`。 |
| `trained_autoencoder_path` | 上游权重 / `--trained-autoencoder-path` | 微调时的起始VAE检查点。 |

训练字段 (`config_maisi_vae_train.json`)：

| 字段 | 标志 | 类型 | 默认值 | 备注 |
|---|---|---|---|---|
| `autoencoder_train.n_epochs` | `--epochs` | int | `1` | |
| `autoencoder_train.batch_size` | `--batch-size` | int | `1` | 每个GPU（单GPU运行者）。 |
| `autoencoder_train.patch_size` | `--patch-size` | int,int,int | `64,64,64` | 训练裁剪。 |
| `autoencoder_train.val_batch_size` | `--val-batch-size` | int | `1` | |
| `autoencoder_train.val_sliding_window_patch_size` | `--val-sliding-window-patch-size` | int,int,int | `96,96,64` | 滑动窗口验证ROI。 |
| `autoencoder_train.lr` | `--lr` | float | `1e-4` | |
| `autoencoder_train.perceptual_weight` | `--perceptual-weight` | float | `0.3` | LPIPS项。 |
| `autoencoder_train.kl_weight` | `--kl-weight` | float | `1e-7` | KL项。 |
| `autoencoder_train.adv_weight` | `--adv-weight` | float | `0.1` | 对抗项。 |
| `autoencoder_train.recon_loss` | `--recon-loss` | `l1`|`l2` | `l1` | |
| `autoencoder_train.val_interval` | `--val-interval` | int | `1` | 两次验证之间经过的epoch数。 |
| `autoencoder_train.cache` | `--cache-rate` | float | `0.0` | MONAI `CacheDataset`分数。 |
| `autoencoder_train.amp` | `--no-amp` | 标志 | 开启 | 混合精度；该标志禁用它。 |
| `data_option.random_aug` | `--no-random-aug` | 标志 | 开启 | 随机增强；该标志禁用它。 |
| `data_option.spacing_type` | `--spacing-type` | `original`|`fixed`|`rand_zoom` | `original` | |
| `data_option.spacing` | `--spacing` | float,float,float | 未设置 | 当`spacing_type`为`fixed`/`rand_zoom`时需要。 |
| `data_option.select_channel` | `--select-channel` | int | `0` | 多通道输入的通道。 |

`--modality`（`ct`或`mri`，默认`mri`）为缺少`class`的数据列表项填充每个条目。验证/测试条目是必需的，因为训练循环会运行验证通过。

有关包括示例数据下载的端到端参考，请参阅上游教程`train_vae_tutorial.ipynb`。

## 2. 使用（单行训练）

仅预置：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python skills/nv-generate-vae-finetune/scripts/run_vae_finetune.py \
  PATH_TO_DATALIST.json \
  --data-base-dir PATH_TO_DATA_ROOT \
  --output-dir runs/nv_generate_vae_finetune_preflight \
  --preflight
```

预置包输入：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python skills/nv-generate-vae-finetune/scripts/run_vae_finetune.py \
  PATH_TO_INPUT_BUNDLE/preflight_datalist.json \
  --data-base-dir PATH_TO_INPUT_BUNDLE/preflight_dataset \
  --output-dir runs/nv_generate_vae_finetune_preflight \
  --preflight
```

GPU微调：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python -m pip install lpips tensorboard && \
python skills/nv-generate-vae-finetune/scripts/run_vae_finetune.py \
  PATH_TO_DATALIST.json \
  --data-base-dir PATH_TO_DATA_ROOT \
  --output-dir runs/nv_generate_vae_finetune \
  --epochs 1 \
  --modality mri \
  --patch-size 64,64,64 \
  --download-model-data
```

将`PATH_TO_DATALIST.json`和`PATH_TO_DATA_ROOT`替换为用户的实际路径。不要使用固定数据列表进行真实训练；它是一个预置的占位符。

## 3. 监控训练（TensorBoard）

运行者将TensorBoard标量（每迭代和每epoch的`recons_loss`、`kl_loss`、`p_loss`、对抗/真实/伪造损失，以及验证`scale_factor`）写入`OUT_DIR/artifacts/tfevent/autoencoder`。针对输出目录启动TensorBoard：

```bash
python -m pip install tensorboard && \
tensorboard --logdir runs/nv_generate_vae_finetune/artifacts/tfevent
```

相同的每epoch损失历史也捕获在`OUT_DIR/artifacts/workflow_summary.json`中，并且包装器会将其打印到stdout中（`loss_history`、最佳检查点路径、`exit_code`、`stderr_tail`）。

## 4. 超参数调优和常见陷阱

- **重建模糊** — 提高`--perceptual-weight`（默认`0.3`）；如果边缘看起来被冲淡，尝试`--recon-loss l2`。
- **后验崩溃/过度正则化的潜在** — `--kl-weight`故意非常小（`1e-7`）；增加它太多会降低重建质量。
- **对抗训练不稳定** — 降低`--adv-weight`（默认`0.1`）或`--lr`；一个预热计划已经在前20个epoch中逐步提高LR。
- **内存不足** — 减少`--patch-size`（例如`48,48,48`）和`--val-sliding-window-patch-size`，保持`--batch-size 1`，并降低`--cache-rate`。
- **`datalist must include non-empty validation[] or testing[]`** — 验证循环是强制性的；添加`validation[]`（或`testing[]`）条目。
- **仅单GPU** — 运行者断言一个CUDA GPU；设置`CUDA_VISIBLE_DEVICES`选择哪一个。

## 5. 评估微调的VAE

验证重建损失（最低`val_weighted_loss` epoch）会自动跟踪，并将最佳自动编码器保存为`autoencoder_epochN.pt`在`OUT_DIR/artifacts/models`下。为了评估下游：

- 在TensorBoard中比较不同运行的验证`recons_loss`/`p_loss`曲线，
- 将微调的自动编码器插入扩散微调/生成运行（例如[`nv-generate-mr-brain-finetune`](../nv-generate-mr-brain-finetune/SKILL.md)通过`--trained-autoencoder-path`）以确认潜在仍然解码为可用的体积。

此技能仅控制文件会计和重建会计——图像质量和下游效用必须由领域专家判断。

## 限制
- 需要一个当前的`NV-Generate-CTMR`上游检出，其中包含VAE配置和辅助API。此技能拥有运行者粘合剂，不依赖于笔记本。
- 完整训练可能很昂贵，并且在硬件、CUDA和包版本之间不可确定。
- 包装器控制文件会计和命令来源，而不是解剖真实性、重建质量或下游模型效用。
- 不用于临床部署、临床解释、自主诊断、监管提交或生产训练数据批准。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| `VAE configs/helpers were not found` | `NV_GENERATE_ROOT`没有指向当前的NV-Generate-CTMR检出。 | 克隆或更新`https://github.com/NVIDIA-Medtech/NV-Generate-CTMR`并设置`NV_GENERATE_ROOT`。 |
| `datalist must include non-empty validation[] or testing[]` | VAE训练需要配置的验证循环的验证数据。 | 添加`validation[]`或`testing[]`条目，带有相对图像路径。 |
| CUDA、MONAI或LPIPS导入失败 | 运行时环境缺少上游依赖项。 | 在选定的环境中安装`"$NV_GENERATE_ROOT/requirements.txt"`加上`lpips tensorboard`。 |
