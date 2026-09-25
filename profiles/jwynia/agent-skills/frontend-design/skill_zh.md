# 前端设计

创建独特、符合生产标准的前端界面，避免通用的"AI劣质"美学。这项技能结合了设计理念指导与实用的TypeScript工具，用于分析现有设计并生成设计系统资源。

**核心原则**：选择清晰的美学方向并精确执行。大胆的极简主义和精致的极简主义都有效果——关键在于意图性，而非强度。

## 使用此技能的场景

**使用时**：
- 构建Web组件、页面或应用程序
- 审计现有CSS的设计不一致性
- 从遗留代码库中提取设计令牌
- 生成调色板和排版系统
- 跨框架创建组件模板
- 检查设计元素的可访问性合规性

**不使用时**：
- 简单的文本内容更改
- 仅后端工作
- 非视觉功能

## 前置条件

- **Deno**运行时（用于脚本执行）
- 可选：用于分析的现有CSS/设计文件
- 可选：用于参考的设计令牌文件

## 快速入门

此技能以三种模式运行：

### 1. 分析模式
审计现有样式、提取令牌、检查可访问性。

```bash
# 审计CSS中的设计模式和一致性
deno run --allow-read scripts/analyze-styles.ts styles.css

# 从现有CSS中提取设计令牌
deno run --allow-read scripts/extract-tokens.ts ./src --format css

# 检查可访问性（对比度、焦点状态）
deno run --allow-read scripts/analyze-accessibility.ts component.tsx
```

### 2. 定义模式
创建JSON规范定义要生成的内容。参见`assets/`中的模式示例。

### 3. 生成模式
创建调色板、排版系统、令牌和组件。

```bash
# 生成调色板
deno run --allow-read --allow-write scripts/generate-palette.ts --seed "#2563eb" --theme warm

# 生成排版系统
deno run --allow-read --allow-write scripts/generate-typography.ts --display "Playfair Display" --body "Source Sans Pro"

# 生成设计令牌文件
deno run --allow-read --allow-write scripts/generate-tokens.ts tokens-spec.json ./output/

# 生成组件
deno run --allow-read --allow-write scripts/generate-component.ts --name Button --framework react --styling tailwind
```

---

## 指令

### 第一阶段：分析（可选但推荐）

在创建新设计之前，审计现有代码以了解当前模式。

#### 1a. 样式分析

分析CSS文件以识别颜色、排版、间距和一致性：

```bash
deno run --allow-read scripts/analyze-styles.ts <输入> [选项]

选项：
  --tokens <文件>    与现有设计令牌进行比较
  --pretty           美化JSON输出
  --format <类型>    输出格式：json（默认），摘要
```

**输出包括**：
- 带有十六进制规范化的颜色使用清单
- 排版模式（字体、大小、粗细）
- 间距值分布
- 不一致性和建议

#### 1b. 令牌提取

从CSS文件中提取设计令牌到标准化格式：

```bash
deno run --allow-read scripts/extract-tokens.ts <输入> [选项]

选项：
  --format <类型>    输出：css, scss, tailwind, style-dictionary, tokens-studio
  --output-css       同时输出CSS变量文件
```

#### 1c. 可访问性审计

检查与设计相关的可访问性问题：

```bash
deno run --allow-read scripts/analyze-accessibility.ts <输入> [选项]

选项：
  --format <类型>    输出：json, 摘要
  --level <AA|AAA>   WCAG合规级别（默认：AA）
```

**检查包括**：
- 颜色对比度比率
- 焦点指示器的存在
- 触摸目标大小
- 对运动偏好的尊重

---

### 第二阶段：生成

#### 2a. 调色板生成

从种子颜色或主题生成协调的调色板：

```bash
deno run --allow-read --allow-write scripts/generate-palette.ts [选项] <输出>

选项：
  --seed <颜色>     主要种子颜色（十六进制）
  --theme <类型>     warm, cool, neutral, vibrant, muted, dark, light
  --style <类型>     minimalist, bold, organic, corporate, playful
  --shades           生成50-950色阶
  --semantic         生成success/warning/error颜色
  --contrast <级别>   目标对比度：AA（默认），AAA
  --format <类型>    css, scss, tailwind, tokens, json
```

**示例规范** (`palette-spec.json`)：
```json
{
  "seedColors": {
    "primary": "#2563eb",
    "accent": "#f59e0b"
  },
  "theme": "cool",
  "generateShades": true,
  "generateSemantics": true,
  "contrastTarget": "AA",
  "outputFormat": "css"
}
```

#### 2b. 排版系统生成

生成带字体堆栈和比例的排版系统：

```bash
deno run --allow-read --allow-write scripts/generate-typography.ts [选项] <输出>

选项：
  --display <字体>   显示/标题字体家族
  --body <字体>      正文文本字体家族
  --mono <字体>      等宽字体家族
  --scale <类型>     minor-second, major-second, minor-third, major-third, perfect-fourth, golden-ratio
  --base <px>        基础字体大小（默认：16）
  --line-height      tight, normal, relaxed
  --responsive       生成响应式断点
  --format <类型>    css, scss, tailwind, tokens
```

**比例类型**：
| 比例 | 比率 | 字符 |
|-------|-------|-------|
| minor-second | 1.067 | 细微、保守 |
| major-second | 1.125 | 平衡、专业 |
| minor-third | 1.200 | 清晰的层次结构 |
| major-third | 1.250 | 强大的存在感 |
| perfect-fourth | 1.333 | 大胆、有影响力 |
| golden-ratio | 1.618 | 戏剧性、艺术性 |

#### 2c. 设计令牌生成

生成多格式全面的设
