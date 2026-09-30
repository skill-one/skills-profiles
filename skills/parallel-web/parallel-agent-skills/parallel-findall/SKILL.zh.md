---
name: parallel-findall
description: 发现与自然语言描述相匹配的实体（公司、人物、产品等）。当用户要求“查找所有X”或“列出所有符合Y的Z”时使用——例如，“查找2026年完成A轮融资的AI初创公司”、“列出北卡罗来纳州夏洛特市的屋顶公司”、“展示YC W24开发工具公司”。与网络搜索（返回网页）和深度研究（返回叙述性报告）不同。当用户需要实体结构化列表时使用此功能。
---

# FindAll：实体发现

Find：$ARGUMENTS

> 完整的 FindAll 需要 `parallel-cli` ≥ 0.3.0；可选的 `entity-search` 路径需要 ≥ 0.6.0。如果缺少文档中提到的命令或选项，请通过此 CLI 使用的安装方法进行更新，然后重试。请参阅 <https://docs.parallel.ai/integrations/cli>。

## 何时使用此技能

使用 FindAll 获取与描述匹配的实体结构化列表。使用 parallel-web-search 搜索网页或快速获取答案，使用 parallel-deep-research 进行叙事分析，使用 parallel-data-enrichment 为用户已有的列表添加字段。

默认使用全面的异步 `findall run`。它支持匹配条件、排除项、丰富、证据和公司及人员之外的实体类型。 “查找所有” 并不保证互联网的全面覆盖。

仅在用户明确希望快速或粗略的公司或人员列表并接受未经单独验证的结果时，才使用同步的 `entity-search` 路径。不要仅因为支持实体类型就选择它。它没有排除项、生成器选择、丰富或 FindAll 条件/丰富引用。

## 第 1 步：启动并保留运行

为保存的 JSON 文件选择一个未使用、描述性、运行特定的 `$FILENAME`。将用户的客观目标作为单个引号参数传递，不要进行 shell 评估。

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json -o "/tmp/$FILENAME-create.json"
```

默认生成器为 `core`，匹配限制为 `10`。使用 `-n 50` 获取最多 50 个匹配实体；允许的限制是 5–1000。除非用户请求不同的权衡，否则保持 `core`。`pro` 搜索更大的池，但更慢/更昂贵；`base` 是一个更快、质量较低的选择，用于明确请求的粗略扫描。针对 `base` 对批量、年份和地理区域等具体声明与可用证据进行抽查。

对于请求的排除项：

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json \
    --exclude '[{"name":"Google","url":"google.com"},{"name":"OpenAI","url":"openai.com"}]' \
    -o "/tmp/$FILENAME-create.json"
```

如果目标需要澄清，`parallel-cli findall ingest "$ARGUMENTS" --json` 预览推断的实体类型、条件和建议的丰富项。这会调用 API；它不是离线或免费的测试。如果推断的条件与用户的意图不同，请在创建运行之前完善目标。

立即捕获返回的 `findall_id`，以及目标、生成器、匹配限制和排除项。如果实际返回了监控 URL，则报告运行已启动并给出监控 URL。不要推断 URL 或保证完成时间。如果创建响应丢失，请在再次提交之前解决现有工作。

## 第 2 步：明确添加请求的字段

`--no-wait` 摄取并创建运行，但**不**应用建议的丰富项。请求的输出字段（如 CEO 名称或员工数量）需要单独的丰富请求；在目标中提及它们是不够的。

```bash
parallel-cli findall enrich "$FINDALL_ID" \
    '{"type":"object","properties":{"ceo":{"type":"string","description":"CEO name"},"employee_count":{"type":"number","description":"Number of employees"}}}' \
    -p core --json
```

使用描述用户字段的 JSON Schema 对象，而不是完整的摄取信封。保留提交的确切模式和处理程序与运行 ID 本地，包括如果使用多个请求。不要依赖模式摘要来稍后重建它们。丰富添加非布尔输出数据；它不会改变匹配条件。

丰富可以在运行活动期间或完成后添加。终端运行可以重新排队以处理字段。创建、丰富接受和填充结果分别是独立的输出。不要仅从丰富响应或完成的轮询中声称字段已准备好。

## 第 3 步：检查状态并检索结果

```bash
parallel-cli findall status "$FINDALL_ID" --json
parallel-cli findall poll "$FINDALL_ID" -o "/tmp/$FILENAME.json" --timeout 60
parallel-cli findall result "$FINDALL_ID" -o "/tmp/$FILENAME-snapshot.json"
```

