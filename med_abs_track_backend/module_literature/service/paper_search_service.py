import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, TypeVar, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module_literature.entity.do.paper_do import PmsPaper
from utils.log_util import logger
from config.env import NCBIConfig

# 定义一个类型变量用于泛型函数
T = TypeVar("T")


class PaperSearchService:
    """文献搜索服务，提供PubMed文献检索和收藏功能"""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    TOOL_NAME = NCBIConfig.ncbi_tool_name
    EMAIL = NCBIConfig.ncbi_email
    API_KEY = NCBIConfig.ncbi_api_key

    # 添加API请求批处理和限流参数
    MAX_REQUESTS_PER_SECOND = (
        10 if API_KEY else 3
    )  # 有API_KEY时可以每秒发送10个请求，否则限制为3个
    BATCH_SIZE = 100  # 增加批处理大小以减少API调用

    # 添加简单的内存缓存
    _cache = {}
    _cache_expiry = {}
    _cache_ttl = timedelta(minutes=30)  # 缓存有效期30分钟

    @classmethod
    def _get_cache_key(cls, query, page_num, page_size, sort_by, date_range):
        """生成缓存键"""
        cache_parts = [query, str(page_num), str(page_size), sort_by]
        if date_range:
            cache_parts.extend(
                [date_range.get("min_date", ""), date_range.get("max_date", "")]
            )
        return tuple(cache_parts)

    @classmethod
    def _get_from_cache(cls, cache_key):
        """从缓存中获取结果"""
        if cache_key in cls._cache and datetime.now() < cls._cache_expiry.get(
            cache_key, datetime.min
        ):
            return cls._cache[cache_key]
        return None

    @classmethod
    def _set_to_cache(cls, cache_key, result):
        """将结果存入缓存"""
        cls._cache[cache_key] = result
        cls._cache_expiry[cache_key] = datetime.now() + cls._cache_ttl
        cls._clear_expired_cache()

    @classmethod
    def _clear_expired_cache(cls) -> None:
        """清理过期的缓存项"""
        now = datetime.now()
        expired_keys = [k for k, v in cls._cache_expiry.items() if v < now]
        for key in expired_keys:
            if key in cls._cache:
                del cls._cache[key]
            if key in cls._cache_expiry:
                del cls._cache_expiry[key]

    @classmethod
    async def _prepare_api_params(cls, base_params: Dict[str, str]) -> Dict[str, str]:
        """
        准备API请求参数，添加通用参数和API密钥

        Args:
            base_params: 基础参数字典

        Returns:
            添加了通用参数的参数字典
        """
        params = {
            **base_params,
            "tool": cls.TOOL_NAME,
            "email": cls.EMAIL,
        }

        # 添加API_KEY (如果配置了)
        if cls.API_KEY:
            params["api_key"] = cls.API_KEY

        return params

    @classmethod
    async def _retry_request(
        cls,
        session: aiohttp.ClientSession,
        url: str,
        params: Dict[str, str],
        process_response: Callable[[aiohttp.ClientResponse], Coroutine[Any, Any, T]],
        error_message: str,
        max_retries: int = 3,
        retry_delay: int = 1,
    ) -> Optional[T]:
        """
        通用的API请求重试逻辑

        Args:
            session: aiohttp会话
            url: 请求URL
            params: 请求参数
            process_response: 处理响应的回调函数
            error_message: 错误日志消息
            max_retries: 最大重试次数
            retry_delay: 重试延迟秒数

        Returns:
            处理后的响应结果，失败时返回None
        """
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"{error_message}: {response.status}, {error_text}"
                        )
                        retry_count += 1
                        if retry_count >= max_retries:
                            return None
                        await asyncio.sleep(retry_delay)
                        continue

                    return await process_response(response)

            except Exception as e:
                logger.error(f"{error_message} 异常: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    return None
                await asyncio.sleep(retry_delay)

        return None

    @classmethod
    def _create_error_response(cls, msg: str, total: int = 0) -> Dict[str, Any]:
        """
        创建错误响应对象

        Args:
            msg: 错误消息
            total: 总记录数

        Returns:
            错误响应字典
        """
        return {
            "success": False,
            "msg": msg,
            "data": None,
            "total": total,
            "rows": [],
        }

    @classmethod
    async def search_pubmed(
        cls,
        query: str,
        page_num: int = 1,
        page_size: int = 10,
        sort_by: str = "relevance",
        date_range: Optional[Dict[str, str]] = None,
        db: Optional[AsyncSession] = None,
        include_perioperative: bool = True,  # 新增参数，控制是否默认包含围手术期相关文章
    ) -> Dict[str, Any]:
        """
        使用PubMed的ESearch和ESummary API搜索文献

        Args:
            query: 搜索关键词，支持布尔运算符（AND, OR, NOT）和字段限制（如 author[au], title[ti]）
            page_num: 页码（从1开始）
            page_size: 每页记录数
            sort_by: 排序方式（relevance|pub_date）
            date_range: 日期范围，格式为 {'min_date': 'YYYY/MM/DD', 'max_date': 'YYYY/MM/DD'}
            db: 数据库会话，如果提供，将检查论文是否已保存
            include_perioperative: 是否默认包含围手术期相关文章，设为True时会自动在查询中添加围手术期条件

        Returns:
            包含搜索结果的字典
        """
        # 检查参数有效性
        if not query or not query.strip():
            if include_perioperative:
                # 如果未提供查询但需要默认包含围手术期，则直接使用围手术期作为查询
                query = "围手术期[All Fields] OR perioperative[All Fields]"
            else:
                return cls._create_error_response("搜索关键词不能为空")
        elif (
            include_perioperative
            and "围手术期" not in query
            and "perioperative" not in query.lower()
        ):
            # 如果查询中未包含围手术期关键词，则添加围手术期条件
            query = f"({query}) AND (围手术期[All Fields] OR perioperative[All Fields])"

        # 尝试从缓存获取结果
        cache_key = cls._get_cache_key(query, page_num, page_size, sort_by, date_range)
        cached_result = cls._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"从缓存获取搜索结果: {query}, 页码: {page_num}")

            # 如果需要检查保存状态且提供了数据库连接，则更新保存状态
            if db is not None and "rows" in cached_result and cached_result["rows"]:
                await cls._update_saved_status(db, cached_result["rows"])

            return cached_result

        try:
            # 计算偏移量
            retstart = (page_num - 1) * page_size

            # 构建ESearch请求参数
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retstart": str(retstart),
                "retmax": str(page_size),
                "usehistory": "y",
            }

            # 添加排序参数
            if sort_by == "pub_date":
                search_params["sort"] = "pub_date"

            # 添加日期参数
            if date_range:
                if "min_date" in date_range:
                    search_params["mindate"] = date_range["min_date"].replace("/", "")
                if "max_date" in date_range:
                    search_params["maxdate"] = date_range["max_date"].replace("/", "")
                search_params["datetype"] = "pdat"  # 使用发布日期

            # 创建一个带重试机制的aiohttp会话
            retry_options = aiohttp.ClientTimeout(total=30, connect=10)
            async with aiohttp.ClientSession(timeout=retry_options) as session:
                # 准备通用参数
                search_params = await cls._prepare_api_params(search_params)

                # 第一步：获取ID列表和Web环境参数
                esearch_url = f"{cls.BASE_URL}/esearch.fcgi"

                # 处理搜索结果
                async def process_search_response(response):
                    search_result = await response.json()
                    if "esearchresult" not in search_result:
                        logger.error(f"PubMed ESearch API返回格式异常: {search_result}")
                        return None
                    return search_result

                search_result = await cls._retry_request(
                    session,
                    esearch_url,
                    search_params,
                    process_search_response,
                    "PubMed ESearch API请求失败",
                )

                if not search_result:
                    return cls._create_error_response("PubMed API请求失败")

                result = search_result["esearchresult"]
                id_list = result.get("idlist", [])
                total = int(result.get("count", 0))
                web_env = result.get("webenv", "")
                query_key = result.get("querykey", "")

                if not id_list:
                    result = {
                        "success": True,
                        "msg": "未找到匹配的文献",
                        "data": None,
                        "total": 0,
                        "rows": [],
                    }
                    cls._set_to_cache(cache_key, result)
                    return result

                # 第二步：使用WebEnv获取文献摘要信息
                summary_params = {
                    "db": "pubmed",
                    "retmode": "json",
                }

                # 准备通用参数
                summary_params = await cls._prepare_api_params(summary_params)

                # 优先使用WebEnv参数批量获取摘要
                if web_env and query_key:
                    summary_params["WebEnv"] = web_env
                    summary_params["query_key"] = query_key
                    summary_params["retstart"] = str(retstart)
                    summary_params["retmax"] = str(page_size)
                else:
                    # 回退到直接使用ID列表
                    summary_params["id"] = ",".join(id_list)

                esummary_url = f"{cls.BASE_URL}/esummary.fcgi"

                # 处理摘要响应
                async def process_summary_response(response):
                    summary_result = await response.json()
                    if "result" not in summary_result:
                        logger.error(
                            f"PubMed ESummary API返回格式异常: {summary_result}"
                        )
                        return None
                    return summary_result

                summary_result = await cls._retry_request(
                    session,
                    esummary_url,
                    summary_params,
                    process_summary_response,
                    "PubMed ESummary API请求失败",
                )

                if not summary_result:
                    return cls._create_error_response("PubMed摘要信息获取失败", total)

                # 处理文献列表
                papers = []
                paper_info_map = {}

                for paper_id in id_list:
                    if paper_id not in summary_result["result"]:
                        continue

                    paper_data = summary_result["result"][paper_id]

                    # 提取作者信息
                    authors = []
                    if "authors" in paper_data:
                        for author in paper_data["authors"]:
                            if author["authtype"] == "Author":
                                authors.append(
                                    {
                                        "name": author["name"],
                                        "authorOrder": len(authors) + 1,
                                    }
                                )

                    # 处理发布日期
                    published_date = None
                    if "pubdate" in paper_data:
                        try:
                            date_str = paper_data["pubdate"]
                            # 尝试处理多种格式的日期
                            if len(date_str) >= 4:  # 至少包含年份
                                year = int(date_str[:4])
                                month = 1
                                day = 1

                                parts = date_str.replace("-", " ").split()
                                if len(parts) >= 2 and parts[1].isdigit():
                                    month = int(parts[1])
                                if len(parts) >= 3 and parts[2].isdigit():
                                    day = int(parts[2])

                                published_date = f"{year:04d}-{month:02d}-{day:02d}"
                        except Exception as e:
                            logger.warning(
                                f"处理发布日期错误: {e}, 原始值: {paper_data.get('pubdate')}"
                            )

                    # 收集DOI
                    doi = None
                    if "articleids" in paper_data:
                        for article_id in paper_data["articleids"]:
                            if article_id["idtype"] == "doi":
                                doi = article_id["value"]
                                break

                    # 创建基本论文信息
                    paper_info = {
                        "pmid": paper_id,
                        "doi": doi,
                        "title": paper_data.get("title", ""),
                        "abstract": "",  # 稍后将批量获取
                        "journal": paper_data.get(
                            "fulljournalname", paper_data.get("source", "")
                        ),
                        "publishStatus": paper_data.get("pubstatus", ""),
                        "publishedDate": published_date,
                        "authors": authors,
                        "keywords": [],  # 稍后将批量获取
                        "isSaved": False,  # 标记是否已保存到本地数据库
                    }

                    papers.append(paper_info)
                    paper_info_map[paper_id] = paper_info

                # 批量获取摘要和关键词
                if papers:
                    # 获取所有PMID
                    pmids = [paper["pmid"] for paper in papers]

                    # 按批次处理PMID以获取详细信息
                    for i in range(0, len(pmids), cls.BATCH_SIZE):
                        batch_pmids = pmids[i : i + cls.BATCH_SIZE]
                        await cls._batch_fetch_paper_details(
                            session, batch_pmids, paper_info_map
                        )

                    # 如果提供了数据库会话，批量检查论文是否已保存
                    if db is not None:
                        await cls._update_saved_status(db, papers)

                result = {
                    "success": True,
                    "msg": "搜索成功",
                    "data": None,
                    "total": total,
                    "rows": papers,
                }

                # 将结果存入缓存
                cls._set_to_cache(cache_key, result)

                return result

        except Exception as e:
            logger.error(f"PubMed搜索异常: {str(e)}")
            return cls._create_error_response(f"PubMed搜索异常: {str(e)}")

    @classmethod
    async def _update_saved_status(cls, db: AsyncSession, papers: List[Dict]) -> None:
        """
        批量更新论文的保存状态

        Args:
            db: 数据库会话
            papers: 论文列表
        """
        try:
            # 提取所有PMID
            pmids = [paper["pmid"] for paper in papers if paper.get("pmid")]

            if not pmids:
                return

            # 批量查询数据库中已存在的论文
            stmt = select(PmsPaper.pmid, PmsPaper.paper_id).where(
                PmsPaper.pmid.in_(pmids)
            )
            result = await db.execute(stmt)
            saved_papers = {row[0]: row[1] for row in result.fetchall()}

            # 更新论文保存状态
            for paper in papers:
                pmid = paper.get("pmid")
                if pmid and pmid in saved_papers:
                    paper["isSaved"] = True
                    paper["paperId"] = saved_papers[pmid]
        except Exception as e:
            logger.warning(f"批量更新论文保存状态异常: {str(e)}")

    @classmethod
    async def _batch_fetch_paper_details(
        cls,
        session: aiohttp.ClientSession,
        pmids: List[str],
        paper_info_map: Dict[str, Dict],
    ) -> None:
        """
        批量获取论文的详细信息（摘要和关键词）

        Args:
            session: aiohttp会话
            pmids: 论文PMID列表
            paper_info_map: 论文信息映射，用于更新结果
        """
        if not pmids:
            return

        try:
            # 使用信号量限制并发请求数量
            semaphore = asyncio.Semaphore(cls.MAX_REQUESTS_PER_SECOND)

            # 准备通用参数
            base_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
            }

            common_params = await cls._prepare_api_params(base_params)

            # 获取XML格式的完整记录，包含摘要和MeSH关键词
            xml_params = {**common_params, "retmode": "xml"}
            efetch_url = f"{cls.BASE_URL}/efetch.fcgi"

            async with semaphore:
                # 处理XML响应
                async def process_xml_response(response):
                    import xml.etree.ElementTree as ET

                    xml_content = await response.text()

                    try:
                        root = ET.fromstring(xml_content)

                        # 处理每篇文章
                        articles = root.findall(".//PubmedArticle")

                        for article in articles:
                            # 提取PMID
                            pmid_elem = article.find(".//PMID")
                            if (
                                pmid_elem is None
                                or pmid_elem.text not in paper_info_map
                            ):
                                continue

                            pmid = pmid_elem.text
                            paper_info = paper_info_map[pmid]

                            # 提取摘要
                            abstract_texts = article.findall(".//AbstractText")
                            abstract = ""

                            for abstract_text in abstract_texts:
                                # 检查是否有标签属性
                                label = abstract_text.get("Label")
                                if label:
                                    abstract += f"{label}: {abstract_text.text}\n"
                                else:
                                    abstract += f"{abstract_text.text}\n"

                            paper_info["abstract"] = abstract.strip()

                            # 提取MeSH关键词
                            mesh_headings = article.findall(".//MeshHeading")
                            for mesh in mesh_headings:
                                descriptor = mesh.find("./DescriptorName")
                                if (
                                    descriptor is not None
                                    and "UI" in descriptor.attrib
                                    and descriptor.text
                                ):
                                    paper_info["keywords"].append(
                                        {
                                            "id": descriptor.attrib["UI"],
                                            "term": descriptor.text,
                                            "type": "MeSH",
                                        }
                                    )

                            # 尝试提取作者关键词（如果有）
                            author_keywords = article.findall(".//Keyword")
                            for keyword in author_keywords:
                                if keyword.text:
                                    paper_info["keywords"].append(
                                        {
                                            "id": None,
                                            "term": keyword.text,
                                            "type": "Author",
                                        }
                                    )
                        return True
                    except Exception as e:
                        logger.warning(f"解析XML响应异常: {str(e)}")
                        return False

                await cls._retry_request(
                    session,
                    efetch_url,
                    xml_params,
                    process_xml_response,
                    "批量获取论文XML详情失败",
                )

        except Exception as e:
            logger.warning(f"批量获取论文详情失败: {str(e)}")
