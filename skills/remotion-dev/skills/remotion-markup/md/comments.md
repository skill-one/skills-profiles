# remotion-markup (`remotion-dev/skills/remotion-markup`)

## comments

- user: 前端老兵, category: 坑, comment: 把网页现成的 CSS transition 直接搬进来，预览正常一渲染就乱——CSS 动画不走时间轴，必须改写成 interpolate()。Tailwind 的 animate-* 类同理。
- user: 用了一年的老用户, category: 妙用, comment: 别写 transform 字符串，用独立的 scale/translate/rotate 属性，Studio 里每个关键帧能直接拖着调，不用回代码；scale 动画配 perceptual-scale 输出更顺滑。
- user: 第一次用的新手, category: 注意, comment: 素材必须放项目根目录 public/ 文件夹，代码里 staticFile("a.mp4") 引用。我写相对路径，预览能看、渲染时白屏。外网 URL 也可以直接传给 <Video>。
- user: 短视频博主, category: 妙用, comment: 字幕贴图错峰出场全靠 from + durationInFrames 按秒排，不用写条件判断；素材开头废几秒就 trimBefore 一行掐掉，内层时钟还会自动对齐。
- user: 后端转行做内容的, category: 注意, comment: 语音解说、地图、字幕不在基础能力里，要点名让 AI 去加载 voiceover/maps/captions 对应子文档；另外一次只提一个场景需求，成功率明显更高。
- user: 效率党运营, category: 启发, comment: 用 Zod schema 把标题、颜色做成参数后，一套模板换数据就能批量出片；验收不用整片渲染，npx remotion still --frame=30 抽一帧看就够。
