# 语义主题聚类

基于SERP重叠驱动的关键词聚类，用于内容架构。通过Google实际排名（共享前10名结果）对关键词进行分组，而不是通过文本相似性。设计带内部链接矩阵的轮辐式内容集群，并生成交互式集群地图可视化。

**脚本：** 位于插件根目录 `scripts/` 文件夹。

---

## 快速参考

| 命令 | 功能 |
|------|------|
| `/seo cluster plan <种子关键词>` | 完整规划工作流：扩展、聚类、架构、可视化 |
| `/seo cluster plan --from strategy` | 从现有的 `/seo plan` 输出导入 |
| `/seo cluster execute` | 执行计划：通过 claude-blog 创建内容或输出概要 |
| `/seo cluster map` | 重新生成交互式集群可视化 |

---

## 规划工作流

### 第1步：种子关键词扩展

使用WebSearch将种子关键词扩展为30-50个变体：

1. **相关搜索**：搜索种子关键词，提取“相关搜索”和“人们也搜索”
2. **人们也问（PAA）**：从SERP结果中提取所有PAA问题
3. **长尾修饰符**：添加常用修饰符：“最佳”、“如何”、“vs”、“初学者适用”、“工具”、“示例”、“指南”、“模板”、“错误”、“清单”
4. **问题挖掘**：生成 who/what/when/where/why/how 变体
5. **意图修饰符**：添加商业修饰符：“价格”、“评论”、“替代品”、“比较”、“免费”、“顶级”

**去重：** 规范化变体（小写、去除冠词），删除完全重复项。
目标：30-50个唯一关键词变体。如果少于30个，使用顶部PAA问题作为种子进行第二次扩展。

### 第2步：SERP重叠聚类

这是核心差异点。加载 `references/serp-overlap-methodology.md` 了解完整算法。

**流程：**
1. 根据初始意图猜测对关键词进行分组（减少成对比较）
2. 在每个分组内，对候选对进行WebSearch
3. 计数前10名有机结果中的共享URL（忽略广告、特色摘要、PAA）
4. 应用阈值：

| 共享结果 | 关系 | 操作 |
|----------|------|------|
| 7-10 | 相同帖子 | 合并到单个目标页面 |
| 4-6 | 相同集群 | 分组到相同的轮辐集群 |
| 2-3 | 互链 | 放置在相邻集群，添加交叉链接 |
| 0-1 | 分离 | 分配到不同集群或排除 |

**优化：** 对于40个关键词，完整成对比较 = 780次比较。改为：
- 按意图预分组（4组约10个 = 4 x 45 = 180次比较）
- 仅交叉检查组边界关键词
- 跳过两个都是相同头词长尾变体的配对（假设相同集群）

