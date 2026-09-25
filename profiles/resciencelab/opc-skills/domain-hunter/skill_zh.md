# 域名猎人技能

帮助用户以最佳价格查找和购买域名。

## 工作流程

### 第一步：生成域名创意并检查可用性

根据用户的项目描述，生成5-10个创意域名建议。

**指南：**
- 域名长度保持在15个字符以内
- 使其易于记忆和品牌化
- 考虑：`{动作}{名词}`、`{名词}{后缀}`、`{前缀}{关键词}`
- 常见后缀：app、io、hq、ly、ify、now、hub

**关键：** 在向用户展示域名前，务必检查可用性！

使用以下方法之一验证可用性：

**方法1：WHOIS查询（最可靠）**
```bash
# 通过whois检查域名是否可用
whois {domain}.{tld} 2>/dev/null | grep -i "no match\|not found\|available\|no data found" && echo "AVAILABLE" || echo "TAKEN"
```

**方法2：注册商查询页面**
在浏览器中打开注册商的域名查询页面进行验证：
```bash
open "https://www.spaceship.com/domains/?search={domain}.{tld}"
```

**方法3：通过Namecheap/Dynadot批量查询**
- https://www.namecheap.com/domains/registration/results/?domain={domain}
- https://www.dynadot.com/domain/search?domain={domain}

**重要：**
- 仅展示确认可用的域名
- 对任何不确定的域名标记为"(未验证)"
- 向用户展示建议并**等待确认**后再继续
- 询问用户选择偏好或提供反馈
- 只有在用户批准域名后，才进入下一步

### 第二步：比较价格

使用**WebSearch**查找当前价格：

```
WebSearch: "2026年最便宜.{tld}域名注册商 site:tld-list.com"
WebSearch: ".{tld}域名价格比较 tldes.com"
```

**关键价格比较网站：**
- tld-list.com/tld/{tld}
- tldes.com/{tld}
- domaintyper.com/{tld}-domain

### 第三步：查找促销代码

使用**Twitter技能**搜索注册商账号：

```bash
cd <twitter_skill_directory>
python3 scripts/search_tweets.py "from:{registrar} 促销代码" --type Latest --limit 15
python3 scripts/search_tweets.py "{registrar} 促销代码 优惠券" --type Latest --limit 15
```

使用**Reddit技能**搜索域名社区：

```bash
cd <reddit_skill_directory>
python3 scripts/search_posts.py "{registrar} 促销代码" --limit 15
python3 scripts/search_posts.py "{registrar} 优惠券 折扣" --subreddit Domains --limit 10
```

**主要注册商Twitter账号：**
- @spaceship、@Dynadot、@Namecheap、@Porkbun、@namesilo、@Cloudflare

### 第四步：推荐

以以下格式展示最终推荐：

```
## 推荐

**域名：** example.ai
**最佳注册商：** Spaceship
**价格：** 68.98美元/年（最低2年合约=137.96美元）
**促销代码：** .ai域名暂无可用促销代码
**购买链接：** https://www.spaceship.com/

### 价格比较
| 注册商     | 第一年 | 续费   | 2年总计 |
|------------|--------|--------|---------|
| Spaceship  | 68.98  | 68.98  | 137.96  |
| Cloudflare | 70.00  | 70.00  | 140.00  |
| Porkbun   | 71.40  | 72.40  | 143.80  |
```

## 重要提示

1. **顶级域名**（.ai、.io）很少提供促销代码 - 批发成本过高
2. **.ai域名**要求最低2年注册
3. **Cloudflare**提供成本价定价，无加价
4. **续费价格**通常与注册价格不同 - 务必检查两者
5. **WHOIS隐私保护**在大多数注册商处免费（Cloudflare、Namecheap、Porkbun）

## 参考文献

- [references/registrars.md](./references/registrars.md) - 详细注册商比较
- [references/spaceship-api.md](./references/spaceship-api.md) - Spaceship API用于自动化域名操作
