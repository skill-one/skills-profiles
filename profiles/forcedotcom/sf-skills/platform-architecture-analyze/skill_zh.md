# 分析架构（架构良好性审查）

使用 **Salesforce Well-Architected** 框架对 Salesforce DX 项目进行评分，并生成一份有据可查、诚实的报告：一个包含代码和元数据的支柱评分表，以及一个用于治理/流程问题的手动检查清单（本地仓库无法揭示的问题）。

这项技能是一个 **协调器**。它不会重新实现静态分析——它驱动插件已提供的分析技能，并将它们的输出映射到 Well-Architected 支柱上。它是 **只读** 的：它进行评分和建议；它从不编辑、部署或删除。

它还支持 `architecture-review` 代理，该代理以专用的只读审查者身份运行此工作流。调用代理进行端到端审查；当你希望在当前会话中直接使用工作流时，直接使用此技能。

## 能力解析

1. **技能协调审查**（此技能）——通过委托给现有技能/MCP 工具运行可观察的检查，对每个子支柱进行评分，并发出手动检查清单。
2. **直接 CLI / grep** —— 仅用于评估评分手册中命名的轻量级结构信号（共享关键字、遗留技术文件类型、部署策略）。可以独立使用，但会跳过此技能提供的支柱评分和治理检查清单。
3. **API** —— 不适用。

## 评分手册（首先阅读这些）

评分之前，请阅读三个参考文件——它们是事实来源：

- [`references/well-architected-rubric.md`](references/well-architected-rubric.md) —— 完整的支柱 → 子支柱 → 标准树，每个标准都标记为 `[可观察]` 或 `[手动]`。
- [`references/observable-checks.md`](references/observable-checks.md) —— 每个 `[可观察]` 标准都映射到其检测（技能 / MCP 工具 / grep 模式）以及它标记的反模式。
- [`references/manual-review-checklist.md`](references/manual-review-checklist.md) —— `[手动]` 标准作为可复制粘贴的治理检查清单。

## 工作流

### 第 1 步——确定项目范围

```bash
# 包目录 + API 版本
cat sfdx-project.json
```

确定：

- **包目录**（来自 `packageDirectories[].path`）——源代码所在的目录。
- **清单**——统计 Apex 类、触发器、LWC 包、Aura、流程、对象：
  ```bash
  find <pkgdir> -name '*.cls' | wc -l
  find <pkgdir> -name '*.trigger' | wc -l
  find <pkgdir> -name '*.js-meta.xml' | wc -l   # LWC 包
  ```
- **工具信号**——仓库中是否有测试（`*Test.cls`，`__tests__/`）、CI（`.github/workflows/`）、代码格式化（`.eslintrc*`，`.prettierrc*`）、`package.xml` 与源代码/包策略？
- **组织连接**——`sf org display --json` 成功 → 组织相关的检查（OWD、权限集）适用；否则将它们标记为手动。

记录报告标题的范围内行。

### 第 2 步——运行可观察的检查（委托；不要重新扫描）

查阅 `references/observable-checks.md`。对于重负载，委托：

- **Apex 安全 + 性能** → `dx-code-analyzer-run`。它运行 `sf code-analyzer` 并按严重程度对发现进行分类。将它的规则映射到评分手册：
  - `ApexSOQLInjection`，`ApexCRUDViolation`，`ApexInsecureEndpoint`，`ApexBadCrypto` → **安全**
  - `ApexSharingViolations` → **安全**（共享） / **组合**（分离）
  - `OperationWithLimitsInLoop`，`OperationWithHighCostInLoop` → **可靠** / **自动化**
  - `AvoidDebugStatements` → **自动化**
- **内联 SOQL 解析 + 选择性、编译时诊断** → `platform-lsp-integrate` (`apex_diagnostics`，`lwc_diagnostics`，`check_soql_selectivity`) 当 `lsp_health` 为绿色时 → **可靠** / **自动化**。
- **OWD / 共享模型 / 权限集** → `platform-metadata-retrieve` + `sf org` 检查，仅当连接到组织时 → **安全**。

对于轻量级结构信号，直接使用 grep（模式在 `references/observable-checks.md` 中），例如：

```bash
# 安全——缺少共享关键字的类
grep -rLE 'with(out)? sharing|inherited sharing' --include='*.cls' <pkgdir>

# 故意——遗留技术仍然存在
find <pkgdir> -name '*.workflow-meta.xml' -o -name '*.flowDefinition-meta.xml'
grep -rl '@future' --include='*.cls' <pkgdir>

# 组合——部署策略
ls manifest/package.xml 2>/dev/null            # package.xml 驱动（PoC 之后的反模式）
grep -l '"path"' sfdx-project.json             # 源代码/包策略

# 组合——运行时配置在自定义设置与 CMT
find <pkgdir> -path '*objects*' -name '*.object-meta.xml' | xargs grep -l 'CustomSetting' 2>/dev/null
```

