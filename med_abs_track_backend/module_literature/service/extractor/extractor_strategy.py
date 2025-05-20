from abc import ABC, abstractmethod
from typing import Dict, Optional

from module_literature.entity.do.extraction_method_do import ExtractionMethodType
from module_literature.entity.vo.paper_vo import AbstractStructureModel, PaperModel


class AbstractExtractor(ABC):
    """
    抽取器抽象策略接口
    """

    @abstractmethod
    async def extract(
        self, paper: PaperModel, execution_parameters: Optional[Dict] = None
    ) -> AbstractStructureModel:
        """
        执行抽取操作

        :param paper: 论文信息模型
        :param execution_parameters: 执行参数
        :return: 抽取结果
        """
        pass


class ExtractorFactory:
    """
    抽取器工厂类
    """

    _extractors = {}

    @classmethod
    def register(cls, extractor_type: str, extractor_class):
        """
        注册抽取器

        :param extractor_type: 抽取器类型
        :param extractor_class: 抽取器类
        """
        cls._extractors[extractor_type] = extractor_class

    @classmethod
    def get_extractor(cls, extractor_type: ExtractionMethodType) -> AbstractExtractor:
        """
        获取抽取器

        :param extractor_type: 抽取器类型
        :return: 抽取器实例
        """
        extractor_class = cls._extractors.get(extractor_type)
        if not extractor_class:
            raise ValueError(f"不支持的抽取器类型: {extractor_type}")
        return extractor_class()
