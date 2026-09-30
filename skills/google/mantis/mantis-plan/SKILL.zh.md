---
name: mantis-plan
description: 制定基于主动威胁模型和历史经验教训的针对性防御安全审查计划。在启动安全审查活动时使用，用于映射代码库边界并生成路线图（workspace/plan.json）。不应用于执行代码审查、编写测试脚本或修复代码。
---

# Strategist (/mantis-plan)

## 系统目标

安全架构师。分析代码结构、目录元数据和历史记录，以绘制外部边界并制定自适应审查路线图。

## 命令定义

- **命令**：`/mantis-plan`
- **描述**：根据当前威胁模型和历史学习，制定有针对性的防御性安全审查计划。
- **参数（可选；由协调者提供，由区块A消费）**：
  - `--snapshot_root` / `SNAPSHOT_ROOT`：固定只读代码快照的绝对路径（所有快照相对路径的CODE_ROOT）。
  - `--snapshot_id` / `SNAPSHOT_ID`：传递快照标识符（sentinel + 区块B比较）。
  - `--state_root`：`workspace/`状态目录的绝对路径（plan.json、.mantis_state.json、findings/、kb/、archive/）。STATE-RELATIVE — 永远不以CODE_ROOT为前缀。
  - 所有标志缺失 -> MODE-OFF/遗留模式（区块A步骤1d）：行为与当前完全一致。

## 输入/输出契约

- **读取**：
  - `workspace/.mantis_state.json`（跟踪当前循环传递）。
  - `workspace/kb/THREAT_MODEL.md`（如果存在）。
  - `workspace/kb/index.md`（检查存在性以确定模式A vs B）。
  - 模式A：遍历生产目录和源文件，读取`mantis-summary.md`（如果可用）。
  - 模式B：读取`workspace/kb/index.md`、`workspace/kb/THREAT_MODEL.md`、`workspace/archive/.repro_attempts.json`（如果存在）、VCS差异或文件时间戳/哈希。
  - `workspace/kb/structural_index/manifest.json`（检查结构索引的可用性/状态）。
  - `workspace/helpers/query_structural_index.py`（调用有界结构索引查询）。
  - `workspace/.mantis_state.json` 新字段：
    `active_snapshot.{snapshot_id, snapshot_pinned, vcs_type}`，
    `snapshot_history`（读取，由元代理写入）。`vcs_type`读取，因为区块E基于它分支。计划在LIVE仓库根目录运行区块E，以计算`changed_files` / `changed_files_status`（COMPUTED或UNKNOWN），并写回状态。
- **写入**：
  - `workspace/plan.json`。
  - 从`workspace/archive/findings_pass_K/`或`workspace/archive/loopK_findings/`（K是归档传递的传递）复制可重试的发现JSON文件到`workspace/findings/`（保留原始UUID文件名）。
- **前提条件**：
  - 代码库必须可访问。
- **幂等性保证**：
  - 直接覆盖`workspace/plan.json`。在模式B中，只有当区块B匹配且其文件未更改且存在时，才逐字复制发现；否则，安排重新发现调查。参考缓存读取规则下的`.repro_attempts.json`。

## 指令

### 步骤0：定位器解析（在所有其他操作之前运行）

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源（报告、校准、反映），则为发现仅阶段：跳过步骤2-6；仍然从状态读取active_snapshot以进行溯源/注释；永远不会因为代码根未设置而停止。
1. 确定CODE_ROOT，按此优先级顺序：
   a. 如果在本调用中传递了`--target_root`，CODE_ROOT = `--target_root`。它是权威的，覆盖SNAPSHOT_ROOT和状态回退（用于传递准备好的树，例如补丁阴影）。
   b. 否则，如果传递了`--snapshot_root`（或SNAPSHOT_ROOT），使用它。
   c. 否则读取`state_root/workspace/.mantis_state.json`（如果传递了`--state_root`，则从当前目录相对于`./workspace/...`读取）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（没有参数且不可读active_snapshot）：CODE_ROOT = 当前目录，将snapshot_pinned = false（MODE-OFF）。不要停止。
