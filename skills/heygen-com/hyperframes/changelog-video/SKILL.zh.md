---
name: changelog-video
description: 将一个每周变更日志 .md 文件转换成一个定制的品牌变更日志视频（方形 1080p，时长约 45-60 秒，Annie 配音，动画品牌背景，模拟 UI 可视化，低调字幕）。当用户提供变更日志/摘要 Markdown 并希望生成每周视频，或说“变更日志视频”时使用。自包含——字体、背景、词汇库和脚本都包含在这个技能中。
---

# 更新日志 → 品牌视频

输入：一个更新日志 .md 文件（主题 + 项目，例如每周 HyperFrames 汇编）。
输出：一个 lint 清洁、seam-gate-green 风格的 HyperFrames 项目，位于 `projects/active/weekly-changelog-<范围>/` 中。仅在要求时渲染。

**必须首先加载，不可协商：** `motion-doctrine` (+ `cut-the-curve`, `oversized-cursor` 如果出现光标, `seam-craft`) 和 `captions-overlay`。这项技能提供特定于更新日志的流程；教义提供运动法则。

## 主要指令：可视化，不要列表

每个主题都由一个**实际 UI 的动画模拟或忠实模拟**来展示变化体验，而不是文本项目点。在编写脚本之前，将每个主题/项目路由到 `references/visualization-registry.md`；注册表决定 ui-recreate / ui-analog / 终端 / 清单。文本清单是最后的手段，保留用于真正非视觉项目（可靠性修复清单）。

## 流程

### 0 · 从本技能的资产中启动项目 — 不可协商

**在编写任何组合 HTML 之前必须这样做。跳过它总是会产生一个看起来像你之前构建的类似项目的视频，而不是本技能的品牌 — 这是本技能失去品牌的唯一最常见方式。** 技能的资产、字体和脚本是技能；`SKILL.md` 提示是路由器。

```bash
mkdir -p project/assets/fonts
cp <SKILL_DIR>/assets/fonts/*.woff2 project/assets/fonts/
cp <SKILL_DIR>/assets/bgm.mp3 project/bgm.mp3
ffmpeg -y -stream_loop 15 -i <SKILL_DIR>/assets/bg-pattern.mp4 -t <TOTAL> \
  -vf "scale=1080:1080,fps=30,eq=saturation=0.72,drawbox=c=black@0.5:t=fill" \
  -an -c:v libx264 -crf 20 -pix_fmt yuv420p project/assets/bg-pattern-<TOTAL>s.mp4
cp <SKILL_DIR>/examples/master-skeleton.html project/index.html
```

然后**通读 `references/build-spec.md`**（不要略读）——它定义了品牌标记（TT Norms Pro + ABC Solar Display + TT Norms Mono, 浅奶油色 `#f5f6f4`, 限制的绿色 `#5ef17c`, 带绿色调边框的玻璃卡片, 播放器/芯片药丸形状, 32px 标题轨道在 `top: 990`）每个场景都继承自脚手架。

仅在此之后开始以下步骤 1-6。步骤 1-4（解析、路由、脚本、VO）规划放入脚手架的内容；步骤 5 填充已复制 `project/index.html` 内的占位符（`<RANGE>`, `<TOTAL>`, `<CUT_N>`, `<DUR_N>`, 场景正文）——你**不**重写脚手架的 chrome、字体、调色板或布局外壳。

如果你发现自己需要从先前的视频的 `index.html` 上使用 `cp`，或者编写自己的 `@font-face` 声明，或者设计 WebGL 着色器背景而不是使用上面编码的 bg-pattern MP4：停止。删除当前的 `index.html` 并从 `cp` 的 master-skeleton 脚手架重新开始。在正确的脚手架上重建场景内容比在错误的脚手架上改造品牌更便宜。

### 1 · 解析 + 编辑剪辑

- 提取：周范围、头条统计数据（发布、提交）、主题、项目。
- **预算：45-60 秒总时长。** 标题 ≤2 秒，结尾 ≤3.5 秒，4 个主题 ≈ 9-12 秒每个。
- 每个主题保留一个英雄可视化 + 至多 3 个口头项目。其他所有内容都只存在于结尾的“完整汇编”指针中。剪辑是工作：带有 30 个项目的更新日志仍然产生 ≤14 个口头节拍。
- 按故事顺序排列主题：主要功能 → 产品表面 → 性能 → 可靠性（汇编通常已经按这种方式阅读）。

