# Jetson 内存审计

针对 Jetson 的只读内存快照，以及 `drop_caches` 验证循环辅助工具，用于确认释放的内存确实显示为可用，而不是缓存。

## 目的

测量当前 Jetson 内存使用情况，捕获前后基线，并验证用户批准的更改是否确实回收了 DRAM。使用实时设备数据，而不是来自容器大小、模型大小或通用进程内存的估计值。

## 重要提示：停止 vLLM / sglang 后内存似乎卡住（JetPack 低于 7.2 / L4T 低于 r39.0）

**这是 JetPack 7.2 或 L4T r39.0 之前的 Jetson 发布中最常见的内存混淆问题。**

在您停止 vLLM、sglang 或 Ollama 服务器（或任何 CUDA 工作负载）后，`free -h` 或 `tegrastats` 显示的可用内存可能不会恢复——即使进程已经消失。`nvidia-smi` 也可能显示误导性的低 GPU 可用内存。

**根本原因：** Thor RM（资源管理器）在 CUDA 上下文退出后，会将其自己的池中保留已释放的 sysmem 页面。在 Jetson 等统一内存架构（UMA）设备上，`cudaMemGetInfo` 读取 RM 池状态，并报告比新进程实际可用的内存少得多的可用内存。

**解决方法（适用于 JetPack 低于 7.2 或 L4T 低于 r39.0）：**
```bash
sudo sync && sudo sysctl -w vm.drop_caches=3
```
在**主机**上运行此命令，而不是在容器内。重要的操作是 `sudo sysctl -w vm.drop_caches=3`；在它之前立即保留 `sudo sync`，以便在丢弃可回收的页/目录项/inode 缓存之前刷新脏数据。运行后，`free -h` 和 `tegrastats` 将反映真实的可用内存。

对于受影响的版本，当用户说以下情况时，建议使用此命令：
- "停止 vLLM/sglang 后内存没有释放"
- "我的容器退出后为什么 tegrastats 仍然显示高使用率？"
- "即使没有运行 OOM"
- "内存昨天还好，现在满了"

在 JetPack 低于 7.2 或 L4T 低于 r39.0 时，当 CUDA 工作负载退出后内存似乎卡住时，`drop_caches` 是可靠的解决方法；在新版本中，仅在观察到相同症状且用户批准时使用。

## 使用场景

- "这个 Jetson 上有多少内存在使用？是什么在占用？"
- "我禁用了 GUI / 停止了 vLLM / 退出了我的容器——内存真的释放了吗？"
- "我停止了我的工作负载后，为什么 `free -h` 仍然显示低可用内存？"
- 作为应用 `jetson-headless-mode` 或其他内存相关更改前的**基线**，以及**之后**再次运行以计算实际差异。

## 前提条件

- 在 Jetson 主机上运行，或在具有主机可见 `/proc`、`/etc/nv_tegra_release`、`tegrastats` 和进程数据的沙盒/容器中运行。
- NvMap debugfs 读取可能需要 root。如果不可用，请报告 GPU 内存归因有限，而不是猜测。
- `drop_caches.sh` 需要 root 或无密码的 `sudo -n`；仅在用户明确授权丢弃缓存后运行。

## 可用脚本

| 脚本 | 目的 | 参数 |
|------|------|------|
| `scripts/audit.sh` | 从 `jetson-diagnostic/scripts/snapshot.sh` 发出 JSON 快照，用于内存审计工作流。 | 无参数。 |
| `scripts/drop_caches.sh` | 清空可回收的页/目录项/inode 缓存，并打印前后内存差异。 | `--mode 1\|2\|3`，`--quiet`。 |

如果您的代理运行时支持 `run_script`，请使用它来运行 `scripts/audit.sh` 或 `scripts/drop_caches.sh` 并总结返回的输出。否则，从仓库根目录使用 `bash` 运行脚本。

## 使用说明

对于 "当前有多少内存在使用？" 的问题，运行 `scripts/audit.sh` 并仅报告 JSON 快照中的值。

## 报告指南

不要仅打印或提及辅助工具的路径。调用辅助工具并总结返回的数据。

