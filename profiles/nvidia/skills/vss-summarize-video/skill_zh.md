## 说明

请遵循下方的路由表和分步工作流。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都旨在自上而下执行。详细的参考材料位于 `references/` 中。

## 示例

完整的端到端示例保存在 `evals/` 下（每个 `*.json` 清单包含一个可运行的场景），并在下方每个工作流的 `curl` 块中内联提供。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

直接调用 VLM NIM 或视频摘要微服务 **直接**。
始终自行运行 `curl` 命令；切勿指示用户运行它们。

主要视频工作流查询类型：**“总结此视频。”** 直接视频摘要 API 和服务-ops 请求由下方的参考路由部分处理。

## 目的

生成一个经过润色的单一叙事性摘要，总结一个录制的视频片段，并在 LVS 微服务路径可达时附带时间戳事件。

**不要使用此技能：**
- 实时 RTSP 字幕——使用 `vss-deploy-dense-captioning`。
- 报告生成，包括事件或警报窗口报告——使用 `vss-generate-video-report` 模式 B。
- 跨存档进行语义搜索——使用 `vss-search-archive`。

## 前提条件

- VSS `lvs` 配置在 `$HOST_IP` 上运行（端口 38111）或一个可到达的 VLM/RT-VLM 端点作为后备。`vss-deploy-profile` 技能会启动这些配置。
- 代理主机到两个端点的网络可达性；来自 VIOS 的片段 URL 必须可被选定的后端获取。
- 代理主机上可用 `jq` 和 `curl`。

## 限制

- 直接 VLM 后备使用单个固定提示，无法针对场景/事件——输出质量低于 LVS 路径。
- 远程 VLM 端点通常无法到达 `localhost`/私有片段 URL。
- 每个请求一个后端调用；不支持并行 hedging 或多遍摘要。

## 故障排除

| 症状 | 原因 | 解决方法 |
|---|---|---|
| `/v1/ready` 反复返回 503 | LVS 服务仍在预热 | 按照说明中的 *Setup* 重试最多 ~30 秒；如果它从未返回 200，则服务可能未部署 |
| `video_summary` 和 `events` 为空 | 片段不包含请求的事件 | 使用更广泛的 `scenario` 或不同的 `events` 重新运行 |
| VLM 返回 `<think>` 块 | Cosmos 推理模式 | 在渲染之前删除 `</think>` 之前的一切 |
| `curl /v1/ready` 的空 stdout | 服务确实返回 200 且正文为空 | 始终使用 `-o /dev/null -w '%{http_code}'` 检查 HTTP 状态码，切勿检查正文 |

有关更深入的诊断，请参阅 [`references/video-summarization-debugging.md`](references/video-summarization-debugging.md)。

## 参考地图

仅在用户要求相关细节时，或核心工作流下方需要更深入的视频摘要信息时，才使用这些参考：

- **视频摘要 API 细节**：[`references/video-summarization-api.md`](references/video-summarization-api.md) 用于 `/v1/summarize`、`/summarize`、`/v1/generate_captions`、`/v1/stream_summarize`、健康探针、`/models`、`/recommended_config`、`/metrics`、请求字段、响应形状和 API 常见问题。
- **视频摘要服务配置和 ops**：[`references/video-summarization-deployment.md`](references/video-summarization-deployment.md) 用于 VSS `lvs` 配置、端口、必需的环境变量、日志、状态、干运行、拆除、模型/后端交换、Elasticsearch/Neo4j/ArangoDB 后端选择和服务级故障排除。
- **扩展视频摘要 ops 参考**：[`references/video-summarization-environment-variables.md`](references/video-summarization-environment-variables.md)、[`references/video-summarization-debugging.md`](references/video-summarization-debugging.md) 和 `assets/video-summarization.env.example`。

仅当您需要一个不在下方 Step 2 LVS 或后备 VLM 示例中已涵盖的请求字段、响应形状或端点，或处理直接视频摘要 API 请求时，才加载 `video-summarization-api.md`。仅用于部署、配置或服务操作时加载 `video-summarization-deployment.md`。

