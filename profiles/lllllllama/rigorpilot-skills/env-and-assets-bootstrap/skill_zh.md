# env-and-assets-bootstrap

将此用作“严谨设置（Rigor Setup）”技能。安装后的标识符仍保持为 `env-and-assets-bootstrap` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；本技能应使设置规划保持保守，同时将环境特定的判断权交给模型。

## 适用场景

- 当仓库接入流程已识别出可信的复现目标后。
- 在运行命令之前需要创建环境或准备资产路径时。
- 当仓库依赖检查点、数据集或缓存目录时。
- 当用户在尝试任何运行之前明确需要设置协助时。

## 不适用场景

- 当仓库已自带可直接运行的环境且无需翻译时。
- 当任务仅为扫描和规划时。
- 当任务仅为报告已运行命令的结果时。
- 当请求属于仓库复现范围之外的通用 conda 或包管理问题时。

## 明确边界

- 本技能准备环境与资产假设。
- 它不负责目标选择。
- 它不负责最终报告。
- 除将缺口转发给可选论文解析器外，本技能不执行论文查询。

## 输入期望

- 目标仓库路径
- 选定的复现目标
- 相关的 README 设置步骤
- 已知的 OS 或包管理限制

## 输出期望

- 保守的环境设置说明
- 候选的 conda 命令
- 资产路径规划
- 检查点与数据集来源提示
- 未解决的依赖或资产风险

## 注意事项

使用 `references/env-policy.md`、`references/assets-policy.md`、`scripts/bootstrap_env.py`、`scripts/plan_setup.py` 和 `scripts/prepare_assets.py`。

仅在 shell 入口点更为便捷时，将 `scripts/bootstrap_env.sh` 用作 Python 引导程序（bootstrapper）的 POSIX 封装。
