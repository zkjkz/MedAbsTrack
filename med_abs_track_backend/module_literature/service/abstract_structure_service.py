from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.vo.abstract_structure_vo import (
    AbstractStructureModel,
    AbstractStructurePageQueryModel,
    DeleteAbstractStructureModel,
)
from utils.log_util import logger
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.abstract_structure_dao import AbstractStructureDao
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class AbstractStructureService:
    """
    摘要结构模块服务层
    """

    @classmethod
    async def get_abstract_structure_list_services(
        cls,
        query_db: AsyncSession,
        query_object: AbstractStructurePageQueryModel,
        is_page: bool = False,
    ):
        """
        获取摘要结构列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 摘要结构列表信息对象
        """
        abstract_structure_list_result = (
            await AbstractStructureDao.get_abstract_structure_list(
                query_db, query_object, is_page
            )
        )

        return abstract_structure_list_result

    @classmethod
    async def add_abstract_structure_services(
        cls, query_db: AsyncSession, page_object: AbstractStructureModel
    ):
        """
        新增摘要结构信息service

        :param query_db: orm对象
        :param page_object: 新增摘要结构对象
        :return: 新增摘要结构校验结果
        """
        try:
            await AbstractStructureDao.add_abstract_structure_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_abstract_structure_services(
        cls, query_db: AsyncSession, page_object: AbstractStructureModel
    ):
        """
        编辑摘要结构信息service

        :param query_db: orm对象
        :param page_object: 编辑摘要结构对象
        :return: 编辑摘要结构校验结果
        """
        edit_abstract_structure = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        abstract_structure_info = await cls.abstract_structure_detail_services(
            query_db, page_object.abstract_id
        )
        if abstract_structure_info.abstract_id:
            try:
                await AbstractStructureDao.edit_abstract_structure_dao(
                    query_db, edit_abstract_structure
                )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="更新成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="摘要结构不存在")

    @classmethod
    async def delete_abstract_structure_services(
        cls, query_db: AsyncSession, page_object: DeleteAbstractStructureModel
    ):
        """
        删除摘要结构信息service

        :param query_db: orm对象
        :param page_object: 删除摘要结构对象
        :return: 删除摘要结构校验结果
        """
        if page_object.abstractIds:
            abstract_id_list = page_object.abstractIds.split(",")

            # 检查是否有论文引用了这些摘要结构
            referenced_papers = (
                await AbstractStructureDao.check_abstract_structure_referenced(
                    query_db, abstract_id_list
                )
            )

            if referenced_papers:
                paper_ids = [str(paper.paper_id) for paper in referenced_papers]
                return CrudResponseModel(
                    is_success=False,
                    message=f"以下论文ID引用了要删除的摘要结构，无法删除: {', '.join(paper_ids)}",
                )

            try:
                for abstract_id in abstract_id_list:
                    await AbstractStructureDao.delete_abstract_structure_dao(
                        query_db, AbstractStructureModel(abstract_id=int(abstract_id))
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入为空")

    @classmethod
    async def abstract_structure_detail_services(
        cls, query_db: AsyncSession, abstract_id: int
    ):
        """
        获取摘要结构详细信息service

        :param query_db: orm对象
        :param abstract_id: 摘要结构ID
        :return: 对应的信息
        """
        abstract_structure = (
            await AbstractStructureDao.get_abstract_structure_detail_by_id(
                query_db, abstract_id=abstract_id
            )
        )
        if abstract_structure:
            result = AbstractStructureModel(
                **CamelCaseUtil.transform_result(abstract_structure)
            )
        else:
            result = AbstractStructureModel(**dict())

        return result

    @classmethod
    async def export_abstract_structure_list_services(
        cls, abstract_structure_list: List
    ):
        """
        导出摘要结构信息service

        :param abstract_structure_list: 摘要结构信息列表
        :return: 摘要结构信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "abstractId": "摘要结构ID",
            "background": "背景部分",
            "methods": "方法部分",
            "results": "结果部分",
            "conclusion": "结论部分",
            "extractionDate": "抽取日期",
            "status": "状态",
            "isExtracted": "是否成功抽取",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }

        # 处理一下导出数据，限制长文本内容
        processed_list = []
        for item in abstract_structure_list.rows:
            item_dict = item.dict()
            for field in ["background", "methods", "results", "conclusion"]:
                if item_dict.get(field) and len(item_dict[field]) > 100:
                    item_dict[field] = item_dict[field][:100] + "..."

            # 处理状态显示
            item_dict["status"] = "正常" if item_dict.get("status") == "0" else "异常"
            item_dict["isExtracted"] = "是" if item_dict.get("isExtracted") else "否"

            processed_list.append(item_dict)

        binary_data = ExcelUtil.export_list2excel(processed_list, mapping_dict)

        return binary_data

    @classmethod
    async def get_abstract_structure_by_paper_id_services(
        cls, query_db: AsyncSession, paper_id: int
    ) -> AbstractStructureModel:
        """
        根据论文ID获取摘要抽取数据service

        :param query_db: orm对象
        :param paper_id: 论文ID
        :return: 摘要结构信息
        """
        try:
            # 获取论文关联的摘要结构
            abstract_structure = (
                await AbstractStructureDao.get_abstract_structure_by_paper_id(
                    query_db, paper_id
                )
            )

            if not abstract_structure:
                raise ServiceException(
                    message=f"论文ID {paper_id} 不存在或没有关联的摘要结构"
                )

            return AbstractStructureModel(
                **CamelCaseUtil.transform_result(abstract_structure)
            )
        except Exception as e:
            logger.error(f"根据论文ID获取摘要结构失败: {str(e)}")
            raise ServiceException(message=f"根据论文ID获取摘要结构失败: {str(e)}")