### 2 · 可视化路由

对于每个主题，从 `references/visualization-registry.md` 选择表面并写一行：`主题 → 表面 → 模拟执行的 2-4 个序列化动作，每个都与脚本短语相关联`。如果没有注册表表面且没有忠实模拟，它是清单场景——不要为无法真实表示的东西编造 UI。

### 3 · 两层脚本（口头 vs 显示）

按照 `references/script-voice.md` 的**标记行**编写脚本：
对话式语调，每个技术术语都带有来自 `references/lexicon.json` 的 `spoken` 发音形式，而 `display` 保持标准拼写。
字幕显示 `display`；VO 读取 `spoken`。任何不在词汇表中的术语：
停止并询问用户如何发音，然后将其添加到词汇表。
保存为 `script-tokens.json` 在项目中。

### 4 · VO — Annie (HeyGen, 固定)

```bash
# 口头层文本仅；单词 JSON = 口头文本的精确时间戳
# 仓库原生路径：更新日志视频技能从 hyperframes 仓库根目录运行，
# 因此它直接使用跟踪的 hyperframes-media TTS 辅助程序（不需要 `npx hyperframes
# skills` 安装步骤）。如果你已将技能复制到另一个仓库，请替换你自己的
# 路径到媒体使用 / hyperframes-media heygen-tts.mjs。
node skills/hyperframes-media/scripts/heygen-tts.mjs ./vo-spoken.txt \
  -o voiceover.mp3 --words vo-words.json \
  --voice 330290724a1b470fb63153f34d4c0183   # Annie — lifelike (不要替换)
```

需要 `heygen` CLI ≥0.3.0 认证 (`heygen auth login --oauth`)。
然后将口头时间戳与显示标记对齐：

```bash
node <SKILL_DIR>/scripts/align-captions.mjs \
  --tokens script-tokens.json --words vo-words.json --out captions.json
```

`captions.json` 是字幕轨道输入（显示拼写、口头时间）。对齐器打印 `MISMATCH` 警告——解决每一个，然后再构建（通常是一个词汇表拼写 TTS 渲染为多个单词）。**音频是时钟**：所有节拍时间都来自 `vo-words.json`；VO 重新生成重新打开每个接缝。

**单词时间是一个硬门槛。** 在继续步骤 5 之前，验证 `vo-words.json` 是否非空并且有一个 `words: [...]` 数组，每个单词有 `start`/`end`。如果它是空的（0 字节）或缺少数组——当 TTS 提供商返回音频但没有时间戳有效负载时的已知故障模式——在没有它们的情况下**不要继续**。后备：使用本地 whisper 强制对齐生成的音频与显示脚本：

```bash
uvx --from openai-whisper whisper voiceover.mp3 \
  --model base.en --language en --word_timestamps True \
  --output_format json --output_dir .
# 然后运行 align-captions.mjs with --words voiceover.json (相同形状)
```

Whisper 错误地听 TTS 渲染（"gee-sap" → "gsap", "heyjen" → "hey Jen", 等.）——字幕仍然使用 `script-tokens.json` 中的显示拼写；whisper 仅提供时间戳。`align-captions.mjs` 处理连接。这是带字幕构建与无声构建之间的区别。

### 5 · 构建

精确遵循 `references/build-spec.md`：品牌标记 + 字体（捆绑在 `<SKILL_DIR>/assets/` 中），动画背景编码，场景脚手架，chrome，字幕轨道，每个场景一个限制的绿色时刻。然后是教义顺序：`ledger.json`（所有普通接缝 cut-the-curve 左）→ seam-stamp → VO 单词上的内部节拍 → seam-gate 验证。

**字幕是可选的。** master-skeleton 发送一个字幕轨道 IIFE，它读取一个 `LINES` 数组——留下该数组为空是一个发送的 Bug，而不是一种风格选择。在继续到步骤 6 之前，从 `captions.json` 填充它：

```javascript
// 粘贴到字幕轨道 IIFE 中的 "const LINES = /* … */ []" 位置：
const LINES = /* captions.json 的内容 */ [
  { id: 0, end: 2.74, w: [["This", 0.0], ["week,", 0.30], …] },
  …
];
```

如果 `align-captions.mjs` 被跳过或 `LINES` 是 `[]`，步骤 6 中的帧检查将失败——不要通过从脚手架中删除 `#cap-line` 来掩盖它。

