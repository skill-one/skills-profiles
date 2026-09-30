---
name: dx-devops-pipeline-manage
description: 使用此技能来管理 DevOps Center 管道的完整生命周期——列出所有管道、获取单个管道的详细信息、创建一个与 Git 仓库关联的新管道、添加或删除阶段、重命名阶段、在阶段上添加或删除 Salesforce 环境、附加或分离项目，以及激活或停用管道。当用户想要设置发布管道、在集成、UAT、测试和生产组织中连接发布阶段、将环境连接到阶段、附加项目或激活持续交付管道时调用。使用 sf devops pipeline 和 sf devops stage 命令，并使用 --json 输出。不用于工作项生命周期、发布或部署执行、冲突检测或独立项目创建（使用其他技能）。
---

# DevOps Center 流水线管理

管理 DevOps Center 中的完整流水线生命周期——从基于存储库创建开始，经过阶段和环境配置以及项目关联，到激活准备就绪的发布流水线。提供无头 CLI 驱动的操作，用于自主发布工作流。

## 范围

- **在范围内**：列出流水线、获取流水线详细信息、创建流水线（链接到现有或新的 Git 仓库）、添加/删除/重命名阶段、在阶段上添加/删除 Salesforce 环境、关联/分离项目、以及激活/停用/重命名流水线
- **超出范围**：工作项生命周期、发布/部署执行、冲突检测、独立项目创建（单独的技能）

---

## 必须的输入

在进行下一步之前收集或推断：

- **操作类型**：list、get、create、add-stage、delete-stage、rename-stage、add-environment、delete-environment、attach-project、detach-project、activate 或 deactivate
- **对于 get / 任何阶段或环境操作**：流水线 ID（必需）——通过 `sf devops pipeline list --json` 获取
- **对于 create**：流水线名称（必需）和一个 Git 仓库（`--repo`，必需）。仓库标志因场景而异：
  - **现有仓库（GitHub 或 Bitbucket）**：仅 `--repo <url>` —— 不要传递 `--repo-type`/`--create-repo`
  - **新的 GitHub 仓库**：`--repo <name> --create-repo --repo-type github --repo-owner <组织或用户>`
  - **新的 Bitbucket 仓库**：`--repo <name> --create-repo --repo-type bitbucket --bitbucket-workspace <工作区>` (`--bitbucket-project-key <key>` 可选)
  - 在所有情况下，描述（`--description`）都是可选的
- **对于 add-stage**：流水线 ID、新阶段名称和 `--next-stage-id`（新阶段之前的前一个阶段）——通过 `sf devops pipeline get` 获取阶段 ID
- **对于 add-environment**：流水线 ID、阶段 ID、环境名称和 `--org-type`（生产或沙盒）
- **对于 attach/detach-project**：流水线 ID 和项目 ID
- **对于 activate/deactivate/rename**：流水线 ID

默认值（除非指定）：
- 输出格式：`--json` 用于无头消费
- 目标组织：如果不依赖默认组织，请使用 `--target-org <别名>`

如果用户给出明确的请求（"在仓库 myorg/myrepo 上创建流水线"、"在生产之前添加 UAT 阶段"、"激活流水线 0XB..."），请立即进行操作，不要进行不必要的询问。

---

## 工作流

所有操作都使用 `sf devops pipeline` 和 `sf devops stage` CLI 命令，并使用 `--json` 输出进行结构化消费。流水线 ID 和阶段 ID 是主要标识符——在修改之前通过 `list` 和 `get` 解决它们。

### 第一阶段——识别操作

1. **根据用户意图确定操作类型**：
   - "list"、"显示所有流水线" → list；"流水线详细信息"、"显示阶段" → get
   - "create"、"设置"、"新流水线" → create
   - "add stage"、"插入阶段" → add-stage；"rename stage" → rename-stage；"remove/delete stage" → delete-stage
   - "连接环境"、"将组织添加到阶段" → add-environment；"删除环境" → delete-environment
   - "attach project"、"连接项目" → attach-project；"detach project" → detach-project
   - "activate"、"开启"；"deactivate"、"关闭"；"rename pipeline" → 生命周期更新

