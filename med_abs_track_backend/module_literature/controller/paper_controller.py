from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, Query
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_literature.service.paper_service import PaperService
from module_literature.service.paper_search_service import PaperSearchService
from module_literature.entity.vo.paper_vo import (
    DeletePaperModel,
    PaperModel,
    PaperDetailModel,
    PaperPageQueryModel,
    CrudPaperAuthorModel,
    CrudPaperKeywordModel,
    PaperAuthorResponseModel,
    PaperKeywordResponseModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil
from typing import Optional


paperController = APIRouter(
    prefix="/literature/paper", dependencies=[Depends(LoginService.get_current_user)]
)


@paperController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:list"))],
    summary="获取围手术期相关论文信息列表",
    description="获取围手术期相关论文列表，支持布尔检索。支持AND、OR、NOT等布尔运算符和字段限制，如author[au]、title[ti]等。",
)
async def get_literature_paper_list(
    request: Request,
    query: str = Query(
        "",
        description="搜索关键词，支持布尔运算符(AND, OR, NOT)和字段限制，如author[au], title[ti]",
    ),
    page_num: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(10, description="每页记录数"),
    sort_by: str = Query(
        "relevance", description="排序方式: relevance(相关性)或pub_date(发布日期)"
    ),
    min_date: Optional[str] = Query(None, description="起始日期，格式为YYYY/MM/DD"),
    max_date: Optional[str] = Query(None, description="截止日期，格式为YYYY/MM/DD"),
    include_perioperative: bool = Query(
        True, description="是否默认包含围手术期相关文章"
    ),
    query_db: AsyncSession = Depends(get_db),
):
    """获取围手术期相关论文列表，支持布尔检索"""
    # 确定是使用本地数据库查询还是PubMed在线查询
    if query:
        # 使用在线PubMed检索
        # 构建日期范围参数
        date_range = None
        if min_date or max_date:
            date_range = {}
            if min_date:
                date_range["min_date"] = min_date
            if max_date:
                date_range["max_date"] = max_date

        # 调用PubMed搜索服务
        search_result = await PaperSearchService.search_pubmed(
            query=query,
            page_num=page_num,
            page_size=page_size,
            sort_by=sort_by,
            date_range=date_range,
            db=query_db,
            include_perioperative=include_perioperative,
        )

        logger.info(
            f"PubMed搜索完成，关键词: {query}, 获取到{search_result.get('total', 0)}条结果"
        )

        return ResponseUtil.success(
            data=search_result.get("data"),
            rows=search_result.get("rows", []),
            total=search_result.get("total", 0),
            msg=search_result.get("msg", "搜索成功"),
        )
    else:
        # 如果没有查询条件，则使用本地数据库查询
        paper_page_query = PaperPageQueryModel(pageNum=page_num, pageSize=page_size)
        paper_page_query_result = await PaperService.get_paper_list_services(
            query_db, paper_page_query, is_page=True
        )
        logger.info("从本地数据库获取文献列表成功")

        return ResponseUtil.success(model_content=paper_page_query_result)


