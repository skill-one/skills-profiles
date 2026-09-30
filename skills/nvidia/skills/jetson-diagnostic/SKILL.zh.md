---
name: jetson-diagnostic
description: 只读的Jetson健康快照，包含身份、内存、GPU、散热、电源、存储、服务和顶级进程。
---

# Jetson 诊断

对正在运行的 Jetson 设备的统一、易于代理理解的视图。取代了需要记住 `tegrastats`、`jtop`、`procrank`、`/sys/kernel/debug/nvmap`、`nvpmodel`、`free`、`swapon`、`df` 和 `systemctl list-units` 哪个产生哪部分真相的需求。

## 目的

从 Jetson 主机捕获只读的健康快照，以便代理可以使用实时数据而不是猜测来回答设备身份、内存、GPU、散热、功耗、存储和服务状态问题。

## 何时使用

当用户询问时激活：

- "这是什么 Jetson？什么 SKU？多少内存？"
- "这个 Jetson 上现在在运行什么？"
- "我的 Jetson 为什么慢 / 热 / 内存不足？"
- "给我 GPU / CPU / 功耗使用的快照。"
- "我的 tegrastats 输出是什么意思？"
- "哪些服务正在运行我可以关闭？"
- 用户已安装 `jetson-memory-audit`、`jetson-headless-mode`、`jetson-inference-mem-tune`、`jetson-llm-benchmark`、`jetson-llm-serve` 或 `jetson-package`，并在运行它们之前需要基线测量。

不要使用此技能来更改功耗模式、丢弃缓存、停止服务、安装软件包或提供模型。报告观察到的状态，然后转交给动作导向的技能。

## 前置条件

- 在 Jetson 主机上运行，或在具有主机可见 Jetson 系统路径和进程数据的沙盒/容器中运行。

## 可用脚本

| 脚本 | 目的 | 参数 |
|------|------|------|
| `scripts/snapshot.sh` | 发出包含身份、内存、GPU、散热、功耗、磁盘、顶级进程和候选服务的全功能 JSON 快照。 | `--human`、`--tegra-secs N`、`--top-procs N`。 |
| `scripts/mem_summary.sh` | 发出紧凑的人类可读的 RAM/GPU/交换总结。 | `--short`、`--watch`、`--interval N`。 |
| `scripts/detect_jetson.sh` | 导出或打印此存储库的规范 Jetson SKU/代数/产品线字段。 | 无参数。 |

如果你的代理运行时支持 `run_script`，请使用它来运行 `scripts/snapshot.sh` 或 `scripts/mem_summary.sh` 并总结返回的输出。否则，从存储库根目录使用 `bash` 运行脚本。

## 说明

1. 运行 `scripts/snapshot.sh` 获取全功能 JSON 视图（首选默认值）。
2. 对于快速的人类可读内存行，运行 `scripts/mem_summary.sh`。
3. 要解释用户粘贴的 tegrastats 行，请参阅 `references/tegrastats-fields.md`。
4. 要解释 NvMap 客户端输出，请参阅 `references/nvmap-clients.md`。

## 报告指南

在总结设备状态之前运行匹配的辅助脚本，并仅报告该脚本返回的字段。如果直接执行被运行时阻止，请使用 `bash {baseDir}/scripts/<script-name>` 而不是尝试修改文件来运行它。

- 对于 "这是什么 Jetson" 问题，引用 `product_model` 或 `sku`、`variant`、`l4t_version` 和 `mem_total_gb`。
- 对于 "慢和热" 问题，运行 `snapshot.sh` 并总结症状的两方面：`thermal_c` 用于热量，加上 `top_processes`、`gpu_processes`、`nvmap.top_clients` 或 `gpu_source` 用于负载。以具体的转交结束，例如 `jetson-memory-audit`、`jetson-headless-mode` 或 `jetson-inference-mem-tune`。
- 对于 "哪个进程在使用内存" 问题，运行 `snapshot.sh` 并命名领先进程为 `pid <number>`、`cmd` 及其 `pss_kb` / MiB 值。如果 NvMap GPU 内存是相关信号，还引用 `gpu_source` 和顶级的 `nvmap.top_clients` 或 `gpu_processes` 条目。

