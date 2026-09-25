PixiJS 提供了五种文本渲染类，它们在样式、性能和动画之间提供了不同的权衡。`Text` 渲染到画布上以实现完整的 CSS 风格保真度。`BitmapText` 从预生成的图集读取以实现廉价的更新。`HTMLText` 通过 SVG `<foreignObject>` 渲染 HTML 片段以支持丰富的标记。`SplitText` 和 `SplitBitmapText` 包装了前两个类，并暴露了按字符、按单词和按行的容器以用于动画。

假设熟悉 `pixijs-scene-core-concepts`。所有文本类都是叶节点；它们不能有子节点。将多个文本实例包装在 `Container` 中以将它们分组。

## 快速入门

```ts
const text = new Text({
  text: "Hello PixiJS",
  style: {
    fontFamily: "Arial",
    fontSize: 36,
    fill: 0xffffff,
    stroke: { color: 0x4a1850, width: 5 },
    dropShadow: { color: 0x000000, blur: 4, distance: 6 },
  },
});

text.anchor.set(0.5);
text.x = app.screen.width / 2;
text.y = 40;

app.stage.addChild(text);
```

所有文本类都使用选项对象构造器；v7 中的位置 `(string, style)` 形式不再支持。

**相关技能：** `pixijs-scene-core-concepts` (叶节点、变换), `pixijs-assets` (字体加载), `pixijs-performance` (BitmapText 权衡), `pixijs-color` (`FillInput` 用于填充/描边), `pixijs-scene-graphics` (通过 `FillInput` 重用渐变和图案)。

## 变体

| 变体           | 使用场景                                                           | 权衡                                                            | 参考                                                          |
| -------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `Text`         | 高质量静态或更新频率较低的标签                                    | 更新成本高 (画布重绘 + GPU 上传)                                 | [references/text.md](references/text.md)                           |
| `BitmapText`   | 分数、计时器、游戏标签、任何每帧变化的元素                         | 样式有限；固定字形图集；需要 MSDF 以实现清晰缩放                 | [references/bitmap-text.md](references/bitmap-text.md)             |
| `HTMLText`     | 丰富格式化的文本、混合样式、真实的 HTML 标签                      | 异步渲染 (一帧延迟)；与 `Text` 相似的更新成本                  | [references/html-text.md](references/html-text.md)                 |
| `SplitText`    | 按字符进行动画且样式丰富的文本                                      | 每个字符都是一个完整的 `Text`；长字符串成本高                    | [references/split-text.md](references/split-text.md)               |
| `SplitBitmapText` | 长字符串或动态内容上的按字符动画                                  | 继承 BitmapText 的限制 (字形图集，无 MSDF 的清晰度)             | [references/split-bitmap-text.md](references/split-bitmap-text.md) |

## 何时使用什么

- **"我需要一个带样式的静态标签"** → `Text`。用于标题、菜单、对话框、错误消息。参见 `references/text.md`。
- **"我需要一个每帧更新的分数或计时器"** → `BitmapText`。仅重新定位四边形；不进行画布重绘。参见 `references/bitmap-text.md`。
- **"我需要混合格式，如 `<b>`、`<i>`、`<br>`"** → `HTMLText`。通过 SVG 进行真实的 HTML/CSS 渲染。参见 `references/html-text.md`。
- **"我需要像 `<red>Warning:</red>` 这样的内联彩色标签"** → `Text` 或 `HTMLText` 配合 `tagStyles`。两者都支持。
- **"我需要单独动画每个字符"** → 短字符串使用 `SplitText`，长字符串或多个实例使用 `SplitBitmapText`。参见 `references/split-text.md` / `references/split-bitmap-text.md`。
- **"我需要 CJK / 阿拉伯 / 表情丰富的文本"** → `Text` 或 `HTMLText`。`BitmapText` 失败，因为单个图集的字形集太大。
- **"我需要自定义字体"** → 首先通过 `Assets.load({ src: 'font.woff2', data: { family: 'MyFont' } })` 加载，然后设置 `style.fontFamily: 'MyFont'`。适用于 `Text` 和 `HTMLText`。

