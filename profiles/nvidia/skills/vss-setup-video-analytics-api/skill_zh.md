## 目的

使用用户选择的配置、数据日志绑定以及 Elasticsearch / Kafka 连接独立部署 video-analytics-api REST 服务。

## 说明

请遵循下方的路由表和分步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都应按从上到下的顺序执行。详细的参考材料位于 `references/` 中。

## 示例

完整的端到端示例保存在 `evals/` 下（每个 `*.json` 清单文件包含一个可运行的场景）。运行 Tier-3 评估以重放它们：

```bash
nv-base validate skills/vss-setup-video-analytics-api --agent-eval
```

一个最小的独立启动看起来像：

```bash
cd $REPO/deploy/docker
export VSS_APPS_DIR=$(pwd)
export VSS_DATA_DIR=${VSS_DATA_DIR:-/tmp/vss-data}
mkdir -p "$VSS_DATA_DIR/data_log/vss_video_analytics_api"
docker compose -f services/analytics/video-analytics-api/compose.yml up -d vss-video-analytics-api
curl -sf http://localhost:8081/livez
```

有关完整工作流程（配置源、数据日志绑定、基础设施依赖项、REST 端点）的信息，请参阅 [`references/deploy-video-analytics-api-service.md`](references/deploy-video-analytics-api-service.md)。有关按字段划分的 JSON 配置参考，请参阅 [`references/configuration.md`](references/configuration.md)。

## 限制

- 需要部署匹配的 VSS 配置文件 / 微服务，并且可以从调用者访问。
- NGC 托管的模型和 NIM 可能会受到速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：来自 NGC 拉取的 HTTP 401/403。**原因**：缺少/过期 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试之前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# VSS 设置视频分析 API — 独立

仅部署 `vss-video-analytics-api` 容器（来自上游 `video-analytics-api` 仓库的 Node.js REST API），而不是作为完整仓库蓝图堆栈的一部分。

完整的操作演练——配置源选项、数据日志卷行为、基础设施依赖项、REST API 端点、部署 + 验证、故障排除——位于 [`references/deploy-video-analytics-api-service.md`](references/deploy-video-analytics-api-service.md)。按字段划分的 JSON 配置参考位于 [`references/configuration.md`](references/configuration.md)。此 SKILL.md 仅处理路由和先决条件。

## 何时使用

- "部署视频分析 api" / "独立运行视频-analytics-api"
- "我只想运行 REST API，而不是完整堆栈"
- "使用我自己的 video-analytics-api 配置"
- "将 API 指向不同的 Elasticsearch / Kafka"
- "无需 Kafka 启动 API" / "无代理运行 API"
- "查看有哪些 REST 端点可用"

## 先决条件

1. **代码库检出**，`$VSS_APPS_DIR` 指向 `<repo>/deploy/docker/`。这是服务 compose 的卷绑定所必需的。
2. **NGC 凭据**——`$NGC_CLI_API_KEY` 设置，以便 docker 可以拉取镜像。请参阅 [`references/ngc-api-key-registry-login.md`](references/ngc-api-key-registry-login.md)。

   > **安全处理 `NGC_CLI_API_KEY` 的注意**：此密钥是一个长寿命凭证，可以拉取您 NGC 组织中可用的所有 NVIDIA 私有镜像。切勿提交密钥，切勿将其粘贴到聊天中，切勿将其存储在 `/tmp` 中。交互式读取 (`read -rs NGC_CLI_API_KEY`) 或在部署时从您的密钥管理器（Vault、AWS Secrets Manager、sealed-secrets）中加载它。使用 `umask 077` + `chmod 600` 写入任何派生的 `.env` 文件，将它们添加到 `.gitignore` 中，并在定义的间隔和每次主机退役后旋转密钥。如果它曾经被暴露（主机快照、共享屏幕、工单附件），请立即旋转。
