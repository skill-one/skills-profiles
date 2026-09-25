# 游戏场构建器

游戏场是一个自包含的HTML文件，一侧有交互控件，另一侧有实时预览，底部有带复制按钮的提示输出。用户调整控件，进行可视化探索，然后将生成的提示复制回Claude。

## 使用此技能的场景

当用户需要交互式游戏场、探索器或可视化工具时，尤其是在输入空间较大、可视化或结构化且难以用纯文本表达的主题上。

## 如何使用此技能

1. **从用户请求中识别游戏场类型**
2. **从`templates/`加载匹配的模板**：
   - `templates/design-playground.md` — 视觉设计决策（组件、布局、间距、颜色、排版）
   - `templates/data-explorer.md` — 数据和查询构建（SQL、API、管道、正则表达式）
   - `templates/concept-map.md` — 学习和探索（概念图、知识差距、范围映射）
   - `templates/document-critique.md` — 文档评审（带批准/拒绝/评论工作流的建议）
   - `templates/diff-review.md` — 代码评审（git差异、提交、PR带逐行评论）
   - `templates/code-map.md` — 代码库架构（组件关系、数据流、层状图）
3. **遵循模板构建游戏场**。如果主题不能完全适配任何模板，使用最接近的模板并进行调整。
4. **在浏览器中打开**。在编写HTML文件后，运行`open <filename>.html`将其在用户的默认浏览器中启动。

## 核心要求（每个游戏场）

- **单个HTML文件**。内联所有CSS和JS。无外部依赖。
- **实时预览**。控件每次更改时立即更新。无需“应用”按钮。
- **提示输出**。自然语言，不是值堆砌。仅提及非默认选择。包含足够上下文以便在不查看游戏场的情况下采取行动。实时更新。
- **合理的默认值+预设**。首次加载时看起来良好。包含3-5个命名的预设，将所有控件设置为协调的组合。
- **暗色主题**。UI使用系统字体，代码/值使用等宽字体。极简界面。

## 状态管理模式

保持单个状态对象。每个控件写入它，每个渲染读取它。

```javascript
const state = { /* 所有可配置值 */ };

function updateAll() {
  renderPreview(); // 更新视觉
  updatePrompt();  // 重建提示文本
}
// 每个控件在更改时调用updateAll()
```

## 提示输出模式

```javascript
function updatePrompt() {
  const parts = [];

  // 仅提及非默认值
  if (state.borderRadius !== DEFAULTS.borderRadius) {
    parts.push(`边框圆角为 ${state.borderRadius}px`);
  }

  // 结合数字使用定性语言
  if (state.shadowBlur > 16) parts.push('一个明显的阴影');
  else if (state.shadowBlur > 0) parts.push('一个微妙的阴影');

  prompt.textContent = `更新卡片以使用 ${parts.join(', ')}.`;
}
```

## 常见错误避免

- 提示输出只是值堆砌 → 写作自然指令
- 控件过多 → 按关注点分组，将高级功能隐藏在可折叠部分
- 预览不立即更新 → 每次控件更改都必须触发立即重新渲染
- 无默认值或预设 → 加载时为空或损坏
- 外部依赖 → 如果CDN中断，游戏场将无法使用
- 提示缺乏上下文 → 包含足够信息以便在没有游戏场的情况下采取行动
