# remotion-to-hyperframes (`heygen-com/hyperframes/remotion-to-hyperframes`)

## whitebox

- 跑 scripts/lint_source.py 扫描 Remotion 源码: 遇到阻断项 (useState/useEffect带依赖/UI库) 直接终止并推荐运行时互操作方案, 警告项则继续
- 读 references/api-map.md 按源码实际用到的 API 按需加载对应主题参考; 表格没覆盖的视觉效果先用 `npx hyperframes catalog --query` 搜在线组件库
- 生成 index.html: 根节点带 data-* 元数据, 场景为扁平 div 列表, CSS 定每个动画属性的 from 态, 底部一个暂停的 gsap.timeline, 把 useCurrentFrame 推导逐个转成对应偏移的 tween
- 双向渲染对比: Remotion 渲 baseline.mp4 + hyperframes 渲 hf.mp4 (像素格式须一致), 跑 render_diff.sh 算 SSIM, 低于复杂度档位阈值即失败, 用 frame_strip.sh 定位分歧帧
- 在 HF 输出旁写 TRANSLATION_NOTES.md 记录未干净转换的部分

- 静态 lint 门禁: Python 脚本按 阻断/警告/信息 三级分类模式, 只有阻断级才拒绝翻译——因为 HF 是 seek 驱动的确定性帧捕获, React 状态机无法翻译
- 机械映射 + 组件目录兜底: ~80% 的 Remotion 惯用法 (Sequence/spring/interpolate/TransitionSeries 等) 有直接 HF 对应物; 查表找不到的效果不手写 GSAP, 优先搜 hyperframes 托管注册表 (~400 个 block/component, 免安装), 但 SSIM diff 仍是最终裁决
- 量化验收: 转译质量不用肉眼判断, 用 SSIM (结构相似度) 对比双向渲染结果, 按源复杂度分档 (T1-T4 测试语料) 校验阈值; 手动播放器是注册在 window.__timelines 的单个 paused GSAP timeline
