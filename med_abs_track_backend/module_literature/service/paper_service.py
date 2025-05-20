from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.paper_dao import PaperDao
from module_literature.entity.vo.paper_vo import (
    DeletePaperModel,
    PaperModel,
    PaperDetailModel,
    PaperPageQueryModel,
    CrudPaperAuthorModel,
    CrudPaperKeywordModel,
    PaperAuthorResponseModel,
    PaperKeywordResponseModel,
)
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class PaperService:
    """
    围手术期相关论文信息模块服务层
    """

    @classmethod
    async def get_paper_list_services(
        cls,
        query_db: AsyncSession,
        query_object: PaperPageQueryModel,
        is_page: bool = False,
    ):
        """
        获取围手术期相关论文信息列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 围手术期相关论文信息列表信息对象
        """
        paper_list_result = await PaperDao.get_paper_list(
            query_db, query_object, is_page
        )

        return paper_list_result

    @classmethod
    async def add_paper_services(cls, query_db: AsyncSession, page_object: PaperModel):
        """
        新增围手术期相关论文信息信息service

        :param query_db: orm对象
        :param page_object: 新增围手术期相关论文信息对象
        :return: 新增围手术期相关论文信息校验结果
        """
        try:
            # 添加论文基本信息
            paper_id = await PaperDao.add_paper_dao(query_db, page_object)

            # 处理作者关联
            if page_object.author_ids:
                author_ids_str = ",".join([str(id) for id in page_object.author_ids])
                await cls.add_paper_author_services(
                    query_db,
                    CrudPaperAuthorModel(
                        paperId=paper_id,
                        authorIds=author_ids_str,
                        updateBy=page_object.create_by,
                    ),
                )

            # 处理关键词关联
            if page_object.keyword_ids:
                keyword_ids_str = ",".join([str(id) for id in page_object.keyword_ids])
                await cls.add_paper_keyword_services(
                    query_db,
                    CrudPaperKeywordModel(
                        paperId=paper_id,
                        keywordIds=keyword_ids_str,
                        updateBy=page_object.create_by,
                    ),
                )

            await query_db.commit()
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_paper_services(cls, query_db: AsyncSession, page_object: PaperModel):
        """
        编辑围手术期相关论文信息信息service

        :param query_db: orm对象
        :param page_object: 编辑围手术期相关论文信息对象
        :return: 编辑围手术期相关论文信息校验结果
        """
        edit_paper = page_object.model_dump(
            exclude_unset=True,
            exclude={"create_by", "create_time", "author_ids", "keyword_ids"},
        )
        paper_info = await cls.paper_detail_services(query_db, page_object.paper_id)
        if paper_info.paper_id:
            try:
                # 更新论文基本信息
                await PaperDao.edit_paper_dao(query_db, edit_paper)

                # 处理作者关联
                if page_object.author_ids is not None:
                    author_ids_str = ",".join(
                        [str(id) for id in page_object.author_ids]
                    )
                    await cls.add_paper_author_services(
                        query_db,
                        CrudPaperAuthorModel(
                            paperId=page_object.paper_id,
                            authorIds=author_ids_str,
                            updateBy=page_object.update_by,
                        ),
                    )

                # 处理关键词关联
                if page_object.keyword_ids is not None:
                    keyword_ids_str = ",".join(
                        [str(id) for id in page_object.keyword_ids]
                    )
                    await cls.add_paper_keyword_services(
                        query_db,
                        CrudPaperKeywordModel(
                            paperId=page_object.paper_id,
                            keywordIds=keyword_ids_str,
                            updateBy=page_object.update_by,
                        ),
                    )

                await query_db.commit()
                return CrudResponseModel(is_success=True, message="更新成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="围手术期相关论文信息不存在")

    @classmethod
    async def delete_paper_services(
        cls, query_db: AsyncSession, page_object: DeletePaperModel
    ):
        """
        删除围手术期相关论文信息信息service

        :param query_db: orm对象
        :param page_object: 删除围手术期相关论文信息对象
        :return: 删除围手术期相关论文信息校验结果
        """
        if page_object.paper_ids:
            paper_id_list = page_object.paper_ids.split(",")
            try:
                for paper_id in paper_id_list:
                    # 删除论文时，关联表数据会通过外键约束级联删除
                    await PaperDao.delete_paper_dao(
                        query_db, PaperModel(paperId=paper_id)
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入为空")

    @classmethod
    async def paper_detail_services(cls, query_db: AsyncSession, paper_id: int):
        """
        获取围手术期相关论文信息详细信息service

        :param query_db: orm对象
        :param paper_id:
        :return: 对应的信息
        """
        # 获取论文基本信息
        paper_detail = await PaperDao.get_paper_detail_by_id(
            query_db, paper_id=paper_id
        )
        if not paper_detail:
            return PaperModel(**dict())

        # 获取关联信息
        journal = await PaperDao.get_journal_by_id(query_db, paper_detail.journal_id)
        abstract_structure = await PaperDao.get_abstract_structure_by_id(
            query_db, paper_detail.abstract_id
        )
        authors = await PaperDao.get_authors_by_paper_id(query_db, paper_id)
        keywords = await PaperDao.get_keywords_by_paper_id(query_db, paper_id)

        # 构建完整的响应结果
        result_data = {
            **CamelCaseUtil.transform_result(paper_detail),
            "journal": CamelCaseUtil.transform_result(journal) if journal else None,
            "abstractStructure": (
                CamelCaseUtil.transform_result(abstract_structure)
                if abstract_structure
                else None
            ),
            "authors": CamelCaseUtil.transform_result(authors) if authors else [],
            "keywords": CamelCaseUtil.transform_result(keywords) if keywords else [],
        }

        result = PaperDetailModel(**result_data)
        return result

    @staticmethod
    async def export_paper_list_services(paper_list: List):
        """
        导出围手术期相关论文信息信息service

        :param paper_list: 围手术期相关论文信息信息列表
        :return: 围手术期相关论文信息信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "paperId": "",
            "pmid": "PubMed ID",
            "doi": "数字对象标识符",
            "title": "论文标题",
            "abstract": "论文摘要",
            "abstractId": "摘要结构ID",
            "journalId": "期刊ID",
            "publishStatus": "发表状态",
            "receivedDate": "收稿日期",
            "acceptedDate": "接受日期",
            "publishedDate": "发表日期",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(paper_list, mapping_dict)

        return binary_data

    @classmethod
    async def get_paper_author_allocated_list_services(
        cls, query_db: AsyncSession, paper_id: int
    ):
        """
        获取论文已分配的作者列表service

        :param query_db: orm对象
        :param paper_id: 论文ID
        :return: 论文作者分配响应模型
        """
        # 获取论文信息
        paper = await PaperDao.get_paper_detail_by_id(query_db, paper_id)
        if not paper:
            raise ServiceException(message="论文不存在")

        # 获取作者列表
        authors = await PaperDao.get_authors_by_paper_id(query_db, paper_id)

        # 构建响应模型
        result = PaperAuthorResponseModel(
            paper=PaperModel(**CamelCaseUtil.transform_result(paper)),
            authors=CamelCaseUtil.transform_result(authors) if authors else [],
        )

        return result

    @classmethod
    async def add_paper_author_services(
        cls, query_db: AsyncSession, paper_author: CrudPaperAuthorModel
    ):
        """
        添加/更新论文作者关联关系service

        :param query_db: orm对象
        :param paper_author: 论文作者关联模型
        :return: 添加结果
        """
        try:
            # 先删除原有关联
            await PaperDao.delete_paper_author_dao(query_db, paper_author.paper_id)

            # 如果有新的作者ID，则添加新关联
            if paper_author.author_ids:
                author_id_list = paper_author.author_ids.split(",")
                for index, author_id in enumerate(author_id_list):
                    # 使用索引作为作者顺序
                    await PaperDao.add_paper_author_dao(
                        query_db, paper_author.paper_id, int(author_id), index + 1
                    )

            return CrudResponseModel(is_success=True, message="分配作者成功")
        except Exception as e:
            raise ServiceException(message=f"分配作者失败: {str(e)}")

    @classmethod
    async def get_paper_keyword_allocated_list_services(
        cls, query_db: AsyncSession, paper_id: int
    ):
        """
        获取论文已分配的关键词列表service

        :param query_db: orm对象
        :param paper_id: 论文ID
        :return: 论文关键词分配响应模型
        """
        # 获取论文信息
        paper = await PaperDao.get_paper_detail_by_id(query_db, paper_id)
        if not paper:
            raise ServiceException(message="论文不存在")

        # 获取关键词列表
        keywords = await PaperDao.get_keywords_by_paper_id(query_db, paper_id)

        # 构建响应模型
        result = PaperKeywordResponseModel(
            paper=PaperModel(**CamelCaseUtil.transform_result(paper)),
            keywords=CamelCaseUtil.transform_result(keywords) if keywords else [],
        )

        return result

    @classmethod
    async def add_paper_keyword_services(
        cls, query_db: AsyncSession, paper_keyword: CrudPaperKeywordModel
    ):
        """
        添加/更新论文关键词关联关系service

        :param query_db: orm对象
        :param paper_keyword: 论文关键词关联模型
        :return: 添加结果
        """
        try:
            # 先删除原有关联
            await PaperDao.delete_paper_keyword_dao(query_db, paper_keyword.paper_id)

            # 如果有新的关键词ID，则添加新关联
            if paper_keyword.keyword_ids:
                keyword_id_list = paper_keyword.keyword_ids.split(",")
                for keyword_id in keyword_id_list:
                    await PaperDao.add_paper_keyword_dao(
                        query_db, paper_keyword.paper_id, int(keyword_id)
                    )

            return CrudResponseModel(is_success=True, message="分配关键词成功")
        except Exception as e:
            raise ServiceException(message=f"分配关键词失败: {str(e)}")
