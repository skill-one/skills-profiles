---
name: editorial-burgundy-principles-template
description: '红棕色/蜜桃色/柔和金色调的编辑工作室模板。

  当用户要求使用带有药丸标签的优质宣言或文化幻灯片、大型排版声明、原则卡片以及引导键盘/点击导航时使用。'
---

# 编辑部酒红色原则模板

一个用于文化叙事、战略故事讲述和内部宣言的三页式编辑演示文稿。

## 资源地图

```text
editorial-burgundy-principles-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 从 `assets/template.html` 开始。
2. 保持三页序列：
   - 数字标题
   - 工作室标签 + 标题组合
   - 八原则卡片网格
3. 替换文案，同时保留卡片和标签的层级结构。
4. 保持交互：
   - 上一页/下一页按钮
   - 点状导航
   - 键盘导航（`ArrowLeft` / `ArrowRight`）
5. 保持HTML自包含且安全。

## 输出契约

输出一句简洁的定向语句和一个HTML文件：

```xml
<artifact identifier="editorial-burgundy-principles" type="text/html" title="编辑部酒红色原则演示文稿">
<!doctype html>
<html>...</html>
</artifact>
```
