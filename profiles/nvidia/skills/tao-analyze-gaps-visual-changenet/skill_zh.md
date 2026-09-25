# TAO VCN 分类差距分析技能

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

您是 NVIDIA TAO VCN Classify（视觉组件网络）推理结果的分析师。您的工作是通过测量从决策阈值*错误方向*的符号距离，来识别每个**地面真实标签的最弱样本**，然后将它们用于下游的增强或重新标记。

此技能有意设计得轻量级。VCN 的分类头是一个单分数二进制边界（通过 `siamese_score` 的 PASS vs NO_PASS），因此分析是计算性的，而不是调查性的。整个计算都在一个直接的 `docker run` 调用中完成，针对固定的 TAO 数据服务镜像（参见设置）。容器的入口点接受 `<category> <action> [hydra 覆盖...]`；我们传递 `gap_analysis vcn_aoi key=value …`。每个覆盖都是 Hydra 的 `key=value`，它选择性地覆盖脚本的 `GapAnalysisConfig` 模式（默认值嵌入到容器中；使用挂载的最小规格 `--cfg=job` 菜单立即进行内省）。（容器内部没有 `dataset` 关键字——那是 TAO 启动器的支柱前缀，在这里被丢弃。）您**不需要**委派分析、多阶段图像审核或组件类型聚类——VCN 没有暴露这些维度。在容器返回后，仅查看一小部分代表性弱样本以确认差距。

CLI 界面可以在数据服务容器构建之间切换。如果 `gap_analysis vcn_aoi` 调用在参数解析上失败，请使用挂载的主机路径上的最小规格在每张镜像上执行一次实际模式内省：

```bash
SPEC_DIR="$(mktemp -d)"
printf '%s\n' 'min_recall: 0.99' 'top_k_per_label: 5' > "$SPEC_DIR/vcn_aoi_spec.yaml"
docker run --rm -v "$SPEC_DIR:/w:ro" "$DS_IMAGE" gap_analysis vcn_aoi \
    -e /w/vcn_aoi_spec.yaml --cfg=job
```

`-e` 路径必须在容器内部解析，因此规范必须位于挂载在 `/w` 的目录下。在重试之前，解决任何重命名的键（例如 `inference_csv` vs `inference_results_dir`，`output_dir` vs `results_dir`）。输出 parquet 名称是 `kpi_gaps.parquet`。

---

## 输入

1. **实验结果目录**——包含 TAO VCN Classify 推理的 `inference/inference.csv`。必需列：`input_path`，`object_name`，`label`，`siamese_score`。传递**目录**（例如 `inference/latest/`），而不是 CSV 文件——容器读取 `inference_results_dir/inference.csv`。
2. **训练代码/配置目录**——包含 VCN 训练 YAML。容器读取它来自 `dataset.classify.input_map`（照明条件列表）和 `dataset.classify.image_ext`，以将每个弱样本扩展为每个照明条件的一行。
3. **数据集目录**——图像根目录前缀附加到每行相对 `input_path`（`kpi_media_path`）。
4. **规范覆盖**——`min_recall`，`top_k_per_label`，以及可选的硬固定 `threshold` 作为 Hydra 覆盖传递（默认：`min_recall=1.0`，`top_k_per_label=50`，`threshold=-1.0` 意味着扫描）。**`top_k_per_label` 必须是一个正整数**——省略它会将容器切换到“低于阈值过滤”模式，在 `min_recall=1.0` 时仅返回错误分类的 PASS 行，并且没有 NO_PASS 行——作为增强队列无用。参见常见陷阱。

---

## 设置

阈值扫描、弱点排名和每个照明的扩展都在下面的固定 TAO 数据服务镜像内部运行。确认 Docker、NVIDIA 容器工具包和一个 GPU 存在，并确保镜像已缓存：

```bash
# 固定的 TAO 数据服务容器 URI（来自发布清单的标记）
DS_IMAGE=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services  # versions-key: images.tao_toolkit.data_services
echo "DS_IMAGE=$DS_IMAGE"

docker info > /dev/null && echo "OK: docker"
nvidia-smi > /dev/null && echo "OK: GPU"
docker image inspect "$DS_IMAGE" > /dev/null \
  || docker pull "$DS_IMAGE"
```

需要 GPU；在无 GPU 的主机上提前中止可以避免混淆的后期错误。

三个设置规则是承重且容易出错的：

