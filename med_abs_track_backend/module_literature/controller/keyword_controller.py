from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_literature.service.keyword_service import KeywordService
from module_literature.entity.vo.paper_vo import KeywordModel
from utils.log_util import logger
from utils.response_util import ResponseUtil


keywordController = APIRouter(
    prefix="/literature/keyword", dependencies=[Depends(LoginService.get_current_user)]
)


@keywordController.get(
    "/list",
    response_model=List[KeywordModel],
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:list"))],
    summary="获取关键词列表",
    description="获取关键词列表",
)
async def get_literature_keyword_list(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    keyword_list = await KeywordService.get_keyword_list_services(query_db)
    logger.info("获取关键词列表成功")

    return ResponseUtil.success(data=keyword_list)


@keywordController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:add"))],
    summary="添加关键词信息",
    description="添加关键词信息",
)
@ValidateFields(validate_model="add_keyword")
@Log(title="关键词信息", business_type=BusinessType.INSERT)
async def add_literature_keyword(
    request: Request,
    add_keyword: KeywordModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_keyword.create_by = current_user.user.user_name
    add_keyword.create_time = datetime.now()
    add_keyword.update_by = current_user.user.user_name
    add_keyword.update_time = datetime.now()
    try:
        add_keyword_result = await KeywordService.add_keyword_services(
            query_db, add_keyword
        )
        logger.info(add_keyword_result.message)
        return ResponseUtil.success(data=add_keyword_result.result)
    except Exception as e:
        logger.error(f"添加关键词失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@keywordController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:edit"))],
    summary="更新关键词信息",
    description="更新关键词信息",
)
@ValidateFields(validate_model="edit_keyword")
@Log(title="关键词信息", business_type=BusinessType.UPDATE)
async def edit_literature_keyword(
    request: Request,
    edit_keyword: KeywordModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_keyword.update_by = current_user.user.user_name
    edit_keyword.update_time = datetime.now()
    try:
        edit_keyword_result = await KeywordService.edit_keyword_services(
            query_db, edit_keyword
        )
        logger.info(edit_keyword_result.message)
        return ResponseUtil.success(data=edit_keyword_result.result)
    except Exception as e:
        logger.error(f"修改关键词失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@keywordController.delete(
    "/{keyword_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:remove"))],
    summary="删除关键词信息",
    description="删除关键词信息",
)
@Log(title="关键词信息", business_type=BusinessType.DELETE)
async def delete_literature_keyword(
    request: Request, keyword_ids: str, query_db: AsyncSession = Depends(get_db)
):
    try:
        keyword_id_list = [int(keyword_id) for keyword_id in keyword_ids.split(",")]
        delete_keyword_result = await KeywordService.delete_keyword_services(
            query_db, keyword_id_list
        )
        logger.info(delete_keyword_result.message)
        return ResponseUtil.success(msg=delete_keyword_result.message)
    except Exception as e:
        logger.error(f"删除关键词失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@keywordController.get(
    "/{keyword_id}",
    response_model=KeywordModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:query"))],
    summary="获取关键词详情",
    description="获取关键词详情",
)
async def query_detail_literature_keyword(
    request: Request, keyword_id: int, query_db: AsyncSession = Depends(get_db)
):
    keyword_detail = await KeywordService.keyword_detail_services(query_db, keyword_id)
    if not keyword_detail.keyword_id:
        return ResponseUtil.failure(msg=f"关键词ID {keyword_id} 不存在")

    logger.info(f"获取关键词ID为{keyword_id}的信息成功")
    return ResponseUtil.success(data=keyword_detail)


@keywordController.post(
    "/batch",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:keyword:add"))],
    summary="批量添加关键词信息",
    description="批量添加关键词信息",
)
@ValidateFields(validate_model="add_keywords")
@Log(title="关键词信息", business_type=BusinessType.INSERT)
async def add_batch_literature_keyword(
    request: Request,
    add_keywords: List[KeywordModel],
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    current_time = datetime.now()
    keyword_results = []
    success_count = 0
    failed_count = 0

    for add_keyword in add_keywords:
        add_keyword.create_by = current_user.user.user_name
        add_keyword.create_time = current_time
        add_keyword.update_by = current_user.user.user_name
        add_keyword.update_time = current_time

        try:
            add_keyword_result = await KeywordService.add_keyword_services(
                query_db, add_keyword
            )
            keyword_results.append(add_keyword_result.result)
            success_count += 1
        except Exception as e:
            keyword_results.append({"error": str(e)})
            failed_count += 1

    result_msg = f"批量添加关键词成功: {success_count}条, 失败: {failed_count}条"
    logger.info(result_msg)
    return ResponseUtil.success(msg=result_msg, data=keyword_results)
