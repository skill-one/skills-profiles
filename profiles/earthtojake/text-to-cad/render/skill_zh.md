# 渲染

使用此技能在 CAD 探索器中打开生成的或修改的 CAD 和机器人描述文件。预期输入是一个或多个已存在的或由其他技能刚刚生成的明确文件路径。

支持的文件：`.step`、`.stp`、`.glb`、`.stl`、`.3mf`、`.dxf`、`.urdf`、`.srdf`、`.sdf`。

## 交接合约

- 从 CAD、URDF、SRDF、SDF、SendCutSend 或标准件工作流中接受明确文件路径。
- 使用 `dev:ensure` 启动或重用 CAD 探索器；不要假设固定端口。将 `dev:ensure` 视为返回链接的查看器活动检查。
- 将端口重用视为强制要求：如果 `dev:ensure` 报告本地绑定/探测拒绝，如 `EPERM` 或 `EACCES`，请重新运行具有所需本地绑定权限/提升的相同 `dev:ensure` 命令，而不是自己选择新端口。
- 不要使用 `npm run dev -- --port ...`、原始 `vite dev` 或原始 `vite preview` 进行正常代理交接；这些会绕过重用策略，并可能留下重复的 localhost 探索器服务器运行。
- 为每个请求的文件返回打印的探索器 URL。
- 对于生成审查或视觉反馈，优先使用快照 CLI 而不是手动打开查看器或使用 Playwright。查看器链接仍然返回以进行交接/实时审查。
- 仅在 CAD STEP 模块参数动画审查时生成 GIF。否则使用静态快照，而不是 GIF。
- 如果启动失败，报告失败并让拥有该技能继续进行非 GUI 验证。

## 命令

从此技能目录：

```bash
npm --prefix scripts/viewer run dev:ensure -- --file path/to/model.step
```

对于保存的头部快照，使用技能级别的快照包装器。它委托到查看器包的 `scripts/viewer/snapshot` 实现：

```bash
python3 scripts/snapshot --job path/to/render-job.json
python3 scripts/snapshot --job -
```

对于常见主题快照，提供快捷标志：

```bash
python3 scripts/snapshot \
  --input path/to/model.step \
  --output /tmp/model.png \
  --mode view \
  --theme technical \
  --camera iso \
  --view-labels
```

STEP 模块侧边栏参数可以通过 `--params` 供应静态或动画参数 GIF：

```bash
python3 scripts/snapshot \
  --input path/to/model.step \
  --output /tmp/model.png \
  --params '{"drive":180,"ringVisible":false}'

python3 scripts/snapshot \
  --input path/to/model.step \
  --output /tmp/model.gif \
  --params '{"values":{"ringVisible":true},"animate":{"drive":{"from":0,"to":1260}},"durationSeconds":6,"fps":18,"loop":true}'
```

快照 CLI 默认为 `--theme technical`，这是一个平面、高对比度的主题，旨在用于视觉诊断而不是演示。`--theme` 接受内置主题名称、内联 JSON 主题对象或 JSON 主题文件路径；将 `theme.display.mode` 设置为 `solid` 或 `wireframe` 以用于表面/线框输出。`--params` 针对探索器 `.step.js` STEP 模块侧边栏参数，而不是 Python/build123d 再生参数。快照 CLI 根据请求上下文选择默认尺寸，当省略宽度/高度时：诊断静态图像 1600x1200，简单无标签零件 1200x900，截面/标签/标注视图至少 1600x1200，复杂装配 1800x1200 或 1920x1440 通过 `render.sizeProfile`，演示渲染 2400x1600 或 2800x1800 通过 `render.sizeProfile`，STEP 模块参数 GIF 960x640，以及接触页至少 2400 px 宽。除非透明度回答了具体的重叠、碰撞或内部关系问题，否则保持透明快照为演示导向。使用 JSON 工作用于自定义主题设置、选择、截面、轨道设置、机器人关节值、STEP 模块参数、DXF 厚度/弯曲选项和多输出快照。支持的渲染模式是 `view`、`orbit`、`section` 和 `list`。支持的输入是 `.step`、`.stp`、`.glb`、`.stl`、`.3mf`、`.dxf`、`.urdf`、`.srdf` 和 `.sdf`。

