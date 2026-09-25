# 技能：Mermaid转GIF

将Mermaid图表转换为带有丰富动画效果的动态GIF。支持`.mmd`文件和从`.md`文件中提取` ```mermaid `代码块。

> **前提条件**：FFmpeg、Python 3.8+、Playwright (`pip install playwright && playwright install chromium`)

---

## 使用场景

- 用户希望将Mermaid图表转换为动态GIF
- 用户拥有`.mmd`文件或包含mermaid代码块的`.md`文件
- 用户需要为演示文稿、文档或社交媒体制作动画视觉效果
- 用户希望批量转换文档中的所有mermaid代码块

---

## 智能样式选择

**重要提示**：从`.md`文件转换mermaid代码块时，请根据周围markdown上下文为每个图表选择最合适的动画样式。**不要**对所有代码块盲目应用相同样式。

### 决策指南

1. **阅读每个mermaid代码块周围的markdown文本** — 理解图表所说明的内容
2. **根据语义意义匹配样式**：

| 上下文线索 | 推荐样式 | 理由 |
|--------------|------------------|-----------|
| 数据管道、ETL流程、请求/响应路径 | `pulse-flow` | 虚线流动表示数据传输 |
| 架构层、组织结构图、层级关系 | `progressive` | 元素逐层激活 |
| 步骤式流程、教程演示 | `highlight-walk` | 聚光灯引导读者逐步理解 |
| 系统概述、标题图表、简单参考 | `wave` | 亮度涟漪增添活力而不分散注意力 |
| 带消息流的时序图 | `progressive` | 消息按对话顺序逐一激活 |
| 类/ER图（参考/静态） | `progressive` 或 `wave` | 结构逐亮或产生微妙涟漪 |

3. **考虑特殊处理**：
   - 如果周围文本说明“数据从A流向B”，即使对于简单流程图也使用`pulse-flow`
   - 如果文本描述“三层”或“两层”，使用`progressive`实现逐层激活
   - 如果图表是装饰性或辅助性，使用`wave`保持简洁
   - 对于非常大的复杂图表，优先使用`wave`或较短的`--duration`以保持GIF大小合理

4. **逐块样式覆盖**：在批量处理`.md`文件时，可能需要多次运行脚本使用不同样式来提取特定代码块。或者使用合理默认值处理整个文件，然后重新处理需要不同处理的单个代码块。

### 示例：智能处理

```markdown
## 数据摄取管道        ← 上下文：“管道” → pulse-flow
[mermaid代码块：包含ETL阶段的graph LR]

## 系统架构            ← 上下文：“架构” → progressive
[mermaid代码块：包含层级的graph TD]

## 快速参考                ← 上下文：“参考” → wave
[mermaid代码块：简单图表]
```

---

## 默认工作流程

### 单个`.mmd`文件

```bash
python <skill-root>/scripts/mermaid_to_gif.py diagram.mmd
```

### 包含mermaid代码块的markdown文件

```bash
python <skill-root>/scripts/mermaid_to_gif.py document.md -o ./images/
```

这会提取所有` ```mermaid `代码块，并为每个块生成一个GIF。

### 多个文件

```bash
python <skill-root>/scripts/mermaid_to_gif.py *.mmd -o ./gifs/
python <skill-root>/scripts/mermaid_to_gif.py doc1.md doc2.md -o ./gifs/
```

### 替换markdown中的mermaid代码块

