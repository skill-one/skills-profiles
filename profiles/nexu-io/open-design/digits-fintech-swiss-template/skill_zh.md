# Digits Fintech Swiss 模板

一个用于瑞士网格语言中数据叙事的优质三页实时艺术品模板。

## 资源地图

```text
digits-fintech-swiss-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 从 `assets/template.html` 开始，并保持三页结构完整。
2. 替换文本和指标值，同时保留卡片层级和阅读顺序。
3. 保留交互：
   - 上一页/下一页按钮
   - 键盘导航 (`ArrowLeft` / `ArrowRight`)
   - 点状导航
4. 保持动画效果微妙（仅滑页淡入+微小悬停抬升）。
5. 保持文件自包含（内联 CSS/JS），无沙盒不友好 API。

## 输出合约

先输出一句简洁的朝向语句，然后输出一个 HTML 艺术品：

```xml
<artifact identifier="digits-fintech-swiss" type="text/html" title="Digits Fintech Swiss Deck">
<!doctype html>
<html>...</html>
</artifact>
```
