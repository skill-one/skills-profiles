---
name: latex-posters
description: 使用 beamerposter、tikzposter 或 baposter 在 LaTeX 中创建专业的调研海报。支持会议展示、学术海报和科学交流。包含版式设计、配色方案、多列格式、图形集成以及针对海报的视觉传达最佳实践。
---

# LaTeX 研究海报

## 概述

研究海报是科学交流的重要媒介，适用于会议、研讨会和学术活动。本技能提供全面的指导，帮助您使用 LaTeX 包创建专业且视觉效果出众的研究海报。生成具有适当布局、排版、配色方案和视觉层次结构的出版物质量海报。

## 何时使用此技能

当您需要：
- 为会议、研讨会或海报展示会创建研究海报
- 为大学活动或论文答辩设计学术海报
- 准备面向公众的研究成果视觉总结
- 将科学论文转换为海报格式
- 为研究小组或部门创建模板海报
- 设计符合特定会议尺寸要求的海报（A0、A1、36×48 英寸等）
- 创建具有复杂多列布局的海报
- 在海报格式中整合图表、表格、公式和引用

## AI 驱动的视觉元素生成

**标准工作流程：在创建 LaTeX 海报之前，使用 AI 生成所有主要的视觉元素。**

这是创建视觉吸引力海报的推荐方法：
1. 规划所有需要的视觉元素（标题、引言、方法、结果、结论）
2. 使用 scientific-schematics 或 Nano Banana Pro 生成每个元素
3. 在 LaTeX 模板中组装生成的图像
4. 在视觉元素周围添加文本内容

**目标：60-70% 的海报区域应为 AI 生成的视觉元素，30-40% 为文本。**

---

### 严格限制（不可超出）

这些是限制，不是指导方针。违反它们是导致海报失败的最常见原因。详细的推理、按图形类型划分的表格和示例在 [references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md) 中。

| 限制条件 | 限制 |
| --- | --- |
| 每个 AI 生成的图形中的元素 | **最多 3-4 个**（理想情况为 3 个） |
| 每个图形中的文字 | **最多 10 个** |
| 每个图形中的空白区域 | **至少 50%**（60% 更好） |
| 关键数字/指标 | **120pt+** |
| 标签 | **80pt+** |
| 海报上的正文 | **24pt+** |
| 内容区域（A0） | **最多 5-6 个** |
| 海报上的总文字 | **300-800 个** |
| 图形宽度 | `0.85\linewidth`，永远不要 `1.0` |

每个图形提示必须包含：`POSTER FORMAT for A0`、明确的元素或文字数量（`ONLY 3 icons`，`3 words total`）、字体大小（`GIANT (120pt+)`）、`60% white space` 和观看距离（`readable from 10-12 feet`）。

**两个强制性的审查关卡。** 跳过任何一个都可能导致海报难以阅读：

- **生成之前** — 确认每个计划的图形包含 3-4 个项目、一条信息，少于 10 个字，并且不是 5+ 步骤的工作流程。如果不是，请将其拆分为多个图形。
- **生成之后、组装之前** — 在 25% 放大倍率下打开每个图形。所有文字可读，4 个或更少的元素，50%+ 的空白区域，2 秒内可理解。任何失败都意味着重新生成或拆分。不要从失败的图形中组装海报。

总是失败的模式：`7-stage workflow`、`带有年度里程碑的时间线`、`一个图形中包含 3 个案例研究`、`比较 5+ 种方法`、`包含所有层的架构`。将每个模式压缩为 3 个高级项目，或制作多个单独的图形。

**溢出是错误，不是警告。** 编译后，运行 `grep -i overfull poster.log` 并在 100% 放大倍率下检查所有四条边。参见 [references/compilation_and_quality_control.md](references/compilation_and_quality_control.md)。

## 科学示意图集成

有关创建示意图的详细指导，请参阅 **scientific-schematics** 技能文档。

**主要功能：**
- Nano Banana Pro 自动生成、审查和改进图表
- 创建具有正确格式的出版物质量图像
- 确保可访问性（对色盲友好，高对比度）
- 支持复杂图形的迭代改进

---

## 核心功能

支持三个海报包 — **beamerposter**（Beamer 语法，机构主题）、**tikzposter**（现代、多彩、灵活）和 **baposter**（结构化多列）。包比较、布局和网格系统、设计原则、标准尺寸、每个包的模板、图形和图像集成、配色方案、排版和二维码都在 [references/latex_poster_reference.md](references/latex_poster_reference.md) 中记录。

可重用的每节内容模式、可访问性要求和演示日指导在 [references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md) 中。

## 海报创建工作流程

### 阶段 1：规划和内容开发

1. **确定海报要求**：
   - 会议尺寸规格（A0、36×48 英寸等）
   - 方向（纵向 vs. 横向）
   - 提交截止日期和格式要求

2. **开发内容大纲**：
   - 确定 1-3 个核心信息
   - 选择关键图形（通常 3-6 个主要视觉元素）
   - 为每个部分起草简洁的文本（首选项目符号）
   - 目标为 300-800 个字

