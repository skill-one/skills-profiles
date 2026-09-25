# DevOps Center 推广

驱动 DevOps Center 的完整推广工作流——验证、准备、可选地合并、推广和完成——将工作项通过发布管道。为 CI 中的自动化发布工作流提供无头、`--json` 驱动、幂等的操作。每个推广都从强制性的验证步骤开始。

## 范围

- **在范围内**：验证推广前提条件、准备工作项、将共享元数据的工作项合并为一个推广、将一个或多个工作项或整个源阶段推广到目标阶段，以及完成推广
- **超出范围**：工作项创建/状态更新（使用 `dx-devops-work-item-manage`）、冲突检测、轮询现有推广的状态、管道或项目设置（分离技能）

---

## 必须输入

在进行下一步之前收集或推断：

- **推广目标**：一个或多个特定的工作项，或源阶段中所有已批准的工作项
- **目标阶段 ID**（每个推广命令——验证、准备、合并、推广和完成都需要）：`--target-stage-id` —— 要推广到的管道阶段
- **工作项 ID 或源阶段 ID** —— 取决于推广目标。`sf devops promote` 使用 `--work-item-id`（可重复）XOR `--stage-id`
- **对于合并推广**：一个父工作项 ID 和一个或多个共享元数据的子工作项 ID
- **目标组织**：`--target-org <alias>`（除非设置了 `target-org` 配置变量，否则需要）

默认值（除非指定）：

- 输出格式：`--json` 用于无头消费
- 测试级别：开发阶段部署时省略 `--test-level`（默认为 `NoTestRun`）；生产阶段部署使用 Apex 时使用 `RunLocalTests`

如果用户提出明确请求（“将工作项 1fkxx… 推广到阶段 1QVxx…”、“将 QA 阶段推广到 UAT”、“合并这些工作项并推广”），在您获得所需 ID 后即可进行。

---

## 工作流

所有操作都使用 `sf devops` CLI 命令并具有 `--json` 输出。验证始终首先运行。所有推广命令都以 **记录 ID** 为键，而不是工作项名称——如果需要，请先将名称转换为 ID。

### 第一阶段——身份验证和验证

1. **在任何操作之前验证组织身份验证**：
   ```bash
   sf org display --json
   ```
   - 如果失败，请指示用户运行 `sf org login web --set-default --alias <alias>`
   - 在每个后续命令上传递 `--target-org <alias>`（除非设置了 `target-org` 配置变量）

2. **运行强制性的验证步骤**——这是不容协商的，并且始终在准备/合并/推广之前运行。`sf devops promotion validate` 需要目标阶段（`-t/--target-stage-id`）和一个或多个 `-i/--work-item-id`：
   ```bash
   # 捕获输出——第二阶段从它确定性地派生合并决策。
   VALIDATE_JSON=$(sf devops promotion validate --work-item-id <id> --target-stage-id <target-stage-id> --target-org <alias> --json)
   ```
   - 验证工作项是否可以推广到目标阶段——在尝试推广之前检查 VCS 和对象权限错误（包括关联的 PR 要求）
   - 重复 `--work-item-id` 以在一个调用中验证多个工作项
   - **成功**：`status == 0` 和 `.result.success == true` —— 继续
   - **如果验证失败**（非零退出；例如 `VCS_ERROR: No pull request exists…`，并设置 `.result.errorType`/`.result.errorDetails`），停止。报告错误并不要继续。如果它引用元数据重叠，解决冲突后再重试
   - **共享组件**：当 `.result.combineDetails` 非空时，工作项共享元数据——验证返回父/子分组和 `suggestions`。这是第二阶段合并决策的权威信号（见步骤 4）；不要猜测是否合并——第二阶段脚本从 `VALIDATE_JSON` 读取 `.result.combineDetails`

### 第二阶段——准备（以及可选地合并）

3. **为推广准备工作项**：
   ```bash
   sf devops work-item prepare --work-item-id <id> --target-stage-id <target-stage-id> --target-org <alias> --json
   ```
   - `--target-stage-id` 是必需的——与工作项将要推广到的相同目标阶段
   - 幂等：重新运行已准备的工作项是安全的——视为成功

