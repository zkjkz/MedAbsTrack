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
from module_literature.service.journal_service import JournalService
from module_literature.entity.vo.paper_vo import JournalModel
from utils.log_util import logger
from utils.response_util import ResponseUtil


journalController = APIRouter(
    prefix="/literature/journal", dependencies=[Depends(LoginService.get_current_user)]
)


@journalController.get(
    "/list",
    response_model=List[JournalModel],
    dependencies=[Depends(CheckUserInterfaceAuth("literature:journal:list"))],
    summary="获取期刊列表",
    description="获取期刊列表",
)
async def get_literature_journal_list(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    journal_list = await JournalService.get_journal_list_services(query_db)
    logger.info("获取期刊列表成功")

    return ResponseUtil.success(data=journal_list)


@journalController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:journal:add"))],
    summary="添加期刊信息",
    description="添加期刊信息",
)
@ValidateFields(validate_model="add_journal")
@Log(title="期刊信息", business_type=BusinessType.INSERT)
async def add_literature_journal(
    request: Request,
    add_journal: JournalModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_journal.create_by = current_user.user.user_name
    add_journal.create_time = datetime.now()
    add_journal.update_by = current_user.user.user_name
    add_journal.update_time = datetime.now()
    try:
        add_journal_result = await JournalService.add_journal_services(
            query_db, add_journal
        )
        logger.info(add_journal_result.message)
        return ResponseUtil.success(data=add_journal_result.result)
    except Exception as e:
        logger.error(f"添加期刊失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@journalController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:journal:edit"))],
    summary="更新期刊信息",
    description="更新期刊信息",
)
@ValidateFields(validate_model="edit_journal")
@Log(title="期刊信息", business_type=BusinessType.UPDATE)
async def edit_literature_journal(
    request: Request,
    edit_journal: JournalModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_journal.update_by = current_user.user.user_name
    edit_journal.update_time = datetime.now()
    try:
        edit_journal_result = await JournalService.edit_journal_services(
            query_db, edit_journal
        )
        logger.info(edit_journal_result.message)
        return ResponseUtil.success(data=edit_journal_result.result)
    except Exception as e:
        logger.error(f"修改期刊失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@journalController.delete(
    "/{journal_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:journal:remove"))],
    summary="删除期刊信息",
    description="删除期刊信息",
)
@Log(title="期刊信息", business_type=BusinessType.DELETE)
async def delete_literature_journal(
    request: Request, journal_ids: str, query_db: AsyncSession = Depends(get_db)
):
    try:
        journal_id_list = [int(journal_id) for journal_id in journal_ids.split(",")]
        delete_journal_result = await JournalService.delete_journal_services(
            query_db, journal_id_list
        )
        logger.info(delete_journal_result.message)
        return ResponseUtil.success(msg=delete_journal_result.message)
    except Exception as e:
        logger.error(f"删除期刊失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))


@journalController.get(
    "/{journal_id}",
    response_model=JournalModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:journal:query"))],
    summary="获取期刊详情",
    description="获取期刊详情",
)
async def query_detail_literature_journal(
    request: Request, journal_id: int, query_db: AsyncSession = Depends(get_db)
):
    journal_detail = await JournalService.journal_detail_services(query_db, journal_id)
    if not journal_detail.journal_id:
        return ResponseUtil.failure(msg=f"期刊ID {journal_id} 不存在")

    logger.info(f"获取期刊ID为{journal_id}的信息成功")
    return ResponseUtil.success(data=journal_detail)
