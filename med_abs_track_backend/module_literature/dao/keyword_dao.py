from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.keyword_do import PmsKeyword


class KeywordDao:
    """
    论文关键词模块数据库操作层
    """

    @classmethod
    async def get_keyword_detail_by_id(cls, db: AsyncSession, keyword_id: int):
        """
        根据ID获取关键词详细信息

        :param db: orm对象
        :param keyword_id: 关键词ID
        :return: 关键词信息对象
        """
        keyword_info = (
            (
                await db.execute(
                    select(PmsKeyword).where(PmsKeyword.keyword_id == keyword_id)
                )
            )
            .scalars()
            .first()
        )

        return keyword_info

    @classmethod
    async def get_keyword_by_text(cls, db: AsyncSession, keyword_text: str):
        """
        根据关键词文本获取关键词信息

        :param db: orm对象
        :param keyword_text: 关键词文本
        :return: 关键词信息对象
        """
        keyword_info = (
            (
                await db.execute(
                    select(PmsKeyword).where(PmsKeyword.keyword == keyword_text)
                )
            )
            .scalars()
            .first()
        )

        return keyword_info

    @classmethod
    async def add_keyword_dao(cls, db: AsyncSession, keyword_dict: dict):
        """
        新增关键词信息

        :param db: orm对象
        :param keyword_dict: 关键词信息字典
        :return: 新增的关键词ID
        """
        db_keyword = PmsKeyword(**keyword_dict)
        db.add(db_keyword)
        await db.flush()

        return db_keyword.keyword_id