### 第二阶段——执行操作

2. **在任何操作之前验证组织认证**：
   ```bash
   sf org display --json
   ```
   - 如果没有设置默认组织或认证已过期，请指示用户运行 `sf org login web --set-default --alias <别名>`
   - 通过运行 `sf devops pipeline list --json` 确认组织已启用 DevOps Center
   - 当针对特定组织时，在每条命令中添加 `--target-org <别名>`

3. **检查流水线**：
   ```bash
   sf devops pipeline list --json                              # 组织中的所有流水线
   sf devops pipeline get --pipeline-id <pipeline-id> --json   # 一个流水线，包括阶段/仓库/项目
   ```
   - `list` 返回以 `.result.pipelines[]` 为下标的 SObject 记录，字段为大写（`.Id`、`.Name`、`.IsActive`）——它**不**包含阶段或连接的项目
   - `get` 返回以 `.result` 为下标的单个流水线，字段为驼峰式（`.id`、`.name`、`.stages[]`、`.connectedProjects[]`）；每个阶段都有 `.id`、`.name`、`.nextStageId`、`.branchName` 和 `.environment.{id,name}`。**阶段是一个链表**——顺序由 `nextStageId` 定义，终端阶段的 `nextStageId` 为 null。使用 `get` 发现**阶段 ID**，然后再进行任何阶段或环境操作

4. **创建流水线**——流水线必须链接到 Git 仓库。`--name` 和 `--repo` 始终是必需的；其余标志取决于仓库场景：
   ```bash
   # 现有仓库（GitHub 或 Bitbucket）——传递完整的仓库 URL，其他什么都不要
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-url> --json

   # 新的 GitHub 仓库——需要 `--repo-owner`
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-name> \
     --create-repo --repo-type github --repo-owner <组织或用户> --json

   # 新的 Bitbucket 仓库——需要 `--bitbucket-workspace`（`--bitbucket-project-key` 可选）
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-name> \
     --create-repo --repo-type bitbucket --bitbucket-workspace <工作区> \
     --bitbucket-project-key <key> --json

   # 自定义阶段链（任何场景）——按推广顺序重复 `--stage`
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-url> \
     --stage Dev --stage QA --stage Prod --json
   ```
   - 提供者特定的必需标志：**GitHub 新仓库** → `--repo-owner`；**Bitbucket 新仓库** → `--bitbucket-workspace`。省略提供者的必需标志会导致创建失败
   - 对于现有仓库，**不要**传递 `--repo-type`/`--create-repo`——通过 `--repo` 仅传递仓库 URL
   - **创建时自定义阶段**：新流水线会生成默认阶段链 **集成 → UAT → 预发布 → 生产**。要生成不同的阶段，按推广顺序重复 `-s/--stage` 一次每个阶段——例如 `--stage Dev --stage QA --stage Prod`。这避免了之后添加/重命名阶段
   - 在任何场景中可选地添加 `--description "<text>"`
   - 捕获返回的流水线 ID，用于后续的阶段/环境/项目/激活步骤
   - **幂等性**：CLI 不会去重。在创建之前，运行 `sf devops pipeline list --json` 并检查是否有相同名称/仓库的现有流水线；如果找到，则返回现有流水线。有关检查前创建的代码片段，请参阅 `references/parsing-patterns.md`

