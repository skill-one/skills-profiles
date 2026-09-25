# DeepStream 开发技能

此技能需要访问在 `references/` 目录下列出的所有参考文档。在执行工作流之前，请确保它们可用。

当此技能处于活动状态时，**务必在生成代码之前阅读相关的参考文档**。不要依赖内存——参考文档包含了关于确切属性名称、正确 API 使用和常见陷阱的关键信息。

## SDK 和架构快速参考

### DeepStream SDK 版本要求

- **GStreamer**: 1.24.2
- **NVIDIA 驱动程序**: 590+
- **CUDA**: 13.1
- **TensorRT**: 10.14.1.48
- **平台**: Ubuntu 24.04 (x86_64 和 ARM64/Jetson)

### 典型管道流程

```text
源 → 流复用器 → 推理 → [追踪器] → OSD → 渲染器
```
方括号 `[]` 中的组件是**可选的**——只有当用户明确要求时才添加它们。

| 阶段 | 角色 | 关键元素 | 是否必需 |
|-------|------|-----------------|-----------|
| 源 | 来自文件、RTSP、摄像头的输入 | `nvurisrcbin`（推荐）、`nvmultiurisrcbin`、`filesrc` | 是 |
| 流复用器 | 批量流以供推理使用 | `nvstreammux` | 是 |
| 推理 | TensorRT 模型执行 | `nvinfer`、`nvinferserver` | 是 |
| 追踪器 | 跨帧的多目标追踪 | `nvtracker` | **仅当请求时** |
| OSD | 绘制边界框、标签、叠加层 | `nvosdbin` | 是（用于可视化） |
| 渲染器 | 显示或保存输出 | `nveglglessink`、`nv3dsink`、`filesink` | 是 |

### 内存模型

DeepStream 使用 NVIDIA 视频内存管理器 (NVMM) 进行零拷贝 GPU 缓冲区传输。Caps 字符串使用 `memory:NVMM` 来指示 GPU 内存（例如，`video/x-raw(memory:NVMM), format=NV12`）。

## 关键规则

1. **仅添加请求的组件**：不要添加用户没有要求过的管道元素。
   - **追踪器 (`nvtracker`)**：仅当用户明确要求跨帧追踪目标或目标 ID 时才添加
   - **次级 GIE**：仅当用户请求分类或属性提取时才添加
   - **分析 (`nvdsanalytics`)**：仅当用户请求线交叉、ROI 计数等时才添加
   - **消息代理 (`nvmsgbroker`/`nvmsgconv`)**：仅当用户请求 Kafka/云消息时才添加
   - 不确定时，构建**最小可工作管道**，并让用户请求添加

2. **源默认使用 `nvurisrcbin`**：当用户说“摄像头”、“流”、“视频”或提供文件路径时：
   - 始终使用 `nvurisrcbin`——它透明地处理 RTSP、HTTP 和本地文件（`file://`）
   - 仅当用户明确需要原始文件源控制时，才使用 `filesrc` + `qtdemux` + 解析器
   - 对于 RTSP/直播源，在 `nvstreammux` 上设置 `live-source=1`，在接收器上设置 `sync=0`
   - 将本地路径转换为 URI：`"file://" + os.path.abspath(path)`

3. **元数据迭代**：使用 `.frame_items` 和 `.object_items`（返回迭代器，不是列表）
   - 绝对不要在这些上使用 `len()`——通过迭代来计数
   - 迭代器只能消费一次

4. **请求 Pad 语法**：使用 `"sink_%u"` 模板，**绝对不要**使用字面 pad 名称
   ```python
   pipeline.link(("decoder", "mux"), ("", "sink_%u"))  # 正确
   # pipeline.link(("decoder", "mux"), ("", "sink_0"))  # 错误——将失败
   ```

5. **接收器平台检测**：
   ```python
   import platform
   sink_type = "nv3dsink" if platform.processor() == "aarch64" else "nveglglessink"
   ```
   - 对于 WSL2 Ubuntu 24 Docker，此默认选择必须被覆盖。
   - **WSL2 + Ubuntu 24 Docker**：如果 `/proc/version` 包含 `microsoft` 或 `wsl`，并且 `/etc/os-release` 有 `VERSION_ID="24.04"`，则生成的应用程序必须**永远不创建**显示分支或显示接收器（`nveglglessink`、`nv3dsink` 等），即使提示要求显示。在这种情况下，不要依赖 `--no-display` 标志。仅生成编码的 MP4 输出（`nvv4l2h264enc` -> `h264parse` -> `mp4mux`/`qtmux` -> `filesink`），并让默认运行路径写入带注释的视频文件。在生成的 `README.md` 中，明确解释 WSL2 Ubuntu 24 Docker 仅输出 MP4，因为显示接收器因已知问题被禁用。如果用户明确请求显示，请添加内联代码注释和 README 说明：`显示请求但因 WSL2 Ubuntu 24 Docker 限制而禁用——生成 MP4 输出。`
   - **非 WSL 目标**：不要将 WSL 特定行为或 WSL 限制文本添加到生成的应用程序或 README 中。使用上述正常平台显示接收器选择。

