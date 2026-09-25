# 设计系统

Token 架构、组件规范、系统化设计、幻灯片生成。

## 使用场景

- 设计 token 创建
- 组件状态定义
- CSS 变量系统
- 间距/排版比例
- 设计到代码的交接
- Tailwind 主题配置
- **幻灯片/演示文稿生成**

## Token 架构

加载：`references/token-architecture.md`

### 三层结构

```
原始值 (Primitive)
       ↓
语义 (目的别名)
       ↓
组件 (组件特定)
```

**示例：**
```css
/* 原始值 */
--color-blue-600: #2563EB;

/* 语义 */
--color-primary: var(--color-blue-600);

/* 组件 */
--button-bg: var(--color-primary);
```

## 脚本路径

本技能及其 `references/` 中的脚本路径相对于包含此 `SKILL.md` 的目录，而不是项目：`scripts/<文件>` 是本技能自己的 `scripts/` 文件夹，而 `../<技能>/scripts/<文件>` 是与其一同安装的兄弟子技能。从该目录（Claude Code 在技能加载时报告为技能的基本目录）构建完整路径，并将工作目录保持在项目根目录——脚本相对于它读取和写入项目文件，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 快速入门

**生成 token：**
```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

**验证使用：**
```bash
node scripts/validate-tokens.cjs --dir src/
```

## 参考

| 主题 | 文件 |
|------|------|
| Token 架构 | `references/token-architecture.md` |
| 原始 token | `references/primitive-tokens.md` |
| 语义 token | `references/semantic-tokens.md` |
| 组件 token | `references/component-tokens.md` |
| 组件规范 | `references/component-specs.md` |
| 状态与变体 | `references/states-and-variants.md` |
| Tailwind 集成 | `references/tailwind-integration.md` |

## 组件规范模式

| 属性 | 默认 | 悬停 | 激活 | 禁用 |
|------|------|------|------|------|
| 背景 | primary | primary-dark | primary-darker | muted |
| 文本 | white | white | white | muted-fg |
| 边框 | none | none | none | muted-border |
| 阴影 | sm | md | none | none |

## 脚本

| 脚本 | 目的 |
|------|------|
| `generate-tokens.cjs` | 从 JSON token 配置生成 CSS |
| `validate-tokens.cjs` | 检查代码中的硬编码值 |
| `search-slides.py` | BM25 搜索 + 上下文推荐 |
| `slide-token-validator.py` | 验证幻灯片 HTML 的 token 合规性 |
| `fetch-background.py` | 从 Pexels/Unsplash 获取图像 |

## 模板

| 模板 | 目的 |
|------|------|
| `design-tokens-starter.json` | 具有三层结构的起始 JSON |

## 集成

**与品牌：** 从品牌颜色/排版中提取原始值
**与 ui-styling：** 组件 token → Tailwind 配置

**技能依赖：** brand, ui-styling
**主要代理：** ui-ux-designer, frontend-developer

## 幻灯片系统

使用设计 token + Chart.js + 上下文决策系统的品牌合规演示文稿。

### 真理来源

| 文件 | 目的 |
|------|------|
| `docs/brand-guidelines.md` | 品牌身份、声音、颜色 |
| `assets/design-tokens.json` | token 定义（原始值→语义→组件） |
| `assets/design-tokens.css` | CSS 变量（在幻灯片中导入） |
| `assets/css/slide-animations.css` | CSS 动画库 |

### 幻灯片搜索 (BM25)

```bash
# 基本搜索（自动检测域）
python scripts/search-slides.py "investor pitch"

# 特定域搜索
python scripts/search-slides.py "problem agitation" -d copy
python scripts/search-slides.py "revenue growth" -d chart

# 上下文搜索（Premium 系统）
python scripts/search-slides.py "problem slide" --context --position 2 --total 9
python scripts/search-slides.py "cta" --context --position 9 --prev-emotion frustration
```

### 决策系统 CSV 文件

| 文件 | 目的 |
|------|------|
| `data/slide-strategies.csv` | 15 张牌结构 + 情感弧 + sparkline 节拍 |
| `data/slide-layouts.csv` | 25 布局 + 组件变体 + 动画 |
| `data/slide-layout-logic.csv` | 目标 → 布局 + break_pattern 标志 |
| `data/slide-typography.csv` | 内容类型 → 排版比例 |
| `data/slide-color-logic.csv` | 情感 → 颜色处理 |
| `data/slide-backgrounds.csv` | 幻灯片类型 → 图像类别（Pexels/Unsplash） |
| `data/slide-copy.csv` | 25 写作公式（PAS, AIDA, FAB） |
| `data/slide-charts.csv` | 25 图表类型 + Chart.js 配置 |

### 上下文决策流程

```
1. 解析目标/上下文
        ↓
2. 搜索 slide-strategies.csv → 获取策略 + 情感节拍
        ↓
3. 对于每张幻灯片：
   a. 查询 slide-layout-logic.csv → 布局 + break_pattern
   b. 查询 slide-typography.csv → 类型比例
   c. 查询 slide-color-logic.csv → 颜色处理
   d. 查询 slide-backgrounds.csv → 如需图像
   e. 应用 slide-animations.css 中的动画类
        ↓
4. 使用设计 token 生成 HTML
        ↓
5. 使用 slide-token-validator.py 验证
```

### 模式打破（Duarte Sparkline）

Premium 牌在 1/3 和 2/3 位置交替情感以增强参与度：
```
"What Is" (frustration) ↔ "What Could Be" (hope)
```

系统在 1/3 和 2/3 位置计算模式打破。

### 幻灯片要求

**所有幻灯片必须：**
1. 导入 `assets/design-tokens.css` - 单一真理来源
2. 使用 CSS 变量：`var(--color-primary)`、`var(--slide-bg)` 等
3. 使用 Chart.js 绘制图表（不是纯 CSS 条形图）
4. 包含导航（键盘箭头、点击、进度条）
5. 内容居中
6. 关注说服/转化

### Chart.js 集成

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // 使用品牌珊瑚色
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### Token 合规性

```css
/* 正确 - 使用 token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* 错误 - 硬编码 */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### 参考实现

包含所有功能的完整示例：
```
assets/designs/slides/claudekit-pitch-251223.html
```

### 命令

```bash
/slides:create "10 张牌的投资人提案 for ClaudeKit Marketing"
```

## 最佳实践

1. 组件中永远不要使用原始十六进制值 - 始终引用 token
2. 语义层支持主题切换（亮/暗）
3. 组件 token 支持每个组件的自定义
4. 使用 HSL 格式控制不透明度
5. 记录每个 token 的目的
6. **幻灯片必须导入 design-tokens.css 并专一使用 var()**
