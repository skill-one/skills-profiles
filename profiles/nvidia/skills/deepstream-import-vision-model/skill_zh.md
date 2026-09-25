# DeepStream 导入视觉模型

当此技能处于活动状态时，**在开始每个阶段之前，请阅读相关参考文档**。不要依赖记忆——参考文档包含确切的脚本路径、bash变量约定、日志文件命名约定以及关键的解析规则。

**当前范围：** 仅限目标检测模型。在`config.json`中检测到分类、分割或其他架构时，快速失败。

## 模型选择——始终提供两个选项

在预检、浏览、下载或文件创建之前，提供以下两个选项。不要从开放式的模型源提示开始。如果用户的请求已经明确选择了模型，请确认匹配的选项，而不是重复询问。

### 1. 默认模型（推荐）

使用经过验证的 Hugging Face RT-DETR 模型：

```yaml
model_id: PekingU/rtdetr_r50vd
source: huggingface
task: object-detection
precision_preference: fp16
```

### 2. 自定义目标检测模型

请求一个受支持源：

- Hugging Face 模型 ID（`organization/model`）或完整模型 URL。
- 包含其版本的 NVIDIA NGC 目录模型 URL。

解释当前技能在检查`config.json`后拒绝分类、分割和其他非检测架构。当自定义源缺失或不受支持时，不要编造或静默替换模型。

对于干运行，提供相同的两个选项，并模拟发现、构建、基准测试和报告阶段，而无需浏览、下载、启动 Docker、写入文件或启动进程。

## 管道概述

| 步骤 | 阶段 | 参考 | 功能 |
|------|-------|-----------|--------------|
| 1–3 | 模型获取 | [references/model-acquire.md](references/model-acquire.md) | 浏览 HF/NGC，检测格式，下载 ONNX 或导出 SafeTensors |
| 4–5 | 引擎构建 | [references/engine-build.md](references/engine-build.md) | 构建动态 TRT 引擎，运行 trtexec BS=1 和 BS=MAX_BS |
| 6–7 | DS 管道 | [references/pipeline-run.md](references/pipeline-run.md) | 自定义 bbox 解析器，nvinfer 配置，单流 + 多流基准测试 |
| 8   | 报告 | [references/report-generation.md](references/report-generation.md) | 5 个图表，HTML，PDF 基准测试报告 |

自主运行完整管道，每个步骤都不需要暂停确认。

## 完全通过 Docker 运行（无需主机包）

**每个步骤都在 DeepStream 容器内部运行。** 主机只需要 **Docker + NVIDIA 驱动程序**——不需要主机 python/venv/torch/trtexec/make/wkhtmltopdf。在 Linux 和 **Windows** 上工作方式相同（Docker Desktop + WSL2 后端，需要`--gpus`）。每个 shell 的绑定挂载标记是唯一的操作系统差异——`-v "$PWD":/work"`（bash），`-v "${PWD}:/work"`（PowerShell），`-v "%cd%:/work"`（cmd）；完整指南在 [references/windows.md](references/windows.md)。所有 venv/ONNX/引擎/解析器/配置/报告工件都位于挂载的工作根目录下，并在临时的 `--rm` 容器之间持久化。

## 预检——引导 + 验证（通过容器）

**1. 一次性引导**——构建 `build/.venv_optimum`（torch/onnx/onnxruntime/report 依赖项；venv 名称是历史的，optimum 不再使用）+ 在容器内安装 `wkhtmltopdf`。从工作根目录：

```bash
docker run --rm -it --gpus all --shm-size=16g -v "$PWD":/work -w /work \
  --entrypoint bash nvcr.io/nvidia/deepstream:9.1-triton-multiarch \
  .claude/skills/deepstream-import-vision-model/setup.sh
```

**2. 预检**——GPU + venv + trtexec，通过容器运行（容器模式自动检测）：

```bash
docker run --rm --gpus all -v "$PWD":/work -w /work \
  --entrypoint bash nvcr.io/nvidia/deepstream:9.1-triton-multiarch \
  .claude/skills/deepstream-import-vision-model/scripts/preflight.sh   # 仅在通过时继续
```

