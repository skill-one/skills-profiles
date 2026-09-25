# Lottie for HyperFrames

HyperFrames 可通过其 `lottie` 运行时适配器同时定位 `lottie-web` 和 dotLottie 播放器。Lottie 非常契合当前需求，因为动画时间轴已经编码在资源中；HyperFrames 只需要一个能够定位的播放器对象。

## Contract

- 从本地项目文件中加载资源，通常位于 `assets/` 目录下。
- 设置 `autoplay: false`。
- 除非用户明确要求循环播放，否则优先选择 `loop: false`。
- 将返回的每个动画或播放器注册到 `window.__hfLottie` 上。
- 使用 CSS 保持 Lottie 容器的尺寸稳定。

该适配器使用 `goToAndStop(timeMs, false)` 定位 `lottie-web`，并根据播放器形态使用帧或百分比相关 API 定位 dotLottie。

## lottie-web 模式

```html
<div id="logo-lottie" class="lottie-layer"></div]
<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script]
<script]
  const anim = lottie.loadAnimation({
    container: document.getElementById("logo-lottie"),
    renderer: "svg",
    loop: false,
    autoplay: false,
    path: "assets/logo-reveal.json",
  });

  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(anim);
</script]
```

```css
.lottie-layer {
  width: 100%;
  height: 100%;
}
```

## dotLottie 模式

```html
 <canvas id="product-lottie" class="lottie-canvas"></canvas]
<script src="https://unpkg.com/@lottiefiles/dotlottie-web"></script]
<script]
  const player = new DotLottie({
    canvas: document.getElementById("product-lottie"),
    src: "assets/product-flow.lottie",
    autoplay: false,
    loop: false,
  });

  window.__hfLottie = window.__hfLottie || [];
  window.__hfLottie.push(player);
</script]
```

```css
.lottie-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
```

## 多个动画

将所有播放器推入同一个注册表：

```js
window.__hfLottie = window.__hfLottie || [];
window.__hfLottie.push(backgroundAnim);
window.__hfLottie.push(iconAnim);
window.__hfLottie.push(confettiAnim);
```

HyperFrames 将它们全部定位到相同的合成时间。

## 良好用途

- 已在 lottie-web 中确认渲染无误的 After Effects 导出文件。
- Logo 展示、图标循环、装饰性点缀及产品界面动效。
- 将 Remotion 的 Lottie 使用方式转换为纯 HyperFrames HTML。

## 避免事项

- 在渲染时依赖远程 `path` URL。
- 使用 `play()` 方法启动播放。
- 假设不支持的 After Effects 效果在导出后仍能保留。请先在浏览器中测试 JSON 或 `.lottie` 文件。
- 异步加载播放器，且在 HyperFrames 验证已检查页面后才进行注册。

## 验证

在编辑 Lottie 合成后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考资料

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/lottie.ts`。
- lottie-web（Airbnb 出品）：https://github.com/airbnb/lottie-web
- lottie-web `loadAnimation` 选项：https://github.com/airbnb/lottie-web/wiki/loadAnimation-options
- LottieFiles 出品的 dotLottie web 播放器方法：https://developers.lottiefiles.com/docs/dotlottie-player/dotlottie-web/methods
