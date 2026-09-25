`Color` 类用于创建和转换用于色调、填充、描边以及 PixiJS 接受任何 `ColorSource` 的地方的颜色。大多数 API 直接接受原始十六进制/字符串，因此显式使用 `new Color(...)` 仅在转换格式或操作值时需要。

## 快速入门

```ts
const fillColor = new Color("#ff6600");
console.log(fillColor.toHex()); // '#ff6600'
console.log(fillColor.toNumber()); // 0xff6600
console.log(fillColor.toArray()); // [1, 0.4, 0, 1]

const g = new Graphics().rect(0, 0, 200, 100).fill(fillColor);
app.stage.addChild(g);

const sprite = Sprite.from("hero.png");
sprite.tint = "dodgerblue";
app.stage.addChild(sprite);

const t = Color.shared.setValue(0xffffff).multiply([1, 0.5, 0.5]).toNumber();
sprite.tint = t;
```

**相关技能：** `pixijs-scene-graphics`（填充/描边颜色）、`pixijs-scene-sprite`（色调）、`pixijs-blend-modes`（合成）。

## 核心模式

### 接受的输入格式

```ts
import { Color } from "pixi.js";

// 十六进制整数
new Color(0xff0000);

// 十六进制字符串
new Color("#ff0000");
new Color("#f00");
new Color("ff0000");

// CSS 颜色名称
new Color("red");
new Color("dodgerblue");

// RGB/RGBA 对象（组件 0-255）
new Color({ r: 255, g: 0, b: 0 });
new Color({ r: 255, g: 0, b: 0, a: 0.5 });

// HSL/HSLA 对象
new Color({ h: 0, s: 100, l: 50 });
new Color({ h: 0, s: 100, l: 50, a: 0.5 });

// HSV/HSVA 对象
new Color({ h: 0, s: 100, v: 100 });

// CSS 字符串
new Color("rgb(255, 0, 0)");
new Color("rgba(255, 0, 0, 0.5)");
new Color("hsl(0, 100%, 50%)");

// 归一化 0-1 数组（Float32Array 或普通数组）
new Color([1, 0, 0]); // RGB
new Color([1, 0, 0, 0.5]); // RGBA

// Uint8 数组（组件 0-255）
new Color(new Uint8Array([255, 0, 0]));
new Color(new Uint8ClampedArray([255, 0, 0, 128]));

// 8 位十六进制带透明度
new Color("#ff0000ff");
new Color("#f00f");

// 从另一个 Color 实例复制
const red = new Color("red");
const copy = new Color(red);
```

### 转换方法

```ts
import { Color } from "pixi.js";

const color = new Color("#ff6600");

color.toHex(); // '#ff6600'
color.toHexa(); // '#ff6600ff'（带透明度的十六进制）
color.toNumber(); // 0xff6600
color.toArray(); // [1, 0.4, 0, 1]（归一化 RGBA）
color.toRgbArray(); // [1, 0.4, 0]（归一化 RGB，无透明度）
color.toRgbaString(); // 'rgba(255,102,0,1)'
color.toRgba(); // { r: 1, g: 0.4, b: 0, a: 1 }
color.toRgb(); // { r: 1, g: 0.4, b: 0 }
color.toUint8RgbArray(); // [255, 102, 0]

// setValue() 是链式更改颜色值的方法
color.setValue(0xff0000).toHex(); // '#ff0000'
```

### 组件访问

```ts
import { Color } from "pixi.js";

const color = new Color("rgba(255, 128, 0, 0.8)");

color.red; // 1
color.green; // ~0.502
color.blue; // 0
color.alpha; // 0.8
```

所有组件获取器返回归一化 0-1 值。

### 操作

```ts
import { Color } from "pixi.js";

const color = new Color("red");

// 设置透明度（链式）
color.setAlpha(0.5);

// 与另一个颜色相乘（破坏性，原地修改）
color.multiply(0x808080);

// 预乘透明度（破坏性，RGB 通道乘以透明度）
color.premultiply(0.8);

// 仅预乘透明度（RGB 不变）
color.premultiply(0.8, false);

// 链式操作
new Color("white").setAlpha(0.5).multiply([0.8, 0.2, 0.2]);
```

`multiply()` 和 `premultiply()` 是破坏性的；它们修改颜色并将 `value` 设置为 null（原始格式丢失）。

### 非破坏性预乘输出

```ts
import { Color } from "pixi.js";

const color = new Color("red").setAlpha(0.5);

const packed = color.toPremultiplied(color.alpha); // 0x7F7F0000
const alphaOnly = color.toPremultiplied(color.alpha, false); // 0x7FFF0000
```

`toPremultiplied(alpha, applyToRGB?)` 返回一个 32 位 `0xAARRGGBB` 整数，而不修改 `this`。在需要重用源颜色的批处理器和色调计算中使用它。当 `applyToRGB` 为 `false` 时，仅打包透明度字节；RGB 保持其完整值。

### 重用输出缓冲区

