# NV-Segment-CTMR

## 目的
- 用于在CT或MRI NIfTI体积上运行NV-Segment-CTMR并记录标签图证据。不用于临床解释。
- 按照文档中所述的方式使用包装器；不要用手工编写的实现替换上游入口点。
- 资源清单I/O：输入是`ct_or_mr_volume`；输出是`label_map`和`result_json`。

## 说明
- 在更改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 通过以下文档中所述的命令运行`scripts/run_ctmr.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了`run_script`，请使用`run_script("scripts/run_ctmr.py", args=[...])`；否则运行以下Bash/Python命令。
- 在将运行视为证据之前，请检查发出的JSON和配对的验证指南。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_ctmr.py` | 由skill_manifest.yaml声明的入口点。 | `PATH_TO_IMAGE.nii.gz --output-dir OUT_DIR --modality CT_BODY [--label-prompts IDS]` |

## 前置条件
- 运行时要求：当资源清单中声明时需要GPU/CUDA；Python包列在`runtime.side_effects.pip_packages`中。
- 可选环境变量：`NV_SEGMENT_CTMR_ROOT`选择受信任的上游检出；`CUDA_VISIBLE_DEVICES`限制可见的GPU；`MONAI_DATA_DIRECTORY`和`PYTORCH_CUDA_ALLOC_CONF`在需要时覆盖包装器的输出本地缓存和分配器默认值。
- 副作用：在调用者的`--output-dir`下写入分割输出，可能缓存模型资源在`~/.cache/huggingface/`下，并在设置期间可能联系`https://github.com`或`https://huggingface.co`。
- 从仓库根目录运行命令，除非以下现有部分另有说明。

## 限制
- 这是一个薄的包装器。推理、预处理和后处理完全委托给$NV_SEGMENT_CTMR_ROOT或工作区本地回退`.workbench_data/upstreams/NV-Segment-CTMR/NV-Segment-CTMR`的上游MONAI包。
- 默认包装器路径对CT_BODY、MRI_BODY或MRI_BRAIN运行自动"分割所有内容"的推理。MRI_BRAIN输入必须已经遵循上游脑预处理要求。
- 标签名称在可用时从上游配置加载。如果缺少标签字典，包装器仍然记录标签ID并将仅负ID标记为无效。
- 无临床、诊断、监管或治疗计划声明。
- 不用于临床部署、临床解释、自主诊断或监管提交。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| 缺少依赖项或导入错误 | 从`skill_manifest.yaml`的运行时包漂移。 | 安装资源清单中声明的包或使用文档中的设置命令。 |
| 空的或模式无效的输出 | 错误的输入路径、不支持的模态或上游失败。 | 使用已知固定件重新运行并检查包装器JSON和stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包并使用门消息来修复输入或包装器代码。 |

