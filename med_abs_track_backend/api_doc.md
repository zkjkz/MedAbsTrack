# NCBI E-utilities API 接口文档

## 目录
- [简介](#简介)
- [通用使用指南](#通用使用指南)
- [E-utilities DTDs](#e-utilities-dtds)
- [EInfo](#einfo)
- [ESearch](#esearch)
- [EPost](#epost)
- [ESummary](#esummary)
- [EFetch](#efetch)
- [ELink](#elink)
- [EGQuery](#egquery)
- [ESpell](#espell)
- [ECitMatch](#ecitmatch)

## 简介

本文档作为NCBI E-utilities所有支持参数的参考，包括可接受的值和使用指南。大多数E-utilities都有一组必需参数和一些扩展功能的可选参数。

## 通用使用指南

在所有E-utility请求中应包含以下两个参数：

- **tool**: 应用程序名称，必须是没有内部空格的字符串。
- **email**: 用户的电子邮件地址，必须是没有内部空格的字符串，应该是有效的电子邮件地址。

如果预计从单个IP地址每秒发送超过3个E-utility请求，请考虑包含以下参数：

- **api_key**: API密钥，适用于每秒发送超过3个请求的站点。

## E-utilities DTDs

除EFetch外，每个E-utility都生成特定于该工具的单一XML输出格式。这些DTD的链接在E-utility返回的XML头部中提供。

ESummary 2.0版本为每个Entrez数据库生成唯一的XML DocSums，因此每个数据库对2.0版本DocSums有唯一的DTD。

EFetch以多种格式生成输出，其中一些是XML。这些XML格式也遵循特定于相关Entrez数据库的DTD或架构。

PubMed DTD:
- PubMed DTD 2018年6月至今
- PubMed DTD 2019年1月 - 即将推出的DTD

## EInfo

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi`

### 功能
- 提供所有有效Entrez数据库名称的列表
- 提供单个数据库的统计信息，包括索引字段和可用链接名称列表

### 必需参数
无。如果没有提供db参数，einfo将返回所有有效Entrez数据库名称的列表。

### 可选参数
- **db**: 要获取统计信息的目标数据库。值必须是有效的Entrez数据库名称。
- **version**: 用于指定2.0版EInfo XML。唯一支持的值是'2.0'。
- **retmode**: 检索类型，确定返回输出的格式。默认值为'xml'，但也支持'json'。

### 示例
- 返回所有Entrez数据库名称列表：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi
  ```
- 返回Entrez Protein的2.0版统计信息：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=protein&version=2.0
  ```

## ESearch

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`

### 功能
- 提供与文本查询匹配的UID列表
- 将搜索结果发布到History服务器
- 从存储在History服务器上的数据集下载所有UID
- 组合或限制存储在History服务器上的UID数据集
- 排序UID集

### 必需参数
- **db**: 要搜索的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。
- **term**: Entrez文本查询。所有特殊字符必须进行URL编码。

### 可选参数 - History服务器
- **usehistory**: 设置为'y'时，ESearch将把搜索操作产生的UID发布到History服务器。
- **WebEnv**: 从先前的ESearch、EPost或ELink调用返回的Web环境字符串。
- **query_key**: 由先前的ESearch、EPost或ELink调用返回的整数查询键。

### 可选参数 - 检索
- **retstart**: 在XML输出中显示的第一个UID的顺序索引（默认为0）。
- **retmax**: 在XML输出中显示的检索集UID总数（默认为20），最多10,000条记录。
- **rettype**: 检索类型。ESearch允许两个值：'uilist'（默认）和'count'。
- **retmode**: 检索类型。默认值为'xml'，但也支持'json'。
- **sort**: 指定ESearch输出中UID的排序方法。

### 可选参数 - 日期
- **datetype**: 用于限制搜索的日期类型。
- **reldate**: 设置为整数n时，搜索仅返回在最近n天内由datetype指定日期的项目。
- **mindate, maxdate**: 用于按datetype指定的日期限制搜索结果的日期范围。

### 示例
- 在PubMed中搜索术语"cancer"，获取在最近60天内具有Entrez日期的摘要：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&reldate=60&datetype=edat&retmax=100&usehistory=y
  ```
- 在PubMed中搜索期刊PNAS，第97卷，从列表中的第七个PMID开始检索六个PMID：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=PNAS[ta]+AND+97[vi]&retstart=6&retmax=6&tool=biomed3
  ```

## EPost

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi`

### 功能
- 将UID列表上传到Entrez History服务器
- 将UID列表附加到附加到Web环境的现有UID列表集

### 必需参数
- **db**: 包含输入列表中UID的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。
- **id**: UID列表。可以提供单个UID或以逗号分隔的UID列表。

### 可选参数
- **WebEnv**: Web环境。如果提供，此参数指定将接收由post发送的UID列表的Web环境。

### 示例
- 将记录发布到PubMed：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi?db=pubmed&id=11237011,12466850
  ```

## ESummary

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`

### 功能
- 返回输入UID列表的文档摘要（DocSums）
- 返回存储在Entrez History服务器上的UID集的DocSums

### 必需参数
- **db**: 从中检索DocSums的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。

### 必需参数 - 仅在输入来自UID列表时使用
- **id**: UID列表。可以提供单个UID或以逗号分隔的UID列表。

### 必需参数 - 仅在输入来自Entrez History服务器时使用
- **query_key**: 查询键。此整数指定附加到给定Web环境的UID列表中的哪一个将用作ESummary的输入。
- **WebEnv**: Web环境。此参数指定包含要作为ESummary输入提供的UID列表的Web环境。

### 可选参数 - 检索
- **retstart**: 要检索的第一个DocSum的顺序索引（默认为1）。
- **retmax**: 从输入集中检索的DocSums总数，最多10,000个。
- **retmode**: 检索类型。默认值为'xml'，但也支持'json'。
- **version**: 用于指定2.0版ESummary XML。唯一支持的值是'2.0'。

### 示例
- PubMed：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=11850928,11482001
  ```
- PubMed，2.0版XML：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=11850928,11482001&version=2.0
  ```

## EFetch

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

### 功能
- 返回输入UID列表的格式化数据记录
- 返回存储在Entrez History服务器上的UID集的格式化数据记录

### 必需参数
- **db**: 从中检索记录的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。

### 必需参数 - 仅在输入来自UID列表时使用
- **id**: UID列表。可以提供单个UID或以逗号分隔的UID列表。

### 必需参数 - 仅在输入来自Entrez History服务器时使用
- **query_key**: 查询键。此整数指定附加到给定Web环境的UID列表中的哪一个将用作EFetch的输入。
- **WebEnv**: Web环境。此参数指定包含要作为EFetch输入提供的UID列表的Web环境。

### 可选参数 - 检索
- **retmode**: 检索模式。此参数指定返回记录的数据格式，如纯文本、HTML或XML。
- **rettype**: 检索类型。此参数指定返回的记录视图，如PubMed的Abstract或MEDLINE，或蛋白质的GenPept或FASTA。
- **retstart**: 要检索的第一条记录的顺序索引（默认为0）。
- **retmax**: 从输入集中检索的记录总数，最多10,000个。

### 可选参数 - 序列数据库
- **strand**: 要检索的DNA链。可用值为"1"表示正链，"2"表示负链。
- **seq_start**: 要检索的第一个序列碱基。
- **seq_stop**: 要检索的最后一个序列碱基。
- **complexity**: 要返回的数据内容。

### 示例
- PubMed - 以文本摘要形式获取PMID 17284678和9997：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=17284678,9997&retmode=text&rettype=abstract
  ```
- 获取XML格式的PMID：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=11748933,11700088&retmode=xml
  ```

## ELink

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi`

### 功能
- 返回在相同或不同Entrez数据库中与输入UID集链接的UID
- 返回与匹配Entrez查询的同一Entrez数据库中的其他UID链接的UID
- 检查同一数据库中一组UID的Entrez链接是否存在
- 列出UID可用的链接
- 列出一组UID的LinkOut URL和属性
- 列出一组UID的主要LinkOut提供者的超链接
- 为单个UID创建到主要LinkOut提供者的超链接

### 必需参数
- **db**: 从中检索UID的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。
- **dbfrom**: 包含输入UID的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。
- **cmd**: ELink命令模式。指定ELink将执行哪个功能。

可用的命令模式包括：
- cmd=neighbor（默认）
- cmd=neighbor_score
- cmd=neighbor_history
- cmd=acheck
- cmd=ncheck
- cmd=lcheck
- cmd=llinks
- cmd=llinkslib
- cmd=prlinks

### 必需参数 - 仅在输入来自UID列表时使用
- **id**: UID列表。可以提供单个UID或以逗号分隔的UID列表。

### 必需参数 - 仅在输入来自Entrez History服务器时使用
- **query_key**: 查询键。此整数指定附加到给定Web环境的UID列表中的哪一个将用作ELink的输入。
- **WebEnv**: Web环境。此参数指定包含要作为ELink输入提供的UID列表的Web环境。

### 可选参数 - 检索
- **retmode**: 检索类型。默认值为'xml'，但也支持'json'。
- **idtype**: 指定序列数据库（nuccore、popset、protein）返回标识符的类型。

### 可选参数 - 限制链接的输出集
- **linkname**: 要检索的Entrez链接的名称。Entrez中的每个链接都被赋予dbfrom_db_subset形式的名称。
- **term**: 用于限制链接UID输出集的Entrez查询。
- **holding**: LinkOut提供者的名称。仅返回由holding指定的LinkOut提供者的URL。

### 可选参数 - 日期
- **datetype**: 用于限制链接操作的日期类型。
- **reldate**: 设置为整数n时，ELink仅返回在最近n天内由datetype指定日期的项目。
- **mindate, maxdate**: 用于按datetype指定的日期限制链接操作的日期范围。

### 示例
- 从蛋白质链接到基因：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=protein&db=gene&id=15718680,157427902
  ```
- 查找与PMID 20210808相关的文章：
  ```
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&id=20210808&cmd=neighbor_score
  ```

## EGQuery

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/egquery.fcgi`

### 功能
提供单个文本查询在所有Entrez数据库中检索的记录数。

### 必需参数
- **term**: Entrez文本查询。所有特殊字符必须进行URL编码。

### 示例
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/egquery.fcgi?term=asthma
```

## ESpell

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/espell.fcgi`

### 功能
为给定数据库中单个文本查询内的术语提供拼写建议。

### 必需参数
- **db**: 要搜索的数据库。值必须是有效的Entrez数据库名称（默认为pubmed）。
- **term**: Entrez文本查询。所有特殊字符必须进行URL编码。

### 示例
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/espell.fcgi?db=pubmed&term=asthmaa+OR+alergies
```

## ECitMatch

### 基本URL
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi`

### 功能
检索与一组输入引用字符串对应的PubMed ID（PMID）。

### 必需参数
- **db**: 要搜索的数据库。唯一支持的值是'pubmed'。
- **rettype**: 检索类型。唯一支持的值是'xml'。
- **bdata**: 引用字符串。每个输入引用必须由以下格式的引用字符串表示：
  ```
  journal_title|year|volume|first_page|author_name|your_key|
  ```
  多个引用字符串可以通过用回车符（%0D）分隔字符串来提供。

### 示例
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi?db=pubmed&retmode=xml&bdata=proc+natl+acad+sci+u+s+a|1991|88|3248|mann+bj|Art1|%0Dscience|1987|235|182|palmenberg+ac|Art2|
```