## 文档

- Cog 参考：<https://cog.run/llms.txt>
- `cog push` 参考：<https://cog.run/cli#cog-push>
- cog-safe-push：<https://github.com/replicate/cog-safe-push>
- 模型 CI 模板：<https://github.com/replicate/model-ci-template>
- 持续部署指南：<https://replicate.com/docs/guides/continuous-model-deployment>

## 何时使用此技能

- 您已经有一个可工作的 Cog 项目（如果没有，请参阅 `build-models`）。
- 您希望在 Replicate 上发布私有或公共模型。
- 您正在发布现有模型的新版本，并希望避免破坏性变更。
- 您正在为模型发布设置 CI/CD。

## 前置条件

- 已安装 Cog 并对 `r8.im` 执行 `cog login`（或 `echo $TOKEN | cog login --token-stdin`）。
- 通过 API、Web UI 或 `r8-model` CLI 在 `replicate.com/{owner}/{name}` 创建模型。
- 环境中设置了 `REPLICATE_API_TOKEN`。

## 简单的 `cog push`

最简单的路径。构建并上传新版本：

```
cog push r8.im/owner/my-model
```

或者设置 `image: r8.im/owner/my-model` 在 `cog.yaml` 中并运行一个裸的：

```
cog push
```

有用的标志：

- `--separate-weights` — 将权重存储在单独的层中；对于权重大于 1GB 的模型，更快的冷启动和推送。
- `--x-fast` — 迭代期间更快的推送（跳过一些验证）。
- `--secret id=hf,src=$HOME/.hf_token` — 在构建时传递密钥，而不会将其烘焙到镜像历史中。

## cog-safe-push（推荐用于任何有用户的模型）

`cog-safe-push` 首先推送到私有的 `-test` 模型，检查与活动版本的架构兼容性，运行预测比较，并模糊输入。在破坏性变更到达用户之前捕获它们。

安装：

```
pip install git+https://github.com/replicate/cog-safe-push.git
```

必需的环境变量：

- `REPLICATE_API_TOKEN`
- `ANTHROPIC_API_KEY`（Claude 判断随机模型的输出相似性）

基本用法：

```
cog-safe-push --test-hardware=gpu-l40s owner/my-model
```

这将：

1. 使用 ruff 检查 `predict.py`。
2. 如果不存在，则创建私有测试模型 `owner/my-model-test`。
3. 将本地 Cog 模型推送到测试模型。
4. 检查架构（描述、默认值等）。
5. 检查与活动 `owner/my-model` 版本的架构兼容性。
6. 在活动和测试版本之间运行预测比较。
7. 使用 AI 生成的输入模糊测试模型。
8. 如果一切通过，则推送到 `owner/my-model`。

## cog-safe-push.yaml 架构

在项目根目录中放置一个 `cog-safe-push.yaml`（或 `cog-safe-push-configs/<variant>.yaml` 对于多模型存储库）。一个示例中包含所有五种测试用例检查器类型：

```yaml
model: owner/my-model
test_model: owner/my-model-test
test_hardware: gpu-l40s

predict:
  compare_outputs: false              # 对于随机模型设置为 false
  predict_timeout: 600
  test_cases:
    - inputs:
        prompt: "a serene mountain landscape"
      match_prompt: "a landscape photo of mountains"   # 通过 Claude AI 判断
    - inputs:
        prompt: "a cat"
      match_url: "https://example.com/reference-cat.png"   # 二进制/图像匹配
    - inputs:
        prompt: ""
      error_contains: "prompt cannot be empty"           # 负面测试
    - inputs:
        mode: "json"
      jq_query: '.confidence > 0.8 and .status == "success"'   # JSON 输出
    - inputs:
        prompt: "echo this"
      exact_string: "echo this"                          # 精确字符串匹配
  fuzz:
    fixed_inputs:
      seed: 42
    disabled_inputs:
      - debug
    iterations: 10
    prompt: "Generate creative and diverse prompts"

train:                                  # 如果您的模型有训练器
  destination: owner/my-model-trained
  destination_hardware: gpu-l40s
  train_timeout: 1800
  test_cases:
    - inputs:
        input_images: "https://.../training.zip"
        steps: 10

deployment:                             # 推送时自动创建或更新
  name: my-model
  owner: owner
  hardware: gpu-l40s

parallel: 4
fast_push: false
ignore_schema_compatibility: false
official_model: owner/my-model         # 对于代理/包装模型，见下文
```

测试用例检查器是互斥的：每个用例选择 `match_prompt`、`match_url`、`error_contains`、`jq_query` 或 `exact_string` 中的一个。对于任何随机模型（扩散、LLM），使用 `compare_outputs: false`；默认的 `true` 是脆弱的。

## CI/CD：GitHub Actions

两种路径，取决于您希望有多少粘合。

### 路径 A：自行构建

```yaml
# .github/workflows/push.yaml
name: Push to Replicate
on:
  workflow_dispatch:
    inputs:
      no_push:
        type: boolean
        default: false

jobs:
  push:
    runs-on: ubuntu-latest-4-cores       # 构建需要磁盘 + 核心
    steps:
      - uses: actions/checkout@v4
      - uses: jlumbroso/free-disk-space@v1.3.1
        with:
          tool-cache: false
          docker-images: false
      - uses: replicate/setup-cog@v2
        with:
          token: ${{ secrets.REPLICATE_API_TOKEN }}
      - run: pip install git+https://github.com/replicate/cog-safe-push.git
      - env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          REPLICATE_API_TOKEN: ${{ secrets.REPLICATE_API_TOKEN }}
        run: |
          cog-safe-push -vv ${{ inputs.no_push && '--no-push' || '' }}
```

