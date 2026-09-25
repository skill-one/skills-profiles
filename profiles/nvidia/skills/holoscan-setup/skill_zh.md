# Holoscan SDK 安装设置

## 目的

通过检查硬件、操作系统、CUDA 驱动程序和现有工具，确定当前主机的 Holoscan SDK 正确安装方法，然后委托给特定方法的安装技能。涵盖 NGC 容器、Debian/apt、pip 轮、Conda 和跨 Ubuntu、RHEL、IGX Orin、Jetson 和 DGX Spark / Grace-Hopper 平台的源代码构建。

## 前置条件

- Linux 主机（Ubuntu 22.04/24.04、RHEL 9.x、IGX Orin、Jetson 或 DGX Spark / Grace-Hopper）
- 带有正常工作的驱动程序的 NVIDIA GPU（`nvidia-smi` 返回 CUDA 版本）
- 网络访问 `docs.nvidia.com` 和 NGC
- 以下之一：Docker + NVIDIA 容器工具包、`apt`、Python 3.10–3.13 带有 `pip`、Conda 或构建工具链——取决于选择的方法

## 可用脚本

| 脚本 | 目的 | 参数 |
|------|------|------|
| `scripts/check_conda.sh` | 检测 Conda 安装，即使不在 PATH 上（搜索 `~/miniconda3`、`~/miniforge3`、`~/anaconda3`、`~/mambaforge`、`/opt/conda` 和 shell rc 文件）；报告环境以及哪些可以导入 `holoscan`。 | 无 |
| `scripts/check_ngc_image.sh` | 检查给定的 CUDA 标签后缀的 NGC Holoscan 容器镜像是否已拉取或可用。 | `<cuda-tag-suffix>` — `cuda13`、`cuda12-dgpu`、`cuda12-igpu` 之一 |

使用 `run_script("scripts/check_conda.sh")` 和 `run_script("scripts/check_ngc_image.sh", "cuda13")` 调用脚本。信任脚本输出而不是 `which conda` 或 `docker images` 等原始命令。

## 说明

以对话式和分步进行——不要一开始就加载所有信息。完成每一步并报告后再继续下一步。

### 工作流规则（必须遵循）

1. 在第 5 步结束时，以**粗体的一行建议**命名方法（例如 `**建议：** NGC 容器——捆绑所有依赖项，最快的工作安装路径。`）。
2. 对于在受支持 x86_64 主机上首次使用的用户，如果 Docker 可用，该建议**必须**是**NGC 容器**。
3. 建议之后，**停止并询问**要使用哪种方法。不要粘贴 `docker pull`、`docker run`、`apt install`、`pip install` 或其他安装命令——这些属于在第 6 步中委托的安装技能。
4. 如果容器路径适用，请在第 4 步**自己**验证 Docker + GPU 转发（运行那里显示的命令）。不要要求用户运行 `nvidia-smi` 或 `docker --version` 来帮助你。

### 第 1 步：先阅读文档

获取 `https://docs.nvidia.com/holoscan/sdk-user-guide/` 然后是 `sdk_installation.html` 以获取当前发布的支持平台、软件包名称和安装要求。不要依赖硬编码的假设。

### 第 2 步：检查机器

并行运行：

```bash
uname -a && (lsb_release -a 2>/dev/null || cat /etc/os-release)
uname -m
nvidia-smi 2>&1 | head -10
nproc && free -h | head -2
```

**关键：** 从 `nvidia-smi` 读取“CUDA 版本”字段（表头右上角）——这是驱动程序支持的最大 CUDA 版本，并决定 `cuda12` 与 `cuda13` 软包的选择。

### 第 3 步：评估兼容性

| 平台 | 可用方法 |
|------|----------|
| Ubuntu 22.04/24.04, x86_64 | 容器、Debian/apt、pip 轮、Conda、源代码 |
| RHEL 9.x, x86_64 | 仅容器 |
| IGX Orin (ARM64) | 容器、Debian/apt、源代码 |
| Jetson AGX Orin / Orin Nano | 容器、Debian/apt（iGPU） |
| Jetson AGX Thor | 容器、Debian/apt |
| DGX Spark / Grace-Hopper | 容器（检查文档中的 OS 要求） |
| 其他 Linux, x86_64 | 容器可能可用；pip 轮如果 glibc ≥ 2.35 |

### 第 4 步：检查工具并呈现选项

并行运行：

```bash
docker --version 2>&1 | head -1; python3 --version 2>&1; pip3 --version 2>&1
dpkg -l | grep holoscan || true
pip3 show holoscan 2>/dev/null | grep -E "^(Name|Version)" || true
~/holoscan/venv/bin/pip show holoscan 2>/dev/null | grep -E "^(Name|Version)" | sed 's/^/venv: /' || true
```

然后自己验证 GPU 转发——**不要**要求用户运行此命令：

```bash
docker run --rm --gpus all ubuntu:22.04 nvidia-smi 2>&1 | tail -5 || true
```

解释结果以用于第 5 步中的状态列：
- `docker` 缺失 → 容器行状态 `✗ — Docker 未安装`。
- Docker 存在但 `could not select device driver "nvidia"` → `✗ — NVIDIA 容器工具包缺失`。
- `nvidia-smi` 输出出现 → `✓`。

然后通过 `run_script` 调用检测脚本：

- `run_script("scripts/check_conda.sh")` — 参考上文“可用脚本”部分，了解为什么这比 `conda --version` 更受青睐。
- `run_script("scripts/check_ngc_image.sh", "<cuda-tag-suffix>")` — 将 `<cuda-tag-suffix>` 替换为从第 2 步确定的标签（例如 `cuda13`、`cuda12-dgpu`、`cuda12-igpu`）。