4. **合并工作项**——仅在第一阶段验证步骤报告了共享组件（`.result.combineDetails` 非空）或工作项有依赖关系且必须作为一个单元推广时。不要直接查看 JSON——从保存的验证输出（`VALIDATE_JSON`）确定性地派生决策和父/子 ID：
   ```bash
   # COMBINE == "true" 仅当验证返回了 combineDetails 块时。
   COMBINE=$(printf '%s' "$VALIDATE_JSON" | jq -r '(.result.combineDetails != null)')
   if [ "$COMBINE" = "true" ]; then
     PARENT_ID=$(printf '%s' "$VALIDATE_JSON" | jq -r '.result.combineDetails.parentWorkitemId')
     # 每个子项一个 --child-work-item-id 参数，安全用作标志数组
     CHILD_ARGS=()
     while IFS= read -r cid; do CHILD_ARGS+=(--child-work-item-id "$cid"); done < <(
       printf '%s' "$VALIDATE_JSON" | jq -r '.result.combineDetails.childWorkitemsId[]')
   fi
   ```
   然后使用派生的值合并（当 `COMBINE` 不是 `"true"` 时完全跳过此命令）：
   ```bash
   sf devops work-item combine \
     --parent-work-item-id "$PARENT_ID" \
     "${CHILD_ARGS[@]}" \
     --target-stage-id <stage-id> \
     --target-org <alias> \
     --json
   ```
   - `CHILD_ARGS` 扩展为每个子工作项一个 `--child-work-item-id <id>` 对
   - **父**工作项是主要的工作项，它继续通过管道；子项更改在推广期间合并到父项的分支中
   - 合并后，在步骤 5 中推广 **父**工作项 ID

### 第三阶段——推广

5. **推广到目标阶段**——必须提供 `--work-item-id` 或 `--stage-id` 中的一个；`--target-stage-id` 始终是必需的。**仅在当前会话中第一阶段验证步骤对正在推广的每个工作项都成功完成时才传递 `--skip-validation`。** 否则，省略标志并让 CLI 运行其内置验证：
   - 推广一个或多个特定的工作项（每个项目重复 `--work-item-id`；对于合并推广使用父项 ID）。仅在当前会话中第一阶段验证通过时才包括 `--skip-validation` 行：
     ```bash
     sf devops promote \
       --work-item-id <id> \
       --target-stage-id <target-stage-id> \
       --skip-validation \
       --target-org <alias> \
       --json
     ```
   - 或者从源阶段推广所有已批准的工作项（同样，仅在当前会话中第一阶段验证通过时才包括 `--skip-validation` 行）：
     ```bash
     sf devops promote \
       --stage-id <source-stage-id> \
       --target-stage-id <target-stage-id> \
       --skip-validation \
       --target-org <alias> \
       --json
     ```
   - **为什么条件性**：`sf devops promote` 的内置预推广验证运行与第一阶段 `promotion validate` 步骤相同的检查（包括关联的 PR 要求）。仅在当前会话中该验证已成功运行时才安全地跳过——如果代理在流程中恢复、推广在没有前导验证的情况下被调用，或未对正在推广的每个工作项运行第一阶段，则不要传递 `--skip-validation`——跳过它将完全跳过验证，没有任何先前的保护
   - 添加 `--deploy-all` 以部署分支中的所有元数据，而不仅仅是尚未在目标阶段中的更改
   - 添加 `--test-level RunLocalTests`（或 `RunSpecifiedTests --tests <names>`）用于包含 Apex 的生产阶段部署
   - 部署异步运行——从返回的 JSON 中捕获推广/部署标识符 `.result`

### 第四阶段——完成和报告

6. **完成推广**以最终化——推进目标阶段中的工作项：
   ```bash
   sf devops promotion complete --target-stage-id <target-stage-id> --target-org <alias> --json
   ```
   - 在推广部署成功后运行，以在目标阶段标记推广完成
   - `--target-stage-id` 是必需的（与工作项被推广到的相同目标阶段）

