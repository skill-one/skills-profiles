## 目的

使用用户选择的入口点、配置和校准，独立部署行为分析服务。

## 说明

请遵循以下路由表和分步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都应按从上到下的顺序执行。详细参考材料位于 `references/` 中。

## 示例

完整的端到端示例保存在 `evals/` 下（每个 `*.json` 配置文件包含一个可运行的场景）。运行 Tier-3 评估以重放它们：

```bash
nv-base validate skills/vss-setup-behavior-analytics --agent-eval
```

最小的独立启动看起来像：

```bash
cd $REPO/deploy/docker
export VSS_APPS_DIR=$(pwd)
docker compose -f services/analytics/behavior-analytics/compose.yml up -d vss-behavior-analytics-base
```

遵循 `references/deploy-behavior-analytics-service.md` 获取完整工作流程（入口点选择、配置源、动态更新）。

## 限制

- 需要部署匹配的 VSS 配置文件 / 微服务，并且可以从调用者处访问。
- NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：来自 NGC 的 HTTP 401/403。**原因**：缺少/过期的 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试之前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# VSS 设置行为分析 — 独立

仅部署 `vss-behavior-analytics` 容器（来自上游 `behavior-analytics` 仓库的空间 AI 分析管道），而不是作为完整仓库蓝图堆栈的一部分。

完整的操作演练——入口点表、配置源选项、校准类型、动态更新线协议、故障排除——是 [`references/deploy-behavior-analytics-service.md`](references/deploy-behavior-analytics-service.md)。此 SKILL.md 仅处理路由和先决条件。

## 何时使用

- "部署行为分析" / "独立运行行为分析"
- "我只想运行分析，而不是完整堆栈"
- "将入口点更改为 fusion_search / dev_example / analytics 3D / mv3dt"
- "使用我自己的行为分析配置 / 校准 JSON"
- "将行为分析指向仓库-3d（或 mv3dt）配置，而无需启动仓库配置文件的其余部分"
- "动态配置 / 动态校准到运行中的行为分析"

## 先决条件

1. **代码库检出**，`$VSS_APPS_DIR` 指向 `<repo>/deploy/docker/`。这是服务 compose 的卷绑定所必需的。
2. **NGC 凭据**——`$NGC_CLI_API_KEY` 设置，以便 docker 可以拉取镜像。参见 [`references/ngc-api-key-registry-login.md`](references/ngc-api-key-registry-login.md)。
3. **Docker 运行时**——Docker Engine **28.3.3** 与 Docker Compose 插件 **v2.39.1+**。使用 `docker --version` 和 `docker compose version` 进行验证。
4. **可选代理**（Kafka / Redis Streams / MQTT）。容器可以**不使用**代理正常启动——Kafka 客户端重试有限次数，然后应用程序退出，`restart: always` 循环容器。状态将在 `docker ps` 中显示为 `Restarting (N)`，直到代理可访问。使用代理，通过 `mdx-notification` 的动态配置 / 动态校准将变得可用。
5. **可选的磁盘上的配置 / 校准文件**，如果用户正在使用自己的。

如果任何必需的先决条件失败，请在继续之前暴露差距。

## 工作流程

将用户 [`references/deploy-behavior-analytics-service.md`](references/deploy-behavior-analytics-service.md) 交给他们，并按顺序引导他们完成其步骤：

1. 选择入口点（2D 分析 / 3D 分析 / mv3dt、dev_example、fusion_search）。
2. 选择配置——预装配置文件或自定义配置文件。
3. 选择校准——可选；预装配置文件或自定义配置文件；否则应用程序将等待动态校准通知。
4. 确定是否可达的代理；如果是，请将他们指向动态更新流程。

compose 文件编辑、YAML 差异、部署 + 验证命令和故障排除表都位于该参考中——不要在此处重复它们。

## 动态更新（运行时，无需重启）

容器启动**并且代理可达**后，两个运行时更新流程可用——两者都不需要重新部署：

### 动态配置

向 `mdx-notification` 主题发布 `upsert`（按键修补）或 `upsert-all`（完整快照）消息，Kafka 键为 `behavior-analytics-config`，并带有标头：

- `event.type`：`upsert` | `upsert-all` | `request-config` | `ack`
- `reference-id`：`video-analytics-api-<uuid>`（由 Web API 发起）、`behavior-analytics-<uuid>`（引导回复）或源类型字面量（`kafka` / `redis` / `mqtt`）用于直接发布者的 upsert。

正文：`{"status": ..., "config": <修补>, "error": ...}`。

监听器在每个消息的包层（拒绝未知键、缺少配置、格式不良的状态/错误）和每个有效载荷层（拒绝禁止部分、不良项目形状）进行验证。成功的 upsert 会被持久化到磁盘，应用于每个工作进程，并通过主题回执。

完整线协议 + 回执语义：[`references/dynamic-config.md`](references/dynamic-config.md)。

### 动态校准

向同一主题发布，Kafka 键为 `calibration`，并带有标头：

- `event.type`：`upsert-all`（完整快照）| `upsert`（按传感器合并）| `delete`（按传感器删除）
- `timestamp`：ISO-8601 UTC（`YYYY-MM-DDTHH:MM:SS.fffZ`）。

正文：JSON 传感器列表（以及 `upsert-all` 的 ROI / 三角线 / 单应性）。

监听器在持久化之前根据vendored AJV 草本进行验证。草本违规将记录 `calibration schema violation` 警告并丢弃——先前良好的校准将保持加载。

完整线协议 + 每个操作验证策略：[`references/dynamic-calibration.md`](references/dynamic-calibration.md)。

这两个流程完全在代理上运行——生产者可以是 `video-analytics-api`、您自己的脚本或任何镜像线形状的 Kafka 客户端。它们是在容器运行后更改配置的推荐方法，因此操作员不必重新部署。

## 路由规则

- 如果用户想要“完整堆栈”（UI / 代理 / 感知）：将他们交给 [`vss-deploy-profile`](../vss-deploy-profile/SKILL.md) 并使用配置文件 `warehouse`（或 `alerts`）。不要并行运行此技能。
- 如果用户想要向已运行的容器发布运行时配置 / 校准更新：引导 [动态更新](#dynamic-updates-runtime-no-restart) 部分。两个流程都需要一个可达的代理。
- 如果用户描述了他们想要验证的行为分析行为更改（新事件类型、新 ROI 规则、新传感器）：在编辑 JSON 之前，将他们指向 [`references/configuration.md`](references/configuration.md)、[`references/dynamic-config.md`](references/dynamic-config.md) 或 [`references/dynamic-calibration.md`](references/dynamic-calibration.md)。
