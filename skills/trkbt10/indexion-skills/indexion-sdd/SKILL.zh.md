---
name: indexion-sdd
description: 从RFCs/规范中生成SDD需求，并定量验证实现符合性。规范草案 → 规范对齐 → 规范验证 → 使用Codex/Clauide进行自动化验证循环。将规范到实现的漂移门作为CI检查来操作。
---

# indexion SDD (基于规范的开发)

将 indexion 的量化规范对齐工具与 SDD 代理工作流程（cc-sdd、codex 等）进行桥接。

提供：RFC/文档 → SDD 草稿、规范 ↔ 实现 的漂移检测，以及一个将 indexion 的量化结果输入代理驱动定性审查的验证循环。

## 使用场景

- 用户希望将 RFC 或规范实现为库/包
- 用户要求验证规范到实现的符合性
- 用户希望使用 cc-sdd + codex + indexion 设置 SDD 项目
- 用户说“运行 SDD 循环”或“与规范进行验证”
- 在合并之前 `codex spec-impl` 完成后，检查漂移

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

在继续之前**验证 indexion 是否可用**。漂移门（第 2.5 步）和验证循环（第 3 步）都依赖于它：

```bash
indexion --version                       # 必须已安装
indexion kgf edges <任何源文件>         # 必须检测语言并显示边
```

如果 `indexion` 未安装，请先安装它。如果您的规范格式的 KGF 未被识别，请更新 `indexion` 到包含它的版本。如果无法解决此问题，请参阅第 2.7 步的降级方案。

### 第 1 步：规范 → SDD 草稿（indexion）

获取规范文档（RFC、ISO 标准等）并准备它：

```bash
# 对于 RFC：保存为 markdown 或 .rfc.txt
indexion spec draft --output .kiro/specs/<功能>/requirements.md rfc_document.md

# 对于 ISO/IEC 标准：使用清理脚本从 PDF 中提取文本，然后起草
python3 scripts/extract_iso_text.py spec.pdf <起始页> <结束页> spec.spec.txt
indexion spec draft --output .kiro/specs/<功能>/requirements.md spec.spec.txt

# 创建 spec.json（设置 requirements.generated=true, approved=true）
```

输出使用 `### Requirement N:` 和 `#### N.M:` 层次结构，与 cc-sdd 预期的 ID 格式匹配。代理的 `$kiro-spec-requirements` 阶段将进一步细化为 EARS 格式，并包含验收标准。

**支持的规范格式：**
| 格式 | 扩展名 | KGF 规范 |
|------|--------|----------|
| RFC 纯文本 | `.rfc.txt` | `rfc-plaintext` |
| ISO/IEC 技术文档 | `.spec.txt` | `technical-document` |
| Markdown (README 等) | `.md` | `markdown` |

### 第 1.5 步：规范保真度检查（indexion）

在编写需求后，验证它们是否涵盖了源规范：

```bash
# 检查需求 ↔ 原始规范对齐
# （spec align 现在接受文档文件作为实现，当找不到代码文件时）
indexion spec align diff .kiro/specs/<功能>/requirements.md spec.spec.txt \
  --format markdown --threshold 0.3

# SPEC_ONLY 项 = 原始规范未涵盖的需求
# DRIFTED 项 = 使用与原始规范不同的词汇的需求
```

**可追溯性链：** `spec align` 在同一抽象级别的文档之间工作。对于完整可追溯性，请检查每一对相邻的文档：

```bash
# 1. 源规范 ↔ 需求（保真度）
indexion spec align diff requirements.md source-spec.spec.txt --threshold 0.3
# 2. 需求 ↔ 设计（设计覆盖率）
indexion spec align diff requirements.md design.md --threshold 0.3
# 3. 需求 ↔ 实现（实现覆盖率） — 在 $kiro-impl 之后
indexion spec align diff requirements.md src/ --threshold 0.3
```

**不要直接将源规范与设计或代码对齐** — 词汇空间差异太大（规范性规范语言 vs. 软件设计 vs. 代码标识符）。每个跳转桥接一个抽象差距。

**语义保真度审查（不可自动执行）：**

