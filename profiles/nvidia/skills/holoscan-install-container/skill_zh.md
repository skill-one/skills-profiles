# Holoscan NGC 容器安装

## 目的

从 NGC (`nvcr.io/nvidia/clara-holoscan/holoscan`) 拉取并验证官方 Holoscan SDK 容器，选择适合主机 GPU 的 CUDA/架构标签，并使用捆绑的 Python 和 C++ 示例进行验证。

## 前置条件

- Linux 主机配备 NVIDIA GPU 和可正常工作的驱动程序 (`nvidia-smi`)。
- 已安装 Docker，用户属于 `docker` 组（或具有 `sudo` 权限）。
- 已安装 NVIDIA 容器工具包 (`docker run --gpus all` 可正常工作)。
- ~10–20 GB 的可用磁盘空间用于镜像拉取。
- 可访问 `nvcr.io` 和 `docs.nvidia.com`。

## 限制

- 容器镜像仅涵盖下表中的标签矩阵——不包含 Conda/pip 环境。
- 需要图形界面示例时需要 X11 转发；此技能以 Holoviz 无头模式运行以避免此问题。
- 标签后缀必须与主机 GPU/驱动程序匹配（cuda13 / cuda12-dgpu / cuda12-igpu）——后缀错误会导致 CUDA 初始化失败。

## 说明

- 容器仓库：`nvcr.io/nvidia/clara-holoscan/holoscan`。
- 文档页面 https://docs.nvidia.com/holoscan/sdk-user-guide/sdk_installation.html 是权威的——如果下方内容有出入，请查阅此页。
- 按顺序执行以下步骤：选择标签、验证 GPU 转发并拉取、使用六个示例进行验证，然后传递启动命令。

## 第 1 步：选择标签

标签格式 = `<版本>-<后缀>`，例如 `v4.1.0-cuda13`。从上方文档页面获取当前 SDK 版本；从 `nvidia-smi` 选择后缀（"CUDA 版本"字段，表头右上角）：

| `nvidia-smi` CUDA 版本 | 后缀 |
|---|---|
| 13.x+ | `cuda13` |
| 12.x, Ampere/Ada dGPU | `cuda12-dgpu` |
| 12.x, ARM64 iGPU (nvgpu) | `cuda12-igpu` |

当容器发送比主机驱动程序支持的更新 CUDA 小版本时，预期会出现 "CUDA 前向兼容模式已启用" 的横幅——这不是错误——前向兼容 shim 允许容器的 CUDA 运行时在相同主版本内与较旧的主机驱动程序协同工作。

## 第 2 步：验证 GPU 转发，然后拉取

```bash
docker run --rm --gpus all ubuntu:22.04 nvidia-smi 2>&1 | tail -5
```

如果 Docker 缺失 → 从 https://docs.docker.com/engine/install/ 安装。如果 GPU 转发失败 → 按照 https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html 安装 NVIDIA 容器工具包，然后重试。

