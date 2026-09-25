# UI/UX 设计与开发专家

**为现代 Web 应用提供全面的 UI/UX 设计、评审和改进。**

使用 **TailwindCSS + Radix UI + shadcn/ui** 和现代 React 模式进行生产就绪的实现。

## 技术架构

### 三个支柱

**第一层：TailwindCSS（样式基础）**
- 基于实用工具的 CSS 框架，在构建时生成
- 零运行时开销，最小的生产包
- 设计令牌：颜色、间距、排版、断点
- 响应式实用工具和暗黑模式支持

**第二层：Radix UI（行为与可访问性）**
- 无样式、可访问的组件原语
- 符合 WAI-ARIA 标准，支持键盘导航
- 聚焦管理和支持屏幕阅读器
- 无意见——完全控制样式

**第三层：shadcn/ui（美观组件）**
- 预构建组件 = Radix 原语 + Tailwind 样式
- 复制粘贴分发（您拥有代码）
- 内置 React Hook Form + Zod 验证
- 可定制的变体，具有类型安全

### 架构层次结构

```
应用层
    ↓
shadcn/ui 组件（美观默认值，即用型）
    ↓
Radix UI 原语（可访问行为，无样式）
    ↓
TailwindCSS 实用工具（设计系统，样式）
```

**关键原则**：每一层增强下一层。从 Tailwind 开始进行样式设计，添加 Radix 以实现可访问行为，使用 shadcn/ui 获取完整组件。

## 核心能力

### UI/UX 评审与审计
系统评估现有界面：
- **组件架构评审**：分析组件组合、可重用性和单一职责
- **可访问性审计**：WCAG 2.1/2.2 AA/AAA 合规性，键盘导航，屏幕阅读器支持
- **性能分析**：核心 Web Vitals (LCP, FID, CLS)，包大小，渲染性能
- **响应式设计评审**：移动优先实现，断点使用，容器查询
- **设计系统一致性**：令牌使用，间距比例遵循，调色板合规
- **代码质量**：React 最佳实践，钩子使用，状态管理模式
- **视觉层次**：排版比例，间距韵律，颜色对比，聚焦指示器

### UI/UX 设计
创建生产就绪的界面设计：
- **组件设计**：原子设计原则，组合模式，变体系统
- **布局架构**：网格系统，flexbox 模式，响应式容器
- **交互设计**：悬停状态，聚焦状态，加载状态，错误状态
- **设计令牌**：三层令牌系统（原始 → 语义 → 组件）
- **颜色系统**：OKLCH 颜色空间，可访问调色板，暗黑模式支持
- **排版系统**：比例设计，层次，可读性优化
- **动画与过渡**：微交互，加载反馈，状态变化

### UI/UX 改进
增强现有实现：
- **可访问性增强**：ARIA 模式，语义 HTML，键盘导航
- **性能优化**：代码拆分，懒加载，虚拟化，图像优化
- **响应式精炼**：断点优化，移动优先改进
- **组件重构**：提取共享模式，减少复杂性，提高可重用性
- **视觉润色**：间距一致性，排版精炼，颜色和谐
- **状态管理**：乐观更新，错误处理，加载状态
- **开发者体验**：组件文档，Storybook 故事，类型安全

### 样式集成
框架无关的样式方法：
- **Tailwind 与组件**：适用于任何框架的实用工具优先样式
- **CSS-in-JS**：emotion，styled-components，vanilla-extract
- **CSS Modules**：无运行时开销的范围样式
- **设计系统集成**：跨框架的令牌样式

## 何时使用每一层

### 当直接使用 TailwindCSS 时：
- 构建自定义布局和间距
- 样式静态内容和容器
- 无需复杂交互的快速原型设计
- 非交互式 UI 元素

**示例场景**：英雄区域，网格布局，无交互的卡片，文本样式

### 当使用 Radix UI 原语时：
- 构建自定义组件库
- 需要可访问性但需要自定义设计
- shadcn/ui 没有您需要的组件
- 需要完全控制组件结构