如果你的代理运行时不自动执行相对于此技能目录的辅助脚本，请使用 AgentSkills 的 `{baseDir}` 占位符解决脚本路径：

```bash
{baseDir}/scripts/snapshot.sh
{baseDir}/scripts/mem_summary.sh
```

除非运行时明确将技能注册为可调用的工具；Agent Skills 通常是说明加上文件，而不是直接的工具函数。不要将 `jetson-diagnostic` 作为工具名称调用；Agent Skills 是说明加上文件，而不是直接的工具函数。

所有脚本都源自动规范的平台检测器 `skills/jetson-diagnostic/scripts/detect_jetson.sh`（导出 `JETSON_SKU`、`JETSON_GENERATION`、`JETSON_PRODUCT_LINE`、`JETSON_VARIANT`、`JETSON_MEM_GB`、`JETSON_L4T_VERSION`、`JETSON_PRODUCT_MODEL`）。其他技能可以源此检测器而不是重复 Jetson 识别逻辑。以平台外的补救信息退出 2。

## 限制

- 看到此技能文件并不保证可以访问 Jetson 主机硬件。如果在 NemoClaw/OpenClaw 沙盒中缺少 `/proc/device-tree/model`、`/etc/nv_tegra_release`、`tegrastats`、`nvpmodel`、`nvidia-smi` 或 `/sys/kernel/debug/nvmap`，请说明沙盒缺乏 Jetson 主机可见性，并要求用户在 Jetson 主机上运行或使用主机可见沙盒配置文件重新启动。
- NvMap debugfs 通常需要 root，因此无特权的运行可能会报告 `gpu_source: "none"` 或不完整的 `nvmap` 字段。
- 此技能仅报告观察到的状态。当工具缺失或无法访问时，不要编造内存、GPU、散热、服务或回收数据。

## 错误处理

- 如果辅助脚本以平台外退出，请报告当前环境不是 Jetson 主机或缺乏主机可见性；不要用通用 Linux 值替换。
- 如果 `tegrastats`、`nvpmodel`、`nvidia-smi` 或 NvMap debugfs 不可用，请保留 JSON 中相应的 `null`、`false` 或空字段，并解释哪个信号受限。
- 如果 `snapshot.sh` 发出格式错误的 JSON，请报告原始失败并修复辅助输出后重新运行；不要手动编辑合成的设备快照。

## `snapshot.sh` 的输出契约

```json
{
  "sku": "orin-nano",
  "generation": "orin",
  "product_line": "orin-nano",
  "variant": "orin-nano-8gb",
  "mem_total_gb": 8,
  "l4t_version": "36.4.0",
  "product_model": "nvidia jetson orin nano developer kit",
  "memory_kb": { "total": 8123456, "available": 4123456, "swap_total": 0, "swap_free": 0, "cached": 1234567 },
  "tegrastats_sample": "RAM 4011/8138MB (lfb 8x4MB) ...",
  "thermal_c": { "CPU": 52.3, "GPU": 49.0, "AO": 47.0 },
  "power": { "nvpmodel_id": 0, "nvpmodel_name": "MAXN" },
  "disk": [ { "mount": "/", "used_pct": 41 } ],
  "gpu_source": "nvmap:iovmm-clients",
  "gpu_devices": [],
  "gpu_processes": [],
  "nvmap": {
    "readable": true,
    "total_kb": 654321,
    "stats_total_bytes": 669985280,
    "top_clients": [ { "pid": 1234, "cmd": "vlm-server", "kb": 524288 } ]
  },
  "top_processes": [ { "pid": 4321, "cmd": "vllm", "pss_kb": 4000000 } ],
  "candidate_services": { "gdm3": { "active": "inactive", "enabled": "disabled" } }
}
```

`gpu_source` 指的是技能用来归因每个进程 GPU 内存的*特定*数据，以便调用者可以确切地知道这些数字代表什么：

