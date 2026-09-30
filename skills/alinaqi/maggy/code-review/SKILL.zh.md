---
name: code-review
description: 通过 /code-review 进行强制代码审查，在提交和部署之前
---

# 代码审查技能

**目的：** 将自动化代码审查作为每次提交和部署前的强制性保护措施。可选择 Claude、OpenAI Codex、Google Gemini 或多个引擎进行全面分析。

**子技能：**
- [adr-gate.md](./adr-gate.md) — 预审查 ADR 和规范执行

---

## 预审查：ADR 门禁（强制）

在任何审查引擎运行之前，ADR 门禁会自动执行：

1. **分类** — 简单变更（拼写错误、依赖项、仅测试）跳过门禁
2. **发现** — 扫描 `docs/adr/`、`_project_specs/`、iCPG ReasonNodes、git 历史记录以查找链接的 ADR 和规范
3. **执行** — 如果非简单变更没有找到 ADR：
   - **交互式**（默认）：从 git 历史记录草拟 ADR，要求用户确认
   - **无值守**（CI）：写入 `Status: proposed`，继续
   - **严格**：阻止审查，直到存在 ADR
4. **注入** — 将发现的 ADR + 规范作为架构上下文输入到审查提示中

### ADR 合规性审查维度

添加到标准的 7 个审查类别：

| 类别 | 检查内容 |
|------|----------|
| **ADR 合规性** | 变更符合记录的决策，没有未记录的架构变更 |

| 发现 | 严重性 |
|------|----------|
| 变更与接受的 ADR 相矛盾 | 关键 |
| 没有在任何 ADR 中记录的架构决策 | 高 |
| 存在 ADR 但已过时/陈旧 | 中 |
| 轻微偏离 ADR 意图 | 低 |

有关完整协议、逆向工程规则和配置，请参阅 [adr-gate.md](./adr-gate.md)。

---

## 审查引擎选择

运行 `/code-review` 时，用户可以选择其首选的审查引擎：

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查 - 选择您的引擎                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ○ Claude (默认)                                               │
│    内置，无需额外设置，完整的对话上下文                         │
│                                                                 │
│  ○ OpenAI Codex CLI                                             │
│    GPT-5.2-Codex 专门用于代码审查，88% 检测率                   │
│    需要：npm install -g @openai/codex                           │
│                                                                 │
│  ○ Google Gemini CLI                                            │
│    Gemini 2.5 Pro 具有 1M 令牌上下文，免费套餐可用               │
│    需要：npm install -g @google/gemini-cli                      │
│                                                                 │
│  ○ 双引擎（任意两个）                                          │
│    运行两个引擎，比较发现结果，捕获更多问题                     │
│                                                                 │
│  ○ 所有三个（最大覆盖范围）                                     │
│    运行 Claude + Codex + Gemini 用于关键/安全代码               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 引擎比较

| 方面 | Claude | Codex | Gemini | 多引擎 |
|------|--------|-------|--------|--------|
| **设置** | 无 | npm + OpenAI API | npm + Google 账户 | 所有设置 |
| **速度** | 快 | 快 | 快 | 2-3 倍时间 |
| **上下文** | 对话 | 每次审查新鲜 | 1M 令牌 | N/A |
| **检测** | 良好 | 88%（最佳） | 63.8% SWE-Bench | 组合 |
| **免费套餐** | 无 | 有限 | 每天 1,000 条 | 变化 |
| **最适合** | 快速审查 | 高精度 | 大型代码库 | 关键代码 |

### 设置默认引擎

```toml
# ~/.claude/settings.toml 或项目 CLAUDE.md
[code-review]
default_engine = "claude"  # 选项：claude, codex, gemini, dual, all
```

### 使用示例

```bash
# 使用默认引擎
/code-review

# 明确选择引擎
/code-review --engine claude
/code-review --engine codex
/code-review --engine gemini

# 双引擎（选择任意两个）
/code-review --engine claude,codex
/code-review --engine claude,gemini
/code-review --engine codex,gemini

# 所有三个引擎
/code-review --engine all

# 快速快捷方式
/code-review              # 使用默认
/code-review --codex      # 使用 Codex
/code-review --gemini     # 使用 Gemini
/code-review --all        # 所有三个引擎
```

---

## 多引擎输出

使用多个引擎时，会比较和去重发现结果：

