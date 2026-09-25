# asc 截图流程 (xcodebuild -> AXe -> frame -> asc)

用于 agent 驱动的截图工作流，其中应用通过 Xcode CLI 工具构建和启动，UI 通过 AXe 驱动，截图通过 `asc` 上传。

## 当前范围
- 当前实现：构建/运行、AXe 计划捕获、帧合成和上传。
- 设备发现通过 `asc screenshots list-frame-devices` 内置。
- 本地截图自动化命令在 asc cli 中为实验性。
- 帧合成固定在 Koubou `0.18.1` 以确保输出确定性。
- 反馈/问题：https://github.com/rorkai/App-Store-Connect-CLI/issues/new/choose

## 默认设置
- 设置文件：`.asc/shots.settings.json`
- 捕获计划：`.asc/screenshots.json`
- 原始截图目录：`./screenshots/raw`
- 帧合成截图目录：`./screenshots/framed`
- 默认帧设备：`iphone-air`

## 1) 首先创建设置 JSON

创建或更新 `.asc/shots.settings.json`：

```json
{
  "version": 1,
  "app": {
    "bundle_id": "com.example.app",
    "project": "MyApp.xcodeproj",
    "scheme": "MyApp",
    "simulator_udid": "booted"
  },
  "paths": {
    "plan": ".asc/screenshots.json",
    "raw_dir": "./screenshots/raw",
    "framed_dir": "./screenshots/framed"
  },
  "pipeline": {
    "frame_enabled": true,
    "upload_enabled": false
  },
  "upload": {
    "version_localization_id": "",
    "device_type": "IPHONE_65",
    "source_dir": "./screenshots/framed"
  }
}
```

如果你有意跳过帧合成，设置：
- `"frame_enabled": false`
- `"upload.source_dir": "./screenshots/raw"`

## 2) 在模拟器上构建和运行应用

使用 Xcode CLI 进行构建/安装/启动：

```bash
xcrun simctl boot "$UDID" || true

xcodebuild \
  -project "MyApp.xcodeproj" \
  -scheme "MyApp" \
  -configuration Debug \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath ".build/DerivedData" \
  build

xcrun simctl install "$UDID" ".build/DerivedData/Build/Products/Debug-iphonesimulator/MyApp.app"
xcrun simctl launch "$UDID" "com.example.app"
```

如果应用包路径与默认位置不同，使用 `xcodebuild -showBuildSettings`。

## 3) 使用 AXe (或 `asc screenshots run`) 捕获截图

优先使用计划驱动的捕获：

```bash
asc screenshots run --plan ".asc/screenshots.json" --udid "$UDID" --output json
```

计划编写期间有用的 AXe 基本操作：

```bash
axe describe-ui --udid "$UDID"
axe tap --id "search_field" --udid "$UDID"
axe type "wwdc" --udid "$UDID"
axe screenshot --output "./screenshots/raw/home.png" --udid "$UDID"
```

`.asc/screenshots.json` 的最小示例：

```json
{
  "version": 1,
  "app": {
    "bundle_id": "com.example.app",
    "udid": "booted",
    "output_dir": "./screenshots/raw"
  },
  "steps": [
    { "action": "launch" },
    { "action": "wait", "duration_ms": 800 },
    { "action": "screenshot", "name": "home" }
  ]
}
```

## 4) 使用 `asc screenshots frame` 帧合成截图

asc CLI 将帧合成固定在 Koubou `0.18.1`。
在运行帧合成步骤前安装和验证：

```bash
pip install koubou==0.18.1
kou --version  # 预期 0.18.1
# 如果 Koubou 报告缺少设备帧，使用网络访问运行一次：
kou setup-frames
```

首先列出支持的帧设备值：

```bash
asc screenshots list-frame-devices --output json
```

帧合成为一个截图（默认为 `iphone-air`）：

```bash
asc screenshots frame \
  --input "./screenshots/raw/home.png" \
  --output-dir "./screenshots/framed" \
  --device "iphone-air" \
  --output json
```

支持的 `--device` 值：
- `iphone-air` (默认)
- `iphone-17-pro`
- `iphone-17-pro-max`
- `iphone-16e`
- `iphone-17`
- `mac`

