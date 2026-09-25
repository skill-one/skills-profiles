> **是否独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。
> 
> /*
> 版权所有 (c) 2026, NVIDIA CORPORATION。保留所有权利。
>
> 根据Apache License, Version 2.0（“许可”）；您不得在遵守许可的情况下使用此文件。
> 您可以在以下网址获取许可副本：
>
>     http://www.apache.org/licenses/LICENSE-2.0
>
> 除非适用法律要求或书面同意，否则根据许可分发的软件
> 是“按原样”提供的，不附带任何明示或暗示的保证或条件。
> 请参阅许可了解管理权限和限制的具体语言。
> */
> 
> # TAO-HF 集成技能
>
> 将 HuggingFace (HF) 计算机视觉模型集成到 NVIDIA TAO Toolkit 生态系统。通过 **构建 → 测试 → 调试 → 修复 → 重新测试** 的迭代循环在每个步骤中工作——不是纯粹线性地——当出现问题时，诊断和修复后再继续；当通过时，进入下一步。
>
> 此 SKILL.md 是工作流协调器。每个阶段都有一个专门的 `references/phase-N-*.md`，其中包含完整的步骤内容、代码、Docker 调用和门控。在每个阶段的开始阅读相应的参考——下面的摘要是不充分的。
>
> ---
>
> ## 仅限本地规则
>
> 所有工作都严格在本地进行。**不要在任何远程（GitLab、GitHub、HuggingFace）上推送/提交/分支**，创建合并/拉取请求或问题，或将 Docker 镜像上传/发布到任何注册表或工件存储库。您只能从远程读取/克隆——所有编辑、Docker 构建 和 测试都在本地机器上保留。
>
> ---
>
> ## 子模块覆盖策略
>
> 用户将四个 TAO 仓库（`tao-core`、`tao-pytorch`、`tao-deploy`、`tao-dataservices`）独立克隆到一个工作目录中。每个仓库嵌套的 `tao-core/` 子模块指向**原始未修改的提交**；修改仅在顶层 `tao-core/` 中存在。**始终从顶层 `tao-core/` 安装，决不使用 `<repo>/tao-core/`**——嵌套的子模块会静默忽略所有修改。覆盖规则：(1) 挂载工作目录 `-v $(pwd):/workspace`；(2) `pip install /workspace/tao-core` **首先**，在 tao-pytorch/tao-deploy 之前；(3) PYTHONPATH 顶层 tao-core 优先，例如 `-e PYTHONPATH=/workspace/tao-core:/workspace/tao-pytorch`。有关目录树，请参阅 `references/cross-cutting.md`。
>
> ---
>
> ## 执行平台
>
> 每个测试、冒烟运行和端到端验证都在本地准备的 TAO Toolkit 容器内执行（`tao-pytorch-base:latest`、`tao-deploy-base:latest`、可选 `tao-dataservices-base:latest`——所有来自阶段 0）。平台技能拥有*如何*运行它们；此技能指定*什么*。**默认平台：`local-docker`**。阶段 0 将驱动器/CUDA/NCT 预检委托给 `tao-setup-nvidia-gpu-host`。有关权威技能表、绑定挂载理由和规范 docker-run 标志集，请参阅 `references/cross-cutting.md`。
>
> ---
>
> ## 阶段映射
>
> | 阶段 | 目标 | 参考 |
> |---|---|---|
> | 0 | 先决条件 + TAO Toolkit 镜像 + 本地镜像标签 | [phase-0-prereqs.md](references/phase-0-prereqs.md) |
> | 1 | 输入、HF 检查容器、验证模型 + 数据集 | [phase-1-inspection.md](references/phase-1-inspection.md), [hf-inspection.md](references/hf-inspection.md) |
> | 2 | 最接近的现有 TAO 参考模型 | [phase-2-codebase.md](references/phase-2-codebase.md), [task-type-guide.md](references/task-type-guide.md) |
> | 3 | tao-core 配置 + tao-pytorch 训练器 / 评估 / 推理 | [phase-3-implementation.md](references/phase-3-implementation.md), [tao-patterns.md](references/tao-patterns.md), [repo-structure.md](references/repo-structure.md) |
> | 4 | ONNX 导出 + tao-deploy TRT 引擎 / 推理 / 评估 | [phase-4-deploy.md](references/phase-4-deploy.md) |
> | 5 | 打包（`console_scripts`）+ L0 测试 | [phase-5-packaging.md](references/phase-5-packaging.md) |
> | 6 | 容器测试 + 端到端验证 | [phase-6-container-tests.md](references/phase-6-container-tests.md), [docker-patterns.md](references/docker-patterns.md) |
> | 7 | （有条件）精度 / 延迟 / 大小调整 | [phase-7-optimization.md](references/phase-7-optimization.md) |
> | 跨阶段参考： | [workflow-consistency.md](references/workflow-consistency.md) (CLI 流程、配置字段路径、跨阶段依赖) | [cross-cutting.md](references/cross-cutting.md) (平台、隔离、模块陷阱、调试) |
>
> **重要提示——通过阶段 6 的持续执行：** 不要在阶段 3–5 后停止等待用户运行测试。阶段 6 是强制性的——直到容器内测试通过且端到端管道验证通过才完成。
>
> ---
>
> ## 开发循环
>
> 在每个步骤：编写代码 → 立即测试（导入检查、单元测试或干运行）→ 如果失败，读取跟踪信息 → 诊断 → 修复 → 重新测试；如果通过，继续下一步。**不要累积未测试的代码——仅在最后测试会累积错误。**
>
> ---
>
> ## 调试手册
>
> 当出现问题时，在尝试随机修复之前，先咨询 `references/cross-cutting.md` 中的症状 → 可能原因 → 修复表——它涵盖了 `ModuleNotFoundError`、`BACKBONE_REGISTRY` `KeyError`、形状不匹配、NaN 损失、ONNX/TRT 构建失败、TRT 与 PyTorch 精度差距、OOM、DDP 挂起、检查点加载失败和陈旧子模块配置问题。
>
> ---
>
> ## 环境隔离策略
>
> 所有 Python 工作都在 **Docker 容器内**运行——没有主机 venvs，没有将 `pip install` 安装到主机 Python（主机只需要 Docker，来自 `tao-setup-nvidia-gpu-host`）。三个上下文：A（阶段 1 HF 检查在 `tao-hf-inspect`，`python:3.12-slim` 备用）、B（阶段 3/4/6 冒烟/L0/e2e 在准备好的容器中，通过 `pip install /workspace/tao-core && python setup.py develop` 源）、C（主机绑定挂载草稿）。有关上下文的完整信息和四个编号规则的逐字版本（`--check-only` 主机包；阶段 1 `--user $(id -u):$(id -g)` 与 root；`HOME=/workspace`/`PIP_USER=1` 备用；发行版包管理器列表；`root:root` 交易；`tao-hf-inspect` 清理），请参阅 `references/cross-cutting.md`。
>
> ---
>
> ## 阶段 0 — 先决条件检查
>
> **目标：** 验证 Python 3.10+ 和 `git`；将驱动器/CUDA/Docker/NVIDIA 容器工具包主机检查委托给 `tao-setup-nvidia-gpu-host`；验证 NGC `docker login` 用于 `nvcr.io`。然后 **要求用户** 提供TAO Toolkit 镜像参考（tao-pytorch、tao-deploy、可选 tao-dataservices），拉取，并准备本地标签 `tao-pytorch-base:latest`、`tao-deploy-base:latest`、`tao-dataservices-base:latest` 以供后续阶段使用——准备会移除预安装的发布 TAO 包，因此用户 `/workspace/...` 克隆通过 `pip install /workspace/tao-core && python setup.py develop` 安装/加载。**硬停止**在任何检查失败时。所需用户输入：镜像参考 + 凭证（NGC 登录、`HF_TOKEN`）。完整命令、提示措辞和每个镜像的 `Dockerfile` 片段：阶段 0 参考。
>
> **门控：** 所有先决条件检查通过；用户提供了所需的镜像参考；本地存在 `tao-pytorch-base:latest` 和 `tao-deploy-base:latest`；如果预期数据服务工作，则存在 `tao-dataservices-base:latest`。
>
> ---
>
> ## 阶段 1 — 信息收集与验证
>
> **目标：** 决定是否继续。收集凭证、定位/克隆四个 TAO 仓库、创建一致的工作分支、启动 `tao-hf-inspect` 容器（上下文 A）、验证 HF 模型是 CV 并具有支持的 `pipeline_tag`、提取配置 + 状态字典模式、检查 ONNX 导出、清理。完整步骤：阶段 1 参考。
>
> **如果拒绝：** `pipeline_tag` 是 NLP / 音频 / LLM（非 CV）；`AutoConfig` 抛出；或者 ONNX 导出根本无法工作（没有重写路径）。
>
> **门控：** 四个 TAO 仓库定位/克隆具有一致分支；`pipeline_tag` 确认 CV；提取 `model_type`、`image_size`、`hidden_size`、`num_labels`；记录状态字典键 + HF→TAO 重新映射计划；ONNX 导出检查通过（或理解失败）；用户确认 `model_short_name` + 任务类型。（完整清单：[phase-1-inspection.md](references/phase-1-inspection.md)。）首先呈现结果并获取用户确认。
>
> ---
>
> ## 阶段 2 — 代码库探索
>
> **目标：** 找到检测到的 `pipeline_tag` 最接近的现有 TAO 参考模型，阅读其在 `tao-core` / `tao-pytorch` / `tao-deploy` 中的实现，并决定主干是否存在于 `backbone_v2/` 或是新的。
>
> HF `pipeline_tag` → TAO 参考模型映射（分类 → `classification_pyt`、检测 → `dino`/`rtdetr`、分割 → `segformer`、实例 → `mask2former`、全景 → `oneformer`、零样本 → `grounding_dino`、深度 → `mono_depth`）驱动**下游所有内容**（配置、架构、损失、ONNX 形状、TRT 构建器、部署类、指标、数据集格式）。有关完整参考列表（每个模型 12 个文件）、`backbone_v2/` 和 `tao-dataservices` 覆盖检查以及每个任务的架构，请参阅阶段 2 参考。
>
> 如果需要新的主干，在阶段 3 之前决定策略（timm 包装 > 重新实现 > HF 黑盒包装）。**决不双重继承自 `transformers.PreTrainedModel` 和 `BackboneBase`**（元类冲突——组合代替）。
>
> **门控：** 参考TAO模型识别 + 读取所有 12 个参考位置；理解任务类型影响（架构、损失、ONNX 输出、部署类、指标、数据集）；主干覆盖决定（重用 / 包装 timm / 新）；数据服务覆盖检查。完整清单：[phase-2-codebase.md](references/phase-2-codebase.md)。
>
> ---
>
> ## 阶段 3 — TAO Core 配置与原生实现
>
> **目标：** 编写 tao-core 配置模式 + tao-pytorch 训练器 / 原生推理 / 评估，步骤间进行冒烟测试。（`<model_name>` = `snake_case` 短名；`<ModelName>` = `PascalCase`。）
>
> 步骤 1–7（每个步骤都基于前一个，步骤间进行冒烟测试）：tao-core 配置（1）、tao-pytorch 训练器（2）、多 GPU/多节点（3）、原生推理 → `result.csv`（4）、原生评估 → `results.json`（5）、MLOps 用于训练和评估/推理 → `status.json`（6–7）。`ExperimentConfig(CommonExperimentConfig)` 必须包含 `model`、`dataset`、`train`、`evaluate`、`inference`、`export`、`gen_trt_engine`、`quantize`。所有 `???` 字段都是 `MISSING`（用户通过 YAML/CLI 提供）；`augmentation.mean`/`std`、`model.head.in_channels`、检查点名称和 `onnx_file` 匹配在清单下方。
>
> 每个步骤的完整主体、代码、规范 `experiment_spec.yaml` 和冒烟测试命令：阶段 3 参考。
>
> **门控：** 步骤 1 — `ExperimentConfig` 在容器内导入干净；步骤 2 — `build_model(cfg)` 运行 + PLModel 在容器内实例化；阶段 3 — 所有 7 步完成，冒烟测试通过，没有缺失的 `__init__.py`。
>
> ---
>
> ## 阶段 4 — 导出、部署与 TensorRT 集成
>
> **目标：** 从 tao-pytorch 导出 ONNX，然后 tao-deploy 中的 TRT 引擎构建器 + 推理 + 评估，重用 tao-core 的 `ExperimentConfig`。
>
> 步骤 8–11：ONNX 导出器（8 — 任务特定输入/输出名称，`batch_size=-1` ⇒ 动态批处理）；TRT 引擎构建器（9 — 子类 `EngineBuilder` 或重用 `ClassificationEngineBuilder`；编写 `specs/{gen_trt_engine,inference,evaluate}.yaml`，相同的 `ExperimentConfig` 模式，`augmentation.mean`/`std` 必须 与训练匹配）；TRT 推理 → `result.csv`（10）；TRT 评估 → `results.json`（11）。有关完整代码和阶段 3+4 门控（3 个容器内检查：导入、模型构建 + 前向、ONNX 循环）的参考，请参阅阶段 4。
>
> **模块陷阱：** tao-pytorch 和 tao-deploy 有**分离**的 `hydra_runner` 和 `monitor_status` — 在部署脚本中使用部署版本。`ExperimentConfig` 在两者中均来自 `nvidia_tao_core`（相同的模式/字段路径）。
>
> **阶段 3+4 门控：** 三个容器内检查通过（`tao-pytorch` 导入 + 模型 + ONNX 导出；`tao-deploy` 导入）。
>
> ---
>
> ## 阶段 5 — 打包与 L0 测试
>
> **目标：** 将模型注册为两个仓库中的 console_script 并添加单元测试。
>
> 步骤 12–15：在 `tao-pytorch/setup.py` 的 `console_scripts` 中注册 `'<model_name>=...:main'`（12）和 `tao-deploy/setup.py`（13，通过 `entrypoint_hydra` 创建部署 `entrypoint/<model_name>.py`）；部署 L0 测试（14）；训练器 L0 测试 — `Trainer(..., fast_dev_run=True)` + `@pytest.mark.cv_unit @pytest.mark.<model_name>`（15）。有关确切入口点字符串、代码和 L0 测试文件列表，请参阅阶段 5 参考。
>
> **门控：** 入口点注册；pytest 文件存在并遵循标记约定。**不要停止——直接进入阶段 6。**
>
> ---
>
> ## 跨阶段数据流与一致性验证
>
> 在 Docker 测试之前，验证链 `train → export → gen_trt_engine → inference / evaluate`（`*_model_latest.pth` → `.onnx` → `.engine` 工件流 + 每个阶段读取/写入的配置字段——完整图示在 `references/cross-cutting.md` 中）。
>
> 一致性清单（在继续之前验证）：`self.checkpoint_filename` → `*_latest.pth` 名称 `evaluate.checkpoint` / `export.checkpoint` 参考；`augmentation.mean`/`std` 在训练规范、`inference.yaml`、`evaluate.yaml`、引擎构建器 `preprocess_mode` 中相同；ONNX `input_names=['input']` / `output_names=['output']`（检测/实例分割使用任务特定名称）；`export.input_width`/`input_height` 匹配 `dataset.img_size`；`model.head.in_channels` 匹配 `model_params_mapping.py`；`classes.txt` 在 `dataset.root_dir` 可被两个仓库读取；所有 `__init__.py` 存在（包括 `scripts/__init__.py` 用于 `get_subtasks()` 通过 `pkgutil`）。完整路径：[workflow-consistency.md](references/workflow-consistency.md)。
>
> ---
>
> ## 阶段 6 — 容器测试与端到端验证
>
> **强制——阶段 5 后立即开始。** 所有 TAO 模型都作为 Docker 镜像交付；仅在容器外工作的代码是不完整的。测试直接在 TAO Toolkit 容器内运行——循环中不构建镜像：挂载 → 安装源 (`setup.py develop`) → 直接运行 `pytest` / `pylint` / `pydocstyle` / `flake8`。使用纯命令，**不要使用** `ci/run_functional_tests.py` / `ci/run_static_tests.py` 包装器（仅内部镜像；公共 `github.com/NVIDIA-TAO/` 镜像没有 `ci/` 目录）。
>
> 步骤 16–25：验证本地镜像标签存在（16）；tao-core / tao-pytorch (`-m cv_unit`, `--shm-size=16G`) / tao-deploy（17–19）的单元测试；lint（20）；轮子（21）；端到端——在一个 tao-pytorch 会话中训练干运行 + 导出，然后在一个 tao-deploy 会话中生成 TRT 引擎 + 推理 + 评估（同一会话至关重要 — `--rm` 会丢弃安装）（22）；原生与 TRT 对比（23）；调试 shell（24）；可选发布镜像（25）。
>
> 完整命令（每个 `docker run`、每个容器的环境变量、确切的 pytest / lint 调用 + 完整套件变体、训练/导出/生成 TRT 引擎/推理/评估的一行命令与所有 CLI 覆盖、`ci/` 注释、修复和重新测试循环）和构建脚本 / 运行者模式：见阶段 6 参考。
>
> **阶段 6 门控（完成标准）：** tao-core / tao-pytorch / tao-deploy 在其容器中单元测试通过；静态测试通过（或仅遗留 lint 警告）；轮子构建；端到端 `<model_name>_model_latest.pth` → `model.onnx` → `model.engine` → 非空 `result.csv` + `results.json`；原生与 TRT 在容差内一致。
>
> ---
>
> ## 阶段 7 — 优化与调整（有条件）
>
> 仅在阶段 6 通过但精度 / 延迟 / 大小需要改进时进入。
>
> **首先要求用户提供目标指标。**
>
> 诊断类别：精度太低；TRT 与原生差距；训练太慢；推理太慢。技术：步骤 27 — 超参数调整；步骤 28 — INT8 量化（PTQ 通过 torchao / modelopt，TRT INT8 + 校准）；步骤 29 — 通道剪枝 + 重新训练；步骤 30 — 知识蒸馏；步骤 31 — 分辨率调整（TAO 自动插值 ViT 位置嵌入）。有关每个类别的检查、配置块、YAML 覆盖、决策树和理由，请参阅阶段 7 参考。
>
> ---
>
> ## 参数
>
> `$ARGUMENTS`
>
> 如果提供，将 `$ARGUMENTS` 解释为 HuggingFace 模型 ID 或 URL 以开始阶段 1。如果凭证或模型短名未包含，请在继续之前要求用户提供。
