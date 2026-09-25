# 颜色面板生成器

从单个品牌十六进制值生成完整的、可访问的颜色系统。生成 Tailwind v4 CSS，可直接粘贴到您的项目中。

## 工作流程

### 第 1 步：获取品牌十六进制值

询问主要品牌颜色。像 `#0D9488` 这样一个十六进制值就足够了。

### 第 2 步：生成 11 色阶比例

将十六进制转换为 HSL，然后通过改变亮度来生成阴影，同时保持色调不变。

#### 十六进制到 HSL 的转换

```javascript
function hexToHSL(hex) {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const diff = max - min;

  let l = (max + min) / 2;
  let s = 0;
  if (diff !== 0) {
    s = l > 0.5 ? diff / (2 - max - min) : diff / (max + min);
  }

  let h = 0;
  if (diff !== 0) {
    if (max === r) h = ((g - b) / diff + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / diff + 2) / 6;
    else h = ((r - g) / diff + 4) / 6;
  }

  return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
}
```

#### 亮度和饱和度值

| 色阶 | 亮度 | 饱和度倍数 | 用途 |
|------|------|------------|------|
| 50   | 97%  | 0.80       | 柔和的背景 |
| 100  | 94%  | 0.80       | 悬停状态 |
| 200  | 87%  | 0.85       | 边框、分隔符 |
| 300  | 75%  | 0.90       | 禁用状态 |
| 400  | 62%  | 0.95       | 占位符文本 |
| 500  | 48%  | 1.00       | **品牌颜色基线** |
| 600  | 40%  | 1.00       | 主要操作（通常是品牌颜色） |
| 700  | 33%  | 1.00       | 主要悬停 |
| 800  | 27%  | 1.00       | 激活状态 |
| 900  | 20%  | 1.00       | 浅色背景上的文本 |
| 950  | 10%  | 1.00       | 最深的强调 |

为浅色色阶（50-200）降低饱和度（减少 15-20%），300-400 减少饱和度（减少 5-10%），以防止过于鲜艳的粉彩色。500-950 保持全饱和度。

#### 完整色阶生成器

```javascript
function generateShadeScale(brandHex) {
  const { h, s } = hexToHSL(brandHex);
  const shades = {
    50:  { l: 97, sMul: 0.8 },  100: { l: 94, sMul: 0.8 },
    200: { l: 87, sMul: 0.85 }, 300: { l: 75, sMul: 0.9 },
    400: { l: 62, sMul: 0.95 }, 500: { l: 48, sMul: 1.0 },
    600: { l: 40, sMul: 1.0 },  700: { l: 33, sMul: 1.0 },
    800: { l: 27, sMul: 1.0 },  900: { l: 20, sMul: 1.0 },
    950: { l: 10, sMul: 1.0 }
  };
  const result = {};
  for (const [shade, { l, sMul }] of Object.entries(shades)) {
    result[shade] = `hsl(${h}, ${Math.round(s * sMul)}%, ${l}%)`;
  }
  return result;
}
```

#### HSL 到十六进制的转换

