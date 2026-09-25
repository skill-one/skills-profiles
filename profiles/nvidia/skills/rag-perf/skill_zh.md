# RAG-Perf — 基于配置的 perf 基准 CLI

## 目的

使用 YAML 配置驱动部署的 NVIDIA RAG Blueprint 服务器，运行服务器端的**分析过程**（每个阶段的计时、引用质量、瓶颈推理）以及可选的**aiperf 负载测试**（TTFT / E2E / token & 请求吞吐量 / 错误率），并生成统一报告。CLI 故意保持极简：`rag-perf -c <config>` 加上 `--help` / `--version`。行为完全由配置驱动；字段变化应放在 YAML 中。

## 范围

- **答案质量 / RAGAS**评分 → 使用 **rag-eval** 技能。
- **部署、修复或配置服务**（compose、helm、NIM 环境变量）→ 使用 **rag-blueprint** 技能。
- **生产监控 / 报警** — rag-perf 是一次性基准工具。
- **运行时要求**：网络可达的已部署 RAG 服务器。

## 前置条件

- 已克隆仓库；**从仓库根目录运行命令**（配置路径在预设中是相对于仓库根目录的）。
- Python **3.11+** 和 **uv** 在 PATH 中。
- 将 rag-perf 安装到其自己的 uv 管理的 venv 中：`uv sync --project scripts/rag-perf`。
- 对于单元测试：安装开发附加项 — `uv sync --project scripts/rag-perf --extra dev`（否则 `pytest-asyncio` 会缺失，异步测试在收集时出错）。
- 一个可达的 RAG 服务器（默认 `http://localhost:8081`）。对于 aiperf 阶段，必须安装捆绑的 `nvidia_rag` 端点插件 — `pip install -e ./scripts/rag-perf` 通过 `aiperf.plugins` 入口点注册它。
- 对于**合成**查询：一个 OpenAI 兼容的 chat-completions 端点，可通过 `synthetic.llm_url`（默认 `http://localhost:8999/v1/chat/completions`）访问。
- rag-perf 本身无需 `NVIDIA_API_KEY`（与 rag-eval 不同）。合成 LLM 端点可能需要其自己的认证 — 这是部署的问题。

## 说明

1. **选择一个预设。** 在 [`scripts/rag-perf/configs/`](../../scripts/rag-perf/configs) 下有三个：
   - `quick_profile.yaml` — 仅分析，~30 秒。跳过负载测试。用于检索 / reranker 调整的快速迭代。
   - `single_run.yaml` — 一个并发级别，分析 + aiperf，~2 分钟。回归检查。
   - `sweep.yaml` — 多轴扫描。`load.concurrency`、`rag.vdb_top_k`、`rag.reranker_top_k` 都是 `int | list[int]`；其中任何一个作为列表都会成为扫描轴（笛卡尔积）。

2. **编辑预设。** **必须**将 `rag.collection_names: ["<collection_name>"]` 替换为部署的 ingestor 服务器上的实际集合。通过在 ingestor 上使用 `GET /v1/collections` 验证集合是否存在。占位符 `<collection_name>` 验证良好，但每个请求在检索时都会失败。使用复制的 YAML 预设进行变体；CLI 表面故意仅配置。

3. **运行。** 从仓库根目录：
   ```bash
   uv run --project scripts/rag-perf rag-perf -c scripts/rag-perf/configs/single_run.yaml
   ```
   其他预设形式相同。CLI 仅接受 `-c / --config`（必需）、`--help`、`--version`。

4. **查看标准输出。** 每次调用按顺序打印：启动横幅、一行摘要、**完全解析的配置作为 YAML**（因此运行可从终端输出重现）、每个网格点的进度以及**shlex-连接的 aiperf 命令**（可复制粘贴形式）、**每个点的丰富摘要表**（阶段分解带条形图、引用质量、瓶颈、负载测试块），最后是一个**并排比较表**自动标记为哪个轴变化。参见 [`references/output-and-analysis.md`](references/output-and-analysis.md)。

