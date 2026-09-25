# Holoscan Conda 安装

## 目的

在 Linux x86_64 系统的 Conda 环境中安装 Holoscan SDK（Python 运行时和/或 C++ 开发头文件），使用 conda-forge + rapidsai 并正确固定 CUDA 元包。

## 前置条件

- Linux x86_64 系统，配备 NVIDIA GPU 和 CUDA 13 驱动（检查 `nvidia-smi`）。
- `conda`（推荐使用 Miniforge）。如果缺失，步骤 1 会自动安装。
- 可访问 conda-forge、rapidsai 和 `docs.nvidia.com` 网络。

## 限制

- **仅限 CUDA 13**（自 v4.3.0 版本起——早期版本为 CUDA 12）。如果用户使用 CUDA 12 驱动，请重定向到 `/holoscan-install-container` 或 `/holoscan-install-wheel`。
- 仅支持 Linux x86_64 —— conda-forge 不支持 aarch64/iGPU。
- 建议在每个运行 Holoscan 的 shell 中使用 `ulimit -s 32768` —— 如果不设置，某些应用**可能**会发生段错误。

## 步骤 0：查阅官方安装说明

在安装前，务必获取 `https://docs.nvidia.com/holoscan/sdk-user-guide/sdk_installation.html` 的当前 Conda 部分——包名、通道选择以及运行时/开发分离可能会在版本之间发生变化。具体提取：

- 精确的运行时包名（例如，用于 Python 绑定的 `holoscan`）。
- C++ 开发包名以及用户是否需要它。自 v4.1.0 版本起，`libholoscan-dev` 是一个单独的包，包含头文件和 CMake 配置——如果用户想开发 C++ 应用，应安装它。没有它，`find_package(holoscan)` 会失败，且没有头文件可以 `#include`。
- 当前版本支持的 Python 版本（v4.3 版本为 3.10–3.13）。
- 当前 `cuda-version` 的固定值（v4.3 → `13`）。

`rmm` 和 `ucxx` 通过 `rapidsai` 通道分发；`holoscan`、`libholoscan` 和 `libholoscan-dev` 来自 `conda-forge`。

如果文档与以下内容不一致，以文档为准——相应地更新安装命令并告知用户。

## 步骤 1：前置条件检查

```bash
conda --version 2>&1
nvidia-smi 2>&1 | head -5
```

如果未找到 `conda`，则静默安装 Miniforge（相对于 Miniconda 更推荐用于 conda-forge）：

```bash
wget -q https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/Miniforge3.sh
bash /tmp/Miniforge3.sh -b -p ~/miniforge3
source ~/miniforge3/etc/profile.d/conda.sh
conda --version
```

`-b` 标志表示非交互式安装，不会修改 `.bashrc`。用户必须在每个新 shell 中 `source ~/miniforge3/etc/profile.d/conda.sh`（或将其添加到 shell RC 文件中），以使 `conda` 可用。

## 步骤 2：创建环境并安装

### 包角色

- `libholoscan` — C++ 运行时符号（`libholoscan_core.so`）。作为依赖自动拉取。
- `holoscan` — Python 绑定。
- `libholoscan-dev` — C++ 头文件、`libholoscan_core.so` 符号链接和 `holoscan-config.cmake`（用于 `find_package(holoscan)`）。
- `rmm` — RAPIDS 内存管理器（rapidsai 通道）。`holoscan` 的未声明运行时依赖；没有它，`import holoscan` 会失败。
- `ucxx` — UCX Python 绑定（rapidsai 通道），用于分布式/多进程应用。
- `cuda-version=13` — 固定 CUDA 13 元包，以便求解器选择兼容的 CUDA 运行时库。

首先创建环境：

```bash
source ~/miniforge3/etc/profile.d/conda.sh   # 如果 conda 尚未在 PATH 中
conda create -n holoscan python=3.13 -y
conda activate holoscan
```

然后根据用户的目标选择以下变体之一。

根据用户的目标选择包——仅 Python 需要 `holoscan`，C++ 开发需要 `libholoscan-dev`，两者结合使用均可：

```bash
conda install <packages> rmm ucxx cuda-version=13 -c rapidsai -c conda-forge -y
```

对于 C++ 开发，还需安装工具链：

```bash
conda install -c conda-forge cxx-compiler cmake ninja -y
```

