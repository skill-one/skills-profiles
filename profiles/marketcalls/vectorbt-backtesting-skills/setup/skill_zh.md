为 VectorBT + OpenAlgo 设置完整的 Python 回测环境。

## 参数

- `$0` = Python 版本（可选，默认：`python3`）。示例：`python3.12`，`python3.13`

## 步骤

### 第 1 步：检测操作系统

运行以下命令以检测操作系统：

```bash
uname -s 2>/dev/null || echo "Windows"
```

映射结果：
- `Darwin` = macOS
- `Linux` = Linux
- `MINGW*` 或 `CYGWIN*` 或 `Windows` = Windows

向用户打印检测到的操作系统。

### 第 2 步：创建虚拟环境

在当前工作目录中创建 Python 虚拟环境：

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
```

如果用户指定了 Python 版本参数，则使用该参数而不是 `python3`：
```bash
$PYTHON_VERSION -m venv venv
```

### 第 3 步：TA-Lib 系统依赖（可选）

**OpenAlgo ta (`from openalgo import ta`) 是此项目的默认指标库 - 它包含 100 多个指标，无需单独的系统依赖。** 只有当用户希望在回测中明确请求时能够使用 "talib"，才需要 TA-Lib。

使用 AskUserQuestion 向用户提问：
- "您是否也想在回测中明确请求时安装 TA-Lib？(可选 - OpenAlgo ta 已经涵盖了相同的指标，并且还有 90 多个更多)"
  - 是，也安装 TA-Lib
  - 否，跳过它（推荐 - 如果需要，稍后安装）

如果用户跳过，则跳过整个步骤，并在第 4 步的 pip 安装中省略 `ta-lib`。如果用户需要，TA-Lib 需要在操作系统级别安装 C 库，然后再运行 `pip install ta-lib`。

**macOS:**
```bash
brew install ta-lib
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**Linux (RHEL/CentOS/Fedora):**
```bash
sudo yum groupinstall -y "Development Tools"
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**Windows:**
```
pip install ta-lib
```
如果失败，请从 https://github.com/cgohlke/talib-build/releases 下载相应的 .whl 文件并使用以下命令安装：
```bash
pip install TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

### 第 4 步：安装 Python 包

安装所有必需的包（最新版本）。`openstatz` 替代 QuantStats 用于 tearsheets - 始终安装它，不要安装 `quantstats`：

```bash
pip install openalgo vectorbt plotly anywidget nbformat pandas numpy yfinance python-dotenv tqdm scipy numba nbformat ipywidgets openstatz ccxt duckdb psutil
```

如果用户在第 3 步中选择了 TA-Lib，则在该安装命令中追加 `ta-lib`（在安装 C 库后）。

### 第 5 步：创建回测文件夹

仅创建顶级的回测目录。策略子文件夹在生成回测脚本时按需创建（由 `/backtest` 技能生成）。

```bash
mkdir -p backtesting
```

不要预先创建策略子文件夹。

### 第 6 步：配置 .env 文件

**6a. 检查项目根目录下是否存在 `.env.sample`。** 如果存在，则将其用作模板。

**6b. 使用 AskUserQuestion 向用户询问他们将回测哪些市场：**
- 印度市场（OpenAlgo） — 需要 OpenAlgo API 密钥
- 印度市场（DuckDB） — 直接加载数据库，无需 API
- 美国市场（yfinance） — 无需 API 密钥
- 加密货币市场（CCXT） — 可选 API 密钥用于私有数据

**6c. 如果用户选择了印度市场**，请询问他们的 OpenAlgo API 密钥：
- 询问： "输入您的 OpenAlgo API 密钥（来自 OpenAlgo 仪表板）："
- 如果用户提供了密钥，将其存储在 `.env`
- 如果用户跳过，则写入占位符