```javascript
function hslToHex(h, s, l) {
  s = s / 100; l = l / 100;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = l - c / 2;
  let r = 0, g = 0, b = 0;
  if (h < 60) { r = c; g = x; }
  else if (h < 120) { r = x; g = c; }
  else if (h < 180) { g = c; b = x; }
  else if (h < 240) { g = x; b = c; }
  else if (h < 300) { r = x; b = c; }
  else { r = c; b = x; }
  r = Math.round((r + m) * 255);
  g = Math.round((g + m) * 255);
  b = Math.round((b + m) * 255);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`.toUpperCase();
}
```

#### 验证

生成的色阶应看起来像同一颜色家族，具有平滑的过渡。浅色色阶（50-300）可用于背景，深色色阶（700-950）可用于文本。品牌颜色在 500-700 范围内应清晰可辨。

---

### 第 3 步：映射语义标记

每个背景标记**必须**有一个对应的文本标记。永远不要单独使用背景标记，否则深色模式会失效。

#### 浅色模式标记

| 标记     | 色阶 | 用途         |
|---------|------|--------------|
| `background` | white | 页面背景     |
| `foreground` | 950  | 正文文本     |
| `card`   | white | 卡片背景     |
| `card-foreground` | 900  | 卡片文本     |
| `popover` | white | 下拉/提示背景 |
| `popover-foreground` | 950  | 下拉文本     |
| `primary` | 600  | 主要按钮、链接 |
| `primary-foreground` | white | 主要按钮上的文本 |
| `secondary` | 100  | 次要按钮     |
| `secondary-foreground` | 900  | 次要按钮上的文本 |
| `muted`  | 50   | 禁用背景、微妙的区域 |
| `muted-foreground` | 600  | 微妙文本、标题 |
| `accent` | 100  | 悬停状态、微妙的强调 |
| `accent-foreground` | 900  | 强调背景上的文本 |
| `destructive` | red-600 | 删除按钮、错误 |
| `destructive-foreground` | white | 删除按钮上的文本 |
| `border` | 200  | 输入边框、分隔符 |
| `input`  | 200  | 输入字段边框 |
| `ring`   | 600  | 聚焦环       |

#### 深色模式标记

| 标记     | 色阶 | 用途         |
|---------|------|--------------|
| `background` | 950  | 页面背景     |
| `foreground` | 50   | 正文文本     |
| `card`   | 900  | 卡片背景     |
| `card-foreground` | 50   | 卡片文本     |
| `popover` | 900  | 下拉背景     |
| `popover-foreground` | 50   | 下拉文本     |
| `primary` | 500  | 主要按钮（深色模式下更亮） |
| `primary-foreground` | white | 主要按钮上的文本 |
| `secondary` | 800  | 次要按钮     |
| `secondary-foreground` | 50   | 次要按钮上的文本 |
| `muted`  | 800  | 禁用背景     |
| `muted-foreground` | 400  | 微妙文本     |
| `accent` | 800  | 悬停状态     |
| `accent-foreground` | 50   | 强调背景上的文本 |
| `destructive` | red-500 | 删除按钮（更亮） |
| `destructive-foreground` | white | 错误文本     |
| `border` | 800  | 边框         |
| `input`  | 800  | 输入边框     |
| `ring`   | 500  | 聚焦环       |

#### 深色模式反转模式

深色模式反转亮度，同时保持色调和饱和度。交换极端值（50 变成 950，950 变成 50），保持中间值（500 保持接近 500）。

| 浅色色阶 | 深色等效值 | 角色   |
|---------|------------|--------|
| 50      | 950        | 背景   |
| 100     | 900        | 微妙的背景 |
| 200     | 800        | 边框   |
| 500     | 500（略亮）| 品牌基线 |
| 600     | 400        | 主要操作 |
| 950     | 50         | 文本颜色 |

深色模式的关键原则：
- 主要色阶使用 500（而不是 600）——在深色背景上更亮，以提高可见性
- 文本使用 50（偏白色）而不是纯 `#FFFFFF` ——更护眼
- 边框需要比背景亮 10-15%（例如，800 边框在 950 背景上）
- 更高的高度 = 更亮的颜色（与浅色模式的阴影相反）
- 更改背景时始终更新文本

---

### 第 4 步：检查对比度

#### WCAG 最小比率

| 内容类型 | AA   | AAA  |
|---------|------|------|
| 普通文本（<18px 或 <14px 加粗） | 4.5:1 | 7:1  |
| 大文本（≥18px 或 ≥14px 加粗） | 3:1  | 4.5:1 |
| UI 组件（按钮、边框） | 3:1  | 未定义 |
| 图形对象（图标、图表） | 3:1  | 未定义 |

大多数项目目标为 AA，高可访问性需求（政府、医疗保健）目标为 AAA。

#### 亮度和对比度公式

