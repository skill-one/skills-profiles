# remotion-interactivity (`remotion-dev/skills/remotion-interactivity`)

## comments

- user: React 前端老兵, category: 坑, comment: 我习惯把样式抽成常量再展开进 style, 结果 Studio 里整块灰掉调不了。想可编辑, 就得老老实实把样式内联写全。
- user: 从 CSS 动画转过来的, category: 坑, comment: 动画我用 transform: translateX 写, Studio 完全认不出。换成独立的 translate 属性才能拖, transform 一次都别用。
- user: 第一次用的新手, category: 注意, comment: 别见 div 就套 Interactive, 元素一多时间轴全是节点找不到东西。只包需要调的几个, 并写死一个看得懂的 name。
- user: 独立全栈开发, category: 坑, comment: defaultProps 提取成变量又加了 as Props 断言, Props 面板改完保存不回代码。必须内联对象字面量, 类型写对就别断言。
- user: 电商短视频运营, category: 妙用, comment: 让开发把动画全写成内联 interpolate 后, 我在 Studio 里自己拖关键帧和缓动曲线, 改个出场节奏不用再排他的档期。
- user: 带团队的前端 lead, category: 启发, comment: 全内联、零复用, 起初很抗拒, 违背我的 DRY 本能。后来想通: 这代码是给编辑器读的配置, 按它的规矩写才换得来可视化编辑。
