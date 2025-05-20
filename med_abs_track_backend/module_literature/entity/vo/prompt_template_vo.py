from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class Prompt_templateModel(BaseModel):
    """
    Prompt模板表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    prompt_id: Optional[int] = Field(default=None, description="")
    prompt_name: Optional[str] = Field(default=None, description="Prompt名称")
    description: Optional[str] = Field(default=None, description="Prompt描述")
    prompt_content: Optional[str] = Field(default=None, description="Prompt内容")
    status: Optional[str] = Field(default=None, description="状态（0正常 1停用）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")

    @NotBlank(field_name="prompt_name", message="Prompt名称不能为空")
    def get_prompt_name(self):
        return self.prompt_name

    @NotBlank(field_name="prompt_content", message="Prompt内容不能为空")
    def get_prompt_content(self):
        return self.prompt_content

    def validate_fields(self):
        self.get_prompt_name()
        self.get_prompt_content()


class Prompt_templateQueryModel(Prompt_templateModel):
    """
    Prompt模板不分页查询模型
    """

    pass


@as_query
class Prompt_templatePageQueryModel(Prompt_templateQueryModel):
    """
    Prompt模板分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeletePrompt_templateModel(BaseModel):
    """
    删除Prompt模板模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    prompt_ids: str = Field(description="需要删除的")
