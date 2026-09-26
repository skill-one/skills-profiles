# Codex Autoresearch

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

Codex Autoresearch 是一个 Codex 技能，它会在你的代码库上运行自主的修改→验证→保留/回滚循环。你用一句话描述一个可衡量的目标；Codex 确认计划，然后进行无人值守的迭代——每一次改进都记录在 git 中，每一次失败都自动回滚——直到被中断或达到上限。该技能受 Karpathy 的 autoresearch 概念启发，从机器学习训练扩展到任何软件指标。

---

## 安装

**选项 A — 手动复制到你的项目中：**

```bash
git clone https://github.com/leo-lilinxiao/codex-autoresearch.git
cp -r codex-autoresearch your-project/.agents/skills/codex-autoresearch
```

**选项 B — Codex 技能安装器：**

```text
$skill-installer install https://github.com/leo-lilinxiao/codex-autoresearch
```

该技能位于你项目中的 `.agents/skills/codex-autoresearch/` 内。首次使用前无需配置文件。

---

## 如何激活

在你的项目目录中打开 Codex，并将你的目标前缀为 `$codex-autoresearch`：

```text
$codex-autoresearch
我想从我的 TypeScript 代码中移除所有 `any` 类型
```

Codex 将：
1. 扫描仓库并推断范围、指标、验证命令和守卫命令。
2. 提供确认摘要——回复 `go`（或修正任何内容）。
3. 无人值守地运行循环，直到你中断它或目标达成。

你永远不会编写配置。Codex 推断所有内容。

---

## 确认流程

循环开始前，Codex 总是会显示它发现的内容并要求你确认。示例交互：

```
Codex: 我在 src/**/*.ts 中发现了 47 个 `any` 出现。

       确认：
       - 目标：在 src/**/*.ts 中消除 `any` 类型
       - 指标：`any` 计数（当前：47），方向：降低
       - 验证：grep + tsc --noEmit 作为守卫

       需要确认：
       - 运行直到全部消失，或迭代次数上限为 N？

       回复 "go" 开始，或告诉我如何更改。

你：   Go, 通宵运行。

Codex: 开始——基线：47。迭代直到中断。
```

最多可能进行五轮确认。之后，Codex 将继续执行。

---

## 循环（内部机制）

```
阶段 0：探测环境（CPU/GPU/RAM/工具链），检查会话恢复
阶段 1：从先前的运行中读取上下文 + 经验文件（如果有的话）

循环（无限次或 N 次）：
  1. 审查当前状态、git 历史、结果日志、经验
  2. 选择一个假设（应用视角，根据环境过滤）
     -- 或如果并行模式激活，选择 N 个假设
  3. 进行一个原子性更改
  4. git commit（在验证之前）
  5. 运行验证命令 → 目标指标是否改善？
     运行守卫命令   → 是否有其他内容崩溃？
  6. 改善 → 保留（提取经验）
     更差    → 批准回滚策略（git revert）
     崩溃  → 修复或跳过
  7. 将结果记录到结果日志
  8. 健康检查（磁盘、git、验证健康）
  9. 如果 3 次以上丢弃 → 细化；5 次以上 → 转向；2 次转向 → 网络搜索
 10. 重复。永不停止。永不提问。
```

循环运行**无限制**，除非你在确认时指定 `Iterations: N`。

---

## 双门验证

两个命令具有不同的目的：

| 门 | 目的 | 失败意味着 |
|------|---------|-------------|
| **验证** | 目标指标是否改善？ | 放弃更改，回滚 |
| **守卫** | 是否有其他内容崩溃？ | 重新修改更改（最多 2 次尝试），然后回滚 |

守卫文件**永远不会**被循环修改。

Python 覆盖运行的示例验证 + 守卫对：

```text
Verify: pytest --cov=src --cov-report=term 2>&1 | grep TOTAL | awk '{print $NF}'
Guard:  python -m mypy src --ignore-missing-imports
```

TypeScript 类型清理的示例：

```text
Verify: grep -r "any" src --include="*.ts" | wc -l
Guard:  npx tsc --noEmit
```

---

