# 调试包使用指南

## 基本使用

```typescript
import debug from 'debug';

// 格式：lobe-[模块]:[子模块]
const log = debug('lobe-server:market');

log('简单消息');
log('带变量：%O', object);
log('格式化数字：%d', number);
```

## 命名空间规范

- 桌面端：`lobe-desktop:[模块]`
- 服务器端：`lobe-server:[模块]`
- 客户端：`lobe-client:[模块]`
- 路由器：`lobe-[类型]-router:[模块]`

## 格式说明符

- `%O` - 展开对象（推荐用于复杂对象）
- `%o` - 对象
- `%s` - 字符串
- `%d` - 数字

## 启用调试输出

### 浏览器

```javascript
localStorage.debug = 'lobe-*';
```

### Node.js

```bash
DEBUG=lobe-* npm run dev
DEBUG=lobe-* pnpm dev
```

### Electron

```typescript
process.env.DEBUG = 'lobe-*';
```

## 示例

```typescript
// src/server/routers/edge/market/index.ts
import debug from 'debug';

const log = debug('lobe-edge-router:market');

log('getAgent 输入：%O', input);
```
