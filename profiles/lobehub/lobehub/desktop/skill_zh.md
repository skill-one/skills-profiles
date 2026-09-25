# 桌面开发指南

## 架构概述

LobeHub 桌面端基于 Electron 构建，采用主进程-渲染进程架构：

1. **主进程** (`apps/desktop/src/main`)：应用生命周期、系统 API、窗口管理
2. **渲染进程**：复用 `src/` 中的 Web 代码
3. **预加载脚本** (`apps/desktop/src/preload`)：安全地向渲染进程暴露主进程

## 添加新的桌面功能

### 1. 创建控制器

位置：`apps/desktop/src/main/controllers/`

```typescript
import { ControllerModule, IpcMethod } from '@/controllers';

export default class NewFeatureCtr extends ControllerModule {
  static override readonly groupName = 'newFeature';

  @IpcMethod()
  async doSomething(params: SomeParams): Promise<SomeResult> {
    // 实现
    return { success: true };
  }
}
```

在 `apps/desktop/src/main/controllers/registry.ts` 中注册。

### 2. 定义 IPC 类型

位置：`packages/electron-client-ipc/src/types.ts`

```typescript
export interface SomeParams {
  /* ... */
}
export interface SomeResult {
  success: boolean;
  error?: string;
}
```

### 3. 创建渲染器服务

位置：`src/services/electron/`

```typescript
import { ensureElectronIpc } from '@/utils/electron/ipc';

const ipc = ensureElectronIpc();

export const newFeatureService = async (params: SomeParams) => {
  return ipc.newFeature.doSomething(params);
};
```

### 4. 实现 Store Action

位置：`src/store/`

### 5. 添加测试

位置：`apps/desktop/src/main/controllers/__tests__/`

## 详细指南

具体主题请参阅 `references/`：

- **功能实现**：`references/feature-implementation.md`
- **本地工具工作流**：`references/local-tools.md`
- **菜单配置**：`references/menu-config.md`
- **窗口管理**：`references/window-management.md`

## 最佳实践

1. **安全**：验证输入、限制暴露的 API
2. **性能**：使用异步方法、批量数据传输
3. **用户体验**：添加进度指示器、提供错误反馈
4. **代码组织**：遵循现有模式、添加文档
