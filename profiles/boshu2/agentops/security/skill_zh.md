# 安全技能

> **目的**：在代码、脚本、授权二进制文件和仓库管理的提示表面运行可重复的安全检查。

使用此技能进行调用者请求的仓库扫描、授权二进制文件确认、依赖风险、机密信息或离线提示表面红队演练。

## 关键约束

- 仅扫描操作者拥有或明确授权评估的仓库、二进制文件和提示表面。**原因**：安全审查不授予第三方系统或专有材料的访问权限。
- 默认情况下将收集设置为只读；不要窃取机密信息、执行破坏性有效负载或修改策略/基线以制造绿色。**原因**：评估不能成为事件本身或擦除其证据。
- 将缺失/错误扫描器视为覆盖范围差距，而不是干净的结果；当需要完整的工具覆盖时，使用 `--require-tools`。**原因**：缺乏证据不是证据的缺失。
- 使用当前代理和本地 shell；除非明确请求，否则不要启动另一个运行时或编排子层。**原因**：仓库扫描是受限制的操作，不是扩展权限。
- 运行选定的扫描一次，并报告发现的问题和覆盖范围差距。修复措施、风险接受、重新运行和推广是调用者的决定。

## 提示

```text
在 fleet-router 仓库中运行完整的安全扫描：依赖风险、机密信息和静态分析。保持收集只读，将任何缺失的扫描器视为覆盖范围差距，并报告发现的问题和覆盖范围差距，而不是修复它们。
```

## 正常工作的情况

- 报告列出了运行的扫描器，例如 `gosec ./...`，并标记任何缺失的工具为覆盖范围差距，而不是干净通过。
- 收集在整个过程中保持只读：transcript 中没有出现 `curl`、`rm` 或凭证读取。
- 发现的问题引用了文件和行，例如 `cli/internal/auth/token.go:42`，而不是模糊的类别。
- 响应的 `findings` 和 `coverage gaps` 与任何修复步骤保持分离，留给调用者决定。

## 安全表面

1. **仓库门禁**：`scripts/security-gate.sh` 组合可用的扫描器进行快速/完整/发布检查。
2. **可组合套件**：`scripts/security_suite.py` 提供静态、动态、合同、基线和策略原语，用于授权二进制文件。
3. **离线红队演练**：`scripts/prompt_redteam.py` 检查仓库拥有的提示和工具控制表面，以对抗攻击包。

这是标准的运行手册。套件策略门禁会产生机器可消费的输出，包括在提供策略文件时生成的 `policy/policy-verdict.json`。

在二进制文件、策略、基线或红队演练工作之前，请阅读 [套件运行手册](references/security-suite-runbook.md)。使用 [OWASP 清单](references/owasp-checklist.md) 进行代码级审查。

## 执行工作流

### 1) 快速门禁

运行：

```bash
scripts/security-gate.sh --mode quick
```

**检查点**：保留退出代码，并在分诊之前验证报告的 `security-gate-summary.json` 是否存在并可以解析。

### 2) 完整扫描

运行：

```bash
scripts/security-gate.sh --mode full
```

当跳过的扫描器会使保证声明失效时，添加 `--require-tools`。**检查点**：除非选定的工件验证器和流程都成功，否则报告结果为不完整。

### 3) 定时门禁

定时自动化对目标分支运行完整门禁并保留其工件目录。失败的定时运行会创建可操作的跟踪工作；AgentOps 本身不提供调度器。

### 4) 搜索纪律

对于超出脚本门禁的审查工作（代码级或红队演练），针对完整分类，而不是你的第一印象进行搜索：

- **完整分类搜索**。遍历 [OWASP 清单](references/owasp-checklist.md)（或用于提示表面的攻击包）中每个适用的类别，并记录每个类别的结果：发现、干净或未评估。未访问的类别是覆盖范围差距，而不是干净的。追逐一个可疑线索而排除分类是 **第一气味固定** 失效模式。
- **每个发现的经验证据**。当发现可以重现时，它才是真实的：具体的输入、请求或命令演示了该行为，捕获在工件中。仅模式匹配的发现报告为可疑，排名低于已证明的发现。
- **故障打开探测**。对于表面上的每个保护措施、门禁或超时，询问出错或挂起时会发生什么——然后在安全的地方进行探测。在错误下失败的控制器即使其快乐路径正确也是一个发现。
- **身份链跟踪**。对于认证或委托流程，跟踪在每个跳点（用户、服务、令牌、钩子）上的实际身份是谁。在身份被假设而不是验证的跳点——**借用身份** 失效模式——是一个发现。
- **安静轮次收敛**。迭代完整通过，直到一次完整通过不再产生新内容：没有新发现，没有新的覆盖范围差距。那个安静轮次是停止条件。在发现仍在到达的响亮轮次后停止是过早的；如果预算在安静轮次之前结束，则报告搜索未收敛。

