# 视频推理标注流程

> **是否独立安装？** 如果本次会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

通过生成多级字幕、结构化描述和问答对（多项选择、二元、开放式），并附带逐步推理轨迹，从视频中生成思维链训练数据集。默认情况下与领域无关——可自定义提示词用于任何视频领域。

## 目的

将原始视频转换为视频理解模型的思维链问答训练数据。视觉语言模型（VLM，例如 Gemini、Qwen）充当“教师”标注员：步骤 0–1 需要模型观看视频（VLM 调用）；步骤 2–3 是文本到文本（更便宜的 LLM 调用）。

## 流程架构

```
步骤 0:  [可选] 过滤和分类视频  → 保留与领域相关的，将异常与正常分类
步骤 1a: 全局 + 密集字幕               → VLM：叙事摘要 + 带时间戳的事件
步骤 1b: 分块字幕                         → VLM：固定时长片段微字幕
步骤 1c: [可选，仅异常] 高亮             → LLM 提取异常时间戳，VLM 标注片段
步骤 2:  描述合成                  → LLM：将字幕合成结构化叙述
步骤 3:  问答生成                          → LLM：多项选择、二元、开放式带推理
步骤 4:  解析输出                          → 每个任务的 `tao-vl-reason-v1.0` JSON 文件
```

可以通过 `workflow.steps` 选择单个步骤。该流程具有内置的恢复功能——每个步骤都会跳过已处理的视频，因此即使提示词微调后重新运行也是安全的。

## 初步咨询

当用户调用此技能时，按顺序询问这些问题。不要跳过——在开始时正确设置领域和 VLM 访问可以防止浪费运行。

### 1. 视频

- 视频目录路径和/或每行包含 `{"video_path": "..."}` 的 JSONL。
- 确认格式（优先 `.mp4`；`.avi`、`.mov`、`.mkv` 也支持）。

### 2. 领域 — 驱动提示词选择

询问用户：*"这些视频来自什么领域？* 选择以下分支之一：

| 领域 | 操作 |
|---|---|
| **general** | 使用默认提示词。设置 `prompts_module: ""`（或省略）。内置的 `nvidia_tao_ds.auto_label.video_reasoning_annotation.prompts` 覆盖与领域无关的内容。 |
| **traffic** (CCTV 十字路口、高速公路；排除行车记录仪) | 使用参考模块。设置 `prompts_module: "nvidia_tao_ds.auto_label.video_reasoning_annotation.prompts_traffic"`，**或者**将 `references/prompts_traffic.py` 复制到用户的项目的用户目录并针对其特定摄像头角度进行微调，然后指向 `prompts_module` 指向副本。 |
| **warehouse** (工业场址 CCTV — 安全、运营、安防) | 相同模式。设置 `prompts_module: "nvidia_tao_ds.auto_label.video_reasoning_annotation.prompts_warehouse"`，或者复制 `references/prompts_warehouse.py` 并进行微调。 |
| **custom** (其他任何领域) | **在 [references/domain_adaptation.md](references/domain_adaptation.md) 中运行工作坊**。它将引导用户完成：阶段 1 — 用户希望模型回答的问题类型；阶段 2 — 标注需求清单；阶段 3 — 填充 `nvidia_tao_ds.auto_label.video_reasoning_annotation.prompt_template` 中的 `[PLACEHOLDER]` 标记。上述两个参考模块是可工作的示例，供用户参考。在运行任何流程之前完成此操作。 |

### 3. 异常 / 正常 / 混合

- 混合数据集 → `workflow.mode: "auto"`（步骤 0 对每个视频进行分类）。
- 预分割仅异常 → `workflow.mode: "anomaly"`，删除步骤 0。
- 预分割仅正常 → `workflow.mode: "normal"`，删除步骤 0 和 1c。

### 4. VLM / LLM 端点 — 在运行前确认访问权限

- **Gemini**（`vlm.backend` 和 `llm.backend` 的默认值）：用户需要设置 `GOOGLE_API_KEY`，或者将密钥放在 YAML 中。
- **OpenAI 兼容**（Qwen 通过 vLLM、NIM 端点等）：用户提供 `base_url`、`model_name` 和 `api_key`。
- 步骤 2–3 是纯文本的——即使 `vlm.backend` 是前沿视频模型，`llm.backend` 也可以使用较小/更便宜的 LLM。

如果用户**没有任何端点**并且希望自行托管，请将他们指向 `skills/applications/tao-run-inference-service` 技能——一个可以本地部署网络特定 TAO 推理微服务的流程，并暴露一个 OpenAI 兼容的端点。应支持 Cosmos、Qwen 和 Gemma。在依赖特定模型之前，请检查 `skills/applications/tao-run-inference-service/references/service.yaml` 中的当前 `valid_network_arch_config_basenames` 列表。

如果用户没有准备好端点访问权限，并且尚未准备好设置一个，请在此停止，并帮助他们先解决。

### 5. 试点运行 vs 全量运行

- **推荐 5–10 个视频的试点运行**，当领域是 `custom` 时，当任何提示词被编辑时，或者当这是用户第一次运行时。
- **全量运行是安全的**，对于 `general` / `traffic` / `warehouse`，一旦用户在相同类型的数据上验证了输出质量。
- 流程具有内置的恢复功能，因此试点运行后跟一个全量运行不会重新处理试点视频。

## 快速入门

流程在 TAO Toolkit 容器内通过 `auto_label` CLI 运行：

