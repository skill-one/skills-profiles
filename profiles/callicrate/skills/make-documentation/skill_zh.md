# 制作文档


## 使用场景

- 编写或更新 README.md、架构笔记、变更日志或发布说明
- 在添加缺失文档之前审计现有项目文档
- 从源材料起草面向客户的安全指南或合作伙伴敏感文章文本
- 编写实时访问、复现、实验室接口、工作站/服务器或操作员运行手册
- 记录笔记本、生成笔记本或表格生成型笔记本工作流
- 编写 WSL、本地、Docker 或特定环境安装文档
- 编写代理操作手册、角色文件、对等状态合同或 AI 可读工作流文档
- 仅在用户明确要求或项目已使用它们时才生成图表文档


## 不应使用场景

- 编写 API 参考文档
- 创建或更新 AGENTS.md。即使更广泛的请求也包括其他文档，也使用 `agents-md`。
- 默认情况下，当文本或表格足够时，不生成图表文件


## 工作流程

1. 运行 `[scripts/audit_documentation.py](scripts/audit_documentation.py)` 用于新文档、大规模重写、文档移动、缺失文档调查或结构不明确的情况。对于微小的显式编辑，直接检查目标文件和附近文档。
2. 仅选择由用户请求和审计证明的交付物。默认情况下，不要生成固定的文档包。
3. 按文档类型路由：使用 `[references/guide-readme.md](references/guide-readme.md)` 用于 `README.md`，使用 `[references/guide-architecture.md](references/guide-architecture.md)` 用于 `docs/architecture.md` 或仓库的现有等效文件，当用户表示文档用于代理/AI 摄入时使用 `[references/guide-ai-ingestion.md](references/guide-ai-ingestion.md)`，使用 `[references/guide-agent-ops-docs.md](references/guide-agent-ops-docs.md)` 用于被代理消费的角色/工作流文档，使用 `[references/guide-access-runbook.md](references/guide-access-runbook.md)` 用于实时访问、复现、操作员、实验室接口或能力账本，使用 `[references/guide-notebook-documentation.md](references/guide-notebook-documentation.md)` 用于笔记本说明，使用 `[references/guide-install-runbook.md](references/guide-install-runbook.md)` 用于 WSL/本地/Docker 安装文档，使用 `[references/guide-security-article.md](references/guide-security-article.md)` 用于合作伙伴敏感安全文章，使用 `[references/guide-changelog.md](references/guide-changelog.md)` 用于 `CHANGELOG.md` 或发布说明。如果 AGENTS.md 成为范围的一部分，将该文件切换到 `agents-md` 而不是扩展此技能。
4. 仅在用户明确要求图表文档或项目已维护它们时使用 `[references/guide-diagrams.md](references/guide-diagrams.md)`。
5. 对于大型文档、迭代报告、功能清单、概念框架或证据审计修订，在编写前加载 `[references/source-discovery-and-heading-stability.md](references/source-discovery-and-heading-stability.md)`。
6. 对于概念或策略文档，在架构深度之前包含一个可见的第一个可使用的工作流，以便读者在吸收模型之前可以执行一小部分。
7. 保持输出源支持且简洁。保留用户提供的术语，并避免改变领域含义或语气的通用重写。
8. 当后续实现工作涉及相同的笔记本、文档或文件夹时，保留先前请求的文档。如果存在风险，无关的实现更改已删除先前的文档，则在完成前重新打开已触及的文档。
9. 在完成前使用 `[references/review-checklist.md](references/review-checklist.md)` 审查结果。


## 反模式

- 错误：从生成的 README、审查包、AI 评论或过时评论中总结笔记本。正确：跟踪可执行单元格、导入、小部件、SQL、配置和输出，然后编写简短说明。
- 错误：在内存中从文件夹移动后编写文件夹合同文档。正确：审计树并一起更新父文档和子文档。
- 错误：在围绕实现编写文档时重复验证器、模式、CLI、表格列表或事实来源模块。正确：扫描现有事实来源资产并链接到它们。
- 错误：除非用户明确要求，否则将工作流文档绑定到 VS Code、一个编辑器或一个 UI。正确：声明与编辑器无关的初始状态和执行平面。
- 错误：除非它们是必需的架构字段，否则在面向用户的文档中保留元标签，如 `review packet`、`AI-generated summary` 或 `analysis artifact`。正确：使用与受众匹配的自然节名。
- 错误：将仅用于演示的标志或过滤器标记为未来的产品接口。正确：将测试脚手架与持久的用户或代理接口分开。


## 确定性工具

| 工具 | 使用场景 | 结果 |
|------|----------|---------|
| `[scripts/audit_documentation.py](scripts/audit_documentation.py)` | 在编写文档前需要确定性清单 | 当前状态文档审计 |


## 参考资料

- `[references/guide-readme.md](references/guide-readme.md)` - README 工作流
- `[references/guide-architecture.md](references/guide-architecture.md)` - 架构文档
- `[references/guide-ai-ingestion.md](references/guide-ai-ingestion.md)` - 紧凑型机器摄入文档模式
- `[references/guide-agent-ops-docs.md](references/guide-agent-ops-docs.md)` - 代理消费的角色、指令、对等状态和执行平面文档
- `[references/guide-access-runbook.md](references/guide-access-runbook.md)` - 实时访问、复现、接口和能力账本
- `[references/guide-notebook-documentation.md](references/guide-notebook-documentation.md)` - 笔记本说明和可运行顺序保留
- `[references/guide-install-runbook.md](references/guide-install-runbook.md)` - 特定环境安装文档
- `[references/guide-security-article.md](references/guide-security-article.md)` - 合作伙伴敏感安全文章工作流
- `[references/guide-changelog.md](references/guide-changelog.md)` - 变更日志和发布说明
- `[references/guide-diagrams.md](references/guide-diagrams.md)` - 仅在可选的情况下使用图表工作流
- `[references/review-checklist.md](references/review-checklist.md)` - 完成前的审查通过
- `[references/source-discovery-and-heading-stability.md](references/source-discovery-and-heading-stability.md)` - 大型文档源发现和稳定标题检查
- `[references/ascii-art-standards.md](references/ascii-art-standards.md)` - 图表在范围内时的图表格式标准
