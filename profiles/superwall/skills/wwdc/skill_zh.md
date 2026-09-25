# WWDC

使用 WWDC.ai 的 markdown 页面作为获取简洁会议摘要和 Apple 官方链接的首选。如果 markdown 摘要缺失或不详细，则使用无时间戳的会议文字记录。

## 辅助工具

在需要时运行捆绑脚本：

```bash
scripts/wwdc.sh llms
scripts/wwdc.sh summary 2026 389
scripts/wwdc.sh transcript 2026 309
```

`summary` 返回 WWDC.ai 的 markdown 页面。`transcript` 返回无时间戳的纯文本会议记录。存在 URL/JSON 辅助工具用于源代码检查。

有关端点详情和示例，请参阅 [references/docs.md](references/docs.md)。
