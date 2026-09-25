# DevOps Center 管道管理

管理 DevOps Center 中的完整管道生命周期——从基于存储库创建开始，经过阶段和环境配置以及项目关联，到激活准备就绪的发布管道。提供无头 CLI 驱动的操作，用于自主发布工作流。

## 范围

- **在范围内**：列出管道、获取管道详细信息、创建管道（链接到现有或新的 Git 仓库）、添加/删除/重命名阶段、在阶段上添加/删除 Salesforce 环境、关联/分离项目、以及激活/停用/重命名管道
- **超出范围**：工作项生命周期、发布/部署执行、冲突检测、独立项目创建（单独的技能）

---

## 必需的输入

在进行下一步之前收集或推断：

- **操作类型**：list、get、create、add-stage、delete-stage、rename-stage、add-environment、delete-environment、attach-project、detach-project、activate 或 deactivate
- **对于 get / 任何阶段或环境操作**：管道 ID（必需）——通过 `sf devops pipeline list --json` 获取
- **对于 create**：管道名称（必需）和一个 Git 仓库（`--repo`，必需）。仓库标志因场景而异：
  - **现有仓库（GitHub 或 Bitbucket）**：仅 `--repo <url>` —— 不要传递 `--repo-type`/`--create-repo`
  - **新的 GitHub 仓库**：`--repo <name> --create-repo --repo-type github --repo-owner <组织或用户>`
  - **新的 Bitbucket 仓库**：`--repo <name> --create-repo --repo-type bitbucket --bitbucket-workspace <工作区>` (`--bitbucket-project-key <key>` 可选)
  - 在所有情况下，描述（`--description`）可选
- **对于 add-stage**：管道 ID、新阶段名称和 `--next-stage-id`（新阶段之前的前一个阶段）——通过 `sf devops pipeline get` 获取阶段 ID
- **对于 add-environment**：管道 ID、阶段 ID、环境名称和 `--org-type`（生产或沙盒）
- **对于 attach/detach-project**：管道 ID 和项目 ID
- **对于 activate/deactivate/rename**：管道 ID

默认值（除非指定）：
- 输出格式：`--json` 用于无头消费
- 目标组织：如果不依赖默认组织，请使用 `--target-org <别名>`

如果用户给出明确请求（"在仓库 myorg/myrepo 上创建管道"、"在生产之前添加 UAT 阶段"、"激活管道 0XB..."），请立即进行，不要提出不必要的问题。

---

## 工作流

所有操作都使用 `sf devops pipeline` 和 `sf devops stage` CLI 命令，并使用 `--json` 输出进行结构化消费。管道 ID 和阶段 ID 是主要标识符——在修改之前通过 `list` 和 `get` 解析它们。

### 第一阶段——识别操作

1. **根据用户意图确定操作类型**：
   - "list"、"显示所有管道" → list；"管道的详细信息"、"显示阶段" → get
   - "create"、"设置"、"新管道" → create
   - "添加阶段"、"插入阶段" → add-stage；"重命名阶段" → rename-stage；"删除/移除阶段" → delete-stage
   - "连接环境"、"将组织添加到阶段" → add-environment；"移除环境" → delete-environment
   - "附加项目"、"连接项目" → attach-project；"分离项目" → detach-project
   - "激活"、"开启"；"停用"、"关闭"；"重命名管道" → 生命周期更新

### 第二阶段——执行操作

2. **在任何操作之前验证组织认证**：
   ```bash
   sf org display --json
   ```
   - 如果没有设置默认组织或认证已过期，指示用户运行 `sf org login web --set-default --alias <别名>`
   - 通过运行 `sf devops pipeline list --json` 确认组织已启用 DevOps Center
   - 当针对特定组织时，在所有命令中添加 `--target-org <别名>`

3. **检查管道**：
   ```bash
   sf devops pipeline list --json                              # 组织中的所有管道
   sf devops pipeline get --pipeline-id <pipeline-id> --json   # 一个管道，包含阶段/仓库/项目
   ```
   - `list` 返回以 `.result.pipelines[]` 为 SObject 记录，字段大写（`.Id`、`.Name`、`.IsActive`）——它**不**包含阶段或连接的项目
   - `get` 返回一个管道在 `.result` 下，字段小写（`.id`、`.name`、`.stages[]`、`.connectedProjects[]`）；每个阶段有 `.id`、`.name`、`.nextStageId`、`.branchName` 和 `.environment.{id,name}`。**阶段是一个链表**——顺序由 `nextStageId` 定义，终端阶段的 `nextStageId` 为 null。使用 `get` 发现**阶段 ID**，然后进行任何阶段或环境操作

