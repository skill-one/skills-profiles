# xurl

使用 `xurl` 进行 X API 操作。快捷命令返回 JSON；原始模式适用于任何 v2 端点。

## 密钥安全

- 不要读取、打印、总结、上传或检查 `~/.xurl`。
- 不要要求用户将令牌/密钥粘贴到聊天中。
- 不要使用带内联密钥的认证命令。
- 在代理会话中不要使用 `--verbose`；它可能会暴露认证头。
- 使用 `xurl auth status` 检查认证状态。

## 常用快捷命令

```bash
xurl post "Hello world!"
xurl reply POST_ID "Nice."
xurl quote POST_ID "My take"
xurl delete POST_ID
xurl read POST_ID
xurl search "query" -n 20
xurl whoami
xurl user @handle
xurl timeline -n 20
xurl mentions -n 10
xurl like POST_ID
xurl unlike POST_ID
xurl repost POST_ID
xurl unrepost POST_ID
xurl bookmark POST_ID
xurl unbookmark POST_ID
xurl followers -n 20
xurl following -n 20
xurl follow @handle
xurl unfollow @handle
xurl block @handle
xurl unblock @handle
xurl mute @handle
xurl unmute @handle
xurl dm @handle "message"
xurl dms -n 10
```

`POST_ID` 可以是一个完整的 `https://x.com/<user>/status/<id>` URL。

## 媒体

```bash
xurl media upload image.jpg
xurl media upload clip.mp4
xurl media status MEDIA_ID
xurl post "caption" --media-id MEDIA_ID
```

视频可能需要处理；使用 `media status` 查询。

## 认证/应用管理

```bash
xurl auth status
xurl auth apps list
xurl auth default
xurl auth default APP_NAME USERNAME
xurl auth apps remove APP_NAME
```

按需使用：

```bash
xurl --app APP_NAME /2/users/me
xurl --auth oauth2 /2/users/me
```

## 原始 API

```bash
xurl /2/users/me
xurl -X POST /2/tweets -d '{"text":"Hello world!"}'
xurl '/2/tweets/search/recent?query=openclaw&max_results=10'
```

当快捷命令无法覆盖端点时使用原始模式。将复杂 JSON 的有效负载保存在临时文件中。

## 输出和错误

- 成功时输出 JSON。
- API/认证/网络错误时非零退出。
- 401/403：认证、权限或应用不匹配；检查 `xurl auth status`。
- 429：速率限制；稍作等待。
- 媒体上传失败：检查文件类型/大小和媒体处理状态。
