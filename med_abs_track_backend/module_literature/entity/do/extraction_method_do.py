from sqlalchemy import DateTime, Text, Integer, Enum, Column, CHAR, String, JSON
from config.database import Base
import enum


class ExtractionMethodType(enum.Enum):
    """
    抽取方法类型枚举
    """

    REGEX = "REGEX"
    LLM = "LLM"
    RULE = "RULE"
    ML = "ML"


class PmsExtractionMethod(Base):
    """
    抽取方法配置表
    """

    __tablename__ = "pms_extraction_method"

    method_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment=""
    )
    method_name = Column(String(100), nullable=False, comment="抽取方法名称")
    method_type = Column(
        Enum(ExtractionMethodType),
        nullable=False,
        comment="抽取方法类型: regex, llm, rule, ml或其他未来方法",
    )
    description = Column(Text, nullable=True, comment="方法描述")
    config_params = Column(JSON, nullable=True, comment="配置参数（JSON格式）")
    template_id = Column(
        Integer, nullable=True, comment="抽取模板ID，用于regex/rule方法"
    )
    model_id = Column(Integer, nullable=True, comment="大语言模型ID，用于llm方法")
    prompt_id = Column(Integer, nullable=True, comment="Prompt模板ID，用于llm方法")
    status = Column(CHAR(1), nullable=False, comment="状态（0正常 1停用）")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
