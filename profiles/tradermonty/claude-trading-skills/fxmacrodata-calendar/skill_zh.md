# FXMacroData 日历

从 FXMacroData 获取官方来源的宏交易日历事件。当交易计划需要事件时间、确认的发布日期或顶级宏交易风险检查时，使用此技能。

## 工作流程

1. 运行日历脚本：

   ```bash
   python3 skills/fxmacrodata-calendar/scripts/fetch_calendar.py --currency usd --min-tier 1
   ```

2. 查看 `events[]` 以获取顶级发布。

   将非零退出视为未验证的事件风险状态，而不是空日历。只有包含 `events: []` 的成功响应才能确定未返回匹配事件。客户端仅在响应货币与请求匹配且 `data_quality` 确认官方、当前、非代理、非回退、时间戳完整、时间点安全的来源时才接受结果。每个事件必须包含公告时间戳和非空的发布标识符。

3. 将事件时间整合到交易计划中：
   - 在高影响发布周围暂停新入场；
   - 降低杠杆或头寸规模；
   - 在实际值可用后安排后续审查；
   - 说明导致调整的事件和时间戳。

## 认证

为经过认证的 FXMacroData 端点设置 `FXMACRODATA_API_KEY`。可以无需密钥获取公共 USD 日历行。客户端使用标准的 `https://api.fxmacrodata.com/v1` 端点，并仅接受 `--min-tier` 值 1、2 或 3。当前的实时日历响应包含 `market_tier`；该技能将其视为扩展字段，并要求使用 1 到 3 的整数值进行过滤，尽管当前的 `CalendarReleaseRow` OpenAPI 模式未声明该字段。
