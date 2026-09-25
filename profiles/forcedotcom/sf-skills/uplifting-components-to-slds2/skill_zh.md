# 目标

使用 SLDS linter 和结构化的指导，系统地将 Lightning Web Components 从 SLDS 1 迁移到 SLDS 2，并修复所有样式钩类别中的违规行为。

## SLDS 2 样式钩类别

| 类别 | 钩前缀 | 替换内容 |
|---|---|---|
| 颜色 | `--slds-g-color-*` | 硬编码颜色、`--lwc-color*` 令牌 |
| 间距 | `--slds-g-spacing-*` | 硬编码的边距、填充、间隙 |
| 尺寸 | `--slds-g-sizing-*` | 硬编码的宽度、高度、尺寸 |
| 字体 | `--slds-g-font-*` | 硬编码的字体大小、权重、行高 |
| 边框/半径 | `--slds-g-radius-border-*`, `--slds-g-sizing-border-*` | 硬编码的 border-radius、border-width |
| 阴影 | `--slds-g-shadow-*` | 硬编码的 box-shadow 值 |

颜色钩需要最多的判断（上下文相关的选择）。非颜色钩大多是编号的刻度，映射关系简单。

## 前置条件

- 安装 Node.js 14.x 或更高版本
- 可以访问组件的 CSS 和标记文件（`.html` 用于 LWC，`.cmp` 用于 Aura）
- 可以通过终端/命令行运行 linter
- Git 仓库用于备份（推荐）

---

# 工作流程

```
1. **必须 — 始终首先运行：** npx @salesforce-ux/slds-linter@latest lint --fix . — 永远不要跳过此步骤。这会自动处理简单的违规行为。
2. 审核linter输出 -> 确定需要手动修复的剩余问题
3. 按违规类型修复 -> 使用每条规则的参考指南
4. 选择正确的钩 -> 优先考虑上下文，在决定前检查 HTML
5. 验证 -> 重新运行 linter 并确认零错误
```

## 第 1 步：运行 SLDS Linter
强制执行：此步骤不是可选的。

```bash
npx @salesforce-ux/slds-linter@latest lint --fix .
```

linter 分析所有 CSS 和标记文件（`.html` 用于 LWC，`.cmp` 用于 Aura），自动修复简单的违规行为，并报告需要手动干预的剩余问题。

## 第 2 步：分析 Linter 输出

linter 以以下格式报告违规行为：

```
componentName.css
  15:3  警告  不支持覆盖 slds-button。为了区分 SLDS 和自定义类，请在您的命名空间中创建一个 CSS 类。
                 示例：myapp-input、myapp-button。                        slds/no-slds-class-overrides

  23:5  错误    '--lwc-colorBackground' 设计令牌已弃用。用 SLDS 2 样式钩替换它，并将回退设置为 '--lwc-colorBackground'。
                 1. --slds-g-color-surface-2
                 2. --slds-g-color-surface-container-2                      slds/lwc-token-to-slds-hook

  30:8  警告  考虑用具有相似值的 SLDS 2 样式钩替换静态值 #ffffff：
                 1. --slds-g-color-surface-1
                 2. --slds-g-color-surface-container-1
                 3. --slds-g-color-on-accent-1
                 4. --slds-g-color-on-accent-2
                 5. --slds-g-color-on-accent-3                              slds/no-hardcoded-values-slds2

  31:15  错误   考虑删除 t(fontSizeMedium) 或用
                 var(--slds-g-font-size-base, var(--lwc-fontSizeMedium, 0.8125rem)) 替换它。
                 将回退设置为 t(fontSizeMedium)。有关更多信息，请参阅 lightningdesignsystem.com 上的样式钩。               slds/no-deprecated-tokens-slds1
```

四种违规类型，每种类型都有其自己的修复方法（见第 3 步）。

**重要提示：** linter 标记了所有硬编码值。修复颜色、间距、尺寸、字体、边框和阴影值 — 但**跳过布局值**（`100%`、`auto`、`0`、`inherit`、`none`）。参见 [rule-no-hardcoded-values.md](references/rule-no-hardcoded-values.md) 以获取完整的修复与跳过决策表。

## 第 3 步：按类型修复违规行为

每条规则都有一个专门的参考指南，包含完整示例和决策逻辑：

