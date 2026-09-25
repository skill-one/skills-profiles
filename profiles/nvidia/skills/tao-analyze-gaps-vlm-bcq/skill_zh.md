# VLM 二分类差距分析

> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

读取 VLM 预测 JSON 文件，将每个模型响应与真实值进行比较，并将 FP/FN 失败案例写入 JSONL 文件，并附带汇总报告。使用 TAO 数据服务规格文件运行它；数据服务入口点需要 `-e <spec>`。

## 目的

在二分类是/否评估任务上运行 VLM 后，需要将预测结果与真实值进行比较以识别失败案例。此技能生成 FP（假阳性）和 FN（假阴性）样本的结构化列表，下游 RCCA 阶段（例如，cosmos 生成、根本原因分析）将其用于驱动 DEFT 迭代。

## 使用方法

使用捆绑的辅助工具生成 `vlm_bcq_spec.yaml`：

```bash
python3 skills/data/tao-analyze-gaps-vlm-bcq/scripts/prepare_vlm_bcq_spec.py \
  --predictions-json /path/to/results.json \
  --videos-dir /path/to/videos/root \
  --results-dir /path/to/output/gaps \
  --output-spec /path/to/output/gaps/vlm_bcq_spec.yaml
```

当预测 `video_id` 值已经是绝对路径时，省略 `--videos-dir`。生成的规格具有以下结构：

```yaml
predictions_json: /path/to/results.json
videos_dir: ""
results_dir: /path/to/output/gaps
```

当预测中的 `video_id` 值是相对路径时，设置 `videos_dir`：

```yaml
predictions_json: /path/to/results.json
videos_dir: /path/to/videos/root
results_dir: /path/to/output/gaps
```

在 TAO Toolkit 数据服务容器内使用 `-e <spec>` 调用 `vlm_bcq` 动作：

```bash
gap_analysis vlm_bcq -e /path/to/vlm_bcq_spec.yaml
```

从选定平台请求一个 GPU（`compute_shape.gpus: 1`, `compute_shape.nodes: 1`）。VLM BCQ 差距分析不执行 GPU 计算，但数据服务镜像始终调用 `nvidia-smi`，如果没有可见的 GPU 则会失败。一个是 GPU 数量，不是设备 ID；平台选择设备。

运行后，从 `kpi_gaps_report.txt` 查看FP/FN计数，并将下游阶段指向 `kpi_gaps.jsonl`。

## 输入

- **config spec**: 使用 `-e` 传递的 YAML 文件。模板：`assets/default_vlm_bcq.yaml`。
- **predictions_json**: 预测 JSON 文件的路径。必须是一个 JSON 数组，其中每个项目都有 `video_id`、`response` 和 `gt` 字段。`response` 和 `gt` 使用词边界匹配进行解析——字符串中任何位置的 `'yes'` 或 `'no'` 都会被识别。如果两者都存在或都不存在，则跳过这些样本并显示警告。
- **videos_dir** (可选): 用于解析相对 `video_id` 路径的基本目录。如果省略，`video_id` 值将用作绝对路径。
- **results_dir**: 差距分析工件的输出目录。

**预测 JSON 格式：**
```json
[
  {
    "video_id": "/path/to/video.mp4",
    "response": "是的，有碰撞。",
    "gt": "B. 没有",
    "question": "有碰撞吗？"
  }
]
```

## 输出

- **kpi_gaps.jsonl**: 每行一个 JSON 对象，每个 FP/FN 案例的 `video_id` (绝对路径)、`error_type` (`FP` 或 `FN`)、`question`、`ground_truth`、`response`。
- **kpi_gaps_report.txt**: 人类可读的表格，显示总 FP/FN 计数。

如果没有找到差距，则不写入文件并记录消息。

## 规格字段

| 参数 | 必填 | 描述 |
|-------|------|------|
| predictions_json | 是 | 预测 JSON 文件的路径 |
| results_dir | 是 | 输出目录；如果不存在则创建 |
| videos_dir | 否 | 用于解析相对 `video_id` 路径的基本目录 |

将规格文件和它引用的所有路径保持在绑定挂载的工作区下，以便它们在容器内解析。即使添加了 Hydra 覆盖，也要传递 `-e <spec>`；当前的 TAO 数据服务入口点在处理覆盖之前硬性要求实验规格文件。

## 错误模式

| 错误 | 原因 | 修复 |
|------|------|------|
| `FileNotFoundError` | `predictions_json` 不存在 | 检查路径 |
| `requires the following argument: -e/--experiment_spec_file` | 容器未使用规格文件启动 | 编写 `vlm_bcq_spec.yaml` 并传递 `gap_analysis vlm_bcq -e <spec>` |
| `ValueError: must be a JSON array` | 预测文件不是列表 | 将预测包裹在 `[...]` 中 |
| `ValueError: missing 'gt'/'response'/'video_id'` | 预测项目缺少必填字段 | 检查并修复预测 JSON |
| 样本被静默跳过 | `response` 或 `gt` 包含 'yes'/'no' 的两者或两者皆无 | 检查日志中的警告；检查这些样本 |