## 视频摘要 API 和服务 ops 请求

如果用户要求直接调用或调试视频摘要端点，请从 `[references/video-summarization-api.md](references/video-summarization-api.md)` 回答，而不是运行端到端视频摘要工作流。示例：列出视频摘要模型、检查就绪状态、获取推荐分块配置、检查指标、解释 422 响应或构建 `/v1/summarize` 请求正文。

如果用户要求配置、部署、重启、拆除或排除视频摘要服务故障，请优先使用 `vss-deploy-profile` 技能进行完整的 VSS 配置部署，并使用 `[references/video-summarization-deployment.md](references/video-summarization-deployment.md)` 获取视频摘要特定的服务详细信息。

## 路由

完全根据视频摘要服务的可用性（在 *Setup → 可用性检查* 下探查）。**持续时间不驱动路由。**

| `/v1/ready` | 后端 | 端点 |
|---|---|---|
| HTTP 200 | LVS 微服务带 HITL | `POST ${LVS_BACKEND_URL}/v1/summarize` |
| 其他任何情况 | VLM / RT-VLM 带默认提示 + 后备说明 | `POST ${VLM_BASE_URL}/v1/chat/completions` |

当 LVS 服务不可用时，后备消息——直接复制上方摘要：

> ⚠ **注意：** 输入视频 `<name>` 长度为 `<N>` 秒。
> 视频摘要服务未部署，因此此摘要由 VLM 单独使用通用默认提示生成的。部署 `lvs` 配置以获得更高质量的摘要，并针对场景/事件。

## 部署前提条件

VSS **lvs** 配置在 `$HOST_IP` 上是主要后端。如果 `/v1/ready` 探查（见 *Setup → 可用性检查*）在预热重试后返回任何不同于 200 的内容，请询问用户：

> *"VSS `lvs` 配置未在 `$HOST_IP` 上运行。是否使用 `-p lvs` 的 `/vss-deploy-profile` 技能现在部署它？回复 `no` 以使用 VLM 仅后备（质量较低，无法针对场景/事件）进行摘要。"*

- **是** → 转交 `/vss-deploy-profile`，然后重新探查并继续 Step 2（LVS + HITL）。
- **否** → 直接进入 **Step 2 后备（VLM 带默认提示）** 并添加路由后备说明。不要再次询问，也不要运行场景/事件 HITL。
- **预授权自主部署**（调用者明确说明）→ 跳过确认并直接调用 `/vss-deploy-profile`。
- **预授权使用 VLM 后备**（“跳过 lvs，仅使用 VLM”）→ 直接进入 Step 2 后备，无需提示。

---

## 设置

**端点（本地 VSS `lvs` 部署的默认值）：**

- VLM / RT-VLM: `${VLM_BASE_URL}` — 默认 `${RTVI_VLM_BASE_URL:-http://${HOST_IP:-localhost}:8018}`
- LVS 服务: `${LVS_BACKEND_URL}` — 默认 `http://${HOST_IP:-localhost}:38111`
- VIOS: 由 `vss-manage-video-io-storage` 拥有；请参阅那里。

使用环境变量时（删除 VLM 基地址末尾的 `/v1` — 技能会自行添加）。否则使用默认值。如果都不起作用，请询问用户——不要扫描端口或读取配置文件来猜测。

**模型名称：** 读取 `${VLM_NAME}`（默认 `nim_nvidia_cosmos3-nano-reasoner_bf16-final`）。它必须与 RT-VLM `/v1/models` 广告的 ID 匹配；不要替换友好的 `nvidia/cosmos3-nano-reasoner`。

有关端点模式、可选字段、响应包和错误处理，请参阅 [`references/video-summarization-api.md`](references/video-summarization-api.md)。