`spec align` 检查词汇重叠，但无法检测到使用相同词汇**反转**源规范意图的需求。常见错误模式：

- 源规范： "The DCTDecode filter **shall decode** JPEG data into samples"
- 需求草稿： "For DCTDecode, the decoder **shall return** an error indicating the filter is not yet supported"

两者都提到了 "DCTDecode"、"filter"、"shall" — 词汇匹配，因此 `spec align` 报告匹配。但需求说的与规范要求相反。这会创建一个隐藏的差距，只有在端到端测试失败时（第 2.9 步）才会暴露。

**在 `spec draft` 生成需求后，审查这些模式：**

- `"not yet supported"`、`"not implemented"`、`"placeholder"`、`"stub"` — 这些表示草稿推迟了规范要求
- `"shall return an error"` 对于源规范说 `"shall decode/process/convert"` 的内容 — 意图反转
- 将多个规范功能分组到一个单独的“不支持”桶中的需求 — 每个规范功能都应该有自己的需求

在继续到第 2 步之前修复这些问题。留下它们会创建一种虚假的规范符合性感觉，只有端到端测试才能暴露。

### 第 2 步：代理 SDD 阶段（codex / claude）

cc-sdd v3+ 使用技能模式（`$kiro-spec-*` 命令）。

**使用 indexion 门在阶段之间进行非交互式执行：**

