from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_literature.entity.do.abstract_structure_do import PmsAbstractStructure
from module_literature.entity.do.paper_do import PmsPaper
from module_literature.entity.vo.abstract_structure_vo import (
    AbstractStructureModel,
    AbstractStructurePageQueryModel,
)
from utils.page_util import PageUtil


class AbstractStructureDao:
    """
    摘要结构模块数据库操作层
    """

    @classmethod
    async def get_abstract_structure_detail_by_id(
        cls, db: AsyncSession, abstract_id: int
    ):
        """
        根据id获取摘要结构详细信息

        :param db: orm对象
        :param abstract_id: 摘要结构ID
        :return: 摘要结构信息对象
        """
        abstract_structure_info = (
            (
                await db.execute(
                    select(PmsAbstractStructure).where(
                        PmsAbstractStructure.abstract_id == abstract_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return abstract_structure_info

    @classmethod
    async def get_abstract_structure_detail_by_info(
        cls, db: AsyncSession, abstract_structure: AbstractStructureModel
    ):
        """
        根据摘要结构参数获取摘要结构信息

        :param db: orm对象
        :param abstract_structure: 摘要结构参数对象
        :return: 摘要结构信息对象
        """
        abstract_structure_info = (
            (await db.execute(select(PmsAbstractStructure).where())).scalars().first()
        )

        return abstract_structure_info

    @classmethod
    async def get_abstract_structure_list(
        cls,
        db: AsyncSession,
        query_object: AbstractStructurePageQueryModel,
        is_page: bool = False,
    ):
        """
        根据查询参数获取摘要结构列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 摘要结构列表信息对象
        """
        query = select(PmsAbstractStructure).where(
            (
                PmsAbstractStructure.abstract_id == query_object.abstract_id
                if query_object.abstract_id
                else True
            ),
            (
                PmsAbstractStructure.background.contains(query_object.background)
                if query_object.background
                else True
            ),
            (
                PmsAbstractStructure.methods.contains(query_object.methods)
                if query_object.methods
                else True
            ),
            (
                PmsAbstractStructure.results.contains(query_object.results)
                if query_object.results
                else True
            ),
            (
                PmsAbstractStructure.conclusion.contains(query_object.conclusion)
                if query_object.conclusion
                else True
            ),
            (
                PmsAbstractStructure.status == query_object.status
                if query_object.status
                else True
            ),
            (
                PmsAbstractStructure.is_extracted == query_object.is_extracted
                if query_object.is_extracted is not None
                else True
            ),
            (
                and_(
                    PmsAbstractStructure.extraction_date
                    >= query_object.extraction_date_begin,
                    PmsAbstractStructure.extraction_date
                    <= query_object.extraction_date_end,
                )
                if query_object.extraction_date_begin
                and query_object.extraction_date_end
                else True
            ),
            (
                and_(
                    PmsAbstractStructure.create_time >= query_object.create_time_begin,
                    PmsAbstractStructure.create_time <= query_object.create_time_end,
                )
                if query_object.create_time_begin and query_object.create_time_end
                else True
            ),
        )

        # 处理排序
        if query_object.order_by_column and query_object.is_asc:
            if hasattr(PmsAbstractStructure, query_object.order_by_column):
                order_column = getattr(
                    PmsAbstractStructure, query_object.order_by_column
                )
                query = query.order_by(
                    order_column.asc()
                    if query_object.is_asc == "ascending"
                    else order_column.desc()
                )
            else:
                query = query.order_by(PmsAbstractStructure.abstract_id.desc())
        else:
            query = query.order_by(PmsAbstractStructure.abstract_id.desc())

        # 执行分页查询
        abstract_structure_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return abstract_structure_list

    @classmethod
    async def add_abstract_structure_dao(
        cls, db: AsyncSession, abstract_structure: AbstractStructureModel
    ):
        """
        新增摘要结构数据库操作

        :param db: orm对象
        :param abstract_structure: 摘要结构对象
        :return: 新增的摘要结构对象
        """
        # 构建数据模型
        db_abstract_structure = PmsAbstractStructure(
            **abstract_structure.model_dump(exclude={})
        )
        db.add(db_abstract_structure)
        await db.flush()

        return db_abstract_structure

    @classmethod
    async def edit_abstract_structure_dao(
        cls, db: AsyncSession, abstract_structure_dict: dict
    ):
        """
        编辑摘要结构数据库操作

        :param db: orm对象
        :param abstract_structure_dict: 需要更新的摘要结构字典
        :return:
        """
        await db.execute(update(PmsAbstractStructure), [abstract_structure_dict])

    @classmethod
    async def delete_abstract_structure_dao(
        cls, db: AsyncSession, abstract_structure: AbstractStructureModel
    ):
        """
        删除摘要结构数据库操作

        :param db: orm对象
        :param abstract_structure: 摘要结构对象
        :return:
        """
        await db.execute(
            delete(PmsAbstractStructure).where(
                PmsAbstractStructure.abstract_id.in_([abstract_structure.abstract_id])
            )
        )

    @classmethod
    async def check_abstract_structure_referenced(
        cls, db: AsyncSession, abstract_id_list: list
    ):
        """
        检查摘要结构是否被论文引用

        :param db: orm对象
        :param abstract_id_list: 摘要结构ID列表
        :return: 引用这些摘要结构的论文列表
        """
        abstract_ids = [int(id_str) for id_str in abstract_id_list if id_str]
        if not abstract_ids:
            return []

        result = await db.execute(
            select(PmsPaper).where(PmsPaper.abstract_id.in_(abstract_ids))
        )

        return result.scalars().all()

    @classmethod
    async def get_abstract_structure_by_paper_id(cls, db: AsyncSession, paper_id: int):
        """
        根据论文ID获取摘要结构

        :param db: orm对象
        :param paper_id: 论文ID
        :return: 摘要结构信息对象
        """
        # 先查询论文获取摘要结构ID
        paper_result = await db.execute(
            select(PmsPaper).where(PmsPaper.paper_id == paper_id)
        )
        paper = paper_result.scalars().first()

        if not paper or not paper.abstract_id:
            return None

        # 查询摘要结构
        abstract_result = await db.execute(
            select(PmsAbstractStructure).where(
                PmsAbstractStructure.abstract_id == paper.abstract_id
            )
        )

        return abstract_result.scalars().first()
