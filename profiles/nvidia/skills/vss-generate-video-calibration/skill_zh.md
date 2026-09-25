## 目的

在本地文件、RTSP 流或捆绑的样本数据集上端到端运行 AutoMagicCalib，并在需要时部署 AMC 微服务。

## 说明

遵循下方的路由表和分步工作流程。以 *workflow*、*quick start* 或 *flow* 结尾的每个部分都意图按顶到底执行。详细参考材料位于 `references/`；仅加载所选输入模式所需的参考材料。

## 示例

完成的端到端示例保存在 `evals/` 下（每个 `*.json` 清单包含一个可运行的场景），并在每个工作流程的 `curl` 块中内联提供。使用 `nv-base validate <this-skill-dir> --agent-eval` 运行 Tier-3 评估以重放它们。

## 限制

- 需要部署匹配的 VSS 配置文件 / 微服务，并且可以从调用者访问。
- NGC 托管的模型和 NIM 可能受速率限制、GPU 内存要求和许可证限制的影响。
- 并发性、GPU 内存和存储限制取决于主机硬件和配置文件的 compose 文件。

## 故障排除

- **错误**：REST 调用返回连接被拒绝。**原因**：目标微服务未运行。**解决方案**：探测 `/docs` 或 `/health`；通过 `vss-deploy-profile` 或匹配的 `vss-deploy-*` 技能重新部署。
- **错误**：来自 NGC 的 HTTP 401/403。**原因**：缺少/过期的 `NGC_CLI_API_KEY`。**解决方案**：`docker login nvcr.io` 并在重试之前重新导出密钥。
- **错误**：容器 OOM 或模型加载失败。**原因**：所选配置文件的 GPU 内存不足。**解决方案**：切换到较小的变体或通过 `docker compose down` 释放 GPU。

# VSS 生成视频校准

