# MCP Builder

根据您需要的工具描述，构建一个可工作的 MCP 服务器。使用 FastMCP 生成可部署的 Python 服务器。

## 工作流程

### 第 1 步：定义要暴露的内容

询问服务器需要提供什么：

- **工具** -- Claude 可以调用的函数（API 封装、计算、文件操作）
- **资源** -- Claude 可以读取的数据（数据库记录、配置、文档）
- **提示** -- 带有参数的可重用提示模板

像“用于查询我们客户数据库的 MCP 服务器”这样的简短描述就足够了。

### 第 2 步：搭建服务器

```bash
pip install fastmcp
```

创建服务器文件。服务器实例必须在模块级别：

```python
from fastmcp import FastMCP

# MUST be at module level for FastMCP Cloud
mcp = FastMCP("My Server")

@mcp.tool()
async def search_customers(query: str) -> str:
    """按名称或邮箱搜索客户。"""
    # 实现部分在这里
    return f"找到匹配：{query}"

@mcp.resource("customers://{customer_id}")
async def get_customer(customer_id: str) -> str:
    """按 ID 获取客户详情。"""
    return f"客户 {customer_id} 详情"

if __name__ == "__main__":
    mcp.run()
```

### 第 3 步：添加辅助 CLI 脚本（可选）

为 Claude 代码终端使用，在 MCP 服务器旁边添加脚本：

```
my-mcp-server/
├── src/index.ts          # MCP 服务器（用于 Claude.ai）
├── scripts/
│   ├── search.ts         # 搜索工具的 CLI 版本
│   └── _shared.ts        # 共享认证/配置
├── SCRIPTS.md            # 可用脚本文档
└── package.json
```

CLI 脚本提供文件 I/O、批量处理和 MCP 无法提供的更丰富的输出。
参考 `assets/SCRIPTS-TEMPLATE.md` 和 `assets/script-template.ts` 获取 TypeScript 模板。

### 第 4 步：本地测试

**快速测试 -- 直接运行：**

```bash
python server.py
```

**开发模式带检查器 UI（推荐）：**

```bash
fastmcp dev server.py
# 在 http://localhost:5173 打开检查器
# 热重载、详细日志、工具/资源检查
```

**HTTP 模式用于远程客户端：**

```bash
python server.py --transport http --port 8000
```

**使用 FastMCP Client 的自动化测试脚本：**

```python
import asyncio
from fastmcp import Client

async def test_server(server_path):
    async with Client(server_path) as client:
        # 列出所有内容
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(f"工具：[{', '.join(t.name for t in tools)}]")
        print(f"资源：[{', '.join(r.uri for r in resources)}]")
        print(f"提示：[{', '.join(p.name for p in prompts)}]")

        # 调用第一个工具
        if tools:
            result = await client.call_tool(tools[0].name, {})
            print(f"工具结果：{result}")

        # 读取第一个资源
        if resources:
            data = await client.read_resource(resources[0].uri)
            print(f"资源数据：{data}")

asyncio.run(test_server("server.py"))
```

### 第 5 步：预部署检查清单

部署前运行这些检查。所有必需的检查必须通过。

**必需（否则会导致部署失败）：**

1. 服务器文件存在
2. Python 语法有效：`python3 -m py_compile server.py`
3. 模块级别的服务器对象（不能在函数内部）：
   ```bash
   grep -q "^mcp = FastMCP\|^server = FastMCP\|^app = FastMCP" server.py
   ```
4. `requirements.txt` 存在，仅包含 PyPI 包（无 `git+`、`-e`、`.whl`、`.tar.gz`）
5. 无硬编码的密钥（检查 `api_key = "..."` 模式，排除 `os.getenv`/`os.environ`）

**建议（警告）：**

6. `fastmcp` 列在 `requirements.txt` 中
7. `.gitignore` 包含 `.env`
8. 无循环导入
9. Git 仓库已初始化并包含远程
10. 服务器可以加载：`timeout 5 fastmcp inspect server.py`