3. **选择 LaTeX 包**：
   - beamerposter：如果熟悉 Beamer，需要机构主题
   - tikzposter：用于现代、多彩的设计，具有灵活性
   - baposter：用于结构化、专业的多列布局

### 阶段 2：生成视觉元素（AI 驱动）

**关键点：生成简单的图形，内容最少。每个图形 = 一个信息。**

**内容限制：**
- 最多 4-5 个元素每个图形
- 每个图形最多 15 个字
- 至少 50% 的空白区域
- 巨大的字体（标签 80pt+，关键数字 120pt+）

1. **创建图形目录**：
   ```bash
   mkdir -p figures
   ```

2. **生成简单的视觉元素**：
   ```bash
   # 引言 - 仅 3 个图标/元素
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE visual with ONLY 3 elements: [icon1] [icon2] [icon3]. ONE word labels (80pt+). 50% white space. Readable from 8 feet." -o figures/intro.png
   
   # 方法 - 最多 4 步
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE flowchart with ONLY 4 boxes: STEP1 → STEP2 → STEP3 → STEP4. GIANT labels (100pt+). 50% white space. NO sub-steps." -o figures/methods.png
   
   # 结果 - 仅 3 个条形/比较
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE chart with ONLY 3 bars. GIANT percentages ON bars (120pt+). NO axis, NO legend. 50% white space." -o figures/results.png
   
   # 结论 - 恰好 3 个项目，巨大数字
   python scripts/generate_schematic.py "POSTER FORMAT for A0. EXACTLY 3 key findings: '[NUMBER]' (150pt) '[LABEL]' (60pt) for each. 50% white space. NO other text." -o figures/conclusions.png
   ```

3. **审查生成的图形 - 检查溢出：**
   - **在 25% 放大倍率下查看**：所有文字仍然可读？
   - **计数元素**：超过 5 个？→ 重新生成更简单的
   - **检查空白区域**：少于 40%？→ 在提示中添加 "60% white space"
   - **字体太小？**：添加 "EVEN LARGER" 或增加 pt 大小
   - **仍然溢出？**：减少为 3 个元素而不是 4-5 个

### 阶段 3：设计和布局

1. **选择或创建模板**：
   - 从 `assets/` 中的提供模板开始
   - 自定义配色方案以匹配品牌
   - 配置页面大小和方向

2. **设计布局结构**：
   - 规划列结构（2、3 或 4 列）
   - 规划内容流（通常从左到右，从上到下）
   - 为标题分配空间（10-15%）、内容（70-80%）、页脚（5-10%）

3. **设置排版**：
   - 配置不同层级级别的字体大小
   - 确保 24pt+ 的正文最小字体
   - 测试从 4-6 英尺的距离的易读性

### 阶段 4：内容集成

1. **创建海报标题**：
   - 标题（简洁、描述性、10-15 个字）
   - 作者和所属机构
   - 机构标志（高分辨率）
   - 如果需要，会议标志

2. **集成 AI 生成的图形**：
   - 将所有来自阶段 2 的图形添加到相应部分
   - 使用 `\includegraphics` 并正确调整大小
   - 确保图形主导每个部分（视觉元素优先，文本其次）
   - 在块中居中图形以增强视觉效果

3. **添加最小的支持文本**：
   - 保持文本最小且可扫描（总共 300-800 个字）
   - 使用项目符号，不要段落
   - 使用主动语态
   - 文本应补充图形，而不是重复图形

4. **添加补充元素**：
   - 用于补充材料的二维码
   - 参考文献（仅引用关键论文，5-10 个典型）
   - 联系信息和致谢

### 阶段 5：改进和测试

1. **审查和迭代**：
   - 检查拼写和错误
   - 验证所有图形都是高分辨率的
   - 确保格式一致
   - 确认配色方案协调

2. **测试易读性**：
   - 在 25% 比例下打印并从 2-3 英尺的距离阅读（模拟从 8-12 英尺的距离）
   - 在不同显示器上检查颜色
   - 验证二维码功能正常
   - 请同事审查

3. **优化打印**：
   - 将所有字体嵌入 PDF
   - 验证图像分辨率
   - 检查 PDF 大小要求
   - 如果需要，包含出血区域

### 阶段 6：编译和交付

1. **编译最终 PDF**：
   ```bash
   pdflatex poster.tex
   # 或为更好的字体支持：
   lualatex poster.tex
   ```

2. **验证输出质量**：
   - 检查所有元素是否可见且位置正确
   - 放大到 100% 并检查图形质量
   - 验证颜色符合预期
   - 确认 PDF 在不同查看器中正确打开

3. **准备打印**：
   - 如果需要，导出为 PDF/X-1a
   - 保存备份副本
   - 首先在普通纸上打印测试
   - 在截止日期前 2-3 天订购专业打印

4. **创建补充材料**：
   - 保存 PNG/JPG 版本用于社交媒体
   - 创建传单版本（8.5×11 英寸摘要）
   - 准备用于通过电子邮件共享的数字版本

