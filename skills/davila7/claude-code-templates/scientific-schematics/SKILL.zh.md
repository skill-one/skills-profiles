---
name: scientific-schematics
description: 使用 Nano Banana Pro AI 创建具有高质量科学图表，通过智能迭代优化。采用 Gemini 3 Pro 进行质量审核。仅在文档类型质量低于阈值时才重新生成。专精于神经网络架构、系统图表、流程图、生物通路和复杂的科学可视化。
---

# 科学示意图与图表

## 概述

科学示意图和图表将复杂的概念转化为清晰的视觉表达，适用于出版发布。**本技能使用 Nano Banana Pro AI 进行图表生成，并由 Gemini 3 Pro 进行质量审查。**

**工作原理：**
- 使用自然语言描述您的图表
- Nano Banana Pro 自动生成就可出版级别的图像
- **Gemini 3 Pro 根据文档类型的阈值进行质量审查**
- **智能迭代**：仅在质量低于阈值时重新生成
- 几分钟内即可输出可发布的成果
- 无需编程、模板或手动绘制

**按文档类型划分的质量阈值：**
| 文档类型 | 阈值 | 说明 |
|---------------|-----------|-------------|
| journal | 8.5/10 | 《自然》、《科学》、同行评审期刊 |
| conference | 8.0/10 | 会议论文 |
| thesis | 8.0/10 | 学位论文、硕士/博士论文 |
| grant | 8.0/10 | 基金申请书 |
| preprint | 7.5/10 | arXiv、bioRxiv 等 |
| report | 7.5/10 | 技术报告 |
| poster | 7.0/10 | 学术海报 |
| presentation | 6.5/10 | 幻灯片、演讲 |
| default | 7.5/10 | 通用用途 |

**只需描述您想要的内容，Nano Banana Pro 便会将其创建出来。** 所有图表都存储在 figures/ 子文件夹中，并在论文/海报中被引用。

## 快速入门：生成任意图表

只需描述即可创建任何科学图表。Nano Banana Pro 会利用**智能迭代**自动处理所有事项：

```bash
# 为期刊论文生成（最高质量阈值：8.5/10）
python scripts/generate_schematic.py "CONSORT 参与者流程图，500 人筛查，150 人排除，350 人随机分组" -o figures/consort.png --doc-type journal

# 为演示文稿生成（较低阈值：6.5/10 - 速度更快）
python scripts/generate_schematic.py "展示多头注意力的 Transformer 编码器-解码器架构" -o figures/transformer.png --doc-type presentation

# 为海报生成（中等阈值：7.0/10）
python scripts/generate_schematic.py "从 EGFR 到基因转录的 MAPK 信号通路" -o figures/mapk_pathway.png --doc-type poster

# 自定义最大迭代次数（最多 2 次）
python scripts/generate_schematic.py "包含运算放大器、电阻器和电容器的复杂电路图" -o figures/circuit.png --iterations 2 --doc-type journal
```

**幕后发生的事情：**
1. **生成 1**：Nano Banana Pro 遵循科学图表最佳实践创建初始图像
2. **审查 1**：**Gemini 3 Pro** 根据文档类型阈值评估质量
3. **决策**：如果质量 >= 阈值 → **完成**（无需更多迭代！）
4. **如果低于阈值**：根据评审意见改进提示词，重新生成
5. **重复**：直到质量达到阈值或达到最大迭代次数

**智能迭代的优势：**
- ✅ 如果首次生成足够好，可节省 API 调用
- ✅ 对期刊论文实行更高的质量标准
- ✅ 加快演示文稿/海报的周转时间
- ✅ 为每种用例提供适当的质量

**输出**：带版本的图像以及详细的审查日志，包含质量评分、评审意见和提前停止信息。

### 配置

设置您的 OpenRouter API 密钥：
```bash
export OPENROUTER_API_KEY='your_api_key_here'
```

在此处获取 API 密钥：https://openrouter.ai/keys

### AI 生成最佳实践

**科学图表的有效提示词：**

✓ **好的提示词**（具体、详细）：
- "展示从筛查（n=500）到随机分组再到最终分析的参与者流程的 CONSORT 流程图"
- "左侧为编码器堆栈、右侧为解码器堆栈的 Transformer 神经网络架构，展示多头注意力和交叉注意力连接"
- "生物信号级联：EGFR 受体 → RAS → RAF → MEK → ERK → 细胞核，标注磷酸化步骤"
- "物联网系统的方框图：传感器 → 微控制器 → WiFi 模块 → 云服务器 → 移动应用"

