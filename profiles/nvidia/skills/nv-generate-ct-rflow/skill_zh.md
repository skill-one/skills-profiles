# NV-Generate-CT (rflow-ct)

## 目的
- 用于使用 NV-Generate-CTMR rflow-ct 生成合成 CT 卷和掩码。不用于未经审核的生产训练数据。
- 精确按照文档使用包装器；不要用手工编写的实现替换上游入口点。
- 不要为常规运行编写自定义推理代码。包装器拥有配置暂存、输出路径、标签映射证据和验证。
- 资源 I/O：输入是 `config_infer_override`；输出是 `synthetic_ct_volumes` 和 `result_json`。

## 说明
- 在更改参数、副作用或验证门之前，先阅读 `skill_manifest.yaml`。
- 通过以下文档中记录的命令运行 `scripts/run_rflow_ct.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露 `run_script`，使用 `run_script("scripts/run_rflow_ct.py", args=[...])`；否则运行以下 Bash/Python 命令。
- 发出一个单一的 bash 代码块，并将 `python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt"` 步骤放在该命令中——运行时可能是没有 `nibabel`/MONAI 的新环境，因此删除安装会导致 `ModuleNotFoundError`。
- 不要添加 `rm`、`mkdir` 或任何 `--output-dir` 的清理；包装器会创建它。使用新的 `--output-dir` 而不是删除一个。
- 在将运行视为证据之前，检查发出的 JSON 和配对的验证指导。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/_anatomy.py` | 主要入口点使用的内部辅助工具。 | 仅导入；不要直接调用。 |
| `scripts/_summary_card.py` | 主要入口点使用的内部辅助工具。 | 仅导入；不要直接调用。 |
| `scripts/list_anatomies.py` | 用于目录或解剖学查找的辅助命令。 | `[--region REGION] [--filter TEXT] [--controllable]` |
| `scripts/run_rflow_ct.py` | 由 skill_manifest.yaml 声明的入口点。 | `CONFIG_INFER.json --output-dir OUT_DIR [--random-seed N] [--version rflow-ct] [--yes]` |
| `scripts/run_ct_mask.py` | 用于独立原始 MAISI 掩码生成的先进诊断辅助工具。 | `REQUEST.json --output-dir OUT_DIR [--random-seed N] [--preflight-only] [--yes]` |
| `scripts/run_ct_from_mask.py` | 用于从 MAISI 标签掩码生成 CT 图像的先进辅助工具。 | `REQUEST.json --output-dir OUT_DIR [--random-seed N] [--yes]` |
| `scripts/run_ct_image.py` | 用于不配对标签的 CT 图像生成的先进辅助工具。 | `MODEL_CONFIG.json --output-dir OUT_DIR [--version rflow-ct] [--random-seed N] [--yes]` |

## 前置条件
- 需要环境变量：`NV_GENERATE_ROOT`。
- 运行时要求：当 manifest 声明时需要 GPU/CUDA；Python 包列在 `runtime.side_effects.pip_packages` 中。
- 副作用：在调用者的 `--output-dir` 下写入生成的输出，可能会在 `~/.cache/huggingface/` 下缓存模型资产，并在设置期间可能联系 `https://huggingface.co` 或 `https://github.com`。
- 除非以下现有部分另有说明，否则从仓库根目录运行命令。

## 限制
- 这是一个薄的包装器。推理、采样和解码完全委托给 NVIDIA-Medtech/NV-Generate-CTMR 的 `scripts.inference`。不要修改 $NV_GENERATE_ROOT 下的代码。
- rflow-ct 需要 CUDA 和 ≈ 16 GB VRAM 最小值，用于默认的 256³ 输出大小。更大的输出大小（例如 512×512×768）需要 A100/H100。
- 输出卷是合成的。它们不安全，不能在没有独立质量审核的情况下用作生产医疗模型的训练数据。
- 不用于临床部署、临床解释、自主诊断、监管提交。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| 缺失依赖或导入错误 | 运行时包从 `skill_manifest.yaml` 的漂移。 | 安装 manifest 中声明的包或使用记录的设置命令。 |
| 空的或模式无效的输出 | 错误的输入路径、不支持的模态或上游失败。 | 使用已知固定件重新运行，并检查包装器 JSON 和 stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息来修复输入或包装器代码。 |

