from datetime import datetime
import json
from pydantic import BaseModel, ConfigDict, Field, Json
from pydantic.alias_generators import to_camel
from typing import Optional
from pydantic import field_serializer, field_validator

from module_admin.annotation.pydantic_annotation import as_query


class AbstractStructureModel(BaseModel):
    """
    摘要结构表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    abstract_id: Optional[int] = Field(default=None, description="摘要结构ID")
    background: Optional[str] = Field(default=None, description="背景部分文本")
    methods: Optional[str] = Field(default=None, description="方法部分文本")
    results: Optional[str] = Field(default=None, description="结果部分文本")
    conclusion: Optional[str] = Field(default=None, description="结论部分文本")
    content: Optional[Json] = Field(default=None, description="结构化内容（JSON格式）")
    extraction_date: Optional[datetime] = Field(
        default=None, description="抽取日期时间"
    )
    status: Optional[str] = Field(default="0", description="状态（0正常 1异常）")
    is_extracted: Optional[bool] = Field(default=True, description="是否成功抽取")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")

    @field_serializer("content")
    def serialize_content(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value) if value else None

    @field_validator("content", mode="before")
    def validate_content(cls, value):
        if isinstance(value, dict):
            return json.dumps(value)
        return value


class AbstractStructureQueryModel(AbstractStructureModel):
    """
    摘要结构不分页查询模型
    """

    extraction_date_begin: Optional[datetime] = Field(
        default=None, description="抽取日期开始时间"
    )
    extraction_date_end: Optional[datetime] = Field(
        default=None, description="抽取日期结束时间"
    )
    create_time_begin: Optional[datetime] = Field(
        default=None, description="创建开始时间"
    )
    create_time_end: Optional[datetime] = Field(
        default=None, description="创建结束时间"
    )


@as_query
class AbstractStructurePageQueryModel(AbstractStructureQueryModel):
    """
    摘要结构分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")
    order_by_column: Optional[str] = Field(default=None, description="排序字段")
    is_asc: Optional[str] = Field(
        default=None, description="排序方式（ascending/descending）"
    )


class DeleteAbstractStructureModel(BaseModel):
    """
    删除摘要结构模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    abstract_ids: str = Field(description="需要删除的摘要结构ID，多个以逗号分隔")
