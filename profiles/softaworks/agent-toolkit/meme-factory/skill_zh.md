# Meme Factory

使用免费的 memegen.link API 和文本 meme 格式创建 meme。

---

## 触发器

| 触发器 | 描述 |
|---------|-------------|
| `/meme-factory` | 手动调用 |
| `/meme-factory {模板} {顶部文本} {底部文本}` | 直接生成 meme |
| `meme-factory: create a meme about X` | 自然语言请求 |

---

## 快速参考

| 操作 | 格式 |
|--------|--------|
| 基础 meme | `https://api.memegen.link/images/{模板}/{顶部文本}/{底部文本}.png` |
| 带尺寸设置 | `?width=1200&height=630` |
| 自定义背景 | `?style=https://example.com/image.jpg` |
| 所有模板 | https://api.memegen.link/templates/ |
| 交互式文档 | https://api.memegen.link/docs/ |

**附加资源：**
- [Markdown meme 指南](references/markdown-memes-guide.md) - 15+ 文本 meme 格式
- [示例](references/examples.md) - 实际使用示例
- [meme_generator.py](scripts/meme_generator.py) - Python 辅助脚本

---

## 快速入门

### 基础 meme 结构

```
https://api.memegen.link/images/{模板}/{顶部文本}/{底部文本}.{扩展名}
```

**示例：**
```
https://api.memegen.link/images/buzz/memes/memes_everywhere.png
```

结果：Buzz Lightyear meme，顶部显示 "memes"，底部显示 "memes everywhere"。

### 文本格式化

| 字符 | 编码 |
|-----------|----------|
| 空格 | `_` 或 `-` |
| 换行 | `~n` |
| 问号 | `~q` |
| 百分号 | `~p` |
| 斜杠 | `~s` |
| 哈希符号 | `~h` |
| 单引号 | `''` |
| 双引号 | `""` |

---

## 热门模板

| 模板 | 用途 | 示例 |
|----------|----------|---------|
| `buzz` | X, X everywhere | bugs/bugs_everywhere |
| `drake` | 比较用途 | manual_testing/automated_testing |
| `success` | 胜利 | deployed/no_errors |
| `fine` | 事情出错 | server_on_fire/this_is_fine |
| `fry` | 不确定性 | not_sure_if_bug/or_feature |
| `changemind` | 热门观点 | tabs_are_better_than_spaces |
| `distracted` | 优先级 | my_code/new_framework/current_project |
| `mordor` | One does not simply | one_does_not_simply/deploy_on_friday |

---

## 模板选择指南

| 上下文 | 模板 | 原因 |
|---------|----------|-----|
| 比较选项 | `drake` | 两面板拒绝/批准格式 |
| 庆祝胜利 | `success` | 强调积极结果 |
| 被忽视的问题 | `fine` | "一切正常" 的讽刺 |
| 不确定性 | `fry` | "不确定 X 或 Y" 格式 |
| 有争议的观点 | `changemind` | 陈述 + 挑战 |
| 普遍事物 | `buzz` | "X, X everywhere" |
| 坏主意 | `mordor` | "One does not simply..." |

---

## 验证

生成 meme 后：

- [ ] URL 返回有效图像（在浏览器中测试）
- [ ] 文本可读（不要太长）
- [ ] 模板与消息上下文匹配
- [ ] 特殊字符正确编码
- [ ] 尺寸适合平台

### 平台尺寸

| 平台 | 尺寸 |
|----------|------------|
| 社交媒体 (Open Graph) | 1200x630 |
| Slack/Discord | 800x600 |
| GitHub | 默认 |

---

## 反模式

| 避免 | 原因 | 而是使用 |
|-------|-----|---------|
| 未编码的空格 | URL 错误 | 使用 `_` 或 `-` |
| 文本过多 | 难以阅读 | 每行 2-6 个词 |
| 错误模板 | 消息不匹配 | 将模板与上下文匹配 |
| 缺少扩展名 | 无效 URL | 始终包含 `.png`, `.jpg` 等 |
| 未编码的特殊字符 | URL 错误 | 使用 `~q`, `~s`, `~p` 等 |
| 假设模板存在 | 404 错误 | 首先检查模板列表 |

---

## 验证

当 meme 生成成功时：

