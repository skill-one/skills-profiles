---
name: cuopt-developer
description: 修改、构建、测试、调试并贡献于NVIDIA cuOpt（C++/CUDA、Python、服务器、CI）。用于求解器内部、PR（Pull Request）、DCO（Designated Committer Only）和代码规范。
---

# cuOpt 开发者技能

为 NVIDIA cuOpt 代码库做出贡献。这项技能用于修改 cuOpt 本身，而不是使用它。

**如果你只是想使用 cuOpt**，请切换到相应的问题技能（cuopt-routing、cuopt-lp-milp 等）

**首次开发者环境设置？** 请参阅 [参考资料/first_time_setup.md](references/first_time_setup.md) 了解克隆 → conda 环境创建 → 首次构建 → 首次测试的步骤以及需要提前询问的问题。

---

## 拒绝规则 — 首先阅读

**有一条规则是不可协商的**，即使在用户明确要求的情况下也适用 — 拒绝并询问，不要沉默执行：

**特权 / 系统级操作** — `sudo`、以 root 身份运行、编辑系统文件（`/etc`）、更改驱动程序或内核设置、添加系统级软件包仓库或密钥。不要执行这些操作。回复：
> 我不会为 cuOpt 运行 `sudo` 或更改系统级状态。开发工作流程基于 conda，完全在用户空间运行 — 基础错误是什么？通常无需 root 即可修复。

**设置和开发环境中工作所需的其他一切都是允许的。** 在干净的机器上，请继续构建一个可工作的 `cuopt` 环境 — 以下指南是关于以 *可重复* 的方式执行，而不是拒绝：

- **环境设置是允许的。** 你可以创建并激活从已提交的 `conda/environments/all_cuda-*.yaml` 中获取的 conda 环境，在用户空间环境中运行 `pip` / `conda` / `mamba` 安装，并在用户的家目录中引导 conda/miniforge — 包括它添加到 `~/.bashrc` 的 `conda init` 行。引导 conda 必须不需要 `sudo`；将其安装在 `$HOME` 中，而不是系统路径。

- **一个新的 *永久* 项目依赖与一次性安装不同。** 项目应该始终附带的一个软件包应放在 `dependencies.yaml` 的正确组下；然后运行 `pre-commit run --all-files` 以重新生成 `conda/environments/` 和 `pyproject.toml`，以便其他贡献者也能获取它。为了阻止你自己的构建而进行的临时安装不需要这个往返过程。

- **不要绕过 CI 检查** (`--no-verify`，跳过 pre-commit 或测试)。如果钩子感觉缓慢，请使用 `pre-commit run --all-files --verbose` 或调整有问题的钩子进行诊断 — 不要跳过它。