收集每个发现，附带 `文件:行` 证据。没有证据的检查 **不是** 通过，**不是** 失败——它是“不可观察的”，并移至手动检查清单。

### 第 3 步——对每个可观察的子支柱进行评分

使用 `references/observable-checks.md` 中的阈值，对每个子支柱分配 ✅ / ⚠️ / ❌：

- **✅** 在可观察的检查中未发现该子支柱的反模式。
- **⚠️** 低/中等发现，或只有部分标准可观察。
- **❌** 严重/高发现（例如 SOQL 注入、FLS 绕过、大规模 SOQL-in-loop）。

然后将子支柱的判定结果汇总到支柱判定（最差情况，并附注）。

### 第 4 步——发出手动检查清单

将 `references/manual-review-checklist.md` 中的 `[手动]` 标准复制到报告中作为未选中的项目，按支柱分组。明确标记该部分：**“未自动评分——与团队一起评估。”** 不要猜测这些；目的是向开发者提供一个结构化的治理检查清单，而不是伪造分数。

### 第 5 步——报告

使用以下格式生成一份报告。首先列出支柱判定，然后是可观察的发现（Trusted/安全优先——永远不要将安全隐藏在风格问题下），然后是手动检查清单，然后是建议的下一步操作，这些操作命名将应用每个修复的技能。

```text
Well-Architected Review — <项目名称>
范围：<包目录>，<N 类 / M 触发器 / K LWC>，测试：<是/否>，CI：<是/否>，组织：<连接的别名 / 无>

支柱判定
  🛡️ Trusted     <✅|⚠️|❌>  (安全 …, 合规 …, 可靠 …)
  ⚡ Easy         <✅|⚠️|❌>  (故意 …, 自动化 …, 互动 …)
  🔁 Adaptable    <✅|⚠️|❌>  (弹性 …, 组合 …)

可观察的发现  (从代码 + 元数据评分)
  子支柱 | 判定 | 发现 | 证据（文件:行 / 工具）

手动审查  (未自动评分——与团队一起评估)
  [ ] <项目>  …

建议的下一步操作
  - <最高信号修复> → 通过 `<技能>`
```

## 示例

### 示例 1——“这个项目架构良好吗？”

确定项目范围，运行所有可观察的检查（将 Apex 分析委托给 `dx-code-analyzer-run`），评分所有三个支柱，发出完整的手动检查清单，并报告。这是默认的完整审查。

### 示例 2——“审查我项目的安全和治理限制风险”

缩小到 **安全** 和 **可靠/自动化** 子支柱：运行 `dx-code-analyzer-run` 并使用安全+性能选择器，使用 `platform-lsp-integrate` `check_soql_selectivity` 进行选择性，grep 缺少共享关键字。评分这些子支柱；仍然发出安全/合规的手动项目（安全矩阵、加密策略）。除非要求，否则跳过 Adaptable 深入分析。

### 示例 3——“在我们为发布打包之前运行一次架构良好性检查”

完整审查，侧重 **组合**（可打包性——CMT 与自定义设置、松散耦合、`LATEST` 别名、无 `package.xml`-驱动部署）和 **弹性**（源代码跟踪、CI、无失败部署）。在报告中首先列出可打包性就绪判定。

## 失败模式

| 症状 | 原因 | 恢复 |
|---|---|---|
| `dx-code-analyzer-run` 报告分析器未安装 | 代码分析器 v5 缺失 | 在报告中记录；回退到基于 grep 的结构检查（Apex）并标记 PMD 仅标准为“不可观察”。 |
| `sf org display` 失败 | 未连接组织 | 将 OWD / 权限集 / 组织元数据标准标记为手动；仅评分基于文件的判定标准。 |
| LSP 工具返回 `lsp_disabled` / `no_apex_workspace` | LSP 关闭或无工作区 | 跳过基于 LSP 的检查；依赖 `dx-code-analyzer-run` + grep。注意差距。 |
| 无 `sfdx-project.json` | 不是 SFDX 项目 | 停止——此技能审查 SFDX 项目。通知开发者。 |
| 仓库巨大，扫描缓慢 | 项目范围的 PMD + 图构建 | 将 `dx-code-analyzer-run` 限制在包目录内；注意跨文件（sfge）发现可能不完整。 |

## 规则

- 评分之前阅读三个 `references/*.md` 文件——评分手册是事实来源。
- 将可观察的检测委托给现有技能/MCP 工具；仅使用 grep 来查找评分手册命名的轻量级结构信号。
- 每个可观察的发现都带有 `文件:行`（或工具结果）证据。无证据 → 手动检查清单，不是评分表。
- 从推断中从未评分 `[手动]` 治理标准——将其列供人工审查。
- 只读：建议修复并命名应用它们的技能（`platform-apex-generate` 用于 Apex 编写/触发器重构）；永不编辑、部署或删除。
- 首先列出 Trusted/安全发现；不要将安全隐藏在风格小节下。
- 揭示零发现子支柱（“在可观察检查中未发现问题”）而不是省略它们。
