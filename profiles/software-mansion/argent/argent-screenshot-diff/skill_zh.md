## 1. 角色

将 `screenshot-diff` 作为 UI QA 和视觉回归检查的辅助视觉证据。它突出显示像素可见的变化或稳定性；它不能替代视觉检查、可访问性/组件树状态、帧/属性检查、日志、网络证据或应用行为。

不要使用截图差异来发现点击坐标。使用 `describe`、`debugger-component-tree` 或 `native-describe-screen` 首先找到目标。

`screenshot-diff` 支持物理 iPhone（类型为 `"device"`）用于保存文件差异和实时捕获。硬件上的实时捕获会通过设备上的运行器以全分辨率进行，是全局性的，并且不需要注册应用。按设备型号和分辨率保留基线，并注意硬件上的 `rotation` 参数会被忽略：捕获将遵循设备的实际方向。

## 2. 何时使用

当像素比较可以回答验证问题时，使用 `screenshot-diff`：

- 对于显式的 "UI 回归测试"、"视觉回归测试"、"截图差异"、"比较截图" 或 "前后视觉比较" 请求，除非无法生成稳定的可比较截图，否则需要使用。
- 适用于受影响屏幕具有稳定的前后状态且预期结果为像素可见的情况：布局、位置、大小、间距、颜色、排版、图像/图标渲染、裁剪、溢出或文本渲染。
- 适用于存在意外视觉回归风险的情况，即超出精确更改元素的范围。
- 不适用于结果更适合结构化验证的情况：状态变化、导航存在、可访问性树内容、控制台/网络行为或单元测试。
- 不适用于动态内容、不可暂停的动画、时间戳、广告、随机数据或缺失基线/当前截图会使比较产生噪声或无意义的情况。

## 3. 捕获规则

使用常规的下采样 `screenshot` 调用来检查 UI 上下文和状态。仅在保存用于视觉回归比较的基线/当前 PNG 文件时使用全分辨率截图。抑制图像块，以便全尺寸 PNG 不会被加载到上下文中：

```json
{ "udid": "<UDID>", "scale": 1.0, "includeImageInContext": false }
```

在可行的情况下，在相关交互之前或编辑之前捕获稳定的基线。在应用重新加载、重建或达到测试状态后，将其与更改后或交互后的屏幕进行比较。

## 4. 参数

为基线侧和当前侧分别提供 `udid` 和恰好一个输入：

- 常见的 UI 回归流程：保存的基线加上实时当前 -> `baselinePath`、`captureCurrent: true`、`udid`、`outputDir`。
- 两个截图都已保存 -> `baselinePath`、`currentPath`、`udid`、`outputDir`。
- 罕见的 fixture 流程：实时基线加上保存的当前 -> `captureBaseline: true`、`currentPath`、`udid`、`outputDir`。
- 不要将 `captureBaseline: true` 与 `captureCurrent: true` 结合使用，或为同一侧同时提供路径和实时捕获标志。

## 5. 确定性流程

1. 导航到已知良好的状态。
2. 使用 `scale: 1.0` 和 `includeImageInContext: false` 通过 `screenshot` 捕获基线 PNG，并保留返回的 `path`。
3. 执行交互，应用代码更改并导航到测试状态。
4. 调用 `screenshot-diff`，使用保存的 `baselinePath`、`captureCurrent: true`、`udid` 和 `outputDir`。
5. 检查摘要和工件路径，然后将差异与正常的视觉检查以及断言所需的任何结构化/运行时证据结合起来。

```json
{
  "baselinePath": "/tmp/baseline.png",
  "captureCurrent": true,
  "udid": "<UDID>",
  "outputDir": "/tmp/argent-diff"
}
```

如果两个图像都已保存，请为两侧使用文件路径：

```json
{
  "baselinePath": "/tmp/baseline.png",
  "currentPath": "/tmp/current.png",
  "udid": "<UDID>",
  "outputDir": "/tmp/argent-diff"
}
```
