from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.extraction_method_do import PmsExtractionMethod
from module_literature.entity.vo.extraction_method_vo import (
    Extraction_methodModel,
    Extraction_methodPageQueryModel,
)
from utils.page_util import PageUtil


class Extraction_methodDao:
    """
    抽取方法配置模块数据库操作层
    """

    @classmethod
    async def get_extraction_method_detail_by_id(cls, db: AsyncSession, method_id: int):
        """
        根据获取抽取方法配置详细信息

        :param db: orm对象
        :param method_id:
        :return: 抽取方法配置信息对象
        """
        extraction_method_info = (
            (
                await db.execute(
                    select(PmsExtractionMethod).where(
                        PmsExtractionMethod.method_id == method_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return extraction_method_info

    @classmethod
    async def get_extraction_method_detail_by_info(
        cls, db: AsyncSession, extraction_method: Extraction_methodModel
    ):
        """
        根据抽取方法配置参数获取抽取方法配置信息

        :param db: orm对象
        :param extraction_method: 抽取方法配置参数对象
        :return: 抽取方法配置信息对象
        """
        extraction_method_info = (
            (await db.execute(select(PmsExtractionMethod).where())).scalars().first()
        )

        return extraction_method_info

    @classmethod
    async def get_extraction_method_list(
        cls,
        db: AsyncSession,
        query_object: Extraction_methodPageQueryModel,
        is_page: bool = False,
    ):
        """
        根据查询参数获取抽取方法配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 抽取方法配置列表信息对象
        """
        query = (
            select(PmsExtractionMethod)
            .where(
                (
                    PmsExtractionMethod.method_name.like(
                        f"%{query_object.method_name}%"
                    )
                    if query_object.method_name
                    else True
                ),
                (
                    PmsExtractionMethod.method_type == query_object.method_type
                    if query_object.method_type
                    else True
                ),
                (
                    PmsExtractionMethod.description == query_object.description
                    if query_object.description
                    else True
                ),
                (
                    PmsExtractionMethod.config_params == query_object.config_params
                    if query_object.config_params
                    else True
                ),
                (
                    PmsExtractionMethod.template_id == query_object.template_id
                    if query_object.template_id
                    else True
                ),
                (
                    PmsExtractionMethod.model_id == query_object.model_id
                    if query_object.model_id
                    else True
                ),
                (
                    PmsExtractionMethod.prompt_id == query_object.prompt_id
                    if query_object.prompt_id
                    else True
                ),
                (
                    PmsExtractionMethod.status == query_object.status
                    if query_object.status
                    else True
                ),
            )
            .order_by(PmsExtractionMethod.method_id)
            .distinct()
        )
        extraction_method_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return extraction_method_list

    @classmethod
    async def add_extraction_method_dao(
        cls, db: AsyncSession, extraction_method: Extraction_methodModel
    ):
        """
        新增抽取方法配置数据库操作

        :param db: orm对象
        :param extraction_method: 抽取方法配置对象
        :return:
        """
        db_extraction_method = PmsExtractionMethod(
            **extraction_method.model_dump(exclude={})
        )
        db.add(db_extraction_method)
        await db.flush()

        return db_extraction_method

    @classmethod
    async def edit_extraction_method_dao(
        cls, db: AsyncSession, extraction_method: dict
    ):
        """
        编辑抽取方法配置数据库操作

        :param db: orm对象
        :param extraction_method: 需要更新的抽取方法配置字典
        :return:
        """
        await db.execute(update(PmsExtractionMethod), [extraction_method])

    @classmethod
    async def delete_extraction_method_dao(
        cls, db: AsyncSession, extraction_method: Extraction_methodModel
    ):
        """
        删除抽取方法配置数据库操作

        :param db: orm对象
        :param extraction_method: 抽取方法配置对象
        :return:
        """
        await db.execute(
            delete(PmsExtractionMethod).where(
                PmsExtractionMethod.method_id.in_([extraction_method.method_id])
            )
        )
