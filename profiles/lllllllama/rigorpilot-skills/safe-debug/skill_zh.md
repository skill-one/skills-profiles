# safe-debug

将此作为 Rigor Debug / Rigor Audit 技能使用。已安装的标识符保持为 `safe-debug` 以保证兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；该技能应指导保守诊断，但不阻止模型寻找本地根本原因。

## 何时应用

- 用户提供了回溯信息、终端错误，或具体的训练或推理失败症状。
- 用户在修改代码前，需要诊断、定位根本原因，以及最小化的补丁建议。
- 用户需要安全调试流程，并在变更（修改）前获得明确的人工审批。

## 不适用情形

- 当用户在没有实际故障的情况下需要进行广泛的代码仓库遍历时。
- 当任务为推测性实验或代码适配时。
- 当用户要求大范围重构或可读性重写时。

## 明确边界

- 先进行诊断。
- 默认不修改仓库代码。
- 如果需要补丁，首先提出最小的修复方案，并要求明确审批。
- 在执行中等风险或高风险变更前，需升级保存点或分支创建。
- 调试修复并不自动构成研究贡献；如果它改变了实验含义或可比性，需明确说明。

## 输出期望

- `debug_outputs/DIAGNOSIS.md`
- `debug_outputs/PATCH_PLAN.md`
- `debug_outputs/status.json`

## 备注

使用 `references/debug-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md`，以及共享的 `../ai-research-reproduction/references/research-pitfall-checklist.md`。
