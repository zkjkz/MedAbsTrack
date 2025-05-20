from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_literature.dao.extraction_method_dao import Extraction_methodDao
from module_literature.entity.vo.extraction_method_vo import DeleteExtraction_methodModel, Extraction_methodModel, Extraction_methodPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class Extraction_methodService:
    """
    抽取方法配置模块服务层
    """

    @classmethod
    async def get_extraction_method_list_services(
        cls, query_db: AsyncSession, query_object: Extraction_methodPageQueryModel, is_page: bool = False
    ):
        """
        获取抽取方法配置列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 抽取方法配置列表信息对象
        """
        extraction_method_list_result = await Extraction_methodDao.get_extraction_method_list(query_db, query_object, is_page)

        return extraction_method_list_result


    @classmethod
    async def add_extraction_method_services(cls, query_db: AsyncSession, page_object: Extraction_methodModel):
        """
        新增抽取方法配置信息service

        :param query_db: orm对象
        :param page_object: 新增抽取方法配置对象
        :return: 新增抽取方法配置校验结果
        """
        try:
            await Extraction_methodDao.add_extraction_method_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_extraction_method_services(cls, query_db: AsyncSession, page_object: Extraction_methodModel):
        """
        编辑抽取方法配置信息service

        :param query_db: orm对象
        :param page_object: 编辑抽取方法配置对象
        :return: 编辑抽取方法配置校验结果
        """
        edit_extraction_method = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        extraction_method_info = await cls.extraction_method_detail_services(query_db, page_object.method_id)
        if extraction_method_info.method_id:
            try:
                await Extraction_methodDao.edit_extraction_method_dao(query_db, edit_extraction_method)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='抽取方法配置不存在')

    @classmethod
    async def delete_extraction_method_services(cls, query_db: AsyncSession, page_object: DeleteExtraction_methodModel):
        """
        删除抽取方法配置信息service

        :param query_db: orm对象
        :param page_object: 删除抽取方法配置对象
        :return: 删除抽取方法配置校验结果
        """
        if page_object.method_ids:
            method_id_list = page_object.method_ids.split(',')
            try:
                for method_id in method_id_list:
                    await Extraction_methodDao.delete_extraction_method_dao(query_db, Extraction_methodModel(methodId=method_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入为空')

    @classmethod
    async def extraction_method_detail_services(cls, query_db: AsyncSession, method_id: int):
        """
        获取抽取方法配置详细信息service

        :param query_db: orm对象
        :param method_id: 
        :return: 对应的信息
        """
        extraction_method = await Extraction_methodDao.get_extraction_method_detail_by_id(query_db, method_id=method_id)
        if extraction_method:
            result = Extraction_methodModel(**CamelCaseUtil.transform_result(extraction_method))
        else:
            result = Extraction_methodModel(**dict())

        return result

    @staticmethod
    async def export_extraction_method_list_services(extraction_method_list: List):
        """
        导出抽取方法配置信息service

        :param extraction_method_list: 抽取方法配置信息列表
        :return: 抽取方法配置信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'methodId': '',
            'methodName': '抽取方法名称',
            'methodType': '抽取方法类型: regex, llm, rule, ml或其他未来方法',
            'description': '方法描述',
            'configParams': '配置参数',
            'templateId': '抽取模板ID，用于regex/rule方法',
            'modelId': '大语言模型ID，用于llm方法',
            'promptId': 'Prompt模板ID，用于llm方法',
            'status': '状态',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }
        binary_data = ExcelUtil.export_list2excel(extraction_method_list, mapping_dict)

        return binary_data
