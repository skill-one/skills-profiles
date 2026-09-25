# 开始前须知

不要先探索工作区。工作流的 Learn 步骤会为你提供所需的一切。

# 目标

使用 Data Designer 库构建一个符合以下描述的合成数据集：

$ARGUMENTS

# 工作流

如果用户暗示他们不想回答问题（例如，他们说“有主见”、“你决定”、“做出合理假设”、“直接构建”、“给我惊喜”等），请使用 **Autopilot** 模式。否则，使用 **Interactive** 模式（默认）。

仅读取与所选模式匹配的工作流文件，然后遵循它：

- **Interactive** → 读取 `workflows/interactive.md`
- **Autopilot** → 读取 `workflows/autopilot.md`

# 规则

- 默认保留所有输出列。仅以下情况例外： (1) 用户明确要求删除，或 (2) 它是一个仅用于派生其他列的辅助列（例如，用于提取姓名、城市等的采样人员对象）。如有疑问，保留该列。
- 不要建议或询问种子数据集。仅在用户明确提供种子数据或要求从现有记录构建时使用。使用种子时，读取 `references/seed-datasets.md`。
- 当数据集需要人员数据（姓名、人口统计、地址）时，读取 `references/person-sampling.md`。
- 如果已存在与数据集描述匹配的数据集脚本，请询问用户是编辑它还是创建一个新的。
- 对于特定于此 NeMo 平台插件的命令和上下文（例如，从 IGW 提供商获取模型配置或在脚本中 `ModelConfig`、安装或发布 Nemotron Personas 本地化、平台侧资源指针），读取 `references/nemo-platform-plugin-additions.md`。

# 使用技巧和常见陷阱

- **采样器和验证列都需要类型和参数。** 例如，`sampler_type="category"` 与 `params=dd.CategorySamplerParams(...)`。
- **`prompt`、`system_prompt` 和 `expr` 字段的 Jinja2 模板**：使用 `{{ column_name }}` 引用列，使用 `{{ column_name.field }}` 引用嵌套字段。
- **`SamplerColumnConfig`**：接受 `params`，而不是 `sampler_params`。
- **LLM 评分访问**：`LLMJudgeColumnConfig` 生成一个嵌套字典，其中每个评分名称映射到 `{reasoning: str, score: int}`。要获取数值评分，请使用 `.score` 属性。例如，对于名为 `quality` 的评分列和名为 `correctness` 的评分，使用 `{{ quality.correctness.score }}`。使用 `{{ quality.correctness }}` 返回完整字典，而不是数值评分。

# 故障排除

- **找不到 `nemo data-designer` CLI**：告诉用户 `nemo data-designer` 未在此环境中安装（需要 Python >= 3.11）。询问他们是否希望您创建虚拟环境并安装它，或他们是否希望自行操作。未经用户许可，不要安装任何内容。
- **预览期间出现网络错误**：沙盒环境可能阻止了出站请求。询问用户是否允许禁用沙盒重试命令。只有在沙盒外重试也失败的情况下，才告诉用户自行运行命令。

# 输出模板

将 Python 文件写入当前目录，该文件包含一个返回 `DataDesignerConfigBuilder` 的 `load_config_builder()` 函数。将文件描述性地命名（例如，`customer_reviews.py`）。使用 PEP 723 内联元数据指定依赖项。

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
    config_builder = dd.DataDesignerConfigBuilder(
        # 在此处以编程方式声明模型配置是可移植的路径：
        # 它适用于本地 `run` 和集群 `submit`，而本地 YAML 注册替代方案仅适用于 `run`。下面的提供者是 `nemo setup` 过程中创建的常见默认值——使用 `nemo inference providers list` 确认它（或发现其他提供者）。有关本地 YAML 替代方案，请参阅 references/nemo-platform-plugin-additions.md。
        model_configs=[
            dd.ModelConfig(
                alias="text",
                model="...",
                provider="default/nvidia-build",
                inference_parameters=dd.ChatCompletionInferenceParams(),
            ),
        ],
    )

    # 种子数据集（仅当用户明确提及种子数据集路径时）
    # config_builder.with_seed_dataset(dd.LocalFileSeedSource(path="path/to/seed.parquet"))

    # config_builder.add_column(...)
    # config_builder.add_processor(...)

    return config_builder
```

仅当任务需要时，才包含 Pydantic 模型、自定义生成器、种子数据集和额外依赖项。当数据集使用 LLM 列时，优先包含 `model_configs`——在脚本中声明配置可以在本地 `run` 和集群 `submit` 之间保持可移植性，而本地 YAML 注册替代方案仅适用于 `run`。
