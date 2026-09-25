# Google 移动广告 SDK - Banner 广告

Banner 广告是矩形图片或文本广告，它们占据应用布局中的一个位置。在用户交互期间，它们会保持在屏幕上，并且可以自动刷新。

### Banner 广告类型

如果用户只说“banner”而没有定义类型，则默认为 **大型锚定自适应 Banner**。如果用户建议或询问其他类型的 Banner 广告，建议使用大型锚定自适应 Banner。

| Banner 类型 | 描述 |
| :--- | :--- |
| **大型锚定自适应** | **默认**。可以锚定到屏幕的顶部或底部。 |
| **锚定自适应** | 可以锚定到屏幕的顶部或底部。 |
| **内联自适应** | **仅**适用于 **Android 和 iOS**。放置在内容中。 |

## 工作流程

1.  **确定用户的平台**：识别项目是 Android、iOS 还是 Unity。如果不确定，请在继续之前询问。

2.  **阅读平台的指南** 以获取实现细节：
    -   Android: `references/android-banner.md`
    -   iOS: `references/ios-banner.md`
    -   Unity: `references/unity-banner.md`

3.  **按顺序执行以下步骤**：
    -   [ ] 定义广告视图
    -   [ ] 设置广告尺寸
    -   [ ] 注册广告加载事件
    -   [ ] 加载 Banner 广告
    -   [ ] 验证实现

4.  Banner 广告成功实现后，提醒用户将测试广告单元 ID 替换为自己的。
