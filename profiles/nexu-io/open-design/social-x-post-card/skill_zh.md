【模板: X (Twitter) 帖子卡】
【意图】将一段推文内容（或用户的金句）渲染成一张高度逼真的X帖子卡片，用于视频叠加、推特发图、知识沉淀。灵感来源于hyperframes x-post。

【画布】1280×720 或 1080×1080，暗背景 `#0f1419` 或亮背景 `#ffffff`（按X主题）；卡片居中，阴影柔和。

【卡片结构】
- 外框: 圆角16px，1px边框 `#2f3336`（暗色） / `#eff3f4`（亮色），内边距16px。
- 顶部row: 头像（48×48圆形，用CSS gradient占位）+ 用户名 + handle `@username` + verified蓝勾 + 时间（等宽字体，12px，灰色）。
- 正文: 17-22px，字重400；链接用X蓝 `#1d9bf0`；hashtag同色；mention同色；段落间空0.6em。
- 可选: 引用卡（小卡内嵌，灰底，圆角12px）。
- 可选: 1张图（CSS渐变+描述占位，不能外链图片），比例16:9，圆角12px。
- 互动row: 4个icon + 数字（回复/转推/引用/点赞），icon用inline SVG（X官方风格），灰色，hover时变色。
- 顶部右上X logo单线SVG。
- 浏览量row: 👁️ + 数字（小字）。

【字体】
- 西文: `Chirp`（X的字体）→ fallback `Inter` 或 `Segoe UI`。
- 中文: `Noto Sans SC` / `PingFang SC`。
- 数字: 同主字体，不用等宽字体。

【设计细节】
- 配色light: bg `#fff`，text `#0f1419`，secondary `#536471`，border `#eff3f4`，accent `#1d9bf0`。
- 配色dark（推荐，视频叠加用）: bg `#000`，text `#e7e9ea`，secondary `#71767b`，border `#2f3336`，accent `#1d9bf0`。
- 数字格式化: 1.2K / 4.5M（不要原始1234）。
- 内容必须来自用户输入，不能编造推文。
- 若用户输入是数据 → 自动总结成一句"金句"推文（≤280字符）。
- 单文件HTML；icon内联SVG；不要任何外部图片URL。
- 可选: 卡片背后加微妙径向高光 `radial-gradient(...)` 增加视频叠加的可读性。