```bash
FEATURE=<功能>
SPEC_DIR=.kiro/specs/$FEATURE
REPORT_DIR=.indexion/sdd-reports/$FEATURE
mkdir -p $REPORT_DIR

# 辅助：在 spec.json 中批准阶段
approve() { jq --arg p "$1" '.approvals[$p].approved = true' $SPEC_DIR/spec.json > /tmp/spec.json && mv /tmp/spec.json $SPEC_DIR/spec.json; }

# --- 设计 ---
codex exec --full-auto --json -C . "\$kiro-spec-design $FEATURE -y" > $REPORT_DIR/design.jsonl
approve design
# 验证需求 ↔ 设计
indexion spec align diff $SPEC_DIR/requirements.md $SPEC_DIR/design.md \
  --format markdown --threshold 0.3 | tee $REPORT_DIR/req-design-align.md
git add $SPEC_DIR && git commit -m "spec: 设计 for $FEATURE"

# --- 任务 ---
codex exec --full-auto --json -C . "\$kiro-spec-tasks $FEATURE -y" > $REPORT_DIR/tasks.jsonl
git add $SPEC_DIR && git commit -m "spec: 任务 for $FEATURE"

# --- 实现 A 阶段：类型和结构 ---
# 阶段 A 实现类型定义、错误类型、数据结构和公共 API 表面。尚未实现逻辑实现。
cat > $REPORT_DIR/impl-phase-a.md << 'PHASE_A_EOF'
## 背景

您正在实现 <功能> 功能的阶段 A（类型和结构）。
阅读 `.kiro/specs/<功能>/tasks.md` 获取任务详细信息，以及 `.kiro/specs/<功能>/design.md` 获取设计。

## 阶段 A 范围

在此阶段，仅实现：
- 公共类型定义（结构、枚举、类型别名）
- 错误类型
- 常量和配置结构
- 带占位符体的公共 API 函数签名
- 测试脚手架（带占位符测试的测试文件）

不要实现：
- 解析、转换或转换逻辑
- 算法实现
- 超过简单构造函数/访问器的复杂函数体

## 每个任务的漂移门

完成每个任务并提交后，运行：

```bash
indexion spec align diff .kiro/specs/<功能>/requirements.md src/<包>/ --format markdown --threshold 0.3
indexion spec align status .kiro/specs/<功能>/requirements.md src/<包>/ --threshold 0.3 --fail-on drifted
```

如果当前任务对应的需求仍有 DRIFTED 项，请修复它们（在公共声明文档注释中添加规范词汇）并重新提交。

当所有任务完成时，`spec align status --fail-on drifted` 必须退出 0。

## 重要提示

完成任务后提交您的工作。不要留下未提交的更改。
PHASE_A_EOF

sed -i '' "s/<功能>/$FEATURE/g; s/<包>/$PKG/g" $REPORT_DIR/impl-phase-a.md

codex exec --full-auto --json -C . \
  "$(cat $REPORT_DIR/impl-phase-a.md)" > $REPORT_DIR/impl-phase-a.jsonl
# 在运行门之前等待阶段 A 完成
indexion spec align status $SPEC_DIR/requirements.md src/$PKG/ \
  --threshold 0.3 --fail-on drifted
git add . && git commit -m "impl: 阶段 A 类型 for $FEATURE"

# --- 实现 B 阶段：逻辑和算法 ---
# 阶段 B 实现实际处理逻辑。阶段 A 的类型已经提交，因此阶段 B 专注于函数体。
cat > $REPORT_DIR/impl-phase-b.md << 'PHASE_B_EOF'
## 背景

您正在实现 <功能> 功能的阶段 B（逻辑和算法）。
阶段 A（类型定义）已经提交。阅读 `src/<包>/` 中的现有类型定义和 `.kiro/specs/<功能>/design.md` 中的设计。

## 阶段 B 范围

在此阶段，实现：
- 解析逻辑（读取器、解码器、解释器）
- 转换和转换算法
- 超越基本类型构建的验证逻辑
- 类型之间的集成（将读取器连接到数据结构）
- 带有真实断言的完整测试实现

描述处理、转换、解释或验证的每个需求都必须有一个相应的函数实现 — 不仅仅是类型定义。

## 浅层解析规则

当需求与一个没有非平凡函数实现（>4 行）的文件中的类型定义匹配时，会检测到浅层。要解决：

**在定义类型的同一文件中添加函数。**

不要将逻辑放在单独的文件中 — 浅层检查按文件进行。如果类型定义在一个文件中，而其方法在另一个文件中，该类型的文件仍然没有函数，并且会触发浅层。

浅层解析的函数示例：
- 类型上的方法，包含 >4 行逻辑（匹配臂、循环、验证、计算）
- 执行非平凡工作的构造函数（解析、验证）

浅层未解析的示例（过于简单，≤4 行）：
- 仅返回结构字面量的默认构造函数
- 一行布尔访问器

## 每个任务的漂移门（带浅层检测）

完成每个任务并提交后，运行：

```bash
indexion spec align diff .kiro/specs/<功能>/requirements.md src/<包>/ --format markdown --threshold 0.3
indexion spec align status .kiro/specs/<功能>/requirements.md src/<包>/ --threshold 0.3 --fail-on any
```

`--fail-on any` 门包括浅层检测：如果需求仅与包含没有同一文件中非平凡函数实现（>4 行）的类型定义匹配，则将其标记为浅层。您必须添加函数实现来解决浅层项。

如果仍有 DRIFTED、SPEC_ONLY 或 SHALLOW 项，请在继续之前修复它们。

当所有任务完成时，`spec align status --fail-on any` 必须退出 0，浅层：0。

## 重要提示

完成任务后提交您的工作。不要留下未提交的更改。
PHASE_B_EOF

sed -i '' "s/<功能>/$FEATURE/g; s/<包>/$PKG/g" $REPORT_DIR/impl-phase-b.md

codex exec --full-auto --json -C . \
  "$(cat $REPORT_DIR/impl-phase-b.md)" > $REPORT_DIR/impl-phase-b.jsonl &
CODEX_PID=$!
```

**监控实现进度：**

```bash
# 实时事件流
tail -f $REPORT_DIR/impl.jsonl | jq -r '
  if .type == "item.completed" and .item.type == "agent_message" then
    "MSG: " + (.item.text[:120])
  elif .type == "item.completed" and .item.type == "command_execution" then
    "CMD: " + (.item.command[:60]) + " -> " + (.item.exit_code|tostring)
  else empty end'

# 停滞检测
ps -p $CODEX_PID -o cputime,%cpu
lsof -p $CODEX_PID 2>/dev/null | grep tcp

# 中断后恢复
codex exec resume --last
```

**操作说明：**

