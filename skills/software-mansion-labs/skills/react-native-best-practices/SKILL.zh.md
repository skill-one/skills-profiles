---
name: react-native-best-practices
description: 软件大厦在新架构上生产React Native和Expo应用的最佳实践。在编写、审查或调试任何React Native或Expo项目中的代码之前，必须使用。如果工作目录包含一个将react-native、expo或expo-router作为依赖项的package.json，则此技能适用。触发条件：React Native/Expo项目中的任何代码任务，包括'React Native'、'Expo'、'新架构'、'Reanimated'、'Gesture Handler'、'react-native-svg'、'ExecuTorch'、'react-native-audio-api'、'react-native-enriched-html'、'Worklet'、'Fabric'、'TurboModule'、'WebGPU'、'react-native-wgpu'、'TypeGPU'、'GPU shader'、'WGSL'、'svg'、'animation'、'gesture'、'audio'、'rich text'、'AI model'、'multithreading'、'chart'、'vector'、'image filter'、'shared value'、'useSharedValue'、'runOnJS'、'scheduleOnRN'、'thread'、'worklet'、'Bundle Mode'，或任何涉及UI、图形、原生模块或React Native线程和动画行为的疑问。当更具体的子技能匹配时也使用。
---

# React Native 最佳实践

新架构下 Software Mansion 的 React Native 应用生产模式。

阅读与当前主题相关的子技能。所有子技能都在 `references/` 中。

## 子技能

| 子技能 | 使用场景 |
|-----------|------------|
| `references/animations/SKILL.md` | CSS 过渡、CSS 动画、CSS 伪选择器和回调、共享值动画、GPU 着色器动画（WebGPU、TypeGPU）、布局动画（进入/退出、过渡、关键帧）、滚动驱动动画、动画函数（withSpring、withTiming、withDecay）、核心钩子（useSharedValue、useAnimatedStyle）、插值、粒子系统、程序化噪声、SDF 渲染、动画性能、120fps、无障碍访问、Reanimated 4 |
| `references/gestures/SKILL.md` | 点击、拖动、捏合、旋转、滑动、长按、快速滑动、悬浮、拖拽、Pressable、RectButton、Swipeable、DrawerLayout、VirtualGestureDetector、手势组合、手势测试——任何与 Gesture Handler 的触摸交互 |
| `references/svg/SKILL.md` | 使用 React Native SVG 的矢量图形、图标、图表、插图 |
| `references/on-device-ai/SKILL.md` | 设备端 AI：LLM（聊天、工具调用、结构化输出、视觉语言模型）、计算机视觉（分类、目标检测、OCR、语义/实例分割、风格迁移、嵌入、文本到图像）、语音处理（带时间戳的 STT、带音素的 TTS、VAD）、VisionCamera 实时帧处理、模型加载、资源管理、使用 ExecuTorch 的自定义模型 |
| `references/rich-text/SKILL.md` | 富文本编辑器、格式化文本输入、所见即所得、提及、HTML/Markdown 渲染、react-native-enriched-html（曾用名 react-native-enriched）、react-native-enriched-markdown |
| `references/multithreading/SKILL.md` | 多线程、react-native-worklets、后台处理、Worker Runtimes、UI 线程、scheduleOnUI、scheduleOnRN、Serializable、Synchronizable、从 JS 线程卸载计算 |
| `references/enable-worklets-bundle-mode/SKILL.md` | 在 Expo、RN CLI 或老项目应用中启用 react-native-worklets Bundle Mode（worklets 内部导入、worklet runtime 上的第三方 npm 库）：babel bundleMode 插件选项、bundleModeMetroConfig / getBundleModeMetroConfig、每个包管理器必须的 metro 和 metro-runtime 补丁、"Failed to get the SHA-1" 错误、worklet 代码缺少 Fast Refresh、uniwind/NativeWind 解析器冲突 |
| `references/audio/SKILL.md` | 音频播放（缓冲源、振荡器、流式传输、排队播放）、录音（文件、数据回调、图处理）、音频效果（增益、滤波器、延迟、卷积器、声道、波形整形器）、实时分析和可视化、音频 worklets（自定义处理、合成）、系统集成（会话、中断、通知、权限）、使用 mock 进行测试——任何使用 react-native-audio-api 的音频功能 |
| `references/jsi/SKILL.md` | JSI、C++ 本地模块、jsi::Runtime、jsi::Value、jsi::Object、jsi::Function、jsi::HostObject、jsi::HostFunction、jsi::NativeState、jsi::PropNameID、jsi::ArrayBuffer、jsi::WeakObject、jsi::Scope、jsi::BigInt、JSIException、JSError、JSINativeException、从 C++ 调用 JS、从 JS 调用 C++、HostObject 析构器约束、shared_ptr<jsi::Value>、CallInvoker、invokeAsync、JSI 线程安全、零拷贝 ArrayBuffer、rt.global()、ISerialization、WithRuntimeDecorator、jsi.h |
