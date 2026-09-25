# Penpot UI/UX 设计指南

使用 `penpot/penpot-mcp` MCP 服务器和成熟的 UI/UX 原则，在 Penpot 中创建专业、以用户为中心的设计。

## 可用的 MCP 工具

| 工具 | 目的 |
| ---- | ------- |
| `mcp__penpot__execute_code` | 在 Penpot 插件上下文中运行 JavaScript 以创建/修改设计 |
| `mcp__penpot__export_shape` | 将形状导出为 PNG/SVG 以进行视觉检查 |
| `mcp__penpot__import_image` | 将图像（图标、照片、标志）导入设计 |
| `mcp__penpot__penpot_api_info` | 获取 Penpot API 文档 |

## MCP 服务器设置

Penpot MCP 工具需要本地运行的 `penpot/penpot-mcp` 服务器。有关详细的安装和故障排除信息，请参阅 [setup-troubleshooting.md](references/setup-troubleshooting.md)。

### 设置前：检查是否已运行

**始终在尝试设置之前检查 MCP 服务器是否已可用：**

1. **首先尝试调用工具**：尝试 `mcp__penpot__penpot_api_info` - 如果它成功，则服务器正在运行并已连接。无需设置。

2. **如果工具失败**，询问用户：
   > "Penpot MCP 服务器似乎未连接。服务器是否已安装并正在运行？如果是，我可以帮助您进行故障排除。如果不是，我可以指导您完成设置。"

3. **仅当用户确认服务器未安装时，才继续执行设置说明。**

### 快速入门（仅当未安装时）

```bash
# 克隆并安装
git clone https://github.com/penpot/penpot-mcp.git
cd penpot-mcp
npm install

# 构建并启动服务器
npm run bootstrap
```

然后在 Penpot 中：
1. 打开一个设计文件
2. 转到 **插件** → **从 URL 加载插件**
3. 输入：`http://localhost:4400/manifest.json`
4. 点击插件 UI 中的 **"连接到 MCP 服务器"**

### VS Code 配置

添加到 `settings.json`：
```json
{
  "mcp": {
    "servers": {
      "penpot": {
        "url": "http://localhost:4401/sse"
      }
    }
  }
}
```

### 故障排除（如果服务器已安装但无法工作）

| 问题 | 解决方案 |
| ----- | -------- |
| 插件无法连接 | 检查服务器是否正在运行 (`npm run start:all` 在 penpot-mcp 目录中) |
| 浏览器阻止本地网络 | 允许本地网络访问提示，或禁用 Brave Shield，或尝试 Firefox |
| 客户端未显示工具 | 完全重新启动 VS Code/Claude 后配置更改 |
| 工具执行失败/超时 | 确保 Penpot 插件 UI 打开并显示 "已连接" |
| "WebSocket 连接失败" | 检查防火墙是否允许端口 4400、4401、4402 |

## 快速参考

| 任务 | 参考文件 |
| ---- | -------------- |
| MCP 服务器安装和故障排除 | [setup-troubleshooting.md](references/setup-troubleshooting.md) |
| 组件规范（按钮、表单、导航） | [component-patterns.md](references/component-patterns.md) |
| 可访问性（对比度、触摸目标） | [accessibility.md](references/accessibility.md) |
| 屏幕尺寸和平台规范 | [platform-guidelines.md](references/platform-guidelines.md) |

## 核心设计原则

### 黄金法则

1. **清晰胜于巧妙**：每个元素都必须有其目的
2. **一致性建立信任**：重用模式、颜色和组件
3. **用户目标优先**：为任务而设计，而非功能
4. **可访问性不是可选项**：为所有人设计
5. **使用真实用户进行测试**：尽早验证假设

### 视觉层次结构（优先级顺序）

1. **大小**：更大 = 更重要
2. **颜色/对比度**：高对比度吸引注意力
3. **位置**：左上角（从左到右）首先被看到
4. **空白**：隔离强调重要性
5. **字体粗细**：粗体突出显示

## 设计工作流程