**后续每个阶段都以相同方式运行**——通过 `docker run … --entrypoint bash … -lc '<commands>'`（或 `.claude/skills/deepstream-import-vision-model/scripts/dsrun.sh` 包装器：`bash .claude/skills/deepstream-import-vision-model/scripts/dsrun.sh '<容器内命令>'`），使用 `PY=build/.venv_optimum/bin/python` 和容器内的 `/usr/src/tensorrt/bin/trtexec`。`deepstream-app`，`gst-launch-1.0`，和 `/opt/nvidia/deepstream/…` 示例路径都存在于 **镜像中**。TensorRT 构建+运行共享一个镜像，因此 **没有版本差异**（旧规则“在主机上构建”试图避免的问题——见 [references/engine-build.md](references/engine-build.md)`）`。`sample_720p.mp4` 随镜像提供；仅当要覆盖时才设置 `DS_VIDEO`。

## 强制输出结构

一旦 `MODEL_NAME` 已知（步骤 1），就创建一次。永远不要扁平化地转储文件。

```
models/{model_name}/
  model/           <- ONNX 文件(s)
  parser/          <- .cpp, Makefile, .so
  config/          <- nvinfer 配置，ds-app 配置，labels.txt
  scripts/         <- 运行辅助脚本
  benchmarks/
    engines/       <- _dynamic_b{MAX_BS}.engine, timing.cache, 构建日志
    b1/            <- trtexec BS=1 日志
    b{MAX_BS}/     <- trtexec BS=MAX_BS 日志
    ds/            <- DS 基准测试日志
  reports/         <- benchmark_report.md, .html, .pdf, benchmark_data.json
    charts/        <- chart_*.png (5 个图表)
  samples/         <- 输出 .mp4 或 .ogv（theoraenc 回退），测试帧
    kitti_output/  <- KITTI 检测 .txt 文件
```

```bash
mkdir -p models/$MODEL_NAME/{model,parser,config,scripts,benchmarks/engines,benchmarks/ds,reports/charts,samples/kitti_output}
```

## 关键规则

1. **引擎命名**——始终为 `{model}_dynamic_b{MAX_BS}.engine`。绝不使用 `model_dynamic.engine`。
2. **batch_size == num_streams**——在 DS 运行中，`batch-size` 和流计数始终相等。
3. **日志文件名是固定的**——`trtexec_b1.log`，`trtexec_b${MAX_BS}.log`，`ds_s${N}_run1.log`，`ds_s${N}_run2.log`。没有时间戳。报告生成读取确切的路径。
4. **解析器零初始化**——始终 `NvDsInferObjectDetectionInfo obj = {};`。对于 DS 9.1 OBB 支持是必需的；裸 `obj;` 会留下 `rotation_angle` 未初始化，导致倾斜的边界框。
5. **KITTI 验证门**——如果 KITTI 帧计数为零或检测率 < 90%，则不要继续到步骤 7。
6. **共享 venv**——`build/.venv_optimum` 在所有模型中重复使用。永远不要为每个模型创建 venv。
7. **trtexec `--noDataTransfers`**——GPU 仅计算匹配 DeepStream 的 GPU-to-GPU 数据流。
8. **报告 HTML+PDF**——始终使用 `.claude/skills/deepstream-import-vision-model/scripts/report/md-to-html-pdf.py`。永远不要编写自定义 HTML 生成器或直接调用 `wkhtmltopdf`。
9. **仅目标检测**——在构建任何东西之前，拒绝 `config.json` 中的非检测架构。
10. **编码器回退（强制）**——`x264enc` 和 `openh264enc` 是 **禁止** 的。在 NVENC 不可用系统上，使用 `theoraenc + oggmux`（LGPL；随 gst-plugins-base 提供；输出为 `.ogv`）。如果 `theoraenc`/`oggmux` 缺失，则跳过视频创建（`DS_SINGLE_STREAM_MODE=skipped`）。报告使用的模式：`nvv4l2h264enc` / `theoraenc-fallback` / `skipped`。
11. **视频源（强制）**——默认始终为 `sample_720p.mp4`（1280×720）。永远不要自主替换 `sample_1080p_h264.mp4` 或任何其他文件。仅在用户明确提供路径时（通过 `DS_VIDEO` 环境变量或脚本参数）使用不同视频。

