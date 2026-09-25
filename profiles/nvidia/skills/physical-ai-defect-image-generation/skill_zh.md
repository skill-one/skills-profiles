# 物理AI缺陷图像生成

## 目录

- [支持的流程](#支持的流程)
- [消除歧义](#消除歧义处理模糊请求前提交)（完整表格在`references/disambiguation.md`）
- [步骤 0：选择流程、Cookbook 并收集输入](#步骤-0选择流程-cookbook-并收集输入)
- [通用先决条件](#通用先决条件所有流程)（长格式在`references/preconditions.md`）
- [流程演练](#流程演练)（每个流程一个条目；详细信息在`references/flows/`）
- [OSMO 监控](#osmo监控)
- [辅助文件](#辅助文件)

为 AOI（自动光学检测）数据集提供缺陷图像生成、增强和标记流程的端到端编排。**AnomalyGen = Cosmos-Predict2-2B 按用例微调**（Cosmos-AnomalyGen-PCB-2B, -Metal-2B, -Glass-2B）。每个流程在`assets/configs/`中都有一个标准的 OSMO 工作流 YAML，该 YAML 非交互式地串联所有步骤。`assets/cookbooks/`中的用例 Cookbooks 提供了 PCBA usd2roi/image-edit 配置和 AnomalyGen 训练配置，用于 PCBA、金属表面和玻璃检测。此技能管理流程选择、数据交接和提交命令；组件内部位于每个组件的`SKILL.md`中。

## 支持的流程

| 流程 | 入口点 | OSMO YAML | 步骤 | 用例 |
|------|-------|----------|------|------|
| **Day 0 — 纹理缺陷** | CAD 场景 USD (`pcba_target.yaml` 随附在 cookbook 中) | `texture_defect_generation_day0.yaml` | usd2roi (扫描网格 + 每个单元格 ROI 剪裁) → image-edit 增强 (`nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL`) → 微调或传递 → 推理（AnomalyGen 标签内联，**包括缺失组件**） | PCBA |
| **Day 0 — 好图像** *(usd2roi + Image-Edit)* | CAD 场景 USD + 每个板的 `pcba_target.yaml` / `day0_image.yaml` / `day0_crop.yaml` | `good_image_generation.yaml` | usd2roi 渲染（扫描网格 + 每个单元格 ROI 剪裁）→ Qwen Image-Edit (OVSL2SL 外观迁移) | PCBA 干净图像集（ChangeNet 金色半部分、微调正例、真实照片配对） |
| **Day 0 — 结构缺陷** | CAD 场景 USD + 每个板的 `pcba_target.yaml` | `structural_defect_generation.yaml` | isaac-render（姿态缺陷：移动 / 坟墓石 / 侧翻）+ 每个组件剪裁（单个模块）→ Qwen Image-Edit (OVSL2SL 光照迁移；姿态几何形状保留） | PCBA 姿态缺陷集；ChangeNet 缺陷半部分 |
| **Day 1 — 推理 + 标签（真实照片对齐，默认）** | CAD 派生的 USD + 真实 PCBA 照片（两者都随附在`datasets/pcb/assets`中） | `texture_defect_generation_day1_real_alignment.yaml` | usd2roi Day 1 渲染 → MI 注册 → 每个ROI剪裁 → yq-render 配置 → 微调或传递 → 推理（AnomalyGen 标签内联） | **默认 PCBA Day 1。** 任何 usd2roi 支持的板的原始 AOI �屏幕截图 |
| **Day 1 — 推理 + 标签（手动 ROI）** | 预捕获的干净图像 + ROI 掩码（NGC 工具或用户上传） | `texture_defect_generation_day1_manual_roi.yaml` | yq-render 配置 → 微调或传递 → 推理（AnomalyGen 标签内联） | 金属表面、玻璃（没有 USD/真实照片流程）；PCBA **仅当用户明确要求**进行预捕获 ROI 实验 |
| **仅微调** | 标记的异常 URL 工具 | `finetune.yaml` | yq-render 配置 → 微调（验证数据集 → 准备测试用例 → torchrun） | 任何用例；生成用于 Day 0 或 Day 1 的检查点。需要原始训练数据在`<dig_url_root>/datasets/<usecase>/raw`下（见`assets/configs/setup/setup_<usecase>.yaml`）。 |

所有流程都在 OSMO 上运行。Day 0 流程需要 `image_edit_endpoint`（Qwen Image-Edit OVSL2SL — 现有 URL 或从`references/nim/`本地部署）；仅微调没有外部端点。

### 为用户选择正确的缺陷类别工作流

| 缺陷类别 | 工作流 | 机制 |
|---|---|---|
| 干净 / 好 / 扫描网格 / `normal_img + cad_mask` 对 | `good_image_generation.yaml` | usd2roi-render + Qwen Image-Edit |
| 纹理缺陷（焊桥、划痕、褪色）**和缺失组件**（由 AnomalyGen 本地处理，不是结构） | `texture_defect_generation_day0.yaml` | Qwen Image-Edit + AnomalyGen AMP/SDG |
| 结构 / 姿态缺陷（坟墓石、移动、侧翻） | `structural_defect_generation.yaml` | IsaacSim 姿态扰动 |
| Day 1 推理 + 标签在真实图像上 | `texture_defect_generation_day1_real_alignment.yaml`（PCBA 默认）或 `texture_defect_generation_day1_manual_roi.yaml`（金属/玻璃；PCBA 仅当用户明确要求预捕获 ROI / 跳过对齐） | usd2roi Day 1 注册（真实对齐）或直接推理（手动 ROI） |

ChangeNet 金色/缺陷对：提交 `good_image_generation.yaml` + `structural_defect_generation.yaml` 并使用相同的 `--set name=`（两个提交的配对约定）。

> **Day 0 和 Day 1 共享相同的下游形状**：一个 Jinja 控制的 `finetune-job`（当`use_pretrained_checkpoint=true`时省略）为 `anomaly-infer` 提供输入。Day 0 预先添加 `usd2roi-render` + `augment-image-edit`；Day 1 从`<dig_url_root>/datasets/<usecase>/raw`开始。每个阶段的详细信息：每个流程的演练。

### 用户意图 → 旋钮映射

**每个 OV 流程都是两阶段的**：`crop_max_emit=N` 限制最终每个单元格的剪裁（阶段 2）；`render_patches=N` 限制原始扫描网格补丁（阶段 1，每个生成多个剪裁）。**不要自动映射“生成 N 张图像”→ `render_patches=N`**（错误阶段）。`crop_max_emit` 在 `structural_defect_generation.yaml` 上不存在（每个组件一个剪裁 — 使用 `render_patches`）或 `texture_defect_generation_day1_real_alignment.yaml` 上不存在（通过 cookbook 的 `crop.classes` 白名单狭窄）。完整旋钮表、烟雾测试配方、默认值、注意事项：`references/knob_mapping.md`。

### 结构缺陷尺寸（没有 `crop_max_emit` 旋钮）

结构输出是 **`render_patches` 的非线性** — 将帧数加倍会增加 ~1.6–1.7× 剪裁，而不是 2×。不要使用 `crop_max_emit`（无效）或 `render_patches=0`（失败）。验证产量表 + 目标尺寸公式：`references/flows/structural_defect_generation.md` §"Sizing the output"。对于模糊的“生成 N 张图像”，通过 `AskUserQuestion` 揭示校准表。

---

## 消除歧义：提交前处理模糊请求

未指明的提示（“生成一些图像”、“运行 PCBA 流程”、“给我缺陷”）**必须**不能通过无声地假设流程 / 用例 / 旋钮映射来解决。当意图不明确时，暂停并通过 `AskUserQuestion`（2–4 个互斥选项）呈现候选解释，然后再提交。消除承重选择：**哪个流程、哪个用例、计数的阶段是什么、微调与传递**。

你应该**不消除**的已确定默认值：PCBA Day 1 → 真实对齐；板 → `0603_H100`；image-edit 端点 → 本地集群服务（`references/nim/`）；`use_pretrained_checkpoint=true`；Day 1 真实对齐 `default_spatial_dependency=cad`（仅在 CAD 掩码不可用时回退到 `free`，见`references/flows/texture_defect_generation_day1_real_alignment.md`）。

**`dig_url_root` 是一个例外 — 没有无声默认值。** 首次（没有内存条目），必须在任何提交 / `osmo data upload` / `preflight_urls.sh` 之前通过 `AskUserQuestion` 询问。`s3://osmo-workflows/dig` 是一个*确认建议*，永远不会自动选择（~80 GB+ 放在那里）。后续运行可能会无声地重用记住的值。见步骤 0 + 内存规则（§4）。

**完整触发表、提示构建和何时-不-询问例外：`references/disambiguation.md`** — 在组装任何模糊请求的 `AskUserQuestion` 选项之前加载。

---

## 步骤 0：选择流程、Cookbook 并收集输入

**在此步骤之前**，如果请求模糊（例如“生成图像”、“运行 PCBA 流程”、“给我缺陷”），暂停并运行上述消除歧义速查表 — 通过 `AskUserQuestion` 呈现候选解释，并让用户选择。不要自动选择用户实际上没有选择的承重默认值。

### 首次门

如果内存中没有此用户的条目，在一个 `AskUserQuestion` 调用中**在**任何预提交 / `osmo` / `kubectl` / `osmo data upload` 之前询问 upfront 偏好问题，保存到内存（§4），然后继续。捆绑：

- **`dig_url_root`** — 必须询问，不能自动选择。提供 `s3://osmo-workflows/dig` 作为可确认的建议；否则用户提供他们自己的 OSMO 支持的存储前缀。~80 GB+ 放在这里。除了内存中记住的先前确认值外，没有逃生通道。
- **默认 OSMO `--pool`** — 来自 `osmo profile list` 的候选者 → `pool.accessible`。
- **Pod 模板确认** — 仅当 `osmo config show POD_TEMPLATE` 返回 403 时（§2 有确切的问题）。
- **Image-edit 端点** — Day 0 仅：选项 A（现有 URL）vs 选项 B（本地部署 NIM）。

后续对话将无声地从内存中读取这些。每个流程的选择（用例、检查点 vs 微调、板、旋钮）每次都询问 — 见下文。

### 预提交顺序（首次门之后）

运行 §1 `preflight_credentials.sh` → §2 `preflight_pod_template.sh` → §3 `preflight_urls.sh <flow> <usecase>` → §4 生成运行戳。**节奏**：§1 和 §2 是每次对话的门控，具有跨对话内存缓存（见 `references/preconditions.md` 中 §4a）— 当内存记录它们已验证 / 用户确认时跳过。§3 在每个提交之前运行（因流程而异）。§4 是代理的工作 — 每个提交一个新鲜的 `$STAMP`。

Pod 模板强制执行是两层：预提交的 `preflight_pod_template.sh` 门控（§2）以及在 Pod 中的运行时预提交（在 OV + 训练任务上，如果缺少 `/usr/share/nvidia/nvoptix.bin` 或 `/dev/shm` < 16 GiB 则快速失败）。尽管 §2 通过，但运行时失败 → 模板被修补出 → 路由到 `physical-ai-infrastructure-setup-and-resilient-scaling`。缺少凭证 / URL 工具 → 首先提交 `setup/setup_<case>.yaml` + `setup/setup_pretrained.yaml`。

然后在一个消息中询问用户 — 仅每个流程的选择（上述首次门已经涵盖了 `dig_url_root`、池、pod-template 和端点偏好；从内存中拉取这些）：

1. **用例** — PCBA（使用 Day 0 + pcb cookbook）、金属表面（Day 1 + metal_surface cookbook）、玻璃（Day 1 + glass cookbook），或自定义？
2. **检查点可用？** — 如果是（`use_pretrained_checkpoint=true`），使用 `<dig_url_root>/models/<usecase>` 并提供 `checkpoint_step`。如果不是，从 `<dig_url_root>/datasets/<usecase>/raw` 微调。
3. **本地-NIM 池容量检查**（Day 0 选项 B 仅）— 在 `kubectl apply` 之前，通过 `physical-ai-infrastructure-setup-and-resilient-scaling` 检查 `Total Capacity`。`Total Capacity < 2` 不能同时托管 NIM + DIG → 询问用户添加 GPU 或切换到选项 A。`image_edit_model` 始终是 `nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL`，永远不会是通用 `qwen-image-edit`。
4. **将用户偏好保存到内存** — 在首次门之后（以及任何偏离已记录默认值的提交之后），持久化承重选择（`dig_url_root`、OSMO 池、默认板、image-edit 端点、pod-template 状态、osmo-admin 角色）。**永远不会保存** `image_edit_model`（恒定值 — 保存会导致漂移）或临时状态（STAMP、一次性 `anomaly_types_json`）。完整表格：**`references/preconditions.md` §4a "Memory rules"**。在每次新对话开始时读取相关记忆并无声应用。

在询问之前查看相关的流程参考 — 大多数值都有合理的默认值。Day 1 路由：PCBA 默认为 `real_alignment`；金属/玻璃没有 USD 流程，所以始终 `manual_roi`；除非用户明确要求跳过对齐，否则不要询问 PCBA“手动或真实对齐”。

---

## 通用先决条件（所有流程）

快速参考。长格式：`references/preconditions.md`。

1. **OSMO 凭证 + 令牌** — 每次对话一次。**如果工作区中存在 `.env`，首先使用它**（`set -a; . ./.env; set +a`）以便 `HF_TOKEN` 被导出。运行 `scripts/preflight_credentials.sh`；权威检查是 OSMO 凭证 `hf-token` 已配置（图像在 `nvcr.io/nvidia/` 上公开 — 无需注册凭证）。在受限出口 shell 中传递 `--no-probe`。见 `references/preconditions.md` §1。
2. **Pod 模板** — 每次对话一次，具有跨对话内存缓存（见步骤 0 §6）。当内存记录集群已验证 / 用户确认 / 409-跳过时跳过。否则运行 `scripts/preflight_pod_template.sh` 并根据退出代码分支（0=验证 / 1=通过 infra 技能修补 / 2=询问用户 (HTTP 403) / 3=跳过 (HTTP 409) / 4=环境修复）。完整分支文本和提示在 `references/preconditions.md` §2。
3. **必需的 URL 工具** — 在每个提交之前。运行 `DIG_URL_ROOT=<dig_url_root> scripts/preflight_urls.sh <0|1|finetune> <usecase> [variant]`。如果任何东西丢失，**停止并首先提交相关的 `setup/setup_<case>.yaml` + `setup/setup_pretrained.yaml`**（OSMO 设置工作流）— 见 `references/setup.md`。**永远不会**本地下载资产以绕过问题；如果设置在凭证上失败，请要求用户更正并重新在 OSMO 上提交。每个流程清单：

   | 流程 | 用例 | `<dig_url_root>` 下所需的 URL 工具 |
   |---|---|---|
   | Day 0 — 纹理缺陷 | PCBA | `models/pretrained`, `models/pcb`, `datasets/pcb/raw`, `datasets/pcb/assets` |
   | Day 0 — 好图像 | PCBA | 仅 `datasets/pcb/assets` |
   | Day 0 — 结构缺陷 | PCBA | 仅 `datasets/pcb/assets` |
   | Day 1 | 金属表面 | `models/pretrained`, `models/metal_surface`, `datasets/metal_surface/raw` |
   | Day 1 | 玻璃 | `models/pretrained`, `models/glass`, `datasets/glass/raw` |
   | Day 1 真实照片对齐 | PCBA | Day 1 PCBA 加上 `datasets/pcb/assets` |
   | 仅微调 | 任何 | `models/pretrained`, `datasets/<usecase>/raw` |

   内置 `usecase` 值是 `pcb`、`metal_surface`、`glass`。见 `references/preconditions.md` §3。

4. **名称戳** — 在每个提交之前重新生成 `$STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)` 并传递 `--set name=<flow>-$STAMP`。生产 YAML 没有默认的 `name`。见 `references/preconditions.md` §4。
5. **玻璃案例（UC3）— Roboflow zip** — 仅用于 `setup_glass.yaml`。首先将 `mobile_screen.zip` 上传到 OSMO URL 前缀；传递 `--set uc3_zip_url_root=<prefix>`。完整程序：`references/setup.md` §"Glass case (UC3)"。

---

## 流程演练

每个流程的完整演练 — 组图、先决条件、提交命令变体、数据交接、每个阶段的故障排除 — 存在于 `references/flows/` 下。代理应在提交它当前对话中未运行的任何流程之前读取匹配的文件。

| 流程 | Workflow YAML | 演练 |
|---|---|---|
| **Day 0 — 纹理缺陷 (PCBA)** | `assets/configs/texture_defect_generation_day0.yaml` | `references/flows/texture_defect_generation_day0.md` |
| **Day 0 — 好图像 (PCBA)** | `assets/configs/good_image_generation.yaml` | `references/flows/good_image_generation.md` |
| **Day 0 — 结构缺陷 (PCBA)** | `assets/configs/structural_defect_generation.yaml` | `references/flows/structural_defect_generation.md` |
| **Day 1 — 推理 + 标签（真实照片对齐，默认 PCBA）** | `assets/configs/texture_defect_generation_day1_real_alignment.yaml` | `references/flows/texture_defect_generation_day1_real_alignment.md` |
| **Day 1 — 推理 + 标签（手动 ROI，金属/玻璃 + PCBA 实验）** | `assets/configs/texture_defect_generation_day1_manual_roi.yaml` | `references/flows/texture_defect_generation_day1_manual_roi.md` |
| **仅微调** | `assets/configs/finetune.yaml` | `references/flows/finetune.md` |

### 跨流程不变量

- `use_pretrained_checkpoint=true`（默认）→ 对 `models/<usecase>` 传递。设置为 `false` 以在 Pod 中插入 `finetune-job` 组（cookbook 在 Pod 中 yq-patched，没有预提交渲染步骤）。
- Day 0 发射每个单元格 `crop/<MATERIAL>/<cell>/...` 树；Day 1 发射针对 USD 注册的每个 ROI 剪裁；结构发射扁平的每个组件剪裁。
- 每个用例的 `checkpoint_step` + `anomaly_types_json` 默认：见 `references/preconditions.md` §"Shipped checkpoint and `anomaly_types_json` defaults"。

---

## OSMO 监控

**在执行任何 `osmo workflow submit`、`osmo workflow query` 或此技能中的 `osmo workflow logs` 操作之前加载 `references/monitoring.md`。** 它定义了轮询节奏、任务状态解释、日志拉取升级阈值、故障分类路由以及向用户呈现的内容与无声重试的内容。不要从内存中组装提交后的监视循环或状态摘要 — 在每个对话的第一次此类操作时重新读取它。

```bash
osmo workflow query <workflow_id> --format-type json | jq '{status, tasks: [.groups[].tasks[] | {name, status, exit_code}]}'
osmo workflow logs <workflow_id> -t <task_name> -n 200
osmo data download <dig_url_root>/runs/<name>/anomaly ./output/anomaly-<name>/
```

监控规范：`references/monitoring.md`。检索：`references/output_retrieval.md`。呈现：`references/output_rendering.md`。陷阱：`references/troubleshooting.md`。

---

## 响应模板

对于“显示我计划 / 配方”请求，使用这些标记部分发出最终响应（以便没有任何内容在配方中间被截断）：

**工作流**：`<flow name>` → `assets/configs/<yaml>`

**预提交**：`scripts/preflight_credentials.sh`; `scripts/preflight_urls.sh <0|1|finetune> <usecase> [variant]`

**`<dig_url_root>` 下所需的 URL 工具**：按 Common Preconditions §3 为所选流程枚举。

**提交命令**：

```bash
STAMP=$(cat /proc/sys/kernel/random/uuid | cut -c1-8)
osmo workflow submit assets/configs/<yaml> --pool <pool> \
  --set name=<flow>-$STAMP dig_url_root=<root> usecase=<usecase> \
        image_edit_endpoint=<endpoint> image_edit_model=nvidia/Qwen-Image-Edit-NVPCB-OVSL2SL \
        checkpoint_step=<step> 'anomaly_types_json=<types>'
```

**监控**：在运行提交之前加载 `references/monitoring.md`；应用其轮询节奏 + 日志拉取阈值，`osmo workflow submit` 返回工作流 ID 后。

**输出位置**：`<dig_url_root>/runs/<flow>-$STAMP/anomaly/`（可覆盖：见流程演练）。

---

## 辅助文件

完整清单 — 工作流 YAML、cookbooks、脚本表、参考、评估、组件技能 — 在 **`references/contents.md`** 中。顶层目录：`assets/configs/`, `assets/cookbooks/`, `scripts/`, `references/`, `evals/`.
