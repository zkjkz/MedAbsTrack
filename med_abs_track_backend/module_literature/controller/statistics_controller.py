from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_literature.service.statistics_service import StatisticsService
from utils.log_util import logger
from utils.response_util import ResponseUtil


statisticsController = APIRouter(
    prefix="/literature/statistics",
    dependencies=[Depends(LoginService.get_current_user)],
)


@statisticsController.get(
    "/top_journals",
    summary="获取论文数量TOP10期刊",
    description="获取论文数量TOP10期刊统计数据",
)
async def get_top_journals(request: Request, query_db: AsyncSession = Depends(get_db)):
    """获取论文数量TOP10期刊统计数据"""
    top_journals_result = await StatisticsService.get_top_journals_services(query_db)
    logger.info("获取TOP10期刊统计数据成功")

    return ResponseUtil.success(data=top_journals_result)


@statisticsController.get(
    "/keyword_cloud",
    summary="获取热门关键词云图数据",
    description="获取热门关键词及其权重数据，用于生成词云图",
)
async def get_keyword_cloud(
    request: Request, limit: int = 50, query_db: AsyncSession = Depends(get_db)
):
    """获取热门关键词及其权重数据，用于生成词云图"""
    keyword_cloud_result = await StatisticsService.get_keyword_cloud_services(
        query_db, limit
    )
    logger.info("获取热门关键词云图数据成功")

    return ResponseUtil.success(data=keyword_cloud_result)


@statisticsController.get(
    "/abstract_structure_analysis",
    summary="获取摘要结构分析数据",
    description="获取摘要中背景、方法、结果、结论各部分的平均长度比例",
)
async def get_abstract_structure_analysis(
    request: Request, query_db: AsyncSession = Depends(get_db)
):
    """获取摘要中背景、方法、结果、结论各部分的平均长度比例"""
    abstract_structure_analysis_result = (
        await StatisticsService.get_abstract_structure_analysis_services(query_db)
    )
    logger.info("获取摘要结构分析数据成功")

    return ResponseUtil.success(data=abstract_structure_analysis_result)