### 双引擎示例

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查结果 - 双引擎 (Claude + Codex)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 一致（两个都发现）：                                        │
│  🔴 SQL 注入在 auth.ts:45                                      │
│  🟡 缺少错误处理在 api.ts:112                                  │
│                                                                 │
│  🔷 Claude 仅发现：                                            │
│  🟠 潜在的竞争条件在 worker.ts:89                              │
│  🟢 考虑提取辅助函数                                           │
│                                                                 │
│  🔶 Codex 仅发现：                                             │
│  🟠 内存泄漏 - 未关闭的流在 upload.ts:34                       │
│  🟡 N+1 查询模式在 orders.ts:156                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  摘要                                                          │
│  一致：2 | Claude 仅发现：2 | Codex 仅发现：2                     │
│  关键：1 | 高：2 | 中：2 | 低：1                                 │
│  状态：❌ 阻止 - 修复关键/高问题                                │
└─────────────────────────────────────────────────────────────────┘
```

### 三引擎示例（所有三个）

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查结果 - 三引擎                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 无异议（所有三个都发现）：                                    │
│  🔴 SQL 注入在 auth.ts:45                                      │
│                                                                 │
│  ✅ 多数（三个中的两个发现）：                                    │
│  🟠 内存泄漏 - 未关闭的流在 upload.ts:34 (Codex+Gemini)         │
│  🟡 缺少错误处理在 api.ts:112 (Claude+Codex)                    │
│                                                                 │
│  🔷 Claude 仅发现：                                            │
│  🟠 潜在的竞争条件在 worker.ts:89                              │
│                                                                 │
│  🔶 Codex 仅发现：                                             │
│  🟡 N+1 查询模式在 orders.ts:156                                │
│                                                                 │
│  🟢 Gemini 仅发现：                                            │
│  🟡 考虑使用批量 API 以获得更好的性能                           │
│  🟢 类型可以在 types.ts:23 中更具体                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  摘要                                                          │
│  无异议：1 | 多数：2 | 单独：5                                     │
│  关键：1 | 高：2 | 中：3 | 低：2                                 │
│  状态：❌ 阻止 - 修复关键/高问题                                │
└─────────────────────────────────────────────────────────────────┘
```

### 何时使用每种模式

| 模式 | 何时使用 |
|------|----------|
| **单引擎（Claude）** | 快速流内审查，探索 |
| **单引擎（Codex）** | CI/CD 自动化，需要高精度 |
| **单引擎（Gemini）** | 大型代码库（100+ 文件），免费套餐 |
| **双引擎** | 重要 PR，合并前审查 |
| **三引擎（所有）** | 安全关键代码，支付系统，认证 |

---

## 核心理念

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查是不可协商的                                      │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  每次提交都必须通过代码审查。                              │
│  每个 PR 在合并前都必须审查。                              │
│  每次部署都必须包含审查签字。                              │
│                                                                 │
│  AI 捕获人类遗漏的，人类捕获 AI 遗漏的。                    │
│  一起：更少的错误，更干净的代码，更好的安全性。             │
├─────────────────────────────────────────────────────────────────┤
│  调用：/code-review                                           │
│  插件：code-review@claude-plugins-official                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 何时运行代码审查

### 强制审查点

| 触发器 | 操作 | 命令 |
|------|------|------|
| **提交前** | 审查暂存变更 | `/code-review` |
| **PR 前** | 审查相对于基准的所有变更 | `/code-review` |
| **合并前** | PR 的最终审查 | `/code-review` |
| **部署前** | 审查部署差异 | `/code-review` |

### 自动集成

**在每次提交前自动运行代码审查：**

```
┌─────────────────────────────────────────────────────────────────┐
│  提交工作流                                                │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. 编写代码                                                  │
│  2. 运行测试 (TDD - 必须通过)                                 │
│  3. 运行 /code-review  ← 强制                                  │
│  4. 修复关键/高问题                                          │
│  5. 提交                                                      │
│  6. 推送                                                        │
│                                                                 │
│  跳过步骤 3？ ❌ 不允许提交                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 使用代码审查插件

### 基本用法

```bash
# 审查当前变更
/code-review

