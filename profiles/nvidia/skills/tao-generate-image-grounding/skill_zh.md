# 图像 grounding 流水线

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

将 `(图像, 标题)` 对转换为每个图像的 grounding 注释：清理后的标题、具有字符范围的指代表达式，以及每个表达式的像素空间边界框。单个 VLM（Gemini 或任何 OpenAI 兼容端点）处理这两个步骤。

## 目的

为指代表达式和 grounding 模型生成短语 grounding 训练数据。VLM 充当“教师”注释员：步骤 0 从标题中提取指代表达式，同时查看图像；步骤 1 为每个图像的每个表达式返回一组 bbox。

## 流水线架构

```
步骤 0：表达式提取  → VLM 清理标题，提取指代表达式 + 字符范围
步骤 1：短语 grounding       → VLM 返回每个表达式的像素 bbox + 分数
```

可以通过 `workflow.steps` 分别选择步骤。每个步骤将每个样本的检查点写入 `step_<N>_*/.ckpt/<sample_id>.json` 并在重新运行时跳过已处理的记录。设置 `workflow.force_reprocess: true` 以忽略检查点并从头开始重新处理。

## 说明

### 初始设置

当用户想要运行此流水线时，请按照以下步骤操作：

1. **输入 JSONL**：请求 JSONL 路径。每行必须是一个对象，如 `{"image_path": "...", "caption": "..."}`。`image_path` 可以是绝对路径或相对路径。
2. **图像根目录**：如果任何 `image_path` 值是相对的，请设置 `data.image_root` 为它们应该解析的目录。
3. **API 访问**：询问用户他们想要使用哪个 VLM 端点。提供这五个选项并根据选择采取行动：
   1. **Gemini** — 设置 `vlm.backend: "gemini"`；需要 `GOOGLE_API_KEY`（环境变量或 `vlm.gemini.api_key`）。
   2. **NIM**（例如 `https://inference-api.nvidia.com/v1`）— 设置 `vlm.backend: "openai"`；收集 `base_url`、`model_name` 和 `api_key`。
   3. **TAO 推理微服务**（自托管，OpenAI 兼容）。确认服务器是否已经在运行：
      - **运行中** — 收集 `base_url`、`model_name` 和（可选的）`api_key`；设置 `vlm.backend: "openai"`。
      - **未运行** — 指导用户通过 `skills/applications/tao-run-inference-service` 技能，该技能将本地 TAO 推理微服务与 OpenAI 兼容的 API 启动。在承诺特定模型之前，检查 `skills/applications/tao-run-inference-service/references/service.yaml` 中的 `valid_network_arch_config_basenames`。服务器启动后，收集 `base_url`、`model_name` 和（可选的）`api_key`；设置 `vlm.backend: "openai"`。
   4. **vLLM**（自托管，OpenAI 兼容）。确认服务器是否已经在运行：
      - **运行中** — 收集 `base_url`、`model_name` 和（可选的）`api_key`；设置 `vlm.backend: "openai"`。
      - **未运行** — 按照 [references/vllm_server.md](references/vllm_server.md) 安装和启动 vLLM 服务器，然后收集 `base_url`、`model_name` 和（可选的）`api_key`；设置 `vlm.backend: "openai"`。
   5. **自定义**（任何其他 OpenAI 兼容端点）— 设置 `vlm.backend: "openai"`；收集 `base_url`、`model_name` 和（可选的）`api_key`。

   如果用户没有端点并且不想设置一个，请停止并帮助解决 API 访问问题。
4. **流水线步骤**：选择以下之一：
   - 完整流水线：`["0", "1"]`
   - 仅表达式提取：`["0"]`
   - 仅 grounding：`["1"]`，这需要现有的步骤-0 输出在 `results_dir/step_0_expression_extraction/annotations.jsonl`
5. **继续运行与全新运行**：默认情况下，流水线重用检查点并跳过已完成记录。要重新处理所有内容，请设置 `image_grounding.workflow.force_reprocess=true`。

