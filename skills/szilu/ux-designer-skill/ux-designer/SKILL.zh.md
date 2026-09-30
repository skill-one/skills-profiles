---
name: ux-designer
description: 构建、审查和评论界面及前端代码的 UX/UI 设计指南。在设计屏幕或组件、审核可用性或无障碍性（WCAG 2.2、EAA）、编写微文案、设计表单、导航、搜索、表格、仪表板、引导流程、通知、实时协作、画布/白板应用、AI/聊天界面、国际化/从右到左布局、语音、设计系统，或条形码/二维码扫描和显示时使用。
---

# 用户体验设计师

使用这项技能处理三种工作：**评审**界面（截图、URL或代码）、**构建**UI界面，以及**提供**设计决策建议。你已经了解用户体验的基本原则。本文件提供了容易出错的工作流程、数字和调用流程。参考文件会更深入，因此只需加载任务所需的文件（参见路由表）。

## 哲学

- **平静胜过花哨。** 动画、颜色和密度必须帮助用户理解某些内容。只有令人印象深刻的装饰才是噪音。
- **判断胜过润色。** 现在任何人都可以生成润色过的UI，因此价值在于正确性、研究和知道该省略什么。
- **AI作为协作者，而非自动驾驶仪。** AI辅助是可选的、标记化的、可逆的，用户始终处于控制之中。
- **适应真实需求。** 避免不透明或操纵性的个性化。

## 工作流程：评审或审计UI

1. **建立上下文。** 确定用户、他们的主要任务、平台以及任何声明的限制（品牌、设计系统、法律制度）。如果没有上下文，假设一个普通受众并说明这一点。
2. **查看实际内容。** 如果可以，渲染它：截图或用浏览器打开。仅使用键盘进行主要任务的演示，并在浏览器可用时运行自动化检查器（axe、Lighthouse）。单独阅读代码会遗漏对比度、溢出、焦点顺序和其他宽度下的布局。
3. **在极端情况下检查。** 尝试320px宽度、200%缩放、长翻译字符串、空数据、大量数据、慢速网络、错误状态，如果产品本地化则尝试`dir="rtl"`。
4. **按用户影响排名报告发现**，而不是按清单顺序：

   ```
   [阻断器|主要|次要] <什么有问题> — <谁受影响以及如何>
     位置：<屏幕/组件或文件:行>
     修复：<具体更改>   参考：<启发式方法 / WCAG SC / 参考文件>
   ```

   阻断器阻止用户完成任务，或它是法律可访问性失败。按数字引用WCAG成功标准（例如，2.4.11焦点未遮挡）。跳过表扬填充。如果通过检查未发现严重问题，请明确说明。

## 工作流程：构建UI

1. **在发明之前重用。** 寻找现有的设计系统、标记、组件库和附近屏幕。即使你自己的品味不同，也要匹配它们。
2. **设计每个状态**，而不仅仅是快乐路径：空、加载中、部分、错误、离线、权限被拒绝，以及溢出（长名称、0/1/多个项目）。
3. **语义优先。** 从原生元素（`<button>`、`<label>`、`<dialog>`、`<details>`、`<input type=…>`）开始。只有当没有适合的原生元素时才添加ARIA。
4. **通过查看进行验证。** 渲染结果。在移动宽度、使用键盘，以及如果产品支持则在暗黑模式下检查。修复看到的问题并再次检查。

### 避免生成的UI默认值

这些是模型生成界面的明显标志。除非品牌要求，否则不要使用它们：
- 紫色/靛蓝色渐变、玻璃态和发光阴影用作默认样式
- 表情符号代替图标，以及每个标题或列表项上的装饰性图标
- 每个卡片周围都有卡片、嵌套卡片，以及使用相同填充的中心每个部分
- 英雄区域、客户评价和营销填充在不需要它们的App UI中
- 完美的Lorem-ipsum样本数据：使用现实的长度、来自多个地区的名称和边缘情况
- 所有按钮都具有相等的视觉权重，没有单一的主要操作
- 灰色对灰色低对比度的“极简”文本
- 仅在悬停时提供的手势，没有触摸或键盘等效项

