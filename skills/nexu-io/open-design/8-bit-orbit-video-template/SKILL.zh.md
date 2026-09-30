---
name: 8-bit-orbit-video-template
description: '基于 Hyperframes 的复古像素风格动态设计视频模板。

  当用户需要使用高保真度、多场景的 HTML 转视频组合，并带有高级过渡效果、交互式预览控制和即用型渲染默认样式时使用。'
---

# Hyperframes 视频模板

提供一种高级模板模式的 Hyperframes 组合，包含预设的默认展示界面和确定性的时间线行为。

## 资源映射

```text
8-bit-orbit-video-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

`example.html` 所使用的渲染 MP4 展示界面托管在
`https://repo-assets.open-design.ai/resources/videos/skills/8-bit-orbit-video-template/default-showcase.mp4`。

## 工作流程

1. 将 `assets/template.html` 复制到 `index.html`。
2. 保留 3 场景结构及过渡节奏，除非用户明确要求改变节奏。
3. 自定义标题、副标题行、标签和调色板，同时保持复古像素美学。
4. 保持时间约束：每个场景的停留时间应控制在 3 秒内。
5. 保留生成组合的确定性行为（无未播种的随机性，无无限 GSAP 循环）。
6. 将所有代码自包含在一个 HTML 文件中，使用内联 CSS/JS。
7. 在发出工件前，根据 `references/checklist.md` 进行验证。

## 输出契约

在工件之前输出一句简短的话，然后是一个单独的 HTML 工件：

```xml
<artifact identifier="8-bit-orbit-video-template" type="text/html" title="8-Bit Orbit Video Template">
<!doctype html>
<html>...</html>
</artifact>
```
