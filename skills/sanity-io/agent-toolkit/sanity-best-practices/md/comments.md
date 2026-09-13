# sanity-best-practices (`sanity-io/agent-toolkit/sanity-best-practices`)

## comments

- user: 电商前端, category: 坑, comment: 把产品演示视频直接传 Sanity file 字段，流量按原始下载计，月底账单吓人。改用 Mux 插件或 Vimeo 存嵌入链接才省心。
- user: 从 Contentful 迁来的内容工程师, category: 坑, comment: 建文档时自己拼 slug 当 _id，同步数据就冲突。后来全交给 Sanity 生成，只有首页这类单例才手写 homePage-en 这种 ID。
- user: Next.js 独立开发者, category: 妙用, comment: 不整本读，直接报任务关键词，只让它加载对应的一两篇参考文档；答案带错误/正确代码对照，照着改就能过。
- user: 刚接手老项目的新人, category: 注意, comment: 提问先说清用哪个框架，Next.js 和 Astro 接法完全不同；问 GROQ 报错时把原文一起贴，定位快很多。
- user: 带团队的技术负责人, category: 启发, comment: 以前关联内容全塞数组里，被提醒改回 reference 字段加 GROQ 解析后，查询和复用都清爽了——模型定对，后面才顺。
- user: 搞自动化的运维老哥, category: 妙用, comment: Blueprints 一定先 plan 再 deploy，变更预览能提前抓错；再配 Functions 监听文档事件自动打标签，运营基本不用手动了。
