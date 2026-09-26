使用 Reward Kit 帮助用户编写任务验证器。Reward Kit 是一个轻量级的 Python 包，它将一组标准文件目录转换为奖励分数。每个标准都是一个 Python 函数调用或一个 TOML 判定文件；文件夹将成为独立的奖励。

## 在 Harbor 任务中设置

将标准与 `test.sh` 放在同一任务目录的 `tests/` 目录中：

```
tests/
├── test.sh
├── checks.py         # 程序化标准
└── judge.toml        # 可选的 LLM/代理判定
```

`tests/test.sh`:
```bash
#!/bin/bash
uvx --from 'harbor-rewardkit==0.2.*' rewardkit /tests
```

这将在 `/tests/` 中运行所有标准，并与工作区 `/app` 进行比较，然后写入 `/logs/verifier/reward.json`。默认值符合 Harbor 的约定——无需额外配置。

如果判定标准需要 API 密钥，请通过 `task.toml` 传递它们：
```toml
[verifier.env]
ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY}"
```

询问 Reward Kit 是否应在代理的共享环境中运行，还是在单独的验证器环境中运行。当判定提示、评分依赖项、API 密钥或干净房间检查不应提供给代理时，请优先选择单独的验证器环境：

```toml
[environment]
network_mode = "no-network"   # 代理环境基线——在代理.run() 期间离线

[verifier]
environment_mode = "separate"

[verifier.environment]
network_mode = "public"     # 验证器环境基线——LLM 判定 API 调用
docker_image = "python:3.12-slim"
```

在共享模式下，验证器在代理容器中运行并继承 `[environment].network_mode`。仅在 `verify()` 需要不同于代理阶段的网络访问时（这是一个阶段覆盖，而不是基线）才放置 `[verifier].network_mode`。如果代理和验证器需要不同的基线且无需运行时切换，请使用 `environment_mode = "separate"` 并设置 `[verifier.environment].network_mode`。

调用外部 API 的判定标准需要在验证器环境中有一个 `public` 基线或允许列表。仅读取本地文件的程序化检查可以使用 `no-network`。

在单独模式下，`tests/` 是验证器镜像构建上下文，必须在运行时提供 `/tests/test.sh`；Harbor 不会将 `tests/` 上传到正在运行的验证器容器中。

## 程序化标准

从 `tests/` 中的任何 `.py` 文件调用内置函数：

```python
import rewardkit as rk

rk.file_exists("output.txt")
rk.file_contains("output.txt", "hello")
rk.command_succeeds("python main.py", weight=2.0)
rk.json_key_equals("result.json", "status", "ok")
```

所有标准都接受 `weight`（默认 `1.0`）和 `isolated`（默认 `False`，在 overlayfs 中运行，因此副作用不会泄漏）。

### 可用的内置函数

- **文件**：`file_exists`，`file_not_exists`，`file_contains`，`file_contains_regex`，`file_matches`，`files_equal`，`diff_ratio`
- **命令**：`command_succeeds`，`command_output_contains`，`command_output_matches`，`command_output_matches_regex`（默认超时 30 秒，可选 `cwd`）
- **数据**：`json_key_equals`，`json_path_equals`，`csv_cell_equals`，`xlsx_cell_equals`（需要 `[office]` 附加），`sqlite_query_equals`
- **HTTP**：`http_status_equals`，`http_response_contains`
- **图像**：`image_similarity`，`image_size_equals`（需要 `[image]` 附加）
- **轨迹**：`trajectory_tool_used`，`trajectory_tool_not_used`，`trajectory_turn_count`

对于附加功能，请使用 `uv tool install harbor-rewardkit[all]` 进行安装。

## 自定义标准

使用 `@criterion` 装饰器。第一个参数始终是 `workspace: Path`。返回 `bool` 或 `float`：

```python
from pathlib import Path
from rewardkit import criterion

@criterion
def has_valid_output(workspace: Path) -> bool:
    return (workspace / "output.txt").read_text().strip() != ""
```

零参数标准自动注册。具有附加参数的标准必须通过 `rk` 调用：

