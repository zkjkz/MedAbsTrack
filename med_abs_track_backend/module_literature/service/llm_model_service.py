from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.llm_model_dao import Llm_modelDao
from module_literature.entity.vo.llm_model_vo import (
    DeleteLlm_modelModel,
    Llm_modelModel,
    Llm_modelPageQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class Llm_modelService:
    """
    大语言模型基座模块服务层
    """

    @classmethod
    async def get_llm_model_list_services(
        cls,
        query_db: AsyncSession,
        query_object: Llm_modelPageQueryModel,
        is_page: bool = False,
    ):
        """
        获取大语言模型基座列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 大语言模型基座列表信息对象
        """
        llm_model_list_result = await Llm_modelDao.get_llm_model_list(
            query_db, query_object, is_page
        )

        return llm_model_list_result

    @classmethod
    async def add_llm_model_services(
        cls, query_db: AsyncSession, page_object: Llm_modelModel
    ):
        """
        新增大语言模型基座信息service

        :param query_db: orm对象
        :param page_object: 新增大语言模型基座对象
        :return: 新增大语言模型基座校验结果
        """
        try:
            await Llm_modelDao.add_llm_model_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_llm_model_services(
        cls, query_db: AsyncSession, page_object: Llm_modelModel
    ):
        """
        编辑大语言模型基座信息service

        :param query_db: orm对象
        :param page_object: 编辑大语言模型基座对象
        :return: 编辑大语言模型基座校验结果
        """
        edit_llm_model = page_object.model_dump(
            exclude_unset=True,
            exclude={
                "create_by",
                "create_time",
            },
        )
        llm_model_info = await cls.llm_model_detail_services(
            query_db, page_object.model_id
        )
        if llm_model_info.model_id:
            try:
                await Llm_modelDao.edit_llm_model_dao(query_db, edit_llm_model)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="更新成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="大语言模型基座不存在")

    @classmethod
    async def delete_llm_model_services(
        cls, query_db: AsyncSession, page_object: DeleteLlm_modelModel
    ):
        """
        删除大语言模型基座信息service

        :param query_db: orm对象
        :param page_object: 删除大语言模型基座对象
        :return: 删除大语言模型基座校验结果
        """
        if page_object.model_ids:
            model_id_list = page_object.model_ids.split(",")
            try:
                for model_id in model_id_list:
                    await Llm_modelDao.delete_llm_model_dao(
                        query_db, Llm_modelModel(modelId=model_id)
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message="传入为空")

    @classmethod
    async def llm_model_detail_services(cls, query_db: AsyncSession, model_id: int):
        """
        获取大语言模型基座详细信息service

        :param query_db: orm对象
        :param model_id:
        :return: 对应的信息
        """
        llm_model = await Llm_modelDao.get_llm_model_detail_by_id(
            query_db, model_id=model_id
        )
        if llm_model:
            result = Llm_modelModel(**CamelCaseUtil.transform_result(llm_model))
        else:
            result = Llm_modelModel(**dict())

        return result

    @staticmethod
    async def export_llm_model_list_services(llm_model_list: List):
        """
        导出大语言模型基座信息service

        :param llm_model_list: 大语言模型基座信息列表
        :return: 大语言模型基座信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            "modelId": "",
            "displayName": "显示名称",
            "modelName": "OpenAI模型名称",
            "modelVersion": "模型版本",
            "provider": "模型提供商",
            "baseUrl": "API基础URL",
            "apiKey": "API密钥",
            "organizationId": "组织ID",
            "defaultParameters": "默认参数配置",
            "contextLength": "上下文长度限制",
            "requestTimeout": "请求超时时间(秒)",
            "status": "状态",
            "createBy": "创建者",
            "createTime": "创建时间",
            "updateBy": "更新者",
            "updateTime": "更新时间",
            "remark": "备注",
        }
        binary_data = ExcelUtil.export_list2excel(llm_model_list, mapping_dict)

        return binary_data
