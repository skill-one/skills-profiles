# remotion-to-hyperframes (`heygen-com/hyperframes/remotion-to-hyperframes`)

## comments

- user: React 前端老兵, category: 坑, comment: 我的合成靠 useState+useEffect 驱动动画，lint 直接拦下——状态驱动没法逐帧翻译，只能走运行时互操作。先跑 lint 再动手，别白写。
- user: 独立开发者, category: 启发, comment: 翻译完肉眼看毫无破绽，diff 一跑 SSIM 低了 0.05，frame_strip 一查是 spring 时序偏了两帧。干这行久了才懂：迁移别信「看着对」，要量化验收。
- user: 渲染服务运维, category: 注意, comment: 第一次 diff 差值大得离谱，排查半天是两边编码没对齐。在 remotion.config.ts 里设 png + bt709 再比，否则量的是编码器噪音，不是翻译保真度。
- user: 视频团队负责人, category: 注意, comment: 提醒：这条路只进不出——HF 导不回 Remotion；AE、Framer Motion 的源也翻不了，得走原生流程重建。另外明确说出 port/convert 才会触发翻译。
- user: 设计师转开发, category: 妙用, comment: 源码里的 CRT 扫描线在 api-map 没对应项，用 catalog --query 搜托管库直接 add 现成组件，比手写 GSAP 逼近还准，SSIM 反而更高。
- user: 第一次用的新手, category: 坑, comment: 看到项目里有 @remotion/lambda 就以为不能迁，差点放弃。其实它只是 warning，会自动删掉照常翻译；真正拦路的是 useState。先跑 lint 再下结论。
