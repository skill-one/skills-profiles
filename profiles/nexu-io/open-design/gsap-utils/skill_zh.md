# gsap.utils

> 从 GreenSock 官方 GSAP 技能库中精选：https://github.com/greensock/gsap-skills

## 何时使用此技能

在编写或审查使用 **gsap.utils** 进行数学计算、数组/集合处理、单位解析或动画中值映射的代码时使用（例如，将滚动映射到值、随机化、对齐到网格或归一化输入）。

**相关技能**：在构建动画时与 **gsap-core**、**gsap-timeline** 和 **gsap-scrolltrigger** 结合使用；CustomEase 和其他缓动工具位于 **gsap-plugins** 中。

## 概述

**gsap.utils** 提供纯辅助函数，无需注册。用于缓动变量（例如基于函数的值）、ScrollTrigger 或 Observer 回调中，或任何驱动 GSAP 的 JavaScript 代码。所有这些都位于 **gsap.utils** 上（例如 `gsap.utils.clamp()`）。

**省略值：函数形式**。许多辅助函数将转换的值作为最后一个参数接受。如果你省略该参数，该辅助函数将返回一个函数，稍后接受该值。当你需要使用相同的配置多次钳位、映射、归一化或对齐多个值时（例如，在鼠标移动处理程序或缓动回调中）使用该函数形式。**例外：random()** — 将 **true** 作为最后一个参数传递以获取可重用的函数（不要省略值）；请参阅 [random()](https://gsap.com/docs/v3/GSAP/UtilityMethods/random())。

```javascript
// 带有值：返回结果
gsap.utils.clamp(0, 100, 150); // 100

// 没有值：返回稍后调用该值的函数
let c = gsap.utils.clamp(0, 100);
c(150);  // 100
c(-10);  // 0
```

## 钳位和范围

### clamp(min, max, value?)

将值限制在 min 和 max 之间。省略 **value** 以获取函数：`clamp(min, max)(value)`。

```javascript
gsap.utils.clamp(0, 100, 150); // 100
gsap.utils.clamp(0, 100, -10); // 0

let clampFn = gsap.utils.clamp(0, 100);
clampFn(150); // 100
```

### mapRange(inMin, inMax, outMin, outMax, value?)

将一个值从一个范围映射到另一个范围。在将滚动位置、进度（0–1）或输入范围转换为动画范围时使用。省略 **value** 以获取函数：`mapRange(inMin, inMax, outMin, outMax)(value)`。

```javascript
gsap.utils.mapRange(0, 100, 0, 500, 50);  // 250
gsap.utils.mapRange(0, 1, 0, 360, 0.5);   // 180 (进度转换为度数)

let mapFn = gsap.utils.mapRange(0, 100, 0, 500);
mapFn(50);  // 250
```

### normalize(min, max, value?)

返回给定范围内的值归一化为 0–1。当目标范围是 0–1 时，这是映射的逆操作。省略 **value** 以获取函数：`normalize(min, max)(value)`。

```javascript
gsap.utils.normalize(0, 100, 50);   // 0.5
gsap.utils.normalize(100, 300, 200); // 0.5

let normFn = gsap.utils.normalize(0, 100);
normFn(50); // 0.5
```

### interpolate(start, end, progress?)

在给定的进度（0–1）处，在两个值之间进行插值。处理数字、颜色和具有匹配键的对象。省略 **progress** 以获取函数：`interpolate(start, end)(progress)`。

```javascript
gsap.utils.interpolate(0, 100, 0.5);       // 50
gsap.utils.interpolate("#ff0000", "#0000ff", 0.5); // 中间颜色
gsap.utils.interpolate({ x: 0, y: 0 }, { x: 100, y: 50 }, 0.5); // { x: 50, y: 25 }

let lerp = gsap.utils.interpolate(0, 100);
lerp(0.5); // 50
```

## 随机和对齐

### random(minimum, maximum[, snapIncrement, returnFunction]) / random(array[, returnFunction])

返回范围内的随机数 **minimum**–**maximum**，或来自 **array** 的随机元素。可选的 **snapIncrement** 将结果对齐到最近的倍数（例如 `5` → 5 的倍数）。**要获取可重用的函数**，将 **true** 作为最后一个参数传递（**returnFunction**）；返回的函数不接受任何参数，每次调用时返回一个新的随机值。这是唯一使用 `true` 作为函数形式而不是省略值的辅助函数。

```javascript
// 立即值：范围内的数字
gsap.utils.random(-100, 100);        // 例如 42.7
gsap.utils.random(0, 500, 5);        // 0–500，对齐到最近的 5

// 可重用的函数：将 true 作为最后一个参数传递
let randomFn = gsap.utils.random(-200, 500, 10, true);
randomFn();  // 范围内的随机值，对齐到 10
randomFn();  // 另一个随机值

// 数组：随机选择一个值
gsap.utils.random(["red", "blue", "green"]);  // "red", "blue", 或 "green"
let randomFromArray = gsap.utils.random([0, 100, 200], true);
randomFromArray();  // 0, 100, 或 200
```

**缓动变量中的字符串形式**：使用 `"random(-100, 100)"`、`"random(-100, 100, 5)"` 或 `"random([0, 100, 200])"`；GSAP 将针对每个目标进行评估。

```javascript
gsap.to(".box", { x: "random(-100, 100, 5)", duration: 1 });
gsap.to(".item", { backgroundColor: "random([red, blue, green])" });
```

### snap(snapTo, value?)

将值对齐到 **snapTo** 的最近倍数，或对齐到允许值数组中的最近值。省略 **value** 以获取函数：`snap(snapTo)(value)`（或 `snap(snapArray)(value)`）。

```javascript
gsap.utils.snap(10, 23);     // 20
gsap.utils.snap(0.25, 0.7);  // 0.75
gsap.utils.snap([0, 100, 200], 150); // 100 或 200（数组中的最近值）

let snapFn = gsap.utils.snap(10);
snapFn(23); // 20
```

在缓动中使用，用于网格或步进动画：

```javascript
gsap.to(".x", { x: 200, snap: { x: 20 } });
```

### shuffle(array)

返回一个具有相同元素但顺序随机的新数组。用于随机化顺序（例如，与 "random" 结合使用 stagger）。

```javascript
gsap.utils.shuffle([1, 2, 3, 4]); // 例如 [3, 1, 4, 2]
```

### distribute(config)

**返回一个函数**，根据其在数组（或网格）中的位置为每个目标分配值。内部用于高级 stagger；在您需要将值分布在许多元素上时使用（例如，缩放、不透明度、x、延迟）。返回的函数接收 `(index, target, targets)` — 可以手动调用它，或将结果直接传递到缓动中；GSAP 将针对每个目标使用索引、元素和数组进行调用。

**配置（所有可选）**：

| 属性 | 类型 | 描述 |
|------|------|------|
| `base` | Number | 起始值。默认 `0`。 |
| `amount` | Number | 在所有目标之间分配的总值（加到 base 上）。例如 `amount: 1` 与 100 个目标 → 每个之间 0.01。使用 **each** 而不是设置每个目标的固定步长。 |
| `each` | Number | 在每个目标之间添加的量（加到 base 上）。例如 `each: 1` 与 4 个目标 → 0, 1, 2, 3。使用 **amount** 而不是分配总数。 |
| `from` | Number \| String \| Array | 分配的起始位置：索引，或 `"start"`、`"center"`、`"edges"`、`"random"`、`"end"`，或比率如 `[0.25, 0.75]`。默认 `0`。 |
| `grid` | String \| Array | 使用网格位置而不是扁平索引：`[rows, columns]`（例如 `[5, 10]`）或 `"auto"` 以检测。省略以用于扁平数组。 |
| `axis` | String | 对于网格：限制到一个轴（`"x"` 或 `"y"`）。 |
| `ease` | Ease | 沿缓动曲线分配值（例如 `"power1.inOut"`）。默认 `"none"`。 |

**在缓动中**：将 `distribute(config)` 的结果作为属性值传递；GSAP 将针对每个目标使用 `(index, target, targets)` 进行调用。

```javascript
// 缩放：中间元素 0.5，外边缘 3（从中心分配 2.5）
gsap.to(".class", {
  scale: gsap.utils.distribute({
    base: 0.5,
    amount: 2.5,
    from: "center"
  })
});
```

**手动使用**：使用 `(index, target, targets)` 调用返回的函数以获取该索引的值。

```javascript
const distributor = gsap.utils.distribute({
  base: 50,
  amount: 100,
  from: "center",
  ease: "power1.inOut"
});
const targets = gsap.utils.toArray(".box");
const valueForIndex2 = distributor(2, targets[2], targets);
```

更多内容请参阅 [distribute()](https://gsap.com/docs/v3/GSAP/UtilityMethods/distribute/)。

## 单位和解析

### getUnit(value)

返回值的单位字符串（例如 `"px"`、`"%"`、`"deg"`）。在归一化或转换值时使用。

```javascript
gsap.utils.getUnit("100px");   // "px"
gsap.utils.getUnit("50%");     // "%"
gsap.utils.getUnit(42);        // ""（无单位）
```

### unitize(value, unit)

为数字附加单位，或如果它已经具有单位则返回该值。在构建 CSS 值或缓动结束值时使用。

```javascript
gsap.utils.unitize(100, "px");  // "100px"
gsap.utils.unitize("2rem", "px"); // "2rem"（未更改）
```

### splitColor(color, returnHSL?)

将颜色字符串转换为数组：**[red, green, blue]**（0–255），或 **[red, green, blue, alpha]**（4 个元素，当 alpha 存在或需要时为 RGBA）。将 **true** 作为第二个参数（**returnHSL**）传递以获取 **[hue, saturation, lightness]** 或 **[hue, saturation, lightness, alpha]**（HSL/HSLA）而不是。适用于 `"rgb()"`、`"rgba()"`、`"hsl()"`、`"hsla()"`、十六进制和命名颜色（例如 `"red"`）。在动画颜色组件或构建渐变时使用。请参阅 [splitColor()](https://gsap.com/docs/v3/GSAP/UtilityMethods/splitColor/)。

```javascript
gsap.utils.splitColor("red");                    // [255, 0, 0]
gsap.utils.splitColor("#6fb936");                // [111, 185, 54]
gsap.utils.splitColor("rgba(204, 153, 51, 0.5)"; // [204, 153, 51, 0.5]（4 个元素）
gsap.utils.splitColor("#6fb936", true);          // [94, 55, 47]（HSL：色调、饱和度、亮度）
```

## 数组和集合

### selector(scope)

返回一个作用域选择器函数，该函数仅在给定元素（或 ref）内查找元素。在组件中使用，以便像 `".box"` 这样的选择器仅匹配该组件的子元素，而不是整个文档。接受 DOM 元素或 ref（例如 React ref；处理 `.current`）。

```javascript
const q = gsap.utils.selector(containerRef);
q(".box");        // 容器内 .box 元素的数组
gsap.to(q(".circle"), { x: 100 });
```

### toArray(value, scope?)

将值转换为数组：作用域到元素的选择器字符串、NodeList、HTMLCollection、单个元素或数组。在将混合输入传递给 GSAP（例如目标）并需要真实数组时使用。

```javascript
gsap.utils.toArray(".item");           // 元素的数组
gsap.utils.toArray(".item", container); // 作用域到容器
gsap.utils.toArray(nodeList);          // NodeList 的 [ ... ]
```

### pipe(...functions)

组合函数：**pipe(f1, f2, f3)(value)** 返回 f3(f2(f1(value)))。在缓动或回调中应用一系列转换（例如，归一化 → mapRange → snap）时使用。

```javascript
const fn = gsap.utils.pipe(
  (v) => gsap.utils.normalize(0, 100, v),
  (v) => gsap.utils.snap(0.1, v)
);
fn(50); // 归一化然后对齐
```

### wrap(min, max, value?)

将值包装到 min–max 范围内（包含 min，不包含 max）。用于无限滚动或循环值。省略 **value** 以获取函数：`wrap(min, max)(value)`。

```javascript
gsap.utils.wrap(0, 360, 370);  // 10
gsap.utils.wrap(0, 360, -10);   // 350

let wrapFn = gsap.utils.wrap(0, 360);
wrapFn(370); // 10
```

### wrapYoyo(min, max, value?)

在范围内包装值，并在两端反弹。用于在范围内来回移动。省略 **value** 以获取函数：`wrapYoyo(min, max)(value)`。

```javascript
gsap.utils.wrapYoyo(0, 100, 150); // 50（反弹回）
let wrapY = gsap.utils.wrapYoyo(0, 100);
wrapY(150); // 50
```

## 最佳实践

- ✅ 当多次使用相同的范围/配置时，省略值参数以获取可重用的函数（例如滚动处理程序、缓动回调）：`let mapFn = gsap.utils.mapRange(0, 1, 0, 360); mapFn(progress)`。
- ✅ 使用 **snap** 进行网格对齐或步进值；使用 **toArray** 当 GSAP 或您的代码需要从选择器或 NodeList 获取真实数组时。
- ✅ 在组件中使用 **gsap.utils.selector(scope)**，以便选择器作用域到容器或 ref。

## 不要

- ❌ 假设 **mapRange** / **normalize** 处理单位；它们在数字上工作。当单位重要时，使用 **getUnit** / **unitize**。
- ❌ 试图覆盖或依赖未记录的行为；坚持记录的 API。

### 更多学习

https://gsap.com/docs/v3/HelperFunctions