1. **URL 有效** - 返回 HTTP 200
2. **图像渲染** - 在 markdown 中正确显示
3. **文本可见** - 图像上正确格式化
4. **上下文匹配** - 模板适合消息

**测试命令：**
```bash
curl -I "https://api.memegen.link/images/buzz/test/test.png"
# 应返回: HTTP/2 200
```

---

<details>
<summary><strong>深入解析：高级功能</strong></summary>

### 图像格式

| 扩展名 | 用途 |
|-----------|----------|
| `.png` | 最佳质量，默认 |
| `.jpg` | 较小的文件大小 |
| `.webp` | 现代，良好压缩 |
| `.gif` | 动画模板 |

### 尺寸

```
?width=800
?height=600
?width=800&height=600  (精确填充)
```

### 布局选项

```
?layout=top     # 仅顶部文本
?layout=bottom  # 仅底部文本
?layout=default # 标准顶部/底部
```

### 自定义字体

查看可用：https://api.memegen.link/fonts/

```
?font=impact  (默认)
```

### 自定义图像

使用任何图像作为背景：

```
https://api.memegen.link/images/custom/hello/world.png?style=https://example.com/image.jpg
```

</details>

<details>
<summary><strong>深入解析：上下文 meme</strong></summary>

### 代码评审

```
模板: fry
https://api.memegen.link/images/fry/not_sure_if_feature/or_bug.png
```

### 部署

```
模板: interesting
https://api.memegen.link/images/interesting/i_dont_always_test/but_when_i_do_i_do_it_in_production.png
```

### 文档

```
模板: yodawg
https://api.memegen.link/images/yodawg/yo_dawg_i_heard_you_like_docs/so_i_documented_the_documentation.png
```

### 性能问题

```
模板: fine
https://api.memegen.link/images/fine/memory_usage_at_99~/this_is_fine.png
```

### 成功部署

```
模板: success
https://api.memegen.link/images/success/deployed_to_production/zero_downtime.png
```

</details>

<details>
<summary><strong>深入解析：工作流集成</strong></summary>

### 响应生成 meme

```markdown
Here's a relevant meme:

![Meme](https://api.memegen.link/images/buzz/bugs/bugs_everywhere.png)
```

### 动态生成（Python）

```python
def generate_status_meme(status: str, message: str):
    template_map = {
        "success": "success",
        "failure": "fine",
        "review": "fry",
        "deploy": "interesting"
    }

    template = template_map.get(status, "buzz")
    words = message.split()
    top = "_".join(words[0:3])
    bottom = "_".join(words[3:6])

    return f"https://api.memegen.link/images/{template}/{top}/{bottom}.png"
```

### 使用辅助脚本

```python
from meme_generator import MemeGenerator

meme = MemeGenerator()
url = meme.generate("buzz", "features", "features everywhere")
print(url)
```

</details>

<details>
<summary><strong>深入解析：API 参考</strong></summary>

### 端点

| 端点 | 目的 |
|----------|---------|
| `/templates/` | 列出所有模板 |
| `/templates/{id}` | 模板详情 |
| `/fonts/` | 可用字体 |
| `/images/{template}/{top}/{bottom}.{ext}` | 生成 meme |

### API 特性

- 免费、开源
- 无需 API 密钥
- 正常使用无速率限制
- 状态无关（所有信息在 URL 中）
- 图像按需生成

### 错误处理

1. 在 https://api.memegen.link/templates/ 检查模板
2. 验证文本格式（使用下划线表示空格）
3. 检查特殊字符编码
4. 确保有效扩展名
5. 在浏览器中测试 URL

</details>

---

## 参考

| 文档 | 内容 |
|----------|---------|
| [markdown-memes-guide.md](references/markdown-memes-guide.md) | 15+ 文本 meme 格式（greentext, copypasta, ASCII 等） |
| [examples.md](references/examples.md) | 实际使用示例 |

### 脚本

| 脚本 | 目的 |
|----------|---------|
| [meme_generator.py](scripts/meme_generator.py) | Python meme 生成辅助脚本 |

---

## 总结

生成上下文 meme 以：

- 为对话添加幽默
- 创建社交媒体视觉效果
- 使代码评审更具吸引力
- 庆祝成功

**黄金法则：** 保持文本简洁，将模板与上下文匹配。
