---
name: swiss-creative-mode-template
description: 瑞士风格创意模式演示模板技能，具有粗体编辑排版、高对比度几何卡片、交互式幻灯片导航、主题切换、热点覆盖层和调色板编排的单文件HTML工件。当用户要求高端演示风格着陆页、瑞士/ brutalist风格牌组外观或具有丰富交互的创意启动页面时使用。
---

# 瑞士创意模式模板

制作一个具有强烈视觉节奏和有意义交互的瑞士/编辑风格高级HTML模板，然后将其作为单个文件工件输出。

## 资源映射

```text
swiss-creative-mode-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 读取活跃的`DESIGN.md`，将调色板/类型/布局决策映射到根CSS变量。
2. 将`assets/template.html`复制到`index.html`。
3. 保持此结构完整：
   - 带有粗体标题和几何框架的英雄场景。
   - 四步流程卡片行。
   - 堆叠/建筑图场景。
4. 保持这些交互功能：
   - 上一/下一幻灯片导航 + 点状导航。
   - 主题切换（纸面/暗黑）。
   - 调色板循环按钮（更改模板中的强调色）。
   - 注释/详情热点切换。
5. 保持输出自包含（`<!doctype html>`，内联CSS/JS，无外部运行时依赖）。
6. 在输出前与`references/checklist.md`进行验证。

## 输出合约

工件前一个简短句子，然后：

```xml
<artifact identifier="swiss-creative-mode" type="text/html" title="Swiss Creative Mode Template">
<!doctype html>
<html>...</html>
</artifact>
```
