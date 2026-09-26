# 代码审查技能

**目的：** 将自动化代码审查作为每次提交和部署前的强制性保护措施。在Claude、OpenAI Codex、Google Gemini或多个引擎之间选择，以进行全面分析。

**子技能：**
- [adr-gate.md](./adr-gate.md) — 预审查ADR和规范执行

---

## 预审查：ADR门（强制性）

在任何审查引擎运行之前，ADR门会自动执行：

1. **分类** — 简单更改（拼写错误、依赖项、仅测试）跳过门
2. **发现** — 扫描 `docs/adr/`、`_project_specs/`、iCPG ReasonNodes、git历史记录以查找链接的ADR和规范
3. **执行** — 如果非简单更改没有找到ADR：
   - **交互式**（默认）：从git历史记录草拟ADR，要求用户确认
   - **非交互式**（CI）：写入 `Status: proposed`，继续
   - **严格**：阻止审查，直到存在ADR
4. **注入** — 将发现的ADR + 规范作为架构上下文输入审查提示

### ADR合规性审查维度

添加到标准的7个审查类别：

| 类别 | 检查内容 |
|------|----------|
| **ADR合规性** | 更改符合记录的决策，没有未记录的架构变更 |

| 发现 | 严重性 |
|------|----------|
| 更改与接受的ADR矛盾 | 关键 |
| 架构决策不在任何ADR中 | 高 |
| ADR存在但已过时/陈旧 | 中 |
| 轻微偏离ADR意图 | 低 |

有关完整协议、逆向工程规则和配置，请参阅 [adr-gate.md](./adr-gate.md)。

---

## 审查引擎选择

运行 `/code-review` 时，用户可以选择他们喜欢的审查引擎：

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查 - 选择您的引擎                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ○ Claude（默认）                                             │
│    内置，无需额外设置，完整的对话上下文                      │
│                                                                 │
│  ○ OpenAI Codex CLI                                             │
│    专为代码审查的GPT-5.2-Codex，检测率88%                     │
│    需要：npm install -g @openai/codex                         │
│                                                                 │
│  ○ Google Gemini CLI                                            │
│    Gemini 2.5 Pro具有1M令牌上下文，免费套餐可用                │
│    需要：npm install -g @google/gemini-cli                  │
│                                                                 │
│  ○ 双引擎（任意两个）                                        │
│    运行两个引擎，比较结果，捕获更多问题                       │
│                                                                 │
│  ○ 所有三个（最大覆盖范围）                                 │
│    运行Claude + Codex + Gemini用于关键/安全代码               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 引擎比较

| 方面 | Claude | Codex | Gemini | 多引擎 |
|------|--------|-------|--------|--------|
| **设置** | 无 | npm + OpenAI API | npm + Google账户 | 所有设置 |
| **速度** | 快 | 快 | 快 | 2-3倍时间 |
| **上下文** | 对话 | 每次审查新鲜 | 1M令牌 | 无 |
| **检测** | 良好 | 88%（最佳） | 63.8% SWE-Bench | 组合 |
| **免费套餐** | 无 | 有限 | 每天1,000次 | 变化 |
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
/code-review --codex      # 使用Codex
/code-review --gemini     # 使用Gemini
/code-review --all        # 所有三个引擎
```

---

## 多引擎输出

使用多个引擎时，会进行比较和去重：

### 双引擎示例

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查结果 - 双引擎 (Claude + Codex)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 一致（两个都发现）：                                         │
│  🔴 SQL注入在auth.ts:45                                        │
│  🟡 缺少错误处理在api.ts:112                                    │
│                                                                 │
│  🔷 Claude仅：                                                │
│  🟠 潜在的竞态条件在worker.ts:89                                │
│  🟢 考虑提取辅助函数                                           │
│                                                                 │
│  🔶 Codex仅：                                                 │
│  🟠 内存泄漏 - 未关闭的流在upload.ts:34                        │
│  🟡 N+1查询模式在orders.ts:156                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  摘要                                                        │
│  一致：2 | Claude仅：2 | Codex仅：2                     │
│  关键：1 | 高：2 | 中：2 | 低：1                     │
│  状态：❌ 阻止 - 修复关键/高问题                                │
└─────────────────────────────────────────────────────────────────┘
```

