## 角色

将 Aura 作为面向客户的产品的默认 UI 系统使用。优先考虑决策层面的指导，而非详尽的规则：
- 首先选择合适的原语，
- 应用语义标记（不使用原始值），
- 保持布局和 UX 状态的一致性，
- 编写简洁、以行动为导向的文案。

> **注意**：确保项目使用 Aura 的最新版本（`@cognite/aura`），以获取最新的指导原则和组件。

你需要知道的一切都在：
- `node_modeules/@cognite/aura` 文件夹中
- Aura 设计指南可以在：`./node_modules/@cognite/aura/DESIGN.md` 找到
- 在 storybook：https://master--695bb4b1b8041ae09768950a.chromatic.com/?path=/docs/primitives
- 在文档网站：https://docs.cognite.com/aura-design-system/primitives

<when-to-reference>

当你需要参考此技能时：

- 创建或迁移交互式 UI、表单、表格、导航或数据展示
- 编写或修改样式、颜色、间距或排版
- 选择组件、标记或布局模式
- 创建或重构页面和响应式布局
- 编写或编辑任何面向用户的文本
- 构建表单、处理 API 响应、异步操作、确认或动态内容
- 实现可访问性（键盘、焦点、标题、ARIA、替代文本）
- 在 Flows 或 React 应用中正确应用 Aura

</when-to-reference>

## 运作原则

1. 在自定义 UI 之前使用 Aura 原语。
2. 通过语义标记和 Aura 默认值遵循基础原则；不要硬编码原始值。
3. 如果一个原语几乎适用，不要强行覆盖视觉效果；首先检查变体/属性，然后记录差距。
4. 保持行为可预测和可访问：键盘支持、可见焦点，以及加载/成功/错误时的清晰反馈。
5. 使用公开可访问的链接 — Aura 设计系统文档、Storybook 和 Figma。
