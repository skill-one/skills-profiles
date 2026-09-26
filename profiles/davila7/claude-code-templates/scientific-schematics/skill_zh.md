# 科学示意图和图表

## 概述

科学示意图和图表将复杂概念转化为清晰的视觉表现形式用于发表。**此技能使用 Nano Banana Pro AI 进行图表生成，并使用 Gemini 3 Pro 质量审查。**

**工作原理：**
- 用自然语言描述您的图表
- Nano Banana Pro 自动生成符合发表标准的图像
- **Gemini 3 Pro 根据文档类型阈值进行质量审查**
- **智能迭代**：仅当质量低于阈值时才重新生成
- 分钟内即可获得符合发表的输出
- 无需编码、模板或手动绘图

**按文档类型划分的质量阈值：**
| 文档类型 | 阈值 | 描述 |
|---------------|-----------|-------------|
| 期刊 | 8.5/10 | Nature、Science、同行评审期刊 |
| 会议 | 8.0/10 | 会议论文 |
| 学位论文 | 8.0/10 | 学位论文、论文 |
| 资助 | 8.0/10 | 资助提案 |
| 预印本 | 7.5/10 | arXiv、bioRxiv 等 |
| 报告 | 7.5/10 | 技术报告 |
| 海报 | 7.0/10 | 学术海报 |
| 演示文稿 | 6.5/10 | 幻灯片、演讲 |
| 默认 | 7.5/10 | 通用 |

**只需描述您想要的内容，Nano Banana Pro 就会为您创建。** 所有图表都存储在 figures/ 子文件夹中，并在论文/海报中引用。

## 快速入门：生成任何图表

通过简单地描述即可创建任何科学图表。Nano Banana Pro 处理所有内容，并使用 **智能迭代**：

```bash
# 为期刊论文生成（最高质量阈值：8.5/10）
python scripts/generate_schematic.py "CONSORT 参与者流程图，500 名受试者筛选，150 名排除，350 名随机分配" -o figures/consort.png --doc-type journal

# 为演示文稿生成（较低阈值：6.5/10 - 更快）
python scripts/generate_schematic.py "Transformer 编码器-解码器架构显示多头注意力" -o figures/transformer.png --doc-type presentation

# 为海报生成（中等阈值：7.0/10）
python scripts/generate_schematic.py "MAPK 信号通路从 EGFR 到基因转录" -o figures/mapk_pathway.png --doc-type poster

# 自定义最大迭代次数（最多 2 次）
python scripts/generate_schematic.py "复杂电路图，包含运算放大器、电阻和电容器" -o figures/circuit.png --iterations 2 --doc-type journal
```

**幕后发生的事情：**
1. **生成 1**：Nano Banana Pro 根据科学图表最佳实践创建初始图像
2. **审查 1**：**Gemini 3 Pro** 根据文档类型阈值评估质量
3. **决策**：如果质量 >= 阈值 → **完成**（无需更多迭代！）
4. **如果低于阈值**：根据评论改进提示，重新生成
5. **重复**：直到质量满足阈值或达到最大迭代次数

**智能迭代的好处：**
- ✅ 如果第一次生成质量足够，则节省 API 调用
- ✅ 为期刊论文设定更高的质量标准
- ✅ 演示文稿/海报更快的周转时间
- ✅ 每种用例都适用适当的质量

**输出**：版本化的图像和包含质量分数、评论和早期停止信息的详细审查日志。

### 配置

设置您的 OpenRouter API 密钥：
```bash
export OPENROUTER_API_KEY='your_api_key_here'
```

在 https://openrouter.ai/keys 获取 API 密钥

### AI 生成最佳实践

**用于科学图表的有效提示：**

✓ **好的提示**（具体、详细）：
- "CONSORT 流程图显示参与者流程从筛选（n=500）通过随机分配到最终分析"
- "Transformer 神经网络架构，编码器堆栈在左侧，解码器堆栈在右侧，显示多头注意力和交叉注意力连接"
- "生物信号级联：EGFR 受体 → RAS → RAF → MEK → ERK → 细胞核，标有磷酸化步骤"
- "物联网系统框图：传感器 → 微控制器 → WiFi 模块 → 云服务器 → 移动应用"

✗ **避免模糊的提示**：
- "制作流程图"（太笼统）
- "神经网络"（哪种类型？包含哪些组件？）
- "通路图"（哪个通路？包含哪些分子？）

**包含的关键元素：**
- **类型**：流程图、架构图、通路、电路等
- **组件**：要包含的特定元素
- **流程/方向**：元素如何连接（从左到右、从上到下）
- **标签**：要包含的关键注释或文本
- **样式**：任何特定的视觉要求

