# Draw.io 架构工作室

生成可编辑的 `.drawio` 文件，而不是扁平化的图片。首选的入口点是 `scripts/diagramctl.py`，它统一了生成、增量同步、多视图投影、语义查询/测试/评审、故障分析以及在共享图表 IR 上的可访问发布。

## 选择工作流程

| 请求类型 | 路径 |
| --- | --- |
| 带精确样式的自然语言图表 | 阅读 `references/diagram-types.md`，然后 `references/xml-authoring.md` 并编写 XML |
| 无特殊样式的标准流程图/思维导图/Gantt/时间线等 | 如果 draw.io >=30，阅读 `references/mermaid-authoring.md` 并将 Mermaid 转换为原生 `.drawio` |
| 需要自动布局的大型图表（约15+节点） | 使用 `autolayout.py`；在传递任何 `--layout` 值之前，阅读 `references/autolayout.md` |
| 代码、Terraform、K8s、compose、SQL、OpenAPI、AsyncAPI 或 CI 源 | 使用 `diagramctl.py build`；阅读 `references/diagram-ir.md` |
| Protocol Buffers 模式（.proto） | 使用 `protoimports.py` 或 `diagramctl.py build`；阅读 `references/toolbox.md` |
| GraphQL SDL 模式（.graphql/.gql）或内省 JSON | 使用 `graphqlerd.py` 或 `diagramctl.py build`；阅读 `references/toolbox.md` |
| 运行的集群/堆栈/云（实际状态，而不是声明配置） | 阅读 `references/live-infra.md`，然后使用 `tfstate.py`、`dockerimports.py` 或 `k8simports.py -` |
| 更新生成的图表而不丢失手动布局 | 使用 `diagramctl.py sync`；阅读 `references/diagram-ir.md` |
| 高管/系统/部署/数据流/安全视图 | 使用 `diagramctl.py views`；阅读 `references/diagram-ir.md` |
| 查询、架构策略、评审、假设或引导式演练 | 阅读 `references/semantic-workflows.md` |
| MCP 主机（Claude 桌面版、Cursor、VS Code、Codex）应调用这些工作流程 | 注册 `scripts/diagramctl_mcp.py`；阅读 `references/mcp.md` |
| 图表类型或语义工作流程的提示措辞 | 阅读 `references/cookbook.md` |
| 在 GitHub Actions CI 中强制执行架构规则或视觉差异 | 阅读 `references/ci-gate.md` |
| 作为 PR 评审评论的渲染前/后/差异图像 | 使用 `prdiff.py`；阅读 `references/pr-bot.md` |
| 现有的 `.drawio` 到 HTML/PPTX/Mermaid/Markdown/动画/运行手册 | 阅读 `references/toolbox.md`；`diagramctl.py transform` 暴露现有工具 |
| 绘制为地铁/地铁地图的管道、旅程或子系统地图 | 使用 `tubemap.py`；阅读 `references/tubemap.md` |
| 图形、云/供应商、AI 或 Databricks 图标 | 阅读 `references/shapes.md` 或 `references/databricks.md`；永远不要猜测图形名称 |
| 学习/应用/管理视觉样式 | 阅读 `references/style-presets.md` |
| 从现有图表或主题中提取可重用的样式 | 阅读 `references/style-extraction.md` |
| 现有图像到可编辑图表（截图、白板照片、遗留 PNG） | 阅读 `references/derasterize.md` |
| 导出/平台问题 | 阅读 `references/troubleshooting.md`；对于访问/网络问题，阅读 `references/security.md` |

## 统一 CLI

从该技能目录运行，或将 `scripts/` 替换为此技能的脚本目录的绝对路径：

```bash
python3 scripts/diagramctl.py doctor
python3 scripts/diagramctl.py build model.json --from ir -o architecture.drawio
python3 scripts/diagramctl.py build ./infra --from terraform --group \
  --ir-output architecture.ir.json -o architecture.drawio
python3 scripts/diagramctl.py sync architecture.drawio ./infra --from terraform \
  -o architecture.next.drawio
python3 scripts/diagramctl.py views architecture.ir.json \
  --views executive,system,deployment,dataflow,security -o views.drawio
python3 scripts/diagramctl.py test architecture.drawio --rules policy.yml
python3 scripts/diagramctl.py review architecture.drawio -o review.md
python3 scripts/diagramctl.py query architecture.drawio --from internet --to orders-db
python3 scripts/diagramctl.py whatif architecture.ir.json --fail kafka \
  --drawio kafka-failure.drawio -o impact.json
python3 scripts/diagramctl.py story architecture.ir.json -o walkthrough.html
```

