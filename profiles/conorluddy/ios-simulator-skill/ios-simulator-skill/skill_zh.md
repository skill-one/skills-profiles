# iOS 模拟器技能

使用可访问性驱动的导航和结构化数据来构建、测试和自动化 iOS 应用程序，而不是使用像素坐标。

## 快速入门

```bash
# 1. 检查环境
bash scripts/sim_health_check.sh

# 2. 启动应用
python scripts/app_launcher.py --launch com.example.app

# 3. 映射屏幕以查看元素
python scripts/screen_mapper.py

# 4. 点击按钮
python scripts/navigator.py --find-text "登录" --tap

# 5. 输入文本
python scripts/navigator.py --find-type TextField --enter-text "user@example.com"
```

所有脚本都支持 `--help` 以获取详细选项和 `--json` 以获取机器可读输出。

## 导航策略

**始终优先使用可访问性树而不是截图进行导航。** 可访问性树为您提供元素类型、标签、框架和可点击目标——比图像分析更便宜、更可靠的结构化数据。

使用此优先级：
1. `screen_mapper.py` → 结构化元素列表（5-7 行，~10 个 token）
2. `navigator.py --find-text/--find-type/--find-id` → 语义交互
3. 截图 → 仅用于视觉验证、错误报告或视觉差异

截图的成本取决于大小，为 1,600–6,300 个 token。可访问性树在默认模式下成本为 10–50 个 token。

## 29 个生产脚本

### 构建与开发（2 个脚本）

1. **build_and_test.py** - 构建 Xcode 项目，运行测试，使用渐进式披露解析结果
   - 带实时结果流式传输构建
   - 从 xcresult 套件中解析错误和警告
   - 按需检索详细的构建日志
   - 选项：`--project`，`--scheme`，`--clean`，`--test`，`--verbose`，`--json`

2. **log_monitor.py** - 带智能过滤的实时日志监控
   - 流式传输日志或按持续时间捕获
   - 按严重性（错误/警告/信息/调试）过滤
   - 去重重复消息
   - 选项：`--app`，`--severity`，`--follow`，`--duration`，`--output`，`--json`

### 设备状态（2 个脚本）

3. **appearance.py** - 控制模拟器外观：深色模式、Dynamic Type 大小以及区域/地区
   - 通过 `xcrun simctl ui` 切换亮/暗主题
   - 使用友好的别名（XS 通过 AX5）设置 Dynamic Type 大小
   - 写入区域和地区默认值；可选通过 `--bundle-id` 重新启动应用
   - 对于 ar/he/fa/ur/yi 区域自动标记为 RTL
   - 选项：`--theme`，`--text-size`，`--locale`，`--region`，`--reset`，`--bundle-id`，`--udid`，`--json`，`--verbose`

4. **location.py** - 模拟 GPS 坐标、命名城市预设和 GPX 场景回放
   - 使用 `--lat`/`--lng` 固定坐标或使用 `--city` 选择城市
   - 通过 `--gpx <scenario>` 播放内置场景（City Run，Freeway Drive 等）
   - 通过 `--waypoints` 和 `--speed` 配置速度动画多路径
   - 使用 `--clear` 清除模拟位置；使用 `--list-scenarios` 列出可用场景
   - 选项：`--lat`，`--lng`，`--city`，`--gpx`，`--waypoints`，`--speed`，`--clear`，`--list-scenarios`，`--udid`，`--json`，`--verbose`

### 导航与交互（5 个脚本）

5. **screen_mapper.py** - 分析当前屏幕并列出交互元素
   - 元素类型分解
   - 交互按钮列表
   - 文本字段状态
   - 选项：`--verbose`，`--hints`，`--json`

6. **navigator.py** - 按语义查找并交互元素
   - 通过文本查找（模糊匹配）
   - 通过元素类型查找
   - 通过可访问性 ID 查找
   - 输入文本或点击元素
   - 选项：`--find-text`，`--find-type`，`--find-id`，`--tap`，`--enter-text`，`--json`

7. **gesture.py** - 执行滑动、滚动、捏合和复杂手势
   - 方向性滑动（上/下/左/右）
   - 多滑动滚动
   - 捏合缩放
   - 长按
   - 拉动刷新
   - 选项：`--swipe`，`--scroll`，`--pinch`，`--long-press`，`--refresh`，`--json`