- 始终使用 `--json` 与文件重定向 + `tail -f`。通过 `| tail` 管道会抑制所有输出直到完成。
- 对于长提示，将内容写入文件并使用 `$(cat file.md)`。使用 `$()` 的 Shell HEREDOC 可能会导致 stdin 阻塞。
- 使用 `/loop`（Claude 代码）每 60-120 秒轮询 `git log --oneline -1` + `ps` 进行长时间实现运行。

### 第 2.5 步：每个任务的漂移门（indexion）

在每次 `$kiro-impl` 任务提交后，运行规范对齐以验证任务是否关闭了其对应的需求差距。如果当前任务对应的需求仍然是 DRIFTED、SPEC_ONLY 或 SHALLOW，则不要继续到下一个任务。

**阶段 A 门**（仅类型 — 浅层是预期且可接受的）：

```bash
indexion spec align status $SPEC_DIR/requirements.md src/ --threshold 0.3 --fail-on drifted
```

**阶段 B 门**（逻辑 — 浅层必须为零）：

```bash
indexion spec align diff $SPEC_DIR/requirements.md src/ --format markdown --threshold 0.3
indexion spec align status $SPEC_DIR/requirements.md src/ --threshold 0.3 --fail-on any
```

**浅层检测：** 当需求仅与一个包含没有非平凡函数实现（>4 行）的类型/结构/枚举声明匹配的文件时，`spec align` 将其分类为浅层。这捕获了两种模式：

1. Codex 将类型定义写入以满足词汇匹配，但省略了需求要求的确切处理逻辑。
2. Codex 在类型定义文件之外的**单独文件**中添加逻辑。浅层检查按文件进行，因此一个文件中的类型与另一个文件中的方法仍然会触发该类型的浅层。

**解决方法：** 在定义类型的同一文件中添加方法。简单函数（构造函数、一行访问器 ≤4 行）不计入。请参阅阶段 B 提示模板中的示例。

当在 Codex 提示中包含此门时，指示代理在每次任务提交后运行这些命令，并在继续之前修复任何标记的项目。提示中的示例指令块：

```
完成每个任务（提交）后运行：
  indexion spec align diff ... --threshold 0.3
  indexion spec align status ... --threshold 0.3 --fail-on any
如果对于您当前任务对应的需求仍有 DRIFTED、SPEC_ONLY 或 SHALLOW 项，请在移动到下一个任务之前修复它们。
- DRIFTED：向公共声明文档注释添加规范词汇
- SPEC_ONLY：实现缺失的需求
- SHALLOW：在定义类型的同一文件中添加非平凡函数实现（>4 行）。不要将逻辑放在单独的文件中 — 浅层检查按文件进行。
当所有任务完成时，spec align status --fail-on any 必须退出 0，浅层：0。
```

### 第 2.6 步：阶段 B 迭代（浅层解决轮次）

阶段 B 很少在一次 Codex 会话中解决所有浅层项。常见原因：
- Codex 在新文件中添加逻辑，而不是在类型定义文件中
- Codex 添加了过于简单的构造函数/访问器（≤4 行），这些不计入
- 添加了没有相应逻辑的新类型定义

**迭代协议：**

每次完成 Phase B 会话后：

1. 运行浅层审计：
   ```bash
   indexion spec align status $SPEC_DIR/requirements.md src/$PKG/ \
     --threshold 0.3 --fail-on shallow
   ```

2. 如果 `Shallow: 0`，则继续进行端到端验证（第 2.9 步）。

3. 如果 SHALLOW > 0，请识别具体项目：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/$PKG/ \
     --format markdown --threshold 0.3 | grep SHALLOW
   ```

4. 编写一个有针对性的轮次提示，该提示：
   - 明确列出剩余的浅层项
   - 指出需要添加函数的确切文件
   - 声明规则：**在类型定义的同一文件中添加函数**
   - 指定要添加的方法（不仅仅是“修复浅层”）

5. 启动下一轮：
   ```bash
   codex exec --full-auto --json -C . \
     "$(cat $REPORT_DIR/round-N.md)" > $REPORT_DIR/round-N.jsonl &
   ```

**典型：2-3 轮。** 第 1 轮添加核心逻辑，第 2 轮强制同一文件方法，第 3 轮捕获剩余边缘情况。

### 第 2.7 步：停滞检测和恢复

Codex 处理过程可能会停滞（丢失 API 连接、被阻塞的审查循环等）。这在长时间 Phase B 会话中很常见。

**检测：**

```bash
# 检查进程关键指标
ps -p $CODEX_PID -o cputime,%cpu,etime
lsof -p $CODEX_PID 2>/dev/null | grep tcp

