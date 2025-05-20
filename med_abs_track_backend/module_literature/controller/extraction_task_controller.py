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
from module_literature.service.extraction_task_service import Extraction_taskService
from module_literature.entity.vo.extraction_task_vo import (
    DeleteExtractionTaskModel,
    ExtractionTaskModel,
    ExtractionTaskPageQueryModel,
    ExtractionRequestModel,
    ExtractionResponseModel,
    CrudTaskPaperModel,
)
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


extractionTaskController = APIRouter(
    prefix="/literature/extraction_task",
    dependencies=[Depends(LoginService.get_current_user)],
)


@extractionTaskController.get(
    "/list",
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:list"))],
    summary="获取抽取任务列表",
    description="获取抽取任务列表",
)
async def get_extraction_task_list(
    request: Request,
    task_page_query: ExtractionTaskPageQueryModel = Depends(
        ExtractionTaskPageQueryModel.as_query
    ),
    query_db: AsyncSession = Depends(get_db),
):
    """获取抽取任务列表"""
    task_page_query_result = (
        await Extraction_taskService.get_extraction_task_list_services(
            query_db, task_page_query, is_page=True
        )
    )
    logger.info("获取成功")

    return ResponseUtil.success(model_content=task_page_query_result)


@extractionTaskController.post(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:add"))],
    summary="添加抽取任务",
    description="添加抽取任务",
)
@ValidateFields(validate_model="add_extraction_task")
@Log(title="抽取任务", business_type=BusinessType.INSERT)
async def add_extraction_task(
    request: Request,
    add_task: ExtractionTaskModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """添加抽取任务"""
    add_task.create_by = current_user.user.user_name
    add_task.create_time = datetime.now()
    add_task.update_by = current_user.user.user_name
    add_task.update_time = datetime.now()
    add_task_result = await Extraction_taskService.add_extraction_task_services(
        query_db, add_task
    )
    logger.info(add_task_result.message)

    return ResponseUtil.success(msg=add_task_result.message, data=add_task_result.data)


@extractionTaskController.put(
    "",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:edit"))],
    summary="更新抽取任务",
    description="更新抽取任务",
)
@ValidateFields(validate_model="edit_extraction_task")
@Log(title="抽取任务", business_type=BusinessType.UPDATE)
async def edit_extraction_task(
    request: Request,
    edit_task: ExtractionTaskModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新抽取任务"""
    edit_task.update_by = current_user.user.user_name
    edit_task.update_time = datetime.now()
    edit_task_result = await Extraction_taskService.edit_extraction_task_services(
        query_db, edit_task
    )
    logger.info(edit_task_result.message)

    return ResponseUtil.success(msg=edit_task_result.message)


@extractionTaskController.delete(
    "/{task_ids}",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:remove"))],
    summary="删除抽取任务",
    description="删除抽取任务",
)
@Log(title="抽取任务", business_type=BusinessType.DELETE)
async def delete_extraction_task(
    request: Request, task_ids: str, query_db: AsyncSession = Depends(get_db)
):
    """删除抽取任务"""
    delete_task = DeleteExtractionTaskModel(taskIds=task_ids)
    delete_task_result = await Extraction_taskService.delete_extraction_task_services(
        query_db, delete_task
    )
    logger.info(delete_task_result.message)

    return ResponseUtil.success(msg=delete_task_result.message)


@extractionTaskController.get(
    "/{task_id}",
    response_model=ExtractionTaskModel,
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:query"))],
    summary="获取抽取任务详情",
    description="获取抽取任务详情",
)
async def query_detail_extraction_task(
    request: Request, task_id: int, query_db: AsyncSession = Depends(get_db)
):
    """获取抽取任务详情"""
    task_detail_result = await Extraction_taskService.extraction_task_detail_services(
        query_db, task_id
    )
    logger.info(f"获取task_id为{task_id}的信息成功")

    return ResponseUtil.success(data=task_detail_result)


@extractionTaskController.post(
    "/export",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:export"))],
    summary="导出抽取任务",
    description="导出抽取任务",
)
@Log(title="抽取任务", business_type=BusinessType.EXPORT)
async def export_extraction_task_list(
    request: Request,
    task_page_query: ExtractionTaskPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    """导出抽取任务"""
    task_query_result = await Extraction_taskService.get_extraction_task_list_services(
        query_db, task_page_query, is_page=False
    )
    task_export_result = (
        await Extraction_taskService.export_extraction_task_list_services(
            task_query_result
        )
    )
    logger.info("导出成功")

    return ResponseUtil.streaming(data=bytes2file_response(task_export_result))


@extractionTaskController.put(
    "/authPaper",
    dependencies=[Depends(CheckUserInterfaceAuth("literature:extraction_task:edit"))],
    summary="更新任务论文关联关系",
    description="更新任务论文关联关系",
)
@Log(title="抽取任务", business_type=BusinessType.GRANT)
async def update_task_paper(
    request: Request,
    task_id: int = Query(alias="taskId"),
    paper_ids: str = Query(alias="paperIds"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新任务论文关联关系"""
    add_task_paper_result = await Extraction_taskService.add_task_paper_services(
        query_db,
        CrudTaskPaperModel(
            taskId=task_id, paperIds=paper_ids, updateBy=current_user.user.user_name
        ),
    )
    logger.info(add_task_paper_result.message)

    return ResponseUtil.success(msg=add_task_paper_result.message)


@extractionTaskController.post(
    "/extract",
    response_model=ExtractionResponseModel,
    dependencies=[
        Depends(CheckUserInterfaceAuth("literature:extraction_task:extract"))
    ],
    summary="执行抽取任务",
    description="执行抽取任务，支持传入文章对象或已有文章ID",
)
@Log(title="抽取任务", business_type=BusinessType.OTHER)
async def execute_extraction(
    request: Request,
    extraction_request: ExtractionRequestModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """执行抽取任务"""
    if extraction_request.paper and not extraction_request.paper.create_by:
        extraction_request.paper.create_by = current_user.user.user_name
        extraction_request.paper.update_by = current_user.user.user_name

    # 添加当前用户信息到请求中，供服务层使用
    extraction_request.create_by = current_user.user.user_name
    extraction_request.update_by = current_user.user.user_name

    # 执行抽取
    extraction_result = await Extraction_taskService.execute_extraction_task_services(
        query_db, extraction_request
    )

    if extraction_result.status == "2":  # 成功
        logger.info(f"抽取任务 {extraction_result.task_id} 执行成功")
        return ResponseUtil.success(data=extraction_result)
    else:  # 失败
        logger.error(
            f"抽取任务 {extraction_result.task_id} 执行失败: {extraction_result.error_message}"
        )
        return ResponseUtil.failure(msg=extraction_result.error_message)
