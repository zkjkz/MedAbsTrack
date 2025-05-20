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
from module_literature.service.extraction_template_service import (
    Extraction_templateService,
)
from module_literature.entity.vo.extraction_template_vo import (
    DeleteExtraction_templateModel,
    Extraction_templateModel,
    Extraction_templatePageQueryModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


extraction_templateController = APIRouter(
    prefix="/literature/extraction_template",
    dependencies=[Depends(LoginService.get_current_user)],
)


@extraction_templateController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:list"))
    ],
    summary="获取摘要抽取模板列表",
    description="获取摘要抽取模板列表",
)
async def get_literature_extraction_template_list(
    request: Request,
    extraction_template_page_query: Extraction_templatePageQueryModel = Depends(
        Extraction_templatePageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    extraction_template_page_query_result = (
        await Extraction_templateService.get_extraction_template_list_services(
            query_db, extraction_template_page_query, is_page=True
        )
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=extraction_template_page_query_result)


@extraction_templateController.post(
    "",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:add"))
    ],
    summary="新增摘要抽取模板",
    description="新增摘要抽取模板",
)
@ValidateFields(validate_model="add_extraction_template")
@Log(title="摘要抽取模板", business_type=BusinessType.INSERT)
async def add_literature_extraction_template(
    request: Request,
    add_extraction_template: Extraction_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_extraction_template.create_by = current_user.user.user_name
    add_extraction_template.create_time = datetime.now()
    add_extraction_template.update_by = current_user.user.user_name
    add_extraction_template.update_time = datetime.now()
    add_extraction_template_result = (
        await Extraction_templateService.add_extraction_template_services(
            query_db, add_extraction_template
        )
    )
    logger.info(add_extraction_template_result.message)

    return ResponseUtil.success(msg=add_extraction_template_result.message)


@extraction_templateController.put(
    "",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:edit"))
    ],
    summary="编辑摘要抽取模板",
    description="编辑摘要抽取模板",
)
@ValidateFields(validate_model="edit_extraction_template")
@Log(title="摘要抽取模板", business_type=BusinessType.UPDATE)
async def edit_literature_extraction_template(
    request: Request,
    edit_extraction_template: Extraction_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_extraction_template.update_by = current_user.user.user_name
    edit_extraction_template.update_time = datetime.now()
    edit_extraction_template_result = (
        await Extraction_templateService.edit_extraction_template_services(
            query_db, edit_extraction_template
        )
    )
    logger.info(edit_extraction_template_result.message)

    return ResponseUtil.success(msg=edit_extraction_template_result.message)


@extraction_templateController.delete(
    "/{template_ids}",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:remove"))
    ],
    summary="删除摘要抽取模板",
    description="删除摘要抽取模板",
)
@Log(title="摘要抽取模板", business_type=BusinessType.DELETE)
async def delete_literature_extraction_template(
    request: Request, template_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_extraction_template = DeleteExtraction_templateModel(
        templateIds=template_ids
    )
    delete_extraction_template_result = (
        await Extraction_templateService.delete_extraction_template_services(
            query_db, delete_extraction_template
        )
    )
    logger.info(delete_extraction_template_result.message)

    return ResponseUtil.success(msg=delete_extraction_template_result.message)


@extraction_templateController.get(
    "/{template_id}",
    response_model=Extraction_templateModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:query"))
    ],
    summary="获取摘要抽取模板详情",
    description="获取摘要抽取模板详情",
)
async def query_detail_literature_extraction_template(
    request: Request, template_id: int, query_db: AsyncSession = Depends(get_db)
):
    extraction_template_detail_result = (
        await Extraction_templateService.extraction_template_detail_services(
            query_db, template_id
        )
    )
    logger.info(f"获取template_id为{template_id}的信息成功")

    return ResponseUtil.success(data=extraction_template_detail_result)


@extraction_templateController.post(
    "/export",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:export"))
    ],
    summary="导出摘要抽取模板列表",
    description="导出摘要抽取模板列表",
)
@Log(title="摘要抽取模板", business_type=BusinessType.EXPORT)
async def export_literature_extraction_template_list(
    request: Request,
    extraction_template_page_query: Extraction_templatePageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    extraction_template_query_result = (
        await Extraction_templateService.get_extraction_template_list_services(
            query_db, extraction_template_page_query, is_page=False
        )
    )
    extraction_template_export_result = (
        await Extraction_templateService.export_extraction_template_list_services(
            extraction_template_query_result
        )
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(
        data=bytes2file_response(extraction_template_export_result)
    )


@extraction_templateController.put(
    "/changeStatus",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_template:edit"))
    ],
    summary="修改摘要抽取模板激活状态",
    description="修改摘要抽取模板激活状态",
)
@Log(title="摘要抽取模板", business_type=BusinessType.UPDATE)
async def change_status_literature_extraction_template(
    request: Request,
    edit_extraction_template: Extraction_templateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建更新模型
    edit_extraction_template.update_by = current_user.user.user_name
    edit_extraction_template.update_time = datetime.now()

    # 调用服务更新状态
    change_status_result = (
        await Extraction_templateService.edit_extraction_template_services(
            query_db, edit_extraction_template
        )
    )
    logger.info(change_status_result.message)

    return ResponseUtil.success(msg=change_status_result.message)
