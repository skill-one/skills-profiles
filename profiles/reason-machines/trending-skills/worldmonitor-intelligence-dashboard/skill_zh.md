# 世界监控智能仪表盘

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能收集。

World Monitor 是一个实时全球智能仪表盘，结合了 AI 驱动的新闻聚合（435+ 数据源，15 个类别）、双地图引擎（3D 地球仪 + WebGL 平面地图，45 个数据层）、地缘政治风险评分、金融雷达（92 个交易所）和跨流信号关联 — 所有这些都来自一个可部署为 Web、PWA 或原生桌面（Tauri 2）的 TypeScript/Vite 代码库。

---

## 安装与快速入门

```bash
git clone https://github.com/koala73/worldmonitor.git
cd worldmonitor
npm install
npm run dev          # 打开 http://localhost:5173
```

基本操作不需要环境变量。默认情况下，所有功能都使用本地 Ollama。

### 网站变体

```bash
npm run dev:tech       # tech.worldmonitor.app 变体
npm run dev:finance    # finance.worldmonitor.app 变体
npm run dev:commodity  # commodity.worldmonitor.app 变体
npm run dev:happy      # happy.worldmonitor.app 变体
```

### 生产构建

```bash
npm run typecheck        # TypeScript 验证
npm run build:full       # 构建所有变体
npm run build            # 构建默认（world）变体
```

---

## 项目结构

```
worldmonitor/
├── src/
│   ├── components/       # UI 组件 (TypeScript)
│   ├── feeds/            # 435+ RSS/API 数据源定义
│   ├── layers/           # 地图数据层 (deck.gl)
│   ├── ai/               # AI 综合处理流程
│   ├── signals/          # 跨流关联引擎
│   ├── finance/          # 市场数据 (92 个交易所)
│   ├── variants/         # 网站变体配置 (world/tech/finance/commodity/happy)
│   └── protos/           # Protocol Buffer 定义 (92 个 proto，22 个服务)
├── api/                  # Vercel Edge Functions (60+)
├── src-tauri/            # Tauri 2 原生桌面应用 (Rust)
├── docs/                 # 文档源代码
└── vite.config.ts
```

---

## 环境变量

创建一个 `.env.local` 文件（永远不要提交密钥）：

```bash
# AI 提供商（全部可选 — Ollama 无需密钥）
VITE_OLLAMA_BASE_URL=http://localhost:11434       # 本地 Ollama 实例
VITE_GROQ_API_KEY=$GROQ_API_KEY                  # Groq 云推理
VITE_OPENROUTER_API_KEY=$OPENROUTER_API_KEY      # OpenRouter 多模型

# 缓存（可选，提升性能）
UPSTASH_REDIS_REST_URL=$UPSTASH_REDIS_REST_URL
UPSTASH_REDIS_REST_TOKEN=$UPSTASH_REDIS_REST_TOKEN

# 地图瓦片（可选，MapLibre GL）
VITE_MAPTILER_API_KEY=$MAPTILER_API_KEY

# 变体选择
VITE_SITE_VARIANT=world   # world | tech | finance | commodity | happy
```

---

## 核心概念

### 数据源类别

World Monitor 聚合了跨越 15 个类别的 435+ 数据源：

```typescript
// src/feeds/categories.ts 模式
import type { FeedCategory } from './types';

const FEED_CATEGORIES: FeedCategory[] = [
  'geopolitics',
  'military',
  'economics',
  'technology',
  'climate',
  'energy',
  'health',
  'finance',
  'commodities',
  'infrastructure',
  'cyber',
  'space',
  'diplomacy',
  'disasters',
  'society',
];
```

### 国家智能指数

每个国家在 12 个信号类别中的复合风险评分：

```typescript
// 示例：访问国家风险评分
import { CountryIntelligence } from './signals/country-intelligence';

const intel = new CountryIntelligence();

// 获取某个国家的复合风险评分
const score = await intel.getCountryScore('UA');
console.log(score);
// {
//   composite: 0.82,
//   signals: {
//     military: 0.91,
//     economic: 0.74,
//     political: 0.88,
//     humanitarian: 0.79,
//     ...
//   },
//   trend: 'escalating',
//   updatedAt: '2026-03-17T08:00:00Z'
// }

// 订阅实时更新
intel.subscribe('UA', (update) => {
  console.log('Risk update:', update);
});
```

### AI 综合处理流程

