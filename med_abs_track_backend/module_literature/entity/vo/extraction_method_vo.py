from datetime import datetime
import json
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    Json,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query
from module_literature.entity.do.extraction_method_do import ExtractionMethodType


class Extraction_methodModel(BaseModel):
    """
    抽取方法配置表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    method_id: Optional[int] = Field(default=None, description="")
    method_name: Optional[str] = Field(default=None, description="抽取方法名称")
    method_type: Optional[ExtractionMethodType] = Field(
        default=None, description="抽取方法类型: regex, llm, rule, ml或其他未来方法"
    )
    description: Optional[str] = Field(default=None, description="方法描述")
    config_params: Optional[Json] = Field(
        default=None, description="配置参数（JSON格式）"
    )
    template_id: Optional[int] = Field(
        default=None, description="抽取模板ID，用于regex/rule方法"
    )
    model_id: Optional[int] = Field(
        default=None, description="大语言模型ID，用于llm方法"
    )
    prompt_id: Optional[int] = Field(
        default=None, description="Prompt模板ID，用于llm方法"
    )
    status: Optional[str] = Field(default=None, description="状态（0正常 1停用）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")

    @NotBlank(field_name="method_name", message="抽取方法名称不能为空")
    def get_method_name(self):
        return self.method_name

    @NotBlank(
        field_name="method_type",
        message="抽取方法类型: regex, llm, rule, ml或其他未来方法不能为空",
    )
    def get_method_type(self):
        return self.method_type

    @NotBlank(field_name="status", message="状态不能为空")
    def get_status(self):
        return self.status

    def validate_fields(self):
        self.get_method_name()
        self.get_method_type()
        self.get_status()

    @field_serializer("config_params")
    def serialize_config_params(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value)

    @field_validator("config_params", mode="before")
    def validate_config_params(cls, value):
        if isinstance(value, dict):
            return json.dumps(value)
        return value


class Extraction_methodQueryModel(Extraction_methodModel):
    """
    抽取方法配置不分页查询模型
    """

    pass


@as_query
class Extraction_methodPageQueryModel(Extraction_methodQueryModel):
    """
    抽取方法配置分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeleteExtraction_methodModel(BaseModel):
    """
    删除抽取方法配置模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    method_ids: str = Field(description="需要删除的")
