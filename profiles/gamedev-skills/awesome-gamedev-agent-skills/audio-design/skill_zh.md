# 音频设计

游戏音频是一个**混音图加上一个音乐系统**。将每个声音路由到一小组总线中，以便你可以平衡和处理分组；让音乐*响应对*应，通过分层和重新排序而不是循环一个音轨。这项技能用于便携式练习；将其绑定到 `godot-audio`、Unity 的 AudioMixer 或中间件（FMOD/Wwise）以获取具体的 API。

## 何时使用

- 用于设计总线/混音器布局，设置分组音量，并将混响、压缩、均衡器等效果应用于声音分组。
- 用于在对话或冲击（侧链）下降低音乐/环境音。
- 用于构建响应战斗/探索强度的自适应音乐。
- 用于添加 SFX 变化（音高/采样随机化）并将事件同步到节拍。

**不使用时**：对于引擎的具体音频节点/流，使用 `godot-audio` 或引擎的音频技能。加载/流式传输和资源导入是引擎的职责。对于驱动总线音量的 UI 滑块，请参阅引擎 UI 技能。

## 核心工作流程

1. **布局总线，而不是每个声音的音量**。一个典型的树状结构：`Master ← {Music, SFX, Ambience, UI, Voice}`。所有声音都播放到总线中；玩家的设置滑块映射到总线音量。切勿手动设置数百个片段音量。
2. **使用分贝而不是线性**。感知的响度是指数级的。音量控制和自动化应在 dB 范围内操作；仅在边缘进行转换。
3. **留出余量**。混音时，主控峰值应低于 0 dBFS（目标响度，例如许多游戏约为 -14 到 -16 LUFS）以避免削波。
4. **使用侧链压缩器（或音量自动化）降低竞争源**：当语音/重要 SFX 播放时，音乐总线会下降，然后恢复。
5. **通过*垂直*分层（音轨淡入淡出）和/或*水平*重新排序（在音乐边界处交换片段）使音乐自适应**。参见参考。
6. **通过小的随机音高/音量偏移和采样池使重复的 SFX 变化，以便脚步声和打击声不会听起来像机器人**。
7. **在真实输出上验证**。通过耳机和扬声器进行监听；检查混音是否平衡，降低音量是否可听但不会泵动，音乐转换是否落在节拍上——不要仅凭编辑器计量表就假设。

## 模式

### 1. 总线路由和 dB 增益

```gdscript
# 将声音路由到命名总线；控制分组，而不是单个片段。
sfx_player.bus = "SFX"
music_player.bus = "Music"

# 将 0..1 设置滑块映射到分贝（linear_to_db），感知单位。
func set_bus_volume(bus_name: String, slider01: float) -> void:
    var idx := AudioServer.get_bus_index(bus_name)
    var db := linear_to_db(clamp(slider01, 0.0001, 1.0))   # 0 -> 沉默, 1 -> 0 dB
    AudioServer.set_bus_volume_db(idx, db)
# 正确：滑块 -> dB 通过 linear_to_db。错误：直接将 slider01 作为 dB 分配
# （"0.5" 将是仅 +0.5 dB——几乎无变化——而 0 将是 0 dB，全音量）。
```

### 2. 通过侧链降低音量（音乐在语音下降低）

```gdscript
# MUSIC 总线上的压缩器，以 VOICE 总线为键，在对话播放时降低音乐，然后释放。这是“侧链降低音量”。
# 设置（特定于引擎）：向音乐总线添加一个压缩器效果，并将其侧链设置为语音总线。然后调整：
#   阈值：触发降低音量的语音电平（例如 -30 dB）
#   比率：降低音量的强度（例如 8:1 以获得清晰的下降）
#   攻击：快速（~10 ms）以便音乐迅速让路
#   释放：慢速（~300-500 ms）以便平稳恢复，而不是泵动
# 无中间件替代方案：在语音开始时降低音乐总线音量，在语音结束时恢复。
func duck_music(active: bool) -> void:
    var target_db := -12.0 if active else 0.0
    create_tween().tween_method(
        func(v): set_bus_volume_db("Music", v), current_music_db, target_db, 0.25)
```

### 3. SFX 变化（消除“机枪”重复）

```gdscript
# 稍微随机化音高并从采样池中挑选，使重复感觉更自然。
func play_varied(samples: Array, bus := "SFX") -> void:
    var p := AudioStreamPlayer.new()
    p.stream = samples[randi() % samples.size()]   # 旋转多个录音
    p.bus = bus
    p.pitch_scale = randf_range(0.94, 1.06)         # +/- ~6% 音高波动
    add_child(p); p.play()
    p.finished.connect(p.queue_free)                # 清理一次性播放器
```

### 4. 节拍同步事件（量化到音乐网格）

```gdscript
# 在音乐时间而不是帧时间上安排游戏/视觉效果，以便它们落在节拍上。
const BPM := 120.0
var seconds_per_beat := 60.0 / BPM

func current_beat(playback_position_sec: float) -> int:
    return int(playback_position_sec / seconds_per_beat)

# 将动作量化到下一个节拍边界，而不是立即触发。
func time_until_next_beat(pos: float) -> float:
    return seconds_per_beat - fmod(pos, seconds_per_beat)
# 从音频播放时钟驱动时间，它比帧增量更稳定。
```

## 陷阱

- **将滑块值视为 dB**。音量是指数级的；通过 `linear_to_db` 映射 `0..1`（并使用 `db_to_linear` 反转）。原始振幅上的线性滑块在底部之前几乎感觉不到变化。
- **每个片段的音量而不是总线** 使全局平衡检查变得不可能并使保存/设置膨胀。在总线上混音。
- **主控削波**。汇总的声音超过 0 dBFS 并失真。留出余量；将限制器放在主控上作为安全网，而不是混音器。
- **泵动降低音量**：释放太快或比率太高会使音乐可听地呼吸。延长释放时间；降低比率。
- **整个游戏循环单个音乐轨道** 感觉很平淡。使用层或响应状态的片段（参见参考）。
- **节拍同步偏离帧时间**。`delta` 漂移；读取**音频播放位置**以获取音乐时间，并考虑输出延迟。
- **无限制的一次性播放器**：没有释放它们而创建的 AudioStreamPlayers 会泄漏。在 `finished` 时释放，或使用一个小型池。

## 参考

- `references/adaptive-music.md` — 垂直分层与水平重新排序、过渡时间（小节/量化）、Stingers、强度映射和交叉淡入淡出。

## 相关技能

- `godot-audio` — 总线、`AudioStreamPlayer`、效果和在 Godot 中同步到节拍。
- `input-systems` — 从输入动作触发音频。
- `physics-tuning` — 驱动冲击 SFX 的碰撞事件。
- `platformer`, `roguelike` — 依赖音频反馈来营造感觉的游戏类型。
