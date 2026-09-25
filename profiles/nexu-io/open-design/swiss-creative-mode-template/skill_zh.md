# 瑞士创意模式模板

制作一个具有强烈视觉韵律和有意义交互的瑞士/编辑风格的高级HTML模板，然后将其作为单个文件构件输出。

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
   - 堆叠/建筑图解场景。
4. 保持这些交互功能：
   - 上一/下一页导航 + 点状导航。
   - 主题切换（纸面/暗黑）。
   - 调色板循环按钮（更改模板中的强调色）。
   - 注释/详情热点切换。
5. 保持输出自包含（`<!doctype html>`，内联CSS/JS，无外部运行时依赖）。
6. 在输出前根据`references/checklist.md`进行验证。

## 输出合约

构件前一个简短句子，然后：

```xml
<artifact identifier="swiss-creative-mode" type="text/html" title="Swiss Creative Mode Template">
<!doctype html>
<html>...</html>
</artifact>
```
