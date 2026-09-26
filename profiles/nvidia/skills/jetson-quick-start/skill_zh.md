# 快速入门 — BSP 自定义入口

`jetson-quick-start` 是一个调度器和输入表单。它不会下载、解压、实例化源代码、绑定文档或派生载体文件。它选择设置路径，收集核心答案，然后将这些答案交给实际工作的技能。

## 模式

不要在单独的提示中询问设置模式。将其作为核心快速入门问卷中的第一个字段，并按此固定顺序显示选项：

1. `自动设置`
2. `引导设置`
3. `使用现有工作区`

单独提供 `取消` 作为退出操作，而不是设置模式。

| 模式 | 使用场景 | 计划技能 |
|---|---|---|
| `自动设置` | 新工作区，网络可用 | target setup, `/jetson-download-bsp`, `/jetson-init-image`, `/jetson-init-source`, `/jetson-link-docs`, `/jetson-generate-kb`, 可选 `/jetson-derive-carrier` |
| `引导设置` | 用户已拥有路径、仓库或归档 | target setup, `/jetson-init-image`, `/jetson-init-source`, `/jetson-link-docs`, `/jetson-generate-kb`, 可选 `/jetson-derive-carrier` |
| `使用现有工作区` | BSP 图像、源树和文档已准备就绪 | target setup, 工作区验证, `/jetson-generate-kb`, 可选 `/jetson-derive-carrier`; 路由到仅用于缺失先决条件的 init 技能 |

目标设置意味着保持活动配置文件，通过 `/jetson-set-target` 切换，或通过 `/jetson-init-target` 创建一个。

## 流程

### 打印免责声明

在打开核心问卷或检查设置输入之前，精确打印一次此免责声明块：

```text
================================================================================
免责声明
这些技能帮助自动化 Jetson BSP 设置和自定义，但它们不能替代 NVIDIA 官方文档或工程评审。在接受之前，请评审生成的计划、命令、差异和提交信息。

烧录可能会擦除设备存储或使目标暂时无法启动。在执行部署步骤之前，请保留备份并验证活动目标、BSP 版本和硬件设置。
================================================================================
```

### 免责声明接受门

在打印免责声明后，立即打开一个单独的一问 `AskUserQuestions` 免责声明表单，并在执行任何其他操作之前等待用户提交的答案。不要使用纯文本聊天回复、推断默认值、先前的运行状态、活动配置文件、缓存答案或任何其他非 UI 信号来收集免责声明接受情况。

表单必须包含恰好一个问题：

1. `accept_disclaimer` — 提示： "接受免责声明并继续快速入门？" 选项：`accept_disclaimer` 和 `取消`。

仅将提交的 `accept_disclaimer` 选项视为接受。免责声明表单与核心问卷是分开的，并且不会取代四个路由关键的核心问题。

如果表单无法打开、不可用、被取消、返回未提交的答案集，或返回任何不是 `accept_disclaimer` 的答案，请立即停止，并报告只有在通过 `AskUserQuestions` 接受免责声明后才能继续快速入门。

### 强制问卷门

在接受免责声明后，`jetson-quick-start` 必须打开核心 `AskUserQuestions` 问卷，并在执行任何设置调度之前等待用户的提交答案。如果问卷无法打开、不可用、被取消或返回未提交的答案集，请立即停止，并报告在没有问卷的情况下无法继续快速入门。

不要通过使用现有活动配置文件、工作区状态、tarball 名称、缓存答案、版本兼容性或“明显”默认值来继续。在通过此门有提交的 `mode` 答案和标准化 `quick_start_prefill` 之前，不要调用下游技能。

### 调查状态

检查 `target-platform/active_target.yml` 和现有的 `target-platform/*.yaml` 配置文件。如果存在活动配置文件，请显示 `reference_devkit.name`、可选的 `custom_carrier.name` 和活动 `flash_config`。不要从 tarballs、repo 名称或文档标题中推断平台身份。

读取 [`../../references/bsp-platforms-catalogue.md`](../../references/bsp-platforms-catalogue.md) 并解析产品/芯片/SKU/烧录配置表中的每一行。此目录是完整 `active_platform` 问卷列表的来源。如果列表不完整，请更新目录；不要在快速入门中重复或修补平台列表。在快速入门预处理期间，不要读取 `jetson-init-target/SKILL.md` 或运行 init-target 流；下游目标创建仍由 `jetson-init-target` 拥有。

