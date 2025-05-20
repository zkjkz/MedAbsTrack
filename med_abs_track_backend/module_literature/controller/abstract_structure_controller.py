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
from module_literature.service.abstract_structure_service import (
    AbstractStructureService,
)
from module_literature.entity.vo.abstract_structure_vo import (
    DeleteAbstractStructureModel,
    AbstractStructureModel,
    AbstractStructurePageQueryModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


abstractStructureController = APIRouter(
    prefix="/literature/abstract_structure",
    dependencies=[Depends(LoginService.get_current_user)],
)


@abstractStructureController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:list"))
    ],
    summary="获取摘要结构列表",
    description="获取摘要结构列表",
)
async def get_literature_abstract_structure_list(
    request: Request,
    abstract_structure_page_query: AbstractStructurePageQueryModel = Depends(
        AbstractStructurePageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    abstract_structure_page_query_result = (
        await AbstractStructureService.get_abstract_structure_list_services(
            query_db, abstract_structure_page_query, is_page=True
        )
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=abstract_structure_page_query_result)


@abstractStructureController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:abstract_structure:add"))],
    summary="新增摘要结构",
    description="新增摘要结构",
)
@ValidateFields(validate_model="add_abstract_structure")
@Log(title="摘要结构", business_type=BusinessType.INSERT)
async def add_literature_abstract_structure(
    request: Request,
    add_abstract_structure: AbstractStructureModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_abstract_structure.create_by = current_user.user.user_name
    add_abstract_structure.create_time = datetime.now()
    add_abstract_structure.update_by = current_user.user.user_name
    add_abstract_structure.update_time = datetime.now()
    add_abstract_structure_result = (
        await AbstractStructureService.add_abstract_structure_services(
            query_db, add_abstract_structure
        )
    )
    logger.info(add_abstract_structure_result.message)

    return ResponseUtil.success(msg=add_abstract_structure_result.message)


@abstractStructureController.put(
    "",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:edit"))
    ],
    summary="编辑摘要结构",
    description="编辑摘要结构",
)
@ValidateFields(validate_model="edit_abstract_structure")
@Log(title="摘要结构", business_type=BusinessType.UPDATE)
async def edit_literature_abstract_structure(
    request: Request,
    edit_abstract_structure: AbstractStructureModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_abstract_structure.update_by = current_user.user.user_name
    edit_abstract_structure.update_time = datetime.now()
    edit_abstract_structure_result = (
        await AbstractStructureService.edit_abstract_structure_services(
            query_db, edit_abstract_structure
        )
    )
    logger.info(edit_abstract_structure_result.message)

    return ResponseUtil.success(msg=edit_abstract_structure_result.message)


@abstractStructureController.delete(
    "/{abstract_ids}",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:remove"))
    ],
    summary="删除摘要结构",
    description="删除摘要结构",
)
@Log(title="摘要结构", business_type=BusinessType.DELETE)
async def delete_literature_abstract_structure(
    request: Request, abstract_ids: str, query_db: AsyncSession = Depends(get_db)
):
    delete_abstract_structure = DeleteAbstractStructureModel(abstractIds=abstract_ids)
    delete_abstract_structure_result = (
        await AbstractStructureService.delete_abstract_structure_services(
            query_db, delete_abstract_structure
        )
    )
    logger.info(delete_abstract_structure_result.message)

    return ResponseUtil.success(msg=delete_abstract_structure_result.message)


@abstractStructureController.get(
    "/{abstract_id}",
    response_model=AbstractStructureModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:query"))
    ],
    summary="获取摘要结构详情",
    description="获取摘要结构详情",
)
async def query_detail_literature_abstract_structure(
    request: Request, abstract_id: int, query_db: AsyncSession = Depends(get_db)
):
    abstract_structure_detail_result = (
        await AbstractStructureService.abstract_structure_detail_services(
            query_db, abstract_id
        )
    )
    logger.info(f"获取abstract_id为{abstract_id}的信息成功")

    return ResponseUtil.success(data=abstract_structure_detail_result)


@abstractStructureController.post(
    "/export",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:export"))
    ],
    summary="导出摘要结构列表",
    description="导出摘要结构列表",
)
@Log(title="摘要结构", business_type=BusinessType.EXPORT)
async def export_literature_abstract_structure_list(
    request: Request,
    abstract_structure_page_query: AbstractStructurePageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    abstract_structure_query_result = (
        await AbstractStructureService.get_abstract_structure_list_services(
            query_db, abstract_structure_page_query, is_page=False
        )
    )
    abstract_structure_export_result = (
        await AbstractStructureService.export_abstract_structure_list_services(
            abstract_structure_query_result
        )
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(
        data=bytes2file_response(abstract_structure_export_result)
    )


@abstractStructureController.put(
    "/changeStatus",
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:edit"))
    ],
    summary="修改摘要结构状态",
    description="修改摘要结构状态",
)
@Log(title="摘要结构", business_type=BusinessType.UPDATE)
async def change_status_literature_abstract_structure(
    request: Request,
    edit_abstract_structure: AbstractStructureModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 构建更新模型
    edit_abstract_structure.update_by = current_user.user.user_name
    edit_abstract_structure.update_time = datetime.now()

    # 调用服务更新状态
    change_status_result = (
        await AbstractStructureService.edit_abstract_structure_services(
            query_db, edit_abstract_structure
        )
    )
    logger.info(change_status_result.message)

    return ResponseUtil.success(msg=change_status_result.message)


@abstractStructureController.get(
    "/by-paper/{paper_id}",
    response_model=AbstractStructureModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:abstract_structure:query"))
    ],
    summary="根据文章ID获取摘要抽取数据",
    description="根据文章ID获取摘要抽取数据",
)
async def get_abstract_structure_by_paper_id(
    request: Request, paper_id: int, query_db: AsyncSession = Depends(get_db)
):
    abstract_structure_result = (
        await AbstractStructureService.get_abstract_structure_by_paper_id_services(
            query_db, paper_id
        )
    )
    logger.info(f"获取paper_id为{paper_id}的摘要结构信息成功")

    return ResponseUtil.success(data=abstract_structure_result)