包装了上游
[`NVIDIA-Medtech/NV-Generate-CTMR`](https://github.com/NVIDIA-Medtech/NV-Generate-CTMR/tree/61c4ec709b84cad468852243c48e250bec732074)
校正流合成管道。包装器不会重新实现扩散、采样或自动编码器解码——它按项目 README 文档中描述的精确方式将 `scripts.inference` 入口点外壳化，并检查生成的图像/掩码对。

## 前置条件

1. 如果 `NV_GENERATE_ROOT` 已经命名本地检出，包装器使用它并在结果中记录其当前提交。否则，创建推荐的固定默认检出（一次性）：

   ```bash
   if [ -z "${NV_GENERATE_ROOT:-}" ]; then
     export NV_GENERATE_COMMIT=61c4ec709b84cad468852243c48e250bec732074
     export NV_GENERATE_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7"
     if [ ! -d "$NV_GENERATE_ROOT/.git" ]; then
       git clone https://github.com/NVIDIA-Medtech/NV-Generate-CTMR.git "$NV_GENERATE_ROOT"
       git -C "$NV_GENERATE_ROOT" checkout --detach "$NV_GENERATE_COMMIT"
     fi
   fi
   python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt"
   ```

2. 将 `rflow-ct` 权重**和**掩码候选数据集下载到克隆中（一次性，≈ 5.5 GB）：

   ```bash
   cd "$NV_GENERATE_ROOT"
   python -m scripts.download_model_data --version rflow-ct --root_dir "./"
   ```

   掩码候选（`datasets/all_masks_flexible_size_and_spacing_4000`）调节扩散采样器；通过 `--model_only` 忽略它们会导致启动时出现缺少文件错误。解剖大小条件文件也是完整 CT 下载的一部分，并且对于可控掩码生成是必需的。

3. NVIDIA GPU，≥ 16 GB VRAM 和 CUDA。没有 CPU 回退。

对于代理生成的用户运行命令，优先使用用法中的短包装器命令。当 `NV_GENERATE_ROOT` 或仓库本地上游缓存已经存在时，不要在前面添加克隆或模型下载设置步骤。在一个新的 Python 环境中，除非活动环境已经证明这些导入是可用的，否则仍然在包装器之前包含 `python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt"`；缓存的权重不意味着缓存的 Python 包。从 medical-AI-skills 仓库根目录运行包装器。如果设置需要 `cd "$NV_GENERATE_ROOT"`，在调用 `skills/nv-generate-ct-rflow/scripts/run_rflow_ct.py` 之前返回 Medical AI Skills 仓库。

## 用法

```bash
export NV_GENERATE_ROOT="${NV_GENERATE_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7}" && \
python -m pip install -r "$NV_GENERATE_ROOT/requirements.txt" && \
python skills/nv-generate-ct-rflow/scripts/run_rflow_ct.py \
  PATH_TO_CONFIG_INFER.json \
  --output-dir runs/nv_generate_ct_rflow_demo \
  --random-seed 0 \
  --version rflow-ct
```

将 `PATH_TO_CONFIG_INFER.json` 替换为用户的实际请求/配置路径。不要从本文档复制固定件路径，除非用户明确要求运行该固定件。如果用户说“案例请求在 `runs/.../chest_lung_tumor_controllable.json`”，那么该确切路径是 `scripts/run_rflow_ct.py` 的第一个位置参数。

固定件参数是一个 `config_infer.json` 覆盖文件：它可以替换 `num_output_samples`、`body_region`、`anatomy_list`、`controllable_anatomy_size`、`output_size` 和 `spacing`。传递 `default` 以使用上游配置逐字。包装器在运行之前将覆盖暂存到上游树中。

### 固定件目录

`fixtures/` 提供了针对常见配对合成用例的精选配置：胸部肺叶、胸部带可控肺肿瘤、腹部实器官、腹部带可控肝肿瘤、头部 + 颈椎、骨盆。有关完整表格，请参阅 [`fixtures/README.md`](fixtures/README.md)。

### 辅助命令

```bash
# 浏览按身体区域分组的 132 类 label_dict。
python skills/nv-generate-ct-rflow/scripts/list_anatomies.py --region chest
python skills/nv-generate-ct-rflow/scripts/list_anatomies.py --controllable
python skills/nv-generate-ct-rflow/scripts/list_anatomies.py --filter tumor

# 验证固定件并在不启动推理的情况下预览成本。
NV_GENERATE_ROOT=$HOME/.cache/nvidia-skills/upstreams/NV-Generate-CTMR-61c4ec7 \
  python skills/nv-generate-ct-rflow/scripts/run_rflow_ct.py \
    skills/nv-generate-ct-rflow/fixtures/abdomen_liver_spleen.json \
    --output-dir runs/preview --preflight-only
```

高级辅助工具保留在此技能中用于调试和不太常见的 CT 生成模式。仅在用户明确要求该模式时使用它们：

```bash
# 原始 MAISI 掩码诊断，用于检查肺肿瘤 -> 标签 23。
python skills/nv-generate-ct-rflow/scripts/run_ct_mask.py \
  skills/nv-generate-ct-rflow/fixtures/ct_mask_lung_tumor.json \
  --output-dir runs/ct_mask_debug --preflight-only

# 从现有的 MAISI 标签掩码生成 CT 图像，身体标签 200。
python skills/nv-generate-ct-rflow/scripts/run_ct_from_mask.py \
  skills/nv-generate-ct-rflow/fixtures/ct_from_mask_request_example.json \
  --output-dir runs/ct_from_mask_demo

# 不配对标签的 CT 图像生成。
python skills/nv-generate-ct-rflow/scripts/run_ct_image.py \
  skills/nv-generate-ct-rflow/fixtures/ct_image_only_default.json \
  --output-dir runs/ct_image_only_demo --version rflow-ct
```

包装器在每次调用时都会进行预检（无论 `--preflight-only` 如何）：配置模式边界、解剖名称与上游 label_dict 匹配、body_region 在支持集中、controllable_anatomy_size 约束、上游 CT 输出大小/间距合同、body-region 感知的 x/y FOV 最小值、`$NV_GENERATE_ROOT/datasets/` 下的数据集存在、CUDA 可用，以及估计的峰值 VRAM / 墙上时间。估计超过 5 分钟墙上时间或 30 GB 峰值 VRAM 的运行需要 `--yes` 才能继续。

每次调用都会运行 `python -m scripts.inference -t configs/config_network_rflow.json
-i configs/config_infer.json -e configs/environment_rflow-ct.json --random-seed <s>
--version rflow-ct`。输出证据记录了上游 git 提交、模型检查点哈希、渲染的配置、每样本图像/掩码几何形状、掩码标签集、图像 HU 范围摘要和每类体素体积。

当 `controllable_anatomy_size` 非空时，上游忽略更广泛的 `anatomy_list` 以保存配对标签图，并过滤标签到可控解剖名称。保存的配对标签值是本地 `1..N` 序数，不是原始 MAISI 标签 ID。阅读 `output.output_label_mapping` 在 `result_json` 中将保存输出标签映射回源标签；例如，输出标签 `1` 可以表示 MAISI 标签 `23` (`lung tumor`)。
对于精选的肺肿瘤示例，优先选择 `0.5` 或更大的可控大小；较小的请求（如 `0.2`）可能会在某些种子上产生缺失或极小的标签-23 组件。

有关 FOV 和设置详情，请参阅 `references/fov-and-downloads.md`。对于高级辅助工具标签空间详情，请参阅
`references/ct-mask-label-space.md` 和 `references/ct-from-mask-format.md`。

### 视觉样本卡

除了 NIfTI 对，包装器还会将 `summary.html` 写入输出目录：每个样本的中片三联画（轴向 / 冠状 / 矢状）带标签叠加，以及渲染配置和验证者面向的汇总表。让你在不启动 3D Slicer 的情况下直观查看结果。传递 `--no-summary-card` 以跳过。

解剖合理性（标签集合理性、体素 HU 范围作为 CT、图像/掩码几何形状匹配、声明的输出标签存在、肺叶 HU 底部）由 `verifiers/ct_synthesis_quality_v1` 检查。

不用于临床解释、生产部署的训练数据或任何非合成研究用途。