```javascript
function getLuminance(hex) {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;
  const rsRGB = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
  const gsRGB = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
  const bsRGB = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
  return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
}

function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

#### 快速检查表 -- 浅色模式

| 文本     | 背景   | 比率   | 通过？ | 用途         |
|---------|--------|--------|--------|--------------|
| 950     | white  | 18.5:1 | AAA    | 正文文本     |
| 900     | white  | 14.2:1 | AAA    | 卡片文本     |
| 700     | white  | 8.1:1  | AAA    | 文本         |
| 600     | white  | 5.7:1  | AA     | 文本、按钮   |
| 500     | white  | 3.9:1  | 失败   | 对文本太亮   |
| white   | 600    | 5.7:1  | AA     | 按钮上的文本 |
| white   | 700    | 8.1:1  | AAA    | 按钮上的文本 |
| 600     | 50     | 5.4:1  | AA     | 微妙区域文本 |

#### 快速检查表 -- 深色模式

| 文本     | 背景   | 比率   | 通过？ | 用途         |
|---------|--------|--------|--------|--------------|
| 50      | 950    | 18.5:1 | AAA    | 正文文本     |
| 50      | 900    | 14.2:1 | AAA    | 卡片文本     |
| 400     | 950    | 8.2:1  | AAA    | 微妙文本     |
| 400     | 900    | 6.3:1  | AA     | 微妙文本     |
| white   | 600    | 5.7:1  | AA     | 按钮上的文本 |

**经验法则**：对于文本，前景和背景之间的亮度差异应至少为 50%。

#### 必须验证的必要对

1. **正文文本**：前景在背景上（浅色：950 on white = 18.5:1，深色：50 on 950 = 18.5:1）
2. **主要按钮**：primary-foreground on primary（浅色：white on 600 = 5.7:1，深色：white on 500 = 3.9:1 —— 边缘情况）
3. **微妙文本**：muted-foreground on muted（浅色：600 on 50 = 5.4:1，深色：400 on 800 = 4.1:1 —— 可能失败）
4. **卡片文本**：card-foreground on card（浅色：900 on white = 14.2:1，深色：50 on 900 = 14.2:1）

#### 修复常见对比度失败

**白色在 primary-500 上失败（3.9:1）**：使用 primary-600（5.7:1），或使用深色文本在按钮上。

**深色模式中的微妙文本失败（400 on 800 = 4.1:1）**：使用 300 on 900 = 6.8:1。

**链接难以看到（500 on white = 3.9:1）**：使用 primary-700（8.1:1），或添加下划线装饰。

---

### 第 5 步：输出 Tailwind v4 CSS

```css
@import "tailwindcss";

@theme {
  /* 色阶 */
  --color-primary-50: #F0FDFA;
  --color-primary-100: #CCFBF1;
  --color-primary-200: #99F6E4;
  --color-primary-300: #5EEAD4;
  --color-primary-400: #2DD4BF;
  --color-primary-500: #14B8A6;
  --color-primary-600: #0D9488;
  --color-primary-700: #0F766E;
  --color-primary-800: #115E59;
  --color-primary-900: #134E4A;
  --color-primary-950: #042F2E;

  /* 浅色模式语义标记 */
  --color-background: #FFFFFF;
  --color-foreground: var(--color-primary-950);
  --color-card: #FFFFFF;
  --color-card-foreground: var(--color-primary-900);
  --color-popover: #FFFFFF;
  --color-popover-foreground: var(--color-primary-950);
  --color-primary: var(--color-primary-600);
  --color-primary-foreground: #FFFFFF;
  --color-secondary: var(--color-primary-100);
  --color-secondary-foreground: var(--color-primary-900);
  --color-muted: var(--color-primary-50);
  --color-muted-foreground: var(--color-primary-600);
  --color-accent: var(--color-primary-100);
  --color-accent-foreground: var(--color-primary-900);
  --color-destructive: #DC2626;
  --color-destructive-foreground: #FFFFFF;
  --color-border: var(--color-primary-200);
  --color-input: var(--color-primary-200);
  --color-ring: var(--color-primary-600);
  --radius: 0.5rem;
}

