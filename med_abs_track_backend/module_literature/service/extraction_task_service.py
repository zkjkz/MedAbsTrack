from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.extraction_task_dao import Extraction_taskDao
from module_literature.dao.abstract_structure_dao import AbstractStructureDao
from module_literature.entity.do.extraction_method_do import ExtractionMethodType
from module_literature.entity.vo.extraction_task_vo import (
    ExtractionTaskModel,
    ExtractionTaskPageQueryModel,
    DeleteExtractionTaskModel,
    ExtractionRequestModel,
    ExtractionResponseModel,
    CrudTaskPaperModel,
)
from module_literature.entity.vo.paper_vo import AbstractStructureModel
from module_literature.service.extraction_method_service import Extraction_methodService
from module_literature.service.paper_service import PaperService
from module_literature.service.extractor.extractor_strategy import ExtractorFactory
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class Extraction_taskService:
    """
    抽取任务模块服务层
    """

    @classmethod
    async def get_extraction_task_list_services(
        cls,
        query_db: AsyncSession,
        query_object: ExtractionTaskPageQueryModel,
        is_page: bool = False,
    ):
        """
        获取抽取任务列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 抽取任务列表信息对象
        """
        extraction_task_list_result = await Extraction_taskDao.get_extraction_task_list(
            query_db, query_object, is_page
        )

        return extraction_task_list_result

    @classmethod
    async def add_extraction_task_services(
        cls, query_db: AsyncSession, task_object: ExtractionTaskModel
    ):
        """
        新增抽取任务信息service

        :param query_db: orm对象
        :param task_object: 新增抽取任务对象
        :return: 新增抽取任务校验结果
        """
        try:
            task_id = await Extraction_taskDao.add_extraction_task_dao(
                query_db, task_object
            )
            await query_db.commit()
            return CrudResponseModel(
                is_success=True, message="新增成功", result={"task_id": task_id}
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_extraction_task_services(
        cls, query_db: AsyncSession, task_object: ExtractionTaskModel
    ):
        """
        编辑抽取任务信息service

        :param query_db: orm对象
        :param task_object: 编辑抽取任务对象
        :return: 编辑抽取任务校验结果
        """
        edit_extraction_task = task_object.model_dump(
            exclude_unset=True, exclude={"create_by", "create_time"}
        )
        extraction_task_info = await cls.extraction_task_detail_services(
            query_db, task_object.task_id
        )
        if extraction_task_info.task_id:
            try:
                await Extraction_taskDao.edit_extraction_task_dao(
                    query_db, edit_extraction_task
                )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="更新成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="抽取任务不存在")

    @classmethod
    async def delete_extraction_task_services(
        cls, query_db: AsyncSession, task_object: DeleteExtractionTaskModel
    ):
        """
        删除抽取任务信息service

        :param query_db: orm对象
        :param task_object: 删除抽取任务对象
        :return: 删除抽取任务校验结果
        """
        if task_object.task_ids:
            task_id_list = task_object.task_ids.split(",")
            try:
                for task_id in task_id_list:
                    await Extraction_taskDao.delete_extraction_task_dao(
                        query_db, ExtractionTaskModel(taskId=task_id)
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入为空")

    @classmethod
    async def extraction_task_detail_services(
        cls, query_db: AsyncSession, task_id: int
    ):
        """
        获取抽取任务详细信息service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 对应的信息
        """
        extraction_task = await Extraction_taskDao.get_extraction_task_detail_by_id(
            query_db, task_id=task_id
        )
        if extraction_task:
            result = ExtractionTaskModel(
                **CamelCaseUtil.transform_result(extraction_task)
            )
            # 获取关联的论文ID
            paper_ids = await Extraction_taskDao.get_task_papers(query_db, task_id)
            result.paper_ids = paper_ids
        else:
            result = ExtractionTaskModel(**dict())

        return result

    @classmethod
    async def add_task_paper_services(
        cls, query_db: AsyncSession, task_paper: CrudTaskPaperModel
    ):
        """
        添加任务与论文关联关系service

        :param query_db: orm对象
        :param task_paper: 关联关系对象
        :return: 操作结果
        """
        try:
            # 检查任务是否存在
            task_info = await cls.extraction_task_detail_services(
                query_db, task_paper.task_id
            )
            if not task_info.task_id:
                return CrudResponseModel(is_success=False, message="任务不存在")

            # 更新关联关系
            paper_ids = []
            if task_paper.paper_ids:
                paper_ids = [
                    int(pid.strip())
                    for pid in task_paper.paper_ids.split(",")
                    if pid.strip()
                ]

            await Extraction_taskDao.add_task_papers(
                query_db, task_paper.task_id, paper_ids
            )

            # 更新任务信息
            task_info.update_by = task_paper.update_by
            task_info.update_time = datetime.now()
            await cls.edit_extraction_task_services(query_db, task_info)

            await query_db.commit()
            return CrudResponseModel(is_success=True, message="关联论文更新成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def save_abstract_structure_services(
        cls, query_db: AsyncSession, abstract_structure: AbstractStructureModel
    ):
        """
        保存摘要结构服务

        :param query_db: orm对象
        :param abstract_structure: 摘要结构对象
        :return: 保存后的摘要结构ID
        """
        try:
            abstract = await AbstractStructureDao.add_abstract_structure_dao(
                query_db, abstract_structure
            )
            return abstract.abstract_id
        except Exception as e:
            raise e

    @classmethod
    async def execute_extraction_task_services(
        cls, query_db: AsyncSession, request: ExtractionRequestModel
    ):
        """
        执行抽取任务service

        :param query_db: orm对象
        :param request: 抽取请求
        :return: 抽取结果
        """
        # 获取抽取方法信息
        method_info = await Extraction_methodService.extraction_method_detail_services(
            query_db, request.method_id
        )
        if not method_info.method_id:
            raise ServiceException(message=f"抽取方法ID {request.method_id} 不存在")

        # 获取或创建论文
        paper = None
        if request.paper_id:
            # 使用已有论文
            paper_info = await PaperService.paper_detail_services(
                query_db, request.paper_id
            )
            if not paper_info:
                raise ServiceException(message=f"论文ID {request.paper_id} 不存在")
            paper = paper_info
        elif request.paper:
            # 保存新论文
            paper = request.paper
            add_paper_result = await PaperService.add_paper_services(query_db, paper)
            if not add_paper_result.is_success:
                raise ServiceException(
                    message=f"保存论文失败: {add_paper_result.message}"
                )

            # 获取新保存的论文ID
            if add_paper_result.data and "paper_id" in add_paper_result.data:
                paper_id = add_paper_result.data["paper_id"]
                paper = await PaperService.paper_detail_services(query_db, paper_id)
            else:
                raise ServiceException(message="无法获取新保存论文的ID")
        else:
            raise ServiceException(message="必须提供论文ID或论文对象")
        # 创建任务记录
        task = ExtractionTaskModel()
        task.method_id = request.method_id
        task.execution_parameters = request.execution_parameters
        task.status = "1"
        task.started_at = datetime.now()
        task.create_by = request.create_by
        task.create_time = datetime.now()
        task.update_by = request.update_by
        # 确保method_id不为空
        if not task.method_id:
            raise ServiceException(message="抽取方法ID不能为空")

        # 确保有创建者和更新者信息
        if not task.create_by and paper and paper.create_by:
            task.create_by = paper.create_by

        if not task.update_by and paper and paper.update_by:
            task.update_by = paper.update_by

        # 如果仍然没有创建和更新信息，使用默认值
        if not task.create_by:
            task.create_by = "system"

        if not task.update_by:
            task.update_by = "system"

        task_result = await cls.add_extraction_task_services(query_db, task)
        if not task_result.is_success:
            raise ServiceException(message=f"创建抽取任务失败: {task_result.message}")

        task_id = task_result.result["task_id"]

        # 根据方法类型选择抽取器
        method_type = ExtractionMethodType(method_info.method_type)

        try:
            # 构建执行参数
            execution_params = request.execution_parameters or {}
            execution_params["db_session"] = query_db

            # 根据方法类型添加必要参数
            if method_type == ExtractionMethodType.REGEX:
                execution_params["template_id"] = method_info.template_id
            elif method_type == ExtractionMethodType.LLM:
                execution_params["model_id"] = method_info.model_id
                execution_params["prompt_id"] = method_info.prompt_id

            # 获取抽取器
            extractor = ExtractorFactory.get_extractor(method_type)

            # 执行抽取
            abstract_structure = await extractor.extract(paper, execution_params)

            abstract_structure.create_by = task.create_by
            abstract_structure.update_by = task.update_by
            abstract_structure.extraction_date = datetime.now()
            abstract_structure.status = "0"

            # 保存摘要结构到数据库
            abstract_id = await cls.save_abstract_structure_services(
                query_db, abstract_structure
            )
            # 更新论文的abstract_id
            paper.abstract_id = abstract_id
            paper.update_time = datetime.now()
            await PaperService.edit_paper_services(query_db, paper)

            # 更新任务状态为完成
            task_update = {
                "task_id": task_id,
                "status": "2",  # 2表示已完成
                "completed_at": datetime.now(),
                "update_time": datetime.now(),
            }
            await Extraction_taskDao.edit_extraction_task_dao(query_db, task_update)

            # 提交事务
            await query_db.commit()

            # 返回抽取结果
            return ExtractionResponseModel(
                task_id=task_id, status="2", abstract_structure=abstract_structure
            )

        except Exception as e:
            await query_db.rollback()

            # 更新任务状态为失败
            try:
                task_update = {
                    "task_id": task_id,
                    "status": "3",  # 3表示失败
                    "completed_at": datetime.now(),
                    "error_message": str(e),
                    "update_time": datetime.now(),
                }
                await Extraction_taskDao.edit_extraction_task_dao(query_db, task_update)
                await query_db.commit()
            except Exception:
                pass

            # 返回失败信息
            return ExtractionResponseModel(
                task_id=task_id, status="3", error_message=str(e)
            )

    @staticmethod
    async def export_extraction_task_list_services(extraction_task_list: List):
        """
        导出抽取任务信息service

        :param extraction_task_list: 抽取任务信息列表
        :return: 抽取任务信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "taskId": "任务ID",
            "methodId": "抽取方法ID",
            "methodName": "抽取方法名称",
            "methodType": "抽取方法类型",
            "status": "状态",
            "startedAt": "开始时间",
            "completedAt": "完成时间",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(extraction_task_list, mapping_dict)

        return binary_data
