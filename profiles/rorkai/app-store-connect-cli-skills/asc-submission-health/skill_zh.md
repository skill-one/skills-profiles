# App Store 提交健康状态

使用此技能解释为什么发布无法进行，并管理现有的审核提交。将健康的发布执行交还给 `asc-release-flow`。

## 责任边界

此技能拥有：

- 准备状态验证和阻塞诊断；
- 公共 API、网络会话和手动修复路由；
- 审核状态和历史记录；
- 取消和重试决策。

使用 `asc-release-flow` 进行预发布、上传、发布和提交。切换技能会继续当前任务及其已解决的靶标、授权和验证进度；它不需要用户重新启动工作流。继续授权的修复，并在健康时返回发布执行。仅在修复超出范围时才请求新的授权。

## 回答顺序

1. 说明版本是否已准备好、被阻塞或已在审核中。
2. 列出每个阻塞项及其证明证据。
3. 将公共 API 修复与网络会话和手动工作分开。
4. 运行所需的只读检查以建立诊断。对于仅诊断请求，报告证据和一个建议的修复命令，但不执行该修复。对于授权执行，继续修复队列并报告已完成的工作和剩余的阻塞项。

## 确定目标

- 解析 `APP_ID`、版本字符串或 `VERSION_ID`、`BUILD_ID`、平台和任何已知的 `SUBMISSION_ID`。
- 使用 `asc auth login` 或 `ASC_*` 环境变量配置授权。
- 仅用于仓库测试和隔离验证，不要用于正常用户会话，使用 `ASC_BYPASS_KEYCHAIN=1`。
- 一旦目标解析，优先使用 ID；当应用、版本或产品解析不明确时停止。

## 诊断准备状态

首先运行标准的准备状态报告：

```bash
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --output table
```

当知道时，使用 `--version-id "VERSION_ID"`。当警告必须导致自动化失败时，添加 `--strict`。

向审核特定的医生请求有序解释：

```bash
asc review doctor --app "APP_ID" --version "1.2.3" --platform IOS --output table
```

当报告指向构建或版本时，收集直接证据：

```bash
asc builds info --build-id "BUILD_ID" --output table
asc versions view --version-id "VERSION_ID" --include-build --include-submission --output table
```

对于数字商品，仅运行相关的产品验证器：

```bash
asc validate iap --app "APP_ID" --output table
asc validate subscriptions --app "APP_ID" --output table
```

将 `asc validate` 的有序修复计划视为修复队列。在移动到下一个之前，修复和验证一类阻塞项。

## 路由修复

当阻塞项是构建处理、元数据、截图、审核详情、加密、内容权利、年龄评级、可用性或版本范围的产品元数据时，使用公共 API 命令。

当诊断识别出那些常见阻塞项或首次发布可用性差距时，阅读 [references/readiness-repairs.md](references/readiness-repairs.md)。

仅当 IAP 或订阅验证失败、Apple 要求首次审核附件或版本化产品必须加入现有的审核提交时，才阅读 [references/digital-goods.md](references/digital-goods.md)。

仅当验证报告 App 隐私建议或发布状态无法通过公共 API 确认时，才阅读 [references/app-privacy.md](references/app-privacy.md)。

当验证报告 Game Center 组件或版本阻塞项时，将其交给 `asc-release-flow` 并请求多项目引用的 **准备每个项目** 部分。不要将 Game Center 通过一般准备状态或数字商品修复路由。

仅当公共 API 无法覆盖的差距时，使用网络会话命令，并说明需要经过认证的 Apple 网络会话。当用户拒绝网络会话自动化时，保留手动 App Store Connect 备用方案。

## 判断版本是否健康

当版本准备好返回 `asc-release-flow` 时：

- `asc validate` 没有阻塞问题；
- 关联的构建是 `VALID`；
- 元数据、截图、应用信息、审核详情、内容权利、加密、年龄评级、定价和可用性已解决；
- 相关的 `asc validate iap` 和/或 `asc validate subscriptions` 检查没有阻塞问题，并且所需的数字商品版本已准备好；
- 任何 Game Center 版本项目已通过 `asc-release-flow` 的多项目提交引用检查；
- App 隐私已确认或发布。

不要仅仅因为一个验证器成功退出就认为版本准备好了。报告任何仍需要网络会话或手动检查的警告。

## 监控审核

当提交 ID 未知时，使用应用范围状态：

```bash
asc review status --app "APP_ID" --version "1.2.3" --platform IOS --output table
```

当可用时，使用确切的提交或版本 ID：

```bash
asc submit status --id "SUBMISSION_ID" --output table
asc submit status --version-id "VERSION_ID" --output table
```

使用发布仪表板查看周围的构建和审核信号：

```bash
asc status --app "APP_ID" --include builds,appstore,submission,review --output table
```

使用历史记录区分当前停滞与之前的拒绝或完成的提交：

```bash
asc review history --app "APP_ID" --version "1.2.3" --paginate --output table
```

## 取消不健康的提交

取消之前，先解析确切的活跃提交。首先预览状态，然后要求确认：

```bash
asc submit status --id "SUBMISSION_ID" --output table
asc submit cancel --id "SUBMISSION_ID" --confirm
```

当通过版本解析时，包括应用以进行现代审核提交查找：

```bash
asc submit status --version-id "VERSION_ID" --output table
asc submit cancel --version-id "VERSION_ID" --app "APP_ID" --confirm
```

当已知确切的审核提交时，可以使用较低级别的等效命令：

```bash
asc review submissions-cancel --id "SUBMISSION_ID" --confirm
```

不要因为审核比预期时间长就取消提交。首先确认状态和用户的意图。

## 决定何时重试

没有专门的重试命令。使用以下顺序：

1. 仅当活跃提交必须撤回时取消。
2. 修复已证明的阻塞项。
3. 重新运行 `asc validate` 和相关的产品验证器。
4. 确认没有活跃提交已拥有版本或审核项目。
5. 将健康的版本和任何保留的 `SUBMISSION_ID` 交给 `asc-release-flow` 进行提交执行。重用检查过的 `READY_FOR_REVIEW` 草稿；当没有匹配的草稿或活跃提交时才创建提交。

## 常见失败路由

| 症状 | 首次证据 | 修复路由 |
| --- | --- | --- |
| 版本不在有效状态 | `asc validate`，`asc review doctor` | 有序的准备状态修复 |
| 导出合规性必须批准 | 构建信息和加密声明 | 准备状态修复 |
| 发现多个应用信息 | `asc apps info list --app "APP_ID"` | 解析确切的 App-info ID |
| IAP 或订阅未准备好 | 产品验证器 | 数字商品参考 |
| Game Center 组件或版本未准备好 | `asc validate` 诊断 | `asc-release-flow` 多项目准备部分 |
| App 隐私发布状态不明确 | 验证建议 | App 隐私参考 |
| 审核似乎停滞 | 审核状态加历史记录 | 监控；仅在有证据和批准时取消 |

## 安全限制

- 不要使用已移除的 `submit-preflight` 或 `submit-create` 快捷方式。
- 不要从此技能提交；将健康的执行返回给 `asc-release-flow`。
- 不要将网络会话自动化视为公共 App Store Connect API 覆盖。
- 不要在验证了之前的提交状态和阻塞项修复之前重试。
- 使用 `--output table` 进行人类诊断，使用 JSON 进行自动化。
- 对于 macOS，使用 `--platform MAC_OS` 同时保持相同健康生命周期。
