# asc 元数据同步

使用此功能将 App Store 元数据与 App Store Connect 同步。优先使用标准的 `asc metadata` 工作流程来处理 app-info 和版本本地化字段。仅在用户需要 `.strings` 文件或遗留 fastlane-format 元数据时，才使用较低级别的 `asc localizations` 和 `asc migrate` 命令。

## 当前标准工作流程

### 1. 拉取标准元数据

```bash
asc metadata pull --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

如果应用有多个 app-info 记录，请先解析 app-info ID，然后显式传递：

```bash
asc apps info list --app "APP_ID" --output table
asc metadata pull --app "APP_ID" --app-info "APP_INFO_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

### 2. 编辑本地文件

标准文件写入路径如下：

- `metadata/app-info/<locale>.json` 用于应用级字段：`name`、`subtitle`、`privacyPolicyUrl`、`privacyChoicesUrl`、`privacyPolicyText`
- `metadata/version/<version>/<locale>.json` 用于版本字段：`description`、`keywords`、`marketingUrl`、`promotionalText`、`supportUrl`、`whatsNew`

版权不是本地化字段。使用以下命令管理：

```bash
asc versions update --version-id "VERSION_ID" --copyright "2026 Your Company"
```

### 3. 上传前验证

```bash
asc metadata validate --dir "./metadata" --output table
```

对于订阅应用，包含额外的 Terms of Use / EULA 启发式：

```bash
asc metadata validate --dir "./metadata" --subscription-app --output table
```

### 4. 预览和应用

先运行干运行：

```bash
asc metadata push --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --dry-run --output table
```

计划正确后应用：

```bash
asc metadata push --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

当用户希望使用相同的标准文件时，使用 `asc metadata apply`：

```bash
asc metadata apply --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --dry-run
asc metadata apply --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
```

对于需要显式批准后再变更的 review-artifact 工作流程，使用 `asc` 2.6.1 引入的元数据审查命令：

```bash
asc metadata plan --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --review-dir ".asc/metadata/review"
asc metadata approve --review-dir ".asc/metadata/review" --all
asc metadata status --review-dir ".asc/metadata/review" --output table
asc metadata apply --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --review-dir ".asc/metadata/review" --confirm
```

当用户希望在受保护的 apply 之前进行选择性批准时，使用 `asc metadata approve --key "version:1.2.3:en-US:whatsNew"` 或 `--scope app-info,version`。版本范围键包含 App Store 版本字符串。

## 关键字工作流程

当只有版本本地化 `keywords` 字段需要变更时使用：

```bash
asc metadata keywords diff --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"
asc metadata keywords apply --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --confirm
```

用于导入关键字研究：

```bash
asc metadata keywords import --dir "./metadata" --version "1.2.3" --locale "en-US" --input "./keywords.csv"
asc metadata keywords sync --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata" --input "./keywords.csv"
```

## 快速字段更新

对于一次性版本本地化编辑，传递显式的版本选择器。当您已有 `--version-id` 时使用 `--version-id` 进行确定性更新，或使用 `--version` 加 `--platform` 从版本字符串工作：

```bash
asc apps info edit --app "APP_ID" --version-id "VERSION_ID" --locale "en-US" --whats-new "Bug fixes and improvements"
asc apps info edit --app "APP_ID" --version "1.2.3" --platform IOS --locale "en-US" --description "Your app description here"
asc apps info edit --app "APP_ID" --version "1.2.3" --platform IOS --locale "en-US" --keywords "keyword1,keyword2,keyword3"
asc apps info edit --app "APP_ID" --version "1.2.3" --platform IOS --locale "en-US" --support-url "https://support.example.com"
```

对于 app-info 字段，优先使用 post-create 设置命令：

```bash
asc app-setup info set --app "APP_ID" --primary-locale "en-US" --privacy-policy-url "https://example.com/privacy"
asc app-setup info set --app "APP_ID" --locale "en-US" --name "Your App Name" --subtitle "Your subtitle"
```

## 较低级别的本地化文件

当用户需要导入/导出文件而不是标准 JSON 时，使用 `.strings` 文件：

```bash
asc localizations list --version "VERSION_ID" --output table
asc localizations download --version "VERSION_ID" --path "./localizations"
asc localizations upload --version "VERSION_ID" --path "./localizations" --dry-run
asc localizations upload --version "VERSION_ID" --path "./localizations"
```

对于 app-info 本地化：

```bash
asc apps info list --app "APP_ID" --output table
asc localizations list --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --output table
asc localizations download --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations" --dry-run
asc localizations upload --app "APP_ID" --type app-info --app-info "APP_INFO_ID" --path "./app-info-localizations"
```

## 遗留 fastlane 元数据

仅用于现有的 fastlane 格式树：

```bash
asc migrate export --app "APP_ID" --version-id "VERSION_ID" --output-dir "./fastlane"
asc migrate validate --fastlane-dir "./fastlane"
asc migrate import --app "APP_ID" --version-id "VERSION_ID" --fastlane-dir "./fastlane" --dry-run
asc migrate import --app "APP_ID" --version-id "VERSION_ID" --fastlane-dir "./fastlane" --confirm
```

Deliverfile 的 `metadata_path` 和 `screenshots_path` 值优先级更高，相对于 Deliverfile 解析。使用 `--fastlane-dir "./fastlane"` 时，使用 `metadata_path "./metadata"` 而不是 `"./fastlane/metadata"`；后者解析为 `./fastlane/fastlane/metadata`。修复 Deliverfile 中的陈旧值，或删除它们以使用标准的 `metadata/` 和 `screenshots/` 目录。

所选 Fastlane 目录外的路径除非操作员显式使用 `--allow-external-metadata` 或 `--allow-external-screenshots` 信任，否则会失败。对于不信任的导入，请关闭这些标志。

检查验证正文以及进程退出：`asc migrate validate` 可能返回 `valid: false` 和非零 `errorCount` 但退出码为 0。确认导入可能打印 `status: "partial"` 并显示已完成阶段和失败详情，但退出码非零，因此非空标准输出不代表成功。

## 字符限制

| 字段 | 限制 |
|-------|-------|
| 名称 | 30 |
| 副标题 | 30 |
| 关键字 | 100 个逗号分隔的字符 |
| 描述 | 4000 |
| 新功能 | 4000 |
| 推广文本 | 170 |

## 代理行为

- 除非用户需要 `.strings` 或 fastlane 元数据，否则从 `asc metadata pull` 开始。
- 在远程写入前始终运行 `asc metadata validate`。
- 当命令支持时，使用 `--dry-run` 预览远程更改。
- 当用户需要 durable review artifact 之后再 apply 时，使用 `asc metadata plan` 加 `approve`/`status`。
- 对于快速编辑，始终传递 `--version-id` 或 `--version` 加 `--platform`；不要依赖模糊的最新版本行为。
- 将 app-info 字段和版本字段分开。
- 使用 `--output table` 进行人工验证，使用 JSON 进行自动化。
