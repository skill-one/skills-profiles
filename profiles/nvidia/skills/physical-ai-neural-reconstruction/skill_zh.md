# 物理AI神经重建（NuRec）路由器

## 目的

这是一个用于NVIDIA神经重建（NuRec）请求的**轻量级路由器**。它指向上游的`nurec-index`技能，位于`https://github.com/NVIDIA/nurec-skills`，以及其兄弟技能（`physical-ai-datasets`、`ncore`、`nre`、`asset-harvester`、`nurec-fixer`）。使用此技能来：

- 识别哪个上游兄弟技能回答NuRec问题。
- 定位、克隆或刷新标准的`nurec-skills`检出。
- 在打开上游配方之前，对多步骤NuRec工作流程（数据→转换→训练→渲染→清理）进行排序。

标准配方（训练、渲染、数据转换、数据集下载、对象采集、帧清理）位于上游兄弟技能中。**切勿在此处复制或重建它们的命令。**

**不要使用此技能用于：**

- CAD或源网格的SimReady打包 → 使用`omniverse-cad-to-simready`。
- 与NuRec无关的通用USD性能调优 → 使用`omniverse-usd-performance-tuning`。
- AKS / OSMO / NIM Operator基础设施设置 → 使用`physical-ai-infrastructure-setup-and-resilient-scaling`。

## 何时使用

每次用户提到以下任何内容时，请**首先**阅读此技能：

`nurec`、`nurec router`、`nurec index`、`神经重建`、`神经重建引擎`、`NRE`、`3DGUT`、`3DGRT`、`USDZ`、`NCore V4`、`sensorsim`、`sensor sim`、`novel view synthesis`、`PhysicalAI-Autonomous-Vehicles-NuRec`、`PhysicalAI-Robotics-NuRec`、`PhysicalAI-NuRec-PPISP`、`Cosmos-Drive-Dreams`、`asset harvester`、`nurec fixer`、`DiffusionHarmonizer`、`harmonizer`、`difix`、`difix3d`、`carline adaptation`、`serve-grpc`、`render-grpc`、`warm serve-grpc`、`nre thin client`、`batch_render_rgb`、`nurec teardown`、"我该如何开始使用NuRec"、"我应该使用哪个NuRec技能来完成X？"

