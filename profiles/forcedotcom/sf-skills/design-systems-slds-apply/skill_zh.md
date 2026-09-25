# 应用 SLDS

**Salesforce Lightning Design System (SLDS)** 是一个包含数千个组件的 CSS 框架。这项技能教导代理如何查找和正确使用它们。

> **版本：** 此技能针对 **SLDS v2**。旧版 `--lwc-*` 令牌和 `slds-*--modifier` 语法已弃用。
>
> **审计范围：** 伴随的 `design-systems-slds-validate` 技能分析器仅扫描 `.css`、`.html` 和 `.js` 文件。直接用于 LWC 和类似的 HTML/CSS/JS 组件；将其视为 JSX/TSX 或其他框架特定模板格式的部分信号，并辅以人工审查。

## SLDS 是什么？

| 组件 | 数量 | 描述 |
|------|-------|-------------|
| **Lightning Base Components** | ~70 | 预构建的 LWC 组件（仅限 LWC） |
| **SLDS Blueprints** | 85 | 适用于任何框架的 CSS/HTML 模板 |
| **Styling Hooks** | 523 | 主题的 CSS 自定义属性 (`--slds-g-*`) |
| **Utility Classes** | 1,147 | 用于间距、布局、可见性的快速样式类 |
| **Icons** | 1,732 | 5 个类别的 SVG 图标 |

---

## 范围

**此技能涵盖：**
- 给定 UI 模式应使用的蓝图
- 如何使用钩子进行样式化（颜色、间距、排版、阴影、边框）
- 哪些 utility classes 用于布局、间距、可见性
- 应使用哪个图标以及来自哪个类别
- SLDS 命名约定、类结构、钩子语法

**此技能在验证清单中包含基本的可访问性提示**（图标 alt 文本、焦点轮廓、颜色非唯一指示器）。完全符合 WCAG 需要专门的可访问性审查。

**此技能不包括（使用伴随技能）：**
- **设计决策** -- 视觉层次结构、构图、交互模式
- **LWC 机制** -- 组件结构、@wire、@api、生命周期、事件（尚未提供）
- **完全可访问性** -- WCAG 合规性、ARIA 模式、键盘导航、焦点管理、对比度比率（尚未提供）

---

## 组件选择层次结构

始终遵循此顺序：

```text
1. Lightning Base Components (LWC 仅限)    ← 首先检查
2. SLDS Blueprints (任何框架)         ← 使用确切的 SLDS 类
3. 带有 Styling Hooks 的自定义       ← 使用 var(--slds-g-*)
4. 自定义 CSS (最后手段)                ← 仍然使用钩子为值
```

