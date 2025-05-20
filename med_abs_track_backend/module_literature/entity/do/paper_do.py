from sqlalchemy import DateTime, Date, Text, Integer, Column, String
from config.database import Base


class PmsPaper(Base):
    """
    围手术期相关论文信息表
    """

    __tablename__ = "pms_paper"

    paper_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment=""
    )
    pmid = Column(String(20), nullable=True, comment="PubMed ID")
    doi = Column(String(100), nullable=True, comment="数字对象标识符")
    title = Column(String(300), nullable=False, comment="论文标题")
    abstract = Column(Text, nullable=True, comment="论文摘要")
    abstract_id = Column(Integer, nullable=True, comment="摘要结构ID")
    journal_id = Column(Integer, nullable=True, comment="期刊ID")
    status = Column(
        String(1), nullable=True, default="0", comment="状态（0预发表 1已出版）"
    )
    received_date = Column(Date, nullable=True, comment="收稿日期")
    accepted_date = Column(Date, nullable=True, comment="接受日期")
    published_date = Column(Date, nullable=True, comment="发表日期")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