保持此调查轻量，以便核心问卷快速出现：读取目标配置文件指针/摘要，在需要时执行廉价的路径存在检查，并仅从官方存档中获取轻量级 Jetson Linux 版本元数据，以填充 `bsp_release` 选项。解析所有当前版本部分，而不仅仅是看似匹配所选平台的部分。不要扫描大型 BSP / 源 / 文档树、检查存档、生成 KB 内容或运行设置工具，直到用户提交核心问卷。为三种模式准备可能的计划；仅在表单提交后选择实际的下游计划。

### 打印平台参考列表

在打开 `AskUserQuestions` UI 之前，打印从 `bsp-platforms-catalogue.md` 解析的完整平台列表，并为此次运行提供稳定的数字索引：

```text
可用平台：
T234 - Orin
  1. Jetson AGX Orin 64GB | CVM P3701-0005 | CVB P3737-0000 | jetson-agx-orin-devkit.conf
  ...
T264 - Thor
  N. Jetson AGX Thor T5000 | CVM P3834-0008 | CVB P4071-0000 | jetson-agx-thor-devkit.conf
```

仅使用这些索引用于接下来的问卷。即使存在活动配置文件或单个明显匹配，也不要自动选择索引。

### 询问核心问卷

使用 `AskUserQuestions` UI 生成一个用于整个设置运行的点击选择核心问卷。不要使用纯文本提示、内联聊天问题、推断默认值或手动总结确认来收集快速入门答案。

这是一个硬门：不要跳过它，不要使用一个配置文件的快捷方式，并且不要从 `active_target.yml`、文件名、tarballs、repo 名称、版本兼容性、工作区状态、缓存答案或先前的运行中自动选择 `mode`、`active_platform`、`bsp_release` 或 `custom_carrier`。可以显示现有活动配置文件作为选项，但只有在用户提交 `AskUserQuestions` 表单后才会选择它。

由于 `AskUserQuestions` 最多可以问四个问题，核心表单必须只包含路由关键字段：

1. `mode` — `自动设置`、`引导设置`、`使用现有工作区` 或 `取消`。
2. `active_platform` — 使用打印的完整平台列表；遵循活动平台问题规则。
3. `bsp_release` — 从官方 Jetson Linux 存档为此次运行生成的最新全局具体版本候选快捷方式，按点数字顺序由新到旧排序，加上 `跳过`。保留每个官方版本标记的每个字符；具体标记可能有两个或三个数字组件，例如 `38.2`、`38.2.1`、`38.4` 或 `R36.4.4`。不要将 `38.2` 规范化为 `38.2.0`，也不要推断缺失的补丁组件。不要硬编码或缓存候选者。如果元数据获取缓慢或失败，仍然显示 `跳过` 和一个键入的具体版本选项。不要在快速入门中平台过滤此列表；至少包含每个当前主要版本线找到存档中的最新具体行。如果解析只返回一条主要版本线，将版本列表视为不完整，并回退到 `跳过` 加上键入输入，而不是显示部分候选列表。
4. `custom_carrier` — 如果所选/活动配置文件已经有一个自定义载体，提供 `keep_existing_custom_carrier`、`no_custom_carrier`、`add_custom_carrier` 和 `跳过`；否则提供 `no_custom_carrier`、`add_custom_carrier` 和 `跳过`。

用户提交此 `AskUserQuestions` 表单一次。只有在提交后，`mode`、活动平台、BSP 版本和自定义载体意图才能决定运行哪些下游设置技能以及哪些预填充答案被消耗或忽略。如果没有提交的表单结果，请停止；永远不要使用推断答案继续。`add_custom_carrier` 只是一个路由意图；载体名称、ID、SKU、修订版和自定义烧录配置仍然是下游拥有的。

