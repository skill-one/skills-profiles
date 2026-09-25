# 浏览器预览

您已经知道 `preview_serve` 和 `preview_stop`。这项技能弥补了空白：`preview_serve` 返回 URL 后会发生什么——用户如何实际看到它。

## 预览面板是什么

前端有一个右侧面板，包含两个选项卡：**文件**和**预览**。预览选项卡在 iframe 内渲染预览 URL。当您调用 `preview_serve` 时，前端会自动打开一个加载该 URL 的预览选项卡。（现在任务通过左侧边栏的独立模态框管理，而不是在右侧面板中管理。）

要点：
- 每个 `preview_serve` 调用创建一个预览选项卡
- URL 格式：`https://<host>/preview/{id}/`
- 预览面板有一个 **⋮ 菜单**（右上角）显示 "RUNNING SERVICES" 列表
- 预览选项卡可以被用户关闭，而不会停止后端服务
- 后端服务停止 → 预览选项卡显示错误页面

## ⚠️ 关键：切勿告诉用户访问 localhost

**用户的浏览器无法访问 `localhost` 或 `127.0.0.1`。** 这些地址指向服务器容器，而不是用户的机器。预览架构使用一个**反向代理**：

```
用户的浏览器 → https://<host>/preview/{id}/path → (反向代理) → 127.0.0.1:{port}/path
```

规则：
- **绝不**告诉用户访问 `http://localhost:{port}` 或 `http://127.0.0.1:{port}`——他们无法访问
- **始终**引导用户到预览 URL：`/preview/{id}/`（或完整 URL `https://<host>/preview/{id}/`）
- `curl http://localhost:{port}` 仅用于**您自己的服务器端诊断**——切勿建议用户将其作为“测试”预览的方式
- 当预览运行时，告诉用户：“检查预览面板，或刷新预览面板”
- 如果您需要给用户提供 URL，请使用 `preview_serve` 返回的 `url` 字段（格式：`/preview/{id}/`）

## ⚠️ 静态资源必须使用相对路径

因为预览在 `/preview/{id}/` 下提供，**HTML/JS/CSS 中的绝对路径会失效**。反向代理在转发到后端之前会剥离 `/preview/{id}` 前缀，但浏览器从域名根目录解析绝对路径。

问题的示例：
```html
<!-- ❌ 破坏性：浏览器请求 https://host/static/app.js → 404（绕过预览代理） -->
<script src="/static/app.js"></script>

<!-- ✅ 正常：浏览器请求 https://host/preview/{id}/static/app.js → 正确代理 -->
<script src="static/app.js"></script>
<script src="./static/app.js"></script>
```

修复常见模式：
| 破坏性（绝对路径） | 修复（相对路径） |
|---|---|
| `"/static/app.js"` | `"static/app.js"` 或 `"./static/app.js"` |
| `"/api/users"` | `"api/users"` 或 `"./api/users"` |
| `"/images/logo.png"` | `"images/logo.png"` 或 `"./images/logo.png"` |
| `url('/fonts/x.woff')` | `url('./fonts/x.woff')` |
| `fetch('/data.json')` | `fetch('data.json')` |

**检查所有出现路径的地方**：
1. HTML `src`、`href` 属性
2. JavaScript `fetch()`、`XMLHttpRequest`、动态导入
3. CSS `url()` 引用
4. JavaScript 字符串字面量（例如，模板字符串或连接中的 `'/static/'`）
5. 框架配置文件（例如，`publicPath`、`base`、`assetPrefix`）

⚠️ 仔细检查——常见错误是修复 CSS `url()` 但遗漏 JS 字符串字面量（如 `'/static/'`，带单引号）。搜索所有文件类型中的绝对路径。

## ⚠️ 切勿浏览文件系统以调试预览

**切勿**查看工作区目录（如 `preview/`、`output/` 或随机文件夹）以了解预览状态。这些是用户数据，不是预览服务状态。

唯一的真相来源：
1. 注册文件：`/data/previews.json`（运行中的服务）
2. 历史文件：`/data/preview_history.json`（所有过去的服务）
3. `preview_serve` / `preview_stop` 工具
4. 通过 `curl` 进行端口检查（仅服务器端，用于您的诊断）

**切勿**在工作区目录上使用 `ls`/`find` 来诊断预览问题。**切勿**调用不相关的工具（如 `list_scheduled_tasks`）。保持专注。

## 分步指南：诊断预览问题

当用户报告任何预览面板问题时，请按以下精确顺序操作：

### 第 1 步：读取注册表（运行中的服务）

```bash
cat /data/previews.json 2>/dev/null || echo "NO_REGISTRY"
```

⚠️ 您的 bash 当前工作目录是 `/data/workspace/`。注册表位于 `/data/previews.json`（绝对路径，上一级）。始终使用绝对路径。

JSON 结构：
```json
{
  "previews": [
    {"id": "f343befc", "title": "My App", "dir": "/data/workspace/my-project", "command": "npm run dev", "port": 9080, "is_builtin": false}
  ]
}
```