生成GIF后，用图像引用替换原始` ```mermaid `代码块：

```markdown
![流程图](images/document-1.gif)
```

根据图表内容使用描述性alt文本。图像路径应相对于markdown文件。

---

## 动画样式

所有样式都保证图表**从第一帧就完全可见** — 没有元素会隐藏或从零淡入。每种样式都在用户始终能看到完整图表结构的同时添加动画效果。

| 样式 | 效果 | 适用场景 |
|-------|--------|----------|
| `progressive` (默认) | 所有元素初始为25%不透明度，按顺序激活至全亮；边框使用stroke动画绘制 | 流程图、架构、层级 |
| `highlight-walk` | 所有元素初始为15%不透明度；一个带有蓝色光晕的聚光灯按顺序移动，照亮已访问元素 | 步骤式流程、教程 |
| `pulse-flow` | 所有元素全亮；边框变为流动虚线（统一虚线长度和速度） | 数据流、管道、请求路径 |
| `wave` | 所有元素全亮；亮度脉冲+蓝色光晕按顺序扫过元素 | 简单图表、概述、参考 |

### 动画细节

- **progressive**：元素初始为25%不透明度（图表结构始终可见）。节点、边框和标签按交错顺序激活（节点→边框→节点→边框），遵循流动方向。边框使用stroke-dashoffset视觉绘制。激活速度快（每个元素占总时长的8%）。
- **highlight-walk**：所有元素初始为15%不透明度。一个带有蓝色光晕的聚光灯按顺序移动，访问过的元素保持90%不透明度。在聚光灯到达每个元素前，整个图表作为“幽灵”可见。
- **pulse-flow**：所有元素全不透明度。边框路径获得统一虚线模式（10px虚线+6px间隙），以固定速度（200px/周期）流动，确保所有边框同步动画，无论长度如何。
- **wave**：所有元素全不透明度。亮度脉冲（1.0→1.4→1.0）+蓝色光晕按顺序扫过元素。位置不变 — 纯粹的视觉涟漪效果。

---

## 常用选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `-o`, `--output-dir` | 与输入相同 | 生成的GIF输出目录 |
| `-s`, `--style` | `progressive` | 动画样式（见上表） |
| `--fps` | `10` | 每秒帧数 |
| `--duration` | `4.0` | 动画持续时间（秒） |
| `--hold` | `1.0` | 循环前最后一帧停留时间（秒） |
| `--theme` | `default` | Mermaid主题：default、dark、forest、neutral |
| `--bg` | `#ffffff` | 背景颜色（十六进制） |
| `--padding` | `40` | 图表周围像素间距 |
| `--scale` | `2` | 渲染缩放因子（2 = 高清质量） |
| `--custom-css` | — | 自定义CSS文件路径 |
| `--no-loop` | — | GIF播放一次而非循环 |

---

## 示例

```bash
# 暗色主题与更快动画
python <skill-root>/scripts/mermaid_to_gif.py arch.mmd --theme dark --bg "#1a1a2e" --duration 3

# 高FPS实现更流畅动画
python <skill-root>/scripts/mermaid_to_gif.py flow.mmd --fps 15 --duration 5

# 批量转换文档中的所有mermaid代码块
python <skill-root>/scripts/mermaid_to_gif.py README.md -o ./images/

# 自定义CSS实现特殊效果
python <skill-root>/scripts/mermaid_to_gif.py diagram.mmd --custom-css my-style.css

# 不循环，适合单次播放
python <skill-root>/scripts/mermaid_to_gif.py intro.mmd --no-loop --duration 6

# 降低分辨率以减小文件大小
python <skill-root>/scripts/mermaid_to_gif.py diagram.mmd --scale 1
```

---

## 自定义CSS

创建CSS文件以自定义动画期间图表的外观：

```css
/* 圆角节点带阴影 */
.node rect {
    rx: 10;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
}

/* 边框线加粗 */
.edgePath path {
    stroke-width: 2.5;
}

/* 序列图中的角色自定义背景 */
.actor {
    fill: #e8f4f8;
}
```

通过`--custom-css`传递：

```bash
python <skill-root>/scripts/mermaid_to_gif.py diagram.mmd --custom-css my-style.css
```

---

## 工作原理

1. **解析输入** — 从`.mmd`或`.md`文件中提取Mermaid代码
2. **生成HTML** — 嵌入Mermaid.js（CDN）+动画JS/CSS到自包含HTML文件
3. **渲染** — Mermaid.js通过Playwright（带2x设备缩放以实现高清质量）在无头Chromium中渲染图表为SVG
4. **缩放** — 小SVG自动缩放至最小700px CSS宽度以提高可读性
5. **动画** — JS动画引擎暴露`setProgress(t)`实现逐帧控制（t: 0→1）。元素按位置排序（尊重左到右/上到下方向），按节点-边框交错顺序动画
6. **捕获** — Playwright每帧拍摄截图
7. **合成** — FFmpeg两通道调色板编码（palettegen → paletteuse使用Floyd-Steinberg抖动）

---

## 重要说明

- **需要网络**：Mermaid.js在渲染时从CDN加载
- **支持的图表类型**：flowchart、sequence、class、state、ER、gitgraph、mindmap、pie、gantt等
- **无隐藏元素**：所有4种样式从第一帧就保持图表可见 — 无需等待元素出现
- **回退行为**：对于未识别的图表类型或未检测到可动画元素时，回退为整个图表的不透明度渐显
- **分辨率**：默认scale=2生成高清图像（约1400-1600px宽）。使用`--scale 1`减小文件
- **GIF大小**：对于非常大的输出，降低FPS至8、缩短duration、使用`--scale 1`或`wave`样式
