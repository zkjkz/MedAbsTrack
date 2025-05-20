from sqlalchemy import delete, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.paper_do import PmsPaper
from module_literature.entity.do.author_do import PmsAuthor
from module_literature.entity.do.keyword_do import PmsKeyword
from module_literature.entity.do.journal_do import PmsJournal
from module_literature.entity.do.abstract_structure_do import PmsAbstractStructure
from module_literature.entity.do.paper_author_do import PmsPaperAuthor
from module_literature.entity.do.paper_keyword_do import PmsPaperKeyword
from module_literature.entity.vo.paper_vo import PaperModel, PaperPageQueryModel
from utils.page_util import PageUtil


class PaperDao:
    """
    围手术期相关论文信息模块数据库操作层
    """

    @classmethod
    async def get_paper_detail_by_id(cls, db: AsyncSession, paper_id: int):
        """
        根据获取围手术期相关论文信息详细信息

        :param db: orm对象
        :param paper_id:
        :return: 围手术期相关论文信息信息对象
        """
        paper_info = (
            (await db.execute(select(PmsPaper).where(PmsPaper.paper_id == paper_id)))
            .scalars()
            .first()
        )

        return paper_info

    @classmethod
    async def get_paper_detail_by_info(cls, db: AsyncSession, paper: PaperModel):
        """
        根据围手术期相关论文信息参数获取围手术期相关论文信息信息

        :param db: orm对象
        :param paper: 围手术期相关论文信息参数对象
        :return: 围手术期相关论文信息信息对象
        """
        paper_info = (await db.execute(select(PmsPaper).where())).scalars().first()

        return paper_info

    @classmethod
    async def get_paper_list(
        cls, db: AsyncSession, query_object: PaperPageQueryModel, is_page: bool = False
    ):
        """
        根据查询参数获取围手术期相关论文信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 围手术期相关论文信息列表信息对象
        """
        query = (
            select(PmsPaper)
            .where(
                PmsPaper.pmid == query_object.pmid if query_object.pmid else True,
                PmsPaper.doi == query_object.doi if query_object.doi else True,
                PmsPaper.title == query_object.title if query_object.title else True,
                (
                    PmsPaper.abstract == query_object.abstract
                    if query_object.abstract
                    else True
                ),
                (
                    PmsPaper.abstract_id == query_object.abstract_id
                    if query_object.abstract_id
                    else True
                ),
                (
                    PmsPaper.journal_id == query_object.journal_id
                    if query_object.journal_id
                    else True
                ),
                PmsPaper.status == query_object.status if query_object.status else True,
                (
                    PmsPaper.received_date == query_object.received_date
                    if query_object.received_date
                    else True
                ),
                (
                    PmsPaper.accepted_date == query_object.accepted_date
                    if query_object.accepted_date
                    else True
                ),
                (
                    PmsPaper.published_date == query_object.published_date
                    if query_object.published_date
                    else True
                ),
            )
            .order_by(PmsPaper.paper_id)
            .distinct()
        )
        paper_list = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return paper_list

    @classmethod
    async def add_paper_dao(cls, db: AsyncSession, paper: PaperModel):
        """
        新增围手术期相关论文信息数据库操作

        :param db: orm对象
        :param paper: 围手术期相关论文信息对象
        :return: 新增的论文ID
        """
        db_paper = PmsPaper(**paper.model_dump(exclude={"author_ids", "keyword_ids"}))
        db.add(db_paper)
        await db.flush()

        return db_paper.paper_id

    @classmethod
    async def edit_paper_dao(cls, db: AsyncSession, paper: dict):
        """
        编辑围手术期相关论文信息数据库操作

        :param db: orm对象
        :param paper: 需要更新的围手术期相关论文信息字典
        :return:
        """
        await db.execute(update(PmsPaper), [paper])

    @classmethod
    async def delete_paper_dao(cls, db: AsyncSession, paper: PaperModel):
        """
        删除围手术期相关论文信息数据库操作

        :param db: orm对象
        :param paper: 围手术期相关论文信息对象
        :return:
        """
        await db.execute(
            delete(PmsPaper).where(PmsPaper.paper_id.in_([paper.paper_id]))
        )

    @classmethod
    async def get_journal_by_id(cls, db: AsyncSession, journal_id: int):
        """
        根据ID获取期刊信息

        :param db: orm对象
        :param journal_id: 期刊ID
        :return: 期刊信息对象
        """
        if not journal_id:
            return None

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
    async def get_abstract_structure_by_id(cls, db: AsyncSession, abstract_id: int):
        """
        根据ID获取摘要结构信息

        :param db: orm对象
        :param abstract_id: 摘要结构ID
        :return: 摘要结构信息对象
        """
        if not abstract_id:
            return None

        abstract_info = (
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

        return abstract_info

    @classmethod
    async def get_authors_by_paper_id(cls, db: AsyncSession, paper_id: int):
        """
        根据论文ID获取作者列表

        :param db: orm对象
        :param paper_id: 论文ID
        :return: 作者列表
        """
        authors = (
            (
                await db.execute(
                    select(PmsAuthor)
                    .join(
                        PmsPaperAuthor, PmsPaperAuthor.author_id == PmsAuthor.author_id
                    )
                    .where(PmsPaperAuthor.paper_id == paper_id)
                    .order_by(PmsPaperAuthor.author_order)
                )
            )
            .scalars()
            .all()
        )

        return authors

    @classmethod
    async def get_keywords_by_paper_id(cls, db: AsyncSession, paper_id: int):
        """
        根据论文ID获取关键词列表

        :param db: orm对象
        :param paper_id: 论文ID
        :return: 关键词列表
        """
        keywords = (
            (
                await db.execute(
                    select(PmsKeyword)
                    .join(
                        PmsPaperKeyword,
                        PmsPaperKeyword.keyword_id == PmsKeyword.keyword_id,
                    )
                    .where(PmsPaperKeyword.paper_id == paper_id)
                )
            )
            .scalars()
            .all()
        )

        return keywords

    @classmethod
    async def delete_paper_author_dao(cls, db: AsyncSession, paper_id: int):
        """
        删除论文作者关联关系

        :param db: orm对象
        :param paper_id: 论文ID
        :return:
        """
        await db.execute(
            delete(PmsPaperAuthor).where(PmsPaperAuthor.paper_id == paper_id)
        )

    @classmethod
    async def add_paper_author_dao(
        cls, db: AsyncSession, paper_id: int, author_id: int, author_order: int
    ):
        """
        添加论文作者关联关系

        :param db: orm对象
        :param paper_id: 论文ID
        :param author_id: 作者ID
        :param author_order: 作者顺序
        :return:
        """
        await db.execute(
            insert(PmsPaperAuthor).values(
                paper_id=paper_id, author_id=author_id, author_order=author_order
            )
        )

    @classmethod
    async def delete_paper_keyword_dao(cls, db: AsyncSession, paper_id: int):
        """
        删除论文关键词关联关系

        :param db: orm对象
        :param paper_id: 论文ID
        :return:
        """
        await db.execute(
            delete(PmsPaperKeyword).where(PmsPaperKeyword.paper_id == paper_id)
        )

    @classmethod
    async def add_paper_keyword_dao(
        cls, db: AsyncSession, paper_id: int, keyword_id: int
    ):
        """
        添加论文关键词关联关系

        :param db: orm对象
        :param paper_id: 论文ID
        :param keyword_id: 关键词ID
        :return:
        """
        await db.execute(
            insert(PmsPaperKeyword).values(paper_id=paper_id, keyword_id=keyword_id)
        )