```typescript
// src/ai/synthesize.ts 模式
import { AISynthesizer } from './ai/synthesizer';

const synth = new AISynthesizer({
  provider: 'ollama',           // 'ollama' | 'groq' | 'openrouter'
  model: 'llama3.2',            // 任何 Ollama 兼容模型
  baseUrl: process.env.VITE_OLLAMA_BASE_URL,
});

// 从多个数据源项合成新闻摘要
const brief = await synth.synthesize({
  items: feedItems,             // FeedItem[]
  category: 'geopolitics',
  region: 'Europe',
  maxTokens: 500,
  language: 'en',
});

console.log(brief.summary);    // AI 生成的综合内容
console.log(brief.signals);    // 提取的信号数组
console.log(brief.confidence); // 0-1 置信度评分
```

### 跨流信号关联

```typescript
// src/signals/correlator.ts 模式
import { SignalCorrelator } from './signals/correlator';

const correlator = new SignalCorrelator();

// 检测军事、经济、灾害信号的收敛
const convergence = await correlator.detectConvergence({
  streams: ['military', 'economic', 'disaster', 'escalation'],
  timeWindow: '6h',
  threshold: 0.7,
  region: 'Middle East',
});

if (convergence.detected) {
  console.log('Convergence signals:', convergence.signals);
  console.log('Escalation probability:', convergence.probability);
  console.log('Contributing events:', convergence.events);
}
```

---

## 地图引擎集成

### 3D 地球仪 (globe.gl)

```typescript
// src/components/globe/GlobeView.ts
import Globe from 'globe.gl';
import { getCountryRiskData } from '../signals/country-intelligence';

export function initGlobe(container: HTMLElement) {
  const globe = Globe()(container)
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png');

  // 加载国家风险层
  const riskData = await getCountryRiskData();

  globe
    .polygonsData(riskData.features)
    .polygonCapColor(feat => riskToColor(feat.properties.riskScore))
    .polygonSideColor(() => 'rgba(0, 100, 0, 0.15)')
    .polygonLabel(({ properties: d }) =>
      `<b>${d.name}</b><br/>Risk: ${(d.riskScore * 100).toFixed(0)}%`
    );

  return globe;
}

function riskToColor(score: number): string {
  if (score > 0.8) return 'rgba(220, 38, 38, 0.8)';   // critical
  if (score > 0.6) return 'rgba(234, 88, 12, 0.7)';   // high
  if (score > 0.4) return 'rgba(202, 138, 4, 0.6)';   // elevated
  if (score > 0.2) return 'rgba(22, 163, 74, 0.5)';   // low
  return 'rgba(15, 118, 110, 0.4)';                    // minimal
}
```

### WebGL 平面地图 (deck.gl + MapLibre GL)

```typescript
// src/components/map/DeckMap.ts
import { Deck } from '@deck.gl/core';
import { ScatterplotLayer, ArcLayer, HeatmapLayer } from '@deck.gl/layers';
import maplibregl from 'maplibre-gl';

export function initDeckMap(container: HTMLElement) {
  const map = new maplibregl.Map({
    container,
    style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    center: [0, 20],
    zoom: 2,
  });

  const deck = new Deck({
    canvas: 'deck-canvas',
    initialViewState: { longitude: 0, latitude: 20, zoom: 2 },
    controller: true,
    layers: [
      // 事件散点层
      new ScatterplotLayer({
        id: 'events',
        data: getActiveEvents(),
        getPosition: d => [d.lng, d.lat],
        getRadius: d => d.severity * 50000,
        getFillColor: d => severityToRGBA(d.severity),
        pickable: true,
      }),
      // 供应链弧层
      new ArcLayer({
        id: 'supply-chains',
        data: getSupplyChainData(),
        getSourcePosition: d => d.source,
        getTargetPosition: d => d.target,
        getSourceColor: [0, 128, 200],
        getTargetColor: [200, 0, 80],
        getWidth: 2,
      }),
    ],
  });

  return { map, deck };
}
```

---

## 金融雷达

