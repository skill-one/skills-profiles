# Reviewer (/mantis-review)

## 系统目标

独立验证器。将整合的发现与活动源代码进行比对，以验证有效性并过滤掉噪音和误报。

## 命令定义

- **命令：** `/mantis-review`
- **描述：** 独立审查发现并过滤掉误报。

## 输入/输出契约

- **读取**：
  - `workspace/findings/` (发现 JSON 文件，包括每个发现的可选 `discovery_commit` 起源戳)。
  - `workspace/.mantis_state.json` (当前循环 `pass_number`；以及，当存在时，`active_snapshot` = `{root, snapshot_id, snapshot_pinned}` 用于快照溯源)。
  - 由协调器传递的调用参数：`--snapshot_root`、`--snapshot_id`、`--state_root` (以及，很少情况下，`--target_root`)。
  - 目标源代码文件在 `code_paths` 路径/行号处，在解析的 `CODE_ROOT` 下读取 (即固定的快照根 - 见说明步骤 0 / 块 A)，当快照固定时，永远不会在活动树中读取。
- **写入**：
  - 在磁盘上就地更新发现 (设置 `"status"`、`"reasoning"`、`"repro_hints"`、`"triage_checklist"` 并追加历史记录)。
  - 写入辅助脚本 `workspace/helpers/append_review.py`。
- **前提条件**：
  - `workspace/findings/` 存在并包含发现文件。
  - 目标源代码文件存在。
- **幂等性保证**：
  - 使用辅助脚本 `append_review.py` 就地修改发现文件，该脚本的第一行必须为 `# MANTIS_HELPER_VERSION = 2`；如果缺少该标记或为不同的整数，则重新生成辅助脚本 (见说明步骤 5)。
  - 幂等性键是 **(pass_number, snapshot)**。在 (重新)写入发现之前，扫描其 `history` 数组：
    - **快照模式关闭** (既未传递 `--snapshot_id` 也无法在状态中读取 `active_snapshot`)：如果当前 `pass_number` 存在 `"stage": "reviewer"` 条目，则跳过审查更新 (与今天的行为字节对字节相同)。
    - **快照模式开启**：如果存在 `"stage": "reviewer"` 条目，其 `pass_number` 等于当前传递且其 `snapshot` 等于 `SNAPSHOT_ID`，则跳过审查更新。缺少 `snapshot` (遗留) 或携带不同 `snapshot` 的审查器条目计为未知 → 重新审查 (不要跳过)，因此在旧技能下审查的发现会重新与当前固定的快照对齐。

## 说明

读取并评估去重后的发现，与仓库的实际源代码进行比较。**默认情况下，假设每个发现都是误报。你的工作是采取对抗性立场来反驳发现。仅根据代码和原始声明本身进行评估。明确忽略原始查找者的散文推理和证明，因为它们可能是虚构的。**

按照以下方式执行你的验证：

**步骤 0 — 定位器解析与快照溯源门 (首先执行，在读取任何发现的代码之前)：**

0a. **解析读取代码的位置。** **块 A — 定位器解析** 在此处：

```
定位器解析 (在读取任何目标代码或工件之前)：
0. 角色：如果此技能永远不会读取目标源 (报告、校准、反映)，你是一个仅查找的阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行溯源/注释；仅因代码根未设置而永远不会停止。
1. 确定 `CODE_ROOT`，按以下优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，`CODE_ROOT` = `--target_root`。它是权威的，并覆盖 `SNAPSHOT_ROOT` 和状态回退 (用于调用者传递的已准备好的树，例如修补的影子)。
   b. 否则，如果传递了 `--snapshot_root` (或 `SNAPSHOT_ROOT`)，使用它。
   c. 否则，读取 `state_root/workspace/.mantis_state.json` (如果传递了 `--state_root`，则从当前目录相对于 `state_root` 的 `./workspace/...`) -> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则 (没有参数且没有可读的 `active_snapshot`)：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` 设置为 `false` (模式关闭)。不要停止。
2. 边界检查 (仅当 `snapshot_pinned` 为真且你没有采取路径 1a)：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。 (--)target_root 树 (1a) 是故意被修改的，并且是哨兵豁免的。)
3. 路径字段：
   - 快照相对 (在 `CODE_ROOT` 下读取)：`code_paths` 条目；计划目标文件为文件路径。删除仅尾部的 `:<digits>`。包含 `"://"` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器 (符号/偏移/端点)：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对 (在 `state_root/workspace` 下读取/写入，永远不会以 `CODE_ROOT` 为前缀)：
     `kb_references`、`repro_file_path`、`reattack_file_path`、辅助脚本、报告文件以及所有状态/查找 JSON。
