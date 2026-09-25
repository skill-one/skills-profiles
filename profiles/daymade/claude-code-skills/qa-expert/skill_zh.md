# QA 专家

使用来自 Google 测试标准的方法论和 OWASP 安全最佳实践，为任何软件项目建立世界一流的 QA 测试流程。

## 使用此技能的场景

在以下情况下触发此技能：
- 为新项目或现有项目设置 QA 基础设施
- 编写标准化的测试用例（AAA 模式合规）
- 执行包含进度跟踪的全面测试计划
- 实施 OWASP Top 10 安全测试
- 以适当的严重性分类提交错误（P0-P4）
- 生成 QA 报告（每日摘要、每周进度）
- 计算质量指标（通过率、覆盖率、门禁）
- 为第三方团队交接准备 QA 文档
- 启用自主 LLM 驱动的测试执行

## 快速入门

**一键初始化**：
```bash
python scripts/init_qa_project.py <项目名称> [输出目录]
```

**创建的内容**：
- 目录结构（`tests/docs/`、`tests/e2e/`、`tests/fixtures/`）
- 跟踪 CSV 文件（`TEST-EXECUTION-TRACKING.csv`、`BUG-TRACKING-TEMPLATE.csv`）
- 文档模板（`BASELINE-METRICS.md`、`WEEKLY-PROGRESS-REPORT.md`）
- 用于自主执行的 QA 主提示
- 包含完整快速入门指南的 README

**对于自主执行**（推荐）：参见 `references/master_qa_prompt.md` - 单个复制粘贴命令可加速 100 倍。

## 核心功能

### 1. QA 项目初始化

使用所有模板初始化完整的 QA 基础设施：

```bash
python scripts/init_qa_project.py <项目名称> [输出目录]
```

创建目录结构、跟踪 CSV 文件、文档模板和用于自主执行的主提示。

**使用场景**：从零开始启动 QA 或迁移到结构化 QA 流程。

### 2. 测试用例编写

编写符合 AAA 模式（Arrange-Act-Assert）的标准、可重复的测试用例：

1. 读取模板：`assets/templates/TEST-CASE-TEMPLATE.md`
2. 遵循结构：前提条件（Arrange）→ 测试步骤（Act）→ 预期结果（Assert）
3. 分配优先级：P0（阻断）→ P4（低）
4. 包括边界情况和潜在错误

**测试用例格式**：TC-[类别]-[编号]（例如，TC-CLI-001、TC-WEB-042、TC-SEC-007）

**参考**：参见 `references/google_testing_standards.md` 获取完整的 AAA 模式指南和覆盖率阈值。

### 3. 测试执行与跟踪

**事实原则**（关键）：
- **测试用例文档**（例如，`02-CLI-TEST-CASES.md`）= **权威来源**，用于测试步骤
- **跟踪 CSV** = 执行状态仅（**不要**信任 CSV 作为测试规范）
- 参见 `references/ground_truth_principle.md` 防止文档/CSV 同步问题

**手动执行**：
1. 从类别文档中读取测试用例（例如，`02-CLI-TEST-CASES.md`）← **始终从这里开始**
2. 按文档执行测试步骤
3. 执行后立即更新 `TEST-EXECUTION-TRACKING.csv`（**每次测试后**，**不要**批量）
4. 如果测试失败，在 `BUG-TRACKING-TEMPLATE.csv` 中提交错误

**自主执行**（推荐）：
1. 从 `references/master_qa_prompt.md` 复制主提示
2. 粘贴到 LLM 会话
3. LLM 自动执行、自动跟踪、自动提交错误、自动生成报告

**创新**：比手动快 100 倍 + 跟踪零人为错误 + 自动恢复功能。

### 4. 错误报告

以适当的严重性分类提交错误：

**必填字段**：
- 错误 ID：顺序（BUG-001、BUG-002、...）
- 严重性：P0（24 小时修复）→ P4（可选）
- 重现步骤：编号、具体
- 环境：操作系统、版本、配置

**严重性分类**：
- **P0（阻断）**：安全漏洞、核心功能损坏、数据丢失
- **P1（关键）**：主要功能损坏（有替代方案）
- **P2（高）**：次要功能问题、边界情况
- **P3（中）**：装饰性问题
- **P4（低）**：文档打字错误

**参考**：参见 `BUG-TRACKING-TEMPLATE.csv` 获取完整的模板和示例。

### 5. 质量指标计算

计算全面的 QA 指标和门禁状态：

```bash
python scripts/calculate_metrics.py <路径/到/TEST-EXECUTION-TRACKING.csv>
```

**指标仪表板包括**：
- 测试执行进度（X/Y 测试，Z% 完成）
- 通过率（通过/执行 %）
- 错误分析（唯一错误、P0/P1/P2 拆分）
- 质量门禁状态（✅/❌ 每个门禁）

**质量门禁**（所有必须通过才能发布）：
| 门禁 | 目标 | 阻断 |
|------|------|------|
| 测试执行 | 100% | 是 |
| 通过率 | ≥80% | 是 |
| P0 错误 | 0 | 是 |
| P1 错误 | ≤5 | 是 |
| 代码覆盖率 | ≥80% | 是 |
| 安全性 | 90% OWASP | 是 |

### 6. 进度报告

为利益相关者生成 QA 报告：

**每日摘要**（每日结束）：
- 执行的测试、通过率、提交的错误
- 阻断（或无）
- 明天的计划

**每周报告**（每周五）：
- 使用模板：`WEEKLY-PROGRESS-REPORT.md`（由初始化脚本创建）
- 与基线比较：`BASELINE-METRICS.md`
- 评估质量门禁和趋势