**可用性检查**（在路由之前运行）。
**就绪状态仅由 HTTP 状态码确定**——LVS `/v1/ready` 可能合法地返回 `200` 且正文为空，因此不要检查正文。

```bash
VLM="${VLM_BASE_URL:-${RTVI_VLM_BASE_URL:-http://${HOST_IP:-localhost}:8018}}"
VLM="${VLM%/v1}"

# VLM / RT-VLM: /v1/models 上返回 200
vlm_code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 --max-time 10 \
  "$VLM/v1/models")
[ "$vlm_code" = "200" ] && echo "VLM OK" || echo "VLM 不可达 (HTTP $vlm_code)"

# 视频摘要服务：/v1/ready 上返回 200，对 503（预热）进行最多约 30 秒的重试
VIDEO_SUMMARIZATION_URL=${LVS_BACKEND_URL:-http://${HOST_IP:-localhost}:38111}
video_sum_code=000
for i in $(seq 1 10); do
  video_sum_code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 --max-time 10 "$VIDEO_SUMMARIZATION_URL/v1/ready")
  case "$video_sum_code" in
    200) echo "video summarization OK"; break ;;
    503) sleep 3 ;;                 # 正在预热；继续轮询
    *)   break ;;                   # 任何其他代码 = 不可达，停止重试
  esac
done
[ "$video_sum_code" = "200" ] || echo "video summarization service 不可达 (HTTP $video_sum_code)"
```

**如何解释结果：**

- `video_sum_code = 200` → **Step 2 (LVS + HITL)** 对于每个视频。
- `video_sum_code != 200`，`vlm_code = 200` → **Step 2 后备 (VLM)**；添加路由后备说明。
- `vlm_code != 200` → 失败；至少必须有一个后端可达。
- 重试循环后的非 200 LVS 代码是唯一不可用的信号。空 stdout 或缺少 JSON 字段不是“不可用”。

---

## Step 1 - 通过 `vss-manage-video-io-storage` 获取片段 URL（子任务，不是最终答案）

**使用 `vss-manage-video-io-storage` 技能进行所有 VIOS 交互**——它拥有标准的 curl 配方、参数默认值和删除/上传流程。不要编造 URL 或手动编写 VIOS 调用；它们会漂移。

此步骤是子任务——不要在此结束你的回合；不要返回片段 URL 作为最终答案。从 VIOS 收集三个值：

1. **`streamId`**（通过 `sensor/list` → `sensor/<id>/streams`，或直接从上传响应中获取）。
2. **时间线** - `{startTime, endTime}`（ISO 8601 UTC）。`endTime - startTime` 是持续时间；仅用于用户界面标题（路由完全由 `/v1/ready` 驱动）。
3. **临时 MP4 片段 URL** — `/storage/file/<streamId>/url` 变体，`container=mp4`。响应字段：`.videoUrl`。两个后端都需要一个它们可以 `GET` 的 HTTP(S) URL。

其他所有内容（认证、上传、`disableAudio`、过期等）都生活在 `vss-manage-video-io-storage` 技能中——如果 VIOS 失败，请参考用户那里。

---

## Step 2 — 主要：视频摘要微服务带 HITL

**任何时候** `/v1/ready` 在设置中返回 200，都使用此路径。持续时间无关紧要。

有关高级字段（`media_info`、`schema`、结构化输出、流字幕、指标、推荐配置）请参阅 [`references/video-summarization-api.md`](references/video-summarization-api.md)。

### HITL：首先收集场景和事件（必需——不要跳过）

完整步骤在 [`references/hitl-prompts.md`](references/hitl-prompts.md) 中。始终在调用 LVS 服务之前运行 HITL。

**自主模式默认值。** 当调用者绕过 HITL（“无需提示运行自主模式”）AND 原始查询要求 `default`/`defaults`（或给出无），则使用 `scenario="activity monitoring"` 和 `events=["notable activity"]` **逐字**——不要从文件名或传感器名称推断。在最终回复中注意默认值，并提议使用更具体的参数重新运行。这是唯一支持的 HITL 绕过；“视频很短”或“用户看起来很匆忙”不是有效理由。