**DataForSEO集成：** 如果DataForSEO MCP可用，使用 `serp_organic_live_advanced` 代替WebSearch获取SERP数据。在每次批处理前运行 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run dataforseo_costs.py check serp_organic_live_advanced --count N`。如果 `"status": "needs_approval"`，显示成本估算并询问用户。如果 `"status": "blocked"`，回退到WebSearch。

### 第3步：意图分类

将每个关键词分类到四个意图类别之一：

| 意图 | 信号 | 是否包含在集群中？ |
|------|------|-------------------|
| 信息性 | how, what, why, guide, tutorial, learn | 是 |
| 商业性 | best, top, review, comparison, vs, alternative | 是 |
| 交易性 | buy, price, discount, coupon, order, sign up | 是 |
| 导航性 | 品牌名称、特定产品名称、登录 | 否（排除） |

从聚类中排除导航性关键词。标记边界情况供人工审核。关键词可以有混合意图（例如，“最佳CRM软件”既是商业性也是信息性）——按主导意图分类。

### 第4步：轮辐式架构

加载 `references/hub-spoke-architecture.md` 了解完整规范。

**设计集群结构：**

1. **选择支柱关键词**：最高量、最广泛意图、与其他关键词SERP重叠最多
2. **将轮辐分组到集群**：每个集群是子主题区域（每个支柱2-5个集群）
3. **将帖子分配到集群**：每个集群获得2-4个轮辐帖子
4. **为每个帖子选择模板**：根据意图分类：

| 意图模式 | 模板选项 |
|----------|----------|
| 信息性（广泛） | ultimate-guide |
| 信息性（如何） | how-to |
| 信息性（列表） | listicle |
| 信息性（概念） | explainer |
| 商业性（比较） | comparison |
| 商业性（评估） | review |
| 商业性（排名） | best-of |
| 交易性 | landing-page |

5. **设置字数目标：**
   - 支柱页面：2500-4000字
   - 轮辐帖子：1200-1800字

6. **竞争性检查**：没有两个帖子共享相同的主要关键词。如果SERP重叠为7+，将那些关键词合并为一个针对两个目标页面的帖子。

### 第5步：内部链接矩阵

设计双向链接结构：

| 链接类型 | 方向 | 要求 |
|----------|------|------|
| 轮辐到支柱 | 轮辐 -> 支柱 | 必须的（每个轮辐） |
| 支柱到轮辐 | 支柱 -> 轮辐 | 必须的（每个轮辐） |
| 集群内轮辐到轮辐 | 轮辐 <-> 轮辐 | 每个帖子2-3个链接 |
| 跨集群 | 轮辐 -> 其他集群的轮辐 | 每个帖子0-1个链接 |

**规则：**
- 每个帖子必须至少有3个内部入站链接
- 没有孤儿页面（每个帖子可在2次点击内从支柱访问）
- 锚文本必须使用目标关键词或接近变体（不能是“点击这里”）
- 链接位置：正文内容中，而不仅仅是导航/侧边栏

生成链接矩阵作为JSON邻接表：
```json
{
  "links": [
    { "from": "pillar", "to": "cluster-0-post-0", "type": "mandatory", "anchor": "keyword" },
    { "from": "cluster-0-post-0", "to": "pillar", "type": "mandatory", "anchor": "keyword" }
  ]
}
```

### 第6步：交互式集群地图

使用 `templates/cluster-map.html` 中的模板生成 `cluster-map.html`。

1. 读取模板文件
2. 从集群计划构建 `CLUSTER_DATA` JSON对象：
   ```javascript
   {
     pillar: { title, keyword, volume, template, wordCount, url },
     clusters: [{ name, color, posts: [{ title, keyword, volume, template, wordCount, url, status }] }],
     links: [{ from, to, type }],
     meta: { totalPosts, totalClusters, totalLinks, estimatedWords }
   }
   ```
3. 将模板中的 `CLUSTER_DATA` 占位符替换为实际JSON
4. 将完成的HTML文件写入输出目录
5. 通知用户：“在浏览器中打开 `cluster-map.html` 探索交互式集群地图。”

---

## 策略导入

使用 `--from strategy` 调用时：

1. 在当前目录中查找最新的 `/seo plan` 输出（搜索匹配 `*SEO*Plan*`、`*strategy*`、`*content-strategy*` 的文件）
2. 解析Markdown表格：关键词、页面类型、内容支柱、URL结构
3. 验证提取的数据：检查重复项、缺失关键词、不完整条目
4. 使用SERP数据丰富：对提取的关键词运行SERP重叠分析
5. 使用导入的关键词作为起始集构建集群计划（跳过第1步）

如果没有找到策略文件，提示用户：“当前目录中未找到现有的SEO计划。请先运行 `/seo plan`，或为全新聚类提供种子关键词。”

---

## 执行工作流

调用 `/seo cluster execute` 时：

### 检查claude-blog

```
测试：`~/.claude/skills/blog/SKILL.md` 是否存在？
```

**如果 claude-blog 已安装：**

1. 加载 `references/execution-workflow.md` 了解完整算法
2. 从当前目录读取 `cluster-plan.json`
3. 检查恢复状态：扫描输出目录查找已写入的帖子
4. 按优先级顺序执行：支柱优先，然后按量（最高优先）执行轮辐
5. 对每个帖子，使用集群上下文调用 `blog-write` 技能：
   - 集群角色（支柱或轮辐）
   - 集群中的位置（集群索引、帖子索引）
   - 目标关键词和次要关键词
   - 模板类型和字数目标
   - 要包含的内部链接（带锚文本）
   - 未来帖子将接收的链接（占位符标记）
6. 每个帖子写入后，扫描之前的帖子查找向后链接占位符并注入新帖子的URL
7. 所有帖子写入后，生成集群评分卡

**如果 claude-blog 未安装：**

1. 为集群计划中的每个帖子生成详细内容概要
2. 每个概要包括：
   - 标题和元描述
   - 主要关键词和次要关键词
   - 模板类型和建议结构（H2/H3大纲）
   - 字数目标
   - 要包含的内部链接（带锚文本）
   - 要涵盖的关键点
   - 要区别于的竞争页面
3. 将概要写入 `cluster-briefs/` 目录作为单独的Markdown文件
4. 通知用户：“安装 [claude-blog](https://github.com/AgriciDaniel/claude-blog) 以自动创建内容。概要已保存到 `cluster-briefs/`。”

---

## 集群评分卡

执行后质量报告。在 `/seo cluster execute` 后自动运行，或在需求时通过分析输出目录运行。

| 指标 | 目标 | 如何衡量 |
|------|------|----------|
| 覆盖率 | 100% | 已写入帖子 / 计划帖子 |
| 链接密度 | 每帖子3+ | 每帖子内部链接计数 |
| 孤儿页面 | 0 | 缺少入站链接的帖子 |
| 竞争性 | 0冲突 | 检查重复的主要关键词 |
| 图片数量 | 每帖子1+ | 至少包含一个图片的帖子 |
| 支柱链接 | 100% | 所有轮辐都链接到支柱且反之亦然 |
| 交叉链接 | 80%+ | 实现了建议的轮辐到轮辐链接 |
| 内容空白 | 0 | 计划中跳过或未完成的帖子 |

---

## 地图重新生成

调用 `/seo cluster map` 时：

1. 从当前目录读取 `cluster-plan.json`
2. 扫描输出目录并更新帖子状态（计划 vs 已写入）
3. 使用更新后的状态重新生成 `cluster-map.html`
4. 报告：已写入帖子 vs 计划帖子，链接完成百分比

---

## 输出文件

所有输出都写入当前工作目录：

| 文件 | 描述 |
|------|------|
| `cluster-plan.json` | 机器可读的集群计划（完整数据） |
| `cluster-plan.md` | 人类可读的集群计划摘要 |
| `cluster-map.html` | 交互式SVG可视化 |
| `cluster-briefs/` | 内容概要（如果没有 claude-blog） |
| `cluster-scorecard.md` | 执行后质量报告 |

---

## 跨技能集成

| 技能 | 关系 |
|------|------|
| `seo-plan` | 导入源：策略导入读取 seo-plan 输出 |
| `seo-content` | 质量检查：生成内容的E-E-A-T验证 |
| `seo-schema` | Schema标记：集群页面的Article、BreadcrumbList、ItemList |
| `seo-dataforseo` | 数据源：当DataForSEO MCP可用时 |
| `seo-google` | 报告：生成集群计划和评分卡的PDF报告 |

集群规划或执行完成后，提供：
“生成PDF报告？使用 `/seo google report`”

---

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| “未提供种子关键词” | 缺少参数 | 提示用户输入种子关键词或URL |
| “关键词变体不足” | 扩展产生 < 15 个关键词 | 使用PAA问题进行第二次扩展 |
| “SERP数据不可用” | WebSearch和DataForSEO都失败 | 30秒后重试；如果仍然存在，使用仅意图聚类并带警告 |
| “未找到策略文件” | `--from strategy` 但没有计划 | 提示用户先运行 `/seo plan` |
| “cluster-plan.json未找到” | 未规划就执行 | 提示用户先运行 `/seo cluster plan` |
| “claude-blog未安装” | 尝试执行但无博客技能 | 生成内容概要；建议安装 |
| “DataForSEO预算超支” | 成本检查返回“blocked” | 回退到WebSearch；通知用户 |
| “重复主要关键词” | 检测到竞争性 | 合并受影响的帖子或重新分配关键词 |
| “检测到孤儿页面” | 帖子缺少入站链接 | 从最近的集群兄弟添加链接 |
| “恢复状态损坏” | 计划和输出不匹配 | 从输出目录扫描重建状态 |

---

## 安全

- 所有通过 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run render_page.py <url> --mode auto` 获取的URL（带SPA感知SSRF保护 via `url_safety`）
- 不存储或传输凭证
- 输出文件不包含PII或API密钥
- DataForSEO成本检查在每次API调用前运行

## FLOW框架集成

用于提示引导的关键词研究和差距分析，使用 `/seo flow find [url|topic]`：FLOW的5个find阶段提示与SERP重叠聚类方法互补，提供结构化发现提示。