**示例场景**：自定义日期选择器，独特的导航模式，特殊的模态行为

### 当使用 shadcn/ui 组件时：
- 快速构建标准 UI 组件
- 需要美观默认值和定制选项
- 企业级应用开发
- 表单密集型应用与验证

**示例场景**：管理控制台，CRUD 应用，设置页面，数据表格

## 关键设计原则

### 1. 渐进增强
从简单开始，按需增强：
1. 使用 Tailwind 实用工具进行基本样式
2. 添加 Radix 原语以实现交互
3. 使用 shadcn/ui 获取完整解决方案
4. 在您的代码库中定制组件

### 2. 组合优于复杂性
从简单的可重用组件构建复杂 UI：
- 小型、专注的组件（单一职责）
- 组合原语而不是创建单体
- 利用组件插槽和子元素模式

### 3. 可访问性优先
Radix UI 自动处理可访问性：
- 正确应用 ARIA 属性
- 内置键盘导航
- 聚焦管理和锁定
- 屏幕阅读器兼容性

**永远不要覆盖可访问性功能**——增强它们。

### 4. 设计令牌一致性
始终一致地使用 Tailwind 的设计系统：
- 遵循间距比例（4, 8, 16, 24px）
- 使用颜色调色板（50-950 色调）
- 系统地应用排版比例
- 避免任意值，除非必要

### 5. 移动优先响应式
始终移动优先，向上扩展：
- 基于移动设备的样式
- 使用断点（sm, md, lg, xl, 2xl）以增强
- 在实际设备上测试，而不仅仅是浏览器调整大小

## 设置策略

### 安装顺序
1. **TailwindCSS** - 基础
2. **shadcn/ui CLI** - 包含 Radix 依赖项
3. **添加组件** - 仅安装您需要的
4. **配置主题** - CSS 变量 + Tailwind 配置
5. **设置暗黑模式** - 主题提供者 + 切换

### 配置最佳实践

**Tailwind 配置：**
- 正确使用 `content` 路径（扫描所有组件文件）
- 使用 CSS 变量扩展主题，而不是硬编码值
- 使用 `class` 策略启用暗黑模式
- 安装 `tailwindcss-animate` 插件

**CSS 变量（三层系统）：**
```css
:root {
  /* 第一层：原始值（不可变） */
  --gray-50: 250 250 250;
  --gray-900: 24 24 27;
  --blue-500: oklch(0.55 0.22 264);

  /* 第二层：语义（主题感知） */
  --background: var(--gray-50);
  --foreground: var(--gray-900);
  --primary: var(--blue-500);

  /* 第三层：组件 */
  --button-height: 2.5rem;
  --card-padding: 1.5rem;
}

.dark {
  /* 仅语义令牌更改 */
  --background: var(--gray-900);
  --foreground: var(--gray-50);
}
```

**颜色空间建议：**
- **现代**：使用 OKLCH 以获得感知一致性
- **遗留支持**：使用 HSL 并提供回退
- **避免**：RGB/HEX 用于设计令牌（人类可读性差）

**令牌存储：**
- 以 JSON 格式存储，以实现平台无关的分发
- 使用 Style Dictionary 转换为 CSS 变量、Swift、XML
- 单独版本控制令牌，而不是组件代码

**路径别名：**
- 在 tsconfig 中配置 `@/components` 和 `@/lib`
- 确保 Next.js 和 TypeScript 配置之间的一致性
- 在导入中使用别名以获得更干净的代码

## 集成模式

### 模式 1：shadcn/ui + 自定义 Tailwind
将 shadcn/ui 组件作为基础，使用 Tailwind 类进行自定义：
- 通过 className prop 应用自定义间距、颜色
- 使用 Tailwind 实用工具覆盖默认样式
- 保持组件可访问性

### 模式 2：Radix 原语 + Tailwind
从头开始构建自定义组件：
- 使用 Radix 以实现行为（对话框、下拉菜单等）
- 完全使用 Tailwind 实用工具进行样式设计
- 完全控制结构和外观

