# 为用户设置添加环境变量

向服务器端添加环境变量以配置用户设置的默认值。

**优先级**: 用户自定义 > 服务器环境变量 > 硬编码默认值

## 步骤

### 1. 定义环境变量

创建 `packages/env/src/<域名>.ts`（导入路径保持 `@/envs/<域名>` — tsconfig 首先映射到 `packages/env/src/*`）：

```typescript
import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

export const get<域名>Config = () => {
  return createEnv({
    server: {
      YOUR_ENV_VAR: z.coerce.number().min(MIN).max(MAX).optional(),
    },
    runtimeEnv: {
      YOUR_ENV_VAR: process.env.YOUR_ENV_VAR,
    },
  });
};

export const <域名>Env = get<域名>Config();
```

### 2. 更新类型（如果新域名）

添加到 `packages/types/src/serverConfig.ts`：

```typescript
import { User<域名>Config } from './user/settings';

export interface GlobalServerConfig {
  <域名>?: PartialDeep<User<域名>Config>;
}
```

**优先重用现有的类型** 来自 `packages/types/src/user/settings`。

### 3. 组合服务器配置（如果新域名）

在 `apps/server/src/globalConfig/index.ts`：

```typescript
import { <域名>Env } from '@/envs/<域名>';

export const getServerGlobalConfig = async () => {
  const config: GlobalServerConfig = {
    <域名>: cleanObject({
      <设置名>: <域名>Env.YOUR_ENV_VAR,
    }),
  };
  return config;
};
```

### 4. 合并到用户存储（如果新域名）

在 `src/store/user/slices/common/action.ts`：

```typescript
const serverSettings: PartialDeep<UserSettings> = {
  <域名>: serverConfig.<域名>,
};
```

### 5. 更新 .env.example

```bash
# <描述>（范围/选项，默认：X）
# YOUR_ENV_VAR=<示例>
```

### 6. 更新文档

- `docs/self-hosting/environment-variables/basic.mdx` (EN)
- `docs/self-hosting/environment-variables/basic.zh-CN.mdx` (CN)

## 示例：AI_IMAGE_DEFAULT_IMAGE_NUM

```typescript
// packages/env/src/image.ts  (导入为 @/envs/image)
AI_IMAGE_DEFAULT_IMAGE_NUM: z.coerce.number().min(1).max(20).optional(),

// packages/types/src/serverConfig.ts
image?: PartialDeep<UserImageConfig>;

// apps/server/src/globalConfig/index.ts
image: cleanObject({ defaultImageNum: imageEnv.AI_IMAGE_DEFAULT_IMAGE_NUM }),

// src/store/user/slices/common/action.ts
image: serverConfig.image,

// .env.example
# AI_IMAGE_DEFAULT_IMAGE_NUM=4
```