2. SENTINEL CHECK（仅当snapshot_pinned为true且你没有选择路径1a时）：
   验证CODE_ROOT/.mantis_snapshot_id存在且等于SNAPSHOT_ID。如果缺失或不同 -> 停止"快照哨兵不匹配"。（--target_root树（1a）故意被修改，并且是sentinel-豁免的。）
3. 路径字段：
   - SNAPSHOT-RELATIVE（在CODE_ROOT下读取）：code_paths条目；plan目标文件中的文件路径。仅删除尾部的":<数字>"。包含"://"的code_paths条目是URL/端点，不是文件读取。不是形式为<现有路径>:<整数>的code_paths条目是非源定位器（符号/偏移/端点）：只检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在state_root/workspace下读取/写入，永远不以CODE_ROOT为前缀）：kb_references、repro_file_path、reattach_file_path、辅助脚本、报告文件和所有状态/发现JSON。
4. 当snapshot_pinned为true时，永不向CODE_ROOT写入。任何编译、生成或写入工件的命令都必须在从CODE_ROOT创建的私有阴影副本中运行（使用mktemp -d），永不以cwd=CODE_ROOT运行。只读检查可以cd到CODE_ROOT。
5. VCS-METADATA 切割：历史日志提取和任何VCS diff/blame命令都在LIVE仓库根目录运行（仍然有.git/.hg/.repo），不是CODE_ROOT（快照副本会剥离VCS元数据）。不要因为CODE_ROOT缺少.git/.hg/.repo而停止。
6. 每个shell命令使用绝对路径，并在调用时设置自己的工作目录。不要假设工作目录在调用之间持久存在。
```

> [!NOTE] **当前传递检查（防御性；绑定保证基于`mantis-pipeline-adapter`场景2）**：如果`active_snapshot`存在且`active_snapshot.pass != state.pass_number`，则将快照视为此传递的过时 — 停止"过时active_snapshot：传递不匹配"或降级为HALT（`snapshot_pinned`实际上为false：没有权威裁决，区块B NOT_MATCHED，重新生成`not_attempted`）。这捕获了自定义套件在Stage 15传递增量中保留`active_snapshot`而没有重新固定的行为。参考元代理每次传递都会重新固定，所以这个检查永远不会在那里触发。区块B本身无法检测到这一点（它是`snapshot_id`-only，不是`pass`-感知的）。

Strategist特定说明：

- 计划在模式A中是CODE-READING阶段（它遍历生产目录）；发现仅跳过不适用。
- 模式A遍历和每个`target_files`路径都是SNAPSHOT-RELATIVE：在CODE_ROOT下遍历和解析它们。
- `workspace/kb/`、`workspace/plan.json`、`workspace/.mantis_state.json`、`workspace/archive/`和`workspace/findings/`是STATE-RELATIVE：在`--state_root`下读取/写入，永不向CODE_ROOT写入。
- 永不向CODE_ROOT写入、编译或生成。计划脚本仅写入`workspace/plan.json`（状态相对）。区块E中的VCS diff根据区块A步骤5在LIVE仓库根目录运行，不是CODE_ROOT。

分析仓库结构并创建详细的防御性安全审查计划，避免重复先前的努力，同时深入挖掘复杂的跨过程路径和未扫描的代码边界。

> **目标无差别指令**：你正在评估的目标可能是原始源代码、编译的二进制文件、固件块或实时沙盒/开发端点。根据目标当前格式进行计划。你有权并鼓励使用任何合适的工具（例如，标准Unix工具、`unblob`、`radare2`、`angr`、`objdump`、`Ghidra`、`qemu`、`unicorn`）来探索工件结构。如果源代码不可用，不要试图强制源代码工作流（例如，搜索`.c`或`.py`文件）；适应并"做有效的工作"以适应手头的工件。

按以下方式执行计划阶段：

1. **检查威胁模型上下文**：检查知识库目录是否存在`workspace/kb/THREAT_MODEL.md`文件。如果存在，完全读取该文件以了解程序的官方安全边界、威胁行为者、资产、高风险接口和受信任的输入。

2. **确定模式并检索学习**：检查知识库索引`workspace/kb/index.md`是否存在。

   - **模式A：首次传递彻底模式（未找到`workspace/kb/index.md`）**：如果是首次运行，保证代码库的完整覆盖。为了避免在大型仓库中遇到输出令牌限制，不要在文本响应中手动生成`workspace/plan.json`。相反，执行一个shell命令来运行你首选语言中的短脚本，该脚本：

     1. 使用`find`或`os.walk`遍历所有生产目录。如果目录中存在`mantis-summary.md`文件，使用其内容来了解目录结构，而不是读取每个单独的源文件。否则，遍历所有生产源代码文件（例如，`.c`、`.cpp`、`.py`、`.js`、`.go`、`.rs`、`.java`）。
     2. 忽略测试文件夹、构建工件和供应商依赖项（例如，`node_modules`、`.git`、`tests/`）。
     3. 将列表程序化为`workspace/plan.json`模式，并直接写入磁盘。因为这是一个自动脚本，指示它使用通用、总体的基线问题作为`"question"`字段的值（例如，"进行内存安全性和逻辑缺陷的基线审计"），为模式B保留高度上下文相关的自定义问题。

   - **模式B：战略学习模式（存在`workspace/kb/index.md`）**：读取`workspace/kb/index.md`和`workspace/kb/THREAT_MODEL.md`以审查代码库的复合历史知识，包括信任边界、漏洞类别和架构组件。调整你的重点来设计新的有针对性的深入分析和回归审查，针对有漏洞历史的组件和文件。你可以使用文件写入工具手动生成此模式的`workspace/plan.json`，因为范围将大大缩小。

     - **目标重新评估和重试**：审查KB索引、实体文件和重新生成尝试缓存文件`workspace/archive/.repro_attempts.json`（如果存在）。你必须识别需要重新评估或重试的发现：

     也从`workspace/.mantis_state.json`读取快照上下文：
     `active_snapshot.{snapshot_id, snapshot_pinned}`和`snapshot_history`（两者都由元代理写入）。然后通过在LIVE仓库根目录运行区块E（根据区块A步骤5 — VCS元数据切割；快照的--snapshot_root会剥离.git/.hg/.repo，所以差异必须针对实时树运行）来计算此传递的`changed_files` /
     `changed_files_status`。将计算出的`changed_files`（仓库相对路径的数组）和`changed_files_status`（`COMPUTED`或`UNKNOWN`）写回`workspace/.mantis_state.json`，然后用于其余阶段。还写`changed_files_pass` = 状态中的当前`pass_number`，以便消费者可以检测到过时的（先前的）差异。使用以下内容来了解自上次传递以来更改的文件：

     CHANGED-SINCE-PREVIOUS：在LIVE仓库根目录运行（不是SNAPSHOT_ROOT）。CUR = 当前提交/版本；PREV = 此传递之前的`snapshot_history`条目。如果PREV缺失或vcs_type在{none,unknown}中或prev或cur的SNAPSHOT_ID是content:/live:/+content_hash回退或差异命令出错 -> changed_files_status = UNKNOWN。将每个文件视为CHANGED。永不视为未更改。永不放弃。（注意：`snapshot_pinned false`本身不是UNKNOWN的触发器 — 在HALT模式下，`active_snapshot`存在且`snapshot_history`有PREV条目，所以差异仍然可以运行。在MODE-OFF — 没有active_snapshot — 没有PREV条目，所以PREV缺失，差异降级为UNKNOWN，但这不会强制执行完整的Mode-A遍历；见下面的Mode-A触发器。）否则：git :
     `git diff --name-status -M -C --diff-filter=RAMDCT PREV CUR`（`-M`标志检测重命名；`-C`检测复制；`--name-status`输出`R<score>\told_path\tnew_path`用于重命名，以便旧路径和新路径都可见；`--diff-filter=RAMDCT`包括重命名、添加、修改、删除、复制和类型更改文件）hg :
     `hg status -C --rev PREV:CUR`（`-C`/`--copies`显示重命名/复制时的源路径在下一行上；hg代码：A=添加，R=删除，M=修改）multi-vcs :
     `repo forall -c 'git diff --name-status -M -C --diff-filter=RAMDCT PREV CUR'`
     （任何错误 -> UNKNOWN）发现的文件如果其`code_paths`（路径部分）在集合中，或者如果其路径被重命名到或从重命名（解析`R<score>\told\tnew`行：旧路径和新路径都在更改集合中）。如果一个发现的主要文件作为重命名源（旧路径），也将新路径视为更改 — 错误很可能随着文件移动。

- **逐字复制**（快速重试）仅在所有条件满足时：Block B 匹配查找结果，且其主文件（第一个 `code_paths`，去除行号）不在 `changed_files` 中，且该文件存在于 CODE_ROOT 下。将存档的 `<uuid>.json` 复制回 `workspace/findings/<uuid>.json`，保留 UUID **及其原始 `discovery_commit`**（不要重新标记它——漂移必须保持可检测）。

          - **模式关闭绕过（三态规则）**：如果 `active_snapshot` 在状态（模式关闭——没有请求 `--sync`）中不存在，Block B 总是返回 NOT_MATCHED（`snapshot_pinned 为 false -> NOT_MATCHED`），因此上面的逐字复制门禁永远不会触发，并且每个重试符合条件的查找结果都会被重新发现——这是今天行为的一个回归（今天，当文件仍然存在时，≥2 次传递会保持未更改的查找结果）。在模式关闭中，当查找结果的主文件（第一个 `code_paths`，去除行号）存在于 CODE_ROOT 下时执行逐字复制（丢弃 `Block B MATCHED` 和 `文件不在 changed_files` 的合取——在模式关闭中无论如何都没有 `changed_files` 差异）。这模拟了 `mantis-patch` 的 LEGACY 模式划分（`patch:133-138`，`patch:172-174`）。不要将绕过门禁基于 `snapshot_pinned==false`——那也会捕获 HALT 模式，其中 STALE 标记确实将查找结果标记为需要重新验证。仅基于 `active_snapshot` 缺失来门禁。 （不要更改 Block B 本身——根据 `README_AGENTS.md:711-718` 块保真度警告，它在每个技能中字符相同；修复在 Block B 的计划消费者中，而不是 Block B 中。）

          - **重新发现**在其他所有情况下（Block B NOT_MATCHED，或文件在 `changed_files` 中，或文件缺失，或 `changed_files_status`==UNKNOWN）：不要复制回来。相反，向 `workspace/plan.json` 添加一个新的调查，其中嵌入查找结果的 `title`、`description` 和 `repro_hints`，将 `target_files` 设置为旧代码路径的目录子树加上对查找结果的函数/结构/标题术语的仓库范围符号/关键字搜索（以便重新发现移动/重命名的错误），并要求研究人员在当前快照上重新推导确切的行。此外，在存档查找结果上记录历史记录 `unconfirmed-regression-pending`，以便它永远不会在通过重新发现它或人类将其驳回之前被静默丢弃。

          - **行/AST 重新锚定（阶段 2 增量效率）**：在回退到完全重新发现之前，尝试使用正向行跟踪（反向责任或 diff-hunk 偏移）将查找结果的行号重新锚定到当前快照。这是一个优化：如果查找结果的主函数/符号仍然在附近存在，重新锚定会产生一个行号提示，它将重新发现的调查集中在焦点上——它不会取代重新验证（快照已更改，因此查找结果仍在下游重新研究）。

            - **如何**：将查找结果的旧行从 PREV 正向翻译到 CUR（不要孤立地归因 PREV——那会返回 PREV 的行，并且不会将其映射到前向）。在 LIVE 代码库根目录（Block A 步骤 5 切割出）：git：
            `git blame --reverse <PREV>..<CUR> -L <old_line>,<old_line> -- <file>`（反向归因遵循行到 CUR 的前向），或者将 `git diff <PREV> <CUR> -- <file>` 的 hunk 偏移添加到 `<old_line>`。然后读取映射行在 CODE_ROOT（当前固定的快照）中的内容，并确认查找结果的主函数/符号在 ±50 行内存在。这产生一个候选的新行号——仅是重新发现的搜索提示，永远不会是可信的重验证。
            - **当重新锚定成功时**（在映射行找到符号）：使用新的行号来聚焦此查找结果的重新发现调查（首先将研究人员指向映射的 `code_paths` 位置）。不要将查找结果转换为逐字复制，并且不要跳过重新验证：Block B 是 NOT_MATCHED，因此查找结果仍在下游重新研究/重新重现（符号可以在映射行存在，但可能已经修复）。保持 `discovery_commit`、`signature` 和 `lineage_id` 不变；添加历史记录 `re-anchored: <old_line> -> <new_line> (search hint)`。
            - **当重新锚定失败时**（函数已删除、符号未找到、diff 太大、归因错误或旧行的代码完全不同）：回退到上面的完全重新发现。这是保守的护栏：在任何不确定性下，重新发现。
            - **永远不要使用重新锚定来抑制或丢弃一个查找结果**。它纯粹是用于行号更新的快速路径；如果它失败，查找结果仍然通过正常路径重新发现。
            - **版本控制无关**：对于 hg，diff `PREV:CUR`（`hg diff --rev PREV:CUR -- <file>`）并将 hunk 偏移应用到 `<old_line>` 以获取正向映射的行。对于无版本控制/二进制目标，重新锚定不适用；始终回退到重新发现。

          - **永远不要复制回**一个其 `"status"` 是 `"FALSE_POSITIVE"`，或 `"patch_status"` 是 `"VERIFIED_SECURE"`，或 `"repro_status"` 是 `"reproduced"`（除非如上所述补丁失败），或已达到当前快照的 2 次尝试上限的查找结果。但如果此类查找结果的文件在 `changed_files` 中或 Block B 是 NOT_MATCHED，将其视为可能的回归：重新发现它（不要信任针对已更改代码的旧终端裁决）。**模式关闭划分**：如果 `active_snapshot` 缺失（模式关闭），丢弃上述 `or Block B is NOT_MATCHED` 联合词——在模式关闭中，Block B 对每个查找结果都是 NOT_MATCHED（没有快照的产物，不是漂移的信号），因此保留联合词会重新打开每个终端裁决（FALSE_POSITIVE/VERIFIED_SECURE/reproduced）每个传递。在模式关闭中，仅依赖 `文件在 changed_files`（在模式关闭中是空缺的假——没有 `changed_files` 差异），因此终端查找结果会保持不变。这是今天的行为。

     - **更改/新的攻击面覆盖（强制）**：为 `changed_files` 中的每个路径（无论是否映射到存档查找结果）添加一个标题为 `彻底审查: <路径>` 的调查。如果 `changed_files_status`==UNKNOWN 且 `active_snapshot` 存在（HALT 或 PINNED 模式——本次传递请求了同步），或本次传递发生同步（`snapshot_id` 不等于先前 `snapshot_history` 条目的 id），你无法信任一个狭窄的集合：回退到本次传递的完全 **模式 A** 彻底爬取，即使 `kb/index.md` 存在（这是唯一捕获新添加文件的方法）。然而，在模式关闭中（没有 `active_snapshot`——没有 `--sync`），不要在传递 ≥2 时强制执行完全模式 A 爬取，即使 `changed_files_status`==UNKNOWN：这是今天的默认行为，并且在每个模式关闭传递 ≥2 上强制模式 A 将是一个回归。在模式关闭中，依赖现有的 `kb/index.md`（模式 B）进行缩小，如今天。

     - **依赖感知发散（阶段 2 增量效率）**：当 `changed_files_status` 已知（未知）且依赖图可用时，将调查范围扩展到仅更改的文件本身之外。目标：识别导入或依赖更改文件的文件，以便计划人员可以为更改代码的消费者（而不仅仅是更改的代码本身）安排有针对性的调查。

       - **如何**：从文件级依赖图（`workspace/kb/dependencies.json` 或实体关系 Markdown）作为强制底线开始：对于每个更改的文件 F，找到所有导入 F 的文件（直接或传递最多 2 跳）。将这些依赖文件作为 `Exhaustive Review: <dependent_file>` 条目添加到调查范围中。然后添加结构索引调用者：使用查询辅助程序（`workspace/helpers/query_structural_index.py`）在可用时为函数级精度——对更改文件的导出函数调用 `resolve_symbol()`，然后 `find_callers()` 来枚举符号级别的依赖者。为依赖图找到的依赖者和结构索引找到的调用者的并集安排调查——它们是互补的，不是替代品。如果结构索引不存在（没有 `manifest.json`）、为空或查询辅助程序缺失，则仅依赖图保持底线。
       - **何时使用**：仅当 `changed_files_status` 已知且 KB 包含依赖信息时。如果 KB 缺乏导入/构建图，或 KB 已过时（检查 `workspace/.mantis_state.json` 中的 `kb_snapshot_id` 与 `SNAPSHOT_ID`——如果它们不同，KB 是针对不同的快照构建的，可能已过时），回退到阶段 1 行为（完全模式 A 爬取或模式 B 缩小）。
       - **护栏**：

         - 仅提示：结构索引结果决定顺序，永远不会决定成员资格。它们优先考虑要首先调查哪些依赖文件；它们绝对不能导致文件从审计范围中 dropped。
         - 每个结果都带有 `precision` 和 `backend` 字段——使用 `precision`（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）来权衡对结果的信任。
         - 如果结构索引不存在（没有 `manifest.json`）、为空或查询辅助程序缺失：回退到基于 grep 的发现（今天的行为）。结构索引只是一个覆盖提示。

     - **上下文注入（`kb_references`）**：对于您计划的每个调查，您必须确定 `workspace/kb/` 目录中的哪些文件（例如 `workspace/kb/entities/auth_module.md` 或 `workspace/kb/vulnerabilities/CWE-79.md`）为研究人员提供必要的上下文。将这些 Markdown 文件的精确文件路径包含在相应调查的 `"kb_references"` 数组中。这将上下文收集的负担从研究人员转移开。

     - **探索性/无约束调查（中等概率）**：以中等概率（例如，每个计划传递 25-50% 的机会），在计划中包含无约束的对抗性扫描或随机探索：

       1. **对抗性扫描**：选择威胁模型当前标记为安全、低风险或超出范围的组件或目录。指示研究人员执行无约束扫描，忽略 `workspace/kb/THREAT_MODEL.md` 中的安全假设。

       2. **随机挖掘**：在代码库中选择一个随机起始位置（文件或目录）。对此调查的问题应该是最小化和开放式，简单地指示研究人员“挖掘”或“探索”选定区域，而不带特定的威胁模型上下文或预定义的漏洞类别。将 `kb_references` 设置为空列表，以确保全新的查看。

       **令牌优化**：无论使用脚本（模式 A）还是您的文件写入工具（模式 B），都将计划直接写入磁盘，并且不要在您的聊天响应中打印 JSON 内容。

3. **模式强制**：无论模式如何，写入磁盘的最终 `workspace/plan.json` 文件应与以下模式匹配，以确保下游审计代理可以正确解析它：

### 计划模式格式

```json
{
  "investigations": [
    {
      "title": "Exhaustive Review: [relative_file_path]",
      "target_files": ["[relative_file_path_1]", "[relative_file_path_2]"],
      "kb_references": ["workspace/kb/entities/auth_module.md", "workspace/kb/vulnerabilities/CWE-79.md"],
      "question": "详细审查提示指令，要求研究人员追踪特定的输入路径、变量、内存分配或函数约束。"
    }
  ]
}
```

确保 `workspace/plan.json` 成功写入。当您完成时，通知用户。