1. **首先检查设计系统**：询问用户是否有现有的令牌/规范，或从当前的 Penpot 文件中发现
2. **理解页面**：使用 `mcp__penpot__execute_code` 调用 `penpotUtils.shapeStructure()` 以查看层次结构
3. **查找元素**：使用 `penpotUtils.findShapes()` 通过类型或名称定位元素
4. **创建/修改**：使用 `penpot.createBoard()`、`penpot.createRectangle()`、`penpot.createText()` 等
5. **应用布局**：使用 `addFlexLayout()` 用于响应式容器
6. **验证**：调用 `mcp__penpot__export_shape` 以视觉检查您的工作

## 设计系统处理

**在创建设计之前，确定用户是否有现有的设计系统：**

1. **询问用户**："您要遵循设计系统或品牌指南吗？"
2. **从 Penpot 发现**：检查现有的组件、颜色和模式

```javascript
// 发现当前文件中的现有设计模式
const allShapes = penpotUtils.findShapes(() => true, penpot.root);

// 查找使用的现有颜色
const colors = new Set();
allShapes.forEach(s => {
  if (s.fills) s.fills.forEach(f => colors.add(f.fillColor));
});

// 查找现有文本样式（字体大小、粗细）
const textStyles = allShapes
  .filter(s => s.type === 'text')
  .map(s => ({ fontSize: s.fontSize, fontWeight: s.fontWeight }));

// 查找现有组件
const components = penpot.library.local.components;

return { colors: [...colors], textStyles, componentCount: components.length };
```

**如果用户有设计系统：**

- 使用其指定的颜色、间距、字体
- 匹配其现有的组件模式
- 遵循其命名约定

**如果用户没有设计系统：**

- 使用以下默认令牌作为起点
- 提供帮助建立一致模式
- 参考 [component-patterns.md](references/component-patterns.md) 中的规范

## 关键 Penpot API 注意事项

- `width`/`height` 是只读的 → 使用 `shape.resize(w, h)`
- `parentX`/`parentY` 是只读的 → 使用 `penpotUtils.setParentXY(shape, x, y)`
- 使用 `insertChild(index, shape)` 进行 z 排序（不是 `appendChild`）
- Flex 子元素数组顺序对于 `dir="column"` 或 `dir="row"` 是反转的
- 在 `text.resize()` 后，将 `growType` 重置为 `"auto-width"` 或 `"auto-height"`

## 新建板的位置

**在创建新板之前始终检查现有板**以避免重叠：

```javascript
// 查找所有现有板并计算下一个位置
const boards = penpotUtils.findShapes(s => s.type === 'board', penpot.root);
let nextX = 0;
const gap = 100; // 板之间的间距

if (boards.length > 0) {
  // 找到最右侧的板边缘
  boards.forEach(b => {
    const rightEdge = b.x + b.width;
    if (rightEdge + gap > nextX) {
      nextX = rightEdge + gap;
    }
  });
}

// 在计算的位置创建新板
const newBoard = penpot.createBoard();
newBoard.x = nextX;
newBoard.y = 0;
newBoard.resize(375, 812);
```

**板间距指南：**

- 使用 100px 间距分隔相关屏幕（相同流程）
- 使用 200px+ 间距分隔不同部分/流程
- 垂直对齐板（相同 y）以进行视觉组织
- 按用户流程顺序水平分组相关屏幕

## 默认设计令牌

**仅在用户没有设计系统时使用这些默认值。如果可用，始终优先使用用户的令牌。**

### 间距比例（8px 基础）

| 令牌 | 值 | 使用 |
| ----- | ----- | ----- |
| `spacing-xs` | 4px | 紧凑的行内元素 |
| `spacing-sm` | 8px | 相关元素 |
| `spacing-md` | 16px | 默认填充 |
| `spacing-lg` | 24px | 章节间距 |
| `spacing-xl` | 32px | 主要章节 |
| `spacing-2xl` | 48px | 页面级间距 |

### 字体大小比例

| 级别 | 大小 | 粗细 | 使用 |
| ----- | ---- | ------ | ----- |
| 显示 | 48-64px | 粗体 | 英雄标题 |
| H1 | 32-40px | 粗体 | 页面标题 |
| H2 | 24-28px | 半粗体 | 章节标题 |
| H3 | 20-22px | 半粗体 | 子章节 |
| 正文 | 16px | 常规 | 主要内容 |
| 小号 | 14px | 常规 | 次要文本 |
| 标签 | 12px | 常规 | 标签、提示 |