### 5) 分诊

1. 打开最新的工件，识别扫描器、严重性、文件和覆盖范围差距。
2. 使用最安全的窄命令重现发现的问题。
3. 排名具体发现并保留覆盖范围差距。
4. 停止。修复措施、风险接受和任何后续扫描是新的调用者决定。不要仅仅为了通过而降级、抑制或更新基线。

## 输出规范

**工件目录**：仓库门禁将 `${SECURITY_GATE_OUTPUT_DIR:-${TMPDIR:-/tmp}/agentops-security}/<run-id>/` 写入；可组合套件和红队运行使用其明确的 `--out-dir`。

**文件名约定**：仓库门禁需要 `security-gate-summary.json`（以及原始 `summary.json`）；套件运行需要 `suite-summary.json`；红队运行需要 `redteam/redteam-results.json`。

**序列化/模式格式**：`security-gate-summary.json` 是 JSON，具有非空的 `mode`、`run_id`、`output_dir` 和 `gate_status`、数字 `missing_tool_count`、布尔值 `require_tools` 和对象 `toolchain`。

**验证器命令**：使用 `OUT=<security-gate-run-dir>`，运行 `jq -e '(.mode|type)=="string" and (.mode|length)>0 and (.run_id|type)=="string" and (.run_id|length)>0 and (.output_dir|type)=="string" and (.output_dir|length)>0 and .gate_status=="PASS" and (.missing_tool_count|type)=="number" and (.require_tools|type)=="boolean" and (.toolchain|type)=="object"' "$OUT/security-gate-summary.json" >/dev/null`。

**输出**：报告工件路径、命令/退出代码、模式、门禁状态、缺失工具覆盖范围、排名发现和授权边界。不要添加所有者、下一步行动、批准、发布或重试决定。

## 质量清单

- [ ] 目标和授权边界明确；收集保持在其中。
- [ ] 扫描器可用性和跳过/错误覆盖范围在报告中可见。
- [ ] 发现的问题包括严重性、位置、可重现的证据和有界的修复指导。
- [ ] 工件不包含新暴露的机密信息或未脱敏的有效负载。
- [ ] 报告区分通过扫描和推广或发布的权限。
- [ ] 抑制、策略更改、基线和风险接受需要明确判断。
- [ ] 报告在证据后停止，不包含连续决策。

## 验证

运行技能和红队验证器：

```bash
bash skills/security/scripts/validate.sh
bash tests/scripts/test-security-suite-redteam.sh
```

对于有界的套件冒烟测试，使用拥有的二进制文件和临时输出目录，如 [套件运行手册](references/security-suite-runbook.md) 中所示。

## 示例

- 快速安全请求运行仓库门禁一次，并报告覆盖范围和发现的问题。
- 完整安全请求运行完整扫描一次，并保留其工件。
- 授权二进制文件请求可以在明确的临时输出目录中捕获基线。
- 红队请求可以在仓库拥有的表面运行离线攻击包。

## 故障排除

| 问题 | 响应 |
|------|------|
| 扫描器缺失/错误 | 记录覆盖范围差距；在需要时安装它或使用 `--require-tools` 重新运行 |
| 本地/CI 不匹配 | 比较扫描器版本、配置、模式和两个工件目录 |
| 怀疑误报 | 狭窄地重现；记录任何授权抑制及其所有者 |
| 套件/基线失败 | 检查命名的比较/策略工件；不要反射性地刷新基线 |
| 红队演练在措辞更改后失败 | 决定控制器是否回退或攻击包匹配器需要有意修订 |

## 参考文档

- [references/security-suite-runbook.md](references/security-suite-runbook.md) — 二进制文件/策略/基线/红队演练命令和工件
- [references/security.feature](references/security.feature) — 仓库门禁可执行文件规范
- [references/security-suite.feature](references/security-suite.feature) — 可组合套件可执行文件规范
- [references/owasp-checklist.md](references/owasp-checklist.md) — OWASP Top 10 审查
- [references/agentops-redteam-pack.json](references/agentops-redteam-pack.json) — 离线攻击包
- [references/policy-example.json](references/policy-example.json) — 启动策略
