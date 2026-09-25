# 抖音视频摘要

摘要抖音视频：提取音频 → 本地转写 → AI 摘要。

## 前置条件

安装这些工具（macOS 示例）：

```bash
brew install whisper-cpp ffmpeg
# 下载 whisper.cpp GGML 模型（推荐小型以平衡速度/质量）
curl -L -o models/ggml-small.bin "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
```

## 工作流程

当收到抖音链接时：

### 第 1 步：提取视频 ID

解析抖音 URL 获取视频 ID。抖音分享链接有两种格式：
- 短链接：`https://v.douyin.com/xxxxx/` → 跟随重定向获取视频 ID
- 直接链接：`https://www.douyin.com/video/7604713801732365681`

```bash
# 跟随重定向获取最终 URL，提取数字视频 ID
curl -sL -o /dev/null -w '%{url_effective}' 'https://v.douyin.com/xxxxx/' | grep -oE '[0-9]{15,}'
```

### 第 2 步：通过浏览器获取音频

抖音阻止直接下载（yt-dlp、aria2c 都会 403）。使用浏览器拦截音频 URL：

1. 在浏览器中打开抖音视频页面
2. 注入 JS 以在导航前拦截网络请求：

```javascript
window.__audioUrls = [];
const origOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
  if (url && (url.includes('.mp3') || url.includes('.m4a') || url.includes('mime_type=audio'))) {
    window.__audioUrls.push(url);
  }
  return origOpen.apply(this, arguments);
};
```

3. 导航到视频页面，点击播放以触发音频加载
4. 检索拦截的 URL：`window.__audioUrls`
5. 使用 curl 下载（需要 Referer 头）：

```bash
curl -H "Referer: https://www.douyin.com/" -o audio.mp4 "<audio_url>"
```

**重要提示：** `aria2c` 在抖音 CDN URL 上会 403。始终使用带 Referer 头的 `curl`。

### 第 3 步：转换为 WAV

```bash
ffmpeg -i audio.mp4 -ar 16000 -ac 1 -c:a pcm_s16le audio.wav
```

### 第 4 步：使用 whisper.cpp 转写

```bash
whisper-cli -m /path/to/ggml-small.bin -l zh -f audio.wav -otxt -of output
```

- 使用 `-l zh` 表示中文内容（不确定时自动检测）
- Apple Silicon GPU 加速自动启用（Metal）
- 性能：M4 上处理 5 分钟音频约需 20 秒

### 第 5 步：生成摘要

读取转写文本并生成结构化摘要：

```
📹 **[视频标题] | [作者]**
时长：X分X秒 | 发布：YYYY-MM-DD

🎯 **核心观点：[一句话核心信息]**

**1. [要点 1 标题]**
• [细节]
• [细节]

**2. [要点 2 标题]**
• [细节]

💬 **一句话总结：[简洁的要点]**
```

### 第 6 步（可选）：同步到飞书文档

如果已配置飞书集成，则使用飞书 Open API 将摘要追加到飞书文档。API 详情请参阅 [参考资料/feishu-sync.md](references/feishu-sync.md)。

## 小贴士

- 对于短视频（<1 分钟），摘要可能非常简短——这是正常的
- 如果浏览器拦截失败，可重试一次；抖音页面有时需要二次加载
- 处理后清理下载的音频/wav 文件以节省磁盘空间
- whisper.cpp `small` 模型是速度/质量的最佳平衡；`medium` 可能会在 8GB 机器上耗尽内存
