---
name: weread-year-in-review-video-template
description: 灵感源自微信读书的 HyperFrames 视频模板，适用于竖版年度阅读报告、个人阅读仪表盘、读书笔记回顾以及可分享的年度回顾故事。当用户希望生成 9:16 比例的 HTML 转 MP4 阅读报告，并采用暖色纸张质感、编辑风格的中文字体、书页隐喻、数据亮点展示及确定性动效时，可使用此模板。
---

# WeRead 年度回顾视频模板

创建一个垂直 HyperFrames 组合，用于年度阅读报告：WeRead、Goodreads、Readwise、Notion 阅读记录、读书俱乐部或个人学习总结。该模板将阅读时间、活跃天数、书架资源、笔记、关键词和阅读形象转化为可分享的 9:16 视频格式。

## 资源映射

```text
weread-year-in-review-video-template/
├── SKILL.md
├── assets/
│   └── template.html
├── references/
│   └── checklist.md
└── example.html
```

`example.html` 所使用的渲染 MP4 展示视频托管在 `https://repo-assets.open-design.ai/resources/videos/skills/weread-year-in-review-video-template/default-showcase.mp4`。

## 工作流程

1. 将 `assets/template.html` 复制到 `index.html`。
2. 替换 `REPORT` 对象中的默认报告数据：
   - 所有者/标题
   - 阅读小时数和活跃天数
   - 书架和完成统计
   - 笔记构成
   - 兴趣关键词
   - 阅读形象和分享语句
3. 除非用户要求更短的剪辑，否则保留 12 场景的时间线。
4. 保持 WeRead 启发的视觉语言：
   - 温暖的纸张背景
   - 墨蓝色字体
   - 适度的 WeRead 绿色点缀
   - 书页、书签、高亮、笔记卡和书架隐喻
5. 动画效果应像翻阅阅读日记一样自然。避免科技感的幻灯片过渡、弹跳的 UI 效果和仪表板加载动画。
6. 保持组合的确定性：
   - 直接 `data-start`、`data-duration` 和 `data-track-index` 属性
   - 无未播种的随机性
   - 无无限循环或 `repeat: -1`
   - 无依赖滚动、悬停、localStorage 或运行时类发现
7. 在发布前，根据 `references/checklist.md` 进行验证。

## 输出契约

发布一句简短的定向语句，然后是一个单独的 HTML 文件：

```xml
<artifact identifier="weread-year-in-review-video-template" type="text/html" title="WeRead 年度回顾视频模板">
<!doctype html>
<html>...</html>
</artifact>
```
