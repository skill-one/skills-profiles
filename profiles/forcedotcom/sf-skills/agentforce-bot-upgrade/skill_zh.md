# Einstein Bot 升级协调器

## 目的

运行多机器人升级和交接循环：

1. 解析和验证来自 `--bots` 的机器人/版本对
2. 根据 bot-version 对遵循 [生成代理规范参考](references/generate-agent-spec.md)（可并行化）
3. 需要所有生成的代理规范进行聚合步骤
4. 每个 Agent Spec 执行 `/agentforce-generate`（可并行化）
5. 每个 生成的代理脚本进行转换后增强（可并行化）

## 输入

输入：
- `--mode <online|offline>` 是可选的；省略时默认为 `online`。
- 如果 `mode=online`，则必需：
  - `--org-alias <org-alias>`
  - `--bots <bot1:v1,bot2:v2,...>`
- 如果 `mode=offline`，则必需：
  - `--offline-dir <offline-dir>`
- `--interactive <true|false>` 是可选的；省略时默认为 `true`。

如果必需输入缺失，则按照下方的缺失输入处理和交互模式规则进行处理。

## 交互模式

`--interactive` 控制技能在执行期间是否暂停等待用户输入：

- `--interactive true`（默认）：通过询问用户来解决歧义、打开问题、并批准交接门，如本技能及其参考中所述。
- `--interactive false`：自主运行。在任何决策点**不要**提示用户。对于每个开放问题、歧义或交接门，应用文档中推荐的默认值/解决方案，并在运行工件（代理规范、开放问题、提取摘要）中记录自动应用的决策。允许的唯一无提示停止是输入缺失或矛盾且没有安全推荐默认值的情况——缺失必需的启动输入（`--org-alias`/`--bots` 对于 online，`--offline-dir` 对于 offline）、未发现机器人或相同机器人给出多个版本。在这些情况下，报告问题并停止执行，无需提示。

将有效的 `--interactive` 值传递到每个机器人的生成代理规范工作流（步骤 2）、规划器工作流（步骤 3）和转换后增强传递（步骤 5）。

## 缺失输入处理

在步骤 1 之前解决缺失的必需启动输入：

1. **在线模式 — 未提供 `--org-alias`。** 在尝试列出机器人之前解决此问题（列出机器人需要目标组织）。
   - 交互：列出登录组织的可用别名，并要求用户选择目标组织。使用 [SF CLI 机器人参考](references/sf-cli-bot-reference.md) 中的 SF CLI 模式。
   - 非交互：使用明确的错误命名缺失的 `--org-alias` 输入停止执行（不要提示或列出）。
2. **在线模式 — 机器人名称和版本 (`--bots`) 不可用。**
   - 交互：使用 `--org-alias` 作为目标组织，列出组织中的每个机器人和其版本，然后要求用户选择要转换为代理的机器人/版本条目。使用 [SF CLI 机器人参考](references/sf-cli-bot-reference.md) 中的 `BotDefinition` 和 `BotVersion` 查询模式——省略名称/版本过滤器以枚举所有机器人和版本——显示结果，并从用户的选择构建 `--bots` 工作负载。
   - 非交互：使用明确的错误命名缺失的 `--bots` 输入停止执行（不要提示或列出）。
3. **离线模式 — 未提供 `--offline-dir`。**
   - 交互：要求用户提供 `--offline-dir` 路径，然后继续。
   - 非交互：使用明确的错误命名缺失的 `--offline-dir` 输入失败（不要提示）。

## 参考

执行期间使用以下参考文件：

1. [SF CLI 机器人参考](references/sf-cli-bot-reference.md)
2. [生成代理规范参考](references/generate-agent-spec.md)
3. [规划器工作流参考](references/planner-workflow-reference.md)
4. [转换后增强参考](references/post-conversion-enhancements-reference.md)
5. [提取蓝图](references/extraction-blueprint.md)
6. [输入契约](references/input-contract.md)
7. [映射规则](references/mapping-rules.md)
8. [交接输出格式](references/handoff-output-format.md)
9. [质量检查清单](references/quality-checklist.md)

## 执行契约

### 步骤 1：解析和验证 `--bots`

按顺序执行步骤 1：

