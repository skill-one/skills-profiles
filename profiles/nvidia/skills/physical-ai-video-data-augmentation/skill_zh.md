# 物理AI视频数据增强工作流编排器

OSMO上VDA执行的默认工作流技能。它拥有流程选择、预提交检查、缓存就绪、推理路径决策、提交时间插值、监控和输出检索。组件技能仅用于咨询。

## 目的

从预提交检查到输出下载，安全且可重复地运行端到端VDA工作流。

**不要**使用此技能来回答仅限于容器内部调优的问题。

## 前置条件

在运行预提交检查或任何提交之前，请确认这些内容。缺少必需的秘密会以`USER_INPUT_REQUIRED:`的形式从`scripts/preflight_credentials.sh`中显示。

| 需求 | 如何满足 | 用途 |
|---|---|---|
| NGC API密钥（可选） | `NGC_API_KEY`、`NGC_CLI_API_KEY`或兼容的`nvapi-*`令牌在`NVIDIA_API_KEY`/`OPENAI_API_KEY`/`VLM_API_KEY`/`LLM_API_KEY`中 | 可选的`nvcr_io`凭证刷新和NGC REST作用域探测；默认VDA镜像引用通过工作流注册表探测进行验证 |
| Hugging Face令牌 | `HF_TOKEN`（或`HUGGING_FACE_HUB_TOKEN`），或缓存在`~/.cache/huggingface/token`的令牌 | 创建OSMO的`hf_token`凭证；拉取受保护的Cosmos/SeedVR权重 |
| OSMO CLI访问 | `osmo`在`PATH`上，已登录，具有默认配置文件，并有一个与`storage_url`匹配的已注册DATA凭证配置文件 | 提交/监控工作流和列出/下载对象 |
| GPU池 | 至少有一个`ONLINE`池在`osmo pool list --mode free`中；`POD_TEMPLATE`包含GPU容忍/选择器 | 调度设置+工作器任务 |

可选（仅用于严格的NGC组织/团队探测）：`NGC_ORG` + `NGC_TEAM`（或`NGC_CLI_ORG` / `NGC_CLI_TEAM`）。外部VLM/LLM端点密钥将分别进行验证，而不是通过预提交检查。

密钥处理规则：`nvapi-*`令牌是`nvcr_io`的一流输入。仅凭令牌前缀拒绝；使用工作流注册表探测结果作为真实来源。

## 说明

1. 从用户意图中选择工作流（`auto_labeling`、`augmentation_and_al`、`e2e`、`e2e_super_resolution`）。
2. 在开始运行操作之前，提供一次性的执行时间概述。
3. 在提交之前运行预提交检查和就绪检查。
4. 从活动数据集后端派生出提交时间值（永远不要猜测`storage_url`）。
5. 使用显式插值值提交工作流并监控到完成。
6. 检索输出，为增强流提供并排比较证据，并总结任务结果。

使用`run_script(...)`执行脚本。规范示例：

```python
run_script("bash scripts/preflight_credentials.sh --workflow assets/configs/osmo/augmentation_and_al.yaml")
run_script("python3 scripts/pre_submit_guard.py --workflow assets/configs/osmo/auto_labeling.yaml")
run_script("bash scripts/prepare_demo_assets.sh /srv/sdg/data/vda_inputs")
```

## 可用脚本

使用脚本级别的`--help`获取确切参数。

| 脚本 | 角色 |
|---|---|
| `scripts/preflight_credentials.sh` | 秘密/控制平面预提交检查和工作流镜像访问检查 |
| `scripts/pre_submit_guard.py` | 提交时间插值、缓存和数据集安全检查 |
| `scripts/prepare_demo_assets.sh` | 演示视频拉取+扁平化到默认演示路径 |
| `scripts/generate_configs.py` | 设置时配置和食谱投影生成 |
| `scripts/cosmos_worker.sh` | 增强工作者执行 |
| `scripts/pl_original_worker.sh` | 原始视频自动标记工作者执行 |
| `scripts/pl_augmented_worker.sh` | 增强视频自动标记工作者执行 |
| `scripts/osmo_barrier.py` | 多节点屏障同步 |
| `scripts/stage_run_artifacts.sh` | 完整运行输出+输入视频的本地镜像 |
| `scripts/render_side_by_side.sh` | 从本地工件进行并排比较渲染 |