### 三引擎示例（所有三个）

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查结果 - 三引擎                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ 一致（所有三个都发现）：                                    │
│  🔴 SQL注入在auth.ts:45                                        │
│                                                                 │
│  ✅ 多数（三个中的两个发现）：                                    │
│  🟠 内存泄漏 - 未关闭的流在upload.ts:34 (Codex+Gemini)         │
│  🟡 缺少错误处理在api.ts:112 (Claude+Codex)                     │
│                                                                 │
│  🔷 Claude仅：                                                │
│  🟠 潜在的竞态条件在worker.ts:89                                │
│                                                                 │
│  🔶 Codex仅：                                                 │
│  🟡 N+1查询模式在orders.ts:156                                  │
│                                                                 │
│  🟢 Gemini仅：                                                │
│  🟡 考虑使用批量API以获得更好的性能                           │
│  🟢 类型可以在types.ts:23中更具体                             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  摘要                                                        │
│  一致：1 | 多数：2 | 单独：5                         │
│  关键：1 | 高：2 | 中：3 | 低：2                     │
│  状态：❌ 阻止 - 修复关键/高问题                                │
└─────────────────────────────────────────────────────────────────┘
```

### 何时使用每种模式

| 模式 | 何时使用 |
|------|----------|
| **单引擎（Claude）** | 流中快速审查、探索 |
| **单引擎（Codex）** | CI/CD自动化，需要高精度 |
| **单引擎（Gemini）** | 大型代码库（100+文件），免费套餐 |
| **双引擎** | 重要PR，合并前审查 |
| **三引擎（所有）** | 安全关键代码，支付系统，认证 |

---

## 核心理念

```
┌─────────────────────────────────────────────────────────────────┐
│  代码审查是不可协商的                                      │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  每次提交都必须通过代码审查。                              │
│  每个PR在合并前都必须经过审查。                            │
│  每次部署都必须包括审查确认。                             │
│                                                                 │
│  AI捕获人类遗漏的内容。人类捕获AI遗漏的内容。              │
│  一起：更少的错误，更干净的代码，更好的安全性。           │
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
| **提交前** | 审查暂存更改 | `/code-review` |
| **PR前** | 审查相对于基线的所有更改 | `/code-review` |
| **合并前** | PR的最终审查 | `/code-review` |
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
│  3. 运行 /code-review  ← 强制性                                  │
│  4. 解决关键/高问题                                          │
│  5. 提交                                                      │
│  6. 推送                                                        │
│                                                                 │
│  跳过步骤3？ ❌ 不允许提交                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 使用代码审查插件

### 基本用法

```bash
# 审查当前更改
/code-review

# 审查特定文件
/code-review src/auth/*.ts

# 审查PR
/code-review --pr 123

# 审查特定关注点
/code-review --focus security
/code-review --focus performance
/code-review --focus architecture
```

### 审查类别

代码审查插件分析：

| 类别 | 检查内容 |
|------|----------|
| **安全** | 漏洞，注入风险，认证问题，密钥 |
| **性能** | N+1查询，内存泄漏，低效算法 |
| **架构** | 设计模式，SOLID原则，耦合 |
| **代码质量** | 可读性，复杂性，重复 |
| **最佳实践** | 语言惯用，框架约定 |
| **测试** | 覆盖率差距，测试质量，边缘情况 |
| **文档** | 缺少文档，过时的注释 |

### 严重性级别

| 级别 | 需要的操作 | 是否可以提交 |
|------|------------|-------------|
| 🔴 **关键** | 立即修复 | ❌ NO |
| 🟠 **高** | 提交前修复 | ❌ NO |
| 🟡 **中** | 尽快修复，可以提交 | ✅ YES |
| 🟢 **低** | 可选 | ✅ YES |
| ℹ️ **信息** | 仅建议 | ✅ YES |