| 违规规则 | 简要概述 | 参考 |
|---|---|---|
| `slds/no-hardcoded-values-slds2` | 替换硬编码值为 SLDS 钩 + 原始值作为回退 | [rule-no-hardcoded-values.md](references/rule-no-hardcoded-values.md)|
| `slds/lwc-token-to-slds-hook` | 用 SLDS 2 钩替换 `--lwc-*` 令牌，保留 LWC 令牌作为回退 | [rule-lwc-token-to-slds-hook.md](references/rule-lwc-token-to-slds-hook.md) |
| `slds/no-slds-class-overrides` | 创建组件前缀类，与 SLDS 类一起添加到标记中 | [rule-no-slds-class-overrides.md](references/rule-no-slds-class-overrides.md) |
| `slds/no-deprecated-tokens-slds1` | 用 SLDS 2 钩 + LWC 回退替换旧的 `t()`/`token()` 语法 | [rule-no-deprecated-tokens-slds1.md](references/rule-no-deprecated-tokens-slds1.md) |

**始终包含回退值** — `var(--slds-g-hook, originalValue)`，其中 `originalValue` 是源 CSS 中的确切原始值。

### 类覆盖快速参考

类覆盖需要对 **CSS 和标记**（`.html` 或 `.cmp`）进行更改。这是最常被遗漏的步骤：

1. **CSS：** 重命名 `.slds-*` 选择器 → `{componentName}-{sldsElementPart}`（驼峰式）
2. **标记：** 添加新类 **与 SLDS 类一起** — 永远不要删除 SLDS 类

```css
/* 之前 */ .slds-button { border-radius: 8px; }
/* 之后 */  .myComponent-button { border-radius: 8px; }
```
```html
<!-- 标记：两个类 --> <button class="slds-button myComponent-button">Click</button>
```

参见 [rule-no-slds-class-overrides.md](references/rule-no-slds-class-overrides.md) 以获取后代选择器、多类选择器和命名约定。

## 第 4 步：选择正确的钩

颜色钩需要基于上下文的选择。**必须：当任何违规行为涉及颜色属性（`color`、`background-color`、`background`、`fill`、`border-color`），您必须在选择钩之前阅读 [color-hooks-decision-guide.md](references/color-hooks-decision-guide.md)。** linter 列出了可能的钩，顺序不分先后 — 不要选择第一个建议。该指南包含基于属性的规则，这些规则决定了正确的钩。

**非颜色钩** 更简单 — 将 CSS 值与编号刻度匹配。参见 **[non-color-hooks-decision-guide.md](references/non-color-hooks-decision-guide.md)** 以获取值到钩的查找表，涵盖间距、尺寸、字体、边框、半径和阴影。

## 第 5 步：验证和确认

**linter 反馈循环 — 重复直到零错误：**

```
1. npx @salesforce-ux/slds-linter@latest lint .
2. 审核错误 -> 按类型修复（第 3 步）
3. 重新运行 linter
4. 重复直到输出显示：0 错误
```

---

# 验证

- [ ] CSS 选择器中没有 `.slds-*` 类
- [ ] 没有 `var(--lwc-*)` 令牌而没有 SLDS 2 替换
- [ ] 所有钩都包含回退值
- [ ] 背景/前景色钩来自同一系列
- [ ] 保留原始 SLDS 类在 HTML 中
- [ ] 间距使用编号钩（不是像 `spacing-medium` 这样的命名）
- [ ] 字体使用编号钩（不是像 `font-weight-bold` 这样的命名）
- [ ] 组件在浅色/深色模式和密度设置中正确渲染

参见 **[migration-checklist.md](references/migration-checklist.md)** 以获取完整的验证清单。

---

# 输出

返回完全迁移的 CSS（以及更新的 HTML 标记，其中类覆盖已修复），且没有 SLDS linter 违规。所有样式钩必须包含回退值，以保留原始 CSS 值。

---

# 高级模式

## 颜色混合用于透明度

当硬编码值使用 `rgba()` 或透明度时，使用 `color-mix()` 与 SLDS 钩来保留不透明度：

```css
/* 之前 */
border-color: rgba(186, 5, 23, 0.7);

/* 之后 — 使用 oklab 颜色空间以实现感知一致性 */
border-color: color-mix(in oklab, var(--slds-g-color-palette-red-40, rgb(181,54,45)), transparent 30%);
```

**公式：** 要实现 X% 不透明度，使用 `(100 - X)%` 透明度在 `color-mix` 中。
- 70% 不透明度 → `transparent 30%`
- 50% 不透明度 → `transparent 50%`