- **路径挂载**——容器读取或写入的每个主机路径（`inference.csv`，训练 YAML，数据集图像根目录，输出目录）必须通过挂载，最简单的是 `-v $WORKSPACE:$WORKSPACE -w $WORKSPACE`，以便绝对路径在两侧解析相同。
- **不要传递 `--user $(id -u):$(id -g)`**——它会在容器的 `transformers` 导入期间触发 `KeyError: 'getpwuid(): uid not found: <uid>'`；`chown` 后输出回主机 UID。
- **`-e <spec>` 是必需的，不是可选的**——当前镜像强制要求它，并在解析 CLI 覆盖之前退出，显示 `ValueError: The subtask vcn_aoi requires the following argument: -e/--experiment_spec_file`。

参见 `references/container-setup.md` 以获取完整的路径挂载模式、`--user`/`chown` 理由和 `alpine` chown 命令、多 `-v` 指导以及 `-e <spec>` 要求的详细信息。

---

## 方法

整个技能是一个 `docker run` 调用，然后是一个小的视觉快速检查。容器内部执行步骤 1–4（阈值扫描、弱点评分、Top-K 选择、每个照明的扩展）。您直接使用读取工具处理步骤 5（视觉快速检查）。

### 步骤 1–4 — 运行容器

```bash
$DOCKER gap_analysis vcn_aoi \
    inference_results_dir=<exp_dir>/inference/<label>/ \
    train_config=<exp_dir>/train.yaml \
    kpi_media_path=<dataset_root> \
    results_dir=<rca_results_dir> \
    top_k_per_label=50
```

> **始终传递 `top_k_per_label`。** 这是切换容器从默认“低于阈值样本”过滤到正确 Top-K-per-label 排名的参数。
> 在 `min_recall=1.0` 时，阈值构建在或低于每个 NO_PASS 分数，因此低于阈值过滤仅返回错误分类的 PASS 行，并且没有 NO_PASS 行——作为增强队列无用。
> 当 `top_k_per_label` 设置为正整数（无论是在规范中还是在 Hydra 覆盖中），容器会针对每行计算相对于阈值的符号弱点，并展示每个地面真实标签的 K 个最弱样本，这是下游步骤消耗的按标签排名的输出。

读取 `inference.csv`，扫描每个唯一的 `siamese_score` 加一个值略低于最小值，保留 NO_PASS 类别召回率 ≥ `min_recall`（具有 `1e-12` 容差）的候选者，然后选择具有最佳 F1（平局：精确度，然后阈值值）的阈值。对于每一行，计算相对于该阈值的符号弱点（正 = 错误分类，负 = 正确，幅度 = 边缘）。按弱点降序排序并选择每个地面真实标签的 Top `top_k_per_label`，然后使用来自训练 YAML 的 `dataset.classify.input_map` 和 `dataset.classify.image_ext` 将每个弱行扩展为每个照明条件的一行。

如果**没有**候选阈值满足召回目标，容器将非零退出并写入 `unreachable_kpi.txt` 到 `results_dir` 解释模型实际上可以达到的召回率。在这种情况下，在 docker 调用后停止分析，编写一个报告解释模型在任何操作点都根本无法达到 KPI，并建议重新训练或重新标记——跳过视觉快速检查。

**TAO 7.2 艺术品合同：**

容器生成的必需艺术品：

| 艺术品 | 内容 |
|----------|----------|
| `kpi_gaps.parquet` | 按标签 Top-K 最弱样本，按照明扩展。列：`filepath`，`label`，`siamese_score`，`weakness`。 |
| `threshold.txt` | 选择的决策阈值（单个浮点数，纯文本）。 |
| `weak_samples_breakdown.txt` | 按标签保留行分解：`<count>` 总计，`<%>` 所有保留行的百分比，`N` 错误分类（weakness > 0），`N` 边际（weakness ≤ 0）。 |

您必须在容器返回后生成必需的七部分 `RCA_Report.md`。在一个可达到的运行中，您还必须在视觉快速检查期间生成 `rca_images/`。容器不生成任何代理拥有的艺术品。

`unreachable_kpi.txt` 是当召回目标无法达到时写入的失败艺术品。其存在意味着：跳过步骤 5，编写简短报告，并建议重新训练。TAO 7.2 的 `vcn_aoi` 动作**不**发出 `metrics.json`；该文件不在 7.2 合同之外。从完整的 `inference.csv` 和 `threshold.txt` 中的选定值计算报告指标。

将容器的 stdout 摘要（选择的阈值、保留行计数、按标签分解）打印到自己的 stdout，以便脚本检查钩子可以验证运行生成了输出。

### 步骤 5 — 视觉快速检查（小，固定）

