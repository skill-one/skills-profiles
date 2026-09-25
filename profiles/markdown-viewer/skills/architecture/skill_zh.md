# 架构图生成器

**快速入门：** 创建具有灵活布局（单列/双列/三列）的 HTML 结构 → 定义层和网格的 CSS 样式 → 使用分类面板添加内容 → 使用语义化颜色区分不同层。

## 关键规则

### 规则 1：直接 HTML 嵌入
**重要提示**：将架构图作为直接的 HTML 写入 Markdown 中。**绝对不要**使用代码块（` ```html `）。HTML 应直接嵌入文档中，无需任何围栏。

### 规则 2：HTML 结构中不允许空行
**关键提示**：在架构图 HTML 结构中**不要**添加任何空行。保持整个 HTML 块连续，以防止解析错误。

### 规则 3：增量创建方法
**推荐做法**：分步创建架构图：
1. **首先**：创建整体框架（包装器、侧边栏、主结构）并定义所有 CSS 样式
2. **其次**：添加带标题的层容器
3. **再次**：逐层填充组件
4. **最后**：添加详细内容和优化

### 规则 4：灵活的布局结构
架构图可以根据复杂度使用灵活的布局：
- **单列**：仅主内容（适用于简单架构）
- **双列**：主内容 + 一个侧边栏（左侧或右侧）
- **三列**：完整布局，包含两个侧边栏（适用于复杂系统）
  - **左侧侧边栏**：支持系统（监控、运维、分析）
  - **主内容**：核心架构层（用户、应用、数据、基础设施）
  - **右侧侧边栏**：横切关注点（安全、合规、治理）

### 规则 5：分层组织
每层应具有：
- 清晰的语义意义（用户、应用、AI/逻辑、数据、基础设施）
- 一致的色彩编码
- 基于网格的组件布局
- 合适的子组件嵌套

### 规则 6：色彩语义
使用一致的语义意义为层——具体的调色板因风格而异（见示例）。标准的语义映射：
- **用户层** — 用户界面和客户端
- **应用层** — 业务逻辑和 API 服务
- **AI/逻辑层** — 智能化、规则、处理引擎
- **数据层** — 数据库、缓存、存储
- **基础设施层** — 容器、网络、DevOps
- **外部服务** — 第三方 API、云服务（通常使用虚线边框）

## 风格示例

选择与项目调性和受众匹配的视觉风格。每个示例都包含一个完整的、可复制粘贴的 HTML 模板。

| # | 风格 | 文件 | 适用于 |
|---|---|---|---|
| 1 | **钢蓝** | [styles/steel-blue.md](styles/steel-blue.md) | 咨询报告、银行/金融、政府项目、RFP 报告 |
| 2 | **暖琥珀** | [styles/ember-warm.md](styles/ember-warm.md) | 零售/电商、教育平台、生活方式品牌、文化机构 |
| 3 | **霓虹暗黑** | [styles/neon-dark.md](styles/neon-dark.md) | 技术演讲、开发者会议、游戏平台、网络安全仪表盘 |
| 4 | ** stark 块** | [styles/stark-block.md](styles/stark-block.md) | 创意工作室、教育平台、独立开发者、技术博客 |
| 5 | **海洋蓝绿** | [styles/ocean-teal.md](styles/ocean-teal.md) | 旅行平台、物流/运输、绿色科技、气象/海洋项目 |
| 6 | **黄昏光晕** | [styles/dusk-glow.md](styles/dusk-glow.md) | 社交媒体、娱乐平台、营销科技、内容创作工具 |
| 7 | **玫瑰绽放** | [styles/rose-bloom.md](styles/rose-bloom.md) | 时尚/美容、奢侈品牌、婚礼平台、高级会员 |
| 8 | **鼠尾草森林** | [styles/sage-forest.md](styles/sage-forest.md) | 医疗保健、农业科技、清洁能源、可持续发展、生物信息学 |
| 9 | **冰霜简洁** | [styles/frost-clean.md](styles/frost-clean.md) | 设计工具、开发者文档、API 参考、极简 SaaS |
| 10 | **靛蓝深邃** | [styles/indigo-deep.md](styles/indigo-deep.md) | 品牌一致性系统、企业白皮书、内部平台 |
| 11 | **粉彩混合** | [styles/pastel-mix.md](styles/pastel-mix.md) | SaaS 产品、初创公司、通用技术架构、产品文档 |
| 12 | **石板暗黑** | [styles/slate-dark.md](styles/slate-dark.md) | 企业暗黑模式、内部工具、开发者仪表盘 |

## 布局示例

选择适合架构复杂度的布局结构。布局使用线框风格（无颜色）以专注于结构模式。可任意组合上述任何风格。

| # | 布局 | 文件 | 最适合 |
|---|---|---|---|
| 1 | **三列** | [layouts/three-column.md](layouts/three-column.md) | 具有横切关注点和监控侧边栏的复杂系统 |
| 2 | **单列堆叠** | [layouts/single-stack.md](layouts/single-stack.md) | 简单服务、微服务详细视图、专注文档 |
| 3 | **左侧侧边栏** | [layouts/left-sidebar.md](layouts/left-sidebar.md) | 侧重于运维/监控的系统、DevOps 中心视图 |
| 4 | **右侧侧边栏** | [layouts/right-sidebar.md](layouts/right-sidebar.md) | 侧重于安全/合规的系统、治理中心视图 |
| 5 | **管道** | [layouts/pipeline.md](layouts/pipeline.md) | 数据管道、CI/CD 流程、ETL 流程、水平阶段流 |
| 6 | **双列分割** | [layouts/two-column-split.md](layouts/two-column-split.md) | 对比视图、双系统视图、迁移架构 |
| 7 | **仪表盘** | [layouts/dashboard.md](layouts/dashboard.md) | 系统概览带 KPI、监控仪表盘、高管摘要 |
| 8 | **网格目录** | [layouts/grid-catalog.md](layouts/grid-catalog.md) | 服务目录、组件库、等权重微服务 |
| 9 | **横幅+中心** | [layouts/banner-center.md](layouts/banner-center.md) | 网关中心架构、面向用户的系统带共享基础设施 |
| 10 | **嵌套容器** | [layouts/nested-containers.md](layouts/nested-containers.md) | 云部署、VPC/网络拓扑、环境隔离 |
| 11 | **层布局** | [layouts/layer-layouts.md](layouts/layer-layouts.md) | 按层布局模式：网格、子组、产品组、KPI、垂直堆叠、区域、内联管道、混合宽度 |
| 12 | **连接器** | [layouts/connectors.md](layouts/connectors.md) | 组件之间 SVG 覆盖连接器：实线/虚线、箭头、标签、曲线和正交路径 |

## 高级功能

**注意**：这些高级组件需要额外的 CSS 样式。将这些添加到 `<style scoped>` 部分：

```css
.arch-product-group { display: flex; gap: 10px; }
.arch-product { flex: 1; border-radius: 8px; padding: 10px; background: rgba(255, 255, 255, 0.6); border: 1px dashed #d97706; }
.arch-product-title { font-size: 12px; font-weight: bold; color: #92400e; margin-bottom: 8px; text-align: center; }
.arch-subgroup { display: flex; gap: 8px; margin-top: 8px; }
.arch-subgroup-box { flex: 1; border-radius: 6px; padding: 8px; background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(0, 0, 0, 0.08); }
.arch-subgroup-title { font-size: 10px; font-weight: bold; color: #374151; text-align: center; margin-bottom: 6px; }
.arch-user-types { display: flex; gap: 4px; justify-content: center; margin-top: 6px; }
.arch-user-tag { font-size: 9px; padding: 2px 6px; border-radius: 10px; background: rgba(59, 130, 246, 0.15); color: #1d4ed8; }
/* 组件之间 SVG 连接线 */
.arch-conn { stroke: #94a3b8; stroke-width: 1.5; fill: none; }
.arch-conn-dashed { stroke: #94a3b8; stroke-width: 1.5; fill: none; stroke-dasharray: 6 4; }
.arch-conn-label { font-size: 9px; fill: #64748b; font-family: sans-serif; }
```

### 自定义产品组
对于具有多个产品/模块的复杂应用：

```html
<div class="arch-product-group">
  <div class="arch-product">
    <div class="arch-product-title">🎯 产品 A</div>
    <div class="arch-grid arch-grid-2">
      <div class="arch-box">功能 1<br><small>描述</small></div>
      <div class="arch-box highlight">功能 2<br><small>关键功能</small></div>
    </div>
  </div>
  <div class="arch-product">
    <div class="arch-product-title">📊 产品 B</div>
    <div class="arch-grid arch-grid-2">
      <div class="arch-box">功能 3<br><small>描述</small></div>
      <div class="arch-box">功能 4<br><small>描述</small></div>
    </div>
  </div>
</div>
```

### 子组组件
在层内进行详细分解：

```html
<div class="arch-subgroup">
  <div class="arch-subgroup-box">
    <div class="arch-subgroup-title">组件组 A</div>
    <div class="arch-grid arch-grid-3">
      <div class="arch-box tech">服务 1<br><small>详情</small></div>
      <div class="arch-box tech">服务 2<br><small>详情</small></div>
      <div class="arch-box tech">服务 3<br><small>详情</small></div>
    </div>
  </div>
  <div class="arch-subgroup-box">
    <div class="arch-subgroup-title">组件组 B</div>
    <div class="arch-grid arch-grid-2">
      <div class="arch-box tech">服务 4<br><small>详情</small></div>
      <div class="arch-box tech">服务 5<br><small>详情</small></div>
    </div>
  </div>
</div>
```

### 用户类型/标签

```html
<div class="arch-user-types">
  <span class="arch-user-tag">管理员用户</span>
  <span class="arch-user-tag">最终用户</span>
  <span class="arch-user-tag">API 客户端</span>
  <span class="arch-user-tag">合作伙伴</span>
</div>
```

### 指标和 KPI

```html
<div class="arch-sidebar-item metric">99.9% 可用性</div>
<div class="arch-sidebar-item metric">&lt;200ms 响应</div>
<div class="arch-sidebar-item metric">1M+ 用户</div>
```

### 组件之间 SVG 连接器
使用 SVG 覆盖在组件之间绘制正交（直角）连接器。**始终使用 `<path>` 与 `M`/`L` 命令绘制严格水平和垂直段。** 不要使用 `<line>`、贝塞尔曲线或斜线。参见 [layouts/connectors.md](layouts/connectors.md) 获取完整参考。

```html
<!-- 将图表内容包裹在相对容器中 -->
<div style="position: relative;">
  <!-- ...层和组件... -->
  <!-- SVG 覆盖作为最后一个子元素 -->
  <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible;">
    <defs>
      <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
        <path d="M0,0 L8,3 L0,6" fill="none" stroke="#94a3b8" stroke-width="1"/>
      </marker>
    </defs>
    <!-- 正交实线箭头（垂直→水平→垂直） -->
    <path d="M 200,72 L 200,90 L 400,90 L 400,108" class="arch-conn" marker-end="url(#arrowhead)"/>
    <!-- 正交虚线 -->
    <path d="M 600,72 L 600,90 L 600,90 L 600,108" class="arch-conn-dashed" marker-end="url(#arrowhead)"/>
    <!-- 标签 -->
    <text x="420" y="86" class="arch-conn-label">数据流</text>
  </svg>
</div>
```

## 样式参考

### 常见类（跨所有风格共享）
- `.arch-wrapper` — 侧边栏 + 主布局的 flex 容器
- `.arch-sidebar` — 固定宽度的侧边栏列
- `.arch-main` — 可扩展的主内容区域
- `.arch-layer` — 层容器（添加语义类：`.user`、`.application`、`.ai`、`.data`、`.infra`、`.external`）
- `.arch-box` — 组件框；`.arch-box.highlight` 用于关键项；`.arch-box.tech` 用于较小技术项
- `.arch-grid-2` 到 `.arch-grid-6` — 网格列布局
- `.arch-sidebar-panel` — 侧边栏面板容器
- `.arch-sidebar-item` — 侧边栏项；`.arch-sidebar-item.metric` 用于突出显示的指标

## 最佳实践

### HTML 使用指南

1. **直接嵌入** — 始终直接在 Markdown 中嵌入 HTML，**不要**使用 ` ```html ` 代码块
2. **结构中不允许空行** — 保持整个 HTML 块连续，无任何空行
3. **增量开发** — 分步构建图表：
   - 从基本框架和布局结构开始（根据需要使用单列/双列/三列）
   - 添加带正确 CSS 类的空层容器
   - 从上到下逐层填充内容
   - 最后优化内容和添加高亮

### 架构设计

1. **保持层逻辑分离** — 每层应代表一个清晰的架构层
2. **使用一致命名** — 遵循组件和服务命名规范
3. **突出关键组件** — 使用 `.highlight` 类突出关键组件
4. **添加技术细节** — 在 `<small>` 标签中包含技术栈信息
5. **平衡信息密度** — 不要过度填充组件的文本
6. **谨慎使用图标** — 在标题中添加表情符号以实现视觉层次
7. **保持色彩语义** — 遵循已建立的色彩含义
8. **考虑响应式设计** — 网格会自动适应内容