```bash
auto_label generate -e /path/to/spec.yaml \
    results_dir=/results \
    video_reasoning_annotation.data.video_root=/videos \
    video_reasoning_annotation.vlm.gemini.api_key=$GOOGLE_API_KEY \
    video_reasoning_annotation.workflow.mode=auto
```

生成一个默认的 spec 以开始：

```bash
auto_label default_specs results_dir=/results module_name=auto_label
# 然后设置：  autolabel_type: "video_reasoning_annotation"
```

所有字段都支持在命令行上使用 Hydra 点标记覆盖。有关完整的 YAML 参考（每个字段、模型/端点设置、错误模式），请参阅 [references/configuration.md](references/configuration.md)。

## 试点流程

在运行 5–10 个视频试点时使用此流程：

1. 使用选择的 `prompts_module` 和 `workflow.mode` 在试点子集上运行流程。
2. 检查 `results_dir/step_1a_caption/captions.jsonl` — 字幕是否准确，是否捕捉到正确的详细程度？
3. 检查 `results_dir/step_3_qa/qa_output.jsonl` — 问题是否有意义，答案是否正确，推理是否逻辑？
4. 如果质量不足：调整提示词（如果领域自定义则在 `prompts_module` 中，或者如果领域模块过调则回退到 `general`），并重新运行。流程会自动跳过已处理的视频。
5. 满意后，通过将 `data.video_root`（或 `data.input_jsonl_files`）指向完整数据集并使用相同的 `results_dir`（恢复）或一个新的（全量重新运行）来扩展到完整数据集。

质量会逐级累积——错误的字幕会产生错误的描述，错误的描述会产生错误的问答。首先关注步骤 1a/1b 输出进行迭代；一旦字幕正确，描述和问答通常会自动改进。

## 配置摘要

关键字段（完整参考在 [references/configuration.md](references/configuration.md)）：

| 字段 | 默认值 | 描述 |
|---|---|---|
| `workflow.steps` | `["0","1a","1b","1c","2","3","4"]` | 执行哪些流程步骤 |
| `workflow.mode` | `"auto"` | `"auto"`、`"anomaly"` 或 `"normal"` |
| `vlm.backend` | `"gemini"` | `"gemini"` 或 `"openai"`（OpenAI 兼容） |
| `llm.backend` | `"gemini"` | 相同选项；纯文本，较便宜的模型即可 |
| `workflow.max_workers` | `4` | 每个步骤的并行线程数（注意 API 速率限制） |
| `license` | `""` | 可选：写入步骤 4 输出的 `metadata.license`（例如 `"CC-BY-4.0"`） |
| `description_extra` | `""` | 可选：附加到步骤 4 元数据中每个任务描述的额外文本 |
| `prompts_module` | `""` | 自定义提示词模块的点标记导入路径 |

## 提示词

- **内置（general）**：`nvidia_tao_ds.auto_label.video_reasoning_annotation.prompts` — 与领域无关，默认使用。
- **模板**：`nvidia_tao_ds.auto_label.video_reasoning_annotation.prompt_template` — 相同 26 个键，带有 `[PLACEHOLDER]` 标记用于领域自定义。
- **参考模块**（`consultation` 中 `traffic` / `warehouse` 分支的工作示例）：[references/prompts_traffic.py](references/prompts_traffic.py)、[references/prompts_warehouse.py](references/prompts_warehouse.py)。
- **自定义领域**：请参阅 [references/domain_adaptation.md](references/domain_adaptation.md) 获取完整工作坊和占位符参考。

## 输入

- **`video_root`**：视频目录（递归遍历 `.mp4`、`.avi`、`.mov`、`.mkv`）。
- **`input_jsonl_files`**：包含 `{"video_path": "..."}` 每行的 JSONL 文件列表。`video` 键也接受；允许额外字段。
- **`filter_field`**：可选的布尔字段用于过滤 JSONL 条目。

提供 `video_root`、`input_jsonl_files` 或两者（列表合并）。

## 输出

所有输出都存放在 `results_dir/`，每个步骤有子目录 (`step_0_filter/`、`step_1a_caption/`、…、`step_4_output/`)：

- **步骤 0–3**：JSONL — 每个视频每行一个 JSON 对象。
- **步骤 4**：每个非空任务类型一个 `<task>.json`，在 **`tao-vl-reason-v1.0`** 封装中。最多 10 个文件：`mcq.json`、`mcq_openended.json`、`bcq.json`、`bcq_openended.json`、`open_qa.json`、`causal_linkage.json`、`temporal_localization.json`、`temporal_description.json`、`scene_description.json`、`video_summarization.json`。

每个步骤 4 文件如下所示：

```json
{
  "format": "tao-vl-reason-v1.0",
  "metadata": {"type": "annotation", "task": "<task>", "date": "YYYY-MM-DD",
               "description": "<per-task + description_extra>", "license": "<from config>"},
  "media_root": "<data.video_root>" | null,
  "items": [{"video_id": "...", "question": "...", "answer": "...", "reasoning": "..."}, ...]
}
```

`media_root` 反射 `data.video_root`（或 `null` 当未设置时）；每个项的 `video_id` 是条目的视频路径，去除了 `video_root` 前缀。在 spec 中设置 `license` 和 `description_extra` 以填充元数据。

## 前置条件

- **容器**：`nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt`。 <!-- versions-key: images.tao_toolkit.pyt -->
- **ffmpeg / ffprobe**：用于分块字幕（步骤 1b）和异常提取（步骤 1c）所必需。
- **VLM 端点**：至少一个——Gemini API 密钥或 OpenAI 兼容端点。
