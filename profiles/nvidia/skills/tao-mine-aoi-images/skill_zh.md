# DEFT 矿掘与嵌入技能

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

您是 VCN AOI DEFT 嵌入后矿掘工作流的操作员。您的工作是取一个弱目标图像的 parquet（即差距分析或路由输出），以及一个源池，然后生成一个去重后的矿掘源图像 parquet，这些图像与目标相似，准备好输入到下一轮训练中。迭代 DEFT 调用者还会运行捆绑的历史感知后处理步骤，以便在早期迭代中选择的样本不会被再次选择。

工作流是固定的和确定性的：**嵌入目标，嵌入源池，矿掘最近邻，然后（对于迭代工作流）移除先前矿掘的样本。** 每个 GPU 步骤的输出 parquet 是下一步的输入；历史感知选择是主机端的后处理步骤，而不是另一个 k-NN 搜索。没有聚类步骤或人工参与选择——深度来自于选择合适的编码器和一个足够宽的 `topn`，以便在历史过滤后保留新颖的候选样本。

整个技能是一个围绕三个直接 `docker run` 调用（针对固定的 TAO 数据服务镜像）和一个可选捆绑的主机 Python 后处理器（用于迭代历史）的薄包装（在 Setup 中运行时解析 `versions.yaml`）。容器的入口点接受 `<category> <action> -e <spec.yaml> [hydra overrides...]` — 输入 `embedding image_embeddings -e <embedding_spec.yaml> …` 用于嵌入，输入 `tmm nearest_neighbors -e <mining_spec.yaml> …` 用于矿掘。`-e` 标志指向一个 YAML 文件，该文件为子任务的架构提供默认值；之后的内容是裸的 Hydra 覆盖（`key=value`），它按需覆盖每次运行中的 spec 字段。（容器内没有 `dataset` 关键字——那是 TAO 启动器的主桩前缀，在这里被丢弃。）如果未缓存，请拉取一次镜像：`docker pull "$DS_IMAGE"`（在 Setup 中解析 `$DS_IMAGE` 后）。

架构键可以在数据服务版本之间重命名（RCA 技能看到了 `inference_csv` → `inference_results_dir`，`output_dir` → `results_dir`）。如有疑问，请每次针对每个图像内省实际架构：`docker run --rm "$DS_IMAGE" embedding image_embeddings --cfg=job` 和 `... tmm nearest_neighbors --cfg=job`。

---

## 输入

1. **目标 parquet** — 差距分析输出，通常是 `tao-route-visual-changenet-samples` 的 `mining_gaps.parquet`（如果路由被跳过，则为 `tao-analyze-gaps-visual-changenet` 的 `kpi_gaps.parquet`）。必需列：`filepath`。如果 `label` 也存在，则在矿掘期间可以进行基于标签的过滤；否则，矿掘任务会静默地忽略过滤器。
2. **源池** — 一个候选图像的 parquet，用于矿掘，带有 `filepath` 列。如果用户只有 CSV，请在步骤 2 之前将其转换为具有相同列的 parquet。对于基于标签的过滤，池必须还携带 `label` 列。
3. **嵌入 spec 文件** — 一个包含 `model`、`model_path`、`batch_size`，以及（仅当 `model_path` 是 TAO `.pth`/`.ckpt` 时）`model_config_path` 的 YAML。跨步骤 1 和 2 重复使用；`input_parquet`/`output_parquet` 每次运行作为 Hydra 覆盖提供。**必须**使用相同的 spec 驱动两个嵌入步骤——来自不同编码器的嵌入是不可比较的，不匹配的编码器是最常见的“矿掘图像看起来不相关”报告的原因。
4. **矿掘 spec 文件** — 一个包含 `topn`、`knn_metric`、`filter_by_label`，以及（很少更改）`source_embed_column_name`/`target_embed_column_name` 的 YAML。`source_parquet`/`target_parquet`/`output_parquet` 是运行时的 Hydra 覆盖。SigLIP 和 CLIP 嵌入应使用 `knn_metric: cosine`。当 `filter_by_label: true` 但任一嵌入 parquet 缺少 `label` 列时，容器记录警告并**不**进行过滤继续进行。
5. **矿掘历史（仅迭代工作流）** — 运行级结果目录下的一组 JSON 账本，加上每次迭代的摘要。`scripts/filter_mined_history.py` 拥有这两个文件。它通过归一化的 `filepath` 识别样本，验证所有早期输出哈希，并拒绝迭代差距或重复选择。恢复时切勿手动编辑或重建此账本。

---

## 设置

使用下方固定的 TAO 数据服务 URI，然后在做任何其他事情之前确认 Docker、NVIDIA 容器工具包和 GPU 的存在。编码器前向传递和 cuML/cuDF k-NN 搜索都需要 GPU；两者在没有 CUDA 的情况下都会失败。

```bash
# 固定的 TAO 数据服务容器 URI（来自发布清单的标记）
DS_IMAGE=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services  # versions-key: images.tao_toolkit.data_services
echo "DS_IMAGE=$DS_IMAGE"

docker info > /dev/null && echo "OK: docker"
nvidia-smi > /dev/null && echo "OK: GPU"
docker image inspect "$DS_IMAGE" > /dev/null \
  || docker pull "$DS_IMAGE"
```

