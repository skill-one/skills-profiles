# NV-Segment-CT Finetune

## 目的

- 用于在CT NIfTI标签上对NV-Segment-CT VISTA3D进行烟测或数据集微调，包括上游固定通道softmax工作流和可选的MLflow跟踪。不用于临床验证。
- 封装了上游MONAI包入口点；不要用手工编写的训练或推理代码替换它。
- 配置文件输入包括`dataset_dir`、`datalist`、`target_anatomy`、`label_mapping`、`smoke`、`sanity`、`auto_seg`、`softmax`、`skip_formal_eval`、`mlflow_tracking_uri`、`mlflow_experiment_name`和`mlflow_run_name`。
- 配置文件输出包括`finetuned_ckpt`和模式校验的`result_json`。

## 说明

- 仅运行调用者请求的预设、数据集、输出目录和计算预算。依赖设置和远程跟踪需要调用者批准。报告结果后停止；进一步训练、发布或部署是单独的请求。
- 运行`scripts/run_finetune.py`；在正常技能使用期间不要修补`bundle/`下的文件或上游检出。
- 对于独立的Bash，请在包装器之前包含新鲜环境设置行；基准venv环境为空。
- 从仓库根目录就地运行提交的脚本。不要将此技能复制到运行时目录，并在生成的调用中不要使用`rm`或清理命令。
- 如果主机暴露`run_script`，则使用`run_script("scripts/run_finetune.py", args=[...])`；否则从仓库根目录运行。
- 对于最短工作流检查，使用`--smoke`；对于MSD Task06 Lung Tumor重现，使用`--sanity`。
- 使用以下标准选择标准工作流和`--softmax`工作流。不要将`--softmax`与`--auto-seg`或`--sanity`组合。
- 将`--mlflow-experiment-name`设置为启用训练阶段的MLflow。`--mlflow-tracking-uri`和`--mlflow-run-name`需要实验名称。正式的预/后评估不会接收MLflow凭证。
- 仅在需要Task06参考详细信息、输出字段定义或手动包设置说明时才读取`references/task06-and-results.md`。

## 选择工作流

仅当所有这些条件都满足时才使用`--softmax`：

- 在训练之前已知完整的类别集，并且在推理请求之间不会变化。
- 标签是互斥的：每个体素是背景或恰好一个前景类别。
- 每个前景数据集标签都映射到现有的VISTA3D类ID，并且希望使用传统的固定通道输出。

如果点提示必须保持可用，类别是在推理时动态选择的，标签可以重叠，或者需要Task06 `--sanity`重现，则保留标准工作流。