## 示例

**默认模型，端到端。** 引导一次，然后运行完整管道：

```bash
docker run --rm -it --gpus all --shm-size=16g -v "$PWD":/work -w /work \
  --entrypoint bash nvcr.io/nvidia/deepstream:9.1-triton-multiarch \
  .claude/skills/deepstream-import-vision-model/setup.sh
# 然后："使用 deepstream-import-vision-model 运行 PekingU/rtdetr_r50vd"
```

**SafeTensors 模型没有发布的 ONNX。** 步骤 2b 首先导出它；包装器报告生成图的后端，如果批处理维度被烘焙，则大声失败：

```bash
bash .claude/skills/deepstream-import-vision-model/scripts/model/safetensors-to-onnx.sh \
  models/$MODEL_NAME/hf_model models/$MODEL_NAME/onnx_export/
#   [导出] backend=dynamo
#   [导出] dynamo 产生静态批处理维度；尝试下一个后端
#   [导出] backend=legacy-torchscript
#   [导出] pixel_values shape=['batch', 3, 640, 640]
```

**固定 Hub 版本** 以实现可重复的构建——任何导出器标志都直接传递：

```bash
bash .claude/skills/deepstream-import-vision-model/scripts/model/safetensors-to-onnx.sh \
  PekingU/rtdetr_r50vd models/rtdetr/onnx_export --revision <commit-sha> --opset 18
```

## 管道时间

包装每个步骤：

```bash
STEP_START=$(date +%s.%N)
# ... 步骤命令 ...
STEP_END=$(date +%s.%N)
STEP_DURATION=$(python3 -c "print(round($STEP_END - $STEP_START, 2))")   # bc 不在容器中；python3 总是存在
echo "[步骤 N] 在 ${STEP_DURATION}s 内完成"
```

跟踪 `PIPELINE_START`（在步骤 1 之前）和 `PIPELINE_END`（在步骤 8 之后）。在基准测试报告中报告所有持续时间。

## 报告输出（强制——所有 3 种格式）

1. `benchmark_report.md` — markdown 源（12 个强制部分）
2. `benchmark_report.html` — 样式化 HTML（图表 base64 内联，无本地文件访问）
3. `benchmark_report_{model_name}.pdf` — 通过 `md-to-html-pdf.py`；通过计算 HTML 输出中 `data:image/png` 出现次数来验证图表是否嵌入：`grep -o 'data:image/png' benchmark_report.html | wc -l` 应等于 5

使用共享 venv 激活时运行图表和报告脚本：`source build/.venv_optimum/bin/activate`。

## 参考文档

**重要**：在开始每个阶段之前，请阅读相关参考文档。**不要**从记忆中生成代码。

| 文档 | 使用时 |
|----------|----------|
| [references/model-acquire.md](references/model-acquire.md) | 步骤 1–3：HF/NGC URL 解析，格式检测，ONNX 下载，SafeTensors 导出，标签提取 |
| [references/engine-build.md](references/engine-build.md) | 步骤 4–5：trtexec 引擎构建，基准测试，PEAK_GPU_STREAMS 推导，迭代缩放 |
| [references/pipeline-run.md](references/pipeline-run.md) | 步骤 6–7：自定义 bbox 解析器，nvinfer 配置，单流验证，KITTI 转储，多流基准测试 |
| [references/report-generation.md](references/report-generation.md) | 步骤 8：benchmark_data.json，5 个图表，12 部分markdown报告，HTML + PDF |

## 脚本

由 `install.sh` 安装到 `.claude/skills/deepstream-import-vision-model/scripts/`。

