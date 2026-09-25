<!-- GENERATED from convex-agents content/capabilities/env.json — do not edit by hand. -->

# 管理环境变量 + 密钥

将密钥存储为 Convex 部署的环境变量（使用 `npx convex env set`），在 actions 中通过 `process.env` 读取它们，切勿提交它们。

## 工作流程

1. `npx convex env set KEY value`（每个部署使用）。
2. 在 actions 中通过 `process.env.KEY` 读取（不在 queries/mutations 中）。
3. 切勿硬编码或提交密钥；仅在本地添加到 `.env.local`。
4. 使用 `npx convex env list` 确认。

## 规则

- 密钥存储在 Convex 环境变量中，绝不在代码或 git 中。
- `process.env` 仅在 actions 中使用（如果需要，使用 'use node'），不在 queries/mutations 中。
- 不同的部署需要它们自己的值。
