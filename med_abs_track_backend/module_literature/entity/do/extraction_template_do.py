from sqlalchemy import Text, Column, Integer, DateTime, String, SmallInteger
from config.database import Base


class PmsExtractionTemplate(Base):
    """
    摘要抽取模板表
    """

    __tablename__ = "pms_extraction_template"

    template_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment=""
    )
    template_name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    template_content = Column(Text, nullable=False, comment="模板内容/规则")
    status = Column(
        String(1), nullable=False, default="0", comment="状态（0正常 1停用）"
    )
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
