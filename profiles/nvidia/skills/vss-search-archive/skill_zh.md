## 目的

对存档视频运行顶层 VSS 融合搜索，摄取新的片段 / RTSP 流用于搜索，并删除搜索源。

## 前置条件

- 可达 `$HOST_IP` 上的活动 VSS 部署（参见 `vss-deploy-profile` 和 `references/`）。
- 安装了 `vss-manage-video-io-storage` 技能（用于搜索前列出和管理视频源）。
- 任何图像拉取都需要 `$NGC_CLI_API_KEY` 和 `$NVIDIA_API_KEY` 中的 NGC 凭证。
- 调用者系统上可用 `curl`、`jq` 和 Docker。

## 说明

遵循下方的路由表和分步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都意图按从上到下的顺序执行。详细的参考材料位于 `references/`。

## 示例

端到端的工作示例保存在 `evals/` 下（每个 `*.json` 清单包含一个可运行的场景）并在每个工作流程的 `curl` 块中内联提供。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

## 限制

- 需要部署并从调用者可达的匹配 VSS 配置文件 / 微服务。
- NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：从 NGC 拉取返回 HTTP 401/403。**原因**：缺少/过期的 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# 视频搜索工作流程

> **Alpha 功能** — 不推荐用于生产环境。

使用 Cosmos Embed1 嵌入使用自然语言搜索视频存档。需要搜索配置文件 — 使用 `vss-deploy-profile` 技能部署（`-p search`）。这些视频源可以是摄取的文件或 RTSP 流。

## 何时使用

- "查找所有叉车实例"
- "某人何时进入限制区域？"
- "显示靠近装卸码头的人"
- "搜索上午 8 点到中午之间的车辆"
- 任何跨视频存档的自然语言搜索
- "摄取 `<file>` 用于搜索" / "上传此视频用于搜索"
- "添加此 RTSP 流用于搜索" / "注册 `<rtsp_url>` 用于搜索"
- "从搜索中删除 `<file>`" / "删除此视频和嵌入"

---

## 部署前置条件

此技能需要在 `$HOST_IP` 上的主机上运行 VSS **搜索** 配置文件。在发出任何请求之前：

1. 探测堆栈：
   ```bash
   curl -sf --max-time 5 "http://${HOST_IP}:8000/docs" >/dev/null \
     && curl -sf --max-time 5 "http://${HOST_IP}:9200/" >/dev/null
   ```
   （第二个检查确认 Elasticsearch 已启动 — 仅限搜索配置文件独特。）

2. **如果探测失败**，询问用户：
   > *"VSS `搜索` 配置文件未在 `$HOST_IP` 上运行。是否现在使用 `/vss-deploy-profile` 技能并使用 `-p search` 部署它？"*

   - 如果是 → 转交 `/vss-deploy-profile` 技能。成功后返回这里。
   - 如果不是 → 停止。不要针对缺失或错误配置的堆栈运行此技能。

   （如果您的调用者已授予明确的预授权以自主部署 — 例如，请求说明“已授权部署先决条件”，或者您正在具有该权限的非交互式评估工具包中运行 — 跳过确认并直接调用 `/vss-deploy-profile`。）

3. 如果探测通过，则继续。

---

## 摄取前置条件（任何 `/generate` 之前都需要）

要使源可搜索，必须通过 VSS 代理后端摄取，而不是仅通过 VIOS。代理的摄取路由拥有 VIOS 上传 + RTVI-CV 注册 + RTVI-嵌入管道作为一个事务；裸 VIOS PUT 仅存储字节，永远不会将它们连接到 Elasticsearch。

首先在 VIOS 中确认源是否存在（强制工作流程步骤 2）。如果缺失，请在触发 `/generate` 之前使用以下配方之一摄取它。摄取成功后，源会以您提供的名称出现在 `sensor/list` 下，并且可以从代理转发到其搜索工具分解器的自然语言查询中引用 — 您不需要自己构建结构化的 `video_sources` 负载。

