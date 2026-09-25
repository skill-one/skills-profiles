# cuPyNumeric 安装（用户）

## 目的

使用此技能从 Python 安装 cuPyNumeric 并验证安装是否真正工作（包括 GPU 使用情况）。每当用户希望通过 conda 或 pip 运行 cuPyNumeric 时，就应用它。不要使用它来从源代码构建（以修改或贡献）——那超出了范围。

## 强制性规则

- **永远不要运行安装。** 不要运行 `pip install`、`conda install` 或任何安装程序。打印命令；让用户运行它。
- **始终隔离。** 不要安装到 base conda、系统 Python 或共享全局环境。
- **在推荐之前检测。** 读取-only `--version` 检查是允许的。

## 前置条件

在推荐任何安装之前，请确认这些系统要求：

- **GPU**：计算能力 ≥ 7.0（Volta+）。也支持仅 CPU。
- **CUDA**：12.2+。
- **操作系统**：Linux (x86_64 / aarch64)、通过 WSL 的 Windows。
- **Python**：3.11 至 3.14
- **conda**：≥ 24.1（仅 conda 路径）。
- **包管理器**：conda（上游推荐）或 pip。如果两者都不存在，请先引导一个（见说明）。

## 说明

按顺序遵循以下步骤：确认前置条件、询问范围问题、通过选定路径安装，然后验证。

### 安装前询问

1. **包管理器？** 检查 `conda --version` 和 `pip --version`。优先选择 conda（上游推荐）；回退到 pip。
1. **环境目标？** GPU 机器、仅 CPU 的笔记本电脑、云、容器或远程/服务器。
1. **CUDA 版本？** 仅在强制在主机上使用 GPU 变体而没有可见 GPU 时询问。使用 `nvidia-smi` / `nvcc --version` 检查。

### 引导程序——先安装包管理器

如果 `conda` 或 `pip` 都不可用，请安装一个。**提供命令和文档链接；不要运行它**。

#### 推荐：Miniforge（完整 conda，conda-forge 默认）

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash "Miniforge3-$(uname)-$(uname -m).sh"
```

文档：https://github.com/conda-forge/miniforge

#### 替代方案：Python + pip

从您的操作系统包管理器（apt/dnf/brew）或 https://www.python.org/downloads/ 安装 Python。如果现有 Python 中缺少 pip：`python -m ensurepip --upgrade`。

安装后，**打开一个新的 shell**，以便二进制文件在 PATH 上。

### 安装——conda 路径

```bash
conda create -n cupynumeric -c conda-forge -c legate cupynumeric
conda activate cupynumeric
```

到现有环境中：`conda install -c conda-forge -c legate cupynumeric`。

conda 会根据安装时 `nvidia-smi` 是否工作来自动选择 GPU 或 CPU 变体。要覆盖此行为，请见下文。

#### 强制 GPU 变体

仅在安装时看不到 GPU 时（例如，为 GPU 主机构建容器）设置 `CONDA_OVERRIDE_CUDA`。使用运行时主机的 CUDA 版本：

```bash
CONDA_OVERRIDE_CUDA="12.2" conda install -c conda-forge -c legate cupynumeric
```

#### 夜间版（验证较少）

```bash
conda install -c conda-forge -c legate-nightly cupynumeric
```

### 安装——pip 路径

```bash
python -m venv .venv
source .venv/bin/activate
pip install nvidia-cupynumeric
```

### 验证

#### 烟雾测试（始终运行）

通过 `legate` 启动器运行一个自包含脚本——无需仓库检出。

```bash
TMP=$(mktemp -d)
cat > "$TMP/smoke.py" <<'EOF'
import cupynumeric as np
a = np.arange(10)
b = np.ones((4, 4))
print("sum:", a.sum())            # 预期 45
print("matmul:", (b @ b).sum())   # 预期 64.0
EOF
legate "$TMP/smoke.py"
rm -rf "$TMP"
```

预期 `sum: 45` 和 `matmul: 64.0`。如果 `legate` 缺失，环境未激活——见故障排除。

#### GPU 使用检查（在存在支持的 GPU 时强制执行）

通过烟雾测试**不能**证明 GPU 使用——在 GPU 机箱上安装 CPU 变体也会产生正确结果。运行两个步骤。

**1. 强制 GPU 启动。** `legate --gpus N` 请求 N 个 GPU；如果没有可见 GPU 或安装了 CPU 变体，则会快速失败。

```bash
TMP=$(mktemp -d)
cat > "$TMP/check.py" <<'EOF'
import cupynumeric as np
print(np.ones((4096, 4096)).sum())
EOF
legate --gpus 1 "$TMP/check.py"
rm -rf "$TMP"
```

预期 `16777216.0`。如果您看到 `CUDA driver`、`libcudart` 或 `no GPUs available`，则安装了 CPU 变体；使用 `CONDA_OVERRIDE_CUDA` 重新安装。

**2. 确认 GPU 被使用。** 从一个 shell 中运行一个有截止时间的矩阵乘法循环，并与 `nvidia-smi` 一起运行——没有第二个终端的竞争：

```bash
TMPDIR_GPU=$(mktemp -d)
SCRIPT="$TMPDIR_GPU/cupynumeric_gpu_check.py"
cat > "$SCRIPT" <<'EOF'
import cupynumeric as np, time
a = np.ones((10000, 10000))
deadline = time.time() + 20
iters = 0
while time.time() < deadline:
    b = a @ a
    _ = float(b.sum())   # 强制同步，以便矩阵乘法实际运行
    iters += 1
