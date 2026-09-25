# Chrome Web Store 发布蓝图

使用此技能作为动手设置指南。代理应逐步引导用户，请求确认，并且仅在本地/CI中可以完成的部分进行自动化。

## 此技能的用途

- 帮助用户从头开始设置 Chrome Web Store 发布自动化。
- 为 Google/CWS 控制台步骤提供清晰的逐步手动说明。
- 在用户提供凭证后，在代码库端实施脚本/工作流。
- 验证提交状态（`PUBLISHED`、`PENDING_REVIEW` 等）。

## 代理行为规则

- 将控制台/OAuth 任务视为用户驱动；不要暗示您已执行它们。
- 一次给出一个清晰的步骤，并在继续之前等待确认。
- 仅在需要时请求确切值，并告知用户每个值来自何处。
- 在日志中遮盖秘密，切勿将秘密值提交到 git。
- 如果 `gh` 可用，提供秘密上传自动化；如果不可用，提供手动回退方案。

## 第 1 步：项目发现（在执行任何凭证工作之前）

收集以下输入：

- 包含扩展版本的清单路径
- 构建命令
- 压缩/打包命令和输出文件名/路径
- CI 平台（默认为 GitHub Actions）
- 发布分支策略（`main`、标签或手动触发）
- 本地秘密文件约定（`.env`、`.env.local` 等）

明确询问：

- "您是否希望 CI 仅在版本更改时发布？"
- "您是否希望我通过 `gh` 配置 GitHub 秘密上传？"

## 第 2 步：详细凭证步骤（用户 + 代理）

### 2.1 在 Google Cloud 中启用 API

指示用户打开：

- `https://console.cloud.google.com/apis/library/chromewebstore.googleapis.com`

用户操作：

1. 选择预期的 Google Cloud 项目。
2. 点击 Chrome Web Store API 的 `启用`。

代理提示示例：

- "当 Chrome Web Store API 显示为已启用时，请告诉我，然后我将进入 OAuth 设置步骤。"

### 2.2 配置 OAuth 同意屏幕

指示用户打开其中一个：

- `https://console.cloud.google.com/apis/credentials/consent`
- 如果 UI 重定向，请继续在 Google 认证平台同意屏幕页面中操作。

用户操作：

1. 选择 `外部` 用户类型（适用于非工作区内部应用）。
2. 填写应用名称、支持邮箱、开发者联系邮箱。
3. 保存并继续，除非需要自定义范围。
4. 如果应用处于测试模式，请添加您的 Google 账户作为测试用户。
5. 保存。

代理指导：

- 如果用户希望获得稳定的长期有效刷新令牌行为，建议在准备就绪时将同意屏幕迁移到生产环境。

### 2.3 创建 OAuth 客户端

指示用户打开：

- `https://console.cloud.google.com/apis/credentials`

用户操作：

1. 点击 `创建凭证` -> `OAuth 客户端 ID`。
2. 选择应用程序类型 `Web 应用`。
3. 精确添加授权重定向 URI：
- `https://developers.google.com/oauthplayground`
4. 创建客户端。

捕获值：

- `CWS_CLIENT_ID`
- `CWS_CLIENT_SECRET`

代理提示示例：

- "准备好时粘贴 `CWS_CLIENT_ID` 和 `CWS_CLIENT_SECRET`（我将将其视为秘密）。"

### 2.4 生成刷新令牌（OAuth Playground）

指示用户打开：

- `https://developers.google.com/oauthplayground/`

用户操作：

1. 点击设置齿轮图标。
2. 启用 `使用您自己的 OAuth 凭证`。
3. 粘贴 `CWS_CLIENT_ID` 和 `CWS_CLIENT_SECRET`。
4. 在步骤 1 中，输入范围：
- `https://www.googleapis.com/auth/chromewebstore`
5. 点击 `授权 API`。
6. 使用拥有/发布扩展的相同 Google 账户登录。
7. 点击 `使用授权代码交换令牌`。
8. 复制刷新令牌。

捕获值：

- `CWS_REFRESH_TOKEN`

代理提示示例：

- "现在粘贴 `CWS_REFRESH_TOKEN`。我将仅将其存储在本地秘密存储/CI 秘密中。"

### 2.5 捕获商店 ID

捕获：

- `CWS_EXTENSION_ID`（来自商店/开发者列表 URL 的扩展项 ID）
- `CWS_PUBLISHER_ID`（来自 Chrome Web Store 开发者账户上下文的开发者/发布者 ID）

代理说明：

- 如果用户不确定，请要求他们打开 Chrome Web Store 开发者控制台，并从项目/账户 URL 或账户详细信息中复制 ID。

### 2.6 凭证检查清单

在继续之前，确保所有五个都存在：

- `CWS_CLIENT_ID`
- `CWS_CLIENT_SECRET`
- `CWS_REFRESH_TOKEN`
- `CWS_PUBLISHER_ID`
- `CWS_EXTENSION_ID`

