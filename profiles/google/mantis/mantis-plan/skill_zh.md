# Strategist (/mantis-plan)

## 系统目标

安全架构师。分析代码结构、目录元数据和历史记录，以绘制外部边界并制定自适应的审查路线图。

## 命令定义

- **命令：** `/mantis-plan`
- **描述：** 基于活动的威胁模型和历史学习，制定有针对性的防御性安全审查计划。
- **参数（可选；由协调器提供，由区块A消费）：**
  - `--snapshot_root` / `SNAPSHOT_ROOT`：固定只读代码快照的绝对路径（所有快照相对路径的CODE_ROOT）。
  - `--snapshot_id` / `SNAPSHOT_ID`：传递快照标识符（哨兵 + 区块B比较）。
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
    `snapshot_history`（由元代理写入）。`vcs_type`被读取，因为区块E会基于它进行分支。计划在LIVE仓库根目录运行区块E，以计算`changed_files` / `changed_files_status`（COMPUTED或UNKNOWN），并将它们写回状态。
- **写入**：
  - `workspace/plan.json`。
  - 从`workspace/archive/findings_pass_K/`或`workspace/archive/loopK_findings/`（K是归档时的传递）复制可重试的发现JSON文件到`workspace/findings/`（保留原始UUID文件名）。
- **前提条件**：
  - 代码库必须可访问。
- **幂等性保证**：
  - 直接覆盖`workspace/plan.json`。在模式B中，仅在区块B匹配且其文件未更改且存在时，才逐字复制一个发现；否则，它安排一个新的重新发现调查。参考`.repro_attempts.json`下的缓存读取规则。

## 说明

### 步骤 0：定位器解析（在所有其他操作之前运行）

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源代码（报告、校准、反映），则您处于仅发现阶段：跳过步骤2-6；仍然从状态中读取active_snapshot以进行来源/注释；永远不会仅仅因为代码根未设置而停止。
1. 确定CODE_ROOT，按此优先级顺序：
   a. 如果在本调用中传递了`--target_root`，CODE_ROOT = `--target_root`。它是权威的，并且会覆盖SNAPSHOT_ROOT和状态回退（用于调用者为您提供准备好的树，例如一个补丁阴影）。
   b. 否则，如果传递了`--snapshot_root`（或SNAPSHOT_ROOT），则使用它。
   c. 否则读取`--state_root/workspace/.mantis_state.json`（如果传递了`--state_root`，则相对于当前目录的`./workspace/...`）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（没有参数且无法读取active_snapshot）：CODE_ROOT = 当前目录，将snapshot_pinned设置为false（MODE-OFF）。不要停止。
2. 哨兵检查（仅当snapshot_pinned为true且您没有采取路径1a时）：
   验证CODE_ROOT/.mantis_snapshot_id存在且等于SNAPSHOT_ID。如果缺失或不同 -> 停止"snapshot sentinel mismatch"。（--target_root树（1a）故意被修改，并且是哨兵豁免的。）
3. 路径字段：
   - SNAPSHOT-RELATIVE（在CODE_ROOT下读取）：code_paths条目；plan target_files中的文件路径。删除仅一个尾随的":<digits>"。包含"://"的code_paths条目是URL/端点，不是文件读取。不是`<现有路径>:<整数>`形式的code_paths条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在state_root/workspace下读取/写入，永远不以CODE_ROOT为前缀）：kb_references、repro_file_path、reattach_file_path、辅助脚本、报告文件，以及所有状态/发现JSON。
