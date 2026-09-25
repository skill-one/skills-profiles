# UI UX Pro Max 技能

> 由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

UI UX Pro Max 是一项AI技能，它将设计智能注入编码代理中，赋予它们161条行业特定推理规则、67种UI风格、57种字体搭配、161种调色板以及预交付检查清单，使其能够一次性生成专业、可访问且优化了转化率的界面。

## 安装

### 通过CLI（推荐）

```bash
# 全局安装CLI
npm install -g uipro-cli

# 将技能添加到您的项目中
npx uipro-cli install

# 或者全局安装
npx uipro-cli install --global
```

### 通过Python（直接）

```bash
# 克隆仓库
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
cd ui-ux-pro-max-skill

# 安装依赖
pip install -r requirements.txt

# 运行设计系统生成器
python main.py
```

### 手动SKILL.md集成

将生成的`SKILL.md`复制到您的项目根目录，以便Claude Code、Cursor、Codex或Windsurf等代理自动获取：

```bash
cp SKILL.md /your-project/SKILL.md
```

---

## 核心概念

### 设计系统生成器

当您描述一个产品时，该技能会在以下领域运行多域搜索：

| 领域       | 数量 | 目的                 |
|------------|------|----------------------|
| 推理规则   | 161  | 行业特定的布局/风格决策 |
| UI风格     | 67   | 视觉语言（玻璃态、粗暴主义等） |
| 调色板     | 161  | 行业匹配的调色板     |
| 字体搭配   | 57   | 字体组合             |
| 主页模式   | 24   | 优化了转化的结构     |

### 输出：完整设计系统

每次生成都会产生：
- **模式** — 页面结构（区域、CTA位置）
- **风格** — 带有关键字的视觉语言
- **颜色** — 主要、次要、CTA、背景、文本
- **排版** — 字体搭配 + Google Fonts URL
- **关键效果** — 动画和交互
- **反模式** — 避免此行业的注意事项
- **预交付检查清单** — 可访问性和UX门槛

---

## Python API使用

### 基础设计系统生成

```python
from uiuxpro import DesignSystemGenerator

# 初始化生成器
generator = DesignSystemGenerator()

# 从描述生成完整设计系统
result = generator.generate(
    description="一个豪华美容水疗中心的落地页",
    stack="react",           # react | nextjs | astro | vue | html
    mode="light"             # light | dark | auto
)

print(result.pattern)        # 落地页结构
print(result.style)          # UI风格建议
print(result.colors)         # 颜色调色板字典
print(result.typography)     # 字体搭配 + 导入URL
print(result.effects)        # 动画和交互
print(result.anti_patterns)  # 需要避免的内容
print(result.checklist)      # 预交付门槛
```

### 查询推理规则

```python
from uiuxpro import ReasoningEngine

engine = ReasoningEngine()

# 查找产品类型的规则
rules = engine.search("金融科技支付应用")
for rule in rules:
    print(rule.category)       # 例如："金融科技/加密货币"
    print(rule.pattern)        # 推荐的页面模式
    print(rule.style_priority) # 风格的有序列表
    print(rule.color_mood)     # 调色板关键词
    print(rule.anti_patterns)  # 例如：["有趣的字体", "霓虹色"]

# 获取某个类别的所有规则
all_healthcare = engine.get_by_category("医疗保健")
```

### 风格查询

```python
from uiuxpro import StyleLibrary

styles = StyleLibrary()

# 获取所有67种风格
all_styles = styles.list_all()

# 通过关键词查找风格
matching = styles.search("玻璃透明模糊")

# 获取完整风格规范
glassmorphism = styles.get("Glassmorphism")
print(glassmorphism.keywords)       # ["磨砂玻璃", "透明度", ...]
print(glassmorphism.best_for)       # ["SaaS仪表盘", "科技产品"]
print(glassmorphism.css_variables)  # CSS自定义属性
print(glassmorphism.tailwind_config) # Tailwind配置
```

### 调色板选择

```python
from uiuxpro import ColorEngine

colors = ColorEngine()

# 获取产品类型的调色板
palette = colors.get_for_product("医疗诊所")
print(palette.primary)     # "#2B7A9F"
print(palette.secondary)   # "#E8F4FD"
print(palette.cta)         # "#0066CC"
print(palette.background)  # "#FFFFFF"
print(palette.text)        # "#1A2B3C"
print(palette.notes)       # "临床信任与人文关怀"

# 通过情绪获取调色板
calm_palettes = colors.get_by_mood("平静")
luxury_palettes = colors.get_by_mood("奢华")
```

### 字体搭配

```python
from uiuxpro import TypographyEngine

typography = TypographyEngine()

# 获取某种情绪的字体搭配
pairing = typography.get_for_mood("优雅精致")
print(pairing.heading)      # "Cormorant Garamond"
print(pairing.body)         # "Montserrat"
print(pairing.google_url)   # Google Fonts导入URL
print(pairing.css_import)   # @import语句

# 获取某个技术栈的所有搭配
react_pairings = typography.get_for_stack("react")
```

