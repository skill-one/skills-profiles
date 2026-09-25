Pydantic 是一种声明批处理作业真实来源的绝佳方式，尤其是在机器学习领域。您可以声明如下内容：

```python
from pydantic import BaseModel, Field

class ModelParams(BaseModel):
    sample_size: int = Field(
        default=1024 * 4, description="每个训练周期的样本数量。"
    )
    learning_rate: float = Field(default=0.01, description="优化器的学习率。")
```

您也可以通过两种方法填充这些模型参数，可以想象一个用户界面中的表单。

```python
el = mo.md("""
{sample_size} 
{learning_rate}
""").batch(
    sample_size=mo.ui.slider(1024, 1024 * 10, value=1024 * 4, step=1024, label="Sample size"),
    learning_rate=mo.ui.slider(0.001, 0.1, value=0.01, step=0.001, label="Learning rate"),
).form()
el
```

但您也可以使用 marimo 的命令行界面。

```python
if mo.app_meta().mode == "script":
    if "help" in mo.cli_args() or len(cli_args) == 0:
        print("用法：uv run git_archaeology.py --repo <url> [--samples <n>]")
        print()
        for name, field in ModelParams.model_fields.items():
            default = f" (默认值：{field.default})" if field.default is not None else " (必需)"
            print(f"  --{name:12s} {field.description}{default}")
        exit()
    model_params = ModelParams(
        **{k.replace("-", "_"): v for k, v in mo.cli_args().items()}
    )
else: 
    model_params = ModelParams(**el.value)
```

用户现在可以通过以下命令行运行此操作：

```bash
uv run notebook.py --sample-size 4096 --learning-rate 0.005
```

这是两全其美的方法，您可以使用 UI 进行测试和迭代，然后使用命令行运行批处理作业。另一个好处是您可以使用设置来快速运行笔记本，以查看笔记本中是否存在任何错误。

用户希望能够使用这种模式运行笔记本，因此请确保询问用户他们希望通过命令行使哪些参数可配置，然后继续对笔记本进行更改。在做出更改之前，请确保与用户验证这些更改。

## 权重和偏差

用户可能对添加权重和偏差的支持感兴趣。请确认是否确实如此（是/否）。如果是，请确保记录这些 ModelParams。您还希望确保 `wandb_project` 和 `wandb_run_name` 是 ModelParams 的一部分，如果用户希望走这条路。

如果用户希望开始机器学习训练作业，请确保使用 [这个起点](references/starting-point.py)。请确保在此笔记本中保持列的完整性！

## 环境变量

您可能需要读取作业的环境变量。如果存在 .env 文件，请使用 python-dotenv 读取它，但还要添加一个 `EnvConfig`，以便用户可以在 UI 中手动添加键。

```python
from wigglystuff import EnvConfig

# 带验证器
config = EnvConfig({
    "OPENAI_API_KEY": lambda k: openai.Client(api_key=k).models.list(),
    "WANDB_API_KEY": lambda k: wandb.login(key=k, verify=True)
})

# 阻塞直到有效，在需要键的单元格中很有用
config.require_valid()

# 访问值
config["OPENAI_API_KEY"]
config.get("OPENAI_API_KEY", "some default")
```

请确保在笔记本顶部添加此 `EnvConfig`。

## 列

较大的 marimo 笔记本通常使用列功能以便于导航。如果是这种情况，您必须保持这些列的完整性！

```python
@app.cell(column=0, hide_code=True)
def _(mo):
    mo.md(r"""demo""")
```

## 计算平台

当作业准备好进行一些严肃的计算时，重要的是要记住良好的实践。考虑数据集的批处理大小，并确保有足够的日志记录，以便用户可以识别问题。

## 网格搜索

当用户希望运行超参数扫描时，请将他们指向 [这个网格启动器](references/grid.py)。它开箱即用地与 `references/starting-point.py` 中的笔记本一起工作：它从与笔记本的 `ModelParams` 字段匹配的搜索空间中采样随机组合，并将每个组合作为单独的作业启动。

默认情况下，脚本执行干运行（`uv run grid.py`），以便用户在花费计算资源之前检查组合。传递 `--launch` 以实际提交作业。`--count` 和 `--seed` 标志控制采样多少组合以及随机数生成器的种子。

参考使用 Hugging Face Jobs 作为计算提供者，但这只是一个选项。用户可以将其替换为 Modal、RunPod 或任何其他可以运行 uv 脚本提供者。
