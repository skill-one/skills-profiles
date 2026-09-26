# VueUse 函数

这项技能是 Vue.js / Nuxt 项目中 VueUse 组合式函数的决策和实现指南。它将需求映射到最合适的 VueUse 函数，应用正确的使用模式，并优先考虑基于组合式函数的解决方案，以保持实现简洁、可维护和高效。

## 应用时机

- 在协助 Vue.js / Nuxt 用户开发工作时，始终应用此技能。
- 始终首先检查是否可以使用 VueUse 函数来实现需求。
- 优先考虑 VueUse 组合式函数而不是自定义代码，以提高可读性、可维护性和性能。
- 将需求映射到最合适的 VueUse 函数，并遵循函数的调用规则。
- 请参考下方函数表中的 `Invocation` 字段。例如：
  - `AUTO`：在适用时自动使用。
  - `EXTERNAL`：仅在用户已经安装所需的外部依赖时使用；否则重新考虑，并在确实需要时才要求安装。
  - `EXPLICIT_ONLY`：仅在用户明确要求时使用。
> *注意* 提示或 `AGENTS.md` 中的用户指令可能会覆盖函数的默认 `Invocation` 规则。

## 函数

下面列出的所有函数都是 [VueUse](https://vueuse.org/) 库的一部分，每个部分根据其功能进行分类。

**重要提示**：每个函数条目都包括简短的 `Description` 和详细的 `Reference`。在使用任何函数时，始终查阅 `./references` 中的相应文档以获取使用细节和类型声明。

### 状态

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`createGlobalState`](references/createGlobalState.md) | 在全局范围内保存状态，以便跨 Vue 实例重用 | AUTO |
| [`createInjectionState`](references/createInjectionState.md) | 创建可以注入到组件中的全局状态 | AUTO |
| [`createSharedComposable`](references/createSharedComposable.md) | 使组合式函数可用与多个 Vue 实例一起使用 | AUTO |
| [`injectLocal`](references/injectLocal.md) | 扩展 `inject`，具有调用 `provideLocal` 以在同一个组件中提供值的 ability | AUTO |
| [`provideLocal`](references/provideLocal.md) | 扩展 `provide`，具有调用 `injectLocal` 以在同一个组件中获取值的 ability | AUTO |
| [`useAsyncState`](references/useAsyncState.md) | 反应式异步状态 | AUTO |
| [`useDebouncedRefHistory`](references/useDebouncedRefHistory.md) | 带有防抖过滤器的 `useRefHistory` 的简写 | AUTO |
| [`useLastChanged`](references/useLastChanged.md) | 记录最后更改的时间戳 | AUTO |
| [`useLocalStorage`](references/useLocalStorage.md) | 反应式 [LocalStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) | AUTO |
| [`useManualRefHistory`](references/useManualRefHistory.md) | 当用户调用 `commit()` 时，手动跟踪 ref 的更改历史 | AUTO |
| [`useRefHistory`](references/useRefHistory.md) | 跟踪 ref 的更改历史 | AUTO |
| [`useSessionStorage`](references/useSessionStorage.md) | 反应式 [SessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage) | AUTO |
| [`useStorage`](references/useStorage.md) | 创建一个反应式 ref，可用于访问和修改 [LocalStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localstorage) 或 [SessionStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionstorage) | AUTO |
| [`useStorageAsync`](references/useStorageAsync.md) | 带有异步支持的反应式存储 | AUTO |
| [`useThrottledRefHistory`](references/useThrottledRefHistory.md) | 带有节流过滤器的 `useRefHistory` 的简写 | AUTO |

