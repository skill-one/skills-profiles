# asc 构建生命周期

使用此技能来管理构建状态、处理过程和保留。

## 找到正确的构建
- 最新构建：
  - `asc builds info --app "APP_ID" --latest --version "1.2.3" --platform IOS`
- 下一安全构建编号：
  - `asc builds next-build-number --app "APP_ID" --version "1.2.3" --platform IOS`
  - 该命令扫描完整的已处理构建历史和正在上传的文件，然后返回比最高正数构建编号大1的编号。空白或非数字的已处理构建编号会带警告被跳过；如果没有可用的编号，它会回退到 `--initial-build-number`。
- 近期构建：
  - `asc builds list --app "APP_ID" --sort -uploadedDate --limit 10`

## 检查处理状态
- `asc builds info --build-id "BUILD_ID"`

## 发布流程
- 优先端到端：
  - `asc publish testflight --app "APP_ID" --ipa "./app.ipa" --group "GROUP_ID" --wait`
  - `asc publish appstore --app "APP_ID" --ipa "./app.ipa" --version "1.2.3" --wait --submit --confirm`

## 清理
- 预览过期：
  - `asc builds expire-all --app "APP_ID" --older-than 90d --dry-run`
- 应用过期：
  - `asc builds expire-all --app "APP_ID" --older-than 90d --confirm`
- 单个构建：
  - `asc builds expire --build-id "BUILD_ID" --confirm`

## 注意事项
- `asc builds upload` 上传并提交 IPA 或 PKG。当工作流必须同时发布到 TestFlight 或准备 App Store 发布时，请使用 `asc publish`。
- 对于长时间处理时间，在支持的情况下使用 `--wait`、`--poll-interval` 和 `--timeout`。