```typescript
// src/finance/radar.ts 模式
import { FinanceRadar } from './finance/radar';

const radar = new FinanceRadar();

// 获取市场综合指数（7 信号）
const composite = await radar.getMarketComposite();
console.log(composite);
// {
//   score: 0.62,
//   signals: {
//     volatility: 0.71,
//     momentum: 0.58,
//     sentiment: 0.65,
//     liquidity: 0.44,
//     correlation: 0.78,
//     macro: 0.61,
//     geopolitical: 0.82
//   },
//   exchanges: 92,
//   timestamp: '2026-03-17T08:00:00Z'
// }

// 监控特定交易所
const exchange = await radar.getExchange('NYSE');
const crypto = await radar.getCrypto(['BTC', 'ETH', 'SOL']);
const commodities = await radar.getCommodities(['GOLD', 'OIL', 'WHEAT']);
```

---

## 语言与 RTL 支持

World Monitor 支持 21 种语言，并提供本地语言数据源：

```typescript
// src/i18n/config.ts 模式
import { setLanguage, getAvailableLanguages } from './i18n';

const languages = getAvailableLanguages();
// ['en', 'ar', 'zh', 'ru', 'fr', 'es', 'de', 'ja', 'ko', 'pt',
//  'hi', 'fa', 'tr', 'pl', 'uk', 'nl', 'sv', 'he', 'it', 'vi', 'id']

// 切换语言（自动处理 RTL 布局）
await setLanguage('ar');  // 阿拉伯语 — 触发 RTL 布局
await setLanguage('he');  // 希伯来语 — 触发 RTL 布局
await setLanguage('fa');  // 波斯语 — 触发 RTL 布局

// 配置数据源语言过滤
import { FeedManager } from './feeds/manager';
const feeds = new FeedManager({ language: 'ar', includeEnglish: true });
```

---

## Protocol Buffers (API 合约)

```typescript
// src/protos — 92 个 proto 定义，22 个服务
// 示例生成的客户端使用：

import { IntelligenceServiceClient } from './protos/generated/intelligence_grpc_web_pb';
import { CountryRequest } from './protos/generated/intelligence_pb';

const client = new IntelligenceServiceClient(
  process.env.VITE_API_BASE_URL || 'http://localhost:8080'
);

const request = new CountryRequest();
request.setCountryCode('DE');
request.setTimeRange('24h');
request.setSignalTypes(['military', 'economic', 'political']);

client.getCountryIntelligence(request, {}, (err, response) => {
  if (err) console.error(err);
  else console.log(response.toObject());
});
```

---

## Vercel Edge 函数模式

```typescript
// api/feeds/aggregate.ts — Edge 函数示例
import type { VercelRequest, VercelResponse } from '@vercel/node';
import { aggregateFeeds } from '../../src/feeds/aggregator';
import { getCachedData, setCachedData } from '../../src/cache/redis';

export const config = { runtime: 'edge' };

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { category, region, limit = '20' } = req.query as Record<string, string>;

  const cacheKey = `feeds:${category}:${region}:${limit}`;
  const cached = await getCachedData(cacheKey);
  if (cached) return res.json(cached);

  const items = await aggregateFeeds({
    categories: category ? [category] : undefined,
    region,
    limit: parseInt(limit),
  });

  await setCachedData(cacheKey, items, { ttl: 300 }); // 5 分钟 TTL
  return res.json(items);
}
```

---

## 原生桌面应用 (Tauri 2)

```bash
# 安装 Tauri CLI
cargo install tauri-cli

# 开发
npm run tauri:dev

# 构建原生应用
npm run tauri:build
# 输出: .exe (Windows), .dmg/.app (macOS), .AppImage (Linux)
```

```rust
// src-tauri/src/main.rs — IPC 命令示例
#[tauri::command]
async fn fetch_intelligence(country: String) -> Result<CountryData, String> {
    // Sidecar Node.js 进程处理数据源聚合
    // Tauri 处理渲染器与后端之间的安全 IPC
    Ok(CountryData::default())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![fetch_intelligence])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## Docker / 自托管

```bash
# 单容器 Docker
docker build -t worldmonitor .
docker run -p 3000:3000 \
  -e VITE_SITE_VARIANT=world \
  -e UPSTASH_REDIS_REST_URL=$UPSTASH_REDIS_REST_URL \
  -e UPSTASH_REDIS_REST_TOKEN=$UPSTASH_REDIS_REST_TOKEN \
  worldmonitor

# Docker Compose 配合 Redis
docker compose up -d
```

```yaml
# docker-compose.yml
version: '3.9'
services:
  app:
    build: .
    ports: ['3000:3000']
    environment:
      - VITE_SITE_VARIANT=world
      - REDIS_URL=redis://redis:6379
    depends_on: [redis]
  redis:
    image: redis:7-alpine
    volumes: ['redis_data:/data']