5. **配置阶段**——阶段相对于现有阶段添加，然后绑定到环境。**在多阶段工作之前阅读 `references/cli-commands.md`** 以获取完整标志详细信息：
   ```bash
   # 在现有阶段之前插入一个空阶段（从 `pipeline get` 获取 `next-stage-id`）
   sf devops pipeline stage add --pipeline-id <id> --name "<stage-name>" --next-stage-id <stage-id> --json
   # 重命名阶段
   sf devops pipeline stage update --pipeline-id <id> --stage-id <stage-id> --name "<new-name>" --json
   # 删除阶段（前驱自动重新链接到后继）
   sf devops pipeline stage delete --pipeline-id <id> --stage-id <stage-id> --json
   ```
   - `stage add` 在 `--next-stage-id` 之前插入一个**空**阶段（没有分支/环境）；单独配置其环境
   - 通过插入每个新阶段在应跟随它的阶段之前来构建推广链

6. **将环境绑定到阶段**——将 Salesforce 组织附加到阶段：
   ```bash
   # 在调用 CLI 之前验证 `org-type` 对固定枚举
   bash scripts/validate-org-type.sh "<Production|Sandbox>"   # 如果值无效，则退出非零
   sf devops stage environment add --pipeline-id <id> --stage-id <stage-id> \
     --environment-name "<env-name>" --org-type <Production|Sandbox> --json
   # 删除环境（流水线必须处于非活动状态）
   sf devops stage environment delete --pipeline-id <id> --environment-id <env-id> --json
   ```
   - `--org-type` 必须是 `Production` 或 `Sandbox`——首先运行 `scripts/validate-org-type.sh <value>`，只有在退出码为 0 时才继续
   - **无头注意事项**：`stage environment add` 触发 OAuth 浏览器流程。在无头/CI 运行中传递 `--no-browser`——CLI 打印一个重定向 URL 以进行手动认证

7. **附加/分离项目**——项目只能附加到一个流水线：
   ```bash
   sf devops pipeline project add --pipeline-id <id> --project-id <project-id> --json
   sf devops pipeline project delete --pipeline-id <id> --project-id <project-id> --json
   ```
   - 如果用户命名项目而不是提供其 ID，通过 `sf devops project list --json` 解析它（请参阅 `references/parsing-patterns.md`）

8. **激活/停用/重命名流水线**：
   ```bash
   # 在激活之前，确认 ≥1 阶段的确定性先决条件
   bash scripts/check-activation-ready.sh <id> [target-org]   # 如果没有阶段，则退出非零
   sf devops pipeline update --pipeline-id <id> --activate --json             # 激活
   sf devops pipeline update --pipeline-id <id> --deactivate --json           # 停用
   sf devops pipeline update --pipeline-id <id> --name "<new-name>" --json    # 重命名
   ```
   - 在 `--activate` 之前，运行 `scripts/check-activation-ready.sh <id>`，只有在退出码为 0 时才继续——当流水线没有阶段时，它会失败并显示可操作的错误消息
   - **激活后不能修改阶段**——在激活并通过它进行更改之前，完成阶段/环境配置
   - `--activate` 和 `--deactivate` 是互斥的；`--deactivate` 和 `--name` 可以在一个命令中组合

### 第三阶段——验证和报告

9. **验证操作成功**——使用 `scripts/verify-operation.sh`，它执行确定性 JSON 状态和后状态字段检查，并在不匹配时退出非零并显示可操作的错误消息：
   ```bash
   # 断言捕获的命令的 JSON 状态为 0（将 CLI 输出管道输入）
   sf devops pipeline update --pipeline-id <id> --activate --json | bash scripts/verify-operation.sh status -
   # 断言激活/阶段/项目操作后的后状态
   bash scripts/verify-operation.sh active      <id> true         [target-org]   # isActive == true
   bash scripts/verify-operation.sh has-stage   <id> "<stage>"    [target-org]   # 链中存在阶段
   bash scripts/verify-operation.sh has-project <id> "<project>"  [target-org]   # 项目已连接
   ```
   - **创建**：通过 `.Name` 确认流水线出现在 `sf devops pipeline list --json` 中，并捕获其 `.Id`
   - **阶段/环境/项目更改**：使用上述 `has-stage` / `has-project` 模式进行验证（它们读取 `sf devops pipeline get` 并检查 `.result.stages[]` / `.result.connectedProjects[]`）
   - **激活**：使用 `active <id> true` 模式进行验证