8. **keyboard.py** - 文本输入和硬件按钮控制
   - 输入文本（快速或慢速）
   - 特殊键（返回、删除、制表符、空格、箭头）
   - 硬件按钮（主屏幕、锁定、音量、截图）
   - 键组合
   - 选项：`--type`，`--key`，`--button`，`--slow`，`--clear`，`--dismiss`，`--json`

9. **app_launcher.py** - 应用生命周期管理
   - 通过 bundle ID 启动应用
   - 终止应用
   - 从 .app 套件安装/卸载
   - 深链接导航
   - 列出已安装应用
   - 检查应用状态
   - 传递启动参数（`--args`）和环境变量（`--env KEY=VALUE`，作为 `SIMCTL_CHILD_*` 注入）到启动/重新启动的应用
   - 选项：`--launch`，`--terminate`，`--restart`，`--install`，`--uninstall`，`--open-url`，`--list`，`--state`，`--args`，`--env`，`--wait-for-debugger`

### 测试与分析（9 个脚本）

10. **accessibility_audit.py** - 检查当前屏幕的 WCAG 合规性
    - 严重问题（缺少标签、空按钮、无替代文本）
    - 警告（缺少提示、小触摸目标）
    - 信息（缺少 ID、深层嵌套）
    - 选项：`--verbose`，`--output`，`--json`

11. **visual_diff.py** - 比较两个截图以进行视觉变化比较
    - 像素级比较
    - 基于阈值的通过/失败
    - 生成差异图像
    - 选项：`--threshold`，`--output`，`--details`，`--json`

12. **test_recorder.py** - 自动记录测试执行
    - 每个步骤捕获截图和可访问性树
    - 生成带时间数据的 markdown 报告
    - 选项：`--test-name`，`--output`，`--verbose`，`--json`

13. **app_state_capture.py** - 创建全面的调试快照
    - 截图、UI 层级结构、应用日志、设备信息
    - 用于错误报告的 markdown 摘要
    - 选项：`--app-bundle-id`，`--output`，`--log-lines`，`--json`

14. **sim_health_check.sh** - 验证环境是否正确配置
    - 检查 macOS、Xcode、simctl、IDB、Python
    - 列出可用和已启动的模拟器
    - 验证 Python 包（Pillow）

15. **model_inspector.py** - 从项目文件中检查 Core Data 和 SwiftData 模型
    - 解析 .xcdatamodeld 包（实体、属性、关系）
    - 检测模型版本和当前活动版本
    - 尽力提取 SwiftData @Model 类
    - 按需为任何模型提供原始源转储（`--raw ModelName`）
    - 选项：`--project-path`，`--core-data-only`，`--swiftdata-only`，`--show-versions`，`--raw`，`--verbose`，`--json`

16. **container.py** - 检查应用沙盒：文件、UserDefaults 和 Core Data 存储路径
    - 通过 `--ls` 在可配置深度处列出数据容器文件
    - 通过 `--cat` 自动检测 plist 解码读取文件（大文件缓存）
    - 通过 `--userdefaults` 将 UserDefaults 转储为 key=value 或 JSON
    - 通过 `--core-data-path` 定位 `.sqlite` / `.sqlite-wal` / `.sqlite-shm` 存储位置
    - 通过 `--export` 导出完整容器快照
    - 选项：`--ls`，`--cat`，`--userdefaults`，`--core-data-path`，`--export`，`--udid`，`--json`，`--verbose`

