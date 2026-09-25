PixiJS 暴露了轻量级的数学原语（Point、Matrix、形状类），这些原语在整个库中用于变换、碰撞检测和坐标转换。导入 `pixi.js/math-extras` 以添加矢量运算（加法、点积、模量、反射）和矩形交集/并集辅助函数。

## 快速入门

```ts
const parent = new Container();
parent.position.set(100, 100);
parent.scale.set(2);
app.stage.addChild(parent);

const child = new Container();
child.position.set(50, 50);
parent.addChild(child);

const globalPt = child.toGlobal(new Point(0, 0));

const m = new Matrix()
  .translate(100, 50)
  .rotate(Math.PI / 4)
  .scale(2, 2);
const world = m.apply(new Point(10, 20));

const hitArea = new Rectangle(0, 0, 200, 100);
console.log(hitArea.contains(50, 50));
```

**相关技能：** `pixijs-scene-container`（变换属性）、`pixijs-events`（碰撞区域使用）、`pixijs-scene-core-concepts`（使用矩形进行剔除）。

## 核心模式

### Point 和 ObservablePoint

Point 是一个简单的 {x, y} 值类型。ObservablePoint 在 x 或 y 变化时触发回调；它由 Container 的 position、scale、pivot、origin 和 skew 内部使用。

```ts
import { Point } from "pixi.js";

const p = new Point(10, 20);
p.set(30, 40); // 同时设置
p.set(50); // x=50, y=50

const clone = p.clone();
console.log(p.equals(clone)); // true

p.copyFrom({ x: 1, y: 2 }); // 接受任何 PointData

// Point.shared：临时点，每次访问时重置为 (0,0)
const temp = Point.shared;
temp.set(100, 200);
// 不要存储 Point.shared 的引用
```

Container 属性如 `position`、`scale`、`pivot`、`origin` 和 `skew` 是 ObservablePoints。在它们上设置 `.x` 或 `.y` 会自动触发变换重新计算。

```ts
import { Container } from "pixi.js";

const obj = new Container();
obj.position.set(100, 200); // 触发观察者 -> 标记变换为脏
obj.position.x = 150; // 也触发观察者
```

### Matrix (2D仿射变换)

Matrix 表示一个 3x3 仿射变换：`| a c tx | b d ty | 0 0 1 |`。它支持平移、缩放、旋转、追加、前置、反转和解构。

```ts
import { Matrix, Point } from "pixi.js";

// 构建变换
const m = new Matrix()
  .translate(100, 50)
  .rotate(Math.PI / 4)
  .scale(2, 2);

// 变换一个点（局部空间 -> 父空间）
const local = new Point(10, 20);
const world = m.apply(local);

// 反变换（父空间 -> 局部空间）
const backToLocal = m.applyInverse(world);

// 合并矩阵
const a = new Matrix().translate(50, 0);
const b = new Matrix().rotate(Math.PI / 2);
a.append(b); // a = a * b

// 解构为位置/缩放/旋转/倾斜
const transform = {
  position: new Point(),
  scale: new Point(),
  pivot: new Point(),
  skew: new Point(),
  rotation: 0,
};
m.decompose(transform);
console.log(transform.rotation); // ~0.785 (PI/4)

// 一个镜像矩阵（一个轴翻转，轴仍然垂直）解构为
// 旋转 + 负缩放.x 和零倾斜。缩放.y 永远不会是负数：y 轴翻转会作为 scale.x = -1 加上半圈。无论如何，这些部分都会重建矩阵。
const mirrored = new Matrix().rotate(Math.PI / 6).scale(-1, 1);
mirrored.decompose(transform);
transform.scale.x; // -1
transform.skew.x; // 0

// 共享临时矩阵（每次访问时重置）
const temp = Matrix.shared;
// IDENTITY 是只读引用
const isDefault = m.equals(Matrix.IDENTITY);
```

### 通过 Container 进行坐标变换

Containers 提供 `toGlobal`、`toLocal` 和 `getGlobalPosition` 用于坐标转换。

