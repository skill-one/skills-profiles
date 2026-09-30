---
name: yara-rule-authoring
description: 用于编写高质量 YARA-X 检测规则以识别恶意软件的指南。在编写、审查或优化 YARA 规则时使用。涵盖命名规范、字符串选择、性能优化、从旧版 YARA 迁移以及减少误报。触发条件：YARA、YARA-X、恶意软件检测、威胁狩猎、IOC、特征码、crx 模块、dex 模块。
---

# YARA-X 规则编写

编写检测规则以捕获恶意软件，同时避免陷入大量误报。

**此技能针对 YARA-X**，它是基于 Rust 的传统 YARA 的继任者——正则表达式速度提升 5-10 倍，错误更少，内置格式化器，更严格的验证，新的模块（crx、dex），规则兼容性达 99%。它为 VirusTotal 的生产系统提供支持。通过 `brew install yara-x` 或 `cargo install yara-x` 安装；CLI 命令是 `yr`。有关现有规则，请参阅 [从传统 YARA 迁移](#migrating-from-legacy-yara)。

## 核心原则

1. **字符串必须生成良好的原子** — YARA 提取 4 字节子序列进行快速匹配。具有重复字节、常见序列或不足 4 字节的字符串会在过多文件上强制执行慢速字节码验证。

2. **针对特定家族，而非类别** — "检测勒索软件" 会捕获所有和什么也捕获不到。 "检测 LockBit 3.0 配置提取例程" 会捕获你想要的内容。

3. **部署前在良好软件上测试** — 在 Windows 系统文件上触发的规则是无用的。在 VirusTotal 的良好软件语料库或你自己的干净文件集上验证。

4. **首先使用廉价的快速检查进行短路** — `filesize`（即时），然后魔数字节（几乎即时），然后字符串（廉价），然后模块（昂贵）。

5. **元数据是文档** — 未来的你（以及你的团队）需要知道这个规则捕获了什么、为什么以及样本来源。

## 使用场景

- 编写用于恶意软件检测的新 YARA-X 规则
- 审查现有规则以查找质量问题或性能问题
- 优化运行缓慢的规则集
- 将 IOCs 或威胁情报转换为检测签名
- 调试误报问题
- 准备用于生产部署的规则
- 将传统 YARA 规则迁移到 YARA-X
- 分析 Chrome 扩展程序（crx 模块）或 Android 应用程序（dex 模块）

## 不应使用的场景

- 需要反汇编的静态分析 → 使用 Ghidra/IDA 技能
- 动态恶意软件分析 → 使用沙箱分析技能
- 基于网络的检测 → 使用 Suricata/Snort 技能
- 使用 Volatility 的内存取证 → 使用内存取证技能
- 简单的基于哈希的检测 → 直接使用哈希列表

## 平台注意事项

YARA 适用于任何文件类型。根据目标平台调整模式：

| 平台 | 魔数字节 | 坏字符串 | 好字符串 |
|------|----------|----------|----------|
| **Windows PE** | `uint16(0) == 0x5A4D` | API 名称、Windows 路径 | 互斥锁名称、PDB 路径 |
| **macOS Mach-O** | `uint32(0) == 0xFEEDFACE`（32 位）、`0xFEEDFACF`（64 位）、`uint32be(0) == 0xCAFEBABE`（通用） | 常见 Obj-C 方法 | 键盘记录器字符串、持久化路径 |
| **JavaScript/Node** | 无需 | `require`、`fetch`、`axios` | 混淆器签名、eval+decode 链 |
| **npm/pip 包** | 无需 | `postinstall`、`dependencies` | 可疑的包名称、数据外泄 URL |
| **Office 文档** | `uint32(0) == 0x04034B50` | VBA 关键字 | 宏自动执行、编码有效负载 |
| **VS Code 扩展程序** | 无需 | `vscode.workspace` | 不常见的激活事件、隐藏文件访问 |
| **Chrome 扩展程序** | 使用 `crx` 模块 | 常见 Chrome API | 权限滥用、清单异常 |
| **Android 应用程序** | 使用 `dex` 模块 | 标准 DEX 结构 | 混淆的类、可疑的权限 |

> **`uintNN()` 以小端格式读取。** 将常量作为反转的字节写入，或使用 `uintNNbe()` 并按文件顺序写入。ZIP/OOXML 文件以字节 `50 4B 03 04` 开头，因此它是 `uint32(0) == 0x04034B50` — `uint32(0) == 0x504B0304` 编译干净且永远不会匹配任何内容。相同的陷阱适用于 Mach-O 通用二进制文件：在磁盘上它们是 `CA FE BA BE`，所以 `uint32(0) == 0xCAFEBABE` 是一个死分支；写入 `uint32be(0) == 0xCAFEBABE` 或 `uint32(0) == 0xBEBAFECA`。在信任任何魔数字节检查之前，使用 `yr scan` 对一个已知良好的样本进行验证。

### macOS 恶意软件检测

目前还没有专门的 Mach-O 模块——使用魔数字节加上字符串模式。良好指标：

- 键盘记录器痕迹：`CGEventTapCreate`、`kCGEventKeyDown`
- SSH 隧道字符串：`ssh -D`、`tunnel`、`socks`
- 持久化路径：`~/Library/LaunchAgents`、`/Library/LaunchDaemons`
- 凭据窃取：`security find-generic-password`、`keychain`

```yara
// 来自 Airbnb BinaryAlert 的模式
rule SUSP_Mac_ProtonRAT
{
    strings:
        $lib1 = "SRWebSocket" ascii          // 库指标
        $lib2 = "SocketRocket" ascii
        $behav1 = "SSH tunnel not launched" ascii   // 行为指标
        $behav2 = "Keylogger" ascii
    condition:
        (uint32(0) == 0xFEEDFACF or uint32be(0) == 0xCAFEBABE) and
        any of ($lib*) and any of ($behav*)
}
```

### JavaScript 检测

| 目标 | 方法 |
|------|------|
| npm 包 | `package.json` 模式、postinstall/preinstall 钩子、数据外泄组合：fetch + 环境访问 + 凭据路径 |
| Chrome 扩展程序 | `crx` 模块 |
| 其他扩展程序 | 清单模式、后台脚本行为 |
| 独立 JavaScript | 混淆标记（eval+atob、fromCharCode 链）、唯一函数/变量名称、打包有效负载 |
| 最小化/webpack 打包 | 在打包中幸存的唯一字符串（URL、魔数值）；**避免函数名称** — 它们会被混淆 |

**良好的 JS 字符串**：以太坊函数选择器 — `{ a9 05 9c bb }`（`transfer(address,uint256)`）、`{ 70 a0 82 31 }`（`balanceOf(address)`）；零宽度字符用于隐写术 — `{ E2 80 8B E2 80 8C }`；混淆器签名 — `_0x`、`var _0x`；特定的 C2 域和 webhook URL。

**不良的 JS 字符串**：`require`、`fetch`、`axios`（过于常见）；`Buffer`、`crypto`（到处都是合法用途）；`process.env` 单独使用（需要特定的环境变量名称）。

## 字符串选择

**价值排名**：互斥锁名称是金子，C2 路径是银子，错误消息是青铜。栈字符串几乎总是唯一的。如果你需要超过 6 个字符串，你就是在过度拟合。

当任何以下情况成立时，拒绝候选字符串：

| 测试 | 失败原因 | 改为 |
|------|----------|------|
| 不足 4 字节 | 没有原子 | 查找更长的字符串 |
| 重复字节（`0000`、`9090`） | 弱原子 | 添加周围上下文 |
| API 名称（`VirtualAlloc`、`CreateRemoteThread`） | 每个打包器和安装器都调用它 | 调用位置的十六进制模式加上一个唯一标记 |
| 出现在 Windows 系统文件中 | 保证误报 | 查找特定于家族的内容 |
| 常见路径（`C:\Windows\`、`cmd.exe`） | 普遍存在 | 查找恶意软件特定路径 |
| 出现在其他恶意软件家族中 | 未能识别 *这个* 家族 | 与特定于家族的标记结合 |

剩下的所有内容——仅此家族独有的内容——就是规则应该依赖的内容。

### 选择字符串类型

| 需要 | 使用 |
|------|------|
| 精确的 ASCII/Unicode 文本 | `$s = "MutexName" ascii wide` |
| 特定字节序列 | `$h = { 4D 5A 90 00 }` |
| 带变化的字节序列 | 十六进制通配符：`{ 4D 5A ?? ?? 50 45 }` |
| 具有结构的模式（URL、路径） | 有界正则表达式：`/https:\/\/[a-z]{5,20}\.onion/` |
| 未知编码（XOR、base64） | 修饰符：`$s = "config" xor(0x00-0xFF)` |

**修饰符纪律**：在没有明确证据的情况下，永远不要使用 `nocase` 或 `wide`——只有在确认大小写或编码在样本之间变化的情况下才使用。`nocase` 会将原子生成量翻倍；`wide` 会将字符串匹配量翻倍。"如果你没有使用这些修饰符的明确理由，就不要使用"——Kaspersky Applied YARA。

## 条件设计

短路顺序：`filesize <`、魔数字节、字符串、模块。如果条件超过 5 行，请将其拆分为多个规则。

### all of vs any of

| 情况 | 使用 |
|------|------|
| 字符串各自对恶意软件是唯一的 | `any of them` — 每个单独都可疑 |
| 字符串常见但组合可疑 | `all of them` — 需要完整模式 |
| 字符串具有不同的置信度 | 分组：`all of ($core_*) and any of ($variant_*)` |
| 看到误报 | 收紧：`any` → `all`，添加更多必需字符串 |

**生产中的教训**：使用 `any of ($network_*)` 的规则，其中包含 `fetch`、`axios` 和 `http` 字符串，几乎匹配了所有网络应用程序。切换为要求凭据路径 AND 网络调用 AND 数据外泄目的地，消除了误报。

### 按置信度分组

不同类型的指标携带不同的权重——C2 域可能是决定性的，而库导入需要佐证。按前缀分组可以让你表达渐进式要求：

```yara
strings:
    $a1 = "SRWebSocket" ascii            // 类别 A：库指标
    $a2 = "SocketRocket" ascii
    $b1 = "SSH tunnel" ascii             // 类别 B：行为
    $b2 = "keylogger" ascii nocase
    $c1 = /https:\/\/[a-z0-9]{8,16}\.onion/   // 类别 C：C2

condition:
    filesize < 10MB and
    any of ($a*) and any of ($b*)        // 来自两个类别的证据
```

### 模块与字节检查

| 需要 | 使用 |
|------|------|
| imphash、丰富头部、 Authenticode | PE 模块——太复杂无法复制 |
| 魔数字节或简单偏移量 | `uint16`/`uint32` — 更快，无模块开销 |
| 节名/大小 | PE 模块，但将魔数字节过滤器放在第一位 |
| Chrome 扩展程序权限 | `crx` 模块 — 字符串解析易碎 |
| LNK 目标路径 | `lnk` 模块 — 格式复杂 |

"避免魔法模块——使用显式的十六进制检查" — Neo23x0。一般化它：如果 `uint32()` 可以完成工作，就不要加载模块。

### 性能

- **正则表达式必须锚定到 4+ 字节的字面量。** 没有锚定，它会在每个文件偏移量上评估——灾难性的。写 `/mshta\.exe http:\/\/.../`，而不是 `/http:\/\/.../`。如果你无法锚定，请使用带通配符的十六进制模式。
- **绑定每个正则表达式限定符** — `.{0,30}`，永远不要 `.*`。无界正则表达式既是性能灾难，也是内存爆炸。
- **用文件大小绑定循环** — `filesize < 100KB and for all i in (1..#a) : ...`。无界的 `#a` 在大文件中可以达到数千个。
- **优先使用十六进制而不是正则表达式**，如果字节是固定的。

## 在编写之前：样本是否被打包？

| 信号 | 做什么 |
|------|------|
| 熵 > 7.0 | 可能被打包 — 首先找到解包层 |
| 可读字符串很少或没有 | 可能被打包 — 使用熵、PE 结构或打包器签名 |
| 检测到 UPX/MPRESS/自定义打包器 | 针对解包的有效负载 OR 检测打包器本身 |
| 可读字符串可用 | 继续进行基于字符串的检测 |

**不要针对打包层编写规则。** 打包器会变化；有效负载不会。

### 当字符串失败时，转向结构

如果提取只返回 API 名称和通用路径：

| 可用信号 | 使用 |
|------|------|
| 高熵段 | `math.entropy()` 在特定段上 |
| 不寻常的导入模式 | `pe.imphash()` 用于导入哈希聚类 |
| PE 结构异常 | 节名、大小、特征 |
| 元数据存在 | 版本信息、时间戳、资源 |
| 没有唯一性 | 这个样本可能无法单独使用 YARA 检测 |

"可以尝试使用其他文件属性，例如元数据、熵、导入哈希或其他保持不变的数据。" — Kaspersky Applied YARA Training

## 调试误报

1. **哪个字符串匹配了？** — `yr scan -s rule.yar false_positive.exe`
2. **在合法库中？** — 添加 `not $fp_vendor_string` 排除
3. **常见的开发模式？** — 用更具体的字符串替换
4. **多个通用字符串匹配在一起？** — 收紧为要求所有，加上一个唯一标记
5. **恶意软件使用常见技术？** — 针对其特定实现细节，而不是技术本身

### 当放弃方法时

- **提取只返回 API 名称和路径** → [转向结构](#when-strings-fail-pivot-to-structure)
- **找不到 3 个唯一字符串** → 可能被打包；针对解包版本或检测打包器
- **规则匹配良好软件** → 1-2 个匹配：调查并收紧；3-5 个：查找不同指标；6 个以上：重新开始
- **优化后性能很差** → 架构问题；拆分为专注的规则或添加严格预过滤器
- **描述很难写** → 规则太模糊。如果你不能解释它捕获什么，它捕获太多

## 拒绝的理由

当你想到这些时，停止并重新考虑。

| 理由 | 专家回应 |
|------|------|
| "这个通用字符串足够唯一" / "这个十六进制模式足够唯一" | 在一个样本中唯一 ≠ 在生态系统中唯一。在良好软件上测试；你的直觉是错误的。 |
| "yarGen 给了我这些字符串" | yarGen 建议，你验证。手动检查每个字符串——预期丢弃 80%。 |
| "我的 10 个样本上它有效" | 10 个样本 ≠ 生产。使用良好软件语料库。 |
| "一个规则捕获所有变体" | 导致误报泛滥。针对特定家族。 |
| "如果出现误报，我会使其更具体" / "我稍后会添加更多条件" | 一开始就写紧密的规则。一个弱规则部署就是损害，误报会消耗信任。 |
| "这只是为了狩猎" | 狩猎规则成为检测规则。相同的质量标准。 |
| "API 名称使其具有恶意" | 合法软件也使用相同的 API。需要行为上下文。 |
| "`any of them` 对这些常见字符串足够了" | 常见字符串 + `any` = 误报泛滥。仅对各自唯一的字符串使用 `any`。 |
| "这个正则表达式足够具体" | `/fetch.*token/` 匹配所有身份验证代码。添加数据外泄目的地要求。 |
| "我会使用 `.*` 以获得灵活性" | 无界正则表达式 = 性能灾难加上内存爆炸。使用 `.{0,30}`。 |
| "JavaScript 看起来很干净" | 攻击者将注入污染合法代码。检查 eval+decode 链。 |
| "性能不重要" | 一个慢速规则会减慢整个规则集。优化原子。 |
| "我会使用 `--relaxed-re-syntax` 到处使用" | 掩盖真实错误。修复正则表达式而不是隐藏问题。 |
| "PEiD 规则仍然有效" | 过时。32 位打包器已无关紧要。 |

## 工具箱

| 工具 | 目的 |
|------|------|
| **yr CLI** | `yr check`（验证）、`yr fmt`（格式化）、`yr scan -s`（扫描，显示字符串）、`yr dump -m pe`（检查结构） |
| **yarGen** | 提取候选字符串：`yarGen.py -m samples/ --excludegood` |
| **FLOSS** | 提取混淆/栈字符串：`floss sample.exe` — 当 yarGen 空时 |
| **signature-base** | 学习高质量示例 |
| **YARA-CI** | 部署前良好软件语料库测试 |

掌握这五个。不要被工具目录分心。

**开发周期：**

```bash
yr check rule.yar                                   # 语法，带精确行号
yr fmt -w rule.yar                                  # 标准化格式化
yr dump -m pe sample.exe --output-format yaml       # 检查结构，无需虚拟规则
time yr scan -s rule.yar corpus/                    # 扫描并计时
```

在调查可用模块字段、调试为什么模块条件不匹配或探索新模块（crx、lnk、dotnet）之前，使用 `yr dump`。YARA-X 错误消息包含精确的源位置——如果 `yr check` 说行 15，问题就在行 15。

**版本控制功能**：`private $helper = "pattern"` 匹配但不出现在输出中（v1.3.0+）；`// suppress: slow_pattern` 内联抑制特定警告（v1.4.0+）；`filesize < 10_000_000` 数字下划线（v1.5.0+）。`$_unused` 也抑制未使用字符串警告。

## Chrome 扩展程序分析（crx 模块）

需要 YARA-X v1.5.0+，或 v1.11.0+ 以使用 `permhash()`。

**关键 API**：`crx.is_crx`、`crx.permissions`、`crx.permhash()`
**危险信号**：`nativeMessaging` + `downloads`、`debugger` 权限、`<all_urls>` 的内容脚本

```yara
import "crx"

rule SUSP_CRX_HighRiskPerms {
    condition:
        crx.is_crx and
        for any perm in crx.permissions : (perm == "debugger")
}
```

有关完整 API、权限风险评估和示例规则的详细信息，请参阅 [crx-module.md](references/crx-module.md)。

## Android DEX 分析（dex 模块）

需要 YARA-X v1.11.0+。**与传统 YARA 的 dex 模块不兼容**——API 完全不同。

**关键API：** `dex.is_dex`, `dex.contains_class()`, `dex.contains_method()`, `dex.contains_string()`
**警告标志：** 单字母类名（混淆）、`DexClassLoader`反射、加密资源

```yara
import "dex"

规则 SUSP_DEX_DynamicLoading {
    条件：
        dex.is_dex and
        dex.contains_class("Ldalvik/system/DexClassLoader;")
}
```

有关完整API、混淆检测和示例规则的详细信息，请参阅 [dex-module.md](references/dex-module.md)。

## 从旧版YARA迁移

99%规则兼容性，但验证更严格：

```bash
yr check --relaxed-re-syntax rules/   # 识别问题
# 修复每个问题，然后无宽松模式验证：
yr check rules/
```

| 问题 | 旧版 | YARA-X修复 |
|-------|------|------------|
| 正则表达式中字面量`{` | `/{/` | `/\{/` |
| 无效转义 | `\R` 沉默字面量 | `\\R` 或 `R` |
| Base64字符串 | 任意长度 | 需要至少3个字符 |
| 负索引 | `@a[-1]` | `@a[#a - 1]` |
| 重复修饰符 | 允许 | 删除重复项 |

`--relaxed-re-syntax`是诊断工具，不是目标。修复正则表达式。

## 命名和元数据

```
{类别}_{平台}_{家族}_{变体}_{日期}      例如：MAL_Win_Emotet_Loader_Jan25
```

**类别：** `MAL_`（恶意软件）、`HKTL_`（黑客工具）、`WEBSHELL_`、`EXPL_`、`SUSP_`（可疑）、`GEN_`（通用）。**平台：** `Win_`、`Lnx_`、`Mac_`、`Android_`、`CRX_`。

每个规则都需要`description`（以"Detects"开头）、`author`、`reference`和`date`：

```yara
元数据：
    description = "通过独特的互斥符和C2路径检测示例恶意软件"
    author = "您的姓名 <email@example.com>"
    reference = "https://example.com/分析"
    date = "2025-01-29"
```

有关完整约定的详细信息，请参阅 [style-guide.md](references/style-guide.md)。

## 工作流程

1. **收集样本** — 多个；单样本规则很脆弱
2. **提取候选** — `yarGen -m samples/ --excludegood`
3. **验证质量** — 应用 [字符串选择](#string-selection) 测试；预期丢弃80%的yarGen输出
4. **编写规则** — 正确的元数据，先进行廉价检查
5. **检查和测试** — `yr check`、`yr fmt`、检查器脚本
6. **良软件验证** — VirusTotal语料库或本地干净文件
7. **部署** — 完整元数据，然后监控误报

过程中的质量信号：匹配不到50%已知变体的规则太窄；匹配良软件的规则太宽。

**审查他人编写的规则** — 运行两个脚本后再用肉眼阅读规则，并引用它们发出的代码：

```bash
uv run {baseDir}/scripts/yara_lint.py suspect.yar      # 风格、元数据、YARA-X兼容性
uv run {baseDir}/scripts/atom_analyzer.py suspect.yar  # 按字符串检查原子质量
```

它们捕获机械性错误 — 短字符串、易产生误报的子字符串、无界量词、廉价项前的昂贵项 — 这样您的注意力可以集中在它们无法做出的判断上：字符串是否识别*这个*家族，条件是否仅对通用字符串触发。通过代码（`E002`、`W009`）报告发现，以便作者可以在 [style-guide.md](references/style-guide.md) 中查找每个问题。

有关验证工作流程的详细信息，请参阅 [testing.md](references/testing.md)，有关完整分步指南，请参阅 [rule-development.md](workflows/rule-development.md)。

## 常见错误

| 错误 | 坏 | 好 |
|------|----|-----|
| API名称作为指示器 | `"VirtualAlloc"` | 调用点的十六进制模式 + 独特互斥符 |
| 无界正则表达式 | `/https?:\/\/.*/` | `/https?:\/\/[a-z0-9]{8,12}\.onion/` |
| 缺少文件类型过滤器 | `pe.imports(...)` 首先检查 | `uint16(0) == 0x5A4D and filesize < 10MB` 首先检查 |
| 短字符串 | `"abc"` (3字节) | `"abcdef"` (4+字节) |
| 未转义的大括号（YARA-X） | `/config{key}/` | `/config\{key\}/` |
| 错误端序的魔数 | `uint32(0) == 0xCAFEBABE` | `uint32be(0) == 0xCAFEBABE` |

## 质量检查清单

部署任何规则前：

- [ ] 名称遵循 `{类别}_{平台}_{家族}_{变体}_{日期}`
- [ ] 描述以"Detects"开头并解释检测内容/方式
- [ ] 所有必需元数据存在（作者、参考、日期）
- [ ] 字符串唯一 — 不是API名称、常见路径或格式字符串
- [ ] 所有字符串4+字节且具有良好原子潜力
- [ ] Base64修饰符仅用于3+字符的字符串
- [ ] 正则表达式有界、锚定到字面量、大括号转义
- [ ] 条件以廉价检查（文件大小、魔数）开头
- [ ] 魔数常量与已知良好样本验证
- [ ] 规则匹配所有目标样本
- [ ] 规则在良软件语料库中不匹配
- [ ] `yr check` 和 `yr fmt --check` 通过
- [ ] 检查器无错误通过
- [ ] 同行评审完成

## 脚本

```bash
uv run {baseDir}/scripts/yara_lint.py rule.yar      # 验证风格/元数据
uv run {baseDir}/scripts/atom_analyzer.py rule.yar  # 检查字符串质量
```

有关详细脚本文档，请参阅 [README.md](../../README.md#scripts)。

## 深入阅读

| 主题 | 文档 |
|------|------|
| 命名和元数据约定 | [style-guide.md](references/style-guide.md) |
| 性能和原子优化 | [performance.md](references/performance.md) |
| 字符串类型和判断 | [strings.md](references/strings.md) |
| 测试和验证 | [testing.md](references/testing.md) |
| Chrome扩展模块（crx） | [crx-module.md](references/crx-module.md) |
| Android DEX模块（dex） | [dex-module.md](references/dex-module.md) |
| 完整规则开发流程 | [rule-development.md](workflows/rule-development.md) |

`examples/` 目录包含真实、归因的规则，值得在编写自己的规则前阅读：

| 示例 | 展示 | 来源 |
|------|------|------|
| [MAL_Win_Remcos_Jan25.yar](examples/MAL_Win_Remcos_Jan25.yar) | PE恶意软件：分级字符串计数，每个家族多个规则 | Elastic Security |
| [MAL_Mac_ProtonRAT_Jan25.yar](examples/MAL_Mac_ProtonRAT_Jan25.yar) | macOS：Mach-O魔数、多类别分组 | Airbnb BinaryAlert |
| [MAL_NPM_SupplyChain_Jan25.yar](examples/MAL_NPM_SupplyChain_Jan25.yar) | npm供应链：真实攻击模式、ERC-20选择器 | Stairwell Research |
| [SUSP_JS_Obfuscation_Jan25.yar](examples/SUSP_JS_Obfuscation_Jan25.yar) | JavaScript：混淆器检测、基于密度的匹配 | imp0rtp3, Nils Kuhnert |
| [SUSP_CRX_SuspiciousPermissions.yar](examples/SUSP_CRX_SuspiciousPermissions.yar) | Chrome扩展：crx模块、权限 | 教育性 |

**学习规则仓库：** [Neo23x0/signature-base](https://github.com/Neo23x0/signature-base) (17,000+ 生产规则)、[elastic/protections-artifacts](https://github.com/elastic/protections-artifacts) (端点测试)、[imp0rtp3/js-yara-rules](https://github.com/imp0rtp3/js-yara-rules) (JavaScript)、[InQuest/awesome-yara](https://github.com/InQuest/awesome-yara) (精选索引)。

**指南：** [YARA风格指南](https://github.com/Neo23x0/YARA-Style-Guide) 和 [YARA性能指南](https://github.com/Neo23x0/YARA-Performance-Guidelines) (Neo23x0)、[YARA-X文档](https://virustotal.github.io/yara-x/)。

**macOS特定：** Apple自己的生产规则随 `/System/Library/CoreServices/XProtect.bundle/` 提供；[objective-see](https://objective-see.org/) 发布macOS恶意软件研究和样本。