如果 Holoscan 已安装，请记下版本并询问是否要升级或验证现有安装。

**CUDA 变体规则**（规范参考——在所有以下步骤中应用）：

| nvidia-smi CUDA 版本 | 本地软件包 | 容器标签 |
|----------------------|------------|----------|
| 13.x+ | `holoscan-cu13` / `holoscan-cuda-13` | `cuda13` |
| 12.x, Blackwell GPU | `holoscan-cu12` / `holoscan-cuda-12` | `cuda13`（向前兼容）或 `cuda12-dgpu` |
| 12.x, Ampere/Ada dGPU | `holoscan-cu12` / `holoscan-cuda-12` | `cuda12-dgpu` |
| ARM64 iGPU（Jetson, IGX） | `holoscan` | `cuda12-igpu` |

本地安装将驱动程序的 CUDA 版本视为硬上限。容器支持向前兼容（预期出现“CUDA 向前兼容模式已启用”的横幅，而不是错误）。

### 第 5 步：呈现选项并建议

始终在表格中呈现**所有方法**——永远不要省略一行。使用状态列指示主机上的可用性（不可用的方法显示 ✗ 并附带简短原因）。使用此表格格式：

| 方法 | 最佳用途 | 状态 |
|------|----------|------|
| **NGC 容器** | 所有依赖项捆绑（CUDA、TensorRT、LibTorch、ONNX 运行时、Vulkan）；C++ + Python。需要 Docker + NVIDIA 容器工具包。 | ✓/✗ 基于docker存在性 |
| **Debian/apt** | 本地 Ubuntu；C++ 仅 | ✓/✗ 如果软件包已安装 |
| **pip 轮** | 仅 Python 项目；需要 CUDA 工具包在 PATH 上；Python 3.10–3.13。 | ✓/✗ 如果轮在虚拟环境中安装在 ~/holoscan/venv |
| **Conda** | 仅 CUDA 13；如果已经在 conda 环境中，则很好。 | ✓/✗ 基于 `check_conda.sh` 输出（不仅仅是 `which conda`） |
| **源代码** | 修改 SDK 内部、自定义 CMake 标志、调试符号、不支持的平台或未发布的分支。 | ✓/✗ 如果已在 ~/holoscan/holoscan-sdk 中克隆 |

在表格之后，以确切的 two-line 形式结束这一轮：

> **建议：** `<方法>` — `<一句话原因>`
>
> **您想使用哪种方法？**（container / apt / wheel / conda / source）

如果用户是 Holoscan 新手，主机是受支持的 x86_64 平台且 Docker 可用，建议 **NGC 容器**。对于 RHEL 9 或其他仅容器的主机，建议容器。对于无 Docker 主机的 Python 仅项目，建议 pip 轮。

**不要**在此轮中包含 `docker pull`、`docker run`、`apt install` 或 `pip install` 命令——这些属于在第 6 步中委托的安装技能。保持此响应简短以避免在表格中间被截断。

### 第 6 步：委托给安装技能

一旦选择了方法，就调用相应的技能——不要在行内重复安装步骤：

| 方法 | 调用的技能 |
|------|----------|
| NGC 容器 | `/holoscan-install-container` |
| Debian/apt | `/holoscan-install-debian` |
| pip 轮 | `/holoscan-install-wheel` |
| Conda | `/holoscan-install-conda` |
| 源代码 | `/holoscan-install-source` |

在调用技能时，将 CUDA 变体（cu12/cu13/igpu）和从第 2 步到第 4 步中的任何其他相关事实作为上下文传递。

安装技能拥有完整的命令集——包括推荐的容器标志（`--gpus all`、`--ipc=host`、`--ulimit memlock=-1`、`--ulimit stack=67108864`、内部 `ulimit -s 32768`）和验证示例。不要从 `holoscan-setup` 中重新声明它们；委托并让安装技能生成它们。

### 第 7 步：摘要

如果安装成功并运行了测试，请打印一个测试结果的表格摘要。

## 限制

- RHEL 9.x 仅支持 NGC 容器方法——未发布本地软件包。
- Conda 软包仅限 CUDA 13；CUDA 12 主机必须使用容器、apt、pip 轮或源代码。
- Debian/apt 安装仅支持 C++，因为 Holoscan v3.0.0；Python 支持需要额外的 pip 轮安装。
- pip 轮需要 glibc ≥ 2.35 和 Python 3.10–3.13。
- 本地安装不能超过驱动程序报告的 CUDA 版本；只有容器可以使用 CUDA 向前兼容。
- DGX Spark / Grace-Hopper OS 要求在不同版本之间变化——始终重新检查 `sdk_installation.html`。

## 故障排除

- **`conda --version` 说“command not found”但 Conda 已安装**——在 zsh 设置中很常见，具有惰性加载的 conda 或只有 `.bashrc` 运行 `conda init`。使用 `run_script("scripts/check_conda.sh")`；它搜索安装目录和 rc 文件。
- **`nvidia-smi` 显示比预期的 CUDA 版本低**——该字段是驱动程序支持的最大 CUDA，不是安装的工具包。在安装更高 CUDA 版本的软件包之前升级驱动程序。
- **Debian 安装成功但 Python 中的 `import holoscan` 失败**——自 v3.0.0 起，apt 安装仅支持 C++。随后使用 `/holoscan-install-wheel`。
- **`pip install holoscan` 因 glibc 错误失败**——主机 glibc < 2.35。使用容器或 apt 代替。
- **`check_ngc_image.sh` 报告镜像缺失**——确认 NGC 登录（`docker login nvcr.io`）并且标签后缀与第 4 步中的 CUDA 变体规则匹配。
