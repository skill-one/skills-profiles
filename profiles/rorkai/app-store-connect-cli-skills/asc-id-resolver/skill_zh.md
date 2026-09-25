# asc id resolver

使用此功能将名称映射到其他命令所需的 ID。

## App ID
- 通过 bundle ID 或名称：
  - `asc apps list --bundle-id "com.example.app"`
  - `asc apps list --name "My App"`
- 获取所有：
  - `asc apps list --paginate`
- 设置默认值：
  - `ASC_APP_ID=...`

## Build ID
- 最新构建：
  - `asc builds info --app "APP_ID" --latest --version "1.2.3" --platform IOS`
- 最近构建：
  - `asc builds list --app "APP_ID" --sort -uploadedDate --limit 5`

## Version ID
- `asc versions list --app "APP_ID" --paginate`

## Digital-goods version IDs

API 4.4.1 版本 ID 与 IAP 产品、订阅和订阅组 ID 不同：

首先解析所属资源：

- IAP：`asc iap list --app "APP_ID" --paginate --output json`
- 订阅组：`asc subscriptions groups list --app "APP_ID" --paginate --output json`
- 订阅：`asc subscriptions list --app "APP_ID" --paginate --output json`
  或 `asc subscriptions list --group-id "GROUP_ID" --paginate --output json`

然后解析它们的版本 ID：

- IAP 版本：`asc iap versions list --iap-id "IAP_ID" --paginate --output json`
- 订阅版本：`asc subscriptions versions list --subscription-id "SUB_ID" --paginate --output json`
- 订阅组版本：`asc subscriptions groups versions list --group-id "GROUP_ID" --paginate --output json`

从相应的版本子树解析子本地化或图像 ID：

- IAP 本地化：`asc iap versions localizations list --version-id "VERSION_ID" --paginate --output json`
- IAP 主要图像：`asc iap versions image --version-id "VERSION_ID" --output json`
- IAP 图像集合：`asc iap versions images list --version-id "VERSION_ID" --paginate --output json`
- 订阅本地化：`asc subscriptions versions localizations list --version-id "VERSION_ID" --paginate --output json`
- 订阅主要图像：`asc subscriptions versions images primary --version-id "VERSION_ID" --output json`
- 订阅图像集合：`asc subscriptions versions images list --version-id "VERSION_ID" --paginate --output json`
- 订阅组本地化：`asc subscriptions groups versions localizations list --version-id "VERSION_ID" --paginate --output json`

## TestFlight IDs
- 组：
  - `asc testflight groups list --app "APP_ID" --paginate`
- 测试者：
  - `asc testflight testers list --app "APP_ID" --paginate`

## Pre-release version IDs
- `asc testflight pre-release list --app "APP_ID" --platform IOS --paginate`

## Review submission IDs
- `asc review submissions list --app "APP_ID" --paginate`

## 输出提示
- 输出默认值是 TTY-aware：终端中的表格和管道或 CI 中的压缩 JSON。显式的 `--output` 优先。
- 用于自动化时使用显式的 `--output json`，仅对人类可读的 JSON 添加 `--pretty`。
- 对人类查看，使用 `--output table` 或 `--output markdown`。

## Guardrails
- 在列表命令上优先使用 `--paginate` 以避免遗漏 ID。
- 在可用时使用 `--sort` 使结果确定性。
