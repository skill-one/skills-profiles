---
name: ui-design
description: '每个视觉输出的UI/UX质量门禁和构建指南——包括着陆页、仪表盘、Web应用、作品集和工具。ui-design仍然是主要入口。


  集成模型：ui-design主分支 + taste-skill覆盖层。

  - ui-design负责工程质量（选择追踪、组件库策略、无障碍性、响应式、主题化、性能、预览交付）

  - taste-skill在ui-design工作流程中调用，用于风格决策（简报推断、设计旋钮、抗滑硬性规则）


  每当项目生成视觉HTML/CSS/JS时，必须与project-builder一起使用。'
---

# UI 设计技能

这项技能是视觉工作的**唯一入口点**。

用于任何面向用户的 HTML/CSS/JS 输出：落地页、仪表盘、产品 UI、内部工具和作品集页面。

---

## 第 1 步 — 选择构建路径

在编码前仔细选择：

- **路径 A（手写构建）**：静态预览、原味 HTML/CSS/JS、快速定制页面
- **路径 B（组件库）**：使用 shadcn/ui、HeroUI 或 coss ui 的 React/Vite/Next 项目

路径决策和组件库策略始终由 `ui-design` 拥有。

---

## 第 2 步 — 尝试覆盖合约（强制要求）

在 ui-design 工作流中，调用 taste-skill 精确处理这 3 个样式模块：

1. **简报推断**
2. **设计旋钮**（布局变化 / 动画强度 / 视觉密度）
3. **抗滑硬性规则**

### 边界

- `ui-design` 保持工程质量和交付的所有权
- `taste-skill` 提供样式方向和抗模板品味约束

这避免了与 ui-design 工程参考（组件库、a11y、预览、数据仪表盘实现）的重叠。

---

## 第 3 步 — 运行时顺序（每次使用）

1. 使用 `ui-design` 选择路径 A/B
2. 在编写 UI 代码前运行 taste 简报推断
3. 应用 taste 设计旋钮设定样式方向
4. 对于任何交互页面，先定义动画计划（什么动画、为什么、频率、时长、缓动曲线、减少动画路径）
5. 使用 ui-design 工程规则实现（a11y/主题/响应式/组件策略/性能）
6. 在交付前运行 taste 抗滑检查作为最终样式门禁

一句话总结：
- **taste 决定样式特征**
- **ui-design 保障稳健实现**

硬性规则：如果页面有交互，动画设计是强制要求（至少需要触觉反馈 + 状态转换反馈）。看起来静态的交互状态被视为不完整的 UI。

---

## 第 4 步 — 冲突仲裁

当规则重叠时：

- **样式冲突** → taste-skill 胜出
- **工程安全/正确性冲突** → ui-design 胜出

工程安全包括：可访问性、响应式稳定性、交互可靠性、运行时正确性和性能约束。

---

## 第 5 步 — 如何读取/下载 taste-skill（无本地镜像）

**不要**维护本地镜像或版本戳文件。

始终直接从 GitHub 读取/更新 taste 规则：

- 仓库：`https://github.com/Leonxlnx/taste-skill`
- 主参考技能：`https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md`
- 原始下载 URL：`https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/SKILL.md`
- 完整技能包目录：`https://github.com/Leonxlnx/taste-skill/tree/main/skills`

当 taste-skill 更新时，直接重新检查 GitHub 源并应用 ui-design 覆盖合约中的必要变更。

---

## 工程参考

| 文件 | 目的 |
|------|------|
| `references/design-process.md` | 工程质量门禁（a11y/主题/响应式/交互/运行时清单） |
| `references/component-libraries.md` | shadcn/ui · HeroUI · coss ui 选择 + 查找工作流 |
| `references/animations.md` | 动画实现标准、交互动画要求（集成 emil-design-eng 决策框架）、GSAP 使用说明 |
| `references/charts.md` | Chart.js/ECharts 实现模式 |
| `references/dashboards.md` | 数据源、实时更新、仪表盘结构、性能 |
| taste-skill GitHub 源 | 直接从 GitHub 读取样式规则：`https://github.com/Leonxlnx/taste-skill/tree/main/skills` |