@paperController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:add"))],
    summary="添加围手术期相关论文信息",
    description="添加围手术期相关论文信息",
)
@ValidateFields(validate_model="add_paper")
@Log(title="围手术期相关论文信息", business_type=BusinessType.INSERT)
async def add_literature_paper(
    request: Request,
    add_paper: PaperModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_paper.create_by = current_user.user.user_name
    add_paper.create_time = datetime.now()
    add_paper.update_by = current_user.user.user_name
    add_paper.update_time = datetime.now()
    add_paper_result = await PaperService.add_paper_services(query_db, add_paper)
    logger.info(add_paper_result.message)

    return ResponseUtil.success(msg=add_paper_result.message)


@paperController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:edit"))],
    summary="更新围手术期相关论文信息",
    description="更新围手术期相关论文信息",
)
@ValidateFields(validate_model="edit_paper")
@Log(title="围手术期相关论文信息", business_type=BusinessType.UPDATE)
async def edit_literature_paper(
    request: Request,
    edit_paper: PaperModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_paper.update_by = current_user.user.user_name
    edit_paper.update_time = datetime.now()
    edit_paper_result = await PaperService.edit_paper_services(query_db, edit_paper)
    logger.info(edit_paper_result.message)

    return ResponseUtil.success(msg=edit_paper_result.message)


@paperController.delete(
    "/{paper_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:remove"))],
    summary="删除围手术期相关论文信息",
    description="删除围手术期相关论文信息",
)
@Log(title="围手术期相关论文信息", business_type=BusinessType.DELETE)
async def delete_literature_paper(
    request: Request, paper_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_paper = DeletePaperModel(paperIds=paper_ids)
    delete_paper_result = await PaperService.delete_paper_services(
        query_db, delete_paper
    )
    logger.info(delete_paper_result.message)

    return ResponseUtil.success(msg=delete_paper_result.message)


@paperController.get(
    "/{paper_id}",
    response_model=PaperDetailModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:query"))],
    summary="获取围手术期相关论文信息详情",
    description="获取围手术期相关论文信息详情",
)
async def query_detail_literature_paper(
    request: Request, paper_id: int, query_db: AsyncSession = Depends(get_db)
):
    paper_detail_result = await PaperService.paper_detail_services(query_db, paper_id)
    logger.info(f"获取paper_id为{paper_id}的信息成功")

    return ResponseUtil.success(data=paper_detail_result)


@paperController.post(
    "/export",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:export"))],
    summary="导出围手术期相关论文信息",
    description="导出围手术期相关论文信息",
)
@Log(title="围手术期相关论文信息", business_type=BusinessType.EXPORT)
async def export_literature_paper_list(
    request: Request,
    paper_page_query: PaperPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    paper_query_result = await PaperService.get_paper_list_services(
        query_db, paper_page_query, is_page=False
    )
    paper_export_result = await PaperService.export_paper_list_services(
        paper_query_result
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(data=bytes2file_response(paper_export_result))


@paperController.get(
    "/authAuthor/{paper_id}",
    response_model=PaperAuthorResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:query"))],
    summary="获取论文已分配的作者列表",
    description="获取论文已分配的作者列表",
)
async def get_literature_allocated_author_list(
    request: Request, paper_id: int, query_db: AsyncSession = Depends(get_db)
):
    """获取论文已分配的作者列表"""
    paper_author_result = await PaperService.get_paper_author_allocated_list_services(
        query_db, paper_id
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=paper_author_result)


@paperController.put(
    "/authAuthor",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:edit"))],
    summary="更新论文作者关联关系",
    description="更新论文作者关联关系",
)
@Log(title="围手术期相关论文信息", business_type=BusinessType.GRANT)
async def update_literature_paper_author(
    request: Request,
    paper_id: int = Query(alias="paperId"),
    author_ids: str = Query(alias="authorIds"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新论文作者关联关系"""
    add_paper_author_result = await PaperService.add_paper_author_services(
        query_db,
        CrudPaperAuthorModel(
            paperId=paper_id, authorIds=author_ids, updateBy=current_user.user.user_name
        ),
    )
    logger.info(add_paper_author_result.message)

    return ResponseUtil.success(msg=add_paper_author_result.message)


@paperController.get(
    "/authKeyword/{paper_id}",
    response_model=PaperKeywordResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:query"))],
    summary="获取论文已分配的关键词列表",
    description="获取论文已分配的关键词列表",
)
async def get_literature_allocated_keyword_list(
    request: Request, paper_id: int, query_db: AsyncSession = Depends(get_db)
):
    """获取论文已分配的关键词列表"""
    paper_keyword_result = await PaperService.get_paper_keyword_allocated_list_services(
        query_db, paper_id
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=paper_keyword_result)


@paperController.put(
    "/authKeyword",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:paper:edit"))],
    summary="更新论文关键词关联关系",
    description="更新论文关键词关联关系",
)
@Log(title="围手术期相关论文信息", business_type=BusinessType.GRANT)
async def update_literature_paper_keyword(
    request: Request,
    paper_id: int = Query(alias="paperId"),
    keyword_ids: str = Query(alias="keywordIds"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新论文关键词关联关系"""
    add_paper_keyword_result = await PaperService.add_paper_keyword_services(
        query_db,
        CrudPaperKeywordModel(
            paperId=paper_id,
            keywordIds=keyword_ids,
            updateBy=current_user.user.user_name,
        ),
    )
    logger.info(add_paper_keyword_result.message)

    return ResponseUtil.success(msg=add_paper_keyword_result.message)