✗ **避免模糊的提示词**：
- "制作一个流程图"（过于笼统）
- "神经网络"（哪种类型？有哪些组件？）
- "通路图"（哪种通路？有哪些分子？）

**应包含的关键要素：**
- **类型**：流程图、架构图、通路、电路等
- **组件**：要包含的具体元素
- **流向/方向**：元素如何连接（从左到右、从上到下）
- **标签**：要包含的关键注释或文本
- **风格**：任何特定的视觉要求

**科学质量准则**（自动应用）：
- 干净的白色/浅色背景
- 高对比度以确保可读性
- 清晰、易读的标签（最小 10pt）
- 专业排版（无衬线字体）
- 对色盲友好的颜色（Okabe-Ito 调色板）
- 适当的间距以防止拥挤
- 在适当位置使用比例尺、图例、坐标轴

## 何时使用此技能

在以下情况下应使用此技能：
- 创建神经网络架构图（Transformer、CNN、RNN 等）
- 说明系统架构和数据流图
- 绘制研究设计的方法论流程图（CONSORT、PRISMA）
- 可视化算法工作流程和处理管道
- 创建电路图和电气原理图
- 描绘生物通路和分子相互作用
- 生成网络拓扑和层级结构
- 说明概念框架和理论模型
- 为技术论文设计方框图

## 如何使用此技能

**只需使用自然语言描述您的图表即可。** Nano Banana Pro 会自动生成：

```bash
python scripts/generate_schematic.py "您的图表描述" -o output.png
```

**就这么简单！** AI 负责处理：
- ✓ 布局和构图
- ✓ 标签和注释
- ✓ 颜色和样式
- ✓ 质量审查和改进
- ✓ 可发布级别的输出

**适用于所有类型的图表：**
- 流程图（CONSORT、PRISMA 等）
- 神经网络架构
- 生物通路
- 电路图
- 系统架构
- 方框图
- 任何科学可视化

**无需编程，无需模板，无需手动绘制。**

---

# AI 生成模式（Nano Banana Pro + Gemini 3 Pro 审查）

## 智能迭代优化工作流

AI 生成系统使用**智能迭代** - 它仅在质量低于您的文档类型阈值时才会重新生成：

### 智能迭代的工作原理

```
┌─────────────────────────────────────────────────────┐
│  1. 使用 Nano Banana Pro 生成图像                    │
│                    ↓                                │
│  2. 使用 Gemini 3 Pro 审查质量                       │
│                    ↓                                │
│  3. 得分 >= 阈值？                                   │
│       是 → 完成！（提前停止）                        │
│       否  → 改进提示词，回到步骤 1                   │
│                    ↓                                │
│  4. 重复直到质量达标或达到最大迭代次数               │
└─────────────────────────────────────────────────────┘
```

### 迭代 1：初始生成
**提示词构建：**
```
科学图表准则 + 用户请求
```

**输出**：`diagram_v1.png`

### 由 Gemini 3 Pro 进行的质量审查

Gemini 3 Pro 从以下方面评估图表：
1. **科学准确性**（0-2 分） - 正确的概念、符号、关系
2. **清晰度和可读性**（0-2 分） - 易于理解，层级清晰
3. **标签质量**（0-2 分） - 完整、易读、一致的标签
4. **布局和构图**（0-2 分） - 逻辑流畅、平衡、无重叠
5. **专业外观**（0-2 分） - 达到可发布的质量

**审查输出示例：**
```
SCORE: 8.0

STRENGTHS:
- 从上到下的流程清晰
- 所有阶段都已正确标注
- 专业排版

ISSUES:
- 参与者计数略微偏小
- 排除框有轻微重叠

VERDICT: ACCEPTABLE (for poster, threshold 7.0)
```

### 决策点：继续还是停止？

| 如果得分... | 操作 |
|-------------|--------|
| >= 阈值 | **停止** - 质量对于此文档类型已足够好 |
| < 阈值 | 使用改进的提示词继续下一次迭代 |

**示例：**
- 对于**海报**（阈值 7.0）：得分 7.5 → **1 次迭代即完成！**
- 对于**期刊**（阈值 8.5）：得分 7.5 → 继续改进

### 后续迭代（仅在需要时）

如果质量低于阈值，系统将：
1. 从 Gemini 3 Pro 的审查中提取具体问题
2. 使用改进指令增强提示词
3. 使用 Nano Banana Pro 重新生成
4. 再次使用 Gemini 3 Pro 审查
5. 重复执行，直到达到阈值或达到最大迭代次数

