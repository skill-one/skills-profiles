# general-video (`heygen-com/hyperframes/general-video`)

## whitebox

- 定位项目状态: 有 BRIEF.md 则按它续做; 新建先经 /hyperframes 路由, npx hyperframes init 脚手架后写入 BRIEF.md。
- 规划: 定故事弧与分场; 对需求点名的每种视觉风格先 npx hyperframes catalog --query 搜索托管注册表 (~400 个 block), 再落成 STORYBOARD.md 的 ## Frame N 调度块 (即使不评审也要写)。
- 构建场景: ≤6 个短场景时内联逐场实现 (先定稿末帧再从 blueprint/rules 加动效); 超出规模则用 frame-packets.mjs 打包, 单波分发给并行子代理 (每人 2~3 场)。
- 组装: 收拢各 worker 的 compositions/<frame_id>.motion.json (时长、出入场向量), 按生产循环挂载场景、媒体、转场、音频; 真实配音时长覆盖估算时长。
- 验证与出片: npx hyperframes check 通过后打开 Studio 终预览, 经用户批准才渲染。

- 确定性合成契约: 定时元素用 class="clip", 根及祖先节点定尺寸, 每个合成在 window.__timelines 注册唯一 paused、可 seek 的时间线; 禁止渲染期网络请求、时钟、未播种随机数, 保证渲染可复现。
- 分包调度机制: frame-packets.mjs 把每场的 storyboard 块 + blueprint 正文 + 所引用 rule 配方全部内联成 packet 及 _role.md; worker 只读 packet 与设计真源文件 (frame.md → design.md → DESIGN.md), 不读 STORYBOARD.md 和技能文档; 无子代理通道时回退为串行逐包处理。
- 校验链与外部依赖: 快速反馈用 npx hyperframes lint (首轮 HTML 及结构变更后), 终门用 npx hyperframes check (内部已含 lint, 不重复单跑); 媒体能力 (配音/BGM/SFX/字幕等) 经 /media-use 的 resolve 与 providers 流程接入外部服务, 首次鉴权动作前必跑 npx hyperframes auth status 并原样转述, 登出时按协作等待/自主走离线 provider 分流。
