# ComfyUI API 技能

连接到 ComfyUI 的 REST API 以执行工作流、监控进度并获取输出。

## 配置

- **默认 URL**: `http://127.0.0.1:8188`
- **自定义 URL**: 在项目清单中设置或作为参数传递
- **超时**: API 调用 30 秒，生成轮询无超时

## 两种模式

### 在线模式（ComfyUI 运行）

完整 API 访问权限。交互式工作的首选模式。

1. **测试连接**: `GET /system_stats`
2. **发现功能**: 使用 `comfyui-inventory` 技能
3. **排队工作流**: `POST /prompt`
4. **轮询结果**: 每 5 秒 `GET /history/{prompt_id}` 一次
5. **获取输出**: `GET /view?filename=...`

### 离线模式（无服务器）

导出工作流 JSON 以在 ComfyUI 中手动加载。

1. 按照 ComfyUI 的格式生成工作流 JSON
2. 保存到 `projects/{project}/workflows/{name}.json`
3. 指示用户拖拽到 ComfyUI 中

## API 操作

### 检查服务器状态

```bash
curl http://127.0.0.1:8188/system_stats
```

**响应字段:**
- `system.os`: 操作系统
- `system.comfyui_version`: 版本字符串
- `devices[0].name`: GPU 名称
- `devices[0].vram_total`: 总 VRAM 字节
- `devices[0].vram_free`: 可用 VRAM 字节

### 排队工作流

```bash
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": WORKFLOW_JSON, "client_id": "video-agent"}'
```

**WORKFLOW_JSON 格式:**
```json
{
  "1": {
    "class_type": "LoadCheckpoint",
    "inputs": {
      "ckpt_name": "flux1-dev.safetensors"
    }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "photorealistic portrait...",
      "clip": ["1", 1]
    }
  }
}
```

每个节点由字符串 ID 键控。输入引用其他节点为 `["{node_id}", {output_index}]`。

**响应:**
```json
{"prompt_id": "abc-123-def", "number": 1}
```

### 轮询完成状态

```bash
curl http://127.0.0.1:8188/history/abc-123-def
```

**未完成**: 返回 `{}` (空对象)
**完成**: 返回包含输出的执行数据:
```json
{
  "abc-123-def": {
    "outputs": {
      "9": {
        "images": [{"filename": "ComfyUI_00001.png", "subfolder": "", "type": "output"}]
      }
    },
    "status": {"completed": true}
  }
}
```

### 获取输出图像

```bash
curl "http://127.0.0.1:8188/view?filename=ComfyUI_00001.png&subfolder=&type=output" -o output.png
```

### 上传参考图像

```bash
curl -X POST http://127.0.0.1:8188/upload/image \
  -F "image=@reference.png" \
  -F "subfolder=input" \
  -F "type=input"
```

### 取消当前生成

```bash
curl -X POST http://127.0.0.1:8188/interrupt
```

### 释放 VRAM

```bash
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true}'
```

## 轮询策略

ComfyUI 在 CLI 环境下不支持 WebSocket。使用 REST 轮询:

1. 通过 `POST /prompt` 排队工作流 → 获取 `prompt_id`
2. 每 **5 秒** 轮询 `GET /history/{prompt_id}`
3. 空响应: 生成进行中，继续轮询
4. 非空响应: 检查 `status.completed`
5. 若 `completed: true`, 提取输出
6. 状态错误: 路由到 `comfyui-troubleshooter`

**超时**: 轮询 10 分钟后警告用户。视频生成 (Wan 14B) 可能需要 15-30 分钟。

## 工作流验证

排队任何工作流前:

1. 读取 `state/inventory.json` (通过 `comfyui-inventory`)
2. 对工作流中的每个节点: 验证 `class_type` 是否存在于已安装节点
3. 对每个模型引用: 验证文件是否存在于已安装模型
4. 标记缺失项:
   - 节点: 建议使用 `ComfyUI-Manager` 安装命令
   - 模型: 提供 `references/models.md` 下载链接
   - 版本不匹配: 建议更新

## 错误处理

| 错误 | 原因 | 操作 |
|-------|-------|--------|
| Connection refused | ComfyUI 未运行 | 切换到离线模式, 保存 JSON |
| 400 Bad Request | 无效工作流 JSON | 验证节点连接 |
| 500 Internal Error | ComfyUI 崩溃 | 建议重启, 检查日志 |
| Timeout (无响应) | 服务器过载 | 等待并重试一次 |

## 参考

完整 API 文档: `foundation/api-quick-ref.md`
