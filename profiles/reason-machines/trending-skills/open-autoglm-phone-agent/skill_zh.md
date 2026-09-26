# Open-AutoGLM 手机代理

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Open-AutoGLM 是一个开源的AI手机代理框架，能够通过自然语言控制Android、HarmonyOS NEXT和iOS设备。它使用AutoGLM视觉语言模型（9B参数版）来感知屏幕内容并执行多步任务，例如“打开美团搜索附近的火锅店”。

## 架构概述

```
用户自然语言 → AutoGLM VLM → 屏幕感知 → ADB/HDC/WebDriverAgent → 设备操作
```

- **模型**: AutoGLM-Phone-9B（中文优化版）或 AutoGLM-Phone-9B-多语言
- **设备控制**: ADB（Android）、HDC（HarmonyOS NEXT）、WebDriverAgent（iOS）
- **模型服务**: vLLM或SGLang（自托管）或BigModel/ModelScope API
- **输入**: 屏幕截图 + 任务描述 → 输出: 结构化操作命令

## 安装

### 前置条件

- Python 3.10+
- ADB安装并在PATH中（Android）或HDC（HarmonyOS）或WebDriverAgent（iOS）
- 安装有开发者模式+USB调试的Android设备
- Android设备上安装ADB键盘APK（用于文本输入）

### 安装框架

```bash
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM
pip install -r requirements.txt
pip install -e .
```

### 验证ADB连接

```bash
# Android
adb devices
# 预期: emulator-5554   device

# HarmonyOS NEXT
hdc list targets
# 预期: 7001005458323933328a01bce01c2500
```

## 模型部署选项

### 选项A：第三方API（推荐用于快速启动）

**BigModel (ZhipuAI)**
```bash
export BIGMODEL_API_KEY="your-bigmodel-api-key"
python main.py \
  --base-url https://open.bigmodel.cn/api/paas/v4 \
  --model "autoglm-phone" \
  --apikey $BIGMODEL_API_KEY \
  "打开美团搜索附近的火锅店"
```

**ModelScope**
```bash
export MODELSCOPE_API_KEY="your-modelscope-api-key"
python main.py \
  --base-url https://api-inference.modelscope.cn/v1 \
  --model "ZhipuAI/AutoGLM-Phone-9B" \
  --apikey $MODELSCOPE_API_KEY \
  "open Meituan and find nearby hotpot"
```

### 选项B：使用vLLM自托管

```bash
# 安装vLLM（或使用官方Docker: docker pull vllm/vllm-openai:v0.12.0）
pip install vllm

# 启动模型服务（严格遵循这些参数）
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs '{"max_pixels":5000000}' \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt '{"image":10}' \
  --model zai-org/AutoGLM-Phone-9B \
  --port 8000
```

### 选项C：使用SGLang自托管

```bash
# 安装SGLang或使用: docker pull lmsysorg/sglang:v0.5.6.post1
# 在容器内: pip install nvidia-cudnn-cu12==9.16.0.29

python3 -m sglang.launch_server \
  --model-path zai-org/AutoGLM-Phone-9B \
  --served-model-name autoglm-phone-9b \
  --context-length 25480 \
  --mm-enable-dp-encoder \
  --mm-process-config '{"image":{"max_pixels":5000000}}' \
  --port 8000
```

### 验证部署

```bash
python scripts/check_deployment_cn.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b
```

预期输出包括一个`<think>...</think>`块，随后是`<answer>do(action="Launch", app="...")`。**如果思维链非常短或混乱，则模型部署失败。**

## 运行代理

### 基本CLI使用

```bash
# Android设备（默认）
python main.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b \
  "打开小红书搜索美食"

# HarmonyOS设备
python main.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b \
  --device-type hdc \
  "打开设置查看WiFi"

# 多语言模型用于英文应用
python main.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b-multilingual \
  "Open Instagram and search for travel photos"
```

### 关键CLI参数

| 参数 | 描述 | 默认值 |
|-------|-------|-------|
| `--base-url` | 模型服务端点 | 必须提供 |
| `--model` | 服务器上的模型名称 | 必须提供 |
| `--apikey` | 第三方服务的API密钥 | 无 |
| `--device-type` | `adb`（Android）或`hdc`（HarmonyOS） | `adb` |
| `--device-id` | 特定设备序列号 | 自动检测 |

## Python API使用

### 基本代理调用

