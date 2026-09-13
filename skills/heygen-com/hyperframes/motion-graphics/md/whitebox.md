# motion-graphics (`heygen-com/hyperframes/motion-graphics`)

## whitebox

- init: 运行 `npx hyperframes init` 在 videos/<project-name>/ 建项目骨架 (hyperframes.json)
- plan: 派 Director 子代理先判断"要不要搜索"——纯文字/图表任务走 form 类目 (kinetic-type/stat/charts/logo-reveal/lower-thirds/maps), 否则产出搜索计划; 写草稿 shot-plan.json (含 asset_needs)
- source (条件步): asset_needs 非空时用 media-use resolve 搜索/生成素材并冻结到 assets/; 为空则直接跳到设计
- design→build: Director Part 2 敲定镜头设计 (catalog block + 布局 + 动效节拍) 后, Builder 子代理 reuse-first 组合 (`npx hyperframes add <block>` + 原地定制), 产出 compositions/index.html
- verify→render: 跑 lint/check/snapshot 三道闸 (失败派修复子代理单轮修补) → 征得用户"渲染"许可 → `hyperframes render` 输出 MP4 或透明 overlay

- 中间表示 (IR) 驱动: shot-plan.json 是全流程唯一交接物, Director 按意图分派类目 (搜索驱动类目 webpage/news/tweet/asset-fusion 由搜索返回的内容类型最终确认); 另有 resume 表按工件存在与否支持断点续跑
- 确定性渲染合约: 产物是 HTML + 暂停在 0 的 GSAP timeline (window.__timelines、class="clip" + 稳定 id、tl.seek(0)), 由 hyperframes CLI (基于浏览器逐帧) 渲染成片, 依赖 Node/npx、ffmpeg, macOS 可开 GPU 硬件渲染; 正因确定性, lint/check/指定时间点 snapshot 才能作为校验闸门
- 复用优先 + 优雅降级: 视觉组件优先复用 catalog block 与 hyperframes-animation 规则/蓝图, 只手写缺口; 素材经 media-use 搜索/生成 (图像生成走 GEMINI_API_KEY, 缺 key 则该类目降级为无素材, 记入 context.log)
