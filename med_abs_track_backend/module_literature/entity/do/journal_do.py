from sqlalchemy import DateTime, Integer, Column, String
from config.database import Base


class PmsJournal(Base):
    """
    期刊信息表
    """

    __tablename__ = 'pms_journal'

    journal_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, comment='期刊ID')
    journal_name = Column(String(255), nullable=False, comment='期刊名称')
    country = Column(String(100), nullable=True, comment='期刊所属国家')
    issn = Column(String(9), nullable=True, comment='期刊ISSN号')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注') 