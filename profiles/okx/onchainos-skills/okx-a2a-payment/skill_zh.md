# 已弃用 — 已合并到 `okx-agent-payments-protocol`

此功能已被整合到统一支付调度器中。功能保持不变；仅入口点已更改。

**操作步骤**：通过技能工具加载 **`okx-agent-payments-protocol`** 并使用该技能。a2a-pay 流程位于：

- `okx-agent-payments-protocol/SKILL.md` — 路径 B（基于 paymentId，无 402）
- `okx-agent-payments-protocol/references/a2a_charge.md` — 完整的创建/支付/状态操作指南

**此占位符存在的原因**：遗留的文本记录、脚本和外部文档可能仍通过名称引用 `okx-a2a-payment`。此占位符捕获这些引用并重定向到已合并的技能。它本身不包含任何触发器 — 新的对话中提及 paymentId / `a2a_...` / "创建支付链接" / "支付状态" 将直接根据该技能的触发器路由到 `okx-agent-payments-protocol`。
