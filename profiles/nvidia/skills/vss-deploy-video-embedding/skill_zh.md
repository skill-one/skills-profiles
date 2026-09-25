# VSS 视频嵌入 (RT-Embed)

当您需要以下功能时，请使用此技能：

- 从 Docker Compose 文件中部署 VSS 视频嵌入微服务。
- 生成针对 Cosmos-Embed1-448p 模型的文本或视频嵌入。
- 嵌入上传的文件、HTTP/S3/文件/数据 URL 或实时 RTSP 流。
- 将服务与 Redis、Kafka 和 OpenTelemetry 一起集成到 VSS 部署中。
- 排查就绪、模型下载、GPU 或流重连失败。

**触发短语：** `vss-deploy-video-embedding`、`RT-Embed`、`rtvi-embed`、`视频嵌入服务`、`Cosmos-Embed1`、`嵌入实时流`、`嵌入视频文件`、`生成视频嵌入`、`视频搜索的文本嵌入`。

## 服务快照

- **VSS 3.2 GA 技能：** `vss-deploy-video-embedding`。
- **旧版 3.1 名称：** RT-Embed。
- **Compose 服务：** `rtvi-embed`。
- **容器名称：** `vss-rtvi-embed`。
- **镜像：** `nvcr.io/nvidia/vss-core/vss-rt-embed`（可使用 `RTVI_EMBED_IMAGE` 覆盖）。
- **默认标签：** `3.2.1`（可使用 `RTVI_EMBED_TAG` 覆盖）。
- **配置文件：** `bp_developer_search_2d`。
- **容器端口：** `8000`（主机端 `${RTVI_EMBED_PORT}`）。
- **默认模型：** 来自 `nvidia/Cosmos-Embed1-448p` 的 `cosmos-embed1-448p`。
- **健康检查端点：** `GET /v1/ready`。
- **健康检查启动宽限期：** 首次启动时为 `1200s`（20 分钟）。

## 前置条件

在启动服务之前：

1. 安装 NVIDIA 驱动程序 + NVIDIA 容器工具包；默认运行时设置为 `nvidia`。
2. Docker Engine 和 Docker Compose 插件版本足够支持 `${VAR:+value}` 条件卷替换。
3. 完成 `docker login nvcr.io`，使用 `$oauthtoken` 和有效的 NGC API 密钥。
4. 主机环境至少提供：`RTVI_EMBED_PORT`、`VSS_DATA_DIR`、`NGC_API_KEY`，以及可选的 `HF_TOKEN` 以避免 Hugging Face 429 速率限制错误（在下载 Cosmos-Embed1 权重时）。
5. 用于持久化缓存的磁盘空间：`rtvi-hf-cache`、`rtvi-ngc-model-cache`、`rtvi-triton-model-repo`（多 GB）。

有关完整前置条件列表，请参阅 `references/deploy-vss-deploy-video-embedding.md`；有关变量矩阵，请参阅 `references/environment.md`。

## 部署

对于 **独立 RT-Embed**，从服务目录开始：

```bash
cd "{{repo_root}}/deploy/docker/services/rtvi/rtvi-embed"
```

对于此独立部署，**不要**使用 `/vss-deploy-profile` 或 `scripts/dev-profile.sh`。

对于代理驱动的验证，**不要**让 `sudo` 提示交互式输入。在执行任何特权所有权或 Docker 操作之前，使用 [`references/deploy-vss-deploy-video-embedding.md`](references/deploy-vss-deploy-video-embedding.md) 和 [`references/troubleshooting.md`](references/troubleshooting.md) 中的非交互式保护：优先使用纯 `docker`；否则使用 `sudo -n docker`；如果 `sudo -n` 失败，请使用主机所有者的确切手动命令停止，而不是尝试交互式 sudo 或降低权限。

在 `docker compose up` 之前设置最小的独立环境。如果 `sudo -n chown` 失败，请在 `docker compose up` 之前停止，并要求主机所有者运行打印的命令。