使用有界的等待。超时（退出码 5）或中断是本地等待耗尽，不是取消。在运行活动期间检查状态并继续使用相同的 ID，在用户的等待窗口内；不要提交另一个运行。共享轮询器不识别兼容性状态 `action_required`。如果出现该状态、`failed`、`cancelled` 或不活跃的未完成状态，请停止自动等待并报告状态和保存的 ID 需要关注。

`result` 返回一个快照，并不能证明完成。一起读取 `status` 和 `is_active`。丰富后，检查每个匹配候选的 `output` 以每个请求的字段。如果字段缺失，在有界等待窗口内进行进一步的结果快照，即使第一个轮询说已完成。报告缺失、空或失败值，而不是凭空捏造；如果窗口过期，返回部分结果和 ID 以便恢复。一个空的匹配集并不能证明成功丰富。

避免对大型结果集使用 `--json`；`-o` 保留完整的 JSON。这些命令可能会覆盖其选择的文件，因此使用属于此运行的路径。保留原始候选列表和状态。`/tmp` 是临时的；在需要时将请求的交付内容复制到持久化的用户位置。

## 展示匹配项和证据

仅将 `match_status: "matched"` 的候选者作为匹配项展示。在原始文件中保留生成的、未匹配的和丢弃的候选者。审查明显的查询回声占位符和不支持的条目，而不是将每个候选者视为实体。

在实体上下文中审查 URL。LinkedIn 个人资料可以合法地识别人员，YC 或 Crunchbase 个人资料可以识别公司。不要仅因为实体不拥有域名就丢弃这些。标记缺失或无法验证的 URL，并使用可用证据来解决不确定性。

使用条件和丰富依据进行事实性声明，并附带其来源 URL。实体的主要 URL 和支持性引用可能不同。除非它支持声明，否则不要将主要/个人资料 URL 标记为证据。

首先展示匹配的实体数量，注意排除项或未解决的条目，并使用带有名称、URL 和请求字段的表格或列表。包括保存的原始结果路径、运行 ID、当前状态和任何不完整的字段。稀疏或嘈杂的结果可能需要建议修改目标或生成器；不要自动创建替代的付费运行。

## 获取更多匹配项

仅在用户请求额外匹配项时扩展：

```bash
parallel-cli findall schema "$FINDALL_ID" --json
parallel-cli findall extend "$FINDALL_ID" 50 --json
```

`50` 是增量，不是新的总数。检查已知的创建限制或当前模式，包括先前的扩展，以确保结果总数保持在 1000 或以下。预览运行不能扩展。只有当其终止原因是 `match_limit_met` 时，完成的运行才有资格；CLI 中的状态/结果会省略该原因，不能证明资格。对于明确请求的、在限制内的扩展，让 API 验证资格并显示任何拒绝，而不要自动创建新的运行。

保留更新的限制并轮询相同的 ID 获取新结果。重新检查请求的丰富字段；如果现有的丰富必须重新应用，请在用户的授权范围内使用原始保留的请求有效负载和处理程序。

## 快速实体搜索

仅用于明确的速度/粗略列表意图，且实体类型为 `companies` 或 `people`。它是同步的，返回 `entity_set_id` 加上排名的 `entities`，而不是 `findall_id` 或验证的候选者。

```bash
parallel-cli findall entity-search "$ARGUMENTS" -t companies -n 10 -o "/tmp/$FILENAME.json"
```

`-n` 限制是 5–1000，默认为 10。选择与用户请求成比例的限值。避免在此路径上设置过于严格的条件：相关性在尾部可能会下降。使用 FindAll 时需要单独的条件检查或丰富。

保留合法的目录/个人资料链接，并审查空的 URL 或查询回声名称。将其作为未验证的线索展示，引用其链接作为指向实体的链接，并避免将缺少 FindAll 基础或验证归因于它们。报告保存的路径和返回的计数。如果用户后来请求这些功能，解释需要一个单独的完整运行，并保留原始快速结果。

## 设置

需要安装并认证的 `parallel-cli`。检查 `parallel-cli --version` 和 `parallel-cli auth --json`；认证可能成功退出，而 `authenticated` 为 false。缺少二进制文件、不支持的命令/选项和认证失败需要不同的补救措施：安装、通过现有安装方法升级或终端登录。请参阅 <https://docs.parallel.ai/integrations/cli>。认证失败时停止受影响的请求，不要在聊天中请求密钥，不要更改账户策略以绕过阻止的设置。
