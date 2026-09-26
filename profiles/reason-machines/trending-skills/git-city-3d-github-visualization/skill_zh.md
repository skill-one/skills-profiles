# Git City — 3D GitHub Profile 可视化

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Git City 将 GitHub 个人资料转化为一个 3D 像素艺术城市。每个用户都成为一个独特的建筑：高度来自贡献量，宽度来自仓库数量，窗户亮度来自星标。使用 Next.js 16（应用路由器）、React Three Fiber 和 Supabase 构建。

## 快速设置

```bash
git clone https://github.com/srizzon/git-city.git
cd git-city
npm install

# 复制环境变量模板
cp .env.example .env.local   # Linux/macOS
copy .env.example .env.local  # Windows CMD
Copy-Item .env.example .env.local  # PowerShell

npm run dev
# → http://localhost:3001
```

## 环境变量

复制 `.env.local` 后填写：

```bash
# Supabase — 项目设置 → API
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# GitHub — 设置 → 开发者设置 → 个人访问令牌
GITHUB_TOKEN=github_pat_your_token_here

# 可选：用于 /admin/ads 访问的逗号分隔的 GitHub 登录名
ADMIN_GITHUB_LOGINS=your_github_login
```

**查找 Supabase 值**：控制台 → 项目设置 → API  
**查找 GitHub 令牌**：github.com → 设置 → 开发者设置 → 个人访问令牌（推荐精细权限）

## 项目结构

```
git-city/
├── app/                    # Next.js 应用路由器页面
│   ├── page.tsx            # 主城市视图
│   ├── [username]/         # 用户资料页面
│   ├── compare/            # 并排比较模式
│   └── admin/              # 管理面板
├── components/
│   ├── city/               # 3D 城市场景组件
│   │   ├── Building.tsx    # 单个建筑网格
│   │   ├── CityScene.tsx   # 主 R3F 画布/场景
│   │   └── LODManager.tsx  # 细节层次系统
│   ├── ui/                 # 2D 叠加 UI 组件
│   └── profile/            # 资料页面组件
├── lib/
│   ├── github.ts           # GitHub API 辅助函数
│   ├── supabase/           # Supabase 客户端 + 服务器工具
│   ├── buildings.ts        # 建筑指标计算
│   └── achievements.ts     # 成就逻辑
├── hooks/                  # 自定义 React 钩子
├── types/                  # TypeScript 类型定义
└── public/                 # 静态资源
```

## 核心概念

### 建筑指标映射

建筑根据 GitHub 个人资料数据生成：

```typescript
// lib/buildings.ts 模式
interface BuildingMetrics {
  height: number;      // 基于 总贡献量
  width: number;       // 基于 公开仓库数量
  windowBrightness: number;  // 基于 收到的总星标
  windowPattern: number[];   // 基于 最近活动模式
}

function calculateBuildingMetrics(profile: GitHubProfile): BuildingMetrics {
  const height = Math.log10(profile.totalContributions + 1) * 10;
  const width = Math.min(Math.ceil(profile.publicRepos / 10), 8);
  const windowBrightness = Math.min(profile.totalStars / 1000, 1);
  
  return { height, width, windowBrightness, windowPattern: [] };
}
```

### 3D 建筑组件（React Three Fiber）

```tsx
// components/city/Building.tsx 模式
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface BuildingProps {
  position: [number, number, number];
  metrics: BuildingMetrics;
  username: string;
  isSelected?: boolean;
  onClick?: () => void;
}

export function Building({ position, metrics, username, isSelected, onClick }: BuildingProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // 选中建筑的动画
  useFrame((state) => {
    if (meshRef.current && isSelected) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime) * 0.05;
    }
  });

  return (
    <group position={position} onClick={onClick}>
      {/* 主建筑体 */}
      <mesh ref={meshRef}>
        <boxGeometry args={[metrics.width, metrics.height, metrics.width]} />
        <meshStandardMaterial color="#1a1a2e" />
      </mesh>
      
      {/* 窗户作为实例网格以提高性能 */}
      <WindowInstances metrics={metrics} />
    </group>
  );
}
```

### 实例网格用于性能优化

Git City 使用实例渲染窗户——对于包含许多建筑的城市场景至关重要：

