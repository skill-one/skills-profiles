# indexion SDD (基于规范的开发)

将 indexion 的量化规范对齐工具与 SDD 代理工作流程（cc-sdd、codex 等）进行桥接。

提供：RFC/文档 → SDD 草稿、规范↔实现漂移检测以及一个验证循环，该循环将 indexion 的量化结果输入到代理驱动的定性审查中。

## 使用场景

- 用户希望将 RFC 或规范实现为库/包
- 用户要求验证规范到实现的符合性
- 用户希望使用 cc-sdd + codex + indexion 设置 SDD 项目
- 用户说“运行 SDD 循环”或“与规范进行验证”
- 在合并之前，在 `codex spec-impl` 完成后检查漂移

## 重要提示

- **将 cc-sdd 的 `--lang` 设置为与实现语言匹配，而不是规范语言。** 如果代码是英文的，请使用 `--lang en`。不匹配的语言会破坏 `spec align diff` 词汇匹配。

## 流程：RFC → 实现 → 验证

### 第 0 步：项目设置

```bash
# 创建项目目录
mkdir my-rfc-impl && cd my-rfc-impl

# 安装适用于您的代理的 cc-sdd — 设置 lang 以匹配代码语言
npx cc-sdd@latest --codex-skills --lang en --yes   # codex (技能模式)
npx cc-sdd@latest --claude-skills --lang en --yes   # claude (技能模式)

# 初始化项目（特定于语言）
# 例如，cargo init、npm init、moon new 等

# 初始化 git
git init && git add -A && git commit -m "init"
```

**在继续之前验证 indexion 是否可用**。漂移门（第 2.5 步）和验证循环（第 3 步）都依赖于它：

```bash
indexion --version                       # 必须已安装
indexion kgf edges <任何源文件>     # 必须检测语言并显示边
```

如果 `indexion` 未安装，请先安装它。如果您的规范格式的 KGF 未被识别，请更新 `indexion` 到包含它的版本。有关无法解决此问题的后备方案，请参阅第 2.7 步。

### 第 1 步：规范 → SDD 草稿（indexion）

获取规范文档（RFC、ISO 标准 等）并准备它：

```bash
# 对于 RFC：保存为 markdown 或 .rfc.txt
indexion spec draft --output .kiro/specs/<功能>/requirements.md rfc_document.md

# 对于 ISO/IEC 标准：使用清理脚本从 PDF 中提取文本，然后草稿
python3 scripts/extract_iso_text.py spec.pdf <起始页> <结束页> spec.spec.txt
indexion spec draft --output .kiro/specs/<功能>/requirements.md spec.spec.txt

# 创建 spec.json（设置 requirements.generated=true, approved=true）
```

输出使用 `### Requirement N:` 和 `#### N.M:` 层次结构匹配 cc-sdd 的预期 ID 格式。代理的 `$kiro-spec-requirements` 阶段将进一步细化为 EARS 格式，并包含验收标准。

**支持的规范格式：**
| 格式 | 扩展名 | KGF 规范 |
|------|--------|----------|
| RFC 纯文本 | `.rfc.txt` | `rfc-plaintext` |
| ISO/IEC 技术文档 | `.spec.txt` | `technical-document` |
| Markdown (README 等) | `.md` | `markdown` |

### 第 1.5 步：规范保真度检查（indexion）

在编写要求后，验证它们是否涵盖了源规范：

```bash
# 检查要求 ↔ 原始规范对齐
# （spec align 现在接受文档文件作为实现，当没有代码文件时）
indexion spec align diff .kiro/specs/<功能>/requirements.md spec.spec.txt \
  --format markdown --threshold 0.3

# SPEC_ONLY 项 = 原始规范未涵盖的要求
# DRIFTED 项 = 使用与原始规范不同的词汇的要求
```

**可追溯性链：** `spec align` 在同一抽象级别的文档之间工作。对于完整的可追溯性，请检查每一对相邻的：