如果存在 `unreachable_kpi.txt`，则跳过此步骤。否则使用读取工具查看 `kpi_gaps.parquet` 中的 5 个最弱 PASS 样本和 5 个最弱 NO_PASS 样本（去重为每个样本一行，使用 FIRST 照明 `filepath`），将每个测试图像分类为**错误分类** / **边缘情况** / **数据质量** / **系统性**中的确切一个，并将每个查看的图像（如果 PIL 可用，则调整大小为 128×128，否则仅复制）复制到 `<results_dir>/rca_images/`。这是唯一需要的图像检查——不要查看几十张图像，运行故障模式聚类，或审核黄金图像（VCN 没有黄金图像）。

参见 `references/visual-spot-check.md` 以获取确切的样本选择排序、每个照明去重规则、每个裁决类别的完整定义以及图像复制细节。

---

## 参考调用

粘贴并编辑工作区、四个路径和两个数字旋钮；这可以端到端运行。捕获 stdout，以便脚本检查钩子可以看到行计数。

```bash
WORKSPACE=<绝对路径>            # 在容器内部以相同方式挂载
EXP_DIR=<实验结果目录>          # 包含 inference/inference.csv 和 train.yaml；必须在 $WORKSPACE 内
DATASET_ROOT=<数据集根目录>      # 推理 inference.csv input_path 条目的图像根；必须在 $WORKSPACE 内
MIN_RECALL=1.0                   # 默认零错；如果 KPI 放宽，则降低
TOP_K=50                         # 每个标签的增强预算
OUT="$EXP_DIR/rca_results/$(date +%Y-%m-%d_%H%M%S)"
SPEC="$OUT/vcn_aoi_spec.yaml"
IMG=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services  # versions-key: images.tao_toolkit.data_services

mkdir -p "$OUT"

# 写入此运行的差距分析规范
cat > "$SPEC" <<EOF
min_recall: $MIN_RECALL
top_k_per_label: $TOP_K
EOF

docker run --gpus all --rm --shm-size=8g \
    -v "$WORKSPACE:$WORKSPACE" -w "$WORKSPACE" \
    "$IMG" gap_analysis vcn_aoi \
    -e "$SPEC" \
    inference_results_dir="$EXP_DIR/inference/latest/" \
    train_config="$EXP_DIR/train.yaml" \
    kpi_media_path="$DATASET_ROOT" \
    results_dir="$OUT"

# 容器以 root 身份写入，`--user` 被丢弃；如果需要，将回主机的 UID 改为 chown。
docker run --rm -v "$WORKSPACE:/w" alpine chown -R "$(id -u):$(id -g)" "/w/$(realpath --relative-to="$WORKSPACE" "$OUT")"

# 确认打印，以便脚本检查钩子可以看到真实数字。报告指标是从 inference.csv 计算的，因为 metrics.json 不在 7.2 合同中。
python3 - "$OUT" "$EXP_DIR/inference/latest/inference.csv" << 'PYEOF'
import os, sys
import pandas as pd
out = sys.argv[1]
unreachable = os.path.join(out, "unreachable_kpi.txt")
if os.path.isfile(unreachable):
    print("KPI UNREACHABLE — see", unreachable)
    sys.exit(0)
with open(os.path.join(out, "threshold.txt")) as f:
    threshold = float(f.read().strip())
inference = pd.read_csv(sys.argv[2])
actual_no_pass = inference["label"].eq("NO_PASS")
predicted_no_pass = inference["siamese_score"].ge(threshold)
tp = int((actual_no_pass & predicted_no_pass).sum())
fp = int((~actual_no_pass & predicted_no_pass).sum())
tn = int((~actual_no_pass & ~predicted_no_pass).sum())
fn = int((actual_no_pass & ~predicted_no_pass).sum())
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
print(f"threshold={threshold} precision={precision:.4f} recall={recall:.4f} f1={f1:.4f}")
print(f"confusion_matrix: tp={tp} fp={fp} tn={tn} fn={fn}")
df = pd.read_parquet(os.path.join(out, "kpi_gaps.parquet"))
print(f"kpi_gaps.parquet: rows={len(df)}, cols={list(df.columns)}")
print(df['label'].value_counts())
PYEOF
```

---

## 输出

将所有内容写入实验结果目录下的带时间戳的文件夹。容器的必需输出直接写入此处；您编写 `RCA_Report.md` 和，对于可达到的 KPI，`rca_images/`。任何会话/配置文件由运行时打包钩子添加的额外内容都不是 TAO 7.2 差距分析艺术品合同的一部分。