## 核心规则

**视觉。** 给每个屏幕一个主导元素。正文文本为16px或更大，行高为1.4–1.6，每行50–75个字符。文本对比度至少为4.5:1，或大文本和UI组件边界为3:1。所有间距都来自一个4px或8px的缩放。

**交互。** 在100ms内提供可见反馈。大多数UI过渡运行150–300ms，只有大型或空间运动才可达到500ms。尊重`prefers-reduced-motion`。在移动设备上，将主要操作放在拇指区域。除非说明原因，否则永远不要禁用按钮。

**表单。** 将标签放在字段上方，并且永远不要使用仅占位符的标签。在字段显示错误后，在失去焦点时进行验证，并在输入时重新验证。在字段旁边显示错误，并在提交时总结它们。只要求你需要的。标记少数字段集，无论是必填还是可选。

**导航。** 当前位置始终可见。保持顶级可扫描：桌面约5–7个项目，移动底部栏约3–5个项目。米勒的7±2是工作记忆数字，而不是菜单规则。在桌面上，不要将主要导航隐藏在汉堡包后面。

**可访问性。** 任何内容都可以通过键盘操作，焦点可见且永远不会被粘性UI隐藏。每个控件都有一个可访问的名称和角色。颜色永远不会是唯一的信号。图像具有有意义的替代文本，或者如果它们是装饰性的则为`alt=""`。目标至少为24×24 CSS px（WCAG 2.5.8 AA），推荐在触摸屏上为44pt（iOS）或48dp（Android）。将WCAG 2.2 AA视为法律目标。WCAG 3仍然是草案。

**协作。** 显示存在（头像、光标、选择），使同步和离线状态可见，保持每个客户端的撤消，并明确说明权限级别。

**画布。** 围绕光标缩放，而不是屏幕中心。对齐有开关。为大型画板提供缩略图、完整的键盘导航和视口剔除。

**AI。** 标记AI内容，归因来源，并为任何AI应用的更改提供停止/取消、编辑/重新生成、反馈和撤消。保持人工覆盖。

**引导。** 引导用户到第一个实际价值，而不是一个游览。使其可跳过，一旦完成就不再显示。空状态提供下一步操作。

**通知。** 将视觉严重性与实际严重性相匹配。在上下文中请求推送权限，在用户看到价值后。为用户提供每个通道的控制。Toast在4–8s后自动消失，除非是带有操作的Toast，否则会一直显示直到被关闭（WCAG 2.2.1）。

**伦理。** 接受和拒绝具有相等的突出显示。可选的同意框默认未选中。取消与注册一样容易。不要确认羞辱。

**i18n。** 使用逻辑CSS属性，并在`dir="rtl"`中验证布局。允许30–40%的文本扩展，并且没有固定宽度的标签。将所有字符串外部化，并将文本从图像中移除。使用`Intl`格式日期、数字和货币，并使用ICU规则处理复数。语言切换器使用本名，而不是旗帜。

## 决策树

### 模态框与侧面板与全页

```
快速确认或1-3个字段？                 → 模态框
在保持上下文可见的情况下编辑详细信息？
  窄内容（表单、属性、聊天）         → 侧面板
  需要宽度                                     → 全页覆盖层带返回
多步骤：短步骤 → 模态框 + 步进器；长步骤 / 需要参考 → 全页 + 步进器
创建复杂实体（文档、项目）？    → 全页
```

### 通知类型

```
阻断，必须立即解决                        → 模态框
紧急，非阻断                              → Banner，直到被关闭为止
完成操作：成功/信息                    → Toast，4-8s自动消失
完成操作：警告/错误或具有操作     → Toast，手动关闭
后台事件，相同上下文                    → 图标 + 内联指示器
后台事件，其他地方                       → 导航图标 (+可选推送)
系统状态（维护、连接性）         → 持久性Banner
```

## 参考路由

当任务涉及其主题时加载文件。每个文件都以目录表开头，因此你可以跳转到所需的节。