### 第 2 步：根据注册表状态分支

**如果注册表有条目** → 转到第 3 步（验证服务）
**如果注册表为空或缺失** → 转到第 4 步（检查历史）

### 第 3 步：注册表有条目——验证和修复

对于注册表中的每个预览，检查端口是否在服务器端响应（这是您的诊断，不是给用户的）：
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:{port}
```

**如果端口响应（200）：**
- 服务正在运行。告诉用户：
  - "您有一个运行中的服务：{title}"
  - "点击预览面板右上角的 ⋮ 菜单，然后在 RUNNING SERVICES 列表中点击它以重新打开"
  - 预览 URL：`/preview/{id}/`
- **如果用户说 ⋮ 菜单为空或不显示服务** → 前端失去同步。通过 `preview_stop(id)` 然后 `preview_serve(dir, title, command)` 使用注册表中的信息修复。这会强制前端重新注册选项卡。

**如果端口不响应：**
- 进程崩溃但注册表条目仍然存在。重新创建：
  ```
  preview_stop(id="{id}")
  preview_serve(dir="{dir}", title="{title}", command="{command}")
  ```

### 第 4 步：没有运行中的服务——首先检查历史，然后扫描工作区

当没有运行中的服务时，使用**双层查找**查找用户可以预览的项目：

#### 第 1 层：读取预览历史（首选——快速且准确）

```bash
cat /data/preview_history.json 2>/dev/null || echo "NO_HISTORY"
```

JSON 结构：
```json
{
  "history": [
    {
      "id": "f343befc",
      "title": "Trading System",
      "dir": "/data/workspace/my-project",
      "command": "python main.py",
      "port": 8000,
      "is_builtin": false,
      "created_at": 1709100000.0,
      "last_started_at": 1709200000.0
    }
  ]
}
```

历史条目**永远不会**被 `preview_stop` 删除——它们跨重启持久存在。只有当项目目录不再存在时，才会自动修剪条目。

**如果历史有条目：**
- 列出所有历史条目给用户，包括标题、目录和最后启动时间
- 询问他们要重新启动哪个
- 使用历史条目中的 `dir`、`title` 和 `command` 调用 `preview_serve`

**如果用户说项目从历史中丢失** → 转到第 2 层。

#### 第 2 层：扫描工作区（备用——当历史为空或不完整时）

```bash
find /data/workspace -maxdepth 2 \( -name "package.json" -o -name "index.html" -o -name "*.html" -o -name "app.py" -o -name "main.py" -o -name "vite.config.*" \) -not -path "*/node_modules/*" -not -path "*/skills/*" -not -path "*/memory/*" -not -path "*/prompt/*" -not -path "*/.git/*" 2>/dev/null
```

然后：
1. 列出发现的项目的简要描述
2. 询问用户要预览哪个
3. 使用适当的目录调用 `preview_serve`

**不要只是说“没有运行的服务”然后停止。** 始终先检查历史，然后扫描，并提供选项。

## 快速参考

| 用户说 | 您做 |
|-----------|--------|
| "选项卡消失" / "选项卡不见了" | 第 1 步 → 2 → 3 或 4 |
| "空白页面" / "白屏" | 检查端口（服务器端），如果死亡 → 重新创建；如果存活 → 检查绝对路径问题 |
| "未更新" / "内容没更新" | 建议在预览选项卡中刷新按钮，或重新创建预览 |
| "端口冲突" / "端口冲突" | `preview_stop` 旧 → `preview_serve` 新 |
| "无法看到服务" / "⋮ 菜单为空" | `preview_stop` + `preview_serve` 以强制重新注册 |
| "我的项目在哪里" / "我构建了什么" | 读取 `/data/preview_history.json` 并列出条目 |
| "资源加载失败" / "JS/CSS 404" | 检查绝对路径（`/static/`、`/api/`），修复为相对路径 |

## 您无法做的事情

- 无法直接打开/关闭/刷新预览选项卡（前端 UI）
- 无法强制刷新 iframe
- 无法读取 iframe 显示的内容

当您无法做某事时，告诉用户手动操作（例如，“在预览选项卡中点击刷新”）。如果手动操作无效，使用 `preview_stop` + `preview_serve` 重新创建预览。

## 常见错误避免

1. ❌ 告诉用户“访问 http://localhost:18791/”——用户无法访问 localhost
2. ❌ 说“刷新 localhost 上的页面”——对用户来说毫无意义
3. ❌ 仅修复 CSS `url()` 路径但遗漏 JS 字符串字面量中的绝对路径
4. ❌ 忘记检查所有文件类型（HTML、JS、CSS、配置）中的绝对路径
5. ✅ 始终使用 `/preview/{id}/` 作为用户界面 URL
6. ✅ 仅使用 `curl localhost:{port}` 仅用于您自己的服务器端诊断
7. ✅ 修复路径后，调用 `preview_stop` + `preview_serve` 重新启动，然后告诉用户检查预览面板