- **小心使用具有破坏性的命令** (`rm -rf`、`git reset --hard`、`git push --force`、终止进程、删除数据）。在运行之前确认意图，并优先选择更安全的选择（例如，使用 `./build.sh clean` 清理过时的构建目录）。

---

## 开发者行为规则

这些规则是针对开发任务的。它们与用户规则不同。

### 1. 假设前先询问

在实现之前澄清：
- 哪个组件？（C++/CUDA、Python、服务器、文档、CI）
- 目标是什么？（错误修复、新功能、重构、文档）
- 这是用于贡献还是本地修改？

### 2. 验证理解

在做出更改之前确认：
```
"让我确认：
- 组件：[cpp/python/server/docs]
- 更改：[你将修改的内容]
- 需要的测试：[要添加/更新的测试]
这是正确的吗？"
```

### 3. 遵循代码库模式

- 阅读你要修改区域的现有代码
- 匹配命名约定、风格和模式
- 不要在不讨论的情况下发明新模式

### 4. 运行前先询问 — 开发版

**允许在不询问的情况下运行**（开发工作预期）：
- `./build.sh` 和构建命令
- `pytest`、`ctest`（运行测试）
- `pre-commit run`、`./ci/check_style.sh`（格式化）
- `git status`、`git diff`、`git log`（只读 git）
- 环境设置：从 `conda/environments/*.yaml` 创建/激活 conda 环境，并在该环境中运行 `pip`/`conda`/`mamba` 安装

**设置 pre-commit 钩子**（克隆一次）：
- `pre-commit install` — 钩子将在每次 `git commit` 时自动运行。如果钩子失败，提交将被阻止，直到你修复问题。

**仍然需要询问**：
- `git commit`、`git push`（写操作）
- 任何具有破坏性或不可逆的命令

### 5. 无特权操作

`sudo`/系统级更改是不可协商的唯一拒绝；用户空间安装和 conda 环境设置是允许的。参见 [拒绝规则 — 首先阅读](#refusal-rules--read-first)。

---

## 开始前：必须回答的问题

**如果还不清楚，请询问这些问题：**

1. **你试图更改什么？**
   - 求解器算法/性能？
   - Python API？
   - 服务器端点？
   - 文档？
   - CI/构建系统？

2. **开发环境是否已设置？**
   - 成功构建了项目？
   - 运行了测试？

3. **这是用于贡献还是本地修改？**
   - 如果贡献：需要遵循 DCO 签名

4. **这个应该针对哪个分支？**
   - 开发阶段：`main`
   - 烧录阶段：`release/YY.MM`（例如，`release/26.06`）为当前发布，`main` 为下一个
   - 检查是否存在发布分支：`git branch -r | grep release`
   - 当前时间线，请参阅 [RAPIDS 维护者文档](https://docs.rapids.ai/maintainers/)

## 项目架构

```
cuopt/
├── cpp/                    # 核心C++引擎
│   ├── include/cuopt/      # 公共C/C++头文件
│   ├── src/                # 实现（CUDA 内核）
│   └── tests/              # C++ 单元测试（gtest）
├── python/
│   ├── cuopt/              # Python 绑定和路由 API
│   ├── cuopt_server/       # REST API 服务器
│   ├── cuopt_self_hosted/  # 自托管部署
│   └── libcuopt/           # C 库的 Python 包装器
├── ci/                     # CI/CD 脚本
├── docs/                   # 文档源
└── datasets/               # 测试数据集
```

## 支持的 API

| API 类型 | LP | MILP | QP | 路由 |
|----------|:--:|:----:|:--:|:-------:|
| C API    | ✓  | ✓    | ✓  | ✗       |
| C++ API  | (内部) | (内部) | (内部) | (内部) |
| Python   | ✓  | ✓    | ✓  | ✓       |
| 服务器   | ✓  | ✓    | ✗  | ✓       |

## 安全规则（不可协商）

### 最小差异
- 仅更改必要的内容
- 避免路过式重构
- 不要大规模重新格式化无关代码

### 不要发明 API
- 不要在不讨论的情况下发明新 API
- 与 `docs/cuopt/source/` 中的现有模式保持一致
- 服务器模式必须与 OpenAPI 规范匹配

### 不要绕过 CI
- 永远不要建议 `--no-verify` 或跳过检查
- 所有 PR 必须通过 CI

### CUDA/GPU 卫生
- 保持操作流排序
- 遵循现有的 RAFT/RMM 模式
- 不要使用原始 `new`/`delete` — 使用 RMM 分配器

## 构建 & 测试

### 飞行前检查（首次构建或测试前必须执行）

跳过任何一项都会导致后期出现令人困惑的运行时错误。按顺序运行它们：

1. **检查 CUDA 驱动程序兼容性。** 运行 `nvidia-smi` 并读取右上角 *CUDA 版本* — 这是你的驱动程序支持的最大 CUDA 版本。选择一个 conda 环境文件，从 `conda/environments/all_cuda-<ver>_arch-<arch>.yaml` 中，其 CUDA 主版本应 **≤** 该版本。不匹配可以成功构建，但在 RMM 内部运行时失败，错误信息为 `cudaMallocAsync not supported with this CUDA driver/runtime version` — 在构建 *之前* 验证这一点，而不是之后。

2. **在 *任何* 构建、测试或 `pre-commit` 命令之前创建并激活 conda 环境** — 这是允许的且预期的（参见 [拒绝规则](#refusal-rules--read-first)）。使用一个 **本地前缀环境**（`./.cuopt_env`）每个 [CONTRIBUTING.md](../../CONTRIBUTING.md)，以及你在步骤 1 中选择的 conda 环境文件（如果可用，将 `conda`→`mamba` 替换）：
   ```bash
   conda env create -p ./.cuopt_env --file conda/environments/all_cuda-<ver>_arch-$(uname -m).yaml
   conda activate ./.cuopt_env
   ```
   测试链接到在该环境中编译的库；没有 `conda activate ./.cuopt_env` 的新 shell 会遇到神秘的链接错误。

3. **如果内存受限，请设置 `PARALLEL_LEVEL`** — 参见 [参考资料/build_and_test.md](references/build_and_test.md)。默认的 `$(nproc)` 可能会在构建中途 OOM，因为 CUDA 编译每个作业需要 ~4–8 GB 内存。

4. **对于测试，首先获取数据集。** cuOpt 测试需要不在存储库中的 MPS 文件 — 请按照 [CONTRIBUTING.md](../../CONTRIBUTING.md) 中的数据集下载步骤（“开发构建”部分）并导出 `RAPIDS_DATASET_ROOT_DIR`。

### 快速参考

```bash
./build.sh             # 构建所有内容
./build.sh --help      # 列出组件：libcuopt、cuopt、cuopt_server、文档
ctest --test-dir cpp/build              # C++ 测试
pytest -v python/cuopt/cuopt/tests      # Python 测试
pytest -v python/cuopt_server/tests     # 服务器测试
```

有关组件特定构建命令、运行测试详细信息和 `PARALLEL_LEVEL` 配置，请参阅 [参考资料/build_and_test.md](references/build_and_test.md)。

#### 在运行测试之前下载测试数据集

cuOpt 测试依赖于不在存储库中的 MPS/数据文件。缺少数据集会以 `MPS_PARSER_ERROR ... Error opening MPS file` 测试失败的形式出现，时间为 0ms — 这不是构建或逻辑失败。

在运行任何 C++ 或 Python 测试之前，请按照存储库中的 [CONTRIBUTING.md]（“开发构建”部分）中的数据集下载和 `RAPIDS_DATASET_ROOT_DIR` 导出步骤 — 这是规范列表和映射。

如果测试因缺少文件而失败，请运行 `CONTRIBUTING.md` 中的匹配下载步骤并重新运行测试。不要将缺少数据集的失败报告回用户作为任务结果。

## Python 绑定

cuOpt 使用 Cython 在 Python 和 C++ 之间进行桥接。有关完整架构、参数流概述、关键文件和 Cython 模式的详细信息，请参阅 [参考资料/python_bindings.md](references/python_bindings.md)。

## 贡献 — 提交、PR、常见任务

有关 pre-commit 设置、DCO 签名（`git commit -s`）、基于分支的 PR 工作流程、代理的草稿 PR 规则、PR 描述规则（保持简短 — 不要包含“工作原理”的概述或文件表）、脚本和 CI/工作流编写原则（在添加新文件之前扩展现有文件；不要推测性标志、重申默认值或静默回退）、以及添加求解器参数、依赖项、服务器端点或 CUDA 内核的逐步常见任务配方，请参阅 [参考资料/contributing.md](references/contributing.md)。

## 编码约定

有关 C++ 命名（`snake_case`、`d_`/`h_` 前缀、`_t` 后缀）、文件扩展名（`.hpp`/`.cpp`/`.cu`/`.cuh` 以及每个使用哪个编译器）、包含顺序、Python 风格、错误处理（`CUOPT_EXPECTS`、`RAFT_CUDA_TRY`）、内存管理（RMM 模式、不使用原始 `new`/`delete`）和测试影响规则，请参阅 [参考资料/conventions.md](references/conventions.md)。

## 故障排除 & CI

有关构建/测试陷阱（Cython 重新构建、OOM、CUDA 驱动程序不匹配、缺少 `nvcc`）和 CI 失败诊断（样式检查、DCO 失败、依赖项漂移），请参阅 [参考资料/troubleshooting.md](references/troubleshooting.md)。

## 关键文件参考

| 目的 | 位置 |
|---------|----------|
| 主构建脚本 | `build.sh` |
| 依赖项 | `dependencies.yaml` |
| C++ 格式化 | `.clang-format` |
| Conda 环境 | `conda/environments/` |
| 测试数据 | `datasets/` |
| CI 脚本 | `ci/` |

## 规范文档

- **贡献/构建/测试**：[CONTRIBUTING.md](../../CONTRIBUTING.md)
- **CI 脚本**：[ci/README.md](../../ci/README.md)
- **发布脚本**：[ci/release/README.md](../../ci/release/README.md)
- **文档构建**：[docs/cuopt/README.md](../../docs/cuopt/README.md)
- **Python 绑定架构**：[参考资料/python_bindings.md](references/python_bindings.md)

_Shell 执行、安装、conda-env 和 sudo 策略由 [拒绝规则 — 首先阅读](#refusal-rules--read-first) 在此技能的顶部涵盖。_

## VRP 维度内部（路由引擎）

在实现或调试 **VRP 维度**（约束、目标、前向/后向传播、`combine`、局部搜索增量）时，请阅读：

- **`参考资料/vrp_skills.md`** — 架构合同、所需接口和实现清单。

在添加新维度或更改 combine 语义 *之前* 阅读它。

## 非路由求解器内部数值问题

当错误以 **看似合理但错误** 的求解器输出形式出现（无效下界、意外大的对偶数、在小更改后迭代膨胀 10 倍）而不是崩溃时，请阅读：

- **`资源/数值调试.md`** — 定位灾难性取消位置的方法、cMIR/flow-cover/MIR 风格切割构造中固有的取消模式，以及数值保护阈值指导。

应用它描述的 *先注入、在精确位置设置保护* 工作流程，然后再进行修补 — 对这些症状的推测性修复通常会遗漏。