---

## 提交前钩子集成

### 安装提交前钩子

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 运行代码审查..."

# 在暂存文件上运行Claude代码审查
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx|py|go|rs)$')

if [ -n "$STAGED_FILES" ]; then
    # 调用代码审查（需要claude CLI）
    claude --print "/code-review $STAGED_FILES" > /tmp/code-review-result.txt 2>&1

    # 检查是否存在关键/高问题
    if grep -q "🔴\|Critical\|🟠\|High" /tmp/code-review-result.txt; then
        echo "❌ 代码审查发现关键/高问题:"
        cat /tmp/code-review-result.txt
        echo ""
        echo "在提交前修复这些问题。"
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

## Codex CLI设置（用于Codex/双模式）

如果您想使用Codex或双模式，请安装Codex CLI：

```bash
# 前提条件：Node.js 22+
node --version  # 必须是22+

# 安装Codex CLI
npm install -g @openai/codex

# 认证（选择一个）：
# 选项1：ChatGPT订阅（Plus, Pro, Team, Enterprise）
codex  # 按提示登录

# 选项2：API密钥
export OPENAI_API_KEY=sk-proj-...
```

### 验证安装

```bash
# 检查Codex是否安装
codex --version

# 测试审查
codex
> /review
```

有关Codex的完整文档，请参阅 `codex-review.md` 技能。

---

## Gemini CLI设置（用于Gemini/多引擎模式）

如果您想使用Gemini或多引擎模式，请安装Gemini CLI：

```bash
# 前提条件：Node.js 20+
node --version  # 必须是20+

# 安装Gemini CLI
npm install -g @google/gemini-cli

# 或通过Homebrew（macOS）
brew install gemini-cli

# 安装代码审查扩展
gemini extensions install https://github.com/gemini-cli-extensions/code-review
```

### 认证

```bash
# 选项1：Google账户（推荐，每天1000次请求免费）
gemini  # 按提示登录浏览器

# 选项2：API密钥（每天100次请求免费）
export GEMINI_API_KEY="your-key-from-aistudio.google.com"
```

### 验证安装

```bash
# 检查Gemini是否安装
gemini --version

# 列出扩展
gemini extensions list

# 测试审查
gemini
> /code-review
```

有关Gemini的完整文档，请参阅 `gemini-review.md` 技能。

---

## CI/CD集成

### GitHub Actions - Claude仅

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

      - name: 获取更改的文件
        id: changed-files
        run: |
          echo "files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | tr '\n' ' ')" >> $GITHUB_OUTPUT

      - name: 运行Claude代码审查
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
              body: `## 🔍 Claude代码审查\n\n${review}`
            });

      - name: 检查关键问题
        run: |
          if grep -q "Critical\|🔴" review.md; then
            echo "❌ 发现关键问题"
            exit 1
          fi
```

### GitHub Actions - Codex仅

```yaml
# .github/workflows/codex-review.yml
name: Codex代码审查

on:
  pull_request:

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Codex Review
        uses: openai/codex-action@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          model: gpt-5.2-codex
          safety_strategy: drop-sudo
```

### GitHub Actions - 双引擎

```yaml
# .github/workflows/dual-review.yml
name: 双引擎代码审查

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

      - name: 安装Codex
        run: npm install -g @openai/codex

      - name: Codex Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codex exec --full-auto --sandbox read-only \
            --output-last-message codex-review.md \
            "Review this code for bugs, security, and quality issues:
          $(cat diff.txt)" > review.md

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
          echo "## 🔍 双引擎代码审查结果" > combined-review.md
          echo "" >> combined-review.md
          echo "### 🟣 Claude发现" >> combined-review.md
          cat claude-review/claude-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🟢 Codex发现" >> combined-review.md
          cat codex-review/codex-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🔵 Gemini发现" >> combined-review.md
          cat gemini-review/gemini-review.md >> combined-review.md

      - name: 发布组合审查
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

      - name: 检查关键问题
        run: |
          # 如果任何引擎发现关键问题，则失败
          if grep -qi "critical\|🔴" combined-review.md; then
            echo "❌ 至少有一个引擎发现关键问题"
            exit 1
          fi