使用不透明的 `rgb()` 作为回退（不是 `rgba()`）— `color-mix` 处理透明度。

## calc() 表达式与令牌

当迁移 `t('calc(...)')` 或 `calc()` 与已弃用的令牌：

```css
/* 之前 — Aura t() 中的 calc */
height: t('calc(' + lineHeightButton + ' + 2px)');

/* 之后 — 如果 calc 仍然需要 */
height: calc(var(--lwc-lineHeightButton) + 2px);

/* 之后 — 如果 calc 不再需要，简化 */
height: var(--lwc-lineHeightButton);
```

对于 `calc()` 与 `--lwc-*` 令牌被替换：

```css
/* 之前 */
padding: calc(var(--lwc-spacingMedium) + 4px);

/* 之后 */
padding: calc(var(--slds-g-spacing-4, var(--lwc-spacingMedium)) + 4px);
```

**提示：** 通常 `calc()` 是不必要的，可以简化。检查结果是否与现有钩值匹配。

---

# 关键约束

- **永远不要发明钩名称** — 只使用 SLDS 设计系统中文档化的钩
- **始终包含回退值** — 回退必须是源 CSS 中的确切原始值
- **永远不要更改硬编码的数值** — 值如 `100%`、`50%`、`200px`、`1.5`、`auto`、`0`、`inherit`、`none`、`flex: 1` 是结构/布局值。不要用钩替换它们，也不要删除它们 — 它们不是样式钩候选
- **没有精确匹配？保持原样** — 如果硬编码值与任何钩的渲染值不密切对应，保持不变，而不是强行匹配
- **匹配钩编号到原始值强度** — 不要默认为 `-1`。选择最接近原始值的变体。参见 [color-hooks-decision-guide.md](references/color-hooks-decision-guide.md)
- **仅编号刻度** — 命名的钩如 `spacing-medium`、`font-weight-bold`、`radius-large` 不存在

# 故障排除

| 问题 | 解决方案 |
|---|---|
| Linter 建议两个或多个颜色钩选项 | 检查 HTML 上下文以确定元素的语义角色 — 见 color-hooks-decision-guide.md |
| 迁移后外观发生变化 | 验证回退值与原始值匹配；检查表面与容器系列 |
| 没有钩可用于硬编码值 | 保持不变；不要发明自定义钩名称 |
| Linter 说“删除静态值”用于 `100%`、`auto` 等 | 保持不变 — 这些是布局值。删除它们会破坏渲染。 |
| CSS 类命名错误 | 使用确切的驼峰式组件名称：`myComponent-button`，而不是 `MyComponent-button` |
| 间距/尺寸不匹配 | 检查值到钩映射在 non-color-hooks-decision-guide.md 中；验证间距与尺寸的使用 |
| 命名钩不起作用（例如，`spacing-medium`） | 命名钩不存在 — 使用编号刻度：`spacing-4` 用于 16px，`font-weight-7` 用于内联粗体强调（非标题） |
| 组件在紧凑密度下看起来不同 | 使用密度感知钩（`--slds-g-spacing-var-*`）用于适应密度的组件 |

---

# 参考

- **[颜色钩决策指南](references/color-hooks-decision-guide.md)** — 所有 5 个颜色钩系列、决策树、背景-前景配对、调色板可访问性
- **[非颜色钩决策指南](references/non-color-hooks-decision-guide.md)** — 间距、尺寸、字体、边框、半径和阴影钩，包含查找表
- **[规则：无硬编码值](references/rule-no-hardcoded-values.md)** — linter 行为、修复与跳过决策、替换模式、实用类工作流
- **[规则：LWC 令牌到 SLDS 钩](references/rule-lwc-token-to-slds-hook.md)** — 已弃用的 `--lwc-*` 令牌替换模式
- **[规则：无 SLDS1 已弃用令牌](references/rule-no-deprecated-tokens-slds1.md)** — 旧的 `t()`/`token()` Aura 语法替换模式
- **[规则：无 SLDS 类覆盖](references/rule-no-slds-class-overrides.md)** — 类重命名和 HTML 更新
- **[迁移示例](references/examples.md)** — 按场景和复杂性的前后示例
- **[常见模式](references/common-patterns.md)** — 永远不要覆盖的类、已弃用的 SLDS 2 类、调色板回退、没有 SLDS 2 等效的令牌
- **[迁移清单](references/migration-checklist.md)** — 完整验证清单
