from sqlalchemy import String, JSON, Integer, DateTime, Column
from config.database import Base


class PmsLlmModel(Base):
    """
    大语言模型基座表
    """

    __tablename__ = "pms_llm_model"

    model_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, comment=""
    )
    display_name = Column(
        String(100), nullable=False, comment="显示名称（用户友好的描述性名称）"
    )
    model_name = Column(
        String(100),
        nullable=False,
        comment="OpenAI模型名称（如gpt-4, gpt-3.5-turbo等）",
    )
    model_version = Column(
        String(50), nullable=True, comment="模型版本（如0613, 0125-preview等）"
    )
    provider = Column(
        String(100), nullable=True, default="OpenAI", comment="模型提供商"
    )
    base_url = Column(
        String(255),
        nullable=True,
        default="https://api.openai.com/v1",
        comment="API基础URL",
    )
    api_key = Column(String(255), nullable=True, comment="OpenAI API密钥（加密存储）")
    organization_id = Column(String(100), nullable=True, comment="OpenAI组织ID")
    default_parameters = Column(
        JSON, nullable=True, comment="默认参数配置（temperature, max_tokens等）"
    )
    context_length = Column(Integer, nullable=True, comment="模型上下文长度限制")
    request_timeout = Column(
        Integer, nullable=True, default=30, comment="请求超时时间（秒）"
    )
    status = Column(
        String(1), nullable=False, default="0", comment="状态（0正常 1停用）"
    )
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