```

### GitHub Actions - Gemini仅

```yaml
# .github/workflows/gemini-review.yml
name: Gemini代码审查

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

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: 安装Gemini CLI
        run: npm install -g @google/gemini-cli

      - name: Gemini Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          # 获取差异
          git diff origin/${{ github.base_ref }}...HEAD > diff.txt
          gemini -p "Review this code diff for bugs, security, and quality issues:
          $(cat diff.txt)" > review.md

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
              body: `## 🤖 Gemini代码审查\n\n${review}`
            });

      - name: 检查关键问题
        run: |
          if grep -qi "critical\|security vulnerability\|injection" review.md; then
            echo "❌ 发现关键问题"
            exit 1
          fi
```

### GitHub Actions - 所有三个引擎

```yaml
# .github/workflows/triple-review.yml
name: 三引擎代码审查

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

      - name: 安装Codex
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

      - name: 安装Gemini CLI
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
          echo "## 🔍 三引擎代码审查结果" > combined-review.md
          echo "" >> combined-review.md
          echo "### 🟣 Claude发现" >> combined-review.md
          cat claude-review/claude-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🟢 Codex发现" >> combined-review.md
          cat codex-review/codex-review.md >> combined-review.md
          echo "" >> combined-review.md
          echo "---" >> combined-review.md
          echo "### 🔵 Gemini发现" >> combined-review.md
          cat gemini-review/gemini-review.md >> combined-review.md

      - name: 发布组合审查
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

      - name: 检查关键问题
        run: |
          # 如果任何引擎发现关键问题，则失败
          if grep -qi "critical\|🔴" combined-review.md; then
            echo "❌ 至少有一个引擎发现关键问题"
            exit 1
          fi
```

---

## 审查清单

### 每次提交前

- [ ] 运行 `/code-review` 在暂存更改上
- [ ] 无关键（🔴）问题
- [ ] 无高（🟠）问题
- [ ] 安全问题已解决
- [ ] 性能问题已考虑

### 每次PR前

- [ ] 审查所有更改相对于基线的代码
- [ ] 所有关键/高问题已解决
- [ ] 添加新功能的测试
- [ ] 如有需要，更新文档

### 每次部署前

- [ ] 最终审查部署差异
- [ ] 安全扫描通过
- [ ] 未引入新漏洞
- [ ] 文档化回滚计划

---

## 常见审查发现

### 安全问题（必须修复）

| 问题 | 示例 | 修复 |
|------|------|------|
| SQL注入 | `query = f"SELECT * FROM users WHERE id = {id}"` | 使用参数化查询 |
| XSS | `innerHTML = userInput` | 使用textContent |
| 密钥在代码中 | `apiKey = "sk-xxx"` | 使用环境变量 |
| 缺少认证 | 未保护的端点 | 添加认证中间件 |
| 不安全的加密 | 使用MD5/SHA1用于密码 | 使用bcrypt/argon2 |

### 性能问题（应该修复）

| 问题 | 示例 | 修复 |
|------|------|------|
| N+1查询 | 循环中的单独查询 | 使用批量/急加载 |
| 内存泄漏 | 未关闭的连接 | 使用连接池 |
| 缺少索引 | 慢查询 | 添加数据库索引 |
| 大负载 | 加载未使用的字段 | 选择仅需要的字段 |
| 无分页 | 加载所有记录 | 实现分页 |

### 代码质量（可选修复）

| 问题 | 示例 | 修复 |
|------|------|------|
| 长函数 | 100+行 | 提取到较小的函数 |
| 深层嵌套 | 5+层 | 使用早期返回，提取方法 |
| 魔术数字 | `if (status === 3)` | 使用命名常量 |
| 重复代码 | 复制粘贴的块 | 提取共享函数 |
| 缺少类型 | `any`到处 | 添加正确的TypeScript类型 |

---

## 审查后：决策提取

审查完成后，自动提取架构决策：

1. 如果审查标记了新的架构决策 → 提示创建ADR在 `docs/adr/`
2. 如果审查批准了新模式 → 记录到 `_project_specs/session/decisions.md`
3. 如果审查发现ADR偏离 → 标记ADR需要更新或取代

```markdown
### 自动记录条目 (decisions.md)
- [YYYY-MM-DD] **[审查发现]**: 简要描述
  - 来源：代码审查 [PR/提交]
  - ADR：创建/更新ADR-NNNN
  - 影响：发生了什么
