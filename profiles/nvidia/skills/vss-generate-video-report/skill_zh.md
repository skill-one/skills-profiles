# 报告

通过路由到两个后端之一来生成视频分析报告——**绝不**通过 VSS 代理上的 `POST /generate`。

| 模式 | 后端 |
|---|---|
| **A. 视频片段** | `/vss-manage-video-io-storage` → 片段 URL → **VLM 聊天/补全** |
| **B. 事件范围** | `/vss-query-analytics` → 事件列表 → 叙述性报告 |

如果请求是模糊的（例如，“报告关于 `<传感器>`” 没有时限且没有事件措辞），默认为 **模式 A**。如果用户同时提到了传感器和时间段，请询问。见下文 **示例**，了解路由到每个模式的请求措辞。

---

## 说明

1.  **选择模式** — 模式 A 用于单个录制的片段/传感器视频，当请求命名时间段或事件/警报时使用模式 B（与 *示例* 匹配）。
2.  **验证部署配置** — 在 *部署先决条件* 下为该模式验证；如果其探测失败，则转交到 `/vss-deploy-profile`。
3.  **运行该模式的编号步骤** — *模式 A* 或 *模式 B* 下面的步骤。
4.  **在报告中嵌入之前，用 `$VSS_PUBLIC_HOST:$VSS_PUBLIC_PORT` 的一行重写每个面向用户的面片 URL**（*浏览器可播放的片段 URL*）。
5.  **将渲染的报告 Markdown 返回给用户**。

评估者的输出合同：
- 模式 A 的顶部标题必须正好是 `# 视频分析报告`。
- 模式 B 的顶部标题必须正好是 `# 事件范围报告`（绝不 `# 事件报告` 或传感器命名的变体）。
- 模式 B 必须包含 `## 基本信息`，包含模板中精确要求的行（报告标识符、范围、范围、总事件数、确认 / 拒绝 / 未验证）。

---

## 示例

- "生成此视频的报告" / "报告 `<传感器ID>`" → **模式 A**
- "分析 warehouse_01.mp4" / "创建上传视频的分析报告" → **模式 A**
- "报告 12:31Z 到 12:32Z 之间的事件" → **模式 B**
- "报告今天的警报" / "传感器 `<传感器>` 上一小时发生了哪些事件" → **模式 B**
- "总结 `<传感器>` 在 `<t1>` 和 `<t2>` 之间的警报" → **模式 B**

---

## 负面触发器

当请求是以下情况时，**不要**使用此技能：

- 对片段进行即席视觉问答，而没有明确要求报告（“卡车是什么颜色？”，“00:12 发生了什么？”）→ 使用 `/vss-ask-video`。
- 存档/语义相似性检索（“查找叉车”，“搜索所有视频中的尾随”）→ 使用 `/vss-search-archive`。
- 读取-only 事件/指标查询，没有报告渲染需求 → 使用 `/vss-query-analytics`。
- 部署/拆除/配置更改（“部署警报”，“切换配置文件”，“启动基础”）→ 使用 `/vss-deploy-profile`。
- 实时警报/规则管理请求 → 使用 `/vss-manage-alerts`。

**绝不**通过 VSS-agent `POST /generate` 路由报告。

---

## 部署先决条件

**模式 A** 需要VSS **基础**配置文件（VST + VLM NIM）。
**模式 B** 需要VSS **警报**配置文件（VA-MCP + Elasticsearch）。

探测：

```bash
# 模式 A — VST + VLM 可达性
curl -sf --max-time 5 "http://${HOST_IP}:30888/vst/api/v1/sensor/version" >/dev/null

# 模式 B — VA-MCP
curl -sf --max-time 5 "http://${HOST_IP}:9901/" >/dev/null
```

如果探测失败，则使用 `-p base`（模式 A）或 `-p alerts`（模式 B）转交到 `/vss-deploy-profile`。**始终**在部署前先确认部署。

---

## 片段 URL：VLM 输入与浏览器报告链接

VST 使用代理内部的 `${HOST_IP}:30888` 主机:端口返回片段 URL。
将原始 URL 保留为 `VIDEO_URL`，用于本地/集群内 VLM 帧拉取。
**不要**仅为了使其浏览器可播放而重写 VLM 输入 URL。

