from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.paper_keyword_do import PmsPaperKeyword


class PaperKeywordDao:
    """
    论文与关键词关联模块数据库操作层
    """

    @classmethod
    async def get_paper_keywords(cls, db: AsyncSession, paper_id: int):
        """
        获取指定论文的所有关键词ID

        :param db: orm对象
        :param paper_id: 论文ID
        :return: 关键词ID列表
        """
        result = await db.execute(
            select(PmsPaperKeyword.keyword_id).where(
                PmsPaperKeyword.paper_id == paper_id
            )
        )

        return [row[0] for row in result.all()]

    @classmethod
    async def get_papers_by_keyword(cls, db: AsyncSession, keyword_id: int):
        """
        获取包含指定关键词的所有论文ID

        :param db: orm对象
        :param keyword_id: 关键词ID
        :return: 论文ID列表
        """
        result = await db.execute(
            select(PmsPaperKeyword.paper_id).where(
                PmsPaperKeyword.keyword_id == keyword_id
            )
        )

        return [row[0] for row in result.all()]

    @classmethod
    async def add_paper_keyword_dao(
        cls, db: AsyncSession, paper_id: int, keyword_id: int
    ):
        """
        添加论文与关键词的关联

        :param db: orm对象
        :param paper_id: 论文ID
        :param keyword_id: 关键词ID
        :return:
        """
        # 检查是否已存在关联
        exist_relation = (
            await db.execute(
                select(PmsPaperKeyword).where(
                    PmsPaperKeyword.paper_id == paper_id,
                    PmsPaperKeyword.keyword_id == keyword_id,
                )
            )
        ).first()

        if not exist_relation:
            db_paper_keyword = PmsPaperKeyword(paper_id=paper_id, keyword_id=keyword_id)
            db.add(db_paper_keyword)
            await db.flush()

    @classmethod
    async def delete_paper_keyword_dao(cls, db: AsyncSession, paper_id: int):
        """
        删除指定论文的所有关键词关联

        :param db: orm对象
        :param paper_id: 论文ID
        :return:
        """
        await db.execute(
            delete(PmsPaperKeyword).where(PmsPaperKeyword.paper_id == paper_id)
        )
