# 设计实验室技能

此技能实现了一个完整的设计探索工作流程：访谈、生成变体、收集反馈、细化、预览和最终确定。

## 关键：清理行为

**所有临时文件必须在流程结束时删除，无论是：**
- 用户确认最终设计 → 清理，然后生成计划
- 用户中止/取消 → 立即清理，不生成计划

**绝对不要留下 `.claude-design/` 或 `__design_lab` 路径。** 如果用户在任何时候说“取消”、“中止”、“停止”或“不必在意”，请确认然后删除所有临时工件。

---

## 第 0 阶段：预检检测

在开始访谈之前，自动检测：

### 包管理器
检查项目根目录中的锁文件：
- `pnpm-lock.yaml` → 使用 `pnpm`
- `yarn.lock` → 使用 `yarn`
- `package-lock.json` → 使用 `npm`
- `bun.lockb` → 使用 `bun`

### 框架检测
检查配置文件：
- `next.config.js` 或 `next.config.mjs` 或 `next.config.ts` → **Next.js**
  - 检查 `app/` 目录 → 应用程序路由器
  - 检查 `pages/` 目录 → 页面路由器
- `vite.config.js` 或 `vite.config.ts` → **Vite**
- `remix.config.js` → **Remix**
- `nuxt.config.js` 或 `nuxt.config.ts` → **Nuxt**
- `astro.config.mjs` → **Astro**

### 样式系统检测
检查 `package.json` 依赖项和配置文件：
- `tailwind.config.js` 或 `tailwind.config.ts` → **Tailwind CSS**
- `@mui/material` 在依赖项中 → **Material UI**
- `@chakra-ui/react` 在依赖项中 → **Chakra UI**
- `antd` 在依赖项中 → **Ant Design**
- `styled-components` 在依赖项中 → **styled-components**
- `@emotion/react` 在依赖项中 → **Emotion**
- `.css` 或 `.module.css` 文件 → **CSS 模块**

### 设计记忆检查
查找现有的设计记忆文件：
- `docs/design-memory.md`
- `DESIGN_MEMORY.md`
- `.claude-design/design-memory.md`

如果找到，请读取它并使用它来预填充默认值并跳过冗余问题。

### 视觉风格推断（关键）

**不要使用通用/预定义的样式。从项目中提取视觉语言：**

**如果检测到 Tailwind，** 读取 `tailwind.config.js` 或 `tailwind.config.ts`：
```javascript
// 提取并使用：
theme.colors      // 色彩调色板
theme.spacing     // 间距尺度
theme.borderRadius // 半径值
theme.fontFamily  // 字体排印
theme.boxShadow   // 抬升系统
```

**如果存在 CSS 变量，** 读取 `globals.css`、`variables.css` 或 `:root` 定义：
```css
:root {
  --color-*     /* 色彩标记 */
  --spacing-*   /* 间距标记 */
  --font-*      /* 字体排印标记 */
  --radius-*    /* 边框半径标记 */
}
```

**如果检测到 UI 库**（MUI、Chakra、Ant），读取主题配置：
- MUI: `theme.ts` 或 `createTheme()` 调用
- Chakra: `theme/index.ts` 或 `extendTheme()` 调用
- Ant: `ConfigProvider` 主题属性

**始终扫描现有组件**以了解模式：
- 找到 2-3 个现有的按钮 → 记录它们的样式模式
- 找到 2-3 个现有的卡片 → 记录填充、边框、阴影
- 找到现有的表单 → 记录输入样式、标签位置
- 找到现有的字体排印 → 记录标题大小、正文文本

**将推断的样式存储在设计简介中**，以便在所有变体中一致使用。

---

## 第 1 阶段：访谈

对所有访谈步骤使用 **AskUserQuestion** 工具。如果存在设计记忆，请根据设计记忆调整问题。

### 第 1.1 步：范围和目标

询问以下问题（可以合并为单个 AskUserQuestion 并包含多个问题）：