```bash
# 1. 源规范 ↔ 要求（保真度）
indexion spec align diff requirements.md source-spec.spec.txt --threshold 0.3
# 2. 要求 ↔ 设计（设计覆盖率）
indexion spec align diff requirements.md design.md --threshold 0.3
# 3. 要求 ↔ 实现（实现覆盖率） — 在 $kiro-impl 之后
indexion spec align diff requirements.md src/ --threshold 0.3
```

**不要直接将源规范与设计或代码对齐** — 词汇空间差异太大（规范性规范语言 vs. 软件设计 vs. 代码标识符）。每个跳转都弥合了一个抽象差距。

**语义保真度审查（不可自动）：**

`spec align` 检查词汇重叠，但无法检测到使用相同词汇但**反转**源规范意图的要求。常见错误模式：

- 源规范： "DCTDecode 滤镜 **应解码** JPEG 数据为样本"
- 要求草稿： "对于 DCTDecode，解码器 **应返回** 指示滤镜尚未支持的错误"

两者都提到了 "DCTDecode"、"滤镜"、"应" — 词汇匹配，因此 `spec align` 报告匹配。但要求说反了源规范的要求。这会创建一个隐藏的差距，只有在端到端测试失败时（第 2.9 步）才会暴露。

**在 `spec draft` 生成要求后，审查以下模式：**

- `"尚未支持"`、`"未实现"`、`"占位符"`、`"桩"` — 这些表示草稿放弃了规范要求
- `"应返回错误"` 对于源规范说 `"应解码/处理/转换"` 的事情 — 意图反转
- 将多个规范功能组合到一个“不支持”的桶中的要求 — 每个规范功能都应该有自己的要求

在继续到第 2 步之前修复这些问题。留下它们会在端到端测试中产生虚假的规范符合性，而端到端测试才能暴露。

### 第 2 步：代理 SDD 阶段（codex / claude）

cc-sdd v3+ 使用技能模式（`$kiro-spec-*` 命令）。

**非交互式执行，阶段之间使用 indexion 门控：**

```bash
FEATURE=<功能>
SPEC_DIR=.kiro/specs/$FEATURE
REPORT_DIR=.indexion/sdd-reports/$FEATURE
mkdir -p $REPORT_DIR

# 辅助：批准 spec.json 中的阶段
approve() { jq --arg p "$1" '.approvals[$p].approved = true' $SPEC_DIR/spec.json > /tmp/spec.json && mv /tmp/spec.json $SPEC_DIR/spec.json; }

# --- 设计 ---
codex exec --full-auto --json -C . "\$kiro-spec-design $FEATURE -y" > $REPORT_DIR/design.jsonl
approve design
# 验证要求 ↔ 设计
indexion spec align diff $SPEC_DIR/requirements.md $SPEC_DIR/design.md \
  --format markdown --threshold 0.3 | tee $REPORT_DIR/req-design-align.md
git add $SPEC_DIR && git commit -m "spec: $功能的设计"

# --- 任务 ---
codex exec --full-auto --json -C . "\$kiro-spec-tasks $FEATURE -y" > $REPORT_DIR/tasks.jsonl
git add $SPEC_DIR && git commit -m "spec: $功能的任务"

# --- 实现 A 阶段：类型和结构 ---
# 阶段 A 实现类型定义、错误类型、数据结构和公共 API 表面。尚未实现逻辑实现。
cat > $REPORT_DIR/impl-phase-a.md << 'PHASE_A_EOF'
## 上下文

您正在实现 <功能> 功能的阶段 A（类型和结构）。
阅读 `.kiro/specs/<功能>/tasks.md` 获取任务详细信息，以及 `.kiro/specs/<功能>/design.md` 获取设计。

## 阶段 A 范围

在此阶段，仅实现：
- 公共类型定义（结构、枚举、类型别名）
- 错误类型
- 常量和配置结构
- 公共 API 函数签名，带有占位符正文
- 测试脚手架（带有占位符测试的测试文件）

不要实现：
- 解析、转换或转换逻辑
- 算法实现
- 超出简单构造器的复杂函数正文

## 每个任务的漂移门

完成每个任务并提交后，运行规范对齐以验证任务是否关闭了其相应的需求差距。如果当前任务所对应的要求仍然是 DRIFTED、SPEC_ONLY 或 SHALLOW，则不要继续到下一个任务。

**阶段 A 门**（仅类型 — SHALLOW 是预期的且可接受的）：

```bash
indexion spec align status $SPEC_DIR/requirements.md src/ --threshold 0.3 --fail-on drifted
```

**阶段 B 门**（逻辑 — SHALLOW 必须为零）：

```bash
indexion spec align diff $SPEC_DIR/requirements.md src/ --format markdown --threshold 0.3
indexion spec align status $SPEC_DIR/requirements.md src/ --threshold 0.3 --fail-on any
```

**SHALLOW 检测：** 当要求仅匹配到包含非平凡函数实现（>4 行）的类型/结构定义的文件时，`spec align` 将其分类为 SHALLOW。这捕获了两种模式：

1. Codex 将类型定义写入以满足词汇匹配，但省略了要求实际需要的实际处理逻辑。
2. Codex 在**与类型定义不同的文件**中添加逻辑。
SHALLOW 检测按文件进行，因此一个文件中的类型和仅在其另一个文件中具有方法仍然会触发 SHALLOW。

**解决方法：** 将方法添加到定义类型的同一文件中。
简单的函数（构造器、一行访问器 ≤4 行）不计入。请参阅阶段 B 提示模板中的示例。

当将此门控包含在 Codex 提示中时，指示代理在每次任务提交后运行这些命令，并在继续之前修复任何标记的项目。提示中的示例指令块：

```
每次完成任务（提交）后运行：
  indexion spec align diff ... --threshold 0.3
  indexion spec align status ... --threshold 0.3 --fail-on any