```ts
import { Container, Point } from "pixi.js";

const parent = new Container();
parent.position.set(100, 100);
parent.scale.set(2);

const child = new Container();
child.position.set(50, 50);
parent.addChild(child);

// 局部点在 child 的空间 -> 全局（世界）空间
const globalPt = child.toGlobal(new Point(0, 0));
// globalPt = { x: 200, y: 200 } (100 + 50*2, 100 + 50*2)

// 全局点 -> child 的局部空间
const localPt = child.toLocal(new Point(200, 200));
// localPt = { x: 0, y: 0 }

// 在两个容器之间转换
const other = new Container();
other.position.set(300, 300);
const ptInOther = child.toLocal(new Point(10, 10), other);
```

### 形状和碰撞检测

Rectangle、Circle、Ellipse、Polygon、RoundedRectangle 和 Triangle 都实现了 `contains(x, y)` 用于点在形状内的测试，以及 `getBounds(out?)` 和 `strokeContains(x, y, width, alignment?)` (`Triangle` 忽略 `alignment` 并始终测试居中的笔触)。它们可以用作容器的 `hitArea` 以实现自定义交互区域。

```ts
import { Rectangle, Circle, Ellipse, Polygon, Container } from "pixi.js";

const rect = new Rectangle(0, 0, 200, 100);
rect.contains(50, 50); // true
rect.contains(300, 50); // false
rect.left; // 0
rect.right; // 200
rect.top; // 0
rect.bottom; // 100
rect.isEmpty(); // false (Rectangle.EMPTY 返回一个新的空矩形)

// 原生 Rectangle-to-Rectangle 方法（不需要 math-extras）
const other = new Rectangle(50, 50, 100, 100);
rect.containsRect(other); // true 如果 `other` 完全在 `rect` 内
rect.containsRect(new Rectangle(100, 0, 100, 100)); // true：一个齐平的右侧边缘计算在内
rect.containsRect(rect.clone()); // true：相同的矩形互相包含
rect.intersects(other); // 布尔值：它们是否重叠？
rect.intersects(other, matrix); // 变换 `other` 后是否重叠

// 笔触碰撞检测（alignment: 1 = 内部, 0.5 = 居中, 0 = 外部）
rect.strokeContains(0, 50, 4); // 如果 (0,50) 位于 4px 居中笔触上则为 true
const circle = new Circle(100, 100, 50);
circle.strokeContains(150, 100, 4, 1); // 内部对齐笔触检查
// 一个笔触延伸到形状的中心之外覆盖整个内部；没有空洞
new Ellipse(0, 0, 10, 10).strokeContains(0, 0, 40, 1); // true

// getBounds 对每个形状都有效（返回一个 Rectangle，接受一个 out 参数）
const bounds = circle.getBounds();
const reused = new Rectangle();
new Polygon([0, 0, 100, 0, 50, 100]).getBounds(reused);

// 用作交互的碰撞区域
const button = new Container();
button.hitArea = new Rectangle(0, 0, 200, 50);
button.eventMode = "static";
button.on("pointerdown", () => {
  /* 点击 */
});
```

不要混淆原生的 `Rectangle.intersects(other)`（返回 `boolean`）和 math-extras 的 `intersection(other)`（返回描述重叠区域的 `Rectangle`）。

### 矩形布局辅助函数

Rectangle 配备了在 UI/布局、边界聚合和像素对齐中广泛使用的可变辅助函数。所有函数都返回 `this` 以支持链式调用。

```ts
import { Rectangle } from "pixi.js";

const r = new Rectangle(10, 10, 100, 50);

r.pad(5); // 在所有边缘增长：x=5, y=5, w=110, h=60
r.pad(10, 4); // 分离水平和垂直填充
r.scale(2); // 将 x, y, width, height 乘以 2

// fit 将 `this` 缩小以适应另一个矩形（裁剪）
const viewport = new Rectangle(0, 0, 200, 200);
new Rectangle(150, 150, 200, 200).fit(viewport); // -> 150, 150, 50, 50

// enlarge 将 `this` 扩展以包含另一个矩形（边界聚合）
const total = new Rectangle();
items.forEach((item) =>
  total.enlarge(new Rectangle().copyFromBounds(item.getBounds())),
);

// ceil 对齐到像素网格（分辨率：1 = 整数像素，2 = 半像素）
new Rectangle(10.2, 10.6, 100.8, 100.4).ceil();

// 直接将 Container/Mesh 边界对象复制到 Rectangle
new Rectangle().copyFromBounds(container.getBounds());
```

