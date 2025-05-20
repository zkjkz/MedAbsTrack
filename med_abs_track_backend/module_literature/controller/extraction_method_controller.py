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
from module_literature.service.extraction_method_service import Extraction_methodService
from module_literature.entity.vo.extraction_method_vo import (
    DeleteExtraction_methodModel,
    Extraction_methodModel,
    Extraction_methodPageQueryModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


extraction_methodController = APIRouter(
    prefix="/literature/extraction_method",
    dependencies=[Depends(LoginService.get_current_user)],
)


@extraction_methodController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_method:list"))],
)
async def get_literature_extraction_method_list(
    request: Request,
    extraction_method_page_query: Extraction_methodPageQueryModel = Depends(
        Extraction_methodPageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    extraction_method_page_query_result = (
        await Extraction_methodService.get_extraction_method_list_services(
            query_db, extraction_method_page_query, is_page=True
        )
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=extraction_method_page_query_result)


@extraction_methodController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_method:add"))],
)
@ValidateFields(validate_model="add_extraction_method")
@Log(title="抽取方法配置", business_type=BusinessType.INSERT)
async def add_literature_extraction_method(
    request: Request,
    add_extraction_method: Extraction_methodModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_extraction_method.create_by = current_user.user.user_name
    add_extraction_method.create_time = datetime.now()
    add_extraction_method.update_by = current_user.user.user_name
    add_extraction_method.update_time = datetime.now()
    add_extraction_method_result = (
        await Extraction_methodService.add_extraction_method_services(
            query_db, add_extraction_method
        )
    )
    logger.info(add_extraction_method_result.message)

    return ResponseUtil.success(msg=add_extraction_method_result.message)


@extraction_methodController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_method:edit"))],
)
@ValidateFields(validate_model="edit_extraction_method")
@Log(title="抽取方法配置", business_type=BusinessType.UPDATE)
async def edit_literature_extraction_method(
    request: Request,
    edit_extraction_method: Extraction_methodModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_extraction_method.update_by = current_user.user.user_name
    edit_extraction_method.update_time = datetime.now()
    edit_extraction_method_result = (
        await Extraction_methodService.edit_extraction_method_services(
            query_db, edit_extraction_method
        )
    )
    logger.info(edit_extraction_method_result.message)

    return ResponseUtil.success(msg=edit_extraction_method_result.message)


@extraction_methodController.delete(
    "/{method_ids}",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_method:remove"))
    ],
)
@Log(title="抽取方法配置", business_type=BusinessType.DELETE)
async def delete_literature_extraction_method(
    request: Request, method_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_extraction_method = DeleteExtraction_methodModel(methodIds=method_ids)
    delete_extraction_method_result = (
        await Extraction_methodService.delete_extraction_method_services(
            query_db, delete_extraction_method
        )
    )
    logger.info(delete_extraction_method_result.message)

    return ResponseUtil.success(msg=delete_extraction_method_result.message)


@extraction_methodController.get(
    "/{method_id}",
    response_model=Extraction_methodModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_method:query"))
    ],
)
async def query_detail_literature_extraction_method(
    request: Request, method_id: int, query_db: AsyncSession = Depends(get_db)
):
    extraction_method_detail_result = (
        await Extraction_methodService.extraction_method_detail_services(
            query_db, method_id
        )
    )
    logger.info(f"获取method_id为{method_id}的信息成功")

    return ResponseUtil.success(data=extraction_method_detail_result)


@extraction_methodController.post(
    "/export",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_method:export"))
    ],
)
@Log(title="抽取方法配置", business_type=BusinessType.EXPORT)
async def export_literature_extraction_method_list(
    request: Request,
    extraction_method_page_query: Extraction_methodPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    extraction_method_query_result = (
        await Extraction_methodService.get_extraction_method_list_services(
            query_db, extraction_method_page_query, is_page=False
        )
    )
    extraction_method_export_result = (
        await Extraction_methodService.export_extraction_method_list_services(
            extraction_method_query_result
        )
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(
        data=bytes2file_response(extraction_method_export_result)
    )


@extraction_methodController.put(
    "/changeStatus",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_method:edit"))],
    summary="修改抽取方法配置激活状态",
    description="修改抽取方法配置激活状态",
)
@Log(title="抽取方法配置", business_type=BusinessType.UPDATE)
async def change_status_literature_extraction_method(
    request: Request,
    edit_extraction_method: Extraction_methodModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建更新模型
    edit_extraction_method.update_by = current_user.user.user_name
    edit_extraction_method.update_time = datetime.now()

    # 调用服务更新状态
    change_status_result = (
        await Extraction_methodService.edit_extraction_method_services(
            query_db, edit_extraction_method
        )
    )
    logger.info(change_status_result.message)

    return ResponseUtil.success(msg=change_status_result.message)
