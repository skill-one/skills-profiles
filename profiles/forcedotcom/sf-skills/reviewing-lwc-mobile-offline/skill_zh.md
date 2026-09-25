# 审核LWC移动离线

对 Lightning Web 组件运行结构化的离线预置合规检查，生成发现的问题报告以及代码级别的修复建议，以使组件符合 Salesforce Mobile App Plus 和 Field Service Mobile App 的 Komaci 静态分析要求。

## 使用场景

- 用户针对特定 LWC 请求“移动离线审核”、“Komaci 检查”或“离线预置审计”。
- 准备在 Salesforce Mobile App Plus 或 Field Service Mobile App 离线模式下发布的组件。
- 调查离线分析器报告的预置失败问题。

**不使用此技能的情况**：

- 构建 使用原生移动功能（条形码扫描器、生物识别、位置等）的 LWC — 使用 `using-mobile-native-capabilities`。
- 通用 LWC 代码审核 — 使用相应的领域技能 (`reviewing-lws-security`, `reviewing-lwc-rtl`, `accessibility-code-review`)。

## 前置条件

- 组件路径（`modules/…` 下的 LWC 打包）。
- 访问组件的 JS/TS 和 HTML 模板。
- 本地 Node + npm；能够运行 `npx eslint` 并使用 `@salesforce/eslint-plugin-lwc-graph-analyzer` 插件。

## 知识库

[移动离线基础](references/grounding.md) 解释了三种违规类别以及每种类别为何会阻止离线预置。在判断前请先阅读它。以下每个审核者的参考是规则和修复建议的权威来源：

- 内联 GraphQL 线路配置：[内联 GraphQL 审核者](references/inline-graphql.md)
- `lwc:if` 条件渲染兼容性：[lwc:if 审核者](references/lwc-if.md)
- Komaci ESLint 静态分析：[Komaci ESLint 审核者](references/komaci-eslint.md)

## 工作流程

### 第 1 步 — 确定审核范围

识别组件打包：`.html`，`.js`/`.ts`。CSS 和元文件不在离线预置的审核范围内。如果打包包含多个 HTML 模板，所有模板都将被审核。

### 第 2 步 — 阅读基础和每个审核者的参考

在判断前，完整阅读 [移动离线基础](references/grounding.md) 和三个每个审核者的参考。在报告每个发现时引用具体的审核者，以便报告可审计。

### 第 3 步 — `lwc:if` / `lwc:elseif` / `lwc:else` (HTML)

遍历打包中的每个 `.html` 文件，并应用 [lwc:if 审核者](references/lwc-if.md) 中的规则。对于每个 `lwc:if={…}`，`lwc:elseif={…}` 或 `lwc:else` 的出现，报告一个包含精确 `if:true` / `if:false` 重写的发现，包括嵌套以保留 `lwc:elseif` 和 `lwc:else` 语义所需的嵌套。

### 第 4 步 — `@wire` 中的内联 GraphQL (JS)

遍历打包中的每个 `.js`/`.ts` 文件，并应用 [内联 GraphQL 审核者](references/inline-graphql.md) 中的规则。对于直接引用 `gql` 模板字面量（或通过顶层常量引用）的每个 `@wire`，报告一个命名具体获取器并显示重写后的 `@wire` 配置的发现。

### 第 5 步 — Komaci ESLint 检查 (JS)

使用捆绑脚本对打包的 JS 文件运行 Komaci ESLint 分析器。它应用了推荐的 `@salesforce/eslint-plugin-lwc-graph-analyzer` 规则集，并启用了 `bundleAnalyzer` 处理器。

```bash
scripts/run-komaci.sh path/to/component.js
```

该脚本要求 `@salesforce/eslint-plugin-lwc-graph-analyzer` 能够从工作目录解析，并且组件的兄弟 HTML 模板必须与 JS 文件相邻（该插件的 `bundleAnalyzer` 处理器使用它们来解析离线数据图）。输出是 ESLint `--format json` 在标准输出上。

对于输出中的每个 `messages[*]` 条目，按 `ruleId` 分组，并在 [Komaci ESLint 审核者](references/komaci-eslint.md) 中查找每个规则的修复建议。按 (规则, 行) 对报告一个发现，并包含来自参考的精确修复文本；不要编造新的建议。如果脚本在运行环境中不可用，请参考参考中的手动 `npx eslint ...` 调用。

### 第 6 步 — 生成报告

以以下格式报告：

```
## 移动离线 (Komaci 预置)
- <reviewer> — <file>:<startLine>:<startColumn>-<endLine>:<endColumn> — <type>
  描述: <来自审核者参考的逐字文本>
  意图分析: <来自审核者参考的逐字文本>
  建议操作: <来自审核者参考的逐字文本>
  代码: |
    <从 startLine 到 endLine 的源代码片段，跨多行时可选但推荐>
  已应用: 是/否

## 总结
- <n> 个问题发现；<m> 个已修复；<k> 个已推迟（原因）
```

对于 Komaci ESLint 发现，从 ESLint 消息的 `line`/`column`/`endLine`/`endColumn` 中获取 `startLine`/`startColumn`/`endLine`/`endColumn`。对于内联 GraphQL 和 `lwc:if` 发现，提供你在源代码中观察到的行/列范围。如果 `endLine`/`endColumn` 对某个发现不可用，则回退到 `<file>:<startLine>` 并省略尾部范围。

在每次发现中引用审核者（内联 GraphQL / lwc:if / Komaci ESLint 规则 ID）。

### 第 7 步 — 应用修复

在用户请求修复时直接应用修复。如果修复与组件在离线外行为冲突（例如，开发者依赖 `lwc:elseif` 以提高可读性，而用户尚未发布到移动离线），则在推迟列表中显示冲突，而不是静默重写。

## 验证清单

- [ ] 每个 `lwc:if` / `lwc:elseif` / `lwc:else` 被标记或不存在。
- [ ] 每个 `@wire` 引用 `gql` 都已检查；内联查询提取到获取器中。
- [ ] Komaci ESLint 分析器确实运行了；发现引用了真实的规则 ID，而不是编造的。
- [ ] 每个发现引用了原始审核者或规则 ID。
- [ ] 没有上述三个类别之外的修复（其他问题属于其他技能）。

## 故障排除

- **`npx eslint` 找不到插件** — 在工作区中安装 `@salesforce/eslint-plugin-lwc-graph-analyzer`，或使用固定的本地安装路径。该插件是 Komaci 规则的权威来源。
- **与 `bundleAnalyzer` 相关的错误** — 推荐的配置驱动捆绑处理器；不要移除它。处理器期望可以找到兄弟 HTML 文件。如果在剥离的 JS 文件上运行，请在临时目录中提供匹配的 HTML。
- **预期的组件没有发现** — 确认应用了推荐的规则集（而不仅仅是空的 `bundleAnalyzer`）。某些规则需要 HTML 与 JS 同时存在。
- **发现重复 `lwc:if` 来自专用审核者** — Komaci 插件不检查模板；`lwc:if` 检查仅限于 HTML，来自第 3 步。第 5 步的发现仅限于 JS。