4. **创建管道**——管道必须链接到 Git 仓库。`--name` 和 `--repo` 始终是必需的；其余标志取决于仓库场景：
   ```bash
   # 现有仓库（GitHub 或 Bitbucket）——传递完整的仓库 URL，其他什么也不要
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-url> --json

   # 新的 GitHub 仓库——需要 `--repo-owner`
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-name> \
     --create-repo --repo-type github --repo-owner <org-or-user> --json

   # 新的 Bitbucket 仓库——需要 `--bitbucket-workspace`（`--bitbucket-project-key` 可选）
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-name> \
     --create-repo --repo-type bitbucket --bitbucket-workspace <workspace> \
     --bitbucket-project-key <key> --json

   # 自定义阶段链（任何场景）——按发布顺序重复 `--stage`
   sf devops pipeline create --name "<pipeline-name>" --repo <repo-url> \
     --stage Dev --stage QA --stage Prod --json
   ```
   - 提供商特定的必需标志：**GitHub 新仓库** → `--repo-owner`；**Bitbucket 新仓库** → `--bitbucket-workspace`。省略提供商的必需标志会导致创建失败
   - 对于现有仓库，**不要**传递 `--repo-type`/`--create-repo` —— 仅通过 `--repo` 传递仓库 URL
   - **创建时自定义阶段**：新管道会生成默认阶段链 **集成 → UAT → 预发布 → 生产**。要生成不同的阶段，按发布顺序重复 `-s/--stage` 一次每个阶段——例如 `--stage Dev --stage QA --stage Prod`。这避免了之后添加/重命名阶段
   - 在任何场景中可选添加 `--description "<text>"`
   - 捕获返回的管道 ID，用于后续的阶段/环境/项目/激活步骤
   - **幂等性**：CLI 不去重。在创建之前，运行 `sf devops pipeline list --json` 并检查是否有相同名称/仓库的管道；如果找到，返回现有管道。参见 `references/parsing-patterns.md` 中的检查前创建片段

5. **配置阶段**——阶段相对于现有阶段添加，然后绑定到环境。**在多阶段工作之前，请阅读 `references/cli-commands.md`**：
   ```bash
   # 在现有阶段之前插入一个空阶段（从 `pipeline get` 获取 next-stage-id）
   sf devops pipeline stage add --pipeline-id <id> --name "<stage-name>" --next-stage-id <stage-id> --json
   # 重命名阶段
   sf devops pipeline stage update --pipeline-id <id> --stage-id <stage-id> --name "<new-name>" --json
   # 删除阶段（前驱自动重新链接到后继）
   sf devops pipeline stage delete --pipeline-id <id> --stage-id <stage-id> --json
   ```
   - `stage add` 插入一个**空**阶段（没有分支/环境）；单独配置其环境
   - 通过插入每个新阶段在应跟随它的阶段之前来构建发布链

6. **将环境绑定到阶段**——将 Salesforce 组织附加到阶段：
   ```bash
   # 在调用 CLI 之前验证 org-type 对固定枚举
   bash scripts/validate-org-type.sh "<Production|Sandbox>"   # 在无效值上退出非零
   sf devops stage environment add --pipeline-id <id> --stage-id <stage-id> \
     --environment-name "<env-name>" --org-type <Production|Sandbox> --json
   # 移除环境（管道必须处于非活动状态）
   sf devops stage environment delete --pipeline-id <id> --environment-id <env-id> --json
   ```
   - `--org-type` 必须是 `Production` 或 `Sandbox`——首先运行 `scripts/validate-org-type.sh <value>`，只有在退出 0 时才继续
   - **无头注意事项**：`stage environment add` 触发 OAuth 浏览器流程。在无头/CI 运行中传递 `--no-browser`——CLI 打印重定向 URL 以进行手动认证

7. **附加/分离项目**——项目只能附加到一个管道：
   ```bash
   sf devops pipeline project add --pipeline-id <id> --project-id <project-id> --json
   sf devops pipeline project delete --pipeline-id <id> --project-id <project-id> --json
   ```
   - 如果用户命名项目而不是提供其 ID，通过 `sf devops project list --json` 解析它（参见 `references/parsing-patterns.md`）

8. **激活/停用/重命名管道**：
   ```bash
   # 在激活之前，确认 ≥1 阶段的确定性先决条件
   bash scripts/check-activation-ready.sh <id> [target-org]   # 如果没有阶段，则退出非零
   sf devops pipeline update --pipeline-id <id> --activate --json             # 激活
   sf devops pipeline update --pipeline-id <id> --deactivate --json           # 停用
   sf devops pipeline update --pipeline-id <id> --name "<new-name>" --json    # 重命名
   ```
   - 在 `--activate` 之前，运行 `scripts/check-activation-ready.sh <id>`，只有在退出 0 时才继续——它会在管道没有阶段时失败并给出可操作的提示
   - **激活后不能修改阶段**——在激活并通过它进行更改之前，完成阶段/环境配置
   - `--activate` 和 `--deactivate` 互斥；`--deactivate` 和 `--name` 可在一个命令中组合

