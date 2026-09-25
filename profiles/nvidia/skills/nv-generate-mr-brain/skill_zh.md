# NV-Generate-MR-Brain

## 目的
- 用于使用 NV-Generate-CTMR rflow-mr-brain v1 生成合成 T1、T2、FLAIR、SWI 或 MRA 脑部 MRI 体积。不用于生产训练数据。
- 按照文档中所述的方式使用包装器；不要用手工编写的实现替换上游入口点。
- 不要为常规运行编写自定义推理代码。包装器拥有配置暂存、输出路径和验证。
- 资源清单 I/O：输入是 `model_config_override`；输出是 `synthetic_mr_brain_volumes` 和 `result_json`。

## 说明
- 在更改参数、副作用或验证门之前，请先阅读 `skill_manifest.yaml`。
- 通过以下文档中记录的命令运行 `scripts/run_mr_brain.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了 `run_script`，请使用 `run_script("scripts/run_mr_brain.py", args=[...])`；否则运行以下 Bash/Python 命令。
- 对于命令形状审查，不要安装包、克隆存储库、下载权重或启动 GPU 推理。仅发出带有提供的配置路径以及显式的 `--output-dir`、`--modality` 和 `--random-seed` 值的确切包装器命令。
- 对于可执行运行，发出单个 bash 代码块，并将 `python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt"` 步骤保留在该相同命令中——运行时可能是没有 `nibabel`/MONAI 的新环境，因此删除安装会失败 `ModuleNotFoundError`。
- 如果选择 `--modality mri_mra`，请说明上游报告稀疏 MRA 训练覆盖率，并且输出质量没有保证。
- 不要添加 `rm`、`mkdir` 或任何清理 `--output-dir`；包装器会创建它。使用新的 `--output-dir` 而不是删除一个。
- 在将运行视为证据之前，请检查发出的 JSON 和配对的验证指导。

## 示例

仅进行命令形状审查（无设置或执行）：

```bash
python skills/nv-generate-mr-brain/scripts/run_mr_brain.py \
  PATH_TO_MR_BRAIN_CONFIG.json \
  --output-dir runs/nv_generate_mr_brain_demo \
  --modality mri_t1 \
  --random-seed 1234
```

对于可执行运行，使用在 [使用](#usage) 下设置的感知命令。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_mr_brain.py` | 由 skill_manifest.yaml 声明的首选入口点。 | `MODEL_CONFIG.json --output-dir OUT_DIR --modality mri_t1 [--random-seed N] [--yes]` |

## 前置条件
- 运行时要求：当资源清单中声明时需要 GPU/CUDA；Python 包列在 `runtime.side_effects.pip_packages` 中。
- 副作用：在调用者的 `--output-dir` 下写入生成的输出，可能会在 `~/.cache/huggingface/` 下缓存模型资产，并在设置期间可能联系 `https://huggingface.co` 或 `https://github.com`。
- 从存储库根目录运行命令，除非以下现有部分另有说明。

## 限制
- 这是一个薄的包装器。推理、采样和解码完全委托给 NVIDIA-Medtech/NV-Generate-CTMR 的 `scripts.diff_model_infer`。不要修改 $NV_GENERATE_ROOT 下或 .workbench_data/upstreams/NV-Generate-CTMR 的代码。
- rflow-mr-brain 生成仅包含图像的合成脑部 MRI 体积。它不会发出配对的分割掩码。
- 输出体积是合成的。它们在没有独立质量审查的情况下不安全作为生产医疗模型训练数据。
- 不用于临床部署、临床解释、自主诊断、监管提交。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| 缺少依赖项或导入错误 | 从 `skill_manifest.yaml` 出现运行时包漂移。 | 安装资源清单中声明的包或使用记录的设置命令。 |
| 空的或模式无效的输出 | 错误的输入路径、不支持的模态或上游失败。 | 使用已知固定件重新运行并检查包装器 JSON 和 stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包并使用门消息来修复输入或包装器代码。 |

包装了上游
[`NVIDIA-Medtech/NV-Generate-CTMR`](https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/da438fec6484cdb6f421f8c7051d954ebefff730)
MR 脑部图像仅生成工作流。包装器不会重新实现扩散采样或自动编码器解码。它会暂存配置覆盖，运行为 `rflow-mr-brain` 的记录的 `python -m scripts.diff_model_infer` 命令，然后总结生成的 NIfTI 体积。

## 精确可运行表面

对于用户运行命令，请使用此存储库根目录包装器路径：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-da438fe}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python skills/nv-generate-mr-brain/scripts/run_mr_brain.py PATH_TO_MR_BRAIN_CONFIG.json --output-dir OUT_DIR --modality mri_t1 --random-seed 1234
```

不要发明 `generate.sh`、`infer.py`、`Medical AI Skills run` 或 `python -m nv_generate_mr_brain` 命令。`PATH_TO_MR_BRAIN_CONFIG.json` 必须是用户提供的请求路径。

## 前提条件

如果 `NV_GENERATE_ROOT` 已经命名本地检出，包装器会使用它并记录其当前提交在结果中。否则，创建推荐的固定默认检出一次：

```bash
if [ -z "${NV_GENERATE_ROOT:-}" ]; then
  export NV_GENERATE_COMMIT=da438fec6484cdb6f421f8c7051d954ebefff730
  export NV_GENERATE_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-da4fe"
  if [ ! -d "$NV_GENERATE_ROOT/.git" ]; then
    git clone https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git "$NV_GENERATE_ROOT"
    git -C "$NV_GENERATE_ROOT" checkout --detach "$NV_GENERATE_COMMIT"
  fi
