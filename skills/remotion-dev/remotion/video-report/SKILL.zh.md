---
name: video-report
description: 生成一份关于视频的报告
---

当用户报告视频无法播放时，我们应该下载该URL，并将其设置为`packages/example/src/NewVideo.tsx`中的`src`属性。

然后，在`packages/example`目录下，我们应该运行`bunx remotion render NewVideo --log=verbose`命令。
