# OKLCH 颜色

OKLCH 是一种感知均匀的颜色空间，其中数值实际上与你认为它们代表的意思一致。CSS 中的大多数颜色问题——如调色板损坏、对比度失败、色相漂移——都源于使用与我们的视觉感知不匹配的颜色空间。OKLCH 修正了模型，使工具能够正常工作。要交互式探索，请访问 [oklch.fyi](https://oklch.fyi)。

## 快速参考

| 类别 | 使用场景 | 参考 |
| --- | --- | --- |
| 转换 | Hex/rgb/hsl 转换为 oklch | [color-conversion.md](color-conversion.md) |
| 调色板 | 生成比例、多色相、暗黑模式 | [palette-generation.md](palette-generation.md) |
| 对比度 | APCA/WCAG 检查、修复失败的对比度 | [accessibility-contrast.md](accessibility-contrast.md) |
| 色域 & Tailwind | P3 备用方案、`@theme` 比例、色域限制 | [gamut-and-tailwind.md](gamut-and-tailwind.md) |

## 为什么使用 OKLCH

- **感知均匀性。** 相同的 L 步长等于相同的亮度。`oklch(0.5 ...)` 视觉上处于中间。HSL 的 `lightness: 50%` 会因色相而剧烈变化。
- **稳定的色相。** HSL 蓝色会随着亮度变化而偏移至紫色。OKLCH 色相在整个亮度范围内保持不变。
- **独立的色度。** 色度是颜色的绝对度量，不依赖于亮度。HSL 饱和度则依赖。
- **有限的色域。** 并非所有 oklch 值都映射到可显示的 sRGB 颜色。在特定色相的高色度值会被裁剪——需要了解色域。

## OKLCH 语法

```
oklch(L C H)
oklch(L C H / alpha)
```

| 通道 | 范围 | 描述 |
| --- | --- | --- |
| L (亮度) | 0–1 | 0 = 黑色，1 = 白色。感知均匀。 |
| C (色度) | 0–~0.4 | 颜色饱和度。0 = 灰色。最大值取决于 L 和 H。 |
| H (色相) | 0–360 | 色相角度（度）。 |
| alpha | 0–1 | 可选透明度。斜杠语法。 |

```css
oklch(0.637 0.237 25.331)
oklch(0.8 0.05 200 / 0.5)
```

**格式化：** L 和 C 使用 3 位小数，H 使用最多 3 位。省略尾随零。将 `-0` 格式化为 `0`。浏览器支持：基础版 2023，全球覆盖率 96%+。

## 关键阈值

| 规则 | 值 |
| --- | --- |
| 亮/暗边界 | L > 0.6 = 亮背景 → 使用深色文字 |
| 亮度差距（亮背景） | 前景 L < 0.45 当背景 L > 0.85 |
| 亮度差距（暗背景） | 前景 L > 0.75 当背景 L < 0.25 |
| 色相漂移阈值 | 调色板步长间 > 10° 的扩散 = 可见漂移 |
| APCA 正常文本 | \|Lc\| >= 60 通过，>= 75 优秀 |
| WCAG 2 正常文本 | 4.5:1 AA，7:1 AAA |
| 对比度修复 | 仅调整 L —— 色度影响可忽略 |

## 审查输出格式

始终以带 **之前** 和 **之后** 列的 markdown 表格形式呈现颜色变化。包含所有被更改的颜色——而不仅仅是子集。不要在表格外以单独的 "之前：" / "之后：" 行列出发现。

| 之前 | 之后 |
| --- | --- |
| `color: #3b82f6` | `color: oklch(0.623 0.188 259.815)` |
| 跨色相的绝对 C 相同 | 每个色相的最大色度的相同 C% |
| P3 颜色无 sRGB 备用方案 | `@media (color-gamut: p3)` 包裹 |

这使反馈易于扫描且适合 diff。每一行都是一个开发者可以独立处理的自我包含的更改。

## 常见错误

| 问题 | 修复 |
| --- | --- |
| 新代码中的 Hex/rgb/hsl 颜色 | 转换为 `oklch()` |
| 色相漂移的 HSL 调色板渐变 | 使用恒定 oklch 色相重建 |
| 失败的对比度（使用 APCA 检查前景与其背景） | 调整 oklch L 通道，保持 C 和 H |
| 无色域检查的高色度 | 对 sRGB 中的 L/H 裁剪至最大色度 |
| 跨不同色相的绝对 C 相同 | 使用相同 C%（最大值的百分比）以保持一致的鲜艳度 |
| 无 sRGB 备用方案的 P3 颜色 | 添加 `@media (color-gamut: p3)` 模式 |
| 手选的暗黑模式颜色 | 通过反转 L 映射从亮调色板派生 |
| Tailwind v4 `@theme` 中的 Hex | 转换为 oklch 值 |
| 带逗号的 alpha 语法 | 使用斜杠：`oklch(L C H / alpha)` |

## 参考文件

- [color-conversion.md](color-conversion.md) — 支持的格式、转换示例、批量转换规则、保留的内容
- [palette-generation.md](palette-generation.md) — 比例约定、生成算法、多色相调色板、暗黑模式、为什么不用 HSL
- [accessibility-contrast.md](accessibility-contrast.md) — APCA 和 WCAG 2 阈值、使用 L 修复对比度、亮度差距指南、色相漂移检测
- [gamut-and-tailwind.md](gamut-and-tailwind.md) — sRGB 与 P3、色域限制、CSS 备用方案模式、Tailwind v4 @theme 和迁移
