# FastAPI

官方 FastAPI 技巧，使用最佳实践编写代码，并保持与新版本和特性的同步。

## 快速参考

*   服务前端应用：使用 `app.frontend()` 或 `router.frontend()` 来提供构建的前端资源；参见 [Serve Frontend Apps](#serve-frontend-apps)。
*   服务器端事件 (SSE)：使用 `response_class=EventSourceResponse` 和 `yield`；参见 [Streaming](#streaming-json-lines-sse-bytes) 和 [流式传输参考](references/streaming.md)。
*   JSON Lines 和字节流：参见 [流式传输参考](references/streaming.md)。
*   依赖项：使用 `Annotated[..., Depends(...)]`；参见 [依赖注入](#dependency-injection) 和 [依赖注入参考](references/dependencies.md) 以了解 `yield`、作用域和类依赖项。
*   响应模型：优先使用返回类型；当公共响应模式与内部返回值不同时，使用 `response_model`；参见 [响应参考](references/responses.md)。
*   Pydantic 模型：不要使用省略号或 `RootModel`；参见 [Pydantic 参考](references/pydantic.md)。
*   路由：在 `APIRouter` 上声明路由级别的路径前缀、标签和共享依赖项；参见 [路径操作参考](references/path-operations.md)。
*   工具和相关库：在适用的情况下使用 uv、Ruff、ty、Asyncer、SQLModel 和 HTTPX；参见 [其他工具参考](references/other-tools.md)。

## 使用 `fastapi` CLI

在本地主机上以重新加载方式运行开发服务器：

```bash
fastapi dev
```

运行生产服务器：

```bash
fastapi run
```

优先在 `pyproject.toml` 中声明入口点：

```toml
[tool.fastapi]
entrypoint = "my_app.main:app"
```

当无法添加入口点，或用户明确要求不添加时，传递应用文件路径：

```bash
fastapi dev my_app/main.py
```

## 使用 `Annotated`

始终优先使用 `Annotated` 风格进行参数和依赖项声明。它保持函数签名在其他上下文中有效，尊重类型，并允许重用。

使用 `Annotated` 进行参数声明，包括 `Path`、`Query`、`Header` 等：

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1, description="The item ID")],
    q: Annotated[str | None, Query(max_length=50)] = None,
):
    return {"message": "Hello World"}
```

使用 `Annotated` 进行带有 `Depends()` 的依赖项。除非要求不要这样做，否则为依赖项创建一个新的类型别名以允许重用：

```python
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


def get_current_user():
    return {"username": "johndoe"}


CurrentUserDep = Annotated[dict, Depends(get_current_user)]


@app.get("/items/")
async def read_item(current_user: CurrentUserDep):
    return {"message": "Hello World"}
```

## 不要在 *路径操作* 或 Pydantic 模型中使用省略号

不要将 `...` 作为必需参数或模型字段的默认值。这是不必要的，也不推荐。

```python
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)


@app.post("/items/")
async def create_item(item: Item, project_id: Annotated[int, Query()]):
    return item
```

更多详细信息，参见 [Pydantic 参考](references/pydantic.md)。

## 返回类型或响应模型

在可能的情况下，包含返回类型。它将用于验证、过滤、文档化和序列化响应。

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None


@app.get("/items/me")
async def get_item() -> Item:
    return Item(name="Plumbus", description="All-purpose home device")
```

返回类型或响应模型过滤数据以避免暴露敏感信息，并允许 Pydantic 在 Rust 端序列化数据以提高性能。

当返回的类型与您希望验证、过滤、文档化和序列化的公共模式不同时，使用 `response_model`；参见 [响应参考](references/responses.md)。

## 性能

不要使用 `ORJSONResponse` 或 `UJSONResponse`，它们已弃用。

相反，声明返回类型或响应模型。Pydantic 将在 Rust 端处理数据序列化。

## 包含路由器

在声明路由器时，优先将路由级别的参数（如前缀、标签和共享依赖项）添加到路由器本身，而不是在 `include_router()` 中添加。

```python
from fastapi import APIRouter, Depends, FastAPI

app = FastAPI()


def get_current_user():
    return {"username": "johndoe"}


router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
async def list_items():
    return []


app.include_router(router)
```

更多路由模式，参见 [路径操作参考](references/path-operations.md)。