# 审查特定文件
/code-review src/auth/*.ts

# 审查 PR
/code-review --pr 123

# 带有特定关注点的审查
/code-review --focus security
/code-review --focus performance
/code-review --focus architecture
```

### 审查类别

代码审查插件分析：

| 类别 | 检查内容 |
|------|----------|
| **安全** | 漏洞，注入风险，认证问题，密钥 |
| **性能** | N+1 查询，内存泄漏，低效算法 |
| **架构** | 设计模式，SOLID 原则，耦合 |
| **代码质量** | 可读性，复杂度，重复 |
| **最佳实践** | 语言习惯，框架约定 |
| **测试** | 覆盖率差距，测试质量，边缘情况 |
| **文档** | 缺少文档，过时的注释 |

### 严重性级别

| 级别 | 需要的操作 | 是否可以提交 |
|------|------------|-------------|
| 🔴 **关键** | 必须立即修复 | ❌ NO |
| 🟠 **高** | 提交前应修复 | ❌ NO |
| 🟡 **中** | 尽快修复，可以提交 | ✅ YES |
| 🟢 **低** | 最好有 | ✅ YES |
| ℹ️ **信息** | 仅建议 | ✅ YES |

---

## 提交前钩子集成

### 安装提交前钩子

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 运行代码审查..."

# 在暂存文件上运行 Claude 代码审查
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx|py|go|rs)$')

if [ -n "$STAGED_FILES" ]; then
    # 调用代码审查（需要 claude CLI）
    claude --print "/code-review $STAGED_FILES" > /tmp/code-review-result.txt 2>&1

    # 检查关键/高问题
    if grep -q "🔴\|关键\|🟠\|高" /tmp/code-review-result.txt; then
        echo "❌ 代码审查发现关键/高问题:"
        cat /tmp/code-review-result.txt
        echo ""
        echo "修复这些问题后再提交。"
        exit 1
    fi

    echo "✅ 代码审查通过"
fi

exit 0
```

### 使钩子可执行

```bash
chmod +x .git/hooks/pre-commit
```

---

## Codex CLI 设置（用于 Codex/双模式）

如果您想使用 Codex 或双模式，请安装 Codex CLI：

```bash
# 前提条件：Node.js 22+
node --version  # 必须是 22+

# 安装 Codex CLI
npm install -g @openai/codex

# 认证（选择一个）：
# 选项 1：ChatGPT 订阅（Plus、Pro、Team、Enterprise）
codex  # 按提示登录

# 选项 2：API 密钥
export OPENAI_API_KEY=sk-proj-...
```

### 验证安装

```bash
# 检查 Codex 是否安装
codex --version

# 测试审查
codex
> /review
```

有关 Codex 的完整文档，请参阅 `codex-review.md` 技能。

---

## Gemini CLI 设置（用于 Gemini/多引擎模式）

如果您想使用 Gemini 或多引擎模式，请安装 Gemini CLI：

```bash
# 前提条件：Node.js 20+
node --version  # 必须是 20+

# 安装 Gemini CLI
npm install -g @google/gemini-cli

# 或通过 Homebrew（macOS）
brew install gemini-cli

# 安装代码审查扩展
gemini extensions install https://github.com/gemini-cli-extensions/code-review
```

### 认证

```bash
# 选项 1：Google 账户（推荐，每天 1000 个请求免费）
gemini  # 按浏览器登录提示操作

# 选项 2：API 密钥（每天 100 个请求免费）
export GEMINI_API_KEY="your-key-from-aistudio.google.com"
```

### 验证安装

```bash
# 检查 Gemini 是否安装
gemini --version

# 列出扩展
gemini extensions list

# 测试审查
gemini
> /code-review
```

有关 Gemini 的完整文档，请参阅 `gemini-review.md` 技能。

---

## CI/CD 集成

### GitHub Actions - 仅 Claude

```yaml
# .github/workflows/code-review.yml
name: 代码审查

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 获取变更文件
        id: changed-files
        run: |
          echo "files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | tr '\n' ' ')" >> $GITHUB_OUTPUT

      - name: 运行 Claude 代码审查
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npx @anthropic-ai/claude-code --print "/code-review ${{ steps.changed-files.outputs.files }}" > review.md

      - name: 发布审查评论
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## 🔍 Claude 代码审查\n\n${review}`
            });

      - name: 检查关键问题
        run: |
          if grep -q "关键\|🔴" review.md; then
            echo "❌ 发现关键问题"
            exit 1
          fi
```

### GitHub Actions - 仅 Codex

```yaml
# .github/workflows/codex-review.yml
name: Codex 代码审查

on:
  pull_request:

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Codex 审查
        uses: openai/codex-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          model: gpt-5.2-codex
          safety_strategy: drop-sudo
```

### GitHub Actions - Both Engines

```yaml
# .github/workflows/dual-review.yml
name: Dual Code Review

on:
  pull_request:

jobs:
  claude-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Claude Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npx @anthropic-ai/claude-code --print "/code-review" > claude-review.md

      - uses: actions/upload-artifact@v4
        with:
          name: claude-review
          path: claude-review.md

  codex-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Codex
        run: npm install -g @openai/codex

      - name: Codex Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codex exec --full-auto --sandbox read-only \
            --output-last-message codex-review.md \
            "Review this code for bugs, security issues, and quality problems"

      - uses: actions/upload-artifact@v4
        with:
          name: codex-review
          path: codex-review.md

  combine-reviews:
    needs: [claude-review, codex-review]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4

      - name: Combine Reviews
        run: |
          echo "## 🔍 Dual Code Review Results" > combined-review.md
          echo "" >> combined-review.md
          echo "### Claude Findings" >> combined-review.md
          cat claude-review/claude-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "### Codex Findings" >> combined-review.md
          cat codex-review/codex-review.md >> combined-review.md

      - name: Post Combined Review
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('combined-review.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: review
            });
```

### GitHub Actions - Gemini Only

```yaml
# .github/workflows/gemini-review.yml
name: Gemini Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Gemini CLI
        run: npm install -g @google/gemini-cli

      - name: Run Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          # Get diff
          git diff origin/${{ github.base_ref }}...HEAD > diff.txt

          # Run Gemini review
          gemini -p "Review this pull request diff for bugs, security issues, and code quality problems. Be specific about file names and line numbers.

          $(cat diff.txt)" > review.md

      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## 🤖 Gemini Code Review\n\n${review}`
            });

      - name: Check for Critical Issues
        run: |
          if grep -qi "critical\|security vulnerability\|injection" review.md; then
            echo "❌ Critical issues found"
            exit 1
          fi
```

### GitHub Actions - All Three Engines

```yaml
# .github/workflows/triple-review.yml
name: Triple Engine Code Review

on:
  pull_request:

jobs:
  claude-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Claude Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npx @anthropic-ai/claude-code --print "/code-review" > claude-review.md

      - uses: actions/upload-artifact@v4
        with:
          name: claude-review
          path: claude-review.md

  codex-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Codex
        run: npm install -g @openai/codex

      - name: Codex Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codex exec --full-auto --sandbox read-only \
            --output-last-message codex-review.md \
            "Review this code for bugs, security issues, and quality problems"

      - uses: actions/upload-artifact@v4
        with:
          name: codex-review
          path: codex-review.md

  gemini-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Gemini CLI
        run: npm install -g @google/gemini-cli

      - name: Gemini Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          git diff origin/${{ github.base_ref }}...HEAD > diff.txt
          gemini -p "Review this code diff for bugs, security, and quality issues:
          $(cat diff.txt)" > gemini-review.md

      - uses: actions/upload-artifact@v4
        with:
          name: gemini-review
          path: gemini-review.md

  combine-reviews:
    needs: [claude-review, codex-review, gemini-review]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4

      - name: Combine Reviews
        run: |
          echo "## 🔍 Triple Engine Code Review Results" > combined-review.md
          echo "" >> combined-review.md
          echo "### 🟣 Claude Findings" >> combined-review.md
          cat claude-review/claude-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🟢 Codex Findings" >> combined-review.md
          cat codex-review/codex-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🔵 Gemini Findings" >> combined-review.md
          cat gemini-review/gemini-review.md >> combined-review.md

      - name: Post Combined Review
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('combined-review.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: review
            });

      - name: Check Critical Issues
        run: |
          # Fail if any engine found critical issues
          if grep -qi "critical\|🔴" combined-review.md; then
            echo "❌ Critical issues found by at least one engine"
            exit 1
          fi
```

---

## Review Checklist

### Before Every Commit

- [ ] Run `/code-review` on staged changes
- [ ] No critical (🔴) issues
- [ ] No high (🟠) issues
- [ ] Security concerns addressed
- [ ] Performance issues considered

### Before Every PR

- [ ] Full code review of all changes
- [ ] All critical/high issues resolved
- [ ] Tests added for new functionality
- [ ] Documentation updated if needed

### Before Every Deployment

- [ ] Final review of deployment diff
- [ ] Security scan passed
- [ ] No new vulnerabilities introduced
- [ ] Rollback plan documented

---

## Common Review Findings

### Security Issues (Always Fix)

| Issue | Example | Fix |
|-------|---------|-----|
| SQL Injection | `query = f"SELECT * FROM users WHERE id = {id}"` | Use parameterized queries |
| XSS | `innerHTML = userInput` | Sanitize or use textContent |
| Secrets in code | `apiKey = "sk-xxx"` | Use environment variables |
| Missing auth | Unprotected endpoints | Add authentication middleware |
| Insecure crypto | MD5/SHA1 for passwords | Use bcrypt/argon2 |

### Performance Issues (Should Fix)

| Issue | Example | Fix |
|-------|---------|-----|
| N+1 queries | Loop with individual queries | Use batch/eager loading |
| Memory leak | Unclosed connections | Use connection pooling |
| Missing index | Slow queries | Add database indexes |
| Large payload | Fetching unused fields | Select only needed fields |
| No pagination | Loading all records | Implement pagination |

### Code Quality (Nice to Fix)

| Issue | Example | Fix |
|-------|---------|-----|
| Long function | 100+ lines | Extract into smaller functions |
| Deep nesting | 5+ levels | Early returns, extract methods |
| Magic numbers | `if (status === 3)` | Use named constants |
| Duplicate code | Copy-pasted blocks | Extract shared function |
| Missing types | `any` everywhere | Add proper TypeScript types |

---

## Post-Review: Decision Extraction

After review completes, extract architectural decisions automatically:

1. If review flagged new architectural choices → prompt to create ADR in `docs/adr/`
2. If review approved a new pattern → log to `_project_specs/session/decisions.md`
3. If review found ADR drift → flag the ADR for update or supersede

```markdown
### Auto-Log Entry (decisions.md)
- [YYYY-MM-DD] **[Review Finding]**: Brief description
  - Source: Code review of [PR/commit]
  - ADR: Created/Updated ADR-NNNN
  - Impact: What changed
```

---

## Integration with TDD Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  TDD + CODE REVIEW WORKFLOW                                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. RED: Write failing tests                                    │
│  2. GREEN: Write code to pass tests                             │
│  3. REFACTOR: Clean up code                                     │
│  4. REVIEW: Run /code-review  ← NEW STEP                        │
│  5. FIX: Address critical/high issues                           │
│  6. VALIDATE: Lint + TypeCheck + Coverage                       │
│  7. COMMIT: Only after review passes                            │
│                                                                 │
│  Review catches what tests miss:                                │
│  - Security vulnerabilities                                     │
│  - Performance issues                                           │
│  - Architecture problems                                        │
│  - Code maintainability                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Review Response Template

When code review finds issues, respond with:

```markdown
## Code Review Results

### 🔴 Critical Issues (Must Fix)
1. **SQL Injection in userController.ts:45**
   - Issue: User input directly interpolated into query
   - Fix: Use parameterized query
   - Code: `db.query('SELECT * FROM users WHERE id = $1', [userId])`

### 🟠 High Issues (Should Fix)
1. **Missing authentication on /api/admin endpoints**
   - Issue: Admin routes accessible without auth
   - Fix: Add auth middleware

### 🟡 Medium Issues (Fix Soon)
1. **N+1 query in getOrders function**
   - Consider eager loading or batch query

### 🟢 Low Issues (Nice to Have)
1. **Consider extracting validation logic to separate file**

### ✅ Strengths
- Good test coverage
- Clear function names
- Proper error handling

### 📊 Summary
- Critical: 1 | High: 1 | Medium: 1 | Low: 1
- **Status: ❌ BLOCKED** - Fix critical/high issues before commit
```

---

## Claude Instructions

### When to Invoke Code Review

Claude should automatically suggest or run code review:

1. **After completing a feature** → "Let me run a code review before we commit"
2. **Before creating a PR** → "Running code review on all changes"
3. **When user says "commit"** → "First, let me review the changes"
4. **After fixing bugs** → "Reviewing the fix for any issues"

### Review Focus Areas

Prioritize review based on change type:

| Change Type | Focus Areas |
|-------------|-------------|
| Auth/Security code | Security, input validation, crypto |
| Database code | SQL injection, N+1, transactions |
| API endpoints | Auth, rate limiting, validation |
| Frontend code | XSS, state management, performance |
| Infrastructure | Secrets, permissions, logging |

---

## Quick Reference

### Commands

```bash
# Basic review
/code-review

# Review specific files
/code-review src/auth.ts src/users.ts

# Review with focus
/code-review --focus security

# Review PR
/code-review --pr 123
```

### Severity Actions

```
🔴 Critical → STOP. Fix now. No commit.
🟠 High     → STOP. Fix now. No commit.
🟡 Medium   → Note it. Fix soon. Can commit.
🟢 Low      → Optional. Nice to have.
ℹ️ Info     → FYI only.
```

### Workflow

```
Code → Test → Review → Fix → Commit → Push → PR → Review → Merge → Deploy
              ↑                              ↑                    ↑
           /code-review                /code-review          /code-review
```
