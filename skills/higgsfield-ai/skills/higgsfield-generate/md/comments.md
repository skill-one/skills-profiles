# higgsfield-generate (`higgsfield-ai/skills/higgsfield-generate`)

## comments

- user: 电商运营, category: 妙用, comment: 不用自己抠图, 把商品页链接甩给它就导入产品了, 再挂个钩子十分钟出一条 UGC 广告片, 日常上新完全够用。
- user: 第一次用的新手, category: 坑, comment: 想让静态图动起来, 只写 prompt 会跑成一条全新视频; 必须带上 --start-image 并且选 omni_reference 模式, 纯文生视频模式不吃图。
- user: 视频剪辑师, category: 注意, comment: Seedance 2.5 最高 1080p, 要原生 4K 得换 2.0; 长视频默认只等 10 分钟, 别像我一样中途超时, 先把 --wait-timeout 调到 20m。
- user: 独立开发者, category: 妙用, comment: 把上一次生成的 job id 直接当参考图喂回去, 抽卡式迭代不用下载再上传, 一晚上能磨出满意的角色图。
- user: 投放优化师, category: 坑, comment: 钩子和场景 ID 只在 ugc 系列和 product_review 模式有效, 我在 tv_spot 里挂直接被拒; 另外广告参考视频和钩子二选一, 不能同时给。
- user: 营销总监, category: 启发, comment: 以前死磕 prompt 措辞, 现在先选对模型: 角色图给 Nano Banana, 带文字的海报给 GPT Image, 一次过的概率高很多。
