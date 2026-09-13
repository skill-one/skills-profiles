# pr-to-video (`heygen-com/hyperframes/pr-to-video`)

## whitebox

- Step 0 定目录并初始化: 跑 preflight 校验 CLI 能力, npx hyperframes init 建项目, 写入 intent layer 已锁定的 BRIEF.md (含 PR 引用), 并展示语音/音乐的登录状态。
- Step 1 摄取 PR: fetch-pr.mjs 用 gh 拉取 capture/pr.json + diff.patch, ingest.mjs 离线折叠成 tokens/visible-text/people.json, 再尽力下载贡献者头像。
- Step 2–3 设计与故事: 套用固定的 code-editorial 预设生成 frame.md + 字幕皮肤; 基于真实 diff 写分镜 STORYBOARD.md 和旁白 SCRIPT.md, 交用户审批 (自主模式改为发摘要后继续)。
- Step 3.1–4 音频与视觉设计: 后台跑 audio.mjs 生成旁白、词级时间戳、BGM; 同时为每帧写按旁白节奏铺开的时间轴 shot sequence, 代码帧指定 code-* 区块。
- Step 5–6 建帧与渲染: 派发有界的 frame worker 池并行产出每帧 HTML 并组装, 最终渲染成 renders/video.mp4。

- 无截图摄取: 输入是代码变更而非网站, fetch-pr.mjs 走 gh (GitHub CLI) 确定性拉取, 用分页 gh api 补全文件列表防大 PR 在 ~100 文件处截断; ingest.mjs 只做离线转换; fetch 失败立即停止, 绝不虚构 PR 内容。
- 门控 + 真实性约束: 每步设 gate 未过不继续 (用户门控点在 Step 0/3/6); 代码帧只能引用从 diff.patch 选出的真实 hunk (≤12 行写进 ### Source excerpt), worker 禁止重开完整 diff; 片尾致谢只用真实贡献者头像。
- 外部依赖: 数据靠 gh; 旁白与 BGM 走 HeyGen API (TTS 生成 + 音乐库检索, 离线回退 Kokoro TTS), 渲染、block 目录搜索 (~400 个托管组件) 与技能更新靠 npx hyperframes CLI; build-frame.mjs 映射自校验, 出错 exit 1。