### Polygon

Polygon 接受四种构造函数格式：一个扁平的数字数组、一个点状对象数组，或作为展开参数传递。

```ts
import { Polygon, Point } from "pixi.js";

new Polygon([0, 0, 100, 0, 50, 100]); // 扁平数字
new Polygon([new Point(0, 0), new Point(100, 0), new Point(50, 100)]); // PointData[]
new Polygon(0, 0, 100, 0, 50, 100); // 展开数字
new Polygon(new Point(0, 0), new Point(100, 0), new Point(50, 100)); // 展开点

const poly = new Polygon([0, 0, 100, 0, 100, 100, 0, 100]);
poly.points; // [0, 0, 100, 0, 100, 100, 0, 100] (可变扁平数组)
poly.closePath; // 默认为 true；false 产生一个开放的路径
poly.startX; // 0  - 第一个顶点
poly.lastX; // 0  - 最后一个顶点（lastY 用于 y）
poly.isClockwise(); // 鞋带法线测试（用于 SVG 穴检测）

// 多边形内多边形包含用于穴检测
const outer = new Polygon([0, 0, 100, 0, 100, 100, 0, 100]);
const hole = new Polygon([25, 25, 75, 25, 75, 75, 25, 75]);
outer.containsPolygon(hole); // true

// 笔触碰撞检测跟随绘制的笔触：alignment 1 = 内部, 0.5 = 居中,
// 0 = 外部，与绕行顺序无关
outer.strokeContains(-5, 50, 20); // true (居中笔触向外延伸 10px)
outer.strokeContains(-5, 50, 20, 1); // false (内部笔触保持内部)
outer.strokeContains(5, 50, 20, 0); // false (外部笔触保持外部)
```

### 常量

```ts
import { DEG_TO_RAD, RAD_TO_DEG, PI_2 } from "pixi.js";

const angle = 45 * DEG_TO_RAD; // 0.785...
const degrees = angle * RAD_TO_DEG; // 45
const fullCircle = PI_2; // Math.PI * 2
```

### 类型

- `PointData` - 最小的 `{x, y}` 接口，大多数 API 接受。在参数只需要读取坐标时使用它。
- `PointLike` - 扩展 `PointData`，带有 `set()`、`copyFrom()`、`copyTo()`、`equals()`。由 `Point` 和 `ObservablePoint` 实现。
- `Size` - `{ width, height }` 接口，由渲染器/画布 API 使用。
- `SHAPE_PRIMITIVE` - 字符串字面量联合：`'rectangle' | 'circle' | 'ellipse' | 'polygon' | 'roundedRectangle' | 'triangle'`。每个形状都暴露 `type`，因此您可以在不使用 `instanceof` 的情况下进行分支。

```ts
import type { PointData } from "pixi.js";

function distance(a: PointData, b: PointData): number {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}
```

### math-extras（副作用导入）

`import 'pixi.js/math-extras'` 通过原型扩展向 Point、ObservablePoint 和 Rectangle 添加方法。不包含在默认包中。

```ts
import "pixi.js/math-extras";
import { Point } from "pixi.js";
```

#### Point / ObservablePoint 矢量方法

所有方法都接受一个可选的 `out` 参数以避免分配。如果没有 `out`，将返回一个新的 Point。

```ts
const a = new Point(3, 4);
const b = new Point(1, 2);

// 算术
const sum = a.add(b); // Point(4, 6)
const diff = a.subtract(b); // Point(2, 2)
const prod = a.multiply(b); // Point(3, 8) - 元素逐个相乘
const scaled = a.multiplyScalar(2); // Point(6, 8)

// 点积和叉积
const dot = a.dot(b); // 11
const cross = a.cross(b); // 2 (3D 叉积的 z 分量)

// 长度
const len = a.magnitude(); // 5
const lenSq = a.magnitudeSquared(); // 25 (比较时更快)

// 归一化为单位向量
const unit = a.normalize(); // Point(0.6, 0.8)

// 投影和反射
const proj = a.project(b); // 将 a 投影到 b 上
const refl = a.reflect(new Point(0, 1)); // 关于法线反射

// 旋转
const rotated = a.rotate(Math.PI / 2); // 旋转 90 度

// 重用现有点以避免分配
const out = new Point();
a.add(b, out); // 结果写入 out
```