### 颜色使用

| 目的 | 建议 |
| ------- | -------------- |
| 主要 | 主要品牌颜色、CTA |
| 次要 | 支持操作 |
| 成功 | #22C55E 范围（确认） |
| 警告 | #F59E0B 范围（注意） |
| 错误 | #EF4444 范围（错误） |
| 中性 | 灰度用于文本/边框 |

## 常见布局

### 手机屏幕 (375×812)

```text
┌─────────────────────────────┐
│ 状态栏 (44px)               │
├─────────────────────────────┤
│ 头部/导航 (56px)            │
├─────────────────────────────┤
│                             │
│ 内容区域                   │
│ (可滚动)                   │
│ 填充：水平 16px            │
│                             │
├─────────────────────────────┤
│ 底部导航/CTA (84px)        │
└─────────────────────────────┘

```

### 桌面仪表板 (1440×900)

```text
┌──────┬──────────────────────────────────┐
│      │ 头部 (64px)                    │
│ 侧边 │──────────────────────────────────│
│ 框   │ 页面标题 + 操作                 │
│      │──────────────────────────────────│
│ 240  │ 内容网格                       │
│ px   │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │
│      │ │卡片 │ │卡片 │ │卡片 │ │卡片 │ │
│      │ └─────┘ └─────┘ └─────┘ └─────┘ │
│      │                                  │
└──────┴──────────────────────────────────┘

```

## 组件检查清单

### 按钮

- [ ] 清晰、以行动为导向的标签（2-3 个词）
- [ ] 最小触摸目标：44×44px
- [ ] 视觉状态：默认、悬停、激活、禁用、加载中
- [ ] 足够的对比度（背景 3:1）
- [ ] 应用程序中一致的边框半径

### 表单

- [ ] 标签在输入框上方（不只是占位符）
- [ ] 必填字段指示器
- [ ] 错误消息紧邻字段
- [ ] 逻辑的 Tab 顺序
- [ ] 输入类型匹配内容（电子邮件、电话等）

### 导航

- [ ] 清晰地指示当前位置
- [ ] 在屏幕之间位置一致
- [ ] 最多 7±2 个顶级项目
- [ ] 移动设备上触摸友好（48px 目标）

## 可访问性快速检查

1. **颜色对比度**：文本 4.5:1，大文本 3:1
2. **触摸目标**：最小 44×44px
3. **焦点状态**：可见的键盘焦点指示器
4. **替代文本**：图像的描述性说明
5. **层次结构**：适当的标题级别（H1→H2→H3）
6. **颜色独立性**：从不完全依赖颜色

## 设计审查检查清单

在最终确定任何设计之前：

- [ ] 视觉层次结构清晰
- [ ] 一致的间距和对齐
- [ ] 字体大小可读（正文 16px+）
- [ ] 颜色对比度符合 WCAG AA
- [ ] 交互元素明显
- [ ] 移动设备友好的触摸目标
- [ ] 考虑加载/空/错误状态
- [ ] 与设计系统一致

## 验证设计

使用 `mcp__penpot__execute_code` 和这些验证方法：

| 检查 | 方法 |
| ----- | ------ |
| 超出边界的元素 | `penpotUtils.analyzeDescendants()` 与 `isContainedIn()` |
| 文本太小（<12px） | `penpotUtils.findShapes()` 通过 `fontSize` 过滤 |
| 缺少对比度 | 调用 `mcp__penpot__export_shape` 并进行视觉检查 |
| 层次结构结构 | `penpotUtils.shapeStructure()` 审查嵌套 |

### 导出 CSS

使用 `penpot.generateStyle(selection, { type: 'css', includeChildren: true })` 通过 `mcp__penpot__execute_code` 从设计提取 CSS。

## 优秀设计的技巧

1. **从内容开始**：真实内容揭示了布局需求
2. **首先为移动设备设计**：限制激发了创造力
3. **使用网格**：8px 基础网格保持对齐
4. **限制颜色**：1 个主要 + 1 个次要 + 中性
5. **限制字体**：最多 1-2 种字体
6. **拥抱空白**：呼吸空间提高了理解力
7. **保持一致性**：相同操作 = 相同外观
8. **提供反馈**：每个操作都需要响应