对于`--label-mapping '[[1,3],[2,13]]'`，通道0是背景，通道1表示从VISTA3D类3初始化的数据集标签1，通道2表示从VISTA3D类13初始化的数据集标签2。在使用生成的`model_softmax.pt`与上游`configs/inference_softmax.json`时，保留条目及其顺序。`nv-segment-ct`和`nv-segment-ctmr`推理技能目前不提供该固定通道推理路径。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/run_finetune.py` | 由`skill_manifest.yaml`声明的入口点；配置文件、运行MONAI并写入`output.json`。 | `[FIXTURE_OR_DATASET] --output-dir OUT_DIR [--smoke] [--sanity] [--auto-seg] [--softmax] [--dataset-dir DIR] [--datalist JSON] [--target-anatomy TEXT] [--label-mapping JSON] [--patch-size JSON] [--mlflow-experiment-name NAME] [--mlflow-tracking-uri URI] [--mlflow-run-name NAME]` |

## 前提条件

- Python 3.10+与CUDA支持的Torch用于GPU运行。
- 从`skill_manifest.yaml`获取运行时包，特别是`monai==1.4.0`、`numpy<2`、`nibabel`、`scipy`、`typer`、`PyYAML`、`fire`、`pytorch-ignite`、`einops`和`huggingface_hub`。当启用MLflow跟踪时，安装`mlflow>=2.10,<4`。
- 可选环境变量：`CUDA_VISIBLE_DEVICES`限制可见GPU；`NPROC_PER_NODE`覆盖GPU数量，值`>=2`选择非sanity运行的多GPU模式；`NVSEG_FINETUNE_AUTO_VENV=0`禁用缓存的MONAI 1.4兼容环境。远程跟踪可能使用`DATABRICKS_CONFIG_PROFILE`、`DATABRICKS_HOST`、`DATABRICKS_TOKEN`、`MLFLOW_TRACKING_CLIENT_CERT_PATH`、`MLFLOW_TRACKING_INSECURE_TLS`、`MLFLOW_TRACKING_PASSWORD`、`MLFLOW_TRACKING_SERVER_CERT_PATH`、`MLFLOW_TRACKING_TOKEN`或`MLFLOW_TRACKING_USERNAME`；这些变量仅在明确启用MLflow时传递，并且不会传递无关的凭证。
- `--softmax`还需要NVIDIA-Medtech源检出的固定版本。将`NV_SEGMENT_CT_ROOT`设置为它的`NV-Segment-CT`目录，或将`NV_SEGMENT_CTMR_ROOT`设置为兄弟`NV-Segment-CTMR`目录。包装器就地读取官方softmax配置和实现，仅在`--output-dir`下写入生成的覆盖文件。
- 运行输出：生成的包配置文件在`skills/nv-segment-ct-finetune/bundle/configs/`下，包括`auto_override.json`、`train_continual_task06_lung.json`和`dfw_no_logging.json`；检查点/证据在`--output-dir`下；启用时，本地跟踪数据在`<output-dir>/mlruns`下。
- 依赖缓存位置：`~/.cache/nvidia-skills/venvs/nv-segment-ct-finetune-monai14/`用于MONAI兼容包，`~/.cache/huggingface/`用于模型资产。这些是可重用的运行时文件，不是代理指令或另一个运行的授权。当兼容环境设置未获批准时，设置`NVSEG_FINETUNE_AUTO_VENV=0`；然后使用调用者提供的兼容环境。
- 网络访问：模型/配置下载使用`https://huggingface.co`和`https://raw.githubusercontent.com`；远程跟踪仅在明确启用时联系调用者批准的MLflow或Databricks目的地。标签字典下载接受固定源主机的HTTPS，并拒绝重定向。

新鲜环境设置：

```bash
python -m pip install "monai==1.4.0" "numpy<2" pytorch-ignite einops nibabel scipy typer PyYAML fire huggingface_hub
```

当MLflow跟踪启用时，还安装：

```bash
python -m pip install "mlflow>=2.10,<4"
```

已知的上游兼容性限制：

- DFW Task06参考：Python `3.10.16`、MONAI `1.4.0`、Torch `2.7.0+cu126`。
- 对于烟测、sanity和证据运行，使用确切的`monai==1.4.0`；MONAI 1.5.x会在布尔标签上崩溃上游微调损失。
- 不要在生成的命令中将依赖项浮动为`monai>=1.4,<1.6`。
- Softmax工作流保持上游的默认100个epoch和学习率`1e-4`，除非调用者覆盖它们。

`--softmax`的一次性源设置：

```bash
export NV_SEGMENT_CTMR_COMMIT=cb921f5c58837c0f42a713855d68b32af88e1cdd
export NV_SEGMENT_CTMR_CHECKOUT="$HOME/.cache/nvidia-skills/upstreams/NV-Segment-CTMR-cb921f5"
if [ ! -d "$NV_SEGMENT_CTMR_CHECKOUT/.git" ]; then
  git clone https://github.com/NVIDIA-Medtech/NV-Segment-CTMR.git "$NV_SEGMENT_CTMR_CHECKOUT"
fi
git -C "$NV_SEGMENT_CTMR_CHECKOUT" checkout --detach "$NV_SEGMENT_CTMR_COMMIT"
export NV_SEGMENT_CT_ROOT="$NV_SEGMENT_CTMR_CHECKOUT/NV-Segment-CT"
```

## 使用

烟测规模工作流检查：

```bash
python -m pip install "monai==1.4.0" "numpy<2" pytorch-ignite einops nibabel scipy typer PyYAML fire huggingface_hub && \
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  PATH_TO_DATASET \
  --smoke \
  --patch-size '[64,64,64]' \
  --output-dir runs/nvseg_smoke
```

使用`PATH_TO_DATASET`作为 staged 数据集。对于微 fixture，使用`skills/nv-segment-ct-finetune/fixtures/spleen_micro`。烟测模式证明布线、配置生成、检查点加载和运行时兼容性；它不是质量标准。