# 停滞指标（所有必须为真）：
# - CPU时间在2次以上检查中未增加
# - CPU使用率为0.0%
# - 无TCP连接
# - JSONL事件计数未增加
```

**恢复 — 永远不要手动提交：**

当确认出现停滞时：

1. 杀死进程：`kill $CODEX_PID`
2. 检查已完成的工作：`git log`, `git status`, `git diff --cached`
3. 如果存在未提交的工作且测试通过，则生成indexion报告：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/ \
     --format markdown --threshold 0.3 -o $REPORT_DIR/align-current.md
   indexion spec verify --spec="$SPEC_DIR/requirements.md" src/ \
     --format md -o $REPORT_DIR/verify-current.md
   ```
4. 编写一个恢复提示文件，该文件：
   - 说明哪些任务已提交，哪些有未提交的工作
   - 包括indexion报告作为当前状态证据
   - 指示Codex验证并提交未提交的工作，然后继续
   - 要求所有剩余任务使用每个任务的漂移门（步骤2.5）
5. 重启：`codex exec --full-auto --json -C . "$(cat $REPORT_DIR/resume-prompt.md)" > $REPORT_DIR/impl-resume.jsonl &`

**永远不要手动提交实现代码。** 所有提交必须来自Codex代理。如果你手动提交，你会绕过SDD协议（RED→GREEN证据、审查、验证）并使工作流失效。

### 步骤2.8：漂移门代理（当Codex无法运行indexion时）

Codex在impl项目目录内运行`indexion`命令。如果`indexion`未安装、过旧或缺少所需的KGF规范，漂移门命令将在Codex内失败或超时。

**预防（推荐）：** 在开始SDD运行之前，在项目目录中验证`indexion`是否正常工作（步骤0）：

```bash
indexion --version
indexion kgf edges <任何项目文件>   # 应显示边，而不是错误
```

如果`indexion`不可用或损坏，请先安装或更新它。

**后备 — 协调器端的漂移门：**

如果在运行前无法修复`indexion`（例如，所需的KGF规范尚未发布），协调器将外部运行漂移门：

1. 告知Codex在impl提示中跳过漂移门命令：
   ```
   此环境中`indexion`二进制文件不可用。
   跳过漂移门命令。协调器将外部运行它们。
   ```
2. Codex每次提交后，协调器运行：
   ```bash
   indexion spec align diff $SPEC_DIR/requirements.md src/ \
     --format markdown --threshold 0.3
   indexion spec align status $SPEC_DIR/requirements.md src/ \
     --threshold 0.3 --fail-on any
   ```
3. 如果出现DRIFTED/SPEC_ONLY项，运行词汇修复步骤（步骤3.5）并使用外部生成的报告。

**`--specs-dir`注意事项：** 当直接运行indexion二进制文件（而非通过项目的构建工具）时，它可能无法自动找到KGF规范。显式传递`--specs-dir`：

```bash
indexion spec align diff ... --specs-dir /path/to/indexion/kgfs
```

否则，`spec align`可能返回“未找到对齐数据”，因为需求文档格式未被识别。

### 步骤2.9：端到端验证（post-SHALLOW）

在所有SHALLOW项解决（`Shallow: 0`）后，验证实现是否真正端到端工作。`spec align`仅检查词汇 — 它无法确认功能正确性。

编写端到端测试，使用真实输入数据对完整管道进行测试：

```bash
# 示例端到端模式：
# 1. 加载真实输入文件（不只是合成固定件）
# 2. 运行完整处理管道端到端
# 3. 断言输出与预期结果匹配
```

**SHALLOW=0后的常见端到端失败模式：**
- 类型定义存在且逻辑函数存在，但管道在真实输入上引发错误（缺少编码表、不支持字体类型等）
- 所有测试在合成固定件上通过，但在真实文件上失败，因为固定件未覆盖完整代码路径
- 函数已实现但未连接到顶层API

