# 微信文章提取器

从微信公众号文章中提取元数据和内容。

## 功能

- 解析微信公众号文章链接 (`mp.weixin.qq.com`)
- 提取文章元数据：标题、作者、描述、发布时间
- 提取账号信息：名称、头像、昵称、描述
- 获取文章内容（HTML）
- 获取封面图链接
- 支持多种文章类型：文章、视频、图片、音频、文本、转发
- 处理各种错误情况：已删除内容、过期链接、访问限制

## 使用方法

### 从URL进行基本提取

```javascript
const { extract } = require('./scripts/extract.js');

const result = await extract('https://mp.weixin.qq.com/s?__biz=...');
// 返回：{ done: true, code: 0, data: {...} }
```

### 从HTML提取

```javascript
const html = await fetch(url).then(r => r.text());
const result = await extract(html, { url: sourceUrl });
```

### 选项

```javascript
const result = await extract(url, {
  shouldReturnContent: true,      // 返回HTML内容（默认：true）
  shouldReturnRawMeta: false,     // 返回原始元数据（默认：false）
  shouldFollowTransferLink: true, // 跟随迁移后的账号链接（默认：true）
  shouldExtractMpLinks: false,    // 提取嵌入的mp.weixin链接（默认：false）
  shouldExtractTags: false,       // 提取文章标签（默认：false）
  shouldExtractRepostMeta: false  // 提取转发来源信息（默认：false）
});
```

## 响应格式

### 成功响应

```javascript
{
  done: true,
  code: 0,
  data: {
    // 账号信息
    account_name: "公众号名称",
    account_alias: "微信号",
    account_avatar: "头像URL",
    account_description: "功能介绍",
    account_id: "原始ID",
    account_biz: "biz参数",
    account_biz_number: 1234567890,
    account_qr_code: "二维码URL",

    // 文章信息
    msg_title: "文章标题",
    msg_desc: "文章摘要",
    msg_content: "HTML内容",
    msg_cover: "封面图URL",
    msg_author: "作者",
    msg_type: "post", // post|video|image|voice|text|repost
    msg_has_copyright: true,
    msg_publish_time: Date,
    msg_publish_time_str: "2024/01/15 10:30:00",

    // 链接参数
    msg_link: "文章链接",
    msg_source_url: "阅读原文链接",
    msg_sn: "sn参数",
    msg_mid: 1234567890,
    msg_idx: 1
  }
}
```

### 错误响应

```javascript
{
  done: false,
  code: 1001,
  msg: "无法获取文章信息"
}
```

## 错误代码

| 代码 | 消息 | 描述 |
|------|---------|-------------|
| 1000 | 文章获取失败 | 一般性失败 |
| 1001 | 无法获取文章信息 | 缺少标题或发布时间 |
| 1002 | 请求失败 | HTTP请求失败 |
| 1003 | 响应为空 | 空响应 |
| 1004 | 访问过于频繁 | 被限流 |
| 1005 | 脚本解析失败 | 脚本解析错误 |
| 1006 | 公众号已迁移 | 账号已迁移 |
| 2001 | 请提供文章内容或链接 | 缺少输入 |
| 2002 | 链接已过期 | 链接过期 |
| 2003 | 内容涉嫌侵权 | 内容被删除（版权） |
| 2004 | 无法获取迁移后的链接 | 迁移链接失败 |
| 2005 | 内容已被发布者删除 | 内容被作者删除 |
| 2006 | 内容因违规无法查看 | 内容被屏蔽 |
| 2007 | 内容发送失败 | 发送失败 |
| 2008 | 系统出错 | 系统错误 |
| 2009 | 不支持的链接 | 不支持的URL |
| 2010 | 内容获取失败 | 内容获取失败 |
| 2011 | 涉嫌过度营销 | 营销/垃圾内容 |
| 2012 | 账号已被屏蔽 | 账号被屏蔽 |
| 2013 | 账号已自主注销 | 账号被删除 |
| 2014 | 内容被投诉 | 内容被举报 |
| 2015 | 账号处于迁移流程中 | 账号正在迁移 |
| 2016 | 冒名侵权 | 仿冒侵权 |

## 依赖项

必需的npm包：
- `cheerio` - HTML解析
- `dayjs` - 日期格式化
- `request-promise` - HTTP请求
- `qs` - 查询字符串解析
- `lodash.unescape` - HTML实体

## 注意事项

- 处理各种微信页面结构和反爬虫措施
- 自动从页面内容检测文章类型
- 支持从百度微信搜索结果 (`weixin.sogou.com`) 提取
- 部分字段可能为null，取决于文章类型和页面结构