## 模式

Codex 会自动将你的句子映射到七种模式之一——你永远不会显式选择模式。

### `loop` — 迭代以实现可衡量的目标（默认）

```text
$codex-autoresearch
将 src/ 的测试覆盖率提高到至少 80%
```

```text
$codex-autoresearch
减少包大小——目前为 2.3 MB，将其降至 1 MB 以下
```

### `plan` — 将模糊目标转换为验证的循环配置

```text
$codex-autoresearch
我想让我们的 API 更快，但不知道从哪里开始
```

Codex 将会向你提问（p95 延迟与吞吐量？哪个端点？），并生成一个可运行的循环配置。

### `fix` — 修复错误直到计数为零

```text
$codex-autoresearch
pytest 失败，重构后 12 个测试损坏——修复它们
```

### `debug` — 基于证据的根因追踪

```text
$codex-autoresearch
我们的 API 在负载下随机返回 503，不知道为什么
```

每次迭代测试一个可证伪的假设。Codex 提供证据，而不是猜测。

### `security` — 只读 STRIDE + OWASP 审计

```text
$codex-autoresearch
这段代码安全吗？
```

### `ship` — 准备状态验证和发布门控

```text
$codex-autoresearch
发布
```

### `exec` — 无循环的单次执行

```text
$codex-autoresearch
运行基准测试套件并总结结果
```

---

## 内联配置（可选）

你可以在确认步骤中内联覆盖默认值——无需编辑文件：

| 短语 | 效果 |
|--------|--------|
| `Iterations: 20` | 将循环限制在 20 次迭代 |
| `Parallel: 3` | 每轮并行测试 3 个假设 |
| `Guard: npm test` | 覆盖推断的守卫命令 |
| `Verify: <command>` | 覆盖推断的验证命令 |
| `Scope: src/api/` | 限制更改到子目录 |

确认步骤中的示例：

```
你：   Go. Iterations: 30, Guard: npm test, Scope: src/api/
```

---

## 跨运行学习

每次迭代结束时，Codex 会将一个结构化经验写入 `.agents/skills/codex-autoresearch/lessons.md`：

```
迭代 7 — 保留
假设：在 src/utils/mapper.ts 中用推断泛型替换显式 `any`
更改：添加 <T extends Record<string, unknown>> 到 mapKeys()
结果：any 计数 31 → 29
经验：工具函数上的泛型约束消除了下游的 `any` 集群。
```

会话恢复时，Codex 首先读取此文件。每次新运行都将受益于先前的运行。

**要恢复中断的运行：**

```text
$codex-autoresearch
恢复
```

Codex 重新读取经验文件，检查 git 状态，重新建立基线，然后继续。

---

## 并行实验

在确认时或任何时间请求并行模式：

```text
你：   Go, 并行 4
```

Codex 并行运行四个假设，保留最佳结果，丢弃其余结果。当假设空间较大时很有用。

---

## 转向协议

如果循环停滞，自动升级会发生：

| 连续丢弃次数 | 操作 |
|---------------------|--------|
| 3 | **细化** — 缩小假设，尝试更小的原子性更改 |
| 5 | **转向** — 完全改变策略 |
| 2 转向 | **网络搜索** — Codex 获取外部参考以摆脱困境 |

升级期间你永远不会被要求许可。循环继续。

---

## 实际代码示例

### 示例 1 — TypeScript `any` 消除（Python 验证脚本）

如果你想要一个自定义验证脚本而不是单行命令：

```python
# scripts/count_any.py
import subprocess, sys

result = subprocess.run(
    ["grep", "-r", "--include=*.ts", r"\bany\b", "src/"],
    capture_output=True, text=True
)
count = len(result.stdout.strip().splitlines())
print(count)
sys.exit(0)  # 总是退出 0；数字是重要的
```

在确认时告诉 Codex：

```text
Verify: python scripts/count_any.py
Guard:  npx tsc --noEmit
```

### 示例 2 — pytest 覆盖率循环（Python）

