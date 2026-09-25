# asc 命令行工具使用方法

当您需要运行或设计 App Store Connect 的 `asc` 命令时，请使用此技能。

## 命令发现
- 始终使用 `--help` 来发现命令和标志。
  - `asc --help`
  - `asc builds --help`
  - `asc builds list --help`
- 当您知道工作流程但不知道命令路径时，使用 `asc search` 进行本地、确定性命令发现。
  - `asc search "提交应用进行审核"`
  - `asc search --output table "上传构建"`
- 使用 `asc schema` 在设计面向 API 的命令之前检查捆绑的 App Store Connect 端点模式以及请求/查询字段。
  - `asc schema --pretty "GET /v1/apps"`
  - `asc schema --method POST appStoreVersions`
- 使用 `asc capabilities` 解释 CLI 支持的、部分的、网页会话的和公共 API 有限的工作流程覆盖范围。
  - `asc capabilities --area 发布 --output table`
  - `asc capabilities --status 网页会话 --output table`
  - `asc capabilities --status 非公共 API --output markdown`

## 标准动词（当前 asc）
- 在文档和自动化中，优先使用 `view` 而不是遗留的 `get` 别名，用于只读命令。
  - `asc apps view --id "APP_ID"`
  - `asc versions view --version-id "VERSION_ID"`
  - `asc pricing availability view --app "APP_ID"`
- 优先使用 `edit` 用于只更新可用性界面和其他标准编辑流程。
  - `asc pricing availability edit --app "APP_ID" --territory "USA,GBR" --available true`
  - `asc app-setup availability edit --app "APP_ID" --territory "USA,GBR" --available true`
  - `asc xcode version edit --build-number "42"`
- 使用 `asc pricing availability create` 在使用只更新的 `edit` 命令之前初始化应用可用性。如果 Apple 拒绝公共 API 引导，请使用网页会话进行身份验证并使用 `asc web apps availability create`，或在 App Store Connect 中配置定价和可用性。
  - `asc pricing availability create --app "APP_ID" --territory "USA,GBR" --available true --available-in-new-territories true`
  - `asc web apps availability create --app "APP_ID" --territory "USA,GBR" --available-in-new-territories true`
- 在 CLI 意图建模高级级替换/配置流程且 `--help` 仍然显示 `set` 为标准动词的地方保留 `set`。

## 标志约定
- 使用明确的长标志（例如，`--app`、`--output`）。
- 在自动化中优先使用明确标志；一些较新的命令在交互式运行时可以提示缺失字段。
- 破坏性操作需要 `--confirm`。
- 当用户想要所有页面时，使用 `--paginate`。

## 输出格式
- 输出默认是 TTY 感知的：交互式终端中的 `table`，管道或非交互式时的 `json`。
- 仅用于人类可读输出，使用 `--output table` 或 `--output markdown`。
- `--pretty` 仅在与 JSON 输出一起使用时才有效。

## 身份验证和默认值
- 优先使用 `asc auth login` 进行密钥链身份验证。
- 备用环境变量：`ASC_KEY_ID`、`ASC_ISSUER_ID`、`ASC_PRIVATE_KEY_PATH`、`ASC_PRIVATE_KEY`、`ASC_PRIVATE_KEY_B64`。
- `ASC_APP_ID` 可以提供默认应用 ID。
- 当权限不明确时，使用 `asc web auth capabilities` 检查精确的 API 密钥角色覆盖范围。
  - 这位于网页会话身份验证界面下。
  - 它可以默认解析当前本地身份验证，或使用 `--key-id` 检查特定密钥。
- 通过缓存的 Apple 账户网页会话创建 App Store Connect 团队 API 密钥，使用 `asc web api-keys create`。
  - 需要账户持有人或管理员会话；在需要时，首先使用 `asc web auth login --apple-id "user@example.com"`。
  - 该命令将一次性 P8 保存为 `AuthKey_<KEY_ID>.p8`，不会打印其内容；使用 `--output-dir` 选择明确的私有目录。
  - 示例：`asc web api-keys create --name "CI 上传" --role APP_MANAGER --output-dir "./keys" --output json`。

## 在请求另一个代码之前重用身份验证
- API 密钥身份验证 (`asc auth`) 和 Apple 账户网页会话 (`asc web auth`) 是分开的。优先使用现有的密钥链 API 配置文件进行支持的操作；在开始网页登录之前检查 `asc auth status` 和命令功能。配置文件名称是本地标签，不是应用级权限边界。
- 对于仅限网页的工作，首先检查 `asc web auth status --apple-id "user@example.com" --output json`。重用经过身份验证的缓存会话，并在进行变更之前验证其提供者是否与预期账户匹配。不要作为常规准备注销或清除信任/会话状态。
- 为 Apple 账户提供一个交互式登录的所有权。当代码提示正在等待时，继续该相同进程；协调或串行化其他代理，而不是启动可能使其挑战失效的另一个登录。
- 将代码与当前提示匹配。受信任设备通知代码和短信备用代码属于不同的验证步骤。一旦 CLI 宣布电话交付，请使用新交付的电话代码，而不是早期的通知代码。不要故意提交错误代码作为正常重发策略；检查安装的命令的帮助以了解支持的恢复。
- 在失败时，区分代码拒绝与验证或提供者选择后的超时。在请求更多代码之前检查精确错误和安装版本。增加请求超时并不能证明交互式会话问题已解决。
- 登录后，使用单独的状态读取验证 `authenticated` 和选择的提供者；在报告成功之前确认下一个网页操作重用了缓存。Apple 可能稍后过期会话，因此不要承诺永久无人值守身份验证。
- 在配置支持的 `--two-factor-code-command` 之前检查 `asc web auth login --help`。将凭证和代码保持在日志、源代码、shell 历史记录和 PR 中。不要假设密码管理器密钥可以提供给 CLI 或浏览器登录刷新其缓存；仅使用安装的 CLI 明确支持的认证机制。

## Apple 广告
- 在选择命令之前使用 `asc ads --help`。
- Apple 广告使用 `asc ads auth`、`--ads-profile` 和 `ASC_ADS_*` 变量。它不使用 App Store Connect API 凭证。
- 直接资源命令使用 Platform API v1 并使用 `--ad-account` 或 `ASC_ADS_AD_ACCOUNT_ID`。已弃用的 Campaign Management API v5 命令位于 `asc ads v5` 下，并使用 `--org` 或 `ASC_ADS_ORG_ID`；永远不要用一个 ID 替换另一个。
- 使用 `asc ads auth discover --output json` 或检查一个 ACL 响应以 `asc ads acls list --output json` 发现广告账户访问权限。
- 身体命令使用 `--file` 并使用叶帮助命名的确切模式。V1 查询过滤器使用单数 `value`，并且批量身体可能使用包装对象而不是 v5 数组。
- Apple 广告资源命令发出 JSON。仅在帮助显示时使用 `--paginate`；报告和大多数查询身体在 JSON 文件中包含分页。
- 删除和支出、计费、交付、定位或访问敏感的变更需要 `--confirm`。明确暂停的营运动作是主要记录的安全例外。
- 对于实时变更测试，使用清晰的测试名称创建暂停资源，保存每个 ID，首先暂停支出承载资源，并仅删除测试创建的资源。

## 超时
- `ASC_TIMEOUT` / `ASC_TIMEOUT_SECONDS` 控制请求超时。
- `ASC_UPLOAD_TIMEOUT` / `ASC_UPLOAD_TIMEOUT_SECONDS` 控制上传超时。