容器读取或写入的每个主机路径都必须进行绑定挂载。最可预测的方法是在容器内外挂载工作区根目录，路径**完全相同**，然后重用 `$DOCKER` 别名进行三次调用：

```bash
WORKSPACE=<包含所有 parquet、输出和源池图像的绝对路径>
DOCKER="docker run --gpus all --rm --shm-size=8g -v $WORKSPACE:$WORKSPACE -w $WORKSPACE $DS_IMAGE"
```

**不要**传递 `--user $(id -u):$(id -g)`——它会在任何工作开始之前在 `transformers` 导入期间触发 `getpwuid()` `KeyError`。容器以 root 身份运行；chown 输出回主机 UID。

每次迭代编写两个 spec 文件，将它们放在 `$WORKSPACE` 下，以便 `-e` 参数在挂载的两侧解析；每次运行值保留在 spec 之外，并通过 Hydra 覆盖传递。如果源池是 CSV，请先将其转换为 parquet（保留 `filepath`，如果存在则保留 `label`）。默认的 `embedding_spec.yaml` 使用 `model: SigLIP`、`model_path: google/siglip-base-patch16-224`、`batch_size: 64`；默认的 `mining_spec.yaml` 使用 `topn: 5`、`knn_metric: cosine`、`filter_by_label: "false"`（带引号——架构将其读取为字符串）。迭代 DEFT 工作流保持 `topn: 5` 默认；保留显式的用户值。仅在历史摘要显示狭窄邻域被先前的选择主导时才增加它。

有关完整环境说明、`TAO_SKILL_BANK_PATH` 处理、路径挂载推理、`getpwuid` chown 解决方案、CSV 到 parquet 段落以及逐字 spec 文件编写块的更多信息，请参阅 `references/setup.md`。

---

## 方法

三个命令，按顺序。每个命令的输出 parquet 是下一个命令的输入。以纯 Bash 运行它们；Setup 中的 `$DOCKER` 别名处理容器、GPU 和挂载。每个调用都遵循相同的形状：`-e <spec>` 用于内置默认值，然后是一小部分 Hydra 覆盖用于运行特定路径。

### 步骤 1 — 嵌入目标图像

```bash
$DOCKER embedding image_embeddings \
    -e <embedding_spec.yaml> \
    input_parquet=<target_parquet> \
    output_parquet=<target_embeddings_parquet>
```

读取差距分析 / 路由输出，并写入一个包含 `filepath`、`embedding` 和任何额外元数据列（例如 `label`、`siamese_score`、`weakness`）的 parquet，这些列从输入中按原样转发。打印输出架构（`pd.read_parquet(...).columns`）到 stdout，以便脚本检查钩子可以确认嵌入列存在。

如果您需要在不编辑 spec 的情况下为一次运行覆盖 `model` / `model_path` / `batch_size`，请将它们作为 Hydra 覆盖追加（例如 `model_path=...`）。

### 步骤 2 — 嵌入源池

```bash
$DOCKER embedding image_embeddings \
    -e <embedding_spec.yaml> \
    input_parquet=<source_pool_parquet> \
    output_parquet=<source_embeddings_parquet>
```

与步骤 1 相同的命令形状，应用于源池。使用**完全相同**的 `embedding_spec.yaml` 作为步骤 1，并且不要在这里不同地覆盖 `model` / `model_path` / `batch_size`——两个步骤之间不匹配的编码器配置会产生不可比较的嵌入。

### 步骤 3 — 矿掘最近邻

```bash
$DOCKER tmm nearest_neighbors \
    -e <mining_spec.yaml> \
    source_parquet=<source_embeddings_parquet> \
    target_parquet=<target_embeddings_parquet> \
    output_parquet=<mined_parquet>
```

对于每个目标嵌入，在选定的指标下找到 `topn` 最接近的源嵌入，跨目标去重，并写入一个单列（`filepath`）的 parquet，其中包含唯一的矿掘源路径。对于一次性运行，这可能是最终的 `mined.parquet`；对于 DEFT 迭代，请将其写入 `mined_candidates.parquet`，以便保留不可变候选集以供步骤 4 使用。容器还在输出 parquet 旁边放置一个 `mining_summary.txt`，其中包含：查询计数、邻居计数、重复项移除，以及（当标签过滤开启时）保留与丢弃对计数。在扫描时调整 `topn`、`knn_metric` 或 `filter_by_label`——无需重写 spec。

当 `filter_by_label=true` 但其中一个嵌入 parquet 缺少 `label` 列时，容器记录警告并继续**不**进行过滤。如果矿掘输出比预期大或包含跨标签对，请在假设任务做了正确的事情之前扫描 docker 日志中的该警告。

有关最小粘贴并编辑的端到端配方（解析 `$DS_IMAGE`、写入两个 spec、运行所有三个步骤、chown 输出、打印行计数）以作为单个流式 Bash 块运行的更多信息，请参阅 `references/reference-invocation.md`。

