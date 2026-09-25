# IMA DAI SDK

使用 IMA DAI SDK 将 HLS 或 DASH 流加载到应用中，用于：

*   **Google Ad Manager 中配置的直播事件**。
*   **Google Ad Manager 中摄入的视频点播 (VOD) 内容**。

## 前置条件

查阅针对目标平台的平台特定集成指南：

*   **Web/HTML5/ReactJs/NodeJs/Angular:** 阅读
    [StreamManager 指南](references/web-StreamManager-guide.md)，了解如何将 Google 全托管 DAI 的流 URL 加载到 `<video>` 元素中。

*   **ChromeCast:** 阅读
    [StreamManager 指南](references/cast-StreamManager-guide.md)，了解如何将 IMA DAI SDK 集成到 ChromeCast Web Receiver 中。

*   **Android:** 阅读
    [ImaServerSideAdInsertionMediaSource 指南](references/android-ImaServerSideAdInsertionMediaSource-guide.md)
    ，了解如何集成 Media3 Exoplayer IMA 扩展。

*   **iOS/tvOS:** 阅读
    [IMAStreamRequest 指南](references/ios-IMAStreamRequest-guide.md)
    ，了解如何使用 `AVPlayer` 播放流。

*   **Roku:** 阅读 [StreamManager 指南](references/roku-StreamManager-guide.md)
    ，了解如何在 Roku SceneGraph 中实现 DAI。

## 快速入门（通用工作流程）

1.  导入 SDK
2.  初始化 SDK
3.  添加流事件监听器
4.  设置定时元数据转发
5.  发起流请求
6.  当流失败或用户离开流时清理 SDK 资源。
