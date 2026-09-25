# asc app create (UI自动化)

使用此技能通过驱动网页UI创建新的App Store Connect应用。
这是一种可选的、仅限本地的自动化，需要用户登录。

## 前置条件
- 可用浏览器自动化工具（Playwright、Cursor browser MCP或等效工具）。
- 用户已登录App Store Connect（或可以完成登录+双因素认证）。
- **bundle ID必须在Apple Developer门户中预先注册**。
- 已知所需输入：
  - 应用名称（最多30个字符）
  - bundle ID（必须存在且未被其他应用使用）
  - SKU
  - 平台（iOS、macOS、tvOS、visionOS）
  - 主要语言
  - 用户访问权限（完全访问或有限访问）

## 安全防护措施
- 永不导出或存储cookies。
- 仅使用可见的浏览器会话。
- 在点击"创建"前暂停最终确认（适用于独立脚本）。
- 失败时不要自动重试创建操作。

## 工作流程

### 1. 预检查：注册bundle ID并验证无现有应用
```bash
# 通过公共API注册bundle ID（如果尚未注册）
asc bundle-ids create --identifier "com.example.app" --name "My App" --platform IOS

# 确认尚无应用记录
asc apps list --bundle-id "com.example.app" --output json
```

### 2. 打开App Store Connect
导航至`https://appstoreconnect.apple.com/apps`并确保用户已登录。

### 3. 打开新建应用表单
"新建应用"按钮（蓝色"+"图标）会打开**下拉菜单**，而不是直接弹出对话框。
- 点击"新建应用"按钮打开下拉菜单。
- 点击下拉菜单中的"新建应用"**菜单项**。
- 创建对话框/模态框出现。

### 4. 按顺序填写必填字段

#### 平台（复选框）
平台是**复选框**（非单选按钮）。点击所需平台(们)的复选框：
- iOS、macOS、tvOS、visionOS
- 可多选。

#### 名称（文本输入）
- 标签：`名称`
- 最多30个字符。

#### 主要语言（选择/组合框）
- 标签：`主要语言`
- 使用`select_option`或等效方式，通过语言标签（例如，`"English (U.S.)"`）进行选择。

#### bundle ID（选择/组合框）
- 标签：`bundle ID`
- 这是一个`<select>`下拉框。平台选择后，选项会异步加载。
- 等待下拉框加载完成（初始显示"加载中..."）。
- 通过匹配包含名称和标识符的标签文本来选择：
  `"My App - com.example.app"`

#### SKU（文本输入）
- 标签：`SKU`

#### 用户访问权限（单选按钮）-- 必填
- **此字段必填**。创建按钮在未选择选项前保持禁用状态。
- 选项：`Limited Access`或`Full Access`。
- 这些是带有`<span>`覆盖层的自定义单选按钮。
- **已知问题**：基于可访问性的点击可能被覆盖层`<span>`拦截。
- **解决方案**：首先将单选元素滚动到视图中（`scrollIntoView`），然后直接点击单选引用。这可绕过覆盖层拦截。

### 5. 点击创建
- "创建"按钮在所有必填字段填写**且**用户访问权限选择后才会启用。
- 点击后，按钮文本会变为"正在创建"以显示处理状态。
- 等待导航至新应用的页面（URL模式：`/apps/<APP_ID>/...`）。

### 6. 通过API验证创建结果
```bash
asc apps view --id "APP_ID" --output json --pretty
# 或
asc apps list --bundle-id "com.example.app" --output json
```

### 7. 交接至创建后设置
```bash
asc app-setup info set --app "APP_ID" --primary-locale "en-US"
asc app-setup categories set --app "APP_ID" --primary GAMES
asc pricing availability create \
  --app "APP_ID" \
  --territory "USA,GBR" \
  --available true \
  --available-in-new-territories true
```

仅首次可用性引导时使用`asc pricing availability create`。如果Apple拒绝该公共API引导，使用`asc web auth login --apple-id "EMAIL"`认证网页会话，并重试`asc web apps availability create --app "APP_ID" --territory "USA,GBR" --available-in-new-territories true`，或直接在App Store Connect中配置定价和可用性。如果应用可用性已存在，后续区域变更时切换至`asc pricing availability edit --app "APP_ID" ...`。

## 已知的UI自动化问题

### "新建应用"是下拉菜单，非直接操作
首次点击会打开包含"新建应用"和"新建应用包"的菜单。必须点击菜单项，不能仅点击按钮。

### 用户访问权限单选按钮有span覆盖层
Apple的自定义单选按钮将`<input type="radio">`包裹在样式化的`<span>`元素中。基于引用的点击可能因"点击目标被拦截"而失败。解决方案：
1. 将单选元素滚动到视图中（`scrollIntoView`）。
2. 直接点击单选引用（非通过偏移或标签点击）。

### bundle ID下拉框异步加载
选择平台后，Bundle ID下拉框显示"加载中..."并处于禁用状态。等待其启用并填充后再选择。

### browser_fill可能无法触发表单验证
Apple的Ember.js表单使用自定义变更处理器。`browser_fill`（原子设置）可能无法触发验证。如果创建按钮在填写所有字段后仍禁用：
- 在至少一个文本字段中缓慢逐字符重写值。
- 或点击字段，清除内容，然后缓慢输入。

## 失败处理
- 如果任何字段或按钮无法定位，停止并请求用户帮助。
- 捕获屏幕截图并报告最后已知步骤。
- 不要自动重试创建点击。
- 失败时，用户应检查浏览器中的验证错误（红色轮廓、内联消息）。

## 注意事项
- 此技能是为解决缺失的公共API而设计的替代方案。Apple文档明确指出："不要使用此API创建新应用；而是在App Store Connect网站上创建新应用。"
- UI选择器可能无通知更改。优先使用角色/标签/文本选择器而非CSS。
- 唯一的手动步骤是登录。其他操作均可由代理驱动。
