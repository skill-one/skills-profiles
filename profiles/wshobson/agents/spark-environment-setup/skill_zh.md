# Spark 环境设置

DGX Spark 预装了 GB10 Grace Blackwell 芯片：aarch64 CPU、SM121 GPU、128GB 联合内存、CUDA 13。这是一个比标准 x86 CUDA 12 机箱更窄、更年轻的平台，因此软件包选择和 ABI 匹配比平时更重要——aarch64 + CUDA 13 的轮子生态系统仍在完善中。

## 何时使用此技能

- 为训练或推理设置全新的 Spark 机箱。
- 遇到提及 `libcudart`、缺失符号或“安装成功但无法加载”的轮子时出现导入错误。
- 框架安装（PyTorch、Unsloth、TRL、vLLM、xformers）失败、卡住或静默回退到 CPU。
- 决定是否使用 NGC 容器或裸 pip。
- 在操作系统重装或基础镜像更新后恢复工作配置，需要从头重新验证。

以上每种情况都接受相同的通用修复方法：匹配容器/轮子组合到 CUDA 13 和 SM121，不要与 ABI 冲突。

## 优先容器规则

在以下细节之前快速决策：

- 标准训练/推理工作 → NGC PyTorch 容器。
- 以 Unsloth 为主的微调 → Unsloth 容器（它预装了针对该路径已验证的固定版 Triton/xformers/transformers 组合）。
- 以上都不适用（自定义系统包、本地 IDE 解释器）→ 裸 pip，按照下文精确序列执行。

默认使用容器。将 `nvcr.io/nvidia/pytorch:25.09-py3` 作为一般工作的基础——最新标签已确认在此硬件上可用；如果本地有更新的受祝福标签，则优先拉取，而不是硬性阻塞 `25.11-py3`。NGC 的标签较旧，直接运行它完全可以：

```bash
docker run --runtime=nvidia --gpus all -it --rm \
  nvcr.io/nvidia/pytorch:25.09-py3
```

`unsloth/unsloth:dgxspark-latest` 是一个 *动态* 标签——在使用它之前，先解析并固定其摘要，以确保可重复性；裸标签仅用于发现步骤，不是默认调用。完整拉取-检查-固定序列和标志推理/卷挂载说明 `references/container-workflow.md`。将裸 pip 视为例外。

采取容器优先策略的原因是固定，而不是便利。Triton、xformers 和 transformers 版本与 GB10 的 SM121 目标和 CUDA 13 狭窄交互；容器将它们全部锁定在一起，以硬件上已验证的组合。裸 pip 将此解析权留给你，一次一个损坏的导入。

当使用裸 pip 合理时，逐字逐句地遵循 NVIDIA 演示文稿的安装顺序：

```bash
pip install "transformers==5.13.1" "peft==0.19.1" "hf_transfer==0.1.9" "datasets==4.3.0" "trl==1.8.0"
pip install --no-deps "unsloth==2026.7.2" "unsloth_zoo==2026.7.2" "bitsandbytes==0.49.2"
pip install -U "torchao==0.17.0"
```

第二个命令的 `--no-deps` 标志不是可选的——让 pip 在 aarch64 上重新解析 Unsloth 的依赖树是引入不兼容 torch 或 triton 构建的常见方法。第三行也不是可选的：NGC 基础镜像捆绑的 `torchao` 过旧，无法支持当前 `peft` 的 LoRA-attach 路径（`ImportError: ... torchao ... 仅支持 0.16.0 以上的版本`）——这是一个硬性障碍，不是警告。上述所有 `==` 固定都承载负载，来自 `references/stack-matrix.md` 中较旧的已知良好版本矩阵（其 `Last verified` 日期决定陈旧性）——未固定的安装会解析当前 PyPI 版本，这些版本远远超出此 Unsloth 发布版支持的范围。

当宣布新的受祝福发布时，拉取一个新标签。仅当项目需要添加额外的系统包时，才从两个基础之一本地重建——不是“升级”图像已经固定的组件。两种路径的详细信息：`references/container-workflow.md`。

再进行一项预检：官方 DGX Spark 演示文稿之前曾发布过损坏的版本。在信任一个长期运行的食谱之前，检查 `github.com/NVIDIA/dgx-spark-playbooks` 上的最新问题（以及 `references/stack-matrix.md` 中的其他资源）。