**参考**：参见 `references/llm_prompts_library.md` 获取 30 多个现成的报告提示。

### 7. 安全测试（OWASP）

实施 OWASP Top 10 安全测试：

**覆盖率目标**：
1. **A01：访问控制损坏** - RLS 绕过、权限提升
2. **A02：密码学失败** - 令牌加密、密码哈希
3. **A03：注入** - SQL 注入、XSS、命令注入
4. **A04：不安全设计** - 速率限制、异常检测
5. **A05：安全配置错误** - 详细错误、默认凭证
6. **A07：身份验证失败** - 会话劫持、CSRF
7. **其他**：数据完整性、日志记录、SSRF

**目标**：90% OWASP 覆盖率（缓解 9/10 个威胁）。

每个安全测试遵循 AAA 模式，并记录具体的攻击向量。

## 第一天入职

对于加入项目的新的 QA 工程师，完成 5 小时入职指南：

**阅读**：`references/day1_onboarding.md`

**时间线**：
- 第 1 小时：环境设置（数据库、开发服务器、依赖项）
- 第 2 小时：文档审查（测试策略、质量门禁）
- 第 3 小时：测试数据设置（用户、CLI、DevTools）
- 第 4 小时：执行第一个测试用例
- 第 5 小时：团队入职 & 第 1 周计划

**检查点**：第一天结束时，环境运行，第一个测试执行，准备好第 1 周。

## 自主执行（⭐ 推荐）

使用单个主提示启用 LLM 驱动的自主 QA 测试：

**阅读**：`references/master_qa_prompt.md`

**功能**：
- 自动从上次完成的测试恢复（读取跟踪 CSV）
- 自动执行测试用例（第 1-5 周进度）
- 自动跟踪结果（每次测试后更新 CSV）
- 自动提交错误（为失败创建错误报告）
- 自动生成报告（每日摘要、每周报告）
- 自动升级 P0 错误（停止测试，通知利益相关者）

**优势**：
- 比手动执行快 100 倍
- 跟踪零人为错误
- 一致的错误文档
- 即时进度可见

**使用方法**：复制主提示，粘贴到 LLM，让其自主运行 5 周。

## 为您的项目调整

### 小型项目（50 个测试）
- 时间线：2 周
- 类别：2-3（例如，前端、后端）
- 每日：5-7 个测试
- 报告：仅每日摘要

### 中型项目（200 个测试）
- 时间线：4 周
- 类别：4-5（CLI、Web、API、DB、安全）
- 每日：10-12 个测试
- 报告：每日 + 每周

### 大型项目（500+ 个测试）
- 时间线：8-10 周
- 类别：6-8（多个组件）
- 每日：10-15 个测试
- 报告：每日 + 每周 + 双周利益相关者

## 参考文档

从捆绑的参考文档中获取详细指南：

- **`references/day1_onboarding.md`** - 新 QA 工程师的 5 小时入职指南
- **`references/master_qa_prompt.md`** - 用于自主 LLM 执行的单个命令（加速 100 倍）
- **`references/llm_prompts_library.md`** - 30 多个现成的 QA 任务提示
- **`references/google_testing_standards.md`** - AAA 模式、覆盖率阈值、快速失败验证
- **`references/ground_truth_principle.md`** - 防止文档/CSV 同步问题（测试套件完整性关键）

## 资产和模板

测试用例模板和错误报告格式：

- **`assets/templates/TEST-CASE-TEMPLATE.md`** - 带有 CLI 和安全示例的完整模板

## 脚本

用于 QA 基础设施的自动化脚本：

- **`scripts/init_qa_project.py`** - 初始化 QA 基础设施（一键设置）
- **`scripts/calculate_metrics.py`** - 生成质量指标仪表板

## 常见模式

### 模式 1：全新开始 QA
```
1. python scripts/init_qa_project.py my-app ./
2. 填写 BASELINE-METRICS.md（记录当前状态）
3. 使用 assets/templates/TEST-CASE-TEMPLATE.md 编写测试用例
4. 从 references/master_qa_prompt.md 复制主提示
5. 粘贴到 LLM → 自主执行开始
```

### 模式 2：LLM 驱动测试（自主）
```
1. 阅读 references/master_qa_prompt.md
2. 复制单个主提示（一个段落）
3. 粘贴到 LLM 会话
4. LLM 执行所有 342 个测试用例，持续 5 周
5. LLM 自动更新跟踪 CSV 文件
6. LLM 自动生成报告（每日摘要、每周报告）
```

### 模式 3：添加安全测试
```
1. 阅读 references/google_testing_standards.md（OWASP 部分）
2. 为每个 OWASP 威胁编写 TC-SEC-XXX 测试用例
3. 目标 90% 覆盖率（缓解 9/10 个威胁）
4. 在测试用例中记录缓解措施
```

### 模式 4：第三方 QA 交接
```
1. 确保所有模板已填写
2. 验证 BASELINE-METRICS.md 完整
3. 打包 tests/docs/ 文件夹
4. 包括 references/master_qa_prompt.md 以支持自主执行
5. QA 团队可以立即开始（第一天入职 → 5 周测试）
```

## 成功标准

当满足以下条件时，此技能有效：
- ✅ 测试用例可由任何工程师重复
- ✅ 质量门禁客观测量
- ✅ 错误完整记录，包含重现步骤
- ✅ 实时可见进度（CSV 跟踪）
- ✅ 启用自主执行（LLM 可执行完整计划）
- ✅ 第三方 QA 团队可立即开始测试
