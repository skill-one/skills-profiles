## 严重规则

- 报告发现结果之前，不要进行任何更改
- 严格按步骤执行，不要跳过
- 在每个 `WAIT` 检查点停止，并等待用户响应后再继续
- 质量比速度更重要：在每次更改前后进行测量
- 始终在设备构建中验证结果；编辑器音频统计信息仅供参考

## 0. 设置执行路径

下面的每个 C# 步骤都在通过 Unity CLI 在实时编辑器中运行。**`unity-cli` 技能负责带你到达那里**——安装 CLI、确认连接的编辑器、添加项目的 `com.unity.pipeline` 包、区分真正的缺失编辑器与处于安全模式的编辑器，以及发现编辑器的命令目录。首先遵循它，不要在这里重新推导任何内容。

有两件事它无法为你知道：

- **你需要 `eval`，而不仅仅是可访问的编辑器**。确认它出现在目录中。它的存在取决于 Pipeline 包版本，而不是 CLI，因此即使安装健康，它也可能缺失——如果缺失，请说明并停止。
- **不要手动编辑 `.meta` 文件来更改导入设置**。导入器值仅通过实时编辑器中的 `SaveAndReimport()` 生效，因此无法访问的编辑器是一个停止信号，而不是直接编辑元数据的提示。

使用 `unity command eval --code '<snippet>'` 运行 C#。从 `unity command --format json` 而不是假设一个来发现参数形状。`unity command` 默认超时时间为 30 秒。

### 将 C# 传递给 `eval`

`eval` 编译一个**语句块，而不是文件**。有两个后果，两者都会导致编译错误而不是警告：

- **没有 `using` 指令**。编译器将 `using UnityEngine;` 读取为资源释放语句并拒绝它 (`CS0210`)。
- **类型必须完全限定**。裸 `AssetDatabase` 或 `AudioImporter` 无法解析 (`CS0246` / `CS0103`)，而裸 `Object` 与 `object` 混淆 (`CS0104`)。

[resources/audio-import-api.md](resources/audio-import-api.md) 中的配方是完全限定的，因此可以原样传递给 `eval`。

## 1. 预检查：检测音频系统

在执行任何其他操作之前，建立音频环境：

1. **检测平台和采样率**：使用 `eval` 读取 `EditorUserBuildSettings.activeBuildTarget` 和 `AudioSettings.outputSampleRate`。输出采样率会影响是否覆盖剪辑采样率实际上会节省内存。
2. **检测 AudioMixer 的存在**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的混音器资产查询配方，查看是否存在混音器图。如果不存在，则注意路由和效果成本不是问题。
3. **检测 AudioListener**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的场景组件查询配方，用于 `UnityEngine.AudioListener`，以确认正好有一个监听器存在。多个监听器会产生不正确的空间化；零个监听器会产生静音。
4. **仅当平台和监听器状态确认后，才继续**。

## 2. 评估当前状态

在推荐任何更改之前，收集可观察的数据：

1. **查找所有 AudioSources**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的场景组件查询配方，用于 `UnityEngine.AudioSource`。对于每个结果，使用 **一个** `eval` 调用来批量读取属性——参见 [resources/audio-import-api.md](resources/audio-import-api.md) 中的批量读取配方。
2. **检查混音器拓扑结构**：如果在预检查中找到混音器，使用 `eval` 读取 AudioMixer 的暴露参数和组数量。组数量超过 ~8 或主组上的效果是立即的标志。
3. **检查 DSP 缓冲区大小**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的 DSP 缓冲区配方来读取缓冲区大小。参见 [resources/platform-settings.md](resources/platform-settings.md) 中的 DSP 缓冲区大小指南，以获取推荐值。
4. **在更改之前报告发现结果**：向用户总结所有检测到的源、监听器数量和混音器深度。标记任何立即的风险（例如，立体声剪辑具有 `spatialBlend = 1`，大于 1 MB 的剪辑上的 Decompress On Load，主组上的混响）。

**等待用户审查评估后再继续。**

## 3. 理解请求

根据用户需要，路由到正确的部分：

| 用户说 | 路径 |
|-------|------|
| "音频内存过高" / "内存分析器显示音频" | 第 4 节 — 导入设置审核 |
| "加载时间慢" / "解压缩停滞" | 第 4 节 — 加载类型审查 |
| "DSP 峰值" / "混音器 CPU" / "音频 CPU 高" | 第 4B 节 — 混音器审核 |
| "3D 声音错误" / "只有左声道播放" / "3D 立体声" | 第 4A 节 — 强制转为单声道 + 空间设置 |
| "质量伪影" / "声音听起来很糟糕" / "Vorbis 嘶嘶声" | 第 4C 节 — 压缩质量调整 |
| "移动音频电池" / "移动内存" | 第 4D 节 — 移动采样率覆盖 |
| "在所有剪辑上设置导入设置" / "批量音频设置" | 第 4 节 — 批量导入审核 |
| "流式传输" / "后台加载" / "Addressables 音频" | 第 4E 节 — 流式传输和异步加载 |

