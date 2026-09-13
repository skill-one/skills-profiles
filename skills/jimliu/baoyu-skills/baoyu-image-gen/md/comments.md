# baoyu-image-gen (`jimliu/baoyu-skills/baoyu-image-gen`)

## comments

- user: 自媒体插画新手, category: 坑, comment: 拿真人照片当参考图, 又写了段很长的外貌描述, 结果生成了个陌生人。改成一句「与参考图同一人, 只改场景和姿势」就稳了。
- user: 想白嫖订阅的开发者, category: 坑, comment: 把 Codex 登录令牌塞进 OPENAI_API_KEY 跑不通, 两套凭证不通用。装 codex 命令行并登录后, 用 --provider codex-cli 才能用订阅出图。
- user: 后端老兵, category: 注意, comment: 优先级是命令行 > EXTEND.md > 环境变量。我在 EXTEND.md 写死了模型, 环境变量一直不生效, 想临时换模型得用 --model。
- user: 第一次用的新手, category: 注意, comment: 第一次运行会强制先做配置, 提前把 API key 备好。默认 2k 高清出图慢, 试想法时加 --quality normal 快很多。
- user: 公众号配图编辑, category: 妙用, comment: 批量配图: 各张提示词先存成文件, build-batch 脚本合成 batch.json, --jobs 4 并行跑, 失败自动重试, 结束还汇总失败原因。
- user: 角色设计师, category: 启发, comment: 把 AI 生成图再喂回去当参考, 角色越改越走样。固定用 2~4 张原始素材才保得住脸; 出图太「网红脸」时, 明确写禁止瘦脸磨皮。
