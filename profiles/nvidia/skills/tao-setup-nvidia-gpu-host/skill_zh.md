# NVIDIA GPU 主机设置

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

在 TAO 工作流在 `docker`、`local-docker` 或 `kubernetes` 后端上运行之前，请使用此设置技能。TAO 全局的默认最低要求是：

- NVIDIA 驱动程序 `>=580`（优先使用开放内核模块）
- CUDA 工具包 `>=13.0`
- NVIDIA 容器工具包 `>=1.19.0`
- Docker 引擎 — 仅在 `docker` / `local-docker` 后端上安装，并且仅在缺少 Docker 时安装。选择的软件包取决于发行版系列（在 Debian 系列默认为 `docker.io`，在 RHEL 系列从 `download.docker.com` 获取 `moby-engine` / `docker-ce`，在 SUSE 系列为 `docker`）。传递 `--skip-docker-install` 以取消操作。

检查是安全的，默认为只读 — 它在任何 Linux 发行版上工作，因为它只探测 `nvidia-smi`、CUDA 工具包路径、安装的容器工具包软件包版本（通过 `dpkg`/`rpm`/`nvidia-ctk` 二进制版本）以及 Docker 守护程序的 NVIDIA 运行时。

安装必须由用户明确授权，并使用 `--install` 重新运行。对于这些发行版系列，安装路径是自动化的：

| 系列 | 测试的发行版 | 管理器 | 备注 |
|---|---|---|---|
| debian | Ubuntu 22.04 / 24.04、Debian 12（以及衍生 Pop!_OS、Mint、Zorin、Raspbian、KDE Neon 等通过 `UBUNTU_CODENAME` / `VERSION_CODENAME`） | `apt-get` | 添加 NVIDIA `cuda-keyring` + 容器工具包 `.list`。Docker 通过 `docker.io`（覆盖 `$DOCKER_PACKAGE_DEBIAN`）。 |
| rhel | Fedora 39+、RHEL / Rocky / AlmaLinux 9 和 10 | `dnf`（或 `yum`） | 添加 NVIDIA `cuda-<distro>.repo` + 容器工具包 `.repo`。Docker 通过 Fedora `moby-engine` 当可用时，否则从 `download.docker.com` 获取 `docker-ce`。 |
| suse | openSUSE Leap 15、SLES 15 | `zypper` | 添加相同的 NVIDIA `.repo` 文件。Docker 通过发行版 `docker` 软件包。 |
| 其他（Arch、Alpine、Gentoo、NixOS、FreeBSD、…） | n/a | n/a | `--install` 以清晰的错误退出，列出版本目标和 NVIDIA 安装指南 URL。手动安装，然后重新运行 `--check-only`。 |

## 快速入门

从技能库根目录：

```bash
# 检查本地 Docker 后端主机。
bash skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh --backend docker --check-only

# 用户批准后安装或修复。
bash skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh --backend docker --install

# 检查 Kubernetes GPU 工作主机。
bash skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh --backend kubernetes --check-only
```

> ⚠️ **注意 — 非交互式运行（代理/技能运行）：** 技能运行没有终端，因此安装程序的 `Continue? [y/N]` 提示无法回答。运行 `--check-only` 预览并获取用户批准后，在 `--install` 命令中附加假设是肯定的标志 (`--yes`)，以便它在不提示的情况下继续 — 这会自动确认系统软件包（NVIDIA 驱动程序、CUDA 工具包、NVIDIA 容器工具包和 Docker 后端 Docker）的安装并修改主机，因此仅在您控制的主机上这样做。在终端直接运行 `--install` 的人会收到提示。

## 工作流契约

Docker 和 Kubernetes 工作流必须在提交 GPU 工作之前运行检查：

```bash
SB="${TAO_SKILL_BANK_PATH:-${TAO_SKILL_BANK_ROOT:-$PWD}}"
SETUP_SCRIPT="${SB}/skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh"

bash "$SETUP_SCRIPT" --backend docker --check-only || {
  echo "缺失：TAO GPU 主机运行时未就绪。"
  echo "在用户批准后，运行（为非交互式代理运行附加 --yes）："
  echo "  bash \"$SETUP_SCRIPT\" --backend docker --install"
  exit 1
}
```

永远不要静默安装。如果检查失败，请说明缺失的内容，要求用户授权修复，然后运行安装命令并重新运行检查。

## 模型运行时覆盖契约