| 脚本 | 阶段 | 目的 |
|--------|-------|---------|
| `model/hf-list-files.sh` | 1–3 | 列出 HuggingFace 仓库文件 |
| `model/hf-download-config.sh` | 1–3 | 从 HF 下载 config.json |
| `model/ngc-list-files.sh` | 1–3 | 列出 NGC 模型文件 |
| `model/ngc-download.sh` | 1–3 | 下载 NGC 模型存档 |
| `model/safetensors-to-onnx.sh` | 1–3 | 导出 SafeTensors → ONNX via `torch.onnx.export`（包装器） |
| `model/safetensors_to_onnx.py` | 1–3 | 导出器——dynamo 后端，TorchScript 回退，验证动态批处理 |
| `model/inspect-onnx.py` | 1–5 | 检查 ONNX 输入/输出形状 |
| `model/make-static-batch-onnx.py` | 4–5 | 将批处理维度烘焙到 ONNX |
| `model/cleanup.sh` | 任何 | 删除暂存目录，保留共享 venv |
| `engine/benchmark-trtexec.sh` | 4–5 | 使用标准标志运行 trtexec |
| `deepstream/ds-single-stream.sh` | 6–7 | 单流视觉验证（NVENC 主要；theoraenc+oggmux 回退；如果没有则跳过） |
| `deepstream/ds-sweep.sh` | 6–7 | 2 阶段批处理大小扫描 |
| `deepstream/benchmark-ds.sh` | 6–7 | 固定流 DS 基准测试 |
| `deepstream/ds-kitti-dump.sh` | 6–7 | 通过 deepstream-app 进行 KITTI 检测转储 |
| `deepstream/ds-perf-run.sh` | 7 | 步骤 7c 两运行基准测试——包装 `deepstream-app` 使用 `enable-perf-measurement=1`，为报告解析器写入固定名称日志 |
| `deepstream/extract-frame.sh` | 6–7 | 从输出视频提取样本帧（`.mp4` NVENC 路径或 `.ogv` theoraenc 回退） |
| `report/generate-benchmark-charts.py` | 8 | 生成 5 个基准测试 PNG 图表 |
| `report/md-to-html-pdf.py` | 8 | Markdown → 样式化 HTML → PDF（规范基准测试报告路径） |
| `report/md-to-pdf.sh` | 任何 | Markdown → PDF via pandoc/pdflatex — 仅用于设计文档和参考，**不**用于基准测试报告（使用 md-to-html-pdf.py） |
| `report/report-style.css` | 8 | HTML 报告的 CSS |
| `report/render-mermaid-for-pdf.py` | 8 | Mermaid 图表 → PNG |
| `report/mermaid-puppeteer.json` | 8 | Vetted Puppeteer 配置用于 Mermaid（沙盒；非 root） |
| `report/mermaid-puppeteer-root.json` | 8 | Vetted Puppeteer 配置用于 Mermaid（作为 root 运行时使用） |

## 快速错误参考

| 错误 | 修复 |
|-------|-----|
| 倾斜/斜向边界框 | 解析器结构未零初始化——使用 `NvDsInferObjectDetectionInfo obj = {};` |
| 零 KITTI 文件 | `gie-kitti-output-dir` 未被 nvinfer 读取——使用 `ds-kitti-dump.sh`（包装 `deepstream-app`） |
| 引擎每次 DS 运行重建 | `model-engine-file` 路径错误——检查相对于 `config/` 目录的相对路径 |
| `setDimensions` 负数维度 | 在 nvinfer 配置中添加 `infer-dims=3;H;W` 用于动态 ONNX 模型 |
| `--memPoolSize` 工作空间 0.03 MiB | 使用 `M` 后缀而不是 `MiB` — 例如 `--memPoolSize=workspace:32768M` |
| ForeignNode 构建失败（DETR） | 运行 `onnxsim` — 见 references/engine-build.md。在 TRT 10.16 上使用任何导出后端均未重现 |
| ONNX 有静态批处理维度 | 两个导出后端都对其进行了特殊化——见 references/model-acquire.md 中的注意事项 |
| 零检测 | 错误的 `net-scale-factor` — 检查 references/pipeline-run.md 中的模型家族表 |
| `No module named 'pyservicemaker'` | 安装到 venv：`pip install /opt/nvidia/deepstream/.../pyservicemaker*.whl` |
