# turborepo (`vercel/turborepo/turborepo`)

## whitebox

- 用户提出 monorepo 相关问题 (turbo.json、缓存、--filter、CI、环境变量、包结构等)，命中触发关键词
- 按内置决策树路由问题类型，定位到对应参考文档 (如缓存问题 → references/caching/gotchas.md)
- 对照反模式清单检查用户现有配置 (根脚本绕过 turbo、&& 链接任务、缺少 outputs、env 未哈希等)
- 按规则给出正确配置: 任务放进各 package.json，根 turbo.json 只注册任务，根 package.json 仅用 turbo run 委派

- 决策树路由: 用 'cache problems?'、'CI setup?' 等固定判断树把用户意图映射到具体 references/*.md 文档，而非自由发挥
- 反模式静态校验: 逐条比对已知错误写法 (turbo 简写写进代码、prebuild 手动构建依赖、--parallel、根目录 .env、跨包相对路径导入)，并判断是否声明 workspace 依赖 (workspace:*) 来决定修复方式
- 依赖图语义: dependsOn 中 ^build = 先构建依赖包、build = 同包内先构建、pkg#task = 指定包任务，以此推导任务编排和缓存失效条件 (env/inputs 进哈希)