## 5) 使用 asc 上传截图

生成并审查上传前的工作成果：

```bash
asc screenshots review-generate --framed-dir "./screenshots/framed" --output-dir "./screenshots/review"
asc screenshots review-open --output-dir "./screenshots/review"
asc screenshots review-approve --all-ready --output-dir "./screenshots/review"
```

对于已审查的多语言集，优先使用计划/应用流程，以便在上传前包含现有的远程截图计数：

```bash
asc screenshots plan --app "APP_ID" --version "1.2.3" --review-output-dir "./screenshots/review" --output json
asc screenshots apply --app "APP_ID" --version "1.2.3" --review-output-dir "./screenshots/review" --confirm --output json
```

从配置的源目录上传（帧合成启用时默认为 `./screenshots/framed`）：

```bash
asc screenshots upload \
  --version-localization "LOC_ID" \
  --path "./screenshots/framed" \
  --device-type "IPHONE_65" \
  --output json
```

需要时列出或验证：

```bash
asc screenshots sizes --output table
asc screenshots list --version-localization "LOC_ID" --output table
```

## Agent 行为
- 始终使用 `--help` 确认确切标志后再运行命令。
- 使用 `asc screenshots --help` 重新检查命令路径，因为截图命令正在快速演进。
- 保持输出确定性：机器步骤默认使用 JSON。
- 优先使用 `asc screenshots list-frame-devices --output json` 选择帧设备前。
- 确保截图文件存在后再上传。
- 使用显式长标志 (`--app`, `--output`, `--version-localization` 等)。
- 将截图本地自动化视为实验性，并在用户界面交接笔记中说明。
- 使用 `asc screenshots plan` / `asc screenshots apply` 处理已审查批次，当需要在现有远程截图上添加限制时。
- 如果帧合成因版本错误失败，重新安装固定的 Koubou：`pip install koubou==0.18.1`。
- 如果帧合成因缺少设备帧失败，使用网络访问运行一次 `kou setup-frames`。

## 6) 多语言捕获（可选）

不要使用 `xcrun simctl launch ... -e AppleLanguages` 进行本地化。
`-e` 是环境变量模式，无法可靠切换应用语言。

对于此流程，使用每个 UDID 的模拟器范围语言默认值。这适用于
`asc screenshots capture`，它会内部重新启动应用。

```bash
# 将每个语言映射到专用的模拟器 UDID。
# (使用 `xcrun simctl create` 一次性创建这些模拟器。)
declare -A LOCALE_UDID=(
  ["en-US"]="UDID_EN_US"
  ["de-DE"]="UDID_DE_DE"
  ["fr-FR"]="UDID_FR_FR"
  ["ja-JP"]="UDID_JA_JP"
)

set_simulator_locale() {
  local UDID="$1"
  local LOCALE="$2"            # 例如 de-DE
  local LANG="${LOCALE%%-*}"   # de
  local APPLE_LOCALE="${LOCALE/-/_}" # de_DE

  xcrun simctl boot "$UDID" || true
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLanguages -array "$LANG"
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLocale -string "$APPLE_LOCALE"
}

for LOCALE in "${!LOCALE_UDID[@]}"; do
  UDID="${LOCALE_UDID[$LOCALE]}"
  echo "在 $UDID 上捕获 $LOCALE..."
  set_simulator_locale "$UDID" "$LOCALE"

  xcrun simctl terminate "$UDID" "com.example.app" || true
  asc screenshots capture \
    --bundle-id "com.example.app" \
    --name "home" \
    --udid "$UDID" \
    --output-dir "./screenshots/raw/$LOCALE" \
    --output json
done
```

如果手动启动（在 `asc screenshots capture` 外），使用应用启动参数：

```bash
xcrun simctl launch "$UDID" "com.example.app" -AppleLanguages "(de)" -AppleLocale "de_DE"
```

## 7) 并行执行以提高速度

每个模拟器 UDID 运行一个语言：

