## 目的

将 RTVI-CV-3D 微服务作为 MV3DT（`MODE=mv3dt`）部署和运行——即单摄像头的 DeepStream 感知加上多台校准摄像头的 BEV 融合——在捆绑的样本数据集、自定义视频或实时 RTSP 上，而无需完整的仓库代理 / LLM / VLM 堆栈。

## 说明

自上而下操作：回答 [路由](#路由) 下的路由问题（Q0–Q3），然后按照所选路径的参考进行操作。详细的分步程序位于 `references/`（部署、校准链、摄像头配置、验证、拆除、故障排除）。

## 示例

- 在样本数据集上启用多摄像头跟踪。
- 将 RTVI-CV-3D 部署到我的视频：`<path/to/videos>`。
- 校准后，在 RTSP 流上运行 MV3DT。

# VSS 部署检测与跟踪 — 3D (RTVI-CV-3D / MV3DT)

从仓库蓝图启动 RTVI-CV-3D 微服务作为 MV3DT 堆栈（`MODE=mv3dt`）：单摄像头 DeepStream 感知（`vss-rtvi-cv-mv3dt`）+ BEV 融合（`vss-rtvi-cv-bev-fusion`）+ mosquitto MQTT 总线 + 中继器 + VST 传感器堆栈——而无需与完整仓库蓝图一起提供的代理 / LLM / VLM 堆栈。

实际的 compose 机制位于 `deploy/docker/industry-profiles/warehouse-operations/warehouse-mv3dt-app/`。这项技能驱动环境覆盖、校准链和验证。

## 路由

最多向用户提出四个问题，然后进行分派。

### Q0 — 配置大小（是否显示覆盖层）

默认为 **扩展**，除非用户明确要求最小。扩展部署在 MV3DT 核心上添加 ELK + `vss-video-analytics-api-mv3dt` + `vss-kibana-init-mv3dt` + `vss-import-calibration-output-mv3dt`——这些是 VST 视频墙需要渲染边界框覆盖层的内容。没有它们，视频墙可以工作，但会显示原始流而没有覆盖层。

| 用户回答 | `MINIMAL_PROFILE` | 您将获得的内容 | 选择何时 |
|---|---|---|---|
| **扩展**（默认） | `""` | MV3DT 核心加上 ELK + 分析 API + Kibana。**VST 视频墙中的覆盖层可以工作。** 推荐用于完整的端到端体验。 | "我想获得完整的端到端体验"、"我想看到边界框"，或未声明偏好 |
| **最小** | `"true"` | 仅 MV3DT 核心。约 5 个更少的容器。**VST 中没有覆盖层。** 元数据仍然在 Kafka/Redis 上。 | "我只需要数据"、"边缘 / Thor 主机"、"最小占用空间" |

> **关于选择性 ELK 的注意**：当前 compose 中没有 "最小 + ELK 仅" 的中间路径。每个 `${MINIMAL_PROFILE:+_extended}`-门控的服务一起启动（ES、Logstash、Kibana、video-analytics-api、kibana-init、import-calibration）。`bash` 的 `:+` 参数扩展在 `MINIMAL_PROFILE` 设置时产生 `_extended` 后缀；扩展将门控字符串切换回普通的 `bp_wh_kafka_mv3dt`，而活动 compose 配置文件已经匹配。要么接受完整的扩展捆绑包，要么保持最小。

### Q1 — 数据源

除非用户的第一条消息中明确说明来源，否则才询问此问题。像 "部署 rtvi-cv-3d" 这样的简单请求会路由到此 MV3DT 技能（`MODE=mv3dt`），但**不**意味着 `sample`。

- **sample** — 捆绑的 4 摄像头合成数据集（`warehouse-4cams-20mx20m-synthetic`）。校准随树提供；无需 AMC 运行。
- **videos** — 用户有本地视频文件（任何 `*.mp4` 都以他们的摄像头命名）。如果缺少校准，将运行独立的 AMC（`auto_calib` 配置文件）。
- **rtsp** — 用户有实时 RTSP URL。通过 VIOS 驱动的 AMC 进行校准；最终部署还需要一个传感器信息文件（`camera_info.json`）包含这些 RTSP URL。

### Q2 — 校准覆盖范围（`sample` 跳过）

对于 `videos` 和 `rtsp`，检查感知容器期望的挂载路径上是否已经存在校准：

```bash
DATASET="${SAMPLE_VIDEO_DATASET:?}"          # 用户的 dataset slug；见 Q3
CAL_DIR="${VSS_APPS_DIR}/industry-profiles/warehouse-operations/warehouse-mv3dt-app/calibration/sample-data/${DATASET}"

# 查找任何一种：calibration.json，以及 camInfo/*.yml 或 *.yaml，其中包含 'cam_*' 或 'Camera*' 命名（随附的样本使用 Camera*.yml，AMC 可能产生 cam_*.yaml — 适当扩展）
test -f "${CAL_DIR}/calibration.json" \
  && ls "${CAL_DIR}/camInfo/"*.{yml,yaml} 2>/dev/null
```

如果用户自己提供了校准路径，请验证该路径——不要重新计算。有关摄像头名称规范和权威摄像头数量发现的详细信息，请参阅 `configure-cameras.md`（解析 `calibration.json`）。

### Q3 — 检测器 + 数据集 slug（仅当 Q2 触发 AMC 时）

- `resnet`（默认，快速）或 `transformer`（较慢，遮挡下更好）——传递给 AMC `/v1/calibrate/<id>` API 在步骤 B（见 `vss-generate-video-calibration/SKILL.md:48-62`）。
- 一个短的小写破折号连接的 dataset slug 用作 `SAMPLE_VIDEO_DATASET`（例如 `customer-aisle-4cams`）。这驱动校准挂载路径，并持久保存在 `.env` 中。

### 路由表

| Q1 | Q2 结果 | 路径 |
|---|---|---|
| `sample` | (校准随树提供且已规范化) | [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) 直接 |
| `videos` | 校准存在 | [`references/configure-cameras.md`](references/configure-cameras.md) → [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) |
| `videos` | 校准缺失 | [`references/calibration-workflow.md`](references/calibration-workflow.md)（videos 模式）→ [`references/configure-cameras.md`](references/configure-cameras.md) → [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) |
| `rtsp` | 校准存在 | [`references/configure-cameras.md`](references/configure-cameras.md) → [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) |
| `rtsp` | 校准缺失 | [`references/calibration-workflow.md`](references/calibration-workflow.md)（rtsp 模式）→ [`references/configure-cameras.md`](references/configure-cameras.md) → [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) |

每条路径在 `up -d` 完成后都会汇聚到 [`references/verify-and-view.md`](references/verify-and-view.md)。[`references/troubleshooting.md`](references/troubleshooting.md) 和 [`references/teardown.md`](references/teardown.md) 是链接的，但不在快乐路径上。

**歧义规则。** 在此技能中，"RTVI-CV-3D" 指的是 MV3DT 微服务部署并使用 `MODE=mv3dt`。仅在用户要求完整仓库蓝图、Sparse4D、`MODE=3d` 或 `warehouse-3d-app` 时才路由到 [`../vss-deploy-profile/references/warehouse.md`](../vss-deploy-profile/references/warehouse.md)。此技能仅用于 **MV3DT**，不包括代理堆栈 / LLM / VLM。

## 前置条件

### 1. 仓库路径

在磁盘上找到 `video-search-and-summarization/`。所有 compose 命令都从 `<repo>/deploy/docker/` 运行。如果未知，请询问用户。

### 2. NGC CLI + 密钥

`$NGC_CLI_API_KEY` 必须设置，并且必须可以访问 `nvidia/vss-core/*` 镜像。如果缺失，请参阅 `vss-deploy-profile/references/ngc.md` 进行设置。

如果用户之前运行了 `ngc config set`，但 `$NGC_CLI_API_KEY` 在此 shell 中未导出，则密钥已经存在于磁盘上：

```bash
NGC_CLI_API_KEY=$(awk -F'= ' '/^apikey/{print $2}' ~/.ngc/config 2>/dev/null)
test -n "${NGC_CLI_API_KEY}" && echo "key sourced from ~/.ngc/config"
```

确保密钥值也出现在 `industry-profiles/warehouse-operations/.env:164`（`NGC_CLI_API_KEY=...`）—— compose 仅在 `up` 时代码读取它，而不是从您的 shell 环境中读取。

### 3. `HARDWARE_PROFILE` slug

> 公开的 MV3DT 支持的流数量列在仓库快速入门指南的 "MV3DT 视觉 AI 配置文件支持部署选项" 下。使用下面匹配的 `HARDWARE_PROFILE` slug。

从 `nvidia-smi --query-gpu=name --format=csv,noheader` 中选择：

| GPU 名称 | `HARDWARE_PROFILE` | MV3DT 支持的流 |
|---|---|---|
| RTX PRO 6000 Blackwell | `RTXPRO6000BW` | 18 |
| H100 (NVL, SXM HBM3) | `H100` | 13 |
| L40S | `L40S` | 7 |
| IGX Thor | `IGX-THOR` | 4 |
| DGX Spark | `DGX-SPARK` | 4 |

如果用户的 GPU 未列在此处，请检查 `industry-profiles/warehouse-operations/.env` 中可用的 `HARDWARE_PROFILE` 值，然后在使用它之前确认匹配的配置文件存在于 `blueprint_configurator/blueprint_config.yml` 中。不要仅根据 slug 推断流数量。

**每个 GPU 的 MV3DT 限制在部署时强制执行。** `vss-configurator-mv3dt` 计算 `final_stream_count = min(NUM_STREAMS, max_streams_supported)` 并对 `${VSS_DATA_DIR}/videos/${SAMPLE_VIDEO_DATASET}/` 应用 `keep_count` 文件管理操作，以便仅保留 `final_stream_count` 个 `.mp4` 文件（按字典顺序排序，保留最后 N 个）。如果您的 GPU 的 MV3DT 支持流数量（上表）低于您的摄像头数量，感知 / `mdx-raw` / `mdx-bev` 将以支持的流数量运行。要么选择一个支持更高流数量的 GPU，要么向用户明确显示限制，以便他们知道哪些流将被处理。

### 4. 磁盘上的应用数据

`VSS_DATA_DIR` 必须指向**提取的 `vss-warehouse-app-data` 目录**（与仓库分开）。将其指向仓库的 `deploy/docker/` 会导致部署停滞：配置器找不到数据集，redis 无法打开其日志文件，感知仍然处于 `Created` 状态。在部署前验证路径。

部署前的预检：

```bash
DATA_DIR="${VSS_DATA_DIR:?VSS_DATA_DIR not set in .env}"
DATASET="${SAMPLE_VIDEO_DATASET:-warehouse-4cams-20mx20m-synthetic}"

for sub in videos models data_log; do
  test -d "${DATA_DIR}/${sub}" || { echo "ERROR: ${DATA_DIR}/${sub} missing"; exit 1; }
done

# 对于 sample / videos 模式——视频目录必须存在
test -d "${DATA_DIR}/videos/${DATASET}" \
  || { echo "ERROR: ${DATA_DIR}/videos/${DATASET} missing — wrong slug or app-data not extracted"; exit 1; }

# 常识：视频计数应与校准计数匹配。
# 一些已发布的 app-data tarball 知道样本数据集的视频数量少于数据集名称暗示的数量——验证并单独源任何缺失的摄像头
ls "${DATA_DIR}/videos/${DATASET}/"*.mp4 2>/dev/null | wc -l

# 确保数据日志/下每个服务子目录都存在。kafka / elasticsearch /
# redis / postgres 和视频分析 API 上传路径（`/web-api-app/files`）
# 作为非 root UIDs 运行针对这些绑定挂载。没有写权限，守护进程或校准/图像导入可能会因权限错误而失败。
mkdir -p \
  "${DATA_DIR}/data_log/analytics_cache" \
  "${DATA_DIR}/data_log/calibration_toolkit" \
  "${DATA_DIR}/data_log/elastic/data" \
  "${DATA_DIR}/data_log/elastic/logs" \
  "${DATA_DIR}/data_log/kafka" \
  "${DATA_DIR}/data_log/redis/data" \
  "${DATA_DIR}/data_log/redis/log" \
  "${DATA_DIR}/data_log/vss_video_analytics_api"

# 仅授予特定容器 UIDs 的写权限——范围 ACL，不是 777，也不是 chown。UID（per data-directory.md）：postgres=70, redis=999, elasticsearch / VST /
# kafka=1000。第一次调用涵盖现有文件；第二次设置*默认* ACL，以便守护进程在运行时（例如 postgres PGDATA）创建的文件/目录继承访问权限。
ACL='u:70:rwx,u:999:rwx,u:1000:rwx'
setfacl -R    -m "$ACL" "${DATA_DIR}/data_log"
setfacl -R -d -m "$ACL" "${DATA_DIR}/data_log"
```

> **范围 ACL，不是 `chmod 777`。** 这仅授予已知容器 UIDs 访问权限——它**不会**使 `data_log` 世
> 界可写，并且它**不会** `chown`（这会破坏 postgres / Elasticsearch，因为它们在首次启动时重新拥有自己的目录）。对于代理驱动运行和共享主机，请优先使用此方法。规范
> [`../vss-deploy-profile/references/data-directory.md`](../vss-deploy-profile/references/data-directory.md)
> 记录了广泛的 `chmod -R 777` 和每个容器的 UID 表；此技能使用范围 ACL 的等效方法。**在更改主机权限之前，请向用户确认。**
>
> 需要 POSIX-ACL 文件系统（ext4 / xfs — 默认的）和 `acl` 软件包（`setfacl`）。如果守护进程在部署后仍然记录权限错误，请找到其 UID
> (`docker inspect <container> --format '{{.Config.User}}'`) 并将 `-m u:<uid>:rwx` 添加到两个调用中。

如果应用数据尚未提取：通过 `ngc registry resource download-version "nvidia/vss-warehouse/vss-warehouse-app-data:<version>"` 下载，然后 `tar -xvf`（参考 [`references/deploy-rtvi-cv-3d-stack.md`](references/deploy-rtvi-cv-3d-stack.md) 获取标签和完整步骤）。

### 5. 预飞检（系统）

`nvidia-smi`、NVIDIA Docker 运行时可见（`docker info | grep -i runtimes`），以及 `docker run --rm --gpus all ubuntu:24.04 nvidia-smi` 都显示绿色。完整的驱动程序 / 内核 / sysctl 检查位于 `vss-deploy-profile/references/prerequisites.md`。

如果任何检查失败，请在继续之前修复——不要继续部署。

### 6. 浏览器可达性（云 / 企业 VPN 主机仅限）

如果用户将通过不同网络上的浏览器（云虚拟机、企业 VPN、ssh-tunnelled 会话）查看 VST 视频墙，则上游防火墙规则可能会阻止 VST WebRTC（STUN 到 `stun.l.google.com:19302`，加上随机 UDP 用于媒体）。参考 [`references/verify-and-view.md#browser-reachability`](references/verify-and-view.md) 了解症状和解决方案。另外：一些主机会阻止 AMC 微服务的默认端口（TCP/8010）；如果用户报告 AMC UI 在 `:5000` 上工作，但其数据调用失败，请尝试使用不同的 `VSS_AUTO_CALIBRATION_PORT`。

## 故障排除

当任何部署、校准或验证步骤失败时，在重试之前停止并分类失败。以下快速检查涵盖了最常见的 MV3DT 错误；使用 [`references/troubleshooting.md`](references/troubleshooting.md) 获取完整的诊断命令和修复，使用 [`../vss-generate-video-calibration/SKILL.md`](../vss-generate-video-calibration/SKILL.md) 获取 AMC 工作流故障，使用 [`../vss-deploy-profile/references/warehouse-debug.md`](../vss-deploy-profile/references/warehouse-debug.md) 获取更广泛的仓库堆栈问题。

| 症状 | 可能的原因 | 首次检查或修复 |
|---|---|---|
| `vss-rtvi-cv-bev-fusion` 不健康或 `/tmp/fusion_ready` 缺失 | 中继器未准备好、`MAX_EXPECTED_SENSORS` 不匹配，或 `STREAM_TYPE` 不匹配 | 检查 `broker-health-check`，`docker inspect --format '{{.State.Health.Status}}' vss-rtvi-cv-bev-fusion`，以及 `mdx-raw` / `mdx-bev`；如果流计数不同，则重新运行 [`references/configure-cameras.md`](references/configure-cameras.md) |
| 感知显示 `Active sources : 0`、无 FPS 或预期摄像头更少 | 过时的 VST 传感器状态、错误的 dataset slug、缺少校准或每 GPU 流限制 | 验证 `SAMPLE_VIDEO_DATASET`、`NUM_STREAMS`、`camInfo/` 和 VST 传感器列表；如果保留旧传感器，请遵循 [`references/teardown.md`](references/teardown.md) 重新部署前 |
| `vss-rtvi-cv-mv3dt` 以 `MqttCommunicator` "无效节点" 或 tracker 提交失败退出 | 视频、`calibration.json` 和 `camInfo/` 中的摄像头名称与 `Camera`、`Camera_01`，... 的约定不匹配 | 与 [`references/configure-cameras.md`](references/configure-cameras.md) Step 0 一起规范化所有摄像头名称，然后清除过时的 VST 状态并重新部署 |
| AMC 项目创建、上传、校准或 MV3DT 导出失败 | AutoMagicCalib 服务/API 问题在此 MV3DT 部署路径之外 | 使用 [`../vss-generate-video-calibration/SKILL.md`](../vss-generate-video-calibration/SKILL.md) 部署/调试 AMC，然后在导出成功后返回到 [`references/calibration-workflow.md`](references/calibration-workflow.md) |
| `vss-behavior-analytics-mv3dt` 以校准模式验证错误重启 | AMC 导出具有空的 `group`、`region` 或 `place` 字段 | 应用 [`references/calibration-workflow.md`](references/calibration-workflow.md) Step 4a 中的占位符补丁，或在导出前填充 AMC 中的这些字段 |
| 扩展配置没有覆盖层，`vss-import-calibration-output-mv3dt` 记录 `imageMetadata.json not found` | AMC MV3DT 导出未生成 `images/Top.png` 和 `images/imageMetadata.json` | 使用 [`references/calibration-workflow.md`](references/calibration-workflow.md) Step 4b 合成这两个文件，然后重新启动一次性导入器 |
| 图像拉取、模型加载或首次启动引擎构建失败 | 缺失/过期的 `NGC_CLI_API_KEY`、不正确的 `VSS_DATA_DIR`、缺少 BodyPose3DNet 文件或 GPU OOM | 重新检查 NGC 认证，确认 `${VSS_DATA_DIR}/models/mv3dt/BodyPose3DNet/`，以及 `vss-rtvi-cv-mv3dt` 日志的尾部，如果 GPU 被耗尽，请释放或更改 `RT_CV_DEVICE_ID` |

在破坏性恢复（`docker compose down -v`、清除 `data_log`、删除 VST 传感器状态或更改主机 ACLs）之前，解释影响并获取用户确认。在执行状态重置更改之前，捕获失败的命令、相关的 `.env` 值、`docker compose ps` 和最后一个容器日志。

## 它们如何组合在一起

```
SKILL.md (此文件 — Q0/Q1/Q2/Q3 路由)
  └─ 如果校准缺失 ─> calibration-workflow.md
  │                     └─ 链接到 vss-generate-video-calibration (部署 + 驱动 API)
  │                     └─ 获取 /v1/result/{project_id}/mv3dt_result?result_type=amc（启用细化时还包括 vggt）
  │                     └─ 将校准文件放置在 warehouse-mv3dt-app/calibration/sample-data/<slug>/
  ├─> configure-cameras.md (摄像头名称规范化、NUM_STREAMS 同步、VST 传感器修剪)
  └─> deploy-rtvi-cv-3d-stack.md (使用 bp_wh_kafka_mv3dt + 扩展/最小值 compose up)
        └─> verify-and-view.md (FPS、fusion_ready、mdx-bev、VST 视频墙 + WebRTC 检查)
```

## 相关技能

- [`vss-generate-video-calibration`](../vss-generate-video-calibration/SKILL.md) — AMC 技能。拥有 AMC 部署、RTSP 捕获、校准 API 和此技能消耗的 `/v1/result/.../mv3dt_result` 导出挂钩。`calibration-workflow.md` 链接到它。
- [`vss-deploy-profile`](../vss-deploy-profile/SKILL.md) — 跨配置文件总括。当用户想要完整仓库蓝图（包括代理 / LLM / VLM）时，请使用那个而不是 MV3DT。
- [`vss-manage-video-io-storage`](../vss-manage-video-io-storage/SKILL.md) — VIOS / VST API 技能。对于 VST 视频墙（覆盖可视化）和 `configure-cameras.md` 中引用的传感器管理很有用。

仓库的权威仓库蓝图参考位于 [`../vss-deploy-profile/references/warehouse.md`](../vss-deploy-profile/references/warehouse.md) 中，涵盖了 2D / 3D / MV3DT 在完整仓库堆栈内部——此技能是 **MV3DT 仅** 的配套，修剪了代理 / LLM / VLM 层。
