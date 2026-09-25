<!-- adk-managed-skill -->

# 审核LWC的RTL

对 Lightning Web Component 运行结构化的从右到左（RTL）国际化合规性检查，生成发现的问题报告以及代码级别的修复建议，以使组件符合 Salesforce 的 RTL 指南。

## 使用场景

- 用户要求对特定 LWC 进行 "RTL 审核检查"、"i18n 检查"、"RTL 合规性检查" 或 "RTL 审计"。
- 准备在 RTL 地区（阿拉伯语、希伯来语、波斯语、乌尔都语）发布组件。
- 调查在 RTL 环境中报告的布局缺陷。
- 验证 CSS 重构后的 SLDS 类使用情况。

**不要使用此技能：**
- 构建新组件（使用 `experience-lwc-generate`）。
- 修改 SLDS 类本身（使用 `design-systems-slds-apply` 或 `design-systems-slds2-migrate`）。
- 可访问性或安全性审核——使用相关工具进行单独的检查。
- 在修复落地后通过功能标志进行限制（在修复落地后应用功能标志限制）。

## 前置条件

- 组件路径（`modules/…` 下的 LWC 包）。
- 可以访问组件的 HTML 模板、JS/TS 和 CSS。

## 知识库

参考是事实来源。不要凭记忆总结——打开参考，应用指南，并在报告中引用你使用的具体章节。

- RTL 国际化：[RTL 专家](references/rtl-expert.md)

## 工作流程

### 第 1 步 — 确定审核范围

收集组件路径并确定要审核的文件：`.html`、`.js`/`.ts`、`.css`，以及同一团队拥有的、在目标组件中调用的子组件。

注意任何现有的功能标志（例如，`Aura.org.rtlPhase1FixEnabled`）——需要代码更改的发现必须遵守它们。

### 第 2 步 — 阅读知识库

在判断之前，从上到下阅读 [RTL 专家](references/rtl-expert.md)。它列出了物理属性到逻辑属性的映射、双向文本处理模式，以及——关键的是——覆盖通用 RTL 建议的 SLDS 限制。

### 第 3 步 — CSS 检查

对包中的每个 `.css` 文件运行确定性扫描器。**扫描器仅匹配 CSS 声明——永远不要在 HTML `class="…"` 属性中标记 SLDS 类名（见第 5 步）。** 内联 `style="…"` 属性必须单独扫描（可以通过将它们提取到临时文件中，或手动检查 HTML 并应用相同规则）。

```bash
"<skill_dir>/scripts/scan-rtl-css.sh" <cssFile1> [<cssFile2> ...]
```

每行输出具有 `<file>:<line>: <property>: <value> -> <logical-property>: <logical-value>` 的形状。扫描器对声明进行标记化（在 `{…}` 内部以 `;` 分隔），因此压缩的多声明行每条物理声明和选择器名称都不会被重写。将每行翻译成第 6 步的要点（`<file>:<line> — <pattern> → <logical property>` 加上一个句子的修复）。空输出是有效结果——在报告中记录为 "未发现问题"。扫描器识别的模式（与脚本的 regex 保持同步——不要在此处添加规则而不更新 `scan-rtl-css.sh`）：

- `left` / `right` → `inset-inline-start` / `inset-inline-end`
- `margin-left` / `margin-right` → `margin-inline-start` / `margin-inline-end`
- `padding-left` / `padding-right` → `padding-inline-start` / `padding-inline-end`
- `text-align: left` / `right` → `text-align: start` / `end`
- `border-left-*` / `border-right-*` → `border-inline-start-*` / `border-inline-end-*`
- `float: left` / `float: right` → `float: inline-start` / `float: inline-end`（或移除并使用 flex/grid）
- `transform: translateX(...)` — 标记；翻转符号或使用逻辑替代方案

带明确角落的 `border-radius` 不会自动扫描——手动检查角落简写并转换为逻辑角落变体。

### 第 4 步 — HTML / JS 检查

检查模板和 JS：

- 图标翻转提示——仅标记具有方向语义且出现在**纯 HTML `<img>` / 内联 SVG / 原始 Unicode / background-image CSS**中的图标。**不要标记 LWC 模板中的 `<lightning-icon>`**（包括方向实用工具名称如 `utility:chevronright`、`utility:chevronleft`、`utility:back`、`utility:forward`）；`lightning-icon` 通过 Lightning 图标服务渲染，该服务在 RTL 地区自动镜像方向实用工具图标。将其与 SLDS 实用工具类相同方式处理。
- `dir` 属性使用情况——确认它来自地区设置，而不是硬编码。
- 键盘箭头键语义——左/右箭头处理器在方向导航时（选项卡栏、滑块、树展开/折叠）应交换 RTL 中。
- 方向 Unicode 控制符——确保用户生成的文本在渲染时不被剥离 RLM/LRM 标记。
- 内联 `style="…"` 带物理属性——与第 3 步相同规则。

### 第 5 步 — SLDS 限制