```bash
#!/bin/bash
# parallel-capture.sh

declare -A LOCALE_UDID=(
  ["en-US"]="UDID_EN_US"
  ["de-DE"]="UDID_DE_DE"
  ["fr-FR"]="UDID_FR_FR"
  ["ja-JP"]="UDID_JA_JP"
)

capture_locale() {
  local LOCALE="$1"
  local UDID="$2"
  local LANG="${LOCALE%%-*}"
  local APPLE_LOCALE="${LOCALE/-/_}"

  echo "开始 $LOCALE 在 $UDID"
  xcrun simctl boot "$UDID" || true
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLanguages -array "$LANG"
  xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLocale -string "$APPLE_LOCALE"
  xcrun simctl terminate "$UDID" "com.example.app" || true

  asc screenshots capture \
    --bundle-id "com.example.app" \
    --name "home" \
    --udid "$UDID" \
    --output-dir "./screenshots/raw/$LOCALE" \
    --output json

  echo "完成 $LOCALE"
}

for LOCALE in "${!LOCALE_UDID[@]}"; do
  capture_locale "$LOCALE" "${LOCALE_UDID[$LOCALE]}" &
done

wait
echo "所有捕获完成。现在帧合成..."
```

或使用 `xargs` 与 `locale:udid` 对：

```bash
printf "%s\n" \
  "en-US:UDID_EN_US" \
  "de-DE:UDID_DE_DE" \
  "fr-FR:UDID_FR_FR" \
  "ja-JP:UDID_JA_JP" | xargs -P 4 -I {} bash -c '
    PAIR="{}"
    LOCALE="${PAIR%%:*}"
    UDID="${PAIR##*:}"
    LANG="${LOCALE%%-*}"
    APPLE_LOCALE="${LOCALE/-/_}"
    xcrun simctl boot "$UDID" || true
    xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLanguages -array "$LANG"
    xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLocale -string "$APPLE_LOCALE"
    xcrun simctl terminate "$UDID" "com.example.app" || true
    asc screenshots capture --bundle-id "com.example.app" --name "home" --udid "$UDID" --output-dir "./screenshots/raw/$LOCALE" --output json
  '
```

## 8) 全部多语言流程示例

```bash
#!/bin/bash
# full-pipeline-multi-locale.sh

declare -A LOCALE_UDID=(
  ["en-US"]="UDID_EN_US"
  ["de-DE"]="UDID_DE_DE"
  ["fr-FR"]="UDID_FR_FR"
  ["es-ES"]="UDID_ES_ES"
  ["ja-JP"]="UDID_JA_JP"
)

DEVICE="iphone-air"
RAW_DIR="./screenshots/raw"
FRAMED_DIR="./screenshots/framed"

# 第 1 步：并行捕获，每个模拟器使用语言默认值
for LOCALE in "${!LOCALE_UDID[@]}"; do
  (
    UDID="${LOCALE_UDID[$LOCALE]}"
    LANG="${LOCALE%%-*}"
    APPLE_LOCALE="${LOCALE/-/_}"

    xcrun simctl boot "$UDID" || true
    xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLanguages -array "$LANG"
    xcrun simctl spawn "$UDID" defaults write NSGlobalDomain AppleLocale -string "$APPLE_LOCALE"
    xcrun simctl terminate "$UDID" "com.example.app" || true

    asc screenshots capture \
      --bundle-id "com.example.app" \
      --name "home" \
      --udid "$UDID" \
      --output-dir "$RAW_DIR/$LOCALE" \
      --output json
    echo "捕获 $LOCALE"
  ) &
done
wait

# 第 2 步：并行帧合成
for LOCALE in "${!LOCALE_UDID[@]}"; do
  (
    asc screenshots frame \
      --input "$RAW_DIR/$LOCALE/home.png" \
      --output-dir "$FRAMED_DIR/$LOCALE" \
      --device "$DEVICE" \
      --output json
    echo "帧合成 $LOCALE"
  ) &
done
wait

# 第 3 步：生成审查（单次运行，聚合所有语言）
asc screenshots review-generate \
  --framed-dir "$FRAMED_DIR" \
  --output-dir "./screenshots/review"

# 第 4 步：上传（如果需要，按语言运行）
for LOCALE in "${!LOCALE_UDID[@]}"; do
  asc screenshots upload \
    --version-localization "LOC_ID_FOR_$LOCALE" \
    --path "$FRAMED_DIR/$LOCALE" \
    --device-type "IPHONE_65" \
    --output json
done
```
