from typing import List, Dict, Any
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_literature.entity.do.paper_do import PmsPaper
from module_literature.entity.do.journal_do import PmsJournal
from module_literature.entity.do.keyword_do import PmsKeyword
from module_literature.entity.do.paper_keyword_do import PmsPaperKeyword
from module_literature.entity.do.abstract_structure_do import PmsAbstractStructure


class StatisticsService:
    """统计分析服务"""

    @staticmethod
    async def get_top_journals_services(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取TOP10期刊的论文数量统计

        Args:
            db: 数据库会话

        Returns:
            List[Dict[str, Any]]: 包含期刊名称和论文数量的列表
        """
        # 联合查询获取期刊和论文数量
        result = await db.execute(
            select(
                PmsJournal.journal_id,
                PmsJournal.journal_name,
                func.count(PmsPaper.paper_id).label("paper_count"),
            )
            .join(PmsPaper, PmsPaper.journal_id == PmsJournal.journal_id)
            .group_by(PmsJournal.journal_id, PmsJournal.journal_name)
            .order_by(desc("paper_count"))
            .limit(10)
        )

        # 转换为字典列表
        top_journals = [
            {
                "journal_id": journal_id,
                "journal_name": journal_name,
                "paper_count": paper_count,
            }
            for journal_id, journal_name, paper_count in result.all()
        ]

        return top_journals

    @staticmethod
    async def get_keyword_cloud_services(
        db: AsyncSession, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取热门关键词及其权重数据，用于生成词云图

        Args:
            db: 数据库会话
            limit: 返回的关键词数量限制，默认50个

        Returns:
            List[Dict[str, Any]]: 包含关键词和权重的列表
        """
        # 联合查询获取关键词及其出现频率
        result = await db.execute(
            select(
                PmsKeyword.keyword_id,
                PmsKeyword.keyword,
                func.count(PmsPaperKeyword.paper_id).label("weight"),
            )
            .join(PmsPaperKeyword, PmsPaperKeyword.keyword_id == PmsKeyword.keyword_id)
            .group_by(PmsKeyword.keyword_id, PmsKeyword.keyword)
            .order_by(desc("weight"))
            .limit(limit)
        )

        # 转换为字典列表
        keyword_cloud = [
            {"keyword_id": keyword_id, "keyword": keyword, "weight": weight}
            for keyword_id, keyword, weight in result.all()
        ]

        return keyword_cloud

    @staticmethod
    async def get_abstract_structure_analysis_services(
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        获取摘要中背景、方法、结果、结论各部分的平均长度比例

        Args:
            db: 数据库会话

        Returns:
            Dict[str, Any]: 包含各部分平均长度和比例的字典
        """
        # 获取所有成功抽取的摘要结构记录
        result = await db.execute(
            select(
                func.avg(func.length(PmsAbstractStructure.background)).label(
                    "avg_background_length"
                ),
                func.avg(func.length(PmsAbstractStructure.methods)).label(
                    "avg_methods_length"
                ),
                func.avg(func.length(PmsAbstractStructure.results)).label(
                    "avg_results_length"
                ),
                func.avg(func.length(PmsAbstractStructure.conclusion)).label(
                    "avg_conclusion_length"
                ),
            ).where(PmsAbstractStructure.is_extracted == 1)
        )

        # 提取平均长度
        avg_data = result.one()
        avg_background_length = avg_data.avg_background_length or 0
        avg_methods_length = avg_data.avg_methods_length or 0
        avg_results_length = avg_data.avg_results_length or 0
        avg_conclusion_length = avg_data.avg_conclusion_length or 0

        # 计算总长度和各部分比例
        total_length = (
            avg_background_length
            + avg_methods_length
            + avg_results_length
            + avg_conclusion_length
        )

        # 避免除零错误
        if total_length == 0:
            return {
                "background": {"length": 0, "percentage": 0},
                "methods": {"length": 0, "percentage": 0},
                "results": {"length": 0, "percentage": 0},
                "conclusion": {"length": 0, "percentage": 0},
                "total_length": 0,
            }

        # 计算各部分比例
        background_percentage = (avg_background_length / total_length) * 100
        methods_percentage = (avg_methods_length / total_length) * 100
        results_percentage = (avg_results_length / total_length) * 100
        conclusion_percentage = (avg_conclusion_length / total_length) * 100

        # 构建返回结果
        structure_analysis = {
            "background": {
                "length": round(avg_background_length, 2),
                "percentage": round(background_percentage, 2),
            },
            "methods": {
                "length": round(avg_methods_length, 2),
                "percentage": round(methods_percentage, 2),
            },
            "results": {
                "length": round(avg_results_length, 2),
                "percentage": round(results_percentage, 2),
            },
            "conclusion": {
                "length": round(avg_conclusion_length, 2),
                "percentage": round(conclusion_percentage, 2),
            },
            "total_length": round(total_length, 2),
        }

        return structure_analysis