---

## CLI命令

```bash
# 交互式生成设计系统
npx uipro-cli generate

# 为特定产品类型生成
npx uipro-cli generate --product "saas仪表盘" --stack nextjs

# 列出所有67种UI风格
npx uipro-cli styles list

# 获取风格详情
npx uipro-cli styles get glassmorphism

# 搜索推理规则
npx uipro-cli rules search "电子商务奢华"

# 列出所有调色板
npx uipro-cli colors list

# 获取字体搭配
npx uipro-cli fonts list
npx uipro-cli fonts get --mood "科技现代"

# 以JSON格式输出设计系统
npx uipro-cli generate --product "餐厅预订" --output json

# 以markdown格式输出
npx uipro-cli generate --product "作品集网站" --output markdown
```

---

## 真实世界示例

### 示例1：React SaaS仪表盘

```python
from uiuxpro import DesignSystemGenerator

gen = DesignSystemGenerator()
ds = gen.generate(
    description="面向企业团队的B2B SaaS分析仪表盘",
    stack="react",
    tech_details={"component_library": "shadcn/ui", "css": "tailwindcss"}
)

# 结果：
# 模式："数据优先 + 逐步披露"
# 风格："玻璃态"或"Bento网格"
# 颜色：主要色#6366F1（靛蓝），CTA #8B5CF6（紫罗兰）
# 字体：Inter / Inter（统一，高可读性）
# 效果：微妙的卡片阴影，平滑的数据过渡200ms
# 避免：装饰性动画，过于复杂的渐变
```

从`ds.tailwind_config`生成的Tailwind配置：

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366F1',
          50: '#EEF2FF',
          500: '#6366F1',
          900: '#312E81',
        },
        cta: '#8B5CF6',
        surface: 'rgba(255,255,255,0.05)',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(99,102,241,0.15)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
}
```

### 示例2：健康/水疗落地页

```python
ds = gen.generate(
    description="豪华健康水疗中心预订和服务落地页",
    stack="html",
    tech_details={"css": "tailwindcss"}
)

# 自动生成完整的CSS变量块：
print(ds.css_variables)
```

输出`ds.css_variables`：

```css
:root {
  /* 温柔UI进化 - 宁静水疗 */
  --color-primary: #E8B4B8;      /* 温柔粉 */
  --color-secondary: #A8D5BA;    /* 芝麻绿 */
  --color-cta: #D4AF37;          /* 金色 */
  --color-background: #FFF5F5;   /* 温暖白 */
  --color-text: #2D3436;         /* 炭灰 */

  /* 排版 */
  --font-heading: 'Cormorant Garamond', Georgia, serif;
  --font-body: 'Montserrat', system-ui, sans-serif;

  /* 效果 */
  --shadow-soft: 6px 6px 12px #d1c4c5, -6px -6px 12px #ffffff;
  --transition-base: 200ms ease-in-out;
  --border-radius-organic: 20px 60px 30px 50px;
}
```

### 示例3：金融科技/银行应用

```python
ds = gen.generate(
    description="个人财务追踪应用，包含预算和投资追踪",
    stack="react-native"
)

# 自动标记的金融反模式：
print(ds.anti_patterns)
# [
#   "圆润有趣的字体（使用几何无衬线体）",
#   "亮色霓虹色（侵蚀信任）",
#   "AI紫色/粉色渐变",
#   "金融数据上的过度动画",
#   "严肃金融行为上的游戏化元素"
# ]

print(ds.checklist)
# [
#   "✓ 所有数字显示的WCAG AA对比度",
#   "✓ 带有区域意识的货币格式",
#   "✓ 清晰且可操作的错误状态",
#   "✓ 所有异步操作的加载状态",
#   "✓ 集成了生物识别认证UI",
#   "✓ 不要使用表情符号作为主要图标 — 使用Lucide或SF Symbols",
# ]
```

### 示例4：Next.js的完整栈集成

```python
from uiuxpro import DesignSystemGenerator, StackExporter

gen = DesignSystemGenerator()
ds = gen.generate(
    description="面向企业HR团队的AI驱动招聘平台",
    stack="nextjs",
    tech_details={
        "component_library": "shadcn/ui",
        "css": "tailwindcss",
        "icons": "lucide-react"
    }
)

# 导出为Next.js可用的文件
exporter = StackExporter(ds, stack="nextjs")
exporter.write_all(output_dir="./src/design-system/")

