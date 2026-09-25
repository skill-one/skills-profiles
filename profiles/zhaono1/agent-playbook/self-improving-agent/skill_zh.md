# 自我改进代理

将已完成工作的证据转化为一个可审计的小型行为改变。默认结果是候选或无变化——不是自动重写技能。

## 使用此技能的情况

- 工具或工作流以可能再次发生的方式失败。
- 用户纠正了假设、需求或操作规则。
- 相同的变通方法出现超过一次。
- 聚焦测试证明了一个更好的可重用方法。
- 用户要求审查或整合学习候选。

不要用于常规会话摘要、原始转录存储、没有证据的推测性想法或属于项目文档的项目事实。

## 必须的结果

每次运行都以恰好一个状态结束：

1. `candidate`：可重用但尚未验证。
2. `validated`：有代表性证据支持该经验教训，但尚未声明所有者变更。
3. `applied`：已验证的经验教训被安装在一个命名的持久所有者中，并带有变更引用。
4. `rejected`：已被证伪、不安全、过于具体或过时。
5. `superseded` 或 `rolled_back`：已应用/验证的经验教训被替换或还原。
6. `no-delta`：未发现可重用的行为改变。
7. `open-question`：证据不足，缺失的证明被命名。

一个工件不是改进的证据。必须改变未来行为并有一个代表性检查来证明该改变。

## 启动数据包

在编辑持久指导之前，声明：

- 未来行为：代理下次应该如何不同地操作。
- 代表性任务：一个具体的场景，现在应该成功。
- 证据：当前来源、失败输出、用户纠正或聚焦测试。
- 所有者：拥有它的一个技能、指令文件、脚本或运行时组件。
- 写边界：允许更改的文件和必须保持本地化的信息。
- 证明：确认新行为的命令、eval 或审查。

如果任何项目未知，捕获候选并停止验证或应用之前。

## 生命周期

### 1. 捕获信号

优先考虑事实而不是解释。仅记录最小的可重用摘要；不要复制转录、工具输入、凭证、私有路径或客户数据。

使用 `apb init --hooks` 明确启用的 Claude Code 失败钩子可以调用：

```bash
agent-playbook self-improve
```

手动纠正或成功使用显式的摘要和证据标签：

```bash
apb self-improve capture \
  --kind correction \
  --summary "在依赖缓存状态之前验证当前来源" \
  --evidence "focused-test"
```

CLI 在 `~/.agent-playbook/self-improvement/` 下存储截断的事件和去重候选。使用 `AGENT_PLAYBOOK_DATA_DIR` 或 `--data-dir` 覆盖根目录。

### 2. 评估可重用性

仅当所有内容都为真时保留候选：

- 它描述了未来行为，而不仅仅是发生了什么。
- 它的用途超出一个私有任务或存储库。
- 它与当前权威来源不冲突。
- 存在一个狭窄的所有者和现实的验证路径。

使用 `apb behavior inbox` 检查优先级队列。重复的证据增加出现次数；它不会自动增加真实性。使用 `apb behavior owners <candidate-id> --repo .` 获取本地建议，但将每个结果视为审查候选而不是所有权决定。

### 3. 验证

选择可以证伪候选的最小证明，将其编码为可执行工件，并使用 `apb self-improve eval` 运行它。参见 `references/eval-artifact.md` 了解模式和安全性边界。

| 候选 | 最小证明 |
|---|---|
| 提示或工作流规则 | 代表性提示加上评分标准 |
| CLI/运行时行为 | 聚焦自动化测试 |
| 外部集成 | 对当前文档/运行时的实时功能检查 |
| 安全规则 | 显示不安全路径被阻止的负面测试 |
| 重复启发式 | 多个独立事件或明确的人类确认 |

分离事实、假设和缺失的证据。仅结构验证不能证明指导在语义上是当前的或主机可执行的。

### 4. 验证、应用或拒绝

首先运行工件。如果可以安全地重现之前的行为，建议使用基线场景；至少需要一个候选场景：

```bash
apb self-improve eval cand-123 --artifact behavior-eval.json

apb self-improve review cand-123 \
  --decision validate \
  --reason "基线重现且候选场景通过" \
  --eval-result /path/printed/by/the/eval/command.json
```

验证仅接受针对同一候选的通过 CLI 生成的 eval 结果。它不声明运行时行为已改变。

在编辑所有者之前生成本地行为改变提案：

```bash
apb behavior proposal cand-123 \
  --owner "skill:self-improving-agent" \
  --output behavior-proposal.md
```

提案包含行为差异意图、eval 证明、接受标准、隐私边界和回滚计划。它不会编辑所有者或创建远程拉取请求。

更改恰好一个持久所有者后，单独记录应用：

```bash
apb self-improve review cand-123 \
  --decision apply \
  --reason "在聚焦测试通过后安装" \
  --owner "skill:self-improving-agent" \
  --change-ref "commit:abc123"
```

其他决定：

```bash
apb self-improve review cand-123 --decision observe --reason "需要第二个事件"
apb self-improve review cand-123 --decision reject --reason "项目特定例外"
```

应用到最狭窄的所有者：

1. 可执行测试、脚本或验证器，当行为可以被强制执行时。
2. 拥有技能或其引用，当代理判断是必需的时。
3. 项目指令，仅用于项目范围的约束。
4. 知识笔记本，用于应检索而不是始终加载的持久事实。

永远不要在捕获时无声地修改存储库规则、发布软件包或触发外部操作作为副作用。

### 5. 证明循环

应用后运行代表性任务。报告：

- 候选 ID 和最终状态；
- 使用的证据和仍然不确定的内容；
- 持久所有者已更改；
- 可执行 eval 结果和工件哈希；
- 回滚路径。

如果新规则没有改变代表性行为，请还原或拒绝它。

## 知识导出

将已应用规则和开放候选导出为 Markdown，用于 Obsidian 或其他本地知识系统：

```bash
apb self-improve export --output /path/to/vault/Agent/Learning.md
```

导出是一个汇点，不是真相的来源。候选和活动规则状态在 CLI 数据目录中保持结构化和可审计。

## 主机边界

技能描述判断；主机适配器提供事件和操作。在声明支持之前检查当前主机：

- Claude Code：仅由明确的 `apb init --hooks` 安装的确定性失败钩子。
- Codex、Gemini、DeepSeek Harness：技能分发是支持的；学习事件接线取决于每个主机当前的扩展 API。
- 不支持的钩子必须保持手动或适配器特定，永远不要通过未记录的行为模拟。

使用 `apb conformance` 检查本地静态合同。`proven` 分发或钩子配置不能证明主机发现或运行时调用；这些仍然 `unverified`，直到观察到的主机运行提供有界证据。

参见 `references/learning-lifecycle.md` 了解模式和适配器合同。使用 `evals/cases.json` 与 `evals/rubric.md` 在更改此技能时。

## 完成清单

- [ ] 候选/无变化决定是明确的。
- [ ] 存储的文本是最小的、截断的和可移植的。
- [ ] 在相关时检查了当前权威来源。
- [ ] 验证使用针对同一候选的通过可执行 eval 结果。
- [ ] 应用命名一个持久所有者和一个具体的变更引用。
- [ ] 应用后测试了代表性行为。
- [ ] 没有将私有项目细节输入公共技能资产。
