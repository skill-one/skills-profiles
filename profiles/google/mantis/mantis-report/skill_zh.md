# Reporter (/mantis-report)

## 系统目标

安全报告专家。将复杂的、技术性的发现日志综合成高质量、人类可读的审查包，供开发人员和利益相关者使用。

## 命令定义

- **命令**：`/mantis-report`
- **描述**：生成包含已确认发现和利用链的人类可读安全审查包。

## 输入/输出契约

- **读取**：
  - `workspace/findings/*.json`（本次传递的所有活动发现文件）。
  - `workspace/archive/findings_pass_*/*.json`（先前传递的存档发现）和遗留的 `workspace/archive/loop*_findings/*.json`。报告是一个跨活动范围的视图：本次传递的完整发现加上先前传递中停止重试（例如达到重试上限）而不会从报告中消失的传递转发发现。
  - `workspace/.mantis_state.json`（用于跟踪当前循环传递，并读取 `vcs_info` 和 `active_snapshot` {`root`, `snapshot_id`, `snapshot_pinned`} 以进行溯源）。
  - 每个发现的快照溯源字段，全部可选：`discovery_commit`, `repro_snapshot_id`, `patch_base_snapshot`。当任何一个缺失/为空时，它会被渲染为 "(未记录)" —— 永远不会因为发现而丢弃。
- **写入**：
  - `workspace/report/review_packet_pass_<N>_<snapshot_tag>.md`（传递和快照标签标记的 Markdown 报告）。在遗留无记录快照的传递上回退到无后缀的 `review_packet_pass_<N>.md`。
  - 更新 `workspace/report/review_packet-latest.md` 处的副本/链接。
- **前提条件**：
  - 在 `workspace/findings/` 或 `workspace/archive/` 中存在校准和可复现的发现。报告是一个跨活动范围的视图：它报告在本传递或任何先前传递中发现的每个未解决发现的当前状态，每个发现的最新状态去重。一个已确认但未修复的发现如果计划停止转发（例如，它达到了 2 次尝试的重试上限），则不会消失——它会以其最新的存档状态出现在这里。
- **幂等性保证**：
  - 写入传递和快照标签文件。原地覆盖 `review_packet-latest.md`。在相同的快照上重新运行相同的传递更新相同的标签文件。在不同的快照上重新运行相同的传递编号写入不同的文件（`<snapshot_tag>` 后缀防止跨快照覆盖）。无记录快照的遗留传递保留无后缀的 `review_packet_pass_<N>.md` 名称并原地覆盖，与之前完全相同。

## 说明

**步骤 0 — 定位器解析。**

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果这个技能永远不会读取目标源（报告、校准、反映），你是一个仅发现阶段：跳过步骤 2-6；仍然读取状态中的 `active_snapshot` 以进行溯源/注释；永远不会因为代码根未设置而停止。
1. 确定代码根，按此优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，代码根 = `--target_root`。它是权威的，并且覆盖了 `SNAPSHOT_ROOT` 和状态回退（在调用者将你交给准备好的树时使用，例如一个修补的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），使用它。
   c. 否则读取状态根 `workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用状态根，否则相对于当前目录的 ./workspace/...）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：代码根 = 当前目录，将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 边界检查（仅当 `snapshot_pinned` 为真且你没有采取路径 1a 时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。 （`--target_root` 树 (1a) 是故意被修改的，并且豁免于哨兵检查。）
3. 路径字段：
   - 快照相对（在代码根下读取）：`code_paths` 条目；计划目标文件（文件路径）。只删除尾部的 `:<数字>`。包含 "://" 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：只检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在状态根 `workspace` 下读取/写入，永远不会以 `CODE_ROOT` 为前缀）：
     `kb_references`, `repro_file_path`, `reattack_file_path`, 帮助脚本、报告文件，以及所有状态/发现 JSON。
4. 当 `snapshot_pinned` 为真时，永远不要在 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在 `CODE_ROOT` 的私有影子副本（从 `CODE_ROOT` 使用 `mktemp -d`）中运行，永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切割：历史日志提取和在 LIVE 仓库根（仍然有 `.git/.hg/.repo`）中运行的任何 VCS diff/blame 命令，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。不要因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径并在此调用上设置它自己的工作目录。不要假设工作目录在调用之间持久存在。
```

然后，以下仅发现的注释适用于 Reporter：