**科学质量指南**（自动应用）：
- 干净的白色/浅色背景
- 高对比度以提高可读性
- 清晰易读的标签（最小 10pt）
- 专业字体（无衬线字体）
- 色盲友好的颜色（Okabe-Ito 调色板）
- 适当的间距以防止拥挤
- 在适当的地方添加比例尺、图例、坐标轴

## 何时使用此技能

当您需要：
- 创建神经网络架构图（Transformer、CNN、RNN 等）
- 描述系统架构和数据流图
- 绘制研究设计的方法学流程图（CONSORT、PRISMA）
- 可视化算法工作流和处理管道
- 创建电路图和电气示意图
- 描绘生物通路和分子相互作用
- 生成网络拓扑和层次结构
- 描述概念框架和理论模型
- 为技术论文设计框图

## 如何使用此技能

**用自然语言描述您的图表。** Nano Banana Pro 自动生成：

```bash
python scripts/generate_schematic.py "your diagram description" -o output.png
```

**就这样！** AI 处理：
- ✓ 布局和构图
- ✓ 标签和注释
- ✓ 颜色和样式
- ✓ 质量审查和改进
- ✓ 符合发表的输出

**适用于所有图表类型：**
- 流程图（CONSORT、PRISMA 等）
- 神经网络架构
- 生物通路
- 电路图
- 系统架构
- 框图
- 任何科学可视化

**无需编码、模板或手动绘图。**

---

# AI 生成模式（Nano Banana Pro + Gemini 3 Pro 审查）

## 智能迭代优化工作流程

AI 生成系统使用 **智能迭代** - 仅当质量低于您的文档类型阈值时才重新生成：

### 智能迭代如何工作

```
┌─────────────────────────────────────────────────────┐
│  1. 使用 Nano Banana Pro 生成图像                 │
│                    ↓                                │
│  2. 使用 Gemini 3 Pro 审查质量                   │
│                    ↓                                │
│  3. 分数 >= 阈值？                             │
│       是 → 完成！ (早期停止)                      │
│       否  → 改进提示，返回步骤 1            │
│                    ↓                                │
│  4. 重复直到质量满足 OR 最大迭代次数      │
└─────────────────────────────────────────────────────┘
```

### 迭代 1：初始生成
**提示构建：**
```
科学图表指南 + 用户请求
```

**输出:** `diagram_v1.png`

### Gemini 3 Pro 进行质量审查

Gemini 3 Pro 评估图表：
1. **科学准确性**（0-2 分）- 正确的概念、符号、关系
2. **清晰度和可读性**（0-2 分）- 易于理解，清晰的层次结构
3. **标签质量**（0-2 分）- 完整、易读、一致的标签
4. **布局和构图**（0-2 分）- 逻辑流程、平衡、无重叠
5. **专业外观**（0-2 分）- 符合发表标准的质量

**示例审查输出：**
```
分数：8.0

优势：
- 从上到下的清晰流程
- 所有阶段都正确标记
- 专业字体

问题：
- 参与者数量略小
- 排除框有轻微重叠

结论：可接受（对于海报，阈值为 7.0）
```

### 决策点：继续还是停止？

| 如果分数... | 操作 |
|-------------|--------|
| >= 阈值 | **停止** - 质量足以满足此文档类型 |
| < 阈值 | 继续到下一个迭代，使用改进的提示 |

**示例：**
- 对于 **海报**（阈值为 7.0）：分数为 7.5 → **1 次迭代后完成！**
- 对于 **期刊**（阈值为 8.5）：分数为 7.5 → 继续改进

### 后续迭代（如果需要）

如果质量低于阈值，系统：
1. 从 Gemini 3 Pro 的审查中提取具体问题
2. 使用改进说明增强提示
3. 使用 Nano Banana Pro 重新生成
4. 再次使用 Gemini 3 Pro 进行审查
5. 重复，直到质量满足阈值或达到最大迭代次数

### 审查日志
所有迭代都保存带有 JSON 审查日志，包括早期停止信息：
```json
{
  "user_prompt": "CONSORT 参与者流程图...",
  "doc_type": "poster",
  "quality_threshold": 7.0,
  "iterations": [
    {
      "iteration": 1,
      "image_path": "figures/consort_v1.png",
      "score": 7.5,
      "needs_improvement": false,
      "critique": "分数：7.5\n优势：..."
    }
  ],
  "final_score": 7.5,
  "early_stop": true,
  "early_stop_reason": "分数 7.5 满足海报的阈值 7.0"
}
```

