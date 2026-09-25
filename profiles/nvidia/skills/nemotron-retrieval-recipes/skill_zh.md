# Nemotron 检索配方

调用：`$nemotron-retrieval-recipes`。

## 目的

使用此技能来处理源代码库或已安装包中的公共 Nemotron 嵌入和重新排序检索配方。优先选择当前代码库，因为配方 CLI、配置文件、容器和输出路径都在积极变化中。将每个配方系列视为只有在其配方目录和匹配的 CLI 文件存在后才可用。

这是一个公共产品技能，而非仅限贡献者的指导。其相对于静态文档的价值在于让代理将用户的检索失败引导至正确的配方系列，协调文档与当前代码库，避免意外长时间运行，保护密钥，并返回具体的预览/执行/运行报告命令。

仅用于与公共 Nemotron `embed` 或 `rerank` 配方流程相关的任务。如果请求与检索理论无关、通用向量数据库选择、通用基准建议或非配方 Docker/Slurm/NIM 故障排除无关，请附带简短的范围说明并停止，并在该回合中不要检查配方文件。

## 安全注意事项

使用 `Bash` 进行代码库范围检查、帮助、干运行和用户批准的执行命令。除非用户明确要求，否则不要运行 API、GPU、Docker、Slurm、NIM 或其他长时间运行的工作。在两个系列的 Stage 0 SDG 之前，确认用户的数据治理策略允许将语料库内容发送到配置的推理端点；否则使用批准的私有或隔离路径。永远不要运行广泛的環境转储或暴露密钥值的命令。优先使用点列表覆盖和配置审查，而不是编辑配方默认值。

## 源代码优先级

按以下顺序解决冲突：

1. 当前代码库的配方、CLI、配置和源文件。
2. 本技能中的捆绑引用。
3. 用户提供的文档或保存的片段。
4. 内存。

对于可运行命令，将当前代码库视为权威。如果缺少必要的配方目录、CLI 命令、配置或环境配置文件，请报告障碍，而不是猜测。

## 前置条件

- 代码库环境：`uv sync --all-extras` 或代码库中记录的最小相关额外内容。
- Stage 0 SDG：`NVIDIA_API_KEY`；永远不要要求用户粘贴密钥值。
- Stages 1–3 GPU 工作：CUDA/NVIDIA 驱动程序可用性和足够的 VRAM。
- Stage 4 导出：使用 TensorRT 时 NeMo Export-Deploy 容器。默认 Nemotron 3 Embed 配置有意跳过导出。
- Stage 5 部署：Docker。默认 Nemotron 3 Embed 可以使用检查入的 vLLM 路径，使用 `backend=vllm`，或使用兼容的 `NEMOTRON3_EMBED_NIM_IMAGE`，使用 `backend=nim`；Llama Embed 和 rerank 部署可能需要 NGC 访问和 `NGC_API_KEY`。
- 远程执行：root `env.toml` 配置文件用于 `--run` 或 `--batch`；在远程调度、日志记录或 GPU 位置相关时加载 `references/remote.md`。

## 说明

1. 确定配方系列。
   - 使用 `references/embed.md` 进行嵌入、嵌入、双编码器、向量搜索、第一阶段检索、低 Recall@k、缺少相关文档、NIM 嵌入或 `nemotron embed`。
   - 使用 `references/rerank.md` 进行 rerank、reranker、交叉编码器、第二阶段检索、可接受的召回率但排名顺序差、低 nDCG 但召回率高，或 `nemotron rerank`。
   - 仅在用户询问两个系列或询问选择哪个系列时使用两个参考。
2. 对于 `embed`，在组合阶段命令之前选择一个模型配置文件。
   - 当请求的模型不明确时，运行 `uv run nemotron embed info`。
   - 使用 `-c default` 进行 `nvidia/Nemotron-3-Embed-1B-BF16`。
   - 使用 `-c llama` 进行 `nvidia/llama-nemotron-embed-1b-v2` 及其导出路径。
   - 将选定的配置文件和 `artifact_root` 传递到每个阶段；永远不要将两个配置文件的工件组合在一起。
3. 根据检索失败模式选择要微调的模型系列。
   - 当候选集中缺少相关文档时，优先进行嵌入微调。
   - 当相关文档检索到但顶部排序差时，优先进行 reranker 微调。
   - 对于生产检索堆栈，记住这些是互补的：先嵌入，再对候选集进行 rerank。
4. 确定意图：计划运行、执行阶段、调试失败、调整超参数、解释指标、导出/部署模型、检查配置，或提出点列表覆盖。
5. 在采取行动之前检查当前公共界面：
   - 配方文件：`src/nemotron/recipes/<embed|rerank>/`
   - CLI 文件：`src/nemotron/cli/commands/<embed|rerank>/`
   - 配置：`src/nemotron/recipes/<family>/stage*/config/<profile>.yaml`
   - 帮助和干运行：`uv run nemotron <family> --help`，`uv run nemotron <family> <stage> -c <profile> -d`

## 安全工作流程

