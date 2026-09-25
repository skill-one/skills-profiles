# 为 Oracle 到 PostgreSQL 迁移创建 Bug 报告

## 使用场景

- 记录因 Oracle 和 PostgreSQL 行为差异导致的缺陷
- 为 Oracle 到 PostgreSQL 迁移项目编写或审查 Bug 报告

## Bug 报告格式

使用 [参考资料/BUG-REPORT-TEMPLATE.md](references/BUG-REPORT-TEMPLATE.md) 中的模板。每份报告必须包含：

- **状态**：✅ 已解决、⛔ 未解决 或 ⏳ 进行中
- **组件**：受影响的端点、存储库或存储过程
- **测试**：相关的自动化测试名称
- **严重程度**：低 / 中 / 高 / 严重 —— 基于影响范围
- **问题**：预期的 Oracle 行为与观察到的 PostgreSQL 行为
- **场景**：包含种子数据、操作、预期结果和实际结果的有序复现步骤
- **根本原因**：导致缺陷的特定 Oracle/PostgreSQL 行为差异
- **解决方案**：所做的更改或所需更改，并明确文件路径
- **验证**：在两个数据库上确认修复的步骤

## Oracle 到 PostgreSQL 指导

- **Oracle 是事实来源** —— 从 Oracle 基线中框定预期行为
- 明确指出数据层的细微差别：空字符串与 NULL、类型强制严格性、排序规则、序列值、时区、填充、约束
- 除非为正确行为所必需，否则应避免客户端代码更改；提出时，应清晰记录并说明理由

## 写作风格

- 简洁语言，短句，清晰的下一步行动
- 始终使用现在时或过去时
- 使用项目符号和编号列表表示步骤和验证
- 最小化 SQL 示例和日志作为证据；省略敏感数据并保持代码片段可复现
- 坚持现有的运行时/语言版本；避免推测性修复

## 文件名规范

将 Bug 报告保存到 `.github/oracle-to-postgres-migration/Reports/{ProjectName}/BUG_REPORT_<DescriptiveSlug>.md`，其中：

- `{ProjectName}` 是项目的程序集/文件夹名称，空格规范化为 `-`（例如 `MyApp.DataAccess`）
- `<DescriptiveSlug>` 是描述缺陷的短 PascalCase 标识符（例如 `EmptyStringNullHandling`、`RefCursorUnwrapFailure`）