拉取 (~10–20 GB — 在开始前提醒用户）：

```bash
docker pull nvcr.io/nvidia/clara-holoscan/holoscan:<TAG>
```

## 第 3 步：使用六个示例进行验证

测试涵盖：纯 Python 绑定 (1a)、纯 C++ 运行时 (1b, 2a)、Python + Holoviz/Vulkan (2b, 3a) 和 C++ + Holoviz/Vulkan (3b)。Holoviz 示例始终以无头模式运行（在 YAML 中注入 `headless: true`）——无论是否连接显示器，这都能正常工作，并避免 SSH 上的 GUI 失败模式。

```bash
IMG=nvcr.io/nvidia/clara-holoscan/holoscan:<TAG>
RUN=(docker run --rm --runtime=nvidia --gpus all --cap-add CAP_SYS_PTRACE --ipc=host --ulimit memlock=-1 --ulimit stack=67108864)

# 1a. hello_world (Python) — 预期输出 "Hello World!"
"${RUN[@]}" "$IMG" bash -c \
  "ulimit -s 32768 && python3 /opt/nvidia/holoscan/examples/hello_world/python/hello_world.py"

# 1b. hello_world (C++) — 预期输出 "Hello World!"
"${RUN[@]}" "$IMG" bash -c \
  "ulimit -s 32768 && /opt/nvidia/holoscan/examples/hello_world/cpp/hello_world"

# 2a. tensor_interop (C++) — 预期张量在每次传递时翻倍，"图执行完成。"
"${RUN[@]}" "$IMG" bash -c \
  "ulimit -s 32768 && /opt/nvidia/holoscan/examples/tensor_interop/cpp/tensor_interop"

# 2b. tensor_interop (Python, 10 帧) — Holoviz，无头模式。默认情况下 YAML 没有 `headless` 字段，因此需要在 `holoviz:` 下注入一个。预期输出 "message received (count: 10)"。
"${RUN[@]}" "$IMG" bash -c "
  ulimit -s 32768
  sed -e 's/count: 0/count: 10/' \
      -e 's/repeat: true/repeat: false/' \
      -e 's/realtime: true/realtime: false/' \
      -e 's/^holoviz:/holoviz:\n  headless: true/' \
      /opt/nvidia/holoscan/examples/tensor_interop/python/tensor_interop.yaml > /tmp/ti.yaml
  cd /opt/nvidia/holoscan/examples/tensor_interop/python
  python3 tensor_interop.py --config /tmp/ti.yaml
"

# 3a. video_replayer (Python, 10 帧) — Holoviz，无头模式。在 `holoviz:` 下注入 `headless: true`（在 `width: 854` 之上）。相同的 `sed` 命令适用于 3b 中的 C++ YAML——这两个文件共享相同的 `holoviz:` 部分结构。
"${RUN[@]}" "$IMG" bash -c "
  ulimit -s 32768
  sed -e 's/count: 0/count: 10/' \
      -e 's/repeat: true/repeat: false/' \
      -e 's/realtime: true/realtime: false/' \
      -e 's/^  width: 854/  headless: true\n  width: 854/' \
      /opt/nvidia/holoscan/examples/video_replayer/python/video_replayer.yaml > /tmp/vr.yaml
  cd /opt/nvidia/holoscan/examples/video_replayer/python
  HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data python3 video_replayer.py --config /tmp/vr.yaml
"

# 3b. video_replayer (C++, 10 帧) — 与 3a 相同的无头注入。C++ YAML 硬编码 `directory: "../data/racerx"`，但 `HOLOSCAN_INPUT_PATH` 会覆盖它，因此无需修补该字段。
"${RUN[@]}" "$IMG" bash -c "
  ulimit -s 32768
  sed -e 's/count: 0/count: 10/' \
      -e 's/repeat: true/repeat: false/' \
      -e 's/realtime: true/realtime: false/' \
      -e 's/^  width: 854/  headless: true\n  width: 854/' \
      /opt/nvidia/holoscan/examples/video_replayer/cpp/video_replayer.yaml > /tmp/vr_cpp.yaml
  cd /opt/nvidia/holoscan/examples/video_replayer/cpp
  HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data ./video_replayer --config /tmp/vr_cpp.yaml
"
```

## 第 4 步：启动命令

- 阅读 https://catalog.ngc.nvidia.com/orgs/nvidia/teams/clara-holoscan/containers/holoscan。
- 向用户解释下方 docker 标志。
- 指导用户查阅该链接以获取更多标志（例如，如何挂载 V4L2 视频设备）。

```bash
docker run -it --rm \
  --runtime=nvidia --gpus all --cap-add CAP_SYS_PTRACE \
  --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
  nvcr.io/nvidia/clara-holoscan/holoscan:<TAG>
# 示例：/opt/nvidia/holoscan/examples/
# 挂载文件：-v /host/path:/container/path
# 图形界面示例：添加 -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY
```

下一步：
- 探索：`ls /opt/nvidia/holoscan/examples/`
- 逐步了解一个：`/holoscan-explain-example`

## 故障排除

- **`docker: Error response from daemon: could not select device driver "nvidia"`。** NVIDIA 容器工具包缺失或未配置。按照第 2 步中的链接安装并重启 Docker。
- **容器内 CUDA 初始化失败。** 标签后缀与主机不匹配。重新检查 `nvidia-smi` CUDA 版本和第 1 步中的表格。
- **启动示例时出现段错误。** 容器内未应用 `ulimit -s 32768`。使用第 3 步中显示的 `bash -c "ulimit -s 32768 && ..."` 模式。
- **Holoviz 示例挂起 / SSH 上无窗口。** YAML 未修补为 `headless: true`。使用第 3 步中显示的 `sed` 注入。
- **`video_replayer` 找不到数据。** 设置 `HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data`——覆盖 YAML 的硬编码路径。
