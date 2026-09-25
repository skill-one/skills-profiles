# Holoscan Debian/apt 安装

## 目的

使用 NVIDIA 的 apt 仓库在 Ubuntu 上安装 Holoscan SDK C++ 运行时 + 头文件，选择适合主机 CUDA 驱动的正确 `holoscan-cuda-*` 软件包，并通过捆绑的 C++ 示例进行验证。

## 前置条件

- Ubuntu x86_64 (22.04 / 24.04) 或 ARM64 (Jetson / IGX) 配备 NVIDIA GPU 和正常工作的驱动程序 (`nvidia-smi`)。
- `sudo` 权限和网络访问权限，可访问 `developer.download.nvidia.com` 和 `docs.nvidia.com`。
- `cuda-keyring` 软件包（步骤 2 会自动安装缺失的软件包）。

## 限制

- apt 源不提供 Python 绑定 — 如果用户需要 Python，请与 `/holoscan-install-wheel` 配合使用。
- 仅限 Ubuntu。其他发行版必须使用容器或轮安装。
- 软件包变体必须与主机 CUDA 驱动匹配 (`holoscan-cuda-12` 对比 `holoscan-cuda-13`)；错误变体 → "CUDA 驱动版本不足"。

## 步骤 0：查阅官方安装说明

在安装前，获取 `https://docs.nvidia.com/holoscan/sdk-user-guide/sdk_installation.html` 的 Debian/apt 部分。提取：

- 精确的软件包名称 (`holoscan-cuda-12`, `holoscan-cuda-13`, `holoscan`)
- 支持的 Ubuntu 版本
- 正确发行版的 `cuda-keyring` URL

如果文档与以下内容不一致，以文档为准。

如果尚未确定操作系统版本和 CUDA 变体，请并行运行：

```bash
lsb_release -a 2>/dev/null || cat /etc/os-release
nvidia-smi 2>&1 | head -5
```

**CUDA 变体规则 — 选择 apt 软件包：**

| nvidia-smi CUDA 版本 | 软件包 |
|------------------------|---------|
| 13.x+ | `holoscan-cuda-13` |
| 12.x (在 IGX 上) | `holoscan` |
| 12.x (不在 IGX 上) | `holoscan-cuda-12` |
| 12.x (nvgpu) | `holoscan-cuda-12` |

## 步骤 1：前置条件检查

```bash
dpkg -l | grep cuda-keyring
dpkg -l | grep -E "holoscan-cuda-(12|13)|^ii  holoscan "
apt-cache show holoscan-cuda-13 holoscan-cuda-12 2>/dev/null | grep -E "^(Package|Version)"
```

根据步骤 1 的结果进行决策：

- 如果 `cuda-keyring` 已安装，则跳过密钥环步骤。
- 如果仓库已配置且软件包在 `apt-cache show` 中可见，则跳过 `apt-get update`。
- **如果正确软件包变体已安装（例如，目标为 cu12 时的 `holoscan-cuda-12`），则完全跳过步骤 2**，直接进入步骤 3。

## 步骤 2：安装

如果软件包已安装（在步骤 1 中检测到）或用户使用 IGX 平台，则跳过此步骤。

```bash
# 如果缺少 cuda-keyring（根据需要调整 ubuntu2204/ubuntu2404）且不在 IGX 平台：
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb && sudo apt-get update

sudo apt-get install -y holoscan-cuda-12   # 或 holoscan-cuda-13
```

## 步骤 3：验证

为该步骤剩余部分设置环境变量，然后运行三个 C++ 检查：

```bash
HS=/opt/nvidia/holoscan
export LD_LIBRARY_PATH=$HS/lib
export HOLOSCAN_INPUT_PATH=$HS/data
ulimit -s 32768

ls $HS/examples/{hello_world,tensor_interop,video_replayer}/

# hello_world — 预期输出: "Hello World!"
$HS/examples/hello_world/cpp/hello_world

# tensor_interop — 预期输出: 张量每次传递翻倍, "Graph execution finished."
# 如果出现 "CUDA driver version is insufficient"：交换软件包变体：
#   sudo apt-get remove -y holoscan-cuda-13 && sudo apt-get install -y holoscan-cuda-12
$HS/examples/tensor_interop/cpp/tensor_interop

# video_replayer (10 帧, 无头模式) — 预期输出: Vulkan 选择 NVIDIA GPU, "Graph execution finished."
# 始终以无头模式运行：无论是否有显示器，都能正常工作，避免 SSH 上的 GUI 失败模式。
ls $HS/data/racerx 2>/dev/null || sudo $HS/examples/download_example_data
python3 -c "
c=open('$HS/examples/video_replayer/cpp/video_replayer.yaml').read()
c=c.replace('count: 0','count: 10').replace('repeat: true','repeat: false').replace('realtime: true','realtime: false')
c=c.replace('  width: 854','  headless: true\n  width: 854')
open('/tmp/vr.yaml','w').write(c)"
$HS/examples/video_replayer/cpp/video_replayer --config /tmp/vr.yaml
```

## 步骤 4：向用户提供可重用的环境片段

验证通过后，与用户分享此片段，并建议如果希望跨会话持久化，将其添加到他们的 shell 启动文件（例如，`~/.bashrc`）：

```bash
export LD_LIBRARY_PATH=/opt/nvidia/holoscan/lib:${LD_LIBRARY_PATH}
export HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data
ulimit -s 32768
```

然后提供下一步操作建议：
- 添加 Python 支持：`/holoscan-install-wheel`
- 浏览示例：`ls /opt/nvidia/holoscan/examples/`
- 查看特定示例：`/explain-example`
- 开始构建自定义 Holoscan 应用程序

## 故障排除

- **`python3 -c "import holoscan"` 在 apt 安装后失败。** 预期 — 自 v3.0.0 起，Debian 软件包仅支持 C++。运行 `/holoscan-install-wheel` 添加 Python 绑定。
- **运行示例时出现 "CUDA driver version is insufficient"。** 软件包变体错误。重新检查 `nvidia-smi` CUDA 版本，并交换变体：`sudo apt-get remove -y holoscan-cuda-13 && sudo apt-get install -y holoscan-cuda-12`（或反之）。
- **`E: Unable to locate package holoscan-cuda-12"。** `cuda-keyring` 未安装或仓库尚未拉取。运行步骤 2 中的密钥环 + `apt-get update` 块（根据主机调整 `ubuntu2204`/`ubuntu2404`）。
- **启动示例时出现段错误。** 当前 shell 未设置 `ulimit -s 32768`。在命令前添加它（步骤 3 模式）。
- **`error while loading shared libraries: libholoscan_core.so"。** `LD_LIBRARY_PATH` 未设置。使用步骤 4 中的环境片段 — `export LD_LIBRARY_PATH=/opt/nvidia/holoscan/lib`。
- **`video_replayer` 找不到数据。** 设置 `HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data`，或运行 `sudo /opt/nvidia/holoscan/examples/download_example_data` 下载 `racerx` 数据集。