#### Rectangle 扩展方法

`containsRect` 和 `intersects` 是原生的 `Rectangle` 方法（见上文）。math-extras 添加了 `equals`、`intersection`（返回重叠矩形）和 `union`：

```ts
import "pixi.js/math-extras";
import { Rectangle } from "pixi.js";

const r1 = new Rectangle(0, 0, 100, 100);
const r2 = new Rectangle(50, 50, 100, 100);

r1.equals(r2); // false

const overlap = r1.intersection(r2); // Rectangle(50, 50, 50, 50)
const envelope = r1.union(r2); // Rectangle(0, 0, 150, 150)

// 可选的 out 参数
const out = new Rectangle();
r1.intersection(r2, out);
```

#### 几何实用函数

这些函数从 `pixi.js/math-extras` 导出，而不是主 `pixi.js` 入口。

```ts
import {
  floatEqual,
  lineIntersection,
  segmentIntersection,
} from "pixi.js/math-extras";
import { Point } from "pixi.js";

// 基于浮点数的比较（默认 epsilon：Number.EPSILON）
floatEqual(0.1 + 0.2, 0.3, 1e-10); // 合理的 epsilon 时为 true
floatEqual(1.0, 1.001, 0.01); // true (自定义 epsilon)

// 无界线段相交（如果平行，返回 {x: NaN, y: NaN}）
const hit = lineIntersection(
  new Point(0, 0),
  new Point(10, 10), // 线段 A
  new Point(10, 0),
  new Point(0, 10), // 线段 B
); // Point(5, 5)
if (isNaN(hit.x)) {
  /* 线段平行 */
}

// 有界线段相交（如果线段不相交，返回 {x: NaN, y: NaN}）
const segHit = segmentIntersection(
  new Point(0, 0),
  new Point(10, 10),
  new Point(10, 0),
  new Point(0, 10),
); // Point(5, 5)
if (isNaN(segHit.x)) {
  /* 线段不相交 */
}
```

## 常见错误

### HIGH：从 @pixi/math 导入

错误：

```ts
import { Point } from "@pixi/math";
```

正确：

```ts
import { Point } from "pixi.js";
```

v8 使用单个 `pixi.js` 包。所有子包如 `@pixi/math`、`@pixi/core` 等都被移除。

### MEDIUM：未触发观察者而修改 ObservablePoint

错误：

```ts
// 替换引用会丢失观察
let pos = container.position;
pos = new Point(100, 200); // container.position 未改变
```

正确：

```ts
// 原地修改以触发观察者
container.position.set(100, 200);
// 或
container.position.x = 100;
container.position.y = 200;
// 或从另一个点复制
container.position.copyFrom(new Point(100, 200));
```

Container 的 position、scale、pivot、origin 和 skew 是 ObservablePoints。在它们上设置 `.x` 或 `.y` 会触发容器的变换更新。重新赋值变量引用不会修改容器。始终通过 `.set()`、`.copyFrom()` 或原始对象的直接属性赋值来修改现有的 ObservablePoint。

### MEDIUM：未导入 math-extras 以使用扩展方法

错误：

```ts
import { Point } from "pixi.js";
const p = new Point(1, 2);
p.add(new Point(3, 4)); // TypeError: p.add is not a function
```

正确：

```ts
import "pixi.js/math-extras";
import { Point } from "pixi.js";
const p = new Point(1, 2);
const sum = p.add(new Point(3, 4)); // 可用
```

扩展数学工具（Point 上的 add、subtract、multiply、magnitude、normalize、dot、cross 等；形状上的交集方法）需要显式 `import 'pixi.js/math-extras'`。这些不包含在默认包中。

### MEDIUM：存储共享/临时对象的引用

错误：

```ts
const myPoint = Point.shared;
myPoint.set(100, 200);
// ... 之后 ...
console.log(myPoint.x); // 0 (每次访问时重置为 0)
```

正确：

```ts
const myPoint = new Point();
myPoint.copyFrom(Point.shared.set(100, 200));
// 或直接
const myPoint = new Point(100, 200);
```

`Point.shared` 和 `Matrix.shared` 每次访问时都会重置为零/单位矩阵。它们用于在单个表达式中进行一次性计算。永远不要存储它们的引用。