## 更新成本比较

| 更新触发      | Text | BitmapText | HTMLText | SplitText                     | SplitBitmapText          |
| ------------- | ---- | ---------- | -------- | ----------------------------- | ------------------------ |
| 更改 `.text`  | 高   | 非常低     | 高       | 非常高 (N 个文本重新渲染)     | 低 (N 个四边形重新定位) |
| 更改 `.style` | 高   | 中等       | 高       | 非常高                       | 中等                   |
| 移动 (`.x`, `.y`) | 免费 | 免费       | 免费     | 免费                          | 免费                     |
| 旋转 / 缩放  | 免费 | 免费       | 免费     | 免费                          | 免费                     |

"免费" = 普通容器变换成本。"高" = 新画布绘制 + GPU 上传。"非常低" = 仅四边形重新定位。仅对 `BitmapText` 或 `SplitBitmapText` 更新每帧变化的字符串。

## 快速概念

- **选项对象构造器。** 每个 v8 文本类使用 `new Text({ text, style, ... })`。v7 的 `(string, style)` 形式已移除。
- **`tagStyles`。** `Text` 和 `HTMLText` 通过 `style.tagStyles` 支持按标签样式。只有当 `tagStyles` 有条目时才会解析标签；否则 `<` 被视为字面量。
- **`BitmapFont.install`。** 在创建任何 `BitmapText` 之前预先生成图集。未安装时，第一个具有新 `fontFamily` 的 `BitmapText` 懒加载生成图集。
- **MSDF 字体。** 多通道符号距离场字体在任何大小下都保持清晰。使用外部工具 (例如 msdf-bmfont) 生成，通过 `Assets.load('font.fnt')` 加载。自定义构建中需要 `import 'pixi.js/text-bitmap'`。

## 常见错误

### [高] 每帧更新 `Text.text`

错误：

```ts
app.ticker.add(() => {
  scoreText.text = `Score: ${score}`;
});
```

正确：

```ts
const scoreText = new BitmapText({ text: "Score: 0", style });
app.ticker.add(() => {
  scoreText.text = `Score: ${score}`;
});
```

每次 `Text` 更新都会重新光栅化整个字符串。使用 `BitmapText` 对任何每帧变化的值。

### [高] 位置构造器参数

错误：

```ts
const text = new Text("Hello", { fontSize: 24 });
```

正确：

```ts
const text = new Text({ text: "Hello", style: { fontSize: 24 } });
```

v8 移除了 `(string, style)` 形式。所有文本类使用选项对象。

### [高] 自定义构建中未导入 `pixi.js/text-bitmap`

在 `skipExtensionImports: true` 或激进树形摇动下，`Assets.load('font.fnt')` 默默返回原始数据，除非你添加 `import 'pixi.js/text-bitmap'`。标准的 `import { ... } from 'pixi.js'` 打包包含扩展。

### [中] 向文本实例添加子节点

每个文本类设置 `allowChildren = false`。将它们包装在 `Container` 中以将文本与其他内容分组。

## API 参考

- [Text](https://pixijs.download/release/docs/scene.Text.html.md)
- [TextStyle](https://pixijs.download/release/docs/text.TextStyle.html.md)
- [BitmapText](https://pixijs.download/release/docs/scene.BitmapText.html.md)
- [BitmapFont](https://pixijs.download/release/docs/text.BitmapFont.html.md)
- [HTMLText](https://pixijs.download/release/docs/scene.HTMLText.html.md)
- [HTMLTextStyle](https://pixijs.download/release/docs/text.HTMLTextStyle.html.md)
- [SplitText](https://pixijs.download/release/docs/text.SplitText.html.md)
- [SplitBitmapText](https://pixijs.download/release/docs/text.SplitBitmapText.html.md)
- [AbstractSplitText](https://pixijs.download/release/docs/text.AbstractSplitText.html.md)
- [AbstractText](https://pixijs.download/release/docs/scene.AbstractText.html.md)
