---
name: excalidraw-diagram-generator
description: 根据自然语言描述生成 Excalidraw 图表。当被要求“创建图表”、“制作流程图”、“可视化流程”、“绘制系统架构”、“创建思维导图”或“生成 Excalidraw 文件”时使用。支持流程图、关系图、思维导图和系统架构图。输出可在 Excalidraw 中直接打开的 .excalidraw JSON 文件。
---

# Excalidraw 图表生成器

一个技能，用于根据自然语言描述生成 Excalidraw 格式的图表。该技能有助于在不手动绘制的情况下创建流程、系统、关系和想法的可视化表示。

## 何时使用此技能

当用户请求时，使用此技能：

- "创建一个显示..."
- "制作一个流程图..."
- "可视化流程..."
- "绘制系统架构..."
- "生成一个关于...的思维导图..."
- "创建一个 Excalidraw 文件..."
- "显示...之间的关系..."
- "绘制工作流..."

**支持的图表类型：**
- 📊 **流程图**：顺序流程、工作流、决策树
- 🔗 **关系图**：实体关系、系统组件、依赖关系
- 🧠 **思维导图**：概念层次结构、头脑风暴结果、主题组织
- 🏗️ **架构图**：系统设计、模块交互、数据流
- 📈 **数据流图 (DFD)**：数据流可视化、数据转换过程
- 🏊 **业务流 (泳道)**：跨职能工作流、基于角色的流程流
- 📦 **类图**：面向对象设计、类结构和关系
- 🔄 **时序图**：对象随时间的交互、消息流
- 🗃️ **ER 图**：数据库实体关系、数据模型

## 前置条件

- 清晰地描述要可视化的内容
- 确定关键实体、步骤或概念
- 理解元素之间的关系或流程

## 分步工作流程

### 第 1 步：理解请求

分析用户的描述以确定：

1. **图表类型**（流程图、关系图、思维导图、架构图）
2. **关键元素**（实体、步骤、概念）
3. **关系**（流程、连接、层次结构）
4. **复杂度**（元素数量）

### 第 2 步：选择合适的图表类型

| 用户意图 | 图表类型 | 示例关键词 |
|-------------|--------------|------------------|
| 流程、步骤、程序 | **流程图** | "工作流"、"流程"、"步骤"、"程序" |
| 连接、依赖、关联 | **关系图** | "关系"、"连接"、"依赖"、"结构" |
| 概念层次结构、头脑风暴 | **思维导图** | "思维导图"、"概念"、"想法"、"分解" |
| 系统设计、组件 | **架构图** | "架构"、"系统"、"组件"、"模块" |
| 数据流、转换过程 | **数据流图 (DFD)** | "数据流"、"数据处理"、"数据转换" |
| 跨职能流程、角色责任 | **业务流 (泳道)** | "业务流程"、"泳道"、"角色"、"责任" |
| 面向对象设计、类结构 | **类图** | "类"、"继承"、"OOP"、"对象模型" |
| 交互序列、消息流 | **时序图** | "序列"、"交互"、"消息"、"时间线" |
| 数据库设计、实体关系 | **ER 图** | "数据库"、"实体"、"关系"、"数据模型" |

### 第 3 步：提取结构化信息

**对于流程图：**
- 顺序步骤列表
- 决策点（如有）
- 开始和结束点

**对于关系图：**
- 实体/节点（名称 + 可选描述）
- 实体之间的关系（从 → 到，带标签）

**对于思维导图：**
- 中心主题
- 主要分支（建议 3-6 个）
- 每个分支的子主题（可选）

**对于数据流图 (DFD)：**
- 数据源和目的地（外部实体）
- 过程（数据转换）
- 数据存储（数据库、文件）
- 数据流（箭头显示从左到右或从左上到右下的数据移动）
- **重要**：不要表示流程顺序，仅表示数据流

**对于业务流 (泳道)：**
- 角色/参与者（部门、系统、人员）- 显示为标题列
- 流程泳道（每个角色的垂直泳道）
- 流程框（每个泳道内的活动）
- 流程箭头（连接流程框，包括跨泳道交接）

