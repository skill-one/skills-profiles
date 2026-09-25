# Spark 训练常见问题

DGX Spark 的 GB10 芯片（Grace Blackwell，SM121，128GB 统一内存，aarch64）在启动、内存、散热、带宽和精度方面有十个常见的故障模式。每个故障模式都命名为 G1–G10，以便通过编号进行检查——编号对于运行这些检查的工具至关重要。在长时间运行之前阅读本文，而不是在第六个小时之后。

## 何时使用此技能

- 训练运行失败无法启动，出现导入错误或无法指向真实原因的段错误。
- 运行时出现 OOM，而 `nvidia-smi` 仍然显示有剩余空间。
- 在运行中途吞吐量下降，而运行开始时一切正常。
- 在 GB10 上进行任何多小时或多轮次的作业之前。
- 将两个 Spark 连接在一起之前，选择并行策略之前。
- 在 Spark 主机的运行中选择 FP8 和 NVFP4 之间。

## 常见问题快速参考

| 编号 | 症状 | 解决方法 |
|---|---|---|
| G1 | 未定义符号 / 段错误 | cu130 轮或容器 |
| G2 | 使用了错误的 flash-attn 后端 | 跳过 pip 构建；在 NGC 上进行猴子补丁 |
| G3 | 尽管 OOM 但仍有剩余空间 | 删除页面缓存 |
| G4 | 吞吐量下降 / 重启 | 预期约 100W 持续上限 |
| G5 | 内存限制步骤缓慢 | 预算 180–192 GB/s |
| G6 | 运行中途缓存被驱逐 | 一次一个 GPU 服务器 |
| G7 | NVFP4 慢于 FP8 | 除非 `sm_121a`，否则保持 FP8 |
| G8 | 播放指南完全失败 | 检查上游问题 |
| G9 | 安装后环境损坏 | 使用容器 |
| G10 | 2-Spark TP 挂起 | 仅 DDP/FSDP，从不使用 TP |

## 十个常见问题

### G1：CUDA 12/13 ABI 不匹配

- **症状：** `ImportError: 未定义符号` 指向 CUDA 函数，或在第一个 `.cuda()` 调用时发生段错误。
- **原因：** 大多数 PyPI 轮子链接 `libcudart.so.12`；Spark 提供 CUDA 13。pip 从不检查 CUDA ABI，因此仅在导入或第一个内核启动时才会出现。
- **检查：** `references/gotcha-checks.md` G1 — 轮子的 CUDA 构建标签。
- **解决方法：** 从 `download.pytorch.org/whl/cu130` 重新安装，或使用匹配的容器。

### G2：flash-attn — 跳过 pip 构建，观察 Unsloth 的自动检测

- **症状：** `pip install flash-attn` 仍然失败/挂起。Unsloth 也可能在未明确请求 SDPA 的情况下静默训练 flash-attn。
- **原因：** 没有 aarch64/sm_121 轮子用于裸 pip — 但 NGC 容器包含可工作的 SM121 flash-attn，Unsloth 自动优先选择它，并丢弃 `attn_implementation="sdpa"`。
- **检查：** `references/gotcha-checks.md` G2 — flash-attn 是否已存在且可工作。
- **解决方法：** 裸 pip — 跳过 flash-attn，使用 SDPA（不变）。在 NGC 上 — 唯一可靠的覆盖是在 `references/gotcha-checks.md` G2 中的猴子补丁。

### G3：UMA 在 128GB 以下 OOM

- **症状：** 在模型加载/训练期间出现 OOM，而 `nvidia-smi` 仍然报告 128GB 上限以下的空闲内存 — 或在某些设置中，直接显示 `[N/A]` 而不是数字。
- **原因：** mmap 和 CUDA 分配器在 safetensors 加载期间双计数页面；QLoRA 由于去量化添加了临时分配，可能比 bf16 更早 OOM。
- **检查：** `references/gotcha-checks.md` G3 — 阅读 `free -g` 和 `/proc/meminfo`，而不是 `nvidia-smi`。
- **解决方法：** 使用 `sync; echo 3 > /proc/sys/vm/drop_caches` 删除页面缓存 — 需要 root 权限，是运行之间的重置，而不是训练中途步骤。

### G4：散热节流

- **症状：** 在多小时运行中途吞吐量下降，或在持续负载下设备自动重启。
- **原因：** 持续功耗上限约为 100W，而不是 240W 的额定值；长时间运行会推入该上限并节流，有时会重启。
- **检查：** `references/gotcha-checks.md` G4 — 样本的 `nvidia-smi --query-gpu=temperature.gpu,power.draw`。
- **解决方法：** 如果在 240W 以下时功耗达到平台期而温度上升，将节流视为原因；改善散热或限制运行长度。

