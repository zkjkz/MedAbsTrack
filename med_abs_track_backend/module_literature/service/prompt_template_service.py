from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.prompt_template_dao import Prompt_templateDao
from module_literature.entity.vo.prompt_template_vo import (
    DeletePrompt_templateModel,
    Prompt_templateModel,
    Prompt_templatePageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class Prompt_templateService:
    """
    Prompt模板模块服务层
    """

    @classmethod
    async def get_prompt_template_list_services(
        cls,
        query_db: AsyncSession,
        query_object: Prompt_templatePageQueryModel,
        is_page: bool = False,
    ):
        """
        获取Prompt模板列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: Prompt模板列表信息对象
        """
        prompt_template_list_result = await Prompt_templateDao.get_prompt_template_list(
            query_db, query_object, is_page
        )

        return prompt_template_list_result

    @classmethod
    async def add_prompt_template_services(
        cls, query_db: AsyncSession, page_object: Prompt_templateModel
    ):
        """
        新增Prompt模板信息service

        :param query_db: orm对象
        :param page_object: 新增Prompt模板对象
        :return: 新增Prompt模板校验结果
        """
        try:
            await Prompt_templateDao.add_prompt_template_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_prompt_template_services(
        cls, query_db: AsyncSession, page_object: Prompt_templateModel
    ):
        """
        编辑Prompt模板信息service

        :param query_db: orm对象
        :param page_object: 编辑Prompt模板对象
        :return: 编辑Prompt模板校验结果
        """
        edit_prompt_template = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        print(edit_prompt_template)
        prompt_template_info = await cls.prompt_template_detail_services(
            query_db, page_object.prompt_id
        )
        if prompt_template_info.prompt_id:
            try:
                await Prompt_templateDao.edit_prompt_template_dao(
                    query_db, edit_prompt_template
                )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="更新成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="Prompt模板不存在")

    @classmethod
    async def delete_prompt_template_services(
        cls, query_db: AsyncSession, page_object: DeletePrompt_templateModel
    ):
        """
        删除Prompt模板信息service

        :param query_db: orm对象
        :param page_object: 删除Prompt模板对象
        :return: 删除Prompt模板校验结果
        """
        if page_object.prompt_ids:
            prompt_id_list = page_object.prompt_ids.split(",")
            try:
                for prompt_id in prompt_id_list:
                    await Prompt_templateDao.delete_prompt_template_dao(
                        query_db, Prompt_templateModel(promptId=prompt_id)
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入为空")

    @classmethod
    async def prompt_template_detail_services(
        cls, query_db: AsyncSession, prompt_id: int
    ):
        """
        获取Prompt模板详细信息service

        :param query_db: orm对象
        :param prompt_id:
        :return: 对应的信息
        """
        prompt_template = await Prompt_templateDao.get_prompt_template_detail_by_id(
            query_db, prompt_id=prompt_id
        )
        if prompt_template:
            result = Prompt_templateModel(
                **CamelCaseUtil.transform_result(prompt_template)
            )
        else:
            result = Prompt_templateModel(**dict())

        return result

    @staticmethod
    async def export_prompt_template_list_services(prompt_template_list: List):
        """
        导出Prompt模板信息service

        :param prompt_template_list: Prompt模板信息列表
        :return: Prompt模板信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "promptId": "",
            "promptName": "Prompt名称",
            "description": "Prompt描述",
            "promptContent": "Prompt内容",
            "isActive": "是否启用",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(prompt_template_list, mapping_dict)

        return binary_data
