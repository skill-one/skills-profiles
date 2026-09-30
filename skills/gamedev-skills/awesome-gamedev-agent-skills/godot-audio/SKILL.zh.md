---
name: godot-audio
description: 在 Godot 4.7 中播放和混合音频：AudioStreamPlayer（2D/3D 变体）、带音量/静音和效果的音频总线、音乐与音效路由、分贝/线性音量以及精确的同步到节拍播放时机。用于在 Godot 项目中播放声音或音乐、将 AudioStreamPlayer 节点路由到总线、通过 AudioServer 调整总线音量，或同步游戏到节拍。
---

# Godot 音频 (4.x)

播放音效和音乐，将它们路由到总线，以分贝控制音量，并使游戏进程与节奏同步。目标为 **Godot 4.7**。

## 何时使用

- 播放音效或音乐时使用，将音频路由到总线（主音/Music/音效），从代码中调整音量/静音，添加总线效果（混响/压缩器），定位3D音频，或将事件与音乐同步。

**不使用时**：引擎无关的音频*设计*（自适应音乐结构、混音理念、压低模式）→ `audio-design`；在Godot外部导入/编码资源。

## 核心工作流程

1. **选择播放节点**：
   - `AudioStreamPlayer` — 非定位（音乐、UI、全局音效）。
   - `AudioStreamPlayer2D` / `AudioStreamPlayer3D` — 定位；音量/声像随距离变化。
2. **将 `AudioStream` 分配给 `stream`**（音乐/循环使用 `.ogg`，短音效使用 `.wav`）并 `play()`。为在场景中启动的音乐设置 `autoplay`。
3. **路由到总线**。将播放器的 `bus` 设置为命名总线（例如 `"Music"`、`"SFX"`）。在音频面板（底部停靠）中定义总线；每个总线都可以有音量、静音、独奏和效果。
4. **以分贝控制音量**，而不是线性（音频是指数级的）。`0 dB` = 不变，`-80 dB` ≈ 静音。使用 `linear_to_db`/`db_to_linear` 进行转换。
5. **通过 `AudioServer` 从代码中控制音量/静音**，使用总线索引。
6. **对于节奏**，使用输出延迟补偿计算精确的播放时间。

## 模式

### 1. 单次触发音效（一触即发）

```gdscript
@onready var sfx: AudioStreamPlayer = $Sfx   # 在编辑器中分配流

func play_jump() -> void:
    sfx.pitch_scale = randf_range(0.95, 1.05)   # 轻微变化可避免疲劳
    sfx.play()

# 对于许多重叠的副本，使用具有
# `AudioStreamPolyphonic` 流的 `AudioStreamPlayer`，或生成短命的播放器并在 `finished` 时释放。
```

### 2. 通过 `AudioServer` 设置总线的音量和静音

```gdscript
func set_music_volume(linear_0_to_1: float) -> void:
    var bus := AudioServer.get_bus_index("Music")
    # 将 0..1 滑块转换为分贝；钳位可避免在 0 时出现 -inf。
    AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(linear_0_to_1, 0.0001)))

func toggle_sfx(muted: bool) -> void:
    AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), muted)
```

### 3. 在两个音乐轨道之间交叉淡入淡出

```gdscript
@onready var a: AudioStreamPlayer = $MusicA
@onready var b: AudioStreamPlayer = $MusicB

func crossfade_to(stream: AudioStream, secs := 1.5) -> void:
    b.stream = stream
    b.volume_db = -40.0
    b.play()
    var tw := create_tween().set_parallel(true)
    tw.tween_property(a, "volume_db", -40.0, secs)   # 淡出当前
    tw.tween_property(b, "volume_db", 0.0, secs)     # 淡入下一个
    tw.chain().tween_callback(a.stop)
    var tmp := a; a = b; b = tmp                      # 交换角色
```

### 4. 精确的节奏同步（补偿输出延迟）

```gdscript
@onready var music: AudioStreamPlayer = $Music

func get_playback_time() -> float:
    # 添加自上次音频混音以来的时间，减去输出延迟，以实现亚帧精度。
    var t := music.get_playback_position() + AudioServer.get_time_since_last_mix()
    return t - AudioServer.get_output_latency()
```

## 陷阱

- **将音量视为线性**。`volume_db`/`set_bus_volume_db` 是分贝。设置 `volume_db = 0.5` 是接近最大音量，而不是一半。使用 `linear_to_db` 映射滑块。
- **`linear_to_db(0.0)` 是 `-inf`**。在转换前将线性值钳位到一个小的最小值（例如 `0.0001`），或特殊处理 0 → 静音。
- **总线名称拼写错误会导致静默失败**。`get_bus_index("Muisc")` 返回 `-1`；调用将出错或无操作。与音频面板中的确切总线名称匹配。
- **短音效在重新触发时被截断**。使用单独的播放器、`AudioStreamPolyphonic` 或每个音效的 `AudioStreamPlayer` 并在 `finished` 时释放。
- **音乐不循环**，除非导入/流循环被启用（`.ogg` 导入有循环选项；`AudioStreamWAV` 有 `loop_mode`）。
- **仅使用 `get_playback_position()` 同步会抖动** — 它按音频混音更新，而不是按帧更新；添加 `get_time_since_last_mix()` 并减去 `get_output_latency()`。
- **3D 音频听不到** → 没有 `AudioListener3D`/`Camera3D` 来听到它，或 `max_distance`/衰减太紧，或总线被静音。

## 参考

- 对于总线布局（`.tres`）、添加效果（混响/压缩器/EQ）和侧链压低、`AudioStreamPolyphonic`/`AudioStreamInteractive`、麦克风捕获，以及使用 `AudioStreamGenerator` 的程序化音频，请参阅 `references/buses-and-effects.md`。

## 相关技能

- `audio-design` — 引擎无关的自适应音乐、混音和压低练习。
- `godot-animation` — 将动画/Tween 同步到 `get_playback_position()`。
- `godot-ui-control` — 音量滑块连接到 `AudioServer`。
