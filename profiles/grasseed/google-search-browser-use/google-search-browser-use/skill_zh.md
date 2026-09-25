# Google 搜索浏览器使用

## 概述

使用 `browser-use` 运行 Google 搜索（优先使用真实浏览器模式），打开结果，并提取相关片段或页面内容。此技能利用用户现有的浏览器会话来减少验证码。

## 前置条件

在运行搜索前，确保环境已准备就绪：

1.  **检查安装**：
    验证 `browser-use` 是否在当前 PATH 中可用。
    ```bash
    which browser-use
    ```

2.  **若缺失则安装**：
    若未找到，使用 pip 安装。
    ```bash
    python3 -m pip install --user browser-use
    ```

3.  **定位二进制文件**：
    安装后若命令仍未找到，它很可能位于用户的本地 bin 目录。动态获取路径：
    ```bash
    python3 -m site --user-base
    # 二进制文件通常位于 <USER_BASE>/bin/browser-use
    ```

## 工作流程

### 1) 启动 Google 搜索（真实浏览器模式）

使用真实浏览器以复用用户的登录会话。

**选项 A：标准执行**
```bash
browser-use --browser real open "https://www.google.com/search?q=YOUR+QUERY"
```

**选项 B：显式路径执行**
若选项 A 失败（命令未找到），使用前置条件中找到的完整路径：
```bash
# 示例（根据 'python3 -m site --user-base' 输出调整）：
${HOME}/Library/Python/3.14/bin/browser-use --browser real open "https://www.google.com/search?q=YOUR+QUERY"
```
*(注意：如果 Python 版本不同，请替换 `3.14`)*

### 2) 检查结果并解析

浏览器打开后：

```bash
# 检查当前页面状态
browser-use --browser real state

# 点击搜索结果（使用状态输出中的索引）
browser-use --browser real click <index>
```

### 3) 提取或总结

-   **目标**：提供包含来源引用的简短总结（3-6 个要点）。
-   **备用方案**：如果 `browser-use` 解析困难，使用 `curl` 结合 Jina AI 获取文本友好版本：
    ```bash
    curl -L "https://r.jina.ai/https://example.com"
    ```

### 4) 关闭会话

```bash
browser-use close
```

## 故障排除

-   **验证码**：若遇到，请在打开的浏览器窗口中手动解决。
-   **路径问题**：如果无法直接调用 `browser-use`，始终优先通过 `python3 -m site --user-base` 找到路径，而不是猜测。
-   **连接**：如果出现超时，确保没有 VPN/代理阻止 Google 结果。
