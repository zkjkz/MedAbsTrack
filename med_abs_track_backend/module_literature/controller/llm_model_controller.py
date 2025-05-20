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
from module_literature.service.llm_model_service import Llm_modelService
from module_literature.entity.vo.llm_model_vo import (
    DeleteLlm_modelModel,
    Llm_modelModel,
    Llm_modelPageQueryModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


llm_modelController = APIRouter(
    prefix="/literature/llm_model",
    dependencies=[Depends(LoginService.get_current_user)],
)


@llm_modelController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:list"))],
    summary="获取大语言模型基座列表",
    description="获取大语言模型基座列表",
)
async def get_literature_llm_model_list(
    request: Request,
    llm_model_page_query: Llm_modelPageQueryModel = Depends(
        Llm_modelPageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    llm_model_page_query_result = await Llm_modelService.get_llm_model_list_services(
        query_db, llm_model_page_query, is_page=True
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=llm_model_page_query_result)


@llm_modelController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:add"))],
    summary="新增大语言模型基座",
    description="新增大语言模型基座",
)
@ValidateFields(validate_model="add_llm_model")
@Log(title="大语言模型基座", business_type=BusinessType.INSERT)
async def add_literature_llm_model(
    request: Request,
    add_llm_model: Llm_modelModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_llm_model.create_by = current_user.user.user_name
    add_llm_model.create_time = datetime.now()
    add_llm_model.update_by = current_user.user.user_name
    add_llm_model.update_time = datetime.now()
    add_llm_model_result = await Llm_modelService.add_llm_model_services(
        query_db, add_llm_model
    )
    logger.info(add_llm_model_result.message)

    return ResponseUtil.success(msg=add_llm_model_result.message)


@llm_modelController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:edit"))],
    summary="编辑大语言模型基座",
    description="编辑大语言模型基座",
)
@ValidateFields(validate_model="edit_llm_model")
@Log(title="大语言模型基座", business_type=BusinessType.UPDATE)
async def edit_literature_llm_model(
    request: Request,
    edit_llm_model: Llm_modelModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_llm_model.update_by = current_user.user.user_name
    edit_llm_model.update_time = datetime.now()
    edit_llm_model_result = await Llm_modelService.edit_llm_model_services(
        query_db, edit_llm_model
    )
    logger.info(edit_llm_model_result.message)

    return ResponseUtil.success(msg=edit_llm_model_result.message)


@llm_modelController.delete(
    "/{model_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:remove"))],
    summary="删除大语言模型基座",
    description="删除大语言模型基座",
)
@Log(title="大语言模型基座", business_type=BusinessType.DELETE)
async def delete_literature_llm_model(
    request: Request, model_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_llm_model = DeleteLlm_modelModel(modelIds=model_ids)
    delete_llm_model_result = await Llm_modelService.delete_llm_model_services(
        query_db, delete_llm_model
    )
    logger.info(delete_llm_model_result.message)

    return ResponseUtil.success(msg=delete_llm_model_result.message)


@llm_modelController.get(
    "/{model_id}",
    response_model=Llm_modelModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:query"))],
    summary="获取大语言模型基座详情",
    description="获取大语言模型基座详情",
)
async def query_detail_literature_llm_model(
    request: Request, model_id: int, query_db: AsyncSession = Depends(get_db)
):
    llm_model_detail_result = await Llm_modelService.llm_model_detail_services(
        query_db, model_id
    )
    logger.info(f"获取model_id为{model_id}的信息成功")

    return ResponseUtil.success(data=llm_model_detail_result)


@llm_modelController.post(
    "/export",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:export"))],
    summary="导出大语言模型基座列表",
    description="导出大语言模型基座列表",
)
@Log(title="大语言模型基座", business_type=BusinessType.EXPORT)
async def export_literature_llm_model_list(
    request: Request,
    llm_model_page_query: Llm_modelPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    llm_model_query_result = await Llm_modelService.get_llm_model_list_services(
        query_db, llm_model_page_query, is_page=False
    )
    llm_model_export_result = await Llm_modelService.export_llm_model_list_services(
        llm_model_query_result
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(data=bytes2file_response(llm_model_export_result))


@llm_modelController.put(
    "/changeStatus",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:llm_model:edit"))],
    summary="修改大语言模型基座激活状态",
    description="修改大语言模型基座激活状态",
)
@Log(title="大语言模型基座", business_type=BusinessType.UPDATE)
async def change_status_literature_llm_model(
    request: Request,
    edit_llm_model: Llm_modelModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建更新模型
    edit_llm_model.update_by = current_user.user.user_name
    edit_llm_model.update_time = datetime.now()

    # 调用服务更新状态
    change_status_result = await Llm_modelService.edit_llm_model_services(
        query_db, edit_llm_model
    )
    logger.info(change_status_result.message)

    return ResponseUtil.success(msg=change_status_result.message)