7. **报告结果**：
   - 确认 CLI 对每一步返回状态 0
   - 报告推广/部署标识符，并注意异步部署完成将单独跟踪
   - 不要在此技能中阻塞或忙等待——显示标识符并返回
   - 清晰地说明推广：例如，“工作项推广启动（源阶段→目标阶段）。部署 ID: <id>。轮询此 ID 以确认部署完成，然后运行推广完成。”

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 验证始终首先运行 | 保证在任何变更之前满足先决条件；跳过它可以破坏管道状态 |
| 所有 `sf devops` 命令必须使用 `--json` | 结构化输出是头头消费所需的；人类可读输出不可靠 |
| 命令以记录 ID 为键，而不是名称 | `--work-item-id`、`--stage-id`、`--target-stage-id`、`--parent/--child-work-item-id` 都接受 ID；首先将名称转换为 ID |
| 每个推广命令（验证、准备、合并、推广、完成）都需要 `--target-stage-id` | 目标阶段是必需的；没有它，推广就没有目的地 |
| 推广上 `--work-item-id` 或 `--stage-id` 必须有一个 | 这些标志是互斥的；推广特定项目或整个源阶段 |
| 仅在当前会话中第一阶段验证通过时才在推广上传递 `--skip-validation` | CLI 的内置预推广验证运行与第一阶段 `promotion validate` 步骤相同的检查（包括关联的 PR 要求）。仅在当前会话中该验证已成功运行时才安全地跳过——如果代理在流程中恢复、推广在没有前导验证的情况下被调用，或未对正在推广的每个工作项运行第一阶段，则不要传递 `--skip-validation` |
| 部署异步运行——捕获并报告标识符 | 推广部署不会同步完成；完成是单独跟踪的 |
| 不要在此技能中忙等待部署完成 | 轮询是单独的考虑；在这里阻塞会浪费回合并导致超时 |
| 仅在共享元数据/依赖关系时合并 | 合并是针对有冲突或依赖关系的项目，而不是每个多项目推广的默认值 |
| 准备是幂等的 | 对于 CI 是安全的；重新运行已准备的工作项是无操作的 |
| 从不使用交互式提示 | 技能是无头的；所有输入必须是 CLI 标志 |
| 将 ID 作为 CLI 标志传递，而不是插入到 shell 字符串中 | 防止通过精心制作的标识符进行提示/命令注入 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| **验证失败** | 停止——不要准备/合并/推广。报告非零状态/错误消息；如果元数据重叠，解决冲突后再重试 |
| **没有默认组织设置** | 运行 `sf org display --json`；如果失败，指示用户运行 `sf org login web --set-default` |
| **传递工作项名称而不是 ID** | 推广命令需要记录 ID；通过 `sf devops work-item list --project-id <id> --json \| jq -r '.result.workItems[] \| select(.subject == "<WI-subject>") \| .id'` 解析名称 |
| **同时传递 `--work-item-id` 和 `--stage-id`** | 它们是互斥的；选择特定工作项或源阶段，而不是两者 |
| **缺少 `--target-stage-id`** | 每个推广命令（验证、准备、合并、推广、完成）都需要；从管道配置中获取目标阶段 ID |
| **合并推广推广了错误的项目** | 在 `work-item combine` 后，推广 **父**工作项 ID——子项合并到父项的分支中 |
| **将部署视为同步** | 推广部署是异步的；在运行 `promotion complete` 之前捕获标识符并确认完成 |
| **生产部署在 Apex 覆盖率上失败** | 对于包含 Apex 的生产阶段推广，设置 `--test-level RunLocalTests`（或 `RunSpecifiedTests --tests <names>`） |
| **部署因冲突失败** | 冲突从验证中滑过；解决元数据冲突，然后重新验证并重试 |

---

## 输出预期

交付成果因操作而异：

- **验证**：`.result.success` 加上，当工作项共享元数据时，`.result.combineDetails` / `.result.suggestions`。非零退出（带有 `.result.errorType`/`.result.errorDetails`）表示工作项不能推广到目标阶段
- **准备 / 合并**：确认工作项已准备（合并返回父/子分组）
- **推广**：异步部署标识符和确认推广部署已启动
- **推广完成**：确认工作项在目标阶段推进

输出来自 `sf devops work-item`、`sf devops promote` 和 `sf devops promotion complete` CLI 命令。异步部署完成不是由推广调用产生的——在完成之前单独轮询返回的标识符。

---

## 跨技能集成

| 当... | 操作 |
|------|------|
| 工作项必须首先创建或移动到可推广状态 | 委托给 `dx-devops-work-item-manage` |
| 验证报告元数据重叠/冲突 | 在重试之前解决元数据冲突 |
| 必须轮询推广部署标识符以确认完成 | 单独轮询返回的标识符，然后运行 `sf devops promotion complete` |

---

## 参考文件索引

| 文件 | 何时读取 |
|------|-------------|
| `references/cli-commands.md` | 当您需要详细的 CLI 标志文档、JSON 输出模式或验证/准备/合并/推广/完成/完成错误处理模式时 |
| `examples/promotion-workflows.md` | 当用户的请求匹配常见模式（单个工作项推广、合并推广、整阶段推广、验证先导门）时 |