```python
# scripts/coverage_pct.py
import subprocess, re, sys

out = subprocess.check_output(
    ["pytest", "--cov=src", "--cov-report=term", "-q"],
    stderr=subprocess.STDOUT, text=True
)
match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
if match:
    print(int(match.group(1)))
    sys.exit(0)
print(0)
sys.exit(0)
```

```text
$codex-autoresearch
提高测试覆盖率——目标 85%

Verify: python scripts/coverage_pct.py
Guard:  python -m mypy src
方向：更高
目标：85
迭代次数：50
```

### 示例 3 — 包大小循环（Node.js 项目）

```bash
# scripts/bundle_size.sh
#!/usr/bin/env bash
npm run build --silent 2>/dev/null
du -k dist/bundle.js | awk '{print $1}'
```

```text
$codex-autoresearch
减少我们的 JS 包大小，目前约 2300 KB，目标低于 900 KB

Verify: bash scripts/bundle_size.sh
Guard:  npm test
方向：降低
目标：900
```

### 示例 4 — 语法检查警告计数（任何语言）

```bash
# scripts/lint_count.sh
#!/usr/bin/env bash
npx eslint src/ --format json 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(len(f['messages']) for f in d))"
```

```text
$codex-autoresearch
将我们的 ESLint 警告计数降至零

Verify: bash scripts/lint_count.sh
方向：降低
目标：0
```

---

## 无人值守运行

对于通宵或长时间运行，确保 Codex CLI 批准设置不会中断 `git commit` 或 `git revert` 命令。最简单的选项是在可丢弃或沙盒化的仓库克隆中运行：

```bash
git clone . /tmp/autoresearch-sandbox
cd /tmp/autoresearch-sandbox
# 在这里以完全权限启动 Codex
```

结果累积在 git 历史中。完成时将获胜的提交拉回你的主仓库：

```bash
# 在你的主仓库
git fetch /tmp/autoresearch-sandbox main
git cherry-pick <winning-commit-sha>
```

---

## 会话工件

| 文件 | 内容 |
|------|----------|
| `.agents/skills/codex-autoresearch/lessons.md` | 每次迭代的结构化经验 |
| `.agents/skills/codex-autoresearch/results.log` | 每次迭代的完整日志（指标值、保留/回滚、耗时） |
| `.agents/skills/codex-autoresearch/session.json` | 当前会话状态以用于恢复 |

这些文件跨 Codex 会话持久化。删除它们以重新开始。

---

## 故障排除

**循环每次都回滚更改：**
- 验证命令可能返回非数字值。手动测试它：`bash -c "<你的验证命令>"` 应该打印一个数字。
- 指标方向可能错误。在设置时确认 `Direction: lower` 或 `Direction: higher`。

**守卫触发于无关文件：**
- 缩小范围：`Scope: src/specific-module/`
- 或明确告诉 Codex：在确认时 `Do not touch tests/`。

**会话恢复拾取错误的基线：**
- 删除 `session.json` 以强制重新建立基线：`rm .agents/skills/codex-autoresearch/session.json`

**并行模式产生合并冲突：**
- Codex 通过转向协议内部处理此问题，但如果它卡住，请减少并行性：`Parallel: 2`

**Codex 在循环中途提问：**
- 这意味着守卫崩溃产生了模糊输出。通过指定 `Guard: <command> || true`（如果守卫失败应该是非致命的）或通过给 Codex 更完整的沙盒权限以自由运行 git 命令来提前阻止它。

**循环达到转向但没有任何进展：**
- 在确认时提供种子假设：`Hint: 首先尝试树摇未使用的导入`
- 或运行 `plan` 模式首先生成更丰富的假设列表，然后再切换到 `loop`。

---

## 快速参考

```text
# 启动循环
$codex-autoresearch
<你的目标，一句话>

# 恢复中断的运行
$codex-autoresearch
恢复

# 有界运行
$codex-autoresearch
<目标> — 迭代次数：25

# 并行假设
$codex-autoresearch
<目标> — 并行：4

# 强制模式
$codex-autoresearch fix
pytest 有 8 个失败，修复它们

# 只读审计
$codex-autoresearch security
审计 src/api/ 以查找注入漏洞
```
