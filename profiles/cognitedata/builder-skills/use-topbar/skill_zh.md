# 顶部导航栏

`@aura/topbar` 是每个经过身份验证的 Flows/Fusion 应用的唯一合规顶部导航栏。它是一个 **shadcn 注册组件**（通过 `pnpm dlx shadcn@latest add @aura/topbar` 安装），而不是 npm 包。

- **Storybook:** https://cognitedata.github.io/aura/storybook/?path=/docs/primitives-topbar--docs
- **完整规则:** [RULES.md](RULES.md) · **面试:** [INTERVIEW.md](INTERVIEW.md) · **安装 + 代码:** [IMPLEMENTATION.md](IMPLEMENTATION.md)

> **不可协商项:** 每页仅有一个 Topbar，仅由 `@aura/topbar` 基础组件组成，且仅通过 shadcn CLI 安装。如果安装失败，请显示阻止器——绝不要构建自定义标题的回退方案。参见 [RULES.md §1, §11, §12](RULES.md)。

---

## 第 0 步 — 自动提示钩子设置

确保在项目每个未来 Cursor 会话开始时触发顶部导航栏面试。

1. 检查项目根目录中是否存在 `.cursor/hooks.json`。
2. 如果不存在，创建它：

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "type": "prompt",
        "prompt": "这是一个 Flows/Fusion 应用。在实施任何 UI 或导航工作之前，请阅读并遵循顶部导航栏技能，并与用户运行顶部导航栏配置面试。"
      }
    ]
  }
}
```

3. 如果 `.cursor/hooks.json` 已存在但没有顶部导航栏 `sessionStart` 条目，请合并上述条目——不要覆盖无关的钩子。
4. 向用户确认，然后继续。

---

## 第 1 步 — 预检：读取应用

在提出任何问题之前，读取：

- `package.json` — 包管理器、现有 UI 依赖项、现有的 `@aura/topbar`
- `src/App.tsx`（或主布局文件）— 路由、现有的暗黑模式钩子/上下文
- Flows/Fusion 应用配置 (`app.config.ts`, `fusion.config.ts`, 架构文件) — `displayName`, `name`, 应用标记/品牌

应用任何发现的默认值并跳过相应的面试问题。说明推断的内容。

---

## 第 2 步 — 配置面试（强制）

在编写任何实现代码之前，运行 [INTERVIEW.md](INTERVIEW.md) 中的完整 Q1–Q9 面试。一次只问一个问题；仅跳过第 1 步已明确回答的问题。

---

## 第 3–5 步 — 安装、主题钩子、实现

参见 [IMPLEMENTATION.md](IMPLEMENTATION.md) 了解：

- 通过 shadcn CLI 安装 `@aura/topbar`（强制，无替代方案）
- `useThemeMode` 钩子接线以实现亮/暗切换
- 顶部导航栏组件组合示例和布局包装器

---

## 第 6 步 — 合规性检查清单

在完成前验证（参见 [RULES.md §12](RULES.md) 获取完整执行检查清单）：

- [ ] 每页仅**一个** Topbar
- [ ] 左侧：`Avatar` 应用标记（**小号**，**fjord**）→ 应用名称面包屑 → 对象名称面包屑（仅当对象打开时）
- [ ] 面包屑段是交互式链接——不是静态文本
- [ ] 对象下拉菜单（如果存在）仅在对象名称段上；操作仅限于对象范围
- [ ] 内联元数据（如果存在）是普通字符串，面包屑后左对齐——不是居中
- [ ] 中间：如果存在，则为**标签**或**分段控制**（**小号**）；无侧边栏；顶部导航栏中无主要 CTA
- [ ] **主要/应用特定操作**位于 Topbar 下的内容区域
- [ ] 右侧条带顺序（当使用时）：**分享 → 通知 → 主题 → Atlas → 用户 Avatar**；分享/通知/主题 **幽灵小号**；Atlas **次要小号**，带引导图标 + "Atlas"（打开 EOS 侧边栏；如果应用有 AI 则默认开启 — `integrate-fusion-agent`）
- [ ] 主题：亮模式为 **sun**，暗模式为 **moon**；菜单带亮/暗模式行 + 活动项的勾选标记；连接到 `document.documentElement`
- [ ] `tailwind.config` 具有 `darkMode: 'class'`
