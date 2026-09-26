# Risk Calibrator (/mantis-calibrate)

## 系统目标

风险分析专家。根据严格的风险矩阵评估已确认的发现，同时考虑成功复现和生产可行性，以生成最终风险评分（1-10）。

## 命令定义

- **命令：** `/mantis-calibrate`
- **描述：** 根据证据和影响校准发现的风险等级。

## 输入/输出契约

- **读取**：
  - `workspace/findings/*.json`（所有发现文件以加载完整的管道状态）。
  - `workspace/kb/THREAT_MODEL.md`（如果存在，用于检查威胁边界覆盖和资产关键性）。
  - `workspace/.mantis_state.json`（用于跟踪当前循环遍历，并读取 `active_snapshot` — `{snapshot_id, snapshot_pinned, root}` — 用于发现来源和历史戳；不存在 ⇒ 降级/今日行为）。
- **写入**：
  - 原地更新发现文件，添加评分/校准字段
    (`impact_score`, `likelihood_score`, `availability_tier`, `inferred_exposure`, `attacker_position`, `mantis_risk_score`, `priority`, `sanity_triage_applied`（当 STALE-EVIDENCE 防护抑制启发式时可能以 `STALE_EVIDENCE` 开头），`calibration_checklist`（条目可能包含 `STALE_EVIDENCE:` 原因），`outrage_commentary`, `executive_summary`）。追加带有 `snapshot` 来源的 `history` 条目（参见正文中的历史 JSON 模板）。
  - 可重用辅助脚本 `workspace/helpers/append_calibrate.py`。
- **前提条件**：
  - 确认或原始发现必须存在于 `workspace/findings/` 中。
- **幂等性保证**：
  - 通过覆盖现有键来原地更新发现。对相同输入多次运行将产生相同的输出，不会出现重复条目。

## 说明

将原始安全发现及其经验结果（复现/补丁）转换为优先级高的可操作风险报告。

按以下方式执行校准：

**定位解析（仅发现）。** 校准永远不需要读取目标源来计算分数，但某些启发式方法可能会重新检查代码；以与每个阶段相同的方式解析代码根。**区块 A** 已内联如下：

```
LOCATOR RESOLUTION (在读取任何目标代码或工件之前):
0. 角色：如果这个技能永远不读取目标源（报告、校准、反射），你是一个仅发现阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行来源/注释；仅仅因为代码根未设置而停止是不对的。
1. 确定 CODE_ROOT，按以下优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，则 `CODE_ROOT = --target_root`。它是权威的，并且覆盖 `SNAPSHOT_ROOT` 和状态回退（在调用者将准备好的树（例如修补的 shadow）交给你时使用）。
   b. 否则如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用 `--state_root`，否则相对于当前目录的 `./workspace/...`）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 边界检查（仅当 `snapshot_pinned` 为 true 且你没有采取路径 1a 时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "snapshot sentinel mismatch"。（--target_root 树 (1a) 故意被修改，并且豁免 sentinel。）
3. 路径字段：
   - SNAPSHOT-RELATIVE（在 CODE_ROOT 下读取）：`code_paths` 条目；计划目标文件为文件路径。仅删除尾部的 ":<数字>". 包含 "://" 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在状态根/workspace下读取/写入，永远不要以 CODE_ROOT 为前缀）：
     `kb_references`, `repro_file_path`, `reattack_file_path`, 辅助脚本、报告文件，以及所有状态/发现 JSON。
4. 当 `snapshot_pinned` 为 true 时，永远不要在 CODE_ROOT 下写入。任何编译、生成或写入工件的命令都必须在 PRIVATE SHADOW 复制中运行（从 CODE_ROOT 使用 `mktemp -d`），永远不要以 cwd=CODE_ROOT 运行。只读检查可以 cd 到 CODE_ROOT。
5. VCS-METADATA 切割：历史日志提取和在 LIVE 仓库根（仍然有 `.git/.hg/.repo`）运行的任何 VCS diff/blame 命令，而不是 CODE_ROOT（快照副本会删除 VCS 元数据）。仅仅因为 CODE_ROOT 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径，并在调用时设置它自己的工作目录。不要假设工作目录在调用之间持续存在。

```

> [!NOTE] **当前-遍历检查（防御性；绑定保证基于 `mantis-pipeline-adapter` 场景 2）：** 如果 `active_snapshot` 存在且 `active_snapshot.pass != state.pass_number`，则将快照视为此遍历的过时——停止 "stale active_snapshot: pass mismatch" 或降级为 HALT (`snapshot_pinned` 实际上为 false：没有权威的裁决，区块 B 未匹配，复现 `not_attempted`)。这捕获了自定义 harness 在 Stage 15 遍历增量中保留了 `active_snapshot` 而没有重新固定的 `active_snapshot`。参考元代理每遍历都会重新固定，所以这里永远不会触发。区块 B 本身无法检测到这一点（它是 `snapshot_id` 而不是 `pass` 感知的）。

**快照来源和 STALE-EVIDENCE 防护（机械；在校准之前做这个）**：

P0. 从 `state_root/workspace/.mantis_state.json` 读取 `active_snapshot` (`{snapshot_id, snapshot_pinned, root}`)（区块 A 步骤 0/1c）。如果它不存在——即使它不存在——校准是一个仅发现阶段（区块 A 步骤 0）。

P1. 模式（整个运行的单个决定——基于 `active_snapshot` 的存在分支，3 状态模型）：
   - `active_snapshot` 在状态中不存在（没有请求 `--sync` — 模式关闭 = 今日默认）-> 模式 = 模式关闭。按今天的行为**精确**评分：运行所有启发式方法，不要计算 PROVENANCE，不要发出 `STALE_EVIDENCE`，并且不要发出任何 HALT/PINNED 旗帜。
   (向后兼容的默认路径——今天的字节级行为。)
   - `active_snapshot` 存在且 `snapshot_pinned` 不 exactly `true`（HALT 模式 — 树竞争或无法固定）-> 模式 = HALT。`SNAPSHOT_ID` = `active_snapshot.snapshot_id`（一个 `live:` ID）。根据 P2 下方计算 PROVENANCE，并保守地触发 STALE-EVIDENCE 防护（对于防护目的与 PINNED 相同），因为发现的定位可能已过时。此遍历不允许权威裁决（VERIFIED_SECURE, failed_to_reproduce, DUPLICATE, FALSE_POSITIVE, NON_VIABLE）。
   - `snapshot_pinned` == `true` -> 模式 = PINNED。`SNAPSHOT_ID` = `active_snapshot.snapshot_id`。完整的来源 + STALE-EVIDENCE 防护如下。

P2. 在模式 = PINNED 或 HALT 中，使用区块 B 的比较规则根据发现 F 计算来源：
   - `F.discovery_commit` 缺失、为空或字面值 `"MIXED"` -> NOT_MATCHED。
   - `F.discovery_commit` != `SNAPSHOT_ID`（精确字符串比较，不模糊）-> NOT_MATCHED。
   - `F.discovery_commit` == `SNAPSHOT_ID` -> MATCHED。

P3. 当模式为 PINNED 或 HALT 且以下任一条件成立时，每个发现的启发式方法对 F 都是**过时**：
   - PROVENANCE(F) == NOT_MATCHED，或
   - 发现的 `code_paths` 目标文件在 CODE_ROOT 下不存在。

P4. 当启发式方法对 F 过时时，不要应用它；保持**保守**（调整前的）分数；并确保 `sanity_triage_applied` 的第一个标记是字面标记 `STALE_EVIDENCE`。四个受防护的启发式方法及其精确的 STALE 处理是：
   - **Dead-code 0.2 乘数**（第 2 节，“资产关键性和可达性”）：不要应用 0.2 减少值；使用您否则会使用的乘数。
   - `repro_failure`（第 3 节规则）：不要强制强制低；设置 `calibration_checklist.repro_failure.outcome = "UNKNOWN"`, `reason` 以 `"STALE_EVIDENCE: "` 开头。
   - `vague_code_paths`（第 3 节规则）：不要强制强制低；设置 `calibration_checklist.vague_code_paths.outcome = "UNKNOWN"`, `reason` 以 `"STALE_EVIDENCE: "` 开头。
   - `static_confirmation` trace-lift（第 3 节规则，其 "valid external stack trace/sanitizer…" 例外）：不要应用 trace-lift；保持静态高上限（`likelihood_score` <= 3, 0.8 危害乘数，不是 CRITICAL）。设置 `calibration_checklist.static_confirmation.outcome = "APPLIES"`, `reason` 以 `"STALE_EVIDENCE: trace-lift suppressed; trace/crash-log 可能早于活动快照; "` 开头。

P5. 非源发现：如果发现的 `code_paths` 条目是非源定位器（包含 `"://"` 或不是 `<路径>:<整数>` 形式——根据区块 A 步骤 3：符号 / 偏移 / 端点），跳过所有仅源启发式方法——死代码、文件路径/导入/调用者层次结构暴露推断，`vague_code_paths` 和静态跟踪重新检查——并从发现的声明元数据（`attacker_position`, `privileges_required`, `production_viability`, `repro_status`, 威胁模型）。非源跳过不是标记 `STALE_EVIDENCE`（它是正常的，不是漂移）。非源发现的默认 `inferred_exposure` 为 `"INTERNAL"`（0.8），除非发现/威胁模型声明其他内容。

1. **加载完整管道状态**：

   - 从 `workspace/findings/` 目录读取所有 JSON 文件。由于管道在每个阶段都向每个发现文件追加数据，这些文件提供了每个发现完整旅程的完整画面（包括其 `id`、复现状态和生产可行性）。
   - **缺失字段回退**：如果任何发现缺少可行性或复现字段（例如链接发现），在校准之前应用以下回退默认值：
     - 如果 `production_viability` 缺失，将其视为 `"CONDITIONAL_VIABLE"`。
     - 如果 `repro_status` 缺失，将其视为 `"not_attempted"`。
   - **快照来源（仅当模式为 PINNED 或 HALT 时）：** 对于每个发现，根据前导步骤 P2 计算来源（MATCHED / NOT_MATCHED）并记录在临时中。此值控制 Sections 2 和 3 中的 STALE-EVIDENCE 处理（前导步骤 P3–P4）。在模式 == 模式关闭时，跳过此操作——按今天的行为评分。
   - 从知识库读取 `workspace/kb/THREAT_MODEL.md`（如果存在）以评估组件暴露、信任边界、资产关键性和任何自定义**校准覆盖**（例如，特定威胁位置或应针对项目定制的上限）。
   - **批量处理**：如果有多个发现需要校准，将任务拆分为批次（一次几个发现）。如果您有调用子代理的能力，将每个批次委托给子代理以并行处理，然后聚合结果。**每个批次/子代理仅检查固定的快照**：传递 `--snapshot_root=<active_snapshot.root>`, `--snapshot_id=<active_snapshot.snapshot_id>`, 和 `--state_root=<workspace parent>` 以确保每个子代理通过区块 A 以相同的方式解析 CODE_ROOT。任何批次执行（暴露推断、死代码、静态跟踪验证）必须通过该 CODE_ROOT（固定的副本）读取，永远不要通过 cwd=CODE_ROOT 运行。只读检查可以 cd 到 CODE_ROOT。
   - **非默认配置**：
     - 如果 `production_viability` 是 **SAMPLE_OR_TEST**：
       - 将上下文乘数缩放因子应用于上下文乘数（即，将当前上下文乘数乘以 **0.4**），以便样本代码中的严重错误通常落在 MEDIUM 范围而不是 HIGH 或 CRITICAL。此缩放因子必须与其他修饰符一起累积应用。不要直接将上下文乘数覆盖为 `0.4`，因为如果组件的暴露或死代码状态已经计算为低于 `0.4`（例如 `0.2`），则此缩放因子会错误地增加它。
       - 在 `executive_summary` 中明确说明这不是一个生产错误。建议集中在修复示例/测试，以便开发人员不会将不安全模式复制到生产代码中。
     - 如果 `production_viability` 是 **CONDITIONAL_VIABLE**：
       - 将上下文乘数缩放因子应用于上下文乘数（即，将当前上下文乘数乘以 **0.7**），以反映它需要特定的非默认配置、编译标志或断言才能被利用。此缩放因子必须与其他修饰符（例如用户交互）一起累积应用。不要直接将上下文乘数覆盖为 `0.7`，因为如果组件的暴露已经深层/隔离 (`0.5`)，则此缩放因子会错误地增加它。
       - 在 `executive_summary` 中记录所需的具体条件。

   **最终分数（Hazard）= (Impact + Likelihood) * Multiplier**（最高为 10.0）。

   *注意关于 Outrage*：在您的推理中，评论更广泛的方程式 **Risk = Hazard + Outrage**，其中“outrage risk”（例如声誉损害、用户情绪余波）被考虑在内。不要将 outrage 因素包含在最终数字分数中。

2. **关键 Sanity Triage（降级和限制发现）**：在确定最终优先级之前，对发现的品质、上下文和累积证据执行第二级 Sanity Check。

**核心原则 - 边际能力**：发现的最终严重性和优先级严格受攻击者在获得其先决条件位置后获得的*边际能力*的限制。如果利用没有赋予攻击者显著新控制、访问或能力的利用，则必须限制或降级发现。

27 个校准 Sanity 规则的完整详细定义存储在参考目录中 [Calibration Rules](references/calibration_rules.md)。您必须根据那里列出的 27 个规则评估每个发现。

检查 `THREAT_MODEL.md` 是否定义了任何 `Calibration Overrides`（例如，`LIFT_CAP: PHYSICAL_LONG_TERM`）。如果存在针对发现的位置或组件的覆盖，则它将优先级，并提升相应的上限。否则，参考目录中指定的上限和降级（以及边际能力的通用应用）将覆盖 Section 2 中计算的任何升级。您还应该应用通用原则来限制或降级提供低边际能力的其他发现。**重要：上限（HIGH 或 MEDIUM）仅限制允许的最大分数/优先级。它必须**不能升级较低的分数/优先级（例如，分数为 5.0 的发现自然为 MEDIUM，必须保持 MEDIUM，即使它受上限限制为 HIGH）。

**优先级 & UNKNOWN 规则策略**：

- **STALE-EVIDENCE 优先级（前导 P3–P4）：** 当模式为 PINNED 或 HALT 且发现已过时（与活动快照 NOT_MATCHED 或其 `code_paths` 文件在固定的 CODE_ROOT 下不存在）时，以下规则必须**不能**用于从实时重新检查中降低或提高分数：`repro_failure`（不要强制强制低），`vague_code_paths`（不要强制强制低），以及 `static_confirmation` **trace-lift 例外**（不要将过时的跟踪/ sanitizer/ crash-log 视为实时复现 — 保持静态高上限）。也不要应用 Section 2 中的死代码 0.2 乘数（见 Section 2）。保持保守分数，并将字面标记 `STALE_EVIDENCE` 作为 `sanity_triage_applied` 的第一个标记（在 `Incomplete Calibration (UNKNOWN: …)` 警告和已触发规则列表之前），记录受保护的规则（前导 P4 中指定 `repro_failure`/`vague_code_paths` -> `UNKNOWN` 带有 `STALE_EVIDENCE:` 原因；`static_confirmation` -> `APPLIES` 带有 `STALE_EVIDENCE:` 原因，指出 trace-lift 被抑制）。

- 评估所有规则。如果多个上限适用，**最严格的** 赢（Force-LOW > cap-MEDIUM > cap-HIGH）。

- **UNKNOWN 结果策略**：如果规则评估为 `UNKNOWN`，则**不要**应用上限或降级（保持分数保守；将分数/优先级保持在计算值较高处）。但是，通过在 `"sanity_triage_applied"` 字符串前添加警告来标记整体校准为不完整/临时：
  `"Incomplete Calibration (UNKNOWN: <rule_name>)"`（如果有多个 UNKNOWN，则使用分号分隔的警告列表）。这表明需要人工审查来解决规则状态。

- 记录每个成功触发/应用的规则在 `sanity_triage_applied` 中作为分号分隔列表，最严格的第一个（例如，`"Local Attack Vector; Internal/Nested"`），如果存在未知警告，则追加到任何未知警告之后，以便有效上限保持可审计。

3. **确定优先级**：

   - **CRITICAL (8.0 - 10.0)：** 需要立即采取行动。风险非常高（例如，高影响和高可能性）。**必须**不使用，除非它代表了一个非特权攻击者（`privileges_required` 为 **NONE**）的明确 RCE（或等效的完全损失），并且 `user_interaction` 为 **NONE**（零点击）。此规则是绝对的：即使发现（如 CSI 主机逃逸）需要高特权进入，也必须不评为 CRITICAL，并且必须限制为 HIGH (7.9)。
   - **HIGH (6.0 - 7.9)：** 高优先级。重大风险，需要及时解决。
   - **MEDIUM (3.0 - 5.9)：** 标准优先级。中等风险，可以安排。
   - **LOW (0.1 - 2.9)：** 低优先级。最小风险。**任何类型为 "代码脆弱", 纯粹的卫生/纵深防御，或仅影响单个用户自己的数据的发现都必须限制为 LOW 优先级，无论计算分数如何（除非缺乏非否认或更广泛的副作用适用）**。

4. **Token-Optimized 文件更新**：为了最小化 LLM 输出 tokens，**不要**重新发出或手动重写整个 JSON 对象。相反，在第一次发现更新时编写一个可重用辅助脚本（例如，
`workspace/helpers/append_calibrate.py`）。对于所有后续发现，不要重新生成脚本；只需使用新参数执行现有的辅助脚本以将所需字段追加到 `workspace/findings/<id>.json`。

   - **辅助版本标记（强制）。** `append_calibrate.py` 的第一行必须是确切的注释 `# MANTIS_HELPER_VERSION = 2`。在重用现有辅助脚本之前，读取其第一行：如果文件不存在，或第一行不是确切的 `# MANTIS_HELPER_VERSION = 2`（缺少标记或不同的整数），**从头开始重新生成辅助脚本**（旧的辅助脚本默默地丢弃了新的 `snapshot` 历史字段和 `STALE_EVIDENCE` 处理）。重新生成的辅助脚本必须能够将 `snapshot` 键写入追加的 `history` 条目，并将 `STALE_EVIDENCE` 作为 `sanity_triage_applied` 的第一个标记（添加一次，在任何未知警告之前和任何已触发的规则列表之前），以便有效上限保持可审计。

   - 沿着现有的核心发现数据，明确追加以下字段以显示矩阵分解：

   - `"impact_score"` (1-5)

   - `"likelihood_score"` (1-5)

   - `"availability_tier"` (CRITICAL, STANDARD, LOW_CRITICALITY 或 null)

   - `"inferred_exposure"` (EXPOSED, INTERNAL 或 PRIVILEGED)

   - `"attacker_position"` (从输入保留，或如果缺失则从回退推断填充)

   - `"mantis_risk_score"` (最终 Hazard 分数)

   - `"priority"` (CRITICAL, HIGH, MEDIUM, LOW)

   - `"sanity_triage_applied"` (分号分隔列表，或 null)。顺序：
     `STALE_EVIDENCE` 首先如果发现已过时（前导 P4）；然后任何 `Incomplete Calibration (UNKNOWN: <rule>)` 警告；然后 Section 3 规则已触发的任何规则，最严格的第一个。示例：
     `"STALE_EVIDENCE; Incomplete Calibration (UNKNOWN: physical_long_term); Local Attack Vector"`.

   - `"calibration_checklist"` 对象，其中包含对所有 27 个 Sanity caps 的评估。对象中的每个键映射到具有匹配名称的 Sanity cap 规则：

     ```json
     {
       "repro_failure": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "unreachable_inputs": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "third_party_reachability": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "minor_config_hygiene": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "non_security_critical": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "vague_code_paths": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "unreliable_triggers": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "prerequisite_shell": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "physical_long_term": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "trusted_controller_zero_delta": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "standard_host_attacks": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "static_confirmation": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "strict_xss": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "internal_nested": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "probabilistic_llm": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "supply_chain_prerequisites": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "non_default_config": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "confidential_computing_host": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "trusted_controller_critical_bypass": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "local_attack_vector": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "self_contained_blast": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "rarely_exposed": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "equivalent_primitives": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "documented_insecure_config": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "physical_temporary": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "high_privilege_external": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" },
       "trusted_controller_standard_bypass": { "outcome": "APPLIES" | "DOES_NOT_APPLY" | "UNKNOWN", "reason": "<string>" }
     ```

     对于每个规则，`outcome` 必须设置为：

     - `"APPLIES"`：如果 Sanity cap 规则适用于此发现（限制或降级其分数/优先级），则需要详细的 `reason` 字符串。
     - `"DOES_NOT_APPLY"`：如果 Sanity cap 规则不适用。`reason` 字段是**可选**的，可以省略以优化 tokens。
     - `"UNKNOWN"`：如果它尚未解决。需要详细的 `reason` 字符串。

     为了向后兼容，模式也允许 `"fires": <bool>`（如果 `fires` 为 `true`，则 `reason` 仅在 `true` 时需要），但新的 `"outcome"` 格式是首选。

   - `"outrage_commentary"`（您对 outrage 因素的推理）

   - `"executive_summary"`

   - `"history"` 数组中的一个条目：

     ```json
     {
       "stage": "calibrate",
       "action": "calibrated",
       "details": "Calculated risk score as [score] and priority as [priority].[ STALE_EVIDENCE: scored without trusting live-code re-inspection.]",
       "pass_number": <current_pass_number>,
       "snapshot": "<active_snapshot.snapshot_id, or omit in MODE-OFF>",
       "timestamp": "<current_iso8601_timestamp>"
     ```

保存您的更新到单个发现文件中。完成时，通知用户。
