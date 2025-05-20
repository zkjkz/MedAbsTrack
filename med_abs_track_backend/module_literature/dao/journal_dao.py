from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.journal_do import PmsJournal


class JournalDao:
    """
    期刊信息模块数据库操作层
    """

    @classmethod
    async def get_journal_detail_by_id(cls, db: AsyncSession, journal_id: int):
        """
        根据ID获取期刊详细信息

        :param db: orm对象
        :param journal_id: 期刊ID
        :return: 期刊信息对象
        """
        journal_info = (
            (
                await db.execute(
                    select(PmsJournal).where(PmsJournal.journal_id == journal_id)
                )
            )
            .scalars()
            .first()
        )

        return journal_info

    @classmethod
    async def get_journal_by_name(cls, db: AsyncSession, journal_name: str):
        """
        根据期刊名称获取期刊信息

        :param db: orm对象
        :param journal_name: 期刊名称
        :return: 期刊信息对象
        """
        journal_info = (
            (
                await db.execute(
                    select(PmsJournal).where(PmsJournal.journal_name == journal_name)
                )
            )
            .scalars()
            .first()
        )

        return journal_info

    @classmethod
    async def add_journal_dao(cls, db: AsyncSession, journal_dict: dict):
        """
        新增期刊信息

        :param db: orm对象
        :param journal_dict: 期刊信息字典
        :return: 新增的期刊ID
        """
        db_journal = PmsJournal(**journal_dict)
        db.add(db_journal)
        await db.flush()

        return db_journal.journal_id
