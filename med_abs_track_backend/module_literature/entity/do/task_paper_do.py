from sqlalchemy import Column, Integer, ForeignKey
from config.database import Base


class PmsTaskPaper(Base):
    """
    抽取任务与论文关联表
    """

    __tablename__ = "pms_task_paper"

    task_id = Column(
        Integer,
        ForeignKey("pms_extraction_task.task_id"),
        primary_key=True,
        nullable=False,
        comment="任务ID",
    )
    paper_id = Column(
        Integer,
        ForeignKey("pms_paper.paper_id"),
        primary_key=True,
        nullable=False,
        comment="论文ID",
    )
