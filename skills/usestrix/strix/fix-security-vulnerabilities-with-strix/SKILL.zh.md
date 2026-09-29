---
name: fix-security-vulnerabilities-with-strix
description: 修复Strix渗透测试（开源CLI或app.strix.ai云端）发现的安全漏洞——按严重程度进行优先级排序，修复根本原因而非症状，并重新运行Strix以证明每个修复确实关闭了漏洞。处理注入、XSS、SSRF、权限控制失效、IDOR以及其他已验证的发现。在Strix扫描报告发现后使用，或当用户要求从strix_runs报告、vulnerabilities.json、findings.sarif或云端扫描中修复、修补或解决安全问题时使用。
---

# 修复 Strix 检测项并验证

将验证过的 Strix 检测项转化为最小化、正确的修复方案——并通过重新扫描来证明其有效性。

## 1. 分类处理

从扫描运行的位置获取检测项：

- **OSS CLI** — 艺术品位于 `strix_runs/<run-name>/`：
  - `vulnerabilities/*.md` — 每个文件包含一个检测项：描述、严重性、PoC 步骤或脚本、受影响代码位置、修复指导。
  - `vulnerabilities.json` — 相同的检测项以 JSON 格式（id、严重性、CWE/CVE，当可用时，`code_locations` 包含 `fix_before`/`fix_after` 建议）。
- **云服务 (app.strix.ai)** — 使用 CLI 拉取检测项：`strix cloud vulns list --scan-id <scan-id> --json`（或 `strix cloud scans get <scan-id> --json | jq '.vulnerabilities'`，或 `strix cloud vulns list --severity critical` 全局）。每个检测项包含 `severity, cwe, endpoint, method, impact, technical_analysis, poc_description, poc_script_code`，对于代码检测项，还有 `code_file`/`code_diff`/`code_before`/`code_after`。修复验证后，使用 `strix cloud vulns update <id> --status fixed` 标记。参考 **使用 Strix 进行管理式渗透测试** 技能获取 `strix cloud login` 和作用域。

按严重性排序工作：关键 → 高 → 中 → 低。每个 Strix 检测项都通过可工作的概念验证进行验证，因此不要在没有自行重新测试 PoC 的情况下将其视为误报而忽略。

## 2. 修复

针对每个检测项：

1. 当可行时，使用检测项文件中的 PoC 重复它。
2. 修复根本原因，而不是特定载荷（参数化每个查询而不是阻塞一个字符串，并在处理器中强制授权而不是隐藏端点）。
3. 优先使用框架的内置防御（ORM 参数化、模板自动转义、CSRF 中间件、集中式授权）而不是临时清理。
4. 保持差异最小，并应用仓库现有的模式。检测项文件通常包含 `fix_before`/`fix_after` 片段——将其作为起点，而不是逐字使用。

常见检测项类别和预期修复：注入 → 在汇点进行参数化/转义；IDOR/权限控制损坏 → 对象级授权检查；SSRF → 允许列表 + 阻止内部范围；XSS → 上下文感知输出编码 + CSP；密钥暴露 → 旋转密钥并从代码/历史中移除；认证问题 → 修复服务器端检查（绝不在客户端）。

## 3. 通过重新运行 Strix 进行验证

修复后，重新扫描限定区域并确认检测项已消失。在扫描的环境（或两个环境）中验证：

**OSS CLI:**
```bash
# 仅重新测试已更改的文件（快速）。解析仓库的实际默认分支，而不是假设 origin/main（许多仓库使用 master/develop）。
# 避免当前分支自己的上游作为基准——其与 HEAD 的合并基将是 HEAD，导致空差异和错误干净的检测结果。
DIFF_BASE=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
# origin/HEAD 可能是一个悬空符号引用——仅在其目标存在时保留它。
git rev-parse --verify --quiet "$DIFF_BASE" >/dev/null 2>&1 || DIFF_BASE=""
if [ -z "$DIFF_BASE" ]; then
  for b in origin/main origin/master origin/develop; do
    git rev-parse --verify --quiet "$b" >/dev/null && DIFF_BASE="$b" && break
  done
fi
# 无静默回退：类似 HEAD~1 的猜测仅覆盖多提交修复分支的最后一个提交。如果无基准解析，提示用户输入基准分支（或使用聚焦的 --instruction 验证，无需差异基准）。
[ -n "$DIFF_BASE" ] || { echo "Set DIFF_BASE to the branch your fix will merge into." >&2; exit 1; }
strix -n -t ./ --scan-mode quick --scope-mode diff --diff-base "$DIFF_BASE" --max-budget 5

# 或使用原始检测项作为焦点重新测试（无需差异基准）
strix -n -t ./ --instruction "Verify the SQL injection in app/api/search.py is fixed. Original PoC: <poc>" --max-budget 5
```
退出代码：`2` = 检测项仍然存在（读取新的 `strix_runs/<run>/vulnerabilities/` 并迭代）；`0` = 干净 **对于分析的内容**。在信任 `0` 之前，确认运行是否被提前终止——检查 `run.json` 是否有完成状态，并比较其 `llm_usage.cost` 与 `--max-budget`：硬预算停止会留下 `status: "stopped"`，但预算警告结束的运行会记录 `"completed"` 并有部分覆盖率。给验证足够的预算以完成，并优先重新运行特定 PoC 作为真实信号。

**云服务：** 使用相同配置重新运行并重新轮询，然后确认检测项不再出现：
```bash
new_id=$(curl -sS "$BASE/scans/$scan_id/rerun" "${auth[@]}" -X POST | jq -r .scan_id)
# poll GET /scans/$new_id 直到完成，然后检查其 vulnerabilities[]
```
或者，如果云扫描来自仓库/PR，在修复分支上触发新的 PR 审查 (`POST /pr-reviews/start`)。平台还直接重新测试单个检测项：`POST /api/v1/vulnerabilities/{vulnerabilityId}/retest`。

- 当 PoC 是简单请求/脚本时，手动重新运行——最快信号。
- 运行项目的测试套件以确保修复不会破坏行为。

## 4. 报告

按检测项总结：严重性、根本原因、已应用的修复（文件:行）、验证结果（重新扫描干净 / PoC 不再重复）。报告中绝不能包含活体密钥；如果密钥泄露，说明需要旋转。
