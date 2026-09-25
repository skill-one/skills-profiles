# Earth2Studio 可发现性技能

## 目的

帮助用户为其天气/气候任务识别合适的 Earth2Studio 模型、数据源和示例。使用场景包括：比较模型按 GPU/VRAM 要求、选择预报类别（临近预报、中程预报、季节预报）、通过词汇表查找兼容的数据源，或定位用于降尺度、集合生成或数据同化的画廊示例。

## 前置条件

- 互联网访问权限，用于从 nvidia.github.io 获取实时文档页面
- 熟悉 Earth2Studio 徽章系统（类别、区域、VRAM、发布版本）

您正在帮助用户为其用例找到合适的 Earth2Studio 组件。您的任务是理解他们想做什么，然后引导他们使用符合需求的模型、数据源和示例——这些信息需经过实时文档验证。

## 核心原则：从实时文档发现，而非死记硬背

Earth2Studio 每次发布都会添加模型、数据源和示例。模型类别会获得新的徽章，新的数据源会出现，示例会被重新组织。任何静态列表在这个技能中都会过时。

**规则：**
1. 推荐组件前，务必先获取相关的实时文档页面。
2. 使用文档中的徽章元数据（区域、类别、VRAM、发布版本）来筛选候选对象。
3. 使用词汇表系统验证数据源 ↔ 模型兼容性（见第 4 步）。
4. 引用文档 URL，以便用户进一步探索。

## 实时文档参考

根据需要获取这些页面（一次不需要全部获取——只需用户问题所需的即可）：

| 类别         | URL                                       |
|------------|------------------------------------------|
| 预报模型     | https://nvidia.github.io/earth2studio/modules/models_px.html |
| 诊断模型     | https://nvidia.github.io/earth2studio/modules/models_dx.html |
| 数据同化     | https://nvidia.github.io/earth2studio/modules/models_da.html |
| 数据源（分析） | https://nvidia.github.io/earth2studio/modules/datasources_analysis.html |
| 数据源（预报） | https://nvidia.github.io/earth2studio/modules/datasources_forecast.html |
| 数据源（数据框） | https://nvidia.github.io/earth2studio/modules/datasources_dataframe.html |
| 示例画廊     | https://nvidia.github.io/earth2studio/examples/index.html |
| 词汇表源     | https://github.com/NVIDIA/earth2studio/tree/main/earth2studio/lexicon |

## 交互协议

### 第 1 步。理解用户的问题

从用户的陈述中提取信息（如有必要，可进行追问，最多 3 个问题）：

- **任务类型** — 中程预报、临近预报、降尺度/超分辨率、季节/次季节、数据同化、气候投影、集合生成、衍生诊断
- **区域** — 全球、北美、欧洲、亚洲、特定国家/地区
- **时间尺度** — 小时内（临近预报）、日内（中程预报）、周/月（季节预报）、气候
- **感兴趣变量** — 温度、降水、风、气压、辐射、特定层级等
- **硬件限制** — GPU 类型、可用 VRAM（40GB、48GB、80GB、96GB）
- **确定性 vs. 集合** — 单个预报或概率性

好的追问措辞：*"您是在寻找单个最佳估计预报还是具有不确定性的集合预报？"* —— 而不是 *"您的用例是什么？"*

### 第 2 步。获取相关模型文档

根据用户的任务类型，获取相应的模型页面：

- 预报 → 预报模型（px）
- 后处理/降尺度/衍生变量 → 诊断模型（dx）
- 观测集成 → 数据同化（da）
- 通常一个工作流会链式使用 px → dx，因此需要检查两个页面

从文档页面中，为每个候选模型提取：
- **类别徽章** — NWC、DS、MR、S2S、DA、CM
- **区域徽章** — 全球、NA、EU、AS 等
- **推荐 VRAM 徽章** — 最小 GPU 内存
- **发布年份** — 同一类别中，较新的模型通常会取代较旧的模型

筛选符合用户任务类型、区域和硬件的模型。展示带有徽章元数据的简短列表（而不是完整目录）。

### 第 3 步。获取相关数据源文档

根据用户的数据需求，获取相应的数据源页面：