### 第三阶段——验证和报告

9. **验证操作成功**——使用 `scripts/verify-operation.sh`，它执行确定性的 JSON 状态和后状态字段检查，并在不匹配时退出非零并给出可操作的提示：
   ```bash
   # 断言捕获的命令的 JSON 状态为 0（将 CLI 输出管道）
   sf devops pipeline update --pipeline-id <id> --activate --json | bash scripts/verify-operation.sh status -
   # 断言激活/阶段/项目操作后的后状态
   bash scripts/verify-operation.sh active <id> true         [target-org]   # isActive == true
   bash scripts/verify-operation.sh has-stage   <id> "<stage>"    [target-org]   # 链中存在阶段
   bash scripts/verify-operation.sh has-project <id> "<project>"  [target-org]   # 连接项目
   ```
   - **创建**：通过 `sf devops pipeline list --json` 确认管道按 `.Name` 出现，并捕获其 `.Id`
   - **阶段/环境/项目更改**：使用上述 `has-stage` / `has-project` 模式进行验证（它们读取 `sf devops pipeline get` 并检查 `.result.stages[]` / `.result.connectedProjects[]`）
   - **激活**：使用 `active <id> true` 模式进行验证

10. **报告结果**：
    - **List**：管道的名称、ID 和活动状态（列表视图中没有阶段/项目）
    - **Get**：管道的名称、ID、活动状态、其阶段链（每个阶段的名称 → 环境 → 分支，按 `nextStageId` 排序）、连接的项目
    - **Create**：管道 ID、名称和链接的仓库（或在幂等匹配上返回现有管道）
    - **Stage op**：更新的有序阶段链
    - **Environment op**：具有绑定环境的阶段（名称、org-type）
    - **Project op**：附加/分离的确认
    - **生命周期**：新的活动状态和/或管道名称

### 验证检查清单（在报告成功之前进行门禁）

确认你执行的操作的项。在报告成功之前，**不要**在适用的框中持有：

- [ ] 每个 `sf devops` 命令都使用 `--json` 运行并返回 `status: 0` (`scripts/verify-operation.sh status -`)
- [ ] **Create**：新管道按名称出现在 `sf devops pipeline list --json` 中，并且（对于新仓库）提供了提供商特定的标志（`--repo-owner` for GitHub，`--bitbucket-workspace` for Bitbucket）
- [ ] **Add-stage / add-environment**：阶段存在于链中并且 `--org-type` 通过了 `scripts/validate-org-type.sh` (`scripts/verify-operation.sh has-stage ...`)
- [ ] **Attach-project**：项目显示在 `.result.connectedProjects[]` 中 (`scripts/verify-operation.sh has-project ...`)
- [ ] **Activate**：`scripts/check-activation-ready.sh` 之前通过，并且 `.result.isActive` 现在是 `true` (`scripts/verify-operation.sh active <id> true`)
- [ ] **Delete-environment**：管道在删除之前处于非活动状态

---

## 规则/约束