**问题 1：范围**
- 标题： "范围"
- 问题： "我们是设计单个组件还是完整页面？"
- 选项：
  - "组件" - 可重用的 UI 元素（按钮、卡片、表单、模态框等）
  - "页面" - 完整的页面或屏幕布局

**问题 2：新建或改版**
- 标题： "类型"
- 问题： "这是一个新建设计还是对现有内容的改版？"
- 选项：
  - "新建" - 从头开始创建
  - "改版" - 改进现有组件/页面

如果选择“改版”，请询问：
**问题 3：现有路径**
- 标题： "位置"
- 问题： "现有 UI 的文件路径或路由是什么？"
- 选项： (让用户通过“其他”提供)

如果目标不明确，请根据仓库模式提出一个名称并确认。

### 第 1.2 步：痛点与灵感

**问题 1：痛点**
- 标题： "问题"
- 问题： "当前设计的顶级痛点是什么（或新设计应避免什么）？"
- 选项：
  - "过于杂乱/密集" - 信息过载，难以扫描
  - "层次结构不明确" - 主要操作不明显
  - "移动端体验差" - 在小屏幕上效果不佳
  - "过时外观" - 感觉过时或与品牌不一致
- multiSelect: true

**问题 2：视觉灵感**
- 标题： "视觉风格"
- 问题： "我应该参考哪些产品或品牌来获取视觉灵感？"
- 选项：
  - "Stripe" - 干净、极简、值得信赖
  - "Linear" - 密集、以键盘优先、面向开发者
  - "Notion" - 灵活、内容导向、有趣
  - "Apple" - 高端、宽敞、精致
- multiSelect: true

**问题 3：功能灵感**
- 标题： "交互"
- 问题： "我应该模仿哪些交互模式？"
- 选项：
  - "行内编辑" - 直接在行内编辑，无需模态框
  - "渐进式披露" - 按需显示更多内容
  - "乐观更新" - 立即反馈，后台同步
  - "键盘快捷键" - 高效用户

### 第 1.3 步：品牌和风格方向

**问题 1：品牌形容词**
- 标题： "品牌语气"
- 问题： "描述所需品牌感觉的 3-5 个形容词是什么？"
- 选项：
  - "极简" - 干净、简单、无杂乱
  - "高端" - 高端、精致、精致
  - "有趣" - 有趣、友好、易接近
  - "实用主义" - 功能性、高效、不拘小节
- multiSelect: true

**问题 2：密度**
- 标题： "密度"
- 问题： "你更喜欢哪种信息密度？"
- 选项：
  - "紧凑" - 更多信息可见，间距更紧
  - "舒适" - 平衡间距，易于扫描
  - "宽敞" - 丰富的空白，专注注意力

**问题 3：暗黑模式**
- 标题： "暗黑模式"
- 问题： "是否需要暗黑模式？"
- 选项：
  - "是" - 必须支持暗黑模式
  - "否" - 仅支持亮色模式
  - "有条件" - 如果容易实现，则支持，但不是必需的

### 第 1.4 步：用户和待办事项

**问题 1：主要用户**
- 标题： "用户"
- 问题： "主要终端用户是谁？"
- 选项：
  - "开发者" - 技术、以键盘为导向
  - "设计师" - 视觉、注重细节
  - "业务用户" - 注重效率、不太技术
  - "最终消费者" - 普通公众，技术能力各异

**问题 2：上下文**
- 标题： "上下文"
- 问题： "主要使用环境是什么？"
- 选项：
  - "以桌面优先" - 主要在大屏幕上使用
  - "以手机优先" - 主要在手机上使用
  - "两者同等" - 必须在所有设备上都能很好地工作

**问题 3：关键任务**
- 标题： "关键任务"
- 问题： "用户必须完成的前 3 个任务是什么？"
- (让用户通过“其他”提供 - 这是一个开放式问题)

### 第 1.5 步：约束

**问题 1：必须保留的元素**
- 标题： "保留"
- 问题： "是否有必须保留的元素？"
- 选项：
  - "现有文本/标签" - 保留当前文本
  - "当前字段/输入" - 保留表单结构
  - "导航结构" - 保留当前导航
  - "无" - 可以自由更改所有内容

