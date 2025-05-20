from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.prompt_template_do import PmsPromptTemplate
from module_literature.entity.vo.prompt_template_vo import (
    Prompt_templateModel,
    Prompt_templatePageQueryModel,
)
from utils.page_util import PageUtil


class Prompt_templateDao:
    """
    Prompt模板模块数据库操作层
    """

    @classmethod
    async def get_prompt_template_detail_by_id(cls, db: AsyncSession, prompt_id: int):
        """
        根据获取Prompt模板详细信息

        :param db: orm对象
        :param prompt_id:
        :return: Prompt模板信息对象
        """
        prompt_template_info = (
            (
                await db.execute(
                    select(PmsPromptTemplate).where(
                        PmsPromptTemplate.prompt_id == prompt_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return prompt_template_info

    @classmethod
    async def get_prompt_template_detail_by_info(
        cls, db: AsyncSession, prompt_template: Prompt_templateModel
    ):
        """
        根据Prompt模板参数获取Prompt模板信息

        :param db: orm对象
        :param prompt_template: Prompt模板参数对象
        :return: Prompt模板信息对象
        """
        prompt_template_info = (
            (await db.execute(select(PmsPromptTemplate).where())).scalars().first()
        )

        return prompt_template_info

    @classmethod
    async def get_prompt_template_list(
        cls,
        db: AsyncSession,
        query_object: Prompt_templatePageQueryModel,
        is_page: bool = False,
    ):
        """
        根据查询参数获取Prompt模板列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: Prompt模板列表信息对象
        """
        query = (
            select(PmsPromptTemplate)
            .where(
                (
                    PmsPromptTemplate.prompt_name.like(f"%{query_object.prompt_name}%")
                    if query_object.prompt_name
                    else True
                ),
                (
                    PmsPromptTemplate.description == query_object.description
                    if query_object.description
                    else True
                ),
                (
                    PmsPromptTemplate.prompt_content == query_object.prompt_content
                    if query_object.prompt_content
                    else True
                ),
                (
                    PmsPromptTemplate.status == query_object.status
                    if query_object.status
                    else True
                ),
            )
            .order_by(PmsPromptTemplate.prompt_id)
            .distinct()
        )
        prompt_template_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return prompt_template_list

    @classmethod
    async def add_prompt_template_dao(
        cls, db: AsyncSession, prompt_template: Prompt_templateModel
    ):
        """
        新增Prompt模板数据库操作

        :param db: orm对象
        :param prompt_template: Prompt模板对象
        :return:
        """
        db_prompt_template = PmsPromptTemplate(**prompt_template.model_dump(exclude={}))
        db.add(db_prompt_template)
        await db.flush()

        return db_prompt_template

    @classmethod
    async def edit_prompt_template_dao(cls, db: AsyncSession, prompt_template: dict):
        """
        编辑Prompt模板数据库操作

        :param db: orm对象
        :param prompt_template: 需要更新的Prompt模板字典
        :return:
        """
        await db.execute(update(PmsPromptTemplate), [prompt_template])

    @classmethod
    async def delete_prompt_template_dao(
        cls, db: AsyncSession, prompt_template: Prompt_templateModel
    ):
        """
        删除Prompt模板数据库操作

        :param db: orm对象
        :param prompt_template: Prompt模板对象
        :return:
        """
        await db.execute(
            delete(PmsPromptTemplate).where(
                PmsPromptTemplate.prompt_id.in_([prompt_template.prompt_id])
            )
        )