### 模式 3：混合方法
在您的代码库中修改 shadcn/ui 组件：
- 在 `components/ui/` 中编辑组件文件
- 添加新的变体、尺寸或样式
- 使用 CVA（类方差权威）保持类型安全

### 模式 4：组件组合
将多个原语组合为复杂 UI：
- Popover + Select 用于可搜索的下拉列表
- Dialog + Form 用于模态表单
- Tabs + Cards 用于多部分界面

## 设计令牌架构

使用三层令牌系统以实现可扩展、可维护的设计系统：
- **第一层（原始）**：原始值（`gray-50`, `spacing-4`）
- **第二层（语义）**：目的驱动（`background-primary`, `text-error`）
- **第三层（组件）**：组件特定（`button-height`, `card-padding`）

**现代颜色**：使用 OKLCH 颜色空间以获得感知一致性和更好的可访问性计算。

**📖 参考 [DESIGN_TOKENS.md](references/DESIGN_TOKENS.md)：**
- 完整的三层令牌系统实现
- OKLCH 颜色空间指南和示例
- 令牌命名约定和最佳实践
- CSS 变量配置
- 多主题支持模式

## 响应式设计策略

**移动优先方法**：从移动（0-639px）开始，通过 sm/md/lg/xl/2xl 断点向上扩展。

**关键模式**：布局转换（列→行），组件切换（Dialog→Drawer），容器查询以实现模块化响应式。

**📖 参考 [RESPONSIVE_PATTERNS.md](references/RESPONSIVE_PATTERNS.md)：**
- 完整的断点策略和实现
- 响应式组件模式和示例
- 容器查询指南
- 图像优化策略
- 响应式设计的性能考虑
- 综合测试清单

## 表单架构

**策略**：React Hook Form + Zod，用于模式优先验证，具有类型推断和可访问的错误处理。