### 文件上传 — 通用三步流程

使用下方的带时间戳的上传表单。VSS 代理/搜索配置文件使用 `2025-01-01T00:00:00.000Z` 作为上传的 `video_file` 基时间戳；VIOS 存储和嵌入必须共享该时间线，否则截图 URL 和关键帧获取可能会失败。

```bash
FILENAME="<filename.mp4>"
FILE_PATH="/path/to/${FILENAME}"

# 1. 询问代理获取分块上传 URL
UPLOAD_URL=$(curl -s -X POST "http://${HOST_IP}:8000/api/v1/videos" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"${FILENAME}\"}" | jq -r .url)

# 2. 将文件分块 POST 到该 VST URL（nvstreamer 协议）。
#    最终块响应包含 sensorId。
IDENTIFIER=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)
UPLOAD_RESPONSE=$(curl -s -X POST "${UPLOAD_URL}" \
  -H "nvstreamer-chunk-number: 1" \
  -H "nvstreamer-total-chunks: 1" \
  -H "nvstreamer-is-last-chunk: true" \
  -H "nvstreamer-identifier: ${IDENTIFIER}" \
  -H "nvstreamer-file-name: ${FILENAME}" \
  -F "mediaFile=@${FILE_PATH};filename=${FILENAME}" \
  -F "filename=${FILENAME}" \
  -F 'metadata={"timestamp":"2025-01-01T00:00:00"}')

# 3. 告知代理上传完成 — 这将分发给 RTVI-CV + RTVI-embed
SENSOR=$(printf '%s' "${UPLOAD_RESPONSE}" | jq -r .sensorId)
[ -z "${SENSOR}" ] || [ "${SENSOR}" = "null" ] \
  && { echo "Upload failed: no sensorId in response: ${UPLOAD_RESPONSE}"; exit 1; }
printf '%s' "${UPLOAD_RESPONSE}" \
  | jq --arg filename "${FILENAME}" '. + {filename: $filename}' \
  | curl -s -X POST "http://${HOST_IP}:8000/api/v1/videos/${SENSOR}/complete" \
      -H "Content-Type: application/json" \
      -d @- | jq .
```

等待 `/complete` 响应（它返回 `chunks_processed > 0` 一旦嵌入到位）。只有到那时视频才可搜索。

> 已弃用的 `PUT /api/v1/videos-for-search/{filename}` 路径也保留用于遗留调用者（单次、代理驱动），但其 OpenAPI 条目已标记为 `deprecated`。请为新工作优先使用上述三步流程。

### RTSP 流 — 单个端点

```bash
curl -s -X POST "http://${HOST_IP}:8000/api/v1/rtsp-streams/add" \
  -H "Content-Type: application/json" \
  -d '{
    "sensorUrl": "rtsp://<host>:<port>/<path>",
    "name": "<sensor-name>",
    "username": "",
    "password": "",
    "location": "",
    "tags": ""
  }' | jq .
```

响应形状为 `{status, message, error}` — 没有 `sensorId`（代理通过您提供的 `name` 键控流）。在任何步骤失败之前，之前的步骤都会回滚。`start_embedding_generation` 步骤是发射并验证：2xx 确认请求已接受并且嵌入管道在后台运行，**不是**流已可搜索。只有在足够的数据块到达 Elasticsearch 之后，搜索命中才会开始出现 — 如果您需要就绪信号，几秒钟后使用低 `top_k` 查询进行轮询。

### 删除源 — 代理后端清理

通过代理后端删除，而不是裸 VIOS，以便 VIOS 存储和搜索嵌入一起清理。

```bash
# 对于视频文件：video_id 是 VIOS sensor/video UUID
curl -s -X DELETE "http://${HOST_IP}:8000/api/v1/videos/<video_id>" | jq .

# 对于 RTSP 流：name 是注册的源名称
curl -s -X DELETE "http://${HOST_IP}:8000/api/v1/rtsp-streams/delete/<name>" | jq .
```