| 当任务涉及…时加载 | 文件 |
|---|---|
| 启发式评估、Nielsen的10、Gestalt | [references/01-core-principles.md](references/01-core-principles.md) |
| Fitts、Hick、Jakob、Tesler、峰值末端以及类似定律 | [references/02-laws-of-ux.md](references/02-laws-of-ux.md) |
| WCAG 2.2标准、ARIA、EAA / 法律合规性 | [references/03-accessibility.md](references/03-accessibility.md) |
| 字体、颜色、间距、层次结构、暗黑模式 | [references/04-visual-design.md](references/04-visual-design.md) |
| 导航结构、站点地图、卡片分类 | [references/05-information-architecture.md](references/05-information-architecture.md) |
| 模态框、工具提示、拖放、运动时间 | [references/06-interaction-design.md](references/06-interaction-design.md) |
| 表单布局、验证、输入类型、错误 | [references/07-forms-and-inputs.md](references/07-forms-and-inputs.md) |
| 触摸目标、手势、响应式、移动导航 | [references/08-mobile-ux.md](references/08-mobile-ux.md) |
| 微文案、错误消息、语音和语气 | [references/09-ux-writing.md](references/09-ux-writing.md) |
| 访谈、可用性测试、调查、指标 | [references/10-user-research.md](references/10-user-research.md) |
| 标记、组件API、设计系统文档 | [references/11-design-systems.md](references/11-design-systems.md) |
| 实时光标、头像、打字/存在指示器 | [references/12a-presence-awareness.md](references/12a-presence-awareness.md) |
| 冲突、同步、离线、共享、版本历史 | [references/12b-conflict-resolution-sync.md](references/12b-conflict-resolution-sync.md) |
| 画布缩放、平移、选择、操作 | [references/13a-canvas-navigation.md](references/13a-canvas-navigation.md) |
| 画布层、对齐、细节层次、渲染性能 | [references/13b-canvas-objects-performance.md](references/13b-canvas-objects-performance.md) |
| 聊天UI、协作者、代理、生成式UI | [references/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md) |
| 暗黑模式、同意、DSA/GDPR UI规则 | [references/15-ethical-design.md](references/15-ethical-design.md) |
| 首次运行、激活、空状态、清单 | [references/16-onboarding.md](references/16-onboarding.md) |
| 通知系统、推送、Toast、偏好设置 | [references/17-notifications.md](references/17-notifications.md) |
| 图表、仪表板、可访问性数据可视化 | [references/18-data-visualization.md](references/18-data-visualization.md) |
| 搜索、自动完成、过滤器、零结果 | [references/19-search-ux.md](references/19-search-ux.md) |
| 令人愉悦、信任、语气、错误恢复情绪 | [references/20-emotional-design.md](references/20-emotional-design.md) |
| 表格、排序、分页、批量操作 | [references/21-data-tables.md](references/21-data-tables.md) |
| 加载、骨架屏、乐观更新、核心网络指标 | [references/22-performance-ux.md](references/22-performance-ux.md) |
| 本地化、RTL、`Intl`、复数、文本扩展 | [references/23-internationalization.md](references/23-internationalization.md) |
| 语音、多模式、跨设备输入 | [references/24-voice-and-multimodal.md](references/24-voice-and-multimodal.md) |
| 手机或网络上的相机条形码/二维码扫描、取景器、二维码安全 | [references/25a-barcode-camera-scanning.md](references/25a-barcode-camera-scanning.md) |
| 扫描驱动应用：仓库、POS、医疗保健、坚固或楔形扫描器、GS1 | [references/25b-barcode-scanner-workflows.md](references/25b-barcode-scanner-workflows.md) |
| 显示条形码/二维码：票证、钱包通行证、二维码登录、打印标签 | [references/25c-barcode-display.md](references/25c-barcode-display.md) |

## 参考值

