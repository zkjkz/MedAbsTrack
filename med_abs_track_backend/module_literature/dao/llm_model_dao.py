from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.llm_model_do import PmsLlmModel
from module_literature.entity.vo.llm_model_vo import (
    Llm_modelModel,
    Llm_modelPageQueryModel,
)
from utils.page_util import PageUtil


class Llm_modelDao:
    """
    大语言模型基座模块数据库操作层
    """

    @classmethod
    async def get_llm_model_detail_by_id(cls, db: AsyncSession, model_id: int):
        """
        根据id获取大语言模型基座详细信息

        :param db: orm对象
        :param model_id:
        :return: 大语言模型基座信息对象
        """
        llm_model_info = (
            (
                await db.execute(
                    select(PmsLlmModel).where(PmsLlmModel.model_id == model_id)
                )
            )
            .scalars()
            .first()
        )

        return llm_model_info

    @classmethod
    async def get_llm_model_detail_by_info(
        cls, db: AsyncSession, llm_model: Llm_modelModel
    ):
        """
        根据大语言模型基座参数获取大语言模型基座信息

        :param db: orm对象
        :param llm_model: 大语言模型基座参数对象
        :return: 大语言模型基座信息对象
        """
        llm_model_info = (
            (await db.execute(select(PmsLlmModel).where())).scalars().first()
        )

        return llm_model_info

    @classmethod
    async def get_llm_model_list(
        cls,
        db: AsyncSession,
        query_object: Llm_modelPageQueryModel,
        is_page: bool = False,
    ):
        """
        根据查询参数获取大语言模型基座列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 大语言模型基座列表信息对象
        """
        query = (
            select(PmsLlmModel)
            .where(
                (
                    PmsLlmModel.display_name.like(f"%{query_object.display_name}%")
                    if query_object.display_name
                    else True
                ),
                (
                    PmsLlmModel.model_name == query_object.model_name
                    if query_object.model_name
                    else True
                ),
                (
                    PmsLlmModel.model_version == query_object.model_version
                    if query_object.model_version
                    else True
                ),
                (
                    PmsLlmModel.provider == query_object.provider
                    if query_object.provider
                    else True
                ),
                (
                    PmsLlmModel.base_url == query_object.base_url
                    if query_object.base_url
                    else True
                ),
                (
                    PmsLlmModel.api_key == query_object.api_key
                    if query_object.api_key
                    else True
                ),
                (
                    PmsLlmModel.organization_id == query_object.organization_id
                    if query_object.organization_id
                    else True
                ),
                (
                    PmsLlmModel.status == query_object.status
                    if query_object.status
                    else True
                ),
            )
            .order_by(PmsLlmModel.model_id)
            .distinct()
        )
        llm_model_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return llm_model_list

    @classmethod
    async def add_llm_model_dao(cls, db: AsyncSession, llm_model: Llm_modelModel):
        """
        新增大语言模型基座数据库操作

        :param db: orm对象
        :param llm_model: 大语言模型基座对象
        :return:
        """
        db_llm_model = PmsLlmModel(**llm_model.model_dump(exclude={}))
        db.add(db_llm_model)
        await db.flush()

        return db_llm_model

    @classmethod
    async def edit_llm_model_dao(cls, db: AsyncSession, llm_model: dict):
        """
        编辑大语言模型基座数据库操作

        :param db: orm对象
        :param llm_model: 需要更新的大语言模型基座字典
        :return:
        """
        await db.execute(update(PmsLlmModel), [llm_model])

    @classmethod
    async def delete_llm_model_dao(cls, db: AsyncSession, llm_model: Llm_modelModel):
        """
        删除大语言模型基座数据库操作

        :param db: orm对象
        :param llm_model: 大语言模型基座对象
        :return:
        """
        await db.execute(
            delete(PmsLlmModel).where(PmsLlmModel.model_id.in_([llm_model.model_id]))
        )