17. **hang_watcher.py** (HangBuster) - 记录并总结 os_log 挂起事件，带渐进式披露
    - **会话模式（HangBuster，agent-native）：** 启动一个分离的记录器，与模拟器交互，停止以获取紧凑的摘要
      - `--start` → 返回会话 ID；分离的工作进程动态规范化 + 阈值事件
      - `--stop SESSION_ID` → 发出 ~80–120 个 token L1 摘要（标题 + 顶部 N 个集群 + 钻探提示）
      - `--get-details SESSION_ID [--cluster N | --raw]` → L2 全集群或 L3 每个事件详情
      - `--list-sessions` / `--clear-sessions [--older-than 24h]` / `--diff A B`（跨会话回归报告）
      - 过滤管道：解析 → 规范化 → 阈值 → 桶 → 集群 → 聚合 → 排序 → 格式（在 `common/hang_pipeline.py` 中）
      - `--budget-tokens N` 选择最密集的级别（L0/L1/L2）以适应；`--terse` 强制 L0
      - `--auto-sample` 在每个集群的第一个事件上捕获主线程堆栈（软依赖：`main_thread_sampler.py` #62；如果不存在则优雅地不操作）
    - **原始捕获模式（完整保真度，用于 `jq` 探索）：** 跳过集群管道，将每个匹配的日志行逐字复制到 `raw.ndjson`
      - `--start --raw-capture [--max-size-mb 10] [--no-gzip]` — 启动 `log stream --style ndjson`
      - 每个会话的大小限制（`--max-size-mb`，默认 10）— 工作进程在达到限制时干净地停止；`extras.truncated=true`
      - `--stop` 压缩 `raw.ndjson` → `raw.ndjson.gz` (~15–19× 压缩；`--no-gzip` 选项退出）
      - `--get-details SESSION_ID` 在原始会话上打印路径，并带有 `zcat | jq ...` 提示
    - **弹性（在流死亡时自动重新启动）：** EOF 或子进程死亡触发 `stream_died` 事件，然后有界重新启动，带 2 秒退避。在 `IOS_SIM_HANG_MAX_RESTARTS`（默认 3）之后，会话被标记为 `crashed`，永远不会处于陈旧的 `running` 状态。`--list-sessions` 显示 `capture=Xs` 和 `restarts=N`。
    - **清理是自动的：** TTL 修剪（`IOS_SIM_HANG_SESSION_TTL_HOURS`，默认 24h）+ 聚合限制（`IOS_SIM_HANG_TOTAL_CAP_MB`，默认 100 MB，最旧的优先驱逐）都在每次 `--start` 时运行。
    - **遗留模式（向后兼容性不变）：** `--watch [--duration N]`（实时流）和 `--since 5m`（历史）
    - 过滤器：`--bundle-id`（解析后——挂起捕获保持模拟器全局，因此 RunningBoard/SpringBoard 事件被保留），`--predicate`（也通过 `IOS_SIM_HANG_PREDICATE`）
    - 所有输出都支持 `--json`；会话存储在 `~/.ios-simulator-skill/sessions/<id>/{meta.json,events.jsonl,summary.json,raw.ndjson.gz}`

    **快速入门（总结模式）：**
    ```bash
    SID=$(python scripts/hang_watcher.py --start --min-hang-ms 200)
    # ... 与模拟器交互（打开表单、滚动、导航）...
    python scripts/hang_watcher.py --stop $SID                  # 紧凑的 L1 摘要
    python scripts/hang_watcher.py --get-details $SID --cluster 1  # 钻探集群 1
    python scripts/hang_watcher.py --diff $SID_BASELINE $SID    # 跨会话回归
    ```

    **快速入门（原始捕获 + `jq` 探索）：**
    ```bash
    SID=$(python scripts/hang_watcher.py --start --raw-capture --max-size-mb 5)
    # ... 与模拟器交互...
    python scripts/hang_watcher.py --stop $SID
    # → "Session ...: 原始模式，737 行，0.96 MB → 0.05 MB 压缩后的"

    # 事件计数最多的进程：
    zcat ~/.ios-simulator-skill/sessions/$SID/raw.ndjson.gz \
      | jq -s 'group_by(.processImagePath) | map({proc: (.[0].processImagePath | split("/") | last), n: length}) | sort_by(-.n) | .[:5]'

    # 所有 RunningBoard 断言无效化：
    zcat .../raw.ndjson.gz | jq -c 'select(.subsystem == "com.apple.runningboard" and (.eventMessage | startswith("Invalidating")))'

    # 每分钟挂起次数：
    zcat .../raw.ndjson.gz | jq -r '.timestamp[:16]' | sort | uniq -c
    ```

18. **localization_audit.py** - 检测字符串目录差距、缺失键和占位符不匹配
    - 按区域报告缺失的键和 `needs_review`/`new` 键在 `.xcstrings` 目录中
    - 通过 `--source` 将目录键与 Swift 源（`String(localized:)` / `NSLocalizedString`）进行交叉引用
    - 标记跨区域占位符计数不匹配（`%d`，`%@`，`%s`，`%lld`）
    - 通过 `plistlib` 支持 `.strings` 和 `.stringsdict` 遗留格式
    - CI 友好的 `--strict` 在任何发现时退出 2
    - 选项：`--catalog`，`--source`，`--locale`，`--strict`，`--json`，`--verbose`

### 高级测试与权限（4 个脚本）

19. **clipboard.py** - 管理 模拟器剪贴板以进行粘贴测试
    - 复制文本到剪贴板
    - 测试粘贴流程而无需手动输入
    - 选项：`--copy`，`--test-name`，`--expected`，`--json`

20. **status_bar.py** - 覆盖模拟器状态栏外观
    - 预设：干净（9:41，100% 电池），测试（11:11，50%），低电量（20%），飞机模式（离线）
    - 自定义时间、网络、电池、WiFi 设置
    - 选项：`--preset`，`--time`，`--data-network`，`--battery-level`，`--clear`，`--json`

21. **push_notification.py** - 发送模拟推送通知
    - 简单模式（标题 + 正文 + 徽章）
    - 自定义 JSON 负载
    - 测试通知处理和深链接
    - 选项：`--bundle-id`，`--title`，`--body`，`--badge`，`--payload`，`--json`

22. **privacy_manager.py** - 授予、撤销和重置应用权限
    - 支持 13 个服务（相机、麦克风、位置、联系人、照片、日历、健康等）
    - 批量操作（逗号分隔的服务）
    - 审计跟踪，带测试场景跟踪
    - 选项：`--bundle-id`，`--grant`，`--revoke`，`--reset`，`--list`，`--json`

### 模拟器发现（2 个脚本）

23. **sim_list.py** - 带渐进式披露列出模拟器
    - 默认情况下提供简洁摘要（总数 / 可用 / 已启动）
    - 通过缓存 ID 在需要时提供完整详细信息
    - 按设备类型过滤
    - 使用 `--suggest` 建议推荐的模拟器
    - 与原始 `simctl list` 相比，96% 的 token 减少（57k → 2k tokens）
    - 选项：`--get-details`，`--suggest`，`--device-type`，`--json`

24. **simulator_selector.py** - 建议最适合工作的模拟器
    - 按最近使用（从 `config.json`）、最新 iOS、常见测试模型和启动状态对候选者进行排名
    - 使用 `--list` 列出所有可用模拟器
    - 直接使用 `--boot` 启动选定的模拟器
    - JSON 输出用于程序使用
    - 选项：`--suggest`，`--list`，`--boot`，`--json`

### 设备生命周期管理（5 个脚本）

25. **simctl_boot.py** - 带可选就绪验证启动模拟器
    - 通过 UDID 或设备名称启动
    - 带超时等待设备就绪
    - 批量启动操作（--all, --type）
    - 性能计时
    - 选项：`--udid`，`--name`，`--wait-ready`，`--timeout`，`--all`，`--type`，`--json`

26. **simctl_shutdown.py** - 优雅地关闭模拟器
    - 通过 UDID 或设备名称关闭
    - 可选验证关闭完成
    - 批量关闭操作
    - 选项：`--udid`，`--name`，`--verify`，`--timeout`，`--all`，`--type`，`--json`

27. **simctl_create.py** - 动态创建模拟器
    - 通过设备类型和 iOS 版本创建
    - 列出可用设备类型和运行时
    - 自定义设备命名
    - 返回 UDID 以用于 CI/CD 集成
    - 选项：`--device`，`--runtime`，`--name`，`--list-devices`，`--list-runtimes`，`--json`

28. **simctl_delete.py** - 永久删除模拟器
    - 通过 UDID 或设备名称删除
    - 默认安全确认（使用 --yes 跳过）
    - 批量删除操作
    - 智能删除（--old N 保留每个设备类型 N 个）
    - 选项：`--udid`，`--name`，`--yes`，`--all`，`--type`，`--old`，`--json`

29. **simctl_erase.py** - 无需删除即可对模拟器进行工厂重置
    - 保留设备 UUID（比删除+创建更快）
    - 删除所有、按类型或已启动模拟器
    - 可选验证
    - 选项：`--udid`，`--name`，`--verify`，`--timeout`，`--all`，`--type`，`--booted`，`--json`

## 常见模式

**自动-UDID 检测**：如果未提供 `--udid`，大多数脚本会自动检测已启动的模拟器。

**设备名称解析**：使用设备名称（例如，"iPhone 16 Pro"）而不是 UDID - 脚本会自动解析。

**批量操作**：许多脚本支持 `--all` 以用于所有模拟器或 `--type iPhone` 以进行设备类型过滤。

**输出格式**：默认为简洁的人类可读输出。使用 `--json` 以在 CI/CD 中获取机器可读输出。

**帮助**：所有脚本都支持 `--help` 以获取详细选项和示例。

**截图大小**：截图会调整大小以节省 token。预设：`full`（3-4 块，~5K tokens），`half`（1 块，~1.6K tokens，默认），`quarter`（1 块，~800 tokens，细节较少）。使用 `quarter` 进行快速视觉检查，`half` 用于可读 UI，`full` 仅当像素级细节很重要时使用。捕获截图的脚本（`app_state_capture.py`，`test_recorder.py`）默认为 `half`。

## 典型工作流程

1. 验证环境：`bash scripts/sim_health_check.sh`
2. 启动应用：`python scripts/app_launcher.py --launch com.example.app`
3. 分析屏幕：`python scripts/screen_mapper.py`
4. 交互：`python scripts/navigator.py --find-text "按钮" --tap`
5. 验证：`python scripts/accessibility_audit.py`
6. 如有需要调试：`python scripts/app_state_capture.py --app-bundle-id com.example.app`

## 配置

大多数操作限制可以通过环境变量进行调节。默认值适用于典型的本地开发；为慢速 CI 运行器、大型单体库构建或复杂屏幕的可访问性审计提高它们。

| 变量 | 默认值 | 控制 |
|---|---|---|
| `IOS_SIM_A11Y_LABEL_MAX` | `80` | 可访问性审计输出中保留的 `AXLabel` 最大字符数 |
| `IOS_SIM_A11Y_TOP_ISSUES` | `10` | 每次审计显示的顶级可访问性问题 |
| `IOS_SIM_APPS_PREVIEW` | `30` | `app_launcher.py` 列出的应用条目在截断之前 |
| `IOS_SIM_BOOT_SUBPROCESS_TIMEOUT` | `60` | `simctl boot` 子进程本身的超时（秒） |
| `IOS_SIM_BOOT_TIMEOUT` | `300` | 启动后等待就绪超时（秒） |
| `IOS_SIM_BUILD_JSON_CAP` | `50` | JSON 输出中的最大构建错误/失败测试 |
| `IOS_SIM_BUILD_LOG_PREVIEW` | `4000` | 默认输出中的构建日志预览字符数 |
| `IOS_SIM_BUILD_TIMEOUT` | `1800` | 在杀死 `xcodebuild build` 调用之前最大秒数 |
| `IOS_SIM_INTROSPECT_TIMEOUT` | `60` | `xcodebuild -list` 和 `simctl list` 查找的超时（秒） |
| `IOS_SIM_TEST_TIMEOUT` | `2700` | 在杀死 `xcodebuild test` 调用之前最大秒数 |
| `IOS_SIM_BUILD_SUMMARY_CAP` | `15` | 默认构建摘要中的错误/失败 |
| `IOS_SIM_BUILD_VERBOSE_CAP` | `100` | 详细构建输出中的错误/警告 |
| `IOS_SIM_CACHE_MAX_ENTRIES` | `500` | 渐进式披露缓存中的最大条目数（LRU 驱逐） |
| `IOS_SIM_CACHE_TTL_HOURS` | `1` | 缓存条目过期时间 |
| `IOS_SIM_ERASE_TIMEOUT` | `90` | 等待擦除超时（秒） |
| `IOS_SIM_HANG_PREDICATE` | _(默认)_ | `hang_watcher.py` 使用的 `os_log` 预测（默认捕获 RunningBoard 杀死 + "Hang detected" + 主线程挂起）。挂起事件来自系统守护进程（RunningBoard, SpringBoard），因此预测保持模拟器全局——`--bundle-id` 在解析后应用，而不是与 AND 匹配。 |
| `IOS_SIM_HANG_MIN_MS` | `250` | HangBuster 阈值——持续时间低于此值的挂起事件永远不会达到磁盘（较小 = 更敏感，较大 = 摘要） |
| `IOS_SIM_HANG_SESSION_TTL_HOURS` | `24` | HangBuster 会话修剪年龄；修剪在每次 `--start` 时运行 |
| `IOS_SIM_HANG_DEFAULT_TOP_N` | `3` | `--stop` L1 输出中的默认顶部 N 集群 |
| `IOS_SIM_HANG_BUDGET_TOKENS` | _(未设置)_ | `--stop` 的默认 token 预算（选择 L0/L1/L2 以适应） |
| `IOS_SIM_HANG_MAX_RESTARTS` | `3` | HangBuster 工作进程：EOF/子进程死亡的最大 `log stream` 重生尝试次数，在会话被标记为 `crashed` 之前 |
| `IOS_SIM_HANG_TOTAL_CAP_MB` | `100` | HangBuster 聚合磁盘限制。当总会话状态超过此限制时，`--start` 会首先删除最旧的会话。设置为 `0` 以禁用。 |
| `IOS_SIM_LOG_JSON_CAP` | `100` | `log_monitor.py` JSON 输出中的最大错误/警告 |
| `IOS_SIM_LOG_LINE_MAX` | `300` | 日志摘要中的每行截断 |
| `IOS_SIM_LOG_TAIL` | `200` | 详细输出/样本输出中的日志尾行数 |
| `IOS_SIM_LOG_TEXT_SUMMARY` | `15` | 文本模式日志摘要中显示的错误/警告 |
| `IOS_SIM_MAX_ELEMENTS` | `25` | `navigator.py` 列出的可点击元素 |
| `IOS_SIM_POLL_INTERVAL` | `0.5` | 启动/擦除状态轮询间隔（秒） |
| `IOS_SIM_RELAUNCH_DELAY_MS` | `1000` | `app_launcher.py` 中终止和重新启动之间的延迟 |
| `IOS_SIM_SCREEN_BUTTONS_PREVIEW` | `15` | `screen_mapper.py` 列出的按钮名称 |
| `IOS_SIM_SCREEN_SECTION_ITEMS` | `10` | `screen_mapper.py` 显示的每个部分项目数 |
| `IOS_SIM_STATE_SUBPROCESS_TIMEOUT` | `15` | `app_state_capture.py` 中的子进程超时（秒） |
| `IOS_SIM_TAP_SETTLE_MS` | `500` | `navigator.py` 中的点击后稳定延迟 |

示例：

```bash
# 慢速 GitHub Actions 运行器：给启动 10 分钟
IOS_SIM_BOOT_TIMEOUT=600 python scripts/simctl_boot.py --wait-ready
```

## 要求

- macOS 15 (Sequoia)+
- Xcode 26+ 和 Command Line Tools
- Python 3.12+
- `idb` **1.5.1+** - 每个交互脚本（点击、滑动、输入）都需要：
  `brew tap facebook/fb && brew install facebook/fb/idb-companion facebook/fb/idb-cli`
- Pillow，仅用于视觉差异：`pip3 install pillow`

使用 `bash scripts/sim_health_check.sh` 验证（添加 `--json` 获取结构化输出）。

## 故障排除

**点击、滑动和输入没有任何反应，但读取工作正常。** `idb` 报告成功，屏幕
从未改变。在 Xcode 27 上这意味着 `idb-companion` 旧于 1.5.1：它查找 Xcode 26 使用的 `SimulatorKit.framework` 路径。升级：
`brew upgrade facebook/fb/idb-companion`.

**需要 HID 交互的 SimulatorKit 是必需的。** 相同原因，相同修复。

**来自每个 idb 调用的 `Connection refused` 或 `No such file`。** 一个死亡的伴侣仍然在
idb 的注册表 `/tmp/idb/state` 中，因此 idb 调用一个无人监听的套接字而不是启动一个新的伴侣。修复：`idb disconnect <udid>`.

**`open -a Simulator` 失败。** Xcode 27 没有 `Simulator.app`；它被替换为
`Xcode.app/Contents/Applications/` 中的 `DeviceHub.app`。以无头方式启动：
`xcrun simctl boot <udid>`。注意，退出 DeviceHub 会关闭它所托管模拟器。

**`idb: 命令未找到`。** 伴侣和 CLI 是分开的软件包；安装两者（见要求）。如果 `which -a idb` 显示多个，则 `PATH` 中的第一个获胜。
