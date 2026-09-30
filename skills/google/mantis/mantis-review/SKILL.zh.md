---
name: mantis-review
description: 独立审查发现，并过滤掉误报。在整合后的发现需要与实际源代码进行验证时使用。不应用于复现崩溃或修补代码。
---

# Reviewer (/mantis-review)

## 系统目标

独立验证器。将整合的发现结果与活动源代码进行比对，以验证其有效性并过滤掉噪音和误报。

## 命令定义

- **命令：** `/mantis-review`
- **描述：** 独立地审查发现结果并过滤掉误报。

## 输入/输出契约

- **读取**：
  - `workspace/findings/` (发现 JSON 文件，包括每个发现的可选 `discovery_commit` 证明戳)。
  - `workspace/.mantis_state.json` (当前的循环 `pass_number`；以及，当存在时，`active_snapshot` = `{root, snapshot_id, snapshot_pinned}` 用于快照证明)。
  - 由协调器传递的调用参数：`--snapshot_root`、`--snapshot_id`、`--state_root` (以及，很少情况下，`--target_root`)。
  - 在 `code_paths` 路径/行号处的目标源代码文件，在解析的 `CODE_ROOT` 下读取 (即固定的快照根 — 见说明步骤 0 / 块 A)，当快照被固定时，永远不会在活树中读取。
- **写入**：
  - 在磁盘上原地更新发现结果 (设置 `"status"`、`"reasoning"`、`"repro_hints"`、`"triage_checklist"` 并追加历史记录)。
  - 写入辅助脚本 `workspace/helpers/append_review.py`。
- **前提条件**：
  - `workspace/findings/` 存在并包含发现文件。
  - 目标源代码文件存在。
- **幂等性保证**：
  - 使用辅助脚本 `append_review.py` 原地修改发现文件，该脚本必须以 `# MANTIS_HELPER_VERSION = 2` 作为其第一行；如果该标记不存在或为不同的整数 (见说明步骤 5)，则重新生成辅助脚本。
  - 幂等性键是 **(pass_number, snapshot)**。在 (重新)写入发现结果之前，扫描其 `history` 数组：
    - **快照模式关闭** (既未传递 `--snapshot_id` 也未可在状态中读取 `active_snapshot`)：如果当前 `pass_number` 已存在 `"stage": "reviewer"` 条目，则跳过审查更新 (与今天的行为字节对字节相同)。
    - **快照模式开启**：如果存在 `"stage": "reviewer"` 条目，其 `pass_number` 等于当前传递，并且其 `snapshot` 等于 `SNAPSHOT_ID`，则跳过审查更新。缺少 `snapshot` (遗留) 或携带不同 `snapshot` 的审查条目计为未知 → 重新审查 (不要跳过)，因此旧技能下审查的发现会重新与当前固定的快照对齐。

## 说明

读取并评估去重后的发现结果与仓库的实际源代码。**默认情况下假设每个发现结果是误报。你的任务是采取对抗性立场来证伪该发现。仅根据代码和原始声明本身进行评估。明确忽略原始查找者的散文式推理和证明，因为它们可能是虚构的。**

按照以下方式执行你的验证：

**步骤 0 — 定位器解析与快照证明门禁 (首先执行，在读取任何发现的代码之前)：**

0a. **解析读取代码的位置。** **块 A — 定位器解析** 在此处：

```
定位器解析 (在读取任何目标代码或工件之前)：
0. 角色：如果此技能永远不会读取目标源 (报告、校准、反映)，则为发现结果仅阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行证明/注释；仅因代码根未设置而永远不会停止。
1. 确定代码根，按以下优先级顺序：
   a. 如果在本调用中传递了 `--target_root`，则代码根 = `--target_root`。它是权威的，并覆盖 `SNAPSHOT_ROOT` 和状态回退 (在调用者将你交给准备好的树时使用，例如修补的影子)。
   b. 否则如果传递了 `--snapshot_root` (或 `SNAPSHOT_ROOT`)，则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json` (如果传递了 `--state_root`，则使用 `--state_root`，否则相对于当前目录的 `./workspace/...`) -> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则 (没有参数且没有可读的 `active_snapshot`)：代码根 = 当前目录，将 `snapshot_pinned` = false (模式关闭)。不要停止。
