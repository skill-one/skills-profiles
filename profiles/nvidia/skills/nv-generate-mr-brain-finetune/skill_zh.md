# NV-Generate-MR-Brain-Finetune

## 目的
- 用于微调 NV-Generate-CTMR `rflow-mr-brain` v1 扩散 UNet，使用用户提供的 T1、T2、FLAIR、SWI 或 MRA NIfTI 训练体积。
- 不用于临床解释、监管使用或批准用于生产训练的合成数据。
- 包装器在本地阶段配置粘合剂并将执行委托给现有的上游脚本：`scripts.diff_model_create_training_data`、`scripts.diff_model_train`，以及可选的 `scripts.diff_model_infer`。它不会执行笔记本。
- 资源 I/O：输入是 `datalist` 和 `data_base_dir`；输出是 `finetuned_checkpoint`、可选的 `inference_outputs` 和 `result_json`。
- 底层训练合同是上游的配置/环境 JSON（与 `train_diff_unet_tutorial.ipynb` 的单元格 `[10]` 驱动的相同）。包装器为您阶段这些 JSON 文件并作为 CLI 标志公开最微调的字段；下文记录了这些字段、它们的默认值以及如何监控/微调运行。

## 说明
- 在更改参数、副作用或验证门之前，请先阅读 `skill_manifest.yaml`。
- 从 Medical AI Skills 仓库根目录运行 `scripts/run_mr_brain_finetune.py`。
- 如果主机代理暴露了 `run_script`，请使用 `run_script("scripts/run_mr_brain_finetune.py", args=[...])`；否则运行下面的 Bash/Python 命令。
- 对于命令形状的审查，不要安装包、克隆仓库、下载权重或启动 GPU 训练。仅发出包装器命令，并提供所提供的 `datalist`、显式的 `--data-base-dir`、显式的 `--output-dir` 和请求的模态。
- 当用户明确要求训练启动命令时，不要将其静默地替换为 `--preflight`；仅在预检请求时包含 `--preflight`。
- 在检查新的 `datalist` 时，首先使用 `--preflight`；仅在用户明确希望启动 GPU 微调时才移除 `--preflight`。
- 对于分阶段的预检输入包目录，当这些文件存在时，使用 `BUNDLE/preflight_datalist.json` 作为 `datalist`，使用 `BUNDLE/preflight_dataset` 作为 `--data-base-dir`。

## 示例

从输入包中验证和阶段预检微调检查（这是推荐的第一个步骤——没有 GPU，没有训练）。这是唯一的规范命令；将 `INPUT_BUNDLE` 和 `OUT_DIR` 替换为您的路径：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-da438fe}" && \
python skills/nv-generate-mr-brain-finetune/scripts/run_mr_brain_finetune.py \
  INPUT_BUNDLE/preflight_datalist.json \
  --data-base-dir INPUT_BUNDLE/preflight_dataset \
  --output-dir OUT_DIR \
  --modality mri_t1 \
  --preflight
```

对于真实的 GPU 微调和其他变化，请参阅下文的 [使用](#2-usage-one-line-training)。

请求训练启动的命令形状审查（无设置或执行）：

```bash
python skills/nv-generate-mr-brain-finetune/scripts/run_mr_brain_finetune.py \
  PATH_TO_DATALIST.json \
  --data-base-dir PATH_TO_DATA_ROOT \
  --output-dir runs/nv_generate_mr_brain_finetune \
  --epochs 2 \
  --modality mri_t1
```

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_mr_brain_finetune.py` | 由 `skill_manifest.yaml` 声明的入口点。 | `DATALIST.json --data-base-dir DATA_DIR --output-dir OUT_DIR [--epochs N] [--modality mri_t1] [--num-gpus N] [--no-amp] [--model-config FILE] [--download-model-data] [--run-inference] [--preflight]` |

## 前置条件
- 显式的 `NV_GENERATE_ROOT` 可以指向调用者的本地检出，并且必须包含 `scripts/diff_model_create_training_data.py`、`scripts/diff_model_train.py` 和 `scripts/diff_model_infer.py`。结果记录其当前提交。
- 如果 `NV_GENERATE_ROOT` 未设置，包装器会在 `.workbench_data/upstreams/NV-Generate-CTMR` 中搜索。
- `CUDA_VISIBLE_DEVICES` 是可选的，可用于选择用于真实训练的 GPU。
- 运行时要求：NVIDIA CUDA GPU 用于真实训练、上游 `requirements.txt` 中的 Python 包以及下载的 MR-脑权重。
- 副作用：在调用者提供的 `--output-dir` 下写入阶段配置、嵌入、检查点、可选的推理图像和日志；可能会在上游检出和 `~/.cache/huggingface/` 下写入模型缓存；可能会联系 `https://huggingface.co` 获取模型资产和 `https://github.com` 获取上游检出。
- `datalist` 是一个 MONAI 风格的 JSON 对象，其中 `training[].image` 路径相对于 `--data-base-dir`。`training[].modality` 是可选的，默认为 `mri_t1`。

当没有本地检出时，创建推荐的固定默认检出一次：