## 支持的工作流

| 工作流 | OSMO YAML | 组序列 | 典型用途 |
|---|---|---|---|
| `augmentation_and_al` | `assets/configs/osmo/augmentation_and_al.yaml` | 设置 -> 增强 -> 自动标记增强 | 增强一个或多个视频，然后自动标记增强输出 |
| `auto_labeling` | `assets/configs/osmo/auto_labeling.yaml` | 设置 -> 自动标记 | 仅标记原始视频 |
| `e2e` | `assets/configs/osmo/e2e.yaml` | 设置 -> (原始视频自动标记 + 增强) -> 自动标记增强 | 吞吐量优先路径 |
| `e2e_super_resolution` | `assets/configs/osmo/e2e_super_resolution.yaml` | 设置 -> 原始视频自动标记 -> 增强 -> 自动标记增强 | 在增强之前具有SR门控的顺序路径 |

遗留别名`assets/configs/osmo/augmentation_and_pl.yaml`保留以向后兼容。

### 为用户的请求选择正确的工作流

| 用户意图 | 工作流 |
|---|---|
| "标记我的源视频" / "仅PL" / "无增强" | `auto_labeling` |
| "创建增强视频并标记它们" | `augmentation_and_al` |
| "快速运行完整管道" | `e2e` |
| "运行完整管道，但首先在SR增强的原始视频上设置门控" | `e2e_super_resolution` |

## 消歧义：在提交之前处理模糊请求

默认为自主性：仅当缺少信息阻止执行时才询问。

### 自主默认值（不要询问）

- 如果数据集源缺失，运行VDA演示路径（`scripts/prepare_demo_assets.sh`）并继续使用`dataset=vda-demo`。
- 如果未明确请求流程，默认为`augmentation_and_al`。
- 如果端点模式未指定，默认为集群内持久NIM重用和当不健康时自动NIM部署/修复。
- 如果缓存缺失，运行`setup_model_cache.yaml`，重新运行预提交保护，并在成功后自动继续。
- 在任何阶段成功完成后，立即继续到下一阶段。不要暂停等待“准备好”或等效的批准提示。

### 应该暂停以进行消歧义的触发器

| 缺少输入 | 为什么重要 | 询问 |
|---|---|---|
| 来自预提交的`USER_INPUT_REQUIRED` | 缺少必需的秘密 | 询问一个简洁的解锁问题，以获取确切缺失的值 |
| 存储后端前缀无法从活动数据集/上传根派生 | 错误的方案会导致运行时存储身份验证不匹配 | "这个运行的本地后端根前缀是什么？" |
| 无法选择任何ONLINE GPU池/平台 | 工作流无法调度设置/工作者 | "这个运行应该针对哪个GPU池/平台？" |

### 不应进行消歧义的情况

- 除非用户明确要求更改场景配置文件，否则不要询问食谱。
- 默认情况下不要提供外部端点。
- 不要询问A/B缓存策略问题；默认是自动缓存设置。
- 不要询问缩小现有NIM；这是禁止的。
- 当输入缺失时，不要编造、刮擦或生成随机视频。
- 不要使用非VDA演示源（例如Carline适应资产），除非用户明确请求不同的数据集。

## 步骤0：选择流程并收集输入

### 输入视频策略（不可协商）