使用共享的
[`用户输入提示样式`](../../context/bsp-customization-workflow.md#user-input-prompt-style)
渲染表单，并将提交的 UI 答案规范化为 `quick_start_prefill`。遵循共享的
[`quick_start_prefill` 合同](../../context/bsp-customization-workflow.md#quick_start_prefill-contract)。
活动平台问题规则：

- 在问卷之前打印完整索引平台列表。
- 明确选择是每个芯片系列组的第 1 行，标记为完整列表索引和产品名称，例如 `Index 1 — Jetson AGX Orin 64GB`。
- 对于所有其他平台，用户选择 `输入一些内容` 并输入打印列表中的数字索引。`输入一些内容` 必须是工具的内置自由形式行，而不是自定义明确选择。
- 提示文本： "选择一个平台快捷方式，或选择输入一些内容并输入上面打印的完整平台列表中的数字索引。输入跳过以跳过平台选择，并让下游设置稍后询问。"
- 只有平台快捷方式可以是明确选择。不要添加 `跳过`、`其他` 或自定义手动输入选择；`跳过` 必须通过内置的 `输入一些内容` 路径键入。不要在提示文本中将 `输入一些内容` 释义为 `其他`。
- 不要在此处解析烧录配置变体；将选定的目录行传递给 `jetson-init-target`，后者拥有验证和烧录配置选择。

每个非 `跳过` 答案必须是明确的，并且可以直接被拥有的下游技能消耗；使用 `跳过` 表示任何未知内容。BSP 版本答案必须是一个具体版本标记，可选地以 `R` 开头，并具有两个或三个数字组件（例如 `R38.4`、`38.2`、`38.2.1` 或 `36.4.4`）。不要将 `R38.x` 或“固定一个较新版本”等系列占位符视为可接受；使用 `跳过`。在传递 `quick_start_prefill.download.bsp_release` 时，保留用户的/源标记。

图像路径、源路径、文档路径、载体详细信息、仓库覆盖、工具链选择和文档绑定是非核心设置细节。留给拥有的下游技能处理。下游设置技能应在安全时使用文档默认值而不询问，仅在冲突、覆盖、不兼容的版本、缺失的工件或用户请求的覆盖时询问。

对于自动设置，`/jetson-download-bsp` 负责列出所选平台支持的所有 BSP 版本，并在平台/BSP 不兼容时发出警告。快速入门可以转发请求的全局候选者或键入版本，但它不会验证支持或覆盖兼容性决策。

### 构建预填充捆绑包

仅规范化明确的非 `跳过` 答案，并将它们保存在内存中：

```yaml
quick_start_prefill:
  mode: 自动设置 | 引导设置 | 使用现有工作区
  target: { active_platform, custom_carrier }
  download: { bsp_release }
```

省略任何跳过的字段，省略没有核心答案的所有者子集。仅验证足够避免明显的错误路由，例如空白模式或 BSP 占位符。下游默认值是技能行为，而不是预填充字段。不要编造缺失的标识值，也不要从快速入门中写入配置文件块。

### 调用下游技能

根据 `quick_start_prefill.mode`、目标状态和先决条件检查构建下游计划。在调用下游技能之前，打印一个非阻塞执行计划摘要，其中包含所选模式、目标平台意图、请求的 BSP 版本或下游版本选择交接、自定义载体意图、按顺序计划的下游技能和非核心细节，下游技能可能仍会询问这些细节。不要要求批准此摘要；除非用户在核心问卷中选择 `取消`，否则继续调度。这不会绕过下游阻塞验证门。

将每个下游技能的相关 `quick_start_prefill` 子集加上顶级 `mode` 传递给它。下游技能必须使用有效的预填充答案，再次询问缺失的、无效的、模糊的或不兼容的必需输入，并拥有其配置文件块的任何变更：`reference_devkit:`、`custom_carrier:`、`bsp_image:`、`source:` 或 `documents:`。

对于 `使用现有工作区`，请验证：

- `<bsp_image.root_path or workspace/Image>/Linux_for_Tegra/` 存在。
- `Linux_for_Tegra/rootfs/etc/nv_tegra_release` 存在，证明 `apply_binaries.sh` 运行了；否则路由到 `/jetson-init-image`。
- `<source.root_path or workspace/Source>/Linux_for_Tegra/` 存在并且是一个 git 仓库。
- 当存在时，记录的 `documents:` 路径存在。

以执行的技能、跳过的技能、剩余的下游问题以及工作区是否准备好 `customize-*` 结束。

### 建议I/O自定义下一步

在调度摘要之后，仅在活动配置文件的 `documents:` 块至少有一个通过 `/jetson-link-docs` 绑定的载体板相关槽位时，打印一个非阻塞的“下一步 — I/O 自定义”列表。符合条件的槽位是：

- `documents.carrier_board_spec`
- `documents.carrier_schematic`
- `documents.ref_devkit_pinmux_xls`
- `documents.custom_carrier_schematic`
- `documents.custom_carrier_pinmux_xls`

如果这些都没有绑定，跳过此步骤——用户尚未提供这些技能依赖的载体板文件，正确的下一步是 `/jetson-link-docs`，而不是 `customize-*` 技能。用一行话说明（“没有绑定载体板文档——运行 `/jetson-link-docs` 在 I/O 自定义之前注册载体原理图 / pinmux xlsx”）并停止。

当至少有一个符合条件的槽位绑定时，打印下面的列表。适配板到其板载外设通常从 pinmux 和 UPHY 开始，然后按控制器分支：

- `/jetson-customize-pinmux` — 每个引脚的 SFIO / 方向 / 拉状态（消耗 `documents.custom_carrier_pinmux_xls` 或 `documents.ref_devkit_pinmux_xls`）。
- `/jetson-customize-uphy` — 通过 `ODMDATA` 分配 UPHY 通道（消耗 `documents.module_design_guide` 和 `documents.custom_carrier_schematic` / `documents.carrier_schematic`）。
- `/jetson-customize-pcie` — 每个控制器的 PCIe 线路（消耗 `documents.module_design_guide`、`documents.custom_carrier_schematic` / `documents.carrier_schematic`，以及 `documents.custom_carrier_pinmux_xls` / `documents.ref_devkit_pinmux_xls`）。
- `/jetson-customize-usb` — USB2 / USB3 SS 端口启用 / 禁用（消耗 `documents.module_design_guide`、`documents.custom_carrier_schematic` / `documents.carrier_schematic`，以及 `documents.custom_carrier_pinmux_xls` / `documents.ref_devkit_pinmux_xls`）。
- `/jetson-customize-mgbe` — 多千兆以太网 PHY 线路（消耗 `documents.module_design_guide`、`documents.custom_carrier_schematic` / `documents.carrier_schematic`，以及 `documents.custom_carrier_pinmux_xls` / `documents.ref_devkit_pinmux_xls`）。
- `/jetson-customize-camera` — CSI / MIPI / GMSL 传感器上电（消耗 `documents.module_design_guide` 和 `documents.custom_carrier_schematic` / `documents.carrier_schematic`）。

对于每个建议的技能，标记任何尚未绑定的必需 `documents.*` 槽位，作为“首先运行 `/jetson-link-docs` 绑定 <字段>”而不是隐藏技能——用户可能想修复绑定并重试。不要在这里调用 `customize-*` 技能；快速入门在建议时结束。

## 目的

单个入口点，收集四个路由关键答案（`mode`、`active_platform`、`bsp_release`、`custom_carrier`），并调度正确的下游设置技能。不是一站式安装器——它自己从不下载、解压、实例化或绑定任何东西。

## 先决条件

- `bsp-platforms-catalogue.md` 可达（用于构建平台列表）。
- 从免责声明 `AskUserQuestions` 表单提交的 `accept_disclaimer` 答案。
- `AskUserQuestions` UI 可用——快速入门拒绝在没有提交免责声明和核心问卷表单的情况下继续。
- 仅 Auto Setup 分支需要网络访问 (`/jetson-download-bsp` 是实际的获取器)。

## 限制

- 最多四个核心问题；任何非核心值（图像路径、源路径、文档路径、载体 ID、工具链）留给拥有的下游技能处理。
- 不验证平台 / BSP 版本兼容性——那是 `/jetson-download-bsp` 的工作。
- 不写入 `target-platform/*.yaml`；配置文件变更仍由 `/jetson-init-target`、`/jetson-init-image` 等处理。

## 故障排除

- **"问卷取消"退出** — 表单必须提交；重新运行 `/jetson-quick-start` 并完成四个问题。
- **"未接受免责声明"退出** — 重新运行 `/jetson-quick-start`，阅读免责声明，并在准备好继续时在免责声明表单中选择 `accept_disclaimer`。
- **活动配置文件未自动选择** — 按设计；即使有一个匹配的配置文件，用户也必须在表单中明确选择它。
- **键入的 `bsp_release` 未知** — 原样传递；`/jetson-download-bsp` 验证版本与官方存档。

## 注意事项

- 一次询问核心问卷。下游技能询问非核心值、空白、无效值或模糊选择。
- 除非用户要求保存，否则将 `quick_start_prefill` 保存在内存中。
- 在此处从不构建 NVIDIA 工件 URL；`/jetson-download-bsp` 遵循从所选 Jetson Linux 存档版本中获取的链接。
- `platform_template.yaml` 没有用户指南 / 版本说明槽位。将那些文件或 URL 存储在最终摘要或 KB 中，而不是作为编造的配置文件字段。

## 参考

- [`../../context/bsp-customization-workflow.md`](../../context/bsp-customization-workflow.md)
- [`../../references/bsp-platforms-catalogue.md`](../../references/bsp-platforms-catalogue.md)
- [`../../references/platform_template.yaml`](../../references/platform_template.yaml)
- [`../jetson-download-bsp/SKILL.md`](../jetson-download-bsp/SKILL.md)
- Jetson Linux 存档：<https://developer.nvidia.com/embedded/jetson-linux-archive>
