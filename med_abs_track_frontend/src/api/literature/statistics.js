import { request } from '@/utils/hsj/service/index'

// 获取TOP10期刊的论文数量统计
export function getTopJournals(query) {
  return request({
    url: '/literature/statistics/top_journals',
    method: 'get',
    params: query
  })
}

// 获取热门关键词及其权重数据，用于生成词云图
export function getKeywordCloud(limit) {
  return request({
    url: '/literature/statistics/keyword_cloud',
    method: 'get',
    params: { limit }
  })
}

// 获取摘要中背景、方法、结果、结论各部分的平均长度比例
export function getAbstractStructureAnalysis() {
  return request({
    url: '/literature/statistics/abstract_structure_analysis',
    method: 'get'
  })
} 