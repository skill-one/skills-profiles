---
name: vfx-text-cursor
description: Cursor light trail, chromatic rays, and directional flares for word-by-word quote reveals in video intros.
---

【模板: VFX 文字光标 (Text Cursor)】
【意图】视频开场/Hero 帧 —— 光标在画布上"打字", 文字逐字浮现, 后面拖着彩色像散尾迹 + 定向光斑。受 hyperframes vfx-text-cursor 启发。

【画布】1920×1080, 背景 `#06070a` 暗哑黑 或 `#0a0d12` (带暖调蓝); 添加微妙光晕效果。

【内容】
- 一句金句 (中英文不限), 居中, 字号 6-8vw, weight 700, 字体 `Inter Tight` / `Source Sans 3` / `Noto Sans SC`。
- 逐字揭示, 每个字符 80ms 间隔; 当前字符后面跟着一个光标 `▍` (或细垂直线)。
- 已揭示文字默认白色 `#f5f5f7`, 不透明度 1; 即将揭示位置添加色散光晕: 一份 `text-shadow: 2px 0 #ff3b6f, -2px 0 #00d4ff` 在揭示瞬间, 200ms 内收敛回正常。
- 光标本身: 16px 宽矩形, 颜色 = 重点色 (选择 1: 热粉红 `#ff3b6f` / 青色 `#00d4ff` / 橙黄 `#ffb547`), 闪烁 `@keyframes` 1.0s 周期; 后面拖一条 60-120px 的运动模糊尾迹 (径向渐变到透明)。

【光斑 / 射线】
- 在打字位置附近随机生成 3-5 道**定向光斑** (光晕): 用 `linear-gradient(45deg, transparent, accent20, transparent)` 的细长矩形 + `mix-blend-mode: screen`, 不规则角度。
- 当文字打完, 整段文字加 0.5s 闪烁扫过 (光带横扫)。

【字段】
- 顶部标题 (大写字母间距 0.18em, 11px, 不透明度 0.5): "FRAME 01 · OPENING"。
- 文字底下副标题 (24-28px, 不透明度 0.6): 来源 / 章节。
- 右下角时间码 (`00:03:21` 单行)。

【设计细节】
- **严禁**: 多色彩虹色散 (只使用 1 个热粉红 + 青色这种二元色散, 不要 R/G/B 全色)。
- 字体: 西文 `Inter Tight` Bold; 中文 `Noto Sans SC` Bold; 禁止衬线。
- 动效用 `@keyframes` + JS 计时器 (`setTimeout` 逐字), 可被 `prefers-reduced-motion` 关闭 (直接显示所有字)。
- 必须使用用户提供的金句; 不得虚构。
- 单文件 HTML, 不使用外链字体以外的资源。