- 历史再分析 → 分析数据源
- 实时或业务运行 → 预报数据源
- 观测/站点数据 → 数据框数据源

注意哪些数据源覆盖了用户的区域和变量。

### 第 4 步。通过词汇表验证兼容性

这是关键的技术步骤。Earth2Studio 模型通过 `input_coords()` 声明其所需的输入变量。数据源通过其词汇表 VOCAB 暴露可用变量。如果数据源词汇表 VOCAB 的键包含模型 `input_coords` 中的所有变量（即“变量”维度），则它们是兼容的。

验证方法：
1. 检查模型的文档页面或源代码以获取其 `input_coords` —— 具体是变量列表
2. 检查数据源的词汇表文件（位于 `earth2studio/lexicon/<source>.py`）以获取其 VOCAB 键
3. 确认数据源 VOCAB 覆盖模型所需的所有变量

如果直接检查源代码（例如用户有本地克隆），词汇表文件位于：
```
earth2studio/lexicon/gfs.py
earth2studio/lexicon/hrrr.py
earth2studio/lexicon/cds.py
earth2studio/lexicon/arco.py
earth2studio/lexicon/wb2.py
...（每个数据源一个文件）
```

每个文件定义了一个 `VOCAB: dict[str, str | tuple]`，将 Earth2Studio 变量名映射到源特定标识符。

表面兼容性结果清晰：*"GraphCastOperational 需要 [变量列表] — GFS 和 ERA5（通过 ARCO/CDS）都提供这些，但 HRRR 没有覆盖气压层级以上 X。"*

### 第 5 步。建议示例

获取示例画廊并识别展示用户工作流模式的示例。示例按类别组织：

- `01_getting_started` — 基本确定性、诊断、集合工作流
- `02_medium_range` — 集合扩展、扰动、气旋跟踪
- `03_downscaling` — CorrDiff、CBottle、集合降尺度
- `04_nowcasting` — StormCast、StormScope
- `05_data_assimilation` — StormCast SDA、HealDA
- `06_seasonal` — DLESyM、统计方法
- `07_misc` — 分布式推理、IO、自定义数据、生成
- `08_extend` — 构建自定义模型、诊断、数据源

将用户指向最相关的 1-3 个示例作为起点。解释每个示例展示了什么以及它如何与用户的问题相关。

### 第 6 步。返回推荐

输出结构（省略空部分）：

```
## 您的用例
[1-2 句话重述用户想做什么]

## 推荐模型
| 模型 | 类别 | 区域 | VRAM | 原因 |
|------|------|------|------|------|
[每行带推理的简短列表]

## 兼容数据源
| 数据源 | 覆盖范围 | 兼容 |
|--------|----------|------|
[通过词汇表验证]

## 相关示例
- [示例名称](链接) — 展示了什么

## 下一步
[需要安装什么，下一步阅读什么]
```

将推荐限制在 2-4 个模型以内。如果存在多个选项，解释权衡（精度 vs. 速度、确定性 vs. 集合、VRAM 等），而不是列出所有内容。

## 限制

- 推荐仅与实时文档的当前状态相关；未发布的模型不可发现。
- 新添加模型的徽章元数据可能不完整。
- 词汇表兼容性检查需要源代码访问才能获得完全准确性；仅文档检查是近似的。

## 故障排除

| 错误       | 原因               | 解决方案             |
|----------|------------------|------------------|
| 模型页面返回 404 | 发布后 URL 变更了 | 检查 https://nvidia.github.io/earth2studio/ 更新后的导航 |
| 词汇表文件未找到 | 数据源是新的或重命名了 | 在 `earth2studio/lexicon/` 目录中搜索当前文件名 |
| 模型缺少徽章   | 模型文档尚未更新   | 回退到模型的源代码 `__init__` 或 README 以获取规格 |

## 责任范围和超出范围

**负责：** 组件发现、模型/数据源兼容性检查、基于徽章的筛选、示例推荐、硬件适配评估。

**不负责：** 安装（使用 earth2studio-install 技能）、编写推理代码、模型训练、自定义模型开发、运行时调试、PhysicsNeMo 模型发现。
