# 物理iPhone设置

仅适用于物理iPhone。模拟器使用`argent-ios-simulator-setup`。

## 首次运行

1. 连接手机，解锁它，保持屏幕常亮，并开启开发者模式（设置 > 隐私与安全 > 开发者模式）。`list-devices`必须显示它`已连接`。
2. `launch-app`仅注册应用。第一个`describe`、手势或`screenshot`构建、签名并在设备上启动运行器：首次运行需要几分钟，从缓存或工具服务器重启后需要几十秒。构建限制15分钟，运行器准备120秒。
3. 首次安装时，手机会要求信任开发者（设置 > 通用 > VPN与设备管理），并且**ArgentRunner**应用会出现在主屏幕上。告诉用户这是一个用于argent自动化运行的应用，必须保持安装。

## 签名和失败

签名无需配置。工具服务器进程的第一个电话会附带一个注明所选团队和`ARGENT_IOS_TEAM_ID`覆盖（工具服务器环境；更改会强制冷重启）的说明。连接、锁定、信任、过期配置文件和缺失证书错误会指明其修复方法：应用修复方法，重试相同的电话。此外：`errSecInternalComponent`：运行`security set-key-partition-list -S apple-tool:,apple:,codesign: -s ~/Library/Keychains/login.keychain-db`（会要求用户的登录密码），重试。`team has no devices`：保持手机连接，重试。bundle id注册失败：免费团队应用id限制，等待几天或使用付费团队签名。任何其他xcodebuild失败会打印原始`error:`行：阅读`~/.argent/ios-device-runner/logs/runner-<udid8>.log`。`RUNNER_WEDGED`：对udid运行`stop-simulator-server`，重试。

然后阅读`argent-ios-device-interact`。
