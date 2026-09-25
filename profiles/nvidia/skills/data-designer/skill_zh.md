# 开始前须知

不要先探索工作区。工作流的"学习"步骤会为你提供所需的一切。

# 目标

使用数据设计器库构建一个符合以下描述的合成数据集：

$ARGUMENTS

# 工作流

如果用户暗示不想回答问题（例如，他们说“直接给出意见”、“你决定”、“做合理的假设”、“直接构建”、“给我惊喜”等类似的话），请使用**自动驾驶**模式。否则，使用**交互**模式（默认）。

仅读取与所选模式匹配的工作流文件，然后遵循它：

- **交互** → 读取 `workflows/interactive.md`
- **自动驾驶** → 读取 `workflows/autopilot.md`

# 规则

- 默认保留所有输出列。仅以下情况例外可以删除列：（1）用户明确要求删除，或（2）它是仅用于派生其他列的辅助列（例如，用于提取姓名、城市等的采样人员对象）。如有疑问，请保留该列。
- 不要建议或询问种子数据集。仅在用户明确提供种子数据或要求从现有记录构建时使用。使用种子时，请读取 `references/seed-datasets.md`。
- 当数据集需要人员数据（姓名、人口统计、地址）时，请读取 `references/person-sampling.md`。
- 如果已存在与数据集描述匹配的数据集脚本，请询问用户是编辑它还是创建一个新的。

# 使用技巧和常见陷阱

- **采样器和验证列都需要类型和参数**。例如，`sampler_type="category"` 与 `params=dd.CategorySamplerParams(...)`。
- **Jinja2模板** 在 `prompt`、`system_prompt` 和 `expr` 字段中：使用 `{{ column_name }}` 引用列，使用 `{{ column_name.field }}` 引用嵌套字段。
- **`SamplerColumnConfig`**：接受 `params`，而不是 `sampler_params`。
- **LLM裁判分数访问**：`LLMJudgeColumnConfig` 生成一个嵌套字典，其中每个分数名称映射到 `{reasoning: str, score: int}`。要获取数值分数，请使用 `.score` 属性。例如，对于名为 `quality` 的裁判列和名为 `correctness` 的分数，使用 `{{ quality.correctness.score }}`。使用 `{{ quality.correctness }}` 返回的是完整字典，而不是数值分数。

# 故障排除

- **找不到 `data-designer` 命令行工具**：告诉用户 `data-designer` 在此环境中未安装（需要 Python >= 3.10）。询问他们是否希望由我创建虚拟环境并安装，或是否希望自行安装。未经用户许可，不要安装任何内容。
- **预览时出现网络错误**：沙盒环境可能正在阻止出站请求。询问用户是否允许禁用沙盒重试该命令。只有在沙盒外重试也失败的情况下，才告诉用户自行运行该命令。

# 输出模板

将包含 `load_config_builder()` 函数（返回 `DataDesignerConfigBuilder`）的 Python 文件写入当前目录。文件名应具有描述性（例如，`customer_reviews.py`）。使用 PEP 723 内联元数据指定依赖项。

```python
# /// script
# dependencies = [
#   "data-designer", # 始终需要
#   "pydantic", # 仅当此脚本从 pydantic 导入时需要
#   # 在此处添加其他依赖项
# ]
# ///
import data_designer.config as dd
from pydantic import BaseModel, Field


# 当输出需要符合特定模式时，使用 Pydantic 模型
class MyStructuredOutput(BaseModel):
    field_one: str = Field(description="...")
    field_two: int = Field(description="...")


# 当内置列类型不足以满足需求时，使用自定义生成器
@dd.custom_column_generator(
    required_columns=["col_a"],
    side_effect_columns=["extra_col"],
)
def generator_function(row: dict) -> dict:
    # 在此处添加依赖于 "col_a" 的自定义逻辑，并就地更新 row
    row["name_in_custom_column_config"] = "custom value"
    row["extra_col"] = "extra value"
    return row


def load_config_builder() -> dd.DataDesignerConfigBuilder:
    config_builder = dd.DataDesignerConfigBuilder()

    # 种子数据集（仅当用户明确提及种子数据集路径时）
    # config_builder.with_seed_dataset(dd.LocalFileSeedSource(path="path/to/seed.parquet"))

    # config_builder.add_column(...)
    # config_builder.add_processor(...)

    return config_builder
```

仅当任务需要时，才包含 Pydantic 模型、自定义生成器、种子数据集和额外依赖项。
