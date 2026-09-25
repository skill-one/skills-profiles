# 图像指代表达流程

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

使用 KITTI 格式的边界框标签从图像生成指代表达和 grounding 注释。单个 VLM（Gemini 或任何 OpenAI 兼容端点）运行四个步骤：对象区域描述、整体图像标题、与边界框绑定的分组 grounding 表达式，以及可选的双重检查验证步骤。

## 目的

将 `(图像, KITTI 标签)` 对转换为一个统一的 `annotations.jsonl`，其中包含丰富的、有 grounding 的指代表达。VLM 充当“教师”标注员：步骤 0-1 查看图像；步骤 2 将步骤 0 的输出分组为带边界框列表的分组短语；步骤 3（可选）重新检查这些边界框与图像，并纠正不匹配。

## 流程架构

```
步骤 0：区域表达式  ──┐
                          ├──▶  步骤 2：Grounding 表达式  ──▶  [步骤 3：双重检查]
步骤 1：图像标题  ──────┘                                                   (可选)
```

- **步骤 0 (region_expr)** — VLM 对每个 KITTI 边界框（`bbox_2d`、`type`、`color`、`description`）发出一个简短的判别短语。
- **步骤 1 (image_caption)** — VLM 发出一个整体、与位置无关的场景标题。
- **步骤 2 (grounding_expr)** — VLM 将步骤 0 的对象分组为分组短语，并为每个组返回一个边界框列表，可选地使用步骤 1 的标题作为额外上下文。
- **步骤 3 (double_check)** — VLM 重新检查每个步骤 2 的边界框与图像；移除不匹配的，微调略微偏移的边界框。

步骤 0 和 1 在单个线程池中并行运行（它们只依赖于种子记录）。每个步骤写入自己的 `step_<N>_*/annotations.jsonl`，并在重新运行时跳过已处理的图像，除非 `workflow.force_reprocess: true`。

## 说明

### 初始设置

当用户想要运行此流程时，请按照以下步骤操作：

1. **图像**：请求 `data.image_dir`，包含 `.jpg`、`.jpeg` 或 `.png` 图像的目录。
2. **KITTI 标签**：请求 `data.kitti_label_dir`，包含每个图像一个 `.txt` 标签文件的目录。每行标签必须使用 KITTI 格式：`<type> <truncated> <occluded> <alpha> <bbox_left> <bbox_top> <bbox_right> <bbox_bottom> ...`。少于 8 个字段的行将被静默跳过。即使仅运行步骤 1 也需要设置此值，因为步骤 0 和 2 需要。
3. **从现有注释恢复**：如果用户已经有一个来自先前运行的统一 `annotations.jsonl`，请将 `data.input_annotations_jsonl` 设置为该文件，而不是从 `data.image_dir` 和 `data.kitti_label_dir` 种子。
4. **API 访问**：询问用户他们想使用哪个 VLM 端点。提供以下五个选项并执行选择：
   1. **Gemini** — 设置 `vlm.backend: "gemini"`；需要 `GOOGLE_API_KEY`（环境变量或 `vlm.gemini.api_key`）。
   2. **NIM**（例如 `https://inference-api.nvidia.com/v1`）— 设置 `vlm.backend: "openai"`；收集 `base_url`、`model_name` 和 `api_key`。
   3. **TAO 推理微服务**（自托管，OpenAI 兼容）。确认服务器是否已经在运行：
      - **运行** — 收集 `base_url`、`model_name` 和（可选）`api_key`；设置 `vlm.backend: "openai"`。
      - **未运行** — 指导用户通过 `skills/applications/tao-run-inference-service` 技能，该技能将本地启动一个 OpenAI 兼容 API 的 TAO 推理微服务。在承诺特定模型之前，检查 `skills/applications/tao-run-inference-service/references/service.yaml` 中的 `valid_network_arch_config_basenames`。服务器启动后，收集 `base_url`、`model_name` 和（可选）`api_key`；设置 `vlm.backend: "openai"`。
   4. **vLLM**（自托管，OpenAI 兼容）。确认服务器是否已经在运行：
      - **运行** — 收集 `base_url`、`model_name` 和（可选）`api_key`；设置 `vlm.backend: "openai"`。
      - **未运行** — 按照 [references/vllm_server.md](references/vllm_server.md) 安装和启动 vLLM 服务器，然后收集 `base_url`、`model_name` 和（可选）`api_key`；设置 `vlm.backend: "openai"`。
   5. **自定义**（任何其他 OpenAI 兼容端点）— 设置 `vlm.backend: "openai"`；收集 `base_url`、`model_name` 和（可选）`api_key`。

   如果用户没有端点且不想设置，请停止并帮助解决 API 访问问题。
5. **工作流步骤**：选择以下之一：
   - 完整流程：`["0", "1", "2", "3"]`
   - 无标题生成：`["0", "2", "3"]`，其中步骤 2 落回仅图像的上下文
   - 无验证：`["0", "1", "2"]`
   - 自定义子集：任何支持的分步子集
