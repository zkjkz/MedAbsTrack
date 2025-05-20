import re
from datetime import datetime
from typing import Dict, Optional

from module_literature.entity.do.extraction_method_do import ExtractionMethodType
from module_literature.entity.vo.paper_vo import AbstractStructureModel, PaperModel
from module_literature.service.extractor.extractor_strategy import (
    AbstractExtractor,
    ExtractorFactory,
)
from module_literature.service.extraction_template_service import (
    Extraction_templateService,
)


class RegexExtractor(AbstractExtractor):
    """
    正则表达式抽取器实现
    """

    async def extract(
        self, paper: PaperModel, execution_parameters: Optional[Dict] = None
    ) -> AbstractStructureModel:
        """
        使用正则表达式进行抽取

        :param paper: 论文信息模型
        :param execution_parameters: 执行参数, 包含template_id等信息
        :return: 抽取结果
        """
        if not paper or not paper.abstract:
            raise ValueError("论文摘要为空，无法进行抽取")

        # 获取执行参数
        template_id = None
        db_session = None

        if execution_parameters:
            template_id = execution_parameters.get("template_id")
            db_session = execution_parameters.get("db_session")

        # 如果没有提供模板ID，则使用默认模板
        if not template_id and not db_session:
            raise ValueError("模板ID和数据库会话不能同时为空")

        # 获取模板内容
        template = await Extraction_templateService.extraction_template_detail_services(
            db_session, template_id
        )
        if not template or not template.template_content:
            raise ValueError(f"找不到ID为{template_id}的抽取模板或模板内容为空")

        # 解析模板内容
        template_content = template.template_content
        # 初始化抽取结果
        result = {
            "background": None,
            "methods": None,
            "results": None,
            "conclusion": None,
            "content": {},
        }

        # 尝试使用正则表达式抽取各个部分
        try:
            # 解析模板内容为JSON
            import json

            # 处理JSON中转义字符问题
            # 将单反斜杠转义序列如\s替换为双反斜杠\\s，确保JSON解析正确
            template_content = template_content.replace(r"\s", r"\\s")
            template_content = template_content.replace(r"\d", r"\\d")
            template_content = template_content.replace(r"\w", r"\\w")
            template_content = template_content.replace(r"\b", r"\\b")
            # 其他可能的正则表达式转义序列
            template_content = template_content.replace(r"\(", r"\\(")
            template_content = template_content.replace(r"\)", r"\\)")
            template_content = template_content.replace(r"\[", r"\\[")
            template_content = template_content.replace(r"\]", r"\\]")
            template_content = template_content.replace(r"\{", r"\\{")
            template_content = template_content.replace(r"\}", r"\\}")
            template_content = template_content.replace(r"\+", r"\\+")
            template_content = template_content.replace(r"\*", r"\\*")
            template_content = template_content.replace(r"\?", r"\\?")
            template_content = template_content.replace(r"\^", r"\\^")
            template_content = template_content.replace(r"\$", r"\\$")
            template_content = template_content.replace(r"\|", r"\\|")
            template_content = template_content.replace(r"\.", r"\\.")
            template_content = template_content.replace(
                r"\\\\", r"\\"
            )  # 修复已经正确转义的情况

            template_json = json.loads(template_content)

            # 处理新的模板格式（包含patterns数组）
            if "patterns" in template_json:
                patterns = template_json["patterns"]
                for pattern_obj in patterns:
                    section = pattern_obj.get("section")
                    regex = pattern_obj.get("regex")

                    if (
                        section
                        and regex
                        and section
                        in ["background", "methods", "results", "conclusion"]
                    ):
                        # 查找匹配的部分
                        match = re.search(regex, paper.abstract, re.DOTALL)
                        if match:
                            # 找到匹配后，提取该部分后面的内容直到下一个部分标记或结束
                            start_pos = match.end()

                            # 查找后续的所有部分标记
                            next_sections = []
                            for p in patterns:
                                if p.get("section") != section:
                                    next_match = re.search(
                                        p.get("regex", ""), paper.abstract, re.DOTALL
                                    )
                                    if next_match and next_match.start() > start_pos:
                                        next_sections.append(
                                            (next_match.start(), p.get("section"))
                                        )

                            # 找到最近的下一个部分
                            next_sections.sort()
                            end_pos = len(paper.abstract)
                            if next_sections:
                                end_pos = next_sections[0][0]

                            # 提取内容
                            content = paper.abstract[start_pos:end_pos].strip()
                            result[section] = content
                            result["content"][section] = content
            else:
                # 处理旧的模板格式（直接映射部分到正则表达式）
                regex_patterns = template_json

                for section, pattern in regex_patterns.items():
                    if section in ["background", "methods", "results", "conclusion"]:
                        match = re.search(
                            pattern, paper.abstract, re.DOTALL | re.IGNORECASE
                        )
                        if match:
                            result[section] = match.group(1).strip()
                            result["content"][section] = match.group(1).strip()

            # 检查是否成功抽取
            is_extracted = any(
                result[section]
                for section in ["background", "methods", "results", "conclusion"]
            )

            # 检查摘要有内容但抽取结果为空的情况
            if not is_extracted and paper.abstract and paper.abstract.strip():
                raise ValueError(
                    "摘要内容存在但正则抽取结果为空，建议尝试其他抽取方法（如LLM抽取）"
                )

            # 创建抽取结果
            abstract_structure = AbstractStructureModel(
                abstract_id=None,  # 新创建的抽取结果，ID由数据库生成
                background=result["background"],
                methods=result["methods"],
                results=result["results"],
                conclusion=result["conclusion"],
                content=result["content"],
                extraction_date=datetime.now(),
                status="0",  # 0表示正常
                is_extracted=is_extracted,
                create_time=datetime.now(),
                update_time=datetime.now(),
            )

            return abstract_structure

        except Exception as e:
            raise e


# 注册到工厂
ExtractorFactory.register(ExtractionMethodType.REGEX, RegexExtractor)
