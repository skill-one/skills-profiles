【模板: Spotify 正在播放卡】
【意图】将一首歌、一段播客或一段个人介绍渲染成 Spotify 正在播放卡，适用于视频叠加/个人关于页面/创作者英雄区域。灵感来源于 hyperframes spotify-card。

【画布】两种尺寸:
- 横版视频叠加: 1280×720, 卡片居中或左下角浮动。
- 紧凑横条 widget: 600×200, 可嵌入到任何英雄区域。

【卡片结构】
- 外框: 圆角 12-16px; 背景使用从专辑封面色提取的暗渐变 (例如 `linear-gradient(135deg, #1e3264 0%, #0d1f3d 100%)`) 或 Spotify 经典 `#121212`; 边缘有 1px 微妙的边框。
- 左侧: **专辑封面** (CSS 渐变 + 大号 monogram 或抽象几何描绘, 不可外链图片), 圆角 6px, 60-200px 方形。
- 右侧:
  - 顶部 `NOW PLAYING` (大写字母间距 0.14em, 11px, 绿色 `#1DB954`)。
  - **歌名 / 标题** (Inter / Spotify Circular, 22-28px, weight 700, 白色)。
  - **艺人 / 副标** (16px, weight 400, opacity 0.7)。
  - 进度条: 4px 高, 圆角, 灰色背景 + 白色 fill (`width: 38%`); 两端时间戳 `1:24 / 3:42` (mono, 11px, 灰)。
  - 控制行: ⏮ ⏯ ⏭ icon (内联 SVG, 24px, 白色 fill), shuffle / repeat icon 较小。
- 右上角: Spotify logo (内联 SVG, 绿色 `#1DB954` 圆 + 三道白色波纹)。
- 可选: 右下角小型音波动效 (3 个 bar `@keyframes`)。

【字体】
- 主: `Spotify Circular` → fallback `Inter` / `Inter Tight`, weight 400 / 700。
- 数字: 同主字体, 不用 mono 太多。

【设计细节】
- Spotify 经典暗模式: `#121212` 背景, `#1DB954` 强调色, `#b3b3b3` 次要文本。
- 若用户输入是文本/标题 → 把 "标题" 当歌名, "副标/作者" 当艺人, 估算"时长" 3:42 默认。
- 若用户输入是音乐相关 → 直接对应。
- 严禁外链图片; 封面用 CSS 渐变 + 文字 logo / 几何描绘。
- 微动效: 音波动效用 `@keyframes`, 可被 `prefers-reduced-motion` 关闭。
- 单文件 HTML。