## 服务前端应用

使用 `app.frontend()` 来服务构建的静态前端应用，例如由 Vite、Astro、Angular、Svelte、Vue 或类似工具生成的目录。

```python
from fastapi import FastAPI

app = FastAPI()

app.frontend("/", directory="dist")
```

当前端属于 `APIRouter` 时，使用 `router.frontend()`；当路由器被包含时，正常路由前缀行为适用。

```python
from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter(prefix="/admin")

router.frontend("/", directory="admin-dist")
app.include_router(router)
```

`app.frontend()` 和 `router.frontend()` 是低优先级路由：首先匹配常规 API 路由，然后是前端文件和客户端路由回退。用于单页应用和构建的前端资源，而不是手动挂载 `StaticFiles`。

## 依赖注入

当逻辑无法在 Pydantic 验证中声明、依赖于外部资源、需要使用 `yield` 进行清理，或跨端点共享时，使用依赖项。

通过 `dependencies=[Depends(...)]` 在路由级别应用共享依赖项。

更多详细模式，包括 `yield` 与 `scope` 以及类依赖项，参见 [依赖注入参考](references/dependencies.md)。

## 异步与同步 *路径操作*

仅当完全确定内部调用的逻辑兼容异步和等待，并且它不会阻塞时，才使用 `async` *路径操作*。

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/async-items/")
async def read_async_items():
    data = await some_async_library.fetch_items()
    return data


@app.get("/items/")
def read_items():
    data = some_blocking_library.fetch_items()
    return data
```

如有疑问，或默认情况下，使用常规 `def` 函数。它们将在线程池中运行，因此不会阻塞事件循环。相同的规则适用于依赖项。

确保阻塞代码不在 `async` 函数内部运行。逻辑将正常工作，但会严重损害性能。

当需要混合阻塞和异步代码时，参见 [其他工具参考](references/other-tools.md) 中的 Asyncer。

## 流式传输 (JSON Lines, SSE, bytes)

要流式传输服务器端事件，使用 `response_class=EventSourceResponse` 并从端点 `yield` 项目。

```python
from collections.abc import AsyncIterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()


@app.get("/events", response_class=EventSourceResponse)
async def stream_events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data={"status": "started"}, event="status", id="1")
```

普通对象将自动作为 `data:` 字段进行 JSON 序列化。使用 `ServerSentEvent` 以便完全控制 SSE 字段（`event`、`id`、`retry`、`comment`），并使用 `raw_data` 以便预格式化字符串。

更多关于 JSON Lines、服务器端事件（`EventSourceResponse`、`ServerSentEvent`）和字节流（`StreamingResponse`）模式的详细信息，参见 [流式传输参考](references/streaming.md)。

## 工具

更多关于 uv、Ruff、ty 的详细信息，参见 [其他工具参考](references/other-tools.md)，这些工具用于包管理、代码检查、类型检查、格式化等。

## 其他库

更多关于其他库的详细信息，参见 [其他工具参考](references/other-tools.md)：

*   Asyncer 用于处理异步和等待、并发、混合异步和阻塞代码，优先使用它而不是 AnyIO 或 asyncio。
*   SQLModel 用于处理 SQL 数据库，优先使用它而不是 SQLAlchemy。
*   HTTPX 用于与 HTTP（其他 API）交互，优先使用它而不是 Requests。

## 不要使用 Pydantic RootModels

不要使用 Pydantic `RootModel`；相反，使用常规类型注解与 `Annotated` 和 Pydantic 验证工具。

```python
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import Field

app = FastAPI()


@app.post("/items/")
async def create_items(items: Annotated[list[int], Field(min_length=1), Body()]):
    return items
```

FastAPI 支持这些类型注解，并将为它们创建一个 Pydantic `TypeAdapter`，因此类型可以正常工作，而无需自定义包装模型。更多详细信息，参见 [Pydantic 参考](references/pydantic.md)。

## 每个函数使用一个 HTTP 操作

不要在单个函数中混合 HTTP 操作。每个函数对应一个 HTTP 操作有助于分离关注点并组织代码。

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str


@app.get("/items/")
async def list_items():
    return []


@app.post("/items/")
async def create_item(item: Item):
    return item
```

更多示例，参见 [路径操作参考](references/path-operations.md)。