`doctor` 除非传递 `--probe`，否则不会启动 GUI 工具。核心语义命令是离线的，仅使用标准库。

## 创建工作流程

1. 从请求中推断图表类型、受众、范围、输出格式和位置。仅在缺少选择实质性改变结果时才询问；默认为工作目录中的 PNG 和 `.drawio`。
2. 从上表中选择编写路径。对于数据支持的图表，优先使用图表 IR 并保留来源。对于大型图表，使用导入器或 `autolayout.py`；不要手动放置超过大约十五个节点。
3. 解析明确命名的样式预设，或用户默认预设，如 `references/style-presets.md` 中所述。结构化图表约定和视觉预设组合；它们不互相替换。
4. 生成 `.drawio`，然后运行结构验证：

   ```bash
   python3 scripts/validate.py diagram.drawio --score
   ```

   当语义元数据或架构策略在范围内时，也运行 `diagramctl.py test`。不要将推断的语义发现呈现为已验证的运行时事实。
5. 导出一个不带嵌入式 XML 的草稿 PNG 并进行视觉检查。修复明显的重叠、裁剪、断开连接的边、边穿过节点路由、堆叠的边和难以读取的标签。在两轮后停止自动视觉修复。当 drawio 二进制文件不可用或视觉检查结果不确定时，验证渲染器自身的 DOM（在查看器 URL 上使用 `--dump-dom`，见 `references/troubleshooting.md`）：直接读取每个边的 `<path>` 段和标签锚坐标——仅靠视觉会遗漏几何缺陷并虚构新的缺陷。
6. 显示草稿并应用有针对性的编辑。保留现有几何形状进行本地更改。使用 `sync` 进行源支持的更改并编写可评审的输出；仅在请求删除时才使用 `--prune`。
7. 批准后，创建最终请求的格式并报告可编辑源和导出路径。

## 导出不变量

一次性解析可用二进制文件（`drawio`、`draw.io`、macOS 应用路径或 Windows 可执行文件），并使用该确切二进制文件运行。

```bash
# 用于视觉检查的草稿：此处永远不要使用 -e
drawio -x -f png --width 2000 -o diagram.png diagram.drawio

# 最终可编辑 PNG
drawio -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio
python3 scripts/repair_png.py diagram.drawio.png

# 最终可编辑 SVG/PDF
drawio -x -f svg -e --embed-svg-images -o diagram.svg diagram.drawio
drawio -x -f pdf -e -o diagram.pdf diagram.drawio
```

不要组合 `--width` 和 `-s`。嵌入式 PNG 导出需要 `repair_png.py`；用于视觉的草稿 PNG 不能使用 `-e`。在 Linux 无头环境下，请遵循 `references/troubleshooting.md` 而不是临时拼凑 Electron 标志。如果 CLI 在 macOS 沙盒中崩溃，尝试一次允许的升级运行，然后使用 `encode_drawio_url.py` 或提供 XML；不要重复启动它。

## 编辑和身份

- 使用稳定的语义 ID，并永远不要重用保留 ID `0` 或 `1`。
- 每条边都需要 `<mxGeometry relative="1" as="geometry"/>`。
- 对于本地编辑，仅更改匹配的单元格；对于全局方向更改，重新生成/重新布局页面。
- 保留来源、`data-model-id`、语义属性、手动几何形状和手动样式，除非用户请求否则不变。
- 在协调时，默认情况下将删除保留为可评审的淡化元素。
- 对于边界处堆叠的边，运行 `edgeports.py`；当边仍然穿过不相关的形状时添加航点。没有仅 CLI 的边重路由器可以保留节点位置。

## 质量和信任

一个吸引人的图表仍然可能是错误的。优先使用源支持的关联，在有用处时显示来源，区分精确提取和 AI 推断，并将架构评审发现作为提示。故事 HTML 必须保持自包含、键盘可用，并包含文本替代。永远不要在节点属性或来源中包含秘密，因为它们嵌入在输出中。

对于所有专注脚本和组合模式，阅读 `references/toolbox.md`；仅加载当前请求所需的特定任务参考。