volumes:
  redis_data:
```

### Vercel 部署

```bash
npm i -g vercel
vercel --prod
# 在 Vercel 控制面板或通过 CLI 设置环境变量：
vercel env add GROQ_API_KEY production
vercel env add UPSTASH_REDIS_REST_URL production
vercel env add UPSTASH_REDIS_REST_TOKEN production
```

---

## 常见模式

### 自定义数据源集成

```typescript
// 向聚合流程添加自定义 RSS 数据源
import { FeedRegistry } from './src/feeds/registry';

FeedRegistry.register({
  id: 'my-custom-feed',
  name: '我的情报来源',
  url: 'https://example.com/feed.xml',
  category: 'geopolitics',
  region: 'Asia',
  language: 'en',
  weight: 0.8,           // 0-1，影响信号权重
  refreshInterval: 300,  // 秒
  parser: 'rss2',        // 'rss2' | 'atom' | 'json'
});
```

### 自定义地图层

```typescript
// 在 45 层系统注册自定义 deck.gl 层
import { LayerRegistry } from './src/layers/registry';
import { IconLayer } from '@deck.gl/layers';

LayerRegistry.register({
  id: 'my-custom-layer',
  name: '自定义事件',
  category: 'infrastructure',
  defaultVisible: false,
  factory: (data) => new IconLayer({
    id: 'my-custom-layer-deck',
    data,
    getPosition: d => [d.lng, d.lat],
    getIcon: d => 'marker',
    getSize: 32,
    pickable: true,
  }),
});
```

### 网站变体配置

```typescript
// src/variants/my-variant.ts
import type { SiteVariant } from './types';

export const myVariant: SiteVariant = {
  id: 'my-variant',
  name: '我的监控',
  title: '我的自定义监控',
  defaultCategories: ['geopolitics', 'economics', 'military'],
  defaultRegion: 'Europe',
  defaultLanguage: 'en',
  mapStyle: 'dark',
  enabledLayers: ['country-risk', 'events', 'supply-chains'],
  aiProvider: 'ollama',
  theme: {
    primary: '#0891b2',
    background: '#0f172a',
    surface: '#1e293b',
  },
};
```

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 地图未渲染 | 检查 `VITE_MAPTILER_API_KEY` 或使用免费 CartoBasemap 样式 |
| AI 综合处理缓慢/失败 | 确保 Ollama 正在运行：`ollama serve && ollama pull llama3.2` |
| 数据源返回 429 错误 | 通过 `UPSTASH_REDIS_REST_*` 环境变量启用 Redis 缓存 |
| 原生应用无法构建 | 确保 Rust + `cargo install tauri-cli` + 平台构建工具 |
| RTL 布局损坏 | 确认 `setLanguage()` 设置了 `<html>` 的 `lang` 属性 |
| 构建时 TypeScript 错误 | 运行 `npm run typecheck` — proto 生成的文件必须存在 |
| Redis 连接被拒绝 | 检查 `REDIS_URL` 或使用 Upstash REST API 替代 TCP |
| `npm run build:full` 构建中途失败 | 单独构建变体：`npm run build -- --mode finance` |

### 本地 AI 的 Ollama 设置

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取推荐模型
ollama pull llama3.2          # 快速，质量良好
ollama pull mistral           # 替代方案
ollama pull gemma2:9b         # 更大，质量更高

# 验证 Ollama 可访问性
curl http://localhost:11434/api/tags
```

### 验证安装

```bash
npm run typecheck   # 应退出 0
npm run dev         # 应打开 localhost:5173
# 访问 /api/health 查看API状态
curl http://localhost:5133/api/health
```

---

## 资源

- **在线应用**: [worldmonitor.app](https://worldmonitor.app)
- **文档**: [docs.worldmonitor.app](https://docs.worldmonitor.app)
- **架构**: [docs.worldmonitor.app/architecture](https://docs.worldmonitor.app/architecture)
- **自托管指南**: [docs.worldmonitor.app/getting-started](https://docs.worldmonitor.app/getting-started)
- **贡献**: [docs.worldmonitor.app/contributing](https://docs.worldmonitor.app/contributing)
- **安全策略**: [SECURITY.md](https://github.com/koala73/worldmonitor/blob/main/SECURITY.md)
- **许可证**: AGPL-3.0（非商业）；SaaS/重品牌需要商业许可证