10. **报告结果**：
    - **List**：流水线名称、ID 和每个流水线的活动状态（没有阶段——那是 `get` 的用途）
    - **Get**：流水线名称、ID、活动状态、阶段链（每个阶段的名称 → 环境 → 分支，按 `nextStageId` 排序）、连接的项目
    - **Create**：流水线 ID、名称和链接的仓库（或在幂等匹配时返回“现有流水线返回”）
    - **Stage / environment / project op**：按推广顺序排列的每个阶段的最终阶段链
    - **生命周期**：新的活动状态和/或名称

### 验证检查清单（在报告成功之前进行门禁）

确认你执行的操作的项。在所有适用的框都包含以下内容之前**不要**报告成功：

- [ ] 每个 `sf devops` 命令都使用 `--json` 运行并返回 `status: 0` (`scripts/verify-operation.sh status -`)
- [ ] **Create**：新流水线通过名称出现在 `sf devops pipeline list --json` 中，并且（对于新仓库）提供了提供者特定的标志（GitHub 的 `--repo-owner`，Bitbucket 的 `--bitbucket-workspace`）
- [ ] **Add-stage / add-environment**：阶段存在于链中，并且 `--org-type` 通过了 `scripts/validate-org-type.sh` (`scripts/verify-operation.sh has-stage ...`)
- [ ] **Attach-project**：项目出现在 `.result.connectedProjects[]` 中 (`scripts/verify-operation.sh has-project ...`)
- [ ] **Activate**：`scripts/check-activation-ready.sh` 之前通过，并且 `.result.isActive` 现在为 `true` (`scripts/verify-operation.sh active <id> true`)
- [ ] **Delete-environment**：在删除之前流水线处于非活动状态

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| 所有 sf devops 命令必须使用 `--json` 标志 | 结构化输出对于无头消费是必需的；人类可读输出不适合解析 |
| 流水线在创建时需要 Git 仓库 | `sf devops pipeline create` 需要 `--name` 和 `--repo`；对于现有仓库传递仅 URL，对于新仓库添加 `--create-repo` 和 `--repo-type` |
| 新仓库创建需要提供者特定的标志 | GitHub 需要 `--repo-owner`；Bitbucket 需要 `--bitbucket-workspace`（`--bitbucket-project-key` 可选）。提供者错误的标志会导致命令失败 |
| 获取、更新和所有阶段/环境/项目操作都需要流水线 ID | 这些命令仅通过 `--pipeline-id` 识别流水线；通过 `sf devops pipeline list` 获取它 |
| 阶段 ID 来自 `pipeline get` | `stage add` (`--next-stage-id`)、`stage update`/`delete` (`--stage-id`) 和 `stage environment add` (`--stage-id`) 都需要阶段 ID |
| `stage add` 在 `--next-stage-id` 之前插入一个空阶段 | 阶段在添加环境之前不携带环境；通过锚定到后续阶段来构建链 |
| `--org-type` 必须是 `Production` 或 `Sandbox` | 该标志是一个固定的枚举；其他值会导致失败 |
| 激活前流水线必须 ≥1 阶段 | `sf devops pipeline update --activate` 拒绝没有阶段的流水线 |
| 激活 + 推广后不要修改阶段 | DevOps Center 一旦通过活动流水线推广更改，就会锁定阶段结构 |
| 删除环境需要非活动流水线 | `stage environment delete` 仅在流水线非活动时成功 |
| 项目只能附加到一个流水线 | `pipeline project add` 如果项目已附加到其他地方会失败；先分离 |
| 检查前创建的幂等性 | CLI 不会去重；列出现有流水线并返回匹配项，而不是报错 |
| 在无头运行中优先使用 `--no-browser` | `stage environment add` 打开 OAuth 浏览器流程；`--no-browser` 打印重定向 URL 以供 CI |