**问题 2：技术约束**
- 标题： "约束"
- 问题： "有任何技术约束吗？"
- 选项：
  - "不添加新依赖项" - 仅使用现有库
  - "使用现有组件" - 基于当前设计系统构建
  - "必须可访问 (WCAG)" - 严格的可访问性要求
  - "无" - 无特殊约束
- multiSelect: true

---

## 第 2 阶段：生成设计简介

在访谈后，创建一个结构化的设计简介作为 JSON 并保存到 `.claude-design/design-brief.json`：

```json
{
  "scope": "component|page",
  "isRedesign": true|false,
  "targetPath": "src/components/Example.tsx",
  "targetName": "Example",
  "painPoints": ["Too dense", "Primary action unclear"],
  "inspiration": {
    "visual": ["Stripe", "Linear"],
    "functional": ["Inline validation"]
  },
  "brand": {
    "adjectives": ["minimal", "trustworthy"],
    "density": "comfortable",
    "darkMode": true
  },
  "persona": {
    "primary": "Developer",
    "context": "desktop-first",
    "keyTasks": ["Complete checkout", "Review order", "Apply discount"]
  },
  "constraints": {
    "mustKeep": ["existing fields"],
    "technical": ["no new dependencies", "WCAG accessible"]
  },
  "framework": "nextjs-app",
  "packageManager": "pnpm",
  "stylingSystem": "tailwind"
}
```

在继续之前向用户显示摘要。

---

## 第 3 阶段：生成设计实验室

### 目录结构

在 `.claude-design/` 下创建所有文件：

```
.claude-design/
├── lab/
│   ├── page.tsx                 # 主要实验室页面（特定于框架）
│   ├── variants/
│   │   ├── VariantA.tsx
│   │   ├── VariantB.tsx
│   │   ├── VariantC.tsx
│   │   ├── VariantD.tsx
│   │   └── VariantE.tsx
│   ├── components/
│   │   └── LabShell.tsx         # 实验室布局包装器
│   ├── feedback/                # 交互式反馈系统
│   │   ├── types.ts             # TypeScript 接口
│   │   ├── selector-utils.ts    # 元素识别
│   │   ├── format-utils.ts      # 反馈格式化
│   │   ├── FeedbackOverlay.tsx  # 主要覆盖组件
│   │   └── index.ts             # 模块导出
│   └── data/
│       └── fixtures.ts          # 共享模拟数据
├── design-brief.json
└── run-log.md
```

### 反馈系统设置（关键 - 绝对不能跳过）

**FeedbackOverlay 是设计实验室的主要功能。** 没有它，用户无法提供交互式反馈。绝对不能在没有 FeedbackOverlay 的情况下生成设计实验室。

**可靠性策略：** 为了避免不同项目配置之间的导入路径问题，将 FeedbackOverlay **直接在路由目录中创建**（例如，`app/design-lab/FeedbackOverlay.tsx`），**不要**在 `.claude-design/` 中创建。这确保了简单的相对导入（`./FeedbackOverlay`）始终有效。

**所需文件在路由目录中：**
```
app/design-lab/           # 或 app/__design_lab/ 如果下划线有效
├── page.tsx              # 主要实验室页面，包含变体
└── FeedbackOverlay.tsx   # 自包含的覆盖组件（从模板复制）
```

**模板来源：** `design-and-refine/templates/feedback/FeedbackOverlay.tsx`

**这种方法的理由：**
- `.claude-design/` 路径可能由于打包器配置而失败
- 相对导入从同一目录始终有效
- 路由目录在任何时候都会被删除

### 路由集成

**Next.js 应用程序路由器：**
创建 `app/__design_lab/page.tsx`，它从 `.claude-design/lab/` 导入

**Next.js 页面路由器：**
创建 `pages/__design_lab.tsx`，它从 `.claude-design/lab/` 导入