2. 边界检查 (仅当 `snapshot_pinned` 为 true 且你没有采取路径 1a 时)：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。 (一个 `--target_root` 树 (1a) 是故意被修改的，并且是哨兵豁免的。)
3. 路径字段：
   - 快照相对 (在代码根下读取)：`code_paths` 条目；计划目标文件为文件路径。仅删除尾部的 `:<数字>`。包含 `"://"` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器 (符号/偏移/端点)：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对 (在状态根 `workspace` 下读取/写入，永远不会前缀代码根)：
     `kb_references`、`repro_file_path`、`reattack_file_path`、辅助脚本、报告文件以及所有状态/发现 JSON。
4. 当 `snapshot_pinned` 为 true 时，永不向代码根写入。任何编译、生成或写入工件的命令都必须在代码根的私有影子副本中运行 (从代码根使用 `mktemp -d`)，永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到代码根。
5. VCS-METADATA 切割：历史记录日志提取和在 LIVE 仓库根 (仍然有 `.git/.hg/.repo`) 中运行的任何 VCS diff/blame 命令，而不是代码根 (快照副本会剥离 VCS 元数据)。不要因为代码根缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径并在其调用上设置自己的工作目录。不要假设工作目录在调用之间持久存在。

审查器读取目标源，因此它不是发现结果仅阶段：运行块 A 的所有步骤 1-6。`CODE_ROOT` 是你在步骤 0 / 块 A — 解析的每个 `code_paths` 条目下读取的固定快照根。根据块 A 步骤 3，包含 `"://"` 的 `code_paths` 条目是 URL (仅进行存在检查)，任何不是 `<现有路径>:<整数>` 形式的条目是非源定位器 (检查工件/符号是否存在；跳过所有行存在逻辑)。不要因为代码根缺少 `.git`/`.hg` (块 A 步骤 5) 而停止。

> [!NOTE] **当前传递检查 (防御性；绑定保证基于 `mantis-pipeline-adapter` 场景 2)：** 如果 `active_snapshot` 存在并且 `active_snapshot.pass != state.pass_number`，则将快照视为此传递中的陈旧 — 停止 "陈旧快照：传递不匹配" 或降级为 HALT (`snapshot_pinned` 实际上为 false：没有权威的判断，块 B NOT_MATCHED，重新生成 `not_attempted`)。这捕获了自定义 harness 在 Stage 15 传递增量中保留 `active_snapshot` 而未重新固定的情况。参考元代理每传递重新固定，所以这里永远不会触发此检查。块 B 本身无法检测此情况 (它是 `snapshot_id` 仅，不是 `pass` 感知的)。

0b. **确定快照模式 (一次，在触摸发现结果之前)：** - 快照模式关闭，如果在本调用中未传递 `--snapshot_id` 并且 `workspace/.mantis_state.json` 没有可读的 `active_snapshot`。这是一个遗留/非同步运行：不要运行下面的快照证明门禁；使用步骤 1-5 正确审查每个发现结果。 - 否则快照模式开启。从块 A 你现在持有 `SNAPSHOT_ID` 和 `snapshot_pinned`。应用块 A 中的快照证明门禁 (0c) 到每个发现结果。

0c. **快照证明门禁 (仅快照模式开启)。** 在步骤 1 加载发现结果后，对每个发现 F 应用匹配检查 **块 B — 快照匹配检查**：