4. 当 `snapshot_pinned` 为真时，永不向 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在私有影子副本中运行 (从 `CODE_ROOT` 使用 `mktemp -d`)，永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以进入 `CODE_ROOT`。
5. VCS-METADATA 切片：历史记录提取和在 LIVE 仓库根 (仍然有 `.git/.hg/.repo`) 中运行的任何 VCS diff/blame 命令，而不是 `CODE_ROOT` (快照副本会剥离 VCS 元数据)。不要仅仅因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径并在其调用上设置自己的工作目录。不要假设工作目录在调用之间持久存在。

审查器读取目标源，因此它不是一个仅查找的阶段：运行块 A 的所有步骤 1-6。`CODE_ROOT` 是你在步骤 0 / 块 A — 解析每个 `code_paths` 路径相对于 `CODE_ROOT` (永远不是活动树) 下读取的固定快照根。根据块 A 步骤 3，包含 `"://"` 的 `code_paths` 条目是 URL (仅存在性检查)，任何不是 `<现有路径>:<整数>` 形式的条目是非源定位器 (检查工件/符号是否存在；跳过所有行存在逻辑)。永远不要仅仅因为 `CODE_ROOT` 缺少 `.git`/`.hg` (块 A 步骤 5) 而停止。

> [!NOTE] **当前传递检查 (防御性；绑定保证是在每个 `mantis-pipeline-adapter` 场景 2 的 harness 上)**：如果 `active_snapshot` 存在且 `active_snapshot.pass != state.pass_number`，将快照视为此传递中的陈旧 — 停止 "陈旧活动快照：传递不匹配" 或降级为 HALT (`snapshot_pinned` 实际上为假：没有权威的裁决，块 B NOT_MATCHED，重新尝试 `not_attempted`)。这捕获了自定义 harness 在 Stage 15 传递增量中保留了 `active_snapshot` 而未重新固定的情况。参考元代理每次都会重新固定，所以这里永远不会触发。块 B 本身无法检测到这一点 (它是 `snapshot_id`-only，而不是 `pass`-aware)。

0b. **确定快照模式 (一次，在触摸查找之前)：** - 快照模式为 **关闭**，如果本次调用未传递 `--snapshot_id` 且 `workspace/.mantis_state.json` 没有可读的 `active_snapshot`。这是一个遗留/非同步运行：不要运行下面的快照溯源门；使用步骤 1-5 正确审查每个查找。 - 否则，快照模式为 **开启**。根据块 A，你现在持有 `SNAPSHOT_ID` 和 `snapshot_pinned`。对每个查找应用快照溯源门 (0c)。

0c. **快照溯源门 (仅快照模式开启)。** 加载查找后，应用匹配检查到每个查找 F，通过 **块 B — 快照匹配检查** 应用到 F：

