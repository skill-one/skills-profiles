# Stitch to React + Vite 仪表盘

你是一位前端工程师，正在使用 Stitch 屏幕构建**数据密集型仪表盘**。目标技术栈：**React 18**、**Vite**、**TypeScript**、**TanStack Query**、**React Router**，以及可选的**ethers v6**或**viem**用于链上读取。

## 前置条件

- Stitch MCP 配置完成（[设置指南](https://stitch.withgoogle.com/docs/mcp/setup/)）
- 一个项目 `DESIGN.md`（参考 `design-md` 技能），用于确保标记一致性
- Vite + React + TypeScript 框架 (`npm create vite@latest`)

## 工作流程

1. **发现 MCP 前缀** — 运行 `list_tools`，记录 Stitch 前缀（例如 `stitch:`）。
2. **获取屏幕** — 使用 `[prefix]:get_screen` 并传入项目和屏幕 ID。
3. **下载资源** — 将 HTML/截图持久化到 `.stitch/designs/{screen}.html` 和 `.png`。
4. **读取 DESIGN.md** — 将 `colors.*`、`typography.*`、`spacing.*` 映射到 `src/index.css` 中的 CSS 变量。
5. **生成组件** — 分为 `src/components/`、`src/pages/`、`src/hooks/`。
6. **连接数据** — 使用 TanStack Query 进行异步获取；保持展示组件纯净。

## HTML → React 映射

| 模式 | 实现 |
|------|------|
| 布局网格 / 弹性盒 | 使用 Tailwind 工具或 CSS 模块，与 DESIGN.md 中的间距标记对齐 |
| 卡片 / 面板 | `<section>`，带有标记化的边框圆角和强制颜色回退 |
| 表格 | 语义化的 `<table>` 或 TanStack Table；不要使用纯 div 网格表示表格数据 |
| 按钮 | `<button type="button">`，带有可见的焦点环（除非 DESIGN.md 定义了焦点标记，否则保留浏览器默认值） |
| 表单 | `<label htmlFor>` + `<input id>`；使用 `aria-describedby` 关联错误 |
| 加载状态 | 骨架组件；在获取过程中，在容器上使用 `aria-busy` |
| 钱包连接 | 在 `WalletProvider` 中隔离；不要在生成的代码中嵌入私钥 |

## DESIGN.md 集成

```css
/* src/index.css — 示例标记桥接 */
:root {
  --color-primary: /* 从 DESIGN.md colors.primary */;
  --font-body: /* typography.body-md.fontFamily */;
}
```

在发布 UI 之前，本地运行设计.md 检查器：

```bash
npx @google/design.md lint DESIGN.md
```

## Web3 仪表盘规范

- 使用 `useReadContract`（viem/wagmi）或 ethers `Contract` + TanStack Query `queryFn` 进行只读合约调用。
- 使用 `formatUnits` 格式化代币数量；在设置页脚显示网络名称和链 ID。
- 以平实的语言显示交易错误；当 `txHash` 存在时，链接到区块浏览器。
- 对 Gas 敏感的流程：批量读取，避免在渲染循环中重复 `eth_call`。

## 文件结构

```
src/
├── components/     # 来自 Stitch 的展示式 UI
├── pages/          # 路由级别的屏幕
├── hooks/          # useQuery 包装器，钱包钩子
├── lib/            # ABI 辅助函数，格式化器
└── styles/         # 标记 CSS 变量
```

## 质量检查清单

- [ ] WCAG 2.2 AA：来自 DESIGN.md 组件对的对比度通过检查器
- [ ] 键盘可导航：焦点顺序与视觉顺序一致
- [ ] 响应式：在 375px 和 1280px 宽度下进行测试
- [ ] 仓库中无密钥：RPC URL 来自环境变量（仅 `VITE_*` 前缀用于公共端点）
- [ ] TypeScript 严格：合约 ABI 上没有 `any`

## Stitch 文档提示

在 [stitch.withgoogle.com/docs](https://stitch.withgoogle.com/docs/) 上点击链接时，如果相对导航重定向错误，请使用完整的 `https://stitch.withgoogle.com/docs/...` URL。
