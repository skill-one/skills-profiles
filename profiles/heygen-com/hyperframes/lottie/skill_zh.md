# HyperFrames 中的 Lottie

HyperFrames 可以通过其 `lottie` 运行时适配器来寻址 `lottie-web` 和 dotLottie 播放器。Lottie 是一个很好的选择，因为动画时间轴已经编码在资源中；HyperFrames 只需要一个可以寻址的播放器对象。

## 协议

- 从本地项目文件加载资源，通常在 `assets/` 目录下。
- 设置 `autoplay: false`。
- 除非用户明确要求循环，否则优先选择 `loop: false`。
- 将每个返回的动画或播放器注册到 `window.__hfLottie`。
- 使用 CSS 保持 Lottie 容器的尺寸稳定。

适配器使用 `goToAndStop(timeMs, false)` 寻址 `lottie-web`，使用 dotLottie 的帧或百分比 API，具体取决于播放器形状。

## lottie-web 模式

```html
<div id="logo-lottie" class="lottie-layer"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<script>
  const anim = lottie.loadAnimation({
    container: document.getElementById("logo-lottie"),
    renderer: "svg",
    loop: false,
    autoplay: false,
    path: "assets/logo-reveal.json",
  });

  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(anim);
</script>
```

```css
.lottie-layer {
  width: 100%;
  height: 100%;
}
```

## dotLottie 模式

```html
<canvas id="product-lottie" class="lottie-canvas"></canvas>
<script src="https://unpkg.com/@lottiefiles/dotlottie-web"></script>
<script>
  const player = new DotLottie({
    canvas: document.getElementById("product-lottie"),
    src: "assets/product-flow.lottie",
    autoplay: false,
    loop: false,
  });

  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(player);
</script>
```

```css
.lottie-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
```

## 多个动画

将每个播放器推送到相同的注册表中：

```js
window.__hfLottie = window.__hfLottie || [];
window.__hfLottie.push(backgroundAnim);
window.__hfLottie.push(iconAnim);
window.__hfLottie.push(confettiAnim);
```

HyperFrames 将它们全部寻址到相同的时间。

## 适用场景

- 已知在 lottie-web 中正确渲染的 After Effects 导出文件。
- Logo 揭示、图标循环、装饰性点缀和产品 UI 动画。
- 将 Remotion Lottie 使用转换为纯 HyperFrames HTML。

## 避免

- 在渲染时依赖远程 `path` URL。
- 使用 `play()` 开始播放。
- 假设不支持的 After Effects 效果会保留在导出中。先在浏览器中测试 JSON 或 `.lottie` 文件。
- 异步加载播放器并在 HyperFrames 验证页面后注册。

## 验证

编辑 Lottie 组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源代码：`packages/core/src/runtime/adapters/lottie.ts`。
- lottie-web by Airbnb: https://github.com/airbnb/lottie-web
- lottie-web `loadAnimation` 选项: https://github.com/airbnb/lottie-web/wiki/loadAnimation-options
- dotLottie web 播放器方法 by LottieFiles: https://developers.lottiefiles.com/docs/dotlottie-player/dotlottie-web/methods
