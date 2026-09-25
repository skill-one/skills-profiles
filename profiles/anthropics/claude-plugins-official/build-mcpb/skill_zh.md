# 构建MCPB（捆绑本地MCP服务器）

MCPB是一个**包含其运行时的本地MCP服务器**。用户安装一个文件；它无需在他们的机器上安装Node、Python或任何工具链即可运行。这是分发本地MCP服务器的官方方式。

> MCPB是**次要**的分发路径。Anthropic建议使用远程MCP服务器进行目录列表——请参阅 https://claude.com/docs/connectors/building/what-to-build。

当服务器必须在用户的机器上运行时使用MCPB——读取本地文件、驱动桌面应用程序、与localhost服务通信、操作系统级API。如果你的服务器只调用云API，你几乎肯定想要一个远程HTTP服务器（参见 `build-mcp-server`）。不要为可以是一个URL的东西支付MCPB打包税。

---

## MCPB捆绑包包含的内容

```
my-server.mcpb              (zip归档)
├── manifest.json           ← 身份、入口点、配置模式、兼容性
├── server/                 ← 你的MCP服务器代码
│   ├── index.js
│   └── node_modules/       ← 捆绑的依赖项（或vendored）
└── icon.png
```

主机读取 `manifest.json`，启动 `server.mcp_config.command` 作为 **stdio** MCP服务器，并管道消息。从你的代码的角度来看，它与本地stdio服务器完全相同——唯一的区别在于打包。

---

## 元数据

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/mcpb/main/schemas/mcpb-manifest-v0.4.schema.json",
  "manifest_version": "0.4",
  "name": "local-files",
  "version": "0.1.0",
  "description": "读取、搜索和监视本地文件系统上的文件。",
  "author": { "name": "Your Name" },
  "server": {
    "type": "node",
    "entry_point": "server/index.js",
    "mcp_config": {
      "command": "node",
      "args": ["${__dirname}/server/index.js"],
      "env": {
        "ROOT_DIR": "${user_config.rootDir}"
      }
    }
  },
  "user_config": {
    "rootDir": {
      "type": "directory",
      "title": "根目录",
      "description": "要暴露的目录。默认为 ~/Documents。",
      "default": "${HOME}/Documents",
      "required": true
    }
  },
  "compatibility": {
    "claude_desktop": ">=1.0.0",
    "platforms": ["darwin", "win32", "linux"]
  }
}
```

**`server.type`** — `node`、`python` 或 `binary`。信息性；实际启动来自 `mcp_config`。

**`server.mcp_config`** — 启动时要使用的字面命令/args/env。使用 `${__dirname}` 表示捆绑包相对路径，使用 `${user_config.<key>}` 替换安装时配置。**没有自动前缀**——你的服务器读取的环境变量名称就是你放在 `env` 中的名称。

**`user_config`** — 安装时设置在主机UI中显示的设置。`type: "directory"` 渲染原生文件夹选择器。`sensitive: true` 存储在操作系统密钥链中。有关所有字段的详细信息，请参阅 `references/manifest-schema.md`。

---

## 服务器代码：与本地stdio相同

服务器本身是一个标准的stdio MCP服务器。工具逻辑中没有MCPB特定的内容。

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";

// ROOT_DIR 来自你放在manifest的 server.mcp_config.env 中——没有自动前缀
const ROOT = (process.env.ROOT_DIR ?? join(homedir(), "Documents"));

const server = new McpServer({ name: "local-files", version: "0.1.0" });

server.registerTool(
  "list_files",
  {
    description: "列出配置根目录下目录中的文件。",
    inputSchema: { path: z.string().default(".") },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const entries = await readdir(join(ROOT, path), { withFileTypes: true });
    const list = entries.map(e => ({ name: e.name, dir: e.isDirectory() }));
    return { content: [{ type: "text", text: JSON.stringify(list, null, 2) }] };
  },
);

server.registerTool(
  "read_file",
  {
    description: "读取文件的内容。路径相对于配置的根目录。",
    inputSchema: { path: z.string() },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const text = await readFile(join(ROOT, path), "utf8");
    return { content: [{ type: "text", text }] };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

**沙盒化完全是你的工作**。没有元数据级沙盒——进程以完整用户权限运行。验证路径，拒绝脱离 `ROOT`，允许列表启动。请参阅 `references/local-security.md`。

在从配置环境变量中硬编码 `ROOT` 之前，检查主机是否支持 `roots/list`——这是获取用户批准目录的规范原生方式。请参阅 `references/local-security.md` 中的模式。

---

## 构建管道

### Node

```bash
npm install
npx esbuild src/index.ts --bundle --platform=node --outfile=server/index.js
# 或者：如果原生依赖项难以捆绑，则整体复制 node_modules
npx @anthropic-ai/mcpb pack
```

`mcpb pack` 压缩目录并验证 `manifest.json` 是否符合模式。

### Python

```bash
pip install -t server/vendor -r requirements.txt
npx @anthropic-ai/mcpb pack
```

将依赖项打包到子目录中，并在你的入口脚本中预置 `sys.path`。原生扩展（numpy等）必须为每个目标平台构建——如果可以，请避免原生依赖项。

---

## MCPB没有沙盒——安全是靠你自己

与移动应用商店不同，MCPB**不强制执行权限**。元数据中没有 `permissions` 块——服务器以完整用户权限运行。`references/local-security.md` 是强制阅读，不是可选的。每条路径都必须验证，每个启动都必须允许列表，因为在平台级别没有任何东西可以阻止你。

如果你来到这里期待元数据中的文件系统/网络范围：它不存在。在工具处理程序中自己构建它。

如果你的服务器的唯一工作就是调用云API，停止——那是一个穿着MCPB服装的远程服务器。用户从本地运行它没有任何好处，而你无缘无故承担了本地安全负担。

---

## MCPB + UI小部件

MCPB服务器可以像远程MCP应用程序一样提供UI资源——小部件机制与传输无关。一个浏览实际磁盘的本地文件选择器，一个控制原生应用程序的对话框等。

小部件创作在 **`build-mcp-app`** 技能中涵盖；在这里它的工作方式相同。唯一的区别是服务器运行的位置。

---

## 测试

```bash
# 交互式元数据创建（第一次）
npx @anthropic-ai/mcpb init

# 直接通过stdio运行服务器，用检查器戳它
npx @modelcontextprotocol/inspector node server/index.js

# 验证元数据是否符合模式，然后打包
npx @anthropic-ai/mcpb validate
npx @anthropic-ai/mcpb pack

# 签名用于分发
npx @anthropic-ai/mcpb sign dist/local-files.mcpb

# 安装：将 .mcpb 文件拖到 Claude Desktop 上
```

在发布前在**没有**你的开发工具链的机器上测试。MCPB中的“在我的机器上工作”失败几乎总是追溯到没有实际捆绑的依赖项。

---

## 参考文件

- `references/manifest-schema.md` — 完整的 `manifest.json` 字段参考
- `references/local-security.md` — 路径遍历、沙盒化、最小权限
