from sqlalchemy import DateTime, Integer, Column, String
from config.database import Base


class PmsKeyword(Base):
    """
    论文关键词表
    """

    __tablename__ = "pms_keyword"

    keyword_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="关键词ID",
    )
    keyword = Column(String(255), nullable=False, comment="关键词文本")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
