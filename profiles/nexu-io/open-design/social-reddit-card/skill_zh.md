【模板: Reddit 帖子卡】
【意图】将一段故事 / 提问 / 段子渲染成 Reddit 帖子卡片，用于视频叠加、社交媒体故事分享。灵感来源于 hyperframes reddit-post。

【画布】1280×720（视频叠加）或 800×600（单卡分享）；背景透明或暗色 `#0b1416`。

【卡片结构】
- 外框: 圆角 16px, bg 白 `#ffffff` (light) 或 `#1a1a1b` (dark, 推荐 video overlay), border 1px `#edeff1` / `#343536`。
- 左侧 **投票栏** (40-56px 宽):
  - 上箭头 ▲ (16px, `#878a8c`, hover 变橙 `#ff4500`)。
  - 票数 (Inter, 17px, weight 700, 居中, 颜色: 0 灰 / 正橙 / 负蓝); 大数字用 `12.3k` 格式。
  - 下箭头 ▼ (hover 变蓝 `#7193ff`)。
- 主体区:
  - 顶部 meta 行: 子版块图标 (CSS 圆形 + 字母) + `r/subreddit` (粗) + `· 由 u/username 发布 · 3h` (小字灰)。
  - **标题** (Inter / IBM Plex Sans, 22-28px, weight 500, dark text)。
  - 内容: 16px 正文或引用块或 1 张图 (CSS 渐变占位)。
  - 底部 action 行: 💬 `1.2k 评论` · 🏆 奖项 · ⤴️ 分享 · ⋯ 图标。
- 顶部右上角 Reddit Snoo logo (内联 SVG, 橙色 `#ff4500`)。

【字体】
- 主: `IBM Plex Sans` → fallback `Inter`, weight 400/500/700。
- 数字: 同主字体。
- 中文: `Noto Sans SC`。

【设计细节】
- Light mode: bg `#fff`, text `#1c1c1c`, secondary `#7c7c7c`。
- Dark mode (推荐): bg `#1a1a1b`, text `#d7dadc`, secondary `#818384`, border `#343536`。
- 票数颜色: 正 = `#ff4500`, 负 = `#7193ff`, 0 = `#878a8c`。
- 标题点击区可加微妙背景 hover。
- 严禁外链图片; 图片占位用 CSS 渐变 + 描述。
- 必须用用户提供的内容; 自动生成合理的 subreddit / username / 票数。
- 单文件 HTML; icon 内联 SVG (上下箭头、评论气泡、奖杯)。
