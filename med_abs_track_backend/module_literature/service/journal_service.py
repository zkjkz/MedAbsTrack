from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from module_literature.dao.journal_dao import JournalDao
from module_literature.entity.vo.paper_vo import JournalModel
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.excel_util import ExcelUtil


class JournalService:
    """
    期刊服务层
    """

    @classmethod
    async def get_journal_list_services(cls, query_db: AsyncSession):
        """
        获取期刊列表信息service

        :param query_db: orm对象
        :return: 期刊列表信息对象
        """
        journal_list = await cls.get_all_journals(query_db)
        return [JournalModel.model_validate(journal) for journal in journal_list]

    @classmethod
    async def get_all_journals(cls, query_db: AsyncSession):
        """
        获取所有期刊信息

        :param query_db: orm对象
        :return: 期刊列表
        """
        from sqlalchemy import select
        from module_literature.entity.do.journal_do import PmsJournal

        journals = (
            (
                await query_db.execute(
                    select(PmsJournal).order_by(PmsJournal.journal_id.desc())
                )
            )
            .scalars()
            .all()
        )

        return journals

    @classmethod
    async def get_journal_detail_services(cls, db: AsyncSession, journal_id: int):
        """
        获取期刊详情服务

        :param db: orm对象
        :param journal_id: 期刊ID
        :return: 期刊详情
        """
        journal = await JournalDao.get_journal_detail_by_id(db, journal_id)
        if not journal:
            return None
        return JournalModel.model_validate(journal)

    @classmethod
    async def add_journal_services(
        cls, query_db: AsyncSession, page_object: JournalModel
    ):
        """
        新增期刊信息service

        :param query_db: orm对象
        :param page_object: 新增期刊对象
        :return: 新增期刊校验结果
        """
        try:
            # 检查期刊是否已存在
            existing_journal = await JournalDao.get_journal_by_name(
                query_db, page_object.journal_name
            )
            if existing_journal:
                return CrudResponseModel(
                    is_success=True,
                    message=f"期刊 {page_object.journal_name} 已存在",
                    result={"journal_id": existing_journal.journal_id},
                )

            journal_dict = page_object.model_dump()
            journal_id = await JournalDao.add_journal_dao(query_db, journal_dict)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f"添加期刊 {page_object.journal_name} 成功",
                result={"journal_id": journal_id},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_journal_services(
        cls, query_db: AsyncSession, page_object: JournalModel
    ):
        """
        编辑期刊信息service

        :param query_db: orm对象
        :param page_object: 编辑期刊对象
        :return: 编辑期刊校验结果
        """
        edit_journal = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        journal_info = await cls.journal_detail_services(
            query_db, page_object.journal_id
        )
        if journal_info.journal_id:
            try:
                # 检查修改后的名称是否与其他期刊冲突
                if journal_info.journal_name != page_object.journal_name:
                    check_journal = await JournalDao.get_journal_by_name(
                        query_db, page_object.journal_name
                    )
                    if (
                        check_journal
                        and check_journal.journal_id != page_object.journal_id
                    ):
                        raise ServiceException(
                            message=f"期刊 {page_object.journal_name} 已存在"
                        )

                await cls.update_journal(query_db, page_object)
                await query_db.commit()
                return CrudResponseModel(
                    is_success=True, message=f"修改期刊 {page_object.journal_name} 成功"
                )
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="期刊不存在")

    @classmethod
    async def update_journal(cls, query_db: AsyncSession, journal: JournalModel):
        """
        更新期刊信息

        :param query_db: orm对象
        :param journal: 期刊对象
        """
        from sqlalchemy import update
        from module_literature.entity.do.journal_do import PmsJournal

        journal_dict = journal.model_dump(exclude={"journal_id"})
        await query_db.execute(
            update(PmsJournal)
            .where(PmsJournal.journal_id == journal.journal_id)
            .values(**journal_dict)
        )

    @classmethod
    async def delete_journal_services(
        cls, query_db: AsyncSession, journal_ids: List[int]
    ):
        """
        删除期刊信息service

        :param query_db: orm对象
        :param journal_ids: 期刊ID列表
        :return: 删除期刊校验结果
        """
        if journal_ids:
            try:
                await cls.delete_journals(query_db, journal_ids)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除期刊成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入ID为空")

    @classmethod
    async def delete_journals(cls, query_db: AsyncSession, journal_ids: List[int]):
        """
        删除期刊信息

        :param query_db: orm对象
        :param journal_ids: 期刊ID列表
        """
        from sqlalchemy import delete
        from module_literature.entity.do.journal_do import PmsJournal

        await query_db.execute(
            delete(PmsJournal).where(PmsJournal.journal_id.in_(journal_ids))
        )

    @classmethod
    async def journal_detail_services(cls, query_db: AsyncSession, journal_id: int):
        """
        获取期刊详细信息service

        :param query_db: orm对象
        :param journal_id: 期刊ID
        :return: 对应的信息
        """
        journal = await JournalDao.get_journal_detail_by_id(
            query_db, journal_id=journal_id
        )
        if journal:
            result = JournalModel.model_validate(journal)
        else:
            result = JournalModel(**dict())

        return result

    @staticmethod
    async def export_journal_list_services(journal_list: List):
        """
        导出期刊信息service

        :param journal_list: 期刊信息列表
        :return: 期刊信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "journalId": "期刊ID",
            "journalName": "期刊名称",
            "country": "所属国家",
            "issn": "ISSN号",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(journal_list, mapping_dict)

        return binary_data