## 第 3 步：本地秘密文件和 CI 秘密设置

创建一个本地模板文件（不提交实际值）：

```env
CWS_CLIENT_ID=
CWS_CLIENT_SECRET=
CWS_REFRESH_TOKEN=
CWS_PUBLISHER_ID=
CWS_EXTENSION_ID=
```

确保实际秘密文件路径被 git 忽略。

如果使用 GitHub Actions，询问用户是否希望 `gh` 自动化。

如果同意，验证：

```bash
gh --version
gh auth status
```

如果 `gh` 认证缺失，请告知用户运行：

- `gh auth login`

然后实现一个辅助脚本，该脚本应：

- 从本地 env 文件读取秘密值
- 验证所有必需的键是否存在
- 支持 `--dry-run`
- 在干运行输出中遮盖值
- 使用 `gh secret set ... --repo ...` 上传
- 在缺少键/认证时快速失败

如果用户拒绝 `gh`，请为仓库设置提供手动秘密输入清单。

## 第 4 步：发布工作流蓝图（版本触发）

围绕以下逻辑设计 CI 工作流：

1. 读取本地清单版本。
2. 可选地与次要版本文件进行比较，并在不匹配时失败。
3. 使用刷新令牌交换访问令牌：
- `POST https://oauth2.googleapis.com/token`
4. 获取 CWS 状态：
- `GET https://chromewebstore.googleapis.com/v2/publishers/<publisherId>/items/<extensionId>:fetchStatus`
5. 从以下提取当前已发布版本：
- `publishedItemRevisionStatus.distributionChannels[0].crxVersion`
6. 如果本地版本等于已发布版本，则跳过发布。
7. 如果版本已更改：
- 构建包 zip
- 上传 zip：
  `POST https://chromewebstore.googleapis.com/upload/v2/publishers/<publisherId>/items/<extensionId>:upload`
- 在需要时使用轮询处理异步上传状态
- 发布：
  `POST https://chromewebstore.googleapis.com/v2/publishers/<publisherId>/items/<extensionId>:publish`

将以下发布状态视为成功提交：

- `PENDING_REVIEW`
- `PUBLISHED`
- `PUBLISHED_TO_TESTERS`
- `STAGED`

## 第 5 步：提交状态检查器蓝图

创建一个专用于“最新提交状态是什么”的脚本。

必需行为：

- 接受环境值（并可选接受 `--env-file`）
- 可选地接受 `--manifest` 以进行本地版本比较
- 支持 `--json`
- 调用令牌端点 + `fetchStatus`
- 输出规范化字段：
  - `itemId`
  - `localVersion`
  - `publishedVersion`
  - `publishedState`
  - `submittedVersion`
  - `submittedState`
  - `upToDate`
  - `pendingReview`
- 在认证/API/输入错误时非零退出

包含以下有用检查：

- 标记清单和包元数据之间的版本不匹配
- 显示上传的版本是否处于待审核状态但尚未发布
- 当不使用 `--json` 时打印简洁的人类摘要

## 第 6 步：引导验证流程

与用户一起运行：

1. 在发布之前确认状态检查器运行成功。
2. 在所有版本源中增加扩展版本（补丁）。
3. 推送分支并触发工作流。
4. 确认工作流要么：
- 跳过（如果无版本更改），要么
- 上传并提交发布。
5. 重新运行状态检查器：
- 在许多情况下，首先期望 `PENDING_REVIEW`
- 后续期望发布渠道与本地版本匹配

## 故障排除脚本（代理应说明的内容）

- `invalid_grant`：
- 可能是刷新令牌错误/过期、OAuth 客户端错误或账户错误
- 从 CWS 端点返回的 `403`：
- 账户缺乏对扩展的发布者权限
- 工作流无操作：
- 本地版本按设计等于已发布版本
- 上传失败：
- 检查 API 响应和打包 zip 结构/清单有效性
- 版本不匹配保护失败：
- 在发布之前对齐所有声明的版本文件

## 实用链接（在指导过程中分享）

- Chrome Web Store API 概述：
`https://developer.chrome.com/docs/webstore/using-api`
- 发布端点：
`https://developer.chrome.com/docs/webstore/publish`
- OAuth Playground：
`https://developers.google.com/oauthplayground/`
- API 启用页面：
`https://console.cloud.google.com/apis/library/chromewebstore.googleapis.com`
- 凭证页面：
`https://console.cloud.google.com/apis/credentials`

## 安全限制

- 永不提交凭证。
- 永不在工作流 YAML 中硬编码秘密。
- 永不自动发布每个推送，而不进行版本比较。
- 保持设置说明清晰，并在每个手动步骤中确认用户。
- 优先选择可重复的辅助脚本，而不是临时的单次命令。
