## 目的

独立部署 RT-VLM 密集式字幕微服务，并测试其暴露的每个端点（文件上传、generate_captions、流添加/删除、chat-completions、Kafka 主题）。

## 前置条件

对于独立 RT-VLM 部署：
- Docker、Docker Compose、NVIDIA 容器工具包和一个可访问的 GPU。
- `$NGC_CLI_API_KEY` 中的 NGC 注册凭证，用于 `docker login nvcr.io`、镜像拉取和本地 NGC 模型/工件下载。
- `curl`、`jq` 和任何可写入的工作目录，用于独立 compose 复制。

对于针对现有服务的 API 调用：
- 可达 `$BASE_URL` 的运行中 RT-VLM 服务。
- `$RTVI_VLM_API_KEY` 或 `$NGC_CLI_API_KEY` 中的 Bearer 令牌，具体取决于服务如何配置。

对于完整 VSS 配置文件部署：
- 使用 `../vss-deploy-profile/SKILL.md`；此技能不会部署完整 VSS 配置文件。

## 说明

遵循以下路由表和逐步工作流。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都旨在按顺序执行。详细参考材料位于 `references/`；除非未来版本命名了具体的辅助工具，否则直接执行文档中记录的工作流。

## 示例

端到端的工作示例保存在 `evals/` 下（每个 `*.json` 清单文件包含一个可运行的场景）和以下每个工作流的 `curl` 块中。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

## 限制

- 需要此技能部署的独立 RT-VLM 服务或可从调用者访问的现有 RT-VLM 服务。
- NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。
- 将 `NGC_CLI_API_KEY`、`RTVI_VLM_API_KEY` 和 `rtvi-vlm.env` 文件排除在 git 和日志之外；不要回显凭证值或在最终响应中包含它们。
- Docker 组访问和 `sudo` 实际上是 root 级别的权限。在部署参考中使用非交互式 `sudo -n` 保护，并在无密码 sudo 不可用时停止并要求主机所有者手动运行打印的命令。

## 故障排除

- **错误**：REST 调用返回连接拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：来自 NGC 拉取的 HTTP 401/403。**原因**：缺少/过期 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试之前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# 部署和使用 RT-VLM 密集式字幕（VSS 3.2）

RT-VLM 是 NVIDIA 的实时视觉语言微服务：解码视频（文件或 RTSP），将其分割成块，运行 VLM（`cosmos-reason1`、`cosmos-reason2`、`cosmos-reason3` 或任何 OpenAI 兼容模型），通过 SSE/HTTP 流式传输密集字幕，并将字幕、事件警报和错误发布到 Kafka。使用此技能在尚未运行完整 VSS 配置文件时部署独立的 RT-VLM 服务，然后调用其 `/v1/...` API 进行字幕生成、文件上传、实时流管理、健康检查、NIM 兼容的聊天完成或 Prometheus 指标。API 参考：<https://docs.nvidia.com/vss/latest/real-time-vlm-api.html>。

## 部署路由

如果用户要求部署完整 VSS 配置文件，请使用
[`../vss-deploy-profile/SKILL.md`](../vss-deploy-profile/SKILL.md)。该技能拥有配置文件路由、`generated.env`、`resolved.yml`、多服务尺寸和完整栈部署/拆除。

如果用户要求独立的 RT-VLM 密集式字幕，或尚未运行 VSS 配置文件，请在使用 API 之前使用
[`references/deploy-rt-vlm-service.md`](references/deploy-rt-vlm-service.md) 中的独立 RT-VLM 流程。这遵循与 `vss-deploy-profile` 相同的以 compose 为中心的模式：收集上下文、运行预检、从本地副本工作、使用 `docker compose config` 进行干运行、审查、部署，然后等待健康状态。

## 独立部署流程

始终遵循此顺序。切勿跳过干运行。

```bash
# 1. 将 deploy/docker/services/rtvi/rtvi-vlm/rtvi-vlm-docker-compose.yml
#    复制到任何可写入的独立工作目录。
# 2. 从该 compose 复本中派生 RTVI_VLM_IMAGE_TAG。
# 3. 从副本中删除仅限独立的悬空 depends_on 块。
# 4. 创建一个 git 忽略的 rtvi-vlm.env，其中包含所需的 RT-VLM 值。
# 5. 准备主机绑定路径，例如 $VSS_DATA_DIR/data_log/vst/clip_storage。
#    使用 `sudo -n` 进行所有权修复；如果无密码 sudo 不可用，
#    停止并要求主机所有者手动运行打印的命令。
# 6. docker compose --env-file rtvi-vlm.env -f rtvi-vlm-docker-compose.yml config --quiet
# 7. docker pull 确切的 RT-VLM 图像标签。
# 8. docker compose ... up -d rtvi-vlm，等待就绪，然后进行烟雾测试。
```