```bash
export RTVI_EMBED_PORT=8017
export VSS_DATA_DIR="${VSS_DATA_DIR:-$(pwd)/.standalone-data}"
export NGC_API_KEY="<your-ngc-api-key>"
export HOST_IP="$(hostname -I | awk '{print $1}')"
export HF_TOKEN="${HF_TOKEN:-}"  # 可选，但建议避免 HF 429s
export RTVI_EMBED_KAFKA_ENABLED=false
export ENABLE_REDIS_ERROR_MESSAGES=false
# 准备 VST clip-storage 主机目录；使用 `sudo -n` 修复所有权。
CLIP_STORAGE_DIR="${VSS_DATA_DIR}/data_log/vst/clip_storage"
mkdir -p "$CLIP_STORAGE_DIR"
if ! sudo -n chown -R 1001:1001 "$CLIP_STORAGE_DIR"; then
  echo "ERROR: passwordless sudo is unavailable for host-path ownership." >&2
  echo "Ask the host owner to run: sudo chown -R 1001:1001 \"$CLIP_STORAGE_DIR\"" >&2
  echo "Do not work around this with chmod 777 or world-writable permissions." >&2
  return 1 2>/dev/null || exit 1
fi
```

这避免了当 `VSS_DATA_DIR` 未设置时从文件系统根目录挂载 `/data_log/vst/clip_storage`，并防止独立模式下因缺少 Kafka/Redis 对等节点而导致启动停滞。

```bash
# 在所需的 Compose 配置文件下启动服务。
docker compose -f rtvi-embed-docker-compose.yml \
  --profile bp_developer_search_2d up -d rtvi-embed
```

如果 Docker 需要提升权限，请使用 `sudo -n docker compose ...`，如果 `sudo -n` 报告需要密码，请快速失败。

```bash
# 在模型下载和 Triton 仓库构建期间查看日志。
docker compose -f rtvi-embed-docker-compose.yml logs -f rtvi-embed
```

首次启动启动可能需要 20 分钟来下载 Cosmos-Embed1 和构建 Triton 模型仓库。在首次启动期间不要缩短 `start_period: 1200s` 健康检查，否则容器将在预热期间被标记为不健康。

### 验证

```bash
BASE_URL="http://localhost:${RTVI_EMBED_PORT}"

curl -fsS "$BASE_URL/v1/ready"               # 热时返回 200。
curl -fsS "$BASE_URL/v1/ready?detailed=true" # 组件级状态。
curl -fsS "$BASE_URL/v1/version"
MODELS_JSON=$(curl -fsS "$BASE_URL/v1/models")
echo "$MODELS_JSON"                          # 确认 cosmos-embed1-448p 已加载。

MODEL_ID="$(echo "$MODELS_JSON" | jq -r '.data[0].id // empty')"
test -n "$MODEL_ID" || { echo "ERROR: /v1/models 没有模型 ID — 等待 /v1/ready 返回 200" >&2; exit 1; }
```

下文调用 API 的部分会重用此块中的 `$BASE_URL` 和 `$MODEL_ID`。

## 常见操作

### 从上传的文件生成视频嵌入

```bash
FILE_ID=$(curl -fsS -X POST "$BASE_URL/v1/files" \
  -F purpose=vision \
  -F media_type=video \
  -F file=@/path/to/clip.mp4 | jq -r .id)

curl -fsS -X POST "$BASE_URL/v1/generate_video_embeddings" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$FILE_ID\",
    \"model\": \"$MODEL_ID\",
    \"chunk_duration\": 60,
    \"chunk_overlap_duration\": 10
  }"
```

### 生成文本嵌入（用于文本到视频搜索）

```bash
curl -fsS -X POST "$BASE_URL/v1/generate_text_embeddings" \
  -H "Content-Type: application/json" \
  -d "{\"text_input\":\"a forklift moving pallets\",\"model\":\"${MODEL_ID}\"}"
```

### 嵌入实时 RTSP 流

实时流**必须**具有 `stream: true` 和 `chunk_duration > 0`。同步调用会返回 `400 BadParameters: "Only streaming output is supported for live-streams"`，而 `streams/add` 返回的 `chunk_duration: 0` 是占位符——必须在嵌入请求中覆盖它，否则会得到 `400 BadParameter: "chunk_duration must be greater than 0"`。

`POST /v1/streams/add` **不**按 `liveStreamUrl` 去重——提交相同的 URL 两次会生成两个不同的 `stream_id`。在添加之前，请调用 `GET /v1/streams/get-stream-info` 并重用任何现有的该 URL 注册，以避免出现孤立的条目。

