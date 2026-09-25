REST 是 agentmemory 的主要接口。MCP 是在其之上构建的桥梁。每个内存操作都在 `http://localhost:3111/agentmemory/*` 下有一个 HTTP 端点。

## 快速入门

```bash
# liveness
curl -fsS http://localhost:3111/agentmemory/livez

# save
curl -X POST http://localhost:3111/agentmemory/remember \
  -H "Content-Type: application/json" \
  -d '{"content":"chose JWT refresh rotation","concepts":["jwt-refresh-rotation"]}'

# recall
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -d '{"query":"auth token strategy","limit":5}'
```

## 认证

默认情况下，localhost 是开放的，不需要认证。当设置了 `AGENTMEMORY_SECRET` 时，每个请求都需要 `Authorization: Bearer $AGENTMEMORY_SECRET`。请参考 agentmemory-config。

## 规范

- 保存操作返回 `201`，读取操作返回 `200`，验证错误返回 `400`。
- 处理器会白名单化请求体字段并丢弃未知字段，因此传递额外键是安全的但会被忽略。
- 端口号可以通过 `--port` 或 `--instance` 进行配置；流、查看器和引擎都由此派生。

## 参考文档

- agentmemory-mcp-tools 用于查找 MCP 的对应内容。
- agentmemory-config 用于查找端口号组合和密钥。

## 参考

完整的端点列表和方法位于 REFERENCE.md 中，该文件由 `src/triggers/api.ts` 生成。
