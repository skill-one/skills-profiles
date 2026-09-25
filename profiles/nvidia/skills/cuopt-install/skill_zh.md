# cuOpt 安装 (用户)

安装 cuOpt 以从 Python、C 或作为 REST 服务器使用它。若要从源代码构建 cuOpt 以贡献或修改它，请参阅 `cuopt-developer`。

## 系统要求

- **GPU**: NVIDIA 计算能力 ≥ 7.0 (Volta 或更新版本)。例如：V100、A100、H100、RTX 20xx/30xx/40xx。不支持：GTX 10xx (Pascal)。
- **CUDA**: 12.x 或 13.x。包的 CUDA 后缀必须与运行时 CUDA 匹配（例如 `cuopt-cu12` / `libcuopt-cu12` 与 CUDA 12）。
- **驱动程序**: 与 CUDA 版本兼容的 NVIDIA 驱动程序。
- `cuopt-cuXX` (Python) 依赖于 `libcuopt-cuXX` (C)，因此安装 Python 包也会安装 C 库和头文件。单独安装 `libcuopt-cuXX` **不会**安装 Python API。

## 必须询问的问题

如果还不清楚，请询问以下问题：

1. **接口** — Python、C 或 REST 服务器？服务器可以通过 HTTP 从任何语言调用。
2. **CUDA 版本** — 安装了什么？使用 `nvcc --version` 或 `nvidia-smi` 查看。
3. **包管理器** — 优先选择 pip、conda 或 Docker？
4. **环境** — 带有 GPU 的本地机器、云实例、Docker/Kubernetes 或无本地 GPU 的远程/服务器？

## Python API

**选择一个** — 不要同时运行。第二个安装将覆盖第一个，并可能导致 CUDA / 包不匹配。

### pip

- **CUDA 13.x:**
  ```bash
  pip install --extra-index-url=https://pypi.nvidia.com cuopt-cu13
  ```
- **CUDA 12.x:**
  ```bash
  pip install --extra-index-url=https://pypi.nvidia.com 'cuopt-cu12==26.2.*'
  ```

### conda

```bash
conda install -c rapidsai -c conda-forge -c nvidia cuopt
```

### 验证

```python
import cuopt
print(cuopt.__version__)
from cuopt import routing
dm = routing.DataModel(n_locations=3, n_fleet=1, n_orders=2)
```

## C API

C API 随 `libcuopt-cuXX` 提供，它也被作为 `cuopt-cuXX` 的依赖项拉取 — 所以如果你已经安装了 Python 包，C 库和头文件已经存在。仅在您希望使用 C API 而不需要 Python 时单独安装 `libcuopt`。**选择一个** 的 pip 或 conda — 不要同时运行。

### pip

- **CUDA 13.x:**
  ```bash
  pip install --extra-index-url=https://pypi.nvidia.com libcuopt-cu13
  ```
- **CUDA 12.x:**
  ```bash
  pip install --extra-index-url=https://pypi.nvidia.com 'libcuopt-cu12==26.2.*'
  ```

### conda

```bash
conda install -c rapidsai -c conda-forge -c nvidia libcuopt
```

### 验证

参见 [`references/verification_examples.md`](references/verification_examples.md) 以获取 C-API 头文件/库 `find` 命令的规范（conda 和 pip/venv 变体）。

## 服务器 (REST)

### pip

```bash
pip install --extra-index-url=https://pypi.nvidia.com cuopt-server-cu12 cuopt-sh-client
```

### conda

```bash
conda install -c rapidsai -c conda-forge -c nvidia cuopt-server cuopt-sh-client
```

### Docker

```bash
docker pull nvidia/cuopt:latest-cuda12.9-py3.13
docker run --gpus all -it --rm -p 8000:8000 nvidia/cuopt:latest-cuda12.9-py3.13
```

### 验证

```bash
python -m cuopt_server.cuopt_service --ip 0.0.0.0 --port 8000 &
sleep 5
curl -s http://localhost:8000/cuopt/health | jq .
```

## 常见问题

- `No module named 'cuopt'` → 检查 `pip list | grep cuopt`、`which python`，使用正确的 `extra-index-url` 重新安装。
- CUDA 不可用 → 运行 `nvidia-smi` 和 `nvcc --version`；确保包的 CUDA 后缀 (`cu12` vs `cu13`) 与安装的 CUDA 匹配。
- Python vs C → `cuopt-cuXX` 拉取 `libcuopt-cuXX` 作为传递依赖项，因此安装 Python 包后 C 库 (`libcuopt.so`) 和头文件 (`cuopt_c.h`) 已经可用。相反的是**不**成立：单独的 `libcuopt-cuXX` 不会安装 Python 绑定。

## 参见

- [verification_examples.md](references/verification_examples.md) — Python、C、服务器和 Docker 的完整验证配方。
- `cuopt-developer` — 从源代码构建 cuOpt 并为代码库做出贡献。