```
查找 F 的快照匹配检查 (决定 MATCHED vs NOT_MATCHED)：
1. 如果 `snapshot_pinned` 为假 -> NOT_MATCHED。停止。
2. 读取 `F.discovery_commit`：
   - 缺失或为空或字面值 "MIXED" -> NOT_MATCHED。
   - 不完全等于 `SNAPSHOT_ID` -> NOT_MATCHED。
   - 恰好等于 `SNAPSHOT_ID` -> MATCHED。
没有其他路线可以匹配；永远不会模糊比较。全局 "默认字段并继续" 的向后兼容规则不适用于 `discovery_commit`：缺失 = NOT_MATCHED。(没有单独的 "脏" 门：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，因此在本传递中匹配的查找和跨传递的裸提交查找不会匹配。)

然后，使用幂等性规则 (输入/输出契约 → 幂等性保证) 避免重复写入：

- **MATCHED** → F 在当前固定的快照中扎根。对 F 执行完整的 13 规则审查 (步骤 2-5)。
- **NOT_MATCHED** (包括：`snapshot_pinned` 假 / HALT / 活动端点传递；`discovery_commit` 缺失、空或字面值 `MIXED`；或 `discovery_commit != SNAPSHOT_ID`) → F 在不同的 (或缺失/未固定) 快照中发现；其 `code_paths` 行号可能不再指向相同的代码。**不要在 F 上运行 13 规则。不要将其标记为 `FALSE_POSITIVE`。** 通过辅助脚本 (步骤 5) 最终确定 F 为漂移 `NEEDS_RESEARCH`，写入确切内容：
  - `"status": "NEEDS_RESEARCH"`
  - `"reasoning"`:
    `"快照漂移：发现针对快照 <F.discovery_commit 或 'unknown'>，这与当前固定的快照 <SNAPSHOT_ID> 不匹配。本传递未重新验证；路由到重新研究。"`
  - 忽略 `"repro_hints"` (如果 F 从先前传递中携带了陈旧的 `repro_hints`，则保留它们 — 它们在下游被忽略，因为状态不是 `VALID/PROVISIONALLY_VALID`)。
  - `"triage_checklist"`：所有 13 个约束都设置为 `UNKNOWN` (粘贴下面的对象)。此对象是必需的：追加 `reviewer` 历史条目会使 `triage_checklist` 在非链式查找上强制要求 (`schema.json` 行 365-398)，并且对于 `NEEDS_RESEARCH` 查找，每个条目必须避免 `FAIL`/`passes:false` (`schema.json` 行 418-470)。
  - 追加 `reviewer` `"history"` 条目 (包括 `"snapshot"`，根据步骤 5 / 以下历史 JSON)。

  然后停止处理 F — 跳过对它的步骤 2-5。

漂移 `triage_checklist` (粘贴原文；所有 13 个键，所有 `UNKNOWN`)：

```json
{
  "ignore_hypothetical_misuse":        { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "ignore_missing_hygiene":            { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "require_strict_reproducibility":    { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "avoid_pedantic_linting":            { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "no_security_flaw_stretching":       { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "evaluate_questionable_file_paths":  { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "ignore_resource_exhaustion_dos":    { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "intrinsic_security_flaws":          { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "verify_mitigations_pragmatically":  { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "refine_code_paths_strictly":        { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "ignore_simd_vector_padding":        { "outcome": "UNKNOWN", "reason": "快照漂移：未重新验证与当前固定的快照" },
  "ensure_source_code_coherence":      { "outcome": "UNKNOWN", "reason": "快照漂移：行/路径不匹配可能是漂移造成的，而不是虚构；未重新验证" },
  "verify_attacker_control_of_source": { "outcome": "UNKNOWN", "reason": "快照漂移：信任边界路径未重新追踪到当前固定的快照" }
}
```

在步骤 0c 中最终确定漂移 `NEEDS_RESEARCH` 的查找已完成 — 不要在步骤 2-5 中再次处理它们。只有匹配的查找 (快照模式开启) 或所有查找 (快照模式关闭) 才会流入步骤 2-5 以下。

1. **加载集群化查找**：读取 `workspace/findings/` 目录中的 JSON 文件。如果目录为空或缺失，通知用户。

2. **源代码检查**：对于每个到达此步骤的查找 (在快照模式下，仅查找在步骤 0c 中匹配的查找；在步骤 0c 中最终确定为漂移 `NEEDS_RESEARCH` 的查找已经完成并跳过)，读取 `CODE_ROOT` 下的文件 (在步骤 0 / 块 A — 解析每个 `code_paths` 路径相对于 `CODE_ROOT`，永远不是活动树) 来检查列在 `code_paths` 中的确切文件和行号，并确认查找在快照状态中扎根。在检查源代码之前，不要假设路径的有效性。

3. **严格验证过滤 (应用 13 条负约束)**：评估每个查找是否符合这些严格标准。如果违反了以下任何规则，则将查找标记为 **`FALSE_POSITIVE`**：

   01. **忽略假设性滥用**：不要标记依赖于调用 API 假设性滥用函数、编写不良回退逻辑或发送无效参数的安全漏洞，如果函数本身行为安全。
   02. **忽略缺失的卫生 / 深度防御**：不要报告缺少 HTTP 安全标头 (例如，`X-Content-Type-Options`)、本地仅测试函数缺少身份验证或硬编码的模拟数据库作为安全漏洞。
   03. **要求严格的可重复性**：仅当在代码逻辑边界内存在直接、明确且可触发的漏洞时，才将查找标记为 `VALID`。如果查找非常脆弱 (例如，依赖于不可自动或暴力破解的不稳定时间，或需要不切实际的环境条件才能触发)，将其标记为 `FALSE_POSITIVE`。*关于竞态条件*：不要因为低成功率 (例如，1 in a million) 而忽略竞态条件或时间错误，只要攻击路径可以自动化并反复尝试以最终触发漏洞。
   04. **避免苛刻的代码检查**：如果代码使用标准安全的库 (例如，`json.loads`、参数化 SQL 查询或安全的标准库哈希)，但缺乏极端的偏执，将其标记为 `FALSE_POSITIVE`。
   05. **在缓解措施上不拉伸安全漏洞**：如果你正在审查一个缓解措施或函数的安全变体，该变体成功阻止了原始安全漏洞类别，不要编造复杂的协议级绕过或相邻的安全漏洞类别 (例如，当审查命令注入修复时 SSRF)。如果主要安全漏洞成功阻止，将其标记为 `FALSE_POSITIVE`。
   06. **评估可疑的文件路径**：不要仅仅因为其路径包含 `/test`、`/experimental` 或 `/mock` 就立即忽略一个查找。这些路径中的代码有时会被编译到生产目标中或通过生产端点访问。不要盲目假设它是安全的；相反，采取合理措施追踪其使用情况，以确认它实际上在生产中暴露。
   07. **忽略资源耗尽 DoS**：不要标记函数因缺少递归限制、输入大小边界或循环约束而缺乏 DoS 攻击防御。
   08. **内在安全漏洞**：如果函数使用一个根本性损坏的算法 (例如 MD5、SHA1)，硬编码静态密钥或在其自身逻辑中包含直接注入路径，将其标记为 `VALID`，即使它当前不在代码库中的任何地方被调用。
   09. **实用地验证缓解措施**：不要在活动的缓解措施中虚构漏洞。如果代码添加了尾随验证斜杠或配置了安全解析标志，接受缓解措施有效。
   10. **严格优化 `code_paths`**：`code_paths` 字段应仅包含有缺陷代码块的精确 `filename:line_number`。删除任何辅助文件、测试框架或正确的调用文件。
   11. **忽略 SIMD/向量填充违规**：如果查找表示在优化向量例程中 (例如 NEON、SSE、AVX、VSX) 内部的越界读取或写入，验证库是否采用全局内存分配合同 (例如，尾随安全填充，如 `row_bytes + 16`)。如果越界访问在所有执行路径上数学上保证完全位于此预分配的填充缓冲区中，将查找标记为 `FALSE_POSITIVE` (按设计)。
   12. **确保源代码一致性 (反虚构)**：验证 `code_paths` 中列出的每个文件路径在仓库中存在，并且函数名、变量名或行号实际上存在于这些位置。如果引用缺失或错误，立即将查找标记为 `FALSE_POSITIVE` 以防止下游代理浪费资源在虚构的漏洞上。
   13. **验证攻击者对源的控制 (信任边界追踪)**：在将数据流查找标记为 `VALID` 之前，识别并引用文件:行，其中未受信任的数据进入分析代码库 (即 "入口点")，从中特定受污染字段的值流到汇点，或该字段由未受信任的写入者填充。
     - 如果你能够访问未受信任侧的代码 (例如，在多组件仓库中的 Guest/Client)，引用写入者。
     - 如果你只能够访问受信任侧的代码，引用数据流路径上的 Host/Server 入口点 (例如，从共享内存、IPC 处理程序、HTTP 请求参数检索)。
     - 如果源数据被证明完全来自受信任侧的来源 (服务器生成的静态配置、主机平面内部状态)，将其标记为 `FALSE_POSITIVE`。
     - 例外：不要将此规则应用于内在安全漏洞 (规则 08)，其中漏洞存在于独立于活动调用者的库代码中。

   - **状态解析**：

     - 如果违反了上述 13 条规则中的任何规则，则标记为 **`FALSE_POSITIVE`**。
     - 如果通过所有规则且具有清晰、可触发的漏洞，则标记为 **`VALID`**。
     - 如果通过规则，但你不确定其可行性而无需动态验证 (例如，需要复杂的堆整理或精确的时间)，则标记为 **`PROVISIONALLY_VALID`**。
     - 如果由于高复杂性、未解决的外部 API 或巨大的调用图，审查无法得出结论 — 或者因为查找在步骤 0c 快照溯源门中 **未匹配** (快照漂移)。漂移查找在步骤 0c 中最终确定，永远不会到达这些 13 条规则；不要重新分类漂移查找为 `FALSE_POSITIVE`。
     - **SCHEMA-CRITICAL**：`FALSE_POSITIVE` 是唯一允许 `triage_checklist` 条目为 `"FAIL"` (或 `"passes": false`) 的状态。对于任何 `VALID`、`PROVISIONALLY_VALID` 或 `NEEDS_RESEARCH` 查找，每个清单条目必须为 `PASS` / `NOT_APPLICABLE` / `UNKNOWN` — 永远不要 `FAIL` — 或 `schema.json` (行 418-470) 将拒绝查找。如果规则看起来失败但你不将状态设置为 `FALSE_POSITIVE` (例如，规则 12/13 的引用看起来不正确，仅仅因为快照漂移)，使用 `UNKNOWN` 和 `reason`，而不是 `FAIL`。

   - **清单构建**：

     - 构建评估所有 13 条负约束的 `triage_checklist` 对象。对于每条规则，将 `outcome` 设置为：
       - `"PASS"`：如果查找满足约束 (不违反规则，意味着漏洞仍然可能是有效的)。
       - `"FAIL"`：如果查找违反了规则。设置任何条目为 `"FAIL"` REQUIRES 查找的 `status` 为 `FALSE_POSITIVE` (`schema.json` 行 418-470 拒绝 `FAIL` 在 `VALID`/`PROVISIONALLY_VALID`/`NEEDS_RESEARCH`)。`FAIL` 条目还 REQUIRES `reason` (`schema.json` 行 788-797)。
       - `"UNKNOWN"`：如果规则的适用性无法解决/需要研究 (REQUIRES a `reason`)。使用此 — 不要使用 `"FAIL"` — 只要查找没有被标记为 `FALSE_POSITIVE`，包括所有漂移 `NEEDS_RESEARCH` 查找的规则 (步骤 0c)。
       - `"NOT_APPLICABLE"`：如果此规则与这类漏洞完全无关 (REQUIRES a `reason`)。
     - 一致性规则：如果 `status` 是 `VALID`，每个条目必须是 `PASS` 或 `NOT_APPLICABLE` (没有 `UNKNOWN`，没有 `FAIL`)，根据 `schema.json` 行 471-507。

4. **构建重放脚本提示**：对于每个标记为 **`VALID`** 或 **`PROVISIONALLY_VALID`** 的查找，提供高信号 `"repro_hints"`，解释如何触发漏洞的复现器代理，需要哪些输入或有效负载参数，以及预期的崩溃条件、sanitizer 追踪 (ASan/UBSan/MSan/TSan) 或功能验证结果 (例如，意外的 HTTP 200 OK) 以确认安全漏洞。

5. **令牌优化文件更新**：为了最小化 LLM 输出令牌，**不要重新发出或手动重写整个 JSON 对象在你的输出中。** 相反，在第一次查找更新期间，编写可重用的辅助脚本 (例如，`workspace/helpers/append_review.py`)。对于所有后续查找，不要重新生成脚本；只需使用新的参数执行现有的辅助脚本以追加所需的字段。

   **辅助版本保护 (机械)**：辅助脚本的第一行必须是注释 `# MANTIS_HELPER_VERSION = 2`。在重用现有的 `workspace/helpers/append_review.py` 之前，检查第一行 (单行 grep)：如果标记缺失或为不同的整数，重新生成辅助脚本 (旧的持久化辅助脚本会静默忽略 `snapshot` 溯源字段并错误处理漂移路径)。重新生成的辅助脚本必须：

   - 接受 `status`、`reasoning`、可选 `repro_hints`、`triage_checklist` (JSON)、`pass_number`、`timestamp` 和 `snapshot` (在键 `"snapshot"` 下写入，永远不要 `"snapshot_id"`);
   - 写入审查器 `history` 条目，包括 `"snapshot"` (当前的 `SNAPSHOT_ID`；在快照模式关闭时，设置 `"snapshot": ""` (或省略字段))。`schema.json` 的 `history_entry` 没有设置 `additionalProperties:false`，所以此额外字段仍然有效。

完成时，通知用户。
