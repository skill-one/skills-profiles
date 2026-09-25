# NV-Segment-CT

## 目的
- 用于在CT NIfTI体积上运行NV-Segment-CT VISTA3D并记录标签图证据。不用于临床解释。
- 按照文档中所述的方式使用包装器；不要用手工编写的实现替换上游入口点。
- 资源清单I/O：输入是`ct_volume`；输出是`label_map`和`result_json`。

## 说明
- 修改参数、副作用或验证门之前，请先阅读`skill_manifest.yaml`。
- 通过以下文档中所述的命令运行`scripts/run_vista3d.py`；将输出保持在调用者提供的运行目录下。
- 如果主机代理暴露了`run_script`，请使用`run_script("scripts/run_vista3d.py", args=[...])`；否则运行以下Bash/Python命令。
- 创建文档中所述的Python 3.10虚拟环境，并直接调用其可执行文件；不要将模型依赖项安装到调用者的活动环境中。
- 在将运行视为证据之前，请检查发出的JSON和配对的验证指导。

## 可用脚本
| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_vista3d.py` | 由skill_manifest.yaml声明的入口点。 | `PATH_TO_CT.nii.gz [--output-dir OUT_DIR] [--label-prompts IDS]` |

## 前置条件
- 运行时要求：Python 3.10支持`venv`，并在资源清单中声明时需要GPU/CUDA。模型包来自固定的上游资源清单文件；仅在本地添加与包装器相关的包。
- 副作用：在`~/.cache/nvidia-skills/venvs/nv-segment-ct-f9f5f51/`下创建隔离环境，在`skills/nv-segment-ct/bundle/`下写入下载的捆绑包，可能缓存模型资产在`~/.cache/huggingface/`，在首次设置期间可能联系`https://huggingface.co`和`https://raw.githubusercontent.com`；可选的脾脏固定件获取器从`https://msd-for-monai.s3-us-west-2.amazonaws.com`下载MSD09。
- 除非下文现有部分另有说明，否则从仓库根目录运行命令。

## 限制
- 这是一个薄的包装器。推理、预处理和后处理完全委托给捆绑包中的官方`hugging_face_pipeline.HuggingFacePipelineHelper`。不要修改`bundle/`下的代码。
- `transformers==4.46.3`是与上游资源清单的Torch 2.0.1兼容的包装器；较新的Transformers版本可以禁用那个旧的Torch后端。
- 固定的上游资源清单包括Torch 2.0.1。仅使用固定的NVIDIA模型资产；不要在这个遗留复现环境中加载不受信任的检查点。
- 设备自动检测（如果可用则为cuda，否则为cpu）；`--device`标志可以覆盖。
- 输出可能是模式有效的，但语义上为空（例如，与输入解剖结构不匹配的标签提示）。合理检查门断言每个请求的解剖结构至少有一个前景体素。
- 不用于临床部署、临床解释、自主诊断、监管提交。

## 故障排除
| 错误 | 原因 | 修复 |
|---|---|---|
| 创建环境时`ensurepip is not available` | 主机Python安装省略了其操作系统的`venv`包。 | 安装匹配的Python 3.10 venv支持包，或使用`virtualenv -p python3.10`创建相同的隔离环境。 |
| 缺少依赖项或导入错误 | 从`skill_manifest.yaml`的运行时包漂移。 | 安装资源清单中声明的包或使用文档中所述的设置命令。 |
| 空或模式无效的输出 | 输入路径错误、不支持的模态或上游失败。 | 使用已知的固定件重新运行，并检查包装器JSON和stderr。 |
| 验证门失败 | 输出违反了声明的工程不变量。 | 保留失败的证据包，并使用门消息来修复输入或包装器代码。 |

包装了上游`nvidia/NV-Segment-CT`辅助工具。包装器不重新实现VISTA3D推理。

## 精确可运行表面

对于CT分割用户运行，请使用此仓库根目录包装器路径：

```bash
"$NV_SEGMENT_CT_VENV/bin/python" skills/nv-segment-ct/scripts/run_vista3d.py PATH_TO_CT.nii.gz --label-prompts "1,3,5,14" --output-dir OUT_DIR
```

不要发明`infer.py`、`Medical AI Skills run`、`python -m nv_segment_ct`或仅包含解剖名称的标志。对于脾脏、肝脏、右肾脏和左肾脏，所需的VISTA3D标签ID正好是`1,3,5,14`。