print("iters:", iters)
EOF
legate --gpus 1 "$SCRIPT" &
WORKLOAD=$!
sleep 5                                     # 为 Legate 启动缓冲
for _ in $(seq 10);                      # 10 个样本，每秒 1 个——覆盖慢启动
  nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  sleep 1
done
wait "$WORKLOAD"
rm -rf "$TMPDIR_GPU"
```

预期 `memory.used` 在大多数样本中为 GiB 范围，并在一些样本中显示非平凡的 `utilization.gpu`。如果两者在每个样本中都保持在基线，则未安装 GPU 变体——检查 `conda list cupynumeric` 中的 `*_gpu`（不是 `*_cpu`）。

#### 更深入的配方

有关多 GPU 检查、CPU 回退、容器和故障排除的说明，请参阅 [verification_examples.md](references/verification_examples.md)。

## 限制

- **不要在一个环境中混合 conda 和 pip。** 混合会覆盖第一个安装并在导入时中断。要切换，请先运行 `pip uninstall nvidia-cupynumeric` 或 `conda remove cupynumeric`。
- **使用 `legate` 启动器进行多 GPU / 多秩运行。** 纯 `python` 运行单进程：`legate --gpus 2 script.py`。
- **在仅 CPU 的主机上使用 `CONDA_OVERRIDE_CUDA` 强制 GPU 变体。** conda 否则会根据安装时 `nvidia-smi` 自动选择 CPU 或 GPU 变体。
- **要求 Volta 或更新版本。** Pascal (GTX 10xx / P100) 不受支持。
- **验证 `conda --version` ≥ 24.1。** 较旧的版本会静默中断变体选择。
- **将多节点 / MPI / UCX 视为超出范围。** 延迟到 https://docs.nvidia.com/legate/latest/networking-wheels.html 和 https://docs.nvidia.com/legate/latest/mpi-wrapper.html。

## 故障排除

- **`ModuleNotFoundError: No module named 'cupynumeric'`** → 从同一 shell 中运行 `which python` 和 `pip list | grep cupynumeric`（或 `conda list | grep cupynumeric`）以查找环境不匹配。
- **`ImportError` 提及 CUDA / `libcudart`** → 使用 `CONDA_OVERRIDE_CUDA="<your-cuda-version>"` 重新安装；GPU 机箱上安装了 CPU 变体，或 CUDA 版本不匹配。
- **`legate: command not found`** → 激活环境，然后运行 `which legate` 以确认。
- **在笔记本电脑上比 NumPy 慢** → 对于小问题（Legate 每任务开销），可以预期这种情况。见 cuPyNumeric FAQ。

## 参见

- [references/verification_examples.md](references/verification_examples.md) — 验证 + 故障排除配方。
- 上游文档：https://docs.nvidia.com/cupynumeric/latest/installation.html
- Legate 要求：https://docs.nvidia.com/legate/latest/installation.html
