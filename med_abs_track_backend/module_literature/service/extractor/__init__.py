"""
抽取器模块初始化文件
用于确保所有抽取器实现都被正确导入和注册
"""

# 导入策略接口
from module_literature.service.extractor.extractor_strategy import (
    AbstractExtractor,
    ExtractorFactory,
)

# 导入所有具体实现
from module_literature.service.extractor.regex_extractor import RegexExtractor
from module_literature.service.extractor.llm_extractor import LLMExtractor

# 可扩展：在此处导入新的抽取器实现


def init_extractors():
    """初始化所有抽取器，确保它们注册到工厂"""
    # 抽取器已经在各自模块中注册到工厂
    # 此函数主要是为了确保所有模块被导入
    pass
