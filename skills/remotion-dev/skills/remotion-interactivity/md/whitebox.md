# remotion-interactivity (`remotion-dev/skills/remotion-interactivity`)

## whitebox

- 接到 Remotion (用 React 写视频的框架) 组件任务, 先判断哪些元素、动画、视频/音频片段需要可在 Studio 中编辑
- 把 <div> 等元素改写成 Interactive.Div 等包装, 写死 name 属性, 只用一次的静态文本直接内联 (<Img>/<Video> 本身已交互式)
- 所有 CSS 写成内联 style 字面量对象; 动画写成内联 interpolate(frame, ...) 直接挂在变化的属性上, 输入/输出区间、easing、夹取全部硬编码
- 用 scale/translate/rotate 替代 transform; 组合元数据 (width/fps/durationInFrames/defaultProps) 保持内联, 动态部分只放 calculateMetadata()
- Remotion Studio 解析这套结构, 元素即可点选/拖拽/缩放, style 与关键帧在编辑器中可改; 结构过于复杂时对应值变灰不可编辑

- 结构约定式解析: Studio 靠 Interactive.* 包装 + 硬编码 name + 内联 style 字面量识别代码; 引用常量、对象展开、算术运算 (如 frame * 10) 均不被识别, 值会灰化
- 动画标准化: 内联 interpolate()/Easing (Remotion 自带 API) 被转成可编辑的关键帧与缓动; 输入只认 frame 及直接从 useVideoConfig() 解构的 durationInFrames/fps/width/height
- 可视化编辑回写: <Composition> 上内联的 defaultProps 让 Studio 的 Props 编辑器能把可视化修改保存回代码; effects 数组同理需内联且形状稳定
