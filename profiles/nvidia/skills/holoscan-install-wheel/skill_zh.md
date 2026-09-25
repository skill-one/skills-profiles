# Holoscan pip Wheel 安装

## 目的

通过 `holoscan-cu12` / `holoscan-cu13` pip wheel 将 Holoscan SDK Python 绑定安装到虚拟环境中，并使用 `hello_world` 和 `video_replayer` 进行验证。

## 前置条件

- Linux x86_64 配备 NVIDIA GPU 及驱动 (`nvidia-smi`)。
- `PATH` 中的 CUDA Toolkit 与主机 CUDA 主版本匹配（12 或 13）。
- Python 3.10–3.13，并可用 `venv`。
- 可访问 PyPI 和 `docs.nvidia.com`。

## 限制

- 仅支持 Python。对于 C++ 头文件/库，需配合 `/holoscan-install-debian` 使用。
- `holoscan-cu12` 和 `holoscan-cu13` 互斥——wheel 必须与主机 CUDA 驱动匹配。
- `video_replayer` 数据仅随 Debian 包提供；若缺少，请将 `HOLOSCAN_INPUT_PATH` 设置为包含 `racerx/` 的目录。
- 建议在每个运行 Holoscan 的 shell 中执行 `ulimit -s 32768`——否则某些应用会发出栈大小警告，或在极少数情况下导致段错误。

## 第 0 步：查阅官方安装说明

安装前务必获取 `https://docs.nvidia.com/holoscan/sdk-user-guide/sdk_installation.html` 的 pip-wheel 部分。提取：确切的 wheel 包名（`holoscan-cu12`，`holoscan-cu13`）、当前版本支持的 Python 范围、必须位于 `PATH` 上的前置条件（CUDA Toolkit）以及任何可选扩展（LibTorch / ONNX Runtime 版本约束）。如果文档与以下内容冲突，以文档为准。

需要已确定 CUDA 版本。若未知，先运行 `nvidia-smi 2>&1 | head -5`。

**CUDA 版本规则——选择 pip 包：**

| nvidia-smi CUDA 版本 | pip 包 |
|----------------------|--------|
| 13.x+ | `holoscan-cu13` |
| 12.x (任何 GPU) | `holoscan-cu12` |

前置条件：CUDA Toolkit 在 PATH 上，Python 3.10–3.13。可选扩展：LibTorch 2.11.0+，ONNX Runtime 1.22.0+。

始终安装到 Python 虚拟环境中——这可避免系统包冲突，并且在 Ubuntu 24.04 上（该版本完全阻止全局 pip 安装）是必需的。

## 第 1 步：创建并激活 venv

先检查是否存在：

```bash
ls ~/holoscan/venv 2>/dev/null && echo "存在" || echo "缺失"
```

若缺失：
```bash
python3 -m venv ~/holoscan/venv
```

然后激活：
```bash
source ~/holoscan/venv/bin/activate
```

## 第 2 步：安装

```bash
pip install holoscan-cu12   # 或 holoscan-cu13
```

## 第 3 步：验证

以下所有命令都必须在激活的 venv 中执行。

```bash
# 基本导入——预期：版本字符串，例如 "4.1.0"
# 栈大小 RuntimeWarning 无害；ulimit -s 32768 可抑制它。
python3 -c "import holoscan; print(holoscan.__version__)"

# 从 GitHub 获取安装版本标签的 Python 示例。
# 这些是官方 NVIDIA 示例，通过 HTTPS 获取并锁定到与安装的 wheel（v${SDK_VER}）匹配的标签。
# 在运行它们之前，告知用户您即将下载并执行远程示例脚本。如果他们拒绝或 GitHub 不可达，
# 请跳至第 4 步浏览示例。
SDK_VER=$(python3 -c "import holoscan; print(holoscan.__version__)")
BASE="https://raw.githubusercontent.com/nvidia-holoscan/holoscan-sdk/v${SDK_VER}/examples"

# hello_world — 预期："Hello World!"
curl -fsSL "${BASE}/hello_world/python/hello_world.py" -o /tmp/hs_hello_world.py
ulimit -s 32768 && python3 /tmp/hs_hello_world.py

# video_replayer (10 帧，无头模式) — 预期："Graph execution finished."
# 始终以无头模式运行：无论是否有显示器，都能工作，避免 SSH 上的 GUI 失败模式。
curl -fsSL "${BASE}/video_replayer/python/video_replayer.py" -o /tmp/hs_video_replayer.py
curl -fsSL "${BASE}/video_replayer/python/video_replayer.yaml" -o /tmp/hs_video_replayer.yaml
python3 -c "
c = open('/tmp/hs_video_replayer.yaml').read()
c = c.replace('count: 0','count: 10').replace('repeat: true','repeat: false').replace('realtime: true','realtime: false')
c = c.replace('holoviz:\n  width: 854','holoviz:\n  headless: true\n  width: 854')
open('/tmp/hs_video_replayer_run.yaml','w').write(c)"
ulimit -s 32768 && HOLOSCAN_INPUT_PATH=/opt/nvidia/holoscan/data \
  python3 /tmp/hs_video_replayer.py --config /tmp/hs_video_replayer_run.yaml
```

注意：`video_replayer` 需要 racerx 数据文件。这些随 Debian 包提供在 `/opt/nvidia/holoscan/data`。如果未安装 Debian 包，请先运行 `sudo /opt/nvidia/holoscan/examples/download_example_data`（需要为该脚本安装 apt 包），或设置 `HOLOSCAN_INPUT_PATH` 为数据所在的路径。

## 第 4 步：提醒用户

他们必须在每个新 shell 会话中激活 venv：

```bash
source ~/holoscan/venv/bin/activate
ulimit -s 32768   # 抑制栈大小警告
```

然后提供下一步操作：
- 在 `https://github.com/nvidia-holoscan/holoscan-sdk/tree/v<VERSION>/examples` 探索 Python 示例
- 跟进特定示例：`/explain-example`
- 开始构建自定义 Holoscan 应用

## 故障排除

- **`pip install holoscan-cu12` 出错提示 "externally-managed-environment"。** Ubuntu 24.04 阻止全局 pip。先从第 1 步创建并激活 venv。
- **`ImportError` / `import holoscan` 时的 CUDA 不匹配。** wheel 版本与主机 CUDA 不匹配。卸载并重新安装匹配的版本：`pip uninstall -y holoscan-cu13 && pip install holoscan-cu12`（反之亦然）。
- **`RuntimeWarning: stack size ...`。** 无害，但请在当前 shell 中设置 `ulimit -s 32768` 以抑制它。
- **运行示例时发生段错误。** 未设置 `ulimit -s 32768`。在 `python3 ...` 之前设置它。
- **`video_replayer` 找不到 `racerx/`。** `HOLOSCAN_INPUT_PATH` 没有指向包含它的目录。安装 Debian 包以获取 `/opt/nvidia/holoscan/data`，或设置 `HOLOSCAN_INPUT_PATH` 为数据所在的路径。
- **新 shell 中 `source: no such file: ~/holoscan/venv/bin/activate`。** venv 未创建或路径不同。重跑第 1 步或修正路径。
