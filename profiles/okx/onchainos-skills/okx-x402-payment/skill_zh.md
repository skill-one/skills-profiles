# 已弃用 — 已合并到 `okx-agent-payments-protocol`

此技能已合并到统一支付调度器中。功能保持不变；仅入口点已更改。

**操作指南**：通过技能工具加载 **`okx-agent-payments-protocol`** 并使用该技能。x402 + MPP 流程位于：

- `okx-agent-payments-protocol/SKILL.md` — 路径 A（HTTP 402 检测 + 调度）
- `okx-agent-payments-protocol/references/exact.md` — x402 `exact` 方案（TEE EIP-3009 或本地密钥回退）
- `okx-agent-payments-protocol/references/aggr_deferred.md` — x402 `aggr_deferred` 方案（会话密钥 + sessionCert）
- `okx-agent-payments-protocol/references/charge.md` — MPP `charge` 意图（一次性、交易或哈希模式）
- `okx-agent-payments-protocol/references/session.md` — MPP `session` 意图（开启 / 优惠券 / 充值 / 关闭）

**此占位符存在的原因**：遗留的文本记录、脚本和外部文档可能仍通过名称引用 `okx-x402-payment`。此占位符捕获这些引用并重定向到合并后的技能。它本身不携带任何触发器——提及 x402 / MPP / 402 / 频道操作的对话将直接路由到 `okx-agent-payments-protocol`，基于该技能的触发器。
