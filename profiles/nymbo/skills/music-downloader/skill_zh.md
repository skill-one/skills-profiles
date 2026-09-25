# 音乐下载器

## 概述

该技能能够使用yt-dlp和spotdl从各种平台（YouTube、SoundCloud、Spotify等）下载高质量音频。它提供单首歌曲、播放列表、专辑的命令模板，以及元数据嵌入、缩略图提取和格式转换等高级功能。

如果用户没有提供特定歌曲或播放列表的链接，您必须使用环境中的工具搜索网络，以找到用户想要的内容。

在使用`Web_Search`工具时，将搜索类型设置为`videos`，并优先选择官方YouTube链接。

## 何时使用此技能

当用户请求以下内容时，使用此技能：
- 从YouTube、SoundCloud、Spotify或其他平台下载音频/音乐
- 从视频中提取音频（MP3、Opus或其他格式）
- 下载整个播放列表或专辑
- 高质量音频，包含元数据和专辑封面
- 批量下载多首歌曲
- 将视频内容转换为音频文件

## 快速入门

**最常见用例 - 从YouTube下载MP3：**
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" "VIDEO_URL"
```

**从Spotify下载：**
```bash
spotdl --audio-quality 320k --embed-metadata --output "{artist}/{title}.{ext}" "SPOTIFY_TRACK_URL"
```

**注意：** 如果遇到问题，尝试通过pip下载或更新yt-dlp：`pip install --upgrade yt-dlp`

## 常用命令

## 列出可用格式
```bash
yt-dlp -F "URL"
```

## 以最高质量下载MP3
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --postprocessor-args "-b:a 320k" -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=xYJki23aeTQ&ab_channel=OnlyRealHipHop49"
```

## 基础高质量MP3下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载自定义比特率
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --postprocessor-args "-b:a 192k" -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载并添加元数据标签
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --embed-metadata -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载整个播放列表
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(playlist_title)s/%(title)s.%(ext)s" "PLAYLIST_URL"
```

## 下载播放列表（特定范围）
```shell
yt-dlp --playlist-items 1-5 -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(playlist_title)s/%(title)s.%(ext)s" "PLAYLIST_URL"
```

## 从SoundCloud下载HQ
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 自动嵌入专辑封面
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --embed-thumbnail --audio-quality 0 -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载特定格式
*Opus代替MP3*
```shell
yt-dlp -f bestaudio --extract-audio --audio-format opus -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 跳过已下载的文件
```shell
yt-dlp --download-archive "downloaded.txt" -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载多个独立文件
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail --write-description --postprocessor-args "-b:a 320k" -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=xYJki23aeTQ&ab_channel=OnlyRealHipHop49" "https://www.youtube.com/watch?v=xKJaew2gMSo&ab_channel=OnlyRealHipHop49" "https://www.youtube.com/watch?v=zLJkO3RnWUk&ab_channel=OnlyRealHipHop49"
```

## 下载并自动按章节分割
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --split-chapters -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 提取视频的一部分（按时间）
```shell
yt-dlp -f bestvideo+bestaudio --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss 00:01:00 -to 00:05:00" -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 更新现有文件的元数据
```shell
yt-dlp --download-archive "downloaded.txt" --skip-download --embed-metadata --embed-thumbnail --write-description "VIDEO_URL"
```

## 自动重命名重复文件
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --force-overwrites -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 从URL列表文件下载
```shell
yt-dlp -a "urls.txt" -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s"
```

## 下载并限制下载速度
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --rate-limit 1M -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 从Vimeo下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Vimeo/%(uploader)s - %(title)s.%(ext)s" "VIMEO_VIDEO_URL"
```

## 从Facebook下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Facebook/%(uploader)s - %(title)s.%(ext)s" "FACEBOOK_VIDEO_URL"
```

## 从Instagram下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Instagram/%(uploader)s - %(title)s.%(ext)s" "INSTAGRAM_VIDEO_URL"
```

## 从Twitter下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Twitter/%(uploader)s - %(title)s.%(ext)s" "TWITTER_VIDEO_URL"
```

## 从TikTok下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "TikTok/%(uploader)s - %(title)s.%(ext)s" "TIKTOK_VIDEO_URL"
```

