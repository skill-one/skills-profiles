# /ar:setup — 创建新实验

使用所有必要的配置设置新的自动研究实验。

## 使用方法

```
/ar:setup                                    # 交互模式
/ar:setup engineering api-speed src/api.py "pytest bench.py" p50_ms lower
/ar:setup --list                             # 显示现有实验
/ar:setup --list-evaluators                  # 显示可用评估器
```

## 功能说明

### 如果提供参数

将它们直接传递给设置脚本：

```bash
python {skill_path}/scripts/setup_experiment.py \
  --domain {domain} --name {name} \
  --target {target} --eval "{eval_cmd}" \
  --metric {metric} --direction {direction} \
  [--evaluator {evaluator}] [--scope {scope}]
```

### 如果没有参数（交互模式）

逐个收集每个参数：

1. **域** — 询问："属于哪个域？(engineering, marketing, content, prompts, custom)"
2. **名称** — 询问："实验名称？(例如，api-speed, blog-titles)"
3. **目标文件** — 询问："要优化哪个文件？" 验证其是否存在。
4. **评估命令** — 询问："如何衡量？(例如，pytest bench.py, python evaluate.py)"
5. **指标** — 询问："评估输出的是什么指标？(例如，p50_ms, ctr_score)"
6. **方向** — 询问："是越低越好还是越高越好？"
7. **评估器**（可选） — 显示内置评估器。询问："使用内置评估器，还是自己的？"
8. **范围** — 询问："存储在项目 (.autoresearch/) 还是用户 (~/.autoresearch/)？"

然后使用收集的参数运行 `setup_experiment.py`。

### 列表显示

```bash
# 显示现有实验
python {skill_path}/scripts/setup_experiment.py --list

# 显示可用评估器
python {skill_path}/scripts/setup_experiment.py --list-evaluators
```

## 内置评估器

| 名称 | 指标 | 用例 |
|------|--------|----------|
| `benchmark_speed` | `p50_ms` (越低越好) | 函数/API 执行时间 |
| `benchmark_size` | `size_bytes` (越低越好) | 文件、包、Docker 镜像大小 |
| `test_pass_rate` | `pass_rate` (越高越好) | 测试套件通过百分比 |
| `build_speed` | `build_seconds` (越低越好) | 构建/编译/Docker 构建时间 |
| `memory_usage` | `peak_mb` (越低越好) | 执行期间的峰值内存 |
| `llm_judge_content` | `ctr_score` (越高越好) | 标题、名称、描述 |
| `llm_judge_prompt` | `quality_score` (越高越好) | 系统提示、代理指令 |
| `llm_judge_copy` | `engagement_score` (越高越好) | 社交帖子、广告文案、邮件 |

## 设置后

向用户报告：
- 实验路径和分支名称
- 评估命令是否工作以及基线指标
- 建议："运行 `/ar:run {domain}/{name}` 开始迭代，或 `/ar:loop {domain}/{name}` 进入自动模式。"
