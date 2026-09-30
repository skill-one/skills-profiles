---
name: mantis-report
description: 生成一份人类可读的安全审查包，该包由已确认的发现和利用链组成。在审查周期结束时使用，以生成面向利益相关者的文档。不要直接用于审计代码或验证补丁。
---

# 报告器 (/mantis-report)

## 系统目标

安全报告专家。将复杂的、技术性的发现日志综合成一份高质量、人类可读的审查包，供开发人员和利益相关者使用。

## 命令定义

- **命令：** `/mantis-report`
- **描述：** 生成包含已确认发现和利用链的人类可读安全审查包。

## 输入/输出契约

- **读取**：
  - `workspace/findings/*.json`（本次运行的所有活动发现文件）。
  - `workspace/archive/findings_pass_*/*.json`（先前运行的归档发现）和遗留的 `workspace/archive/loop*_findings/*.json`。报告是一个活动范围内的视图：本次运行的所有发现加上先前运行中停止重试的发现（例如达到重试上限），以便它们不会从报告中消失。
  - `workspace/.mantis_state.json`（用于跟踪当前循环运行，并读取 `vcs_info` 和 `active_snapshot` {`root`, `snapshot_id`, `snapshot_pinned`} 以进行来源追溯）。
  - 每个发现的快照来源字段，全部可选：`discovery_commit`, `repro_snapshot_id`, `patch_base_snapshot`。当任何一个缺失或为空时，会渲染为 "(未记录)" —— 永远不是丢弃发现的理由。
- **写入**：
  - `workspace/report/review_packet_pass_<N>_<snapshot_tag>.md`（带运行和快照标签的 Markdown 报告）。在遗留运行且没有记录快照的情况下，回退到不带后缀的 `review_packet_pass_<N>.md`。
  - 更新 `workspace/report/review_packet-latest.md` 处的副本/链接。
- **前提条件**：
  - 在 `workspace/findings/` 或 `workspace/archive/` 中存在校准和可复现的发现。报告是一个活动范围内的视图：它报告在本轮或任何先前轮次中发现的每个未解决发现的当前状态，每个发现的最新状态去重。一个已确认但未修复的发现如果计划停止回退（例如，它达到了 2 次尝试的重试上限），则不会消失——它会以其最新的归档状态出现在这里。
- **幂等性保证**：
  - 写入带运行和快照标签的文件。原地覆盖 `review_packet-latest.md`。对同一快照重新运行相同的运行会更新相同的带标签文件。对不同的快照重新运行相同的运行编号会写入不同的文件（`<snapshot_tag>` 后缀防止跨快照覆盖）。没有记录快照的遗留运行保留不带后缀的 `review_packet_pass_<N>.md` 名称，并按之前的方式原地覆盖。

## 说明

**步骤 0 — 定位器解析。**

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果这个技能永远不会读取目标源（报告、校准、反映），你是一个仅发现阶段：跳过步骤 2-6；仍然读取 `active_snapshot` 从状态以进行来源/注释；永远不会因为代码根未设置而停止。
1. 确定 CODE_ROOT，按此优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，CODE_ROOT = `--target_root`。它是权威的，并且会覆盖 `SNAPSHOT_ROOT` 和状态回退（在调用者将你交给准备好的树时使用，例如一个修补的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用来自 `--state_root` 的 `state_root`，否则相对于当前目录的 `./workspace/...`）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：CODE_ROOT = 当前目录，将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 边界检查（仅当 `snapshot_pinned` 为 true 且你没有选择路径 1a 时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（一个 `--target_root` 树（1a）是故意被修改的，并且是哨兵豁免的。）
3. 路径字段：
   - 快照相对（在 `CODE_ROOT` 下读取）：`code_paths` 条目；计划目标文件，它们是文件路径。只删除末尾的 `:<digits>`。包含 "://" 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：只检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会以 `CODE_ROOT` 为前缀）：
     `kb_references`, `repro_file_path`, `reattack_file_path`, 帮助脚本，报告文件，以及所有状态/发现 JSON。
