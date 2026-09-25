# 测试指南

---

## 先回答测试问题

关于禁用测试但不删除测试的问题：

- 功能测试条目保留在 YAML 中；通过在作用域后缀添加 `-broken` 来禁用，例如 `scope: [mr-github]` -> `scope: [mr-github-broken]`。
- 单元测试跳过使用 pytest 标记：`@pytest.mark.flaky_in_dev` 在默认开发环境中跳过，而 `@pytest.mark.flaky` 在 LTS 环境中跳过。
- 当目标是可发现性和易于重新启用时，不要删除测试用例或配方条目。

---

## 测试布局

```text
tests/
├── unit_tests/          # pytest, 1 个节点 × 8 个 GPU，torch.distributed 运行器
├── functional_tests/    # 端到端 shell + 训练脚本
│   └── test_cases/
│       └── {模型}/{测试用例}/
│           ├── model_config.yaml          # 训练参数
│           └── golden_values_{环境}_{平台}.json
└── test_utils/
    ├── recipes/
    │   ├── h100/        # H100 作业的 YAML 配方
    │   └── gb200/       # GB200 作业的 YAML 配方
    └── python_scripts/  # 辅助工具 (recipe_parser, golden-value 下载，…)
```

---

## 测试执行方式

GitHub Actions 运行器调用 `launch_nemo_run_workload.py`，该脚本使用 **nemo-run** 启动 `DockerExecutor` 容器。代码库绑定挂载在 `/opt/megatron-lm`；训练数据挂载在 `/mnt/artifacts`。

**单元测试** 通过 `torch.distributed.run` 分发：

- 排名 0 和 3 被合并输出到 stdout；其他所有排名仅写入日志文件。
- 每个排名的日志文件位于 `{assets_dir}/logs/1/`，并在运行后作为 GitHub 附件上传。

**功能测试** 由 `tests/functional_tests/shell_test_utils/run_ci_test.sh` 驱动。仅排名 0 运行 pytest 验证步骤；所有排名的训练输出作为附件上传。

**易失败自动重试**：`launch_nemo_run_workload.py` 在声明真实失败之前，会针对已知瞬态模式（NCCL 超时、ECC 错误、段错误、HuggingFace 连接性，…）最多重试 **3 次**。

---

## 配方 YAML 结构

配方位于 `tests/test_utils/recipes/`，并由 `tests/test_utils/python_scripts/recipe_parser.py` 解析。每个文件将笛卡尔积 `products` 块扩展为单独的工作负载规范：

```yaml
type: basic
format_version: 1
maintainers: [mcore]
loggers: [stdout]
spec:
  name: "{测试用例}_{环境}_{平台}"
  model: gpt              # 映射到 tests/functional_tests/test_cases/{模型}/
  build: mcore-pyt-{环境}
  nodes: 1
  gpus: 8
  n_repeat: 5
  platforms: dgx_h100
  time_limit: 1800
  script_setup: |
    ...
  script: |-
    bash tests/functional_tests/shell_test_utils/run_ci_test.sh ...
products:
  - test_case: [my_test]
    products:
      - environment: [dev, lts]
        scope: [mr-github]
        platforms: [dgx_h100]
```

关键运行时占位符：`{assets_dir}`、`{artifacts_dir}`、`{测试用例}`、`{环境}`、`{平台}`、`{n_repeat}`。

### 不删除测试用例禁用测试

要在配方 YAML 中临时禁用测试用例，在其 `scope` 值后缀添加 `-broken` — **不要删除条目**：

```yaml
# 之前 (测试在 CI 中运行)
scope: [mr-github]

# 之后 (测试被跳过；条目保留以便轻松重新启用)
scope: [mr-github-broken]
```

---

## 本地运行单元测试

所有单元测试初始化一个 `torch.distributed` 组，因此每次调用都需要 GPU 访问并通过 `torch.distributed.run`：

```bash
# 完整套件
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests

# 单个文件
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests/models/test_gpt_model.py

# 单个测试
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests/models/test_gpt_model.py::TestGPTModel::test_constructor

# 通过名称子字符串过滤
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests -k optimizer
```

### 标记过滤器

```bash
# 在开发期间排除易失败测试
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests -m "not flaky and not flaky_in_dev"

# 包含实验性测试
uv run python -m torch.distributed.run --nproc-per-node 8 -m pytest -q \
  tests/unit_tests --experimental
```

### CI 对齐

使用 `tests/unit_tests/run_ci_test.sh` 来精确重现 CI 桶失败。对于临时运行，请优先使用上述直接的 `torch.distributed.run` 调用。

### 注意事项

- `pyproject.toml` 设置 `addopts = --durations=15 -s -rA` — stdout 不会被捕获 (`-s`)，所以在多排名运行时排名会交错。在调试特定排名时使用 `--capture=fd` 覆盖。
- `tests/unit_tests/conftest.py` 在 `/opt/data` 下查找测试数据，如果缺失则尝试下载。在容器外运行时手动提供它或跳过依赖数据的测试。

---

## 添加单元测试

1. 创建 `tests/unit_tests/<分类>/test_<名称>.py`。
2. 使用 `tests/unit_tests/conftest.py` 中的 fixtures。
3. 根据需要应用标记：
   - `@pytest.mark.internal` — 在 `legacy` 标签上跳过
   - `@pytest.mark.flaky_in_dev` — 在 `dev` 环境中跳过 (CI 默认；使用此标记禁用易失败测试而不阻塞标准管道)
   - `@pytest.mark.flaky` — 在 `lts` 环境中跳过
   - `@pytest.mark.experimental` — 仅 `latest` 标签
4. 本地验证（见上述“本地运行单元测试”）。
5. 如果测试需要专门的 CI 桶，将条目添加到 `tests/test_utils/recipes/h100/unit-tests.yaml`。

---

## 添加功能/集成测试

1. 创建 `tests/functional_tests/test_cases/<模型>/<测试名称>/`。
2. 编写 `model_config.yaml`，包含 `MODEL_ARGS`、`ENV_VARS` 和 `TEST_TYPE`。
3. 在 `tests/test_utils/recipes/h100/` 下添加 YAML 配方（如果需要，在 `gb200/` 下添加）。必需字段：`scope`、`环境`、`平台`、`n_repeat`、`time_limit`。
4. 推送 PR，为触发完整运行添加标签 **"运行功能测试"**。
5. 运行成功后，下载 golden 值：

   ```bash
   python tests/test_utils/python_scripts/download_golden_values.py \
     --source github --pipeline-id <运行 ID>
   ```

6. 提交下载的 golden 值。

---

## 常见陷阱

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| 测试本地通过但在 CI 中失败 | 环境不同或数据路径 | 检查 `DATA_PATH`、`DATA_CACHE_PATH` 和 `环境` 标签 (`dev` vs `lts`) |
| 代码更改后 golden 值不匹配 | 数值回归 | 在干净运行后通过 `download_golden_values.py` 下载新的 golden 值 |
| `cicd-integration-tests-gb200` 未触发 | GB200 作业需要维护者状态 | 请求维护者触发，或添加 `运行功能测试` 标签 |