```python
@criterion(description="输出至少有 {n} 行")
def has_n_lines(workspace: Path, n: int) -> bool:
    return len((workspace / "output.txt").read_text().splitlines()) >= n

rk.has_n_lines(10, weight=2.0)
rk.has_n_lines(50, weight=1.0)
```

对于跨奖励子目录共享的标准，请在根级文件中定义 `shared=True` 并从子目录中调用。

## 判定标准（LLM 或代理作为判定者）

对于主观检查（质量、可读性、边缘情况），创建一个 TOML 文件：

```toml
[judge]
judge = "anthropic/claude-sonnet-5"   # LiteLLM 模型字符串
files = ["/app/main.py"]

[[criterion]]
description = "代码是否正确？"
type = "binary"

[[criterion]]
description = "代码的可读性如何？"
type = "likert"
points = 5
weight = 2.0
```

标准类型：
- `binary` — 是/否 → 1.0 或 0.0
- `likert` — 1..points，归一化到 [0, 1]
- `numeric` — min..max，归一化到 [0, 1]
- `rubric` — 2 到 10 描述的 `levels` 形成一个从最差到最好的量表；位置设置分数

### 代理判定

代理判定通过 CLI 执行，并可以探索文件系统：

```toml
[judge]
judge = "claude-code"
model = "anthropic/claude-sonnet-5"
isolated = true

[[criterion]]
description = "解决方案是否处理了边缘情况？"
type = "binary"
```

比 LLM 判定慢且昂贵，但它们可以运行命令并检查文件。

### JEV 判定

JEV 是 TypeSafe 的一种新型语言模型。它对每个标准用概率或评分回答，并返回不提供推理，因此它快速且便宜。它需要 `jev` 附加功能（`harbor-rewardkit[jev]`）和 `TYPESAFE_API_KEY`。

```toml
[judge]
judge = "jev"
files = ["/app/answer.md"]

[[criterion]]
description = "答案是否解决了请求的任务？"

[[criterion]]
description = "答案的完整性如何？"
type = "rubric"
levels = ["遗漏信息", "覆盖部分", "覆盖全部"]
```

二进制标准在概率 0.5 或更高时通过。仅支持 `binary` 和 `rubric` 标准和文本文件；`atif-trajectory` 和 `prompt_template` 不支持。
任务镜像需要 CA 证书（Debian 和 Ubuntu 上的 `ca-certificates`），因为 TypeSafe SDK 对 TLS 进行验证的系统信任存储。

### 有用的 `[judge]` 选项

`timeout`（默认 300），`reasoning_effort`（`low`|`medium`|`high`），`reference`（参考解决方案的路径），`atif-trajectory`（评估代理的轨迹），`weight`，`prompt_template`（带有 `{criteria}` 占位符的自定义提示）。

### 分数聚合（在一个判定 TOML 内）

```toml
[scoring]
aggregation = "all-pass"   # weighted-mean | weighted-sum | all-pass | any-pass | threshold | required-pass
threshold = 0.7             # 仅用于 threshold
```