当模型没有覆盖时，平台默认值适用。需要不同验证主机堆栈的模型在 `references/skill_info.yaml` 中声明它：

```yaml
runtime_requirements:
  gpu_host:
    min_driver_version: '<version>'
    min_cuda_version: '<version>'
    min_container_toolkit_version: '<version>'
```

在工作流最终平台预检之前读取这些值，并将它们传递给匹配的 `--min-*-version` 标志。模型的最低要求仅对当前工作流优先；不要为其他模型重写平台默认值或要求。版本检查使用数值下限，因此后续兼容版本通过。始终保留选定的 GPU smoke test，因为版本限制无法证明对特定 GPU 架构的支持。

## 安装程序执行的操作

安装程序根据检测到的发行版系列进行分发。在每个支持的家庭中，它添加 NVIDIA 的 CUDA 和容器工具包仓库（如果缺失），安装满足活动最低要求的软件包，可选地安装 Docker，连接 NVIDIA Docker 运行时，并将调用用户添加到 `docker` 组。

常见步骤（所有家庭）：

1. 如果缺失，添加 NVIDIA 的 CUDA 仓库（apt `cuda-keyring` deb，`cuda-<distro>.repo` 对于 dnf/zypper）。
2. 如果缺失，添加 NVIDIA 的容器工具包仓库（`.list` 对于 apt，`.repo` 对于 dnf/zypper）。
3. 安装运行内核的匹配内核头文件 / 开发软件包。
4. 从配置的仓库安装当前开放驱动程序和容器工具包软件包，以及 `--min-cuda-version` 选择的 CUDA 工具包软件包，然后验证这三个软件包是否满足活动最低要求。
5. 对于 Docker 后端，并且在缺少 Docker 时，安装 Docker（覆盖 / 取消操作标志下方），启用/启动守护程序，然后运行 `nvidia-ctk runtime configure --runtime=docker`，并在 `systemctl` 可用时重启 Docker。
6. 将调用用户（`$SUDO_USER` 如果可用，否则 `$USER`）添加到 `docker` 组，以便后续 shell 可以无 `sudo` 运行 `docker` — 使用 `--skip-docker-group` 取消操作。**新的组成员资格不会在当前 shell 中生效**：注销并重新登录，或在每个新 shell 中运行 `newgrp docker`。
7. 尝试 `modprobe nvidia`，以便在重启之前验证可以通过。

特定于系列的软件包选择：

| 步骤 | debian-family | rhel-family | suse-family |
|---|---|---|---|
| 内核头文件 | `linux-headers-$(uname -r)` | `kernel-devel-$(uname -r)`、`kernel-headers-$(uname -r)` | `kernel-default-devel` |
| 驱动程序 | 当前 `nvidia-open`（覆盖：`$NVIDIA_DRIVER_PACKAGE_DEBIAN`） | 当前 `nvidia-driver-cuda`、`kmod-nvidia-open-dkms`（覆盖：`$NVIDIA_DRIVER_PACKAGE_RHEL`、`$NVIDIA_DRIVER_KMOD_RHEL`） | 当前 `nvidia-open-driver-G06-signed-kmp-default`（覆盖：`$NVIDIA_DRIVER_PACKAGE_SUSE`） |
| CUDA 工具包 | 从活动最低要求派生的软件包，例如 `cuda-toolkit-13-0` | 相同 | 相同 |
| 容器工具包 | 当前 `nvidia-container-toolkit` + base/tools/libs，然后最低版本验证 | 相同 | 相同 |
| Docker | `docker.io`（覆盖：`$DOCKER_PACKAGE_DEBIAN`） | Fedora 可用时 `moby-engine`+`moby-cli`，否则从 `download.docker.com` 获取 `docker-ce docker-ce-cli containerd.io` | `docker` |

## 验证

安装后，验证：

```bash
nvidia-smi
nvcc --version
docker info --format '{{json .Runtimes}}' | grep nvidia
sudo docker run --rm --runtime=nvidia --gpus all "$TAO_IMAGE" nvidia-smi -L
```

检测到的驱动程序、CUDA 工具包和容器工具包版本必须满足活动 TAO 全局或模型特定的最低要求。然后运行选定镜像的 GPU smoke test；仅版本比较不足以证明兼容性。