```ts
import { Color } from "pixi.js";

const rgba = new Float32Array(4);
const rgb = new Float32Array(3);
const rgb8 = new Uint8Array(3);

app.ticker.add(() => {
  Color.shared.setValue(sprite.tint).toArray(rgba).toRgbArray(rgb);

  Color.shared.toUint8RgbArray(rgb8);
});
```

`toArray(out?)`, `toRgbArray(out?)`, 和 `toUint8RgbArray(out?)` 接受一个可重用的 `number[]`, `Float32Array`, `Uint8Array` 或 `Uint8ClampedArray` 并写入其中。在热点路径中传递自己的缓冲区以避免每帧分配；省略参数，`Color` 实例返回其内部缓存数组。

### 用于 GPU 缓冲区的打包

| 方法                   | 返回                                                      |
| ------------------------ | ------------------------------------------------------------ |
| `toBgrNumber()`          | 24 位 `0xBBGGRR` 整数，R/B 交换                   |
| `toLittleEndianNumber()` | 相同的 24 位交换，方便小端顶点写入 |

两者都很廉价且在直接将颜色发射到打包的顶点属性时很有用。

### `Color.shared` 用于临时操作

```ts
import { Color } from "pixi.js";

// 一次性转换，不分配新的 Color
const hex = Color.shared.setValue("#ff6600").toNumber();
const arr = Color.shared.setValue(0xff0000).toArray();
```

`Color.shared` 是一个单例，避免每次调用时分配新的 `Color`。这在渲染循环或每帧色调计算等热点路径中很重要，其中重复 `new Color()` 会导致 GC 压力。不要存储对其的引用；其他代码可能会修改它。

```ts
import { Color } from "pixi.js";

// 好：在每帧回调中重用共享实例
app.ticker.add(() => {
  const t = performance.now() / 1000;
  sprite.tint = Color.shared
    .setValue("white")
    .multiply([Math.sin(t) * 0.5 + 0.5, 0.2, 0.8])
    .toNumber();
});
```

### 验证输入

```ts
import { Color } from "pixi.js";

Color.isColorLike("red"); // true
Color.isColorLike("#ff0000"); // true
Color.isColorLike(0xff0000); // true
Color.isColorLike([1, 0, 0]); // true
Color.isColorLike({ r: 1, g: 0, b: 0 }); // true
Color.isColorLike({ foo: 1 }); // false
Color.isColorLike(null); // false
```

`Color.isColorLike()` 检查结构形状（字符串、数字、数组或识别的对象）。它不会验证字符串是否是真实的 CSS 颜色名称，也不会验证数组值是否在范围内。在将用户输入传递给 `new Color()` 或 `setValue()` 之前使用它作为类型保护。

## 常见错误

### [MEDIUM] 期望 `toRgba()` 返回 0-255 值

错误：

```ts
import { Color } from "pixi.js";

const { r, g, b } = new Color({ r: 255, g: 128, b: 0 }).toRgba();
// r = 1, g = ~0.502, b = 0 (NOT 255, 128, 0)
```

正确：

```ts
import { Color } from "pixi.js";

// 使用 toUint8RgbArray() 获取 0-255 输出
const [r, g, b] = new Color({ r: 255, g: 128, b: 0 }).toUint8RgbArray();
// r = 255, g = 128, b = 0
```

RGB 对象输入使用 0-255 范围 (`{ r: 255, g: 0, b: 0 }`)，但所有输出方法 (`toRgba()`, `toRgb()`, `toArray()`, `toRgbArray()`) 归一化到 0-1。当您需要 0-255 整数用于 CSS 或外部 API 时，使用 `toUint8RgbArray()`。

### [MEDIUM] 在颜色数组中使用 0-255 范围

错误：

```ts
import { Color } from "pixi.js";

new Color([255, 0, 0]); // NOT red; 值被解释为 0-1
```

正确：

```ts
import { Color } from "pixi.js";

new Color([1, 0, 0]); // red via 归一化数组
new Color(0xff0000); // red via 十六进制
new Color("red"); // red via CSS 名称
new Color(new Uint8Array([255, 0, 0])); // red via Uint8Array (0-255)
```

普通数字数组 (`number[]` 和 `Float32Array`) 使用归一化 0-1 范围。`[255, 0, 0]` 被裁剪为 `[1, 0, 0]`，因为值被裁剪，但 `[200, 100, 50]` 不会产生预期的颜色。使用 `Uint8Array` 或 `Uint8ClampedArray` 进行 0-255 输入。

### [MEDIUM] 使用 `utils.string2hex` 或 `utils.hex2string`

错误：

```ts
import { utils } from "pixi.js";

const hex = utils.string2hex("#ff0000");
```

正确：

```ts
import { Color } from "pixi.js";

const hex = new Color("#ff0000").toNumber();
const str = new Color(0xff0000).toHex();
```

`utils` 命名空间在 v8 中已移除。使用 `Color` 类进行所有颜色转换。