**Vite React：**
- 如果存在 React Router：添加路由到 `/__design_lab`
- 如果没有路由：在 `App.tsx` 中根据 `?design_lab=true` 查询参数进行条件渲染

**其他框架：**
为检测到的框架创建最合适的临时路由。

### 变体生成指南

**重要：** 阅读 `DESIGN_PRINCIPLES.md` 以获取 UX、交互和运动的最佳实践。但**不要**使用预定义的视觉样式——从项目中推断它们。

**应用通用原则（来自 `DESIGN_PRINCIPLES.md`）：**
- **UX**: Nielsen 的启发式方法，认知负荷减少，渐进式披露
- **组件行为**: 按钮状态，表单结构，卡片结构
- **交互**: 反馈模式，状态处理，乐观更新
- **运动**: 时间（150-300ms），缓动（退出时使用 ease-out，进入时使用 ease-in）
- **可访问性**: 聚焦状态，ARIA 模式，触摸目标（最小 44px）

**从项目中推断视觉样式：**
- 颜色 → 来自 Tailwind 配置，CSS 变量或现有组件
- 字体排印 → 来自代码库中的现有标题，正文文本
- 间距 → 来自项目的间距尺度或现有模式
- 边框半径 → 来自现有的卡片，按钮，输入
- 阴影 → 来自现有的提升组件

---

每个变体必须探索一个不同的设计轴。不要创建微小的变体——使它们有意义的区别。**使用项目的现有视觉语言为所有变体。**

**变体 A：信息层次结构重点**
- 重组内容层次结构（什么是最重要的？）
- 应用格式邻近性——将相关项目组合得更近
- 每个视图只有一个主要操作
- 使用现有的字体排印尺度创建清晰的级别

**变体 B：布局模型探索**
- 尝试不同的布局方法（卡片 vs 列表 vs 表格 vs 分割面板）
- 应用卡片解剖或表格行为模式从 `DESIGN_PRINCIPLES`
- 考虑在每个断点处的响应式行为
- 使用项目的现有网格/布局系统

**变体 C：密度变化**
- 如果简介说“舒适”，尝试更紧凑的版本
- 如果简介说“紧凑”，尝试更宽敞的版本
- 使用项目的现有间距标记——只是以不同的方式应用它们
- 显示权衡：更多可见数据 vs 更容易扫描

**变体 D：交互模型**
- 不同的交互模式（模态框 vs 行内 vs 面板 vs 抽屉）
- 应用反馈模式：立即 → 进度 → 完成
- 实现所有所需状态（加载中，错误，空，禁用）
- 考虑对非破坏性操作进行乐观更新

**变体 E：表达方向**
- 推动用户在访谈中描述的品牌方向
- 探索项目现有设计标记的不同用法
- 更多或更少使用阴影，边框，背景颜色
- 在添加意义的地方应用运动（悬停，聚焦，过渡）

### 实验室页面要求

设计实验室页面必须包含：

1. **标题** with:
   - 设计简介摘要（目标，范围，关键要求）
   - 审查说明

2. **变体网格** with:
   - 清晰的标签 (A, B, C, D, E)
   - 每个变体的简要说明（“为什么存在”）
   - 实际渲染的变体
   - 突出显示关键差异
   - **重要：** 每个变体容器必须有 `data-variant="X"` 属性（其中 X 是 A, B, C, D, E 或 F）。这是反馈系统识别哪些评论属于哪个变体的必要条件。

3. **响应式行为**:
   - 桌面：并排网格（2-3 列）
   - 手机：水平滚动或标签

4. **共享数据**:
   - 所有变体使用来自 `data/fixtures.ts` 的相同固定数据
   - 确保公平比较

5. **反馈覆盖**（关键 - 绝对不能省略）:

   ⚠️ **这是最重要的要求** ⚠️

   FeedbackOverlay 允许用户点击元素并留下评论。没有它，设计实验室只是一个静态页面，没有收集结构化反馈的方式。

   - 在与 `page.tsx` 相同的目录中创建 `FeedbackOverlay.tsx`
   - 使用相对路径导入：`import { FeedbackOverlay } from './FeedbackOverlay'`
   - 在页面末尾渲染，在所有变体之后
   - 传递 `targetName` 属性与组件/页面名称

   **示例集成:**

