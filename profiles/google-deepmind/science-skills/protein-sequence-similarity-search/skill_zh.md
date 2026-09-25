## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并按照其 Setup 指南确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/protein_sequence_similarity_search_LICENSE.txt`，则 (1) 显著通知用户检查 https://www.ebi.ac.uk/jdispatcher/sss/ncbiblast 和 https://colabfold.com 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env` 文件**: 确保您的家目录中存在 `.env` 文件。如果不存在，请创建一个。
4.  **`USER_EMAIL`** (可选但推荐): EBI 推荐用于 BLAST 任务跟踪，但该技能无需此信息即可工作。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此凭证。

## 目标

接收用户提供的氨基酸序列（或 `.fasta` 文件的路径），使用最快的可用方法搜索序列同源物，生成 Markdown 格式的顶部命中表格，解释关键比对指标，总结推断的蛋白质功能，并将结果本地保存以供未来的程序分析。

## 核心规则

-   **严格验证**: 对于 BLAST，仅使用下表中所列的数据库代码。
-   **无幻觉**: 如果脚本出错或未返回命中结果，请明确告知用户。不要编造序列同源物。
-   **不要解析输出文件**: 不要解析 JSON、a3m 或任何其他原始输出文件。依赖生成的 `.md` 文件进行总结。JSON 和其他输出仅用于后续工具使用。
-   **始终声明方法**: 每份报告都必须明确说明搜索是否使用了快速 MMseqs2 (ColabFold API) 或较慢的 EBI BLAST 方法。
-   **通知**: 如果使用此技能，请确保在输出中提及。明确声明使用的相应程序 (MMSEQS2 或 EBI BLAST) 和序列数据库。

## 搜索方法选择

根据用户请求选择搜索方法：

如果用户说“快速搜索”或“快速搜索”，或者没有请求特定方法/一般同源物搜索，或者您不确定：使用 `mmseqs2_search.py` 运行 MMseqs2 (快速，默认)。

如果 MMseqs2 失败（退出代码 2：RATELIMIT 或 API 错误）或用户明确请求“BLAST”或特定 BLAST 数据库（例如 `uniprotkb_swissprot`、`pdb`、`uniprotkb_human`）：使用 `uniprot_blast.py` 运行 BLAST。

## 说明

1.  从用户处识别查询。它可以是原始序列字符串（例如，“MKVLY...”）或本地文件路径（例如，“./data/sequence.fasta”）。
2.  **确定搜索方法** 使用上述列表。

### 路径 A：MMseqs2 搜索（默认）

1.  **生成文件名**: 根据输入生成描述性的输出文件名（例如，`proteinA_mmseqs2.json` 和 `proteinA_mmseqs2.md`）。
2.  执行 MMseqs2 脚本：

    *   **默认**:

    ```
    uv run scripts/mmseqs2_search.py <SEQUENCE_OR_FILE> -o <generated-filename.md> -j <generated-filename.json>
    ```

    *   **使用 mgnify**:

    ```
    uv run scripts/mmseqs2_search.py <SEQUENCE_OR_FILE> -o <generated-filename.md> -j <generated-filename.json> --include-mgnify
    ```

3.  脚本将查询 ColabFold MMseqs2 API 并轮询完成状态。这通常很快（不到 2 分钟）。
4.  **如果脚本以代码 2 退出**（API 失败，速率限制），自动回退到 BLAST（路径 B 下方）。通知用户：“MMseqs2 搜索失败，回退到 BLAST。”
5.  **读取结果**: 打开并读取生成的 `.md` 文件。

### 路径 B：BLAST 搜索（明确或回退）

1.  **数据库选择和验证**: 根据用户的提示确定最合适的数据库（或数据库）。参考下表中的 **可用 BLAST 数据库**。
    *   如果用户指定分类群（例如，“在微生物中查找同源物”），选择相应的 `Database Code`（例如，`uniprotkb_bacteria`）。
    *   如果用户明确请求精选命中，使用 `uniprotkb_swissprot`。
    *   如果未请求特定数据库，则不要指定 `--databases`。
    *   **验证**: 确保数据库代码与表中的条目完全匹配。如果用户请求的数据库不在列表中，**不要继续**并提供允许的列表。
2.  **生成文件名**:（例如，`proteinA_ebi_blast.json` 和 `proteinA_ebi_blast.md`）。
3.  此 API 需要将用户电子邮件地址设置为 `USER_EMAIL` 环境变量，以便包含在请求头中。您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此凭证，如果此技能与用户的请求相关。
4.  执行 BLAST 脚本：

    *   **默认（uniprotkb）**:

    ```
    uv run scripts/uniprot_blast.py <SEQUENCE_OR_FILE> -o <generated-filename.md> -j <generated-filename.json>
    ```

    *   **自定义数据库**:

    ```
    uv run scripts/uniprot_blast.py <SEQUENCE_OR_FILE> -o <generated-filename.md> -j <generated-filename.json> --databases <db1,db2>
    ```