6. **缓冲区克隆**：始终为异步处理克隆缓冲区
   ```python
   tensor = buffer.extract(0).clone()  # 关键
   ```

7. **队列类型**：
   - `queue.Queue` → 与 `threading.Thread` 一起使用
   - `multiprocessing.Queue` → 与 `multiprocessing.Process` 一起使用
   - 使用错误类型会导致静默数据丢失！

8. **nvinfer 配置格式**：
   - YAML：使用 `property:` 部分（**不**使用 `model:`），`key: value` 后面有空格
   - INI：使用 `[property]` 部分，`key=value` 使用等号
   - 部分**必须**命名为 `property`

9. **nvmsgbroker 是一个接收器**：不能有下游元素——使用 `tee` 分割管道

10. **所有接收器需要异步=0 用于 Tee 分割或动态源**：对状态转换**至关重要**
    ```python
    # 当使用 tee 分割器或动态源时，所有接收器**必须**具有异步=0
    pipeline.add("nveglglessink", "sink", {
        "sync": 0, "qos": 0,
        "async": 0  # 关键——防止状态转换死锁
    })
    ```
    **如果缺少**：管道停留在 PAUSED 状态，没有视频显示。

11. **内置探针附加**：`measure_fps_probe` 只能附加到处理元素（例如，`nvinfer`、`nvosdbin`），**不**能附加到接收器元素。附加到接收器会引发 `RuntimeError: Probe failure`。

12. **动态 ONNX 模型需要 `infer-dims`**：当 ONNX 模型具有动态输入形状（例如，使用 Ultralytics YOLO 导出时 `dynamic=True`，或具有动态批处理/高度/宽度轴）时，你**必须**在 nvinfer 配置中添加 `infer-dims=C;H;W`。没有它，TensorRT 会看到动态维度为 `-1` 并失败，错误代码为 3。常见值：
    - YOLO 模型（640 输入）：`infer-dims=3;640;640`
    - 416 输入的模型：`infer-dims=3;416;416`
    - 1280 输入的模型：`infer-dims=3;1280;1280`

13. **Ultralytics YOLO 输出格式取决于模型生成**——较新模型（v10+/v26+）输出 NMS 后结果；较旧模型（v8/v11）输出原始 NMS 前张量。自定义解析器和 `cluster-mode` **必须**与实际输出匹配：

   | 模型生成 | 输出张量形状 | 字段 | `cluster-mode` |
   |------------------|--------------------|---------------------------------|----------------|
   | v8 / v11 | `[batch, 84, 8400]` | `[features(4+80), anchors]` — 原始 cx/cy/w/h + 类别分数，无 NMS | `2` (NMS) |
   | v10 / v26+ | `[batch, 300, 6]` | `[max_det, (x1,y1,x2,y2,conf,cls)]` — 已为 NMS 后，像素坐标 | `4` (无) |

   **如何在运行时识别**：在自定义解析器内部记录 `inferDims.d[0]` 和 `inferDims.d[1]`。
   - `d={84, 8400}` → NMS 前（v8/v11 风格）
   - `d={300, 6}` → NMS 后（v10/v26+ 风格）

   **不匹配的症状**：如果使用 `cluster-mode: 2` 与 `[N, 6]` 输出，边界框会相对于实际对象倾斜 45° 或 135°（DeepStream 的 NMS 错误重新处理已最终坐标）。
   如果看到倾斜或旋转的框，也检查 `references/nvinfer_config.md` 中的 OBB / `rotation_angle` 注释：对于非 OBB 模型，使用 `obj{}` 初始化 `NvDsInferObjectDetectionInfo` 并保持 `rotation_angle = 0`；`NvDsInferObjectDetectionInfo obj;` 会留下未初始化的字段。