```bash
if [ -z "${NV_GENERATE_ROOT:-}" ]; then
  export NV_GENERATE_COMMIT=da438fec6484cdb6f421f8c7051d954ebefff730
  export NV_GENERATE_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-da438fe"
  if [ ! -d "$NV_GENERATE_ROOT/.git" ]; then
    git clone https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git "$NV_GENERATE_ROOT"
    git -C "$NV_GENERATE_ROOT" checkout --detach "$NV_GENERATE_COMMIT"
  fi
fi
```

包装器仅在 `NV_GENERATE_ROOT` 位于确切清单提交且其跟踪文件干净时执行上游代码。通过记录的配置标志而不是编辑检出来提供自定义训练和推理设置。子进程仅接收运行时、CUDA、区域和证书变量的允许列表；API 密钥、令牌、密码和不相关的父环境值不会被转发。公共 v1 资产不需要凭证；如果您的网络设置需要单独的工具，请预先下载它们。

在 GPU 运行之前，下载清单声明的确切自动编码器和 MR-脑 v1 检查点修订版。传递 `--download-model-data` 执行相同的两个固定下载：

```bash
python -m huggingface_hub.commands.huggingface_cli download \
  nvidia/NV-Generate-CT models/autoencoder_v1.pt \
  --revision 75ac080fb1083c403793563477724c038e7d430c \
  --local-dir "$NV_GENERATE_ROOT"
python -m huggingface_hub.commands.huggingface_cli download \
  nvidia/NV-Generate-MR-Brain models/diff_unet_3d_rflow-mr-brain_v1.pt \
  --revision ef9759bf221265b2704569cdeeac20bbf03b62ee \
  --local-dir "$NV_GENERATE_ROOT"
```

## 1. 配置和环境 JSON（根据您的数据调整）

这是上游 `train_diff_unet_tutorial.ipynb` 流的薄包装器。每次运行执行四个步骤，将繁重的工作委托给模型作者的脚本：

1. **阶段配置** — 复制三个配置 JSON 并仅重写运行特定的路径和 `n_epochs`（笔记本单元格 15）。
2. `python -m scripts.diff_model_create_training_data` → 潜在的 `*_emb.nii.gz` 嵌入（单元格 17）。
3. **写入嵌入副件** — 每个嵌入一个 `<emb>.nii.gz.json`，包含 `spacing`/`modality`（当模型使用它们时，还包括身体区域索引）。这是笔记本中唯一粘合剂的部分（单元格 19），不在上游 `scripts/` 中，`diff_model_train` 需要 它；技能拥有它。
4. `python -m scripts.diff_model_train`（单元格 21），可选的 `python -m scripts.diff_model_infer`。

**通过编辑配置 JSON 来微调，而不是添加标志。** 所有训练/推理超参数（`lr`、`batch_size`、`cache_rate`、推理 `dim`/`spacing`/`num_inference_steps`/`cfg_guidance_scale`、…）都位于 `config_maisi_diff_model_rflow-mr-brain.json`。编辑上游副本，或使用 `--model-config FILE` 传递您自己的（以及 `--env-config` / `--model-def` 用于其他两个）。包装器永远只重写以下字段。

环境 JSON (`environment_maisi_diff_model_rflow-mr-brain.json`) — 包装器根据运行重写的字段：

| 字段 | 设置自 | 备注 |
|---|---|---|
| `data_base_dir` | `--data-base-dir` | 相对 `training[].image` 路径的根。 |
| `json_data_list` | 您的 datalist | 阶段的副本，其中包含每个条目的 `modality` 填充。 |
| `embedding_base_dir`、`model_dir`、`output_dir` | `--output-dir` | 潜在嵌入、检查点、推理图像。 |
| `modality_mapping_path` | 上游 | 将模态名称映射到整数代码。 |
| `model_filename` | `--model-filename` | 输出检查点名称（默认 `diff_unet_3d_rflow-mr-brain_v1.pt`）。 |
| `existing_ckpt_filepath` | 上游权重 / `--existing-ckpt-filepath` | 起始检查点；由 `--train-from-scratch` 清除。 |
| `trained_autoencoder_path` | 上游权重 / `--trained-autoencoder-path` | 用于编码/解码潜力的 VAE。 |

模型配置 (`config_maisi_diff_model_rflow-mr-brain.json`) — 包装器仅触及的字段：

| 字段 | 设置自 | 默认值 | 备注 |
|---|---|---|---|
| `diffusion_unet_train.n_epochs` | `--epochs` | `2`（上游配置发送 `1000`） | 便利覆盖（单元格 15 执行相同操作）；包装器默认值很小，用于验证。 |
| `diffusion_unet_inference.modality` | `--modality` | 来自 `modality_mapping.json` | 与训练模态保持一致，以便可选的 `--run-inference`。 |

该文件中的其他内容（`lr`、`batch_size`、`cache_rate`、`diffusion_unet_inference` 的其余部分）保持原样——通过编辑 JSON 来更改它。

固定的 v1 推理块默认为 `dim=[256,256,128]`、`spacing=[0.94,0.94,1.36]` 和 `cfg_guidance_scale=2`。包装器保留这些字段。较旧的 v0 示例可能显示 `256^3`、1 mm 间距和指导比例 10；使用固定的 v1 JSON 作为执行来源的真实。
