# 环境与资源引导

将此用作 Rigor Setup 技能。安装的 slug 保持为
`env-and-assets-bootstrap` 以确保兼容性。

使用
`../ai-research-reproduction/references/agent-operating-principles.md`
中的共享操作原则；此技能应保持设置规划保守，同时将特定环境的判断留给模型。

## 何时应用

- 在代码库摄入识别出可信的复现目标后。
- 在运行命令前需要创建环境或准备资源路径时。
- 当代码库依赖于检查点、数据集或缓存目录时。
- 在用户在任何运行尝试前明确需要设置帮助时。

## 何时不应用

- 当代码库已经包含无需翻译即可运行的现成环境时。
- 当任务仅是扫描和规划时。
- 当任务仅是报告已运行命令的结果时。
- 当请求是代码库复现之外的通用 conda 或包管理问题时。

## 清晰的边界

- 此技能准备环境和资源假设。
- 它不拥有目标选择。
- 它不拥有最终报告。
- 它除了将空白转发给可选的论文解析器外，不执行论文查找。

## 输入预期

- 目标代码库路径
- 选择的复现目标
- 相关的 README 设置步骤
- 任何已知的 OS 或包约束

## 输出预期

- 保守的环境设置说明
- 候选 conda 命令
- 资源路径计划
- 检查点和数据集来源提示
- 未解决的依赖或资源风险

## 注意事项

使用 `references/env-policy.md`、`references/assets-policy.md`、`scripts/bootstrap_env.py`、`scripts/plan_setup.py` 和 `scripts/prepare_assets.py`。
仅当 shell 入口点更方便时，才使用 `scripts/bootstrap_env.sh` 作为 Python 引导器的 POSIX 包装器。