### 6 · 接缝（所有绿色之前呈现）

1. `node packages/cli/bin/hyperframes.mjs check --caption-zone "x0=0;y0=.90;x1=1;y1=1;severity=error;seek=.02,.06,.10,.14,.18,.22,.26,.30,.34,.38,.42,.46,.50,.54,.58,.62,.66,.70,.74,.78,.82,.86,.90,.94,.98"`（或从仓库本地 `skills/hyperframes-cli/` 技能安装的 `hyperframes` CLI）—— 0 个错误（对比：暗文本 ≥ .66 alpha；场景内容保持在字幕轨道之上）。**不要使用 `npx hyperframes@latest`**；跟踪的仓库本地 CLI 是本技能生成的组合合同的标准来源。
2. `seam-gate.mjs verify` — 0 失败。
3. 重新启动预览服务器（它缓存捆绑包），通过 `__player.seek` 在原始组合页面上检查 3-4 个节拍。
4. **除非用户要求，否则不要渲染。** 在请求渲染后，验证 MP4 的帧（`ffmpeg -ss <t> … -frames:v 1`）：字幕存在，背景视频不是黑色，没有微小的/冻结的帧。
5. **字幕存在接缝 — 硬失败。** 在 VO 的口头窗口中采样 3-4 个帧（例如 `t=3`, `t=15`, `t=30`, `t=42` 对于 48 秒的 VO）并确认字幕轨道在 `top: 990` 渲染每个帧上的可见文本。如果任何在口头间隔内的帧缺少字幕，构建将发送无字幕——将其视为红色接缝并重新检查步骤 5 的 `LINES` 填充。这就是 7 月 13-20 v4 构建出错的确切原因。

## 项目布局

```
projects/active/weekly-changelog-<范围>/
├── index.html            # 单文档主（场景作为幻灯片，带接缝印章）
├── ledger.json           # 向量账本（接缝印章输入）
├── script-tokens.json    # 两层脚本（VO + 字幕的真理来源）
├── vo-spoken.txt         # 生成：口头层，一行
├── voiceover.mp3 + vo-words.json + captions.json
├── bgm.mp3               # 从 <SKILL_DIR>/assets/bgm.mp3 复制（主曲目），除非用户提供
└── assets/fonts/ + assets/bg-pattern-<dur>s.mp4
```

## 反模式

| 不要                                                 | 而是                                                                                                                                                                                          |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 用于 UI 变更的带点列表幻灯片                          | 模拟表面执行变化                                                                                                                                                                                 |
| 用于无法表示项目的假 UI                                | 诚实的清单场景                                                                                                                                                                                   |
| TTS 文本中的 "JSON"/"CLI"                              | 词汇表口头形式；显示保持标准                                                                                                                                                                     |
| 字幕中的发音拼写                                      | 字幕始终渲染显示层                                                                                                                                                                               |
| 猜测未知术语的发音                                  | 询问，然后扩展词汇表                                                                                                                                                                             |
| 朗读每个更新日志项目                                  | 每个主题 ≤3 个；汇编链接携带其余内容                                                                                                                                                             |
| 到处都是绿色强调                                      | 每个场景一个绿色时刻 (#5ef17c)                                                                                                                                                                 |
| 从先前的视频的 index.html 开始                        | 步骤 0 — 从本技能复制 `examples/master-skeleton.html` 到 `project/index.html`，始终                                                                                                              |
| 手工制作的 `@font-face` / WebGL 着色器 / 自定义 BGM     | 步骤 0 — 逐字复制本技能的 `assets/`；技能的资产是品牌                                                                                                                                             |
| 未使用 CloudFront 使无效交付                         | 运行 `aws cloudfront create-invalidation` 在分布 `E2BSLVSZ7FG3U0` 上，对于任何 S3 替换后的确切路径——CDN 否则缓存旧文件                                                                                     |
| 带空 `LINES` 数组的 scaffold 发送                     | 步骤 4 必须生成填充的 `captions.json`；步骤 5 必须将其粘贴到 IIFE 中；步骤 6 接缝 5 必须确认在渲染帧上字幕可见。空的 `LINES` = 无字幕交付 = 重新运行                                                                 |
| 没有 `vo-words.json` → 跳过字幕并无论如何发送          | 落回对生成的音频进行 whisper 强制对齐；字幕是可选的                                                                                                                                               |
