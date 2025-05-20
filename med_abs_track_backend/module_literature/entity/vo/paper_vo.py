from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import List, Optional
from module_admin.annotation.pydantic_annotation import as_query


class PaperModel(BaseModel):
    """
    围手术期相关论文信息表对应pydantic模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    paper_id: Optional[int] = Field(default=None, description="")
    pmid: Optional[str] = Field(default=None, description="PubMed ID")
    doi: Optional[str] = Field(default=None, description="数字对象标识符")
    title: Optional[str] = Field(default=None, description="论文标题")
    abstract: Optional[str] = Field(default=None, description="论文摘要")
    abstract_id: Optional[int] = Field(default=None, description="摘要结构ID")
    journal_id: Optional[int] = Field(default=None, description="期刊ID")
    status: Optional[str] = Field(
        default=None, description="状态（0预发表 1已出版）", title="发表状态"
    )
    received_date: Optional[date] = Field(default=None, description="收稿日期")
    accepted_date: Optional[date] = Field(default=None, description="接受日期")
    published_date: Optional[date] = Field(default=None, description="发表日期")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")
    author_ids: Optional[List[int]] = Field(default=None, description="作者ID列表")
    keyword_ids: Optional[List[int]] = Field(default=None, description="关键词ID列表")

    @NotBlank(field_name="title", message="论文标题不能为空")
    def get_title(self):
        return self.title

    def validate_fields(self):
        self.get_title()


# 作者相关模型
class AuthorModel(BaseModel):
    """
    作者信息模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    author_id: Optional[int] = Field(default=None, description="作者ID")
    name: str = Field(description="作者姓名")
    affiliation: Optional[str] = Field(default=None, description="作者所属机构")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


# 关键词相关模型
class KeywordModel(BaseModel):
    """
    关键词信息模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    keyword_id: Optional[int] = Field(default=None, description="关键词ID")
    keyword: str = Field(description="关键词文本")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


# 期刊相关模型
class JournalModel(BaseModel):
    """
    期刊信息模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    journal_id: Optional[int] = Field(default=None, description="期刊ID")
    journal_name: str = Field(description="期刊名称")
    country: Optional[str] = Field(default=None, description="期刊所属国家")
    issn: Optional[str] = Field(default=None, description="期刊ISSN号")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


# 摘要结构相关模型
class AbstractStructureModel(BaseModel):
    """
    摘要结构信息模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    abstract_id: Optional[int] = Field(default=None, description="摘要结构ID")
    background: Optional[str] = Field(default=None, description="背景部分文本")
    methods: Optional[str] = Field(default=None, description="方法部分文本")
    results: Optional[str] = Field(default=None, description="结果部分文本")
    conclusion: Optional[str] = Field(default=None, description="结论部分文本")
    content: Optional[dict] = Field(default=None, description="结构化内容（JSON格式）")
    extraction_date: Optional[datetime] = Field(description="抽取日期时间")
    status: Optional[str] = Field(default="0", description="状态（0正常 1异常）")
    is_extracted: bool = Field(default=True, description="是否成功抽取")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


class PaperDetailModel(PaperModel):
    """
    论文详情模型，包含关联信息
    """

    journal: Optional[JournalModel] = Field(default=None, description="期刊信息")
    abstract_structure: Optional[AbstractStructureModel] = Field(
        default=None, description="摘要结构信息"
    )
    authors: Optional[List[AuthorModel]] = Field(default=None, description="作者列表")
    keywords: Optional[List[KeywordModel]] = Field(
        default=None, description="关键词列表"
    )


class PaperQueryModel(PaperModel):
    """
    围手术期相关论文信息不分页查询模型
    """

    pass


@as_query
class PaperPageQueryModel(PaperQueryModel):
    """
    围手术期相关论文信息分页查询模型
    """

    page_num: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页记录数")


class DeletePaperModel(BaseModel):
    """
    删除围手术期相关论文信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    paper_ids: str = Field(description="需要删除的")


class CrudPaperAuthorModel(BaseModel):
    """
    论文作者关联操作模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    paper_id: int = Field(description="论文ID")
    author_ids: str = Field(description="作者ID列表，逗号分隔")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class CrudPaperKeywordModel(BaseModel):
    """
    论文关键词关联操作模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    paper_id: int = Field(description="论文ID")
    keyword_ids: str = Field(description="关键词ID列表，逗号分隔")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class PaperAuthorResponseModel(BaseModel):
    """
    论文作者分配响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    paper: PaperModel = Field(description="论文信息")
    authors: List[AuthorModel] = Field(description="已分配的作者列表")


class PaperKeywordResponseModel(BaseModel):
    """
    论文关键词分配响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    paper: PaperModel = Field(description="论文信息")
    keywords: List[KeywordModel] = Field(description="已分配的关键词列表")