**对于类图：**
- 带名称的类
- 带可见性的属性（+，-，#）
- 带参数的带可见性的方法
- 关系：继承（实线 + 白色三角形）、实现（虚线 + 白色三角形）、关联（实线）、依赖（虚线）、聚合（实线 + 白色菱形）、组合（实线 + 填充菱形）
- 多重性符号（1，0..1，1..*，*）

**对于时序图：**
- 对象/参与者（水平排列在顶部）
- 生命线（每个对象的垂直线）
- 消息（生命线之间的水平箭头）
- 同步消息（实线箭头）、异步消息（虚线箭头）
- 返回值（虚线箭头）
- 激活框（执行期间生命线上的矩形）
- 时间流从上到下

**对于 ER 图：**
- 实体（带有实体名称的矩形）
- 属性（列在实体内部）
- 主键（下划线或标记为 PK）
- 外键（标记为 FK）
- 关系（连接实体的线）
- 基数：1:1（一对一）、1:N（一对多）、N:M（多对多）
- 连接/关联实体用于多对多关系（虚线矩形）

### 第 4 步：生成 Excalidraw JSON

创建带有适当元素的 `.excalidraw` 文件：

**可用的元素类型：**
- `rectangle`：用于实体、步骤、概念的方框
- `ellipse`：强调的替代形状
- `diamond`：决策点
- `arrow`：方向连接
- `text`：标签和注释

**要设置的关键属性：**
- **位置**：`x`，`y` 坐标
- **大小**：`width`，`height`
- **样式**：`strokeColor`，`backgroundColor`，`fillStyle`
- **字体**：`fontFamily: 5`（Excalifont - **所有文本元素必需**）
- **文本**：嵌入的文本用于标签
- **连接**：`points` 数组用于箭头

**重要**：所有文本元素必须使用 `fontFamily: 5`（Excalifont）以保持一致的视觉外观。

### 第 5 步：格式化输出

结构化完整的 Excalidraw 文件：

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    // 图表元素数组
  ],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

### 第 6 步：保存并提供说明

1. 保存为 `<描述性名称>.excalidraw`
2. 告知用户如何打开：
   - 访问 https://excalidraw.com
   - 点击 "打开" 或拖放文件
   - 或使用 Excalidraw VS Code 扩展

## 最佳实践

### 元素数量指南

| 图表类型 | 推荐数量 | 最大值 |
|--------------|-------------------|---------|
| 流程图步骤 | 3-10 | 15 |
| 关系实体 | 3-8 | 12 |
| 思维导图分支 | 4-6 | 8 |
| 每个分支的思维导图子主题 | 2-4 | 6 |

### 布局技巧

1. **起始位置**：将重要元素居中，使用一致间距
2. **间距**：
   - 水平间距：元素之间 200-300px
   - 垂直间距：行之间 100-150px
3. **颜色**：使用一致的颜色方案
   - 主要元素：浅蓝色 (`#a5d8ff`)
   - 次要元素：浅绿色 (`#b2f2bb`)
   - 重要/中心：黄色 (`#ffd43b`)
   - 警报/警告：浅红色 (`#ffc9c9`)
4. **文本大小**：16-24px 以提高可读性
5. **字体**：始终使用 `fontFamily: 5`（Excalifont）用于所有文本元素
6. **箭头样式**：使用直线箭头表示简单流程，曲线箭头表示复杂关系

### 复杂度管理

**如果用户请求包含太多元素：**
- 建议拆分为多个图表
- 首先关注主要元素
- 提供创建详细子图表的选项

**示例响应：**
```
"您的请求包含 15 个组件。为了清晰起见，我建议：
1. 高级架构图（6 个主要组件）
2. 每个子系统的详细图表

您希望我首先创建高级视图吗？"
```

## 示例提示和响应

### 示例 1：简单流程图

**用户：** "创建一个用于用户注册的流程图"

**代理生成：**
1. 提取步骤："输入邮箱" → "验证邮箱" → "设置密码" → "完成"
2. 创建带有 4 个矩形 + 3 个箭头的流程图
3. 保存为 `user-registration-flow.excalidraw`

### 示例 2：关系图

**用户：** "绘制 User、Post 和 Comment 实体之间的关系"