当工作区根已知时，显式传递：

```bash
npm --prefix scripts/viewer run dev:ensure -- \
  --workspace-root /path/to/workspace \
  --file path/to/model.step
```

仅用于手动探索器开发时使用前景 Vite：

```bash
npm --prefix scripts/viewer run dev
```

`dev:ensure` 首先探测和检查注册的本地 CAD 探索器服务器，在其完整端口范围内，尽可能重用具有匹配扫描根的服务器，然后仅在第一个可用端口上启动分离的 Vite 服务器。使用它打印的 URL。

## MoveIt2 控制

对于 SRDF 探索器审查，仅在用户需要交互式 IK 或路径规划控制时启动 MoveIt2 服务器。SRDF 生成和普通探索器链接不需要它。

从此技能目录：

```bash
scripts/moveit2_server/setup.sh
scripts/moveit2_server/check-moveit2-server.sh
scripts/moveit2_server/run-moveit2-server.sh
```

服务器默认为 `ws://127.0.0.1:8765/ws`。CAD 探索器在本地开发中连接到该 URL，除非设置了 `EXPLORER_MOVEIT2_WS_URL` 或浏览器 `?moveit2Ws=` 查询覆盖。

有关协议和报告的详细信息，请阅读 `references/moveit2-server.md`。

有用的探索器环境变量：

```text
EXPLORER_PORT
EXPLORER_PORT_END
EXPLORER_ROOT_DIR
EXPLORER_DEFAULT_FILE
EXPLORER_WORKSPACE_ROOT
EXPLORER_GITHUB_URL
EXPLORER_MOVEIT2_WS_URL
EXPLORER_ALLOWED_HOSTS
EXPLORER_SERVER_REGISTRY
```

当通过 remotehost/Tailscale Serve 暴露 CAD 探索器时，在启动或重新启动 `dev:ensure` 之前将 `EXPLORER_ALLOWED_HOSTS` 设置为 Serve 域名：

```bash
EXPLORER_ALLOWED_HOSTS=macbook-pro-108.tail3c8ded.ts.net \
  npm --prefix scripts/viewer run dev:ensure -- \
    --workspace-root /path/to/workspace \
    --root-dir models \
    --file path/to/model.urdf
```

在返回远程链接之前，本地验证主机头路径：

```bash
curl -I -H 'Host: macbook-pro-108.tail3c8ded.ts.net' \
  'http://127.0.0.1:PORT/?file=path/to/model.urdf'
```

预期响应是 `200 OK`。

如果远程手机加载页面外壳但通过 Vite 开发服务器显示空白/黑色屏幕，尝试在生产预览之前进行更深入的渲染更改。使用相同的扫描根和默认文件构建，使用相同的 `EXPLORER_ALLOWED_HOSTS` 域名启动 `vite preview`，验证主机头路径，然后重新指向 remotehost/Tailscale Serve 到预览端口：

```bash
EXPLORER_WORKSPACE_ROOT=/path/to/workspace \
EXPLORER_ROOT_DIR=models \
EXPLORER_DEFAULT_FILE=robots/elrobot/elrobot-follower.urdf \
  npm --prefix scripts/viewer run build

cd scripts/viewer
EXPLORER_WORKSPACE_ROOT=/path/to/workspace \
EXPLORER_ROOT_DIR=models \
EXPLORER_DEFAULT_FILE=robots/elrobot/elrobot-follower.urdf \
EXPLORER_ALLOWED_HOSTS=macbook-pro-108.tail3c8ded.ts.net \
EXPLORER_PORT=4202 \
  npm exec vite preview -- --host 127.0.0.1 --port 4202 --strictPort
```

这从手机路径中移除了 Vite 的开发客户端和 HMR websocket，同时保留了相同的 `?file=` URL。

保持 GUI 工作轻量级：仅在需要链接/审查时启动服务器，优先使用 `dev:ensure` 进行代理工作流，除非用户要求，否则不要停止现有的探索器服务器。