- 始终将用户提供的视频输入（数据集URL、本地路径或上传文件夹）作为首选和优先的第一类。
- 永远不要用演示资产或其他来源替换明确的用户视频。
- 如果未提供视频输入，默认通过`scripts/prepare_demo_assets.sh`（HF数据集流）使用VDA演示资产，而无需询问额外的源选择问题。
- 如果用户明确提到输入视频或数据集，请优先使用该输入而不是演示资产。
- 仅使用VDA演示资产（`nvidia/video-data-augmentation-demo`）作为默认演示路径。
- 永远不要提议任意的网络片段下载或占位符视频，除非用户明确要求这种行为。

仅收集缺失的值：

1. 数据集源（优先使用明确的用户提供的`dataset_url`或本地上传文件夹；否则默认为VDA演示资产并继续）。
2. 流（`auto_labeling`、`augmentation_and_al`、`e2e`、`e2e_super_resolution`）；当未指定时，默认为`augmentation_and_al`。
3. OSMO `gpu_platform`用于所有VDA资源（当不明确时自动选择ONLINE平台；仅当不存在有效选项时才询问）。
4. 端点模式（除非明确覆盖，否则默认为集群内NIM重用/部署）。

不要猜测`gpu_platform`（例如`microk8s`）。使用`osmo pool list --mode free`显示的确切当前平台标签（例如`gpu`）。

在每次提交之前生成运行戳：

```bash
STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)
RUN_ID="run-$STAMP"
```

## 执行时间概述（运行之前必需）

在运行任何可变命令（`osmo credential set`、NIM安装/修复、缓存工作流提交或目标VDA工作流提交）之前，向用户提供一个简短的ETA概述。

保持简洁（一个简短段落或4-6个要点），并包括：

- 这看起来像是一个**冷启动**（NIM/缓存缺失）还是**热启动**（NIM/缓存已健康），
- 主要阶段及其近似持续时间，
- 选中工作流的预期总范围。

基准范围（从观察到的MicroK8s + OSMO运行中）：

| 阶段 | 典型持续时间 |
|---|---|
| 凭证+预提交检查 | ~1-2分钟 |
| NIM部署/下载/预热（如果需要） | ~10-15分钟 |
| 演示资产下载/上传（如果使用演示路径） | ~1-3分钟 |
| 模型缓存填充（如果需要） | ~15-25分钟 |
| 工作流提交+排队/启动 | ~1-3分钟 |

提交后工作流运行范围：

| 流程 | 典型运行时间 |
|---|---|
| `auto_labeling` | ~6-15分钟 |
| `augmentation_and_al` | ~20-35分钟 |
| `e2e` | ~22-40分钟 |
| `e2e_super_resolution` | ~25-45分钟 |

冷启动端到端运行通常为~45-80分钟；热启动运行通常为~20-45分钟，具体取决于流程和视频长度。

## 常见前置条件（所有流程）

1. **凭证和控制平面预提交检查**

   ```bash
   bash scripts/preflight_credentials.sh --workflow assets/configs/osmo/<mode>.yaml
   ```

   限制出站：

   ```bash
   bash scripts/preflight_credentials.sh --no-probe --workflow assets/configs/osmo/<mode>.yaml
   ```

   预提交检查不需要工作负载本地`.env`。运行时插值由提交时间值（`dataset`、`run_id`、`gpu_platform`、`video`、`storage_url`、`skills_dir`）在单个`--set-string`列表中提供驱动。

   传递`--workflow`会使用匿名持票人访问验证活动工作流镜像引用（`workflow.groups[].tasks[].image`），使用凭证回退。如果提供了替换的NGC/HF秘密，当存在时，预提交会自动刷新现有的`nvcr_io` / `hf_token`。使用`--refresh`强制覆盖，即使没有提供新的环境秘密：

   ```bash
   bash scripts/preflight_credentials.sh --workflow assets/configs/osmo/<mode>.yaml --refresh
   ```

   如果输出包含`USER_INPUT_REQUIRED:`，请询问一个简洁的解锁问题并停止。

   在工作流镜像`401/403`时，在列出的镜像引用上完成探测检查后，报告注册表访问失败；不要声称密钥家族（例如`nvapi-*`）明确不受支持。

