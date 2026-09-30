---
name: convex-improve-convex-plugin
description: 将本次编码会话的记录发送给 Convex 团队，以便进行 AI 停机分析，以改进快速启动系统。
---

<!-- GENERATED from convex-agents content/capabilities/improve-convex-plugin.json — do not手动编辑。 -->

# improve-convex-plugin

将当前的编码会话记录发送到 anteater 的 POST /review 端点，以进行 AI 命后分析。该分析会返回结构化发现（模糊指令、代理卡住模式、工具失败、成功案例），这些发现针对的是运行手册、引导脚本、技能和组件——而不是最终用户数据。分享是可选的：anteater 提供的助手会询问一次（始终 / 仅这一次 / 从不），并记住选择。

## 工作流程

1. 运行 anteater 提供的助手：`curl -fsSL "<anteater>/send-transcript" | bash -s -- --idea "<从本次会话中获取的一行应用想法>"`。
2. 如果它打印 CONSENT_REQUIRED（退出码 4），则用户尚未做出选择——请他们选择始终、仅这一次或不分享，然后重新运行并附加 --consent always|once|never。在用户回答之前不要发送。
3. 关注输出标记：REVIEW_SOURCE（找到记录）、REVIEW_SUBMITTED id=...（已接受）、REVIEW_DONE status=done（发现已准备好）。
4. 为用户总结最高严重性的发现：标题 → 目标 → 建议的修复方案，然后是成功案例。保持总结聚焦于系统，而不是用户数据。

## 规则

- 在用户明确选择分享之前，不要发送记录（助手打印 CONSENT_REQUIRED 并退出，直到他们做出选择）。
- REVIEW_NO_TRANSCRIPT 表示未找到 Claude/Codex .jsonl 文件——通知用户。
- 不要将原始密钥粘贴回去——脚本在上传前会编辑密钥/令牌；保持总结聚焦于系统。
- 这是一个系统改进循环，不是最终用户功能反馈。