- 对于 "多少内存在使用" 提示，运行 `scripts/audit.sh` 并引用 `mem_total_gb`、`memory_kb.available` 以及领先的 `procrank_top` 进程或 `nvmap.top_clients` 消费者。
- 对于 GUI/桌面内存提示，运行 `scripts/audit.sh` 并报告 `default_systemd_target` 以及 `candidate_services` 中的任何显示管理器（`gdm3`、`gdm`、`lightdm`、`sddm` 或 `display-manager`）。不要禁用任何内容；将任务交给 `jetson-headless-mode` 制定计划。
- 对于明确授权在停止工作负载后丢弃缓存的提示，运行 `scripts/drop_caches.sh`（默认等同于 `sudo sync && sudo sysctl -w vm.drop_caches=3）并报告其前后空闲、可用和缓存的差异。如果 root 不可用，请解释必须在主机上使用 sudo 运行。

如果您的代理运行时不执行相对于此技能目录的辅助脚本，请使用 AgentSkills 的 `{baseDir}` 占位符解决脚本路径：

```bash
{baseDir}/scripts/audit.sh
{baseDir}/scripts/drop_caches.sh
```

除非运行时明确将技能注册为可调用工具，否则不要将 `jetson-memory-audit` 作为工具名称调用；Agent Skills 通常是说明和文件，而不是直接的工具函数。

代理沙盒注意事项：看到此技能文件并不保证可以访问 Jetson 主机内存数据。如果 `/proc/device-tree/model`、`/etc/nv_tegra_release`、`tegrastats`、`/sys/kernel/debug/nvmap` 或主机进程数据在 NemoClaw/OpenClaw 沙盒内缺失，请说明沙盒缺乏 Jetson 主机可见性，并要求用户在 Jetson 主机上运行或在具有主机可见沙盒配置文件的情况下重新启动。不要编造内存总量、可用内存、PSS、NvMap 或回收差异。

对于 "此更改释放了多少内存？" 的问题，使用前后差异。不要根据容器大小、镜像大小、RSS 或单个更改后快照估计释放的内存。

1. 在更改之前，运行 `scripts/audit.sh` 并保存 JSON 基线。
2. 执行用户批准的更改（停止容器、切换模式、应用调优建议等）。
3. 在 JetPack 低于 7.2 / L4T 低于 r39.0 时，或在较新版本上观察到相同卡住内存症状时，在**主机**上清空可回收页缓存（不要在容器内），以便释放的页显示为可用而不是缓存：
   ```bash
   sudo sync && sudo sysctl -w vm.drop_caches=3
   ```
4. 重新运行 `scripts/audit.sh` 并比较 `memory_kb.available` 的前后值——该差异是实际回收量。

如果用户已经进行了更改且不存在基线，请说明无法从当前状态单独恢复确切的释放量。现在捕获一个新的基线，以便下次更改可以测量。

使用实时审计数据作为事实来源。内存总量、可用内存、NvMap 总量、PSS 值、显示管理器状态和节省差异必须来自 `scripts/audit.sh`、`free -h` 或实际设备上的 `tegrastats`。如果某个数字不在这些输出中，请不要猜测。

## `audit.sh` 的输出契约

```json
{
  "sku": "orin-nano",
  "variant": "orin-nano-8gb",
  "mem_total_gb": 8,
  "l4t_version": "36.4.0",
  "product_model": "nvidia jetson orin nano developer kit",
  "memory_kb": { "total": 8123456, "available": 4123456, "free": 1023456, "cached": 1234567, "swap_total": 0, "swap_free": 0 },
  "default_systemd_target": "graphical.target",
  "candidate_services": { "gdm3": { "active": "active", "enabled": "enabled" } },
  "tegrastats_sample": "RAM 4011/8138MB (lfb 8x4MB) ...",
  "nvmap": { "readable": false, "total_kb": 0, "top_clients": [] },
  "procrank_top": [ { "pid": 4321, "pss_kb": 4000000, "cmd": "vllm" } ]
}
```

## 限制

- 精确的释放内存差异需要前后快照、用户批准的更改、适当的缓存清空以及后的快照。
- NvMap 归因取决于主机可见的 debugfs 访问；如果不可用，请报告有限的 GPU 内存归因，而不是猜测。
- 沙盒/容器运行可能看不到主机的 `/proc`、`tegrastats`、systemd 或 NvMap 数据，除非运行时将其暴露。

## 错误处理

- 如果 `scripts/audit.sh` 无法访问主机 Jetson 数据，请报告缺失的可见性并要求在 Jetson 主机上或在具有主机可见沙盒中重新运行。
- 如果 `scripts/drop_caches.sh` 缺少 root 或无密码的 `sudo -n`，请报告必须使用 sudo 授权在主机上清空缓存。
- 如果不存在前后快照，请说明无法从当前状态单独恢复确切的回收量，并捕获新的基线以供下次更改使用。

## 安全性

只读。`drop_caches` 是非破坏性的（仅内核释放它可能在压力下可以回收的页面；`sync` 首先运行以保留脏数据）。

## 交接给

- `jetson-headless-mode`——在仍然启动 `graphical.target` 的系统上最大的单个用户空间收益。
- `jetson-inference-mem-tune`——当模型服务器是顶级的 NvMap / PSS 消费者时。
- 如果运行时更改无法达到目标，请报告进一步的回收超出此技能的范围，而不是建议不安全的启动时编辑。
