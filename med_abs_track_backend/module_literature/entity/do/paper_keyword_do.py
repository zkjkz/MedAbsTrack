from sqlalchemy import Integer, Column, ForeignKey
from config.database import Base


class PmsPaperKeyword(Base):
    """
    论文与关键词关联表
    """

    __tablename__ = 'pms_paper_keyword'

    paper_id = Column(Integer, ForeignKey('pms_paper.paper_id', ondelete='CASCADE'), primary_key=True, nullable=False, comment='论文ID')
    keyword_id = Column(Integer, ForeignKey('pms_keyword.keyword_id', ondelete='CASCADE'), primary_key=True, nullable=False, comment='关键词ID') 