### 审查日志
所有迭代都会与 JSON 审查日志一起保存，其中包含提前停止信息：
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
      "critique": "SCORE: 7.5\nSTRENGTHS:..."
    }
  ],
  "final_score": 7.5,
  "early_stop": true,
  "early_stop_reason": "Quality score 7.5 meets threshold 7.0 for poster"
}
```

**注意**：借助智能迭代，如果早期达到质量要求，您可能只看到 1 次迭代，而不是完整的 2 次！

## 高级 AI 生成用法

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
print(f"最终得分: {results['final_score']}/10")
print(f"最终图像: {results['final_image']}")

# 审查单独的迭代
for iteration in results['iterations']:
    print(f"迭代 {iteration['iteration']}: {iteration['score']}/10")
    print(f"批评: {iteration['critique']}")
```

### 命令行选项

```bash
# 基本用法（默认阈值 7.5/10）
python scripts/generate_schematic.py "图表描述" -o output.png

# 指定文档类型以获得适当的质量阈值
python scripts/generate_schematic.py "diagram" -o out.png --doc-type journal      # 8.5/10
python scripts/generate_schematic.py "diagram" -o out.png --doc-type conference   # 8.0/10
python scripts/generate_schematic.py "diagram" -o out.png --doc-type poster       # 7.0/10
python scripts/generate_schematic.py "diagram" -o out.png --doc-type presentation # 6.5/10

# 自定义最大迭代次数（1-2）
python scripts/generate_schematic.py "complex diagram" -o diagram.png --iterations 2

# 详细输出（查看所有 API 调用和审查）
python scripts/generate_schematic.py "flowchart" -o flow.png -v

# 通过标志提供 API 密钥
python scripts/generate_schematic.py "diagram" -o out.png --api-key "sk-or-v1-..."

# 组合选项
python scripts/generate_schematic.py "neural network" -o nn.png --doc-type journal --iterations 2 -v
```

### 提示词工程技巧

**1. 具体说明布局：**
```
✓ "流程图，垂直流向，从上到下"
✓ "架构图，左侧为编码器，右侧为解码器"
✓ "环形通路图，顺时针流向"
```

**2. 包含定量细节：**
```
✓ "神经网络，输入层（784 个节点），隐藏层（128 个节点），输出（10 个节点）"
✓ "流程图显示 n=500 人筛查，n=150 人排除，n=350 人随机分组"
✓ "电路包含 1kΩ 电阻器，10µF 电容器，5V 电源"
```

**3. 指定视觉风格：**
```
✓ "极简方框图，线条整洁"
✓ "详细的生物通路，包含蛋白质结构"
✓ "技术原理图，使用工程符号"
```

**4. 请求特定标签：**
```
✓ "将所有箭头标注为激活/抑制"
✓ "在每个方框中包含层维度"
✓ "使用时间戳显示时间推移"
```

**5. 提及颜色要求：**
```
✓ "使用对色盲友好的颜色"
✓ "兼容灰度的设计"
✓ "按功能进行颜色编码：输入为蓝色，处理为绿色，输出为红色"
```

## AI 生成示例

### 示例 1：CONSORT 流程图
```bash
python scripts/generate_schematic.py \
  "用于随机对照试验的 CONSORT 参与者流程图。 \
   顶部以“评估资格（n=500）”开始。 \
   显示“排除（n=150）”，原因包括：年龄<18 岁（n=80），拒绝（n=50），其他（n=20）。 \
   然后“随机分组（n=350）”分为两组： \
   “治疗组（n=175）”和“对照组（n=175）”。 \
   每组显示“失访”（n=15 和 n=10）。 \
   以“分析”（n=160 和 n=165）结束。 \
   使用蓝色方框表示流程步骤，橙色表示排除，绿色表示最终分析。" \
  -o figures/consort.png
```

### 示例 2：神经网络架构
```bash
python scripts/generate_schematic.py \
  "Transformer 编码器-解码器架构图。 \
   左侧：包含输入嵌入、位置编码、 \
   多头自注意力、Add & Norm、前馈网络、Add & Norm 的编码器堆栈。 \
   右侧：包含输出嵌入、位置编码、 \
   掩码自注意力、Add & Norm、交叉注意力（接收来自编码器的信号）、 \
   Add & Norm、前馈网络、Add & Norm、线性 & Softmax 的解码器堆栈。 \
   用虚线展示从编码器到解码器的交叉注意力连接。 \
   编码器使用浅蓝色，解码器使用浅红色。 \
   清晰地标注所有组件。" \
  -o figures/transformer.png --iterations 2
```