MSD Task06 Lung Tumor sanity 重现：

```bash
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  /path/to/Task06 \
  --sanity \
  --output-dir runs/nvseg_task06_sanity
```

Sanity预设遵循单GPU DFW配方：折叠-0验证、标签映射`[[1, 23]]`用于`lung tumor`、自动类提示分割、补丁`[128,128,128]`、5个epoch，以及原始间距`configs/evaluate.json`在训练前后评分。预期参考范围是预训练Dice约为`0.6697`，训练最佳Dice约为`0.6905`，微调后的正式Dice约为`0.6836`。

用户数据微调：

```bash
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  --dataset-dir /path/to/dataset \
  --datalist /path/to/datalist.json \
  --target-anatomy "lung tumor" \
  --auto-seg \
  --epochs 5 \
  --patch-size '[128,128,128]' \
  --output-dir runs/nvseg_user_finetune
```

当本地标签值自定义或解剖名称模糊时，使用`--label-mapping '[[1, 23]]'`。

可选的本地MLflow跟踪：

```bash
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  --dataset-dir /path/to/dataset \
  --datalist /path/to/datalist.json \
  --target-anatomy "lung tumor" \
  --epochs 5 \
  --mlflow-experiment-name nvseg-finetune \
  --mlflow-run-name trial-01 \
  --output-dir runs/nvseg_mlflow
```

这使用MONAI的记录的`--tracking mlflow`路径和内置的rank-zero处理器。没有`--mlflow-tracking-uri`，数据将保留在`<output-dir>/mlruns`。仅在打算进行远程跟踪时，传递调用者批准的远程URI，包括`databricks`。MLflow不会更改补丁大小、转换、优化器值、DataLoader设置或其他训练配置。

固定通道softmax微调用于互斥标签：

```bash
export NV_SEGMENT_CT_ROOT="$HOME/.cache/nvidia-skills/upstreams/NV-Segment-CTMR-cb921f5/NV-Segment-CT"
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  --dataset-dir /path/to/dataset \
  --datalist /path/to/datalist.json \
  --label-mapping '[[1,3],[2,13]]' \
  --softmax \
  --epochs 100 \
  --output-dir runs/nvseg_softmax
```

这委托给上游`configs/train_continual_softmax.json`。它产生
`checkpoints/model_softmax.pt`；源`model.pt`初始化网络，但与`configs/inference_softmax.json`不兼容。因此，包装器建议在成功运行后使用生成的softmax检查点。

## 示例

在staged微型数据集上运行烟测：

```bash
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  runs/with_vs_without_nv/_inputs/nv_segment_ct_finetune/input_dataset \
  --smoke \
  --patch-size '[64,64,64]' \
  --output-dir runs/nvseg_smoke
```

在本地MSD缓存上运行Task06 sanity：

```bash
python skills/nv-segment-ct-finetune/scripts/run_finetune.py \
  .workbench_data/datasets/Task06_Lung \
  --sanity \
  --output-dir runs/nvseg_task06_sanity
```

## 数据契约

- 偏好的布局：`dataset/imagesTr/*.nii.gz`和`dataset/labelsTr/*.nii.gz`。
- 标签必须通过basename与图像一对一对应。
- 目标标签值必须存在于训练标签中。
- 当患者级拆分很重要时，使用数据列表。包默认`fold`是`0`，所以`fold: 0`条目是验证，所有其他折叠都是训练。
- 每个训练的前景标签必须映射到现有的VISTA3D全局类ID，来自`bundle/label_dict.json`；这个技能不能发明新的类。
- 在`--softmax`模式下，第一个映射列是保存的数据集标签，第二个是预训练的VISTA类ID。映射顺序固定了通道布局，并且在推理期间必须保持不变。

## 结果

首先检查运行目录中的`output.json`：

- `formal_pretrained_val_dice`和`formal_finetuned_val_dice`：正式评估启用时的原始间距预/后分数。
- `training_start_val_dice`、`val_dice_per_epoch`和`training_best_val_dice`：训练时间的验证跟踪。
- `finetuned_ckpt_matches_pretrained_weights`：检测标准工作流的epoch-0检查点陷阱，当`val_at_start=true`时；softmax使用不同的检查点架构。
- `recommended_ckpt`：根据记录的工作流和指标推导出的检查点建议。在选择检查点之前检查这些记录；最后一个epoch或一个文件名本身不是改进的证据。向调用者报告建议；部署不在此技能的范围内。
- `invocation.mlflow_tracking`：选择的跟踪URI、实验名称和可选的运行名称，或`null`当跟踪被禁用时。
- `runtime.oom`、`runtime.peak_gpu_mb`和阶段日志：区分OOM、慢验证和进程失败。