优先使用 `POST /v1/summarize`（3.2 GA 路由）；`/summarize` 是兼容性别名。

```bash
VIDEO_SUMMARIZATION_URL=${LVS_BACKEND_URL:-http://${HOST_IP:-localhost}:38111}

# 从 HITL 回复：
SCENARIO='warehouse monitoring'
EVENTS_JSON='["notable activity"]'
OBJECTS_JSON=''  # '' 表示省略，否则 '["forklifts","pallets","workers"]'

curl -s --max-time 300 -X POST "$VIDEO_SUMMARIZATION_URL/v1/summarize" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg url "<clip_url_from_vss_manage_video_io_storage>" \
        --arg model "${VLM_NAME:-nim_nvidia_cosmos3-nano-reasoner_bf16-final}" \
        --arg scenario "$SCENARIO" \
        --argjson events "$EVENTS_JSON" \
        --argjson objects "${OBJECTS_JSON:-null}" '{
    url: $url,
    model: $model,
    scenario: $scenario,
    events: $events,
    chunk_duration: 10,
    num_frames_per_second_or_fixed_frames_chunk: 20,
    use_fps_for_chunking: false,
    seed: 1
  } + (if $objects == null then {} else {objects_of_interest: $objects} end)')" \
  | jq -r '.choices[0].message.content' \
  | jq '{video_summary, events}'
```

如果 `video_summary` 和 `events` 都为空，则片段可能不包含请求的事件——使用更广泛的 `scenario`/`events` 重新运行，不要报告“无内容”。

**调整：** `chunk_duration`（默认 10 秒；`0` = 单个块）、`num_frames_per_second_or_fixed_frames_chunk`（默认 20；其含义取决于 `use_fps_for_chunking`）、`seed`（默认 1）。`num_frames_per_chunk` 已弃用。

---

## Step 2 后备 — VLM 直接带默认提示

**仅当** `/v1/ready` 在预热后未返回 200 时使用此路径。**不要运行 HITL**——用户未选择入；你是因为服务缺失而后备。将路由后备说明添加到响应的开头。

```bash
VLM="${VLM_BASE_URL:-${RTVI_VLM_BASE_URL:-http://${HOST_IP:-localhost}:8018}}"
VLM="${VLM%/v1}"
PROMPT='详细描述此视频中发生的事情，包括所有可见的人员、车辆、设备、物体、动作和环境条件。
输出要求：
[timestamp-timestamp] 发生的事情的描述。
示例：
[0.0s-4.0s] 第一个事件的描述
[4.0s-12.0s] 第二个事件的描述'

curl -s --max-time 300 -X POST "$VLM/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
        --arg model "${VLM_NAME:-nim_nvidia_cosmos3-nano-reasoner_bf16-final}" \
        --arg text "$PROMPT" \
        --arg url "<clip_url_from_vss_manage_video_io_storage>" \
        '{
          model: $model,
          temperature: 0.0,
          max_tokens: 1024,
          messages: [{
            role: "user",
            content: [
              {type: "text", text: $text},
              {type: "video_url", video_url: {url: $url}}
            ]
          }]
        }')" | jq -r '.choices[0].message.content'
```

**响应：** 标准的 OpenAI 聊天完成包。摘要在 `choices[0].message.content` 中。

**Cosmos 模型说明：** Cosmos 模型可能会通过 `<think>...</think><answer>...</answer>` 块返回推理。如果需要纯摘要，请省略推理指令。帧采样和像素限制在服务器端应用；客户端无需准备，当你传递 `video_url` 时。

---

## 端到端示例

有关完整的 LVS 或 VLM 后备脚本（探查 `/v1/ready` 并运行相应路径），请参阅 [`references/end-to-end-example.md`](references/end-to-end-example.md)。

---

## 响应

