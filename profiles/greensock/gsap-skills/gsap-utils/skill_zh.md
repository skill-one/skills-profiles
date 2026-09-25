# gsap.utils

## 何时使用此技能

在编写或审查使用 **gsap.utils** 进行动画中的数学、数组/集合处理、单位解析或值映射时应用（例如，将滚动映射为某个值、随机化、吸附到网格或归一化输入等）。

**相关技能：** 构建动画时结合使用 **gsap-core**、**gsap-timeline** 和 **gsap-scrolltrigger**；CustomEase 和其他缓动工具位于 **gsap-plugins** 中。

## 概述

**gsap.utils** 提供纯辅助函数；无需进行注册。在补间变量（例如基于函数的数值）、ScrollTrigger 或 Observer 回调中，或任何驱动 GSAP 的 JavaScript 中使用。所有函数均在 **gsap.utils** 上（例如 `gsap.utils.clamp()`）。

**省略值：函数形式。** 许多辅助函数将待转换的值作为**最后一个**参数接受。如果你省略该参数，则该辅助函数会返回一个稍后接受值的**函数**。当你需要以相同配置对多个值进行限制（clamp）、映射、归一化或吸附（snap）时，请使用函数形式（例如，在鼠标移动处理器或补间回调中使用）。**例外：random()** — 作为最后一个参数传递 **true** 以获取可重复使用的函数（不要省略值）；详见 [random()](https://gsap.com/docs/v3/GSAP/UtilityMethods/random()).

```javascript
// 包含值：返回结果
gsap.utils.clamp(0, 100, 150); // 100

// 不包含值：返回稍后调用值即可的函数
let c = gsap.utils.clamp(0, 100);
c(150);  // 100
c(-10);  // 0
```

## 限制与范围

### clamp(min, max, value?)

将一个值限制在 min 和 max 之间。省略 **value** 以获取函数：`clamp(min, max)(value)`。

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
gsap.utils.mapRange(0, 1, 0, 360, 0.5);   // 180（将进度转换为角度）

let mapFn = gsap.utils.mapRange(0, 100, 0, 500);
mapFn(50);  // 250
```

### normalize(min, max, value?)

返回针对给定范围归一化到 0–1 的值。当目标范围为 0–1 时，是映射的逆运算。省略 **value** 以获取函数：`normalize(min, max)(value)`。

```javascript
gsap.utils.normalize(0, 100, 50);   // 0.5
gsap.utils.normalize(100, 300, 200); // 0.5

let normFn = gsap.utils.normalize(0, 100);
normFn(50); // 0.5
```

### interpolate(start, end, progress?)

在给定进度（0–1）下对两个值进行插值。支持数字、颜色和具有匹配键的对象。省略 **progress** 以获取函数：`interpolate(start, end)(progress)`。

```javascript
gsap.utils.interpolate(0, 100, 0.5);       // 50
gsap.utils.interpolate("#ff0000", "#0000ff", 0.5); // 中间颜色
gsap.utils.interpolate({ x: 0, y: 0 }, { x: 100, y: 50 }, 0.5); // { x: 50, y: 25 }

let lerp = gsap.utils.interpolate(0, 100);
lerp(0.5); // 50
```

## 随机与吸附

### random(minimum, maximum[, snapIncrement, returnFunction]) / random(array[, returnFunction])

返回 **minimum**–**maximum** 范围内的随机数字，或数组中的随机元素。可选 **snapIncrement** 将结果吸附到最近的倍数（例如 `5` → 5 的倍数）。**获取可重复使用的函数**：作为最后一个参数传递 **true**（**returnFunction**）；返回的函数不接受参数，每次调用都返回新的随机值。这是唯一使用 `true` 表示函数形式而非省略值的辅助函数。

```javascript
// 立即获取值：范围内的数字
gsap.utils.random(-100, 100);        // 例如 42.7
gsap.utils.random(0, 500, 5);        // 0–500，吸附到最近的 5

// 可重复使用函数：作为最后一个参数传递 true
let randomFn = gsap.utils.random(-200, 500, 10, true);
randomFn();  // 范围内的随机值，吸附到 10
randomFn();  // 另一个随机值

// 数组：随机选择一个值
gsap.utils.random(["red", "blue", "green"]);  // "red", "blue" 或 "green"
let randomFromArray = gsap.utils.random([0, 100, 200], true);
randomFromArray();  // 0, 100 或 200
```

**补间变量中的字符串形式：** 使用 `"random(-100, 100)"`、`"random(-100, 100, 5)"` 或 `"random([0, 100, 200])"`；GSAP 为每个目标进行评估。

```javascript
gsap.to(".box", { x: "random(-100, 100, 5)", duration: 1 });
gsap.to(".item", { backgroundColor: "random([red, blue, green])" });
```

### snap(snapTo, value?)

将一个值吸附到 **snapTo** 的最近倍数，或吸附到允许值数组的最近值。省略 **value** 以获取函数：`snap(snapTo)(value)`（或 `snap(snapArray)(value)`）。

```javascript
gsap.utils.snap(10, 23);     // 20
gsap.utils.snap(0.25, 0.7);  // 0.75
gsap.utils.snap([0, 100, 200], 150); // 100 或 200（数组中的最近值）

let snapFn = gsap.utils.snap(10);
snapFn(23); // 20
```

在补间动画中进行网格或基于步骤的动画时使用：

```javascript
gsap.to(".x", { x: 200, snap: { x: 20 } });
```

### shuffle(array)

返回元素顺序随机但相同的数组。用于随机化顺序（例如，与副本一起从 "random" 进行错位）。

```javascript
gsap.utils.shuffle([1, 2, 3, 4]); // 例如 [3, 1, 4, 2]
```

### distribute(config)

**返回一个函数**，根据每个目标在数组（或网格）中的位置为其分配一个值。内部用于高级错位（stagger）；当你需要将值分散到许多元素（例如 scale、opacity、x、delay）上时，请使用它。返回的函数接收 `(index, target, targets)` — 可以直接手动调用，或将结果直接传入补间动画；GSAP 会为每个目标调用该函数，并传入索引、元素和数组。

**配置（均可选）：**

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `base` | 数字 | 起始值。默认为 `0`。 |
| `amount` | 数字 | 在所有目标上分布的总量（添加到 base）。例如，`amount: 1` 配合 100 个目标 → 每个目标之间 0.01。请使用 **each** 来为每个目标设置固定步长。 |
| `each` | 数字 | 在每两个目标之间添加的量（添加到 base）。例如，`each: 1` 配合 4 个目标 → 0, 1, 2, 3。请使用 **amount** 来分配总量。 |
| `from` | 数字 \| 字符串 \| 数组 | 分布起始位置：索引，或 `"start"`、`"center"`、`"edges"`、`"random"`、`"end"`，或类似 `[0.25, 0.75]` 的比例。默认为 `0`。 |
| `grid` | 字符串 \| 数组 | 使用网格位置而非扁平索引：`[行数, 列数]`（例如 `[5, 10]`）或 `"auto"` 以自动检测。省略则使用扁平数组。 |
| `axis` | 字符串 | 针对网格：限制为单个轴（`"x"` 或 `"y"`）。 |
| `ease` | 缓动 | 沿缓动曲线分布值（例如 `"power1.inOut"`）。默认为 `"none"`。 |

**在补间动画中：** 将 `distribute(config)` 的结果作为属性值传递；GSAP 会为每个目标以 `(index, target, targets)` 调用该函数。

```javascript
// Scale：中间元素 0.5，外边缘 3（从中心分布 amount 2.5）
gsap.to(".class", {
  scale: gsap.utils.distribute({
    base: 0.5,
    amount: 2.5,
    from: "center"
  })
});
```

**手动使用：** 使用 `(index, target, targets)` 调用返回的函数，即可获取该索引对应的值。

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

详见 [distribute()](https://gsap.com/docs/v3/GSAP/UtilityMethods/distribute/)。

## 单位与解析

### getUnit(value)

返回值的单位字符串（例如 `"px"`、`"%"`、`"deg"`）。在归一化或转换值时使用。

```javascript
gsap.utils.getUnit("100px");   // "px"
gsap.utils.getUnit("50%");     // "%"
gsap.utils.getUnit(42);        // ""（无单位）
```

### unitize(value, unit)

为数字添加单位，如果值已包含单位，则原样返回。在构建 CSS 值或补间结束值时使用。

```javascript
gsap.utils.unitize(100, "px");  // "100px"
gsap.utils.unitize("2rem", "px"); // "2rem"（不变）
```

### splitColor(color, returnHSL?)

将颜色字符串转换为数组：**[red, green, blue]**（0–255），或 **[red, green, blue, alpha]**（当存在 alpha 或需要时，RGBA 为 4 个元素）。作为第二个参数传递 **true**（**returnHSL**）以获取 **[hue, saturation, lightness]** 或 **[hue, saturation, lightness, alpha]**（HSL/HSLA）。支持 `"rgb()"`、`"rgba()"`、`"hsl()"`、`"hsla()"`、十六进制和命名颜色（例如 `"red"`）。用于动画颜色组件或构建渐变时使用。详见 [splitColor()](https://gsap.com/docs/v3/GSAP/UtilityMethods/splitColor/)。

```javascript
gsap.utils.splitColor("red");                    // [255, 0, 0]
gsap.utils.splitColor("#6fb936");                // [111, 185, 54]
gsap.utils.splitColor("rgba(204, 153, 51, 0.5)"); // [204, 153, 51, 0.5]（4 个元素）
gsap.utils.splitColor("#6fb936", true);          // [94, 55, 47]（HSL：色相、饱和度、亮度）
```

## 数组与集合

### selector(scope)

返回一个作用域选择器函数，仅查找给定元素（或 ref）内的元素。在组件中使用，以便像 `".box"` 这样的选择器仅匹配该组件的后代元素，而非整个文档。接受 DOM 元素或 ref（例如 React ref；处理 `.current`）。

```javascript
const q = gsap.utils.selector(containerRef);
q(".box");        // 容器内 .box 元素数组
gsap.to(q(".circle"), { x: 100 });
```

### toArray(value, scope?)

将值转换为数组：选择器字符串（限制在元素范围内）、NodeList、HTMLCollection、单个元素或数组。当需要将混合输入传递给 GSAP（例如目标元素）且需要真正的数组时使用。

```javascript
gsap.utils.toArray(".item");           // 元素数组
gsap.utils.toArray(".item", container); // 限制在容器范围内
gsap.utils.toArray(nodeList);          // 从 NodeList 获取 [ ... ]
```

### pipe(...functions)

组合函数：**pipe(f1, f2, f3)(value)** 返回 f3(f2(f1(value)))。在补间动画或回调中应用变换链（例如 normalize → mapRange → snap）时使用。

```javascript
const fn = gsap.utils.pipe(
  (v) => gsap.utils.normalize(0, 100, v),
  (v) => gsap.utils.snap(0.1, v)
);
fn(50); // 先归一化，再吸附
```

### wrap(min, max, value?)

将值限制在 min–max 范围（包含 min，不含 max）内。用于无限滚动或循环值。省略 **value** 以获取函数：`wrap(min, max)(value)`。

```javascript
gsap.utils.wrap(0, 360, 370);  // 10
gsap.utils.wrap(0, 360, -10);   // 350

let wrapFn = gsap.utils.wrap(0, 360);
wrapFn(370); // 10
```

### wrapYoyo(min, max, value?)

将值带 yoyo（端点反弹）限制在范围内。用于在范围内来回动画。省略 **value** 以获取函数：`wrapYoyo(min, max)(value)`。

```javascript
gsap.utils.wrapYoyo(0, 100, 150); // 50（反弹返回）

let wrapY = gsap.utils.wrapYoyo(0, 100);
wrapY(150); // 50
```

## 最佳实践

- ✅ 当相同范围/配置多次使用（例如滚动处理器、补间回调）时，省略值参数以获取可重复使用的函数：`let mapFn = gsap.utils.mapRange(0, 1, 0, 360); mapFn(progress)`。
- ✅ 为网格对齐或基于步骤的值使用 **snap**；当 GSAP 或你的代码需要从选择器或 NodeList 获取真正的数组时，使用 **toArray**。
- ✅ 在组件中使用 **gsap.utils.selector(scope)**，使选择器限定在容器或 ref 范围内。

## 禁止

- ❌ 假设 **mapRange** / **normalize** 处理单位；它们仅处理数字。当涉及单位时，使用 **getUnit** / **unitize**。
- ❌ 覆盖或依赖未记录的行为；遵循已记录的 API。

### 了解更多

https://gsap.com/docs/v3/HelperFunctions
