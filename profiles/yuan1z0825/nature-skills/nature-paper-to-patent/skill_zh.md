# 论文转中国专利

将此文件用作专利撰写工作流的路由器。不要直接从论文摘要或贡献列表中撰写申请。

## 1. 加载工作流

读取 `manifest.yaml`，然后读取 `always_load` 下面的每个文件。

从用户文件中检测这些轴并请求：

- `source_format`：可选的 PDF、扫描 PDF、粘贴文本或混合项目；
- `task_mode`：完整撰写、权利要求集、说明书分析、技术披露、说明书迭代或论文专利审计；
- `invention_type`：算法/软件、装置/系统、工艺/材料或混合。

用一行简短的话说明检测到的值。仅加载声明中匹配的片段。仅在条件适用时加载详细参考文献。

## 2. 保持源根基

在撰写前创建稳定的源 ID：

- `P001...` 用于论文文本块；
- `E001...` 用于方程式；
- `F001...` 用于源图；
- `C001...` 用于源代码或补充证据。

正式权利要求中的每个材料特征必须映射到一个或多个源 ID。仅使用 `explicit`、`inherent`、`needs-confirmation` 或 `unsupported` 作为支持状态。将 `unsupported` 特征排除在正式权利要求之外。

不要推断发明人资格、所有权、未发表的实施方案细节、发表日期、现有技术结论或法律充分性。当事实缺失时，在正式权利要求外使用 `[TO CONFIRM: specific question]`。

## 3. 通过阶段关卡

对于 `full-draft`、`claim-set`、`disclosure-analysis` 和 `paper-patent-audit`，按顺序完成 `static/core/workflow.md` 中的阶段。持久化那里指定的中间工件。在源映射、术语总账、清单、证据总账和发明概念通过关卡之前，不要进入正式权利要求。

对于 `technical-disclosure`，遵循 `static/fragments/task/technical-disclosure.md` 中按顺序的提示参考。对于 `disclosure-iteration`，遵循 `static/fragments/task/disclosure-iteration.md` 并保留先前的草稿，而不是重新启动正式申请工作流。

对于完整申请，先撰写权利要求，然后对说明书、图、实施例和摘要进行对齐，使其与权利要求的术语和步骤顺序一致。

## 4. 生成中文正式文件

面向代理的分析可以使用用户的偏好语言。当任务是一个正式申请包时，生成中文专利交付成果：

- 权利要求书；
- 说明书；
- 说明书摘要；
- 摘要附图；
- 图标签和描述。

对于 `technical-disclosure` 和 `disclosure-iteration`，生成中文技术披露（技术交底书）作为带时间戳的 Markdown 加匹配的 DOCX，通过 `scripts/disclosure/` 渲染 Mermaid 系统或工艺图。

对于算法发明，保留源支持的核心理念公式，定义每个符号，解释每个公式的技术操作，并将公式渲染为 DOCX 中的原生可编辑 Office Math。不要使用纯 LaTeX 字符串作为可见公式。

从主要方法权利要求的有序步骤生成主流程图。其最终节点必须命名具体领域输出，例如缺陷检测结果、目标姿态、状态估计或控制指令。重用与摘要图和说明书图相同的同一主图。

## 5. 交付前验证

对于正式申请包，填充 `references/draft-schema.md` 中描述的结构化草稿，然后运行：

```bash
python scripts/validate_patent_draft.py draft.json
python scripts/build_patent_package.py draft.json --output-dir outputs --prefix patent
```

解决所有验证 `ERROR` 找到的错误。对照源审查每个 `WARNING`。当 `static/core/output-contract.md` 中未达到所需质量标准时，将结果标记为 `incomplete draft`。

对于技术披露，运行 `references/disclosure/disclosure_self_check.md` 中的内部检查，使用 `scripts/disclosure/mermaid_render.py` 渲染 Mermaid/Word 输出，并在交付前解决公式、参数、现有技术 URL 和章节一致性问题。

生成的包是发明人和专利专业人士审查的草稿辅助工具，不是可专利性意见、侵权意见或提交保证。
