# wind-mcp-skill (`wind-alice/alicemarket/wind-mcp-skill`)

## whitebox

- 定路由：按用户意图的标的类型归类到 7 个领域之一（股票/基金/指数/债券/公告文档/宏观EDB/跨标的聚合），选定 server_type 后只读该领域的契约文件（references/*.md）
- 发命令：cd 到 skill 所在目录，执行 node scripts/cli.mjs call <server_type> <tool_name> '<params_json>'，参数名与取值一律以契约为准
- 读回执：成功时 stdout 是数据对象，后端结果在 content[0].text（多为 JSON）；失败时是 {ok:false, code, message} 错误信封
- 失败自检重试：按 code/message 对照契约修正参数后重发；仅 PARAM_VALIDATION_ERROR 才允许改业务参数，改前逐条过自检清单
- 收口：只报告 Wind 返回值及自带单位元数据，不补常识点评；附数据来源声明并给出完成状态码（DONE / NO_RESULTS / OUT_OF_SCOPE 等）

- 契约驱动 + 禁猜原则：参数名、枚举、字段值只能来自当前领域契约文件，不得凭记忆填；标的未识别（NER 失败）时只询问用户准确全称或 Wind 代码，不自行补交易所后缀
- 外部依赖：本地 Node.js CLI（scripts/cli.mjs）经网络中转调用 Wind 的 7 个 MCP 服务；非 POSIX 环境（PowerShell/cmd 等）把 UTF-8 JSON 参数写入 scripts/request-<唯一后缀>.json 以 @file 传入、用后即删；兜底工具 wind-alice 需先经 npx skills add 安装并征得用户同意
- 探针式流量控制：默认串行（并发 1）；对 2 个以上标的批量调用时先发 1 个探针，探针返回错误信封立即终止整批、不扩散；用户明确要求并发才放宽到上限 10，遇 RATE_LIMIT_ERROR 即回退串行；价格指标单次调用最多 50 个代码（逗号分隔）