使用 `python3 -c "import holoscan; print(holoscan.__version__)"` 验证 Python 安装。使用 `ls "$CONDA_PREFIX/include/holoscan"` 验证 C++ 开发安装。

## 步骤 3：运行 Python 测试

建议使用 `ulimit -s 32768`——否则，某些 Holoscan 应用在启动时**可能**会发生段错误。

`video_replayer` 是一个默认无限循环的显示应用。始终修补其 YAML 文件，使其在 10 帧后停止（`count: 10`，`repeat: false`，`realtime: false`）并以无头模式运行（`headless: true`）——无头模式与是否连接显示器无关，可避免 SSH 上的 GUI 失败模式，因此我们不会根据 `$DISPLAY` 进行分支。

下载脚本和 YAML 配置文件，修补 YAML 文件，然后运行：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate holoscan
ulimit -s 32768

SDK_VER=$(python3 -c "import holoscan; print(holoscan.__version__)")
BASE="https://raw.githubusercontent.com/nvidia-holoscan/holoscan-sdk/v${SDK_VER}/examples"

curl -fsSL "${BASE}/hello_world/python/hello_world.py"         -o /tmp/hs_hello_world.py
curl -fsSL "${BASE}/video_replayer/python/video_replayer.py"   -o /tmp/hs_video_replayer.py
curl -fsSL "${BASE}/video_replayer/python/video_replayer.yaml" -o /tmp/video_replayer.yaml

# 修补 video_replayer.yaml — 10 帧，无头。
python3 -c "
c = open('/tmp/video_replayer.yaml').read()
c = c.replace('count: 0', 'count: 10')
c = c.replace('repeat: true', 'repeat: false')
c = c.replace('realtime: true', 'realtime: false')
c = c.replace('  width: 854', '  headless: true\n  width: 854')
open('/tmp/video_replayer.yaml', 'w').write(c)"

# hello_world — 无显示，无需数据；预期输出："Hello World!"
python3 /tmp/hs_hello_world.py

# video_replayer — 需要racerx数据；预期输出：渲染的帧数，"Graph execution finished."
HOLOSCAN_INPUT_PATH=/path/to/holoscan/data python3 /tmp/hs_video_replayer.py
```

`HOLOSCAN_INPUT_PATH` 必须指向包含 `racerx/` 子目录的目录。如果用户有 SDK 源代码库（例如 `~/repos/holoscan-sdk/data`），否则使用 Debian 或源安装树中的 `download_ngc_data` 脚本下载。

## 步骤 4：提醒用户

他们必须在每个新 shell 会话中执行以下操作：

```bash
source ~/miniforge3/etc/profile.d/conda.sh   # 如果 Miniforge 使用 -b 安装
conda activate holoscan
ulimit -s 32768   # 推荐——防止某些应用发生段错误
```

考虑将这些行添加到 `~/.bashrc` 或 `~/.zshrc` 以避免重复输入。

然后提供下一步操作建议：
- 在 `https://github.com/nvidia-holoscan/holoscan-sdk/tree/v<VERSION>/examples` 探索 C++ 和 Python 示例
- 跟进特定示例：`/explain-example`
- 开始构建自定义 Holoscan 应用

## 故障排除

- **`ImportError: librmm.so: cannot open shared object file`**。未安装 `rmm`。重新运行步骤 2 的 `conda install` 命令——`rmm` 是 `holoscan` 的未声明运行时依赖。
- **求解器选择了一个比预期旧的 `holoscan` 构建**。通道顺序可能错误。使用 `-c rapidsai -c conda-forge`（rapidsai 优先）——这是官方安装命令的顺序，在严格的通道优先级下，conda-forge 优先顺序可能会锁定求解器到一个旧的 `holoscan` 构建。
- **应用启动时发生段错误**。在运行任何 Holoscan 应用前，在当前 shell 中设置 `ulimit -s 32768`。并非所有应用都会触发此问题，但更大的堆栈可以避免该失败模式。
- **在构建 C++ 应用时 `find_package(holoscan)` 失败**。安装 `libholoscan-dev`（自 v4.1.0 版本起，头文件和 CMake 配置在单独的包中）。
- **在新 shell 中 `conda: command not found`**。Miniforge 使用 `-b` 安装且未修补 `.bashrc`。运行 `source ~/miniforge3/etc/profile.d/conda.sh` 或将其添加到您的 shell RC 文件中。