```
<experiment_result_dir>/rca_results/YYYY-MM-DD_HHMMSS/
├── kpi_gaps.parquet           # 容器：按标签 Top-K 最弱样本，按照明扩展
├── threshold.txt              # 容器：选择的决策阈值（单个浮点数）
├── weak_samples_breakdown.txt # 容器：按标签计数/错误分类/边际计数
├── RCA_Report.md              # 您：必需的七部分差距分析报告
├── rca_images/                # 您：可达到运行时必需的；快速检查缩略图
├── unreachable_kpi.txt        # 容器：仅当没有阈值满足 min_recall 时
└── <可选的打包额外内容>       # 运行时依赖；不在 7.2 合同内
```

在运行开始时，通过在 Bash 中运行 `date +%Y-%m-%d_%H%M%S` 获取真实时间戳。不要硬编码或猜测。如果用户指定了自定义输出路径，请使用该路径，但保持相同的内部结构。

---

## 常见陷阱

最严重的失败模式是**在 `min_recall=1.0` 时忘记 `top_k_per_label`**：在 `min_recall=1.0` 时，选择的阈值位于或低于每个 NO_PASS 分数，因此如果没有 `top_k_per_label`，容器会回退到“低于阈值样本”过滤，该过滤仅返回错误分类的 PASS 行，并且没有 NO_PASS 行，从而破坏了增强队列。始终在规范或作为 Hydra 覆盖中包含一个显式的正 `top_k_per_label`（默认 50）。

参见 `references/pitfalls.md` 以获取完整的检查清单，涵盖：忘记 `top_k_per_label`；传递 `--user`；仅使用 Hydra 覆盖调用（没有 `-e <spec>`）；规范文件不在 `$WORKSPACE`；规范文件中的未解析 `???` 发送哨兵；镜像未拉取/错误标签；路径挂载不匹配；写入 `unreachable_kpi.txt`；`inference.csv` 缺少必需列；训练 YAML 缺少 `dataset.classify.input_map` 或 `image_ext`；`kpi_media_path` 不匹配 `input_path` 前缀；以及从容器内部未检测到 GPU。

---

## 报告结构

将 `RCA_Report.md` 作为紧密（1000–1800 字）的计算差距分析编写——深度来自准确的数字和清晰的行动列表，而不是叙述。完整的报告模板（7 部分：裁决、阈值选择、弱点分布、Top-K 最弱样本、视觉快速检查、按标签分解、推荐行动——与混淆矩阵和表格布局）在 `references/output-template.md` 中。当 `unreachable_kpi.txt` 存在时，用该文件的内容替换 3–6 部分，并将 7 部分压缩为一个建议：重新训练或重新标记。

---

## 执行顺序

1. 将 `DS_IMAGE` 设置为固定的数据服务 URI（参见设置），然后运行 `docker info`，`nvidia-smi`，和 `docker image inspect "$DS_IMAGE"`（如果缺失则拉取）一次以确认环境。如果任何失败，则用清晰的错误消息中止。
2. 运行 `date +%Y-%m-%d_%H%M%S` 获取时间戳；创建 `<experiment_result_dir>/rca_results/<timestamp>/`。
3. 在时间戳目录中写入 `vcn_aoi_spec.yaml`，填写 `min_recall` 和 `top_k_per_label`。保持它位于 `$WORKSPACE` 下，以便 `-e` 路径在容器内部解析。
4. 运行 `docker run … "$DS_IMAGE" gap_analysis vcn_aoi -e vcn_aoi_spec.yaml inference_results_dir=… train_config=… kpi_media_path=… output_dir=…`。容器将 `kpi_gaps.parquet`，`threshold.txt`，和 `weak_samples_breakdown.txt` 写入 `results_dir`。将选择的阈值和保留行计数打印到 stdout，以便脚本检查钩子可以验证运行生成了输出。
5. 如果存在 `unreachable_kpi.txt`，则跳过步骤 6 并编写简短报告。否则继续。
6. 从 `kpi_gaps.parquet` 中选择 10 个弱样本（5 个最弱 PASS + 5 个最弱 NO_PASS），使用读取工具查看每个测试图像，分类每个为**错误分类** / **边缘情况** / **数据质量** / **系统性**，并将每个查看的图像（如果 PIL 可用，则调整大小为 128×128，否则仅复制）复制到 `<results_dir>/rca_images/`。
7. 最后编写 `RCA_Report.md`——编写它会触发打包钩子，该钩子将会话日志和技能配置与一起复制。