如果端到端测试失败，编写针对特定失败的Codex提示。spec对齐门确保词汇保持一致，同时Codex修复实现。

### 步骤2.10：并行功能执行

多个功能可以在并行的Codex会话中运行：

```bash
for FEATURE in feature-a feature-b feature-c; do
  codex exec --full-auto --json -C . \
    "$(cat $REPORT_DIR/$FEATURE/impl-phase-b.md)" \
    > $REPORT_DIR/$FEATURE/impl-phase-b.jsonl 2>&1 &
  echo "$FEATURE: $!"
done
```

**注意事项：**
- 多个Codex会话可能会编辑重叠文件（例如，多个功能写入`src/graphics/`）。Git将自动合并，除非相同行被修改。
- 如果会话在不同的分支中提交，合并冲突是协调器的责任。
- 使用`/loop`监控所有会话 — 检查每个PID的事件计数、提交和进程关键指标。
- 并行会话更常见停滞（API速率限制）。使用步骤2.7按会话检测停滞。

### 步骤3：验证循环（indexion + 代理）

这是indexion在纯代理审查之外增加价值的地方。

```bash
# 仅定量分析（无代理）
indexion spec verify --spec='.kiro/specs/<feature>/requirements.md' src/lib/ --format md
indexion spec align diff .kiro/specs/<feature>/requirements.md src/lib/ --format markdown --threshold 0.3
indexion spec align status .kiro/specs/<feature>/requirements.md src/lib/ --threshold 0.3 --fail-on any

# 完整循环：indexion定量 + 代理定性 + 自动修复
./scripts/sdd-validate.sh <feature>           # 仅验证
./scripts/sdd-validate.sh <feature> --fix     # 验证 + 自动修复NO-GO任务
```

验证脚本：
1. 运行`spec verify`（规范和实现之间的词汇差距）
2. 运行`spec align diff`（需求级漂移）
3. 运行`spec align trace`（可追溯性矩阵）
4. 运行`spec align status`（CI式通过/失败）
5. 将所有报告注入代理的`validate-impl`提示
6. 代理生成GO/NO-GO决策及具体任务编号
7. 在`--fix`时，自动重新运行`spec-impl`对失败任务

### 步骤3.5：词汇对齐修复（indexion + 代理）

在`$kiro-validate-impl`通过但`spec align`显示DRIFTED/SPEC_ONLY后，实现功能正确但文档注释中缺少规范词汇。此步骤弥补该差距。

**注意：** `$kiro-validate-impl`（cc-sdd）不内部调用indexion的spec align。此步骤连接这两个工具。

```bash
# 1. 生成对齐报告
indexion spec align diff .kiro/specs/<feature>/requirements.md src/ \
  --format markdown --threshold 0.3 -o .indexion/sdd-reports/align-diff.md
indexion spec verify --spec='.kiro/specs/<feature>/requirements.md' src/ \
  --format md -o .indexion/sdd-reports/verify-gaps.md

# 2. 编写提示文件（避免HEREDOC — 使用文件防止stdin阻塞）
cat > .indexion/sdd-reports/vocab-fix-prompt.md << 'EOF'
spec对齐工具报告多个需求为DRIFTED、SPEC_ONLY或SHALLOW。对于每个项，确定它是：

1. **实现差距**（SPEC_ONLY）— 规范要求完全未实现。添加缺失的实现和测试。
2. **词汇差距**（DRIFTED）— 实现存在但规范词汇缺失于公共文档注释。向公共声明添加规范术语。
3. **深度差距**（SHALLOW）— 需求匹配到类型定义仅，同一文件中无函数实现。添加实际处理/解析/转换逻辑。

你的任务：
- 阅读对齐报告。
- 对于每个DRIFTED或SPEC_ONLY需求，在代码库中搜索相关关键词。如果存在相关代码，它是词汇差距 — 添加文档注释。如果无相关代码，它是实现差距 — 实现。
- 对齐工具仅从公共声明提取词汇。私有函数的文档注释对工具不可见。
- 运行项目的格式化器和测试套件。
- 提交你的更改。不要留下未提交的更改。

## Spec对齐差分报告
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
indexion spec align status .kiro/specs/<feature>/requirements.md src/ \
  --threshold 0.3 --fail-on any
```