```
发现 F 的快照匹配检查 (决定 MATCHED vs NOT_MATCHED)：
1. 如果 `snapshot_pinned` 为 false -> NOT_MATCHED。停止。
2. 读取 `F.discovery_commit`：
   - 缺失 或 空白 或 字面值 "MIXED" -> NOT_MATCHED。
   - 不完全等于 `SNAPSHOT_ID`          -> NOT_MATCHED。
   - 完全等于 `SNAPSHOT_ID`              -> MATCHED。
没有其他路线可以匹配；永远不要模糊比较。全局 "默认字段并继续" 向后兼容规则不适用于 `discovery_commit`：
缺失 = NOT_MATCHED。(没有单独的 "脏" 门禁：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，因此在本传递内发现的匹配，跨传递的裸提交发现不会匹配。)

然后，使用幂等性规则 (输入/输出契约 → 幂等性保证) 避免重复写入：

- **MATCHED** → F 在当前固定的快照中扎根。对 F 执行步骤 2-5 (完整的 13 规则审查)。
- **NOT_MATCHED** (包括：`snapshot_pinned` false / HALT / 活动端点传递；`discovery_commit` 缺失、空白或字面值 `MIXED`；或 `discovery_commit != SNAPSHOT_ID`) → F 是针对不同的 (或缺失/未固定的) 快照发现的；其 `code_paths` 行号可能不再指向相同的代码。**不要对 F 运行 13 规则。不要将其标记为 FALSE_POSITIVE。** 通过辅助脚本完成 F 为漂移 `NEEDS_RESEARCH` (步骤 5)，写入确切内容：
  - `"status": "NEEDS_RESEARCH"`
  - `"reasoning"`:
    `"快照漂移：发现结果针对快照 <F.discovery_commit 或 'unknown'>，该快照与当前固定的快照 <SNAPSHOT_ID> 不匹配。本传递未重新验证；路由到重新研究。"`
  - 忽略 `"repro_hints"` (如果 F 携带来自先前传递的陈旧 `repro_hints`，则保留它们 — 它们在下游被忽略，因为状态不是 VALID/PROVISIONALLY_VALID)。
  - `"triage_checklist"`：所有 13 个约束设置为 `UNKNOWN` (粘贴下面的对象副本)。此对象是必需的：追加 `reviewer` 历史条目使 `triage_checklist` 在非链式发现结果上强制 (参考 `schema.json` 行 365-398)，并且对于 `NEEDS_RESEARCH` 发现，每个条目必须避免 `FAIL`/`passes:false` (`schema.json` 行 418-470)。将 `ensure_source_code_coherence` 和 `verify_attacker_control_of_source` 设置为 `UNKNOWN` (永远不会是 `FAIL`) 的整个要点：由漂移引起的行/路径不匹配不是虚构的证据，因此规则 12/13 必须不在此上触发。
  - 追加 `reviewer` `"history"` 条目 (根据步骤 5 / 以下历史 JSON)。然后停止处理 F — 跳过对它的步骤 2-5。

漂移 `triage_checklist` (粘贴副本；所有 13 个键，所有 `UNKNOWN`)：

```json
{
  "ignore_hypothetical_misuse":        { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "ignore_missing_hygiene":            { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "require_strict_reproducibility":    { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "avoid_pedantic_linting":            { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "no_security_flaw_stretching":       { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "evaluate_questionable_file_paths":  { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "ignore_resource_exhaustion_dos":    { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "intrinsic_security_flaws":          { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "verify_mitigations_pragmatically":  { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "refine_code_paths_strictly":        { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "ignore_simd_vector_padding":        { "outcome": "UNKNOWN", "reason": "快照漂移：未针对当前固定的快照重新验证" },
  "ensure_source_code_coherence":      { "outcome": "UNKNOWN", "reason": "快照漂移：行/路径不匹配可能是漂移引起的，而不是虚构；未重新验证" },
  "verify_attacker_control_of_source": { "outcome": "UNKNOWN", "reason": "快照漂移：信任边界路径未针对当前固定的快照重新追踪" }
}
```

在步骤 0c 中最终化为漂移 `NEEDS_RESEARCH` 的发现结果已完成 — 不要在步骤 2-5 中再次处理它们。只有匹配的发现结果 (快照模式开启) 或所有发现结果 (快照模式关闭) 才会流入步骤 2-5 以下。

1. **加载集群化发现结果：** 读取 `workspace/findings/` 目录中的 JSON 文件。如果目录为空或缺失，通知用户。

2. **源代码检查：** 对于每个达到此步骤的发现结果 (在快照模式开启时，仅那些在步骤 0c 中匹配的发现结果；在步骤 0c 中最终化为漂移 `NEEDS_RESEARCH` 的发现结果已经完成并跳过)，在 `CODE_ROOT` 下读取文件 (在步骤 0 / 块 A — 解析的固定快照根下，解析每个 `code_paths` 路径相对于 `CODE_ROOT`，永远不会是活树) 来检查列在 `code_paths` 中的确切文件和行号，并确认发现结果基于实际快照状态。在检查源代码之前不要假设路径的有效性。

3. **严格验证过滤 (应用 13 个负约束)：** 评估每个发现结果是否符合这些严格标准。如果发现结果违反以下任何规则，则将其标记为 **FALSE_POSITIVE**：

01. **忽略假设性滥用：** 不要标记依赖于调用 API 假设性误用函数、编写不良回退逻辑或发送无效参数的安全漏洞，如果该函数本身表现安全。
   02. **忽略缺失的卫生措施/纵深防御：** 不要报告缺失的 HTTP 安全头（例如 `X-Content-Type-Options`）、本地仅测试函数缺少认证或硬编码的模拟数据库作为安全漏洞。
   03. **要求严格的可复现性：** 只有在代码逻辑边界内存在直接、明确且可触发的漏洞时，才将发现标记为有效。如果发现极其脆弱（例如，依赖于不可自动化的不稳定时间或需要不切实际的运行环境条件才能触发），将其标记为误报。*关于竞态条件：* 不要因为成功概率低（例如，百万分之一）就忽略竞态条件或时间漏洞，只要攻击路径可以被自动化并反复尝试以最终触发利用。
   04. **避免严谨的代码检查：** 如果代码使用标准安全的库（例如 `json.loads`、参数化 SQL 查询或安全的标准库哈希），但缺乏极端的警惕性，将其标记为误报。
   05. **不要在缓解措施上过度扩展安全漏洞：** 如果你正在审查一个缓解措施或函数的安全变体，该变体成功阻止了原始安全漏洞类别，不要编造复杂的协议级绕过或相邻的安全漏洞类别（例如，在审查命令注入修复时报告 SSRF）。如果主要的安全漏洞被成功阻止，将其标记为误报。
   06. **评估可疑的文件路径：** 不要因为路径包含 `/test`、`/experimental` 或 `/mock` 就立即忽略一个发现。这些路径中的代码有时会被编译到生产目标中或可通过生产端点访问。不要盲目假设它是安全的；相反，采取合理措施追踪其使用情况，以确认它是否实际上在生产中暴露。
   07. **忽略资源耗尽型拒绝服务：** 除非模块的主要声明目的是防御拒绝服务攻击，否则不要标记函数缺少递归限制、输入大小边界或循环约束。
   08. **内在安全漏洞：** 如果函数使用根本性损坏的算法（例如 MD5、SHA1）、硬编码静态密钥或在其自身逻辑中包含直接注入路径，即使它当前在代码库中的任何地方都没有被调用，也将其标记为有效。
   09. **实用地验证缓解措施：** 不要在活动的缓解措施中幻觉漏洞。如果代码添加了尾随验证斜杠或配置了安全的解析标志，接受缓解措施有效。
   10. **严格细化 `code_paths`：** `code_paths` 字段应仅包含有缺陷的代码块的精确 `filename:line_number`。从 `code_paths` 中删除任何辅助文件、测试 harness 或正确的调用文件。
   11. **忽略 SIMD/向量填充违规：** 如果一个发现表示在优化的向量例程中（例如 NEON、SSE、AVX、VSX）存在越界读取或写入，验证库是否采用全局内存分配契约（例如尾随安全填充，如 `row_bytes + 16`）。如果越界访问在所有执行路径下都数学上保证完全位于此预分配的填充缓冲区中，将发现标记为误报（按设计）。
   12. **确保源代码一致性（反幻觉）：** 验证 `code_paths` 中列出的每个文件路径都存在于存储库中，并且函数名、变量名或行号确实存在于那些位置。如果引用缺失或不正确，立即将发现标记为误报，以防止下游代理浪费资源在幻觉的漏洞上。
   13. **验证攻击者对源的控制（信任边界追踪）：** 在将数据流发现标记为有效之前，识别并引用未受信任数据进入分析代码库的位置（“入口点”），从该位置到特定受污染字段的值流到汇点，或该字段由未受信任的写入者填充。
      - 如果你能够访问未受信任端的代码（例如多组件存储库中的 Guest/Client），引用写入者。
      - 如果你只能访问受信任端的代码，引用数据流路径上的 Host/Server 入口点（例如，从共享内存、IPC 处理程序、HTTP 请求参数检索）。
      - 如果源数据被证明完全来自受信任端的来源（服务器生成的静态配置、主机平面内部状态），标记为误报。
      - 例外：不要将此规则应用于内在安全漏洞（规则 08），其中漏洞存在于独立于活动调用者的库代码中。

   - **状态解决：**

     - 如果违反了上述 13 条规则中的任何一条，则将其标记为 **误报**。
     - 如果通过所有规则并且具有清晰、可触发的漏洞，则将其标记为 **有效**。
     - 如果通过规则，但你对其可行性不确定，需要动态验证（例如，需要复杂的堆整理或精确的时间），则将其标记为 **暂时有效**。
     - 如果由于复杂性高、未解决的外部 API 或巨大的调用图而导致审查无法得出结论，或者因为发现被步骤 0c 快照溯源门 **未匹配**（快照漂移），则将其标记为 **需要研究**。漂移发现将在步骤 0c 中最终确定，永远不会达到这些 13 条规则；不要将漂移发现重新分类为 `误报`。
     - **SCHEMA-CRITICAL：** `误报` 是唯一一个 `triage_checklist` 条目可能为 `"FAIL"`（或 `"passes": false"）的状态。对于任何 `有效`、`暂时有效` 或 `需要研究` 的发现，每个清单条目必须为 `PASS` / `NOT_APPLICABLE` / `UNKNOWN` — 永不 `FAIL` — 或 `schema.json`（行 418-470）将拒绝该发现。如果一条规则看起来失败了，但你没有将状态设置为 `误报`（例如，规则 12/13 的引用仅因为快照漂移而看起来不正确），请使用 `UNKNOWN` 并附带 `reason`，而不是 `FAIL`。

   - **清单构建：**

     - 构建 `triage_checklist` 对象以评估所有 13 条负面约束。对于每条规则，将 `outcome` 设置为：
       - `"PASS"`：如果发现满足约束（不违反规则，意味着漏洞仍然可能有效）。
       - `"FAIL"`：如果发现违反了规则。设置任何条目为 `"FAIL"` 需要 `finding` 的 `status` 为 `误报`（`schema.json` 行 418-470 拒绝 `FAIL` 在 `有效`/`暂时有效`/`需要研究` 上）。一个 `FAIL` 条目还要求 `reason`（`schema.json` 行 788-797）。
       - `"UNKNOWN"`：如果规则的适用性未解决/需要研究（需要 `reason`）。在发现未被标记为 `误报` 时使用此选项，包括漂移 `需要研究` 发现上的所有规则（步骤 0c）。
       - `"NOT_APPLICABLE"`：如果此规则与这类漏洞完全无关（需要 `reason`）。
     - 一致性规则：如果 `status` 是 `有效`，则每个条目必须为 `PASS` 或 `NOT_APPLICABLE`（没有 `UNKNOWN`，没有 `FAIL`）根据 `schema.json` 行 471-507。

4. **构建复现脚本提示：** 对于每个标记为 **有效** 或 **暂时有效** 的发现，提供高信号 `"repro_hints"`，解释如何触发漏洞，需要哪些输入或有效载荷参数，以及预期的崩溃条件、清理器跟踪（ASan/UBSan/MSan/TSan）或功能验证结果（例如，意外的 HTTP 200 OK）以确认安全漏洞。

5. **令牌优化的文件更新：** 为了最小化 LLM 输出令牌，**不要重新发出或手动重写整个 JSON 对象**。相反，在第一次发现更新时编写一个可重用的辅助脚本（例如 `workspace/helpers/append_review.py`）。对于所有后续发现，不要重新生成脚本；只需使用新参数执行现有的辅助脚本以追加所需字段。

   **辅助版本保护（机械）：** 辅助脚本的第一行必须是注释 `# MANTIS_HELPER_VERSION = 2`。在重用现有的 `workspace/helpers/append_review.py` 之前，检查第一行（单行 grep）：如果标记缺失或为不同的整数，则重新生成辅助脚本（旧的持久化辅助脚本将静默忽略 `snapshot` 溯源字段并错误处理漂移路径）。重新生成的辅助脚本必须：

   - 接受 `status`、`reasoning`、可选的 `repro_hints`、`triage_checklist`（JSON）、`pass_number`、`timestamp` 和 `snapshot`（在键 `"snapshot"` 下写入它，永不 `"snapshot_id"`）的参数；
   - 写入审查者 `history` 条目，包括 `"snapshot"`（当前的 `SNAPSHOT_ID`；仅在关闭 SNAPSHOT 模式时省略或写入 `""`）；
   - 执行（pass_number、snapshot）幂等性检查（幂等性保证）：如果已存在匹配的审查者条目，则不执行任何操作。

   你必须将以下内容追加到现有对象：

   - 一个 `"status"` 字段（`"有效"`、`"误报"`、`"暂时有效"` 或 `"需要研究"` 之一）。

   - 一个 `"reasoning"` 字段。

   - 一个 `"repro_hints"` 字段（对于 `"需要研究"` 或 `"误报"` 可选）。

   - 一个 `"triage_checklist"` 对象，其中包含对 13 条负面约束的所有评估（对象中的每个键映射到上述第 3 节中具有匹配名称的约束）：

     ```json
     {
       "ignore_hypothetical_misuse": { "outcome": "PASS" },
       "ignore_missing_hygiene": { "outcome": "PASS" },
       "require_strict_reproducibility": { "outcome": "FAIL", "reason": "需要不稳定的百万分之一竞态条件且无法自动化。" },
       "avoid_pedantic_linting": { "outcome": "PASS" },
       "no_security_flaw_stretching": { "outcome": "PASS" },
       "evaluate_questionable_file_paths": { "outcome": "PASS" },
       "ignore_resource_exhaustion_dos": { "outcome": "PASS" },
       "intrinsic_security_flaws": { "outcome": "PASS" },
       "verify_mitigations_pragmatically": { "outcome": "PASS" },
       "refine_code_paths_strictly": { "outcome": "PASS" },
       "ignore_simd_vector_padding": { "outcome": "PASS" },
       "ensure_source_code_coherence": { "outcome": "PASS" },
       "verify_attacker_control_of_source": { "outcome": "PASS" }
     }
     ```

     为了向后兼容，模式也允许 `"passes": <bool>` 作为 `"outcome"` 的替代，但 `"outcome"` 更受青睐。如果结果是 `FAIL`、`UNKNOWN` 或 `NOT_APPLICABLE`（或如果 `passes` 是 `false`），必须提供 `reason` 来解释评估；对于 `PASS` / `true` 应省略以节省令牌。

   - 一个到 `"history"` 数组的条目（现在包含审查时针对的快照，用于 `(pass_number, snapshot)` 幂等性）：

   ```json
   {
     "stage": "reviewer",
     "action": "reviewed",
     "details": "确定状态为 [有效/误报/暂时有效/需要研究] 因为 [原因]",
     "pass_number": <当前 pass_number>,
     "snapshot": "<SNAPSHOT_ID>",
     "timestamp": "<当前 iso8601_timestamp>"
   }
   ```

   在关闭 SNAPSHOT 模式（没有快照）时，设置 `"snapshot": ""`（或省略该字段）。`schema.json` 的 `history_entry` 没有 `additionalProperties:false`，因此此额外字段保持有效。

完成时，通知用户。