### 运行流水线

流水线在 TAO Toolkit 容器内通过 `auto_label` CLI 运行：

```bash
auto_label generate -e /path/to/spec.yaml \
    results_dir=/results \
    image_grounding.data.input_jsonl=/data/captions.jsonl \
    image_grounding.data.image_root=/data/images \
    image_grounding.vlm.gemini.api_key=$GOOGLE_API_KEY
```

生成默认 spec：`auto_label default_specs results_dir=/results module_name=auto_label`，然后设置 `autolabel_type: "image_grounding"`。所有字段都支持在命令行上使用 Hydra 点标记覆盖。

参见 [references/configuration.md](references/configuration.md) 了解完整的 YAML 结构、所有参数、模型/端点设置和错误模式。

### 推荐的试点工作流

1. 在 5-10 张图像上运行两个步骤
2. 检查 `step_0_expression_extraction/annotations.jsonl` — `cleaned_caption` 和 `expressions[]` 是否准确？是否捕获了正确的名词短语？
3. 检查 `step_1_grounding/annotations.jsonl` — `expressions[].instances[]` 中的 bbox 是否正确？置信分数是否合理？
4. 如果质量不足，将 VLM 切换到更强的模型（例如 `gemini-2.5-pro`）或提高 `media_resolution`/`max_output_tokens`，然后使用 `force_reprocess=true` 重新运行。
5. 满意后，扩展到完整数据集。

## 配置

关键配置字段（完整参考在 [references/configuration.md](references/configuration.md)）：

| 字段 | 默认值 | 描述 |
|------|--------|-------|
| `workflow.steps` | `["0","1"]` | 执行哪些流水线步骤（`"0"` = 表达式，`"1"` = grounding） |
| `workflow.max_workers` | `4` | 每个步骤的并行线程数（注意 API 速率限制） |
| `workflow.force_reprocess` | `false` | 忽略每个样本的检查点并从头开始重新处理 |
| `vlm.backend` | `"gemini"` | `"gemini"` 或 `"openai"`（OpenAI 兼容端点） |
| `data.input_jsonl` | 必须提供 | 输入 JSONL 路径，每行包含 `image_path` + `caption` |
| `data.image_root` | `""` | 可选的前缀，用于解析相对 `image_path` 条目 |

## 输入

一个位于 `data.input_jsonl` 的 JSONL 文件。每行一个 JSON 对象：

| 字段 | 必须提供 | 描述 |
|------|----------|-------|
| `image_path` | 是 | 绝对路径，或相对于 `data.image_root` 解析的相对路径 |
| `caption` | 是 | 图像的自由文本标题 |
| `image_id` | 否 | 稳定标识符；如果缺失，则从文件名自动派生 |
| `width`, `height` | 否 | 像素中的图像尺寸；如果缺失，则默认为 `1920×1080` 以用于 bbox 夹紧 |

## 输出

所有输出都进入 `results_dir/`：

- `step_0_expression_extraction/annotations.jsonl` — 每条记录的输出，增加了 `cleaned_caption` 和 `expressions[]`（每个表达式具有 `text`、`expression_id`、`char_span`、空的 `instances[]`）。
- `step_1_grounding/annotations.jsonl` — 相同记录，`expressions[].instances[]` 已填充（每个实例具有像素空间中的 `bbox: [x1,y1,x2,y2]`、`score` 在 `[0.0, 1.0]` 和 `bbox_id`）。
- `results_dir/annotations.jsonl` — 最后一步输出的副本，方便使用。
- `step_<N>_*/.ckpt/<sample_id>.json` — 用于继续的每个样本检查点。

## 先决条件

- **容器**：`nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt` <!-- versions-key: images.tao_toolkit.pyt -->
- **API 访问**：至少一个 VLM 端点（Gemini API 密钥或能够处理图像输入的 OpenAI 兼容端点）