### 示例 3：生物通路
```bash
python scripts/generate_schematic.py \
  "MAPK 信号通路图。 \
   从细胞膜（顶部）的 EGFR 受体开始。 \
   箭头向下指向 RAS（带 GTP 标签）。 \
   箭头指向 RAF 激酶。 \
   箭头指向 MEK 激酶。 \
   箭头指向 ERK 激酶。 \
   最后一个箭头指向细胞核，显示基因转录。 \
   将每个箭头标注为“磷酸化”或“激活”。 \
   蛋白质使用圆角矩形，每个蛋白质使用不同的颜色。 \
   在顶部包含膜边界线。" \
  -o figures/mapk_pathway.png
```

### 示例 4：系统架构
```bash
python scripts/generate_schematic.py \
  "物联网系统架构方框图。 \
   底层：传感器（温度、湿度、运动）位于绿色方框中。 \
   中层：位于蓝色方框中的微控制器（ESP32）。 \
   连接到 WiFi 模块（橙色方框）和显示屏（紫色方框）。 \
   顶层：连接到移动应用（浅蓝色方框）的云服务器（灰色方框）。 \
   显示所有组件之间的数据流箭头。 \
   使用协议标注连接：I2C, UART, WiFi, HTTPS。" \
  -o figures/iot_architecture.png
```

---

## 命令行用法

生成科学示意图的主要入口点：

```bash
# 基本用法
python scripts/generate_schematic.py "图表描述" -o output.png

# 自定义迭代次数（最多 2 次）
python scripts/generate_schematic.py "complex diagram" -o diagram.png --iterations 2

# 详细模式
python scripts/generate_schematic.py "diagram" -o out.png -v
```

**注意**：Nano Banana Pro AI 生成系统在其迭代优化过程中包含自动质量审查。每次迭代都会针对科学准确性、清晰度和无障碍性进行评估。

## 最佳实践摘要

### 设计原则

1. **清晰优于复杂** - 简化，移除不必要的元素
2. **风格一致** - 使用模板和样式文件
3. **色盲无障碍** - 使用 Okabe-Ito 调色板，冗余编码
4. **适当的排版** - 无衬线字体，最小 7-8 pt
5. **矢量格式** - 出版时始终使用 PDF/SVG

### 技术要求

1. **分辨率** - 首选矢量格式，或光栅格式需 300+ DPI
2. **文件格式** - LaTeX 使用 PDF，网络使用 SVG，PNG 作为后备
3. **色彩空间** - 数字使用 RGB，印刷使用 CMYK（如有需要则转换）
4. **线宽** - 最小 0.5 pt，典型 1-2 pt
5. **文本大小** - 最终尺寸下最小 7-8 pt

### 集成指南

1. **LaTeX中包含** - 使用`\includegraphics{}`包含生成图像
2. **详细说明** - 描述所有元素和缩写
3. **文本中引用** - 在叙述流程中解释图表
4. **保持一致性** - 论文中所有图表使用相同风格
5. **版本控制** - 将提示和生成图像保存在存储库中

## 常见问题排查

### AI生成问题

**问题**：文本或元素重叠
- **解决方案**：AI生成自动处理间距
- **解决方案**：增加迭代次数：`--iterations 2`以获得更好的细化效果

**问题**：元素连接不正确
- **解决方案**：使提示更具体地描述连接和布局
- **解决方案**：增加迭代次数以获得更好的细化效果

### 图像质量问题

**问题**：导出质量差
- **解决方案**：AI生成自动生成高质量图像
- **解决方案**：增加迭代次数以获得更好的结果：`--iterations 2`

**问题**：生成后元素重叠
- **解决方案**：AI生成自动处理间距
- **解决方案**：增加迭代次数：`--iterations 2`以获得更好的细化效果
- **解决方案**：使提示更具体地描述布局和间距要求

### 质量检查问题

**问题**：误报重叠检测
- **解决方案**：调整阈值：`detect_overlaps(image_path, threshold=0.98)`
- **解决方案**：手动检查视觉报告中的标记区域

**问题**：生成图像质量低
- **解决方案**：AI生成默认生成高质量图像
- **解决方案**：增加迭代次数以获得更好的结果：`--iterations 2`

**问题**：色盲模拟显示对比度差
- **解决方案**：在代码中显式切换到Okabe-Ito调色板
- **解决方案**：添加冗余编码（形状、图案、线型）
- **解决方案**：增加颜色饱和度和亮度差异

**问题**：检测到高严重性重叠
- **解决方案**：查看overlap_report.json以获取确切位置
- **解决方案**：增加这些特定区域的间距
- **解决方案**：使用调整后的参数重新运行并验证