## 前提条件

该技能假设一个具有`venv`支持的Python 3.10解释器。其文档中所述的命令创建一个专用环境，并从`NV-Segment-CT/requirements.txt`安装模型依赖项，该不可变NVIDIA-Medtech提交为`f9f5f51b589e5dc9c23c453cf5138398e4084056`。Hugging Face捆绑包本身不包含`requirements.txt`。

两个一次性下载（文档中所述的命令执行第一个；固定件获取器是一个单独的步骤，在引导时运行）：

```bash
# 脾脏示例固定件来自Decathlon MSD09 (~1.5 GB tar，~11 MB
# 固定件提取到skills/nv-segment-ct/fixtures/spleen_03.nii.gz)：
python skills/nv-segment-ct/fixtures/fetch_spleen_fixture.py
```

两个下载（捆绑包下方，和固定件）都被git忽略（Medical AI Skills政策：git中不包含医疗数据或模型权重）。获取脚本是无副作用的，并将tar缓存到`.workbench_data/datasets/`，因此重新运行是无操作的。

运行时需要一个带有CUDA的NVIDIA GPU。CPU回退是支持的，但很慢。

## 使用

从技能仓库根目录运行完整的引导。直接调用虚拟环境的可执行文件，以防止修改调用者的活动环境：

```bash
export NV_SEGMENT_CT_VENV="${NV_SEGMENT_CT_VENV:-$HOME/.cache/nvidia-skills/venvs/nv-segment-ct-f9f5f51}"
export NV_SEGMENT_CT_REQUIREMENTS="${NV_SEGMENT_CT_REQUIREMENTS:-https://raw.githubusercontent.com/NVIDIA-Medtech/NV-Segment-CTMR/f9f5f51b589e5dc9c23c453cf5138398e4084056/NV-Segment-CT/requirements.txt}"

if [ ! -x "$NV_SEGMENT_CT_VENV/bin/python" ]; then
  python3.10 -m venv "$NV_SEGMENT_CT_VENV"
fi

"$NV_SEGMENT_CT_VENV/bin/python" -m pip install \
  -r "$NV_SEGMENT_CT_REQUIREMENTS" \
  "transformers==4.46.3" \
  "typer>=0.9"

"$NV_SEGMENT_CT_VENV/bin/hf" download nvidia/NV-Segment-CT \
  --revision afb51518689f71e6abb367ee6301b2cd0225c66a \
  --local-dir skills/nv-segment-ct/bundle/

"$NV_SEGMENT_CT_VENV/bin/python" skills/nv-segment-ct/scripts/run_vista3d.py PATH_TO_CT.nii.gz \
  --label-prompts "1,3,5,14" \
  --output-dir vista3d_outputs
```

当用户指定解剖结构时，在运行之前将它们转换为VISTA3D类ID。对于常见的腹部CT请求：

| 解剖结构 | VISTA3D类ID |
|---|---:|
| 肝脏 | 1 |
| 脾脏 | 3 |
| 右肾脏 | 5 |
| 左肾脏 | 14 |

对于"分割脾脏、肝脏、右肾脏和左肾脏"，正确的`--label-prompts`值正好是`"1,3,5,14"`。不要用另一个标签字典中的肾脏ID替换；包装器会验证请求的标签集，如果发出的掩码包含请求集之外的标签，则会将运行标记为无效。

安装和下载步骤是承重的。固定的上游文件拥有模型环境，而Transformers和Typer支持这个薄的包装器。`hf download`将~832 MB的模型捆绑包拉入`skills/nv-segment-ct/bundle/`；后续调用会重用缓存。

`label-prompts`是VISTA3D类ID。证据输出记录输入几何形状、输出掩码路径、观察到的标签ID、意外标签、每类体素计数、每类物理体积（根据输出掩码头间距计算）、运行时、模型身份和固定代码派生的检查，例如掩码形状、仿射匹配、标签集、前景体素计数和类体积边界。

传递`--ground-truth PATH`以在`input.ground_truth_path`下记录参考标签图路径。该技能不计算Dice；那是配对验证器的工作。

解剖结构合理性（每类体积边界、碎片化、双侧对称性、肝脏大于脾脏）和可选的每类Dice/IoU相对于记录的地面真实是`verifiers/ct_segmentation_quality_v1`检查的。

不用于临床解释、生产部署或非CT模态。