```tsx
import { FeedbackOverlay } from './FeedbackOverlay';  // 相对导入 - 始终有效

export default function DesignLabPage() {
  return (
    <div className="min-h-screen bg-background">
      <header>...</header>

      <main>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div data-variant="A">
            <VariantA />
          </div>
          <div data-variant="B">
            <VariantB />
          </div>
          {/* ... 更多变体 */}
        </div>
      </main>

      {/* 关键：必须包含 FeedbackOverlay */}
      <FeedbackOverlay targetName="ComponentName" />
    </div>
  );
}
```

   **如果你遗漏了 FeedbackOverlay，用户无法提供反馈。** 这使得设计实验室失去其全部意义。

---

## 第 7 阶段：最终预览

一旦用户满意：

1. 创建 `.claude-design/preview/` 目录:
   ```
   .claude-design/preview/
   ├── page.tsx                    # 预览页面
   └── FinalDesign.tsx             # 获胜设计
   ```

2. 创建路由在 `/__design_preview`

3. 对于改版，包括前后比较：
   - 切换开关或分割视图
   - 显示原始内容与建议内容

4. 询问最终确认:

**问题：确认最终设计？**
- 标题： "确认"
- 问题： "准备好最终确定这个设计了吗？"
- 选项：
  - "是，最终确定它" - 进行清理并生成实施计划
  - "不，需要修改" - 告诉我需要调整的内容
  - "中止 - 取消所有内容" - 删除所有临时文件，不生成计划

如果“不，需要修改”：收集反馈并迭代。
如果“中止”：进行 **中止处理** 下面操作。

---

## 中止处理

如果用户在任何阶段想要取消/中止流程（不只是最终确认），他们可能会说：
- "取消"
- "中止"
- "停止"
- "不必在意"
- "忘记它"
- "我改变了主意"

当检测到中止时：

1. **确认中止:**
   - "确定要取消吗？这将删除我创建的所有设计实验室文件。"

2. **如果确认，立即清理:**
   - 删除 `.claude-design/` 目录完全
   - 删除临时路由文件 (`app/__design_lab/`, 等)
   - 不要生成任何实施计划
   - 不要更新设计记忆

3. **确认:**
   - "设计探索已取消。已清理所有临时文件。稍后如果您想重新开始，请告诉我。"

---

## 第 8 阶段：最终确定

当用户确认（选择“是，最终确定它”）：

### 第 8.1: 清理

删除所有临时文件：
- 删除 `.claude-design/` 目录完全
- 删除临时路由文件：
  - `app/__design_lab/` (Next.js 应用程序路由器)
  - `pages/__design_lab.tsx` (Next.js 页面路由器)
  - `app/__design_preview/`
  - `pages/__design_preview.tsx`
  - 修改 `App.tsx` 的任何修改（Vite）

**安全规则：**
- 仅删除 `.claude-design/` 内的文件
- 仅删除插件创建的路由文件
- 绝对不要删除用户编写的文件
- 删除前请验证文件路径

### 第 8.2: 生成实施计划

在项目根目录中创建 `DESIGN_PLAN.md`:

```markdown
# 设计实施计划：[TargetName]

## 摘要
- **范围：** [component/page]
- **目标：** [file path]
- **获胜变体：** [A-E]
- **关键改进：** [来自反馈]

## 要更改的文件
- [ ] `src/components/Example.tsx` - 主要组件重构
- [ ] `src/styles/example.css` - 样式更新
- [ ] ... (列出所有受影响的文件)

## 实施步骤
1. [具体的步骤与代码指导]
2. [下一步]
3. ...

## 组件 API
- **属性:**
  - `prop1: type` - 描述
  - ...
- **状态:**
  - 内部状态要求
- **事件:**
  - 回调和处理器

## 所需 UI 状态
- **加载中：** [描述]
- **空：** [描述]
- **错误：** [描述]
- **禁用：** [描述]
- **验证：** [描述]

## 可访问性检查清单
- [ ] 键盘导航工作
- [ ] 聚焦状态可见
- [ ] 标签和 aria-* 属性正确
- [ ] 色彩对比符合 WCAG AA
- [ ] 屏幕阅读器测试

## 测试检查清单
- [ ] 单元测试逻辑
- [ ] 组件测试渲染
- [ ] 视觉回归测试（如果适用）
- [ ] E2E 烟雾测试（如果适用）

## 设计标记
- [要添加的新标记]
- [要使用的现有标记]

---

*由设计变化插件生成*
```

