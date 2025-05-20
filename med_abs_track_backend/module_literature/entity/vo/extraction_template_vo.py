from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class Extraction_templateModel(BaseModel):
    """
    摘要抽取模板表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    template_id: Optional[int] = Field(default=None, description="")
    template_name: Optional[str] = Field(default=None, description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")
    template_content: Optional[str] = Field(default=None, description="模板内容/规则")
    status: Optional[str] = Field(default=None, description="状态（0正常 1停用）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")

    @NotBlank(field_name="template_name", message="模板名称不能为空")
    def get_template_name(self):
        return self.template_name

    @NotBlank(field_name="template_content", message="模板内容/规则不能为空")
    def get_template_content(self):
        return self.template_content

    def validate_fields(self):
        self.get_template_name()
        self.get_template_content()


class Extraction_templateQueryModel(Extraction_templateModel):
    """
    摘要抽取模板不分页查询模型
    """

    pass


@as_query
class Extraction_templatePageQueryModel(Extraction_templateQueryModel):
    """
    摘要抽取模板分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeleteExtraction_templateModel(BaseModel):
    """
    删除摘要抽取模板模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    template_ids: str = Field(description="需要删除的")