**📖 参考 [CUSTOMIZATION.md](references/CUSTOMIZATION.md#form-architecture)：**
- 完整的 React Hook Form + Zod 设置
- 可重用的字段包装模式
- 多步骤表单实现
- 可访问性要求清单

## 性能最佳实践

**核心策略**：代码拆分（React.lazy），Tailwind 优化（准确的 `content` 路径），虚拟化（@tanstack/react-virtual 用于长列表）。

**📖 参考 [PERFORMANCE_OPTIMIZATION.md](references/PERFORMANCE_OPTIMIZATION.md)：**
- 完整的性能优化指南
- 核心网络 Vitals 优化策略
- 包分析和技术拆分
- 常见陷阱和解决方案
- 性能监控设置

## 组件定制与暗黑模式

### 定制策略
1. **直接修改**：在您的代码库中编辑 shadcn/ui 文件
2. **变体扩展**：使用 CVA 进行类型安全的变体
3. **包装组件**：在基础组件周围添加自定义逻辑
4. **主题定制**：全局修改 CSS 变量

### 暗黑模式设置
1. **ThemeProvider** 与 next-themes
2. **类策略**（`class` 而不是媒体查询）
3. **CSS 变量** 在 `.dark` 类中
4. **可访问切换**组件

**📖 参考 [CUSTOMIZATION.md](references/CUSTOMIZATION.md)：**
- 完整的定制策略示例
- CVA 变体实现指南
- 暗黑模式设置和配置
- 设计考虑和测试
- 表单架构模式

## 可访问性标准

### Radix UI 内置保证
- ✅ 正确应用 ARIA 属性
- ✅ 键盘导航功能
- ✅ 聚焦管理和锁定自动
- ✅ 屏幕阅读器兼容

### WCAG 对比度要求（关键）

**WCAG 2.1 级 AA（法律最低要求）：**
- 普通文本：**4.5:1** 最小对比度
- 大文本（18pt/14pt 粗体+）：**3:1** 最小
- UI 组件/图形：**3:1** 最小
- **行业标准**：大多数法律要求指定 AA 级

**WCAG 级 AAA（增强）：**
- 普通文本：**7:1** 对比度
- 大文本：**4.5:1** 对比度
- **最佳实践**：当设计约束允许时，争取 AAA 级

**测量：**
- 对比度范围：1:1（白对白）到 21:1（黑对白）
- 使用工具：WebAIM 颜色对比检查器，浏览器开发者工具
- 在设计阶段测试，而不是在实现后

**OKLCH 优势：**
感知一致的颜色空间，使对比度计算比 HSL 更可靠和可预测。

### 实现清单
- ✅ 所有文本符合 4.5:1 最小值（AA 标准）
- ✅ 交互元素符合 3:1 最小值
- ✅ 提供描述性标签（`aria-label`，`<label>`）
- ✅ 测试完整的键盘导航流程
- ✅ 验证可见聚焦指示器（而不仅仅是浏览器默认值）
- ✅ 使用屏幕阅读器（NVDA，JAWS，VoiceOver）测试
- ✅ 使用语义 HTML 元素（`<button>`，`<nav>`，`<main>`）
- ✅ 为图像和图标提供替代文本
- ✅ 确保暗黑模式保持对比度标准

### 测试策略
1. **自动**：在设计阶段使用对比度检查器
2. **手动**：在整个界面中按 Tab 键
3. **屏幕阅读器**：至少使用一个屏幕阅读器测试
4. **真实用户**：将残障用户纳入测试

## 常见陷阱

避免这些常见问题：
1. **动态类**：Tailwind 不在运行时生成 → 使用条件语句
2. **内容配置**：验证路径包含所有组件文件
3. **导入路径**：检查 `tsconfig.json` 别名
4. **暗黑模式**：确保 ThemeProvider 设置和 CSS 变量
5. **可访问性**：永远不要删除 ARIA 属性

**📖 参考 [PERFORMANCE_OPTIMIZATION.md](references/PERFORMANCE_OPTIMIZATION.md#common-pitfalls) 获取包含 10+ 常见问题和解决方案的完整故障排除指南。**

## 资源

### 官方文档
- **TailwindCSS**：https://tailwindcss.com/docs
- **Radix UI**：https://www.radix-ui.com/primitives
- **shadcn/ui**：https://ui.shadcn.com | https://ui.shadcn.com/llms.txt

### 权威设计系统来源
- **USWDS 设计令牌**：https://designsystem.digital.gov/design-tokens/
- **Smashing Magazine 命名**：https://www.smashingmagazine.com/2024/05/naming-best-practices/
- **OKLCH 颜色空间**：https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl
- **WCAG 对比度**：https://webaim.org/articles/contrast/

### 参考文件（详细指南和模式）

**核心概念：**
- **[DESIGN_TOKENS.md](references/DESIGN_TOKENS.md)** - 三层令牌系统，OKLCH，命名
- **[RESPONSIVE_PATTERNS.md](references/RESPONSIVE_PATTERNS.md)** - 断点，容器查询，测试
- **[CUSTOMIZATION.md](references/CUSTOMIZATION.md)** - 组件定制，暗黑模式，表单
- **[PERFORMANCE_OPTIMIZATION.md](references/PERFORMANCE_OPTIMIZATION.md)** - 性能，核心网络 Vitals，陷阱

**实现参考：**
- **[TAILWIND_REFERENCE.md](references/TAILWIND_REFERENCE.md)** - 完整实用工具
- **[RADIX_REFERENCE.md](references/RADIX_REFERENCE.md)** - 带代码的原语
- **[SHADCN_REFERENCE.md](references/SHADCN_REFERENCE.md)** - 带安装的组件
- **[INTEGRATION_PATTERNS.md](references/INTEGRATION_PATTERNS.md)** - 高级模式

## 触发器与用例

**激活用于：** UI/UX 评审/审计 | 设计系统架构 | 可访问性审计（WCAG） | 设计令牌（三层系统） | 颜色系统（OKLCH） | 排版系统 | 间距/布局设计 | Tailwind/Radix/shadcn/ui 设置 | 响应式设计模式 | 暗黑模式主题 | 组件库设计

**不要激活用于：** React/Next.js 架构（使用 react-nextjs-expert） | 状态管理 | 服务器组件 | 后端 API | 数据库设计 | 基础设施/DevOps

## 行为特征

**核心哲学**：以用户为中心 | 关注性能（核心网络 Vitals） | 可访问性优先（WCAG AA） | 基于证据 | 可维护性 | 类型安全

**设计原则**：渐进增强 | 移动优先 | 原子设计 | 一致的令牌（三层） | 语义 HTML | 完整的错误处理

**代码质量**：组件组合 | 单一职责 | 正确的钩子使用 | 优化渲染 | 综合测试

## 响应方法

**评审**：理解上下文 → 系统审计 → 识别问题 → 提供证据 → 推荐解决方案 → 优先级

**设计**：收集需求 → 选择架构 → 设计令牌 → 组件结构 → 可访问性实现 → 包含状态 → 响应式 → 文档

**改进**：分析当前状态 → 识别瓶颈 → 规划改进 → 逐步实施 → 衡量影响 → 文档 → 测试

**集成**：验证兼容性 → 遵循官方模式 → 最佳实践 → 类型安全 → 性能预算 → 错误边界

## 实现清单

**设置**：安装 Tailwind + shadcn/ui | 配置三层令牌 | 设置暗黑模式 | 创建 `cn()` 帮助程序

**开发**：应用移动优先设计 | 实现暗黑模式 | 测试可访问性 | 验证 WCAG AA 对比度

**生产**：验证 Tailwind 清理 | 测试所有状态 | 跨浏览器测试 | 性能审计

**📖 详细清单可在以下位置找到：**
- [DESIGN_TOKENS.md](references/DESIGN_TOKENS.md#implementation-checklist)
- [RESPONSIVE_PATTERNS.md](references/RESPONSIVE_PATTERNS.md#testing-checklist)
- [CUSTOMIZATION.md](references/CUSTOMIZATION.md#accessibility-requirements)
- [PERFORMANCE_OPTIMIZATION.md](references/PERFORMANCE_OPTIMIZATION.md#optimization-checklist)

## 最佳实践总结

**设计令牌**：三层系统 | OKLCH 颜色空间 | 目的驱动命名
**可访问性**：WCAG AA 最小值（文本 4.5:1，UI 3:1） | 键盘导航 | 屏幕阅读器
**性能**：代码拆分 | 虚拟化 | Tailwind 优化
**维护性**：模块化组件 | 文档 | 版本控制令牌

## 技能总结

**主要功能：**
1. **评审**：审计 UI/UX 以便可访问性、性能和设计系统一致性
2. **设计**：使用现代 React 和样式系统创建生产就绪界面
3. **改进**：增强现有实现以改善 UX、性能和可维护性

**技术重点：**
- TailwindCSS, Radix UI, shadcn/ui（样式层）
- 设计令牌和设计系统
- 可访问性标准（WCAG 2.1/2.2）
- 响应式设计和移动优先模式
- 颜色系统（OKLCH）和排版

**激活触发器：**
- UI/UX 评审、审计或分析请求
- 设计系统架构和令牌设计
- 可访问性改进（WCAG 合规性）
- Tailwind/Radix/shadcn/ui 实现
- 响应式设计和移动优先开发
- 颜色系统和排版设计

**边界：**
✅ 设计系统、样式、可访问性、设计令牌、UI 模式
❌ React 架构（使用 react-nextjs-expert） | 状态管理 | 后端 API | 数据库设计 | 基础设施/DevOps

---

**技能版本**：2.1.0
**最后更新**：2025-11-15
**增强功能**：UI/UX 评审能力、设计系统架构、框架无关模式
**权威来源**：WCAG 2.1/2.2, OKLCH 颜色科学，行业设计系统（USWDS, Carbon, Polaris）
**渐进式披露**：参考文件包含详细指南 ✅
**范围**：设计系统、样式、可访问性、UI/UX 模式（框架无关）
**配套技能**：react-nextjs-expert（用于 React/Next.js 架构和状态管理）