```bash
STREAM_ID=$(curl -fsS -X POST "$BASE_URL/v1/streams/add" \
  -H "Content-Type: application/json" \
  -d '{"streams":[{"liveStreamUrl":"rtsp://host:port/live/video","description":"camera-001"}]}' \
  | jq -r '.results[0].id')

curl -N -X POST "$BASE_URL/v1/generate_video_embeddings" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d "{
    \"id\": \"$STREAM_ID\",
    \"model\": \"$MODEL_ID\",
    \"stream\": true,
    \"chunk_duration\": 10,
    \"chunk_overlap_duration\": 2
  }"

# 列出注册的实时流（用于跨会话恢复 stream_ids）。
curl -fsS "$BASE_URL/v1/streams/get-stream-info"

# 完成嵌入后停止嵌入（终止带有数据: [DONE] 的 SSE）。
curl -fsS -X DELETE "$BASE_URL/v1/generate_video_embeddings/$STREAM_ID"
```

有关完整端点目录、SSE 流式传输和单流控制平面模式，请参阅 `references/rest-api.md`。

## 日志、指标和状态

```bash
docker compose -f rtvi-embed-docker-compose.yml ps
docker compose -f rtvi-embed-docker-compose.yml logs -f rtvi-embed
docker stats vss-rtvi-embed

curl -fsS "$BASE_URL/v1/metrics"          # Prometheus。
curl -fsS "$BASE_URL/v1/assets/stats"     # 资产存储计数和 TTL。
```

如果 `RTVI_EMBED_LOG_DIR` 绑定到主机目录，日志文件也可在主机上的 `/opt/nvidia/rtvi/log/rtvi/` 查看。

## 集成界面

- **输入：** `:${RTVI_EMBED_PORT}` 上的 REST API（`POST /v1/files`、`POST /v1/generate_text_embeddings`、`POST /v1/generate_video_embeddings`、实时流控制端点）。
- **输出：** 同步 REST 响应、可选的用于分块视频嵌入的 SSE、可选的 Kafka 消息（当 Kafka 启用时，主题名称由 `RTVI_EMBED_KAFKA_TOPIC`（容器 `KAFKA_TOPIC`）和 `RTVI_EMBED_ERROR_MESSAGE_TOPIC`（容器 `ERROR_MESSAGE_TOPIC`）指定，主机：`RTVI_EMBED_KAFKA_ENABLED=true`，Compose 映射到容器 `KAFKA_ENABLED`）。
- **可选对等：** Redis（`ENABLE_REDIS_ERROR_MESSAGES=true`）、Kafka（主机：`RTVI_EMBED_KAFKA_ENABLED=true` → 容器 `KAFKA_ENABLED`）、OpenTelemetry 收集器（主机：`RTVI_EMBED_ENABLE_OTEL_MONITORING=true` → 容器 `ENABLE_OTEL_MONITORING`）。

`references/integrate-vss-deploy-video-embedding.md` 记录了完整的集成契约。

## 错误处理

API 失败返回带有 `code` 和 `message` 字段的 JSON：

```json
{
  "code": "BadParameter",
  "message": "chunk_duration must be greater than 0"
}
```

Pydantic / OpenAPI 验证失败使用 HTTP `422` 和 `code: "InvalidParameters"` 以及字段级 `message`。

| 代码 | 含义 | 常见原因 |
|------|-------|--------------|
| 400 | Bad Request | 缺少 `text_input`；未知的 `file_id` / `stream_id` / `model`；实时流调用时没有 `stream: true`；`chunk_duration: 0` 在实时流嵌入请求中；`chunk_overlap_duration >= chunk_duration` |
| 401 | Unauthorized | 缺少或无效的 `Authorization: Bearer <token>` 当部署强制执行认证时 |
| 403 | Forbidden | 禁用 `file://` URL（`FILE_URL_ALLOWED_DIRS` 未设置）或解析路径在允许列表之外（`code: "Forbidden"`） |
| 409 | Conflict | `DELETE /v1/files/{file_id}` 时文件正在使用中（`ResourceInUse`）；另一个客户端已连接到相同的实时流（`Conflict`） |
| 413 | Payload Too Large | 上传的文件或解码的 `data:` URI 超过服务器大小限制 |
| 422 | Unprocessable Entity | 模式验证失败——格式错误的 UUID、错误的 multipart 字段类型、无效的枚举值；不支持的方案的有效 URL 格式 |
| 429 | Rate Limited | 请求速率超过限制——使用指数退避重试 |
| 500 | Internal Server Error | 预测或 I/O 失败——检查 `docker compose -f rtvi-embed-docker-compose.yml logs -f rtvi-embed` |
| 503 | Service Unavailable | `/v1/ready` 仍在预热（模型下载 / Triton 仓库构建）；嵌入端点正忙于处理另一个文件或文本查询；达到最大实时流数量；推理期间 CUDA OOM |

