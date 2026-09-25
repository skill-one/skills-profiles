# asc崩溃分析

使用此功能获取、分析和总结TestFlight崩溃报告、测试版反馈和性能诊断信息。

## 工作流程

1. 如果未提供应用ID，请解析应用ID（使用`asc apps list`）。
2. 使用适当的命令获取数据。
3. 解析JSON输出并呈现人类可读的摘要。

## TestFlight崩溃报告

列出最近的崩溃（最新优先）：

- `asc testflight crashes list --app "APP_ID" --sort -createdDate --limit 10`
- 按构建过滤：`asc testflight crashes list --app "APP_ID" --build-id "BUILD_ID" --sort -createdDate --limit 10`
- 按设备/操作系统过滤：`asc testflight crashes list --app "APP_ID" --device-model "iPhone16,2" --os-version "18.0"`
- 所有崩溃：`asc testflight crashes list --app "APP_ID" --paginate`
- 表格视图：`asc testflight crashes list --app "APP_ID" --sort -createdDate --limit 10 --output table`

## TestFlight测试版反馈

列出最近的反馈（最新优先）：

- `asc testflight feedback list --app "APP_ID" --sort -createdDate --limit 10`
- 带截图：`asc testflight feedback list --app "APP_ID" --sort -createdDate --limit 10 --include-screenshots`
- 按构建过滤：`asc testflight feedback list --app "APP_ID" --build-id "BUILD_ID" --sort -createdDate`
- 所有反馈：`asc testflight feedback list --app "APP_ID" --paginate`

## 性能诊断（卡顿、磁盘写入、启动）

需要构建ID。通过`asc builds info --app "APP_ID" --latest --platform IOS`或`asc builds list --app "APP_ID" --sort -uploadedDate --limit 5`解析。

- 列出诊断签名：`asc performance diagnostics list --build-id "BUILD_ID"`
- 按类型过滤：`asc performance diagnostics list --build-id "BUILD_ID" --diagnostic-type "HANGS"`
  - 类型：`HANGS`, `DISK_WRITES`, `LAUNCHES`
- 查看签名的日志：`asc performance diagnostics view --id "SIGNATURE_ID"`
- 下载所有指标：`asc performance download --build-id "BUILD_ID" --output ./metrics.json`

## 解析ID

- 从名称获取应用ID：`asc apps list --name "AppName"`或`asc apps list --bundle-id "com.example.app"`
- 最新构建ID：`asc builds info --app "APP_ID" --latest --platform IOS`
- 最近构建：`asc builds list --app "APP_ID" --sort -uploadedDate --limit 5`
- 设置默认值：`export ASC_APP_ID="APP_ID"`

## 摘要格式

呈现结果时，按严重程度和频率组织：

1. **总数** — 结果集中崩溃/反馈的数量。
2. **主要崩溃签名** — 按异常类型或崩溃原因分组，按数量排序。
3. **受影响的构建** — 哪些构建版本受影响。
4. **设备和操作系统分析** — 最受影响的设备型号和操作系统版本。
5. **时间线** — 崩溃何时开始或激增。

对于性能诊断，首先突出显示权重最高的签名。

## 注意事项

- 默认输出为JSON；使用`--output table`或`--output markdown`进行快速人类审查。
- 使用`--paginate`进行完整分析时获取所有页面。
- 使用`--pretty`与JSON进行调试命令输出。
- App Store Connect的崩溃数据可能有24-48小时的延迟。