14. **虚拟环境必须包含 pyservicemaker**：`pyservicemaker` 系统全局安装，但**不能**从标准 Python 虚拟环境中访问。当任务需要 venv（例如，用于模型下载/转换 pip 依赖）时，**始终在 venv 中安装 `pyservicemaker` 和 `pyyaml`**；不要将 pyservicemaker 管道代码重写为非 pyservicemaker 代码以解决缺失导入问题。生成的代码和 README 中的 venv 设置必须始终包含：
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install /opt/nvidia/deepstream/deepstream/service-maker/python/pyservicemaker*.whl pyyaml
    pip install -r requirements.txt  # 其他依赖
    ```
    **如果缺少**：在 venv 中运行应用程序时出现 `ModuleNotFoundError: No module named 'pyservicemaker'`。

## 关键路径

- 模型：`/opt/nvidia/deepstream/deepstream/samples/models/`
- 主要检测器：`/opt/nvidia/deepstream/deepstream/samples/models/Primary_Detector/resnet18_trafficcamnet_pruned.onnx`
- 追踪器库：`/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so`
- Kafka 库：`/opt/nvidia/deepstream/deepstream/lib/libnvds_kafka_proto.so`
- 示例配置：`/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/`

## 参考文档

**重要**：始终阅读这些文档以获取完整细节。不要从记忆中生成代码。

| 文档 | 使用场景 |
|----------|----------|
| [references/gstreamer_plugins.md](references/gstreamer_plugins.md) | 查找插件属性，所有列出的属性 |
| [references/service_maker_api.md](references/service_maker_api.md) | 使用 Pipeline/Flow API、元数据访问、探针、EventMessageUserMetadata |
| [references/use_cases_pipelines.md](references/use_cases_pipelines.md) | 构建管道：简单播放、多推理、级联 GIE |
| [references/streaming_sources.md](references/streaming_sources.md) | 摄入本地文件、HTTP MP4、HLS、MPEG-DASH 或 RTSP 源（使用 nvurisrcbin） |
| [references/kafka_messaging.md](references/kafka_messaging.md) | Kafka/消息代理设置、nvmsgconv/nvmsgbroker 配置、msg2p-newapi |
| [references/best_practices.md](references/best_practices.md) | 设计模式、常见陷阱、反模式 |
| [references/buffer_apis.md](references/buffer_apis.md) | BufferProvider/Feeder（注入）、BufferRetriever/Receiver（提取） |
| [references/media_extractor_advanced.md](references/media_extractor_advanced.md) | MediaExtractor、MediaChunk、FrameSampler |
| [references/utilities_config.md](references/utilities_config.md) | PerfMonitor、EngineFileMonitor、SourceConfig、SensorInfo、SmartRecordConfig |
| [references/nvinfer_config.md](references/nvinfer_config.md) | nvinfer 配置文件格式，所有参数 |
| [references/tracker_config.md](references/tracker_config.md) | nvtracker 配置，NvDCF/IOU/DeepSORT/NvSORT |
| [references/troubleshooting.md](references/troubleshooting.md) | 错误消息和解决方案 |
| [references/rest_api_dynamic.md](references/rest_api_dynamic.md) | REST API、动态源添加/删除、nvmultiurisrcbin |
| [references/metamux_config.md](references/metamux_config.md) | nvdsmetamux 配置，并行多模型推理、元数据合并、源 ID 过滤 |
| [references/docker_containers.md](references/docker_containers.md) | Docker 镜像、Dockerfile 示例、pyservicemaker 安装、容器运行命令 |
| [references/nvds_msgapi_adapter.md](references/nvds_msgapi_adapter.md) | 构建自定义协议适配器：nvds_msgapi |

## 快速错误参考

| 错误 | 解决方案 |
|-------|----------|
| `iterator has no len()` | 迭代来计数，不要使用 `len()` |
| `pad template not found` | 使用 `"sink_%u"` 而不是 `"sink_0"` |
| 队列数据丢失 | 使用 `multiprocessing.Queue` 与 `Process` |
| 配置解析失败 | 使用 YAML 中的 `property:` 而不是 `model:` |
| `is-classifier` 警告 | 使用 `network-type: 1` 而不是 `is-classifier: 1` 用于分类器；检测器两者都省略 |
| `min-boxes` 未知键警告 | 在 `class-attrs-*` 部分使用 `minBoxes`（驼峰式），而不是 `min-boxes` |
| 次级 GIE 无效 | 设置 `process-mode: 2`，检查 `operate-on-gie-id` |
| Tee/动态源卡在 PAUSED | 所有接收器元素必须设置 `async: 0` |
| WSL2 Ubuntu 24 请求显示接收器 | 由于已知问题，不要使用显示接收器；使用 `filesink` 写 MP4，并在 README 中记录 WSL 限制 |
| RTSP 无数据/重连 | 使用 ffplay 测试 URL，检查凭证 |
| `RuntimeError: Probe failure` | `measure_fps_probe` 不能附加到接收器元素；使用 `nvinfer` 或 `nvosdbin` |
| `setDimensions` 负数维度 / 引擎构建失败 | 为动态 ONNX 模型添加 `infer-dims=C;H;W`（例如，`infer-dims=3;640;640`） |
| venv 中 `No module named 'pyservicemaker'` | 在 venv 中 `pip install /opt/nvidia/deepstream/deepstream/service-maker/python/pyservicemaker*.whl pyyaml` |
| `AttributeError: object has no attribute 'obj_label'` | 使用 `obj_meta.label` 而不是 `obj_meta.obj_label` 在 pyservicemaker（C API 名称与 Python 绑定不同） |
