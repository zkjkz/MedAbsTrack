from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from module_literature.entity.do.author_do import PmsAuthor


class AuthorDao:
    """
    作者信息模块数据库操作层
    """

    @classmethod
    async def get_author_list(cls, db: AsyncSession):
        """
        获取所有作者列表

        :param db: orm对象
        :return: 作者列表
        """
        author_list = (
            (await db.execute(select(PmsAuthor).order_by(PmsAuthor.author_id.desc())))
            .scalars()
            .all()
        )

        return author_list

    @classmethod
    async def get_author_detail_by_id(cls, db: AsyncSession, author_id: int):
        """
        根据ID获取作者详细信息

        :param db: orm对象
        :param author_id: 作者ID
        :return: 作者信息对象
        """
        author_info = (
            (
                await db.execute(
                    select(PmsAuthor).where(PmsAuthor.author_id == author_id)
                )
            )
            .scalars()
            .first()
        )

        return author_info

    @classmethod
    async def get_author_by_name(
        cls, db: AsyncSession, name: str, affiliation: Optional[str] = None
    ):
        """
        根据作者姓名和所属机构获取作者信息

        :param db: orm对象
        :param name: 作者姓名
        :param affiliation: 作者所属机构
        :return: 作者信息对象
        """
        query = select(PmsAuthor).where(PmsAuthor.name == name)
        if affiliation:
            query = query.where(PmsAuthor.affiliation == affiliation)

        author_info = (await db.execute(query)).scalars().first()
        return author_info

    @classmethod
    async def add_author_dao(cls, db: AsyncSession, author_dict: dict):
        """
        新增作者信息

        :param db: orm对象
        :param author_dict: 作者信息字典
        :return: 新增的作者ID
        """
        db_author = PmsAuthor(**author_dict)
        db.add(db_author)
        await db.flush()

        return db_author.author_id

    @classmethod
    async def edit_author_dao(cls, db: AsyncSession, author: dict):
        """
        编辑作者信息

        :param db: orm对象
        :param author: 需要更新的作者信息字典
        :return:
        """
        await db.execute(update(PmsAuthor), [author])

    @classmethod
    async def delete_author_dao(cls, db: AsyncSession, author_ids: List[int]):
        """
        删除作者信息

        :param db: orm对象
        :param author_ids: 作者ID列表
        :return:
        """
        await db.execute(delete(PmsAuthor).where(PmsAuthor.author_id.in_(author_ids)))
