# higgsfield-generate (`higgsfield-ai/skills/higgsfield-generate`)

## whitebox

- Bootstrap: 检查 higgsfield CLI 是否在 PATH, 缺失则用 curl 安装脚本装; 认证失效 (Session expired) 则要求用户交互式登录并等待确认
- 选模型: 按任务意图分类 (图像/视频/3D/音频/广告/视频分析), 用 higgsfield model list --json | jq 把显示名映射成 --model 的 job_set_type ID
- 校验参数: 不确定时跑一次 higgsfield model get <jst> --json, 只传必要参数其余吃 schema 默认值; 服务端对非致命值返回 adjustments 自动矫正
- 提交: higgsfield generate create <jst> [--prompt] [媒体/参数 flags] --wait, 单命令阻塞到终态并直接在 stdout 打印结果 URL
- 交付: 生成类给主结果 URL + 一行摘要 (模型/时长/GLB); Virality Predictor 给分数、业务解读和 Open 报告链接

- 纯 CLI 封装: 唯一可用工具是 Bash, 全部能力通过 higgsfield CLI 子命令实现 (generate create/wait/list, workflow, marketing-studio 系列), 无独立代码逻辑
- 媒体输入自动解析: --image/--video/--audio 等 flag 同时接受本地文件路径 (CLI 自动上传) 或 UUID (上传 id 或历史 job id, 自动区分), 无需预上传步骤
- 外部依赖: higgsfield CLI (curl 脚本安装), Higgsfield 平台模型 API (GPT Image 2.5 / Seedance 2.5 / Nano Banana 2 / Marketing Studio / Seed Audio 1.0 等), jq 用于解析 JSON 输出