如果症状不明确，请询问："问题是音频内存使用、DSP CPU 峰值还是音频播放质量？"

## 4. 主要诊断工作流程

使用第 2 节的发现来确定哪个子部分适用。可能同时适用多个。

### 4A. 强制转为单声道和空间设置

对于任何 `spatialBlend > 0`（3D 定位声音）的 AudioSource：

1. **检查剪辑通道数**：使用 `eval` 读取 `audioSource.clip.channels`。如果 `channels == 2` 且 `spatialBlend == 1`，则只有左声道播放——这是一个错误，而不是功能。
2. **推荐强制转为单声道**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的读取导入器配方来检查当前设置，然后使用强制转为单声道配方应用。
3. **应用并重新导入**：向用户报告更改前后的通道数。
4. **验证空间混合**：使用 `eval` 确认 `audioSource.spatialBlend` 是 `1.0`（全 3D）并且 `audioSource.rolloffMode` 设置为适当的曲线。

### 4B. 音频混音器审核

1. **测量组深度**：使用 `eval` 遍历混音器的组树并计数层级。超过 3 层级（主组 → SFX / 音乐 / 对话 → 子总线）每帧都会增加路由开销，即使子级处于静音状态。
2. **检查静音组上的效果**：使用 `eval` 查询每个组的效果列表。例如 `AudioReverbFilter` 即使没有 AudioSource 路由到该组也会以全成本运行其 DSP。
3. **标记主组上的 SFX 混响**：这是最昂贵的内置效果。如果它在主组或高级组上找到，请明确标记。
4. **向用户呈现建议**：
   - 删除或绕过没有活动源的组的任何效果。
   - 使用 **快照** 切换混音状态（战斗 / 探索 / 暂停），而不是在运行时切换效果。
   - 展平不必要的子总线；将源重定向到更浅的祖先。

   **等待用户批准混音器更改后再应用。**
5. **验证 DSP 缓冲区大小**：如果预检查中的 `bufferLength` 非常小（< 256），建议增加它——参见 [resources/platform-settings.md](resources/platform-settings.md) 中的 DSP 缓冲区大小指南。

### 4C. 压缩质量调整

1. **读取当前压缩格式**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的读取导入器配方来读取用户报告的剪辑的 `compressionFormat` 和 `quality`。
2. **应用平台矩阵**：参见 [resources/platform-settings.md](resources/platform-settings.md) 中的压缩格式矩阵，以获取每个平台的建议。
3. **警告有损源**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的有损源检查配方。如果原始文件是 MP3，请警告用户 Unity 重新编码后永久丢失有损源质量。建议 WAV 或 AIFF 源。

### 4D. 移动采样率覆盖

1. **识别移动目标上的 SFX 剪辑**：使用场景组件查询配方，用于 `UnityEngine.AudioSource`，并过滤非音乐、非对话剪辑。
2. **读取当前采样率设置**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的读取导入器配方来读取每个剪辑的 `sampleRateSetting` 和 `sampleRateOverride`。
3. **应用移动覆盖**：使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的采样率覆盖配方。参见 [resources/platform-settings.md](resources/platform-settings.md) 中的每个用例速率，以获取建议。
4. **报告节省**：将采样率减半会减半 PCM 内存成本。报告每个更改剪辑的估计节省。

### 4E. 加载类型和流式传输

1. **审核每剪辑的加载类型**：使用 `eval` 读取第 2 节中找到的每个剪辑的 `clip.loadType`。
2. **应用决策规则**：参见 [resources/platform-settings.md](resources/platform-settings.md) 中的加载类型决策表。
3. **标记不匹配**：参见 [resources/platform-settings.md](resources/platform-settings.md) 中的加载类型不匹配标志。向用户报告两种类型的冲突。
4. **对任何流式传输剪辑应用 `Load In Background`**——使用 [resources/audio-import-api.md](resources/audio-import-api.md) 中的加载后台配方。

## 5. 验证

在每次导入设置或混音器更改后：

