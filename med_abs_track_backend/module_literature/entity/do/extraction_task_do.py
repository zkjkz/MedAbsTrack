from sqlalchemy import JSON, Text, Column, Integer, DateTime, String, SmallInteger
from config.database import Base


class PmsExtractionTask(Base):
    """
    抽取任务表
    """

    __tablename__ = "pms_extraction_task"

    task_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment="任务ID"
    )
    method_id = Column(Integer, nullable=False, comment="抽取方法ID")
    execution_parameters = Column(JSON, nullable=False, comment="执行参数")
    status = Column(
        String(1),
        nullable=False,
        default="0",
        comment="状态（0待处理 1处理中 2已完成 3失败）",
    )
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