fi
pip install -r "$NV_GENERATE_ROOT/requirements.txt"
```

包装器仅在 `NV_GENERATE_ROOT` 位于确切资源清单提交并且其跟踪文件干净时执行上游代码。在 `models/` 下保持模型权重未跟踪，并使用包装器覆盖 JSON 而不是编辑上游配置。子进程仅接收运行时、CUDA、区域设置和证书变量的允许列表；API 密钥、令牌、密码和无关的父环境值不会被转发。

从其确切资源清单修订版下载重用的自动编码器和 MR-Brain v1 检查点：

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

包装器在启动推理之前会验证下载的两个文件与其发布的 Git LFS SHA-256 对象 ID。

运行时需要一个至少 16 GB VRAM 的 NVIDIA GPU。上游路径中没有 CPU 回退。

包装器还会搜索 `.workbench_data/upstreams/NV-Generate-CTMR`，如果 `NV_GENERATE_ROOT` 未设置或不具有所需的上游布局。

对于代理生成的用户运行命令，使用使用中的命令。当存储库本地上游缓存已存在时，不要在包装器之前添加克隆或模型下载设置步骤。在一个新的 Python 环境中，仍然在包装器之前包含 `pip install -r "$NV_GENERATE_ROOT/requirements.txt"`，除非活动环境已经证明这些导入是可用的；缓存的权重不意味着缓存的 Python 包。如果设置需要 `cd "$NV_GENERATE_ROOT"`，请在调用 `skills/nv-generate-mr-brain/scripts/run_mr_brain.py` 之前返回 Medical AI Skills 存储库。

## 使用

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-da438fe}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python skills/nv-generate-mr-brain/scripts/run_mr_brain.py \
  PATH_TO_MR_BRAIN_CONFIG.json \
  --output-dir runs/nv_generate_mr_brain_demo \
  --modality mri_t1 \
  --random-seed 1234
```

将 `PATH_TO_MR_BRAIN_CONFIG.json` 替换为用户的实际请求/配置路径。不要从本文件中复制固定件路径，除非用户明确要求运行该固定件。如果用户说“请求在 `runs/.../default_mri_t1.json`”，那么该确切路径是 `scripts/run_mr_brain.py` 的第一个位置参数。

支持的 MR-brain 模态名称是 `mri`、`mri_t1`、`mri_t2`、`mri_flair`、`mri_mra`、`mri_swi`、`mri_t1_skull_stripped`、`mri_t2_skull_stripped`、`mri_flair_skull_stripped`、`mri_mra_skull_stripped` 和 `mri_swi_skull_stripped`。这些映射到上游 `configs/modality_mapping.json` ID，在 README 中有记录。对于 FOV 和设置细节，请参阅 `references/fov-and-downloads.md`。

固定的 v1 配置提供轴向 T1w 默认值 `dim=[256,256,128]`、`spacing=[0.94,0.94,1.36]`、30 推理步骤和 `cfg_guidance_scale=2`。除非特定模型验证证明需要覆盖，否则保留暂存配置值；旧示例可能描述 v0 `256^3`/1 mm 几何形状或指导比例 10。v1 支持MRA，但上游训练数据报告中的 MRA 扫描很少，因此输出质量没有保证。

固定件参数是 `configs/config_maisi_diff_model_rflow-mr-brain.json` 的小型 JSON 覆盖。传递 `default` 以使用上游默认值加上 CLI 模态和随机种子。常见的覆盖键是 `dim`、`spacing`、`num_inference_steps`、`cfg_guidance_scale` 和 `modality`。

每次运行都会记录暂存配置、模型清单、上游命令、输出几何形状、间距、仿射、强度范围和非常数/有限数据检查。输出体积是合成的，如果没有独立审查，它们不安全作为生产训练数据。

不用于临床解释、生产部署、自主诊断或监管提交。