```

---

## 与TDD工作流的集成

```
┌─────────────────────────────────────────────────────────────────┐
│  TDD + 代码审查工作流                                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  1. 红色：编写失败的测试                                    │
│  2. 绿色：编写通过测试的代码                                 │
│  3. 重构：清理代码                                        │
│  4. 审查：运行 /code-review  ← 新步骤                        │
│  5. 修复：解决关键/高问题                                  │
│  6. 验证：Lint + TypeCheck + 覆盖率                         │
│  7. 提交：只有在审查通过后才能提交                            │
│                                                                 │
│  审查捕获测试遗漏的内容：                                    │
│  - 安全漏洞                                              │
│  - 性能问题                                              │
│  - 架构问题                                              │
│  - 代码可维护性                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 审查响应模板

当代码审查发现问题时，使用以下内容进行响应：

```markdown
## 代码审查结果

### 🔴 关键问题 (必须修复)
1. **auth.ts:45中的SQL注入**
   - 问题：用户输入直接插入到查询中
   - 修复：使用参数化查询
   - 代码：`db.query('SELECT * FROM users WHERE id = $1', [userId])`

### 🟠 高问题 (应该修复)
1. **api.ts:112中缺少认证**
   - 问题：未保护的端点
   - 修复：添加认证中间件

### 🟡 中问题 (尽快修复，可以提交)
1. orders.ts:156中的N+1查询模式
   - 考虑尽快修复，可以提交

### 🟢 低问题 (可选)
1. 考虑提取辅助函数

### ✅ 优势
- 良好的测试覆盖率
- 清晰的函数名
- 适当的错误处理

### 📊 摘要
- 关键：1 | 高：2 | 中：2 | 低：1
- **状态：❌ 阻止** - 修复关键/高问题后才能提交
```

---

## Claude指令

### 何时调用代码审查

Claude应在以下情况下自动建议或运行代码审查：

1. **完成功能后** → "在我们提交之前，让我运行代码审查"
2. **创建PR之前** → "运行代码审查所有更改"
3. **说'提交'时** → "在我们提交之前，先进行代码审查"
4. **修复错误后** → "审查修复以查看是否有任何问题"

### 审查重点区域

根据更改类型进行优先级审查：

| 更改类型 | 重点区域 |
|--------|----------|
| 安全代码 | 安全、输入验证、加密 |
| 数据库代码 | SQL注入、N+1、事务 |
| API端点 | 认证、速率限制、验证 |
| 前端代码 | XSS、状态管理、性能 |
| 基础设施 | 密钥、权限、日志记录 |

---

## 快速参考

### 命令

```bash
# 审查当前更改
/code-review

# 审查特定文件
/code-review src/auth.ts src/users.ts

# 审查特定关注点
/code-review --focus security
/code-review --focus performance
/code-review --focus architecture
```

### 严重性操作

```
🔴 关键 → 停止。立即修复。不能提交。
🟠 高     → 停止。立即修复。不能提交。
🟡 中     → 记录。尽快修复。可以提交。
🟢 低      → 可选。可选修复。
ℹ️ 信息     → 仅建议。
```

### 工作流

```
代码 → 测试 → 审查 → 修复 → 提交 → 推送 → PR → 审查 → 合并 → 部署
              ↑                              ↑                    ↑
           /code-review                /code-review          /code-review
```
