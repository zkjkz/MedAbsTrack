import { request } from '@/utils/hsj/service/index'

// 搜索PubMed文献
export function searchPubMedPapers(query) {
  return request({
    url: '/literature/paper_search/search',
    method: 'get',
    params: query
  })
}

// 获取PubMed文献详情
export function getPubMedPaperDetail(pmid) {
  return request({
    url: `/literature/paper_search/detail/${pmid}`,
    method: 'get'
  })
}