3. **Docker 运行时**——Docker Engine **28.3.3** 和 Docker Compose 插件 **v2.39.1+**。使用 `docker --version` 和 `docker compose version` 进行验证。
4. **Elasticsearch**——必须在 `elasticsearch.node` 中配置的 URL 上可访问。服务器在启动时会 ping ES；如果无法访问，它将退出（并且 `restart: always` 会将其重新启动）。如果您需要同时启动 ES，请使用 infra compose：`docker compose -f services/infra/compose.yml up -d elasticsearch`。
5. **可选的 Kafka 代理**。API 可以在没有 Kafka 的情况下运行。如果您想要一个安静的、无代理的部署，请使用图像烘焙的配置或带有 `kafka.brokers: []` 的自定义配置；服务提供的 compose 配置指向 `localhost:9092`，因此直到代理可访问，Kafka 相关功能（动态配置、动态校准、RTLS/AMR）将失败。
6. **`$VSS_DATA_DIR` 对于默认 compose**。基础 compose 绑定挂载 `$VSS_DATA_DIR/data_log/vss_video_analytics_api` 以处理多部分上传和文件支持的资源（例如校准图像）。将目录设置为可写的宿主机路径并预先创建它，或者如果不需要图像上传，则移除该挂载。

如果任何必需的先决条件失败，请在继续之前暴露差距。

## 工作流程

将用户 [`references/deploy-video-analytics-api-service.md`](references/deploy-video-analytics-api-service.md) 交给他们，并按顺序引导他们完成其步骤：

1. 选择配置——图像烘焙的默认值、服务提供的或自定义的。
2. 确定是否需要数据日志卷以进行文件上传。
3. 确认基础设施依赖项——Elasticsearch（必需）、Kafka（可选）。
4. 使用 `docker compose up` 和健康检查进行部署 + 验证。

compose 文件编辑、配置选项、部署 + 验证命令、REST API 端点表和故障排除表都位于该参考中——不要在此处重复它们。

## 端点参考

有关 REST 端点表和运行时依赖项说明，请使用 [`references/deploy-video-analytics-api-service.md`](references/deploy-video-analytics-api-service.md)。

## Kafka 相关功能（运行时，需要代理）

一旦容器启动**并且 Kafka 代理可访问**，就会提供三个附加功能：

### 动态配置

API 作为动态配置更新的**生产者**。当操作员 POST 到 `/config` 时，API 会向 `mdx-notification` 主题发布带有 Kafka 键 `behavior-analytics-config` 的 `upsert` 消息。下游的 `behavior-analytics` 容器消费此消息并返回 ACK。API 还处理引导流程——当 `behavior-analytics` 启动时，它会发布 `request-config` 消息，API 会回复 `upsert-all`，其中包含从 Elasticsearch 获取的最新验证配置。

消费者端验证、ACK 语义和完整线路合同在 `vss-setup-behavior-analytics` 动态配置参考中记录。

### 动态校准

API 在 `mdx-notification` 上发布校准更新通知，带有 Kafka 键 `calibration`。支持 `upsert-all`（完整快照）、`upsert`（每个传感器合并）和 `delete`（每个传感器删除）。下游的 `behavior-analytics` 容器消费这些消息并将它们应用于实时校准。

消费者端验证和按操作策略在 `vss-setup-behavior-analytics` 动态校准参考中记录。

### RTLS / AMR

API 从 Kafka 消费实时位置 (`mdx-rtls`) 和 AMR (`mdx-amr`) 消息，并通过 REST 端点公开它们。

## 路由规则

- 如果用户想要“完整堆栈”（UI / 代理 / 感知）：将其转交给 `vss-deploy-profile`，配置文件为 `warehouse`（或 `alerts`）。不要并行运行此技能。
- 如果用户想要部署分析管道（行为创建、事件检测）：将其转交给 `vss-setup-behavior-analytics`。
- 如果用户想要通过 REST API 发布运行时配置/校准更新：确认 Kafka 可访问，然后使用 `/config` 或校准端点，并将它们指向行为分析动态更新参考以供消费者线路合同。
- 如果用户想要了解动态配置/动态校准线路合同从**消费者**（行为分析）侧：将他们指向 `vss-setup-behavior-analytics` 动态配置和动态校准参考。
- 如果用户想要查询或与 REST API 端点交互：部署参考端点表涵盖了可用内容。有关完整的 OpenAPI 规范，请参阅 `video-analytics-api` 仓库中的 `src/app/specification/openapi.json`。
