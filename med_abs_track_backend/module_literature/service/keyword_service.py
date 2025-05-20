from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from module_literature.dao.keyword_dao import KeywordDao
from module_literature.entity.vo.paper_vo import KeywordModel
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.excel_util import ExcelUtil


class KeywordService:
    """
    关键词模块服务层
    """

    @classmethod
    async def get_keyword_list_services(cls, query_db: AsyncSession):
        """
        获取关键词列表信息service

        :param query_db: orm对象
        :return: 关键词列表信息对象
        """
        keyword_list = await cls.get_all_keywords(query_db)
        return [KeywordModel.model_validate(keyword) for keyword in keyword_list]

    @classmethod
    async def get_all_keywords(cls, query_db: AsyncSession):
        """
        获取所有关键词信息

        :param query_db: orm对象
        :return: 关键词列表
        """
        from sqlalchemy import select
        from module_literature.entity.do.keyword_do import PmsKeyword

        keywords = (
            (
                await query_db.execute(
                    select(PmsKeyword).order_by(PmsKeyword.keyword_id.desc())
                )
            )
            .scalars()
            .all()
        )

        return keywords

    @classmethod
    async def get_keyword_detail_services(cls, db: AsyncSession, keyword_id: int):
        """
        获取关键词详情服务

        :param db: orm对象
        :param keyword_id: 关键词ID
        :return: 关键词详情
        """
        keyword = await KeywordDao.get_keyword_detail_by_id(db, keyword_id)
        if not keyword:
            return None
        return KeywordModel.model_validate(keyword)

    @classmethod
    async def add_keyword_services(
        cls, query_db: AsyncSession, page_object: KeywordModel
    ):
        """
        新增关键词信息service

        :param query_db: orm对象
        :param page_object: 新增关键词对象
        :return: 新增关键词校验结果
        """
        try:
            # 检查关键词是否已存在
            existing_keyword = await KeywordDao.get_keyword_by_text(
                query_db, page_object.keyword
            )
            if existing_keyword:
                return CrudResponseModel(
                    is_success=True,
                    message=f"关键词 {page_object.keyword} 已存在",
                    result={"keyword_id": existing_keyword.keyword_id},
                )

            keyword_dict = page_object.model_dump()
            keyword_id = await KeywordDao.add_keyword_dao(query_db, keyword_dict)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f"添加关键词 {page_object.keyword} 成功",
                result={"keyword_id": keyword_id},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_keyword_services(
        cls, query_db: AsyncSession, page_object: KeywordModel
    ):
        """
        编辑关键词信息service

        :param query_db: orm对象
        :param page_object: 编辑关键词对象
        :return: 编辑关键词校验结果
        """
        edit_keyword = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        keyword_info = await cls.keyword_detail_services(
            query_db, page_object.keyword_id
        )
        if keyword_info.keyword_id:
            try:
                # 检查修改后的文本是否与其他关键词冲突
                if keyword_info.keyword != page_object.keyword:
                    check_keyword = await KeywordDao.get_keyword_by_text(
                        query_db, page_object.keyword
                    )
                    if (
                        check_keyword
                        and check_keyword.keyword_id != page_object.keyword_id
                    ):
                        raise ServiceException(
                            message=f"关键词 {page_object.keyword} 已存在"
                        )

                await cls.update_keyword(query_db, page_object)
                await query_db.commit()
                return CrudResponseModel(
                    is_success=True, message=f"修改关键词 {page_object.keyword} 成功"
                )
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="关键词不存在")

    @classmethod
    async def update_keyword(cls, query_db: AsyncSession, keyword: KeywordModel):
        """
        更新关键词信息

        :param query_db: orm对象
        :param keyword: 关键词对象
        """
        from sqlalchemy import update
        from module_literature.entity.do.keyword_do import PmsKeyword

        keyword_dict = keyword.model_dump(exclude={"keyword_id"})
        await query_db.execute(
            update(PmsKeyword)
            .where(PmsKeyword.keyword_id == keyword.keyword_id)
            .values(**keyword_dict)
        )

    @classmethod
    async def delete_keyword_services(
        cls, query_db: AsyncSession, keyword_ids: List[int]
    ):
        """
        删除关键词信息service

        :param query_db: orm对象
        :param keyword_ids: 关键词ID列表
        :return: 删除关键词校验结果
        """
        if keyword_ids:
            try:
                await cls.delete_keywords(query_db, keyword_ids)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除关键词成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入ID为空")

    @classmethod
    async def delete_keywords(cls, query_db: AsyncSession, keyword_ids: List[int]):
        """
        删除关键词信息

        :param query_db: orm对象
        :param keyword_ids: 关键词ID列表
        """
        from sqlalchemy import delete
        from module_literature.entity.do.keyword_do import PmsKeyword

        await query_db.execute(
            delete(PmsKeyword).where(PmsKeyword.keyword_id.in_(keyword_ids))
        )

    @classmethod
    async def keyword_detail_services(cls, query_db: AsyncSession, keyword_id: int):
        """
        获取关键词详细信息service

        :param query_db: orm对象
        :param keyword_id: 关键词ID
        :return: 对应的信息
        """
        keyword = await KeywordDao.get_keyword_detail_by_id(
            query_db, keyword_id=keyword_id
        )
        if keyword:
            result = KeywordModel.model_validate(keyword)
        else:
            result = KeywordModel(**dict())

        return result

    @staticmethod
    async def export_keyword_list_services(keyword_list: List):
        """
        导出关键词信息service

        :param keyword_list: 关键词信息列表
        :return: 关键词信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "keywordId": "关键词ID",
            "keyword": "关键词文本",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(keyword_list, mapping_dict)

        return binary_data