### 第 8.3: 更新设计记忆

创建或更新 `DESIGN_MEMORY.md`:

如果新建文件:
```markdown
# 设计记忆

## 品牌语气
- **形容词：** [来自访谈]
- **避免：** [反模式发现]

## 布局与间距
- **密度：** [偏好]
- **网格：** [如果已建立]
- **圆角：** [如果一致]
- **阴影：** [如果一致]

## 字体排印
- **标题：** [字体, 重量使用]
- **正文：** [字体, 大小]
- **强调：** [模式]

## 色彩
- **主要：** [色彩标记]
- **次要：** [色彩标记]
- **中性策略：** [方法]
- **语义色彩：** [错误, 成功, 警告]

## 交互模式
- **表单：** [验证方法, 布局]
- **模态框/抽屉：** [何时使用哪个]
- **表格/列表：** [首选模式]
- **反馈：** [toast, 行内, 等]

## 可访问性规则
- **聚焦：** [可见聚焦方法]
- **标签：** [标签约定]
- **运动：** [减少运动支持]

## 仓库约定
- **组件结构：** [文件组织]
- **样式方法：** [Tailwind 类, CSS 模块, 等]
- **现有原语：** [Button, Input, Card, 等]

---

## 错误处理

### 框架未检测到
如果无法检测到框架：
- 询问用户: "我无法检测到您的框架。您使用的是什么？"
- 提供常见选项: Next.js, Vite, Create React App, Vue, 等

### 开发服务器失败
如果开发服务器无法启动：
- 检查端口冲突
- 提供手动说明
- 建议用户自己启动服务器

### 路由集成失败
如果无法创建临时路由：
- 落回创建独立的 HTML 文件
- 提供手动预览说明

### 清理中断
如果清理中断：
- 记录已删除与剩余的内容
- 提供手动清理说明
- 不要留下部分状态而没有通知用户

---

## 配置选项

插件支持这些可选配置（通过环境或项目配置）：

- `DESIGN_AUTO_IMPLEMENT`: 如果 `true`, 确认后立即实施计划
- `DESIGN_KEEP_LAB`: 如果为 `true`, 不要删除实验室，直到明确的清理命令
- `DESIGN_MEMORY_PATH`: 设计记忆文件的自定义路径

---

## 示例会话流程

1. 用户: `/design-variations:design CheckoutSummary`
2. 插件检测: Next.js App Router, Tailwind, pnpm
3. 插件发现: 没有现有的设计记忆
4. 插件询问: 访谈问题（5 步）
5. 插件生成: 设计简介摘要
6. 插件创建: `.claude-design/lab/` 与 5 个变体
7. 插件创建: `app/__design_lab/page.tsx`
8. 插件启动: `pnpm dev`
9. 插件输出: "打开 http://localhost:3000/__design_lab"
10. 用户在浏览器中审查变体
11. 插件询问: "哪个变体获胜？"
12. 用户: "Variant C, 但更改 X 和 Y"
13. 插件细化: 更新 Variant C
14. 用户: "看起来不错"
15. 插件创建: 最终预览在 `/__design_preview`
16. 用户: "确认"
17. 插件: 删除所有临时文件
18. 插件: 生成 `DESIGN_PLAN.md`
19. 插件: 创建 `DESIGN_MEMORY.md`
20. 插件: "完成！查看 DESIGN_PLAN.md 以获取实施步骤"
