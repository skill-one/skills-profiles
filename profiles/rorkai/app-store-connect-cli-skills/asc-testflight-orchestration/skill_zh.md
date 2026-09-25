# asc TestFlight 协调

在管理 TestFlight 测试者、分组和构建分发时使用此技能。

## 导出当前配置
- `asc testflight config export --app "APP_ID" --output "./testflight.yaml"`
- 包含构建/测试者：
  - `asc testflight config export --app "APP_ID" --output "./testflight.yaml" --include-builds --include-testers`

## 管理分组和测试者
- 分组：
  - `asc testflight groups list --app "APP_ID" --paginate`
  - `asc testflight groups create --app "APP_ID" --name "Beta Testers"`
- 测试者：
  - `asc testflight testers list --app "APP_ID" --paginate`
  - `asc testflight testers add --app "APP_ID" --email "tester@example.com" --group "Beta Testers"`
  - `asc testflight testers invite --app "APP_ID" --email "tester@example.com"`

## 分发构建
- `asc builds add-groups --build-id "BUILD_ID" --group "GROUP_ID"`
- 从分组中移除：
  - `asc builds remove-groups --build-id "BUILD_ID" --group "GROUP_ID" --confirm`

## 检查构建的分组
- `asc testflight groups list --build-id "BUILD_ID" --output table`
- 构建查找是实验性的。它会解析应用、分页应用的所有分组，并包含具有所有构建访问权限的分组。

## 无分发上传
- `asc publish testflight --app "APP_ID" --ipa "./app.ipa" --upload-only --output json`
- 当下一步需要处理后的构建时，添加 `--wait`。
- 仅上传需要新的 IPA 或本地 Xcode 构建。不要将其与现有的 `--build-id`、分组、测试者通知、测试笔记或 Beta Review 提交结合使用。`--build-number` 作为上传元数据是允许的，但它不能是唯一的构建输入。

## 要测试的笔记
- `asc builds test-notes create --build-id "BUILD_ID" --locale "en-US" --whats-new "测试说明"`
- `asc builds test-notes update --localization-id "LOCALIZATION_ID" --whats-new "更新笔记"`

## 注意事项
- 在大型分组/测试者列表上使用 `--paginate`。
- 优先使用 ID 进行确定性操作；在需要时使用 ID 解析技能。