确定哪个上游兄弟技能回答了问题，获取它（见[定位和获取上游技能](#locate-and-fetch-the-upstream-skills)），然后遵循该技能的主体。

## 前置条件

路由器本身除了用于获取上游的`git`之外没有其他运行时前置条件。下游兄弟技能需要Linux x86_64、一个NVIDIA GPU（Ampere+、CUDA 12.8、≥ 24 GB VRAM）、Docker加上NVIDIA容器工具包、一个NGC API密钥、一个带有相关受控许可已接受的Hugging Face令牌，以及Python 3.10+。

每个技能的详细信息——驱动器楼层、容器名称、密钥解析顺序、哪些Hugging Face资产受控，以及如何在不回显密钥的情况下验证密钥——在`[`references/prerequisites.md`](references/prerequisites.md)`中。优先选择每个兄弟的`scripts/validate_setup.py`，而不是手动检查。

## 什么是NuRec？

**NuRec**（NVIDIA Omniverse神经重建）将相机、LiDAR、雷达或立体记录——通常来自自动驾驶汽车或机器人——转换为可以从任何视点重新渲染的3D场景。一个典型项目分为三个阶段：获取输入（使用`ncore`转换记录，或使用`physical-ai-datasets`下载现成的数据集）、训练重建（`nre`，它发出USDZ）、然后渲染新视图（`nre`）。仅想*使用*NVIDIA已发布的场景的项目可以跳过训练阶段。

词汇背景——NRE与NuRec、USDZ、NCore V4、3DGUT / 3DGRT——在`[`references/what-is-nurec.md`](references/what-is-nurec.md)`中。

## 选择一个技能

在左侧列中匹配用户的目标，并在右侧打开命名的上游技能。箭头表示“按顺序执行”。

| 我想要… | 上游技能 |
|------------|----------------|
| 查找或下载NVIDIA已发布的NuRec数据集 | `physical-ai-datasets` |
| 将我自己的相机 / LiDAR / 雷达 / 深度 / 立体记录转换为NCore V4 | `ncore` |
| 为不受支持的传感器设置编写新的转换器（无人机、RGB-D、ROS 2包、COLMAP、ScanNet++） | `ncore` |
| 从NCore片段训练3D重建 | `ncore` → `nre` |
| 生成NRE需要的额外输入（分割掩码、深度、ego掩码、DINOv2、LiDAR-seg可见性） | `nre`（使用`nre-tools-ga`容器） |
| 沿原始相机位置渲染USDZ | `nre` |
| 以全分辨率 / 最高质量渲染 | `nre`（见“质量预设”） |
| 沿偏移轨迹渲染（例如，汽车向左移动3米） | `nre` |
| 将现有的USDZ适配到增强的目标车辆 rig（carline adaptation） | `nre`（`export-custom-rig-trajectory` → `render`）→ `nurec-fixer` |
| 通过服务器渲染，以便CARLA / Isaac Sim / AlpaSim / 自定义模拟器可以请求帧 | `nre`（`serve-grpc`） |
| 从Python多次连续渲染相同的USDZ，每次调用延迟最小 | `nre`（热`serve-grpc` + 轻量级Python客户端 / `batch_render_rgb`） |
| 从USDZ渲染LiDAR扫描（点云） | `nre`（`render-grpc --lidar`） |
| 跳过训练，仅渲染NVIDIA已构建的NuRec场景 | `physical-ai-datasets` → `nre` |
| 跳过训练，使用预构建的室内机器人场景 | `physical-ai-datasets` → `nre`（然后是Isaac Sim 5.1） |
| 从驾驶片段中提取单个3D对象（汽车、行人） | `asset-harvester` |
| 在NuRec场景中添加、删除或替换汽车 / 行人 | `asset-harvester` → `nre` |
| 清理或协调渲染帧（鬼影、漂浮物、闪烁、光照/阴影） | `nurec-fixer`、**或** `nre`中的`--enable-difix`用于内联渲染 |
| 将场景导出为PLY、网格、深度图、ego掩码等。 | `nre` |
| 升级旧的USDZ，以便新版本的NRE加载它更快 | `nre`（`upgrade-artifact`） |
| 在浏览器查看器中打开USDZ或PLY | `nre`（`viewer` / `ply_viewer`） |
| 与真实值测量渲染质量（PSNR、SSIM、LPIPS） | `nre`（`eval-rendering-metrics`） |
| 在相同场景上基准测试不同的重建方法 | `physical-ai-datasets`（`PhysicalAI-NuRec-PPISP`）→ `nre` |
| 在多个GPU或SLURM上训练 | `nre` |

## 常见工作流程

七种端到端工作流程在`[`references/workflows.md`](references/workflows.md)`中记录，字母匹配上游`nurec-index`工作流ID：

- **A.** 从您自己的记录制作NuRec场景。
- **B.** 使用NVIDIA已经训练的NuRec场景。
- **C.** 使用NuRec进行室内机器人模拟。
- **D.** 在场景中添加、删除或替换3D对象。
- **E.** 清理渲染帧。
- **F.** 基准测试重建质量。
- **G.** 将NuRec连接到模拟器。

当用户的任务跨越多个兄弟技能时，打开该文件。

## 兄弟技能（上游）

通过其**名称**引用兄弟技能——这是可移植的标识符。文件夹列是它在本地`nurec-skills`检出中的位置，除非名称为repo——`asset-harvester`从其自己的产品repo中发布。

| 名称 | 上游文件夹 | 它的作用 |
|------|-----------------|--------------|
| `physical-ai-datasets` | `skills/physical-ai-datasets/` | 目录和下载Hugging Face上每个NVIDIA物理AI数据集的配方（驾驶、机器人、操作、NuRec场景、基准测试）。 |
| `ncore` | `skills/ncore/` | 将任何传感器记录转换为NCore V4（NRE需要的格式），上游发布`2026.04`。还包括编写新转换器。 |
| `nre` | `skills/nre/` | 神经重建引擎本身（`nvcr.io/nvidia/nre/nre-ga`、`nvcr.io/nvidia/nre/nre-tools-ga`、NRE 26.04——图像标签`26.04.01` / `26.04` / `latest`）。训练、执行carline adaptation、渲染（本地、通过热`serve-grpc` + 轻量级Python客户端 / `batch_render_rgb`、或到外部模拟器）、导出网格 / 点云 / 深度、编辑演员、评估质量。 |
| `asset-harvester` | [`NVIDIA/asset-harvester`](https://github.com/NVIDIA/asset-harvester) → `skills/asset-harvester/` | 开源的Apache-2.0管道（SparseViewDiT + TokenGS），从驾驶片段中的稀疏视图中提取单个3D对象，并将它们保存为`.ply`高斯splat，可选地发出`metadata.yaml`用于NuRec交接。 |
| `nurec-fixer` | `skills/nurec-fixer/` | 独立的NVIDIA **DiffusionHarmonizer**工作流程——公共继任者旧的Fixer / Difix3D+配方——清理渲染帧、协调插入的演员、评估PSNR/LPIPS，以及可选微调模型。 |

对于命名重叠（NRE与Fixer、ncore与nre、AV-NuRec与Cosmos-Drive-Dreams、NuRec与SimReady）见`[`references/mix-ups.md`](references/mix-ups.md)`。

## 定位和获取上游技能

首先尝试本地磁盘，按此顺序——在运行时已安装的兄弟技能比网络获取更可取。这适用于`nurec-skills`托管的兄弟技能；`asset-harvester`从其自己的repo获取（见`references/upstream-fetch.md`）：

1. `.agents/skills/<name>/SKILL.md`（Cursor、Codex、NemoClaw）
2. `.claude/skills/<name>/SKILL.md`（Claude Code）
3. `.cursor/skills/<name>/SKILL.md`（项目范围）
4. `~/.cursor/skills/<name>/SKILL.md`（个人技能）
5. 共享上游根目录下的现有`nurec-skills`克隆。

**此顺序仅涵盖`nurec-skills`托管的兄弟技能。**
`asset-harvester`不在其中——见`[`references/upstream-fetch.md`](references/upstream-fetch.md)`。

**只有在那些都不存在的情况下**，在克隆之前向用户明确获取同意。一个`git clone`是外部存储库的网络获取，加上对本地文件系统的写入；它可能违反组织网络策略，并带有供应链风险。向用户展示您打算运行的内容，并等待“是”的回应。

快速配方（完整版本，包括固定提交布局，在`[`references/upstream-fetch.md`](references/upstream-fetch.md)`中）：

```bash
UPSTREAM_ROOT="${NUREC_SKILLS_UPSTREAM_ROOT:-${PHYSICAL_AI_SKILL_HUB_UPSTREAM_ROOT:-$HOME/.physical-ai-skill-hub/upstreams}}"
mkdir -p "$UPSTREAM_ROOT"
if [ -d "$UPSTREAM_ROOT/nurec-skills/.git" ]; then
  git -C "$UPSTREAM_ROOT/nurec-skills" fetch --tags
  git -C "$UPSTREAM_ROOT/nurec-skills" checkout main
  git -C "$UPSTREAM_ROOT/nurec-skills" pull --ff-only
else
  # 只有在用户同意后。优先`--branch <tag-or-sha>`而不是HEAD。
  git clone --depth 1 https://github.com/NVIDIA/nurec-skills.git \
    "$UPSTREAM_ROOT/nurec-skills"
fi
test -f "$UPSTREAM_ROOT/nurec-skills/skills/nurec-index/SKILL.md"
```

上游树以`skills/<name>/SKILL.md`为根；`.agents/skills`是到`skills/`的符号链接，因此任何路径都可以解析。在运行任何可变命令之前阅读上游技能：

```bash
cat "$UPSTREAM_ROOT/nurec-skills/skills/nurec-index/SKILL.md"  # 上游路由器
cat "$UPSTREAM_ROOT/nurec-skills/skills/<folder>/SKILL.md"     # 兄弟技能
```

配套文件（`references/`、`scripts/`、`assets/`）随**兄弟技能自己的技能目录**一起提供，而不是与此路由器一起提供。

## 硬性规则

- 仅路由器——不要在此处复制上游NuRec配方。在运行任何可变命令之前，请阅读上游兄弟技能的主体。
- 通过其`name:`（例如`nre`）引用兄弟技能，而不是通过repo路径。文件夹布局可能会更改；名称是可移植的。
- **切勿未经明确用户同意就`git clone`上游。**
  对于`nurec-skills`兄弟技能，首先穷尽本地查找顺序，显示确切命令，并仅在用户同意的路径中克隆——永远不要静默地克隆到`/tmp`。不要扫描广泛的开发者工作区，如`~/Codes`或重用不相关的旧克隆。
- 使用GA容器频道：`nvcr.io/nvidia/nre/nre-ga`和`nvcr.io/nvidia/nre/nre-tools-ga`。不带后缀的`nvcr.io/nvidia/nre/nre` / `nre-tools`名称是遗留频道——仍然有效用于缓存的版本固定，但新工作流程不应拉取。
- 解析NGC密钥为`${NGC_CLI_API_KEY:-${NGC_API_KEY:-}}`，并使用`docker login nvcr.io --username '$oauthtoken' --password-stdin`登录。永远不要回显密钥。
- `physical-ai-datasets`涵盖受控的Hugging Face数据集。不要绕过数据集许可条款；用户必须在Hugging Face上接受`PhysicalAI-*`受控许可并提供令牌，然后才能下载。
- Asset Harvester在打包成USDZ**之前**运行。除非用户明确要求跳过Asset Harvester，否则不要在手工制作的`.ply`文件上调用`nre`的`export-external-assets`。
- 对于工件清理，优先选择`nre`中的内置`--enable-difix`路径。仅在用户需要公共代码/模型卡、配对评估、微调或修复先前渲染的帧时，才路由到独立的`nurec-fixer`。
- 不要凭记忆编造NRE / NCore / DiffusionHarmonizer命令。重新阅读上游兄弟技能——版本移动很快（NRE 26.04——拉取`nvcr.io/nvidia/nre/nre-ga:26.04.01`或`:26.04`；发布名称`release_26.04`不是一个有效的图像标签——NCore `2026.04`是当前的固定）。
- 此路由器不部署基础设施。将AKS / OSMO / NIM Operator设置路由到`physical-ai-infrastructure-setup-and-resilient-scaling`。

## 限制

- **仅路由器。** 此技能永远不会执行可变的NuRec命令。所有训练、渲染、转换和协调都在上游兄弟技能中发生。
- **上游固定。** 大多数配方位于`https://github.com/NVIDIA/nurec-skills`；`asset-harvester`位于`https://github.com/NVIDIA/asset-harvester`，它在此repo之外发展。过时的克隆可能会漂移；始终在依赖兄弟技能之前刷新上游。
- **手工策划目录。** 新添加的上游兄弟技能在此处不可发现，直到有人编辑表格（见`[`references/maintenance.md`](references/maintenance.md)`）。
- **受控内容。** `nvidia/PhysicalAI-*`、`nvidia/Harmonizer`和`nvidia/Cosmos-Predict2-0.6B-Text2Image`要求用户首先在Hugging Face上接受许可条款。对于`asset-harvester`，只有其可选的DINOv3、Llama Guard和SAM 3D Body模型受控。路由器无法绕过这一点。
- **重型足迹。** 完整的NuRec工作流程可以在磁盘上留下150 GB+。见`[`references/teardown.md`](references/teardown.md)`。
- **仅NVIDIA堆栈。** 需要Linux x86_64加上一个NVIDIA GPU和NVIDIA容器工具包。aarch64 / AMD / Intel / Apple Silicon不受支持。
- **没有Omniverse / Isaac Sim集成步骤。** 将USDZ交给Isaac Sim 5.1（工作流程C）在Isaac Sim文档中记录，而不是在NuRec技能系列中。
- **不是SimReady管道。** NuRec从记录生成可重新渲染的USDZ；CAD或源网格的SimReady打包是不同的管道（见`omniverse-cad-to-simready`）。

## 故障排除

路由器级别的症状——缺失的上游克隆、受控资产的`403`、NGC登录失败、NRE图像上的`manifest unknown`、过时的缓存技能名称——在与此技能一起提供的故障排除配套文件中进行了说明。
兄弟技能自身命令的特定症状属于该兄弟技能。

## 跨技能清理

完整的NuRec工作流程可以在磁盘上留下**150 GB+**，包括容器镜像、模型权重、代码克隆、conda环境、输出目录。每个兄弟技能都有自己的专用`Teardown`部分——当用户不再需要工作流程时，阅读它们，按`[`references/teardown.md`](references/teardown.md)`中记录的顺序。除非它们被泄露，否则**不要**作为清理撤销`NGC_API_KEY` /
`HF_TOKEN`。

## 保持此路由器更新

添加新兄弟技能、重命名或上游URL更改的步骤在`[`references/maintenance.md`](references/maintenance.md)`中。将上游`nurec-index`（<https://github.com/NVIDIA/nurec-skills/blob/main/skills/nurec-index/SKILL.md>）视为路由分类和流程排序的权威**；此技能仅镜像选择器表格、流程排序和上游获取配方。它不是`asset-harvester`的权威，后者在<https://github.com/NVIDIA/asset-harvester>中维护。