在三种输入源之一上运行 AutoMagicCalib，并通过微服务 REST API 驱动校准。输入分辨率工作因源而异；从 `verify_project` 开始的所有内容都是相同的，并位于此文件中。选择正确的输入模式参考，并将其与下方的 [共享校准尾](#shared-calibration-tail) 配对。

仅在需要时加载共享辅助参考：
- 当模式参考需要共享 `create_project`、视频上传或交接片段时，读取 [`references/common-steps.md`](references/common-steps.md)。
- 当您需要可重用的 Python 实现的验证 → 校准 → 汇报 → 结果尾时，读取 [`references/calibration-tail.md`](references/calibration-tail.md)。

## 输入路由

将用户请求匹配到模式，然后加载该模式的参考以收集输入、模式特定 API 调用和完整的 Python 脚本。

| 用户说 / 拥有 | 模式 | 参考 |
|---|---|---|
| "启动 AMC" / "部署自动校准" / "设置 auto-magic-calib" / "启动 AMC 微服务" | `deploy` | [`references/deploy-auto-calibration-service.md`](references/deploy-auto-calibration-service.md) |
| "校准我的视频" / "从视频文件校准" / 本地 `cam_*.mp4` 文件 | `videos` | [`references/videos.md`](references/videos.md) |
| "校准 RTSP 流" / "从实时摄像头校准" / 实时 RTSP URL | `rtsp` | [`references/rtsp.md`](references/rtsp.md) |
| "测试样本数据集" / "验证 AMC 安装" / "启动并测试" | `sample-dataset` | [`references/sample-dataset.md`](references/sample-dataset.md) |

**歧义规则**：如果用户要求启动 / 部署 / 设置 AMC（没有校准动词）→ `deploy`。如果他们提供 RTSP URL → `rtsp`。如果他们提到本地文件 / 视频目录 → `videos`。如果他们要求验证安装或测试捆绑的样本 → `sample-dataset`。组合意图（例如 "启动 AMC 并校准我的视频"）→ 首先执行 `deploy`，然后执行校准模式。当存在歧义时，通过 `AskUserQuestion` 询问。

## 前提条件（跨校准模式共享）

- AMC 微服务 + UI 正在运行。如果不是，请首先执行 [`references/deploy-auto-calibration-service.md`](references/deploy-auto-calibration-service.md)。
- 微服务可在 `http://<HOST_IP>:${VSS_AUTO_CALIBRATION_PORT:-8010}/v1/ready` 处访问 → `{"code":0,...}`。
- 项目目录可由容器用户写入。如果您没有刚刚部署（因此部署参考的步骤 5 尚未运行），请确认部署参考 [`references/deploy-auto-calibration-service.md` § 步骤 5](references/deploy-auto-calibration-service.md#step-5--confirm-the-projects-directory-is-writable) 中的写入测试——否则第一个 `create_project` 返回 `[Errno 13] Permission denied`。
- 安装 Python 3 并带有 `requests`（每个输入模式参考都包括用于直接运行的自我修复 venv 回退）。

特定模式的先决条件（VIOS for `rtsp`、样本 zip for `sample-dataset`）位于相应的参考中。

## 共享校准尾

无论输入模式如何，验证 → 校准 → 汇报 → 结果序列都是相同的。在模式特定参考上传视频 / 摄取 RTSP 片段 / 上传捆绑样本后，运行此尾。使用 [`references/calibration-tail.md`](references/calibration-tail.md) 获取共享的 Python 片段。

### 步骤 A — 验证项目

```
POST /v1/verify_project/<project_id>
```

响应：`{"project_state": "READY"}`——必须在校准之前为 `READY`。如果不是 READY，请重新检查视频 + 对齐 + 布局是否存在（通过 API 或通过 UI 手动对齐）。

### 步骤 B — 开始校准

**在校准之前确认计划。** 无论设置文件和检测器是自动检测还是询问，都应通过 `AskUserQuestion` 在 `POST /calibrate` 之前显示简短摘要并确认。解析的值是默认值，因此确认只需单击一次——但用户可以切换检测器或跳过自动检测的设置文件。总结：

- **检测器**—— `resnet` 或 `transformer`（要发送的值）。
- **校准设置**——正在应用的文件（路径），或默认参数（可以先在 UI 中调整——见下文）。
- **可选覆盖**——如果有的话，地面真实 zip 和焦距。

样本数据集安装检查运行使用固定的 `resnet`，并且可以在没有此确认的情况下进行。

```
POST /v1/calibrate/<project_id>
Content-Type: application/json

{"detector_type": "resnet"}   # 或 "transformer"
```

`detector_type` 是 `/calibrate` 的单独参数——**不是** 由 `/v1/config/<id>` 消耗的。如果用户提供了一个校准设置文件，请解析它以获取 `"detector"` / `"detector_type"` 并使用该值。如果文件未指定，则默认值 (`resnet`) 是上述确认中显示的值——用户可以在校准之前切换它。如果没有设置文件，则通过 `AskUserQuestion` 询问用户：

- `resnet`——默认，快速。
- `transformer`——较慢，在严重遮挡下表现更好。

UI 步骤 3（参数）**不**涵盖检测器选择；永远不要假设用户在 UI 中选择了其中一个。

**当没有设置文件时，询问是否要先调整校准参数** (`AskUserQuestion`)：

- **使用默认参数继续**——适用于典型的仓库场景；如果不打算进行特定调整，则推荐。
- **先在 UI 中调整参数**——打开项目，转到步骤 3：参数，更改值，然后点击保存；然后继续。

等待用户的选择——如果他们选择调整，请等待他们确认已保存——然后调用 `/calibrate`。

### 步骤 C — 汇报完成

```
GET /v1/get_project_info/<project_id>
```

每 10 秒汇报一次。`project_info.project_state`：

| 状态 | 含义 |
|---|---|
| `RUNNING` | 校准正在进行中 |
| `COMPLETED` | 已完成 |
| `ERROR` | 失败——通过 `GET /v1/amc/calibrate/<id>/log` 查看日志 |

校准开始时，显示项目 ID、UI URL (`http://<HOST_IP>:${VSS_AUTO_CALIBRATION_UI_PORT:-5000}`) 和日志端点，以便用户可以在运行时查看进度。在 `RUNNING` 期间，至少每分钟发出一条进度行，以免长时间运行看起来停滞不前。在 `ERROR` 时，获取并显示 `GET /v1/amc/calibrate/<id>/log` 的最后几行，然后停止。实时日志也可以通过 `GET /v1/calibrate/<project_id>/log/<type>/stream` 流式传输。

典型时间：**10–60 分钟**（您自己的视频），**10–30 分钟**（捆绑样本）。

### 步骤 D — 结果

```
GET /v1/get_project_info/<project_id>                    # 项目状态
GET /v1/result/<project_id>/evaluation_statistics        # 仅当上传了 GT 时
GET /v1/result/<project_id>/overlay_image                # 视觉覆盖（PNG）
GET /v1/amc/calibrate/<project_id>/log                   # 校准日志
```

评估响应包括 `Average L2 distance(m)` 和 `Average reprojection error 0(px)`。评估指标仅在上传了地面真实 `GT.zip` 时生成——否则缺少 `evaluation_statistics` 结果是正常的，并且不是结果报告的结束。

在 `COMPLETED` 后，始终为该项目提供一种方式来查看结果，无论是否存在指标：

- **UI**——`http://<HOST_IP>:${VSS_AUTO_CALIBRATION_UI_PORT:-5000}`；打开项目，然后转到结果页面查看覆盖。
- **磁盘上的覆盖图像**——`${VSS_APPS_DIR}/services/auto-calibration/projects/project_<id>/output/multi_view_results/BA_output/results_ba_scaled_world/overlay_img_*.png`（单摄像头项目使用 `output/single_view_results/cam_00/verification_map_overlay.png`）。
- **项目文件**——`${VSS_APPS_DIR}/services/auto-calibration/projects/project_<id>/`。

### 步骤 E — VGGT 精炼

AMC 运行完成后，始终检查项目信息中的 `vggt_state`。VGGT 模型部署是可选的，并且不得阻塞 AMC 结果，但 AMC 后处理遵循以下状态：

- 如果 `vggt_state == "READY"` 并且用户明确请求 VGGT 精炼或在此次设置流程中部署了 VGGT，则无需再次询问即可运行 VGGT 精炼。
- 如果 `vggt_state == "READY"` 但 VGGT 在此请求之前已经部署，并且用户尚未请求 VGGT 精炼输出，则通过 `AskUserQuestion` 询问是否在开始之前运行精炼。
- 如果 VGGT 未准备就绪，则跳过精炼，并提及在部署模型后可以提供 VGGT 精炼（见 [`references/deploy-auto-calibration-service.md`](references/deploy-auto-calibration-service.md) 步骤 2）。

```
POST /v1/vggt/calibrate/<project_id>
GET  /v1/get_project_info/<project_id>                    # 汇报 vggt_state
GET  /v1/vggt_results/<project_id>/evaluation_statistics  # VGGT 指标
```

## 设置文件 + 检测器模式

在所有三种模式下都是可选的。当用户提供一个 JSON 设置文件（通常从 UI 步骤 3 下载）时，按原样 POST 它：

```
POST /v1/config/<project_id>
Content-Type: application/json

<file contents, posted as-is>
```

该文件将替换用户原本会在 UI 步骤 3 中调整的内容（校正、bundle-adjustment、评估旋钮、检测器等）。成功 POST 后，**还**解析文件以获取 `"detector"` / `"detector_type"`——如果它是 `"resnet"` 或 `"transformer"`，则使用该值用于步骤 B 中的 `/calibrate` 调用（检测器是单独的 API 参数，不是由 `/config` 消耗的）。

非 2xx 会显示出来——不要无声地回退。如果用户选择了 UI 回退路径，请完全跳过此调用。

## UI 回退模式

当对齐 / 布局文件不在磁盘上时，将用户引导到适当的 AMC UI 步骤：

- **设置缺失**→ "打开 UI 项目 `<project_id>`，转到 **步骤 3：参数**，通过设置对话框调整（或接受默认值），点击保存。" **也**：在 `/calibrate` 调用之前，通过 `AskUserQuestion` 询问用户是否要使用 `resnet` 或 `transformer` 检测器——步骤 3 不涵盖检测器选择。
- **布局缺失**→ "打开 UI 项目 `<project_id>`，转到 **步骤 2：视频配置**，仅上传 `layout.png`（不要重新上传视频——它们已经通过 API/RTSP 附着），点击保存。"
- **对齐缺失**→ "打开 UI 项目 `<project_id>`，转到 **步骤 4：对齐**，要么上传 `alignment_data.json`，要么在布局上标记对应点，点击保存。"

等待用户确认。对于对齐/布局，在对继续之前验证磁盘上是否存在：

```bash
# 项目状态位于 $VSS_APPS_DIR/services/auto-calibration/projects
# （MS 容器在
#  deploy/docker/services/auto-calibration/ms/compose.yml
# 中绑定的路径）。
HOST_PROJECTS="${VSS_APPS_DIR}/services/auto-calibration/projects"

ls "$HOST_PROJECTS/project_<project_id>/manual_adjustment/"
# 预期：alignment_data.json, layout.png
```

## 成功标准

- 轮询后 `project_state == "COMPLETED"`。
- 如果使用手动对齐：`${VSS_APPS_DIR}/services/auto-calibration/projects/project_<id>/manual_adjustment/` 包含 `alignment_data.json` + `layout.png`。
- 如果上传了 GT：评估返回典型阈值（您的数据 `Average L2 distance(m)` < 1.5，`Average reprojection error 0(px)` < 5；捆绑样本 < 10）。
- 没有 `ERROR` 状态。

## 关键输出文件

在 `${VSS_APPS_DIR}/services/auto-calibration/projects/project_<project_id>/` 下：

```
project_<project_id>/
├── manual_adjustment/
│   ├── alignment_data.json
│   └── layout.png
├── output/
│   ├── single_view_results/cam_XX/
│   │   ├── camInfo_hyper_XX.yaml
│   │   └── trajDump_Stream_0_3d.txt
│   ├── multi_view_results/BA_output/results_ba/
│   │   ├── initial/camInfo_XX.yaml
│   │   └── refined/camInfo_XX.yaml          # ← 最终校准
│   └── multi_view_results/BA_output/results_ba_scaled_world/
│       └── overlay_img_XX.png               # ← 用于审查的视觉覆盖
└── calibration.log
```

## 跨越性故障排除

特定模式的故障排除位于每个参考自己的故障排除表中。

| 问题 | 解决方案 |
|---|---|
| `verify_project` 状态不是 `READY` | 确认视频已上传/摄取，并且对齐 + 布局存在（通过 API 或通过 UI 手动对齐）。参考中的模式特定上传步骤。 |
| UI 步骤后缺少手动对齐文件 | 用户未点击保存；还请确认 `${VSS_APPS_DIR}/services/auto-calibration/projects/project_<id>/manual_adjustment/` 是否存在。 |
| 校准卡在 `RUNNING` > 90 分钟 | `GET /v1/amc/calibrate/<id>/log`——通常是因为跟踪点不足（场景太静态）。见根 `README.md` 中的“自定义数据集”指南。 |
| 立即 `ERROR` 状态 | 检查视频命名：必须是 `cam_00.mp4`、`cam_01.mp4`、… 连续（视频模式）/ 摄像头名称标签（RTSP 模式）。 |
| 低 L2 但高重投影 | 在输入上传期间提供显式的 `focal_length` 覆盖（见视频 / RTSP 参考）。 |
| VGGT `INIT`，从未 `READY` | VGGT 模型未加载——见 [`references/deploy-auto-calibration-service.md`](references/deploy-auto-calibration-service.md) 步骤 2。 |
| 上传超时 | 大视频——将 `timeout=300` 提高到例如 `600` 在每个模式的 Python 脚本中。 |
| 端口扫描找不到后端 | 后端未运行——首先执行 [`references/deploy-auto-calibration-service.md`](references/deploy-auto-calibration-service.md)。 |

## 下游技能——MV3DT 导出

下游消费者（例如由另一个团队拥有的 Multi-View 3D Tracking 技能）直接从微服务获取 MV3DT 格式的校准输出。此技能返回 `project_id`；下游技能调用：

```
GET /v1/result/{project_id}/mv3dt_result?result_type=amc
# 响应：application/zip — mv3dt_output.zip 包含 transforms.yml
```

对于 VGGT 精炼输出（仅当 VGGT 运行到 `COMPLETED` 时可用，见步骤 E）：

```
GET /v1/result/{project_id}/mv3dt_result?result_type=vggt
# 响应：application/zip — vggt_mv3dt_output.zip
```

下游技能流程：
1. 使用用户的输入调用此技能；捕获打印的 `project_id`。
2. 等待技能返回（它内部轮询直到 `COMPLETED`）。
3. `GET /v1/result/{project_id}/mv3dt_result?result_type=amc`——将 ZIP 本地保存。
4. 如果 VGGT 也运行了，可以选择获取 `?result_type=vggt` 以获取精炼的 MV3DT。

## 相关技能

- [`vss-manage-video-io-storage`](../vss-manage-video-io-storage/SKILL.md) — VIOS API 技能；只有 `rtsp` 校准模式依赖于 VIOS 可达。

根 `README.md` "自定义数据集" 和 "校准工作流 (UI)" 部分记录了输入视频指南和此 API 流的 UI 驱动替代方案。
