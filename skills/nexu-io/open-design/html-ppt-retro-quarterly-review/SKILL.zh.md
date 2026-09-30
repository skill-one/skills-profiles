---
name: html-ppt-retro-quarterly-review
description: 复古季度回顾演示模板，采用大胆的蓝色+橙色编辑风格。当用户需要高冲击力的季度回顾/路线图演示文稿时使用，包含重型板块标题、干净的米色纸页部分、结构化网格，以及快速的高端动态节奏（3张幻灯片，每张在视频模式下持续时间不超过3秒）。
---

# 复古季度回顾模板

一个高对比度、受印刷启发的季度回顾模板，包含三个电影感的幻灯片：

1. 封面（英雄标题锁定）
2. 三个重点（三联画网格）
3. 路线图时间线 + KPI 条带

## 资源映射

```text
html-ppt-retro-quarterly-review/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 首先阅读活跃的 `DESIGN.md`，将请求的标记更改映射到 CSS 变量，同时保留复古蓝/橙/奶油的视觉语法。
2. 从 `assets/template.html` 开始；不要从零开始重建。
3. 保留三页幻灯片的结构信息和排版层级。
4. 保持交互和运动质量：
   - 键盘 `1/2/3` 快速跳转
   - `R` 重新开始
   - 每个场景更新页面指示器
   - 高级擦除过渡和交错揭示
5. 保持输出自包含（单个 HTML，内联 CSS + JS，无框架运行时）。
6. 如果调整文案/数据，保持内容真实且内部一致。
7. 在发出工件前，根据 `references/checklist.md` 进行验证。

## 输出合约

先输出一句简短的定向句子，然后是工件：

```xml
<artifact identifier="retro-quarterly-review" type="text/html" title="Retro Quarterly Review">
<!doctype html>
<html>...</html>
</artifact>
```