## 与其他技能的集成

此技能与以下技能有效集成：
- **Scientific Schematics**：关键 — 用于生成所有海报图表和流程图
- **Generate Image / Nano Banana Pro**：用于风格化图形、概念插图和总结视觉
- **Scientific Writing**：用于从论文中开发海报内容
- **Literature Review**：用于 contextualizing 研究
- **Data Analysis**：用于创建结果图形和图表

**推荐工作流程**：始终在创建 LaTeX 海报之前使用 scientific-schematics 和 generate-image 技能生成所有视觉元素。

## 常见错误避免

**AI 生成的图形错误（最常见）：**
- ❌ 一个图形中元素过多（10+ 个）→ 最多保持 3-5 个
- ❌ AI 图形中的文字太小 → 指定 "GIANT (100pt+)" 或 "HUGE (150pt+)"
- ❌ 提示中细节过多 → 使用 "SIMPLE" 和 "ONLY X elements"
- ❌ 未指定空白区域 → 在每个提示中添加 "50% white space"
- ❌ 复杂的流程图有 8+ 步骤 → 最多 4-5 步
- ❌ 比较图表有 6+ 项 → 最多 3 项
- ❌ 关键发现有 5+ 个指标 → 仅显示前 3 个

**修复 AI 图形中的溢出：**
如果您的 AI 生成的图形溢出或文字太小：
1. 在提示中添加 "SIMPLER" 或 "ONLY 3 elements"
2. 增加字体大小： "150pt+" 而不是 "80pt+"
3. 添加 "60% white space" 而不是 "50%"
4. 移除子细节： "NO sub-steps"，"NO axis labels"，"NO legend"
5. 重新生成，元素更少

**设计错误**：
- ❌ 文字过多（超过 1000 个字）
- ❌ 字体大小太小（正文小于 24pt）
- ❌ 低对比度的颜色组合
- ❌ 杂乱的布局，没有空白区域
- ❌ 各部分风格不一致
- ❌ 图像质量差或像素化

**内容错误**：
- ❌ 没有清晰的故事线或信息
- ❌ 研究问题或目标过多
- ❌ 过度使用术语而没有定义
- ❌ 结果没有背景或解释
- ❌ 缺少作者联系信息

**技术错误**：
- ❌ 会议要求的海报尺寸错误
- ❌ 将 RGB 颜色发送到 CMYK 打印机（颜色偏移）
- ❌ 字体未嵌入 PDF
- ❌ 文件大小太大无法提交
- ❌ 二维码太小或未测试

**最佳实践**：
- ✅ 生成简单的 AI 图形，最多 3-5 个元素
- ✅ 使用 GIANT 字体（100pt+）用于图形中的关键数字
- ✅ 在每个 AI 提示中指定 "50% white space"
- ✅ 精确遵循会议尺寸规格
- ✅ 在最终打印前以缩放比例打印测试
- ✅ 使用高对比度、可访问的配色方案
- ✅ 保持文本最小且高度可扫描
- ✅ 包含清晰的联系信息和二维码
- ✅ 仔细校对（错误在海报上会被放大！）

## 包安装

确保安装了所需的 LaTeX 包：

```bash
# 对于 TeX Live（Linux/Mac）
tlmgr install beamerposter tikzposter baposter

# 对于 MiKTeX（Windows）
# 包通常在首次使用时自动安装

# 其他推荐包
tlmgr install qrcode graphics xcolor tcolorbox subcaption
```

## 脚本和自动化

在 `scripts/` 目录中提供辅助脚本：

- `review_poster.sh`：海报审查和验证
- `generate_schematic.py`：生成科学图表和示意图

## 参考文献

- [references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md)：完整的 AI 图形规则、按类型限制、提示示例和审查关卡。
- [references/latex_poster_reference.md](references/latex_poster_reference.md)：包、布局、设计、尺寸、模板、图形、配色方案、排版、二维码。
- [references/compilation_and_quality_control.md](references/compilation_and_quality_control.md)：编译引擎和完整的预打印质量控制流程。
- [references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md)：内容模式、可访问性、演示技巧。
- [references/latex_poster_packages.md](references/latex_poster_packages.md)：beamerposter、tikzposter 和 baposter 的详细比较和示例。
- [references/poster_layout_design.md](references/poster_layout_design.md)：布局原则、网格系统和视觉流。
- [references/poster_design_principles.md](references/poster_design_principles.md)：排版、色彩理论、视觉层次结构和可访问性。
- [references/poster_content_guide.md](references/poster_content_guide.md)：内容组织、写作风格和各部分指导。

## 模板

`assets/` 目录中提供可即用海报模板：

- beamerposter 模板（经典、现代、多彩）
- tikzposter 模板（默认、射线、波浪、信封）
- baposter 模板（纵向、横向、简约）
- 来自不同科学学科的示例海报
- 配色方案定义和机构模板

加载这些模板并根据您的具体研究和会议要求进行自定义。
