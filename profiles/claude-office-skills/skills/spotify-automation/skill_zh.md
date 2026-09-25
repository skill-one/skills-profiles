# Spotify 自动化

自动化 Spotify 音乐播放、播放列表管理和发现工作流程。

## 核心功能

### 播放控制
```yaml
playback_commands:
  - play_track: "spotify:track:xxx"
  - 暂停
  - 下一曲
  - 上一曲
  - 设置音量: 75
  - 设置随机播放: true
  - 设置重复: "上下文"  # 曲目、上下文、关闭
  - 跳转到位置: 30000  # 毫秒
  - 切换播放设备:
      device_id: "device_xxx"
```

### 播放列表管理
```yaml
playlist_operations:
  创建:
    名称: "{{playlist_name}}"
    描述: "{{description}}"
    公开: false
    协作: false
    
  添加曲目:
    playlist_id: "xxx"
    曲目:
      - "spotify:track:xxx"
      - "spotify:track:yyy"
    位置: 0  # 可选
    
  智能播放列表:
    名称: "运动混音"
    标准:
      能量: "> 0.8"
      节奏: "> 120"
      流派: ["电子", "流行"]
    数量: 50
    刷新: 每周
```

### 音乐发现
```yaml
recommendations:
  种子曲目: ["track_id_1", "track_id_2"]
  种子艺人: ["artist_id"]
  种子流派: ["流行", "摇滚"]
  
  目标特征:
    能量: 0.8
    舞动感: 0.7
    情绪: 0.6  # 积极性
    
  数量: 20
```

### 音频分析
```yaml
audio_features:
  - 声学度: 0.0-1.0
  - 舞动感: 0.0-1.0
  - 能量: 0.0-1.0
  - 乐器性: 0.0-1.0
  - 现场感: 0.0-1.0
  - 功率: -60 至 0 dB
  - 语音性: 0.0-1.0
  - 节奏: BPM
  - 情绪: 0.0-1.0 (心情)
  - 调式: 0-11 (C 至 B)
  - 模式: 0 (小调) 或 1 (大调)
```

## 工作流程示例

### 每日混音生成器
```yaml
workflow:
  触发器: 每日 6:00 AM
  步骤:
    - 获取最近播放: 50
    - 分析情绪: 基于音频特征
    - 获取推荐: 
        基于最近播放
        情绪: 当前时间适用
    - 创建播放列表: "今日混音 - {{date}}"
    - 添加曲目: 推荐
```

### 派对模式
```yaml
party_playlist:
  触发器: "派对模式"
  操作:
    - 获取热门曲目:
        时间范围: 中期
        数量: 20
    - 获取推荐:
        种子: 热门曲目
        能量: "> 0.8"
        舞动感: "> 0.7"
    - 随机播放
    - 设置交叉淡入: 5  # 秒
```

## API 示例

```javascript
// 搜索并播放
const results = await spotify.search("Bohemian Rhapsody", ["track"]);
await spotify.play({ uris: [results.tracks.items[0].uri] });

// 创建智能播放列表
const recs = await spotify.getRecommendations({
  seed_genres: ["chill"],
  target_energy: 0.4,
  数量: 30
});
const playlist = await spotify.createPlaylist("Chill Vibes", {
  description: "AI生成的放松曲目",
  公开: false
});
await spotify.addTracksToPlaylist(playlist.id, recs.tracks.map(t => t.uri));
```

## 最佳实践

1. **速率限制**: 尊重 Spotify API 限制
2. **缓存**: 缓存频繁访问的数据
3. **用户授权**: 请求适当的权限范围
4. **降级处理**: 优雅处理不可用曲目