### 第 6 步：部署

**FastMCP Cloud（最简单）：**

```bash
git add . && git commit -m "Ready for deployment"
git push -u origin main
# 访问 https://fastmcp.cloud，连接仓库，添加环境变量，部署
# URL: https://your-project.fastmcp.app/mcp
```

云要求：
- 模块级别的服务器对象命名为 `mcp`、`server` 或 `app`
- `requirements.txt` 仅包含 PyPI 依赖
- 公共 GitHub 仓库
- 密钥的环境变量（无硬编码值）
- 推送到 main 时自动部署，PR 预览部署

**Docker（自托管）：**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "server.py", "--transport", "http", "--port", "8000"]
```

**Cloudflare Workers（边缘）：**
参考 `cloudflare-worker-builder` 技能，用于基于 Workers 的 MCP 服务器。

---

## 关键模式

### 模块级服务器实例

FastMCP Cloud 要求服务器实例在模块级别：

```python
# 正确
mcp = FastMCP("My Server")

@mcp.tool()
def my_tool(): ...

# 错误 -- Cloud 找不到服务器
def create_server():
    mcp = FastMCP("My Server")
    return mcp

# 工厂模式的修复 -- 模块级别导出
def create_server() -> FastMCP:
    mcp = FastMCP("server")
    return mcp
mcp = create_server()
```

### 类型注解必需

FastMCP 使用类型注解生成工具模式：

```python
@mcp.tool()
async def search(
    query: str,           # 必选参数
    limit: int = 10,      # 带默认值的可选参数
    tags: list[str] = []  # 支持复杂类型
) -> str:
    """Docstring 成为工具描述。"""
    ...
```

### 错误处理

将错误作为字符串返回，不要抛出异常：

```python
@mcp.tool()
async def get_data(id: str) -> str:
    try:
        result = await fetch_data(id)
        return json.dumps(result)
    except NotFoundError:
        return f"错误：未找到 ID 为 {id} 的数据"
```

### 云就绪服务器模式

```python
import os
from fastmcp import FastMCP

mcp = FastMCP("production-server")
API_KEY = os.getenv("API_KEY")

@mcp.tool()
async def production_tool(data: str) -> dict:
    if not API_KEY:
        return {"error": "API_KEY 未配置"}
    return {"status": "success", "data": data}

if __name__ == "__main__":
    mcp.run()
```

---

## 常见错误和修复

这些是你会遇到的问题。在部署前修复它们。

| 错误 | 原因 | 修复 |
|------|------|------|
| `RuntimeError: No server object found at module level` | 服务器在函数内部 | 在模块级别导出 `mcp = FastMCP(...)` |
| `RuntimeError: no running event loop` | 缺少异步/等待 | 使用 `async def` 进行异步操作 |
| `TypeError: missing required argument 'context'` | 未注解上下文 | 添加 `context: Context` 带类型注解 |
| `ValueError: Invalid resource URI` | 缺少 URI 方案 | 使用 `data://`、`file://`、`info://`、`api://` |
| 资源模板参数不匹配 | 名称不匹配 | `user://{user_id}` 需要 `def get_user(user_id: str)` |
| Pydantic 验证错误 | 类型注解错误 | 确保注解与实际数据类型匹配 |
| 传输不匹配 | 客户端/服务器协议不同 | 两者都匹配 stdio 或都匹配 http |
| 可编辑包的导入错误 | 包未安装 | `pip install -e .` 或添加到 PYTHONPATH |
| `DeprecationWarning: mcp.settings` | 旧 API | 使用 `os.getenv()` 代替 |
| 端口已被占用 | 滥用进程 | `lsof -ti:8000 \| xargs kill -9` |
| 模式生成失败 | 非JSON类型 | 使用兼容JSON的类型（无 NumPy 数组） |
| JSON 序列化错误 | 响应中包含 datetime/bytes | 转换为 `.isoformat()` 或字符串 |
| 循环导入 | 工厂在 `__init__.py` 中 | 使用直接导入，避免工厂模式 |
| Python 3.12+ datetime 警告 | `datetime.utcnow()` 已弃用 | 使用 `datetime.now(timezone.utc)` |
| 导入时执行 | 模块级异步资源 | 使用懒加载模式 |