5.  脚本将查询 EBI BLAST API 并轮询服务器。**注意**：这可能需要长达 15 分钟；请耐心等待。
6.  **读取结果**: 打开并读取生成的 `.md` 文件。

### 常见步骤（两种方法）

1.  **解释指标**: 总结前 3 到 5 个序列同源物。使用以下指标评估匹配质量：
    *   **Q-Cov (查询覆盖率)**: 高百分比意味着匹配覆盖了大部分查询序列。
    *   **E-value**: 较低的 E-value（例如，`1e-50`）表示极强的统计显著性。
    *   **Seq Identity**: 提供进化背景（高度保守与远缘同源物）。
2.  **执行功能分析**:
    *   如果结果表格包含蛋白质描述，直接分析它们：报告顶部同源物的特定蛋白质名称/功能，并总结发现的功能、结构域或蛋白质家族的多样性。
    *   如果结果仅包含 UniProt 访问号而没有描述（MMseqs2 常见），在使用其他适当方法查找前 3-5 个命中（使用 **uniprot-database** 技能或其他方法）进行总结之前，查找蛋白质名称和功能。
3.  通知用户新创建的文件（`.json` 和 `.md`）及其位置。

## 可用 BLAST 数据库

*   `uniprotkb` – UniProt 知识库（UniProt 知识库包括 UniProtKB/Swiss-Prot 和 UniProtKB/TrEMBL）：UniProt 知识库 (UniProtKB) 是广泛整理的蛋白质信息的中央访问点，包括功能、分类和交叉引用。搜索 UniProtKB 以检索有关特定序列的“所有已知信息”。
*   `uniprotkb_swissprot` – UniProtKB/Swiss-Prot（UniProtKB 的手动注释部分）：UniProt 知识库的手动注释子集。
*   `uniprotkb_swissprotsv` – UniProtKB/Swiss-Prot 异构体（UniProtKB/Swiss-Prot 的手动注释异构体）：UniProt 知识库的手动注释子集的异构体序列。
*   `uniprotkb_reference_proteomes` – UniProtKB 参考蛋白质组：UniProtKB 参考蛋白质组的分类子集。
*   `uniprotkb_trembl` – UniProtKB/TrEMBL（UniProtKB 的自动注释部分）：来自 ENA 序列（以前为 EMBL-Bank）编码序列翻译并使用自动过程生成的注释的 UniProt 知识库子集。
*   `uniprotkb_refprotswissprot` – UniProtKB 参考蛋白质组加 Swiss-Prot：UniProtKB 参考蛋白质组加 Swiss-Prot。
*   `uniprotkb_archaea` – UniProtKB 古菌：UniProt 知识库的考古分类子集。
*   `uniprotkb_arthropoda` – UniProtKB 节肢动物：UniProt 知识库的节肢动物分类子集。
*   `uniprotkb_bacteria` – UniProtKB 细菌：UniProt 知识库的细菌分类子集。
*   `uniprotkb_complete_microbial_proteomes` – UniProtKB 完整微生物蛋白质组：UniProt 知识库的完整微生物蛋白质组分类子集。
*   `uniprotkb_eukaryota` – UniProtKB 真核生物：UniProt 知识库的真核生物分类子集。
*   `uniprotkb_fungi` – UniProtKB 真菌：UniProt 知识库的真菌分类子集。
*   `uniprotkb_human` – UniProtKB 人类：UniProt 知识库的人类分类子集。
*   `uniprotkb_mammals` – UniProtKB 哺乳动物：UniProt 知识库的哺乳动物分类子集。
*   `uniprotkb_nematoda` – UniProtKB 线虫：UniProt 知识库的线虫分类子集。
*   `uniprotkb_rodents` – UniProtKB 啮齿动物：UniProt 知识库的啮齿动物分类子集。
*   `uniprotkb_vertebrates` – UniProtKB 脊椎动物：UniProt 知识库的脊椎动物分类子集。
*   `uniprotkb_viridiplantae` – UniProtKB 绿色植物：UniProt 知识库的绿色植物分类子集。
*   `uniprotkb_viruses` – UniProtKB 病毒：UniProt 知识库的病毒分类子集。
*   `uniprotkb_enzyme` – UniProtKB 酶：UniProt 知识库的酶分类子集。
*   `uniprotkb_covid19` – UniProtKB COVID-19：UniProt 知识库的 COVID-19 分类子集。
*   `uniref100` – UniProt 100% 聚类（UniRef100）：包含 100% 相同序列的 UniProt 参考聚类 (UniRef)。
*   `uniref90` – UniProt 90% 聚类（UniRef90）：包含 90% 相同序列的 UniProt 参考聚类 (UniRef)。
*   `uniref50` – UniProt 50% 聚类（UniRef50）：包含 50% 相同序列的 UniProt 参考聚类 (UniRef)。
*   `pdb` – 蛋白质结构序列（PDBe 蛋白质结构序列）：来自布鲁克海文蛋白质数据银行 (PDB) 的蛋白质序列。