仅创建 `BROWSER_CLIP_URL` 用于渲染报告中显示的 URL。部署层导出浏览器端的主机:端口为 `$VSS_PUBLIC_HOST` / `$VSS_PUBLIC_PORT`（以及方案作为 `$VSS_PUBLIC_HTTP_PROTOCOL`）在所有配置文件 `.env` 中——Brev 或裸金属——因此报告链接重写为：

```bash
: "${VSS_PUBLIC_HOST:?在重写片段 URL 之前设置 VSS_PUBLIC_HOST}"
: "${VSS_PUBLIC_PORT:?在重写片段 URL 之前设置 VSS_PUBLIC_PORT}"
VSS_PUBLIC_HTTP_PROTOCOL="${VSS_PUBLIC_HTTP_PROTOCOL:-http}"
BROWSER_CLIP_URL=$(echo "$RAW_URL" | sed -E "s|^https?://[^/]+|${VSS_PUBLIC_HTTP_PROTOCOL}://${VSS_PUBLIC_HOST}:${VSS_PUBLIC_PORT}|")
```

如果任何必需的公共主机值缺失，则省略报告面的片段链接，并指出无法生成浏览器可播放的 URL；不要阻止本地 VLM 分析路径。将重写应用于渲染报告中出现的**每个片段 URL**（模式 A 步骤 4 片段 URL 行；模式 B 每个事件子子弹）。当 VLM 是本地/集群内时，在模式 A 步骤 3 上保留 VLM `video_url` 内容块在原始内部 URL。

---

## 模式 A — 报告录制的视频片段

**如果 VSS `lvs` 配置文件已部署**——`curl -sf --max-time 5 "http://${HOST_IP}:38111/v1/ready"` 返回 HTTP 200——运行 `/vss-summarize-video` 生成摘要，然后将其输出粘贴到步骤 4 中的报告模板并跳过步骤 1–3（VLM 直接路径）。仅在 `/v1/ready` 非HTTP 200时运行步骤 1–3。

### 步骤 1 — 解析片段 URL

转交到 `/vss-manage-video-io-storage` 以：

1. 列出传感器并确认命名的 `<传感器ID>` 存在（如果不存在则先上传）。
2. 当用户未提供 `startTime` / `endTime` 时，获取录制的范围 `/storage/<streamId>/timelines`。
3. 请求片段 URL：

   ```bash
   curl -s "http://${HOST_IP}:30888/vst/api/v1/storage/file/<streamId>/url?startTime=<startTime>&endTime=<endTime>&container=mp4&disableAudio=true" | jq -r .videoUrl
   ```

   这提供了一个直接 `mp4` URL，本地/集群内 VLM 可以从中拉取帧。在应用报告链接重写以在步骤 4 产生 `BROWSER_CLIP_URL` 之前，将此绑定到 `VIDEO_URL`（VLM 在步骤 3 中使用）并设置 `RAW_URL="$VIDEO_URL"`。用户无法直接访问 `$VIDEO_URL`。
   模式 A 要求选择的 VLM 端点能够获取 `VIDEO_URL`。
   本地 NIM/RT-VLM 部署通常可以；远程端点通常无法获取 `localhost`、私有 `HOST_IP` 或 VST 内部 URL。如果活动的 `VLM_ENDPOINT` 是远程的，则显示可达性要求，而不是在 `/v1/models` 成功后执行聊天请求。

### 步骤 2 — 解析 VLM 端点和模型

部署可能通过两个堆栈之一提供 VLM。两者都暴露 OpenAI 兼容的 `chat/completions` API — 选择其中之一：

