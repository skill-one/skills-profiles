# 使用 VLM 通过 VSS 代理进行视频问答

当您需要关于视频的详细信息，而 VLM 需要查看视频帧时，请使用此技能——例如，代理没有可用的先前答案，需要针对特定片段进行**全新的像素分析**。

---

## 使用场景

- 用户询问视频中**发生了什么**，出现了哪些**物体/人物/动作**，**颜色**，**时间**，**安全性**或其他需要观看片段的**视觉事实**。
- 用户要求提供**细节**，而这些细节无法从现有消息、摘要、Elasticsearch/MCP 结果或文件名中单独回答——您需要**对视频进行模型推理**。
- 在粗略摘要或报告生成后，关于**内容细节**的后续问题。

除非用户明确要求**与视频进行验证**，否则**不要**使用此技能，当**数据库/MCP/先前工具输出**已经回答了问题时。

---

## 部署前提条件

此技能需要一个提供 `video_understanding` 工具的 VSS 配置文件——通常是**base**（推荐）或**lvs**。在发出任何请求之前：

1. 探测 VSS 代理：
   ```bash
   curl -sf --max-time 5 "http://${HOST_IP}:8000/docs" >/dev/null
   ```

2. **如果探测失败**，请向用户询问：
   > *"在 `$HOST_IP` 上没有运行 VSS 配置文件。是否使用 `/vss-deploy-profile` 技能部署 `base`（推荐用于每片段 VLM 问答）？如果您更喜欢 `lvs`，请说明。"**

   - 如果是 → 转交 `/vss-deploy-profile -p base`（如果用户更喜欢 `-p lvs`）。成功后返回这里。
   - 如果不是 → 停止。

3. 如果探测成功，继续进行。

---

## 传感器前提条件

**您必须在任何 `/generate` 调用之前列出 VST 传感器。** 即使用户明确指定传感器名称，即使用户断言视频已经上传，即使上一轮似乎使用了同一视频，也必须执行此操作。不要跳过此步骤。

1. 列出传感器：
   ```bash
   curl -sf --max-time 5 "http://${HOST_IP}:30888/vst/api/v1/sensor/list" | jq '.[].name'
   ```

2. 将返回的 `name` 值与用户提供的 `<sensor-id>`（或**文件名干**，例如 `warehouse_safety_0001`）进行比较。

3. **如果存在匹配的传感器** → 进入下面的代理工作流程。

4. **如果没有匹配的传感器**——首先上传视频，然后重新列出以确认新传感器出现：
   ```bash
   # 文件名：不能包含空格
   # 时间戳：ISO 8601 UTC — 如果用户未指定，默认为 2025-01-01T00:00:00.000Z
   curl -s -X PUT "http://${HOST_IP}:30888/vst/api/v1/storage/file/<filename>?timestamp=<timestamp>" \
     -H "Content-Type: application/octet-stream" \
     -H "Content-Length: <file_size_in_bytes>" \
     --upload-file /path/to/<filename> | jq .
   ```
   请参阅 `/vss-manage-video-io-storage` 了解完整的上传语义（v1 vs v2，冲突处理，删除流程）。在交互式运行中，上传前请先与用户确认。**永远**不要在运行上述传感器列表检查之前发出无条件的 PUT 命令——这正是此前提条件存在的目的。

---

## 代理工作流程

上述传感器前提条件必须已经确认（或创建）传感器存在于 VST 上。然后：

1. **片段**——确定**传感器 ID**、**文件名**或**URL**，用于一个视频片段。如果存在歧义，请询问用户。
2. 调用 vss 代理，并提供传感器 ID，要求它调用 `video_understanding` 工具来回答用户的问题。
3. 将 vss 代理的答案返回给用户。

## 查询 VSS 代理 (`/generate`)

```bash
# 从部署中设置（compose / .env / vss-agent 监听的 host）
export VSS_AGENT_BASE_URL="http://localhost:8000"

curl -s -X POST "${VSS_AGENT_BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{"input_message": "Call video_understanding tool to answer the following question about <sensor-id>: <user query>"}' | jq .
```

### 响应契约和提取

`/generate` 返回一个包含助手输出的 JSON 对象，其中 `value` 包含答案，例如：

```json
{"value":"<agent-think><agent-think-step ...>...</agent-think-step></agent-think>\n\n<final answer>\n\n"}
```

没有单独的 clean-answer 字段。可消费的答案是删除任何 `<agent-think>...</agent-think>` 块后的 `.value` 中的文本。

此技能（以及任何下游调用者）所需的处理：

1. 从 JSON 响应中读取 `.value`。
2. 删除任何出现的 `<agent-think>...</agent-think>` 部分。
3. 仅将剩余的最终答案文本返回给用户。

示例提取：

```bash
curl -s -X POST "${VSS_AGENT_BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{"input_message":"Call video_understanding tool to answer the following question about <sensor-id>: <user query>"}' \
| jq -r '.value' \
| python3 -c 'import re,sys; t=sys.stdin.read(); t=re.sub(r"<agent-think>.*?</agent-think>\s*", "", t, flags=re.S); print(t.strip())'
```

---

## 参考文档

- **vss-manage-video-io-storage** — VST 存储回放 URL，以便**`VIDEO_URL`** 对 VLM 有效。
- **vss-generate-video-report** — 通过**模式 A（直接 VLM）**或**模式 B（视频分析事件）**生成带时间戳的**报告**；此技能是**VSS-agent `/generate`**，用于**临时视频问答**。
