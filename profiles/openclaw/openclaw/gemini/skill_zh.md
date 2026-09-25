# Gemini CLI

在无头单次模式中使用 Gemini。位置参数启动交互模式；使用 `-p/--prompt`。

快速入门

- `gemini -p "回答这个问题..."` 
- `gemini -m <模型> -p "提示..."`
- `gemini -p "返回 JSON" --output-format json`
- 标准输入追加到 `-p`：`cat notes.md | gemini -p "总结"`

扩展

- 列表：`gemini --list-extensions`
- 管理：`gemini extensions <命令>`
- 技能：`gemini skills <命令>`
- 钩子：`gemini hooks <命令>`
- MCP：`gemini mcp <命令>`

注意事项

- 如果需要认证，请先交互式运行 `gemini` 并遵循登录流程。
- 为安全起见，避免使用 `--yolo`。
