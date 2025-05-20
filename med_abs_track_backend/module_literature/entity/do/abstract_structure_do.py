from sqlalchemy import DateTime, Text, Integer, Column, String, Boolean, JSON, func
from config.database import Base


class PmsAbstractStructure(Base):
    """
    摘要结构化抽取结果表
    """

    __tablename__ = "pms_abstract_structure"

    abstract_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="摘要结构ID",
    )
    background = Column(Text, nullable=True, comment="背景部分文本")
    methods = Column(Text, nullable=True, comment="方法部分文本")
    results = Column(Text, nullable=True, comment="结果部分文本")
    conclusion = Column(Text, nullable=True, comment="结论部分文本")
    content = Column(JSON, nullable=True, comment="结构化内容（JSON格式）")
    extraction_date = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        comment="抽取日期时间",
    )
    status = Column(
        String(1), nullable=False, default="0", comment="状态（0正常 1异常）"
    )
    is_extracted = Column(Boolean, nullable=False, default=True, comment="是否成功抽取")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