---

## 生产模式

### 自包含服务器

将所有工具放在一个文件中，避免循环导入：

```python
from fastmcp import FastMCP
import os

mcp = FastMCP("my-server")

# 配置
class Config:
    API_KEY = os.getenv("API_KEY", "")
    BASE_URL = os.getenv("BASE_URL", "https://api.example.com")

# 辅助函数
def format_success(data): return {"status": "success", "data": data}
def format_error(msg): return {"status": "error", "message": msg}

@mcp.tool()
async def my_tool(query: str) -> dict:
    if not Config.API_KEY:
        return format_error("API_KEY 未配置")
    return format_success({"query": query})
```

### 懒加载初始化

不要在模块级别创建异步资源。在首次使用时初始化：

```python
_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await create_connection(Config.DB_URL)
    return _db
```

### 健康检查资源

```python
@mcp.resource("health://status")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {
            "api": "connected",
            "database": "connected"
        }
    }
```

### 连接池

```python
import httpx

_client = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=Config.BASE_URL,
            headers={"Authorization": f"Bearer {Config.API_KEY}"},
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
            timeout=30.0
        )
    return _client
```

### 带退避的重试

```python
async def retry_with_backoff(func, max_retries=3, initial_delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

---

## 上下文功能（高级）

### 上下文注入

```python
from fastmcp import Context

@mcp.tool()
async def tool_with_context(param: str, context: Context) -> dict:
    # 上下文参数必须有类型注解
    pass
```

### 进度跟踪

```python
@mcp.tool()
async def long_task(items: list[str], context: Context) -> str:
    for i, item in enumerate(items):
        await context.report_progress(i + 1, len(items), f"处理 {item}")
        await process(item)
    return "Done"
```

### 采样（在工具中从 LLM）

```python
@mcp.tool()
async def summarise(text: str, context: Context) -> str:
    result = await context.request_sampling(
        messages=[{"role": "user", "content": f"Summarise: {text}"}],
        max_tokens=200
    )
    return result
```

---

## CLI 快速参考

```bash
fastmcp dev server.py              # 带检查器 UI 的开发模式
fastmcp run server.py              # 运行（stdio）
fastmcp run server.py --transport http --port 8000  # 运行（HTTP）
fastmcp inspect server.py          # 检查而不运行
fastmcp install server.py          # 安装到 Claude Desktop
fastmcp deploy server.py --name my-server  # 部署到 Cloud
```

环境变量：`FASTMCP_LOG_LEVEL`（DEBUG/INFO/WARNING/ERROR）、`FASTMCP_ENV`（development/staging/production）。

---

## 集成模式（可选）

针对特定集成方法，参考 `references/integration-patterns.md`：
- **手动 API** -- `httpx.AsyncClient` 带可重用客户端
- **OpenAPI 自动生成** -- `FastMCP.from_openapi(spec, client, route_maps=[...])`
- **FastAPI 转换** -- `FastMCP.from_fastapi(app)`

---

## 资源文件

- `assets/basic-server.py` -- 最小 FastMCP 服务器模板
- `assets/self-contained-server.py` -- 带存储和中间件的服务器
- `assets/tools-examples.py` -- 工具模式和类型注解
- `assets/resources-examples.py` -- 资源 URI 模式
- `assets/prompts-examples.py` -- 提示模板模式
- `assets/client-example.py` -- MCP 客户端使用
- `assets/SCRIPTS-TEMPLATE.md` -- CLI 伴侣文档模板
- `assets/script-template.ts` -- TypeScript CLI 脚本模板