- Reporter 是仅发现阶段（块 A，角色步骤 0）：它跳过定位器步骤 2-6，不需要或解析代码根，并且永远不会因为代码根或哨兵未设置而停止。
- 它仍然读取 `active_snapshot`（`root`, `snapshot_id`, `snapshot_pinned`）和 `workspace/.mantis_state.json` 中的 `vcs_info` 以进行溯源——用于构建标题、顶部横幅和输出文件名。
- Reporter 触摸的每个路径（`workspace/findings/*.json`, `workspace/.mantis_state.json`, `workspace/report/*`, `workspace/archive/*`）都是状态相对的，并且永远不会以 `CODE_ROOT` 为前缀。

编译专业的 Markdown 报告，详细说明已验证/可复现的漏洞和利用链。

按以下方式执行报告阶段：

1. **加载发现——本次传递的全部内容，以及转发打开的发现（按最新顺序折叠；无脚本）。** 构建一个按发现身份键控的工作集，每个发现在其最新状态下只出现一次：

   **相同 Bug 预测**（用于本阶段所有当前↔存档去重、折叠和抑制；过度报告总是安全的，隐藏真实发现永远不可接受）：只有当两个发现满足以下任一条件时，它们才是相同的 Bug：(i) 它们具有完全相同的 `id`（UUID）；或者 (ii) 它们共享一个非空的 `lineage_id`，它们共享一个非空的 `signature`，并且至少一个 `code_paths` 条目与它们的尾部的 `:line`（包含行）相同。否则它们是不同的——渲染两者。永远不要在 `lineage_id` 单独或 `signature` 单独上认为两个发现是相同的 Bug：两者都比 Bug 的真实身份（基于 basename 派生的 lineage 可以链接两个不同的同名的文件；`signature` 剥掉了行号，所以在不同的同名文件 Bug 之间冲突），并且单独折叠任何一个都可能无声地丢弃一个真实发现。

   **设计说明（重新锚定 vs 折叠）**：`mantis-plan` 的重新锚定（阶段 2\) 只提供一个行提示，引导重新发现——它不会重写转发发现的 `code_paths`。重新发现的发现会在当前快照的新行上出现。因为折叠预测需要行包含的 `code_paths` 匹配，重新发现的发现将不会与它的祖先折叠（行号不同）。这是安全的过度报告——两者都渲染，当前一个显示新位置。未来阶段可以放宽预测，当两者都携带相同的 `signature` 和 `lineage_id`，并且祖先的行在当前快照中确认不存在时，进行路径仅匹配，但今天使用的保守行包含匹配是为了防止任何无声丢弃风险。

   1. 读取所有活动的 `workspace/findings/*.json` 并将每个活动发现添加到工作集中，按其 `id`（UUID）键控——所有修复状态，所以本次传递的 `VERIFIED_SECURE`/`MITIGATION_PROPOSED` 修复仍然与其补丁一起显示在类别 1/2 中。永远不会折叠两个活动发现，即使它们共享 `lineage_id` 或 `signature`——保持每个活动 `id` 作为自己的条目。
   2. 扫描 `workspace/archive/findings_pass_<N>/`（以及遗留的 `loop<N>_findings/`）按降序传递。只有当存档发现仍然打开（见 4）并且工作集中没有发现与它相同的 Bug（根据上述预测）并且没有更早（更高传递）的相同 Bug 的存档副本已添加时，才添加一个存档发现。第一个遇到的副本 = 最新状态；忽略较低目录中的相同 Bug 副本。（存档发现只有在真实的相同 Bug 超过它时才会被抑制；仅仅是 `lineage_id` 或 `signature` 的巧合不会抑制它。）
   3. **超继折叠（阶段 3）**：当存档发现是当前发现的相同 Bug（预测 ii）时，当前发现会超过它——显示一个当前（最新）状态的单一条目；不要也渲染存档副本。当预测不满足时（不同的 `signature`，例如文件重命名），将两者作为单独的条目渲染（安全的过度报告，永远不会隐藏）。
      - **欠报告防护**：如果当前（超继）发现失败可行动预测（步骤 4 下方），但存档祖先会通过它（例如，祖先被 `reproduced` 且打开，但当前传递的重新发现由于瞬态构建/环境失败而导致 `not_attempted`），不要让瞬态降级抑制已确认打开的 Bug。相反，保持祖先的最后确认状态在报告中可见（使用注释 "Open — 在新快照上等待重新发现" 渲染它），以便先前确认的 Bug 永远不会无声地从报告中消失。当前发现的更新元数据（例如，更新的 `code_paths` 行号）仍然可以附加为注释，但显示的裁决/状态必须是祖先的最后确认状态，永远不会是瞬态降级。
   4. **可行动/质量预测**（适用于活动和存档）：仅包括它是利用链（`constituent_findings` 存在，或在标题/历史中为 "Exploit Chain"）或 `repro_status` 是 `reproduced` 或 (`repro_status` 是 `statically_confirmed` 且携带经验执行证据——外部堆栈跟踪、清理器跟踪 (ASan/UBSan/MSan/TSan) 或崩溃日志）。不包括误报、`NON_VIABLE`、`DUPLICATE`、`failed_to_reproduce` 或没有经验跟踪的普通 `statically_confirmed` 发现。
   5. **打开预测**（仅步骤 2 中的存档转发）：如果存档发现满足 (4) 且 `patch_status` 不是 `VERIFIED_SECURE`/`MITIGATION_PROPOSED` 且 `status` 不是 `FALSE_POSITIVE`/`DUPLICATE` 且 `production_viability` 不是 `NON_VIABLE`。 （活动发现无论 `patch_status` 如何加载，所以本次传递的修复仍然可见；存档已修复的发现不会每个传递重新列出——使用可选的 "本次活动已解决" 汇总以获得累积修复视图。）
   6. **规模**：一次处理一个目录，按最新顺序；永远不会一次加载整个存档。

   - **严重性过滤**：从主报告正文中排除优先级为 `"LOW"` 的发现。你必须将这些低优先级问题放入报告末尾的单独、专门的 "附录：低优先级发现" 部分中，以保持主报告专注于高风险问题。

2. **提取关键工件**：对于每个可复现的发现，提取和格式化：

   - **标题元数据**：标题、ID（UUID）、推断出的暴露、最终风险评分和定性优先级。
   - **活动溯源**：用发现首次发现的传递与当前传递（例如 `discovered pass 2 · still open as of pass 7`）注释每个打开的发现，以便转发发现可见为转发发现。首次出现 = `history` 条目中最低的 `pass_number`（或包含它的最低编号存档目录的传递编号）；当前状态 = 你从上述折叠中保留的副本。
   - **重复建议**：如果发现具有 `possible_duplicate_of` 字段（由 `mantis-dedupe` 在跨传递候选者未匹配时设置），发出建议注释：
     `可能与发现 <UUID> 相关（跨传递候选者；快照不同——未确认重复）。`
     这使建议的回归指针对利益相关者可见。
   - **发现快照**：为发现发出 `Discovery Snapshot: <discovery_commit>`。如果 `discovery_commit` 缺失或为空，发出 `Discovery Snapshot: (遗留 — 未记录)`。永远不会因为此字段缺失而省略或丢弃发现。
   - **漏洞描述和影响**：对 Bug 的清晰解释以及对系统的影响的具体说明。
   - **复现证据**：
     - PoC 脚本路径 (`repro_file_path`) 和执行命令 (`run_command`)。
     - 显示成功利用触发器的干净片段 (`repro_output`)。
     - **证据基础**：用它被收集的快照标记复现证据：`Evidence base: <repro_snapshot_id>`。如果 `repro_snapshot_id` 缺失或为空，写入 `Evidence base: (未记录)`。不要假设它等于标题/传递快照。
   - **风险推理**：独立验证推理 (`reasoning`)、生产可行性推理 (`critic_reasoning`) 和愤怒因素分析 (`outrage_commentary`)。
   - **修复和补丁**：
     - 推荐的缓解策略。
     - 已验证的补丁差异 (`patch_diff`) 和重新攻击状态以证明修复是弹性的。
     - **应用于**：用它应用的快照标记补丁差异：`Apply against: <patch_base_snapshot>`。如果 `patch_base_snapshot` 缺失或为空，写入 `Apply against: (未记录)`。如果 `patch_base_snapshot` 存在且与该发现的 `discovery_commit` 不同，添加一行警告，说明补丁是针对不同的快照生成的，可能无法干净地应用于发现快照。
   - **PII 和秘密脱敏**：在将任何发现数据（包括描述、PoC 脚本/命令和复现器日志）写入报告之前，你必须扫描和脱敏任何硬编码的 API 密钥、令牌、凭证、PII（姓名、电子邮件、电话号码）、内部主机名/域名和过度武器化的有效载荷参数，将它们替换为标准占位符，如 `<REDACTED_SECRET>`、`<REDACTED_PII>`、`<REDACTED_INTERNAL_HOST>` 或 `<REDACTED_PAYLOAD>`，以确保报告适合更广泛的分发。

3. **生成审查包**：

   - **报告标题和免责声明**：在报告顶部（在执行摘要之前）：

     **快照溯源横幅**——在以下项目之前，在报告的顶部，每个作为其自己的分隔块引用，按此顺序：**

     a. **非权威性 / 停止横幅（三态规则）。** 从 `workspace/.mantis_state.json` 中读取 `active_snapshot`。- 如果 `active_snapshot` 缺失（模式关闭——没有请求 `--sync`，今天的默认值）：不要发出此横幅。运行是今天的字节对应行为；报告的 `VERIFIED_SECURE` 发现和其他裁决是今天有效的。在此处发出非权威性横幅会与同一运行产生的裁决相矛盾。- 如果 `active_snapshot` 存在但 `snapshot_pinned` 为 `false`（停止模式）：作为报告的第一行发出：
     `> **警告 — 非权威性结果：** 目标无法固定到本次传递的不可变快照（停止模式：树竞争或太大 / 活的 / 复制失败）。发现可能不对应于一个稳定、可复现的树，并且报告中发现的缺失**不**表示目标是安全的。将所有结果视为临时性的。`
     当 `active_snapshot` 缺失（模式关闭）或当 `active_snapshot.snapshot_pinned` 为 `true`（已固定）时，省略此横幅。

     b. **脏工作树警告。** 如果 `vcs_info.dirty` 为 `true`，发出：
     `> **警告 — 脏工作树：** 目标在扫描时具有未提交的本地修改。结果反映确切的工件树（由内容哈希捕获），而不是干净的提交修订版。仅记录的提交本身无法重现此状态。`

     c. **混合快照横幅。** 让 HEADER_SID =
     `active_snapshot.snapshot_id`。如果 HEADER_SID 存在且非空，并且任何包含的发现具有缺失、空的或与 HEADER_SID 字符串相等的 `discovery_commit`，发出：
     `> **警告 — 混合快照：** 此报告结合了在不同代码快照上发现的发现（例如，从先前传递中重试的发现）。传递快照是 <HEADER_SID>。在采取行动之前，请参考每个发现的 "发现快照"；快照之间的行号和代码上下文可能不同。`
     仅按确切字符串比较快照 ID——不要模糊或前缀匹配。

     1. 显示从 `workspace/.mantis_state.json` 中的 `"vcs_info"` 读取的目标代码库版本信息：
        - 如果 `"vcs_type"` 是 `"git"`，显示：
          `Target Version: Git 分支 [branch] 在提交 [commit_hash] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 是 `"hg"`，显示：
          `Target Version: Mercurial 分支 [branch] 在修订 [commit_hash] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 是 `"multi-vcs"`，显示：
          `Target Version: 多 VCS (仓库) 元数据 [revision] [(dirty) 如果 dirty 为 true]`。
        - 如果 `"vcs_type"` 是 `"none"`，显示：
          `Target Version: 无 (未检测到版本控制)`。
        - 如果 `"vcs_type"` 是 `"unknown"`，或者如果 `vcs_info` 缺失，显示：
          `Target Version: 未知 (VCS 检测失败/错误)`。

        在 `Target Version:` 行之后，在第二行追加传递快照标识：
        - 如果 `active_snapshot.snapshot_id` 存在且非空，写入：
          `Snapshot ID: [snapshot_id]  (pinned: [snapshot_pinned])`。
        - 如果 `active_snapshot` 缺失或 `snapshot_id` 为空，写入：
          `Snapshot ID: (遗留 — 未记录)`。这是显示仅溯源；它不会阻止或丢弃任何发现。

     2. 包含一个突出的免责声明，说明：*“此报告由 Mantis AI 自动生成。所有发现和补丁都是 AI 生成的，在部署或披露之前必须由安全或主题专家手动验证。”*

   - **按修复状态分组（排他性）**：按分组组织执行摘要表和报告正文。**利用链必须排除在这些主组之外，并且仅在专门的 "Exploit Chains (Not End-to-End Reproduced)" 部分中报告。** 对于标准（非链）发现，根据它们的修复状态将它们分为三个不同的类别（严格互斥）：

     1. **类别 1：独立验证修复**：`patch_status` 为 `"VERIFIED_SECURE"` 的发现。
     2. **类别 2：提议修复 / 识别缓解**：`patch_status` 在 `["MITIGATION_PROPOSED", "VERIFICATION_INCOMPLETE"]` 或 (`patch_diff` 存在 且 `patch_status` 未设置/为空) 的发现。
     3. **类别 3：未修复 / 验证失败**：`patch_status` 在 `["VERIFICATION_FAILED", "ERROR"]` 或 (`patch_diff` 不存在 且 `patch_status` 未设置/为空) 的发现。

   - **专门的利用链部分**：创建一个专门的标题为 `"Exploit Chains (Not End-to-End Reproduced)" 的部分，专门用于利用链。在此处记录每个链发现，列出其标题、定性优先级、风险评分，并详细说明其构成发现（它们的 ID 和各自状态）。

   - **按传递编号输出**：不要在每次执行时覆盖相同的 `review_packet.md` 文件。相反，确定当前运行/传递编号 `N`（从 `workspace/.mantis_state.json` 中的 `"pass_number"` 解析。如果缺失或无效，扫描 `workspace/archive/` 以查找匹配 `findings_pass_N` 或 `loopN_findings` 的文件夹并解析 `N` 为 `max_found + 1`，如果不存在存档，则默认为 1）。然后从 `active_snapshot.snapshot_id` 派生 `<snapshot_tag>`：将存储的快照 ID 按确切字符替换为单个下划线 `_`（不要截断——结果保持在任何文件名长度限制以下）。然后将报告写入：

     - 当 `active_snapshot.snapshot_id` 存在且非空时（例如 `review_packet_pass_1_content_9f86d081884c...md`），写入 `workspace/report/review_packet_pass_<N>_<snapshot_tag>.md`。`<snapshot_tag>` 后缀保证在针对不同快照的重复传递编号写入不同的文件，并且不能覆盖早期的包。
     - 当 `active_snapshot` 缺失或 `snapshot_id` 为空时，写入 `workspace/report/review_packet_pass_<N>.md`（无后缀——完全遗留名称），保留今天的向后兼容行为。

   - **最新副本/链接**：在写入上述传递编号报告后，更新 `workspace/report/review_packet-latest.md` 处的链接或写入该确切文件（无论它是否携带 `<snapshot_tag>` 后缀），以便最新版本始终可访问。`review_packet-latest.md` 的名称保持不变，并仍然是下游消费者稳定的入口点。

   - 使用干净的、专业的 Markdown 格式化，具有清晰的标题、用于元数据的表格，以及用于日志和差异的语法高亮代码块。

   - 在顶部包含一个高级 **执行摘要** 表，列出所有包含的发现、它们的优先级和它们的风险评分。

   - **可选部分（推荐）**：

     - **本次活动已解决**：使用相同的折叠，但过滤到 `patch_status` 为 `VERIFIED_SECURE` 或 `MITIGATION_PROPOSED` 的发现。这为利益相关者提供了一个可见的 "已修复" 视图，与打开的发现一起出现。
     - **未解决 — 达到重试上限**：一个提示列出那些复现尝试次数达到上限的打开发现。计数不是发现 JSON 上的字段；它存在于缓存文件 `state_root/workspace/archive/.repro_attempts.json` 中，按每个发现的 `signature` 键（如果 `signature` 缺失，则按计算出的 `stable_key` = `normalized_title + "@" + primary_file_path` — 与 `mantis-reproduce` 使用相同的键选择）。对于工作集中的每个打开发现，在缓存中查找其 `signature`（或 `stable_key` 回退），如果缓存的值达到重试上限，则包括此发现在此提示中。根据模式的价值形状规则读取缓存值：一个裸整数 V 表示 `{count: V, last_snapshot: UNKNOWN}`；一个对象表示 `{count: V.count, last_snapshot: V.last_snapshot or UNKNOWN}`。如果缓存文件缺失或发现的键缺失，将其计数视为 0（不要列出它在此处）。这些是规划器停止转发的事项

> [!NOTE] **去重警告**：去重是按发现身份进行的，根据此阶段顶部的 **相同 Bug 预测**：只有当 (i) 它们共享完全相同的 `id` (UUID) 或 (ii) 所有三个都满足——共享非空的 `lineage_id`，共享非空的 `signature`，并且至少有一个行包含的 `code_paths` 匹配时，两个发现才会折叠。永远不要单独在 `lineage_id` 或单独在 `signature` 上折叠（基于 basename 派生的 lineage 可以链接两个不同的同名的文件；`signature` 剥掉了行号，所以在不同的同名文件 Bug 之间冲突）——单独折叠任何一个都可能无声地丢弃一个真实发现。重新发现的 Bug 在新 UUID 下不满足预测 (ii)——回归、文件重命名导致行号变化或非确定性重新发现——作为其存档祖先的单独条目列出：过度报告（安全），永远不会隐藏。随着稳定的发现签名和 lineage 跟踪落地（阶段 3），当完全满足预测 (ii) 时，重新发现的发现会折叠到其祖先的单一条目中；UUID 仅匹配仍然是遗留/未升级发现的 safe 分支。

   - **`review_packet-latest.md` 是权威的**：请注意，`review_packet-latest.md` 现在是整个活动范围的权威当前打开状态（而不仅仅是最新传递）。每个传递的 `review_packet_pass_<N>_<snapshot_tag>.md` 文件保持原样，供历史参考。
