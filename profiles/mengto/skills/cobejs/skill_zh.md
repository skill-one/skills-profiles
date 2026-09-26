# cobe.js — 轻量级 WebGL 地球仪技能

## 使用场景
- 主页或关于页面中的“旋转地球仪”/位置标记
- 需要一个小型、专注的地球仪库（非完整的 three.js）
- 带有标记、旋转等交互的装饰性功能，且设置简单

## 核心API/模式
- 核心：
  - `import createGlobe from "cobe"`
  - `const globe = createGlobe(canvas, { ...options, onRender(state) { ... } })`
- 重要选项（常见）：
  - `devicePixelRatio`, `width`, `height`
  - `phi`, `theta`（旋转角度）
  - `scale`, `dark`, `diffuse`
  - `baseColor`, `markerColor`, `glowColor`
  - `markers: [{ location: [lat, lon], size, color? }]`
- 生命周期：
  - `globe.toggle()` 暂停RAF
  - `globe.destroy()` 移除实例

## 常见问题
- Canvas尺寸不匹配
  - 同时设置CSS尺寸，并设置canvas的`width/height`按DPR缩放。
- 缩放时不更新
  - 重新计算宽高，并重新创建或更新参数。
- 移动设备上DPR过高
  - 将DPR限制在1-2之间。

## 快速示例：带标记的响应式地球仪
```js
import createGlobe from "cobe";

const canvas = document.getElementById("cobe");
let phi = 0;

function setup() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio, 2);
  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);

  const globe = createGlobe(canvas, {
    devicePixelRatio: dpr,
    width: canvas.width,
    height: canvas.height,
    phi: 0,
    theta: 0.2,
    dark: 0,
    diffuse: 1.2,
    scale: 1,
    mapSamples: 16000,
    mapBrightness: 6,
    baseColor: [0.2, 0.2, 0.25],
    glowColor: [1, 1, 1],
    markerColor: [0.8, 0.5, 1],
    markers: [{ location: [1.3521, 103.8198], size: 0.08 }],
    onRender: (state) => {
      state.phi = phi;
      phi += 0.01;
    },
  });

  return globe;
}

let globe = setup();
window.addEventListener("resize", () => {
  globe.destroy();
  globe = setup();
});
```

## 需要询问用户的内容
- 地球仪尺寸和位置（主页、章节、卡片）？
- 标记位置和颜色（符合品牌）？
- 交互需求（拖动旋转 vs. 环境旋转）？
