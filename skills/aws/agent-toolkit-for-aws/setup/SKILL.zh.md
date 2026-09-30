---
name: setup
description: 设置 AWS DevOps 代理和 AWS 安全代理的连接。当用户说“设置”、“配置”或“连接”，或者 MCP 工具缺失时使用。
---

# 设置

按顺序运行以下技能：

1. 调用 `setup-devops-agent` 技能以配置 DevOps Agent MCP 连接。
2. 调用 `setup-security-agent` 技能以配置 Security Agent 工作区（代理空间、IAM 角色、S3 存储桶）。

如果用户只需要一个代理，则只需运行相关的技能。
