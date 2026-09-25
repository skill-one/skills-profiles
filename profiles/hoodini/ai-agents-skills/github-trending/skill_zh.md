# GitHub 热门数据

访问 GitHub 热门仓库和开发者数据。

## 重要提示

**GitHub 不提供官方的热门 API。** 热门页面 `github.com/trending` 必须直接抓取或使用 GitHub 搜索 API 作为替代方案。

## 方法 1：直接网页抓取（推荐）

使用 Cheerio 直接抓取 `github.com/trending`：

```typescript
import * as cheerio from 'cheerio';

interface TrendingRepo {
  owner: string;
  name: string;
  fullName: string;
  url: string;
  description: string;
  language: string;
  languageColor: string;
  stars: number;
  forks: number;
  starsToday: number;
}

async function scrapeTrending(options: {
  language?: string;
  since?: 'daily' | 'weekly' | 'monthly';
} = {}): Promise<TrendingRepo[]> {
  // 构建URL：github.com/trending 或 github.com/trending/typescript?since=weekly
  let url = 'https://github.com/trending';
  if (options.language) {
    url += `/${encodeURIComponent(options.language)}`;
  }
  if (options.since) {
    url += `?since=${options.since}`;
  }

  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (compatible; TrendingBot/1.0)',
    },
  });
  
  if (!response.ok) {
    throw new Error(`抓取热门数据失败：${response.status}`);
  }

  const html = await response.text();
  const $ = cheerio.load(html);
  const repos: TrendingRepo[] = [];

  // 每个热门仓库都在一个 article.Box-row 元素中
  $('article.Box-row').each((_, element) => {
    const $el = $(element);
    
    // 获取仓库链接（例如，/owner/repo）
    const repoLink = $el.find('h2 a').attr('href')?.trim() || '';
    const [, owner, name] = repoLink.split('/');
    
    // 获取描述
    const description = $el.find('p.col-9').text().trim();
    
    // 获取语言
    const language = $el.find('[itemprop="programmingLanguage"]').text().trim();
    
    // 从彩色圆点获取语言颜色
    const langColorStyle = $el.find('.repo-language-color').attr('style') || '';
    const langColorMatch = langColorStyle.match(/background-color:\s*([^;]+)/);
    const languageColor = langColorMatch ? langColorMatch[1].trim() : '';
    
    // 获取星标（总数）
    const starsText = $el.find('a[href$="/stargazers"]').text().trim();
    const stars = parseNumber(starsText);
    
    // 获取分支
    const forksText = $el.find('a[href$="/forks"]').text().trim();
    const forks = parseNumber(forksText);
    
    // 获取今日/本周/本月的星标
    const starsTodayText = $el.find('.float-sm-right, .d-inline-block.float-sm-right').text().trim();
    const starsToday = parseNumber(starsTodayText);

    if (owner && name) {
      repos.push({
        owner,
        name,
        fullName: `${owner}/${name}`,
        url: `https://github.com${repoLink}`,
        description,
        language,
        languageColor,
        stars,
        forks,
        starsToday,
      });
    }
  });

  return repos;
}

function parseNumber(text: string): number {
  const clean = text.replace(/,/g, '').trim();
  if (clean.includes('k')) {
    return Math.round(parseFloat(clean) * 1000);
  }
  return parseInt(clean) || 0;
}
```

## 方法 2：GitHub 搜索 API（官方替代方案）

使用 GitHub 的搜索 API 查找最近创建且星标高的仓库：

```typescript
interface GitHubSearchResult {
  total_count: number;
  items: GitHubRepo[];
}

interface GitHubRepo {
  full_name: string;
  html_url: string;
  description: string;
  language: string;
  stargazers_count: number;
  forks_count: number;
  created_at: string;
}