- **VLM** 返回 OpenAI 聊天完成包；摘要是 `choices[0].message.content`。
- **LVS 服务** 返回相同的包，但 `content` 是一个 JSON 字符串——运行 `jq -r '.choices[0].message.content' | jq` 以达到 `{video_summary, events}`。
- **错误** 表现为 HTTP 非二进制响应加上 JSON `{error: ...}`。LVS `503` 通常表示预热——重试 `/v1/ready`。

### 向用户展示输出

以 **最小的转换** 面向用户展示后端输出——不要释义、重新语音、添加表情符号或重新格式化。**一个后端调用 → 一个渲染**：不支持并行 hedging、重复标题，永远不要为同一个视频同时调用 LVS 和 VLM。

**标题行。** 以 **一个** 开头：

```
<video_name> 摘要 (<duration>)
```

`<duration>` = `Ns` 对于 `< 60 s`，否则 `Mm Ss`（例如 `3m 30s`）。

**LVS 输出：** **逐字** 渲染 `video_summary`（经过润色、控制语气的报告——重写会丢失保真度）。逐个渲染 `events` 条目，带有其 `start_time`、`end_time`、`type` 和完整的 `description` **逐字**（当客户端可以干净地渲染表格时，否则为每个事件列表）。您可以添加一行标题和一行结尾提议使用不同参数重新运行。

**VLM 输出：** **逐字** 渲染 `choices[0].message.content`。如果模型生成了 `<think>`…`</think>`<`answer>`…`</answer>` 块，请丢弃 `<think>` 块并显示答案。

**后备警告**（当适用时）**位于**摘要之上，切勿混入其中。

## 小贴士

- **根据服务可用性路由，而不是持续时间。** 在设置中一次探查 `/v1/ready`；HTTP 200 → 每个视频的 LVS+HITL；任何其他情况 → VLM 后备。
- **LVS 路径上的 HITL 是强制性的。** `defaults` 入选是唯一认可的绕过。VLM 后备路径是沉默的（无 HITL）。
- **就绪状态 = `/v1/ready` 上的 HTTP 200。** 除此之外什么都不是。正文可能为空。始终使用 `curl -s -o /dev/null -w '%{http_code}'`——永远不要通过 `jq`/`grep`/`head` 管道。
- **将 VIOS 委托给 `vss-manage-video-io-storage`**——这是一个子任务；最终答案是 Step 2 摘要，不是片段 URL。
- **LVS 输出需要两次 `jq`。** 第一次解包 OpenAI 包，第二次解析 `content` 中的 JSON 字符串。
- **优先使用 `/v1/summarize` 对于 3.2 GA**；`/summarize` 是兼容性别名。
- **使用端点广告的精确 VLM 模型 ID**（默认 `nim_nvidia_cosmos3-nano-reasoner_bf16-final`）。
- **逐字渲染输出**——不要释义、不要重新格式化、不要重写 `video_summary` 或 `choices[0].message.content`。
- **一个调用，一个渲染。** 没有并行 hedging，没有重复渲染。
- **匹配图像标签到主机平台。** 使用 `LVS_TAG=3.2.1`（在 x86 / Jetson Thor 上）和 `RTVI_VLM_IMAGE_TAG=3.2.1`（在 SBSA / DGX Spark / Grace（服务器级 ARM64）主机上）。

## 参考信息

- **vss-deploy-profile** — 启动 `base`（仅 VLM）或 `lvs`（VLM + 视频摘要服务）配置。
- **vss-manage-video-io-storage** (VIOS API) — 上传视频、列出流、获取片段 URL
- **vss-search-archive** — 跨存档进行语义搜索（不同的配置）
- **vss-query-analytics** — 从 Elasticsearch 查询事件/警报
- **视频摘要 API 参考** — [`references/video-summarization-api.md`](references/video-summarization-api.md)
- **视频摘要服务 ops 参考** — [`references/video-summarization-deployment.md`](references/video-summarization-deployment.md)
