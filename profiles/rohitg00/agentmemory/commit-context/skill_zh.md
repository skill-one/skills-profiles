用户希望提交上下文为：$ARGUMENTS

## 快速入门

```bash
git blame -L 40,52 src/auth/refresh.ts   # -> SHA 9a1b2c3d
```

```json
memory_commit_lookup { "sha": "9a1b2c3d4e5f60718293a4b5c6d7e8f901234567" }
```

预期输出：

```text
9a1b2c3 on main by dev: "rotate refresh tokens"
Linked session 7f3a9c2 "Auth refresh rework", 14 obs.
```

## 原因

仅报告git和查找返回的内容。当查找返回`commit: null`时，该提交早于会话链接；不要编造意图。

## 工作流程

1. 查找SHA：使用`git blame -L <start>,<end> <file>`查找行范围；使用`git log -L :<function>:<file>`查找函数；使用`git log -n 1 -- <file>`查找裸路径。
2. 查找：`memory_commit_lookup { "sha": "<完整SHA>" }`。
3. 当可用时，通过`memory_recall`呈现提交（sha、短sha、分支、作者、消息）、链接的会话（id、项目、开始/结束、观察计数、摘要）以及重要性>=7的观察结果。

## 反模式

错误：查找返回`{ "commit": null }`，你仅根据diff叙述"代理正在重构auth"。

正确："此提交早于会话链接，因此没有记录的代理会话。从`git show`：它更改了refresh.ts中的token旋转。"

## 检查清单

- SHA来自git blame/log，不是猜测。
- `commit: null`报告为"早于链接"，没有编造会话。
- 会话细节逐字引用查找响应。
- 没有声称超出观察结果所陈述的内容。

## 参考文档

- `commit-history`：一次性列出多个代理链接的提交。
- `recall`：深入挖掘链接会话的观察结果。

## 故障排除

如果`memory_commit_lookup`不可用，请参阅../_shared/TROUBLESHOOTING.md。