2. **存储插值策略**

   `storage_url`必须从当前运行的实际数据集/上传后端派生。

   ```text
   dataset_url=azure://storiondevxah69/osmo-workflows/datasets/vda-demo
   storage_url=azure://storiondevxah69/osmo-workflows
   dataset=vda-demo
   ```

   在非S3后端上永远不要无声地默认为陈旧的`s3://`值。

3. **推理策略（不可协商）**

   - 默认情况下重用健康的集群内持久NIM端点。
   - 如果缺失/不健康，自动部署——这是前提条件，不是用户决策。不要暂停以询问；使用VDA允许列表运行安装：

   ```bash
   export NIM_SERVICES="qwen3-vl qwen25-14b"
   skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-nim-operator/scripts/install.sh
   ```

   - 请参阅`references/nim/README.md`以获取完整的端点文档和健康检查。
   - 外部端点是仅选择性的（明确请求或明确URL）；然后才跳过集群内部署。
   - 永远不要从凭证存在中推断外部模式。
   - 永远不要缩小/删除现有的NIM以释放GPU。

4. **就绪保护**

   ```bash
   osmo pool list --mode free
   osmo config show POD_TEMPLATE
   python3 scripts/pre_submit_guard.py --workflow assets/configs/osmo/<mode>.yaml
   ```

5. **缓存自动修复**

   如果`pre_submit_guard.py`报告缓存失败，默认操作是运行：

   ```bash
   osmo workflow submit assets/configs/osmo/setup_model_cache.yaml \
     --set-string storage_url=<backend-prefix> path=data
   ```

   然后重新运行`pre_submit_guard.py`，只有在它通过后才提交目标VDA流。仅在后备/前缀不明确或缓存设置失败时才询问用户。

6. **调度策略**

   VDA模板在`gpu_platform`上调度设置和工作者（用户工作负载没有`system`池依赖）。

## 提交（所有流程）

每个流程都使用相同的提交形状；只有工作流YAML会更改。选择请求的YAML，然后运行下面的命令。每个流程的完整逐步说明（阶段矩阵和工作流详细信息）位于链接的参考中。

| 流程 | 工作流YAML | 步骤说明 |
|---|---|---|
| 增强+自动标记 | `assets/configs/osmo/augmentation_and_al.yaml` | `references/flows/augmentation_and_al.md` |
| 仅自动标记 | `assets/configs/osmo/auto_labeling.yaml` | `references/flows/auto_labeling.md` |
| E2E（并行） | `assets/configs/osmo/e2e.yaml` | `references/flows/e2e.md` |
| E2E（超分辨率门控） | `assets/configs/osmo/e2e_super_resolution.yaml` | `references/flows/e2e_super_resolution.md` |

```bash
SKILLS_DIR="$(cd "$(git rev-parse --show-toplevel)/skills/physical-ai-video-data-augmentation" && pwd)"
STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)
osmo workflow submit assets/configs/osmo/<flow>.yaml \
  --pool <pool> \
  --set-string \
    dataset=<dataset> \
    run_id=run-$STAMP \
    storage_url=<backend-prefix> \
    gpu_platform=<gpu-platform> \
    video=<video-stem> \
    cosmos_model_cache_url=<backend-prefix>/data/models/cosmos_transfer \
    auto_labeling_model_cache_url=<backend-prefix>/data/models/auto_labeling \
    skills_dir="$SKILLS_DIR"
```

兼容性说明：
- 使用恰好一个`--set-string`标志，并在它之后传递所有键/值对。
- 不要在同一命令中重复`--set`/`--set-string`标志；某些OSMO构建仅认可最后一次出现的标志。
- 不要在一条提交命令中混合`--set`和`--set-string`。
- 传递显式的`*_model_cache_url`值以避免跨OSMO环境的嵌套模板插值差异。
- 不要蛮力排列标志。直接使用此形状。

常见的可选覆盖（将键/值对附加到相同的`--set-string`列表）：