**代理生成：**
1. 实体：User、Post、Comment
2. 关系：User → Post ("创建")、User → Comment ("写入")、Post → Comment ("包含")
3. 保存为 `user-content-relationships.excalidraw`

### 示例 3：思维导图

**用户：** "关于机器学习概念的思维导图"

**代理生成：**
1. 中心："机器学习"
2. 分支：监督学习、无监督学习、强化学习、深度学习
3. 每个分支的子主题
4. 保存为 `machine-learning-mindmap.excalidraw`

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 元素重叠 | 增加坐标间距 |
| 文本不适合方框 | 增加方框宽度或减小字体大小 |
| 元素过多 | 拆分为多个图表 |
| 布局不清晰 | 使用网格布局（行/列）或放射状布局（思维导图） |
| 颜色不一致 | 提前定义基于元素类型的颜色方案 |

## 高级技巧

### 网格布局（用于关系图）
```javascript
const columns = Math.ceil(Math.sqrt(entityCount));
const x = startX + (index % columns) * horizontalGap;
const y = startY + Math.floor(index / columns) * verticalGap;
```

### 放射状布局（用于思维导图）
```javascript
const angle = (2 * Math.PI * index) / branchCount;
const x = centerX + radius * Math.cos(angle);
const y = centerY + radius * Math.sin(angle);
```

### 自动生成的 ID
使用时间戳 + 随机字符串生成唯一 ID：
```javascript
const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
```

## 输出格式

始终提供：
1. ✅ 完整的 `.excalidraw` JSON 文件
2. 📊 创建内容的摘要
3. 📝 元素数量
4. 💡 打开/编辑说明

**示例摘要：**
```
创建：user-workflow.excalidraw
类型：流程图
元素：7 个矩形、6 个箭头、1 个标题文本
总计：14 个元素

查看说明：
1. 访问 https://excalidraw.com
2. 拖放 user-workflow.excalidraw
3. 或使用 Excalidraw VS Code 扩展中的 "文件" → "打开"
```

## 验证清单

交付图表前：
- [ ] 所有元素都有唯一 ID
- [ ] 坐标防止重叠
- [ ] 文本可读（字体大小 16+）
- [ ] **所有文本元素使用 `fontFamily: 5`（Excalifont）**
- [ ] 箭头逻辑连接
- [ ] 颜色遵循一致方案
- [ ] 文件是有效的 JSON
- [ ] 元素数量合理（<20 以保持清晰）

## 图标库（可选增强）

对于特殊图表（例如 AWS/GCP/Azure 架构图表），您可以使用 Excalidraw 的预制图标库。这提供了专业、标准化的图标，而不是基本形状。

### 当用户请求图标时

**如果用户要求 AWS/云架构图表或提到想要使用特定图标：**

1. **检查是否存在库**：查找 `libraries/<库名称>/reference.md`
2. **如果库存在**：继续使用图标（见 AI 助手工作流程）
3. **如果库不存在**：回复设置说明：

   ```
   要使用 [AWS/GCP/Azure/etc.] 架构图标，请按照以下步骤操作：
   
   1. 访问 https://libraries.excalidraw.com/
   2. 搜索 "[AWS Architecture Icons/etc.]" 并下载 .excalidrawlib 文件
   3. 创建目录：skills/excalidraw-diagram-generator/libraries/[图标集名称]/
   4. 将下载的文件放置在该目录中
   5. 运行拆分脚本：
      python skills/excalidraw-diagram-generator/scripts/split-excalidraw-library.py skills/excalidraw-diagram-generator/libraries/[图标集名称]/
   
   这将库拆分为单个图标文件，以便高效使用。
   设置完成后，我可以使用实际的 AWS/云图标创建您的图表。
   
   或者，我现在可以使用简单形状（矩形、椭圆）创建图表，您可以稍后手动在 Excalidraw 中替换图标。
   ```

### 用户设置说明（详细）

**步骤 1：创建库目录**
```bash
mkdir -p skills/excalidraw-diagram-generator/libraries/aws-architecture-icons
```

