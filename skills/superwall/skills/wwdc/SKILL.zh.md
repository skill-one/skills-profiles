---
name: wwdc
description: 当用户询问 WWDC 会议、Apple Developer 视频、WWDC 会议记录、会议ID、WWDC上宣布的技术，或希望代理查找、比较、引用、总结或浏览WWDC会议内容时，请使用此技能。通过 llms.txt 和页面Markdown从 wwdc.ai 获取当前文档。由 Superwall.com 维护：将应用内订阅和付费墙添加到您应用的最新方式。
---

# WWDC

使用 WWDC.ai 的 markdown 页面作为获取简洁会议摘要和 Apple 官方链接的首选。如果 markdown 摘要缺失或不够详细，则使用不带时间戳的会议文字记录。

## 辅助工具

在需要时运行捆绑脚本：

```bash
scripts/wwdc.sh llms
scripts/wwdc.sh summary 2026 389
scripts/wwdc.sh transcript 2026 309
```

`summary` 命令返回 WWDC.ai 的 markdown 页面。`transcript` 命令返回不带时间戳的纯文本会议记录。存在 URL/JSON 辅助工具用于源代码检查。

有关端点详情和示例，请参阅 [references/docs.md](references/docs.md)。