1. 解析模式：
   - 如果 `--mode` 省略，使用 `online`。
2. 为本次调用重新开始：
   - 不要发现、检查或重用先前运行产生的输出
   - 将本次调用视为干净的执行上下文
   - 仅使用本次调用流程中产生的工件
3. 构建初始工作负载列表：
   - `mode=online`：读取 `--bots` 并按逗号分割。
   - `mode=offline`：扫描 `<offline-dir>` 并收集直接子目录作为机器人工作负载根目录。
4. 验证输入格式：
   - `mode=online`：每个 `--bots` 标记必须匹配 `<bot-name>:<version>`。
   - `mode=offline`：确保至少存在一个机器人子目录；否则停止（在交互模式下要求用户澄清；在非交互模式下根据交互模式规则使用明确的错误停止）。
5. 规范化工作负载条目：
   - `mode=online`：构建 `{bot_name, bot_version}` 条目。
   - `mode=offline`：构建 `{offline_bot_dir}` 条目（当可从子目录结构推导出时，标注推断的机器人名称和版本；如果不可推导，则保留条目不命名并继续）。
6. 执行在线模式下的每个机器人一个版本的规则：
   - 如果相同的 `bot_name` 出现多个版本，则停止（在交互模式下要求用户澄清；在非交互模式下根据交互模式规则使用明确的错误停止）。
7. 应用离线机器人过滤器：
   - 如果 `mode=offline` 且提供了 `--bots`，则仅将其用作发现子目录的过滤器；不要将其视为必需的离线输入。
8. 持久化步骤 1 输出：
   - 保存并传递给步骤 2 并行执行的验证工作负载列表。

### 步骤 2：运行 Einstein Bot 升级（每个机器人-版本）

根据 [生成代理规范参考](references/generate-agent-spec.md) 为每个机器人-版本组合执行代理规范生成工作流：
- `--mode <online|offline>`（省略时默认为 `online`）
- 模式特定的必需输入：
  - online -> `--org-alias`, `--bot`, `--bot-version`
  - offline -> `--offline-dir`
- `--interactive <true|false>`（传递协调器的有效值；默认为 `true`）

并行化规则：
- 在 `mode=online` 中，并行执行调用，因为每个机器人-版本对是独立的。
- 在 `mode=offline` 中，并行执行 [生成代理规范参考](references/generate-agent-spec.md) 工作流，覆盖步骤 1 中发现的每个机器人子目录。
  - 为每个调用传递 `--mode offline` 和 `--offline-dir <bot-subdirectory-path>`。
确保每个调用（在线/离线）使用隔离的工作目录，以避免跨运行文件冲突。

硬规则：
- 不要跳过此步骤。

### 步骤 3：聚合 + 规划器步骤（条件性）

在所有升级调用完成后：

1. 始终构建包含 `{bot_name, bot_version, run_project_dir, agent_spec_path}` 的合并列表。
2. 始终构建失败的/不完整的升级运行列表（如果有）。
3. 始终构建仅包含有效代理规范条目的初始待编写列表。
   - 每个条目必须包含：`{bot_name, bot_version, run_project_dir, agent_spec_path, handoff_json_path, open_questions_path}`。
4. 如果总机器人工作负载数量大于 1：
   - 执行 [规划器工作流参考](references/planner-workflow-reference.md) 工作流，使用：
     - 所有待编写的 `agent_spec_path` 值作为 `spec_paths`
     - 协调器工作目录作为 `working_dir`
     - 每个待编写条目相关的每个规范工件：`handoff_json_path`（交接 JSON）和 `open_questions_path`（开放问题）
   - 需要输出文件位于 `<orchestrator working directory>/bot-upgrade-planner-output.json`。
   - 读取 `bot-upgrade-planner-output.json` 并应用：
     - 如果 `specs_changed=true`：使用规划器字段（`updated_spec_path`, `run_project_dir`, `handoff_json_path`, `open_questions_path`）替换待编写条目
     - 如果 `specs_changed=false`：保持原始待编写列表不变
5. 如果总机器人工作负载数量为 1：
   - 完全跳过规划器工作流。
   - 保持原始待编写列表不变。