如果要求中仍有 DRIFTED、SPEC_ONLY 或 SHALLOW 项，请在转到下一个任务之前修复它们。
- DRIFTED: 向公共声明文档注释中添加规范词汇
- SPEC_ONLY: 实现缺失的要求
- SHALLOW: 将实际的处理/解析/转换逻辑添加到**同一文件**中，其中匹配了类型定义。不要将逻辑添加到不同的文件 — SHALLOW 检测按文件进行。
当所有任务完成时，spec align status --fail-on any 必须退出 0
```

### 第 2.6 步：阶段 B 迭代（SHALLOW 解决轮次）

阶段 B 很少在一次 Codex 会话中解决所有 SHALLOW 项。常见原因：
- Codex 在新的文件中添加逻辑，而不是在定义类型的文件中添加
- Codex 添加了不计算的非平凡构造器/访问器（≤4 行）的简单构造器/访问器
- 添加了没有相应逻辑的新类型定义

**迭代协议：**

每次完成阶段 B 会话后：

1. 运行 SHALLOW 审计：
   ```bash
   indexion spec align status $SPEC_DIR/requirements.md src/$PKG/ \
     --threshold 0.3 --fail-on shallow
   ```

2. 如果 `Shallow: 0`，则继续到端到端验证（第 2.9 步）。

3. 如果 SHALLOW > 0，则识别特定项：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/$PKG/ \
     --format markdown --threshold 0.3 | grep SHALLOW
   ```

4. 编写一个有针对性的轮次提示，其中：
   - 明确列出剩余的 SHALLOW 项
   - 指定需要添加函数的确切文件
   - 声明规则：**将函数添加到与类型相同的文件**
   - 指定要添加的方法（不仅仅是“修复 SHALLOW”）

5. 启动下一轮：
   ```bash
   codex exec --full-auto --json -C . \
     "$(cat $REPORT_DIR/round-N.md)" \
     > $REPORT_DIR/round-N.jsonl &
   ```

**典型：2-3 轮。** 第 1 轮添加核心逻辑，第 2 轮强制同一文件中的方法，第 3 轮捕获剩余的边缘情况。

### 第 2.7 步：停滞检测和恢复

Codex 处理过程可能会停滞（丢失 API 连接、阻塞审查循环等）。这在长时间运行的阶段 B 会话中很常见。

**检测：**

```bash
# 检查进程生命体征
ps -p $CODEX_PID -o cputime,%cpu,etime
lsof -p $CODEX_PID 2>/dev/null | grep tcp

# 停滞指标（所有必须为真）：
# - CPU 时间在 2 次检查以上没有增加
# - 0.0% CPU
# - 没有 TCP 连接
# - JSONL 事件计数没有增加
```