---

## 搜索工作原理

1. **摄取** — 文件通过代理的三步通用流程传入；RTSP 流通过 `/api/v1/rtsp-streams/add`。这两个路由都将源交给 RTVI-CV（属性检测）和 RTVI-Embed（Cosmos Embed1），它们为视频片段生成向量嵌入。
2. **索引** — 嵌入被 Kafka 管道存储到 Elasticsearch。
3. **查询** — 自然语言查询被嵌入并与存储的向量按相似性匹配。
4. **结果** — 按相关性排序的时间戳视频片段，带有片段播放链接。

由 VSS 代理编排的搜索可以导致 3 种行为：
- 属性仅：当 LLM 分解查询并发现只有外观属性而没有动作时（例如 "穿着红色夹克的人"）
- 嵌入仅：当查询没有可提取的属性时（例如 "显示叉车"）
- 融合：当查询既有动作又有属性时（例如 "穿着红色夹克跑步的人"），它首先运行嵌入搜索，然后使用属性搜索重新排序

---

## 强制工作流程

使用此技能时，始终遵循此高级工作流程：
1. **从用户指令中解析输入 — 如果 `$HOST_IP`
   没有明确提供，则硬停止。** 参见 § 输入解析。不要默认为 `localhost`、`127.0.0.1`、代理本身运行的主机或任何其他猜测。不要在用户提供了端点之前发出
   `POST http://.../generate` 请求。向用户提出一个单一的问题，询问 `HOST_IP` / VSS 代理端点，并等待。
2. **解析源 — 在任何 `/generate` 调用之前硬停止。**
   如果用户查询引用了特定的视频 / 传感器名称（例如 "机场视频"、"warehouse_cam_3"、"sample_warehouse"），请在触发
   `POST .../generate` 之前验证它是否实际上在 VIOS 中注册。通过 `vss-manage-video-io-storage` 技能列出源。

   然后：
   - **如果命名的源（或明显的子字符串匹配名称）在列表中** → 继续步骤 3。逐字转发用户的自然语言查询 — 代理自己的搜索工具分解器 (`services/agent/src/vss_agents/tools/search.py`) 根据可用源从给定的文本中提取 `video_sources`，因此该技能不需要自己构建结构化的 `video sources` 负载。
   - **如果命名的源不在列表中** → 停止。不要作为探测触发 `/generate`。向用户提供注册的源名称，并询问他们是否指其中之一，是否要摄取缺失的源（指向 *摄取前置条件* 并通过代理后端运行匹配的文件或 RTSP 配方，而不是裸 VIOS），或者是否要放弃查询。等待澄清。
   - **如果查询未命名特定源**（"在摄取的视频中查找叉车"、"跨所有源搜索"）→ 跳过子字符串检查，但 `sensor/list` 必须返回非空（否则没有源被摄取 → 硬停止）。
3. 通过选择的方法运行搜索。
4. 向用户查询呈现结果。将响应格式化为专业检查报告，但命名为 `Video Search Results`：
   — 使用清晰的节标题
   - 将发现结果单独组织，并附带支持细节，并在最后加上摘要
   - 在有助于比较的地方使用表格。像技术报告一样写作，而不是聊天消息。
   - 如果标准结果非空，则除了 "Critic result" ("confirmed" | "rejected" | "skipped") 列外，还包括 "Criteria" 列，其中包含此搜索结果的所有标准（{criteria_n}: ✓ | ✗）
5. 关键：简要地向用户解释结果并解释这一点。
   如果搜索失败，或者返回意外结果（即看起来不匹配用户查询的视频、零匹配、零视频返回、错误等），停止。不要在没有阅读 [troubleshooting.md](references/troubleshooting.md) 以迭代反馈循环直到找到并像专业检查报告一样呈现正确结果之前继续。
