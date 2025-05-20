from sqlalchemy import select, func, join
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import json

from module_literature.entity.do.extraction_task_do import PmsExtractionTask
from module_literature.entity.do.extraction_method_do import (
    PmsExtractionMethod,
    ExtractionMethodType,
)
from module_literature.entity.do.task_paper_do import PmsTaskPaper
from module_literature.entity.vo.extraction_task_vo import (
    ExtractionTaskModel,
    ExtractionTaskPageQueryModel,
)
from utils.page_util import PageResponseModel


class Extraction_taskDao:
    """
    抽取任务数据访问对象
    """

    @staticmethod
    async def get_extraction_task_list(
        query_db: AsyncSession,
        query_object: ExtractionTaskPageQueryModel,
        is_page: bool = False,
    ):
        """
        获取抽取任务列表信息dao

        :param query_db: 数据库会话
        :param query_object: 查询对象
        :param is_page: 是否分页
        :return: 抽取任务列表
        """
        # 构建联表查询
        j = join(
            PmsExtractionTask,
            PmsExtractionMethod,
            PmsExtractionTask.method_id == PmsExtractionMethod.method_id,
            isouter=True,
        )
        query = select(
            PmsExtractionTask,
            PmsExtractionMethod.method_name,
            PmsExtractionMethod.method_type,
        ).select_from(j)

        # 添加查询条件
        if query_object.method_id:
            query = query.where(PmsExtractionTask.method_id == query_object.method_id)

        if query_object.status:
            query = query.where(PmsExtractionTask.status == query_object.status)

        # 添加排序
        query = query.order_by(PmsExtractionTask.task_id.desc())

        # 执行查询
        result = []
        if is_page:
            # 计算总记录数
            count_query = select(func.count()).select_from(j)
            if query_object.method_id:
                count_query = count_query.where(
                    PmsExtractionTask.method_id == query_object.method_id
                )
            if query_object.status:
                count_query = count_query.where(
                    PmsExtractionTask.status == query_object.status
                )

            total_result = await query_db.execute(count_query)
            total = total_result.scalar() or 0

            # 添加分页
            query = query.offset(
                (query_object.page_num - 1) * query_object.page_size
            ).limit(query_object.page_size)

            # 执行查询
            rs = await query_db.execute(query)
            rows = []
            for row in rs.fetchall():
                task, method_name, method_type = row
                task_dict = {
                    c.name: getattr(task, c.name) for c in task.__table__.columns
                }
                # 处理JSON格式字段
                if task_dict.get("execution_parameters"):
                    try:
                        task_dict["execution_parameters"] = json.loads(
                            task_dict["execution_parameters"]
                        )
                    except:
                        pass
                task_dict["method_name"] = method_name
                task_dict["method_type"] = (
                    method_type.value.lower() if method_type else None
                )
                rows.append(task_dict)

            result = PageResponseModel(total=total, rows=rows)
        else:
            rs = await query_db.execute(query)
            rows = []
            for row in rs.fetchall():
                task, method_name, method_type = row
                task_dict = {
                    c.name: getattr(task, c.name) for c in task.__table__.columns
                }
                # 处理JSON格式字段
                if task_dict.get("execution_parameters"):
                    try:
                        task_dict["execution_parameters"] = json.loads(
                            task_dict["execution_parameters"]
                        )
                    except:
                        pass
                task_dict["method_name"] = method_name
                task_dict["method_type"] = (
                    method_type.value.lower() if method_type else None
                )
                rows.append(task_dict)
            result = rows

        return result

    @staticmethod
    async def add_extraction_task_dao(
        query_db: AsyncSession, task_object: ExtractionTaskModel
    ) -> int:
        """
        添加抽取任务dao

        :param query_db: 数据库会话
        :param task_object: 任务对象
        :return: 新增的任务ID
        """
        # 转换执行参数为JSON字符串
        execution_parameters = task_object.execution_parameters
        if execution_parameters is not None and not isinstance(
            execution_parameters, str
        ):
            execution_parameters = json.dumps(execution_parameters)

        # 创建任务实体
        task = PmsExtractionTask(
            method_id=task_object.method_id,
            execution_parameters=execution_parameters,
            status=task_object.status,
            started_at=task_object.started_at,
            completed_at=task_object.completed_at,
            error_message=task_object.error_message,
            create_by=task_object.create_by,
            create_time=task_object.create_time,
            update_by=task_object.update_by,
            update_time=task_object.update_time,
            remark=task_object.remark,
        )

        # 添加到会话
        query_db.add(task)
        await query_db.flush()
        task_id = task.task_id

        # 如果有关联的论文，添加关联关系
        if task_object.paper_ids:
            for paper_id in task_object.paper_ids:
                task_paper = PmsTaskPaper(task_id=task_id, paper_id=paper_id)
                query_db.add(task_paper)
            await query_db.flush()

        return task_id

    @staticmethod
    async def edit_extraction_task_dao(
        query_db: AsyncSession, task_object: dict
    ) -> None:
        """
        更新抽取任务dao

        :param query_db: 数据库会话
        :param task_object: 任务对象
        """
        task_id = task_object.pop("task_id")

        # 转换执行参数为JSON字符串
        if (
            "execution_parameters" in task_object
            and task_object["execution_parameters"] is not None
            and not isinstance(task_object["execution_parameters"], str)
        ):
            task_object["execution_parameters"] = json.dumps(
                task_object["execution_parameters"]
            )

        # 查询任务
        task = await query_db.get(PmsExtractionTask, task_id)
        if task:
            # 更新任务属性
            for key, value in task_object.items():
                if hasattr(task, key):
                    setattr(task, key, value)

    @staticmethod
    async def delete_extraction_task_dao(
        query_db: AsyncSession, task_object: ExtractionTaskModel
    ) -> None:
        """
        删除抽取任务dao

        :param query_db: 数据库会话
        :param task_object: 任务对象
        """
        # 首先删除关联关系
        relations = (
            (
                await query_db.execute(
                    select(PmsTaskPaper).where(
                        PmsTaskPaper.task_id == task_object.task_id
                    )
                )
            )
            .scalars()
            .all()
        )

        for relation in relations:
            await query_db.delete(relation)

        # 然后删除任务
        task = await query_db.get(PmsExtractionTask, task_object.task_id)
        if task:
            await query_db.delete(task)

    @staticmethod
    async def get_extraction_task_detail_by_id(
        query_db: AsyncSession, task_id: int
    ) -> Dict[str, Any]:
        """
        根据ID获取抽取任务详情dao

        :param query_db: 数据库会话
        :param task_id: 任务ID
        :return: 任务详情
        """
        # 构建联表查询
        j = join(
            PmsExtractionTask,
            PmsExtractionMethod,
            PmsExtractionTask.method_id == PmsExtractionMethod.method_id,
            isouter=True,
        )
        query = (
            select(
                PmsExtractionTask,
                PmsExtractionMethod.method_name,
                PmsExtractionMethod.method_type,
            )
            .select_from(j)
            .where(PmsExtractionTask.task_id == task_id)
        )

        # 执行查询
        result = await query_db.execute(query)
        row = result.first()

        if row:
            task, method_name, method_type = row
            task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
            # 处理JSON格式字段
            if task_dict.get("execution_parameters"):
                try:
                    task_dict["execution_parameters"] = json.loads(
                        task_dict["execution_parameters"]
                    )
                except:
                    pass
            task_dict["method_name"] = method_name
            task_dict["method_type"] = (
                method_type.value.lower() if method_type else None
            )
            return task_dict

        return {}

    @staticmethod
    async def get_task_papers(query_db: AsyncSession, task_id: int) -> List[int]:
        """
        获取任务关联的论文ID列表

        :param query_db: 数据库会话
        :param task_id: 任务ID
        :return: 论文ID列表
        """
        query = select(PmsTaskPaper.paper_id).where(PmsTaskPaper.task_id == task_id)
        result = await query_db.execute(query)
        paper_ids = [row[0] for row in result.all()]

        return paper_ids

    @staticmethod
    async def add_task_papers(
        query_db: AsyncSession, task_id: int, paper_ids: List[int]
    ) -> None:
        """
        添加任务与论文的关联关系

        :param query_db: 数据库会话
        :param task_id: 任务ID
        :param paper_ids: 论文ID列表
        """
        # 首先删除现有关联
        relations = (
            (
                await query_db.execute(
                    select(PmsTaskPaper).where(PmsTaskPaper.task_id == task_id)
                )
            )
            .scalars()
            .all()
        )

        for relation in relations:
            await query_db.delete(relation)

        # 添加新关联
        for paper_id in paper_ids:
            task_paper = PmsTaskPaper(task_id=task_id, paper_id=paper_id)
            query_db.add(task_paper)

        await query_db.flush()
