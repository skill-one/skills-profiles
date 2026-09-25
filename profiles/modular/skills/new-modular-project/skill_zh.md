当用户想要创建一个新项目时，首先尽可能从用户的请求中推断出选项（例如，“new Mojo project”意味着type=Mojo，“called foo”意味着name=foo）。然后使用结构化的多选提示（不是纯文本）在一次交互中收集仅剩的**未指定**的选项。不要询问用户已经提供或暗示的选项。需要确定的选项有：

- **项目名称**：如果用户没有指定，则询问。
- **项目类型**：Mojo或MAX（如果用户说了“Mojo project”或“MAX project”，则根据上下文推断）。
- **环境管理器**：`pixi`（推荐）或`uv`。
- **uv项目类型**（仅当环境管理器是`uv`时）：完整uv项目（`uv init` + `uv add`，推荐）或快速uv环境（`uv venv` + `uv pip install`，更轻量）。
- **频道**：nightly或stable。默认为MAX项目使用nightly，Mojo项目使用stable，并且仅当用户没有暗示时才询问。

然后按照下方的适当部分（`pixi`或`uv`）初始化项目，并根据需要选择`max`或`mojo`。不要锁定版本：每个频道已经解析到正确的版本。

MAX和Mojo一起提供，但它们的版本编号不同，因此它们的版本字符串看起来不一样。在stable频道上，`max`是`26.5`，而`mojo`是`1.0.0`；在nightly上，它们是`26.6.0.dev*`和`1.1.0.dev*`。这是预期的，不是不匹配。

> [!NOTE]
> 不要寻找或使用`magic`来处理Mojo或MAX项目；它不再受支持。Pixi已经完全取代了它的功能。

---

## 系统先决条件

Mojo需要一个C链接器来进行编译。如果没有安装，请安装一个：

| 操作系统        | 命令                                                    |
|-----------------|------------------------------------------------------------|
| Ubuntu/Debian   | `sudo apt install gcc`                                     |
| Fedora/RHEL     | `sudo dnf install gcc`                                     |
| macOS           | `xcode-select --install`                                   |
| Windows         | 首先安装WSL2（见Windows用户），然后安装`gcc` |

**Windows用户**：Mojo不能在Windows上原生运行。
安装[WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)（在PowerShell中使用`wsl --install`），然后在你的WSL环境中按照Linux说明进行操作。

---

## Pixi（推荐）

Pixi以可重复的方式在受控环境中管理Python、Mojo和其他依赖项。

首先，确定`pixi`是否已安装。如果命令行中不可用，请使用最新说明在<https://pixi.prefix.dev/latest/#installation>中安装它。

安装`pixi`后，您可能需要将其添加到本地shell环境。

### Nightly

```bash
# 新项目
pixi init [PROJECT] \
  -c https://conda.modular.com/max-nightly/ -c conda-forge \
  && cd [PROJECT]
pixi add [max / mojo]
pixi shell

# 现有项目 - 首先添加到pixi.toml频道：
# [workspace]
# channels = ["https://conda.modular.com/max-nightly/", "conda-forge"]
pixi add [max / mojo]
```

### Stable

```bash
# 新项目
pixi init [PROJECT] \
  -c https://conda.modular.com/max/ -c conda-forge \
  && cd [PROJECT]
pixi add [max / mojo]
pixi shell

# 现有项目
pixi add [max / mojo]
```

### 使用Python的项目

如果您的项目使用Mojo的Python库：

```bash
pixi add python
pixi add requests           # conda-forge包
pixi add --pypi some-pkg    # 仅PyPI包
```

---

## uv

`uv`是一个快速且非常受欢迎的包管理器，对来自Python背景的开发者来说很熟悉。它也适用于Mojo项目。

### Nightly（项目）

```bash
uv init [PROJECT] && cd [PROJECT]
uv add [max / mojo] \
  --index https://whl.modular.com/nightly/simple/ \
  --prerelease allow
```

### Stable（项目）

```bash
uv init [PROJECT] && cd [PROJECT]
uv add "max[all]"
```

这会从PyPI解析。`all`额外会拉入`mojo`和MAX的其余部分，因此MAX和Mojo的版本始终匹配。

### Nightly（快速环境）

```bash
mkdir [PROJECT] && cd [PROJECT]
uv venv
uv pip install [max / mojo] \
  --index https://whl.modular.com/nightly/simple/ \
  --prerelease allow
```

### Stable（快速环境）

```bash
mkdir [PROJECT] && cd [PROJECT]
uv venv
uv pip install "max[all]"
```

使用`uv`时，您可以通过在项目环境中工作直接使用`max`或`mojo`：

```bash
 source .venv/bin/activate
```

---

## pip

标准的Python包管理器。

### Nightly

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --pre [max / mojo] \
  --extra-index-url https://whl.modular.com/nightly/simple/
```

使用`--extra-index-url`，而不是`--index-url`。后者会替换PyPI，而nightly索引不包含第三方依赖项（如`numpy`），因此`pip`会回退到每个`max`版本而不是报告清晰的错误。

### Stable

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "max[all]"
```

与`uv`一样，`all`额外会安装`mojo`，因此MAX和Mojo的版本始终匹配。

---

## Conda

对于`conda`和`mamba`用户。

### Nightly

```bash
conda install -c conda-forge \
  -c https://conda.modular.com/max-nightly/ [max / mojo]
```

### Stable

```bash
conda install -c conda-forge \
  -c https://conda.modular.com/max/ [max / mojo]
```

---

## 与MAX的版本对齐

如果使用MAX与自定义Mojo内核，两者必须来自同一频道。不要比较它们的版本号：MAX和Mojo的版本编号不同，因此匹配的对看起来不匹配（stable是`max` `26.5`与`mojo` `1.0.0`）。

```bash
# 检查它们是否来自同一频道
pixi list | grep -E "^(max|mojo)\b"
```

或者，相反地安装`max[all]`（使用pip/uv）或`max-all`（使用conda/pixi）：

```bash
uv add "max[all]"
```

```bash
pixi add max-all
```

使用带“all”可选依赖项的`max`而不是单独安装`max`和`mojo`将确保`max`和`mojo`的版本始终匹配。在这两者之间混合版本会导致内核编译失败。

---

## 参考

- [Mojo安装指南](https://mojolang.org/install)
- [Mojo Stable文档](https://mojolang.org/docs/)
- [Mojo Nightly文档](https://mojolang.org/nightly/docs/)