**步骤 2：下载库**
- 访问：https://libraries.excalidraw.com/
- 搜索您想要的图标集（例如，"AWS Architecture Icons"）
- 点击下载以获取 `.excalidrawlib` 文件
- 示例类别（网站上有可用性变化；请在网站上确认）：
   - 云服务图标
   - UI/Material 图标
   - 流程图符号

**步骤 3：放置库文件**
- 将下载的文件重命名为匹配目录名称（例如，`aws-architecture-icons.excalidrawlib`）
- 将其移动到在步骤 1 创建的目录中

**步骤 4：运行拆分脚本**
```bash
python skills/excalidraw-diagram-generator/scripts/split-excalidraw-library.py skills/excalidraw-diagram-generator/libraries/aws-architecture-icons/
```

**步骤 5：验证设置**
运行脚本后，验证以下结构是否存在：
```
skills/excalidraw-diagram-generator/libraries/aws-architecture-icons/
  aws-architecture-icons.excalidrawlib  (原始文件)
  reference.md                          (生成的图标查找表)
  icons/                                (生成的单个图标文件)
    API-Gateway.json
    CloudFront.json
    EC2.json
    Lambda.json
    RDS.json
    S3.json
    ...
```

### AI 助手工作流程

**当图标库在 `libraries/` 中可用时：**

**推荐方法：使用 Python 脚本（高效且可靠）**

存储库包含 Python 脚本，可自动处理图标集成：

1. **创建基本图表结构**：
   - 创建 `.excalidraw` 文件，包含基本布局（标题、方框、区域）
   - 这建立了画布和整体结构

2. **使用 Python 脚本添加图标**：
   ```bash
   python skills/excalidraw-diagram-generator/scripts/add-icon-to-diagram.py \
     <图表路径> <图标名称> <x> <y> [--label "文本"] [--library-path PATH]
   ```
   - 通过 `.excalidraw.edit` 启用编辑（避免覆盖问题）；传递 `--no-use-edit-suffix` 以禁用。

   **示例**：
   ```bash
   # 在位置 (400, 300) 添加 EC2 图标，带标签
   python scripts/add-icon-to-diagram.py diagram.excalidraw EC2 400 300 --label "Web Server"
   
   # 在位置 (200, 150) 添加 VPC 图标
   python scripts/add-icon-to-diagram.py diagram.excalidraw VPC 200 150
   
   # 从不同库添加图标
   python scripts/add-icon-to-diagram.py diagram.excalidraw Compute-Engine 500 200 \
     --library-path libraries/gcp-icons --label "API Server"
   ```

3. **添加连接箭头**：
   ```bash
   python skills/excalidraw-diagram-generator/scripts/add-arrow.py \
     <图表路径> <from-x> <from-y> <to-x> <to-y> [--label "文本"] [--style solid|dashed|dotted] [--color HEX]
   ```
   - 通过 `.excalidraw.edit` 启用编辑（避免覆盖问题）；传递 `--no-use-edit-suffix` 以禁用。

   **示例**：
   ```bash
   # 从 (300, 250) 到 (500, 300) 的简单箭头
   python scripts/add-arrow.py diagram.excalidraw 300 250 500 300
   
   # 带标签的箭头
   python scripts/add-arrow.py diagram.excalidraw 300 250 500 300 --label "HTTPS"
   
   # 虚线箭头，自定义颜色
   python scripts/add-arrow.py diagram.excalidraw 400 350 600 400 --style dashed --color "#7950f2"
   ```

4. **工作流概述**：
   ```bash
   # 第 1 步：创建带标题和结构的基线图表
   # （创建 .excalidraw 文件并包含初始元素）
   
   # 第 2 步：添加带标签的图标
   python scripts/add-icon-to-diagram.py my-diagram.excalidraw "Internet-gateway" 200 150 --label "Internet Gateway"
   python scripts/add-icon-to-diagram.py my-diagram.excalidraw VPC 250 250
   python scripts/add-icon-to-diagram.py my-diagram.excalidraw ELB 350 300 --label "负载均衡器"
   python scripts/add-icon-to-diagram.py my-diagram.excalidraw EC2 450 350 --label "EC2 实例"
   python scripts/add-icon-to-diagram.py my-diagram.excalidraw RDS 550 400 --label "数据库"
   
   # 第 3 步：添加连接箭头
   python scripts/add-arrow.py my-diagram.excalidraw 250 200 300 250  # Internet → VPC
   python scripts/add-arrow.py my-diagram.excalidraw 300 300 400 300  # VPC → 负载均衡器
   python scripts/add-arrow.py my-diagram.excalidraw 400 330 500 350  # 负载均衡器 → EC2
   python scripts/add-arrow.py my-diagram.excalidraw 500 380 600 400  # EC2 → 数据库
   ```