SLDS 类处理是最高优先级的 RTL 规则。**当以下规则说 "不要标记" 时，该类必须在报告中不作为发现出现——不作为问题，不作为 "修复"，不作为重命名建议。**

1. **带 `_left` / `_right` 后缀的 SLDS 实用工具类是 RTL 感知的，并且绝对不能标记。** 它们在后台自动镜像，因此包括 `slds-text-align_right`、`slds-text-align_left`、`slds-m-left_*`、`slds-m-right_*`、`slds-p-left_*`、`slds-p-right_*`、`slds-float_left`、`slds-float_right`、`slds-border_left`、`slds-border_right` 以及 `_left` / `_right` 实用工具家族的其余部分。保持原样。
2. **SLDS 类的 `_start` / `_end` 变体不存在。** 永远不要重命名 `slds-*_right` → `slds-*_end` 或 `slds-*_left` → `slds-*_start`。此类不存在；重命名会破坏样式表。如果你有修改 SLDS 实用工具类以添加 `_start`/`_end` 的想法，停止——正确操作是保持类不变（见规则 1）。
3. **永远不要修改、重命名或删除任何 `slds-*` 类。** SLDS 提供 RTL 感知的样式表；修改类会破坏契约。
4. **如果自定义 CSS 复制了 SLDS 类已经处理的内容**，修复是**删除——不是转换**。删除冗余的自定义规则；保持 SLDS 类不变。不要将删除的属性转换为逻辑等效项，也不要提供删除+转换作为两个替代方案；只有一个修复，它是删除。示例：`.css` 文件中的 `float: right` 与模板中 `class="slds-button__icon_right"` 并置——删除整个 `.custom-icon { float: right }` 规则。不要 "也建议 `float: inline-end`"——那将是错误的；SLDS 类已经处理了定位。
5. **如果 SLDS 类有 RTL 间隙**，添加补充自定义 CSS 而不是修改 SLDS 类。

**具体的负面示例**——带有 `<span class="slds-text-align_right slds-m-right_small">…</span>` 的模板，以及组件 CSS 中的自定义 `padding-left: 4px`：唯一的发现是 CSS `padding-left`（第 3 步）。两个 `slds-*_right` 类不是发现，并且必须不在报告中出现。

### 第 6 步 — 生成报告

以完全相同的形状编写 `<outputDir>/rtl-review.md`（每个 `##` 标题后空行；每个总结句以句号结尾）：

```markdown
## RTL

- <file>:<line> — <physical pattern> → <logical property / SLDS class>
  修复：<一句话解释>; 应用：是/否
- <file>:<line> — <physical pattern> → <logical property / SLDS class>
  修复：<一句话解释>; 应用：是/否

## 总结

- 发现 <n> 个问题；修复 <m> 个；推迟 <k> 个（原因）。
- <一句话概述发现的内容以及为什么剩余项是正确的或被推迟的>。
- 引用：RTL 专家 — <章节标题>。
```

从 `scan-rtl-css.sh` 输出填充 `## RTL` 要点（CSS 发现），并追加相同形状的手工编写的要点（第 4 步 HTML/JS 发现）。当没有发现时，在 `## RTL` 下发出单个要点 `- 未发现问题。` 并报告 `0 个问题发现；0 个修复；0 个推迟。` 加上一个一句话概述和引用。

### 第 7 步 — 应用修复

对于每个接受的发现：

1. 编辑组件文件（CSS、HTML、JS/TS）以应用修复。
2. 保留现有正确行为和现有功能标志。如果标志已经配置（例如，`Aura.org.rtlPhase1FixEnabled`），保持不变。只有当调用者明确要求对新修复进行分阶段发布时，才在修复后使用功能标志限制；否则直接应用修复。
3. 不要删除或重命名 SLDS 类。
4. 不要无声删除旧代码——如果需要标志，保留原始路径。

### 第 8 步 — 验证

- 对更新后的文件重新运行审核；每个修复的发现都不应再出现。
- 运行 Jest 测试和任何组件级别的 RTL 可视测试。

## 交叉引用

- 相关技能：
  - `design-systems-slds-apply` — 用于 SLDS 类级别的更改，超出自定义 CSS 清理范围。
  - `design-systems-slds2-migrate` — 当 RTL 清理暴露需要先进行 SLDS2 迁移的类时。
  - `experience-lwc-generate` — 当审核发现需要重新生成组件而不是修补它时。
  - 可访问性（WCAG 2.2）和安全性（LWS + 产品安全）审核是单独的检查——使用每个适当的工具运行它们，而不是这个技能。
  - 功能标志限制不在本技能范围内；仅在调用者明确要求分阶段发布时（见第 7 步）单独应用。

## 验证

- 所有 RTL 规则在更新后的组件中都是绿色的（重新运行 `scripts/scan-rtl-css.sh` 对包中的每个 CSS 文件——它必须对每个完全应用的发现返回空）。
- 没有修改、重命名或删除任何 SLDS 类。
- 每个发现要么已应用，要么有明确的推迟说明和原因。
- `rtl-review.md` 符合第 6 步定义的两部分形状（每个 `##` 后空行；总结句以句号结尾）。
