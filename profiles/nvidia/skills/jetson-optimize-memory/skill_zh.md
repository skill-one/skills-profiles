# jetson-optimize-memory

内存按启动顺序分为四个层级（更高行=更早启动，更接近硬件）：

| 层级 | 内容 | 关键文件 |
|---|---|---|
| MB1 BCT | 固件预留区域 | 每个模块的 DTS |
| MB2 BCT | 固件加载 + AST 控制 | 每个模块的 DTS |
| 内核 DTS | 预留内存和驱动绑定 | 每个模块的 DTS |
| SWIOTLB | DMA 回环池大小 | `<module>.conf.common` (`CMDLINE_ADD`) |

**关键规则：**

- 仅验证 **场景配方** 中的场景。拒绝不在该表格中的任何禁用预留区域/集群/节点的请求。
- **清零预留区域需要同时：禁用集群的加载控制 AND 移除引用它的 AST。**
- **为配方中的每个集群发出明确的覆盖设置**，无论源代码 `#ifdef`/`#else` 看起来如何。验证合并后的二进制文件。
- **GPU SW 堆栈必须与芯片匹配**：T234 -> nvgpu, T264 及以后版本 -> OpenRM。遵循 `target-platform-contract.md` 中的共享派生平台规则；在出现不匹配时停止，而不是猜测。
- 不要将 SWIOTLB 设置为 0 — 某些外设无法使用 IOMMU。

---

## 场景配方

| 关键词 | MB1 BCT 预留区域 | MB2 BCT | 内核 DTS |
|---|---|---|---|
| `headless` | DCE 系列（见芯片表） | DCE `auxp_controls` + DCE AST(s) | `display@<addr>`（如果暴露则包含 `dce@<addr>`）→ 禁用 |
| `no-camera` | RCE/VI/ISP 系列 | RCE `auxp_controls`（每个实例）+ RCE AST(s) | 推荐：VI/ISP/NVCSI → 禁用 |

### 芯片特定预留区域

| 场景 | T234 (Orin) | T264 (Thor) |
|---|---|---|
| `headless` | `CARVEOUT_BPMP_DCE`, `CARVEOUT_DCE`, `CARVEOUT_DCE_TSEC`, `CARVEOUT_TSEC_DCE`, `CARVEOUT_DISP_EARLY_BOOT_FB` | `CARVEOUT_DCE`, `CARVEOUT_TSEC_DCE`, `CARVEOUT_HPSE_DCE`, `CARVEOUT DISP_EARLY_BOOT_FB` |
| `no-camera` | `CARVEOUT_RCE`, `CARVEOUT_CAMERA_TASKLIST` | `CARVEOUT_RCE`, `CARVEOUT_RCE1`, `CARVEOUT_RCE_RW`, `CARVEOUT_VI_TASKLIST`, `CARVEOUT_VI1_TASKLIST`, `CARVEOUT_ISP_TASKLIST`, `CARVEOUT_ISP1_TASKLIST` |

> **启动后**：`headless` → `sudo systemctl set-default multi-user.target`。

---

## MB1 BCT 预留区域覆盖

文件：`Linux_for_Tegra/bootloader/generic/BCT/tegra<芯片>-mb1-bct-misc-<模块>.dts`
（例如：`tegra234-mb1-bct-misc-p3767-0000.dts` 用于 Orin Nano，
`tegra264-mb1-bct-misc-p3834-0008-p4071-0000.dts` 用于 Thor）。

对每个预留区域，在现有的 `carveout` 节内添加：

```dts
aux_info@<CARVEOUT_NAME> {
    pref_base = <0x0 0x0>;
    size      = <0x0 0x0>;
    alignment = <0x0 0x0>;
};
```

---

## MB2 BCT 集群 + AST 覆盖

文件：`Linux_for_Tegra/bootloader/generic/BCT/tegra<芯片>-mb2-bct-misc-<模块>.dts`
（包含 `tegra<芯片>-mb2-bct-common.dtsi`）。

对每个目标集群：

1. 覆盖 `auxp_controls@<index>`：
   ```dts
   auxp_controls@<index> {
       enable_init    = <0>;
       enable_fw_load = <0>;
       enable_unhalt  = <0>;
   };
   ```
2. `/delete-node/ auxp_ast_config@<idx>;`

在 `common.dtsi` 中查找索引：`auxp_controls@N` 带有命名其集群的注释；`auxp_ast_config@N` 有 `ast_region` 子节点，其 `carveout = <CARVEOUT_…>;` 行标识了所有者。

---

## 内核 DT 预留内存

```sh
DTB=Linux_for_Tegra/kernel/dtb/<平台-dtb名>.dtb
dtc -I dtb -O dts -o /tmp/platform.dts $DTB
# 编辑：目标节点上的 status = "disabled"
dtc -I dts -O dtb -o $DTB /tmp/platform.dts
```

**显示** — 禁用 `display@<addr>`，如果作为单独的内核节点暴露，则禁用 `dce@<addr>`。

**相机** — 在 `host1x@<addr>` 下，禁用 BSP 上存在的 `vi*` / `isp*` / `nvcsi` 中的任意一个（仅发出存在的节点）：