**恢复 — 永远不要手动提交：**

当确认停滞时：

1. 杀死进程：`kill $CODEX_PID`
2. 检查已完成的内容：`git log`, `git status`, `git diff --cached`
3. 如果存在未提交的工作并且测试通过，生成 indexion 报告：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/ \
     --format markdown --threshold 0.3 -o $REPORT_DIR/align-current.md
   indexion spec verify --spec="$SPEC_DIR/requirements.md" src/ \
     --format md -o $REPORT_DIR/verify-current.md
   ```
4. 编写一个包含所有报告作为当前状态证据的恢复提示文件，其中：
   - 声明已提交的任务和存在未提交工作的任务
   - 指令 Codex 验证并提交未提交的工作，然后继续
   - 要求所有剩余任务使用每个任务的漂移门（第 2.5 步）
5. 重新启动：`codex exec --full-auto --json -C . "$(cat $REPORT_DIR/resume-prompt.md)" > $REPORT_DIR/impl-resume.jsonl &`

**永远不要手动提交实现代码。** 所有提交必须来自 Codex 代理。如果您手动提交，您会绕过 SDD 协议（RED→GREEN 证据、审查、验证），并使工作流程无效。

### 第 1.8 步：漂移门代理（当 Codex 无法运行 indexion 时）

Codex 在实现项目目录内运行 `indexion` 命令。如果 `indexion` 未安装，版本过旧，或缺少所需的 KGF 规范，则漂移门命令将在 Codex 内失败或超时。

**预防（推荐）：** 在第 0 步中验证 `indexion` 在项目目录中是否可用，然后再开始 SDD 运行：

```bash
indexion --version
indexion kgf edges <任何项目文件>   # 应显示边，而不是错误
```

如果 `indexion` 不可用或损坏，请先安装或更新它。

**后备 — 协调器端的漂移门：**

如果在运行之前无法修复 `indexion`（例如，尚未发布的必需 KGF 规范），则协调器在外部运行漂移门：

1. 告知 Codex 在实现提示中跳过漂移门命令：
   ```
   此环境中的 `indexion` 二进制文件不可用。
   跳过漂移门命令。协调器将在外部运行它们。
   ```
2. 在 Codex 提交后，协调器运行：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/ \
     --format markdown --threshold 0.3
   indexion spec align status $SPEC_DIR/requirements.md src/ \
     --threshold 0.3 --fail-on any
   ```
3. 如果出现 DRIFTED/SPEC_ONLY 项，请运行词汇修复步骤（第 3.5 步）使用外部生成的报告。

**`--specs-dir` 注意事项：** 当直接运行 indexion 二进制文件（不是通过项目的构建工具）时，它可能无法自动找到 KGF 规范。明确传递 `--specs-dir`：

```bash
indexion spec align diff ... --specs-dir /path/to/indexion/kgfs
```

如果没有这样做，`spec align` 可能会返回“未找到对齐数据”，因为要求文档格式无法识别。

### 第 2.9 步：端到端验证（解决 SHALLOW 之后）

在所有 SHALLOW 项解决 (`Shallow: 0`) 后，验证实现是否实际按端到端工作。`spec align` 仅检查词汇 — 它无法确认功能正确性。

编写端到端测试，使用真实输入数据对整个管道进行测试：

```bash
# 示例端到端模式：
# 1. 加载真实输入文件（不仅仅是合成固定件）
# 2. 运行完整的处理管道端到端
# 3. 断言输出与预期结果匹配
```

**常见的端到端失败模式（SHALLOW=0 之后）：**
- 类型定义存在且逻辑函数存在，但管道在真实输入上引发错误（缺少编码表、不支持字体类型等）
- 在合成固定件上所有测试都通过，但在真实文件上失败，因为固定件没有执行完整的代码路径
- 已实现函数但未连接到顶级 API

如果端到端测试失败，请编写针对特定失败的 Codex 提示。规范对齐门控确保词汇保持一致，而 Codex 修复了实现。

