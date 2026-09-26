# IMA SDK 基础知识

Google IMA SDK（互动媒体广告）允许您将流媒体视频和音频广告加载到网站、应用程序、电视和其他数字平台中。使用 IMA SDK 从任何符合 VAST 标准的广告服务器请求广告并管理广告播放。

## 前置条件

在集成 IMA SDK 之前，您**必须**阅读以下平台特定指南，以支持您的应用程序可以支持的所有平台：

*   **Web/HTML5/ReactJs/NodeJs/Angular：** 阅读所有这些指南
    [ima-sdk-web-guide.md](references/ima-sdk-web-guide.md),
    [ima-sdk-web-iframe-mode.md](references/ima-sdk-web-iframe-mode.md),
    [ima-sdk-web-mobile-safari.md](references/ima-sdk-web-mobile-safari.md)
*   **Android/AndroidTV/ReactNative：** 阅读 [ima-sdk-android-guide.md](references/ima-sdk-android-guide.md)
*   **iOS/tvOS/ReactNative：** 阅读所有这些指南
    [ima-sdk-ios-guide.md](references/ima-sdk-ios-guide.md),
    [ima-sdk-tvos-guide.md](references/ima-sdk-tvos-guide.md)

--------------------------------------------------------------------------------

## 快速入门（通用工作流程）

1.  导入 SDK：前置条件、依赖项。
2.  初始化：早期设置、预热、设置配置和广告 UI 设置。
3.  广告请求：创建和触发请求、用户手势合规性。
4.  广告加载成功/失败：处理加载事件以获取 AdsManager，或处理早期致命错误。
5.  广告播放事件：通过 AdsManager 监听播放事件以协调内容播放/暂停，并处理非致命 LOG 事件和致命主动播放错误。
6.  清理：正确销毁 AdsManager 以释放资源并防止内存泄漏。

有关详细的、平台特定的实现细节，请始终参考前置条件部分中的指南。
