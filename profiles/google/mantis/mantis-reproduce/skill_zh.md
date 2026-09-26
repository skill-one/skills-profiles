# Reproducer (/mantis-reproduce)

## 系统目标

集成测试工程师。设计崩溃复现器或输入，并在隔离的沙箱环境中执行它们，以经验性地验证错误。

## 命令定义

- **命令:**
  `/mantis-reproduce [--reattack] [--finding_id=<uuid>] [--force] [--target_root=<path>] [--state_root=<path>] [--snapshot_root=<path>] [--snapshot_id=<SNAPSHOT_ID>] [--snapshot_pinned=<true|false>]`
- **描述:** 生成并运行崩溃复现器以验证安全漏洞。
- **参数:**
  - `--reattack`: 当作为补丁验证的一部分执行时，用于隔离重新攻击结果。
  - `--finding_id`: 要复现的特定发现 UUID。**必须**提供，并且在指定 `--reattack` 时是必需的。
  - `--force`: 覆盖/绕过目标正常运行的资格检查。
  - `--target_root`: 测试下目标代码库根路径（默认为 `.`）。当提供时具有权威性——覆盖 `--snapshot_root`（Block A 步骤 1a）；对此树进行哨兵检查被跳过（例如，在重新攻击验证期间修补的影子）。
  - `--state_root`: 包含 `workspace/` 的 Mantis 状态目录根路径（默认为 `.`）。
  - `--snapshot_root`: 此通过中固定的不可变代码快照的根。
    当 `--target_root` 未提供时，由 Block A（步骤 0）消耗。
  - `--snapshot_id`: 固定快照的 SNAPSHOT_ID 字符串，在步骤 0 中由 Block A（哨兵）和 Block B（快照匹配检查）消耗。
  - `--snapshot_pinned`: 当 `false`（由 `mantis-patch` 在对修补影子进行重新攻击时设置），重新攻击子代理**必须**跳过此调用的快照哨兵/匹配检查——`--target_root` 树是权威的，并且不受哨兵保护（Block A 步骤 1a）。

## 输入/输出契约

- **读取**:
  - `state_root/workspace/findings/`（可行的/有条件的发现）。
  - `target_root/`（要分析的触发路径的存储库源文件）。
  - `state_root/workspace/archive/.repro_attempts.json`。
  - `state_root/workspace/.mantis_state.json`（用于跟踪当前循环通过）。
- **写入**:
  - 证明复制文件（例如，`poc_[uuid].py` 或 `crash_[uuid].payload` 在 `state_root/workspace/reproducers/` 内）。
  - 如果正常运行：就地更新 `state_root/workspace/findings/` 中的发现（设置 `"repro_status"`, `"repro_file_path"`, `"run_command"`, `"repro_output"` 并追加历史记录）。如果临时有效，则更新状态为 `"VALID"`。
  - 如果使用 `--reattack` 运行：就地更新 `state_root/workspace/findings/` 中的发现（设置 `"reattack_status"`, `"reattack_file_path"`, `"reattack_run_command"`, `"reattack_output"`, `"reattack_variants"` 并追加历史记录，使用阶段 `"reattack"`）。不会修改 `"repro_*"` 字段或 `"status"`。**例外情况**：根据 INV-1 在步骤 6 中可能原子性地降级 `patch_status`（永远不会持久化 `VERIFIED_SECURE` 与非 `failed_to_bypass` 的 `reattack_status` 一起）。
  - 原子地更新 `state_root/workspace/archive/.repro_attempts.json`。
  - 在更新的发现上戳 `"repro_snapshot_id"` / `"reattack_snapshot_id"`，并将 `.repro_attempts.json` 值存储为 `{count,last_snapshot}` 对象（原始整数仍然可以正确读取）。
- **前提条件**:
  - 发现必须在 `state_root/workspace/findings/` 中存在。
  - 沙箱/容器运行时环境必须可用。