6. 最终验证：
   - ALWAYS 告知用户可以进行最终和进一步验证。将其呈现为 `Verification Step`
   - ONLY IF 用户同意，使用搜索命中（JSON 结果）中最佳候选者（最高相似度分数）的 `screenshot_url` 从 `/tmp` 下载截图。阅读它们并验证它们是否与用户查询对应

## 输入解析

仅从对话或用户查询中推断这些输入（除非提供其他文件）。如果某些无法推断，请立即询问用户：
- $HOST_IP: VSS 代理后端运行的位置

---

## 注意事项

- ALWAYS 如果发生任何意外情况，立即进入工作流程的故障排除步骤，阅读 [troubleshooting.md](references/troubleshooting.md)
- 查询最好使用 **具体的视觉描述**（对象、动作、位置）。如果需要，增强用户查询以提升问题质量，扩展潜在细节
- 该技能假定视频源已通过代理后端摄取（参见 *摄取前置条件*）。当用户明确要求时（"摄取 `<file>` 用于搜索"、"添加 `<rtsp_url>` 用于搜索"）；它不会搜索用户未命名的本地文件系统文件，也不会使用裸 VIOS PUT 路径（不会生成嵌入）。工作流程步骤 2 仍然使确认 "此源存在于 VIOS" 成为 `/generate` 之前的硬前置条件。
- 使用 `vss-query-analytics` 技能将搜索结果与事件/警报数据交叉引用

---

## 通过 REST API 搜索

默认使用此 REST API 方法，除非用户指定其他方式。

```bash
# 默认情况下仅考虑已摄取的视频文件源
curl -s -X POST http://${HOST_IP}:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_message": "find all instances of forklifts"}' | jq .
```

### 更多示例

当传递结构化请求选项（如 `search_source_type`）时使用 `messages` 请求形状；`input_message` 快捷方式不接受额外字段。

```bash
# 通过对象搜索
curl -s -X POST http://${HOST_IP}:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_message": "find vehicles in the parking lot"}' | jq .

# 通过动作搜索
curl -s -X POST http://${HOST_IP}:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_message": "show me people running"}' | jq .

# 通过时间上下文搜索
curl -s -X POST http://${HOST_IP}:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"input_message": "what happened at the entrance between 2pm and 3pm?"}' | jq .

# 仅考虑具有 `search_source_type` 过滤器的 RTSP 源，即实时摄像头流
curl -s -X POST http://${HOST_IP}:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "find all instances of forklifts"}], "search_source_type": "rtsp"}' | jq .
```

### 高级控制旋钮

如果用户查询模糊，用户需要更多指导或需要细粒度控制，通过在纯文本中明确调用某些选项来增强用户 `input_message`，并引导代理朝所需方向。可用控制轴：

| 轴                 | 类型      | 默认 | 描述                                               |
|----------------------|-----------|---------|-----------------------------------------------------------|
| `video sources`      | string[]  | null    | 过滤特定摄像头或传感器名称                |
| `top k`              | int       | 10      | 最大结果
| `minimum similarity` | float     | 0.0     | 最小相似度阈值；提高（例如 0.3）以过滤噪声|
| `critic usage`       | bool      | true    | VLM 验证每个结果并移除误报      |
| `description`        | string    | null    | 如果有元数据，按摄像头元数据（例如位置、类别）过滤 |

选择一些这些调整选项。根据用户的情况和查询进行调整。有关利用这些进行发现模式的示例，请参阅 [discovery_modes.md](references/discovery_modes.md)。

---

## 通过 Agent UI 搜索

打开 `http://${HOST_IP}:3000/` 并输入自然语言查询：

```
find all instances of forklifts
show me people near the loading dock
when did a truck arrive at the gate?
find someone wearing a red jacket
```

结果包括带时间戳的片段和相似度分数。

bump:2
