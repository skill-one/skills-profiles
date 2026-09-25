## 1. 安装步骤

如果你将模拟器任务委托给子代理，请确保它们拥有MCP权限。

1. **找到一个已启动的模拟器**
   使用`list-devices`。筛选出`platform: "ios"`的条目，并跳过任何带有`kind: "device"`的条目（一个物理iPhone，永远不会是模拟器目标）：已启动的模拟器会首先列出。
   如果没有已启动的模拟器，请使用`udid: <选择的UDID>`调用`boot-device`。

2. **验证连接**
   所有交互工具（`gesture-tap`、`gesture-swipe`、`gesture-custom`等）如果服务器尚未运行，则会自动启动服务器。

## 2. 注意事项

- UDID的格式如下：`A1B2C3D4-E5F6-7890-ABCD-EF1234567890`