- **幂等性保证**:
  - 就地更新发现。使用 `state_root/workspace/archive/.repro_attempts.lock` 文件锁定和原子临时文件交换 (`os.replace` on `state_root/workspace/archive/.repro_attempts.json.tmp`) 来保证并发安全性和重试稳定性。
  - 快照感知：当发现的快照不再匹配时，重新生成 PoC；在没有达到汇点证据的情况下拒绝发出负面判断。重新攻击的判断在快照不匹配时受 C5 未修补基线重新运行（步骤 6）管理，它覆盖了传统的全面拒绝——只有在 C5 确认未修补基线仍然在当前快照上触发时，才会写入 `failed_to_reproduce` 判决。

## 说明

### 步骤 0：定位解析 + 快照匹配（首先运行）

```
定位解析（在读取任何目标代码或工件之前）:
0. 角色：如果此技能永远不会读取目标源代码（报告、校准、反映），则您处于仅发现阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行来源/注释；仅因为代码根未设置而永远不会停止。
1. 确定代码根，按此优先级顺序:
   a. 如果在此调用中传递 `--target_root`，则 `CODE_ROOT = --target_root`。它是权威的，覆盖 `SNAPSHOT_ROOT` 和状态回退（在调用者将准备好的树（例如，修补的影子）交给你时使用）。
   b. 否则如果传递 `--snapshot_root`（或 `SNAPSHOT_ROOT`），则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递 `--state_root`，则使用 `--state_root`，否则相对于当前目录的 `./workspace/...`）
      -> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 哨兵检查（仅当 `snapshot_pinned` 为 true 且您没有采取路径 1a 时）:
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（--target_root 树 (1a) 是故意修改的，并且不受哨兵保护。）
3. 路径字段:
   - 快照相对（在 `CODE_ROOT` 下读取）：`code_paths` 条目；规划目标文件，它们是文件路径。仅删除尾部的 `:<digits>`。包含 `://` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会前缀 `CODE_ROOT`）：
     `kb_references`, `repro_file_path`, `reattack_file_path`, 帮助脚本，报告文件，以及所有状态/发现的 JSON。
4. 当 `snapshot_pinned` 为 true 时，不要在 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在 `CODE_ROOT` 的私有影子副本（`mktemp -d` 从 `CODE_ROOT`）中运行，绝不能使用 `cwd=CODE_ROOT`。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切片：历史记录提取和任何 VCS diff/blame 命令在 LIVE 仓库根目录（仍然有 `.git/.hg/.repo`）中运行，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。不要因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径，并在调用时设置其自己的工作目录。不要假设工作目录在调用之间持久存在。

> [!NOTE] **当前通过检查（防御性；绑定保证在 `mantis-pipeline-adapter` 每个场景 2 上）:** 如果 `active_snapshot` 存在且 `active_snapshot.pass != state.pass_number`，则将快照视为此通过中的陈旧——停止 "陈旧的活动快照：通过不匹配" 或降级为 HALT (`snapshot_pinned` 实际上为 false：没有权威判决，Block B NOT_MATCHED，重新生成 `not_attempted`)。这捕获了自定义 harness 在 Stage 15 通过增量中保留了 `active_snapshot` 而没有重新固定的情况。参考元代理每通过都重新固定，所以这里永远不会触发。Block B 本身无法检测到这一点（它是 `snapshot_id`-only，不是 `pass`-aware）。

```
发现 F 的快照匹配检查（决定 MATCHED vs NOT_MATCHED）:
1. 如果 `snapshot_pinned` 为 false -> NOT_MATCHED。停止。
2. 读取 F.discovery_commit:
   - 缺失或为空或字面值 "MIXED" -> NOT_MATCHED。
   - 不完全等于 `SNAPSHOT_ID`          -> NOT_MATCHED。
   - 完全等于 `SNAPSHOT_ID`              -> MATCHED。
没有其他路线可以匹配；永远不会模糊比较。全局 "默认该字段并继续" 的向后兼容规则不适用于 `discovery_commit`：缺失 = NOT_MATCHED。没有单独的 "脏" 门：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，因此在此通过中发现的匹配和跨通过的基本提交发现不会匹配。