4. 当 `snapshot_pinned` 为 true 时，永远不要在 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在 `CODE_ROOT` 的私有影子副本中运行（从 `CODE_ROOT` 使用 `mktemp -d`），永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切割：历史记录日志提取和在 LIVE 仓库根（仍然有 `.git/.hg/.repo`）中运行的任何 VCS diff/blame 命令，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。不要因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径，并在该调用上设置它自己的工作目录。不要假设工作目录在调用之间持久存在。
```

然后，以下仅发现的注释适用于报告器：

- 报告器是一个仅发现阶段（块 A，角色步骤 0）：它跳过定位器步骤 2–6，不需要或解析 `CODE_ROOT`，并且永远不会因为代码根或哨兵未设置而停止。
- 它仍然读取 `active_snapshot`（`root`, `snapshot_id`, `snapshot_pinned`）和 `vcs_info` 从 `workspace/.mantis_state.json` 以进行来源——用于构建标题、顶部横幅和输出文件名。
- 报告器接触的每个路径（`workspace/findings/*.json`, `workspace/.mantis_state.json`, `workspace/report/*`, `workspace/archive/*`）都是状态相对的，并且永远不会以 `CODE_ROOT` 为前缀。

编译一份专业的 Markdown 报告，详细说明已确认/可复现的漏洞和利用链。

按以下方式执行报告阶段：

1. **加载发现——本次运行的全部，以及转发的打开发现（按最新顺序折叠；无脚本）。** 构建一个按发现身份键控的工作集，每个发现在其最新状态下只出现一次：

   **相同 Bug 谓词**（用于此阶段中所有当前↔归档去重、折叠和抑制；在此阶段中总是安全的过报告，隐藏真实发现是不可接受的）：两个发现是同一个 Bug，当且仅当（i）它们具有完全相同的 `id`（UUID）；或者（ii）所有三个都成立——它们共享一个非空的 `lineage_id`，它们共享一个非空的 `signature`，并且至少一个 `code_paths` 条目与它的末尾 `:line`（包含行）在它们之间是相同的。否则它们是不同的——渲染两个。永远不要在 `lineage_id` 单独或 `signature` 单独上认为两个发现是同一个 Bug：两者都比 Bug 的真实身份（基于 basename 派生的 `lineage` 可以链接两个不同命名的文件；`signature` 剥掉了行号，所以它在不同文件 Bug 之间冲突），并且单独折叠任何一个都可能导致真实发现的静默丢失。

   **设计说明（重新锚定 vs 折叠）：** `mantis-plan` 的重新锚定（阶段 2\) 只提供一个行提示，它引导重新发现——它不会重写转发的发现的 `code_paths`。重新发现的发现会在当前快照的新行上出现。因为折叠谓词需要一个包含行的 `code_paths` 匹配，重新发现的发现将不会与它的祖先折叠（行号不同）。这是安全的过报告——两个条目都会渲染，当前条目显示新位置。未来的阶段可以放宽谓词到路径仅匹配，当两者都携带相同的 `signature` AND `lineage_id` AND 祖先的行在当前快照中确认不存在时，但今天使用的保守行包含匹配是为了防止任何静默丢失风险。

   1. 读取所有活动的 `workspace/findings/*.json` 并将每个活动发现添加到工作集中，按其 `id`（UUID）键控——所有修复状态，因此本次运行的 `VERIFIED_SECURE`/`MITIGATION_PROPOSED` 修复仍然与它们的补丁一起出现在类别 1/2 中。永远不会折叠两个活动发现，即使它们共享 `lineage_id` 或 `signature`——保持每个活动 `id` 作为自己的条目。
   2. 按降序扫描 `workspace/archive/findings_pass_<N>/`（以及遗留的 `loop<N>_findings/`）。只有当它仍然是打开的（见 4）AND 工作集中没有发现与它相同的 Bug（根据上述谓词）AND 没有更早（更高运行）的相同 Bug 的归档副本已经被添加时，才添加一个归档发现。第一个遇到的副本 = 最新状态；忽略较低目录中相同 Bug 的后续副本。（一个归档发现只有在真实的相同 Bug 超过它时才会被抑制；仅仅是 `lineage_id` 或 `signature` 的巧合不会抑制它。）
   3. **超集折叠（阶段 3）：** 当归档发现是当前发现的同一个 Bug（谓词 ii）时，当前发现会超过它——在当前（最新）状态下显示一个条目；不要也渲染归档副本。当谓词不满足（不同的 `signature`，例如文件重命名，或 `lineage_id` 缺失）时，作为单独的条目渲染两者（安全的过报告，永远不会隐藏）。
     - **欠报告防护：** 如果当前（超过）发现失败 actionable 谓词（步骤 4 下方），但归档祖先会通过它（例如，祖先被 `reproduced` 且打开，但当前运行的重现由于新快照上的瞬态构建/环境故障导致 `not_attempted`），不要让瞬态降级抑制已确认打开的 Bug。相反，保留祖先的最后确认状态在报告中可见（用注释 "Open — repro pending on new snapshot" 渲染它），以便先前确认的 Bug 永远不会从报告中静默消失。当前发现的更新元数据（例如，更新的 `code_paths` 行号）仍然可以作为注释附加，但显示的裁决/状态必须是祖先的最后确认状态，永远不会是瞬态降级。
   4. **可行动性/质量谓词**（适用于活动和归档）：
      只有当它是利用链（`constituent_findings` 存在，或在标题/历史中为 "Exploit Chain"）OR `repro_status` 是 `reproduced` OR (`repro_status` 是 `statically_confirmed` AND 它携带经验证据——一个外部堆栈跟踪、清理器跟踪（ASan/UBSan/MSan/TSan）或崩溃日志）时才包括一个发现。不包括误报，`NON_VIABLE`，`DUPLICATE`，`failed_to_reproduce` 或没有经验跟踪的普通 `statically_confirmed` 发现。
   5. **打开谓词**（仅在步骤 2 中归档转发）：
      如果归档发现满足（4）AND `patch_status` 不是 `VERIFIED_SECURE`/`MITIGATION_PROPOSED` AND `status` 不是 `FALSE_POSITIVE`/`DUPLICATE` AND `production_viability` 不是 `NON_VIABLE`，则归档发现是 "仍然打开的"。（活动发现是加载的，而不管 `patch_status` 如何，因此本次运行的修复仍然会显示；归档的已修复发现不会每个运行重新列出——使用可选的 "Resolved this campaign" 汇总以获得累积修复视图。）
   6. **规模**：一次处理一个目录，按最新顺序；永远不会一次性加载整个存档。

   - **严重性过滤**：从主报告正文中排除优先级为 `"LOW"` 的发现。你必须将这些低优先级问题放入报告末尾的单独、专门的 "附录：低优先级发现" 部分中，以保持主报告专注于高风险问题。

2. **提取关键工件**：对于每个可复现的发现，提取并格式化：

   - **头部元数据**：标题、ID（UUID）、推断出的暴露、最终风险评分和定性优先级。
   - **活动来源**：用它首次发现的轮次与当前轮次标注每个打开的发现（例如 `discovered pass 2 · still open as of pass 7`），以便转发的发现作为此类可见。首次发现 = 发现中 `history` 条目中最低的 `pass_number`（或包含它的最低编号归档目录的 `pass_number`）；当前状态 = 你从上述折叠中保留的副本。
   - **重复建议**：如果发现有一个 `possible_duplicate_of` 字段（由 `mantis-dedupe` 在跨运行候选不是 `NOT_MATCHED` 时设置），发出一个建议注释：
     `可能与发现 <UUID> 相关（跨运行候选；快照不同——未确认重复）。`
     这使建议的回归指针对利益相关者可见。
   - **发现快照**：为发现发出 `Discovery Snapshot: <discovery_commit>`。如果 `discovery_commit` 缺失或为空，发出 `Discovery Snapshot: (遗留——未记录)`。永远不会因为此字段缺失而省略或丢弃发现。
   - **漏洞描述和影响**：对 Bug 的清晰解释以及对系统的影响的具体说明。
   - **复现证据**：
     - PoC 脚本路径（`repro_file_path`）和执行命令（`run_command`）。
     - 显示成功利用触发器的干净片段的 stdout/stderr（`repro_output`）。
     - **证据基础**：用它收集的快照标记复现证据：`Evidence base: <repro_snapshot_id>`。如果 `repro_snapshot_id` 缺失或为空，写入 `Evidence base: (未记录)`。不要假设它等于头部/运行快照。
   - **风险推理**：独立验证推理（`reasoning`）、生产可行性推理（`critic_reasoning`）和愤怒因素分析（`outrage_commentary`）。
   - **修复和补丁**：
     - 推荐的缓解策略。
     - 经验证的补丁差异（`patch_diff`）和重新攻击状态以证明修复是弹性的。
     - **应用于**：用它应用于的快照标记补丁差异：`Apply against: <patch_base_snapshot>`。如果 `patch_base_snapshot` 缺失或为空，写入 `Apply against: (未记录)`。如果 `patch_base_snapshot` 存在且与该发现的 `discovery_commit` 不同，添加一行警告，说明补丁差异是针对不同的快照生成的，可能无法干净地应用于发现快照。
   - **PII & 密码红移**：在将任何发现数据（包括描述、PoC 脚本/命令和复现器日志）写入报告之前，你必须扫描和红移任何硬编码的 API 密钥、令牌、凭证、PII（姓名、电子邮件、电话号码）、内部主机名/域名和过度武器化的负载参数，将它们替换为标准占位符，如 `<REDACTED_SECRET>`、`<REDACTED_PII>`、`<REDACTED_INTERNAL_HOST>` 或 `<REDACTED_PAYLOAD>`，以确保报告适合更广泛的分发。

3. **生成审查包**：

   - **报告头部和免责声明**：在报告顶部（在执行摘要之前）：

     **快照来源横幅——在下面第 1 项之前，在报告的顶部，每个作为其自己的分隔块引用，按此顺序发出：**

a. **非权威性 / HALT 标记（三态规则）。** 从 `workspace/.mantis_state.json` 读取 `active_snapshot`。- 如果 `active_snapshot` **不存在**（MODE-OFF — 未请求 `--sync`，今日默认）：则不显示此标记。今天的运行是字节对字节的行为；报告的 `VERIFIED_SECURE` 发现和其他结论是有效的。在此处显示非权威性标记将与同一运行产生的结论相矛盾。- 如果 `active_snapshot` **存在** 但 `snapshot_pinned` 为 `false`（HALT 模式）：作为报告的第一行显示：
     `> **警告 — 非权威性结果：** 目标无法固定到不可变的快照中（HALT 模式：树竞争或太大 / 活动 / 复制失败）。发现可能无法对应到一个稳定、可重现的树，并且在此报告中未发现结果**不**表示目标安全。将所有结果视为临时结果。`
     当 `active_snapshot` 不存在（MODE-OFF）或 `active_snapshot.snapshot_pinned` 为 `true`（已固定）时，省略此标记。

     b. **脏工作树警告。** 如果 `vcs_info.dirty` 为 `true`，则显示：
     `> **警告 — 脏工作树：** 扫描目标时存在未提交的本地修改。结果反映的是精确的工作树（通过内容哈希捕获），**不是**干净的提交版本。单独记录的提交无法重现此状态。`

     c. **混合快照标记。** 令 HEADER_SID = `active_snapshot.snapshot_id`。如果 HEADER_SID 存在且非空，并且任何包含的发现具有 `discovery_commit` 为缺失、空或与 HEADER_SID 字符串不等于，则显示：
     `> **警告 — 混合快照：** 此报告结合了在不同代码快照上发现的发现（例如，从早期运行重试的发现）。运行快照是 <HEADER_SID>。在采取行动之前，请参考每个发现的“发现快照”；不同快照之间的行号和代码上下文可能不同。`
     仅按精确字符串比较快照 ID — 不进行模糊或前缀匹配。

     1. 显示从 `workspace/.mantis_state.json` 中读取的 `"vcs_info"` 的目标代码库版本信息：

        - 如果 `"vcs_type"` 为 `"git"`，则显示：
          `目标版本：Git 分支 [branch] 在提交 [commit_hash] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 为 `"hg"`，则显示：
          `目标版本：Mercurial 分支 [branch] 在版本 [commit_hash] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 为 `"multi-vcs"`，则显示：
          `目标版本：多 VCS (仓库) 清单 [revision] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 为 `"none"`，则显示：
          `目标版本：无（未检测到版本控制）。`。
        - 如果 `"vcs_type"` 为 `"unknown"`，或者 `vcs_info` 缺失，则显示：
          `目标版本：未知（VCS 检测失败/错误）`。

        在 `Target Version:` 行之后，在第二行追加运行快照标识：

        - 如果 `active_snapshot.snapshot_id` 存在且非空，则写入：
          `快照 ID: [snapshot_id]  (已固定: [snapshot_pinned])`。
        - 如果 `active_snapshot` 缺失或 `snapshot_id` 为空，则写入：
          `快照 ID: (遗留 — 未记录快照)。` 这是仅用于显示的来源；它不会阻止或丢弃任何发现。

     2. 包含一个显眼的免责声明，声明：*“此报告由 Mantis AI 自动生成。所有发现和补丁都是 AI 生成的，必须在部署或披露前由安全或主题专家手动验证。”*

   - **按补丁状态分组（排他性）：** 将执行摘要表格和报告主体按发现分组。**利用链必须排除在这些主要分组之外，并且仅在专门的“利用链（未完全重现）”部分中报告。** 对于标准（非链）发现，根据其修复状态（严格互斥）将其分为三个不同类别：

     1. **类别 1：独立验证的补丁**：`patch_status` 为 `"VERIFIED_SECURE"` 的发现。
     2. **类别 2：提议补丁 / 识别缓解措施**：`patch_status` 在 `["MITIGATION_PROPOSED", "VERIFICATION_INCOMPLETE"]` 或 (`patch_diff` 存在 AND `patch_status` 未设置/为空) 的发现。
     3. **类别 3：未修复 / 验证失败**：`patch_status` 在 `["VERIFICATION_FAILED", "ERROR"]` 或 (`patch_diff` 不存在 AND `patch_status` 未设置/为空) 的发现。

   - **专门的利用链部分：** 创建一个名为 `"利用链（未完全重现）”` 的专门部分，专门用于利用链。在此处记录每个链发现，列出其标题、定性优先级、风险评分，并详细说明其构成发现（它们的 ID 和单独状态）。不要将利用链与类别 1、2 或 3 中的标准发现混合。

   - **按运行编号输出：** 不要在每次执行时覆盖相同的 `review_packet.md` 文件。相反，确定管道的当前运行/编号 `N`（从 `workspace/.mantis_state.json` 中的 `"pass_number"` 解析。如果缺失或无效，扫描 `workspace/archive/` 以查找匹配 `findings_pass_N` 或 `loopN_findings` 的文件夹，并将 `N` 解析为 `max_found + 1`，如果不存在存档则默认为 1）。然后从 `active_snapshot.snapshot_id` 衍生出 `<snapshot_tag>`：取存储的快照 ID，并将不在 `[A-Za-z0-9.-]` 中的每个字符替换为单个下划线 `_`（不要截断 — 结果保持在任何文件名长度限制以下）。将报告写入：

     - `workspace/report/review_packet_pass_<N>_<snapshot_tag>.md` 当 `active_snapshot.snapshot_id` 存在且非空（例如 `review_packet_pass_1_content_9f86d081884c...md`）。`<snapshot_tag>` 后缀确保对不同的快照运行重用相同的编号会写入不同的文件，并且不会覆盖先前的包。
     - `workspace/report/review_packet_pass_<N>.md`（无后缀 — 恰好是遗留名称），保留今日向后兼容的行为。

   - **最新副本/链接：** 在写入上述按运行编号的报告之后，更新一个链接或写入该确切文件（无论是否带有 `<snapshot_tag>` 后缀）到 `workspace/report/review_packet-latest.md`，以便最新版本始终可访问。`review_packet-latest.md` 的名称保持不变，并仍然是下游消费者的稳定入口点。

   - 使用干净、专业的 Markdown 格式，带有清晰的标题、用于元数据的表格，以及用于日志和差异的语法高亮代码块。

   - 在顶部包含一个高级 **执行摘要** 表格，列出所有包含的发现、它们的优先级和风险评分。

   - **可选部分（推荐）：**

     - **已解决此活动：** 使用相同的折叠，但过滤到 `patch_status` 为 `VERIFIED_SECURE` 或 `MITIGATION_PROPOSED` 的发现。这为利益相关者提供了一个可见的“已修复”视图，与开放的发现一起显示。
     - **未解决 — 重试次数达到上限：** 列出重试次数达到上限的开放发现。计数不是发现 JSON 的字段；它存在于缓存文件 `state_root/workspace/archive/.repro_attempts.json` 中，按每个发现的 `signature`（如果 `signature` 缺失，则按计算出的 `stable_key` = `normalized_title + "@" + primary_file_path`）键值。对于工作集中的每个开放发现，查找其 `signature`（或 `stable_key` 备用）。如果缓存值达到重试上限，则在此处包含该发现。根据模式的价值形状规则读取缓存值：一个裸整数 V 表示 `{count: V, last_snapshot: UNKNOWN}`；一个对象表示 `{count: V.count, last_snapshot: V.last_snapshot 或 UNKNOWN}`。如果缓存文件缺失或发现的键不存在，将其计数视为 0（不要列出它）。这些都是规划者停止携带的项目

   > [!NOTE] **去重注意事项：** 去重是按发现身份进行的，根据本阶段顶部的 **相同错误预测**：只有当 (i) 它们共享完全相同的 `id`（UUID）时，或者 (ii) 所有三个都满足 — 共享的非空 `lineage_id`、共享的非空 `signature`，并且至少有一条 `code_paths` 的行包含匹配时，两个发现才会折叠。永远不要单独基于 `lineage_id` 或单独基于 `signature` 进行折叠（基于文件名生成的 lineage 可以链接两个不同的同名文件；`signature` 剥掉了行号，因此会在不同的同名文件错误中冲突）— 单独折叠可能会无声地丢弃真实发现。在重新发现一个不满足预测 (ii) 的新 UUID 下 — 一个回归、文件重命名导致行号移动，或非确定性重新发现 — 列为与其存档祖先的**单独条目**：会报告过多（安全），永远不会隐藏。随着稳定的发现签名和 lineage 跟踪落地（阶段 3），当预测 (ii) 完全满足时，重新发现的发现才会折叠到其祖先的单一条目中；UUID 仅匹配仍然是遗留/未升级发现的安全分支。

   - **`review_packet-latest.md` 是权威的：** 注意 `review_packet-latest.md` 现在是整个活动（不仅仅是最新运行）的权威当前开放状态。每个运行的 `review_packet_pass_<N>_<snapshot_tag>.md` 文件保持不变，供历史参考。
