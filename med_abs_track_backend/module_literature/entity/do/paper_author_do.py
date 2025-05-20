from sqlalchemy import Integer, Column, ForeignKey
from config.database import Base


class PmsPaperAuthor(Base):
    """
    论文与作者关联表
    """

    __tablename__ = 'pms_paper_author'

    paper_id = Column(Integer, ForeignKey('pms_paper.paper_id', ondelete='CASCADE'), primary_key=True, nullable=False, comment='论文ID')
    author_id = Column(Integer, ForeignKey('pms_author.author_id', ondelete='CASCADE'), primary_key=True, nullable=False, comment='作者ID')
    author_order = Column(Integer, nullable=False, comment='作者排序') 