### 第 2.10 步：并行功能执行

多个功能可以运行在并行的 Codex 会话中：

```bash
for FEATURE in feature-a feature-b feature-c; do
  codex exec --full-auto --json -C . \
    "$(cat $REPORT_DIR/$FEATURE/impl-phase-b.md)" \
    > $REPORT_DIR/$FEATURE/impl-phase-b.jsonl 2>&1 &
  echo "$FEATURE: $!"
done
```

**注意事项：**
- 多个 Codex 会话可能会编辑重叠的文件（例如，多个功能写入 `src/graphics/`）。Git 将自动合并，除非相同的行被修改。
- 如果会话在不同的分支中提交，则合并冲突是协调器的责任。
- 使用 `/loop` 监控所有会话 — 检查每个 PID 的事件计数、提交和进程生命体征。
- 并行会话更容易出现停滞（API 速率限制）。使用第 2.7 步的检测每个会话。

### 第 3 步：验证循环（indexion + 代理）

这是 indexion 添加价值的地方，超越了纯代理审查。

```bash
# 仅量化分析（无代理）
indexion spec verify --spec='.kiro/specs/<功能>/requirements.md' src/lib/ --format md
indexion spec align diff .kiro/specs/<功能>/requirements.md src/lib/ --format markdown --threshold 0.3
indexion spec align status .kiro/specs/<功能>/requirements.md src/lib/ --threshold 0.3 --fail-on any

# 全循环：indexion 量化 + 代理定性 + 自动修复
./scripts/sdd-validate.sh <功能>           # 仅验证
./scripts/sdd-validate.sh <功能> --fix     # 验证 + 自动修复失败的 NO-GO 任务
```

验证脚本：
1. 运行 `spec verify`（规范与实现之间的词汇差距）
2. 运行 `spec align diff`（要求级别的漂移）
3. 运行 `spec align trace`（可追溯性矩阵）
4. 运行 `spec align status`（CI 门控）
5. 将所有报告注入代理的 `validate-impl` 提示
6. 代理生成 GO/NO-GO 决策和特定任务编号
7. 在 `--fix` 下，自动重新运行 `spec-impl` 对于失败的任务

### 第 3.5 步：词汇对齐修复（indexion + 代理）

在 `$kiro-validate-impl` 通过但 `spec align` 显示 DRIFTED/SPEC_ONLY 的情况下，实现功能正确但缺少规范词汇的文档注释。此步骤关闭了此差距。

**注意：** `$kiro-validate-impl`（cc-sdd）不会在内部调用 indexion 的 spec align。此步骤桥接了这两个工具。

```bash
# 1. 生成对齐报告
indexion spec align diff .kiro/specs/<功能>/requirements.md src/ \
  --format markdown --threshold 0.3 -o .indexion/sdd-reports/align-diff.md
indexion spec verify --spec='.kiro/specs/<功能>/requirements.md' src/ \
  --format md -o .indexion/sdd-reports/verify-gaps.md

# 2. 编写提示文件（避免 HEREDOC — 使用文件以防止 stdin 阻塞）
cat > .indexion/sdd-reports/vocab-fix-prompt.md << 'EOF'
提示工具报告显示，一些要求是 DRIFTED、SPEC_ONLY 或 SHALLOW。对于每个项，确定它是否为：

1. **实现差距**（SPEC_ONLY） — 规范要求完全未实现。添加缺失的实现和测试。
2. **词汇差距**（DRIFTED） — 实现存在，但缺少规范词汇的公共文档注释。添加规范术语到公共声明。
3. **深度差距**（SHALLOW） — 要求仅匹配到类型定义，同一文件中没有任何非平凡函数实现（>4 行），要求需要添加实际的处理/解析/转换逻辑

您的任务：
- 阅读对齐报告下方。
- 对于每个 DRIFTED 或 SPEC_ONLY 要求，在代码库中搜索来自该要求的关联关键字。如果存在相关代码，则它是词汇差距 — 添加文档注释。如果不存在相关代码，则它是实现差距 — 实现。
- 对齐工具仅从公共声明中提取词汇。私有函数的文档注释对 `spec align` 不可见。
- 完成编辑后运行项目的格式化程序和测试套件。
- 提交您的更改。不要留下未提交的更改。

## 规范对齐修复提示
EOF
cat .indexion/sdd-reports/align-diff.md >> .indexion/sdd-reports/vocab-fix-prompt.md
echo -e "\n## 词汇差距报告" >> .indexion/sdd-reports/vocab-fix-prompt.md
head -40 .indexion/sdd-reports/verify-gaps.md >> .indexion/sdd-reports/vocab-fix-prompt.md

# 3. 使用提示文件运行代理
codex exec --full-auto --json -C . \
  "$(cat .indexion/sdd-reports/vocab-fix-prompt.md)" \
  > .indexion/sdd-reports/vocab-fix.jsonl &

# 4. 监控（可选）
tail -f .indexion/sdd-reports/vocab-fix.jsonl | jq -r '
  if .type == "item.completed" and .item.type == "agent_message"
  then "MSG: " + (.item.text[:120])
  elif .type == "item.completed" and .item.type == "command_execution"
  then "CMD: " + (.item.command[:50]) + " -> " + (.item.exit_code|tostring)
  else empty end'

# 5. 代理完成后重新检查对齐
indexion spec align status .kiro/specs/<功能>/requirements.md src/ \
  --threshold 0.3 --fail-on any
```