| 约束 | 理由 |
|-----------|-----------|
| 所有 sf devops 命令必须使用 `--json` 标志 | 结构化输出对于无头消费是必需的；人类可读输出不可靠，无法解析 |
| 管道在创建时需要 Git 仓库 | `sf devops pipeline create` 需要 `--name` 和 `--repo`；对于现有仓库传递仅 URL，对于新仓库添加 `--create-repo` 和 `--repo-type` |
| 新仓库创建需要提供商特定的标志 | GitHub 需要 `--repo-owner`；Bitbucket 需要 `--bitbucket-workspace` (`--bitbucket-project-key` 可选)。错误的提供商标志会导致命令失败 |
| 获取、更新和所有阶段/环境/项目操作都需要管道 ID | 这些命令仅通过 `--pipeline-id` 识别管道；通过 `sf devops pipeline list` 获取它 |
| 阶段 ID 来自 `pipeline get` | `stage add` (`--next-stage-id`)、`stage update`/`delete` (`--stage-id`) 和 `stage environment add` (`--stage-id`) 都需要阶段 ID |
| `stage add` 在 `--next-stage-id` 之前插入一个空阶段 | 阶段在添加环境之前不携带任何环境；通过锚定到后续阶段来构建链 |
| `--org-type` 必须是 `Production` 或 `Sandbox` | 该标志是固定的枚举；其他值会导致失败 |
| 激活前管道必须 ≥1 阶段 | `sf devops pipeline update --activate` 拒绝没有阶段的管道 |
| 激活后 + 推广不能修改阶段 | DevOps Center 一旦通过活动管道推广更改，就会锁定阶段结构 |
| 环境删除需要非活动管道 | `stage environment delete` 仅在管道非活动时才成功 |
| 项目只能附加到一个管道 | `pipeline project add` 如果项目已附加到其他管道会失败；先分离 |
| 幂等创建通过检查前创建 | CLI 不去重；列出现有管道并返回匹配项，而不是报错 |
| 在无头运行中优先使用 `--no-browser` | `stage environment add` 打开 OAuth 浏览器流程；`--no-browser` 打印重定向 URL 用于 CI |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| **未设置默认组织** | 首先运行 `sf org display --json`；如果失败，指示用户运行 `sf org login web --set-default` |
| **创建失败——缺少仓库** | `--repo` 是必需的；传递现有仓库 URL，或 `--create-repo` + `--repo-type` for a new repo |
| **新仓库创建失败——缺少提供商标志** | GitHub 新仓库需要 `--repo-owner`；Bitbucket 新仓库需要 `--bitbucket-workspace`。不要混合提供商的标志（`--repo-owner` with `bitbucket`，或 `--bitbucket-workspace` with `github`） |
| **`stage add` 失败——没有 next-stage-id** | `--next-stage-id` 是必需的；运行 `sf devops pipeline get --pipeline-id <id> --json` 找到阶段 ID，并选择新阶段应先于其之前 |
| **环境添加在 CI 中挂起** | OAuth 浏览器流程阻塞无头运行；添加 `--no-browser` 并通过打印的重定向 URL 完成认证 |
| **激活被拒绝** | 管道至少需要一个阶段；在 `--activate` 之前添加阶段（及其环境） |
| **无法修改阶段** | 管道处于活动状态并且已推广更改；阶段结构被锁定——配置必须在激活前完成 |
| **环境删除失败** | 管道处于活动状态；使用 `pipeline update --deactivate` 激活前删除环境 |
| **项目已附加** | 项目只能附加到一个管道；首先通过 `pipeline project delete` 从其他管道分离 |
| **管道/阶段/项目未找到** | ID 无效；运行 `sf devops pipeline list --json`、`sf devops pipeline get --json` 或 `sf devops project list --json` 找到有效 ID |

---

## 输出预期

交付成果因操作而异：

- **List**：具有 ID、名称和每个管道的活动状态（列表视图中没有阶段/项目）
- **Get**：具有 ID、名称、活动状态、其阶段链（每个阶段的名称 → 环境 → 分支，按 `nextStageId` 排序）、和连接的项目
- **Create**：管道 ID、名称和链接的仓库（或在幂等匹配上返回现有管道）
- **Stage op**：更新的有序阶段链
- **Environment op**：具有绑定环境的阶段（名称、org-type）
- **Project op**：附加/分离的确认
- **生命周期**：新的活动状态和/或管道名称

输出来自 `sf devops pipeline` 和 `sf devops stage` CLI 命令。

---

## 跨技能集成

| 委托给 | 当... |
|-------------|------|
| `dx-devops-work-item-manage` | 用户希望在管道激活后创建或推进工作项 |

如果用户想要附加的项目找不到，通过 `sf devops project list --json` 解析或列出现有项目（参见 `references/parsing-patterns.md`），而不是委托——项目创建不在此技能范围内。

---

## 参考文件索引

| 文件 | 当你需要...时阅读 |
|------|-------------|
| `references/cli-commands.md` | 你需要详细的 CLI 标志文档和每个 `sf devops pipeline` / `sf devops stage` 命令的 JSON 输出模式 |
| `references/parsing-patterns.md` | 你需要 jq 片段来解析 JSON（阶段链、管道/项目 ID 解析）、错误处理参考、检查前创建的幂等模式或认证要求 |
| `examples/common-workflows.md` | 当用户的请求匹配常见模式（端到端管道设置、插入阶段、绑定环境、附加项目、激活） |
| `scripts/validate-org-type.sh` | 在 `stage environment add` 之前运行，以验证 `--org-type` 对 `Production`/`Sandbox` 枚举 |
| `scripts/check-activation-ready.sh` | 在 `pipeline update --activate` 之前运行，以确认管道有 ≥1 阶段 |
| `scripts/verify-operation.sh` | 在第三阶段运行，以断言命令的 JSON 状态和后状态字段 (`status` / `active` / `has-stage` / `has-project`) |