**6d. 如果用户选择了印度市场（DuckDB）**，请询问 DuckDB 数据库路径：
- 询问： "输入您的 DuckDB 数据库文件路径（例如，D:/data/market_data.duckdb）："
- 自动检测格式：如果数据库具有 `market_data` 表，其中包含 `symbol, exchange, interval, timestamp` 列，则为 OpenAlgo Historify 格式（存储为 `HISTORIFY_DB_PATH`）。否则存储为 `DUCKDB_PATH`。
- 如果用户同时具有 OpenAlgo Historify，请询问： "这是一个 OpenAlgo Historify 数据库吗？(y/n)"

**6e. 如果用户选择了加密货币市场**，请询问他们是否要配置交易所 API 密钥：
- 询问： "您是否有用于认证数据的交易所 API 密钥？(可选 — 无需密钥即可使用公共 OHLCV 数据)"
- 如果是，请询问 API 密钥和密钥，存储在 `.env`
- 如果不是，请在 `.env` 中留空

**6f. 在项目根目录中写入 `.env` 文件**。使用此模板，填写用户提供的任何密钥/路径：

```
# 印度市场（OpenAlgo）
OPENALGO_API_KEY={user_provided_key or "your_openalgo_api_key_here"}
OPENALGO_HOST=http://127.0.0.1:5000

# DuckDB 数据源（直接加载数据库 - 速度最快）
# 自定义 DuckDB（用户创建的 OHLCV 表）
DUCKDB_PATH={user_provided_path or ""}
# OpenAlgo Historify DuckDB（market_data 表具有 epoch 时间戳）
HISTORIFY_DB_PATH={user_provided_path or ""}

# 加密货币市场（CCXT） - 可选
CRYPTO_API_KEY={user_provided_key or ""}
CRYPTO_SECRET_KEY={user_provided_key or ""}
```

**6g. 如果存在，将 `.env` 添加到 `.gitignore`**（永远不要提交密钥）：

脚本使用 `find_dotenv()` 自动向上遍历并找到单个根 `.env`，因此不需要在子目录中复制副本。

```bash
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

### 第 7 步：验证安装

运行快速验证：

```bash
python -c "
import vectorbt as vbt
from openalgo import ta
import plotly
import duckdb
import anywidget
import nbformat
import openstatz
from dotenv import load_dotenv
print('All packages installed successfully')
print(f'  vectorbt: {vbt.__version__}')
print(f'  plotly: {plotly.__version__}')
print(f'  duckdb: {duckdb.__version__}')
print(f'  nbformat: {nbformat.__version__}')
print(f'  openstatz: {openstatz.__version__}')
print(f'  OpenAlgo ta: available (default indicator library)')
print(f'  python-dotenv: available')
"
```

如果用户选择了 TA-Lib，也使用 `python -c "import talib; print('TA-Lib available')"` 进行验证。如果导入失败，请告知用户需要先安装 C 库（见第 3 步）。

### 第 8 步：打印摘要

打印摘要，显示：
- 检测到的操作系统
- 使用的 Python 版本
- 虚拟环境路径
- 安装的包和版本
- 回测文件夹创建（策略子文件夹由 `/backtest` 按需创建）
- `.env` 文件状态（配置了密钥 / 占位符） — 项目根目录中的单个文件
- 提醒： "运行 `cp .env.sample .env` 并填写 API 密钥，如果您跳过了配置"

## 重要提示

- 永远不要全局安装包 — 始终使用虚拟环境
- TA-Lib C 库安装需要 Linux 上的管理员/sudo 权限
- 在 macOS 上，必须安装 Homebrew 才能使用 `brew install ta-lib`
- 如果用户已经有一个虚拟环境，请在创建新环境之前询问
- 回测/ 文件夹是所有生成的回测脚本将保存的位置
- 永远不要提交 `.env` 文件 — 它们包含密钥。始终使用 `.gitignore`。
- 如果用户在设置过程中提供了 API 密钥，请直接将其写入 `.env` — 不要要求他们手动编辑文件
- `python-dotenv` 包含在 pip 安装中，所有脚本都必须使用它来加载 `.env`
