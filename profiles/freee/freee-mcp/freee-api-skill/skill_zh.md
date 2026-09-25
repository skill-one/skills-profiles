# freee API 技能

## 概要

freee 的会计、人事劳务、发票、工时管理、销售、IT管理、固定资产、业务委托管理、调查、开业、人事评估、申报等数据可直接由AI操作。通过 [freee-mcp](https://www.npmjs.com/package/freee-mcp) (MCP服务器) 与freee API联动。

此技能的作用:

- 提供freee API的详细参考文档
- 提供freee-mcp使用指南和API调用示例

## 设置

若已安装`freee_*`工具，则无需设置。

仅当符合以下情况时，请引导用户阅读`SETUP.md`并指导连接步骤:

- 未安装任何`freee_*`工具
- `freee_auth_status`返回未认证，且通过「错误处理」步骤无法解决
- 用户询问连接方法或初始设置

连接模式可在`freee_server_info`的transport字段中确认（`remote` = 远程MCP，`stdio` = 本地）。

## 参考

API参考文档包含在`references/`目录中。每个参考文档包含参数、请求体、响应信息。

查找目标API的步骤:

1. 阅读`references/INDEX.md`（按服务分类的文件名和内容列表）
2. 若索引中无法找到，请在`references/`目录内进行关键词搜索

参考文档的格式:

- `名前*`表示必填，无标记表示可选
- 标题`### 请求体*`表示请求体本身为必填项
- 参数若无特别说明，均为query。`(path)` `(header)` 会明确标注在对应位置
- 参数名末尾的`[]`是参数名的一部分，API调用时不可省略
- `GET /xxx 与相同`表示同一文件内的对应端点与内容相同
- 响应仅记录顶级项目。嵌套结构需实际调用API确认

法人税报表XML（XTX / XBRL）的各元素与纸质报表项目的对应关系在`tax-return-references/`中。索引和通用规范在`tax-return-references/index.md`中，各报表文件可通过索引的报表列表使用`sheet_code`获取（报表系列中的附表或明细表会合并到一个文件中）。

## 使用方法

### MCP工具

认证与门店管理:

- `freee_authenticate` - OAuth认证（Remote MCP会自动处理认证，通常无需此步骤）
- `freee_auth_status` - 认证状态确认
- `freee_clear_auth` - 清除认证信息（本地模式使用）
- `freee_current_user` - 获取登录用户信息
- `freee_list_companies` - 门店列表
- `freee_set_current_company` - 切换门店
- `freee_get_current_company` - 获取当前门店

服务器信息:

- `freee_server_info` - 获取服务器信息（版本、transport: remote/stdio）

文件操作:

- `freee_file_upload` - 将文件上传至文件箱 (POST /api/1/receipts) ※仅限本地模式

API调用:

- `freee_api_get` - GET请求
- `freee_api_post` - POST请求
- `freee_api_put` - PUT请求
- `freee_api_delete` - DELETE请求
- `freee_api_patch` - PATCH请求
- `freee_api_list_paths` - 列出可用API路径

service参数（必填）:

- `accounting` - freee会计（交易、会计科目、交易对手等） 例: `/api/1/deals`
- `hr` - freee人事劳务（员工、考勤等） 例: `/api/v1/employees`
- `invoice` - freee发票（发票、报价单、送货单） 例: `/invoices`
- `pm` - freee工时管理（项目、工时等） 例: `/projects`
- `sm` - freee销售（报价、订单、销售额等） 例: `/businesses`
- `it_management` - freeeIT管理（SaaS账户、办公用品、成员） 例: `/hub/it_management/members`
- `fixed_asset_management` - freee固定资产（固定资产列表、详情、登记、更新、删除） 例: `/hub/fixed_asset_management/fixed_assets`
- `partner_management` - freee业务委托管理（业务委托企业的用户和部门） 例: `/hub/partner_management/orderer/company_users`
- `survey` - freee调查（调查计划、实施回）※仅限freee-mcp（远程版） 例: `/hub/survey/base_surveys`
- `launch` - freee开业（开业申请用数据的查看和更新）※仅限freee-mcp（远程版） 例: `/hub/launch/kaigyo_application`
- `employee_evaluation` - 人事评估（获取人事评估结果）※仅限freee-mcp（远程版） 例: `/hub/employee_evaluation/evaluation_results`
- `tax_return` - freee申报（法人税申报和报表查看） 例: `/hub/tax_return/corporate`

### 基本工作流程

若不确定连接模式，可通过`freee_server_info`确认（transport为`remote`则为远程MCP，`stdio`则为本地）。Remote MCP模式下，认证会自动处理，可直接从步骤1开始。本地模式下未认证需先执行`freee_authenticate`。

1. 确认门店: 使用`freee_get_current_company`获取当前门店ID（首次必须。会话内获取一次后可重复使用）
   - API按门店分离数据，若选择错误门店可能导致访问非预期数据
2. 确认食谱: 阅读`recipes/`内的对应食谱
   - 汇总了常见操作模式和注意事项，比直接调用API更高效且减少错误
3. 搜索参考: 根据需要从`references/INDEX.md`获取对应文件
   - 确认食谱中未包含的详细参数或响应规格
4. 调用API: 使用`freee_api_*`工具（需要company_id的端点使用步骤1获取的值）

注意:
- `company_id`必须与当前设置门店一致。不一致会导致错误
- 更改门店时: 先使用`freee_set_current_company`切换，再执行请求

### 食谱

常见操作的用户案例和技巧参考:

- `recipes/expense-application-operations.md` - 管理费用申请
- `recipes/deal-operations.md` - 交易（收入/支出）
- `recipes/manual-journal-operations.md` - 转账凭证
- `recipes/payment-request-operations.md` - 支付请求
- `recipes/hr-employee-operations.md` - 人事劳务（员工/工资）
- `recipes/hr-attendance-operations.md` - 考勤（出勤/打卡/休息登记）
- `recipes/invoice-operations.md` - 发票/报价单/送货单
- `recipes/receipt-operations.md` - 文件箱（凭证文件的上传/管理）
- `recipes/pm-operations.md` - 工时管理（项目/工时实绩）
- `recipes/pm-workload-registration.md` - 安全的工时登记（PM/HR协作流程）
- `recipes/sm-operations.md` - 销售管理（项目/订单）
- `recipes/it-management-operations.md` - IT管理（成员/SaaS账户/办公用品）
- `recipes/survey-operations.md` - 调查（调查计划/实施回获取）
- `recipes/launch-operations.md` - 开业（开业申请用数据的查看/更新）
- `recipes/fixed-asset-management-operations.md` - 固定资产管理（安全的更新/删除判断/转接至Web界面）
- `recipes/corporate-tax-return-operations.md` - 申报（法人税申报/报表查看）
- `recipes/report-operations.md` - 试算表/总账（报表获取/未审批分录确认）
- `recipes/freee-mcp-tag.md` - 附加「freee-mcp」标签的指南

## freee 签名（电子签约）

freee 签名由另一个MCP服务器（`freee-sign-mcp`）提供。
若可使用`sign_api_get`等签名工具，请参考`SIGN-GUIDE.md`。

## 数据可视化

若需将freee数据以图表、表格、HTML等形式可视化，请阅读`COLORS.md`并使用其中指定的配色方案。

## 错误处理

- 版本确认: 阅读`VERSION.md`确认技能版本（若文件不存在则使用开发版），并使用`freee_server_info`确认服务器版本。若技能版本较服务器版本旧，可能是技能信息未适配最新服务器。请更新技能至最新版后重试。
- 认证错误（Remote MCP）: MCP客户端（Claude Desktop等）会自动提示重新认证。若无法解决，请删除自定义连接器后重新添加。
- 认证错误（本地）: 使用`freee_auth_status`确认 → `freee_clear_auth` → `freee_authenticate`
- 门店错误: `freee_list_companies` → `freee_set_current_company`
- 详细说明: 参考`troubleshooting/INDEX.md`（按症状分为auth / company / expense-errors / support）

## 仅限freee-mcp（远程版）的端点

部分API端点仅可在freee-mcp（远程版）中使用，本地模式下不可使用。相关`recipes/` `references/`中会标注「⚠ freee-mcp（远程版）限定」。

调用对应端点前，请使用`freee_server_info`确认transport，若为`stdio`（本地模式），则不调用，并引导用户切换至freee-mcp（远程版）[设置方法](https://support.freee.co.jp/hc/ja/articles/56390747520537)。

## API功能限制

因freee API自身功能限制导致的问题，freee-mcp也无法解决。详情参考`troubleshooting/support.md`。