在任何拉取或 `up` 之前运行预检；在调试 RT-VLM 之前停止并修复这里的失败：

```bash
nvidia-smi --query-gpu=index,name --format=csv,noheader
nvidia-container-cli info
docker compose version
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

对于独立的单文件部署，不要直接运行原始
`deploy/docker/services/rtvi/rtvi-vlm/rtvi-vlm-docker-compose.yml`：它包含指向仅在完整 VSS/met-blueprints compose 项目中定义的兄弟 VLM/NIM 服务的 `depends_on` 引用。独立参考显示了如何复制 compose 文件、从它派生当前图像标签、删除 `depends_on` 块并在 `up` 之前验证结果。

对于代理驱动的验证，永远不要让 `sudo` 提示交互式。在任何特权所有权或 Docker 操作之前，在
[`references/deploy-rt-vlm-service.md`](references/deploy-rt-vlm-service.md) 中使用非交互式保护：
优先使用纯 `docker`；否则使用 `sudo -n docker`；如果 `sudo -n` 失败，停止并要求主机所有者提供确切的用于主机的手动命令，而不是尝试交互式 sudo 或减弱权限。

如果 `docker pull` 在 Docker 28+ 上因容器快照程序/解包错误失败，请在独立参考中应用 `/etc/docker/daemon.json` 的 `containerd-snapshotter=false` 修复，然后重试。

最小独立 `rtvi-vlm.env` 值：

| 主机环境变量 | 需要时 | 目的 |
|---|---|---|
| `NGC_CLI_API_KEY` | 独立部署路径 | NGC 注册库图像拉取和 NGC 模型/工件下载 |
| `RTVI_VLM_API_KEY` 或 `NGC_CLI_API_KEY` | 经过身份验证的 API 调用 | 服务运行后 RT-VLM 带宽认证 |
| `RTVI_VLM_PORT` | 始终 | 映射到容器 `8000` 的主机 API 端口 |
| `HOST_IP` | 始终 | Kafka 引导主机 (`${HOST_IP}:9092`) |
| `VSS_DATA_DIR` | 始终 | 需要的 clip-storage 绑定挂载 |
| `RTVI_VLM_MODEL_TO_USE` | 始终对于独立 | 后端选择器；使用 `cosmos-reason3` 用于默认本地模型或 `openai-compat` 用于远程/兄弟端点 |
| `RTVI_VLM_MODEL_PATH` | 本地自我托管模型 | 源支持的 Cosmos Reason3 Nano BF16 路径：`ngc:nim/nvidia/cosmos3-nano-reasoner:bf16-final` |
| `RTVI_VLM_ENDPOINT` | `RTVI_VLM_MODEL_TO_USE=openai-compat` | 远程/兄弟 OpenAI 兼容 VLM 端点 |
| `VLM_NAME` | `RTVI_VLM_MODEL_TO_USE=openai-compat` | 该端点暴露的模型/部署名称 |

## 设置

```bash
export BASE_URL="http://localhost:${RTVI_VLM_PORT:-8018}"  # 主机侧 RT-VLM 端口
export API_KEY="${NGC_CLI_API_KEY:-${RTVI_VLM_API_KEY:-}}" # 主机侧 curl 命令使用的带宽令牌
: "${API_KEY:?在调用经过身份验证的端点之前设置 NGC_CLI_API_KEY 或 RTVI_VLM_API_KEY}"
```

以下每个请求都使用 `Authorization: Bearer $API_KEY`。健康端点（`/v1/health/*`、`/v1/ready`、`/v1/live`、`/v1/startup`）通常无需身份验证即可工作。

**使用前进行烟雾测试：**
```bash
curl -fsS "$BASE_URL/v1/health/ready"
MODEL_ID="$(curl -fsS "$BASE_URL/v1/models" -H "Authorization: Bearer $API_KEY" | jq -r '.data[0].id // .id')"
curl -fsS "$BASE_URL/openapi.json" | jq -r '.paths | keys[]' | sort
```

## RTSP 示例流保护

当任务或评估命名 `RTSP_SAMPLE_URL` 时，将此确切的环境变量视为必需输入。在探测或注册任何流之前验证它已设置且非空；如果缺失，请停止并显示清晰的失败消息。不要从 NvStreamer、VIOS、样本数据包或任何其他回退中派生替代项，因为这将验证调用者请求的不同流。

```bash
: "${RTSP_SAMPLE_URL:?在 RTSP 验证之前将 RTSP_SAMPLE_URL 设置为可访问的 RTSP 示例流}"
case "$RTSP_SAMPLE_URL" in
  rtsp://*) ;;
  *) echo "RTSP_SAMPLE_URL 必须是 rtsp:// URL，得到： $RTSP_SAMPLE_URL" >&2; exit 1 ;;
esac

if command -v ffprobe >/dev/null 2>&1; then
  ffprobe -v error -rtsp_transport tcp \
    -select_streams v:0 -show_entries stream=codec_type \
    -of csv=p=0 "$RTSP_SAMPLE_URL" | grep -qx video
elif command -v gst-discoverer-1.0 >/dev/null 2>&1; then
  gst-discoverer-1.0 "$RTSP_SAMPLE_URL" | grep -qi 'video'
else
  echo "在 RTSP 验证之前安装 ffprobe 或 gst-discoverer-1.0。" >&2
  exit 1
fi
```

## 快速入门 — 来自本地视频的密集字幕

```bash
# 1. 上传视频，捕获其文件 ID
FILE_ID=$(curl -fsS -X POST "$BASE_URL/v1/files" \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@/path/to/warehouse.mp4" \
  -F "purpose=vision" \
  -F "media_type=video" | jq -r '.id')

# 2. 生成字幕 + 警报（分块响应的 SSE 流）
curl -N -X POST "$BASE_URL/v1/generate_captions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$FILE_ID\",
    \"prompt\": \"为这个仓库视频的每个 10 秒段写一个简洁的密集字幕。\",
    \"model\": \"$MODEL_ID\",
    \"chunk_duration\": 10,
    \"stream\": true
  }"
```

## API 表面

在调用可选端点之前，使用实时 OpenAPI 作为真实来源：

```bash
curl -fsS "$BASE_URL/openapi.json" | jq -r '.paths | keys[]' | sort
```

VSS 3.2 的核心路径是：

- `POST /v1/files` 用于多部分媒体上传；将返回的文件 `id` 传入字幕生成，并在完成后删除文件。
- `POST /v1/generate_captions` 用于文件或流字幕。使用 `GET /v1/models` 返回的确切模型 ID；别名（如 `cosmos-reason2` 或 `cosmos-reason3`）是后端选择器，不是请求模型 ID。
- `POST /v1/streams/add`、`GET /v1/streams/get-stream-info` 和
  `DELETE /v1/streams/delete/{stream_id}` 用于 RTSP 生命周期。从 `results[0].id` 解析流 ID。
- `POST /v1/chat/completions` 用于 OpenAI 兼容的文本和多模态调用。当前 26.05 构建的 `/v1/completions` 仅返回文本时返回 HTTP 400；在验证遗留行为时将其视为预期行为。
- `GET /v1/health/ready`、`/v1/models`、`/v1/assets/stats` 和 `/v1/metrics` 用于服务探测。除非 OpenAPI 列出它，否则不要假设 `/v1/license` 存在。

详细的端点模式、响应形状、CV 风格的单个流端点和 26.05 兼容性说明位于
[`references/api-surface-26.05.md`](references/api-surface-26.05.md)。

## 常见工作流

- 存储文件字幕：使用 `POST /v1/files` 上传，使用返回的文件 ID 调用
  `/v1/generate_captions`，使用 `stream=true` 进行 SSE，然后删除文件以释放存储。
- RTSP 实时字幕：当调用者提供 `RTSP_SAMPLE_URL` 时，使用该确切 URL 并在注册之前运行 **RTSP 示例流保护**。当 `RTSP_SAMPLE_URL` 为空时，不要从 NvStreamer 或 VIOS 派生替代流；快速失败。在注册之前需要实际视频流/字幕条目；添加流、字幕它，然后注销它。
- 警报提示：包含一个确定的 `Anomaly Detected: Yes/No` 行。Kafka 发布是服务器端配置，附加到 HTTP 响应，并在 [`references/kafka-workflows.md`](references/kafka-workflows.md) 中记录。
- Kafka 验证：信任实时 `vss-rtvi-vlm` 环境以获取主题名称。在完整的 VSS 警报实时配置文件中，使用现有的 VSS Kafka 容器 `mdx-kafka` 进行 CLI 检查和最终事件消费者命令。对于独立验证，使用宣传 `${HOST_IP}:9092` 的代理；永远不要停止或替换预存在的代理，除非用户确认。

## 错误参考

常见原因：400 表示无效的请求形状或模型 ID，401/403 表示缺少或错误的带宽令牌，404 表示已删除的文件/流或不支持的端点，413 表示上传过大，422 表示模式验证，429 表示并发量过多，500 表示推理/运行时失败，503 而在启动仍在进行中时。检查 `docker logs vss-rtvi-vlm` 以获取服务端失败。