# 生成的文件：
# ./src/design-system/tokens.css        — CSS自定义属性
# ./src/design-system/tailwind.config.js — Tailwind配置
# ./src/design-system/typography.ts     — 字体配置
# ./src/design-system/colors.ts         — TypeScript颜色标记
# ./src/design-system/README.md         — 设计决策及理由
```

---

## 支持的技术栈

| 栈       | 关键 | 备注                 |
|----------|------|----------------------|
| React    | `react` | 组件模式 + Tailwind |
| Next.js  | `nextjs` | App Router + RSC感知 |
| Astro    | `astro` | 岛架构模式           |
| Vue 3    | `vue` | 组合API模式           |
| Nuxt.js  | `nuxt` | 自动导入感知         |
| Nuxt UI  | `nuxt-ui` | 组件覆盖             |
| Svelte   | `svelte` | 反应式存储模式       |
| SwiftUI  | `swiftui` | iOS/macOS原生模式     |
| React Native | `react-native` | 移动优先响应式       |
| Flutter  | `flutter` | 组件树模式           |
| HTML + Tailwind | `html` | 独立CSS输出         |
| shadcn/ui | `shadcn` | 主题标记覆盖         |
| Jetpack Compose | `jetpack` | Android Material3   |

---

## 预交付检查清单（通用）

该技能在每次生成的设计中强制执行以下门槛：

```
可访问性
[ ] 不要使用表情符号作为图标 — 使用SVG (Heroicons / Lucide / Phosphor)
[ ] 所有可点击元素上cursor-pointer
[ ] 带有平滑过渡的悬停状态（150–300ms）
[ ] 浅色模式：文本对比度至少4.5:1
[ ] 深色模式：文本对比度至少4.5:1
[ ] 键盘导航的焦点状态可见
[ ] 尊重prefers-reduced-motion
[ ] 图标按钮上带有ARIA标签
```

```
响应式
[ ] 手机：375px断点测试
[ ] 平板：768px断点测试
[ ] 桌面：1024px断点测试
[ ] 宽屏：1440px断点测试
```

```
性能
[ ] 图片使用下一代格式（WebP / AVIF）
[ ] 字体使用font-display: swap加载
[ ] 字体加载时保留空间，避免布局偏移
[ ] 动画仅使用transform/opacity（不使用布局属性）
```

```
交互
[ ] 所有异步操作都有加载状态
[ ] 错误状态清晰且可操作
[ ] 空状态设计（非空白）
[ ] 表单提交后有成功反馈
```

---

## 按行业划分的常见模式

### 科技/软件即服务
- **风格**：玻璃态、Bento网格、AI原生UI
- **颜色**：靛蓝/紫罗兰主要色，仪表盘深色背景
- **避免**：库存照片、剪贴画、彩虹渐变

### 电子商务/奢华
- **风格**：极简主义、编辑式、陶土态（休闲用）
- **颜色**：奢华用黑/金色；休闲用亮/大胆色
- **避免**：杂乱布局、过多CTA、Comic Sans相邻字体

### 医疗保健/医疗
- **风格**：干净极简主义、温柔UI
- **颜色**：蓝色、蓝绿色、白色 — 临床但温暖
- **避免**：红色作为主要操作（紧急含义），医疗数据上的深色模式

### 金融/金融科技
- **风格**：专业极简主义、数据密集UI
- **颜色**：深蓝、绿色、中性色
- **避免**：有趣字体、霓虹色、AI紫色渐变、过度动画

### 食品与餐厅
- **风格**：温暖极简主义、摄影优先
- **颜色**：温暖中性色、诱人红色/橙色、大地色
- **避免**：冷蓝色作为主要色、食物照片上低对比度文本

---

## 故障排除

### 安装后CLI未找到
```bash
# 确保npm全局二进制文件在PATH中
export PATH="$(npm bin -g):$PATH"

# 或者直接使用npx
npx uipro-cli generate
```

### Python导入错误
```bash
# 确保您在项目目录中并激活了venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 生成返回通用输出
- 描述要具体：包括行业、受众和目标
- ✗ `"一个网站"` → ✓ `"一个B2B项目管理工具的SaaS落地页，面向远程工程团队"`
- 包含框架上下文以获取框架特定输出

### 未找到匹配的推理规则
```python
# 引擎会回退到最接近的类别匹配
# 检查匹配分数以验证
result = engine.search("自主无人机配送车队")
print(result[0].score)      # BM25相关性分数
print(result[0].category)   # 匹配的类别
print(result[0].fallback)   # 如果是近似匹配
```

### Tailwind配置与现有配置冲突
```python
# 仅获取主题扩展，而不是完整配置
theme_extension = ds.tailwind_theme_extension  # dict，不是完整配置

# 手动将主题扩展合并到您的现有tailwind.config.js
import json
print(json.dumps(theme_extension, indent=2))
```

---

## 资源

- **主页**：https://uupm.cc
- **GitHub**：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **npm CLI**：https://www.npmjs.com/package/uipro-cli
- **许可证**：MIT