**使用 Python 脚本方法的优点**：
- ✅ **不消耗 token**：图标 JSON 数据（每份 200-1000 行）不会进入 AI 上下文
- ✅ **精确转换**：坐标计算由确定性处理
- ✅ **ID 管理**：自动生成 UUID 防止冲突
- ✅ **可靠**：无坐标计算错误或 ID 冲突风险
- ✅ **快速**：直接文件操作，无解析开销
- ✅ **可复用**：适用于您提供的任何 Excalidraw 库

**替代方案：手动图标集成（不推荐）**

仅在无法使用 Python 脚本时使用：

1. **检查库**：
   ```
   列出目录：skills/excalidraw-diagram-generator/libraries/
   查找包含 reference.md 文件的子目录
   ```

2. **读取 reference.md**：
   ```
   打开：libraries/<库名>/reference.md
   这是一份轻量级文档（通常 <300 行），列出所有可用图标
   ```

3. **查找相关图标**：
   ```
   在 reference.md 表格中搜索与图表需求匹配的图标名称
   示例：对于包含 EC2、S3、Lambda 的 AWS 图表 → 在表格中查找 "EC2"、"S3"、"Lambda"
   ```

4. **加载特定图标数据**（警告：大文件）：
   ```
   仅读取所需的图标文件：
   - libraries/aws-architecture-icons/icons/EC2.json (200-300 行)
   - libraries/aws-architecture-icons/icons/S3.json (200-300 行)
   - libraries/aws-architecture-icons/icons/Lambda.json (200-300 行)
   注意：每个图标文件包含 200-1000 行 - 这会消耗大量 token
   ```

5. **提取和转换元素**：
   ```
   每个图标 JSON 包含一个 "elements" 数组
   计算边界框（min_x, min_y, max_x, max_y）
   对所有 x/y 坐标应用偏移
   为所有元素生成新的唯一 ID
   更新 groupIds 引用
   将转换后的元素复制到您的图表中
   ```

6. **定位图标并添加连接**：
   ```
   调整 x/y 坐标以在图表中正确定位图标
   更新 ID 以确保图表内唯一性
   根据需要添加连接箭头和标签
   ```

**手动集成挑战**：
- ⚠️ 高 token 消耗（每个图标 200-1000 行 × 图标数量）
- ⚠️ 复杂的坐标转换计算
- ⚠️ 如果处理不当，存在 ID 冲突风险
- ⚠️ 对于包含许多图标的图表，耗时较长

### 示例：使用图标创建 AWS 图表

**请求**：创建一个包含 Internet Gateway、VPC、ELB、EC2 和 RDS 的 AWS 架构图表

**推荐工作流程（使用 Python 脚本）**：

```bash
# 第 1 步：创建带标题的基线图表文件
# 创建 my-aws-diagram.excalidraw 并包含基本结构（标题等）

# 第 2 步：检查图标可用性
# 读取：libraries/aws-architecture-icons/reference.md
# 确认图标存在：Internet-gateway、VPC、ELB、EC2、RDS

# 第 3 步：使用 Python 脚本添加图标
python scripts/add-icon-to-diagram.py my-aws-diagram.excalidraw "Internet-gateway" 150 100 --label "Internet Gateway"
python scripts/add-icon-to-diagram.py my-aws-diagram.excalidraw VPC 200 200
python scripts/add-icon-to-diagram.py my-aws-diagram.excalidraw ELB 350 250 --label "负载均衡器"
python scripts/add-icon-to-diagram.py my-aws-diagram.excalidraw EC2 500 300 --label "Web 服务器"
python scripts/add-icon-to-diagram.py my-aws-diagram.excalidraw RDS 650 350 --label "数据库"

# 第 4 步：添加连接箭头
python scripts/add-arrow.py my-aws-diagram.excalidraw 200 150 250 200  # Internet → VPC
python scripts/add-arrow.py my-aws-diagram.excalidraw 265 230 350 250  # VPC → 负载均衡器
python scripts/add-arrow.py my-aws-diagram.excalidraw 415 280 500 300  # 负载均衡器 → EC2
python scripts/add-arrow.py my-aws-diagram.excalidraw 565 330 650 350 --label "SQL" --style 虚线

# 结果：包含专业 AWS 图标、标签和连接的完整图表
```

