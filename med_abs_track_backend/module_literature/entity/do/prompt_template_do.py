from sqlalchemy import String, Integer, DateTime, Column, SmallInteger, Text
from config.database import Base


class PmsPromptTemplate(Base):
    """
    Prompt模板表
    """

    __tablename__ = "pms_prompt_template"

    prompt_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment=""
    )
    prompt_name = Column(String(100), nullable=False, comment="Prompt名称")
    description = Column(Text, nullable=True, comment="Prompt描述")
    prompt_content = Column(Text, nullable=False, comment="Prompt内容")
    status = Column(
        String(1), nullable=False, default="0", comment="状态（0正常 1停用）"
    )
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
