# After Hours 编辑模板

制作一个自包含的 HTML 编辑动效作品，采用暗黑奢华风格，
包含三个短页，电影感字体，以及高级过渡语言。

## 资源映射

```text
after-hours-editorial-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 读取活跃的 `DESIGN.md`，将颜色、字体调性、布局节奏映射到 CSS 变量中，
   同时保持暗黑编辑基线。
2. 将 `assets/template.html` 复制到 `index.html`。
3. 保持三个叙事页面按顺序排列；不要将默认页面停留时间超过 3 秒。
4. 保留高级动效行为：
   - 分阶段文本揭示层级
   - 章节擦除过渡
   - 环境颗粒/暗角深度
   - 限制性光标交互用于本地预览
5. 保持单文件 HTML 输出，包含内联 CSS 和 JS。
6. 避免沙盒不友好的浏览器 API（例如 localStorage 和 confirm）。
7. 在发布前使用 `references/checklist.md` 进行验证。

## 输出合约

一句简短的开场白，然后：

```xml
<artifact identifier="after-hours-editorial" type="text/html" title="After Hours 编辑模板">
<!doctype html>
<html>...</html>
</artifact>
```
