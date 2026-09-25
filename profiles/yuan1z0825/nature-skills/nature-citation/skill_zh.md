# Nature 引证 — 路由器

## 路由协议

对于新任务，加载以下核心和匹配资源。重用已加载的指导进行后续操作；只有当任务需要时才加载更多。

### 1. 加载清单和核心层

读取 [manifest.yaml](manifest.yaml)。然后读取 `always_load` 下列出的每个文件：

- `static/core/principles.md` — 技能生成的产出内容、严格的期刊范围、来源层级以及搜索质量规则。
- `static/core/workflow.md` — 七步工作流程和最终报告格式。

### 2. 无内容轴 — 直接在行内确认范围和语言

与其他 nature-* 技能不同，nature-citation 没有片段轴。其变化是运行时参数，而不是不同的内容体：

- **期刊范围** — `Nature系列` / `CNS` / `CNS及子刊` / 仅旗舰期刊。从用户的措辞中读取它（参见 `core/principles.md`），并将其作为 `--scope` 传递给脚本。
- **用户语言** — 如果用户使用中文或请求中文指导，读取 `static/core/chinese-mode.md`（中文注释、英文搜索查询）。
- **输入长度** — 如果有超过 ~10 个片段，则切换到 `references/script-usage.md` 中的批量长文章策略。

在搜索之前，用一句话说明检测到的范围和日期限制。

### 3. 运行工作流程

遵循 `core/workflow.md` 中的七个步骤：分段、解析、搜索、保守地评估支持、验证完整的结构化作者元数据、导出一个参考文献管理器文件，并在必要时生成评审工件。仅在生成时才将 HTML 浏览器路径放在第一位。当有网络访问时，优先使用 `scripts/nature_citation.py` 进行搜索/导出；打开 `references/script-usage.md` 获取其完整标志列表和长文章批量策略。当 DOI 元数据缺少给定名时，通过 PMID 重新获取记录或验证其与出版商，而不是导出仅包含姓氏的 `AU` 字段。

仅因为论文标题相关就将其作为支持呈现，并且不要在检查摘要或出版商页面之前引用仅包含元数据的候选者。不要编造缺失的参考文献字段。

### 4. 仅在需要时才查找参考文献

`references/` 下面的文件是深度参考文献，不是默认值。根据清单中的 `references.on_demand` 表格按需打开它们：

- 运行脚本、完整标志、长文章批量 → `references/script-usage.md`。
- 将主张转换为搜索查询和支持等级 → `references/search-strategy.md`。
- 精确的 Nature/CNS 期刊家族边界 → `references/journal-scope.md`。
- RIS / EndNote / Zotero RDF 导出细节 → `references/ris-endnote.md`。
