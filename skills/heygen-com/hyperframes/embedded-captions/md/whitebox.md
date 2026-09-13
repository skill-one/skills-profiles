# embedded-captions (`heygen-com/hyperframes/embedded-captions`)

## whitebox

- 决策门先行: ffprobe + 按时间点抽帧探测视频, 硬性拒绝坏素材 (多说话人/无真人主体/已有烧录字幕/Whisper 转出乱语/小于3秒或无语音)。
- 从 CATALOG.md 的 35 个视觉身份里预筛 2~3 个, 推荐一个并让用户拍板 (自主模式下自选并说明理由); 身份一经选定即锁定后续引擎与编译器。
- hyperframes init 后跑 prepare.sh 一条命令: 抠像 (matte)、Whisper 转录、音频包络并行执行, 再算出 safe-zones.json (安全区 + 场景配色/光学/光照采样)。
- 唯一创意步骤: 手写一个小 JSON (电影模式 cinematic.json / 主题模式 theme.json), 交给锁定的编译器 (make-cinematic.cjs / render-theme.sh) 自动生成时序与合成层 — 不手写 HTML。
- preview-frames.cjs 以约 2 秒/帧出忠实合成预览做视觉 QA, 通过后 render-and-composite.sh 过确定性门禁产出 final.mp4 (主题模式一条命令直接出 final_fx.mp4)。

- 三分类字幕模型: 转录后每句话归为 drop (填充词, 不显示) / rail (前景底部逐字字幕, 承载正文) / embed (晋升高潮词, 合成到主体身后); hero 按语义块限流 (每块 ≤1 个、互不同框、间隔 <0.6s 编译器告警), 核心原则是嵌入必须稀缺, 全片嵌入是常见错误。
- 抠像遮挡合成, 原片零改动: matte.cjs 从原片分离主体前景; rail 在前、embed 在后, 主体自然遮挡大字形成景深; ffmpeg 亮度探测 (<60 / 60–180 / >180) 决定文字是否加 scrim, 但永不调色/改色原片 (唯一例外是主题模式的 plate reaction, 且在抠像合成之后应用)。
- 编译器生成 + 双重校验: 手写的只是声明式小 JSON, 由锁定编译器自动生成转录对齐时序、块内累积、hero lockup、阅读顺序; 渲染前 preview-frames.cjs (~2s/帧) 快速视觉 QA 避免整片渲染浪费, 渲染时再过 timing / occlusion+hero / overflow / hand-off 四道门禁才出片。外部依赖: ffmpeg/ffprobe (探测+渲染)、Whisper (transcribe.cjs 转录, 近静音时告警防幻觉词)、Node.js 脚本链、hyperframes CLI (init/技能更新)。