- `"nvidia-smi:compute-apps"` — 来自 `nvidia-smi --query-compute-apps` 的每个进程 `used_memory` 值。在统一 `nvidia.ko` 堆栈上使用（今天 Thor 系列）。注意：在此堆栈上，`nvidia-smi` 的*设备级* `memory.used` 查询在某些 BSP 上返回 `[N/A]`，这就是为什么技能对每个进程列表求和而不是读取顶级总数。求和总数出现在 `gpu_processes[*].used_mib`。
- `"nvmap:iovmm-clients"` — 来自 `/sys/kernel/debug/nvmap/iovmm/clients` 的每个进程大小。在 `nvgpu` 堆栈上使用（今天 Orin 系列），其中 `nvidia-smi` 是一个存根，对每个计算/内存查询返回 `[N/A]`。每个进程条目出现在 `nvmap.top_clients`；内核端总数在 `nvmap.total_kb` 中，并且（当可读时）在 `nvmap.stats_total_bytes` 中。
- `"none"` — 没有可授权的来源可达。典型情况是在未特权的 `nvgpu`-堆栈 Jetson 上运行（`/sys/kernel/debug/nvmap` 下的 debugfs 需要 `sudo`）；使用 `sudo` 运行以填充 `nvmap` 字段。

代理应将显著部分呈现回用户（SKU、可用内存、每个 `gpu_source` 的顶级 GPU 消费者、最热区域、功耗模式），并提供深入特定细节的选项（`top_processes`、`gpu_processes` / `nvmap`、`services`）。

## 安全性

此技能是**只读**的。它不会更改 `nvpmodel`，不会运行 `jetson_clocks`，不会修改服务。要基于发现采取行动，请转交给：

- `jetson-memory-audit` — 专注内存快照 + 丢弃缓存验证循环
- `jetson-headless-mode` — 禁用 GUI + 辅助守护进程（安全、可逆）
- `jetson-inference-mem-tune` — 选择运行时 + 内存标志（vLLM / SGLang / llama.cpp / TensorRT Edge-LLM）
- `jetson-llm-serve` — vLLM 和相关 GHCR 镜像，使用 Jetson 默认值
- `jetson-llm-benchmark` — 可重复的延迟/吞吐量基准
- `jetson-package` — GHCR + Jetson AI Lab PyPI 索引与通用 ARM 轮

## 跨平台行为

| 系列                | 技能识别的变体                              | `tegrastats` | `nvidia-smi`          | `nvpmodel` | NvMap debugfs |
|---------------------|--------------------------------------------|--------------|-----------------------|------------|----------------|
| Jetson Thor         | `thor-t5000`、`thor-t4000`                 | 是           | 是（完整）            | 是        | 是（root）     |
| Jetson AGX Orin     | `orin-agx-64gb`、`orin-agx-32gb`、`orin-agx-industrial` | 是           | 是（存根，`nvgpu`）*  | 是        | 是（root）     |
| Jetson Orin NX      | `orin-nx-16gb`、`orin-nx-8gb`               | 是           | 是（存根，`nvgpu`）*  | 是        | 是（root）     |
| Jetson Orin Nano    | `orin-nano-8gb`、`orin-nano-4gb`            | 是           | 是（存根，`nvgpu`）*  | 是        | 是（root）     |

\* 在 GPU 由树内 `nvgpu` 内核驱动程序的 Jetson 上，`nvidia-smi` 二进制文件存在，但大多数字段（`Memory-Usage`、功耗、利用率、计算进程表）报告 `Not Supported` / `N/A`。为了在运行时决定信任哪个来源，脚本执行能力探测 — `nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits` — 并且仅在查询返回实际整数时使用 `nvidia-smi`。当它不返回时，脚本回退到 `/sys/kernel/debug/nvmap/iovmm/clients`，在 `nvgpu`-堆栈 Jetson 上，这是权威的每个进程 GPU 内存来源。

脚本优雅地处理每个工具的存在，并在无法访问工具时报告 `null` / `false`（典型情况是代理没有运行时所需的权限来访问 `/sys/kernel/debug`）。变体检测首先使用 `/proc/device-tree/model` 字符串（识别名称如 `T5000` / `T4000`），当模型字符串是通用时，回退到内存大小启发式方法。