5. **检查工件。** 布局取决于运行形状 — 对于单点 + `iterations=1` 是扁平的，否则嵌套在 `iter_<i>/<point>/...` 下。参见 [`references/output-and-analysis.md`](references/output-and-analysis.md) 了解完整的目录树、文件用途以及如何解析 `results.json` / `results.csv` / `report.md`。

6. **为用户总结。** 报告时，请遵循 [`references/output-and-analysis.md#summarising-results-to-the-user`](references/output-and-analysis.md#summarising-results-to-the-user) 中的剧本：为运行形状选择规范结果文件，构建标题表（并发 × top-k 轴 × TTFT × 吞吐量 × 瓶颈 × 引用质量），计算扫描的扩展效率，**始终标记**零引用 / 非零错误率 / 可疑 `llm_ttft_ms` / 小样本 p99，并提出一个具体的下次实验 YAML。

7. **调整。** 模式完全在 [`docs/performance-benchmarking.md`](../../docs/performance-benchmarking.md) 和以下深入参考中记录。常见旋钮：将 `aiperf.enabled: false` 用于仅分析模式，增加 `load.iterations` 用于方差估计，设置 `load.sleep_between_points_s: 60` 用于夜间笛卡尔扫描。

## 示例

**仅分析（检索 / reranker 调整的最快信号）：**

```bash
uv run --project scripts/rag-perf rag-perf -c scripts/rag-perf/configs/quick_profile.yaml
```

输出：`rag-perf-results/quick_profile/run_<ts>/{profile_report.md, profile_results.json, profiling/}`。省略了 `aiperf_rag_on/` 目录。由于 `aiperf.enabled: false`，文件名是 `profile_*`。

**单个基准点带完整报告：**

```bash
uv run --project scripts/rag-perf rag-perf -c scripts/rag-perf/configs/single_run.yaml
```

输出：扁平 `run_<ts>/{report.md, results.json, results.csv, profiling/, aiperf_rag_on/}`。

**并发扫描：**

```bash
uv run --project scripts/rag-perf rag-perf -c scripts/rag-perf/configs/sweep.yaml
```

输出：每个点 `run_<ts>/iter_1/<CR:_VDB-K:_RERANKER-K:_…>/{profiling,aiperf_rag_on}/`，加上运行根目录的汇总 `report.md` / `results.json` / `results.csv`。

**运行单元测试：**

```bash
uv sync --project scripts/rag-perf --extra dev   # 一次性，安装 pytest-asyncio
uv run --project scripts/rag-perf python -m pytest tests/unit/test_rag_perf/
```

## 限制

- CLI 是**配置驱动**：作者或复制 YAML 以改变参数。
- `load.concurrency` / `rag.vdb_top_k` / `rag.reranker_top_k` 接受 `int | list[int]`；验证器要求列表值唯一，因为每个值命名一个唯一的点目录。
- `input.file` 和 `input.synthetic` 遵循 XOR 规则 — 同时设置会导致验证失败。当两者都未设置时，`synthetic` 会用默认值自动填充，因此空配置仍然有效。
- 基于文件的输入格式**仅从扩展名推断**（`.jsonl` 或 `.csv`）；其他扩展名会被拒绝。
- 合成生成将每个查询在完成时流到磁盘（具有容错性），但在**第一个 LLM 错误时快速失败** — 部分JSONL 会被保留。修复端点后重新运行，可减少 `num_queries`，或将 `input.file` 指向部分文件。
- 推理模型（Nemotron Omni、Qwen-Reasoning）需要 `synthetic.disable_thinking: true`（默认值）。否则模型在思维链上耗尽 token 预算，`content` 返回空 — 现在生成器会抛出清晰的错误消息，而不是用 `reasoning_content` 替换答案。
- aiperf 特定旋钮（请求速率分布、GPU 遥测配置等）需要编辑 `AiperfRunner._base_aiperf_cmd` 在 `scripts/rag-perf/rag_perf/runner.py` 中。
- 过程细节位于 **`references/`** 下以保持此文件简洁。

## 故障排除

| 错误 / 信号 | 可能原因 | 应该怎么办 |
|---|---|---|
| `Configuration errors in <yaml>:  •  input  —  ... XOR rule` | 两者 `input.file` 和 `input.synthetic` 都设置 | 选择一个。XOR 验证器在 YAML 加载时运行。 |
| `input.file must end in .jsonl or .csv` | 扩展名不是 `.jsonl` / `.csv` | 重命名或转换。 |
| `load.concurrency has duplicate values` | 例如 `[2, 2, 4]` | 每个并发映射到一个唯一的点目录；去重。 |
| `warmup_requests must be >= 1` | YAML 有 `warmup_requests: 0` | aiperf 拒绝 warmup=0；最小值是 1。 |
| `LLM returned empty content (reasoning_content was populated — model exhausted its budget on chain-of-thought; raise min_query_tokens or set synthetic.disable_thinking=true).` | 使用推理模型 CoT 并耗尽 token | 设置 `synthetic.disable_thinking: true`（默认值）或提高 `min_query_tokens`。 |
| `✗ All N profiling requests failed across M point(s).` + exit 1 | 坏 URL、服务器宕机、错误集合 | 验证 `target.url`、`rag.collection_names`（`<collection_name>` 占位符会触发此问题）。 |
| Per-iteration `⚠ N profiling requests failed` 警告，运行继续 | 一些请求在运行中途超时 / 出错 | 检查 rag-server 日志，提高 `target.timeout_s`，降低并发。 |
| `RuntimeError: Random synthetic query generation failed at query N: ...` | LLM 端点在生成中途拒绝了请求 | 部分JSONL 位于 `synthetic.jsonl_output_path`；修复端点，用减少的 `num_queries` 重新运行，或将 `input.file` 指向部分文件。 |
| `Citation count (mean): 0` and `Citation relevance score: N/A` for a non-empty deployment | `rag.collection_names` 与实际摄入的集合不匹配 | 运行 `curl -s http://<ingestor>:8082/v1/collections` 列出真实集合。 |
| 测试错误 `ModuleNotFoundError: No module named 'pytest_asyncio'` | 缺少开发附加项 | `uv sync --project scripts/rag-perf --extra dev`。 |
| CI: `ModuleNotFoundError: No module named 'ruamel'` from `tests/unit/test_rag_perf/` | rag-perf 包缺失于 CI venv | 在单元测试作业中顶级安装后添加 `uv pip install -e ./scripts/rag-perf`。 |

## 注意事项

- **从仓库根目录运行。** 预设配置参考 `scripts/rag-perf/examples/queries.jsonl` 和 `scripts/rag-perf/prompts/default_prompts.yaml` 使用仓库根目录相对路径。在 `scripts/rag-perf/` 内运行将失败这些文件查找。
- **CLI 仅配置驱动。** 编辑 YAML 或复制预设以设置 URL、并发、集合等字段。
- **在第一次运行前始终编辑 `rag.collection_names`。** 预设使用 `["<collection_name>"]` 作为故意占位符。验证通过，检索将沉默失败 — 表现为 `Citation count (mean): 0` 处处。
- **`load.concurrency_list`, `rag.vdb_top_k_list`, `rag.reranker_top_k_list`** 是只读属性，将标量或列表标准化为列表。用于思考网格；底层 YAML 字段是用户写入的。
- **`aiperf.enabled: false` 改变文件名。** 顶级输出变为 `profile_report.md` / `profile_results.json` / `profile_results.csv`。汇总扫描表也抑制负载测试行和“最佳吞吐量”页脚。
- **解析配置转储** 很长（50+ 行） — 预期。它是终端输出作为自包含重现器的基础；不要在脚本中过滤它。
- **aiperf shell 命令** 在每个子进程之前记录。在标准输出中查找 `\n  $ python -m aiperf profile -m ... --endpoint-type nvidia_rag ...` — 复制粘贴可运行形式以在 rag-perf 外重现单个点。
- **`--endpoint-type nvidia_rag`** 来自捆绑的插件 `scripts/rag-perf/rag_perf/plugin/nvidia_rag.py`。它教 aiperf 关于 RAG `/v1/generate` 请求形状，并从 SSE 流中解析引用 + 每个阶段的 `metrics`。如果 aiperf 无法解析 `nvidia_rag`，rag-perf 需要在 venv 中可编辑安装 — 重新运行 `uv sync --project scripts/rag-perf`（或 `uv pip install -e ./scripts/rag-perf`）。
- **扫描模式点名冲突。** 当两个点仅在并发上不同（例如 `[1, 4]` × 单个 `vdb_top_k`）时，目录名编码所有内容：`CR:1_ISL:50_OSL:512_VDB-K:20_RERANKER-K:4_Model:...`。追加集群 / GPU / 实验名 (`output.cluster`、`output.gpu`、`output.experiment_name`) — 对跨机器的差分友好工件路径有用。
- **`load.iterations > 1` 重复整个网格**。每个重复写入其自己的 `iter_<i>/`。汇总 CSV 行数 = `n_points × iterations`。

## 真实来源

| 片段 | 位置 |
|---|---|
| 驱动 | [`scripts/rag-perf/rag_perf/cli.py`](../../scripts/rag-perf/rag_perf/cli.py) (`main` 是单个 Click 命令) |
| 模式 | [`scripts/rag-perf/rag_perf/config.py`](../../scripts/rag-perf/rag_perf/config.py) (`RunConfig` 和子模型) |
| 协调器 | [`scripts/rag-perf/rag_perf/runner.py`](../../scripts/rag-perf/rag_perf/runner.py) (`BenchmarkRunner.run`, `RagProfiler`, `AiperfRunner`) |
| aiperf 插件 | [`scripts/rag-perf/rag_perf/plugin/nvidia_rag.py`](../../scripts/rag-perf/rag_perf/plugin/nvidia_rag.py) |
| 用户文档 | [`docs/performance-benchmarking.md`](../../docs/performance-benchmarking.md) |
| 预设 | [`scripts/rag-perf/configs/{quick_profile,single_run,sweep}.yaml`](../../scripts/rag-perf/configs/) |
| 示例查询 | [`scripts/rag-perf/examples/queries.jsonl`](../../scripts/rag-perf/examples/queries.jsonl) |
| 合成提示 | [`scripts/rag-perf/prompts/default_prompts.yaml`](../../scripts/rag-perf/prompts/default_prompts.yaml) |
| 配置模式细节 | [`references/config-schema.md`](references/config-schema.md) |
| 合成查询生成 | [`references/synthetic-generation.md`](references/synthetic-generation.md) |
| 输出布局 & 指标语义 | [`references/output-and-analysis.md`](references/output-and-analysis.md) |

## 代理剧本

1. **同步依赖项：** `uv sync --project scripts/rag-perf`（每次检出一次性）。
2. **选择并自定义预设：** 如果需要变体，复制 `scripts/rag-perf/configs/<preset>.yaml`；始终将 `rag.collection_names` 设置为实际集合。
3. **运行：** 从仓库根目录 `uv run --project scripts/rag-perf rag-perf -c <config>`。
4. **查看标准输出上的每个点和汇总表。** 瓶颈推理在每点分析部分；跨点的比较是最后的汇总表。
5. **解析工件** 在 `output.dir/run_<ts>/` 下 — 参见 [`references/output-and-analysis.md`](references/output-and-analysis.md)。对于多点运行，`results.csv` 有一行对应于（点 × 迭代）。
6. **为用户总结** 使用 [`references/output-and-analysis.md#summarising-results-to-the-user`](references/output-and-analysis.md#summarising-results-to-the-user) 中的剧本 — 标题表，扫描的扩展效率计算，必须标记零引用 / 非零错误率 / 可疑 `llm_ttft_ms` / 低样本量，以及一个具体的下次实验 YAML。
7. **调整检索 / reranker：** 切换到 `quick_profile.yaml` 或 `aiperf.enabled: false` 进行快速迭代，然后在负载下返回 `single_run.yaml` / `sweep.yaml` 进行特征分析。
8. **筛选失败：** 参见上述故障排除和 [`references/output-and-analysis.md`](references/output-and-analysis.md) 中的空引用 / 瓶颈=N/A 模式。