1. 仅收集与任务相关的上下文：配方系列、选定的配置文件、语料库路径、现有的 SDG/训练/评估数据、目标阶段范围、工件根、检查点路径、执行模式、GPU ID，以及是否配置了所需密钥。永远不要要求用户粘贴密钥值。
2. 在进行昂贵工作之前，从廉价的检查开始：
   - `uv run nemotron <family> --help`
   - `uv run nemotron <family> <stage> --help`
   - `uv run nemotron <family> <stage> -c <profile> -d`
   - `uv run nemotron <family> run -c <profile> -d --from <stage> --to <stage>`
   - `run --help` 可能省略继承的 `-c` 和 `-d` 选项，即使 `run -c default -d ...` 也有效；不确定时通过运行干运行进行验证。
   - 在已准备好的代码库中，`uv run --no-sync ... --help` 或 `uv run --no-sync ... -d` 可以避免在只读检查期间出现意外的依赖同步。
3. 检查请求阶段的先决条件：
   - 代码库环境：`uv sync --all-extras` 或代码库记录的最小相关额外内容。
   - Stage 0 SDG：`NVIDIA_API_KEY`。
   - Stages 1–3 GPU 工作：CUDA/NVIDIA 驱动程序可用性和足够的 VRAM。
   - Stage 4 导出：使用 TensorRT 时 NeMo Export-Deploy 容器。默认 Nemotron 3 Embed 跳过此阶段。
   - Stage 5 部署：Docker 加上选定的后端镜像和工件合同；默认 Nemotron 3 可能使用检查入的 vLLM 镜像而无需 NIM 凭证。在要求 NGC 凭证之前加载系列参考。
   - 远程执行：root `env.toml` 配置文件用于 `--run` 或 `--batch`；在远程调度、日志记录或 GPU 位置相关时加载 `references/remote.md`。
4. 除非用户要求可重用的配置更改，否则使用点列表覆盖而不是编辑默认值。保持选定的配置文件、工件根、序列长度、前缀、池化/归一化、提示模板和硬负样本计数在各个阶段保持一致。
5. 除非用户明确要求运行，否则避免启动 API、GPU、Docker、Slurm、NIM 或长时间运行的工作。首先提供或运行干运行、配置审查和小型试点。
6. 对于本地执行，使用 `CUDA_VISIBLE_DEVICES=<ids>` 限制请求的 GPU ID。对于 `--run` 或 `--batch`，在选定的 `env.toml` 配置文件中配置调度器资源，如 `gpus_per_node`，并让调度器分配设备；不要假设提交 shell 的 `CUDA_VISIBLE_DEVICES` 会远程传播。
7. 对于多阶段本地运行，优先使用 `uv run nemotron <family> run -c <profile> --from <stage> --to <stage>`。使用 `default` 进行 rerank。默认的 `run` 目标在 `eval` 停止；`export` 和 `deploy` 是可选的。
8. 在评估质量时，在推荐部署之前，在固定的保留评估集上与基础模型进行比较。不要用独立的公共基准评估代替配方的 Stage 3 评估。
9. 对于长时间运行的 SDG、准备、微调或评估工作，以安全会话的方式启动进程，并以人类时间尺度间隔轮询：小试点约为 60 秒，较大运行约为 120-300 秒。
10. 对于失败，定位失败的阶段，然后检查阶段配置、预期输入、输出目录和相应的 CLI 包装器或 `run_uv.py`。

## 参考

- `references/embed.md`：嵌入配方阶段、命令、默认值、输出路径和操作模式。
- `references/rerank.md`：rerank 配方阶段、命令、默认值、输出路径和操作模式。
- `references/evaluation.md`：指标解释、比较卫生和部署就绪检查。
- `references/remote.md`：远程执行配置文件、批处理/运行模式、GPU 限制、日志记录和轮询。

## 示例

用户询问："召回率尚可，但 nDCG 较差，正确段落在排名 40 附近。我应该微调嵌入还是 rerank？"

加载 `references/rerank.md` 和 `references/evaluation.md`，解释可接受的召回率但顶部排名顺序差指向 reranker 微调，然后提供廉价的预览后再进行训练。

```bash
uv run nemotron rerank run -c default -d --from prep --to eval
```

## 故障排除

定位失败阶段，然后检查阶段配置、预期输入、输出目录和相应的 CLI 包装器或 `run_uv.py`。

## 限制

- 捆绑引用是简化的快照；在执行之前，验证命令、标志、默认值和输出路径与活动代码库。
- 此技能不提供数据集、检查点、凭证、GPU 容量、Docker 镜像或 NIM 服务。

## 输出样式

对于计划或调试建议，当它有助于时使用以下形状：`Decision`，`Why`，`Required inputs`，`Preview command`，`Execution command`，`Avoid`，和 `Next step`。省略与简短答案无关的字段。

给出具体的命令和文件路径。说明假设、预期输入、预期输出，以及证明下一步行动已就绪的最廉价验证步骤。对于长时间运行的阶段，将预览命令与执行命令分开，以便用户可以有意选择。

当报告干运行或实际运行时，包括紧凑的运行报告：命令、模式、配置、点列表覆盖、输入路径、输出路径、验证信号或指标文件，以及下一个最廉价的检查。当可用时，包括代码库提交。