规划器输出预期：
1. 布尔值 `specs_changed`
2. `updated_specs` 数组，包含条目：
   - `original_spec_path`
   - `updated_spec_path`
   - `run_project_dir`
   - `handoff_json_path`
   - `open_questions_path`
3. `updated_specs` 在 `specs_changed=false` 时必须为空

### 步骤 4：调用 Agentforce-Generate（每个代理规范）

对于最终待编写列表（步骤 3 规划器协调后）的每个条目：

0. 在调用 `/agentforce-generate` 之前，将此建议添加到生成的调用上下文中：
   - 在本次协调运行中**不要**激活代理脚本版本。
   - 需要草稿迭代：生成 `.agent`、验证、部署和预览测试是允许的。
   - 激活应推迟，除非用户明确要求发布。
1. 从最终待编写条目中解析有效的 `run_project_dir`。
2. 完全读取 `<run_project_dir>/agentforce-generate-invocation-prompt.md`。
3. 如果步骤 3 产生了规划器更新的规范路径/工件，则在调用上下文中应用路径替换，以便规范/交接/开放问题引用指向更新后的文件。
   - 如果规划器也更改了 `run_project_dir`，则使用更新的 `run_project_dir` 来解析提示/输出契约路径。
4. 保持原始生成提示中的所有非路径指令不变。
5. 使用此解析的调用上下文调用 `/agentforce-generate`。
6. 读取 `<run_project_dir>/agentforce-generate-output-contract.md` 并精确捕获输出。

并行化规则：
- 跨代理规范并行调用 `/agentforce-generate`，因为每个运行是独立的。

输出契约捕获规则：

1. 将输出契约视为必需字段/工件的权威来源。
2. 如果任何契约字段缺失，则将状态标记为部分，并明确列出缺失字段。
3. 返回捕获的输出，其键与契约名称匹配。
4. 保留输出文件路径和每个必需工件的状态。
5. 如果某个条目缺少预期的提示/契约文件，则将该条目标记为 `partial`，记录缺失路径，并继续处理其他条目。

### 步骤 5：转换后代理脚本增强（每个生成的代理脚本）

在步骤 4 完成后，对于每个生成的 `.agent` 工件：

1. 从捕获的 `/agentforce-generate` 输出中解析生成的 `.agent` 文件路径。
2. 执行 [转换后增强参考](references/post-conversion-enhancements-reference.md) 中的后转换增强工作流，使用：
   - `agentscript_file=<generated-agent-file-path>`
   - `mode=<online|offline>`（步骤 1 中解析的有效协调器运行模式）
   - online 模式仅：`org_alias=<org-alias>`（必需，以便增强的代理脚本可以重新部署）
3. 要求原位增强：
   - 优化/增强的输出必须写入相同的 `.agent` 文件位置。
4. 捕获每个文件的增强状态和任何部分失败。

并行化规则：
- 跨生成的 `.agent` 文件并行执行后转换增强工作流，因为每个文件增强是独立的。

### 步骤 6：合并运行报告并结束

对于工作负载中的每个机器人，在步骤 5 完成后：

1. 在协调器工作目录中编写单个合并的、人类可读的运行报告，作为非空的 Markdown 文件。对于每个机器人，报告必须声明：有效运行模式、规划器是否运行（`executed` 或 `skipped`）、生成的代理规范路径和生成的 `.agent` 路径、行动清单（包括任何 `NEEDS_STUB` 条目），以及当 `--interactive=false` 时——自动应用的决策。
2. 将运行报告视为最终工件：仅在所有其他工件（代理规范、交接 JSON、开放问题、任何规划器输出和生成的 `.agent` 文件）都已写入后写入它。

## 可交付成果

返回：
1. 解析的机器人/版本列表
2. 每个机器人升级执行状态
3. 聚合输出（完整的代理规范列表 + 最终待编写子集）
4. 规划器工作流状态（`executed` 或 `skipped`）和 `bot-upgrade-planner-output.json` 路径（当执行时）
5. 每个规范的 `/agentforce-generate` 执行状态
6. 每个机器人/规范的生成交接工件路径（包括适用时的规划器更新工件）
7. 每个 `/agentforce-generate` 输出契约捕获
8. 每个代理转换后增强状态（包括增强的 `.agent` 文件路径）
9. 步骤 6 中编写的运行报告路径