**问题**：视觉报告生成失败
- **解决方案**：检查Pillow和matplotlib的安装
- **解决方案**：确保图像文件可读：`Image.open(path).verify()`
- **解决方案**：检查报告生成所需的磁盘空间

### 无障碍问题

**问题**：在灰度图中颜色无法区分
- **解决方案**：运行无障碍检查器：`verify_accessibility(image_path)`
- **解决方案**：添加图案、形状或线型以实现冗余
- **解决方案**：增加相邻元素之间的对比度

**问题**：打印时文本太小
- **解决方案**：运行分辨率验证器：`validate_resolution(image_path)`
- **解决方案**：最终尺寸设计，使用最小7-8磅字体
- **解决方案**：检查分辨率报告中的物理尺寸

**问题**：无障碍检查始终失败
- **解决方案**：查看accessibility_report.json以获取具体失败情况
- **解决方案**：至少增加20%的颜色对比度
- **解决方案**：在实际灰度转换前进行测试

## 资源和参考

### 详细参考

加载这些文件以获取特定主题的全面信息：

- **`references/diagram_types.md`** - 科学图表类型的目录及示例
- **`references/best_practices.md`** - 出版标准和无障碍指南

### 外部资源

**Python库**
- Schemdraw文档：https://schemdraw.readthedocs.io/
- NetworkX文档：https://networkx.org/documentation/
- Matplotlib文档：https://matplotlib.org/

**出版标准**
- Nature图表指南：https://www.nature.com/nature/for-authors/final-submission
- Science图表指南：https://www.science.org/content/page/instructions-preparing-initial-manuscript
- CONSORT图表：http://www.consort-statement.org/consort-statement/flow-diagram

## 与其他技能的集成

这项技能与其他技能协同工作：

- **科学写作** - 图表遵循图表最佳实践
- **科学可视化** - 共享调色板和样式
- **LaTeX海报** - 为海报演示生成图表
- **研究资助** - 提案的方法论图表
- **同行评审** - 评估图表清晰度和无障碍性

## 快速参考清单

提交图表前请验证：

### 视觉质量
- [ ] 高质量图像格式（AI生成PNG）
- [ ] 无重叠元素（AI自动处理）
- [ ] 所有组件之间间距充足（AI优化）
- [ ] 清洁、专业的对齐
- [ ] 所有箭头正确连接到目标

### 无障碍性
- [ ] 使用色盲安全调色板（Okabe-Ito）
- [ ] 在灰度图中可用（使用无障碍检查器测试）
- [ ] 元素之间对比度充足（已验证）
- [ ] 适当位置添加冗余编码（形状+颜色）
- [ ] 色盲模拟通过所有检查

### 字体和可读性
- [ ] 最终尺寸文本最小7-8磅
- [ ] 所有元素标签清晰完整
- [ ] 统一的字体家族和尺寸
- [ ] 无文本重叠或裁剪
- [ ] 包含适用单位

### 出版标准
- [ ] 与文稿中其他图表风格一致
- [ ] 完整的说明，定义所有缩写
- [ ] 在文稿文本中正确引用
- [ ] 满足期刊特定的尺寸要求
- [ ] 导出期刊要求的格式（PDF/EPS/TIFF）

### 质量验证（必需）
- [ ] 运行`run_quality_checks()`并达到PASS状态
- [ ] 查看过重叠检测报告（无高严重性重叠）
- [ ] 通过无障碍验证（灰度和色盲）
- [ ] 在目标DPI（打印300+）验证分辨率
- [ ] 生成并审查视觉质量报告
- [ ] 所有质量报告与图表文件一起保存

### 文档和版本控制
- [ ] 保存源文件（.tex, .py）以供将来修改
- [ ] 将质量报告存档在`quality_reports/`目录
- [ ] 记录配置参数（颜色、间距、尺寸）
- [ ] Git提交包含源文件、输出和质量报告
- [ ] README或注释说明如何重新生成图表

### 最终集成检查
- [ ] 图表在编译文稿中正确显示
- [ ] 交叉引用正确（`\ref{}`指向正确图表）
- [ ] 图表编号与文本引用一致
- [ ] 说明出现在图表相对于的正确页面上
- [ ] 与图表相关的无编译警告或错误

## 环境设置

```bash
# 必需的
export OPENROUTER_API_KEY='your_api_key_here'

# 获取密钥：https://openrouter.ai/keys
```

## 入门指南

**最简单的用法：**
```bash
python scripts/generate_schematic.py "你的图表描述" -o output.png
```

---

使用这项技能创建清晰、无障碍、符合出版标准的图表，以有效传达复杂的科学概念。AI驱动的迭代细化工作流程确保图表符合专业标准。