## ABI 规则

Spark 上最常见的单个失败是 CUDA 12/13 ABI 不匹配：针对 `libcudart.so.12` 构建的轮子加载到只有 `libcudart.so.13` 的系统上。安装通常成功；问题稍后以缺失符号错误或无法明显指向 CUDA 的段错误出现。

修复：从 `download.pytorch.org/whl/cu130` 拉取轮子（cu130 标签的 aarch64 构建），或使用上述容器之一，它们已经包含匹配的构建。在使用 CUDA 符号堆栈跟踪之前，检查已安装轮子针对哪个 CUDA 标签构建：

```bash
python3 -c "import torch; print(torch.version.cuda)"
```

如果输出不以 `13` 开头，则首先修复 ABI 不匹配。NGC 容器构建（例如 `nvcr.io/nvidia/pytorch:25.09-py3`）内部使用 CUDA 13 构建 torch，没有 `+cu130` 轮子标签——`pip show torch` 不会显示 `cu130`，并且仅凭此缺失本身不是失败。

典型症状：

- `ImportError: undefined symbol` 引用 CUDA 运行时函数。
- 在第一个 `.cuda()` 调用上出现段错误，没有有用的回溯。
- 轮子安装干净，但在导入时失败——pip 的解析器只检查版本约束，不检查 CUDA ABI。
- 两个“相同”的环境表现不同——通常一个有 cu130 轮子，另一个有 cu121/cu124 残留。

无论症状如何，修复方法都是匹配轮子的 CUDA 标签到系统，或使用已匹配的容器。

## 组件快速表

最可能出现的组件的精简状态。完整表格包含轮子 URL、构建标志、sm_121 与 sm_121a 的区别，以及较旧的已知良好版本矩阵：`references/stack-matrix.md`。

| 组件 | 状态 |
|---|---|
| PyTorch | ✅ 官方 cu130 aarch64 轮子 |
| bitsandbytes | ✅ 开箱即用 |
| Triton | ✅ 需要设置 `TRITON_PTXAS_PATH` 参数 |
| flash-attn | ❌ 跳过 pip 构建；NGC 捆绑了一个可工作的版本——见 `spark-training-gotchas` G2 |
| xformers | 仅源代码构建 (`TORCH_CUDA_ARCH_LIST=12.1`) |
| vLLM | 仅夜间轮子 |
| TransformerEngine / NVFP4 训练 | 仅容器 |

其他所有内容——Unsloth、Axolotl、TRL、PEFT——都通过上述优先容器路径干净地安装。LLaMA-Factory 和 NeMo 在 Spark 上脆弱；先检查上游问题。

## 验证命令

在运行任何昂贵操作之前，确认环境实际上可以看到 GPU：

```python
import torch
print(torch.cuda.is_available(), torch.version.cuda)
```

此调用返回两个值；确切输出格式为一行，`<bool> <cuda-version>`：

```text
True 13.0
```

如果它打印 `False`，不要直接跳到轮子重装——ABI 不匹配是几个可能原因之一：

| 假设 | 快速检查 |
|---|---|
| 运行时/标志 | `nvidia-smi` 在容器内也失败 |
| 设备可见性 | `echo $CUDA_VISIBLE_DEVICES` |
| 权限 | `ls -l /dev/nvidia*` |
| CUDA 初始化状态 | 堵塞进程；重试新 shell/容器 |
| ABI 不匹配（通常元凶） | `torch.version.cuda` 不是 `13.x` |

首先检查 `nvidia-smi`——如果它不显示 GPU，则是前三个，不是 ABI。确认 ABI 后才重装轮子。按假设的详细信息：`references/stack-matrix.md`。在容器启动后、安装特定项目包之前立即运行。

再进行一项检查：如果 Triton 内核编译在训练开始时失败，设置 `TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas` 并重试——见 `references/stack-matrix.md` 中的完整修复列表。

## 下一步

验证的环境只是起点。另见：`spark-training-gotchas` 用于训练运行前的失败预检，以及 `spark-memory-thermal-ops` 用于长时间运行中的统一内存 OOM 和热节流。