```bash
cookbook=<scene_profile> \
vlm_url=<openai_base_url> \
llm_url=<openai_base_url> \
cosmos_model_cache_url=<url> \
auto_labeling_model_cache_url=<url>
```

自动标记仅流没有增强阶段，因此它在运行时省略`cosmos_model_cache_url`；传递它是无害的，并保持跨流程的提交形状。

## OSMO监控

```bash
# 工作流状态+任务状态
osmo workflow query <workflow_id> --format-type json \
  | jq '{status, tasks: [.groups[].tasks[] | {name, status, exit_code}]}'

# 特定任务的日志
osmo workflow logs <workflow_id> --task <task_name> -n 200

# 输出检索
osmo data list --no-pager <output_url>
osmo data download <output_url> <local_dir>/
```

对于完成工件，始终将完整运行输出镜像到工作区：

```bash
ROOT="$(git rev-parse --show-toplevel)"
RUN_LOCAL_DIR="$ROOT/media/vda/runs/<run_id>"
mkdir -p "$RUN_LOCAL_DIR"
osmo data download "<storage_url>/datasets/<dataset>-outputs/<run_id>/" "$RUN_LOCAL_DIR/"
```

对于预期超过两分钟的运行，至少每两分钟发送一次心跳更新。对于媒体证据，为每个消息气泡发出一条独立的`MEDIA:<绝对路径>`行。

执行连续性要求：

- 心跳必须在继续工作时报告进度；它们是状态更新，不是权限提示。
- 不要在绿色阶段之间停止等待批准。
- 仅在阻塞失败或明确用户停止/重定向时暂停。
- 如果提交因插值失败，使用相同的规范单标志形状和修正值重新运行一次；不要循环通过临时的标志实验。

MEDIA格式严格：

- 发出恰好一行：`MEDIA:/absolute/path/to/file.mp4`
- 保持`MEDIA:`在同一行上连续（永远不会跨行分割）。
- 同一气泡中不要有额外文本。
- 不要在指令周围使用代码围栏、项目符号或引号。
- 如果渲染失败：从稳定的工作区路径重试一次，然后发出PNG回退。

## 运行后比较证据（增强流必需）

适用于`augmentation_and_al`、`e2e`和`e2e_super_resolution`在成功运行后。

必需的完成输出（不要在原始输出URL处停止）：

1. 将阶段完整输出+输入视频到工作区本地路径：

   ```bash
   bash scripts/stage_run_artifacts.sh \
     --storage-url <storage_url> --dataset <dataset> --run-id <run_id> --video <video>
   ```

2. 从该本地运行副本进行并排渲染：

   ```bash
   bash scripts/render_side_by_side.sh \
     --run-local-dir "<repo>/media/vda/runs/<run_id>" --dataset <dataset> --video <video>
   ```

3. 从本地运行副本发出MEDIA并包括：
   - 增强摘要来自`<run_local_dir>/setup_b0/configs/manifest.yaml`（`sampled_vars` for `<video>_aug0`）
   - 自动标记摘要来自`<run_local_dir>/outputs/pseudo_labeled_augmented/<video>_aug0`
   - 对于`e2e` / `e2e_super_resolution`，原始标签摘要来自`<run_local_dir>/outputs/pseudo_labeled/<video>`

如果`ffmpeg`不可用，从相同的本地运行副本发出输入和增强MEDIA，并提供增强+自动标记摘要。

对于演示运行（未提供用户视频），明确说明输入来自`nvidia/video-data-augmentation-demo`。

## 支持文件

使用这些规范位置：

- 工作流：`assets/configs/osmo/*.yaml`
- 运行时脚本：`scripts/*.sh`，`scripts/*.py`
- 流程逐步说明：`references/flows/*.md`
- 设置和分诊：`references/setup.md`，`references/troubleshooting.md`
- 图像和端点策略：`references/container-images.md`，`references/nim/README.md`
- 食谱调整：`assets/cookbooks/TUNING_GUIDE.md`
