from datetime import datetime
import json
from pydantic import BaseModel, ConfigDict, Field, Json
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from pydantic import field_serializer, field_validator

from module_admin.annotation.pydantic_annotation import as_query


class Llm_modelModel(BaseModel):
    """
    大语言模型基座表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    model_id: Optional[int] = Field(default=None, description="")
    display_name: Optional[str] = Field(
        default=None, description="显示名称（用户友好的描述性名称）"
    )
    model_name: Optional[str] = Field(
        default=None, description="OpenAI模型名称（如gpt-4, gpt-3.5-turbo等）"
    )
    model_version: Optional[str] = Field(
        default=None, description="模型版本（如0613, 0125-preview等）"
    )
    provider: Optional[str] = Field(default=None, description="模型提供商")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    api_key: Optional[str] = Field(
        default=None, description="OpenAI API密钥（加密存储）"
    )
    organization_id: Optional[str] = Field(default=None, description="OpenAI组织ID")
    default_parameters: Optional[Json] = Field(
        default=None, description="默认参数配置（temperature, max_tokens等）"
    )
    context_length: Optional[int] = Field(
        default=None, description="模型上下文长度限制"
    )
    request_timeout: Optional[int] = Field(
        default=None, description="请求超时时间（秒）"
    )
    status: Optional[str] = Field(default=None, description="状态（0正常 1停用）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")

    @NotBlank(field_name="display_name", message="显示名称不能为空")
    def get_display_name(self):
        return self.display_name

    @NotBlank(field_name="model_name", message="模型名称不能为空")
    def get_model_name(self):
        return self.model_name

    def validate_fields(self):
        self.get_display_name()
        self.get_model_name()

    @field_serializer("default_parameters")
    def serialize_default_parameters(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value)

    @field_validator("default_parameters", mode="before")
    def validate_default_parameters(cls, value):
        if isinstance(value, dict):
            return json.dumps(value)
        return value


class Llm_modelQueryModel(Llm_modelModel):
    """
    大语言模型基座不分页查询模型
    """

    pass


@as_query
class Llm_modelPageQueryModel(Llm_modelQueryModel):
    """
    大语言模型基座分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeleteLlm_modelModel(BaseModel):
    """
    删除大语言模型基座模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    model_ids: str = Field(description="需要删除的")