**关键约束：**
- 提示**不指定**要添加的特定词汇。它提供对齐报告和让代理确定要修复的内容。
- 代理必须仅针对公共声明 — 私有函数的文档注释对 `spec align` 不可见。
- 典型：1-2 个修复周期。如果 SPEC_ONLY 持续存在，代理可能需要指导，即相关的公共 API 入口点应携带词汇（例如，顶级 `open` 函数记录了完整流程）。

**已知的盲点：**

- **没有公共 API 的 CLI 入口点**：主/入口点模块通常没有公共声明 — 所有函数都是模块私有的。`spec align` 仅从公共声明中提取词汇，因此入口点模块始终显示为 Matched: 0 / SPEC_ONLY 对于所有要求。**解决方法：** 将 CLI 逻辑拆分为一个库模块，该模块公开公共函数，入口点作为瘦的调度器。将要求与库对齐，而不是入口点。

- **空的文档注释**：Codex 常常写入文档注释语法，但没有实际内容。这些对 `spec align` 不可见，因为它们不包含词汇。词汇修复提示必须明确指示代理：**不要让文档注释为空。每个公共声明都必须有一个描述其用途的文档注释，使用来自要求中的术语。**

- **仅限内部的模块（私有函数）**：当实现逻辑完全为私有时，`spec align` 无法看到。这在过滤器/编解码器包中很常见，其中公共管道函数调度到私有解码器。**解决方法：** 要么将关键内部函数提升为公共（它们成为可测试的 API 表面），要么将规范词汇合并到公共管道函数的文档注释中，以便要求在那里匹配。

- **字面要求与标识符匹配**：引用项目特定字面量（包名、表编号、配置键）的要求，如果实现文档注释中未提及确切字面量，将显示为 DRIFTED。这通常是一个信号，即**要求包含不应存在于要求中的项目特定详细信息** — 修复要求以使用通用描述，或者接受词汇修复代理必须传播这些字面量。

- **“回退”框架与规范要求的实现**：当代理提议对不支持的功能的“回退”时，请验证该功能是否确实由源规范要求。例如：TrueType 字体 cmap 表解析被提议为“回退”，但实际上规范确实要求 TrueType 字体编码解析。将规范要求表述为回退会创建不正确的优先级，并可能导致不完整的实现。

- **词汇匹配 ≠ 功能正确性**：DRIFTED=0 和 SHALLOW=0 确认词汇一致，但无法验证实现是否实际工作。端到端测试（从真实文件中提取文本、视觉渲染比较）至关重要，以捕获：
- 编译通过的类型定义在执行时引发错误
- 在合成固定件上所有测试都通过，但在真实文件上失败，因为固定件没有执行完整的代码路径
- 已实现函数但未连接到顶级 API
