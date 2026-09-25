# UI设计技能

这项技能是视觉工作的**唯一入口点**。

用于任何面向用户的HTML/CSS/JS输出：着陆页、仪表盘、产品UI、内部工具和作品集页面。

---

## 第1步 — 选择构建路径

在编码前仔细选择：

- **路径A（手动构建）**：静态预览、原味HTML/CSS/JS、快速定制页面
- **路径B（组件库）**：使用shadcn/ui、HeroUI或coss ui的React/Vite/Next项目

路径决策和组件库策略始终由`ui-design`负责。

---

## 第2步 — 尝试覆盖协议（强制要求）

在ui-design工作流程中，调用taste-skill处理以下3个样式模块：

1. **简报推断**
2. **设计旋钮**（布局变化 / 动画强度 / 视觉密度）
3. **抗滑硬性规则**

### 边界

- `ui-design`保持工程质量和交付权
- `taste-skill`提供样式方向和抗模板化约束

这避免了与ui-design工程参考（组件库、a11y、预览、数据仪表盘实现）的冲突。

---

## 第3步 — 运行时顺序（每次使用）

1. 使用`ui-design`选择路径A/B
2. 在编写UI代码前运行taste简报推断
3. 应用taste设计旋钮设定样式方向
4. 对于任何交互页面，先定义动画计划（动画内容、原因、频率、时长、缓动曲线、无动画路径）
5. 使用ui-design工程规则实现（a11y/主题/响应式/组件策略/性能）
6. 在交付前运行taste抗滑检查作为最终样式门禁

一句话总结：
- **taste决定样式特征**
- **ui-design保证稳健实现**

硬性规则：如果页面有交互，动画设计是强制要求（至少包含触觉反馈+状态转换反馈）。静态外观的交互状态被视为不完整的UI。

---

## 第4步 — 冲突仲裁

当规则冲突时：

- **样式冲突** → taste-skill获胜
- **工程安全/正确性冲突** → ui-design获胜

工程安全包括：可访问性、响应式稳定性、交互可靠性、运行时正确性和性能约束。

---

## 第5步 — 如何读取/下载taste-skill（无本地镜像）

**不要**维护本地镜像或版本戳文件。

始终直接从GitHub读取/更新taste规则：

- 仓库：`https://github.com/Leonxlnx/taste-skill`
- 主技能参考：`https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md`
- 原始下载URL：`https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/skills/taste-skill/SKILL.md`
- 完整技能包目录：`https://github.com/Leonxlnx/taste-skill/tree/main/skills`

当taste-skill更新时，直接检查GitHub源并更新ui-design覆盖协议中的必要变更。

---

## 工程参考

| 文件 | 目的 |
|------|------|
| `references/design-process.md` | 工程质量门禁（a11y/主题/响应式/交互/运行时检查清单） |
| `references/component-libraries.md` | shadcn/ui · HeroUI · coss ui选择+查找工作流 |
| `references/animations.md` | 动画实现标准、交互式动画要求（集成emil-design-eng决策框架）、GSAP使用说明 |
| `references/charts.md` | 图表.js/ECharts实现模式 |
| `references/dashboards.md` | 数据源、实时更新、仪表盘结构、性能 |
| taste-skill GitHub源 | 直接从GitHub读取样式规则：`https://github.com/Leonxlnx/taste-skill/tree/main/skills` |