决策规则：当存在时，优先考虑正式原始间距预/后分数；拒绝张量相同的“微调”检查点用于sanity恢复；将`improved: false`视为有效证据，而不是包装器失败。

## 限制

- 薄包装器。训练、验证、转换和检查点委托给`bundle/`中的上游包。
- 张量比较使用限制的`weights_only=True`检查点加载。不支持的序列化对象产生比较错误；它们不会使用无限制的pickle加载重试。这种比较不是对上游训练/检查点加载的安全审计。
- 仅记录重现：成功的五epoch Task06运行使用了Python
  `3.12.3`、PyTorch `2.12.0+cu130`与CUDA `13.0`、MONAI `1.4.0`、NumPy
  `1.26.4`、PyTorch-Ignite `0.5.4`、NiBabel `5.4.2`、SciPy `1.16.0`、einops
  `0.8.2`、Fire `0.7.1`、Hugging Face Hub `0.36.2`、Transformers `4.57.6`,
  Typer `0.25.1`、PyYAML `6.0.3`和MLflow `3.14.0`在一个NVIDIA RTX 6000
  Ada 48 GB GPU上。这些版本记录了证据环境；它们不是额外的包约束或声称其他版本不能工作。
- 自动推导的计划是启发式的；调用者提供的`--patch-size`、`--cache-rate`、`--epochs`和`--learning-rate`优先。
- `--softmax`与`--sanity`不兼容：Task06参考分数和原始间距预/后评估属于标准VISTA3D持续学习工作流。Softmax运行记录训练验证轨迹，但在质量声明之前需要单独的任务特定评估。
- Task06 sanity配方故意强制单GPU执行以匹配DFW参考。其他数据集的多GPU模式需要主机`torchrun`支持。
- 配对验证器是CPU仅的，并审计证据包；它不会重新运行GPU分割。
- MLflow支持是可选的，并使用MONAI的内置跟踪处理器。跟踪错误是上游MONAI运行的一部分，因此可能使微调命令失败。
- 不用于临床部署、临床解释、自主诊断或监管提交。

## 故障排除

| 错误 | 原因 | 修复 |
|---|---|---|
| 缺少依赖或导入错误 | 运行时从`skill_manifest.yaml`漂移。 | 安装上述包或使用记录的环境。 |
| Task06预训练Dice低 | 配置错误、检查点错误、数据拆分漂移或依赖漂移。 | 在更改训练逻辑之前，比较环境字段和staged配置。 |
| `model_finetune.pt`与预训练匹配 | `val_at_start=true`选择epoch 0作为最佳。 | 使用`recommended_ckpt`；除非更改的检查点提高了正式Dice，否则将sanity恢复视为失败。 |
| 缺少正式Dice字段 | 正式评估失败或被跳过。 | 检查`eval_pretrained.log`、`eval_finetuned.log`和`metrics.csv`。 |
| GPU内存不足 | 补丁/缓存设置太大。 | 减少`--patch-size`，降低`--cache-rate`，或减少工作者。 |
| 没有验证案例 | 数据列表缺少`fold: 0`。 | 提供至少一个验证条目。 |
| `--softmax需要固定...检出` | 八月的softmax配置/实现缺失或检出在另一个提交上。 | 检出`cb921f5c58837c0f42a713855d68b32af88e1cdd`并设置`NV_SEGMENT_CT_ROOT`或`NV_SEGMENT_CTMR_ROOT`。 |
| MLflow跟踪失败 | MLflow缺失、凭证无效或实验无法访问。 | 检查`finetune.log`，修复MLflow客户端配置，并重新运行；省略`--mlflow-experiment-name`以禁用跟踪。 |

## 验证

当质量门很重要时，运行实现的验证器：

```bash
python -m eval_engine.run_trusted skills/nv-segment-ct-finetune \
  --fixture skills/nv-segment-ct-finetune/fixtures/spleen_micro \
  --out runs/nvseg_trusted
```
