# 猿人压缩

## 目的

将自然语言文件（CLAUDE.md、待办事项、偏好设置）压缩成猿人语言以减少输入令牌。压缩版本会覆盖原始文件。人类可读的备份文件保存为`<filename>.original.md`。

## 触发方式

`/caveman:compress <文件路径>` 或当用户要求压缩内存文件时。

## 处理流程

1. 此 `SKILL.md` 与 `scripts/` 目录位于同一目录下。找到该目录。

2. 运行：

```bash
cd <包含此_SKILL.md> 的目录 && python3 -m scripts <绝对文件路径>
```

3. 命令行界面（CLI）将：
- 检测文件类型（无令牌）
- 调用 Claude 进行压缩
- 验证输出（无令牌）
- 如果出错：使用 Claude 进行挑战认修（仅针对性修复，不重新压缩）
- 最多重试 2 次
- 如果 2 次重试后仍失败：向用户报告错误，保留原始文件不变

4. 返回结果给用户

## 压缩规则

### 删除

- 冠词：a、an、the
- 填充词：just、really、basically、actually、simply、essentially、generally
- 礼貌用语："sure"、"certainly"、"of course"、"happy to"、"I'd recommend"
- 模棱两可的表达："it might be worth"、"you could consider"、"it would be good to"
- 重复短语："in order to" → "to"、"make sure to" → "ensure"、"the reason is because" → "because"
- 连接性填充："however"、"furthermore"、"additionally"、"in addition"

### 精确保留（永不修改）

- 代码块（带分隔符 ``` 和缩进）
- 行内代码（`backtick content`）
- URL 和链接（完整 URL、Markdown 链接）
- 文件路径（`/src/components/...`、`./config.yaml`）
- 命令（`npm install`、`git commit`、`docker build`）
- 技术术语（库名称、API 名称、协议、算法）
- 专有名词（项目名称、人名、公司名称）
- 日期、版本号、数值
- 环境变量（`$HOME`、`NODE_ENV`）

### 保留结构

- 所有 Markdown 标题（保留精确标题文本，压缩下方内容）
- 项目符号层级（保留缩进级别）
- 编号列表（保留编号）
- 表格（压缩单元格文本，保留结构）
- Markdown 文件中的 Frontmatter/YAML 头部

### 压缩

- 使用简短同义词："big" 而不是 "extensive"、"fix" 而不是 "implement a solution for"、"use" 而不是 "utilize"
- 片段式表达：OK，"Run tests before commit" 而不是 "You should always run tests before committing"
- 删除 "you should"、"make sure to"、"remember to" —— 直接陈述动作
- 合并重复的、表达相同意思的项目符号
- 保留一个示例，如果多个示例展示相同模式

**关键规则**：
``` ... ``` 内的内容必须精确复制。
不要：
- 删除注释
- 删除空格
- 重新排序行
- 缩短命令
- 简化任何内容

行内代码（`...`）必须精确保留。
不要修改反引号内的任何内容。

如果文件包含代码块：
- 将代码块视为只读区域
- 仅压缩它们周围的文本
- 不要合并代码块周围的区域

## 模式

原始：
> You should always make sure to run the test suite before pushing any changes to the main branch. This is important because it helps catch bugs early and prevents broken builds from being deployed to production.

压缩：
> Run tests before push to main. Catch bugs early, prevent broken prod deploys.

原始：
> The application uses a microservices architecture with the following components. The API gateway handles all incoming requests and routes them to the appropriate service. The authentication service is responsible for managing user sessions and JWT tokens.

压缩：
> Microservices architecture. API gateway route all requests to services. Auth service manage user sessions + JWT tokens.

## 边界

- 仅压缩自然语言文件（.md、.txt、.typ、.typst、.tex、无扩展名）
- 永不修改：.py、.js、.ts、.json、.yaml、.yml、.toml、.env、.lock、.css、.html、.xml、.sql、.sh
- 如果文件包含混合内容（散文+代码），仅压缩散文部分
- 如果不确定某部分是代码还是散文，保留不变
- 原始文件在覆盖前备份为 FILE.original.md
- 永不压缩 FILE.original.md（跳过）
