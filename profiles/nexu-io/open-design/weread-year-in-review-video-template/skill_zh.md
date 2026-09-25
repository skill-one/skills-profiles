# WeRead 年度回顾视频模板

创建一个垂直 HyperFrames 组合，用于年度阅读报告：WeRead、Goodreads、Readwise、Notion 阅读日志、读书俱乐部或个人学习总结。该模板将阅读时间、活跃天数、书架资源、笔记、关键词和阅读角色转化为可分享的 9:16 视频格式。

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
   - 阅读角色和分享语句
3. 除非用户要求更短的剪辑，否则保留 12 场景的时间线。
4. 保持 WeRead 启发的视觉语言：
   - 温暖的纸张背景
   - 墨蓝色字体
   - 适度的 WeRead 绿色点缀
   - 书页、书签、高亮、笔记卡和书架隐喻
5. 动画效果应像翻阅阅读日记一样自然。避免科技感的幻灯片过渡、弹跳式 UI 效果和仪表盘加载动画。
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