### G5：带宽上限

- **症状：** 内存限制型工作负载，尤其是解码密集型 RL 循环，在预期吞吐量以下达到平台期。
- **原因：** 273 GB/s 是一个规格上限，而不是持续值；测量带宽运行 180–192 GB/s。
- **检查：** `references/gotcha-checks.md` G5 — 观测到的步骤时间与测量范围，而不是规格。
- **解决方法：** 预算 180–192 GB/s 的吞吐量；修订基于 273 GB/s 的计划。

### G6：全局 UMA 资源争用

- **症状：** 进程的 KV 缓存/权重在运行中途被静默驱逐，其自己的日志中没有 OOM。
- **原因：** 统一内存是一个全局池；无上限或接近上限的进程会与任何其他进程竞争并驱逐它。小而受限制的工作负载不会 — <4GB 的 LoRA 可以与 vLLM（`gpu-memory-utilization<=0.5`）共存。
- **检查：** `references/gotcha-checks.md` G6 — 其他 GPU 居住进程和是否受限制。
- **解决方法：** 对无上限或接近上限的工作负载适用“一个重负载规则” — 首先限制或停止无关服务器。一个小而受限制的工作负载无需停止。

### G7：SM121 上 NVFP4 慢于 FP8

- **症状：** 将推理工作负载从 FP8 切换到 Spark 上的 NVFP4 使其变慢，而不是变快。
- **原因：** SM121 除非内核针对 `sm_121a`，否则缺少 `cvt.e2m1x2`；没有它，NVFP4 运行速度慢约 32%。
- **检查：** `references/gotcha-checks.md` G7 — 能力报告 `(12, 1)`；构建是否针对 `sm_121a`？
- **解决方法：** 除非构建针对 `sm_121a`，否则保持 FP8。

### G8：过时的官方播放指南

- **症状：** 按照官方 DGX Spark 播放指南仍然失败，没有任何本地配置错误可以解释。
- **原因：** 官方播放指南以前可能已损坏；堆栈的移动速度比文档快。
- **检查：** `references/gotcha-checks.md` G8 — 播放指南仓库的最新问题。
- **解决方法：** 在信任昂贵运行的食谱之前，检查 `github.com/NVIDIA/dgx-spark-playbooks` 的问题。

### G9：优先使用容器，而不是裸 pip

- **症状：** 昨天可以工作的裸 pip 环境在无关的 `pip install` 后损坏，或者两个“相同”的环境表现不同。
- **原因：** 裸 pip 允许 Triton、xformers 和 transformers 独立漂移；没有任何东西将它们固定到 GB10 的 SM121 目标。
- **检查：** `references/gotcha-checks.md` G9 — 容器或裸 pip？
- **解决方法：** 优先使用 NGC 容器（参考 `spark-environment-setup` 获取标签指导）或 Unsloth 的容器。如果无法避免裸 pip，请遵循 NVIDIA 安装顺序，包括 Unsloth 上的 `--no-deps`。

### G10：双 Spark 仅限 DDP/FSDP

- **症状：** 跨两个 Spark 的张量并行启动挂起、运行远慢于单 Spark，或出错。
- **原因：** ConnectX-7 对于梯度/参数同步（DDP、FSDP）足够快，但对于 TP 的细粒度流量太薄。
- **检查：** `references/gotcha-checks.md` G10 — 配置的并行策略。
- **解决方法：** 在双 Spark 设置中，选择 DDP 或 FSDP，从不使用张量并行 — TP 仅在此为单节点。

## 快速排查

在运行任何其他操作之前运行的最便宜的检查：

```bash
python3 -c "import torch; print(torch.version.cuda)"  # 预期 13.x (G1)；NGC 构建有 no +cu130 标签 — 那不是失败
```

```python
import torch; print(torch.cuda.get_device_capability())  # 预期 (12, 1) (G7)
```

```bash
{ [ -f /.dockerenv -o -f /run/.containerenv ] || grep -qE 'docker|containerd' /proc/1/cgroup; } 2>/dev/null && echo container || echo unknown  # G9
```

`assets/preflight.sh` 运行 G1、G3、G4、G7、G9 并以固定格式生成每个常见问题的输出行：首先 G 编号，然后自动化的 PASS/FAIL/WARN，不可用时为 SKIP，或 `INFO:` 用于原始读取（G3、G4）。完整命令：
`references/gotcha-checks.md`。另见
`spark-environment-setup` 假设的工作环境。