### 步骤 4 — 历史感知选择（仅迭代 DEFT）

在任何标签/相似度保留过滤器之后运行，以便输入代表实际有资格用于训练的候选者：

```bash
python3 skills/data/tao-mine-aoi-images/scripts/filter_mined_history.py \
    --candidate-parquet <mined_candidates.parquet> \
    --output-parquet <mined.parquet> \
    --history-file <run_results_dir>/mining_history.json \
    --summary <iteration_dir>/mining_history_summary.json \
    --iteration <N> \
    --topn <topn>
```

输出保留候选顺序和架构，但只包含先前已提交迭代的样本未选择的文件路径。账本记录了选择的路径、候选/输出哈希、计数和 `topn`；`--resume` 仅在验证这些工件后才会重用已提交的迭代。零行输出是有效证据，表明当前的 k-NN 候选集中不包含任何新颖样本。调用者决定是否另一个生产者（例如 AnomalyGen）可以继续迭代，或者是否要强制停止。当摘要报告高 `historical_candidate_rate` 时，增加 `topn` 或扩展源池；历史过滤在每次迭代检索相同的弱邻域时无法制造方差。

---

## 输出和报告

将所有内容写入实验/迭代目录下的带时间戳的文件夹中。通过在 Bash 中运行 `date +%Y-%m-%d_%H%M%S` 获取真实时间戳——**不要**硬编码或猜测。如果用户指定了自定义输出路径，请直接使用它，但保持相同的内部布局。当 `Mining_Report.md` 被写入时，打包钩子会自动添加 `mining_config/` 和 `claude_session.jsonl`。

最终经过历史过滤的矿掘 parquet 是迭代下游训练阶段消费的工件。保留预历史候选 parquet、每次迭代的摘要历史记录和运行级 `mining_history.json`，以及两个嵌入 parquet；这些可以区分“k-NN 找不到任何东西”和“k-NN 只返回了先前迭代中已使用的样本”。

有关完整输出目录布局和逐字 `Mining_Report.md` 模板（结论、输入、编码器一致性、矿掘运行、按标签细分、输出合理性、推荐操作；保持 600–1200 字）的更多信息，请参阅 `references/outputs-and-reporting.md`。

---

## 常见陷阱

最频繁的失败是**两个嵌入步骤之间不匹配的编码器**——垃圾矿掘输出的最常见原因；两个步骤必须消耗相同的 `embedding_spec.yaml`。其他反复出现的陷阱：传递 `--user`（`getpwuid` `KeyError`）、跳过嵌入步骤、缺少 `label` 列静默地忽略 `filter_by_label=true`、spec 文件不在 `$WORKSPACE`、未解析的 `???` 占位符、没有 `model_config_path` 的 TAO 检查点、直接输入的 CSV 源池、主机/容器路径不匹配、没有 GPU、未拉取或 `:latest` 镜像标签、`topn × N_targets ≫ source size`（预期——报告实际矿掘计数）、以及历史过滤后 `topn` 太窄无法产生任何新颖样本。

有关完整陷阱列表、确切错误、原因和修复方案的更多信息，请参阅 `references/troubleshooting.md`。

---

## 执行顺序

1. 将 `DS_IMAGE` 设置为固定的数据服务 URI（见 Setup），然后运行 `docker info`、`nvidia-smi` 和 `docker image inspect "$DS_IMAGE"`（如果缺失则拉取）一次以确认环境。如果任何失败，请以清晰的错误消息中止。
2. 运行 `date +%Y-%m-%d_%H%M%S` 获取时间戳；创建 `<output_dir>/mining_results/<timestamp>/`。
3. 将 `embedding_spec.yaml` 和 `mining_spec.yaml` 写入时间戳目录，填写编码器选择和矿掘设置。将这些保留在 `$WORKSPACE` 下，以便 `-e` 路径在容器内解析。
4. 如果源池是 CSV，请先将其转换为 parquet（保留 `filepath` 和 `label`）。
5. 通过 `docker run … embedding image_embeddings -e embedding_spec.yaml input_parquet=… output_parquet=…` 运行步骤 1（嵌入目标）。打印输出 parquet 的行数和列到 stdout。
6. 使用与步骤 1 **完全相同**的 `embedding_spec.yaml` 运行步骤 2（嵌入源池）。打印输出行数和列。
7. 通过 `docker run … tmm nearest_neighbors -e mining_spec.yaml source_parquet=… target_parquet=… output_parquet=…` 运行步骤 3（矿掘最近邻）。确认 `mining_summary.txt` 是否写入在原始/候选 parquet 旁边。
8. 对于迭代 DEFT 调用者，应用所有配置的保留过滤器，然后使用当前迭代编号、记录的 `topn`、运行级账本路径和一个不同的最终 `mined.parquet` 运行步骤 4。**切勿**将原始候选 parquet 直接输入累积训练。
9. 通过在两个都携带 `label` 的目标嵌入 parquet 上 filepath 进行连接来计算按标签细分（第 5 节）。
10. 最后写入 `Mining_Report.md`——写入它会触发打包钩子，该钩子会复制会话日志和技能配置。