**关键约束：**
- 提示不指定要添加的特定词汇。它提供对齐报告并让代理决定修复内容。
- 代理必须仅针对公共声明 — 私有函数文档注释对`spec align`不可见。
- 典型：1-2个修复周期。如果SPEC_ONLY持续存在，代理可能需要指导，即相关公共API入口点应包含词汇（例如，顶级`open`函数记录完整流程）。

**已知盲点：**

- **无公共API的CLI入口点：** 主/入口点模块通常无公共声明 — 所有函数都是模块私有的。`spec align`仅从公共声明提取词汇，因此入口点模块对所有需求始终显示Matched: 0 / SPEC_ONLY。**解决方案：** 将CLI逻辑拆分为暴露公共函数的库模块，入口点作为薄调度器。对齐需求针对库，而非入口点。

- **空文档注释：** Codex常写入无实际文本内容的文档注释语法。这些因不含词汇而对`spec align`不可见。词汇修复提示必须明确指示代理：“不要留下空文档注释。每个公共声明必须有描述其用途的文档注释，使用需求中的术语。”

- **仅内部模块（私有函数）：** 当实现逻辑完全私有时，`spec align`无法看到。这在过滤器/编解码包中常见，公共管道函数调度到私有解码器。即使类型文件触发SHALLOW，逻辑存在。**解决方案：** 要么将关键内部函数提升为公共（它们成为可测试的API表面），要么将规范词汇整合到公共管道函数的文档注释中，使需求在那里匹配。

- **字面需求与标识符匹配：** 参考项目特定字面值（包名、表号、配置键）的需求，如果实现文档注释未提及确切字面值，将显示为DRIFTED。这通常是**需求包含不应存在的项目特定细节**的迹象 — 修复需求使用通用描述，或接受词汇修复代理必须传播这些字面值。

- **“后备”框架与规范要求的实现：** 当代理为不支持的功能提议“后备”时，验证该功能是否实际由源规范要求。示例：TrueType字体cmap表解析被提议为“后备”，但实际上是TrueType字体编码解析规范所要求的。将规范要求框架为后备会创建错误优先级，并可能导致实现不完整。

- **词汇匹配≠功能正确性：** DRIFTED=0和SHALLOW=0确认词汇对齐，但无法验证实现是否真正工作。端到端测试（从真实文件提取文本、视觉渲染比较）至关重要，以捕获：
  - 编译但未执行的类型定义
  - 在真实输入上引发错误的处理管道
  - 坐标变换产生错误输出
  - 字体/编码路径静默返回空结果

### 步骤4：文档漂移检测（计划协调）

实现后，使用`plan reconcile`检测实现代码与其文档（README、文档注释等）之间的漂移：

```bash
# 检测impl ↔ 文档漂移
indexion plan reconcile --format md src/lib/

# 限制到特定文档
indexion plan reconcile --format md --doc 'README.md' src/lib/
```

`plan reconcile`补充SDD工作流中的`spec align`：
- **spec align**：requirements.md ↔ 实现代码（规范符合性）
- **plan reconcile**：实现代码 ↔ 文档（文档新鲜度）

使用`spec align`进行预合并门（CI）。使用`plan reconcile`进行功能发布后的持续文档维护。

### 步骤5：视觉端到端验证（像素差分）

对于生成视觉输出（PDF渲染、SVG导出、图像处理）的项目，基于词汇的spec对齐不足。添加像素级比较以参考渲染。

**流程：**
1. 从库生成输出（例如，`pdf svg input.pdf output.svg`）
2. 在固定DPI下光栅化到PNG（`rsvg-convert`、`puppeteer`等）
3. 从已建立工具生成参考PNG（`pdftoppm`等）
4. 使用`pixelmatch`比较 — 报告差异百分比

