from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.extraction_template_do import PmsExtractionTemplate
from module_literature.entity.vo.extraction_template_vo import (
    Extraction_templateModel,
    Extraction_templatePageQueryModel,
)
from utils.page_util import PageUtil


class Extraction_templateDao:
    """
    摘要抽取模板模块数据库操作层
    """

    @classmethod
    async def get_extraction_template_detail_by_id(
        cls, db: AsyncSession, template_id: int
    ):
        """
        根据获取摘要抽取模板详细信息

        :param db: orm对象
        :param template_id:
        :return: 摘要抽取模板信息对象
        """
        extraction_template_info = (
            (
                await db.execute(
                    select(PmsExtractionTemplate).where(
                        PmsExtractionTemplate.template_id == template_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return extraction_template_info

    @classmethod
    async def get_extraction_template_detail_by_info(
        cls, db: AsyncSession, extraction_template: Extraction_templateModel
    ):
        """
        根据摘要抽取模板参数获取摘要抽取模板信息

        :param db: orm对象
        :param extraction_template: 摘要抽取模板参数对象
        :return: 摘要抽取模板信息对象
        """
        extraction_template_info = (
            (await db.execute(select(PmsExtractionTemplate).where())).scalars().first()
        )

        return extraction_template_info

    @classmethod
    async def get_extraction_template_list(
        cls,
        db: AsyncSession,
        query_object: Extraction_templatePageQueryModel,
        is_page: bool = False,
    ):
        """
        根据查询参数获取摘要抽取模板列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 摘要抽取模板列表信息对象
        """
        query = (
            select(PmsExtractionTemplate)
            .where(
                (
                    PmsExtractionTemplate.template_name.like(
                        f"%{query_object.template_name}%"
                    )
                    if query_object.template_name
                    else True
                ),
                (
                    PmsExtractionTemplate.description == query_object.description
                    if query_object.description
                    else True
                ),
                (
                    PmsExtractionTemplate.template_content
                    == query_object.template_content
                    if query_object.template_content
                    else True
                ),
                (
                    PmsExtractionTemplate.status == query_object.status
                    if query_object.status
                    else True
                ),
            )
            .order_by(PmsExtractionTemplate.template_id)
            .distinct()
        )
        extraction_template_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return extraction_template_list

    @classmethod
    async def add_extraction_template_dao(
        cls, db: AsyncSession, extraction_template: Extraction_templateModel
    ):
        """
        新增摘要抽取模板数据库操作

        :param db: orm对象
        :param extraction_template: 摘要抽取模板对象
        :return:
        """
        db_extraction_template = PmsExtractionTemplate(
            **extraction_template.model_dump(exclude={})
        )
        db.add(db_extraction_template)
        await db.flush()

        return db_extraction_template

    @classmethod
    async def edit_extraction_template_dao(
        cls, db: AsyncSession, extraction_template: dict
    ):
        """
        编辑摘要抽取模板数据库操作

        :param db: orm对象
        :param extraction_template: 需要更新的摘要抽取模板字典
        :return:
        """
        await db.execute(update(PmsExtractionTemplate), [extraction_template])

    @classmethod
    async def delete_extraction_template_dao(
        cls, db: AsyncSession, extraction_template: Extraction_templateModel
    ):
        """
        删除摘要抽取模板数据库操作

        :param db: orm对象
        :param extraction_template: 摘要抽取模板对象
        :return:
        """
        await db.execute(
            delete(PmsExtractionTemplate).where(
                PmsExtractionTemplate.template_id.in_([extraction_template.template_id])
            )
        )