在反编译的 DTS 中定位显示控制器节点并禁用它。节点的单元地址是芯片特定的 — 通过 `compatible` 字符串查找（例如 `nvidia,tegra234-display`）而不是硬编码地址。

```dts
host1x@<addr> {
    vi0@<addr>   { status = "disabled"; };
    vi1@<addr>   { status = "disabled"; };
    isp@<addr>   { status = "disabled"; };
    isp1@<addr>  { status = "disabled"; };
    nvcsi@<addr> { status = "disabled"; };
};
```

---

## SWIOTLB DMA 回环池

NVIDIA IOMMU 覆盖外设 DMA，因此 SWIOTLB 很少使用。编辑 `CMDLINE_ADD`（**永远**不要 `CMDLINE`）在 `Linux_for_Tegra/<模块>.conf.common`：

```sh
# 总字节数 = swiotlb_value × 2048；4 MiB 池：
CMDLINE_ADD="... swiotlb=2048"
```

---

## 覆盖验证（强制要求）

在每次修补的 MB1/MB2 BCT `.dts` 后，使用 `bootloader/tegraflash_impl_t<芯片>.py` 中 `bct_flags.append(...)` 的相同 `-D…` 标志重新生成 BSP 的编译 + 反编译：

```sh
gcc -E -nostdinc -x assembler-with-cpp \
    -DENABLE_<FLAG_1> -DENABLE_<FLAG_2> \
    -I bootloader -I bootloader/generic/BCT \
    -o /tmp/cpp.dts <patched-bct.dts>
dtc -q -I dts -O dtb -o /tmp/cpp.dtb /tmp/cpp.dts
dtc -q -I dtb -O dts /tmp/cpp.dtb | less
```

在合并输出中确认：
- 每个清零的 `aux_info@<NAME>`（或宏扩展后的 `aux_info@<id>U`）具有 `size = <0x0 0x0>` 和 `pref_base = <0x0 0x0>`。
- 每个禁用的 `auxp_controls@<idx>` 的所有三个 `enable_*` 字段 `<0>`。
- 每个 `/delete-node/` 的 `auxp_ast_config@<idx>` 不存在。

---

## 验证（在已启动目标上）

```sh
sudo cat /proc/iomem | grep -iE 'nv-reserved|cma|fb|carveout'
ls /proc/device-tree/reserved-memory/
dmesg | grep -iE 'firmware|carveout|bpmp|reserved|fail|error' | head -20
free -m
```

| 场景 | Sysfs | dmesg grep |
|---|---|---|
| 显示关闭 | `ls /sys/class/drm/`（空） | `tegra-drm\|nvdisplay\|dce\|host1x\|fb0` |
| 相机关闭 | `ls /dev/video* 2>/dev/null`（无） | `rce\|nvcsi\|tegra-camera\|vi0\|vi1\|isp` |
| SWIOTLB 缩小 | `cat /sys/kernel/debug/swiotlb/io_tlb_nslabs` 与 cmdline 匹配 | `swiotlb` |

对于 SWIOTLB：`/proc/cmdline` 必须包含 `swiotlb=<值>`，并且 `watch -n5 cat /sys/kernel/debug/swiotlb/io_tlb_used` 必须保持在 `io_tlb_nslabs` 以下 — 如果超出，恢复原始 `CMDLINE_ADD` 并重新刷写 `kernel-dtb`。

## 目的

在 Jetson 部署跳过显示、相机或其他外设时，裁剪参考 BSP 中启用的未使用 DRAM 预留区域，释放这些字节供应用程序使用。始终按启动顺序编辑四个层级，以便早期阶段的裁剪不会优先于后期阶段的缩减。

## 前提条件

- 根据 `../../context/target-platform-contract.md` 解析的活动目标配置文件。
- BSP 图像提取并源代码树初始化完成 (`/jetson-init-image`, `/jetson-init-source` 完成)。
- 对于 headless / no-camera 配方：确认工作负载确实不需要显示或相机。

## 限制

- 仅显示验证过的配方（`headless`, `no-camera`, `swiotlb`） — 配方集外的自定义子系统禁用被拒绝。
- SWIOTLB 缩小受峰值 DMA 流量限制 — 超出新的 `io_tlb_nslabs` 需要恢复更改。
- BPMP-DTB 编辑仅在 Customize + Build + Deploy 运行后出现在覆盖跟踪器中；这项技能不会自行刷写。

## 故障排除

- **MB1 BCT 裁剪禁用后启动失败** — 恢复原始的 misc DTS 并重新刷写；缺少的裁剪对于活动 SoC 是必需的。
- **`io_tlb_used` 超出 `io_tlb_nslabs`** — 恢复 `swiotlb=` 在 `CMDLINE_ADD` 中并重新刷写内核 DTB 分区。
- **回收的增量小于预期** — 验证配方是否真正匹配部署（例如显示仍然连接）；使用此文件中的 `dmesg | grep -iE 'firmware|carveout'` 检查进行确认。
- **验证 `dmesg` 显示禁用子系统仍在探测** — 变更可能未通过 `bsp_image` 推广；重新运行 `/jetson-promote-image`。