/* 深色模式覆盖 */
.dark {
  --color-background: var(--color-primary-950);
  --color-foreground: var(--color-primary-50);
  --color-card: var(--color-primary-900);
  --color-card-foreground: var(--color-primary-50);
  --color-popover: var(--color-primary-900);
  --color-popover-foreground: var(--color-primary-50);
  --color-primary: var(--color-primary-500);
  --color-primary-foreground: #FFFFFF;
  --color-secondary: var(--color-primary-800);
  --color-secondary-foreground: var(--color-primary-50);
  --color-muted: var(--color-primary-800);
  --color-muted-foreground: var(--color-primary-400);
  --color-accent: var(--color-primary-800);
  --color-accent-foreground: var(--color-primary-50);
  --color-destructive: #EF4444;
  --color-destructive-foreground: #FFFFFF;
  --color-border: var(--color-primary-800);
  --color-input: var(--color-primary-800);
  --color-ring: var(--color-primary-500);
}
```

将 `assets/tailwind-colors.css` 作为起始模板复制。

---

## 组件使用示例

```tsx
// 主要按钮
<button className="bg-primary text-primary-foreground hover:bg-primary/90">Click me</button>

// 次要按钮
<button className="bg-secondary text-secondary-foreground hover:bg-secondary/80">Cancel</button>

// 卡片
<div className="bg-card text-card-foreground border-border rounded-lg">
  <h2>Title</h2>
  <p className="text-muted-foreground">Description</p>
</div>

// 输入
<input className="bg-background text-foreground border-input focus:ring-ring" />
```

---

## 常见调整

- **浅色色阶过于鲜艳**：降低饱和度 10-20%
- **主要对比度不佳**：使用 700+ 色阶的文本
- **深色模式太暗**：使用 900 而不是 950 作为背景
- **品牌颜色太亮/太暗**：调整到 500-600 范围
- **深色模式看起来过于苍白**：使用 500 作为主要颜色（比浅色模式的 600 更亮）
- **纯白色文本在深色模式下过于刺眼**：使用 50（偏白色）代替
- **深色模式中的微妙文本对比度失败**：使用更极端的色阶（300 on 900 而不是 400 on 800）

### 品牌身份调整

- **保守品牌**（金融、法律）：使用 primary-700 作为按钮，减少浅色色阶的饱和度
- **鲜艳品牌**（创意、科技）：使用 primary-500-600，保持全饱和度
- **简约品牌**（设计、建筑）：少量使用 primary，强调微妙色调，使用细微边框（primary-100）

---

## 验证清单

- [ ] 正文文本：≥4.5:1（普通）或 ≥3:1（大）
- [ ] 主要按钮文本：≥4.5:1
- [ ] 次要按钮文本：≥4.5:1
- [ ] 微妙文本：≥4.5:1
- [ ] 链接：≥4.5:1（或带下划线）
- [ ] UI 元素（边框）：≥3:1
- [ ] 聚焦指示器：≥3:1
- [ ] 错误文本：≥4.5:1
- [ ] 深色模式：所有上述检查均通过
- [ ] 每个背景都有一个文本对
- [ ] 品牌颜色在两种模式下都清晰可辨
- [ ] 边框可见但不刺眼
- [ ] 卡片/区域有清晰的边界

**在发布前测试两种模式。**

---

## 可选参考

- **在线对比度检查器**：WebAIM（webaim.org/resources/contrastchecker）、Coolors（coolors.co/contrast-checker）、Accessible Colors（accessible-colors.com）
- **CI/CD 对比度测试**：在测试套件中使用 `getContrastRatio()` 断言所有标记对的最小比率
- **透明/渐变边缘情况**：对于具有不透明度的颜色，计算最终渲染颜色。对于渐变，检查两个端点
- **OLED 深色模式**：使用 `@media (prefers-contrast: high)` 与 `#000000` 背景在 AMOLED 屏幕上节省电池
- **多色调色板**：为每个品牌颜色生成单独的色阶，映射到不同的语义角色（主要、强调）
- **调色板可视化工具**：coolors.co、paletton.com、Figma 色板
- `assets/tailwind-colors.css` — 完整 CSS 输出模板
