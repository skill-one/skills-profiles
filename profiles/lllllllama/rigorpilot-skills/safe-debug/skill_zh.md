# safe-debug

将此用作 Rigor Debug / Rigor Audit 技能。安装的模块名称保持为 `safe-debug` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；此技能应指导保守的诊断，同时不阻止模型找到局部根本原因。

## 何时应用

- 用户提供了堆栈跟踪、终端错误或具体的训练或推理失败症状。
- 用户希望在代码更改之前进行诊断、根本原因缩小和最小化补丁建议。
- 用户希望在变异之前获得安全的调试流程和明确的人工批准。

## 何时不应用

- 当用户希望在不活跃故障的情况下进行广泛的代码库遍历时。
- 当任务涉及推测性实验或代码适配时。
- 当用户要求进行大规模重构或可读性重写时。

## 明确的界限

- 首先进行诊断。
- 默认情况下不要修改代码库代码。
- 如果需要补丁，首先提出最小的修复方案并要求明确批准。
- 在进行中风险或高风险更改之前，升级保存点或分支创建。
- 调试修复不自动构成研究贡献；如果它改变了实验意义或可比性，请明确说明。

## 输出预期

- `debug_outputs/DIAGNOSIS.md`
- `debug_outputs/PATCH_PLAN.md`
- `debug_outputs/status.json`

## 注意事项

使用 `references/debug-policy.md`、`../ai-research-reproduction/references/research-rigor-principles.md` 和共享的 `../ai-research-reproduction/references/research-pitfall-checklist.md`。