**阈值：**
- < 0.01%：完美像素（仅字体AA差异）
- < 0.1%：轻微字形定位差异
- < 1%：可见文本漂移或图像放置问题
- > 1%：结构渲染失败

**迭代改进：** 视觉精度需要多轮。每轮修复一个类别（字体映射→字形定位→图像CTM→颜色转换）。跟踪每轮所有PDF以捕获回归 — 修复一个PDF不得破坏其他PDF。

**视觉差分的已知限制：**
- 光栅化器之间字体抗锯齿不同（rsvg-convert vs pdftoppm）
- 亚像素渲染受平台依赖
- 0.01%可能是跨光栅器比较的实际底线

## 单个命令

### spec draft — RFC/文档 → SDD需求草稿

```bash
indexion spec draft <源文件或目录>
indexion spec draft --output requirements.md --format markdown rfc.md
indexion spec draft --profile sdd-requirement rfc.md
```

| 选项 | 默认 | 描述 |
|------|------|------|
| `--output, -o` | stdout | 输出文件路径 |
| `--format` | markdown | 输出格式：markdown, json |
| `--profile` | sdd-requirement | 草稿配置文件（KGF规范名称） |
| `--max-requirements` | 64 | 最大提取需求数 |
| `--specs-dir` | auto | KGF规范目录 |

### spec verify — 词汇差距检查

```bash
indexion spec verify --spec='requirements.md' src/lib/ --format md
```

| 选项 | 默认 | 描述 |
|------|------|------|
| `--spec` | (必需) | 规范文档glob（可重复） |
| `--format` | json | 输出格式：json, md, github-issue |
| `--focus` | all | 令牌类型过滤器：ident, text, vocab, all |
| `--max-candidates` | 200 | 输出中的最大项数 |
| `-o, --output` | stdout | 输出文件路径 |

### spec align diff — 需求级漂移

```bash
indexion spec align diff requirements.md src/lib/ --format markdown --threshold 0.3
```

报告：MATCHED, DRIFTED, SPEC_ONLY（无实现匹配的规范）、IMPL_ONLY（无规范匹配的实现）、SHALLOW（匹配到仅类型占位符而无函数实现）。

### spec align trace — 可追溯性矩阵

```bash
indexion spec align trace requirements.md src/lib/ --format json --threshold 0.3
```

为审计生成需求→实现映射。

### spec align 状态 — CI 网关

```bash
indexion spec align status requirements.md src/lib/ --fail-on any --threshold 0.3
# 使用 --fail-on 时，失败时退出码非零
```

| `--fail-on` | 描述 |
|-------------|-------------|
| `none` | 总是通过 |
| `drifted` | 如果有任何 DRIFTED 则失败 |
| `spec-only` | 如果有任何 SPEC_ONLY 则失败 |
| `shallow` | 如果有任何 SHALLOW（仅类型桩，无函数实现）则失败 |
| `any` | 在 DRIFTED、SPEC_ONLY、SHALLOW 或 CONFLICT 上失败 |

### spec align 监控 — 监控模式

```bash
indexion spec align watch --mode=diff requirements.md src/lib/
indexion spec align watch --mode=status requirements.md src/lib/
```

当规范或实现输入更改时重新运行对齐。

### spec align 建议 — 调整建议

```bash
indexion spec align suggest requirements.md src/lib/ --format tasks --agent codex
```

生成可操作的建议以关闭规范↔实现差距。

## 阈值

为 SDD 对齐命令使用 `--threshold 0.3`。默认的 `0.6` 太高，因为 SDD 接受标准是短文本与代码+文档注释匹配，而不是整个文档的相似性。

## 多语言支持

SDD 管道适用于任何具有 KGF 规范的语言。

### SDD 的 KGF 要求

为使 spec align 正常工作，该语言的 KGF 必须：
1. **在声明边捕获文档注释** — `doc` 必须非空
2. **使用正确的 PEG 替代排序** — 在 Item 替代中，DocComment 必须在声明规则之后
3. **处理文档和关键字之间的非语言文本** — `doc:DocComment?` 之后必须有 `NL?` 或 `NL*`

验证方式：`indexion kgf edges <文件>` — 如果声明边缺少 `doc=`，则 KGF 需要修复。