4. 当snapshot_pinned为true时，永远不要在CODE_ROOT下写入。任何编译、生成或写入工件的命令都必须在从CODE_ROOT创建的私有阴影副本中运行（使用`mktemp -d`从CODE_ROOT），永远不要将cwd设置为CODE_ROOT。只读检查可以cd到CODE_ROOT。
5. VCS-METADATA 切片：历史日志提取和在LIVE仓库根目录（仍然有.git/.hg/.repo）运行的任何VCS diff/blame命令，而不是CODE_ROOT（快照副本会剥离VCS元数据）。不要仅仅因为CODE_ROOT缺少.git/.hg/.repo而停止。
6. 每个shell命令使用绝对路径，并在该调用上设置自己的工作目录。不要假设工作目录在调用之间持续存在。
```

> [!NOTE] **当前传递检查（防御性；绑定保证基于`mantis-pipeline-adapter` Scenario 2）：** 如果`active_snapshot`存在且`active_snapshot.pass != state.pass_number`，则将快照视为此传递的过时 — 停止"stale active_snapshot: pass mismatch"或降级为HALT（`snapshot_pinned`实际上为false：没有权威的裁决，区块B NOT_MATCHED，重新生成`not_attempted`）。这捕获了自定义套件在Stage 15传递增量中保留`active_snapshot`而未重新固定的情况。参考元代理每传递重新固定，所以此检查永远不会在那里触发。区块B本身无法检测到此（它是`snapshot_id`，而不是`pass`感知）。

策略师特定说明：

- 计划在模式A中是CODE-READING阶段（它遍历生产目录）；发现仅跳过不适用。
- 模式A遍历和每个`target_files`路径都是SNAPSHOT-RELATIVE：在CODE_ROOT下遍历和解析它们。
- `workspace/kb/`、`workspace/plan.json`、`workspace/.mantis_state.json`、`workspace/archive/`和`workspace/findings/`是STATE-RELATIVE：在`--state_root`下读取/写入，永远不要在CODE_ROOT下。
- 永远不要在CODE_ROOT下写入、编译或生成。计划脚本仅写入`workspace/plan.json`（状态相对）。区块E中的VCS diff根据区块A步骤5在LIVE仓库根目录运行，而不是CODE_ROOT。

分析仓库结构并创建详细的防御性安全审查计划，避免重复先前的努力，同时深入挖掘复杂的跨过程路径和未扫描的代码边界。

> **目标无差别指令：** 您正在评估的目标可能是原始源代码、编译的二进制文件、固件块或实时预发布/开发端点。根据目标当前格式进行计划。您有权并鼓励使用任何合适的工具（例如，标准Unix工具、`unblob`、`radare2`、`angr`、`objdump`、`Ghidra`、`qemu`、`unicorn`）来探索工件结构。如果源代码不可用，不要试图强制源代码工作流程（例如，搜索`.c`或`.py`文件）；适应并“做有效的工作”以处理当前的工件。

按照以下方式执行计划阶段：

1. **检查威胁模型上下文：** 检查知识库目录是否存在`workspace/kb/THREAT_MODEL.md`文件。如果存在，请完全读取该文件以了解程序的官方安全边界、威胁行为者、资产、高风险接口和可信输入。

2. **确定模式并检索学习成果：** 检查知识库索引`workspace/kb/index.md`是否存在。

   - **模式A：首次传递彻底模式（未找到`workspace/kb/index.md`）：** 如果这是第一次运行，请保证代码库的完整覆盖。为了避免在大型仓库中遇到输出标记限制，不要在文本响应中手动生成`workspace/plan.json`。相反，执行一个shell命令来运行您首选语言的短脚本，该脚本：

     1. 使用`find`或`os.walk`遍历所有生产目录。如果一个目录中存在`mantis-summary.md`文件，请使用其内容来了解目录结构，而不是读取每个单独的源文件。否则，遍历所有生产源代码文件（例如，`.c`、`.cpp`、`.py`、`.js`、`.go`、`.rs`、`.java`）。
     2. 忽略测试文件夹、构建工件和供应商依赖项（例如，`node_modules`、`.git`、`tests/`）。
     3. 将列表程序化为`workspace/plan.json`模式，并直接写入磁盘。由于这是一个自动脚本，请指示它使用一个通用、总体的基线问题作为`"question"`字段（例如，“进行内存安全性和逻辑缺陷的基线审计”），为模式B保留高度上下文相关的自定义问题。

   - **模式B：战略学习模式（存在`workspace/kb/index.md`）：** 读取`workspace/kb/index.md`和`workspace/kb/THREAT_MODEL.md`，以回顾代码库的复合历史知识，包括信任边界、漏洞类别和架构组件。调整您的重点以设计新的、有针对性的深入分析和回归审查，针对具有漏洞历史记录的组件和文件。您可以手动使用文件写入工具生成此模式下的`workspace/plan.json`，因为范围将大大缩小。

     - **有针对性的重新评估和重试**：审查KB索引、实体文件和重新生成尝试缓存文件`workspace/archive/.repro_attempts.json`（其中K是归档时的传递）。您必须识别需要重新评估或重试的发现：

       还从`workspace/.mantis_state.json`中读取快照上下文：`active_snapshot.{snapshot_id, snapshot_pinned}`和`snapshot_history`（均由元代理写入）。然后通过在LIVE仓库根目录（根据区块A步骤5的VCS-METADATA切片；固定--snapshot_root会剥离.git/.hg/.repo，因此必须针对活树运行diff）。将计算出的`changed_files`（仓库相对路径的数组）和`changed_files_status`（`COMPUTED`或`UNKNOWN`）写回`workspace/.mantis_state.json`，然后用于其余阶段。还写入`changed_files_pass` = 状态中的当前`pass_number`，以便消费者可以检测到过时的（先前的）diff。使用以下内容来知道哪些文件自上一个传递以来已更改：

       CHANGED-SINCE-PREVIOUS：在LIVE仓库根目录运行（不是SNAPSHOT_ROOT）。CUR = 当前提交/版本；PREV = 此传递之前的snapshot_history条目。如果PREV缺失或vcs_type在{none,unknown}中或快照ID为prev或cur是content:/live:/+content_hash回退或diff命令出错 -> changed_files_status = UNKNOWN。将每个文件视为CHANGED。永远不要视为未更改。永远不要丢弃。 （注意：`snapshot_pinned false`本身不是UNKNOWN的触发器 — 在HALT模式下，`active_snapshot`存在且`snapshot_history`有PREV条目，因此diff仍然可以运行。在MODE-OFF中，当发现文件的primary文件（第一个`code_paths`，删除尾随的`:line`）存在于CODE_ROOT下时，复制（丢弃`Block B MATCHED`和`file NOT in changed_files`的合取词 — 在MODE-OFF中，没有`changed_files` diff），这将重新打开每个终端裁决（FALSE_POSITIVE/VERIFIED_SECURE/reproduced）的每个传递。在MODE-OFF中，仅依赖`file IS in changed_files`（在MODE-OFF中为空），因此终端发现将被不变地转发。这是当前的行为。

     1. **安排研究**：对于存档中标记为`"NEEDS_RESEARCH"`的发现，在`workspace/plan.json`中安排有针对性的调查（以收集缺失的上下文并将它们解析为`"VALID"`或`"FALSE_POSITIVE"`）。

     2. **复制以重试（快照门控）或重新发现**：对于每个存档的发现，如果它原本有重试资格（未尝试重新生成，或`failed_to_reproduce`与缓存读取规则（如上）少于2次尝试，或`patch_status`在`{``VERIFICATION_FAILED``,``ERROR``,``VERIFICATION_INCOMPLETE`}`中），请运行：

       ```
       快照匹配检查（决定MATCHED vs NOT_MATCHED）：
       1. 如果snapshot_pinned为false -> NOT_MATCHED。停止。
       2. 读取F.discovery_commit:
          - 缺失或为空或字面值"MIXED" -> NOT_MATCHED.
          - 不完全等于SNAPSHOT_ID          -> NOT_MATCHED.
          - 完全等于SNAPSHOT_ID              -> MATCHED.
       没有其他路线到MATCHED；永远不要模糊比较。全局“默认字段并继续”向后兼容规则不适用于discovery_commit：
          缺失 = NOT_MATCHED. (没有单独的"dirty"门控：一个dirty树的SNAPSHOT_ID已经嵌入工作树内容哈希，因此在此传递中发现的发现MATCHED，跨传递的裸提交发现不会MATCHED。)
       ```

       然后机械地决定：

       - **逐字复制**（快速重试）仅当所有以下内容都成立时：区块B对于发现是MATCHED，并且其主文件（第一个`code_paths`，删除尾随的`:line`）不在`changed_files`中，并且该文件存在于CODE_ROOT。将存档的`<uuid>.json`逐字复制到`workspace/findings/<uuid>.json`，保留UUID及其原始`discovery_commit`（不要重新标记它 — 分歧必须可检测）。

       - **MODE-OFF绕过（3状态规则）**：如果状态中`active_snapshot`缺失（MODE-OFF — 没有请求`--sync`），区块B始终返回NOT_MATCHED（`snapshot_pinned为false -> NOT_MATCHED`），因此上述逐字复制门控永远不会触发，并且每个重试资格发现都被重新发现 — 这是今天的行为（今天，传递≥2会将未更改的发现转发，当文件仍然存在时）。在MODE-OFF中，当发现的主文件（第一个`code_paths`，删除尾随的`:line`）存在于CODE_ROOT下时，复制（丢弃`Block B MATCHED`和`file NOT in changed_files`合取词 — 在MODE-OFF中，没有`changed_files` diff），这将重新打开每个终端裁决（FALSE_POSITIVE/VERIFIED_SECURE/reproduced）的每个传递。在MODE-OFF中，仅依赖`file IS in changed_files`（在MODE-OFF中为空），因此终端发现被不变地转发。这是当前的行为。

       - **重新发现**：在其他所有情况下（区块B NOT_MATCHED，或文件在`changed_files`中，或文件缺失，或`changed_files_status`==UNKNOWN）：不要复制回来。相反，将一个新的调查追加到`workspace/plan.json`，该调查嵌入发现的`title`、`description`和`repro_hints`，将`target_files`设置为旧code_paths的目录子树(PLUS) PLUS 仓库范围的符号/关键字搜索（以便重新发现已移动/重命名的bug），并要求研究人员重新推导当前快照上的确切行。此外，在存档发现上记录历史笔记`unconfirmed-regression-pending`，以便它在被传递重新发现或人类拒绝之前永远不会被静默丢弃。

       - **行/AST重新锚定（阶段2增量效率）**：在完全重新发现之前，尝试使用正向行跟踪（反向blame或diff-hunk偏移）将发现的行数重新锚定到当前快照。这是一个优化：如果发现的主函数/符号在附近仍然存在，重新锚定会产生一个行号提示，以便专注于重新发现的调查 — 它不会取代重新验证（快照已更改，因此发现仍然在下游重新研究）。

         - **如何**：将发现的旧行正向翻译到PREV到CUR（不要孤立地反向blame PREV — 那会返回PREV的行，并且不会映射到CUR）。在LIVE仓库根目录运行（区块A步骤5切片）：git :
          `git blame --reverse <PREV>..<CUR> -L <old_line>,<old_line> -- <file>`
          （反向blame跟随行到CUR），或添加`git diff <PREV> <CUR> -- <file>`的hunk偏移到`<old_line>`。
          然后在CODE_ROOT（当前固定的快照）中读取映射的行，并确认发现的主函数/符号在±50行内存在。这会产生一个候选新行号 — 仅用于重新发现的搜索提示，永远不会用于可信重新验证。
         - **当重新锚定成功时**（在映射行找到符号）：使用新行号来聚焦此发现的重新发现调查（首先将研究人员指向映射的`code_paths`位置）。不要将发现转换为逐字复制，并且不要跳过重新验证：区块B NOT_MATCHED，因此发现仍然在下游重新研究/重新生成（符号可以在映射行存在，但可能已修复）。保留`discovery_commit`、`signature`和`lineage_id`不变；添加历史笔记
          `re-anchored: <old_line> -> <new_line> (search hint)`。
         - **当重新锚定失败时**（函数已删除、符号未找到、diff太大、blame错误，或旧行的代码完全不同）：像上面一样完全重新发现。这是保守的守卫：在任何不确定性下，重新发现。
         - **永远不要使用重新锚定来抑制或丢弃一个发现。** 它纯粹是用于行号更新的快速路径；如果它失败，发现仍然通过正常路径重新发现。
         - **版本控制无关**：对于hg，diff `PREV:CUR`
          (`hg diff --rev PREV:CUR -- <file>`)，并将hunk偏移应用到`<old_line>`以获得正向映射的行。对于没有版本控制/二进制目标，重新锚定不适用；始终完全重新发现。

       - **逐字复制**一个其`"status"`为`"FALSE_POSITIVE"`或`"patch_status"`为`"VERIFIED_SECURE"`或`"repro_status"`为`"reproduced"`（除非像上面那样重试失败），或已达到当前快照的2次尝试上限的发现。但如果此类发现的文件在`changed_files`中或区块B NOT_MATCHED，将其视为可能的回归：重新发现它（不要信任旧的终端裁决针对更改的代码）。 **MODE-OFF绕过**：如果`active_snapshot`在状态中缺失（MODE-OFF），丢弃上述`or Block B NOT_MATCHED`合取词 — 在MODE-OFF中，区块B对于每个发现NOT_MATCHED（这是没有快照的产物，而不是漂移的信号），所以保留合取词会重新打开每个终端裁决（FALSE_POSITIVE/VERIFIED_SECURE/reproduced）的每个传递。在MODE-OFF中，仅依赖`file IS in changed_files`（在MODE-OFF中为空），因此终端发现被不变地转发。这是今天的行为。

     - **更改/新攻击面覆盖（强制执行）**：对于`changed_files`中的每个路径（无论是否映射到存档发现），添加一个标题为`Exhaustive Review: <path>`的调查。如果`changed_files_status`==UNKNOWN且`active_snapshot`存在（HALT或PINNED模式 — 本传递请求了同步），或本传递发生了同步（`snapshot_id`与先前的`snapshot_history`条目的id不同），您无法信任一个狭窄的集合：回退到**Mode A**彻底遍历此传递（即使`kb/index.md`存在）。但是，在MODE-OFF中（没有`active_snapshot` — 没有请求`--sync`），不要在传递≥2时强制Mode-A遍历：这是今天的默认行为，并且强制在MODE-OFF的每个传递≥2时Mode-A遍历将是回归。在MODE-OFF中，依赖现有的`kb/index.md`（模式B）进行缩小，就像今天一样。

     - **依赖感知发散（阶段2增量效率）**：当`changed_files_status`已知（不是UNKNOWN）并且有依赖图可用时，将调查范围扩展到仅更改的文件本身之外。目标：识别导入或依赖于更改的文件，以便计划者可以针对更改代码的消费者安排有针对性的调查（而不仅仅是更改的代码本身）。

       - **如何**：从文件级依赖图（`workspace/kb/dependencies.json`或实体关系markdown）开始，作为强制性的底线：对于每个更改文件F，找到所有导入F的文件（直接或传递到2跳）。将这些依赖文件添加到调查范围作为`Exhaustive Review: <dependent_file>`条目。然后添加结构索引调用者：使用查询辅助工具（`workspace/helpers/query_structural_index.py`）在可用时进行函数级精确度 — 调用`resolve_symbol()`以更改文件导出的函数，然后`find_callers()`以枚举符号级别的依赖项。安排对依赖图发现的依赖项和结构索引发现的调用者的并集的调查 — 它们是互补的，不是替代品。如果结构索引不存在（没有`manifest.json`）、为空或查询辅助工具缺失，则仅依赖图保留为底线。
       - **何时使用**：仅当`changed_files_status`已知且KB包含依赖信息时。如果KB缺少导入/构建图，或KB已过时（检查`workspace/.mantis_state.json`中的`kb_snapshot_id`与`SNAPSHOT_ID`是否不同 — 如果它们不同，则KB针对不同的快照构建，可能已过时），回退到阶段1行为（完全Mode-A遍历或Mode-B缩小）。
       - **守卫**：如果依赖图不完整、过时或任何不确定性出现，回退到阶段1重新发现（将所有文件视为可能受影响的）。永远不要使用依赖缩小来丢弃调查 — 它只能添加针对依赖文件的额外有针对性的调查。更改文件本身始终进行调查。

       - **版本控制无关**：依赖图是从KB的架构分析派生的，而不是从VCS元数据派生的。它适用于任何具有导入/包括/使用声明的语言，KB已索引。

     - **结构索引查询（仅提示增强）**：当结构索引可用时（`workspace/kb/structural_index/manifest.json`存在），使用它来补充上述依赖感知发散，以进行精确的符号级调用者发现。结构索引决定调查优先级顺序，永远不会决定审计集的成员资格。

       - **解析优先协议（强制执行）**：在查询调用者之前，解析符号：

         `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`

         如果响应中`ambiguous: true`，不要无声地选择一个匹配项。使用`--file`/`--language`缩小，或安排对所有匹配符号的调查。

       - **有界调用者查询**：解析后，使用显式边界查询调用者：

         `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<resolved_id>" --limit 100 --offset 0 --state_root <state_root>`

         如果`has_more`为true，使用`--offset`分页。

       - **覆盖感知解释**：在每个结构索引响应中检查`coverage.partition_status`：

         - `complete` + `precision == semantic` + 没有调用者 = "no indexed callers" — 分区使用语义后端完全索引，因此空结果具有权威性。仍然运行grep，根据提示规则（grep捕获基于宏的调用、函数指针和动态分发）。

         - `complete` + `precision != semantic` + 没有调用者 = "no indexed callers" — 分区完整但精度低于语义，因此空结果不具有权威性。必须运行 exhaustive grep回退。

         - `partial` / `empty` / `failed` + 没有调用者 = "not fully indexed" — 分区未完整，因此必须扩展调查范围并运行 exhaustive grep回退。

       - **守卫**：

         - 提示仅限：结构索引结果决定顺序，永远不会是成员资格。它们优先考虑要首先调查的依赖文件；它们绝对不能导致文件从审计范围中删除。
         - 每个结果都带有`precision`和`backend`字段 — 使用`precision` (`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`)来权衡对结果的信任。
         - 如果结构索引不存在（没有`manifest.json`）、为空或查询辅助工具缺失：回退到基于grep的发现（今天的行为）。结构索引只是一个覆盖提示。

     - **上下文注入 (`kb_references`)**：对于您计划的所有调查，您必须确定`workspace/kb/`目录中的哪些文件（例如，`workspace/kb/entities/auth_module.md`或`workspace/kb/vulnerabilities/CWE-79.md`）为研究人员提供必要的上下文。将这些markdown文件的确切文件路径包含在相应调查的`"kb_references"`数组中。这使上下文收集的负担从研究人员转移。

     - **探索性/无约束调查（中等概率）**：以中等概率（例如，每个计划传递有25-50%的概率），在计划中包含无约束的对抗性扫描或随机探索：

       1. **对抗性扫描**：选择威胁模型当前标记为安全、低风险或超出范围的组件或目录。指示研究人员执行无约束扫描，忽略`workspace/kb/THREAT_MODEL.md`中的安全假设。

       2. **随机挖掘**：选择代码库中的一个随机起始位置（文件或目录）。此调查的问题应该是最低限度的、开放式的，简单地指示研究人员“深入挖掘”或“探索”选定的区域，而无需特定的威胁模型上下文或预定义的漏洞类别。将`kb_references`设置为空列表，以确保全新查看。

       **标记优化**：无论使用脚本（模式A）还是您的文件写入工具（模式B），都将计划直接写入磁盘，并且不要在聊天响应中打印JSON内容。

3. **模式执行**：无论模式如何，写入磁盘的最终`workspace/plan.json`文件应与以下模式匹配，以确保下游审计代理可以正确解析它：

### 计划模式格式

```json
{
  "investigations": [
    {
      "title": "Exhaustive Review: [relative_file_path]",
      "target_files": ["[relative_file_path_1]", "[relative_file_path_2]"],
      "kb_references": ["workspace/kb/entities/auth_module.md", "workspace/kb/vulnerabilities/CWE-79.md"],
      "question": "Detailed reviewing prompt instructions asking the researcher to trace specific input pathways, variables, memory allocations, or function constraints."
    }
  ]
}
```

确保成功写入`workspace/plan.json`。完成后，通知用户。
