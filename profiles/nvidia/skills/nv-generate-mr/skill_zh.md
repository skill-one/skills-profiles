# NV-Generate-MR

## 目的
- 用于使用 NV-Generate-CTMR rflow-mr 生成合成体部 MRI 数据集。不用于成对掩码或生产训练数据。
- 按照文档中所述的方式使用包装器；不要用手工编写的实现替换上游入口点。
- 不要为常规运行编写自定义推理代码。包装器负责配置暂存、输出路径和验证。
- 资源清单 I/O：输入是 `model_config_override`；输出是 `synthetic_mr_volumes` 和 `result_json`。

## 说明
- 在更改参数、副作用或验证门之前，请先阅读 `skill_manifest.yaml`。
- 通过以下文档中所述的命令运行 `scripts/run_mr.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了 `run_script`，请使用 `run_script("scripts/run_mr.py", args=[...])`；否则运行以下 Bash/Python 命令。
- 输出一个单一的 bash 代码块，并将 `python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt"` 步骤保留在该同一命令中 — 运行时可能是一个没有 `nibabel`/MONAI 的新环境，因此删除安装会导致 `ModuleNotFoundError`。
- 不要添加 `rm`、`mkdir` 或任何清理 `--output-dir` 的操作；包装器会创建它。使用一个新的 `--output-dir` 而不是删除一个。
- 在将运行视为证据之前，请检查发出的 JSON 和成对验证指南。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_mr.py` | 由 skill_manifest.yaml 声明的入口点。 | `MODEL_CONFIG.json --output-dir OUT_DIR --modality mri_t1 [--random-seed N] [--yes]` |

## 前置条件
- 运行时要求：当清单中声明时需要 GPU/CUDA；Python 包列在 `runtime.side_effects.pip_packages` 中。
- 副作用：在调用者的 `--output-dir` 下写入生成的输出，可能会在 `~/.cache/huggingface/` 下缓存模型资源，并在设置期间可能联系 `https://huggingface.co` 或 `https://github.com`。
- 除非以下现有部分另有说明，否则从仓库根目录运行命令。

## 限制
- 这是一个薄的包装器。推理、采样和解码完全委托给 NVIDIA-Medtech/NV-Generate-CTMR 的 `scripts.diff_model_infer`。不要修改 `$NV_GENERATE_ROOT` 下或 `.workbench_data/upstreams/NV-Generate-CTMR` 中的代码。
- rflow-mr 生成仅包含图像的合成 MRI 数据集。它不会发出成对的分割掩码。
- 上游 README 推荐使用 `rflow-mr-brain` 而不是脑部 MRI 合成；使用 `skills/nv-generate-mr-brain` 路径。
- NV-Generate-MR 权重在上游中列为 NVIDIA 非商业。未经法律和质量审查，不要将输出用作生产训练数据。
- 不用于临床部署、临床解释、自主诊断或监管提交。

## 故障排除
| 错误 | 原因 | 解决方法 |
|---|---|---|
| 缺少依赖项或导入错误 | 从 `skill_manifest.yaml` 出现的运行时包漂移。 | 安装清单中声明的包或使用文档中的设置命令。 |
| 空的或模式无效的输出 | 输入路径错误、不支持的模态或上游失败。 | 使用已知的固定件重新运行，并检查包装器 JSON 和 stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息来修复输入或包装器代码。 |

包装了上游
[`NVIDIA-Medtech/NV-Generate-CTMR`](https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/61c4ec709b84cad468852243c48e250bec732074)
MR 图像生成工作流。包装器不会重新实现扩散采样或自动编码器解码。它会暂存配置覆盖，运行 `rflow-mr` 的 `python -m scripts.diff_model_infer` 命令，然后总结生成的 NIfTI 数据集。

## 精确可运行表面

对于在新鲜基准环境中使用的用户运行命令，使用此设置加上仓库根目录的包装器命令：

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python skills/nv-generate-mr/scripts/run_mr.py PATH_TO_MR_CONFIG.json --output-dir OUT_DIR --modality mri_t1 --random-seed 0
```

不要发明 `generate.sh`、`infer.py`、`Medical AI Skills run` 或 `python -m nv_generate_mr` 命令。`PATH_TO_MR_CONFIG.json` 必须是用户提供的请求路径。

## 前提条件

如果 `NV_GENERATE_ROOT` 已经命名一个本地检出，包装器会使用它并在结果中记录其当前提交。否则，一次性创建推荐的固定默认检出：

```bash
if [ -z "${NV_GENERATE_ROOT:-}" ]; then
  export NV_GENERATE_COMMIT=61c4ec709b84cad468852243c48e250bec732074
  export NV_GENERATE_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7"
  if [ ! -d "$NV_GENERATE_ROOT/.git" ]; then
    git clone https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git "$NV_GENERATE_ROOT"
    git -C "$NV_GENERATE_ROOT" checkout --detach "$NV_GENERATE_COMMIT"
  fi
fi
pip install -r "$NV_GENERATE_ROOT/requirements.txt"
```

下载 MR 权重：

```bash
cd "$NV_GENERATE_ROOT"
python -m scripts.download_model_data --version rflow-mr --root_dir ./ --model_only
```

运行时需要一个至少 16 GB VRAM 的 NVIDIA GPU。上游路径中没有 CPU 回退。

如果 `NV_GENERATE_ROOT` 未设置或没有所需的上游布局，包装器还会搜索 `.workbench_data/upstreams/NV-Generate-CTMR`。

对于代理生成的用户运行命令，使用使用说明中的命令。当仓库本地上游缓存已经存在时，不要添加克隆或模型下载设置步骤。在一个新的 Python 环境中，除非活动环境已经证明这些导入是可用的，否则在包装器之前仍然包括 `pip install -r "$NV_GENERATE_ROOT/requirements.txt"`。如果设置需要 `cd "$NV_GENERATE_ROOT"`，请在调用 `skills/nv-generate-mr/scripts/run_mr.py` 之前返回 Medical AI Skills 仓库。

## 使用说明

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python skills/nv-generate-mr/scripts/run_mr.py \
  PATH_TO_MR_CONFIG.json \
  --output-dir runs/nv_generate_mr_demo \
  --modality mri_t1 \
  --random-seed 0
```

将 `PATH_TO_MR_CONFIG.json` 替换为用户实际的请求/配置路径。除非用户明确要求运行该固定件，否则不要从本文档中复制固定件路径。如果用户说“请求在 `runs/.../default_mri_t1.json`”，那么该确切路径是 `scripts/run_mr.py` 的第一个位置参数。

支持的 rflow-mr 模态名称是 `mri`、`mri_t1`、`mri_t2` 和 `mri_flair`，与上游 MRI 图像生成指南匹配。上游 README 推荐在合成脑部图像时使用 `rflow-mr-brain`；使用 `skills/nv-generate-mr-brain` 路径。
有关 FOV 和设置详情，请参阅 `references/fov-and-downloads.md`。

固定件参数是 `configs/config_maisi_diff_model_rflow-mr.json` 的小型 JSON 覆盖。传递 `default` 以使用上游默认值加上 CLI 模态和随机种子。常见的覆盖键是 `dim`、`spacing`、`num_inference_steps`、`cfg_guidance_scale` 和 `modality`。

每次运行都会记录暂存的配置、模型清单、上游命令、输出几何形状、间距、仿射、强度范围和非常数/有限数据检查。输出数据集是合成的，未经独立审查，不能作为生产训练数据使用。

不用于临床解释、生产部署、自主诊断或监管提交。