如果使用 LWC 构建，请首先检查 LBC：[Lightning 组件库](https://developer.salesforce.com/docs/component-library/overview/components)

如果不存在 LBC（或未使用 LWC），则选择 SLDS Blueprint。参见 [references/component-selection.md](references/component-selection.md)。

---

## 核心规则

### 做

- 遵循选择层次结构：LBC > Blueprint > Hooks > Custom CSS
- 使用 `var(--slds-g-*, fallback)` 为所有可主题化的值
- 创建自定义类（`my-*`，`c-*`）而不是覆盖 `.slds-*`
- **在使用之前验证每个钩子、类和 utility** — 运行搜索脚本；永远不要根据命名模式假设组件存在（参见 [Verify Before You Use](#verify-before-you-use)）
- 将表面颜色与文本上的颜色配对
- 在每个 `<lightning-icon>` 上提供 `alternative-text`

### 不要

- 硬编码颜色、间距或排版值
- 直接覆盖 `.slds-*` 类
- 使用已弃用的 `--lwc-*` 令牌作为主要值
- 使用 `--slds-s-*`（共享）钩子 -- 它们是私有/内部
- 重新分配钩子值 -- 仅使用 `var()` 引用它们
- 单独使用颜色传达含义
- 通过从其他家族中插值模式来发明钩子名称（参见命名陷阱下方）

---

## 钩子命名陷阱

SLDS 钩子家族**不**都遵循相同的命名模式。代理经常通过假设 `{prefix}-{number}` 适用于所有情况来发明不存在的钩子。**在使用之前，始终通过捆绑的 `search-hooks.cjs` 脚本或 `assets/hooks-index.json` 验证钩子是否存在**。

### 陷阱 1：字体大小钩子**不是**编号的

| 错误（不存在） | 正确 | 备注 |
|----------------|------|------|
| `--slds-g-font-size-3` | `--slds-g-font-scale-1` | 字体大小使用 `font-scale-*`，不是 `font-size-*` |
| `--slds-g-font-size-4` | `--slds-g-font-scale-2` | 仅存在 `--slds-g-font-size-base`（基本大小） |
| `--slds-g-font-size-8` | `--slds-g-font-scale-6` | 规模：负-4 通过 10 |

**规则：** 对于字体大小，使用 `--slds-g-font-size-base`（唯一基本大小）或 `--slds-g-font-scale-*`（编号的规模）。永远不要 `--slds-g-font-size-N`。

### 陷阱 2：颜色钩子始终需要编号

| 错误（不存在） | 正确 | 备注 |
|----------------|------|------|
| `--slds-g-color-on-surface` | `--slds-g-color-on-surface-2` | 所有颜色钩子都需要编号 |
| `--slds-g-color-on-accent` | `--slds-g-color-on-accent-1` | 通过强调级别选择 1/2/3 |
| `--slds-g-color-surface` | `--slds-g-color-surface-1` | 没有未编号的基本形式 |

**规则：** 每个 `--slds-g-color-*` 钩子都以数字结尾。按强调选择：`-1`（低）、`-2`（中）、`-3`（高）。

### 陷阱 3：并非所有值都有钩子等效物

某些 CSS 值（例如，`min-width: 7rem` 用于标签对齐）没有 SLDS 钩子。这是可以接受的：

```css
.c-field-label {
  /* 没有SLDS钩子存在；有意自定义值 */
  min-width: 7rem;
}
```

**规则：** 当没有钩子时，直接使用值并添加注释说明它是故意的。尽可能使用 SLDS 网格 utility（`slds-size_*`）作为硬编码宽度的替代方案。

---

## 使用前验证

> **规则：** 在生成代码中包含 SLDS 钩子、utility class、蓝图类或图标之前，必须先确认它在元数据中存在。根据命名模式猜测是发明组件的主要来源。

在使用任何 SLDS 组件之前运行适当的搜索命令：

| 组件 | 验证命令 | 真实来源 |
|------|----------|----------|
| 样式钩子 (`--slds-g-*`) | `node scripts/search-hooks.cjs --prefix "<hook-name>"` | `assets/hooks-index.json` |
| Utility class (`slds-*`) | `node scripts/search-utilities.cjs --search "<class-name>"` | `assets/utilities-index.json` |
| 蓝图 / CSS 类 | `node scripts/search-blueprints.cjs --search "<pattern>"` 然后读取 YAML | `assets/blueprints/components/*.yaml` |
| 图标 | `node scripts/search-icons.cjs --query "<description>"` | `assets/icon-metadata.json` |

如果搜索没有返回匹配项：**不要使用该组件。** 从搜索结果中找到替代方案或使用验证的钩子构建自定义组件。

---

## 命名约定

使用一致的自定义类前缀以避免与 SLDS 冲突：

| 模式 | 用途 | 示例 |
|------|------|------|
| `my-*` | 一般自定义样式 | `my-card-header` |
| `c-*` | LWC 组件特定 | `c-accountList-row` |
| `[namespace]-*` | 包含/应用程序命名空间 | `acme-dashboard-widget` |

**避免：** 通用名称（`container`，`wrapper`）、SLDS 类似名称（`custom-slds-button`）、SLDS 类上的 BEM（`slds-card__custom-header`）。

自定义钩子命名空间：

```css
:root {
  --my-app-primary: var(--slds-g-color-accent-1);
  --my-app-card-padding: var(--slds-g-spacing-4);
}
```

---

## 知识地图

这项技能捆绑了全面的 SLDS 知识。按需阅读文件 -- 不要一开始就读所有内容。

### 决策指南（每个任务从这里开始）

| 文件 | 阅读时机 |
|------|----------|
| [references/component-selection.md](references/component-selection.md) | 选择组件或蓝图 |
| [references/styling-decision-guide.md](references/styling-decision-guide.md) | 应用颜色、间距、排版、阴影 |
| [references/icons-decision-guide.md](references/icons-decision-guide.md) | 选择或实现图标 |
| [references/utilities-quick-ref.md](references/utilities-quick-ref.md) | 使用 utility classes 进行布局/间距 |

### 搜索脚本（查找特定组件）

| 脚本 | 它搜索什么 | 示例 |
|------|------------|------|
| `scripts/search-blueprints.cjs` | 85 蓝图 YAML | `--search "dialog"` |
| `scripts/search-hooks.cjs` | 523 样式钩子 | `--prefix "--slds-g-color-accent-"` |
| `scripts/search-icons.cjs` | 1,732 带同义词的图标 | `--query "save button"` |
| `scripts/search-utilities.cjs` | 1,147 utility classes | `--category "grid"` |

### 深入指导（阅读以获取详细规则）

| 文件夹 | 内容 | 索引 |
|------|------|------|
| `references/overviews/` | 基础概念（颜色、间距、排版等） | [references/README.md](references/README.md) |
| `references/styling-hooks/` | 钩子类别，详细使用说明 | [references/README.md](references/README.md) |
| `references/utilities/` | 27 utility class 类别 | [references/README.md](references/README.md) |
| `references/slds-development-guide.md` | 完整 SLDS 开发指南 | -- |

### 原始元数据（用于查找的结构化数据）

> **不要直接阅读元数据 JSON 文件** — 它们太大，无法用于代理上下文（hooks-index.json 是 6,000 多行；icon-metadata.json 是 38,000 多行）。使用上述搜索脚本查询它们。

| 文件 | 内容 | 行数 |
|------|------|------|
| `assets/blueprints/components/*.yaml` | 85 蓝图规范（类、变体、a11y、HTML） | ~50-200 每个文件 |
| `assets/hooks-index.json` | 523 钩子，值和 CSS 属性 | ~6,300 |
| `assets/icon-metadata.json` | 1,732 带搜索同义词的图标 | ~38,500 |
| `assets/utilities-index.json` | 1,147 utility classes，CSS 规则 | ~6,900 |

---

## 编写工作流

### 第一阶段：理解需求

识别：
- 需要什么 UI 模式？（表单、表格、模态框、卡片等）
- 什么框架？（LWC、React、Vue、Angular、纯 HTML）
- 它将显示什么数据？
- 它需要什么状态？（加载中、空、错误、成功）

### 第二阶段：选择组件

1. **如果 LWC**：检查 [Lightning 组件库](https://developer.salesforce.com/docs/component-library/overview/components) 是否有 LBC
2. 搜索蓝图：`node scripts/search-blueprints.cjs --search "<pattern>"`
3. 读取蓝图 YAML：`assets/blueprints/components/<name>.yaml` 以获取确切的类、修饰符、状态和可访问性要求
4. 没有匹配项？使用钩子构建自定义（见第三阶段）

详情：[references/component-selection.md](references/component-selection.md)

### 第三阶段：应用样式

1. **阅读**：[references/styling-decision-guide.md](references/styling-decision-guide.md)
2. **颜色**：按角色分类（表面、强调、反馈、边框）然后选择钩子
3. **间距**：使用 utility classes (`slds-p-*`，`slds-m-*`) 或钩子 (`--slds-g-spacing-*`)
4. **布局**：使用网格 utility (`slds-grid`，`slds-col`，`slds-size_*`)
5. **自定义 CSS**：使用 `var(--slds-g-*, fallback)`，仅使用自定义类前缀

### 第四阶段：添加图标

1. **阅读**：[references/icons-decision-guide.md](references/icons-decision-guide.md)
2. **搜索**：`node scripts/search-icons.cjs --query "<description>"`
3. **在 LWC 中**：使用 `<lightning-icon>` 并提供 `alternative-text`
4. **在非 LWC 中**：使用 SVG 并提供 `slds-icon` 类和 `slds-assistive-text`

### 第五阶段：验证（强制执行 — 不要跳过）

**步骤 1：运行 SLDS linter。** 这是必需的。目标是零违规。

```bash
npx @salesforce-ux/slds-linter@latest lint <component-path>
```

Linter 捕获硬编码值、类覆盖和已弃用的令牌。**在继续之前修复所有违规。** 不要合理化违规为可接受的。

**步骤 2：验证没有发明的钩子。** 确认输出中的每个 `--slds-g-*` 钩子都存在于 `assets/hooks-index.json` 中。与 [checklists.md](references/checklists.md) 中的 T051 交叉引用。

**步骤 3：运行 [checklists.md](references/checklists.md)** 进行 linter 无法自动化的检查：
- 所有 `var(--slds-g-*)` 都有后备值（T002）
- 表面/强调/反馈颜色钩子正确配对（T010–T013）
- 间距使用钩子或 utility classes — 没有 `px` 值（T020–T021）
- 字体大小使用 `--slds-g-font-scale-*`，不是 `--slds-g-font-size-N`（T031）
- 所有图标都有可访问性文本（A004）
- 自定义类使用 `my-*` 或 `c-*` 前缀（Q010）

**步骤 4（可选）：** 使用 `design-systems-slds-validate` 技能运行完整质量审计，在代码审查或部署之前获取评分报告。直接用于 LWC / HTML-CSS-JS 组件；对于 JSX/TSX 输出，将结果视为部分覆盖率。在标记工作完成之前，目标 B 级（≥80）或更高。

---

## 快速参考

### 常见钩子模式

```css
/* 表面 + 文本配对（始终使用编号变体） */
background: var(--slds-g-color-surface-1, #ffffff);
color: var(--slds-g-color-on-surface-2, #181818);

/* 标准间距 */
padding: var(--slds-g-spacing-4, 1rem);

/* 卡片式容器 */
border-radius: var(--slds-g-radius-border-2, 0.25rem);
box-shadow: var(--slds-g-shadow-1, 0 2px 4px rgba(0,0,0,0.1));

/* 强调用于主要操作 */
background: var(--slds-g-color-accent-1, #0176d3);
color: var(--slds-g-color-on-accent-1, #ffffff);

/* 排版 -- 使用 font-scale-*，不是 font-size-*（仅 font-size-base 存在） */
font-size: var(--slds-g-font-scale-2, 0.875rem);
```

### 常见 utility 模式

```html
<!-- 响应式网格 -->
<div class="slds-grid slds-wrap slds-gutters">
  <div class="slds-col slds-size_1-of-1 slds-medium-size_1-of-2">...</div>
</div>

<!-- 间距 -->
<div class="slds-p-around_medium slds-m-bottom_small">...</div>

<!-- 截断 -->
<p class="slds-truncate" title="Full text here">Full text here</p>
```

---

## 示例

参见 [examples.md](references/examples.md) 以获取展示完整工作流从意图到 SLDS 组件选择的工作示例。

## 验证

参见 [checklists.md](references/checklists.md) 以获取与 design-systems-slds-validate 技能对齐的验证清单。

## 资源

| 资源 | URL |
|------|-----|
| SLDS 网站 | https://www.lightningdesignsystem.com/ |
| Lightning 组件库 | https://developer.salesforce.com/docs/component-library/overview/components |
| SLDS Linter | https://developer.salesforce.com/docs/platform/slds-linter/guide |
| Styling Hooks 参考 | https://www.lightningdesignsystem.com/2e1ef8501/p/591960-global-styling-hooks |