**优点**：
- 无需手动计算坐标
- 图标数据不消耗 token
- 可靠、确定性的结果
- 易于迭代和调整位置

**替代工作流程（手动，如果脚本不可用）**：
1. 检查：`libraries/aws-architecture-icons/reference.md` 是否存在 → 是
2. 读取 reference.md → 查找 Internet-gateway、VPC、ELB、EC2、RDS 的条目
3. 加载：
   - `icons/Internet-gateway.json`（298 行）
   - `icons/VPC.json`（550 行）
   - `icons/ELB.json`（363 行）
   - `icons/EC2.json`（231 行）
   - `icons/RDS.json`（类似大小）
   **总计：约 2000+ 行 JSON 需要处理**
4. 从每个 JSON 中提取元素
5. 为每个图标计算边界框和偏移
6. 转换所有坐标（x, y）以进行定位
7. 为所有元素生成唯一 ID
8. 添加显示数据流的箭头
9. 添加文本标签
10. 生成最终的 `.excalidraw` 文件

**手动方法的挑战**：
- ⚠️ 高 token 消耗（~2000-5000 行）
- ⚠️ 复杂的坐标数学计算
- ⚠️ 如果处理不当，存在 ID 冲突风险

### 支持的图标库（示例 — 验证可用性）

- 此工作流程适用于您提供的任何有效的 `.excalidrawlib` 文件。
- https://libraries.excalidraw.com/ 上可能找到的库类别示例：
   - 云服务图标
   - Kubernetes / 基础设施图标
   - UI / Material 图标
   - 流程图 / 图表符号
   - 网络图表图标
- 可用性和命名可能会变化；在使用前在网站上验证确切的库名称。

### 备用方案：无图标可用

**如果未设置图标库**：
- 使用基本形状（矩形、椭圆、箭头）创建图表
- 使用颜色编码和文本标签区分组件
- 告知用户他们稍后可以添加图标或为未来图表设置库
- 图表仍然功能齐全且清晰，只是视觉上不太精致

## 参考

查看捆绑的参考文档：
- `references/excalidraw-schema.md` - 完整 Excalidraw JSON 架构
- `references/element-types.md` - 详细的元素类型规范
- `templates/flowchart-template.excalidraw` - 基本流程图模板
- `templates/relationship-template.excalidraw` - 关系图模板
- `templates/mindmap-template.excalidraw` - 思维导图模板
- `templates/business-flow-swimlane-template.excalidraw` - 业务流程泳道模板
- `templates/class-diagram-template.excalidraw` - 类图表模板
- `templates/data-flow-diagram-template.excalidraw` - 数据流图表模板
- `templates/er-diagram-template.excalidraw` - 实体关系图模板
- `templates/sequence-diagram-template.excalidraw` - 顺序图模板
- `scripts/add-icon-to-diagram.py` - 将 Excalidraw 库中的图标添加到图表
- `scripts/add-arrow.py` - 在图表中的元素之间添加箭头（连接）
- `scripts/split-excalidraw-library.py` - 用于拆分 `.excalidrawlib` 文件的工具
- `scripts/README.md` - 库工具的文档
- `scripts/.gitignore` - 防止提交本地 Python 生成物

## 限制

- 复杂曲线简化为直线/基本曲线
- 手绘粗糙度设置为默认值（1）
- 无嵌入式图像支持
- 每个图表最大推荐元素：20 个
- 无自动碰撞检测（使用间距指南）

## 未来改进

潜在改进：
- 自动布局优化算法
- 从 Mermaid/PlantUML 语法导入
- 模板库扩展
- 生成后交互式编辑