1. **重新读取剪辑统计信息**：使用 `eval` 重新读取 `clip.loadType`、`clip.channels`、`AudioSettings.outputSampleRate` 和导入器的 `compressionFormat`，以确认更改在重新导入后已应用。
2. **确认 AudioSource 路由**：使用场景组件查询配方，用于 `UnityEngine.AudioSource`，并验证 `audioSource.outputAudioMixerGroup` 在任何混音器重构后是否按预期分配。
3. **报告差异**：声明每个更改设置的值。不要假设更改有效，除非读取回应用的导入器值。
4. **迭代限制**：最多 3 次调整和验证循环后暂停，以征求用户反馈。

## 6. 故障排除

### 3D AudioSource 上的立体声剪辑——只有左声道可听

1. 确认 `audioSource.spatialBlend == 1`。
2. 确认 `audioSource.clip.channels == 2`。
3. 在剪辑导入器中启用 `forceToMono` 并重新导入。Unity 在导入时将两个通道混合为单声道，保留 `normalize = true`（保持开启）的级别。
4. 如果用户不想重新导入：将 `audioSource.panStereo = 0` 作为运行时解决方案设置，但警告这不会恢复立体声信息。

### Decompress On Load 剪辑导致内存峰值

1. 确认 `clip.loadType == AudioClipLoadType.DecompressOnLoad` 且 `clip.length` 很长（> 5 秒）。
2. 如果是音乐或环境音，切换到 `Streaming`；如果偶尔播放，切换到 `CompressedInMemory`。
3. 如果剪辑很短但仍然很大：检查 `clip.channels`（立体声会浪费双倍内存）和 `clip.frequency`（在移动目标上高采样率会浪费内存）。应用强制转为单声道和/或采样率覆盖。

### 音频混音器 CPU 峰值——DSP 线程过热

1. 使用混音器资产查询配方确认混音器图存在。
2. 使用 `eval` 列出所有组及其附加效果。查找高级组上的混响、合唱或 EQ。
3. 将昂贵的效果向下移动到仅在源播放时活动的叶组。
4. 在游戏状态（例如，在菜单期间绕过混响）中不听到它们时使用快照绕过效果链。
5. 如果 DSP 缓冲区很小（64 或 128 个样本），请增加它——参见 [resources/platform-settings.md](resources/platform-settings.md) 中的 DSP 缓冲区大小指南。

### 对话中的 Vorbis 质量伪影

1. 确认 `defaultSampleSettings.compressionFormat == AudioCompressionFormat.Vorbis`。
2. 确认 `defaultSampleSettings.quality`——默认值为 0.5，通常在语音中可听。提高到 0.7–0.85。
3. 在 iOS 上：切换到 AAC 而不是 Vorbis（硬件解码，在等效比特率下质量更好）。
4. 确认源文件是无损的（WAV 或 AIFF）。MP3 源无法恢复 Unity 重新编码前丢失的质量。

### AudioListener 数量不是正好一个

- **零个监听器**：所有音频都将静音。使用 `eval` 将 `AudioListener` 组件添加到主摄像机：`UnityEngine.Camera.main.gameObject.AddComponent<UnityEngine.AudioListener>()`。
- **多个监听器**：Unity 使用最后启用的一个，产生不可预测的空间化。使用场景组件查询配方，用于 `UnityEngine.AudioListener`，并禁用所有但预期的那个。

### `Load In Background` 导致首次播放静音

这是预期行为：剪辑在首次调用 `Play()` 时尚未完成加载。通过以下方式缓解：

1. 在场景启动时通过在需要之前调用 `clip.LoadAudioData()` 来预加载剪辑。
2. 使用 `AudioSource.PlayScheduled()` 并带有一点延迟，以允许异步加载完成。
3. 对于必须立即播放的 AudioSource：切换到 `CompressedInMemory`（首次播放同步）而不是 `Streaming` 与后台加载。

## 7. 完成

完成审核或优化后：

- 总结每个更改设置的值，包括更改前后的值。
- 列出仍需关注的任何剪辑或组（例如，需要设备测量以确认节省的剪辑）。
- 如果用户需要运行时内存测量，请指向内存分析器包，该包按运行时字节成本报告最大的 AudioClips。
- 如果审核后混音器 CPU 仍然很高，请指向 Unity Profiler 的音频模块，以进行 DSP 线程分析。

## 详细参考

- **平台设置、压缩矩阵、加载类型、采样率**：[resources/platform-settings.md](resources/platform-settings.md)
- **AudioImporter API 配方和代码模式**：[resources/audio-import-api.md](resources/audio-import-api.md)

## 参见

- **内存分析器包**——按运行时字节成本找到最大的 AudioClips。
- **Unity Profiler，音频模块**——DSP CPU 标记和帧时间预算。
- `audio-setup-mixers`——创建混音器并将 AudioSource 路由到组中。
