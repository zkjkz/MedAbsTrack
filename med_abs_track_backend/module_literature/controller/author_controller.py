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
from module_literature.service.author_service import AuthorService
from module_literature.entity.vo.paper_vo import AuthorModel
from utils.log_util import logger
from utils.response_util import ResponseUtil


authorController = APIRouter(
    prefix="/literature/author", dependencies=[Depends(LoginService.get_current_user)]
)


@authorController.get(
    "/list",
    response_model=List[AuthorModel],
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:list"))],
    summary="获取作者列表",
    description="获取作者列表",
)
async def get_literature_author_list(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    author_list = await AuthorService.get_author_list_services(query_db)
    logger.info("获取作者列表成功")

    return ResponseUtil.success(data=author_list)


@authorController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:add"))],
    summary="添加作者信息",
    description="添加作者信息",
)
@ValidateFields(validate_model="add_author")
@Log(title="作者信息", business_type=BusinessType.INSERT)
async def add_literature_author(
    request: Request,
    add_author: AuthorModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_author.create_by = current_user.user.user_name
    add_author.create_time = datetime.now()
    add_author.update_by = current_user.user.user_name
    add_author.update_time = datetime.now()
    try:
        add_author_result = await AuthorService.add_author_services(
            query_db, add_author
        )
        logger.info(add_author_result.message)
        return ResponseUtil.success(data=add_author_result.result)
    except Exception as e:
        logger.error(f"添加作者失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@authorController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:edit"))],
    summary="更新作者信息",
    description="更新作者信息",
)
@ValidateFields(validate_model="edit_author")
@Log(title="作者信息", business_type=BusinessType.UPDATE)
async def edit_literature_author(
    request: Request,
    edit_author: AuthorModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_author.update_by = current_user.user.user_name
    edit_author.update_time = datetime.now()
    try:
        edit_author_result = await AuthorService.edit_author_services(
            query_db, edit_author
        )
        logger.info(edit_author_result.message)
        return ResponseUtil.success(data=edit_author_result.result)
    except Exception as e:
        logger.error(f"修改作者失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@authorController.delete(
    "/{author_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:remove"))],
    summary="删除作者信息",
    description="删除作者信息",
)
@Log(title="作者信息", business_type=BusinessType.DELETE)
async def delete_literature_author(
    request: Request, author_ids: str, query_db: AsyncSession = Depends(get_db)
):
    try:
        author_id_list = [int(author_id) for author_id in author_ids.split(",")]
        delete_author_result = await AuthorService.delete_author_services(
            query_db, author_id_list
        )
        logger.info(delete_author_result.message)
        return ResponseUtil.success(msg=delete_author_result.message)
    except Exception as e:
        logger.error(f"删除作者失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@authorController.get(
    "/{author_id}",
    response_model=AuthorModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:query"))],
    summary="获取作者详情",
    description="获取作者详情",
)
async def query_detail_literature_author(
    request: Request, author_id: int, query_db: AsyncSession = Depends(get_db)
):
    author_detail = await AuthorService.author_detail_services(query_db, author_id)
    if not author_detail.author_id:
        return ResponseUtil.failure(msg=f"作者ID {author_id} 不存在")

    logger.info(f"获取作者ID为{author_id}的信息成功")
    return ResponseUtil.success(data=author_detail)


@authorController.post(
    "/batch",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:author:add"))],
    summary="批量添加作者信息",
    description="批量添加作者信息",
)
@ValidateFields(validate_model="add_authors")
@Log(title="作者信息", business_type=BusinessType.INSERT)
async def add_batch_literature_author(
    request: Request,
    add_authors: List[AuthorModel],
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    current_time = datetime.now()
    author_results = []
    success_count = 0
    failed_count = 0

    for add_author in add_authors:
        add_author.create_by = current_user.user.user_name
        add_author.create_time = current_time
        add_author.update_by = current_user.user.user_name
        add_author.update_time = current_time

        try:
            add_author_result = await AuthorService.add_author_services(
                query_db, add_author
            )
            author_results.append(add_author_result.result)
            success_count += 1
        except Exception as e:
            author_results.append({"error": str(e)})
            failed_count += 1

    result_msg = f"批量添加作者成功: {success_count}条, 失败: {failed_count}条"
    logger.info(result_msg)
    return ResponseUtil.success(msg=result_msg, data=author_results)