包装了上游
[`NVIDIA-Medtech/NV-Segment-CTMR`](https://github.com/NVIDIA-Medtech/NV-Segment-CTMR/tree/cb921f5c58837c0f42a713855d68b32af88e1cdd/NV-Segment-CTMR)
CT/MRI分割包。包装器不会重新实现VISTA3D推理。它调用文档中的`python -m monai.bundle run`入口点，然后检查生成的NIfTI标签图。

## 精确可运行表面

对于CT身体分割用户运行和基准答案，请精确使用以下安全的新环境仓库根命令：

```bash
export NV_SEGMENT_CTMR_ROOT="${NV_SEGMENT_CTMR_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Segment-CTMR-cb921f5/NV-Segment-CTMR}" && \
python -m pip install "monai>=1.5,<1.6" "numpy<2" nibabel scipy typer PyYAML fire huggingface_hub pytorch-ignite einops && \
python skills/nv-segment-ctmr/scripts/run_ctmr.py PATH_TO_IMAGE.nii.gz --modality CT_BODY --output-dir OUT_DIR
```

不要发明`python -m nv_segment_ctmr`、`infer.py`或`Medical AI Skills run`命令。`PATH_TO_IMAGE.nii.gz`必须是用户提供的输入路径。
对于基准/用户运行答案，如果bash块包含`mkdir -p .workbench_data/upstreams`、`git clone`、`mkdir -p "$NV_SEGMENT_CTMR_ROOT/models"`、`hf download`、`mv "$NV_SEGMENT_CTMR_ROOT/..."`或任何其他在共享上游检出中创建、下载或移动文件的命令，则该bash块无效。

## 前提条件

仅限一次性维护者设置；不要将这些命令包含在用户答案或基准命令中。基准环境已经提供了仓库本地上游缓存和模型文件。

如果`NV_SEGMENT_CTMR_ROOT`已经命名本地包检出，包装器会使用它并在结果中记录其当前提交。否则，一次性克隆推荐的固定默认值：

```bash
if [ -z "${NV_SEGMENT_CTMR_ROOT:-}" ]; then
  export NV_SEGMENT_CTMR_COMMIT=cb921f5c58837c0f42a713855d68b32af88e1cdd
  export NV_SEGMENT_CTMR_CHECKOUT="$HOME/.cache/nvidia-skills/upstreams/NV-Segment-CTMR-cb921f5"
  if [ ! -d "$NV_SEGMENT_CTMR_CHECKOUT/.git" ]; then
    git clone https://github.com/NVIDIA-Medtech/NV-Segment-CTMR.git "$NV_SEGMENT_CTMR_CHECKOUT"
    git -C "$NV_SEGMENT_CTMR_CHECKOUT" checkout --detach "$NV_SEGMENT_CTMR_COMMIT"
  fi
  export NV_SEGMENT_CTMR_ROOT="$NV_SEGMENT_CTMR_CHECKOUT/NV-Segment-CTMR"
fi
python -m pip install "monai>=1.5,<1.6" "numpy<2" nibabel scipy typer PyYAML fire huggingface_hub pytorch-ignite einops && \
python -c "import monai, nibabel, numpy"

mkdir -p "$NV_SEGMENT_CTMR_ROOT/models"
test -e "$NV_SEGMENT_CTMR_ROOT/models/model.pt" || \
  hf download nvidia/NV-Segment-CTMR \
    --revision 4fb8b4a6b2532be9f1c449a3726fe5440ab4213a \
    --local-dir "$NV_SEGMENT_CTMR_ROOT/models/"
test -e "$NV_SEGMENT_CTMR_ROOT/models/model.pt" || \
  mv "$NV_SEGMENT_CTMR_ROOT/models/vista3d_pretrained_model/model.pt" \
    "$NV_SEGMENT_CTMR_ROOT/models/model.pt"
```

包装器还会搜索`.workbench_data/upstreams/NV-Segment-CTMR/NV-Segment-CTMR`，如果`NV_SEGMENT_CTMR_ROOT`未设置或没有所需的包布局。

对于代理生成的用户运行命令，请使用用法中的命令。不要将一次性前提条件块复制到答案中：不要在`$NV_SEGMENT_CTMR_ROOT`下创建或写入，不要运行`hf download`，并且在基准或用户运行期间不要在共享上游检出中移动文件。在Python 3.12环境中不要预加`pip install -r "$NV_SEGMENT_CTMR_ROOT/requirements.txt"`；上游要求固定NumPy 1.24.4，它在那里无法干净地构建。在一个新的Python环境中，在包装器之前安装最小的兼容运行时（`monai>=1.5,<1.6`、`numpy<2`、`nibabel`、`scipy`、`typer`、`PyYAML`、`fire`、`huggingface_hub`、`pytorch-ignite`、`einops`）。缓存的模型不意味着缓存的Python包。

运行时需要一个带有CUDA的NVIDIA GPU。上游包可能在仅CPU的主机上导入，但此技能声明为需要CUDA，因为发布的流程是一个3D CT/MRI基础模型推理路径。

## 用法

从Medical AI Skills仓库根目录：

```bash
export NV_SEGMENT_CTMR_ROOT="${NV_SEGMENT_CTMR_ROOT:-$HOME/.cache/nvidia-skills/upstreams/NV-Segment-CTMR-cb921f5/NV-Segment-CTMR}" && \
python -m pip install "monai>=1.5,<1.6" "numpy<2" nibabel scipy typer PyYAML fire huggingface_hub pytorch-ignite einops && \
python skills/nv-segment-ctmr/scripts/run_ctmr.py PATH_TO_IMAGE.nii.gz \
  --modality CT_BODY \
  --output-dir runs/nv_segment_ctmr_demo
```

将`PATH_TO_IMAGE.nii.gz`替换为用户的实际输入路径。不要将示例固定件路径复制到用户运行中。如果用户在`runs/`下提供了一个明确的输入路径，则该路径必须是`scripts/run_ctmr.py`的第一个位置参数。

支持的自动分割模态是`CT_BODY`、`MRI_BODY`和`MRI_BRAIN`。对于`MRI_BRAIN`，上游README要求在包推理之前进行脑特定预处理；将一个已经预处理的图像传递给此包装器。

传递`--label-prompts "3,14"`以请求特定的上游类ID，而不是仅模态级别的"分割所有内容"集。证据输出记录输入几何形状、输出掩码路径、观察到的标签ID、意外标签、每类体素计数、每类物理体积从掩码头空间、运行时、上游命令、模型清单和几何形状检查。

传递`--ground-truth PATH`以在`input.ground_truth_path`下记录参考标签图路径。该技能不会计算Dice；那是配对验证器的工作。

解剖学合理性和可选的每类Dice/IoU相对于记录的地面真实可以由`verifiers/ct_segmentation_quality_v1`检查CT身体输出。

不用于临床解释、生产部署、自主诊断或监管提交。
