from datetime import datetime
from fastapi import APIRouter, Depends, Query
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_literature.service.paper_search_service import PaperSearchService
from utils.log_util import logger
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel


paperSearchController = APIRouter(
    prefix="/literature/paper_search",
    dependencies=[Depends(LoginService.get_current_user)],
)


@paperSearchController.get(
    "/search",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:search"))],
    summary="搜索PubMed文献",
    description="通过关键词搜索PubMed文献，支持分页、排序和日期范围筛选",
)
async def search_pubmed_papers(
    query: str = Query(..., description="搜索关键词"),
    page_num: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(10, description="每页记录数"),
    sort_by: str = Query("relevance", description="排序方式（relevance|pub_date）"),
    min_date: Optional[str] = Query(None, description="最早日期，格式为YYYY/MM/DD"),
    max_date: Optional[str] = Query(None, description="最晚日期，格式为YYYY/MM/DD"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    logger.info(f"用户{current_user.user.user_name}搜索PubMed文献: {query}")
    # 构建日期范围参数
    date_range = None
    if min_date or max_date:
        date_range = {}
        if min_date:
            date_range["min_date"] = min_date
        if max_date:
            date_range["max_date"] = max_date

    # 调用服务层方法搜索文献
    search_result = await PaperSearchService.search_pubmed(
        query=query,
        page_num=page_num,
        page_size=page_size,
        sort_by=sort_by,
        date_range=date_range,
        db=query_db,
    )
    if search_result["success"]:
        logger.info(f"搜索成功，找到{search_result['total']}条结果")

        # 构建分页响应对象
        page_response = {
            "rows": search_result["rows"],
            "total": search_result["total"],
            "pageNum": page_num,
            "pageSize": page_size,
            "hasNext": (page_num * page_size) < search_result["total"],
        }

        return ResponseUtil.success(data=page_response)
    else:
        logger.error(f"搜索失败: {search_result['msg']}")
        return ResponseUtil.error(msg=search_result["msg"])


@paperSearchController.get(
    "/detail/{pmid}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:detail"))],
    summary="获取PubMed文献详情",
    description="通过PMID获取PubMed文献的详细信息",
)
async def get_paper_detail(
    pmid: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    logger.info(f"用户{current_user.user.user_name}获取文献详情: PMID={pmid}")

    # 这里我们使用search_pubmed方法来获取单篇文献的详情
    # 直接使用PMID作为搜索词，并将页码和页大小设置为1
    search_result = await PaperSearchService.search_pubmed(
        query=f"{pmid}[uid]",  # 使用PMID作为唯一标识符搜索
        page_num=1,
        page_size=1,
        db=query_db,
    )

    if search_result["success"] and search_result["rows"]:
        paper_detail = search_result["rows"][0]
        logger.info(f"获取文献详情成功: {paper_detail['title']}")
        return ResponseUtil.success(data=paper_detail)
    else:
        error_msg = search_result.get("msg", f"未找到PMID为{pmid}的文献")
        logger.error(f"获取文献详情失败: {error_msg}")
        return ResponseUtil.error(msg=error_msg)