| 后端 | 环境变量 | 典型主机端点 | 选择条件 |
|---|---|---|---|
| **NIM Cosmos** | `VLM_BASE_URL`、`VLM_NAME`、`VLM_MODE`、`VLM_MODEL_TYPE` | `${VLM_BASE_URL}/v1`（环境变量中末尾没有 `/v1`；代理会追加它） | `VLM_MODEL_TYPE != rtvi` **and** `VLM_MODE` ∈ {`local`、`local_shared`、`remote`} **and** `VLM_BASE_URL` 非空 |
| **RT-VLM Cosmos** | `RTVI_VLM_BASE_URL`、`RTVI_VLM_MODEL_TO_USE`、`VLM_MODEL_TYPE` | `${RTVI_VLM_BASE_URL}/v1` — 如果未设置，则从 `${HOST_IP}` 衍生（警报为 `http://${HOST_IP}:8018/v1`，基础为 `http://${HOST_IP}:30082/v1`） | `VLM_MODEL_TYPE = rtvi`，或 `VLM_MODE=none`，或 `VLM_BASE_URL` 为空；也是 `warehouse` 的唯一路径 |

从运行中的代理容器读取实时值——不要猜测：

```bash
docker exec vss-agent sh -lc '
for k in HOST_IP VLM_MODE VLM_MODEL_TYPE VLM_BASE_URL VLM_NAME RTVI_VLM_BASE_URL RTVI_VLM_MODEL_TO_USE; do
  v="$(printenv "$k")"
  [ -n "$v" ] && printf "%s=%s\n" "$k" "$v"
done
'
```

不要从 `vss-agent` 环境变量要求 `RTVI_VLM_ENDPOINT`；几个配置文件没有注入它。

选择规则：

```bash
if [ "${VLM_MODEL_TYPE:-}" = "rtvi" ]; then
  VLM_BACKEND="rtvlm"
  VLM_ENDPOINT="${RTVI_VLM_BASE_URL:+${RTVI_VLM_BASE_URL%/}/v1}"
  [ -z "${VLM_ENDPOINT}" ] && VLM_ENDPOINT="http://${HOST_IP}:8018/v1"   # 警报默认
  VLM_MODEL="${RTVI_VLM_MODEL_TO_USE}"
elif [ -n "${VLM_BASE_URL}" ] && [ "${VLM_MODE}" != "none" ]; then
  VLM_BACKEND="nim_cosmos"
  VLM_ENDPOINT="${VLM_BASE_URL%/}/v1"
  VLM_MODEL="${VLM_NAME}"
else
  VLM_BACKEND="rtvlm"
  VLM_ENDPOINT="${RTVI_VLM_BASE_URL:+${RTVI_VLM_BASE_URL%/}/v1}"
  [ -z "${VLM_ENDPOINT}" ] && VLM_ENDPOINT="http://${HOST_IP}:30082/v1"  # 基础默认
  VLM_MODEL="${RTVI_VLM_MODEL_TO_USE}"
fi
```

在发送聊天请求之前探测 `/v1/models` 以确认选择的端点是否活跃且模型已加载：

```bash
curl -sf --max-time 5 "${VLM_ENDPOINT}/models" | jq -r '.data[].id'
```

如果探测失败或列出的 ids 不包含 `${VLM_MODEL}`，则回退到另一个后端（或显示错误——绝不静默地选择服务器上没有的模型）。

### 步骤 3 — 直接调用 VLM

使用 OpenAI 兼容的 `chat/completions` 端点，并带有 `video_url` 内容块——相同的有效负载形状**和多模态设置** `video_understanding` 在 `src/vss_agents/tools/video_understanding.py` 中构建（`_build_vlm_messages` + Cosmos `base_vlm.bind(...)` 调用）。

帧采样和视觉标记（像素）预算必须镜像**实时** `video_understanding` 设置为活动配置文件。**发送 `mm_processor_kwargs` 和 `media_io_kwargs`**，以便直接调用使用与代理内 `video_understanding` 工具相同的帧采样和像素预算——省略它们会让 VLM 应用其自己的默认值，因此输出与代理路径不一致。