**首次启动时 `/v1/ready` 出现 503 是预期的**，直到 Cosmos-Embed1 完成下载并构建 Triton 模型仓库（最多约 20 分钟）。在健康检查 `start_period: 1200s` 过期后，不要将其视为应用程序错误。

**嵌入端点出现 503** 并带有消息 `"Server is busy processing another file or text"` 或 `"Server is busy processing another file / live-stream."` 表示服务一次只处理一个同步嵌入任务——使用退避重试或跨实例分片工作。

有关端点特定约束（实时流 SSE 要求、URL 方案、响应模式），请参阅 [`references/rest-api.md`](references/rest-api.md)。有关 Compose 启动、缓存和权限失败，请参阅 [`references/troubleshooting.md`](references/troubleshooting.md)。

## 故障排除

有关常见失败模式和解决方案，请参阅 `references/troubleshooting.md`。频繁出现的问题：

- `/v1/ready` 卡在 503 → 检查缺少 `NGC_API_KEY`、首次启动时 Hugging Face 429 速率限制错误（设置 `HF_TOKEN` 以避免）、启用这些标志时 Redis/Kafka 对等节点无法到达。
- 健康检查在首次 20 分钟内切换为不健康 → 恢复 `start_period: 1200s`。
- 绑定挂载的缓存目录出现权限错误 → 在主机路径上使用 `sudo -n chown -R 1001:1001`；如果无法使用无密码 sudo，请要求主机所有者运行打印的命令（不要使用 `chmod 777`）。
- 部署期间出现 `sudo` 提示密码 → 使用 `sudo -n` 并快速失败；请参阅 `references/troubleshooting.md`；在代理会话中永远不要使用交互式 sudo 重试。

## 升级和回滚

固定 `RTVI_EMBED_IMAGE` / `RTVI_EMBED_TAG`，拉取，使用 `--profile bp_developer_search_2d` 重新创建，并在切换前等待 `/v1/ready`。命名卷在镜像交换时持续存在。

完整步骤：[升级和回滚](references/deploy-vss-deploy-video-embedding.md#upgrade--rollback)。

## 拆卸

使用 `docker compose -f rtvi-embed-docker-compose.yml down` 停止独立堆栈。仅在打算销毁命名模型缓存时才使用 `down -v`。

完整步骤和缓存警告：[拆卸](references/deploy-vss-deploy-video-embedding.md#tear-down)。

## 参考

| 文件 | 何时阅读 |
|---|---|
| [references/README.md](references/README.md) | 所有参考文件的目录。 |
| [references/deploy-vss-deploy-video-embedding.md](references/deploy-vss-deploy-video-embedding.md) | 构建 Vision Agent 部署参考：镜像、GPU、存储、启动、前置条件、已知问题。 |
| [references/integrate-vss-deploy-video-embedding.md](references/integrate-vss-deploy-video-embedding.md) | 构建 Vision Agent 集成参考：对等、输入/输出、环境变量、网络、示例 Compose 片段。 |
| [references/rest-api.md](references/rest-api.md) | 带有工作示例 `curl` 的完整 REST 端点目录，用于文件上传、视频/文本嵌入、实时流和健康/指标。 |
| [references/environment.md](references/environment.md) | 完整的环境变量矩阵，包括主机到容器的重命名和敏感于密钥的环境变量。 |
| [references/troubleshooting.md](references/troubleshooting.md) | 用于启动、模型/缓存、运行时和可观察性问题的操作诊断。 |
