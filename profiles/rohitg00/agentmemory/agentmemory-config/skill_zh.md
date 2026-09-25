agentmemory 从环境变量和 `~/.agentmemory/.env` 文件中读取配置（每行一个 `KEY=value`，无需 `export` 前缀）。修改后需要重启服务器。

## 快速入门

在 `~/.agentmemory/.env` 文件中设置提供者密钥以启用更丰富的记忆功能：

```env
ANTHROPIC_API_KEY=sk-ant-...
AGENTMEMORY_AUTO_COMPRESS=true
AGENTMEMORY_INJECT_CONTEXT=true
```

## 值得了解的默认设置

- 无需 API 密钥。如果没有密钥，agentmemory 将以 BM25 加本地嵌入的方式运行零 LLM。
- 旨在关闭 token 消耗功能：`AGENTMEMORY_AUTO_COMPRESS`（LLM 摘要）和 `AGENTMEMORY_INJECT_CONTEXT`（自动上下文注入）都会根据工具使用频率按比例消耗 token。
- 工具可见性：`AGENTMEMORY_TOOLS=all`（默认）或 `core` 用于精简版。
- 认证：设置 `AGENTMEMORY_SECRET` 以要求 REST API 使用 `Authorization: Bearer`。

## 端口

REST 是 3111 端口的锚点。流 = N+1（3112），查看器 = N+2（3113），引擎 = N+46023（49134）。使用 `--port <N>` 或 `--instance <N>` 可以整体移动这一组端口。

## 参考资料链接

- [agentmemory-rest-api](https://example.com) 了解密钥的使用方式。
- [agentmemory-architecture](https://example.com) 了解端口分组的原因。

## 参考

完整的已识别变量列表位于 REFERENCE.md 文件中，该文件通过扫描 `src/` 目录生成。