**注意：** 使用智能迭代时，您可能会看到仅 1 次迭代而不是完整的 2 次迭代，如果早期达到质量！

## 高级 AI 生成使用

### Python API

```python
from scripts.generate_schematic_ai import ScientificSchematicGenerator

# 初始化生成器
generator = ScientificSchematicGenerator(
    api_key="your_openrouter_key",
    verbose=True
)

# 使用迭代优化生成（最多 2 次迭代）
results = generator.generate_iterative(
    user_prompt="Transformer 架构图",
    output_path="figures/transformer.png",
    iterations=2
)

# 访问结果
print(f"最终分数：{results['final_score']}/10")
print(f"最终图像：{results['final_image']}")

# 审查单个迭代
for iteration in results['iterations']:
    print(f"迭代 {iteration['iteration']}: {iteration['score']}/10")
    print(f"评论：{iteration['critique']}")
```

### 命令行选项

```bash
# 基本用法（默认阈值 7.5/10）
python scripts/generate_schematic.py "diagram description" -o output.png

# 自定义迭代次数（最多 2 次）
python scripts/generate_schematic.py "复杂 diagram" -o diagram.png --iterations 2

# 详细模式
python scripts/generate_schematic.py "diagram" -o out.png -v
```

**注意：** Nano Banana Pro AI 生成系统在其迭代优化过程中包括自动质量审查。每个迭代都根据科学准确性、清晰度和可访问性进行评估。

## 最佳实践总结

### 设计原则

1. **清晰胜于复杂** - 简化，移除不必要的元素
2. **一致的样式** - 使用模板和样式文件
3. **色盲可访问性** - 使用 Okabe-Ito 调色板，冗余编码
4. **适当的字体** - 无衬线字体，最小 7-8 pt
5. **矢量格式** - 优先使用 PDF/SVG，或 300+ DPI 用于栅格

### 技术要求

1. **分辨率** - 优先矢量，或 300+ DPI 用于栅格
2. **文件格式** - PDF 用于 LaTeX，SVG 用于网页，PNG 作为备用
3. **色域** - 数字 RGB，印刷 CMYK（如有必要则转换）
4. **线权重** - 最小 0.5 pt，典型 1-2 pt
5. **文本大小** - 7-8 pt 最小最终尺寸

### 集成指南

1. **LaTeX 中包含** - 使用 `\includegraphics{}` 引用生成的图像
2. **详细说明** - 描述所有元素和缩写
3. **文本中引用** - 在叙述流程中解释图表
4. **保持一致性** - 论文中所有图表使用相同样式
5. **版本控制** - 将提示和生成的图像保存在存储库中

## 常见问题排查

### AI 生成问题

**问题**：文本或元素重叠
- **解决方案**：AI 生成自动处理间距
- **解决方案**：增加迭代次数：`--iterations 2` 以获得更好的优化

**问题**：元素连接不正确
- **解决方案**：更具体地描述连接和布局的提示
- **解决方案**：增加迭代次数以获得更好的优化

### 图像质量问题

**问题**：导出质量差
- **解决方案**：AI 生成自动生成高质量图像
- **解决方案**：增加迭代次数以获得更好的结果：`--iterations 2`

**问题**：生成后元素重叠
- **解决方案**：AI 生成自动处理间距
- **解决方案**：增加迭代次数：`--iterations 2` 以获得更好的优化
- **解决方案**：更具体地描述布局和间距要求的提示

### 质量检查问题

**问题**：误报重叠
- **解决方案**：调整阈值：`detect_overlaps(image_path, threshold=0.98)`
- **解决方案**：在视觉报告中手动审查标记的区域

**问题**：生成图像质量低
- **解决方案**：AI 生成默认生成高质量图像
- **解决方案**：增加迭代次数以获得更好的结果：`--iterations 2`

**问题**：色盲模拟显示对比度差
- **解决方案**：明确在代码中切换到 Okabe-Ito 调色板
- **解决方案**：添加冗余编码（形状、图案、线型）
- **解决方案**：增加颜色饱和度和亮度差异

**问题**：检测到高严重性重叠
- **解决方案**：审查 overlap_report.json 以获取确切位置
- **解决方案**：在那些特定区域增加间距
- **解决方案**：使用调整后的参数重新运行并验证

**问题**：视觉报告生成失败
- **解决方案**：检查 Pillow 和 matplotlib 的安装
- **解决方案**：确保图像文件可读：`Image.open(path).verify()`
- **解决方案**：检查生成报告所需的磁盘空间

