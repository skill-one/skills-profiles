---
name: swiss-user-research-video-template
description: '瑞士风格用户研究叙事模板，采用暖纸版式编辑美学。

  当用户要求高端研究演示文稿或以故事为先的现场展示时使用，

  具有极简主义排版、高清晰度布局、微妙动效、环形图解，

  以及在一个HTML文件中跨幻灯片进行键盘/点击导航。'
---

# 瑞士用户研究视频模板

一个面向叙事性强的现场实物的瑞士编辑风格用户研究模板。
视觉语言采用温暖纸张、严格的空间节奏、细线规则和内敛的微交互，将注意力聚焦于故事。

## 资源地图

```text
swiss-user-research-video-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

## 工作流程

1. 阅读 `DESIGN.md`，然后将标记映射到模板的 CSS 变量（`--paper`、`--ink`、`--muted`、规则颜色、分段颜色），同时不改变布局语义。
2. 从 `assets/template.html` 开始；保持三页结构：
   - 标题/框架
   - 参与者分解环形图
   - 行为模式+证据面板
3. 保留交互：
   - 点击/键盘幻灯片导航（`ArrowLeft`/`ArrowRight`）
   - 底部分页点带激活状态
   - 环形图图例悬停高亮
   - 微妙的线条绘制和面板抬升过渡
4. 保持所有数据真实且在文案、环形图标签和百分比之间内部一致。
5. 保持 HTML 自包含（内联 CSS/JS），无外部框架依赖。
6. 在输出前使用 `references/checklist.md` 进行验证。

## 输出合约

输出一句简洁的引导句，然后是一个单独的 HTML 实物：

```xml
<artifact identifier="swiss-user-research-deck" type="text/html" title="瑞士用户研究综合">
<!doctype html>
<html>...</html>
</artifact>
```
