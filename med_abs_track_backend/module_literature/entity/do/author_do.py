from sqlalchemy import DateTime, Text, Integer, Column, String
from config.database import Base


class PmsAuthor(Base):
    """
    论文作者表
    """

    __tablename__ = 'pms_author'

    author_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, comment='作者ID')
    name = Column(String(255), nullable=False, comment='作者姓名')
    affiliation = Column(Text, nullable=True, comment='作者所属机构')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注') 