### 可访问性问题

**问题**：在灰度中颜色无法区分
- **解决方案**：运行可访问性检查器：`verify_accessibility(image_path)`
- **解决方案**：添加图案、形状或线型以实现冗余
- **解决方案**：增加元素之间的对比度

**问题**：打印时文本太小
- **解决方案**：运行分辨率验证器：`validate_resolution(image_path)`
- **解决方案**：在最终尺寸下设计，使用最小 7-8 pt 字体
- **解决方案**：检查分辨率报告中的实际尺寸

**问题**：可访问性检查始终失败
- **解决方案**：审查可访问性报告.json 以获取具体失败原因
- **解决方案**：将颜色对比度至少增加 20%
- **解决方案**：在实际灰度转换前测试

## 资源和参考

### 详细参考

加载这些文件以获取特定主题的全面信息：

- **`references/diagram_types.md`** - 科学图表类型目录及示例
- **`references/best_practices.md`** - 发表标准和可访问性指南

### 外部资源

**Python 库**
- Schemdraw 文档：https://schemdraw.readthedocs.io/
- NetworkX 文档：https://networkx.org/documentation/
- Matplotlib 文档：https://matplotlib.org/

**发表标准**
- Nature 图表指南：https://www.nature.com/nature/for-authors/final-submission
- Science 图表指南：https://www.science.org/content/page/instructions-preparing-initial-manuscript
- CONSORT 图表：http://www.consort-statement.org/consort-statement/flow-diagram

## 与其他技能的集成

此技能与以下技能协同工作：

- **科学写作** - 图表遵循图表最佳实践
- **科学可视化** - 共享调色板和样式
- **LaTeX 海报** - 为海报演示文稿生成图表
- **研究资助** - 提案的方法学图表
- **同行评审** - 评估图表清晰度和可访问性

## 快速参考清单

提交图表前请验证：

### 视觉质量
- [ ] 高质量图像格式（来自 AI 生成的 PNG）
- [ ] 无重叠元素（AI 自动处理）
- [ ] 适当间距（AI 优化）
- [ ] 干净专业的对齐
- [ ] 所有箭头正确连接到目标

### 可访问性
- [ ] 使用色盲安全调色板（Okabe-Ito）
- [ ] 在灰度中工作（使用可访问性检查器测试）
- [ ] 元素之间具有足够对比度（已验证）
- [ ] 适当的地方使用冗余编码（形状 + 颜色）
- [ ] 色盲模拟通过所有检查

### 字体和可读性
- [ ] 文本最小 7-8 pt 最终尺寸
- [ ] 所有元素标记清晰完整
- [ ] 一致的字体家族和大小
- [ ] 无文本重叠或截断
- [ ] 包含单位（如适用）

### 发表标准
- [ ] 与论文中其他图表保持一致的样式
- [ ] 编写详细的图表说明，定义所有缩写
- [ ] 在文本中适当引用
- [ ] 满足期刊特定的尺寸要求
- [ ] 按期刊要求导出所需格式（PDF/EPS/TIFF）

### 质量验证（必需）
- [ ] 运行 `run_quality_checks()` 并获得通过状态
- [ ] 审查重叠检测报告（无高严重性重叠）
- [ ] 通过可访问性验证（灰度和色盲）
- [ ] 验证目标 DPI 的分辨率（印刷 300+ DPI）
- [ ] 生成并审查视觉质量报告
- [ ] 所有质量报告与图表文件一起保存

### 文档和版本控制
- [ ] 保存源文件（.tex, .py）以供将来修改
- [ ] 存档质量报告在 `quality_reports/` 目录
- [ ] 记录配置参数（颜色、间距、尺寸）
- [ ] Git 提交包含源文件、输出和质量报告
- [ ] README 或注释解释如何重新生成图表

### 最终集成检查
- [ ] 图表在编译的论文中正确显示
- [ ] 参考文献工作正常（`\ref{}` 指向正确的图表）
- [ ] 图表编号与文本引用匹配
- [ ] 图表说明出现在正确的页面上
- [ ] 与图表相关的编译警告或错误

## 环境设置

```bash
# 必需
export OPENROUTER_API_KEY='your_api_key_here'

# 在 https://openrouter.ai/keys 获取密钥
```

## 入门指南

**最简单的用法：**
```bash
python scripts/generate_schematic.py "your diagram description" -o output.png
```

---

使用此技能创建清晰、可访问、符合发表标准的图表，有效传达复杂的科学概念。AI 驱动的流程与迭代优化确保图表符合专业标准。