```python
from phone_agent import PhoneAgent
from phone_agent.config import AgentConfig

config = AgentConfig(
    base_url="http://localhost:8000/v1",
    model="autoglm-phone-9b",
    device_type="adb",  # 或"hdc"用于HarmonyOS
)

agent = PhoneAgent(config)

# 运行任务
result = agent.run("打开淘宝搜索蓝牙耳机")
print(result)
```

### 带设备选择的自定义任务

```python
from phone_agent import PhoneAgent
from phone_agent.config import AgentConfig
import os

config = AgentConfig(
    base_url=os.environ["MODEL_BASE_URL"],
    model=os.environ["MODEL_NAME"],
    apikey=os.environ.get("MODEL_API_KEY"),
    device_type="adb",
    device_id="emulator-5554",  # 特定设备
)

agent = PhoneAgent(config)

# 带敏感操作确认的任务
result = agent.run(
    "在京东购买最便宜的蓝牙耳机",
    confirm_sensitive=True  # 在购买操作前提示用户
)
```

### 直接调用模型API（用于测试/集成）

```python
import openai
import base64
import os
from pathlib import Path

client = openai.OpenAI(
    base_url=os.environ["MODEL_BASE_URL"],
    api_key=os.environ.get("MODEL_API_KEY", "dummy"),
)

# 加载屏幕截图
screenshot_path = "screenshot.png"
with open(screenshot_path, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="autoglm-phone-9b",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                },
                {
                    "type": "text",
                    "text": "Task: 搜索附近的咖啡店\nCurrent step: Navigate to search",
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
# 输出格式: <think>...</think>\n<answer>do(action="...", ...)
```

### 解析模型操作输出

```python
import re

def parse_action(model_output: str) -> dict:
    """将AutoGLM模型输出解析为结构化操作."""
    # 提取answer块
    answer_match = re.search(r'<answer>(.*?)(?:</answer>|$)', model_output, re.DOTALL)
    if not answer_match:
        return {"action": "unknown"}
    
    answer = answer_match.group(1).strip()
    
    # 解析do()调用
    # 格式: do(action="ActionName", param1="value1", param2="value2")
    action_match = re.search(r'do\(action="([^"]+)"(.*?)\)', answer, re.DOTALL)
    if not action_match:
        return {"action": "unknown", "raw": answer}
    
    action_name = action_match.group(1)
    params_str = action_match.group(2)
    
    # 解析参数
    params = {}
    for param_match in re.finditer(r'(\w+)="([^"]*)"', params_str):
        params[param_match.group(1)] = param_match.group(2)
    
    return {"action": action_name, **params}

# 示例使用
output = '<think>需要启动京东</think>\n<answer>do(action="Launch", app="京东")'
action = parse_action(output)
# {"action": "Launch", "app": "京东"}
```

## ADB设备控制模式

### 代理使用的常见ADB操作

```python
import subprocess

def take_screenshot(device_id: str = None) -> bytes:
    """捕获当前设备屏幕."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["exec-out", "screencap", "-p"])
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout

def send_tap(x: int, y: int, device_id: str = None):
    """在屏幕坐标处点击."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["shell", "input", "tap", str(x), str(y)])
    subprocess.run(cmd)

def send_text_adb_keyboard(text: str, device_id: str = None):
    """通过ADB键盘发送文本（必须安装并启用ADB键盘）."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    # 首先启用ADB键盘
    cmd_enable = cmd + ["shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"]
    subprocess.run(cmd_enable)
    # 发送文本
    cmd_text = cmd + ["shell", "am", "broadcast", "-a", "ADB_INPUT_TEXT",
                      "--es", "msg", text]
    subprocess.run(cmd_text)

def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, device_id: str = None):
    """在屏幕上执行滑动手势."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["shell", "input", "swipe",
                str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
    subprocess.run(cmd)

def press_back(device_id: str = None):
    """按Android返回键."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["shell", "input", "keyevent", "KEYCODE_BACK"])
    subprocess.run(cmd)

def launch_app(package_name: str, device_id: str = None):
    """通过包名启动应用."""
    cmd = ["adb"]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["shell", "monkey", "-p", package_name, "-c",
                "android.intent.category.LAUNCHER", "1"])
    subprocess.run(cmd)
```

## Midscene.js集成

用于使用AutoGLM进行JavaScript/TypeScript自动化：

```javascript
// .env配置
// MIDSCENE_MODEL_NAME=autoglm-phone
// MIDSCENE_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
// MIDSCENE_OPENAI_API_KEY=your-api-key

import { AndroidAgent } from "@midscene/android";

const agent = new AndroidAgent();
await agent.aiAction("打开微信发送消息给张三");
await agent.aiQuery("当前页面显示的消息内容是什么？");
```

