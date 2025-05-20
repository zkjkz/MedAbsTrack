from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_literature.service.prompt_template_service import Prompt_templateService
from module_literature.entity.vo.prompt_template_vo import (
    DeletePrompt_templateModel,
    Prompt_templateModel,
    Prompt_templatePageQueryModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


prompt_templateController = APIRouter(
    prefix="/literature/prompt_template",
    dependencies=[Depends(LoginService.get_current_user)],
)


@prompt_templateController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:list"))],
    summary="获取Prompt模板列表",
    description="获取Prompt模板列表",
)
async def get_literature_prompt_template_list(
    request: Request,
    prompt_template_page_query: Prompt_templatePageQueryModel = Depends(
        Prompt_templatePageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    prompt_template_page_query_result = (
        await Prompt_templateService.get_prompt_template_list_services(
            query_db, prompt_template_page_query, is_page=True
        )
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=prompt_template_page_query_result)


@prompt_templateController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:add"))],
    summary="新增Prompt模板",
    description="新增Prompt模板",
)
@ValidateFields(validate_model="add_prompt_template")
@Log(title="Prompt模板", business_type=BusinessType.INSERT)
async def add_literature_prompt_template(
    request: Request,
    add_prompt_template: Prompt_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_prompt_template.create_by = current_user.user.user_name
    add_prompt_template.create_time = datetime.now()
    add_prompt_template.update_by = current_user.user.user_name
    add_prompt_template.update_time = datetime.now()
    add_prompt_template_result = (
        await Prompt_templateService.add_prompt_template_services(
            query_db, add_prompt_template
        )
    )
    logger.info(add_prompt_template_result.message)

    return ResponseUtil.success(msg=add_prompt_template_result.message)


@prompt_templateController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:edit"))],
    summary="编辑Prompt模板",
    description="编辑Prompt模板",
)
@ValidateFields(validate_model="edit_prompt_template")
@Log(title="Prompt模板", business_type=BusinessType.UPDATE)
async def edit_literature_prompt_template(
    request: Request,
    edit_prompt_template: Prompt_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_prompt_template.update_by = current_user.user.user_name
    edit_prompt_template.update_time = datetime.now()
    edit_prompt_template_result = (
        await Prompt_templateService.edit_prompt_template_services(
            query_db, edit_prompt_template
        )
    )
    logger.info(edit_prompt_template_result.message)

    return ResponseUtil.success(msg=edit_prompt_template_result.message)


@prompt_templateController.delete(
    "/{prompt_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:remove"))],
    summary="删除Prompt模板",
    description="删除Prompt模板",
)
@Log(title="Prompt模板", business_type=BusinessType.DELETE)
async def delete_literature_prompt_template(
    request: Request, prompt_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_prompt_template = DeletePrompt_templateModel(promptIds=prompt_ids)
    delete_prompt_template_result = (
        await Prompt_templateService.delete_prompt_template_services(
            query_db, delete_prompt_template
        )
    )
    logger.info(delete_prompt_template_result.message)

    return ResponseUtil.success(msg=delete_prompt_template_result.message)


@prompt_templateController.get(
    "/{prompt_id}",
    response_model=Prompt_templateModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:query"))],
    summary="获取Prompt模板详情",
    description="获取Prompt模板详情",
)
async def query_detail_literature_prompt_template(
    request: Request, prompt_id: int, query_db: AsyncSession = Depends(get_db)
):
    prompt_template_detail_result = (
        await Prompt_templateService.prompt_template_detail_services(
            query_db, prompt_id
        )
    )
    logger.info(f"获取prompt_id为{prompt_id}的信息成功")

    return ResponseUtil.success(data=prompt_template_detail_result)


@prompt_templateController.post(
    "/export",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:export"))],
    summary="导出Prompt模板列表",
    description="导出Prompt模板列表",
)
@Log(title="Prompt模板", business_type=BusinessType.EXPORT)
async def export_literature_prompt_template_list(
    request: Request,
    prompt_template_page_query: Prompt_templatePageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    prompt_template_query_result = (
        await Prompt_templateService.get_prompt_template_list_services(
            query_db, prompt_template_page_query, is_page=False
        )
    )
    prompt_template_export_result = (
        await Prompt_templateService.export_prompt_template_list_services(
            prompt_template_query_result
        )
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(
        data=bytes2file_response(prompt_template_export_result)
    )


@prompt_templateController.put(
    "/changeStatus",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:prompt_template:edit"))],
    summary="修改Prompt模板激活状态",
    description="修改Prompt模板激活状态",
)
@Log(title="Prompt模板", business_type=BusinessType.UPDATE)
async def change_status_literature_prompt_template(
    request: Request,
    edit_prompt_template: Prompt_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建更新模型
    edit_prompt_template.update_by = current_user.user.user_name
    edit_prompt_template.update_time = datetime.now()

    # 调用服务更新状态
    change_status_result = await Prompt_templateService.edit_prompt_template_services(
        query_db, edit_prompt_template
    )
    logger.info(change_status_result.message)

    return ResponseUtil.success(msg=change_status_result.message)