```tsx
// components/city/WindowInstances.tsx 模式
import { useRef, useEffect } from 'react';
import { InstancedMesh, Matrix4, Color } from 'three';

export function WindowInstances({ metrics }: { metrics: BuildingMetrics }) {
  const meshRef = useRef<InstancedMesh>(null);
  
  useEffect(() => {
    if (!meshRef.current) return;
    
    const matrix = new Matrix4();
    const color = new Color();
    let index = 0;
    
    // 根据建筑尺寸计算窗户位置
    for (let floor = 0; floor < metrics.height; floor++) {
      for (let col = 0; col < metrics.width; col++) {
        const isLit = metrics.windowPattern[index] > 0.5;
        
        matrix.setPosition(col * 1.1 - metrics.width / 2, floor * 1.2, 0.51);
        meshRef.current.setMatrixAt(index, matrix);
        meshRef.current.setColorAt(
          index,
          color.set(isLit ? '#FFD700' : '#1a1a2e')
        );
        index++;
      }
    }
    
    meshRef.current.instanceMatrix.needsUpdate = true;
    if (meshRef.current.instanceColor) {
      meshRef.current.instanceColor.needsUpdate = true;
    }
  }, [metrics]);

  const windowCount = Math.floor(metrics.height) * metrics.width;
  
  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, windowCount]}>
      <planeGeometry args={[0.4, 0.5]} />
      <meshBasicMaterial />
    </instancedMesh>
  );
}
```

### GitHub API 集成

```typescript
// lib/github.ts 模式
import { Octokit } from '@octokit/rest';

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

export async function fetchGitHubProfile(username: string) {
  const [userResponse, reposResponse] = await Promise.all([
    octokit.users.getByUsername({ username }),
    octokit.repos.listForUser({ username, per_page: 100, sort: 'updated' }),
  ]);

  const totalStars = reposResponse.data.reduce(
    (sum, repo) => sum + (repo.stargazers_count ?? 0),
    0
  );

  return {
    username: userResponse.data.login,
    avatarUrl: userResponse.data.avatar_url,
    publicRepos: userResponse.data.public_repos,
    followers: userResponse.data.followers,
    totalStars,
  };
}

export async function fetchContributionData(username: string): Promise<number> {
  // 使用 GitHub GraphQL 获取贡献日历数据
  const query = `
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
  `;
  
  const response = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, variables: { username } }),
  });
  
  const data = await response.json();
  return data.data.user.contributionsCollection.contributionCalendar.totalContributions;
}
```

### Supabase 集成

```typescript
// lib/supabase/server.ts 模式 — 服务器端客户端
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export function createClient() {
  const cookieStore = cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        },
      },
    }
  );
}

// lib/supabase/client.ts — 浏览器端客户端
import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

### 成就系统

```typescript
// lib/achievements.ts 模式
export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  condition: (stats: UserStats) => boolean;
}

export const ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first-commit',
    name: '首次提交',
    description: '做出了你的首次贡献',
    icon: '🌱',
    condition: (stats) => stats.totalContributions >= 1,
  },
  {
    id: 'thousand-commits',
    name: '提交狂人',
    description: '总贡献量达到1,000+',
    icon: '⚡',
    condition: (stats) => stats.totalContributions >= 1000,
  },
  {
    id: 'star-collector',
    name: '星标收集者',
    description: '跨仓库获得100+星标',
    icon: '⭐',
    condition: (stats) => stats.totalStars >= 100,
  },
  {
    id: 'open-sourcer',
    name: '开源者',
    description: '20+公开仓库',
    icon: '📦',
    condition: (stats) => stats.publicRepos >= 20,
  },
];

export function calculateAchievements(stats: UserStats): Achievement[] {
  return ACHIEVEMENTS.filter((achievement) => achievement.condition(stats));
}
```

### 添加新建筑装饰

```typescript
// types/decorations.ts
export type DecorationSlot = 'crown' | 'aura' | 'roof' | 'face';

export interface Decoration {
  id: string;
  slot: DecorationSlot;
  name: string;
  price: number;
  component: React.ComponentType<DecorationProps>;
}

// components/city/decorations/Crown.tsx
export function CrownDecoration({ position, buildingWidth }: DecorationProps) {
  return (
    <group position={[position[0], position[1], position[2]]}>
      <mesh>
        <coneGeometry args={[buildingWidth / 3, 2, 4]} />
        <meshStandardMaterial color="#FFD700" metalness={0.8} roughness={0.2} />
      </mesh>
    </group>
  );
}

