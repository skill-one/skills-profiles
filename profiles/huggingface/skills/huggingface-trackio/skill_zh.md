# Trackio - 用于机器学习训练的实验跟踪

Trackio 是一个用于记录和可视化机器学习训练指标的实验跟踪库。它可以与 Hugging Face Spaces 同步，以实现实时监控仪表板。

## 三个接口

| 任务 | 接口 | 参考 |
|------|-----------|-----------|
| **在训练期间记录指标** | Python API | [references/logging_metrics.md](references/logging_metrics.md) |
| **触发用于训练诊断的警报** | Python API | [references/alerts.md](references/alerts.md) |
| **在训练后/期间检索指标和警报** | CLI | [references/retrieving_metrics.md](references/retrieving_metrics.md) |

## 何时使用每个接口

### Python API → 记录

在训练脚本中使用 `import trackio` 来记录指标：

- 使用 `trackio.init()` 初始化跟踪
- 使用 `trackio.log()` 记录指标，或使用 TRL 的 `report_to="trackio"`
- 使用 `trackio.finish()` 结束

**关键概念**：对于远程/云训练，请传递 `space_id` — 指标将同步到 Space 仪表板，以便在实例终止后仍然存在。自动创建的 Space 默认为 **公开** — 如果指标不应公开，请传递 `private=True`。

→ 参考 [references/logging_metrics.md](references/logging_metrics.md) 了解设置、TRL 集成和配置选项。

### Python API → 警报

在训练代码中插入 `trackio.alert()` 调用来标记重要事件 — 类似于插入用于调试的打印语句，但结构化且可查询：

- `trackio.alert(title="...", level=trackio.AlertLevel.WARN)` — 触发警报
- 三个严重程度级别：`INFO`、`WARN`、`ERROR`
- 警报将打印到终端、存储在数据库中、显示在仪表板中，并可选择发送到 webhook（Slack/Discord）

**关键概念对于 LLM 代理**：警报是自主实验迭代的主要机制。代理应在训练代码中插入警报以进行诊断条件（损失峰值、NaN 梯度、低准确率、训练停滞）。由于警报会打印到终端，因此正在监视训练脚本输出的代理将自动看到它们。对于后台或分离运行，代理可以通过 CLI 进行轮询。

→ 参考 [references/alerts.md](references/alerts.md) 了解完整的警报 API、webhook 设置和自主代理工作流程。

### CLI → 检索

使用 `trackio` 命令查询记录的指标和警报：

- `trackio list projects/runs/metrics` — 查找可用内容
- `trackio get project/run/metric` — 检索摘要和值
- `trackio list alerts --project <name> --json` — 检索警报
- `trackio show` — 启动仪表板
- `trackio sync` — 同步到 HF Space

**关键概念**：添加 `--json` 以获得适合自动化和 LLM 代理的程序化输出。

→ 参考 [references/retrieving_metrics.md](references/retrieving_metrics.md) 了解所有命令、工作流程和 JSON 输出格式。

## 最小记录设置

```python
import trackio

# Space 默认为公开（适用于可共享的仪表板）；
# 如果指标不应公开，请传递 private=True
trackio.init(project="my-project", space_id="username/trackio", private=True)
trackio.log({"loss": 0.1, "accuracy": 0.9})
trackio.log({"loss": 0.09, "accuracy": 0.91})
trackio.finish()
```

### 最小检索

```bash
trackio list projects --json
trackio get metric --project my-project --run my-run --metric loss --json
```

## 自主机器学习实验工作流程

当作为 LLM 代理自主运行实验时，推荐的工作流程是：

1. **设置带警报的训练** — 插入 `trackio.alert()` 调用来进行诊断条件
2. **启动训练** — 在后台运行脚本
3. **轮询警报** — 使用 `trackio list alerts --project <name> --json --since <timestamp>` 检查新警报
4. **读取指标** — 使用 `trackio get metric ...` 检查特定值
5. **迭代** — 根据警报和指标，停止运行、调整超参数并启动新运行

```python
import trackio

trackio.init(project="my-project", config={"lr": 1e-4})

for step in range(num_steps):
    loss = train_step()
    trackio.log({"loss": loss, "step": step})

    if step > 100 and loss > 5.0:
        trackio.alert(
            title="Loss divergence",
            text=f"Loss {loss:.4f} still high after {step} steps",
            level=trackio.AlertLevel.ERROR,
        )
    if step > 0 and abs(loss) < 1e-8:
        trackio.alert(
            title="Vanishing loss",
            text="Loss near zero — possible gradient collapse",
            level=trackio.AlertLevel.WARN,
        )

trackio.finish()
```

然后在单独的终端/进程中轮询：

```bash
trackio list alerts --project my-project --json --since "2025-01-01T00:00:00"
```