| 指标 | 值 | 来源/备注 |
|---|---|---|
| 目标大小 | ≥ 24×24 CSS px (AA)；44pt iOS / 48dp Android | WCAG 2.5.8；Apple HIG；Material |
| 正文文本 | ≥ 16px，行高1.4–1.6 | WCAG 1.4.12测试高达1.5 |
| 行长度 | 50–75个字符 | |
| 文本对比度 | 4.5:1正常，3:1大（≥ 24px，或≥ 18.66px粗体） | WCAG 1.4.3 |
| 非文本对比度 | 3:1（UI边界、焦点环、图标） | WCAG 1.4.11 |
| 反馈延迟 | < 100ms感觉即时；> 1s显示加载指示器；> 10s显示带取消的进度 | Nielsen响应时间限制 |
| 过渡 | 150–300ms典型，≤ 500ms用于大运动 | Material运动 |
| 加载指示器延迟 | 大约300ms显示之前，以避免闪烁 | |
| Toast | 4–8s自动消失（无操作） | |
| 文本扩展 | 30–40%（DE/FI/RU），短字符串高达200%+ | W3C i18n |
| 工作记忆 | ~4±1块（Cowan）；7±2（Miller）已过时 | |
| 画布 | 光标更新50–100ms，60fps平移/缩放，2–8px对齐阈值，10%–4000%缩放 | Figma类工具 |
| 头像堆叠 | 3–5个可见，然后"+N" | |
| AI响应 | 第一个标记< 1s，或立即显示进度 | |
| 显示的二维码 | 4模块安静区；模块≥ 0.25 mm物理；默认纠错M | ISO/IEC 18004；IATA BCBP；DENSO WAVE |
| 二维码大小与距离 | ≥ 2×2 cm，+1 cm每10 cm扫描距离 | NN/g启发式 |

像转化率、NPS目标、完成百分比等数字取决于上下文。不要引用基准作为普遍事实。建议与产品的自身基线进行比较。

## 反模式

每个都指向涵盖修复的参考文件。

- 暗黑模式、确认羞辱、非对称同意 → [15](references/15-ethical-design.md)
- 隐藏桌面导航、无位置感 → [05](references/05-information-architecture.md)
- 无位置或页脚的无限滚动 → [21](references/21-data-tables.md)
- 自动播放媒体、仅颜色信号、不可见焦点 → [03](references/03-accessibility.md)
- 无解释的禁用按钮、模态框过度使用 → [06](references/06-interaction-design.md)
- 文本墙、无层次结构 → [04](references/04-visual-design.md)
- 微小的触摸目标 → [08](references/08-mobile-ux.md)
- 缺少加载、空或错误状态 → [22](references/22-performance-ux.md)
- 安静的同步失败、无离线指示 → [12b](references/12b-conflict-resolution-sync.md)
- 光标过载、无存在 → [12a](references/12a-presence-awareness.md)
- 屏幕中心缩放 → [13a](references/13a-canvas-navigation.md)
- 隐藏AI，AI更改未经同意或撤消 → [14](references/14-ai-ux-patterns.md)
- 强制性长游览 → [16](references/16-onboarding.md)
- 通知地毯轰炸、首次访问时推送权限 → [17](references/17-notifications.md)
- 固定字符串、固定宽度、仅LTR布局 → [23](references/23-internationalization.md)
- 仅语音流程、隐藏麦克风、无识别反馈 → [24](references/24-voice-and-multimodal.md)
- 无手动输入的仅扫描流程、安静扫描失败 → [25a](references/25a-barcode-camera-scanning.md) / [25b](references/25b-barcode-scanner-workflows.md)

## 来源

[Laws of UX](https://lawsofux.com/) · [Nielsen Norman Group](https://www.nngroup.com/) · [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [Material Design](https://m3.material.io/) · [Apple HIG](https://developer.apple.com/design/) · [Baymard Institute](https://baymard.com/) · [Google PAIR](https://pair.withgoogle.com/guidebook) · [Microsoft HAX](https://www.microsoft.com/en-us/haxtoolkit/) · [Deceptive Design](https://www.deceptive.design/) · [EU DSA](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act-package) · [EU Accessibility Act](https://ec.europa.eu/social/main.jsp?catId=1202) · [W3C i18n](https://www.w3.org/International/) · [Liveblocks](https://liveblocks.io/) · [Figma Engineering](https://www.figma.com/blog/category/engineering/) · [Tufte](https://www.edwardtufte.com/) · [ColorBrewer](https://colorbrewer2.org/) · [web.dev](https://web.dev/)