```bash
PROMPT='详细描述视频中发生的事情，并为每个片段或事件提供时间戳（从片段开始算起的秒数）。涵盖场景、对象、人员、车辆和显着动作。'

# 推理默认关闭——与基础配置文件的 `video_understanding` 配置（`reasoning: false`）匹配。
# video_understanding.py 使用 config.reasoning，除非调用者覆盖它，因此默认为非推理。
# 仅当用户明确要求推理时才附加 Cosmos Reason 2 推理后缀
# （对于非 cosmos-reason2 VLM，请删除它）。关闭推理时，响应没有 <think> 块。
if [ "${REASONING:-false}" = "true" ]; then
PROMPT="${PROMPT}

使用以下格式回答问题：

<think>
你的推理。
</think>

立即在 </think> 标签后写下你的最终答案。"
fi

# 如果步骤 3 独立运行，则从当前环境/模型推导出缺失的后端。
[ -z "${VLM_BACKEND:-}" ] && {
  if [ "${VLM_MODEL_TYPE:-}" = "rtvi" ]; then
    VLM_BACKEND="rtvlm"
  elif [[ "${VLM_MODEL:-}" == nvidia/cosmos* ]]; then
    VLM_BACKEND="nim_cosmos"
  else
    VLM_BACKEND="rtvlm"
  fi
}

# 多模态设置——从实时代理配置文件路径解析，而不是硬编码候选者。
CFG_JSON=$(
docker exec vss-agent python3 -c '
import json, os, yaml
p = os.getenv("VSS_AGENT_CONFIG_FILE")
if not p:
    raise SystemExit("VSS_AGENT_CONFIG_FILE is not set in vss-agent")
if not os.path.isabs(p):
    p = os.path.join("/vss-agent", p.lstrip("./"))
with open(p, encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}
vu = (cfg.get("functions", {}) or {}).get("video_understanding", {}) or {}
print(json.dumps({
    "max_fps": int(vu.get("max_fps", 2)),
    "max_frames": int(vu.get("max_frames", 30)),
    "min_pixels": int(vu.get("min_pixels", 3136)),
    "max_pixels": int(vu.get("max_pixels", 8388608)),
}))
')
)
[ -n "${CFG_JSON}" ] || { echo "Failed to read video_understanding config from vss-agent"; exit 1; }
printf '%s' "${CFG_JSON}" | jq -e . >/dev/null || { echo "Invalid config JSON from vss-agent"; exit 1; }
MAX_FPS="$(printf '%s' "${CFG_JSON}" | jq -r '.max_fps')"
MAX_FRAMES="$(printf '%s' "${CFG_JSON}" | jq -r '.max_frames')"
MIN_PIXELS="$(printf '%s' "${CFG_JSON}" | jq -r '.min_pixels')"
MAX_PIXELS="$(printf '%s' "${CFG_JSON}" | jq -r '.max_pixels')"

# num_frames = min(int(clip_seconds) * max_fps, max_frames), min 1 — 与 video_understanding.py 匹配。
# clip_seconds (Step 1 endTime-startTime) 可能是分数的；截断为整数秒——bash $((...))
# 仅支持整数，对 "15.0"/"1.5" 错误。默认 15s -> 限制在 MAX_FRAMES。
CLIP_SECONDS=$(awk -v s="${CLIP_SECONDS:-15}" 'BEGIN{printf "%d", s}')
NUM_FRAMES=$(( CLIP_SECONDS * MAX_FPS ))
[ "$NUM_FRAMES" -gt "$MAX_FRAMES" ] && NUM_FRAMES=$MAX_FRAMES
[ "$NUM_FRAMES" -lt 1 ] && NUM_FRAMES=1

# 仅在 NIM Cosmos 路径上应用 Cosmos mm/media kwargs。
# RT-VLM 模式使用其自己的服务器端预处理，不应接收这些 kwargs。
MM_KWARGS=""
if [ "${VLM_BACKEND}" = "nim_cosmos" ]; then
  case "$VLM_MODEL" in
    *cosmos-reason2*) MM_KWARGS=", \"mm_processor_kwargs\": {\"size\": {\"shortest_edge\": ${MIN_PIXELS}, \"longest_edge\": ${MAX_PIXELS}}}, \"media_io_kwargs\": {\"video\": {\"num_frames\": ${NUM_FRAMES}}}" ;;
    *cosmos*)         MM_KWARGS=", \"mm_processor_kwargs\": {\"videos_kwargs\": {\"min_pixels\": ${MIN_PIXELS}, \"max_pixels\": ${MAX_PIXELS}}}, \"media_io_kwargs\": {\"video\": {\"num_frames\": ${NUM_FRAMES}}}" ;;
    *)                      MM_KWARGS="" ;;
  esac
fi

curl -s --connect-timeout 5 --max-time 120 -X POST "${VLM_ENDPOINT}/chat/completions" \
  -H "Content-Type: application/json" \
  -d @- <<EOF | jq -r '.choices[0].message.content'
{
  "model": $(printf '%s' "${VLM_MODEL}" | jq -Rs .),
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": $(printf '%s' "${PROMPT}" | jq -Rs .)},
        {"type": "video_url", "video_url": {"url": $(printf '%s' "${VIDEO_URL}" | jq -Rs .)}}
      ]
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.0${MM_KWARGS}
}
EOF
```

