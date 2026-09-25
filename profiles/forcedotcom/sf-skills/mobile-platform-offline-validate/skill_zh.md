# 审核LWC移动离线

对一个Lightning Web Component运行结构化的离线预置合规检查，生成一个包含发现问题和代码级修复建议的报告，以使组件符合Komaci对Salesforce Mobile App Plus和Field Service Mobile App的静态分析要求。

## 使用场景

- 用户针对特定LWC请求"移动离线审核"、"Komaci检查"或"离线预置审计"。
- 准备在Salesforce Mobile App Plus或Field Service Mobile App离线模式下发布的组件。
- 调查离线分析器报告的预置失败问题。

**不使用此技能的情况**：

- 构建使用原生移动功能的LWC（条码扫描器、生物识别、位置等）— 使用`mobile-platform-native-capabilities-integrate`。
- 通用LWC代码审核 — 使用相应的领域技能（`reviewing-lws-security`、`reviewing-lwc-rtl`、`accessibility-code-review`）。

## 前置条件

- 组件路径（`modules/…`下的LWC包）。
- 可访问组件的JS/TS和HTML模板。
- 本地Node + npm；能够运行`npx eslint`并使用`@salesforce/eslint-plugin-lwc-graph-analyzer`插件。

## 知识库

[移动离线基础](references/grounding.md)解释了三种违规类别以及每个类别为何会阻止离线预置。在判断前请先阅读它。以下每个审核者的参考是规则和修复建议的权威来源：

- 内联GraphQL线配置：[内联GraphQL审核者](references/inline-graphql.md)
- `lwc:if`条件渲染兼容性：[lwc:if审核者](references/lwc-if.md)
- Komaci ESLint静态分析：[Komaci ESLint审核者](references/komaci-eslint.md)

## 工作流程

### 第1步 — 确定审核范围

识别组件包：`.html`、`.js`/`.ts`。CSS和元文件不在离线预置的审核范围内。如果包包含多个HTML模板，所有模板都将被审核。

### 第2步 — 阅读基础和每个审核者的参考

在判断前，完整阅读[移动离线基础](references/grounding.md)和三个每个审核者的参考。在报告每个发现时引用具体的审核者，以便报告可审计。

### 第3步 — `lwc:if` / `lwc:elseif` / `lwc:else`（HTML）

遍历包中的每个`.html`文件，并应用[lwc:if审核者](references/lwc-if.md)中的规则。对于每个`lwc:if={…}`、`lwc:elseif={…}`或`lwc:else`的出现，发出一个包含精确`if:true` / `if:false`重写的发现 — 包括必要的嵌套以保留`lwc:elseif`和`lwc:else`的语义。

### 第4步 — `@wire`中的内联GraphQL（JS）

遍历包中的每个`.js`/`.ts`文件，并应用[内联GraphQL审核者](references/inline-graphql.md)中的规则。对于每个直接引用`gql`模板字面量（或通过顶层常量引用）的`@wire`，发出一个命名具体获取器并显示重写后的`@wire`配置的发现。

### 第5步 — Komaci ESLint检查（JS）

使用捆绑脚本对包的JS文件运行Komaci ESLint分析器。它应用了`@salesforce/eslint-plugin-lwc-graph-analyzer`推荐的规则集，并启用了`bundleAnalyzer`处理器。

```bash
scripts/run-komaci.sh path/to/component.js
```

该脚本要求`@salesforce/eslint-plugin-lwc-graph-analyzer`可以从工作目录解析，并且组件的兄弟HTML模板必须与JS文件相邻（插件的`bundleAnalyzer`处理器使用它们来解析离线数据图）。输出是ESLint `--format json`在标准输出上。

对于输出中的每个`messages[*]`条目，按`ruleId`分组，并在[Komaci ESLint审核者](references/komaci-eslint.md)中查找每个规则的修复建议。为每个（规则，行）对发出一个发现，包含来自参考的精确修复文本；不要编造新的建议。如果脚本在运行时环境中不可用，请参考参考中的手动`npx eslint ...`调用。

### 第6步 — 生成报告

以以下格式发出报告：

```text
## 移动离线（Komaci预置）
- <审核者> — <文件>:<起始行>:<起始列>-<结束行>:<结束列> — <类型>
  描述：<来自审核者参考的逐字文本>
  意图分析：<来自审核者参考的逐字文本>
  建议操作：<来自审核者参考的逐字文本>
  代码：|
    <从起始行到结束行的源代码片段，跨多行时可选但推荐>
  已应用：是/否

## 总结
- 发现了<n>个问题；修复了<m>个；推迟了<k>个（原因）
```

对于Komaci ESLint发现，从ESLint消息的`line`/`column`/`endLine`/`endColumn`中获取`startLine`/`startColumn`/`endLine`/`endColumn`。对于内联GraphQL和`lwc:if`发现，提供你在源代码中观察到的行/列范围。如果`endLine`/`endColumn`对某个发现不可用，则回退到`<文件>:<起始行>`并省略尾部范围。

在每次发现中引用审核者（内联GraphQL / lwc:if / Komaci ESLint规则ID）。

### 第7步 — 应用修复

在用户要求修复时直接应用修复建议。如果修复建议与组件在离线外行为冲突（例如，开发者依赖`lwc:elseif`以提高可读性，而用户尚未发布到移动离线），则在推迟列表中显示冲突，而不是静默重写。

## 验证清单

- [ ] 每个`lwc:if` / `lwc:elseif` / `lwc:else`被标记或不存在。
- [ ] 每个`@wire`引用`gql`都进行了检查；内联查询提取到获取器中。
- [ ] 实际运行了Komaci ESLint分析器；发现引用了真实的规则ID，而不是编造的。
- [ ] 每个发现引用了原始审核者或规则ID。
- [ ] 没有上述三个类别之外的修复建议（其他问题属于其他技能）。

## 故障排除

- **`npx eslint`找不到插件** — 在工作区中安装`@salesforce/eslint-plugin-lwc-graph-analyzer`，或使用固定的本地安装路径。插件是Komaci规则的权威来源。
- **与`bundleAnalyzer`相关的错误** — 推荐的配置驱动捆绑处理器；不要移除它。处理器期望可以找到兄弟HTML文件。如果在一个精简的JS文件上运行，请在临时目录中提供匹配的HTML。
- **对于你预期会失败的组件没有发现** — 确认应用了推荐的规则集（而不仅仅是带有空规则的`bundleAnalyzer`）。某些规则需要HTML与JS同时存在。
- **发现重复`lwc:if`来自专用审核者** — Komaci插件不检查模板；`lwc:if`检查仅限HTML，来自第3步。第5步的发现仅限JS。