async function getTrendingViaSearch(options: {
  language?: string;
  days?: number;
  minStars?: number;
} = {}): Promise<GitHubRepo[]> {
  const days = options.days || 7;
  const minStars = options.minStars || 100;
  
  // 计算 N 天前的日期
  const date = new Date();
  date.setDate(date.getDate() - days);
  const since = date.toISOString().split('T')[0];

  // 构建搜索查询
  const queryParts = [
    `created:>${since}`,
    `stars:>=${minStars}`,
  ];
  if (options.language) {
    queryParts.push(`language:${options.language}`);
  }
  const query = queryParts.join(' ');

  const response = await fetch(
    `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=stars&order=desc&per_page=25`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`, // 可选但推荐
        'User-Agent': 'TrendingApp/1.0',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`GitHub API 错误：${response.status}`);
  }

  const data: GitHubSearchResult = await response.json();
  return data.items;
}
```

**注意：** 搜索 API 有速率限制（未认证时每分钟 10 个请求，使用令牌时每分钟 30 个请求）。

## Next.js API 路由（服务器端抓取）

```typescript
// app/api/trending/route.ts
import { NextRequest } from 'next/server';
import * as cheerio from 'cheerio';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const language = searchParams.get('language') || '';
  const since = searchParams.get('since') || 'daily';

  try {
    let url = 'https://github.com/trending';
    if (language) url += `/${encodeURIComponent(language)}`;
    url += `?since=${since}`;

    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible)' },
      next: { revalidate: 3600 }, // 缓存 1 小时
    });

    const html = await response.text();
    const repos = parseGitHubTrending(html);
    
    return Response.json(repos);
  } catch (error) {
    console.error('抓取热门数据失败:', error);
    return Response.json(
      { error: '抓取热门仓库失败' },
      { status: 500 }
    );
  }
}

function parseGitHubTrending(html: string) {
  const $ = cheerio.load(html);
  const repos: any[] = [];

  $('article.Box-row').each((_, el) => {
    const $el = $(el);
    const repoLink = $el.find('h2 a').attr('href') || '';
    const [, owner, name] = repoLink.split('/');
    
    repos.push({
      owner,
      name,
      fullName: `${owner}/${name}`,
      url: `https://github.com${repoLink}`,
      description: $el.find('p.col-9').text().trim(),
      language: $el.find('[itemprop="programmingLanguage"]').text().trim(),
      stars: parseNumber($el.find('a[href$="/stargazers"]').text()),
      forks: parseNumber($el.find('a[href$="/forks"]').text()),
      starsToday: parseNumber($el.find('.float-sm-right').text()),
    });
  });

  return repos;
}

function parseNumber(text: string): number {
  const clean = text.replace(/,/g, '').trim();
  if (clean.includes('k')) return Math.round(parseFloat(clean) * 1000);
  return parseInt(clean) || 0;
}
```

## React Hook

```tsx
import { useState, useEffect } from 'react';

function useTrending(options: { language?: string; since?: string } = {}) {
  const [repos, setRepos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTrending() {
      setIsLoading(true);
      try {
        const params = new URLSearchParams();
        if (options.language) params.set('language', options.language);
        if (options.since) params.set('since', options.since);

        const response = await fetch(`/api/trending?${params}`);
        if (!response.ok) throw new Error('抓取失败');
        setRepos(await response.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : '未知错误');
      } finally {
        setIsLoading(false);
      }
    }

    fetchTrending();
  }, [options.language, options.since]);

  return { repos, isLoading, error };
}
```

## 重要注意事项

1. **无官方 API**：GitHub 的热门页面没有官方 API - 抓取是唯一选项
2. **速率限制**：尊重 GitHub 的服务器 - 积极缓存
3. **HTML 结构变化**：GitHub 可能会更改他们的 HTML - 监控以防止中断
4. **User-Agent**：始终包含 User-Agent 头
5. **仅服务器端**：在服务器端抓取以避免 CORS 问题

## 资源

- **GitHub 热门页面**：https://github.com/trending
- **GitHub 搜索 API**：https://docs.github.com/en/rest/search
