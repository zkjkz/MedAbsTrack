import json
from datetime import datetime
import openai
from typing import Dict, Optional

from module_literature.entity.do.extraction_method_do import ExtractionMethodType
from module_literature.entity.vo.paper_vo import AbstractStructureModel, PaperModel
from module_literature.service.extractor.extractor_strategy import (
    AbstractExtractor,
    ExtractorFactory,
)
from module_literature.service.llm_model_service import Llm_modelService
from module_literature.service.prompt_template_service import Prompt_templateService


class LLMExtractor(AbstractExtractor):
    """
    大语言模型抽取器实现
    """

    async def extract(
        self, paper: PaperModel, execution_parameters: Optional[Dict] = None
    ) -> AbstractStructureModel:
        """
        使用大语言模型进行抽取

        :param paper: 论文信息模型
        :param execution_parameters: 执行参数, 包含model_id, prompt_id等信息
        :return: 抽取结果
        """
        if not paper or not paper.abstract:
            raise ValueError("论文摘要为空，无法进行抽取")

        # 获取执行参数
        model_id = None
        prompt_id = None
        db_session = None

        if execution_parameters:
            model_id = execution_parameters.get("model_id")
            prompt_id = execution_parameters.get("prompt_id")
            db_session = execution_parameters.get("db_session")

        # 检查参数
        if not model_id or not prompt_id or not db_session:
            raise ValueError("模型ID、Prompt ID和数据库会话不能为空")

        # 获取模型配置
        model_config = await Llm_modelService.llm_model_detail_services(
            db_session, model_id
        )
        if not model_config:
            raise ValueError(f"找不到ID为{model_id}的大语言模型配置")

        # 获取Prompt模板
        prompt_template = await Prompt_templateService.prompt_template_detail_services(
            db_session, prompt_id
        )
        if not prompt_template or not prompt_template.prompt_content:
            raise ValueError(f"找不到ID为{prompt_id}的Prompt模板或模板内容为空")

        # 准备请求参数
        base_url = model_config.base_url
        api_key = model_config.api_key
        organization_id = model_config.organization_id
        model_name = model_config.model_name

        # 准备Prompt
        prompt_content = prompt_template.prompt_content
        # 替换占位符
        prompt = prompt_content.replace("{title}", paper.title or "").replace(
            "{abstract}", paper.abstract or ""
        )

        # 默认参数
        default_params = model_config.default_parameters or {}

        # 初始化结果
        result = {
            "background": None,
            "methods": None,
            "results": None,
            "conclusion": None,
            "content": {},
        }

        # 调用LLM API
        try:
            # 配置OpenAI客户端
            openai_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=model_config.request_timeout or 30.0,
                organization=organization_id if organization_id else None,
            )

            # 准备请求体
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的医学摘要结构化提取助手。请从给定的论文摘要中提取背景(Background)、方法(Methods)、结果(Results)和结论(Conclusion)部分。",
                },
                {"role": "user", "content": prompt},
            ]

            # 发送请求
            response = await openai_client.chat.completions.create(
                model=model_name, messages=messages, **default_params
            )

            # 解析响应
            llm_response = response.choices[0].message.content
            # 尝试解析JSON响应
            try:
                # 假设LLM返回了JSON格式的结果
                parsed_response = json.loads(llm_response)

                # 尝试提取各个部分
                for section in ["background", "methods", "results", "conclusion"]:
                    if section in parsed_response:
                        result[section] = parsed_response[section]
                        result["content"][section] = parsed_response[section]
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接存储到content
                result["content"]["raw_response"] = llm_response

            # 检查是否成功抽取
            is_extracted = any(
                result[section]
                for section in ["background", "methods", "results", "conclusion"]
            )
            # 创建抽取结果
            abstract_structure = AbstractStructureModel(
                extraction_date=datetime.now(),  # 使用当前时间作为抽取日期
                background=result.get("background"),
                methods=result.get("methods"),
                results=result.get("results"),
                conclusion=result.get("conclusion"),
                content=result.get("content"),
                is_extracted=is_extracted,
            )
            return abstract_structure

        except Exception as e:
            raise e


# 注册到工厂
ExtractorFactory.register(ExtractionMethodType.LLM, LLMExtractor)