添加一个 `concurrency:` 块，以便 PR 构建相互取消，而主分支推送排队：

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

### 路径 B：可重用的模型 CI 模板工作流

对于 Replicate 风格的多模型存储库，放入：

```yaml
# .github/workflows/ci.yaml
name: CI
on:
  pull_request: { branches: [main] }
  push: { branches: [main] }
  workflow_dispatch:
    inputs:
      models: { type: string, default: "all" }
      ignore_schema_checks: { type: boolean, default: false }
      cog_version: { type: string, default: "latest" }
      test_only: { type: boolean, default: false }

jobs:
  ci:
    uses: replicate/model-ci-template/.github/workflows/template.yaml@main
    with:
      trigger_type: ${{ github.event_name }}
      models: ${{ inputs.models || 'all' }}
      ignore_schema_checks: ${{ inputs.ignore_schema_checks || false }}
      cog_version: ${{ inputs.cog_version || 'latest' }}
      test_only: ${{ inputs.test_only || false }}
    secrets: inherit
```

可重用工作流期望：

- `cog-safe-push-configs/<model>.yaml` — 每个模型变体一个。
- `script/select-model` — 包含 `if/elif [[ "$MODEL" == "..." ]]` 块的 bash 文件，列出有效模型名称。
- 密钥：`COG_TOKEN`、`REPLICATE_API_TOKEN`、`ANTHROPIC_API_KEY`。

## 多模型矩阵推送

来自 `replicate/cog-flux` 的模式：一个存储库，N 个变体，并行推送它们。

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - id: set
        run: |
          if [ "${{ inputs.models }}" = "all" ]; then
            echo 'matrix={"model":["schnell","dev","krea-dev"]}' >> "$GITHUB_OUTPUT"
          else
            list=$(echo "${{ inputs.models }}" | jq -Rc 'split(",")')
            echo "matrix={\"model\":$list}" >> "$GITHUB_OUTPUT"
          fi

  push:
    needs: prepare
    runs-on: ubuntu-latest-4-cores
    strategy:
      fail-fast: false
      matrix: ${{ fromJson(needs.prepare.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4
      - run: ./script/select.sh ${{ matrix.model }}     # 从模板生成 cog.yaml
      - run: cog-safe-push --config cog-safe-push-configs/${{ matrix.model }}.yaml -vv
```

## 代理/官方模型的二阶段推送

当您维护一个包装第三方 API 的代理时，您首先推送到私有包装器，然后更新面向公众的官方模型卡。模式来自 `replicate/cog-official-template`：

```bash
./script/write-api-key                                              # 将 API 密钥烘焙到配置中
cog-safe-push --config cog-safe-push-configs/${MODEL}.yaml -vv

./script/delete-api-key                                             # 删除密钥
cog-safe-push --push-official-model --config cog-safe-push-configs/${MODEL}.yaml -vv
```

在配置中设置 `official_model: owner/name`，以便 `--push-official-model` 知道发布位置。

## 部署

在每次推送时自动创建或更新 Replicate 部署，向 `cog-safe-push.yaml` 添加一个 `deployment` 块：

```yaml
deployment:
  name: my-model
  owner: owner
  hardware: gpu-l40s
```

扩展默认值：CPU 部署扩展 1-20 个实例，GPU 部署扩展 0-2。当需要时，手动通过 API 或 Web UI 调整。

## 监控已发布的模型

运行一个每小时金丝雀，以执行注册路径。模式来自 `replicate/cog-pagerduty-check`：

```yaml
name: Hourly cog push check
on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: |
          # 生成一个具有唯一 uuid 的微小模型，推送它，运行预测
          # 通过摘要，如果任何内容中断，请大声失败。
          ./script/canary.sh
```

对于任何生产关键模型都值得做，尤其是在收入取决于注册处于活动状态时。

## 指南

- 除非您有意，否则不要破坏架构兼容性。cog-safe-push 捕获它；`--ignore-schema-compatibility` 是退出选项。
- 固定 `test_hardware`，以便测试推送可重复。
- 在 PR CI 中使用 `--no-push` 进行干跑；合并到 main 或版本标签时进行完整推送。
- 一旦有用户，请从 CI 而不是笔记本电脑推送。
- 对于随机模型，使用 `compare_outputs: false`。使用 `match_prompt:` 对于图像/视频输出（VLM 判断），`match_url:` 对于您控制的二进制输出，`jq_query:` 对于 JSON，`error_contains:` 对于负面测试。
- 永远不要提交 `REPLICATE_API_TOKEN` 或 `ANTHROPIC_API_KEY`。使用存储库密钥。
- 对于权重大于 1GB 的模型，使用 `--separate-weights` 推送。

## 生产参考

- <https://github.com/replicate/cog-safe-push> — 该工具本身及其配置架构。
- <https://github.com/replicate/model-ci-template> — 可重用的 GitHub Actions 工作流。
- <https://github.com/replicate/cog-official-template> — 代理/官方模型模板。
- <https://github.com/replicate/cog-flux/blob/main/.github/workflows/push.yaml> — 跨 FLUX 变体的矩阵推送。
- <https://github.com/replicate/cog-comfyui/blob/main/.github/workflows/ci.yaml> — ComfyUI 模型 CI，带有自定义节点安装步骤。
- <https://github.com/replicate/cog-pagerduty-check> — 每小时金丝雀模式。