### 元素

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useActiveElement`](references/useActiveElement.md) | 反应式 `document.activeElement` | AUTO |
| [`useDocumentVisibility`](references/useDocumentVisibility.md) | 反应式跟踪 [`document.visibilityState`](https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilityState) | AUTO |
| [`useDraggable`](references/useDraggable.md) | 使元素可拖动 | AUTO |
| [`useDropZone`](references/useDropZone.md) | 创建一个可以放置文件的区域 | AUTO |
| [`useElementBounding`](references/useElementBounding.md) | 反应式 HTML 元素的边界框 | AUTO |
| [`useElementOverflow`](references/useElementOverflow.md) | 反应式元素的溢出状态 | AUTO |
| [`useElementSize`](references/useElementSize.md) | 反应式 HTML 元素的大小 | AUTO |
| [`useElementVisibility`](references/useElementVisibility.md) | 跟踪元素在视口中的可见性 | AUTO |
| [`useIntersectionObserver`](references/useIntersectionObserver.md) | 检测目标元素的可见性变化 | AUTO |
| [`useMouseInElement`](references/useMouseInElement.md) | 与元素相关的反应式鼠标位置 | AUTO |
| [`useMutationObserver`](references/useMutationObserver.md) | 监听 DOM 树中的更改 | AUTO |
| [`useParentElement`](references/useParentElement.md) | 获取给定元素的父元素 | AUTO |
| [`useResizeObserver`](references/useResizeObserver.md) | 报告元素内容或边框盒尺寸的变化 | AUTO |
| [`useWindowFocus`](references/useWindowFocus.md) | 使用 `window.onfocus` 和 `window.onblur` 事件反应式跟踪窗口焦点 | AUTO |
| [`useWindowScroll`](references/useWindowScroll.md) | 反应式窗口滚动 | AUTO |
| [`useWindowSize`](references/useWindowSize.md) | 反应式窗口大小 | AUTO |

### 浏览器

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useBluetooth`](references/useBluetooth.md) | 反应式 [Web Bluetooth API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Bluetooth_API) | AUTO |
| [`useBreakpoints`](references/useBreakpoints.md) | 反应式视口断点 | AUTO |
| [`useBroadcastChannel`](references/useBroadcastChannel.md) | 反应式 [BroadcastChannel API](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel) | AUTO |
| [`useBrowserLocation`](references/useBrowserLocation.md) | 反应式浏览器位置 | AUTO |
| [`useClipboard`](references/useClipboard.md) | 反应式 [Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API) | AUTO |
| [`useClipboardItems`](references/useClipboardItems.md) | 反应式 [Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API) | AUTO |
| [`useColorMode`](references/useColorMode.md) | 反应式颜色模式（暗 / 亮 / 自定义）并具有自动数据持久性 | AUTO |
| [`useCssSupports`](references/useCssSupports.md) | 兼容 SSR 的反应式 [`CSS.supports`](https://developer.mozilla.org/docs/Web/API/CSS/supports_static) | AUTO |
| [`useCssVar`](references/useCssVar.md) | 操作 CSS 变量 | AUTO |
| [`useDark`](references/useDark.md) | 反应式暗模式并具有自动数据持久性 | AUTO |
| [`useEventListener`](references/useEventListener.md) | 轻松使用 EventListener | AUTO |
| [`useEyeDropper`](references/useEyeDropper.md) | 反应式 [EyeDropper API](https://developer.mozilla.org/en-US/docs/Web/API/EyeDropper_API) | AUTO |
| [`useFavicon`](references/useFavicon.md) | 反应式图标 | AUTO |
| [`useFileDialog`](references/useFileDialog.md) | 轻松打开文件对话框 | AUTO |
| [`useFileSystemAccess`](references/useFileSystemAccess.md) | 使用 [FileSystemAccessAPI](https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API) 创建、读取和写入本地文件 | AUTO |
| [`useFullscreen`](references/useFullscreen.md) | 反应式 [Fullscreen API](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API) | AUTO |
| [`useGamepad`](references/useGamepad.md) | 提供 [Gamepad API](https://developer.mozilla.org/en-US/docs/Web/API/Gamepad_API) 的反应式绑定 | AUTO |
| [`useImage`](references/useImage.md) | 反应式在浏览器中加载图像 | AUTO |
| [`useLiveAnnouncer`](references/useLiveAnnouncer.md) | 以屏幕阅读器用户（ARIA live regions）友好的方式宣布消息 | AUTO |
| [`useMediaControls`](references/useMediaControls.md) | 反应式 `audio` 和 `video` 元素的媒体控制 | AUTO |
| [`useMediaQuery`](references/useMediaQuery.md) | 反应式 [Media Query](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries/Testing_media_queries) | AUTO |
| [`useMemory`](references/useMemory.md) | 反应式内存信息 | AUTO |
| [`useObjectUrl`](references/useObjectUrl.md) | 反应式表示对象的 URL | AUTO |
| [`usePerformanceObserver`](references/usePerformanceObserver.md) | 观察 Performance 指标 | AUTO |
| [`usePermission`](references/usePermission.md) | 反应式 [Permissions API](https://developer.mozilla.org/en-US/docs/Web/API/Permissions_API) | AUTO |
| [`usePreferredColorScheme`](references/usePreferredColorScheme.md) | 反应式 [prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) 媒体查询 | AUTO |
| [`usePreferredContrast`](references/usePreferredContrast.md) | 反应式 [prefers-contrast](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-contrast) 媒体查询 | AUTO |
| [`usePreferredDark`](references/usePreferredDark.md) | 反应式暗主题偏好 | AUTO |
| [`usePreferredLanguages`](references/usePreferredLanguages.md) | 反应式 [Navigator Languages](https://developer.mozilla.org/en-US/docs/Web/API/NavigatorLanguage/languages) | AUTO |
| [`usePreferredReducedMotion`](references/usePreferredReducedMotion.md) | 反应式 [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) 媒体查询 | AUTO |
| [`usePreferredReducedTransparency`](references/usePreferredReducedTransparency.md) | 反应式 [prefers-reduced-transparency](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency) 媒体查询 | AUTO |
| [`useScreenOrientation`](references/useScreenOrientation.md) | 反应式 [Screen Orientation API](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Orientation_API) | AUTO |
| [`useScreenSafeArea`](references/useScreenSafeArea.md) | 反应式 `env(safe-area-inset-*)` | AUTO |
| [`useScriptTag`](references/useScriptTag.md) | 创建脚本标签 | AUTO |
| [`useShare`](references/useShare.md) | 反应式 [Web Share API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share) | AUTO |
| [`useSSRWidth`](references/useSSRWidth.md) | 用于设置全局视口宽度，当渲染依赖视口宽度的 SSR 组件时使用，如 [`useMediaQuery`](../useMediaQuery/index.md) 或 [`useBreakpoints`](../useBreakpoints/index.md) | AUTO |
| [`useStyleTag`](references/useStyleTag.md) | 在头部注入反应式 `style` 元素 | AUTO |
| [`useTextareaAutosize`](references/useTextareaAutosize.md) | 根据内容自动更新文本区域的高度 | AUTO |
| [`useTextDirection`](references/useTextDirection.md) | 反应式元素文本的 `dir` | AUTO |
| [`useTitle`](references/useTitle.md) | 反应式文档标题 | AUTO |
| [`useUrlSearchParams`](references/useUrlSearchParams.md) | 反应式 [URLSearchParams](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams) | AUTO |
| [`useVibrate`](references/useVibrate.md) | 反应式 [Vibration API](https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API) | AUTO |
| [`useWakeLock`](references/useWakeLock.md) | 反应式 [Screen Wake Lock API](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Wake_Lock_API) | AUTO |
| [`useWebMCP`](references/useWebMCP.md) | 注册 [WebMCP](https://github.com/webmachinelearning/webmcp) 工具并将其生命周期与当前 Vue 范围绑定 | AUTO |
| [`useWebNotification`](references/useWebNotification.md) | 反应式 [Notification](https://developer.mozilla.org/en-US/docs/Web/API/notification) | AUTO |
| [`useWebWorker`](references/useWebWorker.md) | 简单的 [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers) 注册和通信 | AUTO |
| [`useWebWorkerFn`](references/useWebWorkerFn.md) | 在不阻塞 UI 的情况下运行昂贵的函数 | AUTO |

### 传感器

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`onClickOutside`](references/onClickOutside.md) | 监听元素外的点击 | AUTO |
| [`onElementRemoval`](references/onElementRemoval.md) | 当元素或包含它的任何元素从 DOM 中被移除时触发 | AUTO |
| [`onKeyStroke`](references/onKeyStroke.md) | 监听键盘按键 | AUTO |
| [`onLongPress`](references/onLongPress.md) | 监听元素的长按 | AUTO |
| [`onStartTyping`](references/onStartTyping.md) | 当用户在非可编辑元素上开始输入时触发 | AUTO |
| [`useBattery`](references/useBattery.md) | 反应式 [Battery Status API](https://developer.mozilla.org/en-US/docs/Web/API/Battery_Status_API) | AUTO |
| [`useDeviceMotion`](references/useDeviceMotion.md) | 反应式 [DeviceMotionEvent](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent) | AUTO |
| [`useDeviceOrientation`](references/useDeviceOrientation.md) | 反应式 [DeviceOrientationEvent](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent) | AUTO |
| [`useDevicePixelRatio`](references/useDevicePixelRatio.md) | 反应式跟踪 [`window.devicePixelRatio`](https://developer.mozilla.org/docs/Web/API/Window/devicePixelRatio) | AUTO |
| [`useDevicesList`](references/useDevicesList.md) | 反应式 [enumerateDevices](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/enumerateDevices) 列表可用输入/输出设备 | AUTO |
| [`useDisplayMedia`](references/useDisplayMedia.md) | 反应式 [`mediaDevices.getDisplayMedia`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getDisplayMedia) 流媒体 | AUTO |
| [`useElementByPoint`](references/useElementByPoint.md) | 反应式通过点定位元素 | AUTO |
| [`useElementHover`](references/useElementHover.md) | 反应式元素悬停状态 | AUTO |
| [`useFocus`](references/useFocus.md) | 反应式跟踪或设置 DOM 元素的焦点状态的工具 | AUTO |
| [`useFocusWithin`](references/useFocusWithin.md) | 反应式跟踪元素或其任何后代是否具有焦点 | AUTO |
| [`useFps`](references/useFps.md) | 反应式每秒帧数 (FPS) | AUTO |
| [`useGeolocation`](references/useGeolocation.md) | 反应式 [Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API) | AUTO |
| [`useIdle`](references/useIdle.md) | 跟踪用户是否处于非活动状态 | AUTO |
| [`useInfiniteScroll`](references/useInfiniteScroll.md) | 元素的无限滚动 | AUTO |
| [`useKeyModifier`](references/useKeyModifier.md) | 反应式 [Modifier State](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/getModifierState) | AUTO |
| [`useMagicKeys`](references/useMagicKeys.md) | 反应式按键按下状态 | AUTO |
| [`useMouse`](references/useMouse.md) | 反应式鼠标位置 | AUTO |
| [`useMousePressed`](references/useMousePressed.md) | 反应式鼠标按下状态 | AUTO |
| [`useNavigatorLanguage`](references/useNavigatorLanguage.md) | 反应式 [navigator.language](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language) | AUTO |
| [`useNetwork`](references/useNetwork.md) | 反应式 [Network status](https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API) | AUTO |
| [`useOnline`](references/useOnline.md) | 反应式在线状态 | AUTO |
| [`usePageLeave`](references/usePageLeave.md) | 反应式状态，显示鼠标是否离开页面 | AUTO |
| [`useParallax`](references/useParallax.md) | 轻松创建视差效果 | AUTO |
| [`usePointer`](references/usePointer.md) | 反应式 [pointer state](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events) | AUTO |
| [`usePointerLock`](references/usePointerLock.md) | 反应式 [pointer lock](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_Lock_API) | AUTO |
| [`usePointerSwipe`](references/usePointerSwipe.md) | 基于 [PointerEvents](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent) 的反应式滑动检测 | AUTO |
| [`useScroll`](references/useScroll.md) | 反应式滚动位置和状态 | AUTO |
| [`useScrollLock`](references/useScrollLock.md) | 锁定元素的滚动 | AUTO |
| [`useSpeechRecognition`](references/useSpeechRecognition.md) | 反应式 [SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition) | AUTO |
| [`useSpeechSynthesis`](references/useSpeechSynthesis.md) | 反应式 [SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) | AUTO |
| [`useSwipe`](references/useSwipe.md) | 基于 [`TouchEvents`](https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent) 的反应式滑动检测 | AUTO |
| [`useTextSelection`](references/useTextSelection.md) | 基于 [`Window.getSelection`](https://developer.mozilla.org/en-US/docs/Web/API/Window/getSelection) 反应式跟踪用户文本选择 | AUTO |
| [`useUserMedia`](references/useUserMedia.md) | 反应式 [`mediaDevices.getUserMedia`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia) 流媒体 | AUTO |

### 网络

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useEventSource`](references/useEventSource.md) | [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) 或 [Server-Sent-Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 实例打开与 HTTP 服务器的持久连接 | AUTO |
| [`useFetch`](references/useFetch.md) | 反应式 [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) 提供中止请求的能力 | AUTO |
| [`useWebSocket`](references/useWebSocket.md) | 反应式 [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket) 客户端 | AUTO |

### 动画

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useAnimate`](references/useAnimate.md) | 反应式 [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) | AUTO |
| [`useInterval`](references/useInterval.md) | 每个间隔增加的反应式计数器 | AUTO |
| [`useIntervalFn`](references/useIntervalFn.md) | `setInterval` 的包装器，具有控制功能 | AUTO |
| [`useNow`](references/useNow.md) | 反应式当前 Date 实例 | AUTO |
| [`useRafFn`](references/useRafFn.md) | 在每个 `requestAnimationFrame` 上调用函数 | AUTO |
| [`useTimeout`](references/useTimeout.md) | 在给定时间后变为 `true` 的反应式值 | AUTO |
| [`useTimeoutFn`](references/useTimeoutFn.md) | `setTimeout` 的包装器，具有控制功能 | AUTO |
| [`useTimestamp`](references/useTimestamp.md) | 反应式当前时间戳 | AUTO |
| [`useTransition`](references/useTransition.md) | 在值之间进行过渡 | AUTO |

### 组件

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`computedInject`](references/computedInject.md) | 结合 `computed` 和 `inject` | AUTO |
| [`createReusableTemplate`](references/createReusableTemplate.md) | 在组件作用域内定义和重用模板 | AUTO |
| [`createTemplatePromise`](references/createTemplatePromise.md) | 将模板作为 Promise | AUTO |
| [`tryOnBeforeMount`](references/tryOnBeforeMount.md) | 安全的 `onBeforeMount` | AUTO |
| [`tryOnBeforeUnmount`](references/tryOnBeforeUnmount.md) | 安全的 `onBeforeUnmount` | AUTO |
| [`tryOnMounted`](references/tryOnMounted.md) | 安全的 `onMounted` | AUTO |
| [`tryOnScopeDispose`](references/tryOnScopeDispose.md) | 安全的 `onScopeDispose` | AUTO |
| [`tryOnUnmounted`](references/tryOnUnmounted.md) | 安全的 `onUnmounted` | AUTO |
| [`unrefElement`](references/unrefElement.md) | 从 Vue ref 或组件实例中检索底层 DOM 元素 | AUTO |
| [`useCurrentElement`](references/useCurrentElement.md) | 将当前组件的 DOM 元素作为 ref 获取 | AUTO |
| [`useMounted`](references/useMounted.md) | ref 中的挂载状态 | AUTO |
| [`useTemplateRefsList`](references/useTemplateRefsList.md) | 简写，用于将 refs 绑定到 `v-for` 中的模板元素和组件 | AUTO |
| [`useVirtualList`](references/useVirtualList.md) | 轻松创建虚拟列表 | AUTO |
| [`useVModel`](references/useVModel.md) | `v-model` 绑定的简写 | AUTO |
| [`useVModels`](references/useVModels.md) | `props v-model` 绑定的简写 | AUTO |

### 监听

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`until`](references/until.md) | 一次性监听变化的 Promise | AUTO |
| [`watchArray`](references/watchArray.md) | 监听数组，包括添加和删除 | AUTO |
| [`watchAtMost`](references/watchAtMost.md) | 触发次数有限的 `watch` | AUTO |
| [`watchDebounced`](references/watchDebounced.md) | 防抖监听 | AUTO |
| [`watchDeep`](references/watchDeep.md) | 简写，用于监听具有 `{deep: true}` 的值 | AUTO |
| [`watchIgnorable`](references/watchIgnorable.md) | 可忽略的监听 | AUTO |
| [`watchImmediate`](references/watchImmediate.md) | 简写，用于监听具有 `{immediate: true}` 的值 | AUTO |
| [`watchOnce`](references/watchOnce.md) | 简写，用于监听具有 `{ once: true }` 的值 | AUTO |
| [`watchPausable`](references/watchPausable.md) | 可暂停的监听 | AUTO |
| [`watchThrottled`](references/watchThrottled.md) | 节流监听 | AUTO |
| [`watchTriggerable`](references/watchTriggerable.md) | 可以手动触发的监听 | AUTO |
| [`watchWithFilter`](references/watchWithFilter.md) | 具有附加 EventFilter 控制的 `watch` | AUTO |
| [`whenever`](references/whenever.md) | 简写，用于监听值为 truthy 的值 | AUTO |

### 反应性

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`computedAsync`](references/computedAsync.md) | 用于异步函数的 `computed` | AUTO |
| [`computedEager`](references/computedEager.md) | 无惰性计算的 `computed` | AUTO |
| [`computedWithControl`](references/computedWithControl.md) | 明确定义计算依赖项 | AUTO |
| [`createRef`](references/createRef.md) | 根据 `deep` 参数返回 `deepRef` 或 `shallowRef` | AUTO |
| [`extendRef`](references/extendRef.md) | 向 Ref 添加额外属性 | AUTO |
| [`reactify`](references/reactify.md) | 将普通函数转换为反应式函数 | AUTO |
| [`reactifyObject`](references/reactifyObject.md) | 将 `reactify` 应用于对象 | AUTO |
| [`reactiveComputed`](references/reactiveComputed.md) | 计算反应式对象 | AUTO |
| [`reactiveOmit`](references/reactiveOmit.md) | 从反应式对象中反应式忽略字段 | AUTO |
| [`reactivePick`](references/reactivePick.md) | 从反应式对象中反应式选择字段 | AUTO |
| [`refAutoReset`](references/refAutoReset.md) | 在一段时间后重置为默认值的 ref | AUTO |
| [`refDebounced`](references/refDebounced.md) | 防抖执行 ref 值 | AUTO |
| [`refDefault`](references/refDefault.md) | 将默认值应用于 ref | AUTO |
| [`refManualReset`](references/refManualReset.md) | 创建具有手动重置功能的 ref | AUTO |
| [`refThrottled`](references/refThrottled.md) | 节流 ref 值更改 | AUTO |
| [`refWithControl`](references/refWithControl.md) | 对 ref 和其反应性进行细粒度控制 | AUTO |
| [`syncRef`](references/syncRef.md) | 双向 refs 同步 | AUTO |
| [`syncRefs`](references/syncRefs.md) | 使目标 refs 与源 ref 保持同步 | AUTO |
| [`toReactive`](references/toReactive.md) | 将 ref 转换为反应式 | AUTO |
| [`toRef`](references/toRef.md) | 将值/ref/getter 规范为 `ref` 或 `computed` | EXPLICIT_ONLY |
| [`toRefs`](references/toRefs.md) | 扩展 [`toRefs`](https://vuejs.org/api/reactivity-utilities.html#torefs) 接受对象 refs | AUTO |

### 数组

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useArrayDifference`](references/useArrayDifference.md) | 反应式获取两个数组的差异 | AUTO |
| [`useArrayEvery`](references/useArrayEvery.md) | 反应式 `Array.every` | AUTO |
| [`useArrayFilter`](references/useArrayFilter.md) | 反应式 `Array.filter` | AUTO |
| [`useArrayFind`](references/useArrayFind.md) | 反应式 `Array.find` | AUTO |
| [`useArrayFindIndex`](references/useArrayFindIndex.md) | 反应式 `Array.findIndex` | AUTO |
| [`useArrayFindLast`](references/useArrayFindLast.md) | 反应式 `Array.findLast` | AUTO |
| [`useArrayIncludes`](references/useArrayIncludes.md) | 反应式 `Array.includes` | AUTO |
| [`useArrayJoin`](references/useArrayJoin.md) | 反应式 `Array.join` | AUTO |
| [`useArrayMap`](references/useArrayMap.md) | 反应式 `Array.map` | AUTO |
| [`useArrayReduce`](references/useArrayReduce.md) | 反应式 `Array.reduce` | AUTO |
| [`useArraySome`](references/useArraySome.md) | 反应式 `Array.some` | AUTO |
| [`useArrayUnique`](references/useArrayUnique.md) | 反应式唯一数组 | AUTO |
| [`useSorted`](references/useSorted.md) | 反应式排序数组 | AUTO |

### 时间

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useCountdown`](references/useCountdown.md) | 反应式秒数倒计时 | AUTO |
| [`useDateFormat`](references/useDateFormat.md) | 根据传入的标记字符串获取格式化的日期 | AUTO |
| [`useTemporalNow`](references/useTemporalNow.md) | 反应式 [Temporal API](https://tc39.es/proposal-temporal/docs/)，支持时区转换和日历系统 | AUTO |
| [`useTimeAgo`](references/useTimeAgo.md) | 反应式时间差 | AUTO |
| [`useTimeAgoIntl`](references/useTimeAgoIntl.md) | 支持国际化的反应式时间差 | AUTO |

### 工具

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`createDisposableDirective`](references/createDisposableDirective.md) | 编写可丢弃指令的工具 | AUTO |
| [`createEventHook`](references/createEventHook.md) | 创建事件钩子的工具 | AUTO |
| [`createUnrefFn`](references/createUnrefFn.md) | 接受 ref 和原始值作为参数的普通函数 | AUTO |
| [`get`](references/get.md) | `ref.value` 的简写 | EXPLICIT_ONLY |
| [`isDefined`](references/isDefined.md) | Ref 的非空检查类型守卫 | AUTO |
| [`makeDestructurable`](references/makeDestructurable.md) | 使对象和数组同时具有等价解构 | AUTO |
| [`set`](references/set.md) | `ref.value = x` 的简写 | EXPLICIT_ONLY |
| [`useAsyncQueue`](references/useAsyncQueue.md) | 按顺序依次执行异步任务，并将当前任务结果传递到下一个任务 | AUTO |
| [`useBase64`](references/useBase64.md) | 反应式 base64 转换 | AUTO |
| [`useCached`](references/useCached.md) | 使用自定义比较器缓存 ref | AUTO |
| [`useCloned`](references/useCloned.md) | ref 的反应式克隆 | AUTO |
| [`useConfirmDialog`](references/useConfirmDialog.md) | 创建事件钩子以支持模态框和确认对话框链 | AUTO |
| [`useCounter`](references/useCounter.md) | 基本计数器，带有实用函数 | AUTO |
| [`useCycleList`](references/useCycleList.md) | 循环遍历项目列表 | AUTO |
| [`useDebounceFn`](references/useDebounceFn.md) | 防抖执行函数 | AUTO |
| [`useEventBus`](references/useEventBus.md) | 基本事件总线 | AUTO |
| [`useMemoize`](references/useMemoize.md) | 缓存函数结果，并保持其反应性 | AUTO |
| [`useOffsetPagination`](references/useOffsetPagination.md) | 反应式偏移量分页 | AUTO |
| [`usePrevious`](references/usePrevious.md) | 持有 ref 的先前值 | AUTO |
| [`useStepper`](references/useStepper.md) | 提供构建多步骤向导界面的辅助函数 | AUTO |
| [`useSupported`](references/useSupported.md) | 兼容 SSR 的 `isSupported` | AUTO |
| [`useThrottleFn`](references/useThrottleFn.md) | 节流执行函数 | AUTO |
| [`useTimeoutPoll`](references/useTimeoutPoll.md) | 使用超时轮询某物 | AUTO |
| [`useToggle`](references/useToggle.md) | 布尔开关器，带有实用函数 | AUTO |
| [`useToNumber`](references/useToNumber.md) | 反应式将字符串 ref 转换为数字 | AUTO |
| [`useToString`](references/useToString.md) | 反应式将 ref 转换为字符串 | AUTO |

### @Electron

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useIpcRenderer`](references/useIpcRenderer.md) | 提供 [ipcRenderer](https://www.electronjs.org/docs/api/ipc-renderer) 及其所有 API，并具有 Vue 反应性 | EXTERNAL |
| [`useIpcRendererInvoke`](references/useIpcRendererInvoke.md) | 反应式 [ipcRenderer.invoke API](https://www.electronjs.org/docs/api/ipc-renderer#ipcrendererinvokechannel-args) 结果 | EXTERNAL |
| [`useIpcRendererOn`](references/useIpcRendererOn.md) | 轻松使用 [ipcRenderer.on](https://www.electronjs.org/docs/api/ipc-renderer#ipcrendereronchannel-listener) 并在卸载时自动使用 [ipcRenderer.removeListener](https://www.electronjs.org/docs/api/ipc-renderer#ipcrendererremovelistenerchannel-listener) | EXTERNAL |
| [`useZoomFactor`](references/useZoomFactor.md) | 反应式 [WebFrame](https://www.electronjs.org/docs/api/web-frame#webframe) 缩放因子 | EXTERNAL |
| [`useZoomLevel`](references/useZoomLevel.md) | 反应式 [WebFrame](https://www.electronjs.org/docs/api/web-frame#webframe) 缩放级别 | EXTERNAL |

### @Firebase

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useAuth`](references/useAuth.md) | 反应式 [Firebase Auth](https://firebase.google.com/docs/auth) 绑定 | EXTERNAL |
| [`useFirestore`](references/useFirestore.md) | 反应式 [Firestore](https://firebase.google.com/docs/firestore) 绑定 | EXTERNAL |
| [`useRTDB`](references/useRTDB.md) | 反应式 [Firebase Realtime Database](https://firebase.google.com/docs/database) 绑定 | EXTERNAL |

### @Head

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`createHead`](https://github.com/vueuse/head#api) | 创建头部管理器实例 | EXTERNAL |
| [`useHead`](https://github.com/vueuse/head#api) | 反应式更新头部元标签 | EXTERNAL |

### @Integrations

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useAsyncValidator`](references/useAsyncValidator.md) | [`async-validator`](https://github.com/yiminghe/async-validator) 的包装器 | EXTERNAL |
| [`useAxios`](references/useAxios.md) | [`axios`](https://github.com/axios/axios) 的包装器 | EXTERNAL |
| [`useChangeCase`](references/useChangeCase.md) | [`change-case`](https://github.com/blakeembrey/change-case) 的反应式包装器 | EXTERNAL |
| [`useCookies`](references/useCookies.md) | [`universal-cookie`](https://www.npmjs.com/package/universal-cookie) 的包装器 | EXTERNAL |
| [`useDrauu`](references/useDrauu.md) | [drauu](https://github.com/antfu/drauu) 的反应式实例 | EXTERNAL |
| [`useFocusTrap`](references/useFocusTrap.md) | [`focus-trap`](https://github.com/focus-trap/focus-trap) 的反应式包装器 | EXTERNAL |
| [`useFuse`](references/useFuse.md) | 使用 [Fuse.js](https://github.com/krisk/fuse) 实现模糊搜索的简写 | EXTERNAL |
| [`useIDBKeyval`](references/useIDBKeyval.md) | [`idb-keyval`](https://www.npmjs.com/package/idb-keyval) 的包装器 | EXTERNAL |
| [`useJwt`](references/useJwt.md) | [`jwt-decode`](https://github.com/auth0/jwt-decode) 的包装器 | EXTERNAL |
| [`useNProgress`](references/useNProgress.md) | [`nprogress`](https://github.com/rstacruz/nprogress) 的反应式包装器 | EXTERNAL |
| [`useQRCode`](references/useQRCode.md) | [`qrcode`](https://github.com/soldair/node-qrcode) 的包装器 | EXTERNAL |
| [`useSortable`](references/useSortable.md) | [`sortable`](https://github.com/SortableJS/Sortable) 的包装器 | EXTERNAL |

### @Math

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`createGenericProjection`](references/createGenericProjection.md) | `createProjection` 的通用版本 | EXTERNAL |
| [`createProjection`](references/createProjection.md) | 反应式从一个域映射到另一个域的数字投影 | EXTERNAL |
| [`logicAnd`](references/logicAnd.md) | refs 的 `AND` 条件 | EXTERNAL |
| [`logicNot`](references/logicNot.md) | ref 的 `NOT` 条件 | EXTERNAL |
| [`logicOr`](references/logicOr.md) | refs 的 `OR` 条件 | EXTERNAL |
| [`useAbs`](references/useAbs.md) | 反应式 `Math.abs` | EXTERNAL |
| [`useAverage`](references/useAverage.md) | 反应式获取数组的平均值 | EXTERNAL |
| [`useCeil`](references/useCeil.md) | 反应式 `Math.ceil` | EXTERNAL |
| [`useClamp`](references/useClamp.md) | 反应式将值限制在两个其他值之间 | EXTERNAL |
| [`useFloor`](references/useFloor.md) | 反应式 `Math.floor` | EXTERNAL |
| [`useMath`](references/useMath.md) | 反应式 `Math` 方法 | EXTERNAL |
| [`useMax`](references/useMax.md) | 反应式 `Math.max` | EXTERNAL |
| [`useMin`](references/useMin.md) | 反应式 `Math.min` | EXTERNAL |
| [`usePrecision`](references/usePrecision.md) | 反应式设置数字的精度 | EXTERNAL |
| [`useProjection`](references/useProjection.md) | 反应式从一个域映射到另一个域的数字投影 | EXTERNAL |
| [`useRound`](references/useRound.md) | 反应式 `Math.round` | EXTERNAL |
| [`useSum`](references/useSum.md) | 反应式获取数组的总和 | EXTERNAL |
| [`useTrunc`](references/useTrunc.md) | 反应式 `Math.trunc` | EXTERNAL |

### @Motion

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useElementStyle`](https://motion.vueuse.org/api/use-element-style) | 将反应式对象同步到目标元素的 CSS 样式 | EXTERNAL |
| [`useElementTransform`](https://motion.vueuse.org/api/use-element-transform) | 将反应式对象同步到目标元素的 CSS 变换 | EXTERNAL |
| [`useMotion`](https://motion.vueuse.org/api/use-motion) | 将组件置于动画状态 | EXTERNAL |
| [`useMotionProperties`](https://motion.vueuse.org/api/use-motion-properties) | 获取目标元素的 Motion Properties | EXTERNAL |
| [`useMotionVariants`](https://motion.vueuse.org/api/use-motion-variants) | 处理变体状态和选择 | EXTERNAL |
| [`useSpring`](https://motion.vueuse.org/api/use-spring) | 弹簧动画 | EXTERNAL |

### @Router

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useRouteHash`](references/useRouteHash.md) | 反应式 `route.hash` 的简写 | EXTERNAL |
| [`useRouteParams`](references/useRouteParams.md) | 反应式 `route.params` 的简写 | EXTERNAL |
| [`useRouteQuery`](references/useRouteQuery.md) | 反应式 `route.query` 的简写 | EXTERNAL |

### @RxJS

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`from`](references/from.md) | 包装 RxJS 的 [`from()`](https://rxjs.dev/api/index/function/from) 和 [`fromEvent()`](https://rxjs.dev/api/index/function/fromEvent) 以允许它们接受 `ref`s | EXTERNAL |
| [`toObserver`](references/toObserver.md) | 将 `ref` 转换为 RxJS [Observer](https://rxjs.dev/guide/observer) 的简写 | EXTERNAL |
| [`useExtractedObservable`](references/useExtractedObservable.md) | 使用从一个或多个组合式函数中提取的 RxJS [`Observable`](https://rxjs.dev/guide/observable) | EXTERNAL |
| [`useObservable`](references/useObservable.md) | 使用 RxJS [`Observable`](https://rxjs.dev/guide/observable) | EXTERNAL |
| [`useSubject`](references/useSubject.md) | 将 RxJS [`Subject`](https://rxjs.dev/guide/subject) 绑定到 `ref` 并双向传播值更改 | EXTERNAL |
| [`useSubscription`](references/useSubscription.md) | 无需担心取消订阅或创建内存泄漏地使用 RxJS [`Subscription`](https://rxjs.dev/guide/subscription) | EXTERNAL |
| [`watchExtractedObservable`](references/watchExtractedObservable.md) | 监听从一个或多个组合式函数中提取的 RxJS [`Observable`](https://rxjs.dev/guide/observable) 的值 | EXTERNAL |

### @SchemaOrg

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`createSchemaOrg`](https://vue-schema-org.netlify.app/api/core/create-schema-org.html) | 创建 schema.org 管理器实例 | EXTERNAL |
| [`useSchemaOrg`](https://vue-schema-org.netlify.app/api/core/use-schema-org.html) | 反应式更新 schema.org | EXTERNAL |

### @Sound

| 函数 | 描述 | 调用方式 |
|------|------|----------|
| [`useSound`](https://github.com/vueuse/sound#examples) | 反应式播放音效 | EXTERNAL |
