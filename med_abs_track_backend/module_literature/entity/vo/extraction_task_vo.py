from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, Json
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Dict, List, Optional
from module_admin.annotation.pydantic_annotation import as_query
from module_literature.entity.vo.paper_vo import PaperModel, AbstractStructureModel


class ExtractionTaskModel(BaseModel):
    """
    抽取任务表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    task_id: Optional[int] = Field(default=None, description="任务ID")
    method_id: Optional[int] = Field(default=None, description="抽取方法ID")
    execution_parameters: Optional[Json] = Field(default=None, description="执行参数")
    status: Optional[str] = Field(
        default="0",
        description="状态（0待处理 1处理中 2已完成 3失败）",
        title="任务状态",
    )
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")
    paper_ids: Optional[List[int]] = Field(default=None, description="论文ID列表")

    @NotBlank(field_name="method_id", message="抽取方法ID不能为空")
    def get_method_id(self):
        return self.method_id

    def validate_fields(self):
        self.get_method_id()


class ExtractionRequestModel(BaseModel):
    """
    抽取请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    method_id: int = Field(description="抽取方法ID")
    paper_id: Optional[int] = Field(default=None, description="论文ID，与paper二选一")
    paper: Optional[PaperModel] = Field(
        default=None, description="论文信息，与paper_id二选一"
    )
    execution_parameters: Optional[Dict] = Field(default=None, description="执行参数")
    create_by: Optional[str] = Field(default=None, description="创建者")
    update_by: Optional[str] = Field(default=None, description="更新者")


class ExtractionResponseModel(BaseModel):
    """
    抽取响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: int = Field(description="任务ID")
    status: str = Field(description="任务状态（0待处理 1处理中 2已完成 3失败）")
    abstract_structure: Optional[AbstractStructureModel] = Field(
        default=None, description="抽取结果"
    )
    error_message: Optional[str] = Field(default=None, description="错误信息")


class ExtractionTaskQueryModel(ExtractionTaskModel):
    """
    抽取任务不分页查询模型
    """

    pass


@as_query
class ExtractionTaskPageQueryModel(ExtractionTaskQueryModel):
    """
    抽取任务分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeleteExtractionTaskModel(BaseModel):
    """
    删除抽取任务模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_ids: str = Field(description="需要删除的任务ID列表，逗号分隔")


class CrudTaskPaperModel(BaseModel):
    """
    任务论文关联操作模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: int = Field(description="任务ID")
    paper_ids: str = Field(description="论文ID列表，逗号分隔")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