6. **输出格式**：选择以下之一：
   - `jsonl`：统一架构仅
   - `legacy`：仅字节兼容的 `.txt.stepN` 文件
   - `both`：写入两种格式，并为下游工具是默认设置

### 运行流程

流程在 TAO Toolkit 容器内通过 `auto_label` CLI 运行：

```bash
auto_label generate -e /path/to/spec.yaml \
    results_dir=/results \
    image_referring_expression.data.image_dir=/data/images \
    image_referring_expression.data.kitti_label_dir=/data/labels \
    image_referring_expression.vlm.gemini.api_key=$GOOGLE_API_KEY
```

生成默认 spec：`auto_label default_specs results_dir=/results module_name=auto_label`，然后设置 `autolabel_type: "image_referring_expression"`。所有字段都支持在命令行上使用 Hydra 点标记覆盖。

参见 [references/configuration.md](references/configuration.md) 了解完整的 YAML 结构、所有参数、模型/端点设置和错误模式。

### 推荐的试点工作流

1. 在 5-10 张图像上运行所有四个步骤。
2. 检查 `step_0_region_expr/annotations.jsonl` — 对象类型、颜色和判别短语是否准确？
3. 检查 `step_2_grounding_expr/annotations.jsonl` — 对象是否合理分组，边界框坐标是否与描述的组匹配？
4. 检查 `step_3_double_check/annotations.jsonl` — 是否移除了不匹配的边界框或微调了略微偏移的边界框？是否引入了新错误（罕见）？
5. 如果质量不足，将 VLM 切换到更强的模型（例如 `gemini-2.5-pro` 或更大的 Qwen3-VL 端点），提高 `media_resolution` / `max_output_tokens`，然后使用 `workflow.force_reprocess=true` 重新运行。
6. 满意后，扩展到完整数据集。

## 配置

关键配置字段（完整参考在 [references/configuration.md](references/configuration.md)）：

| 字段 | 默认值 | 描述 |
|------|--------|-------|
| `workflow.steps` | `["0","1","2","3"]` | 执行哪些步骤（`0`=region_expr, `1`=image_caption, `2`=grounding_expr, `3`=double_check) |
| `workflow.max_workers` | `4` | 每个步骤的并行线程数（注意 API 速率限制） |
| `workflow.force_reprocess` | `false` | 忽略缓存的每步输出并从头重新处理 |
| `workflow.output_format` | `"jsonl"`（在默认 spec 中设置为 `"both"`） | `"jsonl"`、`"legacy"` 或 `"both"` |
| `vlm.backend` | `"gemini"` | `"gemini"` 或 `"openai"`（OpenAI 兼容端点） |
| `data.image_dir` | 必须提供 | 输入图像目录（`.jpg` / `.jpeg` / `.png`） |
| `data.kitti_label_dir` | 必须提供（除非恢复） | KITTI 格式 `.txt` 标签文件目录 |
| `data.input_annotations_jsonl` | `""` | 可选的预种子 `annotations.jsonl`（跳过 KITTI 种子） |

## 输入

种子流程的两种方式：

1. **图像目录 + KITTI 标签**（默认）。设置 `data.image_dir` 和 `data.kitti_label_dir`。协调器遍历图像目录，读取匹配的 `<stem>.txt` KITTI 文件，解析边界框（字段 0 + 4-7），通过 PIL 读取每个图像的 `width`/`height`，并将 `seed_annotations.jsonl` 写入 `results_dir/`。
2. **预种子注释 JSONL**（恢复 / 预计算区域）。将 `data.input_annotations_jsonl` 设置为一个文件，每行包含一个 `{"image_id", "image_path", "width", "height", "kitti_bboxes": [...]}` 对象。

## 输出

所有输出都到 `results_dir/`：

- `seed_annotations.jsonl` — 初始每张图像记录（除非提供了 `input_annotations_jsonl`）。
- `step_0_region_expr/annotations.jsonl` — 添加 `regions[]`（每个带有 `bbox`/`bbox_2d`、`type`、`color`、`description`）。
- `step_1_image_caption/annotations.jsonl` — 添加 `caption`（字符串）。
- `step_2_grounding_expr/annotations.jsonl` — 添加 `expressions[]`（每个 `{text, instances: [{bbox: [x1,y1,x2,y2]}]}`）。
- `step_3_double_check/annotations.jsonl` — 与步骤 2 形状相同，但边界框被移除/更新。
- `results_dir/annotations.jsonl` — 最后完成步骤的输出副本。
- 当 `workflow.output_format` 为 `"legacy"` 或 `"both"` 时，每个步骤还会写入字节兼容的 `step_<N>_*/labels/<stem>.txt.stepN` 文件，用于原始 2d-data-engine 工具。

## 前置条件

- **容器**：`nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt` <!-- versions-key: images.tao_toolkit.pyt -->
- **API 访问**：至少一个 VLM 端点（Gemini API 密钥或能够处理图像输入的 OpenAI 兼容端点）
- **PIL / Pillow**：在种子时读取图像尺寸需要（已在 TAO 容器中提供）
