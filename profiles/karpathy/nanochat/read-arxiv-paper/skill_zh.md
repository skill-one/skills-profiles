您将获得一篇arxiv论文的URL，例如：

https://www.arxiv.org/abs/2601.07372

### 第一部分：规范化URL

目标是获取论文的TeX源代码（不是PDF！），URL始终看起来像这样：

https://www.arxiv.org/src/2601.07372

注意URL中的/src/。一旦您获得了URL：

### 第二部分：下载论文源代码

将URL获取到本地.tar.gz文件。一个良好的位置是`~/.cache/nanochat/knowledge/{arxiv_id}.tar.gz`。

（如果文件已存在，则无需重新下载）。

### 第三部分：在该文件夹中解压文件

将内容解压到`~/.cache/nanochat/knowledge/{arxiv_id}`目录。

### 第四部分：定位入口点

每个LaTeX源代码通常都有一个入口点，例如`main.tex`或类似的东西。

### 第五部分：阅读论文

一旦您找到了入口点，阅读其内容，然后递归地通过所有其他相关源文件来阅读论文。

### 第六部分：报告

一旦您阅读了论文，将论文的摘要生成到`./knowledge/summary_{tag}.md`的markdown文件中。注意1) 使用本地知识目录（在这里更容易打开和引用），而不是`~/.cache`，2) 生成一个合理的`tag`，例如`conditional_memory`或根据论文生成任何看起来合适的其他标签。可能需要确保标签不存在，以免覆盖文件。

至于摘要本身，请记住您是在nanochat仓库的上下文中处理这篇论文，因此我们通常会对如何将论文及其教训应用于nanochat项目感兴趣。因此，您应该可以自由地通过阅读相关部分来“提醒自己”相关的nanochat代码，然后明确地说明这篇论文如何与nanochat相关联，或者我们可以从中获得哪些启发或尝试。