对于 Cosmos 后端，扩展该 smoke test 以进行后端契约的 Python 和入口点检查。Cosmos Framework 必须执行 `/workspace/.venv/bin/python` 作为非根 UID，导入 `cosmos_framework.callbacks.tao_status`，找到原生 torchrun，并在主机报告计算能力 8.0 时验证 A100 PatchEmbed 兼容性标记。Cosmos-RL 必须解析其请求的操作可执行文件，导入系统 PyAV 以进行视频工作流，解析受限的 FFmpeg `h264_cuvid` 解码器，加载 `libnvcuvid.so.1`，验证向后安全的线性 Qwen3-VL PatchEmbed 标记，并验证其检查点加载器接受准备的 `qwen3_vl` 目录。仅通过 `nvidia-smi` 通过的容器尚未准备好进行 Cosmos 训练。

## Kubernetes 注意事项

对于自管理的 Kubernetes 集群，在 GPU 工作节点上运行主机安装程序，或在安装 NVIDIA GPU Operator 或设备插件之前将相同的软件包集烘焙到节点镜像中。

工作流检查还会警告如果 `kubectl` 可用，但集群报告没有 `nvidia.com/gpu` 可分配容量。在这种情况下，在工作主机运行时就绪后安装/配置 NVIDIA GPU Operator：

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install --wait gpu-operator -n gpu-operator --create-namespace nvidia/gpu-operator
```

托管 Kubernetes 提供商可能通过节点镜像或 GPU Operator 策略拥有驱动程序安装。不要在没有用户批准和回滚计划的情况下覆盖提供商管理的 GPU 节点。

## 失败模式

**不支持的发行版系列**：`--install` 自动化 debian-、rhel- 和 suse-family 主机。在 Arch、Alpine、Gentoo、NixOS、FreeBSD 或任何没有 `/etc/os-release`（例如 macOS）的地方，脚本会以清晰的错误退出，列出四个版本目标和上游 NVIDIA 安装指南 URL：

- `https://docs.nvidia.com/cuda/cuda-installation-guide-linux/`
- `https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html`
- `https://docs.docker.com/engine/install/`

使用您发行版的软件包管理器安装这四个组件，然后使用 `--check-only` 重新运行脚本以验证。检查是通用的可移植性 — 它只查询二进制文件 / 软件包数据库 — 因此一旦运行时就绪，无论底层发行版如何，工作流契约都得到满足。

**不支持的 Ubuntu/Debian 衍生版本**：当 `ID` 为例如 `pop`、`mint`、`zorin`、`raspbian` 或其他 debian-family 衍生版本时，脚本通过 `UBUNTU_CODENAME` / `VERSION_CODENAME` (`focal`/`jammy`/`noble` → Ubuntu 20.04/22.04/24.04；`bullseye`/`bookworm`/`trixie` → Debian 11/12/12）将主机映射到上游 Ubuntu/Debian CUDA 仓库。如果主机的 codename 不匹配已知上游版本，`--install` 会以上述手动安装指导退出。

**Docker 未安装**：`--check-only` 报告 `MISSING: Docker 未安装` 并打印适用于检测到发行版系列的精确重新运行命令。默认的 `--install` 路径安装 Docker (`docker.io` / `moby-engine` / `docker-ce` / `docker` 取决于系列)，启用/启动守护程序，配置 NVIDIA 运行时，并将调用用户添加到 `docker` 组。如果您希望自行管理 Docker，请在重新运行脚本之前安装它或传递 `--skip-docker-install`。

**Docker 已安装但 `docker run` 仍然需要 sudo**：脚本将调用用户添加到 `docker` 组，但 Linux 仅在新的登录会话中刷新组成员资格。注销并重新登录，或在每个新 shell 中运行 `newgrp docker`，直到新的成员资格生效。

**Docker 运行时仍然缺失**：重启 Docker，然后重新运行 `nvidia-ctk runtime configure --runtime=docker`。

**检测到的版本低于活动最低要求**：在批准后重新运行相同的命令并保留任何模型特定的 `--min-*-version` 标志。软件包名环境覆盖选择特定于分布的驱动程序软件包，但不会削弱最低版本检查。

**驱动程序已安装但 `nvidia-smi` 失败**：使用 `sudo modprobe nvidia` 加载模块或重启。安全启动可能需要在启用了安全启动的系统上进行 MOK 注册。

**Kubernetes 仍然没有 GPU 容量**：使用 `nvidia-smi` 确认每个 GPU 节点上的驱动程序是否正常工作，然后检查 GPU Operator/设备插件 Pod 和节点标签。
