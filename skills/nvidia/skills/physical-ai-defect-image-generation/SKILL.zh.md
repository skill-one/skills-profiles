---
name: physical-ai-defect-image-generation
description: '当用户希望在OSMO上使用NVIDIA Cosmos AnomalyGen（源自Cosmos-Predict2）对PCBA、金属表面和玻璃进行缺陷图像生成时使用。Day 0路径处理冷启动，包括USD到ROI的转换、图像编辑增强以及AnomalyGen创建初始PCBA数据集。Day 1路径对真实图像进行推理和标注。此技能有助于首次资产设置、微调检查点创建以及部署配置。


  触发关键词：缺陷图像生成、dig工作流、dig管道、缺陷图像检测工作流、aoi管道、aoi异常生成、usd2roi异常生成、day 0 pcba、day 1 pcba、day 1真实图像对齐、day 1手动ROI、金属表面异常、玻璃缺陷、异常生成微调、setup_pcb、setup_metal、setup_glass、setup_pretrained、dig设置、dig数据集、dig预训练检查点、dig图像编辑端点、cosmos缺陷生成、cosmos-predict2缺陷、cosmos-anomalygen、cosmos predict2微调。'
---

# 物理AI缺陷图像生成

## 目录

- [支持的工作流](#supported-flows)
- [消歧](#disambiguation-handle-vague-requests-before-committing)（完整表格位于 `references/disambiguation.md`）
- [步骤 0：选择工作流、参考手册并收集输入](#step-0-select-flow-cookbook-and-gather-inputs)
- [通用前置条件](#common-preconditions-all-flows)（详细版位于 `references/preconditions.md`）
- [工作流详解](#flow-walkthroughs)（每种工作流一个条目；详细信息位于 `references/flows/`）
- [OSMO 监控](#osmo-monitoring)
- [辅助文件](#supporting-files)

针对 AOI（自动光学检测）数据集的缺陷图像生成、增强和标注流程的端到端编排。**AnomalyGen = 针对每种用例微调的 Cosmos-Predict2-2B**（Cosmos-AnomalyGen-PCB-2B、-Metal-2B、-Glass-2B）。每种工作流在 `assets/configs/` 中都有一个规范的 OSMO 工作流 YAML，可非交互式地串联所有步骤。`assets/cookbooks/` 中的用例参考手册提供了 PCBA 的 usd2roi/image-edit 配置，以及 PCBA、金属表面和玻璃检测的 AnomalyGen 训练配置。本技能管控工作流选择、数据交接和提交命令；各组件的内部细节位于对应组件的 `SKILL.md` 中。

## 支持的工作流

| 工作流 | 入口点 | OSMO YAML | 步骤 | 用例 |
|------|-------------|-----------|-------|-----------|
| **第 0 天 — 纹理缺陷** | CAD 场景 USD（`pcba_target.yaml` 随参考手册提供） | `texture_defect_generation_day0.yaml` | usd2roi（scan_grid + 按单元 ROI 裁剪）→ image-edit 增强（`nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL`）→ 微调或直通 → 推理（anomalygen 内联标签，**包括元件缺失**） | PCBA |
| **第 0 天 — 正常图像** *(usd2roi + Image-Edit)* | CAD 场景 USD + 按板卡的 `pcba_target.yaml` / `day0_image.yaml` / `day0_crop.yaml` | `good_image_generation.yaml` | usd2roi-render（scan_grid + 按单元 ROI 裁剪）→ Qwen Image-Edit（OVSL2SL 外观迁移） | PCBA 正常图像集（ChangeNet 黄金半部分、微调正样本、真实照片配对） |
| **第 0 天 — 结构缺陷** | CAD 场景 USD + 按板卡的 `pcba_target.yaml` | `structural_defect_generation.yaml` | isaac-render（位姿缺陷：位移 / 墓碑 / 侧翻）+ 按元件裁剪（单 pod）→ Qwen Image-Edit（OVSL2SL 光照迁移；保留位姿几何） | PCBA 位姿缺陷集；ChangeNet 缺陷半部分 |
| **第 1 天 — 推理 + 标签（真实照片对齐，默认）** | CAD 导出的 USD + 真实 PCBA 照片（两者均位于 `datasets/pcb/assets` 中） | `texture_defect_generation_day1_real_alignment.yaml` | usd2roi 第 1 天渲染 → MI 配准 → 按 ROI 裁剪 → yq-render 配置 → 微调或直通 → 推理（anomalygen 内联标签） | **默认 PCBA 第 1 天。** 任意 usd2roi 支持的板卡的原始 AOI 截图 |
| **第 1 天 — 推理 + 标签（手动 ROI）** | 预采集的正常图像 + ROI 掩码（NGC 工件或用户上传） | `texture_defect_generation_day1_manual_roi.yaml` | yq-render 配置 → 微调或直通 → 推理（anomalygen 内联标签） | 金属表面、玻璃（无 USD/真实照片工作流）；PCBA **仅在用户明确要求** 进行预采集 ROI 实验时 |
| **仅微调** | 带标签的异常 URL 工件 | `finetune.yaml` | yq-render 配置 → 微调（validate_dataset → prep_testcase → torchrun） | 任何用例；生成第 0 天或第 1 天的检查点。需要 `<dig_url_root>/datasets/<usecase>/raw` 下的原始训练数据（参见 `assets/configs/setup/setup_<usecase>.yaml`）。 |

所有工作流均在 OSMO 上运行。第 0 天工作流需要 `image_edit_endpoint`（Qwen Image-Edit OVSL2SL — 现有 URL 或来自 `references/nim/` 的本地部署）；仅微调工作流无外部端点。

### 为用户的缺陷类型选择合适的 工作流

| 缺陷类型 | 工作流 | 机制 |
|---|---|---|
| 正常 / 良好 / 扫描网格 / `normal_img + cad_mask` 配对 | `good_image_generation.yaml` | usd2roi-render + Qwen Image-Edit |
| 纹理缺陷（桥接、划痕、变色）**且 元件缺失**（由 AnomalyGen 原生处理，非结构类） | `texture_defect_generation_day0.yaml` | Qwen Image-Edit + AnomalyGen AMP/SDG |
| 结构 / 位姿缺陷（墓碑、位移、侧翻） | `structural_defect_generation.yaml` | IsaacSim 位姿扰动 |
| 第 1 天在真实图像上的推理 + 标签 | `texture_defect_generation_day1_real_alignment.yaml`（PCBA 默认）或 `texture_defect_generation_day1_manual_roi.yaml`（金属/玻璃；仅当用户明确要求预采集 ROI / 跳过对齐时用于 PCBA） | usd2roi 第 1 天配准（真实对齐）或直接推理（手动 ROI） |

ChangeNet 黄金/缺陷配对：使用相同的 `--set name=` 提交 `good_image_generation.yaml` + `structural_defect_generation.yaml`（双提交配对惯例）。

> **第 0 天和第 1 天共享相同的下游结构**：一个由 Jinja 控制的 `finetune-job`（当 `use_pretrained_checkpoint=true` 时省略），供 `anomaly-infer` 使用。第 0 天在开头添加 `usd2roi-render` + `augment-image-edit`；第 1 天从 `<dig_url_root>/datasets/<usecase>/raw` 开始。每阶段细节：参见各工作流的详解。

### 用户意图 → 旋钮映射

**所有 OV 工作流均为两阶段**：`crop_max_emit=N` 限制*最终*按单元裁剪（阶段 2）；`render_patches=N` 限制*原始*扫描网格补丁（阶段 1，每个产生多个裁剪）。**不要自动映射“生成 N 张图像” → `render_patches=N`**（阶段错误）。`structural_defect_generation.yaml` 中不存在 `crop_max_emit`（每个元件一个裁剪 — 使用 `render_patches`），`texture_defect_generation_day1_real_alignment.yaml` 中也不存在（通过参考手册的 `crop.classes` 白名单进行过滤）。完整的旋钮表格、冒烟测试配方、默认值、注意事项：`references/knob_mapping.md`。

### 结构缺陷尺寸（不存在 `crop_max_emit` 旋钮）

结构输出与 `render_patches` 呈**非线性关系** — 帧数翻倍增加约 1.6–1.7 倍裁剪，而非 2 倍。不要使用 `crop_max_emit`（无效）或 `render_patches=0`（会失败）。经验证的产出表格 + 目标尺寸公式：`references/flows/structural_defect_generation.md` §“输出尺寸”。对于模糊的“生成 N 张图像”，通过 `AskUserQuestion` 显示校准表格。

---

## 消歧：在提交前处理模糊请求

未明确指定的提示词（“给我生成一些图像”、“运行 PCBA 工作流”、“给我缺陷”）**不得**通过静默假设工作流 / 用例 / 旋钮映射来解决。当意图模糊时，暂停并通过 `AskUserQuestion`（2–4 个互斥选项）展示候选解释，然后再提交。消歧关键选择：**哪个工作流、哪个用例、数量指哪个阶段、微调还是直通**。

不应消歧的既定默认值：PCBA 第 1 天 → 真实对齐；板卡 → `0603_H100`；image-edit 端点 → 本地集群服务（`references/nim/`）；`use_pretrained_checkpoint=true`；第 1 天真实对齐 `default_spatial_dependency=cad`（仅在 CAD 掩码不可用时回退到 `free`，参见 `references/flows/texture_defect_generation_day1_real_alignment.md`）。

**`dig_url_root` 是唯一例外 — 无静默默认值。** 首次（无内存条目）时，必须在任何提交 / `osmo data upload` / `preflight_urls.sh` 之前通过 `AskUserQuestion` 引导获取。`s3://osmo-workflows/dig` 是一个*待确认的建议*，绝不自动选择（约 80 GB+ 将存储于此）。后续运行可静默复用记忆中的值。参见步骤 0 + 内存规则（§4）。

**完整触发表格、提示词构建、以及何时*不*询问的例外情况：`references/disambiguation.md`** — 在为任何模糊请求组装 `AskUserQuestion` 选项前必须加载。

---

## 步骤 0：选择工作流、参考手册并收集输入

**在此步骤之前**，如果请求模糊（例如“给我生成图像”、“运行 PCBA 工作流”、“给我缺陷”），暂停并运行上述消歧速查表 — 通过 `AskUserQuestion` 展示候选解释并让用户选择。不要自动选择用户未实际选择的关键默认值。

### 首次门槛

如果该用户的内存中没有条目，在任何预检 / `osmo` / `kubectl` / `osmo data upload` 之前，通过*一次* `AskUserQuestion` 调用询问提前偏好问题，保存到内存（§4），然后继续。打包内容：

- **`dig_url_root`** — 必须引导获取，不可自动选择。提供 `s3://osmo-workflows/dig` 作为可确认的建议；否则用户提供自己的 OSMO 支持存储前缀。约 80 GB+ 将存储于此。除回忆之前确认的值（内存回忆）外无替代方案。
- **默认 OSMO `--pool`** — 来自 `osmo profile list` → `pool.accessible` 的候选。
- **Pod 模板确认** — 仅当 `osmo config show POD_TEMPLATE` 返回 403 时（§2 有确切问题）。
- **Image-edit 端点** — 仅第 0 天：选项 A（现有 URL）对比 选项 B（部署本地 NIM）。

后续对话静默地从内存中读取这些设置。按工作流的选择（用例、检查点 vs 微调、板卡、旋钮）每次都会询问 — 见下文。

### 预检顺序（首次门槛后）

运行 §1 `preflight_credentials.sh` → §2 `preflight_pod_template.sh` → §3 `preflight_urls.sh <flow> <usecase>` → §4 生成运行戳记。**频率**：§1 和 §2 是每次对话一次的门槛，具有跨对话内存缓存（参见 `references/preconditions.md` §4a）— 当内存记录它们已验证 / 用户确认时跳过。§3 在每次提交前运行（按工作流而异）。§4 是代理的工作 — 每次提交使用新的 `$STAMP`。

Pod 模板强制执行分两层：提交前 `preflight_pod_template.sh` 门槛（§2）加上每个 OV + 训练任务在 Pod 内的运行时预检（当缺少 `/usr/share/nvidia/nvoptix.bin` 或 `/dev/shm` < 16 GiB 时快速失败）。§2 通过但运行时失败 → 模板被修补 → 路由到 `physical-ai-infrastructure-setup-and-resilient-scaling`。缺少凭据 / URL 工件 → 建议先提交 `setup/setup_<case>.yaml` + `setup/setup_pretrained.yaml`。

然后在一个消息中询问用户 — 仅按工作流的选择（上述首次门槛已涵盖 `dig_url_root`、池、Pod 模板和端点偏好；从内存中提取这些）：

1. **用例** — PCBA（使用第 0 天 + PCB 参考手册）、金属表面（第 1 天 + 金属表面参考手册）、玻璃（第 1 天 + 玻璃参考手册），还是自定义？
2. **检查点可用吗？** — 如果是（`use_pretrained_checkpoint=true`），使用 `<dig_url_root>/models/<usecase>` 并提供 `checkpoint_step`。如果否，从 `<dig_url_root>/datasets/<usecase>/raw` 微调。
3. **本地 NIM 池容量检查**（仅第 0 天选项 B）— 在 `kubectl apply` 之前，通过 `physical-ai-infrastructure-setup-and-resilient-scaling` 检查 `Total Capacity`。`Total Capacity < 2` 无法同时托管 NIM + DIG → 询问用户添加 GPU 或切换到选项 A。`image_edit_model` 始终是 `nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL`，绝不用通用的 `qwen-image-edit`。
4. **将用户偏好保存到内存** — 在首次门槛之后（以及在任何偏离文档默认值的提交之后），持久化关键选择（`dig_url_root`、OSMO 池、默认板卡、image-edit 端点、Pod 模板状态、osmo-admin 角色）。**绝不保存** `image_edit_model`（常量 — 保存会导致漂移）或临时状态（STAMP、一次性 `anomaly_types_json`）。完整表格：**`references/preconditions.md` §4a “内存规则”**。在每次新对话开始时读取相关内存并静默应用。

在询问前查看相关的工作流参考 — 大多数值都有合理的默认值。第 1 天路由：PCBA 默认为 `real_alignment`；金属/玻璃无 USD 工作流，因此始终为 `manual_roi`；除非用户明确要求跳过对齐，否则不要询问用户 PCBA 是“手动还是真实对齐？”

---

## 通用前置条件（所有工作流）

快速参考。详细版：`references/preconditions.md`。

1. **OSMO 凭据 + 令牌** — 每次对话一次。**如果工作区中存在 `.env`，首先 source 它**（`set -a; . ./.env; set +a`）以导出 `HF_TOKEN`。运行 `scripts/preflight_credentials.sh`；权威检查是 OSMO 凭据 `hf-token` 已配置（图像在 `nvcr.io/nvidia/` 上是公开的 — 不需要注册表凭据）。在受限出口的外壳中传递 `--no-probe`。参见 `references/preconditions.md` §1。
2. **Pod 模板** — 每次对话一次，具有跨对话内存缓存（参见步骤 0 §6）。当内存记录集群已验证 / 用户确认 / 409 跳过时跳过。否则运行 `scripts/preflight_pod_template.sh` 并根据退出码分支（0=已验证 / 1=通过基础设施技能修补 / 2=询问用户（HTTP 403） / 3=跳过（HTTP 409） / 4=环境修复）。`references/preconditions.md` §2 中有完整的分支说明和提示词。
3. **必需的 URL 工件** — 每次提交前。运行 `DIG_URL_ROOT=<dig_url_root> scripts/preflight_urls.sh <flow> <usecase> [variant]`。如果缺少任何内容，**停止并先提交相关的 `setup/setup_<case>.yaml` + `setup/setup_pretrained.yaml`**（OSMO 设置工作流）— 参见 `references/setup.md`。**切勿本地下载资源来绕过问题；如果设置在凭据上失败，请用户更正并重新提交到 OSMO。** 按工作流检查清单：

   | 工作流 | 用例 | `<dig_url_root>` 下必需的 URL 工件 |
   |---|---|---|
   | 第 0 天 — 纹理缺陷 | PCBA | `models/pretrained`, `models/pcb`, `datasets/pcb/raw`, `datasets/pcb/assets` |
   | 第 0 天 — 正常图像 | PCBA | 仅 `datasets/pcb/assets` |
   | 第 0 天 — 结构缺陷 | PCBA | 仅 `datasets/pcb/assets` |
   | 第 1 天 | 金属表面 | `models/pretrained`, `models/metal_surface`, `datasets/metal_surface/raw` |
   | 第 1 天 | 玻璃 | `models/pretrained`, `models/glass`, `datasets/glass/raw` |
   | 第 1 天 真实照片对齐 | PCBA | 第 1 天 PCBA 加上 `datasets/pcb/assets` |
   | 仅微调 | 任何 | `models/pretrained`, `datasets/<usecase>/raw` |

   内置的 `usecase` 值为 `pcb`、`metal_surface`、`glass`。参见 `references/preconditions.md` §3。

4. **名称戳记** — 在每次提交前重新生成 `$STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)` 并传递 `--set name=<flow>-$STAMP`。生产 YAML 不提供 `name` 默认值。参见 `references/preconditions.md` §4。
5. **玻璃用例（UC3）— Roboflow zip** — 仅用于 `setup_glass.yaml`。首先将 `mobile_screen.zip` 上传到 OSMO URL 前缀；传递 `--set uc3_zip_url_root=<prefix>`。完整过程：`references/setup.md` §“玻璃用例（UC3）”。

---

## 工作流详解

每种工作流的完整详解 — 组图表、前置条件、提交命令变体、数据交接、按阶段故障排查 — 位于 `references/flows/` 下。代理应在提交当前对话中未运行过的任何工作流之前读取匹配的文件。

| 工作流 | 工作流 YAML | 详解 |
|---|---|---|
| **第 0 天 — 纹理缺陷（PCBA）** | `assets/configs/texture_defect_generation_day0.yaml` | `references/flows/texture_defect_generation_day0.md` |
| **第 0 天 — 正常图像（PCBA）** | `assets/configs/good_image_generation.yaml` | `references/flows/good_image_generation.md` |
| **第 0 天 — 结构缺陷（PCBA）** | `assets/configs/structural_defect_generation.yaml` | `references/flows/structural_defect_generation.md` |
| **第 1 天 — 推理 + 标签（真实照片对齐，默认 PCBA）** | `assets/configs/texture_defect_generation_day1_real_alignment.yaml` | `references/flows/texture_defect_generation_day1_real_alignment.md` |
| **第 1 天 — 推理 + 标签（手动 ROI，金属/玻璃 + PCBA 实验）** | `assets/configs/texture_defect_generation_day1_manual_roi.yaml` | `references/flows/texture_defect_generation_day1_manual_roi.md` |
| **仅微调** | `assets/configs/finetune.yaml` | `references/flows/finetune.md` |

### 跨工作流不变量

- `use_pretrained_checkpoint=true`（默认）→ 对`models/<usecase>`进行passthrough。设置为`false`以在 Pod 内插入`finetune-job`组（cookbook yq-patched Pod 内，无预提交渲染步骤）。
- 第 0 天发出每个细胞的`crop/<MATERIAL>/<cell>/...`树；第 1 天发出与 USD 注册的每个 ROI 作物；结构发出扁平的每个组件作物。
- 按用例分发的`checkpoint_step` + `anomaly_types_json`默认值：参见`references/preconditions.md` §"分发的检查点和`anomaly_types_json`默认值"。

---

## OSMO 监控

**在执行任何此技能中的`osmo workflow submit`、`osmo workflow query`或`osmo workflow logs`操作之前，加载`references/monitoring.md`。** 它定义了轮询频率、任务状态解释、日志拉取升级阈值、故障分类路由，以及向用户展示的内容与静默重试的内容。不要从内存中组装提交后的监视循环或状态摘要——在每个对话的第一个此类操作时重新读取它。

```bash
osmo workflow query <workflow_id> --format-type json | jq '{status, tasks: [.groups[].tasks[] | {name, status, exit_code}]}'
osmo workflow logs <workflow_id> -t <task_name> -n 200
osmo data download <dig_url_root>/runs/<name>/anomaly ./output/anomaly-<name>/
```

监控规范：`references/monitoring.md`。检索：`references/output_retrieval.md`。呈现：`references/output_rendering.md`。注意事项：`references/troubleshooting.md`。

---

## 响应模板

对于"显示我计划/配方"请求，使用以下标记部分发出最终响应（以便配方不会在中间被截断）：

**工作流：** `<flow name>` → `assets/configs/<yaml>`

**预检查：** `scripts/preflight_credentials.sh`；`scripts/preflight_urls.sh <0|1|finetune> <usecase> [variant]`

**在`<dig_url_root>`下所需的 URL 产物：** 按照所选流的常见先决条件 §3 列出。

**提交命令：**

```bash
STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)
osmo workflow submit assets/configs/<yaml> --pool <pool> \
  --set name=<flow>-$STAMP dig_url_root=<root> usecase=<usecase> \
        image_edit_endpoint=<endpoint> image_edit_model=nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL \
        checkpoint_step=<step> 'anomaly_types_json=<types>'
```

**监控：** 在运行提交之前加载`references/monitoring.md`；在`osmo workflow submit`返回工作流 ID 后应用其轮询频率 + 日志拉取阈值。

**输出位置：** `<dig_url_root>/runs/<flow>-$STAMP/anomaly/`（按工作流覆盖：参见工作流概述）。

---

## 支持文件

完整清单——工作流 YAML、cookbook、脚本表、参考资料、评估、组件技能——在**`references/contents.md`**中。顶层目录：`assets/configs/`、`assets/cookbooks/`、`scripts/`、`references/`、`evals/`。
