# wecomcli-meeting (`wecomteam/wecom-cli/wecomcli-meeting`)

## whitebox

- 识别用户意图 → 映射到一种操作类型（创建/列表/搜索/详情/更新/取消/转写原文/纪要总结）
- 创建类先做消歧：用户没明确『日程还是会议』时，固定追问『需要创建日程还是会议？』再路由（查询类不追问，模糊则日程+会议都查后合并展示）
- 用 Read 读取该操作的参考文档（强制步骤，禁止凭记忆直接执行命令），拿到精确的参数格式与工作流
- 参数补全与校验：姓名经 wecomcli-contact 解析成 wo 前缀 userid；查忙闲、订会议室需借 wecomcli-calendar 技能；缺失的必要参数用文字向用户追问
- 执行 wecom-cli meeting [action] --json，再按输出规范渲染结果（只展示主题/时间/人名，不暴露 userid、会议号、入会链接）

- 技能间协作链：本体只封装企业微信 meeting 接口（依赖外部二进制 wecom-cli，JSON 单引号传参）；姓名→userid 依赖 wecomcli-contact 技能搜索验证（禁止拼接/猜测）；忙闲查询与会议室查询（buildings list + rooms search 拿 meeting_room_id）依赖 wecomcli-calendar 技能。
- 上下文传递表驱动：操作间靠提取字段串联——search/list 返回的 meeting_id（mt 前缀长串）喂给 get/cancel/update/original get，周期会议额外带 sub_meeting_id；attendees 必须是 [{"userid":"woxxx"}] 对象数组；get 返回的 repeat_rule 非空即周期会议，cancel/update 直接拒绝并引导客户端手动操作。
- 规则校验硬约束：写操作参数就绪即执行不二次确认；权限判定交给接口（返回权限错误才提示，不重试）；同一操作失败最多重试 2 次后停止并输出诊断；搜索/列表查无时主动兜底去日程侧再查一把（「会」可能落在日程里）。