## 远程ADB（WiFi调试）

```bash
# 首先通过USB连接设备，然后启用TCP/IP模式
adb tcpip 5555

# 获取设备IP地址
adb shell ip addr show wlan0

# 无线连接（连接后断开USB）
adb connect 192.168.1.100:5555

# 验证连接
adb devices
# 192.168.1.100:5555   device

# 与代理一起使用
python main.py \
  --base-url http://model-server:8000/v1 \
  --model autoglm-phone-9b \
  --device-id "192.168.1.100:5555" \
  "打开支付宝查看余额"
```

## 常见操作类型

AutoGLM模型输出结构化操作：

| 操作 | 描述 | 示例 |
|-------|-------|-------|
| `Launch` | 打开应用 | `do(action="Launch", app="微信")` |
| `Tap` | 点击屏幕元素 | `do(action="Tap", element="搜索框")` |
| `Type` | 输入文本 | `do(action="Type", text="火锅")` |
| `Swipe` | 滚动/滑动 | `do(action="Swipe", direction="up")` |
| `Back` | 按返回键 | `do(action="Back")` |
| `Home` | 进入主屏幕 | `do(action="Home")` |
| `Finish` | 任务完成 | `do(action="Finish", result="已完成搜索")` |

## 模型选择指南

| 模型 | 用途 | 语言 |
|-------|-------|-------|
| `AutoGLM-Phone-9B` | 中文应用（微信、淘宝、美团） | 中文优化版 |
| `AutoGLM-Phone-9B-Multilingual` | 国际应用、混合内容 | 中文+英文+其他 |

- HuggingFace: `zai-org/AutoGLM-Phone-9B` / `zai-org/AutoGLM-Phone-9B-Multilingual`
- ModelScope: `ZhipuAI/AutoGLM-Phone-9B` / `ZhipuAI/AutoGLM-Phone-9B-Multilingual`

## 环境变量参考

```bash
# 模型服务
export MODEL_BASE_URL="http://localhost:8000/v1"
export MODEL_NAME="autoglm-phone-9b"
export MODEL_API_KEY=""  # 对于BigModel/ModelScope API是必需的

# BigModel API
export BIGMODEL_API_KEY=""
export BIGMODEL_BASE_URL="https://open.bigmodel.cn/api/paas/v4"

# ModelScope API
export MODELSCOPE_API_KEY=""
export MODELSCOPE_BASE_URL="https://api-inference.modelscope.cn/v1"

# 设备配置
export ADB_DEVICE_ID=""      # 留空以自动检测
export HDC_DEVICE_ID=""      # HarmonyOS设备ID
```

## 故障排除

### 模型输出混乱或思维链非常短
**原因**: vLLM/SGLang启动参数不正确。
**解决**: 确保`--chat-template-content-format string`（vLLM）和`--mm-process-config`带`max_pixels:5000000`被设置。检查transformers版本兼容性。

### `adb devices`显示无设备
**解决**: 
1. 验证USB线支持数据传输（非充电专用）
2. 在手机上接受“允许USB调试”对话框
3. 尝试`adb kill-server && adb start-server`
4. 某些设备需要在启用开发者选项后重启

### Android文本输入无效
**解决**: ADB键盘必须安装且启用:
```bash
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
```

### 代理卡在循环中
**原因**: 模型无法识别完成任务路径。
**解决**: 框架包含敏感操作确认 — 确保对于购买/删除任务`confirm_sensitive=True`。对于登录/CAPTCHA屏幕，代理支持人工接管。

### vLLM CUDA显存不足
**解决**: AutoGLM-Phone-9B需要~20GB VRAM。使用`--tensor-parallel-size 2`进行多GPU，或使用API服务。

### 连接模型服务器失败
**解决**: 检查防火墙规则。对于远程服务器:
```bash
# 测试连接
curl http://YOUR_SERVER_IP:8000/v1/models
# 应返回模型列表JSON
```

### HarmonyOS设备未识别（HarmonyOS）
**解决**: HarmonyOS NEXT（非早期版本）是必需的。在设置→关于→版本号（快速连续点击10次）中启用开发者模式。

## iOS设置

对于iPhone自动化，请参阅专用设置指南:
```bash
# 按照文档/ios_setup/ios_setup.md配置WebDriverAgent后
python main.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b-multilingual \
  --device-type ios \
  "Open Maps and navigate to Central Park"
```
