# App Store发布编排

使用此技能将一个经过批准的计划从版本带到App Store审核。在此处保留Game Center项目准备；将其他阻塞诊断和审核恢复保留在`asc-submission-health`中。

## 责任边界

此技能拥有：

- 部署元数据和附加构建；
- 发布IPA或本地构建；
- 提交准备好的版本；
- 组装多项目审核提交。

使用[准备部分](references/multi-item-submissions.md#prepare-every-item)进行Game Center项目准备或附加阻塞器。在App版本已部署并选择多项目通道后，才使用该参考的组装和提交部分。对于其他验证阻塞器、卡住的提交、取消或重试决策，切换到`asc-submission-health`。

在当前任务内切换技能，同时保留解析的目标、授权和验证进度。失败的关卡会阻塞依赖的变更，而不是诊断或独立授权的工作。继续授权的修复并恢复此流程；仅在修复超出约定范围时请求新的授权。

## 前置条件

- 解析`APP_ID`、版本字符串、当需要时`VERSION_ID`和当构建已存在时`BUILD_ID`。
- 使用`asc auth login`或`ASC_*`环境变量配置授权。
- 确认预期平台。除非应用针对其他平台，否则使用`IOS`。
- 当工作流应用元数据时，将规范元数据保留在`./metadata`中。
- 在执行高级别变更命令之前需要干运行，然后提交时需要`--confirm`。

## 选择发布通道

| 意图 | 命令 |
| --- | --- |
| 准备元数据和附加现有构建但不提交 | `asc release stage` |
| 提交已准备好的版本 | `asc review submit` |
| 上传IPA或本地构建，然后可选提交 | `asc publish appstore` |
| 提交包含IAP、订阅或Game Center版本项目的应用版本 | lower-level `asc review` 提交命令 |

在创建审核提交后，不要混合通道。首先检查现有提交，然后通过匹配的低级别命令继续。

## 运行就绪关卡

将此关卡应用于已附加预期构建的版本。对于部署通道，首先完成[部署现有构建](#stage-an-existing-build)；`asc release stage`附加构建并运行验证，之后可以评估此关卡。不要将预期的预部署"构建未附加"结果路由到`asc-submission-health`。

在提交之前进行验证：

```bash
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --output table
```

当警告必须停止自动化时使用严格模式：

```bash
asc validate --app "APP_ID" --version "1.2.3" --platform IOS --strict --output table
```

数字商品是一个硬关卡。如果发布包含IAP或订阅，请停止并在`asc-submission-health`中运行相关产品检查。只有在这些检查没有阻塞问题并且预期产品版本已准备好后，才恢复此流程。

对于Game Center项目，仅完成[准备每个项目](references/multi-item-submissions.md#prepare-every-item)，然后返回到此流程。在就绪阶段期间不要组装或提交多项目审核提交。

如果应用验证报告Game Center项目阻塞器，请停止并使用该准备部分。如果唯一阻塞器是部署通道中的未附加构建，请继续到部署部分。对于其他阻塞器，暂停依赖的发布操作并使用`asc-submission-health`；在授权修复通过验证后恢复。

## 部署现有构建

使用`asc release stage`在更改版本、应用或复制元数据、附加构建并运行验证而不创建审核提交之前，验证所选构建属于应用。

预览元数据驱动的部署：

```bash
asc release stage \
  --app "APP_ID" \
  --version "1.2.3" \
  --build-id "BUILD_ID" \
  --metadata-dir "./metadata/version/1.2.3" \
  --dry-run \
  --output table
```

应用已审查的计划：

```bash
asc release stage \
  --app "APP_ID" \
  --version "1.2.3" \
  --build-id "BUILD_ID" \
  --metadata-dir "./metadata/version/1.2.3" \
  --confirm
```

当携带本地化元数据时，使用`--copy-metadata-from "1.2.2"`而不是`--metadata-dir`。当警告应导致阶段失败时，添加`--strict-validate`。

如果元数据计划包含删除，干运行和确认运行都需要`--allow-deletes`。首先审查这些删除；该标志还禁用当本地不存在时回退到现有区域。

当发布包含路由应用覆盖范围时，使用`--routing-coverage-file "./coverage.geojson"`。此实验步骤在变更之前验证GeoJSON，并在就绪检查之前部署它。

结构化输出在`steps[]`的开头包含一个`validate_build`步骤。按名称匹配步骤，而不是数组位置。

## 提交已准备好的版本

在元数据、审核详情、可用性、构建处理和产品就绪已解决后，使用`asc review submit`。

```bash
asc review submit --app "APP_ID" --version "1.2.3" --build-id "BUILD_ID" --dry-run --output table
asc review submit --app "APP_ID" --version "1.2.3" --build-id "BUILD_ID" --confirm
```

当已知确切版本ID时，使用`--version-id "VERSION_ID"`而不是`--version`。`--build-id`始终是必需的，并且必须标识预期构建。

## 上传或构建，然后发布

当发布从IPA或本地Xcode项目/workspace开始时，使用`asc publish appstore`。

预览IPA上传和提交：

```bash
asc publish appstore \
  --app "APP_ID" \
  --ipa "./App.ipa" \
  --version "1.2.3" \
  --submit \
  --dry-run \
  --output table
```

在审查计划后运行它：

```bash
asc publish appstore \
  --app "APP_ID" \
  --ipa "./App.ipa" \
  --version "1.2.3" \
  --submit \
  --wait \
  --confirm
```

对于本地构建模式，使用`--workspace`或`--project`与`--scheme`而不是`--ipa`。当发布命令应在确保版本后应用规范版本元数据时，使用`--metadata-dir`。当用户只想上传和附加时，省略`--submit`。

## 提交多个审核项目

当应用版本必须与版本化的IAP、订阅、订阅组或Game Center项目一起发布时，请阅读[references/multi-item-submissions.md](references/multi-item-submissions.md)。仅添加用户已解析和检查的项目。

## 提交后交接

报告：

- 应用、版本、平台、构建和提交ID；
- 运行的通道及其是否完成；
- 用户授权下执行的变更；
- 监控结果提交的确切命令。

使用`asc-submission-health`进行监控、取消、拒绝诊断或重试决策。

## 安全限制

- 不要使用已移除的`submit-preflight`、`submit-create`或`release-run`快捷方式。
- 直至干运行计划与请求的发布匹配之前，不要添加`--confirm`。
- 当版本已存在审核提交时，不要创建第二个审核提交。
- 不要将验证失败转换为部分发布；在失败关卡处停止。
- 在自动化中包装命令时，将数据保留在stdout，将诊断保留在stderr。