这仅影响此文件自己的标准如何组合。要跨维度聚合，请参阅 [维度聚合](#aggregating-dimensions)。

### 程序化文件的分数配置

注册标准的每个 `.py` 文件都是一个等权重的分数组件，以文件名干命名。仅提供导入或共享标准工厂而不注册检查的文件会被忽略。要更改文件内标准的组合方式，请在同一目录的 `reward.toml` 中使用 `[scoring.<stem>]`：

```toml
# tests/structure/reward.toml
[scoring.files_exist]       # 配置 files_exist.py
aggregation = "all-pass"

[scoring.behavior]          # 配置 behavior.py
aggregation = "threshold"
threshold = 0.75
```

每个条目与判定 TOML 具有相同的聚合值。未知键和未解析为具有标准的 Python 文件的干会引发错误。

目录可以递归嵌套。非根目录可以聚合其本地 Python 文件、本地判定和直接子目录，使用一个未命名的 `[[reward]]` 表：

```toml
# tests/correctness/reward.toml
[[reward]]
aggregation = "weighted-mean"
weights = { files = 2.0, behavior = 1.0 }
```

成员资格是隐式的。子目录的权重为 1.0，除非被覆盖；使用文件名干表示本地 Python 文件和判定 TOML，使用目录名表示子组。没有 `[[reward]]`，目录默认为加权平均。

## 多奖励任务

将标准放在子目录中——每个标准将成为一个独立的奖励：

```
tests/
├── test.sh
├── correctness/
│   └── check.py
├── structure/
│   └── files_exist.py
└── quality/
    └── quality.toml
```

判定 TOML 文件也可以直接放在测试根目录与奖励子目录旁边。每个都以其文件名干命名的顶级奖励命名，并且可以被根聚合引用。

测试根目录中的具有标准的 Python 文件也是以其干命名的顶级维度。根支持文件如果未注册标准会被忽略。

生成：
```json
{ "correctness": 0.75, "structure": 1.0, "quality": 0.6 }
```

### 维度聚合

要在每个维度键上添加聚合分数，请添加一个或多个 `[[reward]]` 表的根级 `tests/reward.toml`。每个表向 `reward.json` 添加一个键，以与 `[scoring]` 相同的模式聚合维度：

```toml
# tests/reward.toml
[[reward]]
name = "reward"
aggregation = "all-pass"   # weighted-mean | weighted-sum | all-pass | any-pass | threshold | required-pass
# threshold = 0.7          # 仅用于 threshold
weights = { correctness = 2.0, quality = 1.0 }
```

```json
{ "correctness": 0.75, "structure": 1.0, "quality": 0.6, "reward": 0.0 }
```

每个维度的分数保持不变；聚合键将与其并列添加（一个 `name` 可能不会与维度冲突）。顶级维度权重相等，除非该聚合的行内映射覆盖它们；`reward-details.json` 保留完整的递归分解。

## 输出文件

- `/logs/verifier/reward.json` — 每个奖励的分数
- `/logs/verifier/reward-details.json` — 每个标准的检查结果、判定推理、错误

## 多步任务

在多步任务中，每个步骤都有自己的 `tests/` 在 `steps/{name}/tests/` 下，验证器每个步骤运行一次。Reward Kit 的行为与单步任务相同：对于每个步骤，它读取 `/tests`，运行标准与 `/app` 进行比较，并为该步骤写入 `/logs/verifier/reward.json`。Harbor 然后通过 `task.toml` 中的 `multi_step_reward_strategy` 将每个步骤的结果聚合为试验级奖励——聚合发生在 Reward Kit 外部，因此不要尝试在标准中编码跨步骤逻辑。

任务级的 `tests/` 目录（在任务根目录）首先上传到 `/tests`，然后是步骤自己的 `tests/` 覆盖在顶部（同名文件获胜）。将共享帮助程序（具有 `shared=True` 的常见 `checks.py` 函数、固定文件、备用 `test.sh`）放在任务级，步骤特定的标准放在每个步骤下。

多奖励子目录仍然在步骤内工作：`steps/foo/tests/` 可以包含 `correctness/`、`structure/`、`quality/`——每个为该步骤生成一个独立的奖励键，并且 `multi_step_reward_strategy = "mean"` 将每个键在步骤间平均。使用 `"final"` 时，最后一个步骤是一个端到端检查，其奖励已经代表整个任务。

## 何时选择什么

- **使用内置函数** 进行文件存在、字符串匹配、命令输出、JSON/CSV 检查、HTTP 探测。
- **使用 `@criterion`** 当逻辑是任务特定的但仍然是程序化时。
- **使用 LLM 判定** 对于主观质量维度（可读性、散文的正确性）。
- **使用代理判定** 当评分需要探索文件系统或运行代码时（例如，“测试套件是否真的通过？”）。
- **使用子目录** 当您希望有独立的分数（正确性 vs 结构 vs 质量）而不是一个混合数字时。
- **使用 `isolated=True`** 对于任何运行可变命令的标准，这样它不会破坏工作区供其他标准使用。

## 工作示例

请参阅 Harbor 仓库中的 `examples/tasks/reward-kit-example/`。
