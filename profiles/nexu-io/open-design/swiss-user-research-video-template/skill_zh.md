# 瑞士用户研究视频模板

一个面向叙事性强的现场实物的瑞士编辑风格用户研究模板。
视觉语言采用温暖纸张、严格的空间节奏、细线规则和内敛的微交互，以保持对故事的注意力。

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
   - 微妙的线条绘制和面板提升过渡
4. 保持所有数据真实且在文案、环形图标签和百分比之间内部一致。
5. 保持 HTML 自包含（内联 CSS/JS），无外部框架依赖。
6. 在输出前使用 `references/checklist.md` 进行验证。

## 输出合约

输出一句简洁的定向语句，然后是一个单独的 HTML 实物：

```xml
<artifact identifier="swiss-user-research-deck" type="text/html" title="瑞士用户研究综合">
<!doctype html>
<html>...</html>
</artifact>
```
