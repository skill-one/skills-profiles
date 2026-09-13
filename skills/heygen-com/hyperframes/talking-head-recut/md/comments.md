# talking-head-recut (`heygen-com/hyperframes/talking-head-recut`)

## comments

- user: 自媒体新手, category: 坑, comment: 转写最后一个词的时间戳常超出视频实际时长, 我没管, 成片结尾黑了一秒。让 AI 把每张卡和总时长都对齐原片元数据就没事了。
- user: 播客主理人, category: 妙用, comment: 只丢原始录像, 一句文案没写, AI 从转写里把我随口报的数字和金句全做成数据卡。播客先剪 5 分钟精华再包装, 快得多。
- user: 竖屏剪辑师, category: 妙用, comment: 同一条横版访谈选 16:9 和 9:16 各渲一版, 原片不动, 一鱼两吃发两平台。侧边卡在竖屏下会自动挪到底部, 不用重想版式。
- user: 程序员up主, category: 注意, comment: 开跑前先 npx hyperframes doctor, 我机器缺 ffmpeg 卡在转写那步; macOS 记得 export PRODUCER_BROWSER_GPU_MODE=hardware, 渲染明显快。
- user: 财经口播博主, category: 坑, comment: 我以为是自动加字幕的, 其实它做的是标题、数据卡这类设计图形, 原片完整播放不动。只想要口播字幕请找 embedded-captions。
- user: 知识区up主, category: 注意, comment: 开始会被问比例/布局/风格/卡数四个问题, 直接回"全用默认"可跳过。单张卡超 15 秒记得让它做分步弹出, 静态一句会很闷。
