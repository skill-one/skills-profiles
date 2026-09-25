此技能通过按顺序运行每个技能来协调完整的设计师工作流程。您是引导设计师完成每个阶段的向导。不要催促。每个阶段必须完成后确认才能进入下一阶段。

## 示例提示

- "运行完整设计流程"
- "带我完成新项目的完整流程"
- "从零开始，带我完成所有步骤"
- "仪表盘应用的设计流程"

## 顺序

```
1. Grill Me          → 澄清思路
2. Design Brief      → 记录意图
3. Info Architecture  → 定义结构
4. Design Tokens     → 建立视觉系统
5. Brief to Tasks    → 规划构建
6. Frontend Design   → 构建
—
7. Design Review     → 准备好时单独运行
```

## 规则

1. **开始时**，告诉设计师完整流程的步骤（1-6阶段，7阶段可单独运行）并询问是否要跳过任何阶段。常见跳过模式：
   - 已有清晰想法 → 跳过 Grill Me
   - 单个组件，非完整页面 → 跳过信息架构
   - 现有项目含 token → 跳过设计 token

2. **每个阶段开始前**，宣布进入的阶段及其产出物。示例："阶段2：设计简报。我将向您提问关于项目并生成 DESIGN_BRIEF.md 文件。准备好了吗？"

3. **每个阶段中**，阅读对应的 SKILL.md 文件并遵循其完整指令。不要总结或简略技能。正确运行。

4. **每个阶段结束后**，总结产出物（文件名、关键决策、任何开放问题）并询问："准备好进入下一阶段了吗？" 等待确认。

5. **阶段之间**，检查上一阶段的输出是否影响下一阶段。例如，如果简报命名了理念，则 token 阶段将使用它。

6. **设计师可随时停止**。如果他们表示"现在足够了"，总结他们当前的流程位置和返回时将进入的阶段。

## 阶段详情

### 阶段1：Grill Me

阅读 `grill-me` 技能（grill-me/SKILL.md）并遵循其指令。
**产出**：项目共同理解。无文件输出。
**过渡**："我们已解决关键决策。准备好将此记录为设计简报了吗？"

### 阶段2：设计简报

阅读 `design-brief` 技能（design-brief/SKILL.md）并遵循其指令。
**产出**：`.design/<feature-slug>/DESIGN_BRIEF.md`。
**过渡**："简报已保存。下一步是信息架构，我们将定义页面结构和导航。构建单个组件可跳过此阶段。继续？"

### 阶段3：信息架构

阅读 `information-architecture` 技能（information-architecture/SKILL.md）并遵循其指令。
**产出**：`.design/<feature-slug>/INFORMATION_ARCHITECTURE.md`。
**过渡**："IA 已定义。接下来我们将基于简报中的理念生成设计 token（颜色、间距、字体、阴影）。继续？"

### 阶段4：设计 Token

阅读 `design-tokens` 技能（design-tokens/SKILL.md）并遵循其指令。
**产出**：Token 文件（CSS 变量、Tailwind 配置或主题文件，取决于技术栈）。
**过渡**："Token 已设置。接下来我将简报拆分为任务列表以便按顺序构建。继续？"

### 阶段5：简报到任务

阅读 `brief-to-tasks` 技能（brief-to-tasks/SKILL.md）并遵循其指令。
**产出**：`.design/<feature-slug>/TASKS.md`。
**过渡**："任务已准备就绪。现在我们开始构建。我将从列表中的第一个任务开始。继续？"

### 阶段6：前端设计

阅读 `frontend-design` 技能（frontend-design/SKILL.md）并遵循其指令。
按顺序处理 `TASKS.md` 中的任务。完成每个任务后，检查并确认设计师再进入下一个任务。
**产出**：构建的组件和页面。
**过渡**："流程已完成。您的简报、IA、token 和任务都已保存在项目中。准备好设计评审时，运行 `/design-review` 并我将根据简报评审构建。"

**流程在此结束。** 阶段7不会自动运行。

### 阶段7：设计评审（仅按需运行）

此阶段**不会自动运行**。仅在以下情况运行：

- 设计师在流程中明确要求评审
- 设计师构建后单独运行 `/design-review`

评审需要已构建的代码进行检查。如果尚未构建组件或页面，则不要运行此阶段。改为提醒设计师："构建一些内容后运行 `/design-review`。它将根据简报检查输出。"

触发时，阅读 `design-review` 技能（design-review/SKILL.md）并遵循其指令。评审将使用 Playwright MCP（首选）、Cursor IDE 浏览器（备用）或如果无浏览器工具则要求用户手动提供截图。

**产出**：`.design/<feature-slug>/DESIGN_REVIEW.md` + 保存于 `.design/<feature-slug>/screenshots/` 的截图。
**过渡**："评审完成。截图保存在 `.design/<feature-slug>/screenshots/`。如果有必须修复项，我可以现在处理。"

## 项目文件结构

所有设计流程产出物保存在 `.design/<feature-slug>/` 下，其中 `<feature-slug>` 是来自所设计功能的简短、小写、连字符命名的名称。这确保多个功能可以独立设计而不互相覆盖。

```
.design/
└── <feature-slug>/
    ├── DESIGN_BRIEF.md              ← 阶段2：项目意图、目标、美学方向
    ├── INFORMATION_ARCHITECTURE.md  ← 阶段3：导航、页面结构、用户流程
    ├── DESIGN_TOKENS.*              ← 阶段4：颜色、间距、字体、阴影（CSS/Tailwind/主题）
    ├── TASKS.md                     ← 阶段5：从简报生成的有序构建清单
    ├── DESIGN_REVIEW.md             ← 阶段7：根据简报的优先级评审
    └── screenshots/                 ← 阶段7：运行应用的视觉证据
        ├── review-[page]-desktop-1280.png
        ├── review-[page]-tablet-768.png
        ├── review-[page]-mobile-375.png
        ├── review-[page]-dark-mode-*.png
        └── review-[component]-[state].png
```

`screenshots/` 子文件夹在设计评审阶段创建。所有评审视觉证据（响应式断点、交互状态、暗黑模式）都保存在此处，文件名描述性命名以便 `DESIGN_REVIEW.md` 中的发现可追溯。

## 如果设计师中途返回

检查 `.design/` 文件夹中的现有功能子文件夹。如果功能文件夹内存在早期阶段的文件（DESIGN_BRIEF.md、INFORMATION_ARCHITECTURE.md、TASKS.md），则读取它们以了解设计师中途的位置。如果存在多个文件夹，询问要恢复哪个功能。从下一个未完成的阶段继续。