| 问题 | 解决方案 |
|-------|------------|
| **未设置默认组织** | 首先运行 `sf org display --json`；如果失败，指导用户运行 `sf org login web --set-default` |
| **创建失败 — 缺少仓库** | 需要 `--repo` 参数；传递现有仓库 URL，或 `--create-repo` + `--repo-type` 创建新仓库 |
| **新仓库创建失败 — 缺少提供者标志** | GitHub 新仓库需要 `--repo-owner`；Bitbucket 新仓库需要 `--bitbucket-workspace`。不要混合提供者的标志（`--repo-owner` 与 `bitbucket`，或 `--bitbucket-workspace` 与 `github`） |
| **`stage add` 失败 — 无下一阶段 ID** | 需要 `--next-stage-id` 参数；运行 `sf devops pipeline get --pipeline-id <id> --json` 找到阶段 ID，并选择新阶段应前置的阶段 |
| **环境添加在 CI 中卡住** | OAuth 浏览器流程阻塞无头运行；添加 `--no-browser` 并通过打印的重定向 URL 完成认证 |
| **激活被拒绝** | 管道至少需要一个阶段；在 `--activate` 之前添加阶段（及其环境） |
| **无法修改阶段** | 管道处于激活状态且已推进变更；阶段结构已锁定 — 配置必须在激活前完成 |
| **环境删除失败** | 管道处于激活状态；使用 `pipeline update --deactivate` 激活前删除环境 |
| **项目已附加** | 项目仅能附加到一个管道；先通过 `pipeline project delete` 从其他管道中分离 |
| **管道 / 阶段 / 项目未找到** | ID 无效；运行 `sf devops pipeline list --json`、`sf devops pipeline get --json` 或 `sf devops project list --json` 找到有效 ID |

---

## 输出预期

交付成果因操作而异：

- **列表**：管道的 ID、名称和激活状态（列表视图中不显示阶段/项目）
- **获取**：管道的 ID、名称、激活状态、其阶段链（每个阶段包含环境和分支，按 `nextStageId` 排序）以及连接的项目
- **创建**：管道 ID、名称和链接的仓库（或在幂等匹配上的现有管道）
- **阶段操作**：更新的有序阶段链
- **环境操作**：包含其绑定环境的阶段（名称、org-type）
- **项目操作**：附加/分离确认
- **生命周期**：新的激活状态和/或管道名称

输出基于 `sf devops pipeline` 和 `sf devops stage` CLI 命令生成。

---

## 跨技能集成

| 委托给 | 当...时 |
|-------------|------|
| `dx-devops-work-item-manage` | 用户希望在管道激活后创建或推进工作项 |

如果用户想附加的项目找不到，通过 `sf devops project list --json` 解决或列出现有项目（参见 `references/parsing-patterns.md`）而不是委托 — 项目创建不在本技能范围内。

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/cli-commands.md` | 需要每个 `sf devops pipeline` / `sf devops stage` 命令的详细 CLI 标志文档和 JSON 输出模式 |
| `references/parsing-patterns.md` | 需要用于解析 JSON（阶段链、管道/项目 ID 解析）、错误处理参考、创建前的幂等模式检查或认证要求 |
| `examples/common-workflows.md` | 用户请求匹配常见模式（端到端管道设置、插入阶段、绑定环境、附加项目、激活） |
| `scripts/validate-org-type.sh` | 在 `stage environment add` 前运行，验证 `--org-type` 对 `Production`/`Sandbox` 枚举 |
| `scripts/check-activation-ready.sh` | 在 `pipeline update --activate` 前运行，确认管道有 ≥1 阶段 |
| `scripts/verify-operation.sh` | 在第 3 阶段运行，断言命令的 JSON 状态和后状态字段 (`status` / `active` / `has-stage` / `has-project`) |