## 从Reddit下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Reddit/%(uploader)s - %(title)s.%(ext)s" "REDDIT_VIDEO_URL"
```

## 从Dailymotion下载
```shell
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "Dailymotion/%(uploader)s - %(title)s.%(ext)s" "DAILYMOTION_VIDEO_URL"
```

## 下载YouTube字幕为文本
```shell
yt-dlp --write-auto-subs --sub-lang en --skip-download -o "%(title)s.%(ext)s" "VIDEO_URL"
```

## 下载YouTube字幕为Markdown
```shell
yt-dlp --write-auto-subs --sub-lang en --skip-download --convert-subs srt -o "%(title)s.md" "VIDEO_URL"
```

## 下载视频信息并保存为JSON
```shell
yt-dlp --write-info-json --skip-download -o "%(title)s.json" "VIDEO_URL"
```

## 列出可用格式而不下载
```shell
yt-dlp -F "VIDEO_URL"
```

## 下载YouTube受年龄限制的内容
```shell
yt-dlp --username "YOUR_YOUTUBE_EMAIL" --password "YOUR_PASSWORD" -f bestvideo+bestaudio -o "%(title)s.%(ext)s" "AGE_RESTRICTED_VIDEO_URL"
```

---

# SoundCloud命令

## 列出可用格式
```bash
yt-dlp -F "URL"
```

## 从SoundCloud下载高质量MP3
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud下载HQ并嵌入元数据
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --embed-metadata -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud下载整个播放列表
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(playlist_title)s/%(title)s.%(ext)s" "SOUNDCLOUD_PLAYLIST_URL"
```

## 从SoundCloud下载整个播放列表并嵌入元数据
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --embed-metadata --add-metadata --embed-thumbnail -o "%(playlist_title)s/%(title)s.%(ext)s" "SOUNDCLOUD_PLAYLIST_URL"
```

## 下载多个播放列表并嵌入元数据
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --embed-metadata --add-metadata --embed-thumbnail -o "SoundCloud/%(playlist_title)s/%(title)s.%(ext)s" "x" "x" "x" "x" "x" "x" "x"
```

## 下载播放列表（特定范围）
```bash
yt-dlp --playlist-items 1-5 -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(playlist_title)s/%(title)s.%(ext)s" "SOUNDCLOUD_PLAYLIST_URL"
```

## 下载并嵌入专辑封面
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --embed-thumbnail -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 跳过下载已下载的SoundCloud文件
```bash
yt-dlp --download-archive "downloaded_soundcloud.txt" -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud下载多个曲目
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL_1" "SOUNDCLOUD_TRACK_URL_2" "SOUNDCLOUD_TRACK_URL_3"
```

## 限制SoundCloud下载速度
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --rate-limit 1M -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud下载并按章节分割（如果可用）
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --split-chapters -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud下载曲目并提取特定部分
```bash
yt-dlp -f bestaudio --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss 00:01:00 -to 00:05:00" -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 更新现有SoundCloud下载的元数据
```bash
yt-dlp --download-archive "downloaded_soundcloud.txt" --skip-download --embed-metadata --embed-thumbnail "SOUNDCLOUD_TRACK_URL"
```

## 自动重命名重复的SoundCloud文件
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 --force-overwrites -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s" "SOUNDCLOUD_TRACK_URL"
```

## 从SoundCloud URL列表文件下载
```bash
yt-dlp -a "soundcloud_urls.txt" -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 -o "SoundCloud/%(uploader)s - %(title)s.%(ext)s"
```

---

# SpotifyDL命令

## 下载单曲
```bash
spotdl --audio-quality 320k --embed-metadata --output "{artist}/{title}.{ext}" "SPOTIFY_TRACK_URL"
```
## 下载整个播放列表
```bash
spotdl --playlist "SPOTIFY_PLAYLIST_URL" --audio-quality 320k --embed-metadata --output "{playlist}/{title}.{ext}"
```
## 下载整个专辑
```bash
spotdl --album "SPOTIFY_ALBUM_URL" --audio-quality 320k --embed-metadata --output "{album}/{title}.{ext}"
```
## 同时下载多个专辑和播放列表
```bash
spotdl --playlist "SPOTIFY_PLAYLIST_URL1" "SPOTIFY_PLAYLIST_URL2" --audio-quality 320k --embed-metadata --output "{playlist}/{title}.{ext}"
spotdl --album "SPOTIFY_ALBUM_URL1" "SPOTIFY_ALBUM_URL2" --audio-quality 320k --embed-metadata --output "{album}/{title}.{ext}"
```