// 在装饰注册表中注册
export const DECORATIONS: Decoration[] = [
  {
    id: 'golden-crown',
    slot: 'crown',
    name: '金色王冠',
    price: 500,
    component: CrownDecoration,
  },
];
```

### 相机/飞行控制

```tsx
// components/city/CameraController.tsx 模式
import { useThree, useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

export function CameraController() {
  const { camera } = useThree();
  const targetRef = useRef(new THREE.Vector3());
  const velocityRef = useRef(new THREE.Vector3());

  useFrame((_, delta) => {
    // 平滑插值相机到目标位置
    camera.position.lerp(targetRef.current, delta * 2);
  });

  // 通过上下文或引用暴露 flyTo 函数
  const flyTo = (position: THREE.Vector3) => {
    targetRef.current.copy(position).add(new THREE.Vector3(0, 10, 20));
  };

  return null;
}
```

### 服务器操作（Next.js 应用路由器）

```typescript
// app/actions/kudos.ts
'use server';

import { createClient } from '@/lib/supabase/server';
import { revalidatePath } from 'next/cache';

export async function sendKudos(toUsername: string) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) throw new Error('必须登录才能发送赞');

  const { error } = await supabase.from('kudos').insert({
    from_user_id: user.id,
    to_username: toUsername,
    created_at: new Date().toISOString(),
  });

  if (error) throw error;
  
  revalidatePath(`/${toUsername}`);
}
```

### 资料页面路由

```tsx
// app/[username]/page.tsx 模式
import { fetchGitHubProfile } from '@/lib/github';
import { createClient } from '@/lib/supabase/server';
import { calculateAchievements } from '@/lib/achievements';
import { BuildingPreview } from '@/components/profile/BuildingPreview';

interface Props {
  params: { username: string };
}

export default async function ProfilePage({ params }: Props) {
  const { username } = params;
  
  const [githubProfile, supabase] = await Promise.all([
    fetchGitHubProfile(username),
    createClient(),
  ]);

  const { data: cityProfile } = await supabase
    .from('profiles')
    .select('*, decorations(*)')
    .eq('username', username)
    .single();

  const achievements = calculateAchievements({
    totalContributions: githubProfile.totalContributions,
    totalStars: githubProfile.totalStars,
    publicRepos: githubProfile.publicRepos,
  });

  return (
    <main>
      <BuildingPreview profile={githubProfile} cityProfile={cityProfile} />
      <AchievementGrid achievements={achievements} />
    </main>
  );
}

export async function generateMetadata({ params }: Props) {
  return {
    title: `${params.username} — Git City`,
    description: `查看 ${params.username} 在 Git City 中的建筑`,
    openGraph: {
      images: [`/api/og/${params.username}`],
    },
  };
}
```

## 常见开发模式

### 细节层次（LOD）系统

```typescript
// 城市中使用的简化 LOD 模式
import { useThree } from '@react-three/fiber';

export function useLOD(buildingPosition: THREE.Vector3) {
  const { camera } = useThree();
  const distance = camera.position.distanceTo(buildingPosition);
  
  if (distance < 50) return 'high';    // 完整细节 + 动画窗户
  if (distance < 150) return 'medium'; // 简化窗户
  return 'low';                        // 仅方盒
}
```

### 城市视图中使用 SWR 获取数据

```tsx
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function useCityBuildings() {
  const { data, error, isLoading } = useSWR('/api/buildings', fetcher, {
    refreshInterval: 30000, // 每30秒刷新一次以获取实时活动信息
  });
  
  return { buildings: data, error, isLoading };
}
```

## 关键 API 路由

| 路由 | 目的 |
|------|------|
| `GET /api/buildings` | 获取所有城市建筑位置 |
| `GET /api/profile/[username]` | GitHub + 城市资料数据 |
| `POST /api/kudos` | 向用户发送赞 |
| `GET /api/og/[username]` | 生成 OG 分享卡片图像 |
| `POST /api/webhook/stripe` | Stripe 支付网关 |
| `GET /admin/ads` | 管理面板（需要 `ADMIN_GITHUB_LOGINS`） |

## 故障排除

**3D 场景未渲染**  
检查 `@react-three/fiber` 和 `three` 版本是否兼容。画布容器 div 需要设置高度。

**GitHub API 速率限制**  
使用具有适当范围的精细权限令牌。应用程序在 Supabase 中缓存 GitHub 响应以避免重复 API 调用。

**本地 Supabase 认证不工作**  
在您的 Supabase 项目中配置 GitHub OAuth 提供商并确保本地回调 URL (`http://localhost:3001/auth/callback`) 已允许。

**建筑未出现**  
检查 Supabase 行级安全策略是否允许匿名用户读取 `profiles` 和 `buildings` 表。

**窗户闪烁/闪烁**  
这通常是 Z 冲突问题。沿法线轴将窗户网格位置偏移一点点（`0.001`）。

**许多建筑导致性能问题**  
确保使用实例网格渲染窗户并激活 LOD 系统。避免在渲染循环中创建新的 `THREE.Material` 实例——将它们定义在组件外部或使用 `useMemo`。

## 技术栈参考

| 层级 | 技术 |
|------|------|
| 框架 | Next.js 16 (应用路由器, Turbopack) |
| 3D 渲染 | Three.js + @react-three/fiber + drei |
| 数据库 | Supabase (PostgreSQL + RLS) |
| 认证 | Supabase GitHub OAuth |
| 支付 | Stripe |
| 样式 | Tailwind CSS v4 + Silkscreen 字体 |
| 托管 | Vercel |
| 许可证 | AGPL-3.0 |