> kwargs 块具有后端感知性：在 `nim_cosmos` 上，Reason2 变体（`nvidia/cosmos-reason2*`）使用 `mm_processor_kwargs.size{shortest_edge,longest_edge}` 和其他 NIM Cosmos 变体（`nvidia/cosmos*`）使用 `mm_processor_kwargs.videos_kwargs{min_pixels,max_pixels}`；两者还发送 `media_io_kwargs.video.num_frames`。在 `rtvlm` 上，不发送 Cosmos kwargs。

如果 VLM 返回 `<think>…</think>` 块（Cosmos Reason 推理模式），则仅保留 `</think>` 后面的文本作为报告正文。

### 步骤 4 — 填充视频分析报告模板

复制 [`assets/video-analysis-report.md`](assets/video-analysis-report.md)，填写每个占位符，并将渲染的 Markdown 返回给用户。保留源资产不变。在渲染之前，验证 `BROWSER_CLIP_URL` 已设置且非空，然后在 `Clip URL` 行中替换 `<BROWSER_CLIP_URL>` 为该确切值。绝不保留占位符在输出中，绝不包含模板说明在填充的单元格中，也绝不使用原始 `HOST_IP:30888` URL。

---

## 模式 B — 报告时间段内的事件

### 步骤 1 — 解析时间范围和（可选的）传感器

- `start_time` / `end_time` 必须是 ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SS.sssZ`)。相对于当前主机时钟解析相对短语（“上一小时”，“今天”）。
- 如果用户命名了传感器，则将其捕获为 `source` + `source_type=sensor`。否则，将两者都留空以进行所有传感器查询。

### 步骤 2 — 通过 `/vss-query-analytics` 获取事件

转交到 `/vss-query-analytics`（初始化 → `tools/call`）并传递：

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "video_analytics__get_incidents",
    "arguments": {
      "source": "<传感器ID或省略>",
      "source_type": "sensor",
      "start_time": "<ISO>",
      "end_time": "<ISO>",
      "max_count": 100,
      "includes": ["objectIds", "info"]
    }
  },
  "id": 1
}
```

只读边界（强制）：
- 模式 B 严格是只读分析检索。绝不写入、播种、回填或修改 Elasticsearch/VA 数据。
- 禁止示例：索引合成事件，将固定负载回放至 ES，调用写入/更新/删除 API 以“使数据可用于报告”。
- 如果请求的时间段/范围没有事件，则按空结果处理（见下文）；不要编造数据。

对于每个事件保留：`id`、`sensorId`、`timestamp`、`end`、`category`、`place.name`、`info.verdict`、`info.reasoning`、`objectIds`，以及片段 URL（通常是 `info.clip_url`、`clip_url` 或响应携带的任何片段指针字段）。**在将其粘贴到报告中之前，将 `$VSS_PUBLIC_HOST:$VSS_PUBLIC_PORT` 重写应用于每个片段 URL**——原始值是用户浏览器无法访问的 `HOST_IP:30888` URL。

### 步骤 3 — 填充事件范围报告模板

复制 [`assets/incident-range-report.md`](assets/incident-range-report.md)，然后按传感器分组（如果没有传感器范围则按类别分组），统计裁决，并列出每个事件的时间戳 / 类别 / 裁决 / 推理。保留源资产不变。每个事件片段值必须是重写的浏览器可播放 URL；当事件不携带片段 URL 时，省略片段行。绝不包含填充单元格中的模板说明。

如果 `get_incidents` 返回零结果，则停止并返回一个仅包含请求范围和范围的精确单行空范围声明。不要渲染完整的 Incident Range 模板，不要编造事件，不要播种测试数据，也不要回退到模式 A。
