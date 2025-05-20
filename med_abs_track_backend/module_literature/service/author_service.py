from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from module_literature.dao.author_dao import AuthorDao
from module_literature.entity.vo.paper_vo import AuthorModel
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.excel_util import ExcelUtil


class AuthorService:
    """
    作者模块服务层
    """

    @classmethod
    async def get_author_list_services(cls, query_db: AsyncSession):
        """
        获取作者列表信息service

        :param query_db: orm对象
        :return: 作者列表信息对象
        """
        author_list = await AuthorDao.get_author_list(query_db)
        return [AuthorModel.model_validate(author) for author in author_list]

    @classmethod
    async def get_author_detail_services(cls, db: AsyncSession, author_id: int):
        """
        获取作者详情服务

        :param db: orm对象
        :param author_id: 作者ID
        :return: 作者详情
        """
        author = await AuthorDao.get_author_detail_by_id(db, author_id)
        if not author:
            return None
        return AuthorModel.model_validate(author)

    @classmethod
    async def add_author_services(
        cls, query_db: AsyncSession, page_object: AuthorModel
    ):
        """
        新增作者信息service

        :param query_db: orm对象
        :param page_object: 新增作者对象
        :return: 新增作者校验结果
        """
        try:
            # 检查作者是否已存在
            existing_author = await AuthorDao.get_author_by_name(
                query_db, page_object.name, page_object.affiliation
            )
            if existing_author:
                return CrudResponseModel(
                    is_success=True,
                    message=f"作者 {page_object.name} 已存在",
                    result={"author_id": existing_author.author_id},
                )

            author_dict = page_object.model_dump()
            author_id = await AuthorDao.add_author_dao(query_db, author_dict)
            await query_db.commit()
            return CrudResponseModel(
                is_success=True,
                message=f"添加作者 {page_object.name} 成功",
                result={"author_id": author_id},
            )
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_author_services(
        cls, query_db: AsyncSession, page_object: AuthorModel
    ):
        """
        编辑作者信息service

        :param query_db: orm对象
        :param page_object: 编辑作者对象
        :return: 编辑作者校验结果
        """
        edit_author = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        author_info = await cls.author_detail_services(query_db, page_object.author_id)
        if author_info.author_id:
            try:
                # 检查修改后的名称是否与其他作者冲突
                if (
                    author_info.name != page_object.name
                    or author_info.affiliation != page_object.affiliation
                ):
                    check_author = await AuthorDao.get_author_by_name(
                        query_db, page_object.name, page_object.affiliation
                    )
                    if check_author and check_author.author_id != page_object.author_id:
                        raise ServiceException(
                            message=f"作者 {page_object.name} 已存在"
                        )

                await AuthorDao.edit_author_dao(
                    query_db, {"author_id": page_object.author_id, **edit_author}
                )
                await query_db.commit()
                return CrudResponseModel(
                    is_success=True, message=f"修改作者 {page_object.name} 成功"
                )
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="作者不存在")

    @classmethod
    async def delete_author_services(
        cls, query_db: AsyncSession, author_ids: List[int]
    ):
        """
        删除作者信息service

        :param query_db: orm对象
        :param author_ids: 作者ID列表
        :return: 删除作者校验结果
        """
        if author_ids:
            try:
                await AuthorDao.delete_author_dao(query_db, author_ids)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除作者成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入ID为空")

    @classmethod
    async def author_detail_services(cls, query_db: AsyncSession, author_id: int):
        """
        获取作者详细信息service

        :param query_db: orm对象
        :param author_id: 作者ID
        :return: 对应的信息
        """
        author = await AuthorDao.get_author_detail_by_id(query_db, author_id=author_id)
        if author:
            result = AuthorModel.model_validate(author)
        else:
            result = AuthorModel(**dict())

        return result

    @staticmethod
    async def export_author_list_services(author_list: List):
        """
        导出作者信息service

        :param author_list: 作者信息列表
        :return: 作者信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "authorId": "作者ID",
            "name": "作者姓名",
            "affiliation": "所属机构",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(author_list, mapping_dict)

        return binary_data
