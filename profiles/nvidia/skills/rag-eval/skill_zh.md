# 磁盘上的 RAG 评估 (`corpus/` + `train.json`)

## 目的

指导代理通过 NVIDIA RAG 蓝图 **文件系统** 基准测试：准备 `corpus/` 和 `train.json`，运行 `scripts/eval/evaluate_rag.py`，调整检索和生成标志以进行 **质量** 比较，解释 RAGAS JSON 输出，以及排查故障（HTTP/流错误、空上下文、集合不匹配、裁判 API）。

对于 **延迟、吞吐量和负载测试**，请使用 **rag-perf** 技能 (`scripts/rag-perf`, `docs/performance-benchmarking.md`) —— 不要使用此技能。

## 不应使用的情况

**不要** 使用此技能来：部署或修复服务（使用 rag-blueprint）；评估没有 `corpus/` + `train.json` 布局的 API；与此评估器无关的一般机器学习实验；生产监控/告警；或延迟/吞吐量基准测试（使用 **rag-perf**）。

## 前提条件

- 代码库已克隆；**从代码库根目录运行命令**（导入和路径假设如此）。
- Python **3.11+** 和 **uv**；评估依赖项：`uv sync --project scripts/eval`。
- 可达的 **RAG 服务器** 和 **摄取器**（默认通常为 `localhost:8081` / `8082`）。
- RAGAS 的 **`NVIDIA_API_KEY`**（参见 [凭证卫生](references/benchmark-execution.md#credential-hygiene-nvidia_api_key)）；可选的 **`RAG_EVAL_JUDGE_MODEL`**。
- 传递给 `--dataset-paths` 的数据集根目录均包含 **`corpus/`** 和 **`train.json`**。

## 说明

1. **准备数据** — 确保每个数据集目录符合 [`references/dataset-and-conversion.md`](references/dataset-and-conversion.md) 中的布局和 `train.json` 规则。当源作为公共链接（网站或数据集页面）到达时，在 `corpus/` 下创建文档——优先选择 **PDF** 以保留多模态内容中的 **图像嵌入**；使用那里的模式转换 CSV/JSONL 等。
2. **运行评估** — `uv run --project scripts/eval python scripts/eval/evaluate_rag.py` 并使用 `--dataset-paths`、`--host` 和 `--port`。有关命令示例、输出和错误的更多信息，请参阅 [`references/benchmark-execution.md`](references/benchmark-execution.md)。有关标志级别的详细信息，请参阅 [`references/evaluate-rag-cli.md`](references/evaluate-rag-cli.md)。
3. **调整质量** — 在比较检索/生成配置以获取 RAGAS 分数时，根据 [`references/benchmark-execution.md`](references/benchmark-execution.md) 文档调整 `--top_k` / `--vdb_top_k`、重新排序器和查询重写开关，以及生成覆盖 (`--temperature`, `--top-p`, `--max-tokens`)。
4. **分析结果** — 使用 [`references/result-analysis.md`](references/result-analysis.md) 中的脚本；扫描 `rag_*_evaluation_summary.json` 以获取主要 RAGAS 指标。
5. **排查错误** — 使用 [错误信号表](references/benchmark-execution.md#common-error-cases-and-signals) 和下文的 **故障排除** 部分。

## 示例

**在不将密钥放入 shell 历史记录的情况下设置 API 密钥（首选模式）：** 从 git 忽略的 env 文件或密钥管理器中加载；避免提交 `.env`；如果暴露，请旋转密钥。详细信息：[`references/benchmark-execution.md#credential-hygiene-nvidia_api_key`](references/benchmark-execution.md#credential-hygiene-nvidia_api_key)。

**最小评估（密钥已在环境中）：**

```bash
uv sync --project scripts/eval
uv run --project scripts/eval python scripts/eval/evaluate_rag.py \
  --dataset-paths /path/to/my_dataset \
  --host localhost \
  --port 8081
```

**格式化输出摘要 JSON：**

```bash
python3 -m json.tool results/my_dataset/rag_my_dataset_evaluation_summary.json
```

更多示例（跳过摄取、质量扫描）：[`references/benchmark-execution.md`](references/benchmark-execution.md)。

## 限制

- 评估器行为固定于 **文件系统契约** 和 `evaluate_rag.py`；它不能替代自定义离线裁判或非 RAG 基准测试。
- **向量数据库 / 嵌入** 选择遵循已部署的摄取器和 RAG 环境——仅此 CLI 不能单独覆盖。
- **分数取决于** 检索质量、裁判模型可用性和 `NVIDIA_API_KEY`；空上下文会产生部分 RAGAS 指标（参见参考资料）。
- 大型过程细节位于 **`references/`** 下以保持路由简洁；当用户需要分步转换、完整标志或错误表时，请阅读那些文件。

## 故障排除

| 错误 / 信号 | 可能的原因 | 应该怎么办 |
|----------------|--------------|------------|
| 立即退出并提及 `NVIDIA_API_KEY` | 缺失或无效密钥 | 通过安全渠道设置密钥；参见 [`references/benchmark-execution.md`](references/benchmark-execution.md) 中的凭证卫生。 |
| `train.json 必须是一个 JSON 数组` | 错误的 JSON 形状 | 顶级对象数组；根据 [`references/dataset-and-conversion.md`](references/dataset-and-conversion.md) 进行验证。 |
| `evaluation_data.json` 中的行数少于 `train.json` | 每个查询的失败 | 检查 stderr：网络或流 JSON 错误；参见基准测试执行中的错误表。 |
| 所有 `generated_contexts` 为空 | 检索差距 | 验证集合、摄取、`top_k` / `vdb_top_k` 和 `ingestor_server_url` **不带** `/v1` 后缀。 |
| 摄取器上传时返回 404 | 坏的摄取器基础 URL | 仅传递 `http://host:port`——代码会自动追加 `/v1/`。 |

完整信号表：[`references/benchmark-execution.md#common-error-cases-and-signals`](references/benchmark-execution.md#common-error-cases-and-signals)。

## 注意事项

- **从代码库根目录运行**：`scripts/eval/evaluate_rag.py` 中的路径和导入假设如此；错误的目录会无声地破坏导入。
- **`--ingestor_server_url`**：传递 `http://host:port` 而不带 `/v1`——代码会自动追加 `/v1/`。包含 `/v1` 会导致摄取器调用时返回 404。
- **向量数据库 / 嵌入设置**：此 CLI 不设置；通过已部署的摄取器和 RAG 服务器环境变量（例如 `APP_VECTORSTORE_URL`、嵌入模型）进行配置。
- **`--model` / `--llm_endpoint`**：仅当明确设置时才转发；省略以保留服务器的配置 LLM。
- **过时的集合**：除非使用 `--force_ingestion`，否则先前运行的数据会持续存在。在跨独立运行比较质量时，使用 `--collection` 并指定一个唯一名称。
- **空上下文指标**：如果所有 `generated_contexts` 都为空，RAGAS 仅评分 `nv_accuracy` 并将其他两个指标留空——这不是无声的成功。

## 真实来源

| 项目 | 位置 |
|-------|----------|
| 驱动 | `scripts/eval/evaluate_rag.py` (`CORPUS_DIRECTORY` = `corpus`, `EVAL_DATA` = `train.json`) |
| 人类 README（始终在代码库中） | `scripts/eval/README.md` |
| 完整 CLI（标志、默认值） | `scripts/eval/evaluate_rag.py --help`；[`references/evaluate-rag-cli.md`](references/evaluate-rag-cli.md) |
| 数据集 / 转换 | [`references/dataset-and-conversion.md`](references/dataset-and-conversion.md) |
| 运行、输出、错误 | [`references/benchmark-execution.md`](references/benchmark-execution.md) |
| 结果分析脚本 | [`references/result-analysis.md`](references/result-analysis.md) |
| 延迟 / 吞吐量 | **rag-perf** 技能，`docs/performance-benchmarking.md` |

## 代理剧本

1. **运行评估** — `uv sync --project scripts/eval` 然后 `uv run --project scripts/eval python scripts/eval/evaluate_rag.py` 并使用必要的 `--dataset-paths`、`--host` 和 `--port`（以及环境 `NVIDIA_API_KEY`）。参数 `--ingestor_server_url` 是可选的（默认为 `http://localhost:8082`）；仅当覆盖摄取器端点时才传递它。
2. **质量调整** — 参见 [`references/benchmark-execution.md`](references/benchmark-execution.md)：`--top_k`/`--vdb_top_k`、重新排序器和查询重写开关、`--temperature`、`--top-p`、`--max-tokens`。
3. **数据转换** — 根据 [`references/dataset-and-conversion.md`](references/dataset-and-conversion.md)。
4. **分析结果** — [`references/result-analysis.md`](references/result-analysis.md)；快速扫描：`python3 -m json.tool results/<dataset>/rag_<dataset>_evaluation_summary.json`。
5. **排查错误** — [`references/benchmark-execution.md#common-error-cases-and-signals`](references/benchmark-execution.md#common-error-cases-and-signals)。
